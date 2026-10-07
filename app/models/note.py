from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Note(BaseModel):
    id: str = ""
    project_id: str
    user_id: str
    title: str = ""
    body: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "Note":
        data = doc.to_dict()
        data.setdefault("title", "")
        return cls(id=doc.id, **data)
