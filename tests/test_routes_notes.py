"""Tests for /projects/{id}/notes/* routes."""
from unittest.mock import patch

from tests.conftest import FAKE_NOTE, FAKE_PROJECT


class TestNotesList:
    def test_get_notes_returns_200(self, client):
        with (
            patch("app.routers.notes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.notes.notes_service.list_notes", return_value=[]),
        ):
            resp = client.get("/projects/p1/notes")
        assert resp.status_code == 200

    def test_get_notes_shows_note_title(self, client):
        with (
            patch("app.routers.notes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.notes.notes_service.list_notes", return_value=[FAKE_NOTE]),
        ):
            resp = client.get("/projects/p1/notes")
        assert b"My Note" in resp.content

    def test_wrong_user_redirects(self, client):
        from app.models import Project
        from datetime import datetime, timezone
        other = Project(
            id="p2", user_id="other", name="Other",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        with patch("app.routers.notes.project_service.get_project", return_value=other):
            resp = client.get("/projects/p2/notes")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestCreateNote:
    def test_create_note_redirects(self, client):
        with (
            patch("app.routers.notes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.notes.notes_service.create_note", return_value=FAKE_NOTE),
        ):
            resp = client.post(
                "/projects/p1/notes",
                data={"title": "My Note", "body": "Some content"},
            )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/notes"

    def test_create_note_empty_body_no_action(self, client):
        with (
            patch("app.routers.notes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.notes.notes_service.create_note") as mock_create,
        ):
            resp = client.post("/projects/p1/notes", data={"body": "  "})
        assert resp.status_code == 303
        mock_create.assert_not_called()

    def test_create_note_wrong_user_redirects(self, client):
        from app.models import Project
        from datetime import datetime, timezone
        other = Project(
            id="p2", user_id="other", name="Other",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        with patch("app.routers.notes.project_service.get_project", return_value=other):
            resp = client.post("/projects/p2/notes", data={"body": "content"})
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestEditNote:
    def test_edit_note_redirects(self, client):
        with (
            patch("app.routers.notes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.notes.notes_service.update_note") as mock_update,
        ):
            resp = client.post(
                "/projects/p1/notes/n1/edit",
                data={"title": "Updated", "body": "Updated body"},
            )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/notes"
        mock_update.assert_called_once()

    def test_edit_note_empty_body_no_update(self, client):
        with (
            patch("app.routers.notes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.notes.notes_service.update_note") as mock_update,
        ):
            resp = client.post(
                "/projects/p1/notes/n1/edit",
                data={"title": "X", "body": ""},
            )
        assert resp.status_code == 303
        mock_update.assert_not_called()


class TestDeleteNote:
    def test_delete_note_redirects(self, client):
        with (
            patch("app.routers.notes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.notes.notes_service.delete_note") as mock_del,
        ):
            resp = client.post("/projects/p1/notes/n1/delete")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/notes"
        mock_del.assert_called_once()
