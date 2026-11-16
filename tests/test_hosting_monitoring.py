"""Tests for hosted mode: Hugging Face AI provider, access log, admin usage dashboard."""
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from app import config, monitoring
from app.clients import ai, huggingface
from app.exceptions import AIUnavailableError
from app.services import usage as usage_service
from tests.conftest import FAKE_USER

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


# ── Hugging Face client ─────────────────────────────────────────────────────

class _FakeResp:
    def __init__(self, status, data):
        self.status_code, self._data = status, data
        self.text = str(data)

    def json(self):
        return self._data


class _FakeClient:
    """Stands in for httpx.AsyncClient; records the last request."""
    last = {}

    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def post(self, url, json=None, headers=None):
        _FakeClient.last = {"url": url, "json": json, "headers": headers}
        return self.response


def _hf(response):
    return patch("app.clients.huggingface.httpx.AsyncClient", lambda **kw: _FakeClient(response))


@pytest.fixture
def hf_on():
    with patch.object(config, "AI_PROVIDER", "huggingface"), patch.object(config, "HF_TOKEN", "hf_test"):
        yield


async def test_hf_generate_uses_chat_completions(hf_on):
    resp = _FakeResp(200, {"choices": [{"message": {"content": "Hello"}}]})
    with _hf(resp):
        assert await huggingface.generate("Hi") == "Hello"
    assert _FakeClient.last["url"].endswith("/v1/chat/completions")
    assert _FakeClient.last["json"]["model"] == config.HF_CHAT_MODEL
    assert _FakeClient.last["headers"]["Authorization"] == "Bearer hf_test"


async def test_hf_embeddings_batched_in_one_call(hf_on):
    resp = _FakeResp(200, [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])
    with _hf(resp):
        out = await huggingface.embed_many(["a", "b", "c"])
    assert out == [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
    assert _FakeClient.last["json"]["inputs"] == ["a", "b", "c"]
    assert "/pipeline/feature-extraction" in _FakeClient.last["url"]


async def test_hf_token_level_vectors_are_mean_pooled(hf_on):
    resp = _FakeResp(200, [[[1.0, 3.0], [3.0, 5.0]]])
    with _hf(resp):
        assert await huggingface.embed_many(["x"]) == [[2.0, 4.0]]


async def test_hf_http_error_becomes_ai_unavailable(hf_on):
    with _hf(_FakeResp(402, {"error": "no credits"})):
        with pytest.raises(AIUnavailableError):
            await huggingface.generate("Hi")


async def test_hf_without_token_is_not_alive():
    with patch.object(config, "HF_TOKEN", ""):
        assert await huggingface.is_alive() is False
        with pytest.raises(AIUnavailableError):
            await huggingface.generate("Hi")


async def test_facade_routes_to_provider_and_tracks_time(hf_on):
    usage = ai.start_tracking()
    with _hf(_FakeResp(200, {"choices": [{"message": {"content": "ok"}}]})):
        assert await ai.generate("p") == "ok"
    assert usage["calls"] == 1 and usage["errors"] == 0
    assert ai.provider() == "huggingface" and not ai.runs_locally()
    assert "try again in a minute" in ai.unavailable_message()


async def test_facade_counts_failures(hf_on):
    usage = ai.start_tracking()
    with _hf(_FakeResp(500, {})):
        with pytest.raises(AIUnavailableError):
            await ai.generate("p")
    assert usage["errors"] == 1


def test_local_provider_message_mentions_ollama():
    with patch.object(config, "AI_PROVIDER", "ollama"):
        assert ai.runs_locally()
        assert "ollama serve" in ai.unavailable_message()


# ── Access log ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize("method,route,q,expected", [
    ("GET", "/projects", False, "Home"),
    ("GET", "/projects/{project_id}/search", False, "Find papers"),
    ("GET", "/projects/{project_id}/search", True, "Search papers"),
    ("POST", "/projects/{project_id}/sources/{source_id}/ask", False, "Ask AI about a paper"),
    ("POST", "/projects/{project_id}/sources/{source_id}/save-note", False, "Save AI answer as note"),
    ("GET", "/projects/{project_id}/outline", False, "Outline"),
    ("POST", "/auth/login", False, "Sign in"),
    ("GET", "/auth/login", False, None),
    (None, None, False, None),
])
def test_feature_labels(method, route, q, expected):
    assert monitoring.feature_for(method, route, q) == expected


def _wait_for(mock, timeout=2.0):
    end = time.time() + timeout
    while not mock.called and time.time() < end:
        time.sleep(0.01)


