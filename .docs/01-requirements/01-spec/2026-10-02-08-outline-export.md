# Spec: Outline Export

> **File:** `.docs/01-requirements/01-spec/2026-10-02-08-outline-export.md`
> **Date:** 2026-10-02
> **Pain notes summary:** Must-priority backlog row BL-23 covering PDF and Markdown/plain-text export of the generated outline, clearly labeled as a draft aid.
> **Open questions resolved:** 0 (BL-23 was sufficiently defined in the source backlog)

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| EXP-FR-01 | student | download my generated outline as a PDF and as a Markdown file | I have a portable starting point to continue writing in my own tool | Must | "Download as PDF" exports the outline as a single-column PDF containing: a visible draft label (see EXP-NFR-01) on every page, the project name as the title block, numbered IEEE sections with their bullet-point ideas and any draft passages (per BL-38 / GEN-FR-02 where present), and a numbered IEEE-format reference list; "Download as Markdown" exports the same content as plain Markdown text; both exports must complete within 15 s for a standard-length outline (4 IEEE sections + ≤ 20 references) on a local single-user deployment. | BL-23 |

## Non-Functional Requirements

| ID | Quality | Measure | Priority | BL ref |
|----|---------|---------|----------|--------|
| EXP-NFR-01 | Draft-label visibility | The label "DRAFT OUTLINE — FOR REFERENCE ONLY, NOT A SUBMISSION-READY PAPER" must appear on every page of the PDF export (header or footer); it must not appear only on the first page | Must | BL-23 |
| EXP-NFR-02 | Export latency | PDF and Markdown export must each complete within 15 s for a standard outline (4 IEEE sections, ≤ 20 saved references) on a local single-user deployment | Must | BL-23 |

## Legal / Compliance Requirements

*(None triggered — export reads and formats existing project-scoped data that is already stored; no new personal data is collected, no new external service is called, and the resulting file is written to the student's own filesystem.)*
