# ScholarForge — Software Requirements Specification v2.0

> **Status:** Approved product direction (replaces all prior spec files under `.docs/01-requirements/`)
> **Date:** 2026-10-03
> **Author:** Product Architecture Review

---

## Table of Contents

1. Product Vision
2. Problem Statement
3. Target Users
4. User Personas
5. User Stories
6. Functional Requirements
7. Non-Functional Requirements
8. Domain Model
9. Core User Flows
10. MVP Definition
11. Features to Remove or Downgrade
12. AI Requirements
13. Local-First Requirements
14. Export Requirements
15. Architecture Requirements
16. Suggested Module Structure
17. MVP Backlog
18. Acceptance Criteria
19. Success Metrics
20. Research Validation Hypotheses

---

## 1. Product Vision

**ScholarForge is a research workspace that helps university students transform scattered sources, quotes, and ideas into an organized, evidence-backed research structure — while keeping the student's reasoning and final writing entirely their own.**

ScholarForge is not a search engine. It is not a citation manager. It is not a writing assistant. It is the missing connective layer between finding sources and writing a paper: a structured environment where students can extract evidence, build themes, form claims, connect everything to an outline, and export a research scaffold that they then write from.

The student remains the author. ScholarForge makes the organizational work tractable.

---

## 2. Problem Statement

### The Real Gap

Students doing serious academic work face a fragmented workflow that no single tool solves:

| Phase | What students do today | Pain |
|-------|----------------------|------|
| Discovery | Search Google Scholar, Semantic Scholar, library databases | Finding papers is not the bottleneck |
| Collection | Save PDFs to folders, bookmark URLs, add to Zotero | Items accumulate without structure |
| Reading | Highlight PDFs in Adobe, paste quotes into Word/Notes | Evidence is scattered across apps and files |
| Organization | Manually group notes in Notion, Excel, physical cards | No formal connection between evidence and argument |
| Claim-building | Try to remember which paper supported which point | High cognitive load; citations get lost |
| Outline | Write an outline in a separate doc, hope it connects | Outline is disconnected from the evidence base |
| Writing | Switch between 4–6 apps simultaneously | Constant context switching; citations get wrong |
| Citation | Manually format references or fight Zotero plugins | Time-consuming; error-prone |

### The Core Problem

**Students have sources. They lack structure.**

The gap is not between finding a paper and saving it. The gap is between:

- reading a paper and knowing *which specific sentence* supports *which specific argument*
- having a pile of evidence and knowing *how these pieces relate to each other*
- having themes and claims and knowing *how they connect to an outline section*
- having an outline and being able to *trace every section back to real evidence*

Existing tools solve adjacent problems:

- **Semantic Scholar / Google Scholar** — discovery (solved)
- **Zotero / Mendeley** — citation storage (adequately solved)
- **Elicit** — AI paper summarization (niche, works for some workflows)
- **Notion / Obsidian** — free-form notes (no academic structure)
- **Word / Google Docs** — writing (solved; ScholarForge does not replace this)

No tool solves the organizational layer: evidence extraction, theme building, claim construction, and structured outline assembly from real research materials.

ScholarForge owns that layer.

---

## 3. Target Users

### Primary

University students working on academically rigorous written assignments:

- **Undergraduate research papers** (3,000–8,000 words, 10–30 sources)
- **Final-year capstone projects and dissertations**
- **Postgraduate theses** (Masters, PhD)
- **Literature reviews** (systematic or narrative)
- **Major seminar papers** requiring evidence-based argumentation

### Secondary

- Research assistants organizing literature for a supervisor
- Academic teams managing shared source collections

### Out of Scope

- Casual browsing / lightweight homework
- Professional researchers with existing workflows (Zotero + LaTeX)
- Secondary school students

---

## 4. User Personas

### Persona A — Fah, Undergraduate Researcher

**Background:** Third-year sociology student writing a 6,000-word research paper on social media's effect on political polarization. Has 20 papers to work through. Not a strong writer but a careful reader.

**Current workflow:** Downloads PDFs, highlights sections in Adobe, pastes interesting quotes into a Google Doc titled "Notes." Before writing, re-reads all 20 PDFs and the notes doc simultaneously. Frequently cannot find which paper a specific quote came from.

**Pain points:**
- Loses track of which quote came from which source
- Cannot see which argument has enough evidence and which doesn't
- Outline is written after all reading, disconnected from notes
- Frequently mis-cites or forgets to cite in-text

**Goals:**
- Know at a glance which papers support each section of her outline
- Be able to trace any claim back to a real quote and page number
- Not have to re-read everything when she starts writing

**How ScholarForge helps:** Fah extracts evidence as she reads, tags it to themes (Polarization / Echo Chambers / Platform Design), builds claims, then assembles an outline where each section shows its supporting evidence. When she writes, she works from the outline with all evidence already organized under each section.

---

### Persona B — Krit, Masters Student

**Background:** Masters student in computer science writing a thesis on federated learning for healthcare. Very organized technically but overwhelmed by the literature volume (60+ papers). Uses LaTeX for writing.

**Current workflow:** Zotero for references, handwritten notes in a physical notebook indexed by topic, a separate Notion database for key findings. Has three tools open simultaneously while writing. Citations are correct but the connection between evidence and argument is in his head.

**Pain points:**
- Connecting related findings across papers requires mental effort every session
- Themes emerge as he reads but are not formally captured anywhere
- The gap between "I've read everything" and "I know what I'm arguing" takes weeks
- Exporting structured notes to LaTeX is manual

**Goals:**
- A single place to see which themes have strong evidence and which are thin
- See relationships between findings from different papers
- Export citations and evidence to BibTeX/LaTeX without manual transcription

**How ScholarForge helps:** Krit imports sources, extracts key findings as evidence, groups findings into themes (Privacy, Communication Cost, Model Drift), identifies claims from theme clusters, builds an outline that references claims and evidence directly, then exports BibTeX and a Markdown scaffold into his LaTeX workflow.

---

### Persona C — Ploy, Thesis Student (Literature Review)

**Background:** PhD student conducting a systematic literature review on mindfulness interventions in workplace settings. Needs to synthesize 80+ papers, identify gaps, and make original contributions. Supervised by a strict professor who demands full traceability.

**Current workflow:** Spreadsheet with paper metadata, Word document for evidence notes, separate document for gap analysis. Everything is manual. Supervisor asks "what's your evidence for that?" and she has to search across three documents.

**Pain points:**
- Full traceability from claim to evidence to source is nearly impossible to maintain manually
- Cannot quickly show the supervisor which claims have strong vs. weak evidence
- Identifying themes and gaps in the literature takes weeks of manual re-reading
- Any change to her argument structure requires updating multiple disconnected documents

**Goals:**
- Full traceability from outline section → claim → evidence → source
- Quickly see which claims are well-supported and which need more evidence
- Share a structured view of her research with her supervisor
- Export the full evidence structure to a document her supervisor can review

**How ScholarForge helps:** Ploy has every piece of evidence linked to its source (with page number), grouped under themes, connected to claims. The outline is assembled from claims with their evidence. When her supervisor asks "what supports this argument?" she navigates directly to the evidence and its source rather than searching across documents.

---

## 5. User Stories

### Project Management

| ID | User Story |
|----|-----------|
| US-P01 | As a student, I want to create a named research project with a research question, so that all my work for one assignment is organized in one place. |
| US-P02 | As a student, I want to see a dashboard of all my projects, so that I can switch between assignments without confusion. |
| US-P03 | As a student, I want to edit my research question after I start, so that I can refine my focus as my understanding deepens. |
| US-P04 | As a student, I want to delete a project and all its contents, so that I can remove abandoned work. |
| US-P05 | As a student, I want to see a project overview showing how many sources, evidence items, themes, claims, and outline sections I have, so that I can gauge my progress. |

### Source Management

| ID | User Story |
|----|-----------|
| US-S01 | As a student, I want to add a source by entering its title, authors, year, DOI/URL, and type, so that I have a record of every paper I'm using. |
| US-S02 | As a student, I want to add a source by pasting a DOI and have the metadata fetched automatically, so that I don't have to type bibliographic details manually. |
| US-S03 | As a student, I want to tag sources with status (unread / reading / done), so that I know what I still need to process. |
| US-S04 | As a student, I want to add notes to a source, so that I can record my overall impression before extracting specific evidence. |
| US-S05 | As a student, I want to see which sources have evidence extracted and which don't, so that I know what I haven't processed yet. |
| US-S06 | As a student, I want to remove a source from a project, so that I can remove irrelevant papers I added by mistake. |
| US-S07 | As a student, I want to see an open-access badge on each source, so that I know whether I can read it without a paywall. |

