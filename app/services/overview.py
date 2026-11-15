"""Cross-project views for the simplified UI (Home, My Library, My Notes).

Data still lives inside projects (no schema change); these helpers just gather
a user's papers and notes from all of their projects in one place.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone

from google.cloud import firestore

from app.models import Note, Project, SavedResource
from app.services import library as library_service
from app.services import notes as notes_service
from app.services import projects as project_service

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


@dataclass
class ProjectSummary:
    project: Project
    papers: list[SavedResource] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)

    @property
    def last_activity(self) -> datetime:
        stamps = [self.project.updated_at, self.project.created_at]
        stamps += [p.added_at for p in self.papers]
        stamps += [p.last_opened_at for p in self.papers if p.last_opened_at]
        stamps += [n.updated_at for n in self.notes]
        return max(stamps)


@dataclass
class Overview:
    projects: list[ProjectSummary]

    @property
    def project_names(self) -> dict[str, str]:
        return {s.project.id: s.project.name for s in self.projects}

    @property
    def papers(self) -> list[SavedResource]:
        out = [p for s in self.projects for p in s.papers]
        return sorted(out, key=lambda p: p.added_at, reverse=True)

    @property
    def notes(self) -> list[Note]:
        out = [n for s in self.projects for n in s.notes]
        return sorted(out, key=lambda n: n.updated_at, reverse=True)

    @property
    def recently_opened(self) -> list[SavedResource]:
        opened = [p for p in self.papers if p.last_opened_at]
        return sorted(opened, key=lambda p: p.last_opened_at or _EPOCH, reverse=True)

    def getting_started(self) -> list[dict]:
        """The four first-run steps, each with done/current state and one link."""
        papers = self.papers
        first_project = self.projects[0].project if self.projects else None
        first_paper = papers[0] if papers else None
        has_project = bool(self.projects)
        has_paper = bool(papers)
        asked = any(p.questions_asked > 0 for p in papers)
        has_note = bool(self.notes)

        steps = [
            {"label": "Create your first project", "done": has_project,
             "action": "Create project", "href": "?new=1"},
            {"label": "Add your first paper", "done": has_paper,
             "action": "Find papers",
             "href": f"/projects/{first_project.id}/search" if first_project else "?new=1"},
            {"label": "Ask a question about a paper", "done": asked,
             "action": "Open a paper",
             "href": f"/projects/{first_paper.project_id}/sources/{first_paper.id}" if first_paper else None},
            {"label": "Save your first note", "done": has_note,
             "action": "Open a paper",
             "href": f"/projects/{first_paper.project_id}/sources/{first_paper.id}" if first_paper else None},
        ]
        current_marked = False
        for s in steps:
            s["current"] = (not s["done"]) and not current_marked
            if s["current"]:
                current_marked = True
        return steps


def gather(db: firestore.Client, user_id: str, projects: list[Project] | None = None) -> Overview:
    if projects is None:
        projects = project_service.list_projects(db, user_id)
    summaries = [
        ProjectSummary(
            project=p,
            papers=library_service.list_resources(db, p.id),
            notes=notes_service.list_notes(db, p.id),
        )
        for p in projects
    ]
    summaries.sort(key=lambda s: s.last_activity, reverse=True)
    return Overview(projects=summaries)
