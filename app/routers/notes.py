from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import require_auth
from app.models import User
from app.services import notes as notes_service
from app.services import projects as project_service

router = APIRouter(prefix="/projects/{project_id}/notes", tags=["notes"])
templates = Jinja2Templates(directory="app/templates")


def _guard(db, project_id, user):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return None, RedirectResponse(url="/projects", status_code=303)
    return project, None


@router.get("")
async def notes_list(
    project_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    all_notes = notes_service.list_notes(db, project_id)
    return templates.TemplateResponse("projects/notes.html", {
        "request": request,
        "user": user,
        "project": project,
        "notes": all_notes,
    })


@router.post("")
async def create_note(
    project_id: str,
    title: str = Form(default=""),
    body: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    body = body.strip()
    if body:
        notes_service.create_note(db, project_id, user.id, body=body, title=title)
    return RedirectResponse(url=f"/projects/{project_id}/notes", status_code=303)


@router.post("/{note_id}/edit")
async def edit_note(
    project_id: str,
    note_id: str,
    title: str = Form(default=""),
    body: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    body = body.strip()
    if body:
        notes_service.update_note(db, project_id, note_id, title=title, body=body)
    return RedirectResponse(url=f"/projects/{project_id}/notes", status_code=303)


@router.post("/{note_id}/delete")
async def delete_note(
    project_id: str,
    note_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    notes_service.delete_note(db, project_id, note_id)
    return RedirectResponse(url=f"/projects/{project_id}/notes", status_code=303)
