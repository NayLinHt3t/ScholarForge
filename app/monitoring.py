"""Access log (Computer Crime Act §26) + usage data for the admin dashboard.

Every request (except static files) writes one append-only entry to the
Firestore collection `access_log`:

    ts, expire_at, user_id, ip, forwarded_for, method, path, route,
    feature, status, duration_ms, ai_calls, ai_ms, ai_errors

`expire_at` drives a Firestore TTL policy (see the deploy guide) so entries are
deleted automatically after ACCESS_LOG_RETENTION_DAYS (91 days ≥ the 90-day minimum).
Writes happen in a background thread and never slow down or break a request.
"""
import asyncio
import logging
import re
import time
from datetime import datetime, timedelta, timezone

from fastapi import Request

from app import config
from app.clients import ai

log = logging.getLogger(__name__)

from app.collections import ACCESS_LOG  # noqa: E402  (single source of truth)
UNAUTHENTICATED = "unauthenticated"

# (method, route-template regex, feature label) — first match wins.
# Only user-facing actions get a label; everything else is logged with feature=None.
_FEATURES: list[tuple[str, re.Pattern, str]] = [(m, re.compile(p), label) for m, p, label in [
    ("POST", r"^/auth/signup$", "Sign up"),
    ("POST", r"^/auth/login$", "Sign in"),
    ("GET",  r"^/projects$", "Home"),
    ("POST", r"^/projects$", "Create project"),
    ("GET",  r"^/projects/\{project_id\}$", "Open project"),
    ("GET",  r"^/projects/\{project_id\}/search$", "Find papers"),
    ("POST", r"^/projects/\{project_id\}/library$", "Save paper"),
    ("POST", r"^/projects/\{project_id\}/search/add-by-url$", "Add paper by link"),
    ("POST", r"^/projects/\{project_id\}/sources$", "Add paper by hand"),
    ("GET",  r"^/projects/\{project_id\}/sources/\{source_id\}$", "Read paper"),
    ("POST", r"/sources/\{source_id\}/ask$", "Ask AI about a paper"),
    ("POST", r"/sources/\{source_id\}/save-note$", "Save AI answer as note"),
    ("POST", r"/sources/\{source_id\}/summarize$", "Summarize a paper"),
    ("POST", r"/notes(/\{note_id\}/edit)?$", "Write or edit a note"),
    ("GET",  r"^/projects/\{project_id\}/notes/(new|\{note_id\})$", "Open note editor"),
    ("GET",  r"^/library$", "My Library"),
    ("GET",  r"^/notes$", "My Notes"),
    ("GET",  r"^/settings$", "Settings"),
    ("*",    r"outline", "Outline"),
    ("*",    r"summarize", "Summarize several papers"),
    ("*",    r"/evidence", "Saved quotes"),
    ("*",    r"/themes", "Themes"),
    ("*",    r"/claims", "Claims"),
    ("GET",  r"export|\.bib$", "Download"),
]]


def feature_for(method: str, route: str | None, has_query: bool = False) -> str | None:
    if not route:
        return None
    for m, pattern, label in _FEATURES:
        if (m == "*" or m == method) and pattern.search(route):
            if label == "Find papers" and has_query:
                return "Search papers"
            return label
    return None


def client_ip(request: Request) -> tuple[str, str]:
    """(best-guess client IP, raw X-Forwarded-For chain). Behind Cloud Run the
    client IP is in X-Forwarded-For; the raw chain is kept as evidence."""
    fwd = request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()[:64], fwd[:200]
    return (request.client.host if request.client else "unknown"), ""


def build_entry(request: Request, status: int, duration_ms: int, usage: dict, now: datetime) -> dict:
    route_obj = request.scope.get("route")
    route = getattr(route_obj, "path", None)
    ip, chain = client_ip(request)
    return {
        "ts": now,
        "expire_at": now + timedelta(days=config.ACCESS_LOG_RETENTION_DAYS),
        "user_id": getattr(request.state, "user_id", None) or UNAUTHENTICATED,
        "ip": ip,
        "forwarded_for": chain,
        "method": request.method,
        "path": request.url.path[:300],
        "route": route,
        "feature": feature_for(request.method, route, bool(request.query_params.get("q"))),
        "status": status,
        "duration_ms": duration_ms,
        "ai_calls": usage.get("calls", 0),
        "ai_ms": usage.get("ms", 0),
        "ai_errors": usage.get("errors", 0),
    }


def _write(db, entry: dict) -> None:
    try:
        db.collection(ACCESS_LOG).document().set(entry)
    except Exception as e:  # noqa: BLE001 — logging must never break the app
        log.warning("access_log.write_failed error=%s", type(e).__name__)


def _db_for(request: Request):
    from app.database import get_db
    provider = request.app.dependency_overrides.get(get_db, get_db)
    return provider()


async def access_log_middleware(request: Request, call_next):
    if not config.ACCESS_LOG_ENABLED or request.url.path.startswith("/static") or request.url.path == "/favicon.ico":
        return await call_next(request)

    usage = ai.start_tracking()
    started = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        try:
            entry = build_entry(
                request, status, int((time.perf_counter() - started) * 1000), usage,
                datetime.now(timezone.utc),
            )
            db = _db_for(request)
            asyncio.get_running_loop().run_in_executor(None, _write, db, entry)
        except Exception as e:  # noqa: BLE001
            log.warning("access_log.build_failed error=%s", type(e).__name__)