### Evidence Management

| ID | User Story |
|----|-----------|
| US-E01 | As a student, I want to add an evidence item by typing or pasting a quote from a source with a page/section reference, so that I capture the exact text and where it came from. |
| US-E02 | As a student, I want to add my own note to an evidence item, so that I can record what I think this evidence means or how I plan to use it. |
| US-E03 | As a student, I want to see all evidence extracted from a specific source, so that I can review what I found in that paper. |
| US-E04 | As a student, I want to see all evidence across my project, so that I can see the full body of material I have collected. |
| US-E05 | As a student, I want to edit or delete an evidence item, so that I can fix mistakes or remove irrelevant extracts. |
| US-E06 | As a student, I want to flag an evidence item as a key finding, so that I can highlight the most important material. |

### Notes

| ID | User Story |
|----|-----------|
| US-N01 | As a student, I want to add a standalone note to my project (not tied to a source), so that I can record ideas, questions, and thoughts that arise during my research. |
| US-N02 | As a student, I want to view all my project notes in one place, so that I can review my thinking over time. |

### Themes

| ID | User Story |
|----|-----------|
| US-T01 | As a student, I want to create a named theme with a description, so that I can define a recurring concept in my research. |
| US-T02 | As a student, I want to link one or more evidence items to a theme, so that I can see all supporting material for a concept in one place. |
| US-T03 | As a student, I want to see how many evidence items are linked to each theme, so that I can identify well-supported themes and thin ones. |
| US-T04 | As a student, I want to remove an evidence item from a theme without deleting the evidence, so that I can reorganize without losing work. |
| US-T05 | As a student, I want to delete a theme, so that I can remove a concept I decided not to pursue. |

### Claims

| ID | User Story |
|----|-----------|
| US-C01 | As a student, I want to create a claim as a statement I want to argue, so that I can articulate my own position or argument. |
| US-C02 | As a student, I want to link evidence to a claim as supporting evidence, so that I can see what evidence backs up each argument. |
| US-C03 | As a student, I want to see which claims have no supporting evidence, so that I know which arguments need more work. |
| US-C04 | As a student, I want to link a theme to a claim, so that I can connect a cluster of evidence to an argument without linking every item individually. |
| US-C05 | As a student, I want to mark a claim's confidence level (speculative / supported / strongly supported), so that I know which arguments are ready to use. |

### Outline Management

| ID | User Story |
|----|-----------|
| US-O01 | As a student, I want to create an outline with named sections, so that I have a structural skeleton for my paper. |
| US-O02 | As a student, I want to reorder outline sections, so that I can rearrange my paper's structure. |
| US-O03 | As a student, I want to link claims to an outline section, so that I know which arguments belong in each section. |
| US-O04 | As a student, I want to link specific evidence to an outline section, so that I know which quotes I plan to use in each section. |
| US-O05 | As a student, I want to add writing notes to each outline section, so that I can record what I want to say before I start writing. |
| US-O06 | As a student, I want to see a coverage view showing which outline sections have no linked claims or evidence, so that I can identify structural gaps before I start writing. |
| US-O07 | As a student, I want to see all claims and evidence linked to an outline section in one view, so that I have everything I need when I start writing that section. |

### Citation Management

| ID | User Story |
|----|-----------|
| US-CI01 | As a student, I want each source to automatically have a formatted citation in APA, MLA, and IEEE styles, so that I can copy citations without formatting by hand. |
| US-CI02 | As a student, I want to choose a citation style for my project, so that all citations match my assignment requirements. |
| US-CI03 | As a student, I want to export BibTeX for one source or all sources in a project, so that I can use citations in LaTeX tools. |

### Search

| ID | User Story |
|----|-----------|
| US-SR01 | As a student, I want to search across all evidence in my project by keyword, so that I can find relevant material quickly without scrolling. |
| US-SR02 | As a student, I want to filter evidence by theme or claim, so that I can see a specific subset of my material. |
| US-SR03 | As a student, I want to search my sources by title, author, or keyword, so that I can quickly find a specific paper. |

### AI Assistance

| ID | User Story |
|----|-----------|
| US-AI01 | As a student, I want AI to suggest possible themes from my evidence collection, so that I can see patterns I might have missed. |
| US-AI02 | As a student, I want AI to suggest which of my existing evidence might be relevant to a specific claim, so that I can find connections I overlooked. |
| US-AI03 | As a student, I want AI to generate a short summary of a source based on its abstract and my extracted evidence, so that I can quickly refresh my understanding without re-reading the whole paper. |
| US-AI04 | As a student, I want AI-generated suggestions to be clearly labeled as AI-generated, so that I never confuse AI suggestions with my own work. |
| US-AI05 | As a student, I want to accept, reject, or ignore each AI suggestion, so that I remain in control of what enters my research structure. |

### Export

| ID | User Story |
|----|-----------|
| US-EX01 | As a student, I want to export my full research structure as a Markdown file, so that I have a portable, human-readable record of all my organized work. |
| US-EX02 | As a student, I want to export all citations as BibTeX, so that I can import them into LaTeX or Zotero. |
| US-EX03 | As a student, I want to export my outline with linked evidence as a Markdown scaffold, so that I have a structured starting point for writing. |

### Privacy and Account

| ID | User Story |
|----|-----------|
| US-PR01 | As a student, I want to sign up with an email and password, so that my research is private to my account. |
| US-PR02 | As a student, I want to permanently delete my account and all associated data, so that I can exercise my right to erasure. |
| US-PR03 | As a student, I want my research projects to be private and inaccessible to other users, so that my work remains confidential. |

---

## 6. Functional Requirements

### FR Group 1 — Project Management

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-001 | A student can create a research project with a name and a research question. | P0 | Project is created with a unique ID, owner user_id, name (required), research question (optional at creation, editable), and created_at timestamp. Project appears in the project list immediately. |
| FR-002 | A student can view a list of all their projects. | P0 | Project list shows all projects owned by the authenticated user, ordered by last-modified date. No other user's projects are visible. |
| FR-003 | A student can edit a project's name and research question. | P0 | Changes are persisted immediately. Research question can be set, updated, or cleared at any time. |
| FR-004 | A student can delete a project. A confirmation step is required. Deletion cascades to all project data. | P0 | On confirmation: all sources, evidence, notes, themes, claims, outline sections, and citations belonging to the project are deleted atomically. Other projects are unaffected. |
| FR-005 | A project dashboard shows counts of sources, evidence items, themes, claims, and outline sections. | P0 | Dashboard reflects current counts in real time. Counts are scoped to the authenticated user's project. |
| FR-006 | All project-scoped data operations are isolated to the authenticated user's project. | P0 | No cross-user or cross-project data leakage. All queries are parameterized with both project_id and user_id. |

### FR Group 2 — Source Management

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-010 | A student can add a source manually by entering: title, authors, year, type (journal article / book / conference paper / website / dataset / other), DOI (optional), URL (optional), abstract (optional). | P0 | Source is persisted with a unique ID, project_id, and user_id. It appears in the project's source list immediately. |
| FR-011 | A student can add a source by entering a DOI; metadata (title, authors, year, venue, abstract) is fetched from CrossRef. | P1 | CrossRef is queried; available fields are populated automatically. Student can review and edit before saving. If CrossRef returns no result, manual entry is offered. |
| FR-012 | Each source has a read status: Unread / Reading / Done. The student can update the status at any time. | P0 | Status is displayed on the source card. Default status is Unread. |
| FR-013 | A student can add a general note to a source (not tied to a specific extract). | P0 | Source note is a free-text field. Blank is valid. |
| FR-014 | The source list shows which sources have at least one evidence item extracted. | P0 | Sources with no extracted evidence show an "No evidence extracted" indicator. |
| FR-015 | A student can remove a source from a project. Removal cascades to evidence extracted from that source. | P0 | On removal: all evidence items whose source_id matches the deleted source are also deleted. Claims and outline sections that referenced that evidence are updated to reflect the removal (citation markers removed). A confirmation warning names the number of evidence items that will be deleted. |
| FR-016 | Each source stores an open-access status (Open Access / Paywalled / Unknown). For sources added via DOI lookup, this is derived from the CrossRef/metadata response where available; otherwise Unknown. For manually added sources, the student can set it. | P1 | Badge is displayed on the source card. Default for manually added sources is Unknown. |

