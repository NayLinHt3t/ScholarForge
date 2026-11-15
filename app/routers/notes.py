from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import require_auth
from app.models import User
from app.services import library as library_service
from app.services import notes as notes_service
from app.services import projects as project_service

router = APIRouter(prefix="/projects/{project_id}/notes", tags=["notes"])
templates = Jinja2Templates(directory="app/templates")


def _guard(db, project_id, user):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return None, RedirectResponse(url="/projects", status_code=303)
    return project, None


def _safe_return(return_to: str, fallback: str) -> str:
    # only allow local paths, never an external URL
    return return_to if return_to.startswith("/") and not return_to.startswith("//") else fallback


def _source_link(db, project_id: str, source_id: str) -> tuple[str | None, str]:
    """Validate a linked paper id and return (source_id, title)."""
    if not source_id:
        return None, ""
    src = library_service.get_resource(db, project_id, source_id)
    if not src:
        return None, ""
    return src.id, src.title


@router.get("")
async def notes_list(
    project_id: str,
    request: Request,
    q: str = "",
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    all_notes = notes_service.list_notes(db, project_id)
    total = len(all_notes)
    q = q.strip()
    if q:
        ql = q.lower()
        all_notes = [n for n in all_notes if ql in n.title.lower() or ql in n.body.lower()]
    return templates.TemplateResponse("notes/list.html", {
        "request": request,
        "user": user,
        "project": project,
        "scoped_project": project,
        "notes": all_notes,
        "total": total,
        "projects": [project],
        "project_names": {project.id: project.name},
        "q": q,
        "project_filter": project.id,
    })


@router.get("/new")
async def new_note(
    project_id: str,
    request: Request,
    source_id: str = "",
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    papers = library_service.list_resources(db, project_id)
    return templates.TemplateResponse("notes/editor.html", {
        "request": request, "user": user, "project": project,
        "note": None, "papers": papers, "linked_source_id": source_id,
    })


@router.get("/{note_id}")
async def open_note(
    project_id: str,
    note_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    note = notes_service.get_note(db, project_id, note_id)
    if not note:
        return RedirectResponse(url=f"/projects/{project_id}/notes", status_code=303)
    papers = library_service.list_resources(db, project_id)
    return templates.TemplateResponse("notes/editor.html", {
        "request": request, "user": user, "project": project,
        "note": note, "papers": papers, "linked_source_id": note.source_id or "",
    })


@router.post("")
async def create_note(
    project_id: str,
    title: str = Form(default=""),
    body: str = Form(...),
    source_id: str = Form(default=""),
    return_to: str = Form(default=""),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    body = body.strip()
    dest = _safe_return(return_to, f"/projects/{project_id}/notes")
    if body:
        sid, stitle = _source_link(db, project_id, source_id)
        notes_service.create_note(
            db, project_id, user.id, body=body, title=title,
            **({"source_id": sid, "source_title": stitle} if sid else {}),
        )
    return RedirectResponse(url=dest, status_code=303)


@router.post("/{note_id}/edit")
async def edit_note(
    project_id: str,
    note_id: str,
    title: str = Form(default=""),
    body: str = Form(...),
    source_id: str | None = Form(default=None),
    return_to: str = Form(default=""),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    body = body.strip()
    if body:
        extra = {}
        if source_id is not None:   # field present on the form → update the link
            sid, stitle = _source_link(db, project_id, source_id)
            extra = {"source_id": sid, "source_title": stitle}
        notes_service.update_note(db, project_id, note_id, title=title, body=body, **extra)
    return RedirectResponse(url=_safe_return(return_to, f"/projects/{project_id}/notes"), status_code=303)


@router.post("/{note_id}/delete")
async def delete_note(
    project_id: str,
    note_id: str,
    return_to: str = Form(default=""),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    notes_service.delete_note(db, project_id, note_id)
    return RedirectResponse(url=_safe_return(return_to, f"/projects/{project_id}/notes"), status_code=303)
