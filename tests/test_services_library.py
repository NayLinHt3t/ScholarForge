"""Unit tests for app.services.library."""
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.exceptions import DuplicateResourceError
from app.services import library as library_service
from app.models import SavedResource


def _make_doc(id_: str, data: dict):
    doc = MagicMock()
    doc.id = id_
    doc.exists = True
    doc.to_dict.return_value = data
    return doc


def _resource_data(**overrides):
    now = datetime.now(timezone.utc)
    base = {
        "project_id": "p1",
        "title": "Test Paper",
        "authors": ["Alice"],
        "year": 2023,
        "venue": None,
        "doi": None,
        "arxiv_id": None,
        "url": None,
        "abstract": None,
        "source": "manual",
        "embedding": None,
        "source_type": "journal_article",
        "read_status": "unread",
        "source_note": "",
        "access_status": "unknown",
        "added_at": now,
    }
    return {**base, **overrides}


class TestSaveResource:
    def test_saves_and_returns_resource(self):
        db = MagicMock()
        ref = MagicMock()
        ref.id = "s1"
        saved_ref = db.collection.return_value.document.return_value.collection.return_value
        saved_ref.where.return_value.limit.return_value.get.return_value = []
        saved_ref.document.return_value = ref

        result = library_service.save_resource(
            db, "p1", "Paper", ["Alice"], 2023,
            None, "10.1234/test", None, None, None, "manual", None,
        )
        assert result.title == "Paper"
        ref.set.assert_called_once()

    def test_raises_duplicate_on_same_doi(self):
        db = MagicMock()
        saved_ref = db.collection.return_value.document.return_value.collection.return_value
        existing = MagicMock()
        saved_ref.where.return_value.limit.return_value.get.return_value = [existing]

        with pytest.raises(DuplicateResourceError):
            library_service.save_resource(
                db, "p1", "Paper", [], None,
                None, "10.1234/dup", None, None, None, "manual", None,
            )

    def test_raises_duplicate_on_same_arxiv_id(self):
        db = MagicMock()
        saved_ref = db.collection.return_value.document.return_value.collection.return_value
        existing = MagicMock()
        saved_ref.where.return_value.limit.return_value.get.return_value = [existing]

        with pytest.raises(DuplicateResourceError):
            library_service.save_resource(
                db, "p1", "Paper", [], None,
                None, None, "2301.12345", None, None, "manual", None,
            )


class TestGetResource:
    def test_returns_resource_when_exists(self):
        db = MagicMock()
        doc = _make_doc("s1", _resource_data())
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = doc

        result = library_service.get_resource(db, "p1", "s1")
        assert result is not None
        assert result.id == "s1"

    def test_returns_none_when_not_exists(self):
        db = MagicMock()
        doc = MagicMock()
        doc.exists = False
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = doc

        result = library_service.get_resource(db, "p1", "missing")
        assert result is None


class TestListResources:
    def test_returns_sorted_by_added_at(self):
        db = MagicMock()
        now = datetime.now(timezone.utc)
        older = datetime(2025, 1, 1, tzinfo=timezone.utc)
        doc1 = _make_doc("s1", _resource_data(added_at=now))
        doc2 = _make_doc("s2", _resource_data(added_at=older))
        db.collection.return_value.document.return_value.collection.return_value.get.return_value = [doc2, doc1]

        result = library_service.list_resources(db, "p1")
        assert len(result) == 2
        assert result[0].id == "s1"  # newer first


class TestDeleteResource:
    def test_calls_firestore_delete(self):
        db = MagicMock()
        library_service.delete_resource(db, "p1", "s1")
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.delete.assert_called_once()


class TestUpdateSource:
    def test_updates_only_provided_fields(self):
        db = MagicMock()
        library_service.update_source(db, "p1", "s1", read_status="done")
        update_ref = db.collection.return_value.document.return_value.collection.return_value.document.return_value
        update_ref.update.assert_called_once()
        args = update_ref.update.call_args[0][0]
        assert args == {"read_status": "done"}

    def test_no_update_when_no_fields(self):
        db = MagicMock()
        library_service.update_source(db, "p1", "s1")
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.update.assert_not_called()
