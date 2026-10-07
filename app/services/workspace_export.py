"""Markdown export for the research workspace (FR-100, FR-101, FR-103)."""
from datetime import datetime, timezone

from app.models.claim import Claim
from app.models.evidence import Evidence
from app.models.note import Note
from app.models.outline_section import OutlineSection
from app.models.project import Project
from app.models.resource import SavedResource
from app.models.theme import Theme
from app.services.citations import format_one

_HEADER = (
    "ScholarForge Research Export — {name} — {date}\n"
    "This is an organizational scaffold. The student's written paper is not included.\n"
)


def _fmt_authors(authors: list[str]) -> str:
    if not authors:
        return "Unknown authors"
    if len(authors) <= 3:
        return ", ".join(authors)
    return ", ".join(authors[:3]) + " et al."


def export_full_structure(
    project: Project,
    sources: list[SavedResource],
    evidence_items: list[Evidence],
    notes: list[Note],
    themes: list[Theme],
    claims: list[Claim],
    sections: list[OutlineSection],
) -> str:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines: list[str] = []

    lines += [
        _HEADER.format(name=project.name, date=date_str),
        f"# {project.name}",
        "",
    ]
    if project.research_question:
        lines += [f"**Research Question:** {project.research_question}", ""]

    # ── Sources ──
    lines += ["---", "## Sources", ""]
    if sources:
        source_map = {s.id: s for s in sources}
        for s in sources:
            citation = format_one(s, project.citation_style)
            ev_count = sum(1 for e in evidence_items if e.source_id == s.id)
            lines += [
                f"### {s.title}",
                f"- **Type:** {s.source_type.replace('_', ' ').title()}",
                f"- **Status:** {s.read_status.capitalize()}",
                f"- **Citation:** {citation}",
            ]
            if s.url:
                lines += [f"- **URL:** {s.url}"]
            if s.doi:
                lines += [f"- **DOI:** {s.doi}"]
            if s.abstract:
                lines += [f"- **Abstract:** {s.abstract[:400]}{'…' if len(s.abstract) > 400 else ''}"]
            if s.source_note:
                lines += [f"- **Note:** {s.source_note}"]
            lines += [f"- **Evidence items:** {ev_count}", ""]
    else:
        lines += ["*No sources added yet.*", ""]

    # ── Evidence ──
    lines += ["---", "## Evidence", ""]
    if evidence_items:
        source_map = {s.id: s for s in sources}
        for e in evidence_items:
            src = source_map.get(e.source_id)
            src_title = src.title if src else "Unknown source"
            lines += [f'> “{e.quote}”']
            lines += [f'— *{src_title}*' + (f', p. {e.page_reference}' if e.page_reference else '')]
            if e.student_note:
                lines += [f"**Note:** {e.student_note}"]
            lines += [""]
    else:
        lines += ["*No evidence extracted yet.*", ""]

    # ── Notes ──
    lines += ["---", "## Research Notes", ""]
    if notes:
        for n in notes:
            if n.title:
                lines += [f"### {n.title}"]
            lines += [n.body, ""]
    else:
        lines += ["*No notes yet.*", ""]

    # ── Themes ──
    lines += ["---", "## Themes", ""]
    if themes:
        ev_map = {e.id: e for e in evidence_items}
        src_map = {s.id: s for s in sources}
        for t in themes:
            lines += [f"### {t.name}"]
            if t.description:
                lines += [t.description]
            lines += [f"*{len(t.evidence_ids)} evidence item(s) linked*", ""]
            for eid in t.evidence_ids:
                ev = ev_map.get(eid)
                if ev:
                    src = src_map.get(ev.source_id)
                    lines += [f'- "{ev.quote[:120]}{"…" if len(ev.quote) > 120 else ""}" — *{src.title if src else "?"}*']
            lines += [""]
    else:
        lines += ["*No themes created yet.*", ""]

    # ── Claims ──
    lines += ["---", "## Claims", ""]
    if claims:
        ev_map = {e.id: e for e in evidence_items}
        src_map = {s.id: s for s in sources}
        theme_map = {t.id: t for t in themes}
        for c in claims:
            has_support = bool(c.evidence_ids or c.theme_ids)
            lines += [f"### {c.statement}"]
            if not has_support:
                lines += ["⚠️ *No evidence linked*"]
            if c.theme_ids:
                theme_names = [theme_map[tid].name for tid in c.theme_ids if tid in theme_map]
                lines += [f"**Themes:** {', '.join(theme_names)}"]
            if c.evidence_ids:
                lines += ["**Supporting evidence:**"]
                for eid in c.evidence_ids:
                    ev = ev_map.get(eid)
                    if ev:
                        src = src_map.get(ev.source_id)
                        lines += [f'- "{ev.quote[:120]}{"…" if len(ev.quote) > 120 else ""}" — *{src.title if src else "?"}*']
            lines += [""]
    else:
        lines += ["*No claims created yet.*", ""]

    # ── Outline ──
    lines += ["---", "## Outline", ""]
    if sections:
        ev_map = {e.id: e for e in evidence_items}
        src_map = {s.id: s for s in sources}
        claim_map = {c.id: c for c in claims}
        for sec in sections:
            has_content = bool(sec.claim_ids or sec.evidence_ids)
            lines += [f"### {sec.title}"]
            if not has_content:
                lines += ["⚠️ *No claims or evidence linked*"]
            if sec.writing_notes:
                lines += [f"**Planning notes:** {sec.writing_notes}"]
            if sec.claim_ids:
                lines += ["**Claims:**"]
                for cid in sec.claim_ids:
                    cl = claim_map.get(cid)
                    if cl:
                        lines += [f"- {cl.statement}"]
            if sec.evidence_ids:
                lines += ["**Evidence:**"]
                for eid in sec.evidence_ids:
                    ev = ev_map.get(eid)
                    if ev:
                        src = src_map.get(ev.source_id)
                        lines += [f'- "{ev.quote[:120]}{"…" if len(ev.quote) > 120 else ""}" — *{src.title if src else "?"}*']
            lines += [""]
    else:
        lines += ["*No outline sections yet.*", ""]

    return "\n".join(lines)


