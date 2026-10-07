"""Unit tests for app.services.projects."""
from datetime import datetime, timezone
from unittest.mock import MagicMock, call

import pytest

from app.services import projects as project_service
from app.models import Project


def _make_doc(id_: str, data: dict):
    doc = MagicMock()
    doc.id = id_
    doc.exists = True
    doc.to_dict.return_value = data
    return doc


def _project_data(user_id="u1", name="My Project"):
    now = datetime.now(timezone.utc)
    return {
        "user_id": user_id,
        "name": name,
        "research_question": "",
        "citation_style": "IEEE",
        "created_at": now,
        "updated_at": now,
    }


class TestCreateProject:
    def test_creates_document_and_returns_project(self):
        db = MagicMock()
        doc_ref = MagicMock()
        doc_ref.id = "new_id"
        db.collection.return_value.document.return_value = doc_ref

        result = project_service.create_project(db, "u1", "My Project")

        assert result.name == "My Project"
        assert result.user_id == "u1"
        doc_ref.set.assert_called_once()

    def test_strips_whitespace_from_name(self):
        db = MagicMock()
        doc_ref = MagicMock()
        doc_ref.id = "id1"
        db.collection.return_value.document.return_value = doc_ref

        result = project_service.create_project(db, "u1", "  Spaces  ")
        assert result.name == "Spaces"


class TestListProjects:
    def test_returns_sorted_projects(self):
        db = MagicMock()
        now = datetime.now(timezone.utc)
        earlier = datetime(2025, 1, 1, tzinfo=timezone.utc)
        doc1 = _make_doc("p1", {**_project_data(), "created_at": now, "updated_at": now})
        doc2 = _make_doc("p2", {**_project_data(name="Older"), "created_at": earlier, "updated_at": earlier})
        db.collection.return_value.where.return_value.get.return_value = [doc1, doc2]

        projects = project_service.list_projects(db, "u1")

        assert len(projects) == 2
        assert projects[0].id == "p1"  # newer first

    def test_empty_list_when_no_projects(self):
        db = MagicMock()
        db.collection.return_value.where.return_value.get.return_value = []
        projects = project_service.list_projects(db, "u1")
        assert projects == []


class TestGetProject:
    def test_returns_project_when_exists(self):
        db = MagicMock()
        doc = _make_doc("p1", _project_data())
        db.collection.return_value.document.return_value.get.return_value = doc

        result = project_service.get_project(db, "p1")
        assert result is not None
        assert result.id == "p1"

    def test_returns_none_when_not_exists(self):
        db = MagicMock()
        doc = MagicMock()
        doc.exists = False
        db.collection.return_value.document.return_value.get.return_value = doc

        result = project_service.get_project(db, "missing")
        assert result is None


class TestUpdateProject:
    def test_calls_firestore_update(self):
        db = MagicMock()
        project_service.update_project(db, "p1", "New Name", "New RQ")
        db.collection.return_value.document.return_value.update.assert_called_once()
        args = db.collection.return_value.document.return_value.update.call_args[0][0]
        assert args["name"] == "New Name"
        assert args["research_question"] == "New RQ"


class TestDeleteProject:
    def test_deletes_subcollections_then_project(self):
        db = MagicMock()
        subcoll_ref = MagicMock()
        subdoc = MagicMock()
        subdoc.reference.delete = MagicMock()
        subcoll_ref.get.return_value = [subdoc]
        db.collection.return_value.document.return_value.collection.return_value = subcoll_ref

        project_service.delete_project(db, "p1")

        db.collection.return_value.document.return_value.delete.assert_called_once()
