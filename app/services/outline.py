import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from google.cloud import firestore

from app.clients import ollama
from app.collections import OUTLINES, PROJECTS
from app.exceptions import OllamaUnavailableError
from app.models import Outline, SavedResource
from app.services import citations, library

SECTION_ORDER = [
    "title", "abstract", "index_terms",
    "introduction", "related_work", "methodology", "contribution", "references",
]

SECTION_DISPLAY_NAMES = {
    "title": "Title",
    "abstract": "Abstract",
    "index_terms": "Index Terms",
    "introduction": "I. Introduction",
    "related_work": "II. Related Work",
    "methodology": "III. Proposed Methodology",
    "contribution": "IV. Expected Contribution",
    "references": "References",
}

# Sections eligible for per-section regeneration (references are built deterministically)
REGENERABLE_SECTIONS = {"abstract", "index_terms", "introduction", "related_work", "methodology", "contribution"}


@dataclass
class GenerationResult:
    outline: Outline | None
    invalid_markers: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.outline is not None


# ── prompt builders ────────────────────────────────────────────────────────────

def _resource_block(resources: list[SavedResource], abstract_chars: int = 200) -> str:
    lines = []
    for i, r in enumerate(resources, 1):
        snippet = (r.abstract or "")[:abstract_chars].replace("\n", " ")
        authors = ", ".join(r.authors[:3]) if r.authors else "Unknown"
        year = str(r.year) if r.year else "n.d."
        lines.append(f'[{i}] "{r.title}" — {authors} ({year})\n    {snippet}')
    return "\n\n".join(lines)


def _build_full_prompt(resources: list[SavedResource]) -> str:
    n = len(resources)
    return f"""You are an academic writing assistant. Generate a structured IEEE paper outline scaffold.

SAVED RESOURCES — use ONLY citation numbers [1] through [{n}]:

{_resource_block(resources)}

RULES:
1. Never use a citation number higher than {n} or lower than 1.
2. Every section (abstract, introduction, related work, methodology, contribution) must include at least one [N] citation.
3. Each body section has 2–3 bullet points followed by a DRAFT: passage of 2–4 sentences.
4. Start the draft passage with the exact text "DRAFT: ".

Output using EXACTLY these section markers and no others:

[SECTION: title]
(suggested paper title)

[SECTION: abstract]
(3–4 sentence abstract with [N] citations)

[SECTION: index_terms]
(5–8 comma-separated keywords)

[SECTION: introduction]
- (bullet point with [N] citation)
- (bullet point with [N] citation)
- (bullet point with [N] citation)
DRAFT: (2–4 sentence draft with [N] citations)

[SECTION: related_work]
- (bullet point with [N] citation)
- (bullet point with [N] citation)
- (bullet point with [N] citation)
DRAFT: (2–4 sentence draft with [N] citations)

[SECTION: methodology]
- (bullet point with [N] citation)
- (bullet point with [N] citation)
- (bullet point with [N] citation)
DRAFT: (2–4 sentence draft with [N] citations)

[SECTION: contribution]
- (bullet point with [N] citation)
- (bullet point with [N] citation)
- (bullet point with [N] citation)
DRAFT: (2–4 sentence draft with [N] citations)"""


def _build_section_prompt(
    resources: list[SavedResource],
    section_key: str,
    existing_sections: dict[str, str],
) -> str:
    n = len(resources)
    label = SECTION_DISPLAY_NAMES.get(section_key, section_key)
    title = existing_sections.get("title", "(untitled)")

    if section_key == "abstract":
        fmt = "(3–4 sentence abstract with [N] citations)"
    elif section_key == "index_terms":
        fmt = "(5–8 comma-separated keywords)"
    else:
        fmt = (
            "- (bullet point with [N] citation)\n"
            "- (bullet point with [N] citation)\n"
            "- (bullet point with [N] citation)\n"
            "DRAFT: (2–4 sentence draft with [N] citations)"
        )

    return f"""You are an academic writing assistant. Regenerate only the {label} section.

PAPER TITLE: {title}

RESOURCES — use ONLY [1] through [{n}]:
{_resource_block(resources, abstract_chars=150)}

Output ONLY the section below, using this exact marker:

[SECTION: {section_key}]
{fmt}"""


# ── parsing & validation ───────────────────────────────────────────────────────

def _parse_sections(text: str) -> dict[str, str]:
    parts = re.split(r'\[SECTION:\s*(\w+)\]', text, flags=re.IGNORECASE)
    sections: dict[str, str] = {}
    for i in range(1, len(parts) - 1, 2):
        key = parts[i].strip().lower()
        sections[key] = parts[i + 1].strip()
    return sections


