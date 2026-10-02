# Feature List — ScholarForge (DISCOVER Design)

Priorities follow MoSCoW. Each group maps to one implementation epic.

1. **Account & Projects** (Must) — private email/password accounts; named project workspaces that scope all data; cascade-delete; session persistence
2. **Semantic Paper Search** ⬅ *core — build first* (Must) — free-text idea input; Semantic Scholar + CrossRef retrieval; local embedding re-ranking; result cards (title / authors / year / venue / abstract)
3. **Research Library** (Must) — save papers to the active project; DOI/arXiv deduplication with warning for no-ID sources; view, remove, and persist across sessions
4. **Citation Formatting** (Must) — auto-format in APA, MLA, and IEEE; IEEE `[N]` numbered in first-cited order; graceful omission of missing fields
5. **Outline Generation** (Must) — RAG scaffold from saved library using IEEE paper structure; project name as title block; draft prose per section (Should); citation validator blocks hallucinated refs
6. **Review & Export** (Must) — read-only outline; copy section / copy all; PDF download labeled DRAFT; Markdown export
7. **Compliance** (Must) — bcrypt cost ≥ 12; access logs ≥ 90 days append-only (CCA §26); full deletion cascade on account and project delete (PDPA)
