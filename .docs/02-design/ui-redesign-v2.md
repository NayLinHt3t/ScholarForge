# UI Redesign v2 — Simplicity First

Goal: a first-time university student can use ScholarForge without help.
Success is measured by usability, not by the number of features.

## 1. What was confusing before (audit)

| Problem in v1 | Fix in v2 |
|---|---|
| Dark sidebar changed completely inside a project (9 links + "Research tools" group + Export) | One fixed nav everywhere: **Home · My Library · My Notes · Settings** + **New project** |
| Project page was a dashboard of 6 counters (Sources, Evidence, Notes, Themes, Claims, Outline sections) | Project page = papers list + notes list + one primary action (**Find papers**) |
| Jargon in the UI: "Sources", "Evidence", "Claims", "semantic similarity", "Ollama", "RAG" | Plain words: "Papers", "Saved quotes", "closest matching papers", "AI assistant" |
| Paper page had 5 stacked cards (header, AI summary, citations, notes, quotes) | Reader layout: paper text on the left, **Ask about this paper** assistant on the right; citations and quotes collapsed |
| Notes were only per project and not linked to papers | My Notes lists all notes; every note can link to a paper; AI answers can be saved as notes |
| "Add a source" form showed 9 fields up front | Title + authors + abstract; the rest is under "More details" |
| No guidance for a new user | "Getting started" checklist on Home (4 steps) + an empty state with a next step on every screen |

## 2. Information architecture

```
Home (/projects)          welcome · getting started · recent projects · recently opened papers
  └ Project (/projects/{id})       papers · notes · More tools (collapsed)
      ├ Find papers (/search)
      ├ Paper reader (/sources/{id})   abstract + plain-English summary | AI assistant sidebar
      └ More tools: Outline · Summarize several papers · Saved quotes · Themes · Claims · Add by hand · Downloads · Delete
My Library (/library)     all papers · search · project + status filters
My Notes (/notes)         all notes · search · editor (/projects/{id}/notes/{id}) with linked paper
Settings (/settings)      account · AI assistant status · privacy · delete account
```

Advanced features (Outline, Themes, Claims, Evidence, Summary) are unchanged and still reachable — they are only moved out of the main navigation (progressive disclosure).

## 3. Design tokens (`app/static/css/app.css`)

- **Colour:** neutral warm-grey background `#f6f6f3`, white surfaces, one accent `#2f5bd3`. Green / amber / red are used only for status, never for decoration.
- **Type:** system UI font for the interface; a serif reading font (Charter / Georgia) only for paper text and notes. Sizes: 12 · 13 · 15 · 18 · 24 px.
- **Spacing:** 4 px grid (4, 8, 12, 16, 24, 32, 48).
- **Shape:** radius 6 / 8 / 12 px, 1 px borders, almost no shadows.

## 4. Components

Button (primary / secondary / quiet / danger; sm / xs) · Text input, textarea, select · Search input · List + list row (the main way content is shown — instead of card grids) · Status chip · Notice (info / success / warning / error) · Empty state (title + one sentence + one action) · Getting-started steps · Dialog (New project) · Disclosure ("More tools", "Cite this paper") · Reader layout + assistant panel · Mobile tab bar.

Rules: one primary button per screen; every empty list says what to do next; destructive actions always ask for confirmation; no icon without a text label in navigation.

## 5. Responsive

- ≥ 761 px: fixed left nav; reader shows the assistant as a right sidebar that can be hidden.
- ≤ 760 px: bottom tab bar (Home, Library, New, Notes, Settings); reader switches between **Paper** and **Ask AI** tabs.

## 6. Deferred (on purpose)

- **PDF upload and full-text reading.** v2 reads the saved abstract. PDF upload needs text extraction, chunking and retrieval in the backend, so it is the next step, not part of this UI pass.
- Shared papers across projects (one paper in several projects) — would need a data-model change.