### FR Group 3 — Evidence Management

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-020 | A student can add an evidence item to a source. Each evidence item has: quote/extract (required), page or section reference (optional), student note (optional). | P0 | Evidence item is persisted with a unique ID, source_id, project_id, user_id, and created_at. It appears immediately in the source's evidence list and the project-wide evidence list. |
| FR-021 | A student can edit the quote, page reference, or note of an existing evidence item. | P0 | Changes are persisted immediately. |
| FR-022 | A student can delete an evidence item. Any theme links and claim links for that evidence item are also deleted. | P0 | After deletion, the evidence item no longer appears in any theme or claim view. |
| FR-023 | A student can view all evidence items for a specific source. | P0 | Evidence list is scoped to the selected source within the current project. |
| FR-024 | A student can view all evidence items across the entire project. | P0 | Project-wide evidence list shows all evidence items, each displaying its source title, quote excerpt, and student note. |
| FR-025 | A student can flag an evidence item as a key finding. | P1 | Key findings are visually distinguished and can be filtered separately. |

### FR Group 4 — Notes

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-030 | A student can create a standalone note in a project (not tied to any source or evidence). | P0 | Note has title (optional), body (required), and created_at. It appears in the project's note list. |
| FR-031 | A student can edit or delete a standalone note. | P0 | Changes are persisted immediately. Deletion removes only the note; no other data is affected. |
| FR-032 | A student can view all standalone notes for a project in one list. | P0 | Notes list is scoped to the current project. |

### FR Group 5 — Themes

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-040 | A student can create a theme with a name and optional description. | P0 | Theme is persisted with a unique ID, project_id, user_id, and created_at. |
| FR-041 | A student can link one or more evidence items to a theme. | P0 | A many-to-many relationship is created between theme and evidence. The evidence item remains accessible from the source view; it is not moved. |
| FR-042 | The theme list displays the count of evidence items linked to each theme. | P0 | Count updates immediately when evidence is added to or removed from a theme. |
| FR-043 | A student can view all evidence items linked to a specific theme. | P0 | Theme detail view lists all linked evidence with source titles and student notes. |
| FR-044 | A student can remove an evidence item from a theme without deleting the evidence item. | P0 | The many-to-many link is removed. The evidence item remains in the source and the project evidence list. |
| FR-045 | A student can delete a theme. Theme deletion removes the theme and all its evidence links but does not delete evidence items. | P0 | Theme disappears from the theme list. Evidence items remain intact. |

### FR Group 6 — Claims

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-050 | A student can create a claim as a free-text statement. | P0 | Claim is persisted with a unique ID, project_id, user_id, and created_at. |
| FR-051 | A student can link one or more evidence items to a claim as supporting evidence. | P0 | Many-to-many relationship between claim and evidence. |
| FR-052 | A student can link one or more themes to a claim. | P0 | Many-to-many relationship between claim and theme. This is a convenience: all evidence under the linked theme becomes visible in the claim view but individual evidence-claim links are not created automatically. |
| FR-053 | A student can set a confidence level on a claim: Speculative / Supported / Strongly Supported. | P1 | Confidence level is displayed on the claim card. Default is Speculative. |
| FR-054 | The claims list identifies claims with no linked evidence or themes. | P0 | Claims with no support are visually flagged as "No evidence linked." |
| FR-055 | A student can delete a claim. Deletion removes the claim and all its evidence/theme links but does not delete the evidence or themes. | P0 | Claim is removed. Evidence and themes remain intact. |

### FR Group 7 — Outline Management

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-060 | A student can create an outline for a project. Each project has at most one active outline. | P0 | Outline is created with a unique ID and project_id. |
| FR-061 | A student can add, rename, reorder, and delete outline sections. | P0 | Sections have a title, an order index, and optional writing notes. Reordering persists immediately. Deleting a section removes only the section and its claim/evidence links; claims and evidence remain. |
| FR-062 | A student can link one or more claims to an outline section. | P0 | Many-to-many relationship between outline section and claims. |
| FR-063 | A student can link one or more evidence items directly to an outline section. | P0 | Many-to-many relationship between outline section and evidence. |
| FR-064 | An outline section detail view shows all linked claims and evidence, each with its source and student note. | P0 | The view is the student's writing brief for that section. |
| FR-065 | A coverage view identifies outline sections with no linked claims and no linked evidence. | P0 | Empty sections are visually flagged. The student can act on them before starting to write. |
| FR-066 | A student can add writing notes to each outline section. | P0 | Writing notes are a free-text field on the section. Not shown in export as a quote; exported as a planning note. |

### FR Group 8 — Citation Management

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-070 | Each source in a project is associated with one citation record. The citation is derived from the source's stored metadata. | P0 | Citation data is not stored separately; it is computed from source fields on demand. |
| FR-071 | Each source renders a formatted citation string in APA, MLA, and IEEE styles. | P0 | Citation is deterministic given the same metadata. Missing fields degrade gracefully per-style conventions (e.g., "n.d." for missing year in APA). Output never contains "undefined", "null", or broken separators. |
| FR-072 | A student can select a project-wide citation style (APA / MLA / Chicago / IEEE; default IEEE). All citation renderings use this style. | P1 | Style preference is stored on the project record. Changing the style immediately re-renders all visible citation strings without re-saving sources. |
| FR-073 | A student can copy a formatted citation for a single source to the clipboard. | P0 | One-click copy. No download required. |
| FR-074 | A student can export BibTeX for a single source or for all sources in the project. | P1 | Per-source: copies to clipboard. All sources: downloads as a `.bib` file. Each entry has a unique cite-key (first-author surname + year). Standard BibTeX fields are populated from source metadata; absent fields are omitted. Output must be valid BibTeX (parseable by BibTeX/Biber). |

### FR Group 9 — Search

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-080 | A student can perform keyword search across all evidence items in a project. | P0 | Search matches against quote text and student notes. Results display source title, quote excerpt, and highlights. |
| FR-081 | A student can filter evidence items by theme, claim, or source. | P0 | Filters are combinable. Applying a filter reduces the visible evidence list immediately. |
| FR-082 | A student can perform keyword search across all sources in a project. | P0 | Search matches against title, authors, and abstract. |
| FR-083 | Source discovery from external APIs (e.g., Semantic Scholar) is available as an optional import pathway, not as the core search surface. | P1 | A student can optionally search Semantic Scholar from within the source-adding workflow and import a result. This is a convenience, not the primary input. The primary input is always manual or DOI-based. |

### FR Group 10 — AI Assistance

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-090 | AI can suggest possible themes from the project's evidence collection. | P1 | Suggestions are presented as a candidate list. Each is labeled "AI Suggestion." Student can accept (creates a real theme), reject, or ignore. Accepted suggestions become student-owned themes. |
| FR-091 | AI can suggest which existing evidence items might support a given claim. | P1 | Student selects a claim; AI returns a ranked list of evidence items from the project with a relevance note. Each suggestion is labeled "AI Suggestion." Student individually accepts or rejects each. |
| FR-092 | AI can generate a short summary (100–150 words) of a source based on its abstract and extracted evidence items. | P1 | Summary is displayed in a read-only panel labeled "AI-Generated Summary — not verified." Student can dismiss or copy the summary. Summary is not saved as evidence; it is transient. |
| FR-093 | AI can suggest a possible outline structure based on the project's themes and claims. | P2 | Outline suggestion is presented as a candidate list of section names. Student can accept/reject each section. Accepted sections are added to the outline as student-owned sections with no linked evidence. |
| FR-094 | All AI-generated content is visually distinguishable from student-created content throughout the interface. | P0 | AI content uses a distinct visual treatment (badge, color, or label) that cannot be removed until the student explicitly accepts/converts the content. There is no pathway for AI-generated content to appear as student-authored content without an explicit accept action. |
| FR-095 | The student can disable all AI features for a project. | P1 | A per-project toggle disables all AI suggestions. When disabled, no AI API calls are made for that project. |

