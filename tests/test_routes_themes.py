"""Tests for /projects/{id}/themes/* routes."""
from unittest.mock import patch

from tests.conftest import FAKE_EVIDENCE, FAKE_PROJECT, FAKE_SOURCE, FAKE_THEME


class TestThemesList:
    def test_get_themes_returns_200(self, client):
        with (
            patch("app.routers.themes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.themes.themes_service.list_themes", return_value=[]),
        ):
            resp = client.get("/projects/p1/themes")
        assert resp.status_code == 200

    def test_get_themes_shows_theme_name(self, client):
        with (
            patch("app.routers.themes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.themes.themes_service.list_themes", return_value=[FAKE_THEME]),
        ):
            resp = client.get("/projects/p1/themes")
        assert b"Test Theme" in resp.content

    def test_wrong_user_redirects(self, client):
        from app.models import Project
        from datetime import datetime, timezone
        other = Project(
            id="p2", user_id="other", name="Other",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        with patch("app.routers.themes.project_service.get_project", return_value=other):
            resp = client.get("/projects/p2/themes")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestCreateTheme:
    def test_create_theme_redirects(self, client):
        with (
            patch("app.routers.themes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.themes.themes_service.create_theme", return_value=FAKE_THEME),
        ):
            resp = client.post(
                "/projects/p1/themes",
                data={"name": "New Theme", "description": "desc"},
            )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/themes"

    def test_create_theme_empty_name_no_action(self, client):
        with (
            patch("app.routers.themes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.themes.themes_service.create_theme") as mock_create,
        ):
            resp = client.post("/projects/p1/themes", data={"name": "  "})
        assert resp.status_code == 303
        mock_create.assert_not_called()


class TestThemeDetail:
    def test_get_theme_detail_returns_200(self, client):
        with (
            patch("app.routers.themes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.themes.themes_service.get_theme", return_value=FAKE_THEME),
            patch("app.routers.themes.evidence_service.list_evidence_for_project", return_value=[]),
            patch("app.routers.themes.library_service.list_resources", return_value=[]),
        ):
            resp = client.get("/projects/p1/themes/t1")
        assert resp.status_code == 200
        assert b"Test Theme" in resp.content

    def test_theme_not_found_redirects(self, client):
        with (
            patch("app.routers.themes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.themes.themes_service.get_theme", return_value=None),
        ):
            resp = client.get("/projects/p1/themes/missing")
        assert resp.status_code == 303
        assert "/themes" in resp.headers["location"]


class TestEditTheme:
    def test_edit_theme_redirects(self, client):
        with (
            patch("app.routers.themes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.themes.themes_service.update_theme") as mock_update,
        ):
            resp = client.post(
                "/projects/p1/themes/t1/edit",
                data={"name": "Updated Theme", "description": "new desc"},
            )
        assert resp.status_code == 303
        assert "/themes/t1" in resp.headers["location"]
        mock_update.assert_called_once()


class TestLinkUnlinkEvidence:
    def test_link_evidence_redirects(self, client):
        with (
            patch("app.routers.themes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.themes.themes_service.link_evidence") as mock_link,
        ):
            resp = client.post(
                "/projects/p1/themes/t1/link",
                data={"evidence_id": "e1"},
            )
        assert resp.status_code == 303
        assert "/themes/t1" in resp.headers["location"]
        mock_link.assert_called_once()

    def test_unlink_evidence_redirects(self, client):
        with (
            patch("app.routers.themes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.themes.themes_service.unlink_evidence") as mock_unlink,
        ):
            resp = client.post(
                "/projects/p1/themes/t1/unlink",
                data={"evidence_id": "e1"},
            )
        assert resp.status_code == 303
        assert "/themes/t1" in resp.headers["location"]
        mock_unlink.assert_called_once()


class TestDeleteTheme:
    def test_delete_theme_redirects(self, client):
        with (
            patch("app.routers.themes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.themes.themes_service.delete_theme") as mock_del,
        ):
            resp = client.post("/projects/p1/themes/t1/delete")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/themes"
        mock_del.assert_called_once()
