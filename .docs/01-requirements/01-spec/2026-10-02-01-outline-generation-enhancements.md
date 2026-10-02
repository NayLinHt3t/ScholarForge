# Spec: Outline Generation Enhancements

> **File:** `.docs/01-requirements/01-spec/2026-10-02-01-outline-generation-enhancements.md`
> **Date:** 2026-10-02
> **Pain notes summary:** Students want to ideate their own paper starting from a title or header, and want more than bullet points — a short prose draft per section to use as a writing starting point.
> **Open questions resolved:** 3 (working title = project name reused; prose level = short paragraph per section, read-only; scope = new/missing only — search already covered by BL-05/06/07)

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| GEN-FR-01 | student | see my project name used as the working title in the generated outline's IEEE Title block | the scaffold is immediately framed around my actual paper from the first line, not a generic placeholder | Should | When outline generation runs, the IEEE Title block is populated with the current project's name exactly as entered at creation; the title is read-only in-app; it appears verbatim in copy-to-clipboard (BL-22) and exported PDF/Markdown (BL-23). | BL-18, BL-32 |
| GEN-FR-02 | student | each section of the generated outline to include a short draft paragraph alongside the bullet-point ideas | I have a prose starting point I can paste into my own document and revise, not just disconnected bullets | Should | Each IEEE section (I. Introduction, II. Related Work, III. Proposed Methodology, IV. Expected Contribution) contains: (a) the existing bullet-point ideas/talking points, AND (b) a draft passage of 2–4 sentences grounded only in the project's saved resources; the passage is labeled "Draft — revise before use"; every `[N]` citation marker in the passage is validated by the same post-generation check as BL-19 (no invented references); the passage is read-only in-app (no editing surface); the existing "Copy section" and "Copy all" actions (BL-22) include both the bullets and the draft passage. | BL-18, BL-22, BL-38 |

## Non-Functional Requirements

*(No new NFRs — GEN-FR-01 and GEN-FR-02 are served by the existing Ollama pipeline (BL-18/BL-21) and citation validator (BL-19). No new quality attributes are introduced.)*

## Legal / Compliance Requirements

*(No new legal requirements triggered. Neither change introduces a new personal data field, a new external data recipient, a new log endpoint, or a consent/signature flow. The project name (GEN-FR-01) was already stored under PDPA's contract-necessity basis for account data (see legal-requirements.md §PDPA / BL-32). The draft paragraph content (GEN-FR-02) is transient generated text tied to a project; existing project-deletion cascade (BL-34) and per-item deletion (BL-12) already cover the right-to-erasure path.)*