### FR Group 11 — Export

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-100 | A student can export the full research structure as a Markdown file. | P0 | Export includes: project name, research question, all sources (with citation), all evidence per source (with student notes), all themes (with linked evidence), all claims (with confidence and linked evidence), outline with sections (with linked claims and evidence). Clearly structured with headings. |
| FR-101 | A student can export the outline with linked claims and evidence as a writing scaffold in Markdown. | P0 | Export shows each outline section, its writing notes, linked claims, and linked evidence items (with quotes and source references). Intended as a working document the student writes from. |
| FR-102 | A student can export all citations as BibTeX. | P1 | See FR-074. |
| FR-103 | All exports are clearly labeled as a research scaffold and not a finished paper. | P0 | Every exported file contains a header: "ScholarForge Research Export — [project name] — [date]. This is an organizational scaffold. The student's written paper is not included." |

### FR Group 12 — Privacy and Account

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| FR-110 | A student can register with an email and password. | P0 | Email validated (format). Password hashed (bcrypt, cost ≥ 12). Duplicate email rejected. No plaintext password stored or logged. |
| FR-111 | A student can log in and maintain a session. | P0 | Session cookie: HttpOnly, SameSite=Lax, signed, 30-day expiry. Generic invalid-credentials error (does not distinguish wrong email from wrong password). |
| FR-112 | A student can log out. Session is invalidated server-side. | P0 | Session row deleted/invalidated on logout. Cookie cleared in response. |
| FR-113 | A student can permanently delete their account. All data is deleted atomically. | P0 | Deletion cascades: user record → projects → sources → evidence → notes → themes → claims → outline sections → citations. All atomic. Confirmation step (re-enter email). |
| FR-114 | All project data is accessible only to the project owner. | P0 | All queries scoped by both project_id and user_id. HTTP 401/403 on cross-user access attempts. |
| FR-115 | Terms and privacy policy acceptance is recorded at signup. | P1 | Recorded fields: user_id, terms version string, UTC timestamp, UI action (checkbox + submit). Stored in a dedicated consent_records table not deleted by account deletion. |

---

## 7. Non-Functional Requirements

### Security

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-S01 | Passwords stored only as bcrypt hashes, work factor ≥ 12. | P0 |
| NFR-S02 | Session tokens are signed, HttpOnly, SameSite=Lax. | P0 |
| NFR-S03 | All HTTP endpoints require authentication except signup and login. | P0 |
| NFR-S04 | All database queries parameterized; no string-concatenated queries. | P0 |
| NFR-S05 | AI API keys stored in environment variables; never exposed to the client. | P0 |
| NFR-S06 | No personal data (name, email, IP) is included in prompts sent to external AI APIs. Only project-scoped research content is sent. | P0 |

### Privacy

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-P01 | Personal data (email, hashed password) collected only under contract necessity (PDPA). Legal basis documented at the point of collection. | P0 |
| NFR-P02 | Account deletion cascades to every table holding the user's data. | P0 |
| NFR-P03 | Access logs retained for ≥ 90 days (CCA §26 compliance). Append-only. Stored separately from application data. | P0 |
| NFR-P04 | Research content sent to external AI APIs must not include student PII. | P0 |
| NFR-P05 | If external AI API usage is introduced, the data-processing purpose must be within the scope consented to at signup. | P1 |

### Performance

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-PE01 | Project dashboard loads in ≤ 2 s under normal conditions (Firestore, single user). | P0 |
| NFR-PE02 | Evidence search within a project returns results in ≤ 1 s for a project with ≤ 500 evidence items. | P0 |
| NFR-PE03 | Export (Markdown, BibTeX) completes in ≤ 5 s for a project with ≤ 50 sources and ≤ 200 evidence items. | P0 |
| NFR-PE04 | AI suggestion responses return in ≤ 10 s. A loading indicator is shown if response takes > 2 s. | P1 |

### Reliability

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-R01 | If an AI API call fails, the rest of the application remains fully functional. AI failure surfaces a user-facing message; it does not crash or degrade non-AI features. | P0 |
| NFR-R02 | If DOI metadata fetch fails, the student is offered manual entry instead of seeing an error screen. | P1 |
| NFR-R03 | All data mutations are atomic at the persistence layer. Partial writes do not leave data in an inconsistent state. | P0 |

### Maintainability

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-M01 | Business logic (domain and application layers) must not import or reference Firestore SDK types directly. All persistence is accessed through repository interfaces. | P0 |
| NFR-M02 | Each module (sources, evidence, themes, claims, outlines, citations, ai) is independently testable with mocked repositories. | P0 |
| NFR-M03 | AI provider is accessed through an abstraction (AIService interface). The concrete implementation (OpenAI, Gemini, local) is injected. | P0 |

### Usability

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-U01 | A student with no training should be able to add a source and extract evidence within 5 minutes of first use. | P0 |
| NFR-U02 | AI suggestions are always visually distinct from student-created content. No student should be able to confuse the two. | P0 |
| NFR-U03 | The outline coverage view makes gaps in evidence immediately visible without requiring the student to check each section individually. | P0 |

### Data Portability

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-DP01 | A student can export their complete research structure at any time without needing to contact support. | P0 |
| NFR-DP02 | Export formats (Markdown, BibTeX) are open standards not tied to ScholarForge's proprietary format. | P0 |

### AI Transparency

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-AT01 | Every AI-generated item (suggestion, summary, theme candidate) carries a persistent "AI Suggestion" label until the student explicitly accepts or converts it. | P0 |
| NFR-AT02 | AI summaries are labeled "AI-Generated — not verified" and cannot be saved as evidence without the student re-typing or editing the content. | P0 |
| NFR-AT03 | The application does not present AI-generated claims, evidence, or themes as student research. | P0 |

---

## 8. Domain Model

### Entities

#### User
**Purpose:** Authenticated student account.
| Field | Type | Notes |
|-------|------|-------|
| id | string | Unique identifier |
| email | string | Login credential; personal data |
| passwordHash | string | bcrypt hash |
| createdAt | timestamp | |

#### Project
**Purpose:** Top-level workspace for one research assignment.
| Field | Type | Notes |
|-------|------|-------|
| id | string | |
| userId | string | Owner |
| name | string | Human-readable project name |
| researchQuestion | string | Optional; editable |
| citationStyle | enum | APA / MLA / Chicago / IEEE (default: IEEE) |
| createdAt | timestamp | |
| updatedAt | timestamp | |

#### Source
**Purpose:** A research source (paper, book, website, dataset).
| Field | Type | Notes |
|-------|------|-------|
| id | string | |
| projectId | string | |
| userId | string | |
| type | enum | journal_article / book / conference_paper / website / dataset / other |
| title | string | Required |
| authors | string[] | |
| year | number | Optional |
| venue | string | Journal/conference name (optional) |
| doi | string | Optional |
| url | string | Optional |
| abstract | string | Optional |
| generalNote | string | Student's note on the source |
| readStatus | enum | unread / reading / done |
| accessStatus | enum | open_access / paywalled / unknown |
| createdAt | timestamp | |

#### Evidence
**Purpose:** A specific extracted quote or finding from a source, with a student note.
| Field | Type | Notes |
|-------|------|-------|
| id | string | |
| projectId | string | |
| sourceId | string | Foreign key to Source |
| userId | string | |
| quote | string | The extracted text (required) |
| pageReference | string | Page, section, timestamp, etc. (optional) |
| studentNote | string | Student's interpretation or intended use |
| isKeyFinding | boolean | |
| createdAt | timestamp | |

#### Note
**Purpose:** A standalone student note not tied to any source.
| Field | Type | Notes |
|-------|------|-------|
| id | string | |
| projectId | string | |
| userId | string | |
| title | string | Optional |
| body | string | Required |
| createdAt | timestamp | |

#### Theme
**Purpose:** A named recurring concept grouping related evidence.
| Field | Type | Notes |
|-------|------|-------|
| id | string | |
| projectId | string | |
| userId | string | |
| name | string | |
| description | string | Optional |
| createdAt | timestamp | |

#### ThemeEvidence *(join table)*
| Field | Type |
|-------|------|
| themeId | string |
| evidenceId | string |

#### Claim
**Purpose:** An argument or statement the student wants to make.
| Field | Type | Notes |
|-------|------|-------|
| id | string | |
| projectId | string | |
| userId | string | |
| statement | string | The claim text |
| confidence | enum | speculative / supported / strongly_supported |
| createdAt | timestamp | |

#### ClaimEvidence *(join table)*
| Field | Type |
|-------|------|
| claimId | string |
| evidenceId | string |

