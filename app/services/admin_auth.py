"""Admin portal authentication — completely separate from student accounts.

* One admin login: ADMIN_USERNAME + ADMIN_PASSWORD_HASH (bcrypt) from the environment
  (a Secret Manager secret when hosted). The plain password is never stored anywhere.
* Admin sessions live in the Firestore collection `admin_sessions`; only a SHA-256 of
  the session token is stored, so a database leak does not leak usable sessions.
* Failed logins are rate-limited per IP and every login/logout is written to audit_log.
"""
import hashlib
import hmac
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

import bcrypt
from google.cloud import firestore

from app import config
from app.collections import ADMIN_SESSIONS, AUDIT_LOG
from app.models import AuditLogEntry

ADMIN_COOKIE = "sf_admin"

# A real bcrypt hash used when the admin is not configured, so a login attempt
# takes the same time whether or not the username exists.
_DUMMY_HASH = bcrypt.hashpw(b"not-the-password", bcrypt.gensalt(rounds=4))

MAX_FAILURES = 5
FAILURE_WINDOW_S = 15 * 60
_failures: dict[str, deque] = defaultdict(deque)


def is_configured() -> bool:
    return bool(config.ADMIN_USERNAME and config.ADMIN_PASSWORD_HASH)


# ── rate limiting (per IP, per server instance) ─────────────────────────────

def _prune(ip: str, now: float) -> deque:
    q = _failures[ip]
    while q and now - q[0] > FAILURE_WINDOW_S:
        q.popleft()
    return q


def is_locked(ip: str, now: float | None = None) -> bool:
    return len(_prune(ip, now or time.time())) >= MAX_FAILURES


def record_failure(ip: str, now: float | None = None) -> None:
    now = now or time.time()
    _prune(ip, now).append(now)


def clear_failures(ip: str) -> None:
    _failures.pop(ip, None)


# ── credentials ─────────────────────────────────────────────────────────────

def verify_credentials(username: str, password: str) -> bool:
    expected_user = config.ADMIN_USERNAME or ""
    stored = (config.ADMIN_PASSWORD_HASH or "").encode() or _DUMMY_HASH
    try:
        password_ok = bcrypt.checkpw(password.encode(), stored)
    except ValueError:      # malformed hash in config
        password_ok = False
    user_ok = hmac.compare_digest(username.strip().lower().encode(), expected_user.strip().lower().encode())
    return is_configured() and user_ok and password_ok


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


# ── sessions ────────────────────────────────────────────────────────────────

def _key(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_session(db: firestore.Client, username: str, source_ip: str) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=config.ADMIN_SESSION_HOURS)
    db.collection(ADMIN_SESSIONS).document(_key(token)).set({
        "username": username,
        "created_at": now,
        "expires_at": expires,
        "expire_at": expires,          # Firestore TTL field — expired sessions are removed automatically
        "source_ip": source_ip,
    })
    return token


def get_session(db: firestore.Client, token: str | None) -> dict | None:
    if not token:
        return None
    doc = db.collection(ADMIN_SESSIONS).document(_key(token)).get()
    if not doc.exists:
        return None
    data = doc.to_dict() or {}
    expires = data.get("expires_at")
    if not isinstance(expires, datetime) or expires <= datetime.now(timezone.utc):
        return None
    if data.get("username", "").lower() != (config.ADMIN_USERNAME or "").lower():
        return None     # admin username was changed — old sessions stop working
    return data


def delete_session(db: firestore.Client, token: str | None) -> None:
    if token:
        db.collection(ADMIN_SESSIONS).document(_key(token)).delete()


def audit(db: firestore.Client, action: str, username: str | None, source_ip: str | None) -> None:
    ref = db.collection(AUDIT_LOG).document()
    ref.set(AuditLogEntry(
        id=ref.id, action=action, user_id=f"admin:{username}" if username else None,
        source_ip=source_ip, extra={"portal": "admin"},
    ).to_firestore())
