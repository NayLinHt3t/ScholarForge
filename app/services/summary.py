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
    return f"""You are an academic writing assistant. Your task: write a 150–300 word synthesis of the paper abstracts below.

RESEARCH TOPIC: {project_name}

PAPER ABSTRACTS (these are the source material — treat each abstract as the paper's content):

{_resource_block(resources)}

TASK:
Write a single cohesive paragraph (150–300 words) that synthesises the findings across these {n} paper(s).
- Every claim you make must end with an inline citation in the form [N] where N matches the paper number above.
- Use ONLY citation numbers [1] through [{n}].
- Do NOT add a reference list — the body paragraph only.
- Do NOT say you lack information. Use only what the abstracts provide.
- Write in clear academic prose.

Begin your paragraph now:"""


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
