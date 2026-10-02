# Project Charter for Software Engineering Case Study

## Project Title
ScholarForge — Local Research & Idea/Outline Assistant for Students

## Team Members

| Student ID | Name |
|---|---|
| 6631503079 | Nay Lin Htet |
| 6631503066 | Lin Myat Oo |
| 6631503067 | Min Htet Kaung Pyae |
| 6631503075 | Myo Min Min Oo |

> Reusing the team roster from the shared charter template — update this table if it differs for this project.

## 1. Purpose

To provide a locally-run, privacy-respecting research assistant for students that makes discovering relevant academic literature by *idea* rather than exact keywords, organizing sources per project, and drafting a structured starting outline for a thesis or research paper more convenient — without relying on third-party logins, cloud hosting, or external AI services.

## 2. Problem Statement

Students working on a thesis, research paper, or course project consistently struggle with the same early-stage bottleneck: turning a rough idea into a grounded, well-sourced starting point.

At the idea stage, a student often cannot yet name the exact paper title, author, or precise keyword that would find the right literature — they only have a concept. Keyword-only search tools penalize this mismatch and return shallow or irrelevant results. Sources that are found then get scattered across bookmarks, notes, and separate citation tools, with nothing connecting "the papers I found" to "the outline I'm trying to write." Manually producing correct citations is tedious and error-prone, and going from "sources gathered" to "first words written" is the hardest step most tools stop short of helping with.

In addition, existing AI-assisted research tools carry costs and trust concerns that don't fit a student's situation: recurring subscription fees, mandatory third-party logins, and sending personal research ideas to an external cloud AI provider.

## 3. Objectives

- Provide a single local platform for students to discover research papers by describing an idea in plain language, not just exact titles or keywords.
- Let students organize their research into separate projects, so different assignments and theses never mix.
- Allow students to save relevant papers into a project's library with automatically formatted citations (APA, MLA, Chicago, IEEE).
- Generate a structured idea/outline scaffold from a project's saved sources to reduce the blank-page problem — without claiming to produce a finished, submission-ready paper.
- Keep every account, all stored data, and the AI models used entirely on the student's own machine — no third-party identity provider, no external LLM API, no cloud hosting.
- Ensure every citation in a generated outline traces back to a real saved source, with no invented references.

## 4. Scope

The project focuses on developing a locally-run web application: ScholarForge.

The system will include:
- Local account system (email/password signup and login)
- Project-based workspaces for organizing research
- Idea-based semantic search across external academic sources
- Personal resource library, scoped per project
- Citation formatting (APA, MLA, Chicago, IEEE, BibTeX)
- AI-generated idea/outline scaffolding (read-only, section-by-section)
- Per-section outline regeneration
- Copy-to-clipboard and file export (PDF, Markdown)
- Reliability handling for external API and local AI-engine failures
- Compliance-driven data handling (logging, deletion, consent)

## 5. Target Users

### 5.1 Students (Primary Users)
- Create and manage separate research projects
- Describe a research idea in plain language
- Discover semantically relevant papers, not just keyword matches
- Save resources into a project's library with auto-formatted citations
- Generate an idea/outline scaffold grounded in their saved sources
- Regenerate individual outline sections
- Copy or export the outline and citations to continue writing in their own tool

### 5.2 Academic Supervisors/Advisors (Secondary, Indirect)
- Not direct users of the system in this version
- Benefit indirectly by receiving better-structured, properly cited starting points from students who used the tool

## 6. Proposed Solution

Develop a locally-run web application (FastAPI backend, SQLite database, local Ollama models) where a student signs up with their own account and creates a separate project per assignment or thesis. Within a project, the student describes a research idea in plain language and receives semantically ranked papers pulled from academic APIs, saves the relevant ones with automatically formatted citations, and generates a read-only idea/outline scaffold — bullet-point ideas and short example passages grounded only in that project's saved sources, following IEEE structure by default. The student then copies or downloads the scaffold and writes the actual paper themselves, in their own tool.

## 7. Core Workflow

Sign Up / Log In → Create Project → Describe Idea → Discover Papers → Save to Library → Generate Idea/Outline Scaffold → Copy or Export → Student Writes the Paper

## 8. Key Features

- Local account system (no third-party login)
- Project-based workspaces with isolated libraries and outlines
- Idea-based semantic search (conceptual, not keyword-only)
- Semantic re-ranking via local embeddings
- Personal resource library, scoped per project, with duplicate detection
- Citation formatting (APA, MLA, Chicago, IEEE, BibTeX)
- IEEE-structured idea/outline generation (RAG), grounded only in saved sources
- Citation-marker validation (no hallucinated references)
- Per-section outline regeneration
- Read-only outline view with copy and export (PDF, Markdown) — no in-app text editor
- Local LLM via Ollama for embeddings and generation (no external AI API)
- Graceful degradation when an external paper source or the local AI engine is unavailable

## 9. Success Criteria / KPIs

- Reduced time for students to find conceptually relevant papers compared to keyword-only search.
- A single tool covers idea search, source saving, and outline drafting instead of scattered tools and bookmarks.
- Reduced time and errors spent manually formatting citations.
- Reduced blank-page time when starting a proposal or paper section.
- Zero third-party identity provider and zero external AI API calls, confirmed in the running system.
- Deleting one project never affects another project's saved resources or outlines.
- Every citation in a generated outline traces to a real saved source — no invented references.
- Users can run the entire system locally through a standard web browser, with no cloud account required.

### Before → After

| Before | After |
|---|---|
| Papers found only by exact keyword or title match | Papers found by describing the underlying idea (semantic search) |
| Sources and citations scattered across bookmarks, notes, and separate tools | One local, project-scoped library with auto-formatted citations |
| Blank-page start when writing a proposal or paper | AI-generated idea/outline scaffold to kick off writing |
| Reliance on third-party logins and cloud AI tools with unclear data handling | Fully local accounts and a local AI engine — no data leaves the machine |
| Different projects' notes and sources mixed together | Separate projects keep each assignment's resources and outlines isolated |
