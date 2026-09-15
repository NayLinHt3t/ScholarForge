# Prototype — ScholarForge

A clickable, static (no backend) HTML mockup lives at [`prototype.html`](prototype.html) in this folder — open it directly in a browser. It uses fake/hardcoded data (two sample projects) to demonstrate the six core screens and the navigation between them; nothing is persisted or sent anywhere, though the mock does simulate per-project save/delete state in memory so you can see isolation working live.

> Scope reflected here: (1) everything is scoped inside a **project** — no screen ever shows another project's data; (2) the generated outline screen is **read-only** — no rich-text editor, only Copy/Regenerate/Export actions.

## Screens covered

### 1. Login / Signup
- Single form, toggle between "Log in" and "Sign up".
- Email + password fields only — no social login buttons, by design (BL-01).

### 2. My Projects
- Landing screen right after login — a list of the student's projects (name, created date, resource count, whether an outline exists), each with **Open** and **Delete** (with a confirmation prompt).
- A "New project name" field creates an empty project instantly.
- Deleting a project removes only that project's data — the mock demonstrates this live: create/save into one project, delete it, and the other project's data is untouched (BL-32–BL-35).
- Every other screen is nav-disabled until a project is opened, mirroring the real app's scoping rule.

### 3. Dashboard
- Shows the currently open project's name (also pinned as a badge in the top nav at all times) and its own counts — resources saved, outline generated or not.
- Two primary actions: "Search a new idea" and "View my library," both implicitly scoped to the open project.

### 4. Idea Search
- One large text input ("Describe your research idea...") instead of a title/keyword search box — the UI copy itself signals "you don't need an exact title" (BL-05).
- Results render as cards: title, authors, year, venue, abstract excerpt, and a "Save to this project" button — wording makes the scoping explicit.
- A relevance indicator (percentage + bar) communicates that ranking is conceptual, not exact-match.
- Saving a paper already in the current project's library shows "Already saved" instead of duplicating it (BL-11).

### 5. My Library
- List of the open project's saved resources only, each rendered as a formatted citation.
- A style dropdown (IEEE default / APA / MLA / Chicago) re-renders every citation instantly (BL-15).
- "Copy citation," "View BibTeX," and "Remove" per entry — Remove actually splices the item out of that project's in-memory library in the mock.
- Empty state: "You haven't saved anything in this project yet — try an idea search."

### 6. Idea & Outline Scaffold — read-only
- A persistent info banner frames the screen honestly: *"This is a starting scaffold — bullet ideas and short example passages, not a finished paper. Copy or download it, then write the actual paper yourself in your own document."*
- If the open project has no saved resources, generation is blocked with an explicit empty state rather than a disabled button with no explanation.
- "Generate outline from this project's library" produces a read-only IEEE-structured scaffold: Title, Abstract, Index Terms, then Roman-numeral sections, each containing a **bullet list of ideas/talking points** plus one italicized "Starter line" example — deliberately not full polished prose.
- **No `contenteditable` anywhere** — verified in the mock (`document.querySelectorAll('[contenteditable]').length === 0`). Instead: a "Copy" and "Regenerate" button per section, and a "Copy all" action at the top.
- Regenerate shows a brief "Regenerating…" state on just that section, leaving every other section untouched (BL-37).
- A references list is generated separately from the body text, in the chosen style, to reinforce that the bibliography is deterministic/trustworthy even though the section text is AI-drafted.
- "Download outline as PDF" / "as Markdown" — button copy and the (disabled-in-mock) alert text both say "outline," not "paper" or "proposal," to keep the framing honest.

## Interaction notes
- Navigation uses a persistent top nav (My Projects / Dashboard / Search / Library / Outline / Log out) once logged in; the current project's name shows as a pill next to the logo at all times so it's never ambiguous which project's data is on screen.
- Error/empty states are first-class screens in the mockup (empty project's library, empty project blocking outline generation, Ollama-unreachable banner, no-search-results) since these are explicit backlog items (BL-08, BL-21), not afterthoughts.
