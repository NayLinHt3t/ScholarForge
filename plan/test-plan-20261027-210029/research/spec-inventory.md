# Spec Inventory (source: .docs/01-requirements/01-spec/)

14 spec files. Each row below is one testable requirement ID pulled from the spec tables. Full acceptance criteria live in the original spec files — this is an index, not a copy.

## 01 — Outline Generation Enhancements
- GEN-FR-01 — project name as IEEE title, read-only, verbatim in copy/export
- GEN-FR-02 — per-section draft paragraph (2–4 sentences), citation-validated, read-only

## 02 — Account & Authentication
- AUTH-FR-01 — signup (unique email, bcrypt ≥12, no plaintext anywhere)
- AUTH-FR-02 — login (session cookie HttpOnly/SameSite=Lax/30d, generic 401 on failure)
- AUTH-FR-03 — logout (sync server-side invalidation, cookie cleared, reuse → 401)
- AUTH-FR-04 — per-account data isolation (user_id-scoped queries, 401/403 on violation)
- AUTH-FR-05 — account deletion (cascade sessions→projects→resources/outlines→user, atomic, re-type-email confirm)
- AUTH-NFR-01 — bcrypt cost ≥12, no plaintext persistence
- AUTH-NFR-02 — cookie hygiene, Secure flag off-localhost
- AUTH-LR-01/02/03 — PDPA legal basis record, erasure cascade, access-log (signup/login/logout)
- AUTH-LW-01 — consent checkbox evidence (watch item, not yet built)

## 03 — Project Management
- PROJ-FR-01 — project-scoped actions (search/save/generate/list/delete)
- PROJ-FR-02 — project delete w/ confirmation, atomic cascade
- PROJ-NFR-01/02 — DB-level FK ownership, atomic transaction
- PROJ-LR-01/02 — per-project erasure (excludes access logs), action logging

## 04 — Semantic Search
- SRCH-FR-01 — free-text idea search, dual-API (Semantic Scholar + CrossRef), partial-failure handling
- SRCH-FR-02 — cosine-similarity re-rank, raw API order hidden
- SRCH-FR-03 — result card fields (title/authors/year/venue/abstract ≤300 chars)
- SRCH-NFR-01 — ≤8s P95 latency
- SRCH-NFR-02 — idea text never persisted/logged
- SRCH-LR-01/02 — idea-text privacy, search-request logging (no idea text content)

## 05 — Resource Library
- LIB-FR-01 — save result to project library
- LIB-FR-02 — duplicate detection (DOI/arXiv), no-ID warning path
- LIB-FR-03 — remove resource, outline citation strip+renumber, notification
- LIB-FR-04 — persistence across logout/login
- LIB-NFR-01 — DB-level unique constraint (project_id, doi/arxiv_id)
- LIB-LR-01/02 — erasure path, save/remove action logging

## 06 — Citation Formatting
- CITE-FR-01 — APA/MLA/IEEE auto-render, no garbage tokens
- CITE-FR-02 — IEEE `[N]` numbering, first-cited order, arXiv variant
- CITE-NFR-01/02 — determinism, no "undefined"/"null"/"None"/"NaN"/empty separators

## 07 — Outline Generation Core Reliability
- GENC-FR-01 — 100% citation-marker validation, reject whole outline on any invalid marker
- GENC-FR-02 — Ollama liveness ping (5s timeout), actionable error, non-blocking UI
- GENC-NFR-01/02 — full-coverage validation, bounded ping latency

## 08 — Outline Export
- EXP-FR-01 — PDF + Markdown export (title, sections, bullets, draft passages, references)
- EXP-NFR-01 — draft label on every PDF page
- EXP-NFR-02 — export ≤15s for standard outline

## 09 — Compliance (Logging & Data Protection)
- COMP-FR-01 — request-logging middleware (every endpoint, no exemptions)
- COMP-FR-02 — PDPA data minimisation/storage/erasure
- COMP-NFR-01/02 — ≥90-day retention, append-only, isolated log store
- COMP-LW-01 — breach-notification procedure (org-level, watch item)

## 10 — Source Summarization
- SUMM-FR-01 — multi-select sources (checklist, ≥1 required)
- SUMM-FR-02 — 150–300 word summary, project-name header, inline `[N]`, style-matched reference list
- SUMM-FR-03 — citation-validator (same contract as GENC-FR-01), discard+retry on failure
- SUMM-FR-04 — copy summary (body + citations + references), read-only
- SUMM-NFR-01/02/03/04 — 100% citation fidelity, local-only Ollama call, graceful failure, 150–300 word band

## 11 — Search Low-Confidence Feedback
- SRCH-FR-04 — "try rephrasing" message (zero results vs. all-below-threshold), "Low relevance" badge, threshold never hides cards
- SRCH-NFR-03 — threshold as named config constant

## 12 — Citation Style Selector & BibTeX Export
- CITE-FR-03 — project-wide style selector (APA/MLA/Chicago/IEEE), live re-render, default IEEE
- CITE-FR-04 — per-resource + whole-library BibTeX export, valid syntax, omitted-not-placeholder fields
- CITE-NFR-03/04 — ≤500ms re-render @50 resources, BibTeX parses clean

## 13 — Project Switcher, Per-Section Regen, Consent Recording
- PROJ-FR-03 — "Back to projects" link on every in-project page, no stale data on switch
- GEN-FR-03 — per-section regeneration, other sections byte-identical, same validator gate
- AUTH-FR-06 — signup consent checkbox + `consent_records` write (user_id, version, timestamp, action)
- GEN-NFR-01 — byte-level isolation of unregenerated sections
- AUTH-NFR-03 — consent_records immutable, survives account deletion
- AUTH-LR-04/05/06 — ETA §9 evidence, consent scope snapshot, signup access-log

## 14 — Search Quality (Cap, Badges, Access Warning)
- SRCH-FR-05 — open-access badge (Open access / Paywalled / Access unknown) on result + library cards
- SRCH-FR-06 — "Open access only" toggle filter, resets per search
- RELY-FR-01 — pre-generation blocking modal for non-open-access sources, "Proceed anyway" / "Go back"
- SRCH-NFR-04 — 20-card display cap, named config constant
