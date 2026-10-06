from datetime import datetime, timezone

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = ""
    email: str
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "User":
        return cls(id=doc.id, **doc.to_dict())
