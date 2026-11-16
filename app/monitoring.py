"""Access log (Computer Crime Act §26) + usage data for the admin dashboard.

Every request (except static files) produces one entry; entries are written to
the Firestore collection `access_log` in append-only batch documents
({first_ts, last_ts, expire_at, count, entries: [...]}). Each entry has:

    ts, expire_at, user_id, ip, forwarded_for, method, path, route,
    feature, status, duration_ms, ai_calls, ai_ms, ai_errors

Batches are deleted by purge_expired() once their newest entry is older than
ACCESS_LOG_RETENTION_DAYS (91 days ≥ the 90-day minimum). Writing never slows
down or breaks a request.
"""
import asyncio
import logging
import re
import threading
import time
from contextlib import asynccontextmanager
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


# ── Batched writing ─────────────────────────────────────────────────────────
# One Firestore document per batch of requests (not one per request), so the
# free Spark quota (20,000 writes / 50,000 reads per day) is enough. Each batch
# document is written once and never changed (append-only).

FLUSH_SIZE = 100               # write when this many entries are waiting …
FLUSH_INTERVAL_S = 600         # … or every 10 minutes
PURGE_EVERY_S = 6 * 3600       # delete expired logs/sessions every 6 hours
PURGE_LIMIT = 300              # max documents deleted per collection per run

_buffer: list[dict] = []
_buffer_lock = threading.Lock()
_db_ref = None


def _enqueue(db, entry: dict) -> None:
    global _db_ref
    with _buffer_lock:
        _buffer.append(entry)
        _db_ref = db
        full = len(_buffer) >= FLUSH_SIZE
    if full:
        try:
            asyncio.get_running_loop().run_in_executor(None, flush)
        except RuntimeError:          # no running loop (e.g. called from a thread)
            flush()


def flush(db=None) -> int:
    """Write all waiting entries as one batch document. Returns how many were written."""
    with _buffer_lock:
        batch = list(_buffer)
        _buffer.clear()
        db = db or _db_ref
    if not batch or db is None:
        return 0
    stamps = [e["ts"] for e in batch]
    doc = {
        "first_ts": min(stamps),
        "last_ts": max(stamps),
        "expire_at": max(stamps) + timedelta(days=config.ACCESS_LOG_RETENTION_DAYS),
        "count": len(batch),
        "entries": batch,
    }
    try:
        db.collection(ACCESS_LOG).document().set(doc)
        return len(batch)
    except Exception as e:  # noqa: BLE001 — logging must never break the app
        log.warning("access_log.write_failed error=%s entries=%d", type(e).__name__, len(batch))
        with _buffer_lock:            # keep them for the next try (bounded)
            if len(_buffer) < 5 * FLUSH_SIZE:
                _buffer[:0] = batch
        return 0


def purge_expired(db, now: datetime | None = None) -> int:
    """Delete access-log batches and admin sessions whose expire_at has passed.
    Replaces Firestore TTL, which needs billing enabled."""
    from app.collections import ADMIN_SESSIONS
    from google.cloud import firestore as fs
    now = now or datetime.now(timezone.utc)
    deleted = 0
    for name in (ACCESS_LOG, ADMIN_SESSIONS):
        try:
            docs = (db.collection(name)
                    .where(filter=fs.FieldFilter("expire_at", "<", now))
                    .limit(PURGE_LIMIT).get())
            for d in docs:
                d.reference.delete()
                deleted += 1
        except Exception as e:  # noqa: BLE001
            log.warning("purge.failed collection=%s error=%s", name, type(e).__name__)
    if deleted:
        log.info("purge.ok deleted=%d", deleted)
    return deleted


def _db_for_app(app):
    from app.database import get_db
    return app.dependency_overrides.get(get_db, get_db)()


async def _background(app) -> None:
    last_purge = 0.0
    while True:
        await asyncio.sleep(FLUSH_INTERVAL_S)
        await asyncio.to_thread(flush)
        if time.monotonic() - last_purge >= PURGE_EVERY_S:
            last_purge = time.monotonic()
            try:
                await asyncio.to_thread(purge_expired, _db_for_app(app))
            except Exception as e:  # noqa: BLE001
                log.warning("purge.skipped error=%s", type(e).__name__)


@asynccontextmanager
async def lifespan(app):
    task = asyncio.create_task(_background(app)) if config.ACCESS_LOG_ENABLED else None
    try:
        yield
    finally:
        if task:
            task.cancel()
        # Don't lose waiting entries when the server stops — but never hang shutdown on it.
        try:
            await asyncio.wait_for(asyncio.to_thread(flush), timeout=10)
        except (asyncio.TimeoutError, Exception) as e:  # noqa: BLE001
            log.warning("access_log.final_flush_failed error=%s", type(e).__name__)


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
            _enqueue(_db_for(request), entry)
        except Exception as e:  # noqa: BLE001
            log.warning("access_log.build_failed error=%s", type(e).__name__)
