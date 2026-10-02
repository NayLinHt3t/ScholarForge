# Spec: Citation Formatting

> **File:** `.docs/01-requirements/01-spec/2026-10-02-06-citation-formatting.md`
> **Date:** 2026-10-02
> **Pain notes summary:** Must-priority backlog rows BL-14 and BL-30 covering multi-style citation rendering and the exact IEEE numbered-citation format.
> **Open questions resolved:** 0 (BL-14 and BL-30 were fully specified in the source backlog and feature-list.md)

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| CITE-FR-01 | student | have each saved resource automatically formatted as a citation in APA, MLA, and IEEE styles | I don't have to format citations by hand | Must | Every saved resource renders a correctly formatted citation string in APA, MLA, and IEEE; the formatted string is derived deterministically from the stored metadata (no re-fetch); the citation is visible on the resource card in the library view; output must never contain "undefined", "null", "None", or empty repeated separators regardless of which metadata fields are absent (see CITE-NFR-02). | BL-14 |
| CITE-FR-02 | student | IEEE in-text citations numbered [1], [2], … in first-cited order with a matching reference-list entry | my outline and bibliography match IEEE conference paper conventions | Must | `toIEEE(resource, n)` produces: `[N] A. B. Author, "Title of paper," *Abbreviated Venue*, vol. X, no. Y, pp. ZZ–ZZ, Mon. Year.` For a preprint/arXiv source with no journal: `[N] A. Author, "Title," *arXiv preprint arXiv:XXXX.XXXXX*, Year.` Fields absent from the metadata are omitted silently (no placeholder text); reference numbers are assigned by order of first citation in the document, not alphabetical order. | BL-30 |

## Non-Functional Requirements

| ID | Quality | Measure | Priority | BL ref |
|----|---------|---------|----------|--------|
| CITE-NFR-01 | Determinism | Given identical resource metadata and the same citation number N, `toIEEE(resource, n)` must return a byte-for-byte identical string on every invocation; no non-deterministic field abbreviation or ordering | Must | BL-14, BL-30 |
| CITE-NFR-02 | No garbage output | Citation output in any supported style must never contain the literal strings "undefined", "null", "None", "NaN", or empty repeated separators (e.g. `", , ,"`) regardless of which metadata fields are absent | Must | BL-14, BL-30 |

## Legal / Compliance Requirements

*(None triggered — citation formatting is pure deterministic text transformation over stored metadata. No new personal data is collected, no external service is called, and no consent or signature flow is involved.)*
