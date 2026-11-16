"""Top-level screens of the simplified UI: My Library, My Notes, Settings."""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from app.templating import templates
from google.cloud import firestore

from app.clients import ai
from app.config import GENERATE_MODEL
from app.database import get_db
from app.dependencies import require_auth
from app.models import User
from app.models.resource import READ_STATUSES
from app.services import overview as overview_service

router = APIRouter(tags=["views"])


def _matches(text: str, q: str) -> bool:
    return q.lower() in (text or "").lower()


@router.get("/library")
async def library(
    request: Request,
    q: str = "",
    project: str = "",
    status: str = "",
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    ov = overview_service.gather(db, user.id)
    papers = ov.papers
    total = len(papers)
    q = q.strip()
    if q:
        papers = [p for p in papers if _matches(p.title, q) or _matches(" ".join(p.authors), q)]
    if project:
        papers = [p for p in papers if p.project_id == project]
    if status in READ_STATUSES:
        papers = [p for p in papers if p.read_status == status]
    return templates.TemplateResponse("library.html", {
        "request": request, "user": user,
        "papers": papers, "total": total,
        "projects": [s.project for s in ov.projects],
        "project_names": ov.project_names,
        "q": q, "project_filter": project, "status_filter": status,
    })


@router.get("/library/find")
async def library_find(project: str = "", user: User = Depends(require_auth)):
    """'Find papers' from My Library: jump to the chosen project's search."""
    if project:
        return RedirectResponse(url=f"/projects/{project}/search", status_code=303)
    return RedirectResponse(url="/library", status_code=303)


@router.get("/notes")
async def all_notes(
    request: Request,
    q: str = "",
    project: str = "",
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    ov = overview_service.gather(db, user.id)
    notes = ov.notes
    total = len(notes)
    q = q.strip()
    if q:
        notes = [n for n in notes if _matches(n.title, q) or _matches(n.body, q)]
    if project:
        notes = [n for n in notes if n.project_id == project]
    return templates.TemplateResponse("notes/list.html", {
        "request": request, "user": user,
        "notes": notes, "total": total,
        "projects": [s.project for s in ov.projects],
        "project_names": ov.project_names,
        "q": q, "project_filter": project, "scoped_project": None,
    })


@router.get("/notes/new")
async def new_note_pick_project(
    project: str = "",
    user: User = Depends(require_auth),
):
    if project:
        return RedirectResponse(url=f"/projects/{project}/notes/new", status_code=303)
    return RedirectResponse(url="/notes", status_code=303)


@router.get("/settings")
async def settings(
    request: Request,
    user: User = Depends(require_auth),
):
    ai_ready = await ai.is_alive()
    return templates.TemplateResponse("settings.html", {
        "request": request, "user": user,
        "ai_ready": ai_ready, "model": GENERATE_MODEL,
    })
