# Product Backlog — ScholarForge

Priorities use MoSCoW (**Must** / **Should** / **Could** / **Won't-for-v1**). Epics are ordered to match the implementation build order in the approved plan, so the backlog can be worked top-to-bottom.

> **Scope correction (this revision)**: two changes from the previous version. (1) **Projects** — saved resources and generated outlines are now scoped per-project, not one big account-wide pile, so different assignments never mix. (2) **No in-app text editor** — the app generates ideas/outline scaffolding (bullet points, example starter text, citations), read-only in-app with copy/export actions. Writing the actual final paper is explicitly the student's own task, done in their own tool.

## Epic 1 — Account & Authentication

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|----------------------|
| BL-01 | As a student, I want to sign up with my email and a password, so that I have my own private account with no third-party login required. | Must | Signup form validates email format + minimum password length; password stored only as a bcrypt hash; duplicate email is rejected with a clear error. (spec: AUTH-FR-01) |
| BL-02 | As a returning student, I want to log in and stay logged in across visits, so that I don't have to re-authenticate every time. | Must | Login sets a signed, httponly session cookie; session persists across browser restarts until expiry (e.g. 30 days) or logout. (spec: AUTH-FR-02) |
| BL-03 | As a student, I want to log out, so that my session ends on this device. | Must | Logout clears the session cookie and invalidates the session row server-side. (spec: AUTH-FR-03) |
| BL-04 | As a student, I want my projects, saved resources, and outlines to be private to my account, so that no one else on the same machine can see them. | Must | Every project/resource/outline query is scoped by the authenticated user's ID; unauthenticated or cross-account access attempts are rejected. (spec: AUTH-FR-04) |
| BL-39 | As a student, I want to permanently delete my account and all its data, so that I can exercise my right to erasure and nothing personal remains in the system. | Must | "Delete account" action invalidates all active sessions, cascades to delete every owned project (which in turn cascades to that project's saved_resources and outlines per BL-34), then deletes the user record; all deletions are atomic; a confirmation step (re-enter email) prevents accidental deletion. (spec: AUTH-FR-05) |

## Epic 2 — Projects (Workspaces)

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|----------------------|
| BL-32 | As a student, I want to create a named project (e.g. "Thesis: Remote Work Trust"), so that everything I gather and generate stays organized around that one piece of work. | Must | Create-project form takes a name; the project appears in the project list immediately, empty. (spec: GEN-FR-01) |
| BL-33 | As a student, I want to open a project and see only that project's saved resources and generated outlines, so that different assignments never mix. | Must | Entering a project scopes every subsequent search/save/generate/list/delete action to that project's ID; no cross-project data ever appears, even accidentally. (spec: PROJ-FR-01) |
| BL-34 | As a student, I want to delete a project I no longer need, so that my workspace stays clean without touching my other work. | Must | Deleting a project cascades to delete all of that project's saved resources and generated outlines; every other project is completely unaffected; a confirmation step prevents accidental deletion. (spec: PROJ-FR-02) |
| BL-35 | As a student, I want to switch between my projects from one place, so that I can move between assignments without losing my place in either. | Should | A project switcher is reachable from every in-project screen; switching updates the visible library/outline immediately, with no stale data from the previous project flashing on screen. |

## Epic 3 — Idea-Based Semantic Search

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|----------------------|
| BL-05 | As a student, I want to type a research idea in plain language and get back relevant papers, so that I don't need to already know exact titles or keywords. | Must | Free-text idea input returns a ranked list of candidate papers pulled from Semantic Scholar and CrossRef. (spec: SRCH-FR-01) |
| BL-06 | As a student, I want results ranked by conceptual relevance, not just keyword overlap, so that I find papers I wouldn't have found by exact search terms. | Must | Candidates are re-ranked by embedding cosine similarity between the idea text and each paper's title+abstract before being shown. (spec: SRCH-FR-02) |
| BL-07 | As a student, I want to see enough detail per result (title, authors, year, venue, abstract snippet) to judge relevance at a glance, so that I don't have to open every link. | Must | Each result card shows title, authors, year, venue/source, and a short abstract excerpt. (spec: SRCH-FR-03) |
| BL-08 | As a student, I want a clear message when a search returns nothing useful, so that I know to rephrase rather than assume the app is broken. | Should | Empty/low-confidence result sets show a "try rephrasing your idea" message instead of a blank list. |
| BL-09 (v2) | As a student, I want the app to try alternate phrasings of my idea automatically, so that I get better coverage on an ambiguous query. | Could (v2) | LLM-based query rewriting generates 2-3 alternate search phrasings; explicitly deferred until the direct-embedding pipeline is verified. |

## Epic 4 — Personal Resource Library (per project)

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|----------------------|
| BL-10 | As a student, I want to save a search result into the current project's library, so that I can come back to it later without re-searching. | Must | "Save" persists the paper's normalized metadata + its embedding, tagged to the current `project_id`. (spec: LIB-FR-01) |
| BL-11 | As a student, I want to avoid saving the same paper twice within one project, so that a project's library doesn't fill up with duplicates. | Must | Saving is blocked/merged when a DOI or arXiv ID already exists **within that project**; the same paper may still be saved separately into a different project on purpose. (spec: LIB-FR-02) |
| BL-12 | As a student, I want to see and remove items from a project's library, so that I can curate it as that piece of work evolves. | Must | Library view lists only the current project's saved resources; delete removes the resource from that project only and is handled gracefully in any outline already generated for that project. (spec: LIB-FR-03) |
| BL-13 | As a student, I want a project's library to persist across logins, so that it represents ongoing work, not a single session. | Must | A project's library contents are unchanged after logout/login on the same account. (spec: LIB-FR-04) |

## Epic 5 — Citation Formatting

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|----------------------|
| BL-14 | As a student, I want each saved resource formatted as a proper citation, so that I don't have to format it by hand. | Must | Each saved resource renders correctly in APA, MLA, and IEEE by default. (spec: CITE-FR-01) |
| BL-15 | As a student, I want to switch citation style, so that I can match my assignment's required format. | Should | A style selector (APA/MLA/Chicago/**IEEE**) re-renders all saved citations without needing to re-save or re-fetch data. |
| BL-16 | As a student, I want to export a BibTeX entry, so that I can use it in LaTeX-based writing tools. | Should | Each resource (and the whole library) can be exported as valid BibTeX. |
| BL-17 | As a student, I want a citation to degrade gracefully when a field (like author or year) is missing, so that I still get a usable citation instead of a broken one. | Should | Missing fields render per-style conventions (e.g. "n.d." for missing year in APA; omit volume/pages in IEEE) rather than blank/undefined text. |
| BL-30 | As a student, I want IEEE-style numbered citations (`[1]`, `[2]`, ...), so that my outline matches the format expected in CS/engineering courses. | Must | `toIEEE(resource)` produces `[N] A. Author, "Title," *Venue*, vol. X, no. Y, pp. Z, Year.` (fields omitted cleanly when absent); reference numbers are assigned by first-cited-order, consistent with IEEE convention. (spec: CITE-FR-02) |

## Epic 6 — Idea & Outline Generation (RAG)

*Reframed: the app generates a scaffold — bullet-point ideas and short example starter text per section — not a finished, ready-to-submit narrative. Writing the actual paper is the student's task.*

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|----------------------|
| BL-18 | As a student, I want to generate an idea/outline scaffold from the current project's saved library, so that I have a structured starting point instead of a blank page. | Must | Generation produces a read-only outline following **IEEE paper structure by default** — Title, Abstract, Index Terms, Roman-numeral sections (I. Introduction, II. Related Work, III. Proposed Methodology, IV. Expected Contribution) — where each section holds a short list of bullet-point ideas/talking points plus one example starter sentence or two, grounded only in that project's saved resources. It is explicitly presented as a starting aid, not a finished draft. (spec: GEN-FR-01, GEN-FR-02) |
| BL-19 | As a student, I want every citation in the generated outline to point to a real saved source, so that I can trust it instead of fact-checking every claim. | Must | A post-generation validator checks every `[N]` citation marker maps to an actual saved resource in that project; no invented references appear. (spec: GENC-FR-01) |
| BL-20 | As a student, I want to choose which citation style is used in the generated outline's bibliography, so that it matches my assignment requirements. | Should | The final references section is generated deterministically from resource metadata in the chosen style (APA/MLA/Chicago/**IEEE**, **default: IEEE**), independent of what the LLM produced for the idea text. |
| BL-21 | As a student, I want a clear error if the local AI engine isn't running, so that I understand why generation failed instead of seeing a crash. | Must | If Ollama is unreachable, the UI shows a specific, actionable error rather than a generic failure or hang. (spec: GENC-FR-02) |
| BL-37 | As a student, I want to regenerate just one section (e.g. only "Related Work") instead of the whole outline, so that I can iterate on one part without losing the rest. | Should | A per-section "Regenerate" action re-runs generation for that section only, using the same saved-resource subset, and leaves every other section untouched. |
| BL-38 | As a student, I want each generated section to include a short draft paragraph alongside the bullet-point ideas, so that I have a prose starting point to paste into my own document and revise. | Should | Each IEEE section contains a draft passage of 2–4 sentences grounded in saved resources, labeled "Draft — revise before use"; all `[N]` citation markers in the passage pass the same post-generation validation as BL-19; passage is read-only; "Copy section" and "Copy all" (BL-22) include it. (spec: GEN-FR-02) |

## Epic 7 — Outline Review & Export (no in-app editor)

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|----------------------|
| BL-22 | As a student, I want to copy any generated section — or the whole outline — to my clipboard, so that I can paste it into my own document and write the real paper there. | Must | Each section has a "Copy" button; a "Copy all" action copies the full outline including the reference list in the chosen style. Content is **read-only** — there is no rich-text editing surface in the app. (spec: GEN-FR-02) |
| BL-23 | As a student, I want to download the generated outline as a file, so that I have a portable starting point to keep writing in my own tool. | Must | "Download as PDF" renders the outline clearly labeled as a **draft outline/aid** (title block, abstract, numbered IEEE sections with bullet ideas, numbered references) — not styled to look like a finished, submission-ready paper. Markdown/plain-text export is available alongside it. (spec: EXP-FR-01) |
| BL-24 | As a student, I want to keep multiple generated outlines per project, so that I can try different angles without losing earlier ones. | Could | A project can hold more than one saved outline, listed with a label and last-generated timestamp. |
| BL-31 (v2) | As a student, I want my downloaded outline PDF to look closer to a real IEEE conference paper layout, so that it's a stronger starting point visually. | Could (v2) | Two-column IEEE typesetting is a known-hard stretch goal (needs proper column-balancing, not just CSS columns) — v1 ships a clean single-column IEEE-structured PDF; two-column is revisited once v1 export is verified. |

## Epic 8 — Reliability & Error Handling

| ID | User Story | Priority | Acceptance Criteria |
|----|------------|----------|----------------------|
| BL-25 | As a student, I want the search to still return results if one external paper database is slow or down, so that a single outage doesn't block my work. | Should | The search pipeline returns partial results from whichever source succeeded rather than failing the whole request. |
| BL-26 | As a student, I want to know when I've hit a rate limit or network hiccup, so that I know to wait and retry rather than assume it's broken. | Could | Fetch failures surface a generic "try again shortly" message rather than a raw error/stack trace. |

## Non-functional / Compliance backlog (see [rule.md](../../rule.md) and [legal-requirements.md](../03-compliance/legal-requirements.md))

| ID | Requirement | Priority |
|----|-------------|----------|
| BL-27 | All access/action logs are retained for at least 90 days and tied to an identifiable account. | Must | (spec: COMP-FR-01) |
| BL-28 | Personal data (email, password) is minimized, hashed where applicable, and deletable on request — including a full project delete cascading correctly (BL-34). | Must | (spec: COMP-FR-02) |
| BL-29 | Terms/consent acceptance at signup is recorded with who/what/when/how. | Should |

## Won't-do for v1

- Multi-user cloud/hosted deployment.
- Any third-party OAuth login (Google/Facebook/etc.).
- Any call to an external hosted LLM API.
- **A rich in-app text editor for writing/editing the full outline or paper** — generated content is read-only (copy-out or export only); the actual writing happens in the student's own document tool.
- Real-time collaborative editing.
- Ingesting/storing a large independent corpus of papers (search stays live-API-based).
