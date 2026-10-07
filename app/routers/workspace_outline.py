from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import require_auth
from app.models import User
from app.services import claims as claims_service
from app.services import evidence as evidence_service
from app.services import library as library_service
from app.services import outline_sections as sections_service
from app.services import projects as project_service
from app.services import workspace_export

router = APIRouter(prefix="/projects/{project_id}", tags=["workspace_outline"])
templates = Jinja2Templates(directory="app/templates")


def _guard(db, project_id, user):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return None, RedirectResponse(url="/projects", status_code=303)
    return project, None


@router.get("/outline")
async def outline_workspace(
    project_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    sections = sections_service.list_sections(db, project_id)
    claims = claims_service.list_claims(db, project_id)
    evidence_items = evidence_service.list_evidence_for_project(db, project_id)
    sources = library_service.list_resources(db, project_id)
    source_map = {s.id: s for s in sources}
    claim_map = {c.id: c for c in claims}
    ev_map = {e.id: e for e in evidence_items}
    return templates.TemplateResponse("projects/outline_workspace.html", {
        "request": request,
        "user": user,
        "project": project,
        "sections": sections,
        "claims": claims,
        "claim_map": claim_map,
        "ev_map": ev_map,
        "source_map": source_map,
    })


@router.post("/outline/sections")
async def add_section(
    project_id: str,
    title: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    title = title.strip()
    if title:
        existing = sections_service.list_sections(db, project_id)
        next_index = len(existing)
        sections_service.add_section(db, project_id, user.id, title=title, order_index=next_index)
    return RedirectResponse(url=f"/projects/{project_id}/outline", status_code=303)


@router.get("/outline/sections/{section_id}")
async def section_detail(
    project_id: str,
    section_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    section = sections_service.get_section(db, project_id, section_id)
    if not section:
        return RedirectResponse(url=f"/projects/{project_id}/outline", status_code=303)
    all_claims = claims_service.list_claims(db, project_id)
    all_evidence = evidence_service.list_evidence_for_project(db, project_id)
    sources = library_service.list_resources(db, project_id)
    source_map = {s.id: s for s in sources}
    return templates.TemplateResponse("projects/section_detail.html", {
        "request": request,
        "user": user,
        "project": project,
        "section": section,
        "all_claims": all_claims,
        "all_evidence": all_evidence,
        "source_map": source_map,
        "linked_claim_ids": set(section.claim_ids),
        "linked_evidence_ids": set(section.evidence_ids),
    })


@router.post("/outline/sections/{section_id}/edit")
async def edit_section(
    project_id: str,
    section_id: str,
    title: str = Form(...),
    writing_notes: str = Form(default=""),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    title = title.strip()
    if title:
        sections_service.update_section(db, project_id, section_id, title=title, writing_notes=writing_notes)
    return RedirectResponse(url=f"/projects/{project_id}/outline/sections/{section_id}", status_code=303)


@router.post("/outline/sections/{section_id}/link-claim")
async def link_claim(
    project_id: str,
    section_id: str,
    claim_id: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    sections_service.link_claim(db, project_id, section_id, claim_id)
    return RedirectResponse(url=f"/projects/{project_id}/outline/sections/{section_id}", status_code=303)


@router.post("/outline/sections/{section_id}/unlink-claim")
async def unlink_claim(
    project_id: str,
    section_id: str,
    claim_id: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    sections_service.unlink_claim(db, project_id, section_id, claim_id)
    return RedirectResponse(url=f"/projects/{project_id}/outline/sections/{section_id}", status_code=303)


@router.post("/outline/sections/{section_id}/link-evidence")
async def link_evidence(
    project_id: str,
    section_id: str,
    evidence_id: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    sections_service.link_evidence(db, project_id, section_id, evidence_id)
    return RedirectResponse(url=f"/projects/{project_id}/outline/sections/{section_id}", status_code=303)


@router.post("/outline/sections/{section_id}/unlink-evidence")
async def unlink_evidence(
    project_id: str,
    section_id: str,
    evidence_id: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    sections_service.unlink_evidence(db, project_id, section_id, evidence_id)
    return RedirectResponse(url=f"/projects/{project_id}/outline/sections/{section_id}", status_code=303)


@router.post("/outline/sections/{section_id}/reorder")
async def reorder_section(
    project_id: str,
    section_id: str,
    direction: str = Form(...),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    sections = sections_service.list_sections(db, project_id)
    idx = next((i for i, s in enumerate(sections) if s.id == section_id), None)
    if idx is None:
        return RedirectResponse(url=f"/projects/{project_id}/outline", status_code=303)
    if direction == "up" and idx > 0:
        sections_service.reorder_section(db, project_id, section_id, idx - 1)
        sections_service.reorder_section(db, project_id, sections[idx - 1].id, idx)
    elif direction == "down" and idx < len(sections) - 1:
        sections_service.reorder_section(db, project_id, section_id, idx + 1)
        sections_service.reorder_section(db, project_id, sections[idx + 1].id, idx)
    return RedirectResponse(url=f"/projects/{project_id}/outline", status_code=303)


@router.post("/outline/sections/{section_id}/delete")
async def delete_section(
    project_id: str,
    section_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    _, redir = _guard(db, project_id, user)
    if redir:
        return redir
    sections_service.delete_section(db, project_id, section_id)
    return RedirectResponse(url=f"/projects/{project_id}/outline", status_code=303)


# ── Export ──────────────────────────────────────────────────────────────────

@router.get("/export/full.md")
async def export_full_markdown(
    project_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    from app.services import notes as notes_service, themes as themes_service
    sources = library_service.list_resources(db, project_id)
    evidence_items = evidence_service.list_evidence_for_project(db, project_id)
    notes = notes_service.list_notes(db, project_id)
    themes = themes_service.list_themes(db, project_id)
    claims = claims_service.list_claims(db, project_id)
    sections = sections_service.list_sections(db, project_id)
    content = workspace_export.export_full_structure(
        project, sources, evidence_items, notes, themes, claims, sections
    )
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in project.name)[:40]
    return PlainTextResponse(
        content,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}-research.md"'},
        media_type="text/markdown",
    )


@router.get("/export/outline.md")
async def export_outline_markdown(
    project_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project, redir = _guard(db, project_id, user)
    if redir:
        return redir
    sources = library_service.list_resources(db, project_id)
    evidence_items = evidence_service.list_evidence_for_project(db, project_id)
    claims = claims_service.list_claims(db, project_id)
    sections = sections_service.list_sections(db, project_id)
    content = workspace_export.export_outline_scaffold(
        project, sources, evidence_items, claims, sections
    )
    safe_name = "".join(c if c.isalnum() or c in "-_ " else "_" for c in project.name)[:40]
    return PlainTextResponse(
        content,
        headers={"Content-Disposition": f'attachment; filename="{safe_name}-outline.md"'},
        media_type="text/markdown",
    )