#### ClaimTheme *(join table)*
| Field | Type |
|-------|------|
| claimId | string |
| themeId | string |

#### Outline
**Purpose:** The structural skeleton of the student's research paper.
| Field | Type | Notes |
|-------|------|-------|
| id | string | |
| projectId | string | One per project |
| userId | string | |
| createdAt | timestamp | |

#### OutlineSection
**Purpose:** A named section of the outline, linked to claims and evidence.
| Field | Type | Notes |
|-------|------|-------|
| id | string | |
| outlineId | string | |
| projectId | string | |
| title | string | |
| orderIndex | number | For reordering |
| writingNotes | string | Student's planning notes for this section |

#### OutlineSectionClaim *(join table)*
| Field | Type |
|-------|------|
| sectionId | string |
| claimId | string |

#### OutlineSectionEvidence *(join table)*
| Field | Type |
|-------|------|
| sectionId | string |
| evidenceId | string |

### Entity Relationships

```
User
└── Project (1:many)
    ├── Source (1:many)
    │   └── Evidence (1:many)
    │       ├── ThemeEvidence (many:many → Theme)
    │       ├── ClaimEvidence (many:many → Claim)
    │       └── OutlineSectionEvidence (many:many → OutlineSection)
    ├── Note (1:many)
    ├── Theme (1:many)
    │   ├── ThemeEvidence (many:many → Evidence)
    │   └── ClaimTheme (many:many → Claim)
    ├── Claim (1:many)
    │   ├── ClaimEvidence (many:many → Evidence)
    │   ├── ClaimTheme (many:many → Theme)
    │   └── OutlineSectionClaim (many:many → OutlineSection)
    └── Outline (1:1)
        └── OutlineSection (1:many)
            ├── OutlineSectionClaim (many:many → Claim)
            └── OutlineSectionEvidence (many:many → Evidence)
```

### Key Invariants

1. Evidence always belongs to exactly one Source. Deleting a Source deletes its Evidence.
2. Themes, Claims, and Outline Sections reference Evidence; they do not own it.
3. Deleting a Theme or Claim removes the join records but not the Evidence.
4. A Project has at most one Outline.
5. All entities in a Project share the same projectId and userId.

---

## 9. Core User Flows

### Flow A — Starting a Research Project

1. Student signs in.
2. Student clicks "New Project."
3. Student enters a project name (required) and optionally a research question.
4. Project is created; student is taken to the project dashboard.
5. Dashboard shows zero counts; student sees prompts to add sources.

### Flow B — Adding a Source

**Manual path:**
1. Student opens a project and navigates to Sources.
2. Student clicks "Add Source."
3. Student selects type (journal article, book, etc.) and enters metadata.
4. Source is saved; read status defaults to Unread; access status defaults to Unknown.

**DOI path (P1):**
1. Student enters a DOI.
2. System fetches metadata from CrossRef.
3. Student reviews pre-filled fields and confirms or edits.
4. Source is saved.

### Flow C — Extracting Evidence

1. Student opens a source (e.g., opens PDF externally, ScholarForge side-by-side).
2. Student reads and finds a relevant passage.
3. Student returns to ScholarForge, opens the source, clicks "Add Evidence."
4. Student pastes the quote, enters a page reference, and writes a student note.
5. Evidence is saved and linked to the source.
6. Source's evidence count updates; source shows "Evidence extracted" indicator.

### Flow D — Connecting Evidence to a Claim

1. Student navigates to Claims.
2. Student creates a new claim: "Social media algorithms amplify political polarization by rewarding outrage."
3. Student clicks "Link Evidence."
4. Evidence list shows all project evidence with search/filter.
5. Student selects relevant evidence items.
6. Claim now shows evidence count; confidence defaults to Speculative.
7. Student updates confidence to "Supported."

### Flow E — Building an Outline

1. Student navigates to Outline.
2. Student adds sections: Introduction / Literature Review / Methodology / Discussion / Conclusion.
3. Student opens "Literature Review" section.
4. Student clicks "Link Claims" and selects relevant claims.
5. Student clicks "Link Evidence" and selects specific quotes to use.
6. Student writes planning notes in the section.
7. Coverage view updates: Literature Review now shows 3 claims, 7 evidence items.

### Flow F — Finding Relevant Evidence for an Outline Section

**Manual:**
1. Student opens an outline section.
2. Student uses the evidence search/filter within the link-evidence panel.
3. Student finds evidence by theme or keyword.

**AI-assisted (P1):**
1. Student opens an outline section and clicks "AI: Suggest Evidence."
2. AI returns a ranked list of evidence items relevant to the section title and writing notes.
3. Each suggestion is labeled "AI Suggestion."
4. Student accepts or rejects each.

### Flow G — Exporting Research

1. Student navigates to Export.
2. Student selects "Export full research structure (Markdown)."
3. System generates a Markdown file with: project name, research question, sources, evidence, themes, claims, outline with linked evidence.
4. File downloads. Header indicates this is a research scaffold, not a paper.

### Flow H — Using AI Assistance

1. Student navigates to Themes.
2. Student clicks "AI: Suggest Themes from My Evidence."
3. AI analyzes evidence and returns 3–5 candidate theme names with descriptions.
4. Each is labeled "AI Suggestion."
5. Student reviews, accepts 2, rejects 1, ignores 2.
6. Accepted themes appear in the theme list as student-owned themes with "(from AI suggestion)" note, which the student can edit away.

---

## 10. MVP Definition

### What MVP Must Prove

The MVP exists to validate one hypothesis: **students will use a structured workflow (evidence → themes → claims → outline) in preference to unstructured notes if the tool makes it easy enough to maintain.**

MVP is not a feature showcase. It is the minimum necessary to run this validation.

### P0 — MVP Core (Must Ship)

| Area | What is included |
|------|-----------------|
| Account | Signup, login, logout, account deletion |
| Projects | CRUD, research question, dashboard counts, data isolation |
| Sources | Manual add, read status, source note, evidence count indicator, remove |
| Evidence | Add (quote + page + note), edit, delete, view by source, view all |
| Notes | Standalone note CRUD |
| Themes | CRUD, link/unlink evidence, evidence count |
| Claims | CRUD, link/unlink evidence, link/unlink theme, unsupported claim indicator |
| Outline | CRUD sections, reorder, link claims, link evidence, coverage view, writing notes |
| Citations | Computed from source metadata, IEEE/APA/MLA rendering, copy to clipboard |
| Export | Full structure as Markdown, outline scaffold as Markdown |
| Privacy | All P0 privacy FRs (PDPA, CCA §26 logging, account deletion cascade) |

### P1 — Post-MVP (Next Sprint)

| Feature | Reason to defer |
|---------|----------------|
| DOI metadata fetch | Manual entry works; this is convenience |
| Citation style selector | Default IEEE works for MVP |
| BibTeX export | Markdown covers basic export need |
| Source open-access badge | Useful but not core to the evidence workflow |
| AI theme suggestions | Validate manual workflow first |
| AI evidence suggestions | Validate manual workflow first |
| AI source summary | Validate manual workflow first |
| External source search (Semantic Scholar import) | Manual add sufficient for MVP |
| Key finding flag | Nice-to-have; not core |
| Claim confidence level | Nice-to-have; not core |

### P2 — Future

| Feature | Reason to defer |
|---------|----------------|
| AI outline structure suggestion | Validate manual outline first |
| DOCX / LaTeX export | Higher implementation cost |
| JSON research archive export | Infrastructure complexity |
| Local-first (SQLite) persistence | Firestore acceptable for MVP |
| Offline access | Requires significant architectural work |
| Local AI models (Ollama) | External API sufficient for P1 AI features |
| Source sharing between projects | Adds complexity to data model |
| Collaborative projects | Multi-user architecture required |
| PDF text extraction | Requires third-party service |

---

## 11. Features to Remove or Downgrade

The following features from the original concept are explicitly evaluated:

