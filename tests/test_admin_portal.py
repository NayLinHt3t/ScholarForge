"""Admin portal: separate login, session, rate limiting, dashboard access."""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import bcrypt
import pytest
from fastapi.testclient import TestClient

from app import config
from app.database import get_db
from app.main import app
from app.services import admin_auth

PASSWORD = "correct horse battery"
HASH = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt(rounds=4)).decode()


@pytest.fixture
def admin_cfg():
    with patch.object(config, "ADMIN_USERNAME", "boss"), patch.object(config, "ADMIN_PASSWORD_HASH", HASH):
        admin_auth._failures.clear()
        yield
        admin_auth._failures.clear()


@pytest.fixture
def web(mock_db):
    """Client with NO student login — the admin portal must not depend on it."""
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app, follow_redirects=False)
    app.dependency_overrides.clear()


def _valid_session():
    return {"username": "boss", "expires_at": datetime.now(timezone.utc) + timedelta(hours=1)}


# ── credentials ─────────────────────────────────────────────────────────────

def test_verify_credentials(admin_cfg):
    assert admin_auth.verify_credentials("boss", PASSWORD)
    assert admin_auth.verify_credentials("BOSS ", PASSWORD)          # username not case-sensitive
    assert not admin_auth.verify_credentials("boss", "wrong")
    assert not admin_auth.verify_credentials("other", PASSWORD)


def test_not_configured_never_logs_in():
    with patch.object(config, "ADMIN_USERNAME", ""), patch.object(config, "ADMIN_PASSWORD_HASH", ""):
        assert not admin_auth.is_configured()
        assert not admin_auth.verify_credentials("", "")


def test_session_token_is_stored_hashed(admin_cfg, mock_db):
    token = admin_auth.create_session(mock_db, "boss", "1.2.3.4")
    doc_id = mock_db.collection.return_value.document.call_args.args[0]
    assert token not in doc_id and len(doc_id) == 64                 # sha256 hex, not the token
    data = mock_db.collection.return_value.document.return_value.set.call_args.args[0]
    assert data["expire_at"] - data["created_at"] == timedelta(hours=config.ADMIN_SESSION_HOURS)


def test_expired_session_rejected(admin_cfg, mock_db):
    doc = MagicMock(exists=True)
    doc.to_dict.return_value = {"username": "boss", "expires_at": datetime.now(timezone.utc) - timedelta(seconds=1)}
    mock_db.collection.return_value.document.return_value.get.return_value = doc
    assert admin_auth.get_session(mock_db, "tok") is None


def test_session_for_renamed_admin_rejected(admin_cfg, mock_db):
    doc = MagicMock(exists=True)
    doc.to_dict.return_value = {"username": "old-admin", "expires_at": datetime.now(timezone.utc) + timedelta(hours=1)}
    mock_db.collection.return_value.document.return_value.get.return_value = doc
    assert admin_auth.get_session(mock_db, "tok") is None


# ── pages ───────────────────────────────────────────────────────────────────

def test_dashboard_requires_admin_login(admin_cfg, web):
    with patch("app.routers.admin.admin_auth.get_session", return_value=None):
        resp = web.get("/admin")
    assert resp.status_code == 303 and resp.headers["location"] == "/admin/login"


def test_student_login_does_not_open_admin(admin_cfg, client):
    """A signed-in student (client fixture) still gets sent to the admin login."""
    with patch("app.routers.admin.admin_auth.get_session", return_value=None):
        resp = client.get("/admin")
    assert resp.headers["location"] == "/admin/login"


def test_login_page_renders(admin_cfg, web):
    resp = web.get("/admin/login")
    assert resp.status_code == 200 and b"Admin sign in" in resp.content
    assert b"noindex" in resp.content


def test_login_page_explains_setup_when_not_configured(web):
    with patch.object(config, "ADMIN_USERNAME", ""), patch.object(config, "ADMIN_PASSWORD_HASH", ""):
        resp = web.get("/admin/login")
    assert b"isn't set up yet" in resp.content


