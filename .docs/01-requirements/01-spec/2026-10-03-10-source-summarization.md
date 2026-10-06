# Spec: Source Summarization with Cited References

> **File:** `.docs/01-requirements/01-spec/2026-10-03-10-source-summarization.md`
> **Date:** 2026-10-03
> **Pain notes summary:** Students want to select specific saved papers from their project library and get a concise summary of those sources, with every claim in the summary citing the exact source it came from.
> **Open questions resolved:** 3 (scope = user-selected subset only, not whole library; citations = inline [N] markers matching the project's chosen citation style; output = read-only, copy-able, not a replacement for outline generation)

---

## Functional Requirements

| ID | As a… | I want to… | So that… | Priority | Acceptance Criteria | BL ref |
|----|-------|------------|----------|----------|---------------------|--------|
| SUMM-FR-01 | student | select one or more saved resources from the current project's library before generating a summary | the summary is grounded only in the papers I actually chose, not the entire library | Must | The source-selection UI presents the current project's saved resources as a checklist (title + authors + year per row); the student must check at least one item; the "Summarize" action is disabled until at least one source is selected; the set of selected resource IDs is passed verbatim to the generation pipeline — no other resources are used. | BL-40 |
| SUMM-FR-02 | student | receive a concise written summary of the selected sources, headed by my project's name | I can quickly understand what those papers collectively say without reading each one in full, and the summary is immediately framed around my actual research topic | Must | The generated summary is headed by the current project's name exactly as entered at creation (same title-reuse rule as GEN-FR-01); the title is read-only and appears verbatim in the copy-to-clipboard output; the generation pipeline then sends the selected resources' title + abstract metadata (no full-text fetch) to the local Ollama model and produces a body of 150–300 words; the body synthesises across the selected papers and must not introduce claims absent from the supplied metadata; every factual claim is followed by an inline citation marker (`[N]`) referencing the source that supports it; the style of the `[N]` reference list appended at the end matches the project's currently active citation style (APA / MLA / Chicago / **IEEE default**). | BL-40, BL-41 |
| SUMM-FR-03 | student | every citation in the summary to trace back to a real source I selected | I can trust the summary and verify any point without hunting for phantom references | Must | A post-generation validator checks that: (a) every `[N]` marker in the summary body maps to an entry in the reference list; (b) every reference-list entry corresponds to one of the user-selected resource IDs stored in the database; (c) no `[N]` marker appears that does not satisfy (a) and (b). Any summary that fails validation is discarded; the UI shows a "retry" option rather than displaying an invalid result. Same validation contract as BL-19. | BL-41 |
| SUMM-FR-04 | student | copy the generated summary (including its inline citations and reference list) to my clipboard | I can paste it into my own document as a cited starting point for my writing | Must | A "Copy summary" button copies the full summary text — body paragraphs, inline `[N]` markers, and the reference list formatted in the active citation style — as plain text to the clipboard; the summary is **read-only** in-app (no editing surface); no separate export action is required for v1 (copy-out is sufficient). | BL-42 |

## Non-Functional Requirements

| ID | Quality | Measure | Priority | BL ref |
|----|---------|---------|----------|--------|
| SUMM-NFR-01 | Citation fidelity | 100 % of `[N]` markers in a delivered summary must resolve to a user-selected resource; zero hallucinated references reach the user | Must | BL-41 |
| SUMM-NFR-02 | Local-only generation | The summary pipeline must call only the local Ollama endpoint (`localhost`); no paper metadata or student query is sent to any external API | Must | BL-40 |
| SUMM-NFR-03 | Graceful Ollama failure | If Ollama is unreachable, the UI surfaces the same actionable error message as BL-21 — no hang, no silent empty result | Must | BL-40 |
| SUMM-NFR-04 | Length constraint | Generated summaries stay within 150–300 words; the prompt must include an explicit word-count instruction and the backend must log a warning (not reject) if the model overshoots by more than 20 % | Should | BL-40 |

## Legal / Compliance Requirements

- **PDPA (data minimisation):** The pipeline forwards only stored title + abstract metadata to Ollama — not the student's account details, email, or any other personal data field. No new personal data field is introduced. (rule.md §PDPA)
- **PDPA (purpose limitation):** Saved resource metadata was collected for search/library/outline purposes; summarization is a direct extension of the same stated research-aid purpose. No purpose-expansion check required, but this should be re-confirmed if a future version sends metadata to an external API.
- **CCA §26 (log retention):** The "summarize" action is a user-initiated request on a network-facing endpoint; it must emit the standard access log entry (timestamp, source IP, authenticated user ID, action) per the existing logging middleware — no special treatment needed beyond confirming the new endpoint is not exempted. (rule.md §CCA-§26)
- **No new consent, signature, or cross-border transfer obligations** are triggered by this feature. All processing remains on `localhost`.