| Feature | Decision | Reason |
|---------|----------|--------|
| Semantic search as the primary UI | **Remove from core; downgrade to P1 import helper** | ScholarForge is not a search engine. Students already have Semantic Scholar. Semantic search as a source-discovery layer is a convenience, not a value proposition. |
| AI-generated outlines (full IEEE scaffold) | **Remove; replace with evidence-linked outline** | An AI-generated outline does not help students learn to connect their own evidence. The value is in the student building the outline from their own claims and evidence. AI can suggest structure at P2, after the manual workflow is validated. |
| Ollama local AI in MVP | **Remove from MVP** | Local AI adds significant setup complexity. External AI API is sufficient for P1 AI features. Local-first AI is a P2 goal. |
| CrossRef + Semantic Scholar as primary search | **Downgrade to P1 convenience import** | Source discovery is a solved problem. The core workflow starts after the student already has a source. |
| Citation style switching as P0 | **Downgrade to P1** | IEEE default is sufficient for MVP. The citation rendering infrastructure exists; the selector is a small P1 add-on. |
| "Full text editor" in-app | **Confirmed removed** | ScholarForge is a research workspace, not a writing tool. Export to Markdown is the bridge to the student's own writing tool. |
| Competing with Zotero for citation management | **Confirmed removed** | ScholarForge is not a reference manager. Basic citation rendering for export purposes is retained; deep citation management (browser import, PDF metadata extraction) is out of scope. |
| Fully local database in MVP | **Confirmed deferred to P2** | Firestore is acceptable. Architecture must be repository-abstracted from day one. |
| Automated paper writing | **Confirmed removed** | Violates the AI philosophy. AI assists; the student writes. |
| Rate-limit / network-hiccup messaging | **Retain as basic error handling** | A simple "try again" message on failed API calls is table-stakes reliability. |

---

## 12. AI Requirements

### AI Capabilities (P1 unless noted)

| Capability | Description | Notes |
|-----------|-------------|-------|
| Theme suggestion | Given a project's evidence collection, suggest 3–7 candidate theme names with descriptions | P1 |
| Evidence-to-claim matching | Given a claim statement, rank existing project evidence by relevance | P1 |
| Source summary | Given a source's abstract + extracted evidence, produce a 100–150 word summary | P1 |
| Evidence relevance for outline section | Given a section title and writing notes, rank project evidence by relevance | P1 |
| Outline structure suggestion | Given themes and claims, suggest a possible outline section order | P2 |
| Research gap suggestion | Identify topics mentioned in evidence but not yet covered in themes/claims | P2 |

### AI Limitations (enforced by system)

- AI must not generate new evidence items (fabricated quotes or findings).
- AI must not fabricate citation data or page references.
- AI must not create claims that are presented as verified student research.
- AI must not modify existing student-created content without an explicit accept action.
- AI must not write the student's final paper or produce submission-ready text.

### Transparency Requirements

- Every AI-generated item carries a persistent "AI Suggestion" label until accepted.
- AI summaries are labeled "AI-Generated — not verified."
- An AI suggestion that is accepted is converted to student-owned content; the "(from AI suggestion)" note is editable by the student.
- The student must make an explicit action (click "Accept") to incorporate any AI output.
- AI suggestions that are not acted on within a session are discarded unless explicitly saved.

### Hallucination Safeguards

- AI suggestions are generated from the student's own project data (evidence text, source abstracts). The AI does not retrieve external information.
- AI summaries are grounded in the source's abstract and the student's extracted evidence. No external retrieval is performed.
- Evidence suggestions are re-ranked from the student's existing evidence pool; the AI does not introduce new evidence.
- A post-suggestion display shows which source each AI-suggested evidence item came from, so the student can verify provenance before accepting.

### Privacy Requirements

- Research content sent to an external AI API must not include: student email, student name, user ID, or any other personally identifiable information.
- The AI request contains only: project-scoped research content (evidence text, source abstracts, theme names, claim statements).
- The AI provider is accessed through an `AIService` interface. The concrete provider (OpenAI, Gemini, etc.) is configured via environment variable. Changing provider requires no application logic change.
- If the external AI API is rate-limited or unavailable, the application degrades gracefully: AI features show "AI unavailable — try later" and all non-AI features continue to function.

---

## 13. Local-First Requirements

### Current MVP — Firestore Acceptable

Firestore is the persistence layer for MVP. The following Firestore-specific behaviors are acceptable:

- Collections: users, projects, sources, evidence, notes, themes, theme_evidence, claims, claim_evidence, claim_themes, outlines, outline_sections, outline_section_claims, outline_section_evidence
- Firestore security rules enforce user ownership (userId match required for all reads and writes)
- Firestore is accessed only from the infrastructure layer; never from domain or application code

### Architecture Preparation (Required in MVP)

The repository pattern must be implemented from the start:

```typescript
// Domain/application layer knows only the interface:
interface SourceRepository {
  findById(id: string, userId: string): Promise<Source | null>
  findByProject(projectId: string, userId: string): Promise<Source[]>
  save(source: Source): Promise<void>
  delete(id: string, userId: string): Promise<void>
}

// Infrastructure layer provides the implementation:
class FirestoreSourceRepository implements SourceRepository { ... }

// Dependency injection wires them together:
const sourceRepo: SourceRepository = new FirestoreSourceRepository(db)
```

This pattern must be applied to every entity repository. No application or domain layer code may import `firebase/firestore` or any Firestore-specific type.

### Future Local-First (P2)

When local-first is implemented, the following changes are required:

- `FirestoreRepository` implementations are replaced by `SQLiteRepository` implementations.
- A local embedding engine (Ollama + `nomic-embed-text`) replaces any cloud-based semantic search.
- A local AI model (Ollama + `llama3.2` or equivalent) replaces the external AI API.
- Local file storage replaces Firestore document storage for large text fields (if needed).
- Offline sync strategy is defined (last-write-wins or CRDT).

No MVP code should need to change in the domain or application layer when this migration occurs. Only the infrastructure implementations are swapped.

---

## 14. Export Requirements

### MVP Exports (P0)

**Full Research Structure — Markdown**

```markdown
# [Project Name]
**Research Question:** [Research question]
**Exported:** [date]

> ScholarForge Research Export — this is an organizational scaffold, not a finished paper.

---

## Sources

### [Source Title] ([Year])
**Authors:** [Authors]
**Type:** [Type] | **DOI:** [DOI] | **Access:** [Open Access / Paywalled / Unknown]
**Citation (IEEE):** [formatted citation]
**My Note:** [student note]

#### Evidence
1. "[Quote]" (p. [page])
   *My note: [student note]*

---

## Themes

### [Theme Name]
[Description]

**Linked Evidence:**
- "[Quote]" — [Source Title] (p. [page])

---

## Claims

### [Claim Statement]
**Confidence:** [Speculative / Supported / Strongly Supported]

**Supporting Evidence:**
- "[Quote]" — [Source Title] (p. [page])

---

## Outline

### [Section Title]
**Writing Notes:** [student's planning notes]

**Claims:**
- [Claim statement]

**Evidence:**
- "[Quote]" — [Source Title] (p. [page])
```

**Outline Writing Scaffold — Markdown**

A condensed version showing only the outline with claims and evidence per section. Intended as the student's writing brief.

### Post-MVP Exports (P1)

- **BibTeX** — all sources as valid `.bib` file (see FR-074)
- **Citation copy** — single formatted citation to clipboard (FR-073)

### Future Exports (P2)

| Format | Notes |
|--------|-------|
| DOCX | Microsoft Word format using a template |
| LaTeX | `.tex` file with `\bibliography` block |
| JSON | Machine-readable research archive |
| Full project ZIP | All of the above in one archive |

---

## 15. Architecture Requirements

### Overview

ScholarForge uses a **modular-monolith** architecture in TypeScript. All modules run in a single process but have clear boundaries enforced by module ownership and dependency direction rules.

### Layers (per module)

```
domain/       — Pure TypeScript entities, value objects, domain rules.
               No external dependencies. No Firestore. No Express.

application/  — Use cases (CreateSource, AddEvidence, LinkEvidenceToClaim, etc.).
               Depends on domain and repository interfaces.
               No Firestore. No HTTP.

infrastructure/ — Concrete repository implementations (Firestore, later SQLite).
                  HTTP controllers (Express/Next.js route handlers).
                  AI provider implementations.
```

### Dependency Direction Rule

```
domain ← application ← infrastructure
```

The domain layer knows nothing about the application layer. The application layer knows nothing about the infrastructure layer. The infrastructure layer may import from both.

Violations of this rule (e.g., importing Firestore in a use case) are a build-time architectural error.

### Repository Interfaces

Each module defines its own repository interface in its `application/` layer:

