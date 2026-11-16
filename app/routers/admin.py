"""Admin portal (/admin): its own login, its own session, its own layout.

Student accounts can never open these pages — admin access uses separate
credentials (ADMIN_USERNAME / ADMIN_PASSWORD_HASH) and a separate cookie.
"""
import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from google.cloud import firestore

from app import config
from app.clients import ai
from app.collections import PROJECTS, USERS
from app.database import get_db
from app import monitoring
from app.monitoring import client_ip
from app.services import admin_auth
from app.services import usage as usage_service
from app.templating import templates

router = APIRouter(prefix="/admin", tags=["admin"])

PERIODS = (7, 30, 90)
_CHART_W, _CHART_H = 720, 150


# ── auth ────────────────────────────────────────────────────────────────────

def require_admin(request: Request, db: firestore.Client = Depends(get_db)) -> dict:
    session = admin_auth.get_session(db, request.cookies.get(admin_auth.ADMIN_COOKIE))
    if not session:
        raise HTTPException(status_code=303, headers={"Location": "/admin/login"})
    request.state.user_id = f"admin:{session['username']}"   # for the access log
    return session


def _login_page(request: Request, error: str | None = None, status_code: int = 200, username: str = ""):
    return templates.TemplateResponse("admin/login.html", {
        "request": request, "error": error, "username": username,
        "configured": admin_auth.is_configured(),
    }, status_code=status_code)


@router.get("/login")
async def login_page(request: Request, db: firestore.Client = Depends(get_db)):
    if admin_auth.is_configured() and admin_auth.get_session(db, request.cookies.get(admin_auth.ADMIN_COOKIE)):
        return RedirectResponse(url="/admin", status_code=303)
    return _login_page(request)


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(default=""),
    password: str = Form(default=""),
    db: firestore.Client = Depends(get_db),
):
    ip, _ = client_ip(request)
    if not admin_auth.is_configured():
        return _login_page(request, status_code=503)
    if admin_auth.is_locked(ip):
        admin_auth.audit(db, "admin_login_blocked", None, ip)
        return _login_page(request, "Too many failed attempts. Please wait 15 minutes and try again.",
                           status_code=429, username=username)
    if not admin_auth.verify_credentials(username, password):
        admin_auth.record_failure(ip)
        admin_auth.audit(db, "admin_login_failed", None, ip)
        return _login_page(request, "Wrong username or password.", status_code=401, username=username)

    admin_auth.clear_failures(ip)
    token = admin_auth.create_session(db, config.ADMIN_USERNAME, ip)
    admin_auth.audit(db, "admin_login", config.ADMIN_USERNAME, ip)
    response = RedirectResponse(url="/admin", status_code=303)
    response.set_cookie(
        key=admin_auth.ADMIN_COOKIE, value=token, path="/admin",
        httponly=True, samesite="strict", secure=config.COOKIE_SECURE,
        max_age=config.ADMIN_SESSION_HOURS * 3600,
    )
    return response


@router.post("/logout")
async def logout(request: Request, db: firestore.Client = Depends(get_db)):
    token = request.cookies.get(admin_auth.ADMIN_COOKIE)
    session = admin_auth.get_session(db, token)
    admin_auth.delete_session(db, token)
    if session:
        admin_auth.audit(db, "admin_logout", session.get("username"), client_ip(request)[0])
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie(admin_auth.ADMIN_COOKIE, path="/admin")
    return response


# ── dashboard ───────────────────────────────────────────────────────────────

def bar_geometry(values: list[int], width: int = _CHART_W, height: int = _CHART_H, gap: int = 2) -> list[dict]:
    """x/y/w/h for a simple bar chart; bars anchor to the baseline, 2px gaps between them."""
    n = len(values) or 1
    top = max(values) if values and max(values) > 0 else 1
    step = width / n
    w = max(step - gap, 1)
    out = []
    for i, v in enumerate(values):
        h = 0 if v == 0 else max(2.0, v / top * height)
        out.append({"x": round(i * step + gap / 2, 2), "y": round(height - h, 2), "w": round(w, 2), "h": round(h, 2), "v": v})
    return out


def _bar_path(b: dict, r: float = 4) -> str:
    """Bar with rounded top corners only (4px data-end), flat on the baseline."""
    x, y, w, h = b["x"], b["y"], b["w"], b["h"]
    r = min(r, w / 2, h)
    return (f"M{x},{y + h} L{x},{y + r} Q{x},{y} {x + r},{y} L{x + w - r},{y} "
            f"Q{x + w},{y} {x + w},{y + r} L{x + w},{y + h} Z")


@router.get("")
async def admin_dashboard(
    request: Request,
    days: int = 7,
    admin: dict = Depends(require_admin),
    db: firestore.Client = Depends(get_db),
):
    days = days if days in PERIODS else 7
    # Save log entries still waiting in memory, so the dashboard includes activity up to now.
    await asyncio.to_thread(monitoring.flush, db)
    now = datetime.now(timezone.utc)
    entries, truncated = usage_service.load(db, days, now=now)
    u = usage_service.summarize(entries, days, now, config.DASHBOARD_TZ, truncated=truncated)

    daily_bars = bar_geometry([d.users for d in u.daily])
    for b, d in zip(daily_bars, u.daily):
        b["path"] = _bar_path(b)
        b["tip"] = f"{d.day.strftime('%a %d %b')}: {d.users} active user{'s' if d.users != 1 else ''}, {d.actions} actions"
    hourly_bars = bar_geometry(u.hourly)
    for h, b in enumerate(hourly_bars):
        b["path"] = _bar_path(b)
        b["tip"] = f"{h:02d}:00–{h:02d}:59: {u.hourly[h]} actions"

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request, "admin": admin, "u": u, "days": days, "periods": PERIODS,
        "daily_bars": daily_bars, "hourly_bars": hourly_bars,
        "label_every": max(1, len(u.daily) // 8),
        "chart_w": _CHART_W, "chart_h": _CHART_H,
        "max_daily": max([d.users for d in u.daily] or [0]),
        "max_hourly": max(u.hourly or [0]),
        "max_feature": max([f.uses for f in u.features] or [1]),
        "total_users": usage_service.count_collection(db, USERS),
        "total_projects": usage_service.count_collection(db, PROJECTS),
        "ai_provider": ai.provider(), "ai_model": ai.model_name(),
        "tz": config.DASHBOARD_TZ,
        "generated_at": now,
    })
