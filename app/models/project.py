from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Project(BaseModel):
    id: str = ""
    user_id: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "Project":
        return cls(id=doc.id, **doc.to_dict())
