# User Journeys — ScholarForge

> Scope note: Journeys below reflect two corrections — (1) all library/outline work happens inside a **project**, so different assignments never mix; (2) the app generates a read-only idea/outline scaffold, not an editable finished draft — the student copies/exports it and writes the real paper in their own tool.

## Journey A — First-time signup, first project, first idea search

| Stage | User action | System response | Notes / pain point addressed |
|-------|-------------|------------------|-------------------------------|
| 1. Discover | Opens the app on their own machine for the first time | Shows login/signup page | No account required elsewhere — sets the "this is mine, local" expectation immediately. |
| 2. Sign up | Enters email + password | Validates, hashes password, creates account, logs in, redirects to the (empty) project list | No third-party login screen — addresses privacy/trust concern. |
| 3. Create a project | Names a new project, e.g. "Thesis: Remote Work Trust" | Project is created and opened | Establishes the boundary that keeps this assignment's resources/ideas from ever mixing with another one (BL-32). |
| 4. Describe idea | Inside the project, types a rough research idea in plain language (e.g. "how remote work affects team trust over time") | Sends idea to search pipeline; shows a loading state | User isn't required to know a title or exact keywords — this is the core problem being solved. |
| 5. Review results | Skims ranked results with title/authors/year/abstract excerpt | Semantically ranked list renders, including some papers with no literal keyword overlap | Validates the "semantic, not keyword" value proposition — a bad outcome here is the highest-risk failure mode. |
| 6. Save | Clicks "save" on 2-3 promising papers | Resources persist to **this project's** library with auto-formatted citations | Immediate payoff — citation formatting "just happens," scoped to the right project automatically. |

## Journey B — Building a library over multiple sessions, across multiple projects

| Stage | User action | System response | Notes / pain point addressed |
|-------|-------------|------------------|-------------------------------|
| 1. Return | Logs back in on a later day, opens the same project from the project list | That project's library shows everything saved previously — nothing from any other project | Addresses the "scattered resources" problem, and confirms projects stay cleanly separated (BL-33). |
| 2. Start a second project | Creates a second project for an unrelated course assignment | A brand-new, empty library and outline space — completely independent of project 1 | Directly validates the "do not mix with others" requirement — this is the core acceptance test for the Projects feature. |
| 3. Refine idea | Back in project 1, runs a follow-up, more specific search as understanding deepens | New ranked results, independent of earlier saves and of project 2 entirely | Supports iterative idea refinement typical of early research, without cross-contamination. |
| 4. Curate | Removes a resource that turned out to be off-topic | Resource removed from that project only; no dangling reference issues | Keeps each project's library a trustworthy working set, not a junk drawer. |
| 5. Switch citation style | Changes the style dropdown from APA to IEEE because their assignment format changed | All of that project's saved citations re-render instantly in the new style | No re-fetching or manual reformatting needed. |
| 6. Clean up | Deletes an abandoned third project | That project's resources and outlines are gone; projects 1 and 2 are untouched | Confirms cascade-delete is scoped correctly (BL-34) — the highest-risk failure mode for this feature. |

## Journey C — From library to idea/outline scaffold (not a finished paper)

| Stage | User action | System response | Notes / pain point addressed |
|-------|-------------|------------------|-------------------------------|
| 1. Trigger generation | Clicks "Generate outline" from the current project's library view | Backend builds a section-by-section RAG prompt from that project's saved resources only | Directly targets the "blank page" problem, without pulling in resources from other projects. |
| 2. Wait | Sees a generation-in-progress state | Local LLM drafts bullet ideas + a short example passage per section; citation validator checks every marker | If Ollama isn't running, a specific actionable error appears instead of a hang — addresses BL-21. |
| 3. Review scaffold | Reads the structured, **read-only** outline (Title, Abstract, Index Terms, I. Introduction, II. Related Work, III. Proposed Methodology, IV. Expected Contribution) with inline `[N]` citations | Outline renders with a deterministically generated bibliography matching the chosen style | Trust is reinforced because every citation traceably points to something the user actually saved. There is no editable text field — this is explicitly a scaffold, not a submission. |
| 4. Iterate | Doesn't like how "Related Work" turned out; clicks "Regenerate" on just that section | Only that section re-generates; the rest of the outline is untouched | Supports iteration without an editor — regenerate, don't hand-edit (BL-37). |
| 5. Take it to their own tool | Clicks "Copy" on a section (or "Copy all"), or downloads the whole outline as PDF/Markdown | Content copied/exported, clearly labeled as a draft aid | This is the handoff point: **the student writes the actual paper themselves**, in Word/LaTeX/Google Docs, using this as a structured starting point — not inside ScholarForge. |

## Cross-cutting pain points this app targets
- **Idea-first discovery** (Journey A, steps 4-5) — the single biggest gap in existing tools.
- **Fragmentation without cross-contamination** (Journey A step 3; Journey B) — persistent, per-project libraries instead of one undifferentiated pile or scattered bookmarks/notes.
- **Blank-page starting point, honestly scoped** (Journey C) — the app gets the student to a structured scaffold with real citations; it deliberately stops short of pretending to hand them a finished paper.
- **Trust/privacy** (Journey A, steps 1-2; Journey C, step 2) — local-only account and local-only LLM, reinforced at exactly the moments a student would otherwise worry about where their data/idea is going.
