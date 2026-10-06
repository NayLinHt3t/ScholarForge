from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Session(BaseModel):
    id: str = ""        # session token — used as the Firestore document ID
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "Session":
        return cls(id=doc.id, **doc.to_dict())
