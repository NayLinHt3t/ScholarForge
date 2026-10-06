# Spec: Search Low-Confidence Feedback

> **File:** `.docs/01-requirements/01-spec/2026-10-03-11-search-low-confidence.md`
> **Date:** 2026-10-03
> **Pain notes summary:** Students see a blank results list when their search idea is too vague or misses all papers, with no guidance on what to do next. A threshold-based "try rephrasing" message should appear when results are empty or all results score below the cosine-similarity threshold.
> **Open questions resolved:** 1 (trigger condition = zero results OR all results below a defined cosine-similarity threshold, e.g. 0.25; message is "try rephrasing your idea")

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| SRCH-FR-04 | student | see a clear "try rephrasing your idea" message when my search returns no useful results | I know the search ran successfully but found nothing relevant, and I know what action to take | Should | After the search and re-ranking pipeline (SRCH-FR-01, SRCH-FR-02) complete: (a) if zero papers are returned from both APIs, display the message "No results found. Try rephrasing your idea with different keywords or a more specific question."; (b) if one or more papers are returned but every paper's cosine-similarity score falls below the configured threshold (default 0.25), display the message "No closely matching results found. Try rephrasing your idea to get better matches." and do not show the low-scoring results; (c) if at least one paper scores at or above the threshold, display results as normal with no message; the threshold value (0.25) must be defined as a named configuration constant, not a magic number in the search pipeline. | BL-08 |

## Non-Functional Requirements

| ID | Quality | Measure | Priority | BL ref |
|----|---------|---------|----------|--------|
| SRCH-NFR-03 | Threshold configurability | The cosine-similarity threshold used in SRCH-FR-04(b) must be defined as a single named constant in the application configuration (e.g. `SEARCH_RELEVANCE_THRESHOLD = 0.25`); changing the value must require editing only that one location and restarting the server — no code changes required elsewhere | Should | BL-43 |

## Legal / Compliance Requirements

*(None triggered — SRCH-FR-04 operates entirely over already-computed embedding scores; it introduces no new personal data field, no new external API call, no new log endpoint, and no consent or signature flow. The same logging obligation from SRCH-LR-02 already covers every search request; SRCH-FR-04 does not alter what is logged.)*
