import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from google.cloud import firestore

from app.collections import AUDIT_LOG, CONSENT_RECORDS, PROJECTS, SESSIONS, USERS
from app.models import AuditLogEntry, ConsentRecord, Session, User

SESSION_EXPIRY_DAYS = 30
TERMS_VERSION = "v1.0"


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def get_user_by_email(db: firestore.Client, email: str) -> User | None:
    docs = (
        db.collection(USERS)
        .where(filter=firestore.FieldFilter("email", "==", email))
        .limit(1)
        .get()
    )
    for doc in docs:
        return User.from_firestore(doc)
    return None


def get_user_by_id(db: firestore.Client, user_id: str) -> User | None:
    doc = db.collection(USERS).document(user_id).get()
    return User.from_firestore(doc) if doc.exists else None


def create_user(
    db: firestore.Client,
    email: str,
    password: str,
    source_ip: str | None = None,
) -> User:
    if get_user_by_email(db, email):
        raise ValueError("Email already registered")

    doc_ref = db.collection(USERS).document()
    user = User(id=doc_ref.id, email=email, password_hash=_hash_password(password))
    doc_ref.set(user.to_firestore())

    # Immutable consent record — never deleted (BL-47, BL-48)
    consent_ref = db.collection(CONSENT_RECORDS).document()
    consent_ref.set(
        ConsentRecord(
            id=consent_ref.id,
            user_id=user.id,
            terms_version=TERMS_VERSION,
            accepted_at=datetime.now(timezone.utc),
        ).to_firestore()
    )

    _write_audit(db, action="signup", user_id=user.id, source_ip=source_ip)
    return user


def authenticate_user(db: firestore.Client, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not _verify_password(password, user.password_hash):
        return None
    return user


def create_session(db: firestore.Client, user_id: str) -> Session:
    token = secrets.token_hex(32)
    session = Session(
        id=token,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=SESSION_EXPIRY_DAYS),
    )
    db.collection(SESSIONS).document(token).set(session.to_firestore())
    return session


def get_session(db: firestore.Client, token: str) -> Session | None:
    doc = db.collection(SESSIONS).document(token).get()
    if not doc.exists:
        return None
    session = Session.from_firestore(doc)
    if session.expires_at < datetime.now(timezone.utc):
        doc.reference.delete()
        return None
    return session


def delete_session(db: firestore.Client, token: str) -> None:
    db.collection(SESSIONS).document(token).delete()


def delete_account(db: firestore.Client, user_id: str) -> None:
    # Invalidate all active sessions
    for doc in (
        db.collection(SESSIONS)
        .where(filter=firestore.FieldFilter("user_id", "==", user_id))
        .get()
    ):
        doc.reference.delete()

    # Cascade delete projects → saved_resources + outlines
    from app.services.projects import delete_project  # late import avoids circular dependency

    for project_doc in (
        db.collection(PROJECTS)
        .where(filter=firestore.FieldFilter("user_id", "==", user_id))
        .get()
    ):
        delete_project(db, project_doc.id)

    # Delete user — consent_records intentionally skipped (BL-47)
    db.collection(USERS).document(user_id).delete()

    _write_audit(db, action="delete_account", user_id=user_id)


def _write_audit(
    db: firestore.Client,
    action: str,
    user_id: str | None = None,
    source_ip: str | None = None,
) -> None:
    ref = db.collection(AUDIT_LOG).document()
    ref.set(
        AuditLogEntry(id=ref.id, action=action, user_id=user_id, source_ip=source_ip).to_firestore()
    )