def export_outline_scaffold(
    project: Project,
    sources: list[SavedResource],
    evidence_items: list[Evidence],
    claims: list[Claim],
    sections: list[OutlineSection],
) -> str:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines: list[str] = [
        _HEADER.format(name=project.name, date=date_str),
        f"# {project.name} — Outline Scaffold",
        "",
    ]
    if project.research_question:
        lines += [f"**Research Question:** {project.research_question}", ""]

    if not sections:
        lines += ["*No outline sections yet.*"]
        return "\n".join(lines)

    ev_map = {e.id: e for e in evidence_items}
    src_map = {s.id: s for s in sources}
    claim_map = {c.id: c for c in claims}

    for sec in sections:
        lines += [f"## {sec.title}"]
        if sec.writing_notes:
            lines += [f"> **Planning notes:** {sec.writing_notes}", ""]
        if sec.claim_ids:
            lines += ["**Arguments to make:**"]
            for cid in sec.claim_ids:
                cl = claim_map.get(cid)
                if cl:
                    lines += [f"- {cl.statement}"]
            lines += [""]
        if sec.evidence_ids:
            lines += ["**Evidence to use:**"]
            for eid in sec.evidence_ids:
                ev = ev_map.get(eid)
                if ev:
                    src = src_map.get(ev.source_id)
                    ref = f", p. {ev.page_reference}" if ev.page_reference else ""
                    lines += [f'- "{ev.quote}" — *{src.title if src else "?"}*{ref}']
            lines += [""]
        if not sec.claim_ids and not sec.evidence_ids:
            lines += ["⚠️ *Nothing linked to this section yet.*", ""]

    return "\n".join(lines)
