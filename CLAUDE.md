# CLAUDE.md — How ClockChasers Uses AI on ScholarForge

This file documents how the team uses AI coding tools on this repo, for grading transparency (see `.docs/00-charter/project-charter.md` Team Rules).

## Tools used

- **Claude Code** (this CLI) for implementation, debugging, and documentation work, using the specialized subagents in `.claude/agents/`:
  - `requirement-writer` — turns raw pain points into structured specs under `.docs/01-requirements/01-spec/` and keeps `backlog.md` in sync.
  - `tester` — drives the running app through Playwright to verify a spec file against real browser behavior; never edits source to force a pass.
  - `diagram-checker` — checks diagrams in `.docs/02-design/diagrams/` stay consistent with the spec they describe.
- AI is used for: generating first-draft code from an agreed spec, writing/fixing tests, debugging failing tests, and drafting documentation — never for inventing user research, test results, or metrics.

## Review process

- Every AI-generated change is read and understood by the team member who requested it before it's committed.
- AI-authored code goes through the same PR review as human-authored code (see Team Rules in the charter) — no exception for "AI wrote it."
- AI is not used to write the Role Statement reflections, interview findings, or test session logs — those must reflect what a real person actually did/said.

## Boundaries

- No real user data (interview answers, test session transcripts, survey responses) is ever fabricated by AI. Where no real-user data exists, the gap is labeled `SECONDARY`/`PROXY` per the course rubric instead of invented.
- Legal/compliance rules for AI-assisted work on this repo are in [`rule.md`](rule.md) — read before touching anything that stores or processes user data.
