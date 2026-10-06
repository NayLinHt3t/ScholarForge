from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request  # noqa: E402
from fastapi.exception_handlers import http_exception_handler as _default_http_handler
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse

from app.routers import auth as auth_router
from app.routers import library as library_router
from app.routers import outline as outline_router
from app.routers import projects as projects_router
from app.routers import search as search_router

app = FastAPI(title="ScholarForge")
app.include_router(auth_router.router)
app.include_router(projects_router.router)
app.include_router(search_router.router)
app.include_router(library_router.router)
app.include_router(outline_router.router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code in (301, 302, 303, 307, 308) and exc.headers and "Location" in exc.headers:
        return RedirectResponse(url=exc.headers["Location"], status_code=exc.status_code)
    return await _default_http_handler(request, exc)


@app.get("/")
async def root():
    return RedirectResponse(url="/auth/login", status_code=303)
