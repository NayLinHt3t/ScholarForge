from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    id: str = ""
    project_id: str
    source_id: str
    user_id: str
    quote: str
    page_reference: str = ""
    student_note: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "Evidence":
        data = doc.to_dict()
        data.setdefault("page_reference", "")
        data.setdefault("student_note", "")
        return cls(id=doc.id, **data)
