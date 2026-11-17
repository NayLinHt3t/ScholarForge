# AI Logic — Where, How, Prove, Measure

## Where AI is used

| Feature | Backlog ID | File |
|---|---|---|
| Semantic search re-ranking (embedding cosine similarity) | BL-05, BL-06 | `app/services/search.py` |
| Idea/outline scaffold generation (RAG) | BL-18, BL-37, BL-38 | `app/services/outline.py`, `app/services/outline_sections.py` |
| Source summarization with inline citations | BL-40–BL-42 | `app/services/summary.py` |

AI provider is swappable: `app/clients/ollama.py` (local) or `app/clients/groq.py` (hosted free tier), selected by `AI_PROVIDER` in `app/config.py`. Embeddings: `nomic-embed-text` (Ollama) or `BAAI/bge-small-en-v1.5` run locally via FastEmbed (Groq mode — embeddings never leave the server even when generation is hosted). Generation: `llama3.2:3b` (Ollama) or `openai/gpt-oss-20b` (Groq).

## How it's built

- **Retrieval**: idea query + saved resources embedded, ranked by cosine similarity (`app/services/search.py`). Results below `SEARCH_LOW_CONFIDENCE_THRESHOLD` (single named constant, BL-43) trigger a "try rephrasing" notice instead of a generic empty state.
- **Generation (outline/summary)**: prompt is built only from the user's own saved resources for that project (`_resource_block`, `_build_full_prompt` / `_build_workspace_prompt` in `outline.py`) — the model is explicitly instructed to cite only `[1]`..`[N]` where N = number of selected resources, and retrieved abstracts are marked as data, not instructions, to resist prompt injection from paper content.
- **Validation (prevents hallucinated citations)**: `_validate_citations()` in both `app/services/outline.py` and `app/services/summary.py` parses every `[N]` marker in the model's output and rejects/retries generation if any marker falls outside `1..N`. This is the deterministic guardrail — the LLM never gets to invent a reference.

## Prove (test set, baseline, eval)

- **Test set**: `tests/test_services_search.py` (183 lines) — embedding/ranking/URL-resolution regression tests, 15/15 passing as of the last fix (search link resolution: DOI/arXiv prioritized over raw aggregator URLs).
- **Test set**: `tests/test_routes_outline.py` — exercises the outline generation route including citation-marker handling.
- **Test set**: `tests/test_services_claims.py` (104 lines) — evidence/claim-linking regression coverage.
- **Baseline**: pre-fix, search results linked to Semantic Scholar's own landing page (not the paper) or stale/missing CrossRef URLs — documented in `plan/test-plan-20261027-210029/`.
- **Run it yourself**: `pytest tests/ -v` (requires the venv with `pytest` installed per `requirements.txt`).
- **Known gap**: no automated eval harness scoring citation-validator false-negative rate (a hallucinated `[N]` slipping through) — current coverage is unit-level (parser correctness), not an end-to-end red-team eval. Flagged here rather than claimed as covered.

## Measure

- **Reliability guardrail**: 100% of generated outline/summary text passes `_validate_citations()` before being shown — any output that fails is discarded with a retry path, never silently shown to the user with a broken reference (BL-19, BL-41).
- **Latency**: structured logging records search/embedding/ranking/generation latency per request (see README "Engineering highlights") — no committed baseline numbers yet; capture during real-user test sessions (see Test Plan) rather than inventing a figure here.
- **Failure mode**: if the configured AI provider is unreachable, the UI surfaces a specific actionable error (BL-21) instead of a crash or silent hang — `app/clients/ai.py:unavailable_message()` picks the Ollama-specific message ("run `ollama serve`") when running locally, or a generic "try again in a minute" message for hosted providers; covered by `tests/test_simple_ui.py::TestAskRoute::test_ai_down_gives_helpful_error` and `TestSettings::test_settings_shows_ai_status`.
