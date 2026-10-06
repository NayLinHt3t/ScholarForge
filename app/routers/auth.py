from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from google.cloud import firestore

from app.database import get_db
from app.dependencies import COOKIE_NAME, get_current_user
from app.models import User
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(directory="app/templates")

_COOKIE_MAX_AGE = 30 * 24 * 60 * 60  # 30 days in seconds


def _set_session_cookie(response: RedirectResponse, token: str) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
    )


@router.get("/signup")
async def signup_page(request: Request, user: User | None = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/projects", status_code=303)
    return templates.TemplateResponse("auth/signup.html", {"request": request})


@router.post("/signup")
async def signup(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    terms_accepted: str = Form(default=""),
    db: firestore.Client = Depends(get_db),
):
    if terms_accepted != "on":
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": "You must accept the terms to continue."},
            status_code=400,
        )
    if len(password) < 8:
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": "Password must be at least 8 characters."},
            status_code=400,
        )
    try:
        user = auth_service.create_user(
            db,
            email=email.strip().lower(),
            password=password,
            source_ip=request.client.host if request.client else None,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            "auth/signup.html",
            {"request": request, "error": str(exc)},
            status_code=400,
        )

    session = auth_service.create_session(db, user.id)
    response = RedirectResponse(url="/projects", status_code=303)
    _set_session_cookie(response, session.id)
    return response


@router.get("/login")
async def login_page(request: Request, user: User | None = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/projects", status_code=303)
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: firestore.Client = Depends(get_db),
):
    user = auth_service.authenticate_user(db, email.strip().lower(), password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Invalid email or password."},
            status_code=401,
        )

    session = auth_service.create_session(db, user.id)
    response = RedirectResponse(url="/projects", status_code=303)
    _set_session_cookie(response, session.id)
    return response


@router.post("/logout")
async def logout(request: Request, db: firestore.Client = Depends(get_db)):
    token = request.cookies.get(COOKIE_NAME)
    if token:
        auth_service.delete_session(db, token)
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response


@router.get("/delete-account")
async def delete_account_page(
    request: Request, user: User | None = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=303)
    return templates.TemplateResponse("auth/delete_account.html", {"request": request})


@router.post("/delete-account")
async def delete_account(
    request: Request,
    email_confirm: str = Form(...),
    db: firestore.Client = Depends(get_db),
):
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return RedirectResponse(url="/auth/login", status_code=303)

    session = auth_service.get_session(db, token)
    if not session:
        return RedirectResponse(url="/auth/login", status_code=303)

    user = auth_service.get_user_by_id(db, session.user_id)
    if not user or user.email != email_confirm.strip().lower():
        return templates.TemplateResponse(
            "auth/delete_account.html",
            {"request": request, "error": "Email does not match. Account not deleted."},
            status_code=400,
        )

    auth_service.delete_account(db, user.id)
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response
