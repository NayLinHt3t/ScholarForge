from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import PlainTextResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import require_auth
from app.exceptions import OllamaUnavailableError
from app.models import User
from app.services import export as export_service
from app.services import outline as outline_service
from app.services import projects as project_service
from app.services.citations import STYLES
from app.services.outline import REGENERABLE_SECTIONS, SECTION_DISPLAY_NAMES, SECTION_ORDER

router = APIRouter(tags=["outline"])
templates = Jinja2Templates(directory="app/templates")


@router.post("/projects/{project_id}/outlines")
async def generate_outline(
    project_id: str,
    request: Request,
    citation_style: str = Form(default="IEEE"),
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)

    try:
        result = await outline_service.generate(db, project_id, citation_style)
    except OllamaUnavailableError:
        return RedirectResponse(
            url=f"/projects/{project_id}?ollama_down=1", status_code=303
        )
    except ValueError as exc:
        return RedirectResponse(
            url=f"/projects/{project_id}?gen_error=1", status_code=303
        )

    if result.success:
        return RedirectResponse(
            url=f"/projects/{project_id}/outlines/{result.outline.id}", status_code=303
        )

    # Citation validation failed — render error page, do not save
    return templates.TemplateResponse(
        "projects/outline_error.html",
        {
            "request": request,
            "user": user,
            "project": project,
            "invalid_markers": result.invalid_markers,
            "citation_style": citation_style,
        },
        status_code=422,
    )


@router.get("/projects/{project_id}/outlines/{outline_id}")
async def view_outline(
    project_id: str,
    outline_id: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)

    outline = outline_service.get_outline(db, project_id, outline_id)
    if not outline:
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)

    return templates.TemplateResponse(
        "projects/outline.html",
        {
            "request": request,
            "user": user,
            "project": project,
            "outline": outline,
            "section_order": SECTION_ORDER,
            "section_names": SECTION_DISPLAY_NAMES,
            "regenerable": REGENERABLE_SECTIONS,
            "styles": STYLES,
        },
    )


@router.post("/projects/{project_id}/outlines/{outline_id}/sections/{section_key}/regenerate")
async def regenerate_section(
    project_id: str,
    outline_id: str,
    section_key: str,
    request: Request,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)

    base_url = f"/projects/{project_id}/outlines/{outline_id}"

    try:
        result = await outline_service.regenerate_section(db, project_id, outline_id, section_key)
    except OllamaUnavailableError:
        return RedirectResponse(url=f"{base_url}?ollama_down=1", status_code=303)
    except ValueError:
        return RedirectResponse(url=base_url, status_code=303)

    if result.success:
        return RedirectResponse(url=f"{base_url}?regenerated={section_key}", status_code=303)

    outline = outline_service.get_outline(db, project_id, outline_id)
    return templates.TemplateResponse(
        "projects/outline_error.html",
        {
            "request": request,
            "user": user,
            "project": project,
            "invalid_markers": result.invalid_markers,
            "outline_id": outline_id,
        },
        status_code=422,
    )


@router.get("/projects/{project_id}/outlines/{outline_id}/export.md")
async def export_markdown(
    project_id: str,
    outline_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)
    outline = outline_service.get_outline(db, project_id, outline_id)
    if not outline:
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)

    md = export_service.render_markdown(project.name, outline)
    slug = project.name[:40].replace(" ", "_").replace("/", "-")
    return PlainTextResponse(
        md,
        headers={"Content-Disposition": f'attachment; filename="{slug}_outline.md"'},
        media_type="text/markdown; charset=utf-8",
    )


@router.get("/projects/{project_id}/outlines/{outline_id}/export.pdf")
async def export_pdf(
    project_id: str,
    outline_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)
    outline = outline_service.get_outline(db, project_id, outline_id)
    if not outline:
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)

    pdf_bytes = export_service.render_pdf(project.name, outline)
    slug = project.name[:40].replace(" ", "_").replace("/", "-")
    return Response(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{slug}_outline.pdf"'},
    )


@router.post("/projects/{project_id}/outlines/{outline_id}/delete")
async def delete_outline(
    project_id: str,
    outline_id: str,
    user: User = Depends(require_auth),
    db: firestore.Client = Depends(get_db),
):
    project = project_service.get_project(db, project_id)
    if not project or project.user_id != user.id:
        return RedirectResponse(url="/projects", status_code=303)
    outline_service.delete_outline(db, project_id, outline_id)
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
