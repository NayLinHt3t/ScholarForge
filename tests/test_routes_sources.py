"""Tests for /projects/{id}/sources/* routes."""
from unittest.mock import patch

from app.exceptions import DuplicateResourceError
from tests.conftest import FAKE_EVIDENCE, FAKE_PROJECT, FAKE_SOURCE


class TestSourcesList:
    def test_get_sources_returns_200(self, client):
        with (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.sources.library_service.list_resources", return_value=[]),
            patch("app.routers.sources.evidence_service.count_for_source", return_value=0),
        ):
            resp = client.get("/projects/p1/sources")
        assert resp.status_code == 200

    def test_get_sources_shows_source_title(self, client):
        with (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.sources.library_service.list_resources", return_value=[FAKE_SOURCE]),
            patch("app.routers.sources.evidence_service.count_for_source", return_value=0),
        ):
            resp = client.get("/projects/p1/sources")
        assert b"Test Paper" in resp.content

    def test_wrong_user_redirects(self, client):
        from app.models import Project
        from datetime import datetime, timezone
        other = Project(
            id="p2", user_id="other", name="Other",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        with patch("app.routers.sources.project_service.get_project", return_value=other):
            resp = client.get("/projects/p2/sources")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestAddSource:
    def test_add_source_redirects(self, client):
        with (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.sources.library_service.save_resource", return_value=FAKE_SOURCE),
        ):
            resp = client.post(
                "/projects/p1/sources",
                data={"title": "New Paper", "authors_raw": "Alice, Bob", "year": "2023"},
            )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/sources"

    def test_add_source_empty_title_returns_400(self, client):
        with (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.sources.library_service.list_resources", return_value=[]),
            patch("app.routers.sources.evidence_service.count_for_source", return_value=0),
        ):
            resp = client.post(
                "/projects/p1/sources",
                data={"title": "   "},
            )
        assert resp.status_code == 400
        assert b"required" in resp.content.lower()

    def test_add_duplicate_source_still_redirects(self, client):
        with (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch(
                "app.routers.sources.library_service.save_resource",
                side_effect=DuplicateResourceError(),
            ),
        ):
            resp = client.post(
                "/projects/p1/sources",
                data={"title": "Duplicate Paper"},
            )
        assert resp.status_code == 303


class TestSourceDetail:
    def test_get_source_detail_returns_200(self, client):
        with (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.sources.library_service.get_resource", return_value=FAKE_SOURCE),
            patch("app.routers.sources.evidence_service.list_evidence_for_source", return_value=[]),
            patch("app.routers.sources.format_one", return_value="Citation text"),
        ):
            resp = client.get("/projects/p1/sources/s1")
        assert resp.status_code == 200
        assert b"Test Paper" in resp.content

    def test_source_not_found_redirects(self, client):
        with (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.sources.library_service.get_resource", return_value=None),
        ):
            resp = client.get("/projects/p1/sources/missing")
        assert resp.status_code == 303
        assert "/sources" in resp.headers["location"]


class TestUpdateSourceStatus:
    def test_update_read_status_redirects(self, client):
        with (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.sources.library_service.update_source") as mock_update,
        ):
            resp = client.post(
                "/projects/p1/sources/s1/status",
                data={"read_status": "done"},
            )
        assert resp.status_code == 303
        mock_update.assert_called_once()

    def test_update_source_note_redirects(self, client):
        with (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.sources.library_service.update_source") as mock_update,
        ):
            resp = client.post(
                "/projects/p1/sources/s1/note",
                data={"source_note": "A great paper"},
            )
        assert resp.status_code == 303
        mock_update.assert_called_once()


class TestDeleteSource:
    def test_delete_source_redirects(self, client):
        with (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch(
                "app.routers.sources.evidence_service.list_evidence_for_source",
                return_value=[FAKE_EVIDENCE],
            ),
            patch("app.routers.sources.evidence_service.delete_evidence") as mock_del_ev,
            patch("app.routers.sources.library_service.delete_resource") as mock_del,
        ):
            resp = client.post("/projects/p1/sources/s1/delete")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/sources"
        mock_del_ev.assert_called_once()
        mock_del.assert_called_once()