def test_successful_login_sets_separate_cookie(admin_cfg, web):
    with patch("app.routers.admin.admin_auth.create_session", return_value="tok123"), \
         patch("app.routers.admin.admin_auth.audit") as audit:
        resp = web.post("/admin/login", data={"username": "boss", "password": PASSWORD})
    assert resp.status_code == 303 and resp.headers["location"] == "/admin"
    cookie = resp.headers["set-cookie"]
    assert "sf_admin=tok123" in cookie and "Path=/admin" in cookie
    assert "HttpOnly" in cookie and "SameSite=strict" in cookie
    assert audit.call_args.args[1] == "admin_login"


def test_wrong_password(admin_cfg, web):
    with patch("app.routers.admin.admin_auth.audit") as audit:
        resp = web.post("/admin/login", data={"username": "boss", "password": "nope"})
    assert resp.status_code == 401 and b"Wrong username or password" in resp.content
    assert "set-cookie" not in resp.headers
    assert audit.call_args.args[1] == "admin_login_failed"


def test_lockout_after_five_failures(admin_cfg, web):
    with patch("app.routers.admin.admin_auth.audit"):
        for _ in range(admin_auth.MAX_FAILURES):
            web.post("/admin/login", data={"username": "boss", "password": "nope"})
        resp = web.post("/admin/login", data={"username": "boss", "password": PASSWORD})
    assert resp.status_code == 429
    assert "set-cookie" not in resp.headers           # even the right password is refused while locked


def test_dashboard_with_admin_session(admin_cfg, web):
    with (
        patch("app.routers.admin.admin_auth.get_session", return_value=_valid_session()),
        patch("app.routers.admin.usage_service.load", return_value=([], False)),
        patch("app.routers.admin.usage_service.count_collection", return_value=5),
    ):
        resp = web.get("/admin?days=30")
    assert resp.status_code == 200
    assert b"Usage dashboard" in resp.content and b"Signed in as boss" in resp.content
    assert b"5 accounts in total" in resp.content
    assert b"My Library" not in resp.content         # no student navigation in the portal


def test_logout_clears_session(admin_cfg, web):
    web.cookies.set("sf_admin", "tok", path="/admin")
    with patch("app.routers.admin.admin_auth.get_session", return_value=_valid_session()), \
         patch("app.routers.admin.admin_auth.delete_session") as delete, \
         patch("app.routers.admin.admin_auth.audit"):
        resp = web.post("/admin/logout")
    assert resp.headers["location"] == "/admin/login"
    delete.assert_called_once()


def test_admin_activity_not_counted_as_student_usage():
    from app.services import usage as usage_service
    now = datetime(2026, 11, 16, 5, tzinfo=timezone.utc)
    entries = [{"ts": now, "user_id": "admin:boss", "feature": "Home", "status": 200}]
    u = usage_service.summarize(entries, 7, now, "Asia/Bangkok")
    assert u.active_users == 0 and u.actions == 0


def test_password_tool_prints_hash(monkeypatch, capsys):
    from app.tools import admin_password
    answers = iter([PASSWORD, PASSWORD])
    monkeypatch.setattr(admin_password.getpass, "getpass", lambda prompt="": next(answers))
    assert admin_password.main() == 0
    out = capsys.readouterr().out
    line = next(l for l in out.splitlines() if l.startswith("ADMIN_PASSWORD_HASH="))
    assert bcrypt.checkpw(PASSWORD.encode(), line.split("'")[1].encode())


def test_password_tool_rejects_short(monkeypatch):
    from app.tools import admin_password
    monkeypatch.setattr(admin_password.getpass, "getpass", lambda prompt="": "short")
    assert admin_password.main() == 1


def test_dashboard_saves_waiting_log_entries_first(admin_cfg, web, mock_db):
    from app import monitoring
    monitoring._buffer.clear()
    monitoring._enqueue(mock_db, {"ts": datetime.now(timezone.utc), "user_id": "u1", "feature": "Home", "status": 200})
    with (
        patch("app.routers.admin.admin_auth.get_session", return_value=_valid_session()),
        patch("app.routers.admin.usage_service.load", return_value=([], False)),
        patch("app.routers.admin.usage_service.count_collection", return_value=1),
    ):
        resp = web.get("/admin")
    assert resp.status_code == 200
    assert not [e for e in monitoring._buffer if e.get("user_id") == "u1"]   # flushed before reading
    monitoring._buffer.clear()
