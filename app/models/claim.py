from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Claim(BaseModel):
    id: str = ""
    project_id: str
    user_id: str
    statement: str
    evidence_ids: list[str] = Field(default_factory=list)
    theme_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "Claim":
        data = doc.to_dict()
        data.setdefault("evidence_ids", [])
        data.setdefault("theme_ids", [])
        return cls(id=doc.id, **data)
