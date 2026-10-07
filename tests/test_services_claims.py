"""Unit tests for app.services.claims."""
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.services import claims as claims_service
from app.models import Claim


def _make_doc(id_: str, data: dict):
    doc = MagicMock()
    doc.id = id_
    doc.exists = True
    doc.to_dict.return_value = data
    return doc


def _claim_data():
    return {
        "project_id": "p1",
        "user_id": "u1",
        "statement": "Test claim",
        "evidence_ids": [],
        "theme_ids": [],
        "created_at": datetime.now(timezone.utc),
    }


class TestCreateClaim:
    def test_creates_and_returns_claim(self):
        db = MagicMock()
        ref = MagicMock()
        ref.id = "c1"
        db.collection.return_value.document.return_value.collection.return_value.document.return_value = ref

        result = claims_service.create_claim(db, "p1", "u1", "Test claim")

        assert result.statement == "Test claim"
        ref.set.assert_called_once()

    def test_strips_whitespace(self):
        db = MagicMock()
        ref = MagicMock()
        ref.id = "c1"
        db.collection.return_value.document.return_value.collection.return_value.document.return_value = ref

        result = claims_service.create_claim(db, "p1", "u1", "  Spaced  ")
        assert result.statement == "Spaced"


class TestListClaims:
    def test_returns_list_of_claims(self):
        db = MagicMock()
        doc = _make_doc("c1", _claim_data())
        db.collection.return_value.document.return_value.collection.return_value.order_by.return_value.get.return_value = [doc]

        result = claims_service.list_claims(db, "p1")
        assert len(result) == 1
        assert result[0].id == "c1"

    def test_empty_list(self):
        db = MagicMock()
        db.collection.return_value.document.return_value.collection.return_value.order_by.return_value.get.return_value = []

        result = claims_service.list_claims(db, "p1")
        assert result == []


class TestGetClaim:
    def test_returns_claim_when_exists(self):
        db = MagicMock()
        doc = _make_doc("c1", _claim_data())
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = doc

        result = claims_service.get_claim(db, "p1", "c1")
        assert result is not None
        assert result.id == "c1"

    def test_returns_none_when_not_exists(self):
        db = MagicMock()
        doc = MagicMock()
        doc.exists = False
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.get.return_value = doc

        result = claims_service.get_claim(db, "p1", "missing")
        assert result is None


class TestLinkEvidence:
    def test_link_calls_array_union(self):
        db = MagicMock()
        claims_service.link_evidence(db, "p1", "c1", "e1")
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.update.assert_called_once()

    def test_unlink_calls_array_remove(self):
        db = MagicMock()
        claims_service.unlink_evidence(db, "p1", "c1", "e1")
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.update.assert_called_once()


class TestDeleteClaim:
    def test_delete_calls_firestore(self):
        db = MagicMock()
        claims_service.delete_claim(db, "p1", "c1")
        db.collection.return_value.document.return_value.collection.return_value.document.return_value.delete.assert_called_once()
