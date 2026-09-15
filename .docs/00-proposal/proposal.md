# ScholarForge — Updated Proposal
*A local, account-based research assistant that turns a research idea into a cited project proposal.*

> Working name — rename freely. This proposal supersedes the earlier "citation-tool" framing; scope was expanded after clarifying requirements (see [Design draft](../02-design/) and the approved plan referenced from the backlog).

## Problem Statement

Students working on a thesis, research paper, or course project consistently struggle with the same early-stage bottleneck: **turning a rough idea into a grounded, well-sourced proposal.**

Concretely:

1. **Discovery starts before vocabulary does.** At the idea stage, a student often can't yet name the exact paper title, author, or precise keyword that would find the right literature — they only have a *concept* ("how social media algorithms might amplify polarization among teenagers"). Keyword-only search tools (Google Scholar, library catalogs) penalize this mismatch and return shallow or irrelevant results.
2. **Resources are scattered.** Papers get found in one tool, saved as browser bookmarks or a messy folder, cited by hand in a third tool — nothing connects "the papers I found" to "the proposal I'm writing," so students manually re-read and re-summarize sources every time they sit down to write.
3. **Citation formatting is tedious and error-prone.** Manually producing correct APA/MLA/Chicago/BibTeX entries — especially with multiple authors, missing fields, or preprints — is a common source of both wasted time and avoidable grade deductions.
4. **Going from "sources gathered" to "first words written" is the hardest step.** Most tools stop at bibliography management; none help assemble the gathered sources into a structured starting outline (introduction, literature review, methodology) grounded in what was actually found — leaving a blank-page problem exactly where help is needed most, with the actual writing still left entirely to the student either way.
5. **Existing AI-assisted tools carry costs and trust concerns that don't fit a student's situation**: recurring subscription fees, mandatory third-party logins (Google/Facebook), and sending personal research ideas and drafts to an external cloud LLM provider. Students and their institutions are increasingly privacy-conscious about where research data and account credentials go.

**Net effect**: the idea-to-proposal pipeline is fragmented across search, note-taking, citation, and writing tools, with no tool addressing the *semantic* gap between "an idea in a student's head" and "papers that are actually about that idea" — and no privacy-respecting, locally-run option that keeps the whole workflow, and the student's account, on their own machine.

## Target Users

**Primary**: undergraduate and graduate students actively working on a thesis, capstone project, term paper, or research proposal, who are:
- **Early-stage / idea-first**, without a reading list yet — they need to explore a concept, not look up a known paper.
- **Building a personal library over time**, across multiple sessions, that should persist and grow with their project (not a one-off search).
- **Writing-blocked at the drafting stage** — they have sources but need help structuring them into a coherent proposal outline with correct citations.
- **Privacy- and cost-conscious** — prefer or require a tool that doesn't demand a third-party login, doesn't send their research data to an external AI vendor, and doesn't carry a subscription fee, because it runs entirely on their own machine.

**Secondary (not directly designed for in v1, but who benefit indirectly)**: academic supervisors/advisors who receive better-structured, properly-cited starting points from students using the tool; peer study groups who might each run their own local instance and compare saved libraries informally.

**Out of scope for v1**: institutions wanting a multi-user hosted deployment, journal/publisher-facing citation workflows, any user needing collaborative real-time co-editing, and a rich in-app text editor for writing the final paper — these would require re-introducing the shared-server/cloud constraints this proposal deliberately avoids, or overstate what the app should actually do (see Solution Summary, point 4).

## Solution Summary

A locally-run web app (FastAPI + SQLite + local Ollama models) where a student:
1. Signs up with their own account (email/password, no third-party login),
2. Creates a separate **project** per assignment/thesis, so resources and ideas for different pieces of work never mix,
3. Within a project, describes a research idea in plain language and gets back semantically ranked papers (not just keyword matches), then saves relevant ones with auto-formatted citations (APA/MLA/Chicago/IEEE/BibTeX),
4. Generates a **read-only idea/outline scaffold** — bullet-point ideas and short example passages per section, grounded in that project's saved sources, following IEEE paper structure by default — which the student copies or downloads (PDF/Markdown) and uses as a starting point. **Writing the actual paper stays the student's own task**, done in their own word processor or LaTeX setup — the app is deliberately not a text editor.

Full technical approach, data model, and build order are captured in the approved implementation plan; feature-level detail is in the [Design draft](../02-design/).
