from fastapi import Depends, HTTPException, Request
from google.cloud import firestore

from app.database import get_db
from app.models import User
from app.services import auth as auth_service

COOKIE_NAME = "sf_session"


def get_current_user(
    request: Request,
    db: firestore.Client = Depends(get_db),
) -> User | None:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    session = auth_service.get_session(db, token)
    if not session:
        return None
    return auth_service.get_user_by_id(db, session.user_id)


def require_auth(user: User | None = Depends(get_current_user)) -> User:
    if user is None:
        raise HTTPException(status_code=303, headers={"Location": "/auth/login"})
    return user
