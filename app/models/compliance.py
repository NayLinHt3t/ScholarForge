from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ConsentRecord(BaseModel):
    """Immutable record of a user accepting a terms version (BL-48, AUTH-LR-01).

    Never deleted — account deletion explicitly skips this collection so the
    regulatory audit trail is preserved (BL-47).
    """

    id: str = ""
    user_id: str
    terms_version: str
    accepted_at: datetime
    how: str = "checkbox+form-submit"

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "ConsentRecord":
        return cls(id=doc.id, **doc.to_dict())


class AuditLogEntry(BaseModel):
    id: str = ""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str | None = None              # None for unauthenticated events (e.g. signup attempt)
    action: str
    source_ip: str | None = None
    extra: dict | None = None               # arbitrary JSON context

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "AuditLogEntry":
        return cls(id=doc.id, **doc.to_dict())
