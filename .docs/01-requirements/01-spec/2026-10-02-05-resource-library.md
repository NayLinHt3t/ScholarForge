# Spec: Personal Resource Library

> **File:** `.docs/01-requirements/01-spec/2026-10-02-05-resource-library.md`
> **Date:** 2026-10-02
> **Pain notes summary:** Must-priority backlog rows BL-10 – BL-13 covering save, deduplication, per-item removal with outline healing, and cross-session persistence.
> **Open questions resolved:** 2 (deduplication fallback for papers with no DOI/arXiv → allow save with warning; graceful outline handling on resource delete → strip [N] markers and renumber remaining citations)

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| LIB-FR-01 | student | save a search result into the current project's library | I can return to it later without repeating the search | Must | "Save" action persists the paper's normalized metadata (title, authors, year, venue, abstract, DOI and arXiv ID where available) and its embedding vector, tagged to the current project_id and user_id; a success indicator is shown immediately after the row is committed. | BL-10 |
| LIB-FR-02 | student | be prevented from saving the same paper twice within one project | the project library stays clean without manual deduplication | Must | Before committing a save, the system checks for an existing row with the same (project_id, doi) or (project_id, arxiv_id); if a duplicate is detected, the save is blocked and the student sees: "This paper is already in your library for this project." The same paper may be saved in a different project without restriction. If the paper has neither a DOI nor an arXiv ID, the save proceeds and a persistent warning is shown on the saved item: "No DOI or arXiv ID — duplicate detection is unavailable for this source." | BL-11 |
| LIB-FR-03 | student | view and remove individual resources from a project's library | I can curate the library as the project evolves | Must | Library view lists only the current project's saved resources; each item has a "Remove" action; on removal: (1) the resource row is deleted, (2) every [N] citation marker for that resource in any saved outline for this project is stripped from the outline text, and all remaining [N] markers are renumbered to maintain continuous [1], [2], … ordering; the student receives a notification if any outlines were affected ("N outline(s) updated: citation removed and renumbered"). | BL-12 |
| LIB-FR-04 | student | have the project library available every time I return to the project | it represents my ongoing work, not just the current session | Must | Saved resources are stored persistently in the database; after logout and login on the same account, the library contents for each project are identical to what they were before logout. | BL-13 |

## Non-Functional Requirements

| ID | Quality | Measure | Priority | BL ref |
|----|---------|---------|----------|--------|
| LIB-NFR-01 | Deduplication integrity | Duplicate detection must be enforced by database-level unique constraints on (project_id, doi) and (project_id, arxiv_id) — not only application-layer logic — to prevent race conditions on concurrent save requests | Must | BL-11 |

## Legal / Compliance Requirements

| ID | Law | Obligation | Concrete requirement | Applies to |
|----|-----|------------|---------------------|------------|
| LIB-LR-01 | PDPA | Library-data erasure path | Bibliographic metadata is personal account data linked via project_id; it must be deletable per-item (LIB-FR-03) and in bulk via project deletion cascade (PROJ-FR-02 / BL-34); no orphaned saved_resources rows may remain after the owning project is deleted | LIB-FR-03 |
| LIB-LR-02 | CCA §26 | Library-action logging | Save and remove actions must each generate an access-log entry containing: timestamp (UTC), source IP, user_id, action (save-resource / remove-resource), project_id, resource_id; the full bibliographic metadata content must not be included in the log entry | LIB-FR-01, LIB-FR-03 |
