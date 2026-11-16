"""Free Firestore (Spark) friendly behaviour: batched access log, in-app purge, search fallback."""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app import config, monitoring
from app.database import get_db
from app.exceptions import AIUnavailableError
from app.main import app
from app.services import search as search_service
from app.services import usage as usage_service

NOW = datetime(2026, 11, 16, 5, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def empty_buffer():
    monitoring._buffer.clear()
    yield
    monitoring._buffer.clear()


def _entry(minutes_ago=0, **kw):
    e = {"ts": NOW - timedelta(minutes=minutes_ago), "user_id": "u1", "feature": "Home", "status": 200}
    e.update(kw)
    return e


def test_flush_writes_one_document_for_many_requests():
    db = MagicMock()
    for i in range(30):
        monitoring._enqueue(db, _entry(i))
    assert monitoring.flush() == 30
    db.collection.assert_called_with("access_log")
    doc = db.collection.return_value.document.return_value.set.call_args.args[0]
    assert doc["count"] == 30 and len(doc["entries"]) == 30
    assert doc["first_ts"] == NOW - timedelta(minutes=29) and doc["last_ts"] == NOW
    assert doc["expire_at"] == NOW + timedelta(days=config.ACCESS_LOG_RETENTION_DAYS)
    assert db.collection.return_value.document.return_value.set.call_count == 1
    assert monitoring.flush() == 0          # nothing left


def test_flush_failure_keeps_entries_for_next_try():
    db = MagicMock()
    db.collection.return_value.document.return_value.set.side_effect = RuntimeError("quota")
    monitoring._enqueue(db, _entry())
    assert monitoring.flush() == 0
    assert len(monitoring._buffer) == 1


def test_full_buffer_flushes_without_waiting():
    db = MagicMock()
    with patch.object(monitoring, "FLUSH_SIZE", 3):
        for i in range(3):
            monitoring._enqueue(db, _entry(i))      # no running loop here → flushes inline
    assert db.collection.return_value.document.return_value.set.call_count == 1


def test_purge_deletes_expired_logs_and_sessions():
    db = MagicMock()
    old = MagicMock()
    db.collection.return_value.where.return_value.limit.return_value.get.return_value = [old, old]
    assert monitoring.purge_expired(db, NOW) == 4           # 2 per collection
    names = [c.args[0] for c in db.collection.call_args_list]
    assert "access_log" in names and "admin_sessions" in names
    assert old.reference.delete.call_count == 4


def test_server_stop_flushes_waiting_entries(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    try:
        with patch("app.monitoring.flush") as flush_mock:
            with TestClient(app):           # runs startup + shutdown (lifespan)
                pass
        flush_mock.assert_called()
    finally:
        app.dependency_overrides.clear()


def test_usage_load_expands_batches():
    db = MagicMock()
    batch = MagicMock()
    batch.to_dict.return_value = {"entries": [_entry(5), _entry(60 * 24 * 40)]}   # 2nd is outside 7 days
    db.collection.return_value.where.return_value.limit.return_value.get.return_value = [batch]
    entries, truncated = usage_service.load(db, 7, now=NOW)
    assert len(entries) == 1 and truncated is False


# ── search keeps working without the ranking model ─────────────────────────

@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_search_falls_back_to_source_order_when_embeddings_unavailable():
    raw = [{"paperId": "a", "title": "Paper A", "abstract": "x", "authors": [], "year": 2024, "isOpenAccess": True}]
    with (
        patch("app.services.search.semantic_scholar.search", new=AsyncMock(return_value=raw)),
        patch("app.services.search.openalex.search", new=AsyncMock(return_value=[])),
        patch("app.services.search.ai.embed_many", new=AsyncMock(side_effect=AIUnavailableError())),
    ):
        resp = await search_service.run("remote work trust")
    assert resp.ranked is False and resp.low_confidence is False
    assert [r.title for r in resp.results] == ["Paper A"]


@pytest.mark.anyio
async def test_embed_provider_none_turns_ranking_off():
    from app.clients import ai
    with patch.object(config, "EMBED_PROVIDER", "none"):
        with pytest.raises(AIUnavailableError):
            await ai.embed_many(["x"])
