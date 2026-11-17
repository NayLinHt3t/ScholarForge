# Comparison Table — Before / After

Source rows: [project-charter.md §9](../00-charter/project-charter.md), backlog acceptance criteria in [backlog.md](../01-requirements/backlog.md). "Measured with" / "Evidence" columns for rows not yet backed by a committed test or log are marked **TODO** — fill from the Test Plan's before/after numbers once real-user sessions run; do not fill with invented numbers.

| Item | Before | After | Change | Measured with | Evidence |
|---|---|---|---|---|---|
| Paper discovery | Exact keyword/title match only | Idea described in plain language, ranked by embedding cosine similarity | Finds conceptually relevant papers keyword search misses | Manual test query + result inspection | `app/services/search.py`; regression tests `tests/test_services_search.py` |
| Source tracking | Scattered across bookmarks/notes/separate tools | One project-scoped library, duplicate-detected per project | Single source of truth per assignment | Code inspection (BL-10–BL-13) | `tests/test_services_library.py` |
| Citation formatting | Hand-formatted APA/MLA/Chicago/IEEE | Auto-rendered on save; instant style switch; BibTeX export | Time/errors removed from citation formatting | Unit tests on citation renderers | `tests/test_citations.py`, backlog BL-14–BL-17, BL-30 |
| First-draft outline | Blank page | IEEE-structured scaffold (bullets + draft paragraph) grounded in saved sources, with citation validation | Removes blank-page start | Code inspection + citation-validator tests | `app/services/outline.py` `_validate_citations`; `tests/test_routes_outline.py` |
| Citation trust in generated text | N/A (no generation existed) | Every `[N]` marker validated against actual saved resources; invalid output discarded with retry | Zero hallucinated references reach the user | Unit test on validator | `app/services/outline.py`, `app/services/summary.py` |
| Data/account privacy | Third-party login + cloud AI vendor, in comparable tools | Local account system; AI provider configurable (local Ollama or Groq free tier), no third-party identity provider either way | No forced third-party login | Code inspection | `app/config.py` `AI_PROVIDER`; README |
| Project isolation | N/A | Deleting one project never touches another's resources/outlines | Prevents cross-assignment data mixing | Unit test on cascade delete | `tests/test_services_projects.py` |
| **AI row** — outline/summary generation quality & trust | No AI assistance; manual synthesis of sources | RAG-generated scaffold/summary, citation-marker validated before display | See [ai-logic.md](ai-logic.md) for full Prove/Measure detail | Unit tests (validator) | `ai-logic.md` |
