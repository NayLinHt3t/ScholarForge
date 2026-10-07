from pydantic import BaseModel, Field


class OutlineSection(BaseModel):
    id: str = ""
    project_id: str
    user_id: str
    title: str
    order_index: int = 0
    writing_notes: str = ""
    claim_ids: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)

    def to_firestore(self) -> dict:
        return self.model_dump(exclude={"id"})

    @classmethod
    def from_firestore(cls, doc) -> "OutlineSection":
        data = doc.to_dict()
        data.setdefault("writing_notes", "")
        data.setdefault("claim_ids", [])
        data.setdefault("evidence_ids", [])
        return cls(id=doc.id, **data)