```typescript
// src/modules/evidence/application/EvidenceRepository.ts
export interface EvidenceRepository {
  findById(id: string, userId: string): Promise<Evidence | null>
  findBySource(sourceId: string, projectId: string, userId: string): Promise<Evidence[]>
  findByProject(projectId: string, userId: string): Promise<Evidence[]>
  save(evidence: Evidence): Promise<void>
  delete(id: string, userId: string): Promise<void>
}
```

### Dependency Injection

A composition root (e.g., `src/container.ts`) wires interfaces to concrete implementations. Frameworks such as `tsyringe` or manual construction are both acceptable.

```typescript
const evidenceRepo: EvidenceRepository = new FirestoreEvidenceRepository(db)
const addEvidenceUseCase = new AddEvidenceUseCase(evidenceRepo, sourceRepo)
```

### AI Abstraction

```typescript
// src/modules/ai/application/AIService.ts
export interface AIService {
  suggestThemes(evidence: Evidence[]): Promise<ThemeSuggestion[]>
  suggestEvidenceForClaim(claim: Claim, evidence: Evidence[]): Promise<EvidenceSuggestion[]>
  summarizeSource(source: Source, evidence: Evidence[]): Promise<string>
}
```

The concrete implementation (`OpenAIService`, `GeminiService`, etc.) is injected. No module's domain or application layer imports the concrete implementation.

### Firestore Implementation

- All Firestore SDK imports are confined to `src/infrastructure/firestore/`.
- Firestore security rules are the last line of defence; application-level user_id checks are the primary defence.
- Firestore real-time listeners are acceptable for the MVP UI but must go through infrastructure adapters, not directly in UI components.

---

## 16. Suggested Module Structure

```
src/
├── modules/
│   ├── projects/
│   │   ├── domain/
│   │   │   └── Project.ts
│   │   ├── application/
│   │   │   ├── ProjectRepository.ts        (interface)
│   │   │   ├── CreateProject.ts            (use case)
│   │   │   ├── UpdateProject.ts
│   │   │   └── DeleteProject.ts
│   │   └── infrastructure/
│   │       ├── FirestoreProjectRepository.ts
│   │       └── ProjectController.ts        (HTTP handlers)
│   │
│   ├── sources/
│   │   ├── domain/
│   │   │   └── Source.ts
│   │   ├── application/
│   │   │   ├── SourceRepository.ts
│   │   │   ├── AddSource.ts
│   │   │   ├── FetchSourceByDOI.ts
│   │   │   └── RemoveSource.ts
│   │   └── infrastructure/
│   │       ├── FirestoreSourceRepository.ts
│   │       ├── CrossRefClient.ts           (external API)
│   │       └── SourceController.ts
│   │
│   ├── evidence/
│   │   ├── domain/
│   │   │   └── Evidence.ts
│   │   ├── application/
│   │   │   ├── EvidenceRepository.ts
│   │   │   ├── AddEvidence.ts
│   │   │   ├── EditEvidence.ts
│   │   │   └── DeleteEvidence.ts
│   │   └── infrastructure/
│   │       ├── FirestoreEvidenceRepository.ts
│   │       └── EvidenceController.ts
│   │
│   ├── notes/
│   │   ├── domain/
│   │   │   └── Note.ts
│   │   ├── application/
│   │   │   ├── NoteRepository.ts
│   │   │   └── NoteUseCases.ts
│   │   └── infrastructure/
│   │       └── FirestoreNoteRepository.ts
│   │
│   ├── themes/
│   │   ├── domain/
│   │   │   └── Theme.ts
│   │   ├── application/
│   │   │   ├── ThemeRepository.ts
│   │   │   ├── CreateTheme.ts
│   │   │   ├── LinkEvidenceToTheme.ts
│   │   │   └── DeleteTheme.ts
│   │   └── infrastructure/
│   │       └── FirestoreThemeRepository.ts
│   │
│   ├── claims/
│   │   ├── domain/
│   │   │   └── Claim.ts
│   │   ├── application/
│   │   │   ├── ClaimRepository.ts
│   │   │   ├── CreateClaim.ts
│   │   │   ├── LinkEvidenceToClaim.ts
│   │   │   └── DeleteClaim.ts
│   │   └── infrastructure/
│   │       └── FirestoreClaimRepository.ts
│   │
│   ├── outlines/
│   │   ├── domain/
│   │   │   ├── Outline.ts
│   │   │   └── OutlineSection.ts
│   │   ├── application/
│   │   │   ├── OutlineRepository.ts
│   │   │   ├── CreateOutline.ts
│   │   │   ├── AddOutlineSection.ts
│   │   │   ├── ReorderSections.ts
│   │   │   ├── LinkClaimToSection.ts
│   │   │   ├── LinkEvidenceToSection.ts
│   │   │   └── GetCoverageReport.ts
│   │   └── infrastructure/
│   │       └── FirestoreOutlineRepository.ts
│   │
│   ├── citations/
│   │   ├── domain/
│   │   │   └── CitationFormatter.ts        (pure functions; no I/O)
│   │   ├── application/
│   │   │   └── FormatCitation.ts
│   │   └── infrastructure/
│   │       └── CitationController.ts
│   │
│   └── ai/
│       ├── domain/
│       │   ├── ThemeSuggestion.ts
│       │   └── EvidenceSuggestion.ts
│       ├── application/
│       │   ├── AIService.ts                (interface)
│       │   ├── SuggestThemes.ts
│       │   ├── SuggestEvidenceForClaim.ts
│       │   └── SummarizeSource.ts
│       └── infrastructure/
│           ├── OpenAIService.ts            (implements AIService)
│           └── AIController.ts
│
├── shared/
│   ├── errors/
│   │   └── DomainError.ts
│   ├── types/
│   │   └── Result.ts
│   └── utils/
│       └── timestamp.ts
│
├── infrastructure/
│   ├── firestore/
│   │   └── db.ts                          (Firestore instance)
│   ├── http/
│   │   └── router.ts
│   └── auth/
│       └── SessionMiddleware.ts
│
└── container.ts                            (composition root)
```

---

## 17. MVP Backlog

### P0 — Must Have (MVP)

| # | Feature | Description | Dependencies |
|---|---------|-------------|--------------|
| 1 | User Authentication | Signup, login, logout, session management, account deletion cascade | None |
| 2 | Project CRUD | Create, read, update, delete projects; dashboard counts; data isolation | Auth |
| 3 | Source Management | Manual add source, read status, general note, evidence count indicator, remove | Projects |
| 4 | Evidence CRUD | Add evidence (quote + page + note), edit, delete, view by source, view all | Sources |
| 5 | Standalone Notes | Create/edit/delete project-level notes not tied to sources | Projects |
| 6 | Theme Management | Create themes, link/unlink evidence, evidence count display | Evidence |
| 7 | Claim Management | Create claims, link evidence and themes, unsupported claim indicator | Evidence, Themes |
| 8 | Outline Builder | Add/reorder/delete sections, link claims and evidence, writing notes, coverage view | Claims, Evidence |
| 9 | Citation Rendering | Format source as APA/MLA/IEEE from stored metadata, copy to clipboard | Sources |
| 10 | Markdown Export | Full structure export; outline scaffold export | All above |
| 11 | Evidence Search | Keyword search within project evidence; filter by theme/claim/source | Evidence |
| 12 | Privacy Compliance | Access logging (CCA §26), PDPA account deletion cascade, data isolation | Auth |
| 13 | Repository Abstraction | All persistence behind interfaces; Firestore as implementation | All above |
| 14 | AI Abstraction Interface | AIService interface wired up; no concrete AI features yet | Architecture |

### P1 — Should Have (Post-MVP)

| # | Feature | Description | Dependencies |
|---|---------|-------------|--------------|
| 15 | DOI Metadata Fetch | Fetch source metadata from CrossRef by DOI | Sources |
| 16 | Citation Style Selector | Project-wide APA/MLA/Chicago/IEEE selector; immediate re-render | Citations |
| 17 | BibTeX Export | Per-source and all-sources BibTeX download | Sources, Citations |
| 18 | Open-Access Badge | Display access status on source cards | Sources |
| 19 | AI Theme Suggestions | Suggest themes from evidence; student accepts/rejects | AI interface, Evidence |
| 20 | AI Evidence-to-Claim Matching | Suggest evidence for a claim | AI interface, Claims |
| 21 | AI Source Summary | Summary from abstract + evidence; labeled as AI-generated | AI interface, Sources |
| 22 | External Source Search | Optional Semantic Scholar import in source-add workflow | Sources |
| 23 | Key Finding Flag | Mark evidence as key finding; filter by key findings | Evidence |
| 24 | Claim Confidence Level | Speculative / Supported / Strongly Supported | Claims |
| 25 | Terms/Consent Recording | ETA §9 consent record at signup | Auth |

