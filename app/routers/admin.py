"""Admin-only usage dashboard (/admin). Only emails listed in ADMIN_EMAILS can open it."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from google.cloud import firestore

from app import config
from app.clients import ai
from app.collections import PROJECTS, USERS
from app.database import get_db
from app.dependencies import require_auth
from app.models import User
from app.services import usage as usage_service
from app.templating import is_admin, templates

router = APIRouter(tags=["admin"])

PERIODS = (7, 30, 90)
_CHART_W, _CHART_H = 720, 150


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


@router.get("/admin")
async def admin_dashboard(
    request: Request,
    days: int = 7,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    if not is_admin(user):
        # Hide that the page exists from non-admins.
        raise HTTPException(status_code=404)
    days = days if days in PERIODS else 7
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

    # Show at most ~8 date labels on the x axis.
    label_every = max(1, len(u.daily) // 8)

    return templates.TemplateResponse("admin.html", {
        "request": request, "user": user, "u": u, "days": days, "periods": PERIODS,
        "daily_bars": daily_bars, "hourly_bars": hourly_bars, "label_every": label_every,
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
