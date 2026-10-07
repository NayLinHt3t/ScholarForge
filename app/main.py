import logging

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.exception_handlers import http_exception_handler as _default_http_handler
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.routers import auth as auth_router
from app.routers import claims as claims_router
from app.routers import evidence as evidence_router
from app.routers import library as library_router
from app.routers import notes as notes_router
from app.routers import outline as outline_router
from app.routers import projects as projects_router
from app.routers import search as search_router
from app.routers import sources as sources_router
from app.routers import summary as summary_router
from app.routers import themes as themes_router
from app.routers import workspace_outline as workspace_outline_router

app = FastAPI(title="ScholarForge")
_templates = Jinja2Templates(directory="app/templates")
app.include_router(auth_router.router)
app.include_router(projects_router.router)
# workspace MVP routes (order matters: more specific paths first)
app.include_router(sources_router.router)
app.include_router(evidence_router.router)
app.include_router(notes_router.router)
app.include_router(themes_router.router)
app.include_router(claims_router.router)
app.include_router(workspace_outline_router.router)
# legacy / P1 routes (kept functional, demoted from nav)
app.include_router(search_router.router)
app.include_router(library_router.router)
app.include_router(outline_router.router)
app.include_router(summary_router.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code in (301, 302, 303, 307, 308) and exc.headers and "Location" in exc.headers:
        return RedirectResponse(url=exc.headers["Location"], status_code=exc.status_code)
    return await _default_http_handler(request, exc)


@app.get("/")
async def root():
    return RedirectResponse(url="/auth/login", status_code=303)


@app.get("/terms")
async def terms(request: Request):
    return _templates.TemplateResponse("terms.html", {"request": request})