def test_middleware_writes_one_entry_per_request(client, mock_db):
    writer = MagicMock()
    with (
        patch("app.monitoring._write", writer),
        patch("app.routers.projects.project_service.list_projects", return_value=[]),
    ):
        resp = client.get("/projects", headers={"x-forwarded-for": "203.0.113.7, 10.0.0.1"})
        _wait_for(writer)
    assert resp.status_code == 200
    db, entry = writer.call_args.args
    assert db is mock_db                       # uses the same DB as the app
    assert entry["route"] == "/projects" and entry["feature"] == "Home"
    assert entry["status"] == 200 and entry["method"] == "GET"
    assert entry["ip"] == "203.0.113.7"
    assert entry["expire_at"] - entry["ts"] >= timedelta(days=90)


def test_static_files_are_not_logged(client):
    writer = MagicMock()
    with patch("app.monitoring._write", writer):
        client.get("/static/css/app.css")
        time.sleep(0.05)
    writer.assert_not_called()


def test_logging_can_be_disabled(client):
    writer = MagicMock()
    with patch.object(config, "ACCESS_LOG_ENABLED", False), patch("app.monitoring._write", writer), \
         patch("app.routers.projects.project_service.list_projects", return_value=[]):
        client.get("/projects")
        time.sleep(0.05)
    writer.assert_not_called()


def test_current_user_is_recorded_on_request_state():
    from app.dependencies import get_current_user
    request = MagicMock()
    request.cookies = {"sf_session": "tok"}
    request.state = type("S", (), {})()
    with (
        patch("app.dependencies.auth_service.get_session", return_value=MagicMock(user_id="u1")),
        patch("app.dependencies.auth_service.get_user_by_id", return_value=FAKE_USER),
    ):
        assert get_current_user(request, MagicMock()) == FAKE_USER
    assert request.state.user_id == "u1"


# ── Usage summary ───────────────────────────────────────────────────────────

NOW = datetime(2026, 11, 16, 5, 0, tzinfo=timezone.utc)   # 12:00 in Bangkok


def _e(hours_ago, user="u1", feature="Read paper", status=200, ai_calls=0, ai_ms=0, ai_errors=0, method="GET"):
    return {"ts": NOW - timedelta(hours=hours_ago), "user_id": user, "feature": feature, "status": status,
            "ai_calls": ai_calls, "ai_ms": ai_ms, "ai_errors": ai_errors, "method": method, "route": "/x"}


def test_summarize_counts_users_hours_features_and_ai():
    entries = [
        _e(1, "u1"), _e(2, "u2", "Ask AI about a paper", ai_calls=1, ai_ms=2000),
        _e(26, "u1", "Search papers", ai_calls=1, ai_ms=4000),
        _e(3, "unauthenticated", "Sign up", status=303, method="POST"),
        _e(4, "u3", None, status=500),
        _e(24 * 20, "u9"),                                  # outside the 7-day window
    ]
    u = usage_service.summarize(entries, 7, NOW, "Asia/Bangkok")
    assert u.active_users == 3                               # u1, u2, u3
    assert u.active_today == 3
    assert u.actions == 4 and u.signups == 1
    assert u.hourly[11] == 1                                 # 1h before 12:00 Bangkok
    assert {f.label: f.uses for f in u.features}["Read paper"] == 1
    assert u.ai_calls == 2 and u.ai_median_ms == 3000
    assert len(u.errors) == 1 and u.errors[0]["status"] == 500
    assert len(u.daily) == 7 and u.daily[-1].users == 3


def test_summarize_empty():
    u = usage_service.summarize([], 30, NOW, "Asia/Bangkok")
    assert u.active_users == 0 and u.busiest_hour is None and len(u.daily) == 30


# ── Admin dashboard access ─────────────────────────────────────────────────

def test_admin_hidden_from_normal_users(client):
    with patch.object(config, "ADMIN_EMAILS", frozenset()):
        resp = client.get("/admin")
    assert resp.status_code == 404


def test_admin_dashboard_renders_for_admin(client):
    with (
        patch.object(config, "ADMIN_EMAILS", frozenset({"test@example.com"})),
        patch("app.routers.admin.usage_service.load", return_value=([_e(1), _e(2, "u2", "Ask AI about a paper", ai_calls=1, ai_ms=1500)], False)),
        patch("app.routers.admin.usage_service.count_collection", return_value=12),
    ):
        resp = client.get("/admin?days=30")
    assert resp.status_code == 200
    assert b"Active users per day" in resp.content
    assert b"Ask AI about a paper" in resp.content
    assert b"12 accounts in total" in resp.content


def test_settings_links_admin_only_for_admins(client):
    with patch("app.routers.views.ai.is_alive", new=MagicMock(return_value=_coro(True))), \
         patch.object(config, "ADMIN_EMAILS", frozenset({"test@example.com"})):
        assert b'href="/admin"' in client.get("/settings").content
    with patch("app.routers.views.ai.is_alive", new=MagicMock(return_value=_coro(True))), \
         patch.object(config, "ADMIN_EMAILS", frozenset()):
        assert b'href="/admin"' not in client.get("/settings").content


async def _coro_impl(v):
    return v


def _coro(v):
    return _coro_impl(v)
