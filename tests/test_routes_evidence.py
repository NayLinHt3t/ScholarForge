"""Tests for /projects/{id}/evidence/* and /projects/{id}/sources/{sid}/evidence routes."""
from unittest.mock import patch

from tests.conftest import FAKE_EVIDENCE, FAKE_PROJECT, FAKE_SOURCE


class TestEvidenceList:
    def test_get_evidence_list_returns_200(self, client):
        with (
            patch("app.routers.evidence.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.evidence.evidence_service.list_evidence_for_project", return_value=[]),
            patch("app.routers.evidence.library_service.list_resources", return_value=[]),
        ):
            resp = client.get("/projects/p1/evidence")
        assert resp.status_code == 200

    def test_get_evidence_shows_quote(self, client):
        with (
            patch("app.routers.evidence.project_service.get_project", return_value=FAKE_PROJECT),
            patch(
                "app.routers.evidence.evidence_service.list_evidence_for_project",
                return_value=[FAKE_EVIDENCE],
            ),
            patch("app.routers.evidence.library_service.list_resources", return_value=[FAKE_SOURCE]),
        ):
            resp = client.get("/projects/p1/evidence")
        assert b"Important finding here" in resp.content

    def test_wrong_user_redirects(self, client):
        from app.models import Project
        from datetime import datetime, timezone
        other = Project(
            id="p2", user_id="other", name="Other",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        with patch("app.routers.evidence.project_service.get_project", return_value=other):
            resp = client.get("/projects/p2/evidence")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestAddEvidence:
    def test_add_evidence_redirects_to_source(self, client):
        with (
            patch("app.routers.evidence.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.evidence.evidence_service.add_evidence", return_value=FAKE_EVIDENCE),
        ):
            resp = client.post(
                "/projects/p1/sources/s1/evidence",
                data={"quote": "Key finding", "page_reference": "p.42"},
            )
        assert resp.status_code == 303
        assert "/sources/s1" in resp.headers["location"]

    def test_add_evidence_empty_quote_no_action(self, client):
        with (
            patch("app.routers.evidence.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.evidence.evidence_service.add_evidence") as mock_add,
        ):
            resp = client.post(
                "/projects/p1/sources/s1/evidence",
                data={"quote": "   "},
            )
        assert resp.status_code == 303
        mock_add.assert_not_called()


class TestEditEvidence:
    def test_edit_evidence_redirects_to_source(self, client):
        with (
            patch("app.routers.evidence.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.evidence.evidence_service.update_evidence") as mock_upd,
        ):
            resp = client.post(
                "/projects/p1/evidence/e1/edit",
                data={"quote": "Updated quote", "source_id": "s1"},
            )
        assert resp.status_code == 303
        assert "/sources/s1" in resp.headers["location"]
        mock_upd.assert_called_once()

    def test_edit_evidence_without_source_id_redirects_to_evidence(self, client):
        with (
            patch("app.routers.evidence.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.evidence.evidence_service.update_evidence"),
        ):
            resp = client.post(
                "/projects/p1/evidence/e1/edit",
                data={"quote": "Updated quote"},
            )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/evidence"


class TestDeleteEvidence:
    def test_delete_evidence_redirects_to_evidence_list(self, client):
        with (
            patch("app.routers.evidence.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.evidence.evidence_service.delete_evidence") as mock_del,
        ):
            resp = client.post("/projects/p1/evidence/e1/delete", data={})
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/evidence"
        mock_del.assert_called_once()

    def test_delete_evidence_with_source_id_redirects_to_source(self, client):
        with (
            patch("app.routers.evidence.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.evidence.evidence_service.delete_evidence"),
        ):
            resp = client.post(
                "/projects/p1/evidence/e1/delete",
                data={"source_id": "s1"},
            )
        assert resp.status_code == 303
        assert "/sources/s1" in resp.headers["location"]