def _validate_citations(sections: dict[str, str], n_resources: int) -> list[str]:
    combined = " ".join(sections.values())
    seen: set[str] = set()
    invalid: list[str] = []
    for m in re.finditer(r'\[(\d+)\]', combined):
        n = int(m.group(1))
        marker = m.group(0)
        if (n < 1 or n > n_resources) and marker not in seen:
            invalid.append(marker)
            seen.add(marker)
    return invalid


def _render_full_text(sections: dict[str, str]) -> str:
    chunks = []
    for key in SECTION_ORDER:
        if key not in sections or not sections[key]:
            continue
        label = SECTION_DISPLAY_NAMES.get(key, key.upper())
        content = sections[key]
        if key == "title":
            chunks.append(f"# {content}")
        else:
            chunks.append(f"\n{label}\n{content}")
    return "\n".join(chunks)


# ── Firestore helpers ──────────────────────────────────────────────────────────

def _outlines_ref(db: firestore.Client, project_id: str):
    return db.collection(PROJECTS).document(project_id).collection(OUTLINES)


def _save(
    db: firestore.Client,
    project_id: str,
    sections: dict[str, str],
    cited_ids: list[str],
    citation_style: str,
) -> Outline:
    ref = _outlines_ref(db, project_id).document()
    content = _render_full_text(sections)
    outline = Outline(
        id=ref.id,
        project_id=project_id,
        label=(sections.get("title") or "Untitled")[:80],
        citation_style=citation_style,
        content=content,
        sections=sections,
        cited_resource_ids=cited_ids,
    )
    ref.set(outline.to_firestore())
    return outline


def list_outlines(db: firestore.Client, project_id: str) -> list[Outline]:
    docs = _outlines_ref(db, project_id).get()
    outlines = [Outline.from_firestore(doc) for doc in docs]
    return sorted(outlines, key=lambda o: o.created_at, reverse=True)


def get_outline(db: firestore.Client, project_id: str, outline_id: str) -> Outline | None:
    doc = _outlines_ref(db, project_id).document(outline_id).get()
    return Outline.from_firestore(doc) if doc.exists else None


def delete_outline(db: firestore.Client, project_id: str, outline_id: str) -> None:
    _outlines_ref(db, project_id).document(outline_id).delete()


# ── generation pipeline ────────────────────────────────────────────────────────

async def generate(
    db: firestore.Client,
    project_id: str,
    citation_style: str = "IEEE",
) -> GenerationResult:
    resources = library.list_resources(db, project_id)
    if not resources:
        raise ValueError("No saved resources to generate from.")

    if not await ollama.is_alive():
        raise OllamaUnavailableError()

    raw = await ollama.generate(_build_full_prompt(resources))
    sections = _parse_sections(raw)

    if not sections:
        sections = {"introduction": raw.strip()}

    invalid = _validate_citations(
        {k: v for k, v in sections.items() if k != "references"},
        len(resources),
    )
    if invalid:
        return GenerationResult(outline=None, invalid_markers=invalid)

    # Build bibliography deterministically — never from LLM output
    sections["references"] = citations.build_bibliography(resources, citation_style)

    cited_ids = [r.id for r in resources]
    outline = _save(db, project_id, sections, cited_ids, citation_style)
    return GenerationResult(outline=outline)


async def regenerate_section(
    db: firestore.Client,
    project_id: str,
    outline_id: str,
    section_key: str,
) -> GenerationResult:
    outline = get_outline(db, project_id, outline_id)
    if not outline:
        raise ValueError("Outline not found.")
    if section_key not in REGENERABLE_SECTIONS:
        raise ValueError(f"Section '{section_key}' cannot be regenerated.")

    resources = library.list_resources(db, project_id)
    if not await ollama.is_alive():
        raise OllamaUnavailableError()

    raw = await ollama.generate(_build_section_prompt(resources, section_key, outline.sections))
    new_sections = _parse_sections(raw)
    new_content = new_sections.get(section_key, raw.strip())

    invalid = _validate_citations({section_key: new_content}, len(resources))
    if invalid:
        return GenerationResult(outline=None, invalid_markers=invalid)

    # Update only the targeted section — all others byte-for-byte unchanged (BL-46)
    updated_sections = dict(outline.sections)
    updated_sections[section_key] = new_content
    updated_content = _render_full_text(updated_sections)

    now = datetime.now(timezone.utc)
    _outlines_ref(db, project_id).document(outline_id).update({
        f"sections.{section_key}": new_content,
        "content": updated_content,
        "updated_at": now,
    })

    updated = get_outline(db, project_id, outline_id)
    return GenerationResult(outline=updated)
