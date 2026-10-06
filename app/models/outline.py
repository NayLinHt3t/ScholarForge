from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Outline(BaseModel):
    id: str = ""
    project_id: str
    label: str | None = None
    citation_style: str = "IEEE"
    content: str                                # full rendered text for copy/export
    sections: dict[str, str] = Field(default_factory=dict)  # section_key -> content for per-section regen
    cited_resource_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "Outline":
        return cls(id=doc.id, **doc.to_dict())
