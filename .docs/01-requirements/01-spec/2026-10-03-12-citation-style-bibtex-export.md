# Spec: Citation Style Selector and BibTeX Export

> **File:** `.docs/01-requirements/01-spec/2026-10-03-12-citation-style-bibtex-export.md`
> **Date:** 2026-10-03
> **Pain notes summary:** Students need to switch citation style to match their assignment requirements, and need BibTeX export for use in LaTeX-based tools. The citation style is a single project-wide setting that applies to both the library view and the generated outline bibliography.
> **Open questions resolved:** 2 (Q4: citation style = one shared project-wide setting, applies to both library view BL-15 and outline bibliography BL-20; Q5: BibTeX export = one FR covering both per-resource and whole-library export at Should priority)

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| CITE-FR-03 | student | select one citation style (APA, MLA, Chicago, or IEEE) as a project-wide setting and have it applied consistently everywhere citations appear | I don't have to set the style separately in the library and in the outline — one choice governs both | Should | A citation-style selector (APA / MLA / Chicago / IEEE, default IEEE) is accessible within the project and persists as a field on the project record (stored server-side, not as a browser-local preference); changing the style immediately re-renders all citations in the current project's library view (the resource card citations from CITE-FR-01) without requiring a page reload or re-save of any resource; the same active style value is read by the outline-generation pipeline when building the bibliography section (BL-20 / SUMM-FR-02); if no style has been explicitly set for a project, IEEE is the default. | BL-15, BL-20 |
| CITE-FR-04 | student | export a BibTeX entry for a single saved resource, or export BibTeX for every resource in the current project's library at once | I can import citations directly into my LaTeX editor without manual transcription | Should | A "Copy BibTeX" or "Export BibTeX" action is available on each individual resource card in the library view; a "Export all as BibTeX" action is available at the library level for the current project; both actions produce valid BibTeX output where: (a) each entry has a unique cite-key derived from first-author surname + year (e.g. `Smith2023`); (b) each entry includes all available standard BibTeX fields (`author`, `title`, `year`, `journal` or `booktitle`, `volume`, `number`, `pages`, `doi`, `url`) — fields absent from the stored metadata are omitted entirely rather than populated with placeholder text; (c) the output passes BibTeX syntax validation (no malformed braces, no missing closing tokens); (d) per-resource "Copy BibTeX" copies to clipboard; per-resource "Export BibTeX" and library-level "Export all as BibTeX" download as a `.bib` file. | BL-16 |

## Non-Functional Requirements

| ID | Quality | Measure | Priority | BL ref |
|----|---------|---------|----------|--------|
| CITE-NFR-03 | Style-switch re-render latency | Switching citation style must re-render all visible resource cards in the current project's library within 500 ms of the user's selection, measured from the moment the selection event fires to the moment all visible cards display the new style, with the library containing up to 50 resources on a local single-user deployment | Should | BL-44 |
| CITE-NFR-04 | BibTeX syntax validity | Every BibTeX entry produced by CITE-FR-04 must be parseable by standard BibTeX processors (e.g. BibTeX, Biber) without errors; invalid characters in field values must be escaped per BibTeX conventions | Should | BL-45 |

## Legal / Compliance Requirements

*(None triggered — citation style is a project-level preference field; it contains no personal data beyond being tied to a project owned by a user (already governed by the erasure cascade in PROJ-LR-01 / BL-34). BibTeX export reads and re-formats stored bibliographic metadata already held under the same purpose; no new external service is called, no new data is collected, and no consent or signature flow is involved.)*
