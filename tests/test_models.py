"""Tests for Pydantic model serialization and Firestore round-trips."""
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.models import Claim, Evidence, Note, Project, SavedResource, Theme, User
from app.models.outline_section import OutlineSection


def _make_doc(id_: str, data: dict):
    doc = MagicMock()
    doc.id = id_
    doc.exists = True
    doc.to_dict.return_value = data
    return doc


# ── Project ──────────────────────────────────────────────────────────────────

class TestProject:
    def test_to_firestore_excludes_id(self):
        p = Project(id="p1", user_id="u1", name="My Project")
        data = p.to_firestore()
        assert "id" not in data
        assert data["user_id"] == "u1"
        assert data["name"] == "My Project"

    def test_from_firestore_roundtrip(self):
        now = datetime.now(timezone.utc)
        doc = _make_doc("p1", {
            "user_id": "u1",
            "name": "My Project",
            "research_question": "RQ",
            "citation_style": "IEEE",
            "created_at": now,
            "updated_at": now,
        })
        p = Project.from_firestore(doc)
        assert p.id == "p1"
        assert p.name == "My Project"
        assert p.user_id == "u1"

    def test_from_firestore_backfills_research_question(self):
        now = datetime.now(timezone.utc)
        doc = _make_doc("p2", {
            "user_id": "u1",
            "name": "Old Project",
            "citation_style": "IEEE",
            "created_at": now,
            "updated_at": now,
        })
        p = Project.from_firestore(doc)
        assert p.research_question == ""

    def test_default_citation_style(self):
        p = Project(id="", user_id="u1", name="X")
        assert p.citation_style == "IEEE"


# ── SavedResource ─────────────────────────────────────────────────────────────

class TestSavedResource:
    def test_to_firestore_excludes_id(self):
        r = SavedResource(id="s1", project_id="p1", title="Paper", source="manual")
        data = r.to_firestore()
        assert "id" not in data
        assert data["title"] == "Paper"

    def test_from_firestore_backfills_workspace_fields(self):
        now = datetime.now(timezone.utc)
        doc = _make_doc("s1", {
            "project_id": "p1",
            "title": "Paper",
            "authors": [],
            "source": "manual",
            "added_at": now,
        })
        r = SavedResource.from_firestore(doc)
        assert r.source_type == "journal_article"
        assert r.read_status == "unread"
        assert r.source_note == ""
        assert r.access_status == "unknown"

    def test_from_firestore_preserves_existing_fields(self):
        now = datetime.now(timezone.utc)
        doc = _make_doc("s2", {
            "project_id": "p1",
            "title": "Book",
            "authors": ["Alice"],
            "source": "manual",
            "source_type": "book",
            "read_status": "done",
            "source_note": "good book",
            "access_status": "open_access",
            "added_at": now,
        })
        r = SavedResource.from_firestore(doc)
        assert r.source_type == "book"
        assert r.read_status == "done"
        assert r.access_status == "open_access"


# ── Evidence ──────────────────────────────────────────────────────────────────

class TestEvidence:
    def test_to_firestore_excludes_id(self):
        e = Evidence(
            id="e1", project_id="p1", source_id="s1",
            user_id="u1", quote="Some quote",
        )
        data = e.to_firestore()
        assert "id" not in data
        assert data["quote"] == "Some quote"

    def test_from_firestore_backfills_optional_fields(self):
        now = datetime.now(timezone.utc)
        doc = _make_doc("e1", {
            "project_id": "p1", "source_id": "s1",
            "user_id": "u1", "quote": "Q",
            "created_at": now,
        })
        e = Evidence.from_firestore(doc)
        assert e.page_reference == ""
        assert e.student_note == ""


# ── Note ──────────────────────────────────────────────────────────────────────

class TestNote:
    def test_to_firestore_excludes_id(self):
        n = Note(id="n1", project_id="p1", user_id="u1", body="Body")
        data = n.to_firestore()
        assert "id" not in data
        assert data["body"] == "Body"

    def test_from_firestore_backfills_title(self):
        now = datetime.now(timezone.utc)
        doc = _make_doc("n1", {
            "project_id": "p1", "user_id": "u1",
            "body": "Body", "created_at": now, "updated_at": now,
        })
        n = Note.from_firestore(doc)
        assert n.title == ""


# ── Theme ─────────────────────────────────────────────────────────────────────

class TestTheme:
    def test_to_firestore_excludes_id(self):
        t = Theme(id="t1", project_id="p1", user_id="u1", name="Theme A")
        data = t.to_firestore()
        assert "id" not in data
        assert data["name"] == "Theme A"

    def test_from_firestore_backfills_optional_fields(self):
        now = datetime.now(timezone.utc)
        doc = _make_doc("t1", {
            "project_id": "p1", "user_id": "u1",
            "name": "Theme A", "created_at": now,
        })
        t = Theme.from_firestore(doc)
        assert t.description == ""
        assert t.evidence_ids == []


# ── Claim ─────────────────────────────────────────────────────────────────────

class TestClaim:
    def test_to_firestore_excludes_id(self):
        c = Claim(id="c1", project_id="p1", user_id="u1", statement="Stmt")
        data = c.to_firestore()
        assert "id" not in data
        assert data["statement"] == "Stmt"

    def test_from_firestore_backfills_id_lists(self):
        now = datetime.now(timezone.utc)
        doc = _make_doc("c1", {
            "project_id": "p1", "user_id": "u1",
            "statement": "Stmt", "created_at": now,
        })
        c = Claim.from_firestore(doc)
        assert c.evidence_ids == []
        assert c.theme_ids == []


# ── OutlineSection ────────────────────────────────────────────────────────────

class TestOutlineSection:
    def test_to_firestore_excludes_id(self):
        s = OutlineSection(id="sec1", project_id="p1", user_id="u1", title="Intro")
        data = s.to_firestore()
        assert "id" not in data
        assert data["title"] == "Intro"

    def test_from_firestore_backfills_optional_fields(self):
        doc = _make_doc("sec1", {
            "project_id": "p1", "user_id": "u1",
            "title": "Intro", "order_index": 0,
        })
        s = OutlineSection.from_firestore(doc)
        assert s.writing_notes == ""
        assert s.claim_ids == []
        assert s.evidence_ids == []