### P2 — Future

| # | Feature | Description | Dependencies |
|---|---------|-------------|--------------|
| 26 | AI Outline Suggestions | Suggest outline structure from themes and claims | AI, Outline |
| 27 | Research Gap Suggestions | Identify evidence gaps in themes/claims | AI, Themes |
| 28 | DOCX Export | Word format export | Export |
| 29 | LaTeX Export | `.tex` + `.bib` export | Export |
| 30 | JSON Archive Export | Full machine-readable project archive | Export |
| 31 | SQLite Persistence | Replace Firestore with local SQLite | Repository interfaces |
| 32 | Local AI Models | Replace external AI API with local Ollama | AI interface |
| 33 | Offline Access | Full offline-capable local-first operation | SQLite, Local AI |
| 34 | PDF Text Extraction | Extract text from uploaded PDFs for evidence | Sources |
| 35 | Source Sharing | Share a source library between projects | Projects, Sources |

---

## 18. Acceptance Criteria

### AC-01 — Creating a Research Project

```
Given a student is logged in,
When they create a project with name "AI in Education" and research question "How does AI affect learning outcomes?",
Then the project appears in their project list,
  and the project dashboard shows: 0 sources, 0 evidence, 0 themes, 0 claims, 0 outline sections,
  and no other user can see this project.
```

### AC-02 — Adding a Source

```
Given a student has an open project,
When they add a source with type "journal article", title "Learning with AI", authors ["Smith, J."], year 2023,
Then the source appears in the project's source list with status "Unread",
  and the project dashboard source count increments by 1.
```

### AC-03 — Extracting Evidence

```
Given a student has added a source to their project,
When they add evidence with quote "Students using AI tutoring showed improved test scores", page reference "p. 12", note "Supports my main claim",
Then the evidence appears in the source's evidence list,
  and the evidence appears in the project-wide evidence list,
  and the source's evidence count indicator shows at least 1 evidence item.
```

### AC-04 — Linking Evidence to a Theme

```
Given a student has created a theme "AI Effectiveness" and has evidence in their project,
When they link two evidence items to that theme,
Then the theme shows evidence count = 2,
  and the theme detail view lists both evidence items with their source titles,
  and the evidence items still appear in their source views (they are not moved).
```

### AC-05 — Linking Evidence to a Claim

```
Given a student has created a claim and has evidence in their project,
When they link evidence to the claim,
Then the claim no longer shows "No evidence linked",
  and the claim detail view shows the linked evidence with source and page reference.
```

### AC-06 — Outline Coverage View

```
Given a student has an outline with 4 sections,
  and 2 sections have linked claims and evidence,
  and 2 sections have no links,
When the student views the outline coverage report,
Then the 2 empty sections are visually flagged as "No claims or evidence linked".
```

### AC-07 — Evidence Search

```
Given a project with 20 evidence items,
When a student searches for the keyword "polarization",
Then only evidence items containing "polarization" in the quote or student note are returned,
  and each result shows the source title and quote excerpt.
```

### AC-08 — Markdown Export

```
Given a student has a project with 3 sources, 10 evidence items, 2 themes, 3 claims, and an outline with 4 sections,
When the student exports the full research structure as Markdown,
Then the downloaded file contains: project name, research question, all 3 sources with citations, all 10 evidence items under their sources, both themes with linked evidence, all 3 claims with linked evidence, and the outline with linked claims and evidence per section,
  and the file header identifies it as a research scaffold, not a finished paper.
```

### AC-09 — AI Suggestion Labeling

```
Given a student requests AI theme suggestions,
When the AI returns 3 candidate themes,
Then each suggestion is labeled "AI Suggestion" and visually distinct from student-created themes,
  and no suggestion appears in the student's theme list until the student clicks "Accept",
  and rejecting a suggestion removes it without creating any theme.
```

### AC-10 — Account Deletion

```
Given a student has 2 projects, each with sources, evidence, themes, claims, and an outline,
When the student deletes their account and confirms by re-entering their email,
Then the user record is deleted,
  and all projects, sources, evidence, notes, themes, claims, outlines, and citations are deleted,
  and the student cannot log in again with those credentials,
  and no data from any other user is affected.
```

---

## 19. Success Metrics

### Primary Metrics (Validate Core Hypothesis)

| Metric | Definition | Target |
|--------|-----------|--------|
| Evidence linkage rate | % of saved evidence items linked to at least one theme or claim | ≥ 70% within a single research session |
| Outline evidence coverage | % of outline sections with at least one linked evidence item when export is triggered | ≥ 80% |
| Claim support rate | % of claims with at least one piece of supporting evidence | ≥ 75% |
| Workflow completion rate | % of students who create a project and reach at least the "outline with linked evidence" state | ≥ 50% in a semester-long study |

### Secondary Metrics

| Metric | Definition |
|--------|-----------|
| Tool switching reduction | Student self-report: fewer tools needed simultaneously (survey item) |
| Research session length | Time from project creation to first export (proxy for workflow efficiency) |
| Evidence-per-source rate | Mean number of evidence items extracted per source (indicates depth of use) |
| Return rate | % of students who use ScholarForge for more than one assignment |
| AI acceptance rate | % of AI suggestions accepted vs. rejected (if AI features ship) |
| Export frequency | % of students who export their structure before writing |

### Anti-Metrics (Signal That Something Is Wrong)

| Anti-metric | What it signals |
|------------|----------------|
| High source count, near-zero evidence count | Students are treating ScholarForge as a bibliography manager, not a workspace |
| High evidence count, near-zero theme/claim count | Students are extracting evidence but not using the organizational layer |
| High outline section count, near-zero linked evidence | Students are treating the outline as a text editor |

---

## 20. Research Validation Hypotheses

### H1 — Research Organization Problem

**Hypothesis:** University students working on multi-source research assignments experience significant friction organizing their evidence and connecting it to their arguments.

**Test:** Semi-structured interviews asking students to walk through their current research workflow for a recent assignment.

**Confirms H1 if:** Students describe using ≥ 3 tools simultaneously, report losing track of which evidence supports which argument, or describe the gap between "I've read everything" and "I know what I'm arguing" as a significant time cost.

**Disconfirms H1 if:** Students report that their current workflow (e.g., Notion database, index cards, Zotero notes) is working well and they feel their evidence is well-organized and connected to their arguments.

---

### H2 — Evidence Traceability Problem

**Hypothesis:** Students frequently lose track of which specific quote or finding from which specific source supports which specific argument.

**Test:** Ask students in interviews: "When you're mid-draft and you need to find which source a specific point came from, how long does that take? Does it ever fail?"

**Confirms H2 if:** Students report spending > 5 minutes locating a source for a specific quote, or report that citations in their final paper are sometimes inaccurate because they couldn't find the original source.

**Disconfirms H2 if:** Students report that they always know which source a quote came from and can find it immediately, or report that Zotero/note-taking app satisfactorily handles this.

---

### H3 — Research-to-Outline Problem

**Hypothesis:** There is a significant and painful gap between having a pile of evidence and being able to write a structured, evidence-backed outline.

**Test:** Ask students to describe how they go from "finished reading" to "starting to write." Ask specifically how they build their outline and how they know which evidence belongs in which section.

**Confirms H3 if:** Students describe the outline-building phase as taking days, being primarily mental work, and/or resulting in sections that they "fill in" during writing rather than planning upfront.

**Disconfirms H3 if:** Students report that building an outline is quick and easy given their current tools, or that their courses do not require this level of evidence-to-argument traceability.

---

### H4 — Local/Privacy Value

**Hypothesis:** Students (especially in contexts handling sensitive research topics) care about keeping their research materials private and on their own machine.

**Test:** Ask students: "How would you feel about your research notes and extracted quotes being stored in a cloud service? Would a local-first option (data stays on your laptop) change whether you'd use the tool?"

**Confirms H4 if:** ≥ 30% of students express concern about cloud storage of research notes, or express a clear preference for local-first storage.

**Disconfirms H4 if:** Students are indifferent to data location and treat cloud storage as the default expectation with no concern.

---

*End of ScholarForge SRS v2.0*
