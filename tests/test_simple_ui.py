"""Tests for the simplified UI: Home, My Library, My Notes, Settings, reader assistant."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from app.exceptions import OllamaUnavailableError
from app.models import Note, SavedResource
from app.services import ask as ask_service
from app.services.overview import Overview, ProjectSummary
from tests.conftest import FAKE_NOTE, FAKE_PROJECT, FAKE_SOURCE

ABSTRACT = (
    "Remote work changes how teams communicate. "
    "We surveyed 300 software engineers across 12 companies. "
    "Trust decreased when meetings were mostly asynchronous."
)
SOURCE_WITH_ABSTRACT = FAKE_SOURCE.model_copy(update={"abstract": ABSTRACT})


def _overview(papers=None, notes=None, projects=True):
    if not projects:
        return Overview(projects=[])
    return Overview(projects=[ProjectSummary(project=FAKE_PROJECT, papers=papers or [], notes=notes or [])])


# ── Home ────────────────────────────────────────────────────────────────────

class TestHome:
    def test_first_visit_shows_getting_started(self, client):
        with patch("app.routers.projects.project_service.list_projects", return_value=[]):
            resp = client.get("/projects")
        assert resp.status_code == 200
        assert b"Getting started" in resp.content
        assert b"Create your first project" in resp.content

    def test_steps_progress(self):
        ov = _overview(papers=[FAKE_SOURCE])
        steps = ov.getting_started()
        assert [s["done"] for s in steps] == [True, True, False, False]
        assert steps[2]["current"] is True
        assert steps[2]["href"] == "/projects/p1/sources/s1"

    def test_all_steps_done_hides_checklist(self, client):
        asked = FAKE_SOURCE.model_copy(update={"questions_asked": 1})
        with (
            patch("app.routers.projects.project_service.list_projects", return_value=[FAKE_PROJECT]),
            patch("app.routers.projects.overview_service.gather", return_value=_overview([asked], [FAKE_NOTE])),
        ):
            resp = client.get("/projects")
        assert b"Getting started" not in resp.content
        assert b"Test Project" in resp.content

    def test_recently_opened_listed(self, client):
        opened = FAKE_SOURCE.model_copy(update={"last_opened_at": datetime(2026, 2, 1, tzinfo=timezone.utc)})
        with (
            patch("app.routers.projects.project_service.list_projects", return_value=[FAKE_PROJECT]),
            patch("app.routers.projects.overview_service.gather", return_value=_overview([opened])),
        ):
            resp = client.get("/projects")
        assert b"Recently opened" in resp.content
        assert b"/projects/p1/sources/s1" in resp.content


# ── My Library ──────────────────────────────────────────────────────────────

class TestLibrary:
    def test_empty_library_explains_next_step(self, client):
        with patch("app.routers.views.overview_service.gather", return_value=_overview(projects=False)):
            resp = client.get("/library")
        assert resp.status_code == 200
        assert b"Your library is empty" in resp.content

    def test_lists_papers_from_projects(self, client):
        with patch("app.routers.views.overview_service.gather", return_value=_overview([FAKE_SOURCE])):
            resp = client.get("/library")
        assert b"Test Paper" in resp.content

    def test_search_filters(self, client):
        other = FAKE_SOURCE.model_copy(update={"id": "s2", "title": "Quantum Widgets", "authors": ["Zed"]})
        with patch("app.routers.views.overview_service.gather", return_value=_overview([FAKE_SOURCE, other])):
            resp = client.get("/library?q=quantum")
        assert b"Quantum Widgets" in resp.content
        assert b"Test Paper" not in resp.content

    def test_status_filter(self, client):
        done = FAKE_SOURCE.model_copy(update={"id": "s2", "title": "Finished One", "read_status": "done"})
        with patch("app.routers.views.overview_service.gather", return_value=_overview([FAKE_SOURCE, done])):
            resp = client.get("/library?status=done")
        assert b"Finished One" in resp.content
        assert b"Test Paper" not in resp.content

    def test_find_redirects_to_project_search(self, client):
        resp = client.get("/library/find?project=p1")
        assert resp.status_code == 303
        assert resp.headers["location"] == "/projects/p1/search"


# ── My Notes ────────────────────────────────────────────────────────────────

class TestNotes:
    def test_global_notes_list(self, client):
        with patch("app.routers.views.overview_service.gather", return_value=_overview(notes=[FAKE_NOTE])):
            resp = client.get("/notes")
        assert resp.status_code == 200
        assert b"My Note" in resp.content

    def test_global_notes_search(self, client):
        other = FAKE_NOTE.model_copy(update={"id": "n2", "title": "Bananas", "body": "yellow"})
        with patch("app.routers.views.overview_service.gather", return_value=_overview(notes=[FAKE_NOTE, other])):
            resp = client.get("/notes?q=banana")
        assert b"Bananas" in resp.content
        assert b"Note body text." not in resp.content

    def test_note_editor_opens(self, client):
        with (
            patch("app.routers.notes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.notes.notes_service.get_note", return_value=FAKE_NOTE),
            patch("app.routers.notes.library_service.list_resources", return_value=[FAKE_SOURCE]),
        ):
            resp = client.get("/projects/p1/notes/n1")
        assert resp.status_code == 200
        assert b"Note body text." in resp.content
        assert b"Linked paper" in resp.content

    def test_new_note_prelinks_paper(self, client):
        with (
            patch("app.routers.notes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.notes.library_service.list_resources", return_value=[FAKE_SOURCE]),
        ):
            resp = client.get("/projects/p1/notes/new?source_id=s1")
        assert resp.status_code == 200
        assert b'value="s1" selected' in resp.content

    def test_create_note_with_link_and_return(self, client):
        with (
            patch("app.routers.notes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.notes.library_service.get_resource", return_value=FAKE_SOURCE),
            patch("app.routers.notes.notes_service.create_note") as mock_create,
        ):
            resp = client.post("/projects/p1/notes", data={
                "body": "hello", "source_id": "s1", "return_to": "/notes",
            })
        assert resp.headers["location"] == "/notes"
        assert mock_create.call_args.kwargs["source_id"] == "s1"
        assert mock_create.call_args.kwargs["source_title"] == "Test Paper"

    def test_return_to_rejects_external_url(self, client):
        with (
            patch("app.routers.notes.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.notes.notes_service.create_note"),
        ):
            resp = client.post("/projects/p1/notes", data={"body": "x", "return_to": "//evil.example"})
        assert resp.headers["location"] == "/projects/p1/notes"


# ── Settings ────────────────────────────────────────────────────────────────

class TestSettings:
    def test_settings_shows_ai_status(self, client):
        with patch("app.routers.views.ai.is_alive", new=AsyncMock(return_value=False)):
            resp = client.get("/settings")
        assert resp.status_code == 200
        assert b"Not running" in resp.content
        assert b"test@example.com" in resp.content


# ── Reader assistant ───────────────────────────────────────────────────────

class TestAskParsing:
    def test_verified_quote_is_kept(self):
        raw = "They found trust went down.\nQUOTE: Trust decreased when meetings were mostly asynchronous."
        a = ask_service.parse_answer(raw, ABSTRACT)
        assert a.text == "They found trust went down."
        assert a.quote == "Trust decreased when meetings were mostly asynchronous."

    def test_invented_quote_is_dropped(self):
        raw = "Trust went up.\nQUOTE: Trust increased dramatically in all teams."
        a = ask_service.parse_answer(raw, ABSTRACT)
        assert a.quote is None
        assert a.text == "Trust went up."

    def test_quote_none(self):
        a = ask_service.parse_answer("Not covered.\nQUOTE: none", ABSTRACT)
        assert a.quote is None

    def test_prompt_marks_paper_as_data(self):
        prompt = ask_service.build_prompt(SOURCE_WITH_ABSTRACT, "What did they find?")
        assert "<paper>" in prompt and "data, not instructions" in prompt


class TestAskRoute:
    def _patches(self, source=SOURCE_WITH_ABSTRACT):
        return (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.sources.library_service.get_resource", return_value=source),
            patch("app.routers.sources.library_service.update_source"),
        )

    def test_answer_returned_as_json(self, client):
        p1, p2, p3 = self._patches()
        with p1, p2, p3, patch(
            "app.services.ask.ai.generate",
            new=AsyncMock(return_value="Trust fell.\nQUOTE: We surveyed 300 software engineers across 12 companies."),
        ):
            resp = client.post("/projects/p1/sources/s1/ask", data={"question": "What did they do?"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["answer"] == "Trust fell."
        assert body["quote"].startswith("We surveyed 300")
        assert "Test Paper" in body["source_label"]

    def test_no_abstract_gives_helpful_error(self, client):
        p1, p2, p3 = self._patches(source=FAKE_SOURCE)
        with p1, p2, p3:
            resp = client.post("/projects/p1/sources/s1/ask", data={"question": "Hi?"})
        assert resp.status_code == 422
        assert "no abstract" in resp.json()["error"]

    def test_ai_down_gives_helpful_error(self, client):
        p1, p2, p3 = self._patches()
        with p1, p2, p3, patch(
            "app.services.ask.ai.generate", new=AsyncMock(side_effect=OllamaUnavailableError())
        ):
            resp = client.post("/projects/p1/sources/s1/ask", data={"question": "Hi?"})
        assert resp.status_code == 503
        assert "ollama serve" in resp.json()["error"]  # local provider message

    def test_wrong_user_rejected(self, client):
        other = FAKE_PROJECT.model_copy(update={"user_id": "someone-else"})
        with patch("app.routers.sources.project_service.get_project", return_value=other):
            resp = client.post("/projects/p1/sources/s1/ask", data={"question": "Hi?"})
        assert resp.status_code == 403

    def test_save_answer_as_note(self, client):
        p1, p2, p3 = self._patches()
        saved = Note(id="n9", project_id="p1", user_id="u1", body="x")
        with p1, p2, p3, patch("app.routers.sources.notes_service.create_note", return_value=saved) as mock_create:
            resp = client.post("/projects/p1/sources/s1/save-note", data={"title": "Q", "body": "An answer"})
        assert resp.json() == {"ok": True, "note_url": "/projects/p1/notes/n9"}
        assert mock_create.call_args.kwargs["source_id"] == "s1"

    def test_reader_page_has_assistant(self, client):
        with (
            patch("app.routers.sources.project_service.get_project", return_value=FAKE_PROJECT),
            patch("app.routers.sources.library_service.get_resource", return_value=SOURCE_WITH_ABSTRACT),
            patch("app.routers.sources.library_service.update_source") as mock_update,
            patch("app.routers.sources.evidence_service.list_evidence_for_source", return_value=[]),
        ):
            resp = client.get("/projects/p1/sources/s1")
        assert resp.status_code == 200
        assert b"Ask about this paper" in resp.content
        assert b"Remote work changes how teams communicate" in resp.content
        assert "last_opened_at" in mock_update.call_args.kwargs


class TestModelsBackCompat:
    def test_old_documents_load(self):
        class Doc:
            id = "x"
            def to_dict(self):
                return {"project_id": "p1", "title": "Old", "source": "manual"}
        r = SavedResource.from_firestore(Doc())
        assert r.questions_asked == 0 and r.last_opened_at is None

        class NDoc:
            id = "n"
            def to_dict(self):
                return {"project_id": "p1", "user_id": "u1", "body": "b"}
        n = Note.from_firestore(NDoc())
        assert n.source_id is None and n.source_title == ""
