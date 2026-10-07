"""Tests for /projects/{id}/claims/* routes."""
from unittest.mock import patch

from tests.conftest import FAKE_CLAIM, FAKE_EVIDENCE, FAKE_PROJECT, FAKE_SOURCE, FAKE_THEME


class TestClaimsList:
    def test_get_claims_returns_200(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.list_claims", return_value=[]),
        ):
            resp = client.get("/projects/p1/claims")
        assert resp.status_code == 200

    def test_get_claims_shows_statement(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.list_claims", return_value=[FAKE_CLAIM]),
        ):
            resp = client.get("/projects/p1/claims")
        assert b"AI will change research" in resp.content

    def test_wrong_user_redirects(self, client):
        from app.models import Project
        from datetime import datetime, timezone
        other = Project(
            id="p2", user_id="other", name="Other",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        with patch("app.routers.claims.project_service.get_project", return_value=other):
            resp = client.get("/projects/p2/claims")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestCreateClaim:
    def test_create_claim_redirects(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.create_claim", return_value=FAKE_CLAIM),
        ):
            resp = client.post(
                "/projects/p1/claims",
                data={"statement": "New claim statement"},
            )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/claims"

    def test_create_claim_empty_statement_no_action(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.create_claim") as mock_create,
        ):
            resp = client.post("/projects/p1/claims", data={"statement": "  "})
        assert resp.status_code == 303
        mock_create.assert_not_called()

    def test_create_claim_wrong_user_redirects(self, client):
        from app.models import Project
        from datetime import datetime, timezone
        other = Project(
            id="p2", user_id="other", name="Other",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        with patch("app.routers.claims.project_service.get_project", return_value=other):
            resp = client.post("/projects/p2/claims", data={"statement": "claim"})
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestClaimDetail:
    def test_get_claim_detail_returns_200(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.get_claim", return_value=FAKE_CLAIM),
            patch("app.routers.claims.evidence_service.list_evidence_for_project", return_value=[]),
            patch("app.routers.claims.library_service.list_resources", return_value=[]),
            patch("app.routers.claims.themes_service.list_themes", return_value=[]),
        ):
            resp = client.get("/projects/p1/claims/c1")
        assert resp.status_code == 200
        assert b"AI will change research" in resp.content

    def test_claim_not_found_redirects(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.get_claim", return_value=None),
        ):
            resp = client.get("/projects/p1/claims/missing")
        assert resp.status_code == 303
        assert "/claims" in resp.headers["location"]


class TestEditClaim:
    def test_edit_claim_redirects(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.update_claim_statement") as mock_upd,
        ):
            resp = client.post(
                "/projects/p1/claims/c1/edit",
                data={"statement": "Updated statement"},
            )
        assert resp.status_code == 303
        assert "/claims/c1" in resp.headers["location"]
        mock_upd.assert_called_once()


class TestLinkUnlinkEvidence:
    def test_link_evidence_redirects(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.link_evidence") as mock_link,
        ):
            resp = client.post(
                "/projects/p1/claims/c1/link-evidence",
                data={"evidence_id": "e1"},
            )
        assert resp.status_code == 303
        assert "/claims/c1" in resp.headers["location"]
        mock_link.assert_called_once()

    def test_unlink_evidence_redirects(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.unlink_evidence") as mock_unlink,
        ):
            resp = client.post(
                "/projects/p1/claims/c1/unlink-evidence",
                data={"evidence_id": "e1"},
            )
        assert resp.status_code == 303
        assert "/claims/c1" in resp.headers["location"]
        mock_unlink.assert_called_once()


class TestLinkUnlinkTheme:
    def test_link_theme_redirects(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.link_theme") as mock_link,
        ):
            resp = client.post(
                "/projects/p1/claims/c1/link-theme",
                data={"theme_id": "t1"},
            )
        assert resp.status_code == 303
        assert "/claims/c1" in resp.headers["location"]
        mock_link.assert_called_once()

    def test_unlink_theme_redirects(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.unlink_theme") as mock_unlink,
        ):
            resp = client.post(
                "/projects/p1/claims/c1/unlink-theme",
                data={"theme_id": "t1"},
            )
        assert resp.status_code == 303
        mock_unlink.assert_called_once()


class TestDeleteClaim:
    def test_delete_claim_redirects(self, client):
        with (
            patch("app.routers.claims.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.claims.claims_service.delete_claim") as mock_del,
        ):
            resp = client.post("/projects/p1/claims/c1/delete")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/claims"
        mock_del.assert_called_once()
