import re
from dataclasses import dataclass, field

from google.cloud import firestore

from app.clients import ollama
from app.exceptions import OllamaUnavailableError
from app.models import SavedResource
from app.services import citations, library


@dataclass
class SummaryResult:
    text: str | None
    references: str = ""
    invalid_markers: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.text is not None


def _resource_block(resources: list[SavedResource]) -> str:
    lines = []
    for i, r in enumerate(resources, 1):
        snippet = (r.abstract or "")[:250].replace("\n", " ")
        authors = ", ".join(r.authors[:3]) if r.authors else "Unknown"
        year = str(r.year) if r.year else "n.d."
        lines.append(f'[{i}] "{r.title}" — {authors} ({year})\n    {snippet}')
    return "\n\n".join(lines)


def _build_prompt(project_name: str, resources: list[SavedResource]) -> str:
    n = len(resources)
    return f"""You are an academic writing assistant. Write a concise 150–300 word summary synthesising the key findings from the selected research papers listed below. Frame it around the research topic: "{project_name}".

SELECTED RESOURCES — use ONLY citation numbers [1] through [{n}]:

{_resource_block(resources)}

RULES:
1. Every factual claim must carry an inline [N] citation referencing the source.
2. Use only citation numbers [1] through [{n}]. Never invent a citation number.
3. Write 150–300 words total.
4. Do NOT include a reference list — write the summary body only.
5. Write in clear academic prose. Do not use bullet points.

Write the summary now:"""


def _validate_citations(text: str, n_resources: int) -> list[str]:
    seen: set[str] = set()
    invalid: list[str] = []
    for m in re.finditer(r'\[(\d+)\]', text):
        n = int(m.group(1))
        marker = m.group(0)
        if (n < 1 or n > n_resources) and marker not in seen:
            invalid.append(marker)
            seen.add(marker)
    return invalid


async def generate(
    db: firestore.Client,
    project_id: str,
    project_name: str,
    resource_ids: list[str],
    citation_style: str = "IEEE",
) -> SummaryResult:
    resources = [library.get_resource(db, project_id, rid) for rid in resource_ids]
    resources = [r for r in resources if r is not None]
    if not resources:
        raise ValueError("No valid resources selected.")

    if not await ollama.is_alive():
        raise OllamaUnavailableError()

    raw = await ollama.generate(_build_prompt(project_name, resources))

    invalid = _validate_citations(raw, len(resources))
    if invalid:
        return SummaryResult(text=None, invalid_markers=invalid)

    references = citations.build_bibliography(resources, citation_style)
    return SummaryResult(text=raw.strip(), references=references)
