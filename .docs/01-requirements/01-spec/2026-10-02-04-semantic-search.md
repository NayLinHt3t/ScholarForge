# Spec: Idea-Based Semantic Search

> **File:** `.docs/01-requirements/01-spec/2026-10-02-04-semantic-search.md`
> **Date:** 2026-10-02
> **Pain notes summary:** Must-priority backlog rows BL-05, BL-06, BL-07 covering free-text idea search, embedding-based re-ranking, and result-card display.
> **Open questions resolved:** 1 (search + re-rank end-to-end latency target → ≤ 8 s P95)

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| SRCH-FR-01 | student | type a research idea in plain language and receive a list of relevant papers | I don't need to know exact titles, authors, or keywords before I start | Must | A free-text idea input field accepts any plain-language phrase; on submit the system queries both Semantic Scholar and CrossRef APIs; a ranked list of candidate papers is returned; if only one API responds successfully, partial results from the responding API are shown rather than failing the whole request; if both APIs fail, a user-facing error is shown. | BL-05 |
| SRCH-FR-02 | student | see results ranked by conceptual relevance to my idea, not just keyword overlap | I find papers that match my concept even when I don't know the right academic terms | Must | After retrieval, all candidates are re-ranked by cosine similarity between a locally computed embedding of the idea text and each paper's title+abstract embedding; the student sees results in re-ranked order; raw API-returned order is not exposed. | BL-06 |
| SRCH-FR-03 | student | see enough detail per result to judge relevance without opening every link | I can quickly triage the list before deciding which papers to read or save | Must | Each result card displays: full title, author list, publication year, venue or source name, and an abstract excerpt of ≤ 300 characters (or the first 2 sentences, whichever is shorter). | BL-07 |

## Non-Functional Requirements

| ID | Quality | Measure | Priority | BL ref |
|----|---------|---------|----------|--------|
| SRCH-NFR-01 | End-to-end latency | Full search + re-rank pipeline (Semantic Scholar API + CrossRef API + local embedding computation) responds in ≤ 8 s at P95 for a single concurrent user on a local laptop deployment | Must | BL-05, BL-06 |
| SRCH-NFR-02 | Idea-text non-retention | The idea text submitted by the student must not be persisted in any database column or log record; it is transmitted to Semantic Scholar and CrossRef as a transient query parameter and discarded after the API response is processed | Must | BL-05 |

## Legal / Compliance Requirements

| ID | Law | Obligation | Concrete requirement | Applies to |
|----|-----|------------|---------------------|------------|
| SRCH-LR-01 | PDPA | Idea-text privacy | Idea text could reveal personal information (e.g. a health-related research topic); SRCH-NFR-02 is the implementing control; access logs must record the search event (timestamp, IP, user_id, endpoint) but must NOT include the idea text content in the log entry | SRCH-FR-01, SRCH-NFR-02 |
| SRCH-LR-02 | CCA §26 | Search-request logging | Each search request must generate an access-log entry containing: timestamp (UTC), source IP, user_id, action (search), endpoint — without the idea text content | SRCH-FR-01 |

### Legal watch items

- **SRCH-LW-01** (PDPA): Semantic Scholar and CrossRef receive the idea text as a search query string. Confirm that their terms of service and privacy policies permit this use case (plain academic search query; no user account data is passed) before the app is used with real users. Flag to a human if either service's terms restrict this type of automated querying.
