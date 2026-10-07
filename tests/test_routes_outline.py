"""Tests for /projects/{id}/outline/* routes."""
from unittest.mock import patch

from tests.conftest import (
    FAKE_CLAIM,
    FAKE_EVIDENCE,
    FAKE_PROJECT,
    FAKE_SECTION,
    FAKE_SOURCE,
)


class TestOutlineWorkspace:
    def test_get_outline_returns_200(self, client):
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.list_sections",
                return_value=[],
            ),
            patch("app.routers.workspace_outline.claims_service.list_claims", return_value=[]),
            patch(
                "app.routers.workspace_outline.evidence_service.list_evidence_for_project",
                return_value=[],
            ),
            patch(
                "app.routers.workspace_outline.library_service.list_resources",
                return_value=[],
            ),
        ):
            resp = client.get("/projects/p1/outline")
        assert resp.status_code == 200

    def test_wrong_user_redirects(self, client):
        from app.models import Project
        from datetime import datetime, timezone
        other = Project(
            id="p2", user_id="other", name="Other",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        with patch(
            "app.routers.workspace_outline.project_service.get_project", return_value=other
        ):
            resp = client.get("/projects/p2/outline")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects"


class TestAddSection:
    def test_add_section_redirects(self, client):
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.list_sections",
                return_value=[],
            ),
            patch(
                "app.routers.workspace_outline.sections_service.add_section",
                return_value=FAKE_SECTION,
            ) as mock_add,
        ):
            resp = client.post(
                "/projects/p1/outline/sections",
                data={"title": "Introduction"},
            )
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/outline"
        mock_add.assert_called_once()

    def test_add_section_empty_title_no_action(self, client):
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.add_section"
            ) as mock_add,
        ):
            resp = client.post("/projects/p1/outline/sections", data={"title": "  "})
        assert resp.status_code == 303
        mock_add.assert_not_called()


class TestSectionDetail:
    def test_get_section_detail_returns_200(self, client):
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.get_section",
                return_value=FAKE_SECTION,
            ),
            patch("app.routers.workspace_outline.claims_service.list_claims", return_value=[]),
            patch(
                "app.routers.workspace_outline.evidence_service.list_evidence_for_project",
                return_value=[],
            ),
            patch(
                "app.routers.workspace_outline.library_service.list_resources",
                return_value=[],
            ),
        ):
            resp = client.get("/projects/p1/outline/sections/sec1")
        assert resp.status_code == 200
        assert b"Introduction" in resp.content

    def test_section_not_found_redirects(self, client):
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.get_section",
                return_value=None,
            ),
        ):
            resp = client.get("/projects/p1/outline/sections/missing")
        assert resp.status_code == 303
        assert "/outline" in resp.headers["location"]


class TestEditSection:
    def test_edit_section_redirects(self, client):
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.update_section"
            ) as mock_upd,
        ):
            resp = client.post(
                "/projects/p1/outline/sections/sec1/edit",
                data={"title": "Updated Title", "writing_notes": "notes here"},
            )
        assert resp.status_code == 303
        assert "/sections/sec1" in resp.headers["location"]
        mock_upd.assert_called_once()


class TestSectionLinkUnlink:
    def test_link_claim_redirects(self, client):
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.link_claim"
            ) as mock_link,
        ):
            resp = client.post(
                "/projects/p1/outline/sections/sec1/link-claim",
                data={"claim_id": "c1"},
            )
        assert resp.status_code == 303
        mock_link.assert_called_once()

    def test_unlink_claim_redirects(self, client):
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.unlink_claim"
            ) as mock_unlink,
        ):
            resp = client.post(
                "/projects/p1/outline/sections/sec1/unlink-claim",
                data={"claim_id": "c1"},
            )
        assert resp.status_code == 303
        mock_unlink.assert_called_once()

    def test_link_evidence_redirects(self, client):
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.link_evidence"
            ) as mock_link,
        ):
            resp = client.post(
                "/projects/p1/outline/sections/sec1/link-evidence",
                data={"evidence_id": "e1"},
            )
        assert resp.status_code == 303
        mock_link.assert_called_once()

    def test_unlink_evidence_redirects(self, client):
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.unlink_evidence"
            ) as mock_unlink,
        ):
            resp = client.post(
                "/projects/p1/outline/sections/sec1/unlink-evidence",
                data={"evidence_id": "e1"},
            )
        assert resp.status_code == 303
        mock_unlink.assert_called_once()


class TestDeleteSection:
    def test_delete_section_redirects(self, client):
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.delete_section"
            ) as mock_del,
        ):
            resp = client.post("/projects/p1/outline/sections/sec1/delete")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/outline"
        mock_del.assert_called_once()


class TestReorderSection:
    def test_reorder_up_redirects(self, client):
        from app.models.outline_section import OutlineSection
        sec0 = OutlineSection(id="sec0", project_id="p1", user_id="u1", title="First", order_index=0)
        sec1 = OutlineSection(id="sec1", project_id="p1", user_id="u1", title="Second", order_index=1)
        with (
            patch(
                "app.routers.workspace_outline.project_service.get_project",
                return_value=FAKE_PROJECT,
            ),
            patch(
                "app.routers.workspace_outline.sections_service.list_sections",
                return_value=[sec0, sec1],
            ),
            patch(
                "app.routers.workspace_outline.sections_service.reorder_section"
            ) as mock_reorder,
        ):
            resp = client.post(
                "/projects/p1/outline/sections/sec1/reorder",
                data={"direction": "up"},
            )
        assert resp.status_code == 303
        assert mock_reorder.call_count == 2
