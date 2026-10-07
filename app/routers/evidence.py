from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import require_auth
from app.models import User
from app.services import evidence as evidence_service
from app.services import library as library_service
from app.services import projects as project_service

router = APIRouter(prefix="/projects/{project_id}", tags=["evidence"])
templates = Jinja2Templates(directory="app/templates")


def _guard(db, project_id, user):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return None, RedirectResponse(url="/projects", status_code=303)
    return project, None


@router.get("/evidence")
async def evidence_list(
    project_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    items = evidence_service.list_evidence_for_project(db, project_id)
    sources = library_service.list_resources(db, project_id)
    source_map = {s.id: s for s in sources}
    return templates.TemplateResponse("projects/evidence_list.html", {
        "request": request,
        "user": user,
        "project": project,
        "evidence_items": items,
        "source_map": source_map,
    })


@router.post("/sources/{source_id}/evidence")
async def add_evidence(
    project_id: str,
    source_id: str,
    quote: str = Form(...),
    page_reference: str = Form(default=""),
    student_note: str = Form(default=""),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    quote = quote.strip()
    if quote:
        evidence_service.add_evidence(
            db, project_id, source_id, user.id,
            quote=quote,
            page_reference=page_reference,
            student_note=student_note,
        )
    return RedirectResponse(
        url=f"/projects/{project_id}/sources/{source_id}", status_code=303
    )


@router.post("/evidence/{evidence_id}/edit")
async def edit_evidence(
    project_id: str,
    evidence_id: str,
    quote: str = Form(...),
    page_reference: str = Form(default=""),
    student_note: str = Form(default=""),
    source_id: str = Form(default=""),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    quote = quote.strip()
    if quote:
        evidence_service.update_evidence(
            db, project_id, evidence_id, quote, page_reference, student_note
        )
    back = f"/projects/{project_id}/sources/{source_id}" if source_id else f"/projects/{project_id}/evidence"
    return RedirectResponse(url=back, status_code=303)


@router.post("/evidence/{evidence_id}/delete")
async def delete_evidence(
    project_id: str,
    evidence_id: str,
    source_id: str = Form(default=""),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    evidence_service.delete_evidence(db, project_id, evidence_id)
    back = f"/projects/{project_id}/sources/{source_id}" if source_id else f"/projects/{project_id}/evidence"
    return RedirectResponse(url=back, status_code=303)
