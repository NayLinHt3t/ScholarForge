"""Tests for /projects/* routes."""
from unittest.mock import patch

import pytest

from tests.conftest import FAKE_PROJECT, FAKE_SOURCE, FAKE_USER


class TestProjectsList:
    def test_get_projects_returns_200(self, client):
        with patch("app.routers.projects.project_service.list_projects", return_value=[]):
            resp = client.get("/projects")
        assert resp.status_code == 200

    def test_get_projects_shows_project_name(self, client):
        with patch(
            "app.routers.projects.project_service.list_projects",
            return_value=[FAKE_PROJECT],
        ):
            resp = client.get("/projects")
        assert resp.status_code == 200
        assert b"Test Project" in resp.content


class TestCreateProject:
    def test_create_project_redirects(self, client):
        with patch(
            "app.routers.projects.project_service.create_project",
            return_value=FAKE_PROJECT,
        ):
            resp = client.post("/projects", data={"name": "My New Project"})
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"

    def test_create_project_empty_name_returns_400(self, client):
        with patch(
            "app.routers.projects.project_service.list_projects", return_value=[]
        ):
            resp = client.post("/projects", data={"name": "   "})
        assert resp.status_code == 400
        assert b"empty" in resp.content.lower()

    def test_create_project_with_research_question(self, client):
        with patch(
            "app.routers.projects.project_service.create_project",
            return_value=FAKE_PROJECT,
        ) as mock_create:
            client.post(
                "/projects",
                data={"name": "Proj", "research_question": "Why?"},
            )
        mock_create.assert_called_once()
        assert mock_create.call_args[1].get("research_question") == "Why?"


class TestProjectDetail:
    def test_get_detail_returns_200(self, client):
        counts = {"sources": 0, "evidence": 0, "notes": 0, "themes": 0, "claims": 0, "sections": 0}
        with (
            patch("app.routers.projects.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.projects.project_service.get_dashboard_counts", return_value=counts),
        ):
            resp = client.get("/projects/p1")
        assert resp.status_code == 200
        assert b"Test Project" in resp.content

    def test_get_detail_wrong_user_redirects(self, client):
        from app.models import Project
        from datetime import datetime, timezone
        other_project = Project(
            id="p2", user_id="other_user", name="Other",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        with patch("app.routers.projects.project_service.get_project", return_value=other_project):
            resp = client.get("/projects/p2")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"

    def test_get_detail_not_found_redirects(self, client):
        with patch("app.routers.projects.project_service.get_project", return_value=None):
            resp = client.get("/projects/missing")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestEditProject:
    def test_edit_project_redirects(self, client):
        with (
            patch("app.routers.projects.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.projects.project_service.update_project") as mock_update,
        ):
            resp = client.post(
                "/projects/p1/edit",
                data={"name": "Updated Name", "research_question": "New RQ"},
            )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1"
        mock_update.assert_called_once()

    def test_edit_project_wrong_user_redirects(self, client):
        from app.models import Project
        from datetime import datetime, timezone
        other = Project(
            id="p2", user_id="other", name="Other",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        with patch("app.routers.projects.project_service.get_project", return_value=other):
            resp = client.post("/projects/p2/edit", data={"name": "X"})
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestDeleteProject:
    def test_get_confirm_delete_page(self, client):
        with patch("app.routers.projects.project_service.get_project", return_value=FAKE_PROJECT):
            resp = client.get("/projects/p1/delete")
        assert resp.status_code == 200

    def test_post_delete_redirects(self, client):
        with (
            patch("app.routers.projects.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.projects.project_service.delete_project") as mock_del,
        ):
            resp = client.post("/projects/p1/delete")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"
        mock_del.assert_called_once()

    def test_post_delete_wrong_user_does_not_delete(self, client):
        from app.models import Project
        from datetime import datetime, timezone
        other = Project(
            id="p2", user_id="other", name="Other",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        with (
            patch("app.routers.projects.project_service.get_project", return_value=other),
            patch("app.routers.projects.project_service.delete_project") as mock_del,
        ):
            resp = client.post("/projects/p2/delete")
        assert resp.status_code == 303
        mock_del.assert_not_called()


class TestBibtexExport:
    def test_export_bib_returns_text_file(self, client):
        with (
            patch("app.routers.projects.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.projects.library_service.list_resources", return_value=[]),
            patch("app.routers.projects.build_bibtex_all", return_value="@article{fake}"),
        ):
            resp = client.get("/projects/p1/library/export.bib")
        assert resp.status_code == 200
        assert "attachment" in resp.headers.get("content-disposition", "")
