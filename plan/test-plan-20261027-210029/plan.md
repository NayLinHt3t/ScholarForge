# ScholarForge — Test Plan

Status: DRAFT, blocked on environment (§7). Goal: verify all 14 specs under `.docs/01-requirements/01-spec/` behave as written, at every test level, ending in real-user UAT with quantified usability/adoption metrics.

## 1. Scope

**In scope**
- All 61 functional/non-functional/legal requirement IDs across the 14 specs (full list: `research/spec-inventory.md`).
- Auth, project CRUD, search, library, citation formatting/export, outline generation/export, summarization, compliance logging, search-quality (badges/cap/access-warning).
- UAT with real students (the actual target user — not internal testers) on the full golden path: signup → search → save → cite → generate outline → export.

**Out of scope**
- Load/stress testing beyond the stated NFR targets (e.g. not testing beyond P95 single-concurrent-user latency claims).
- Penetration testing (separate security-expert engagement if needed).
- Semantic Scholar / CrossRef / Ollama internal correctness — treated as external dependencies; only ScholarForge's handling of their responses (success, partial failure, total failure, malformed data) is tested.

## 2. Test Levels

| Level | What | Tooling | Owner |
|---|---|---|---|
| L1 — Unit | Pure functions: `toIEEE`, BibTeX formatter, citation validator, embedding cosine-sim, threshold/cap config constants | pytest (existing: `tests/test_models.py`, `test_services_*.py`) | existing suite, extend as gaps found |
| L2 — Integration | Route handlers against test DB: auth, projects, sources, evidence, notes, claims, outline routes | pytest (existing: `tests/test_routes_*.py`) | existing suite, extend as gaps found |
| L3 — System / E2E (browser) | Full stack, real browser, real UI, spec-by-spec acceptance criteria | `tester` subagent + Playwright MCP, against a running local instance | `tester` agent |
| L4 — UAT | Real students, real tasks, think-aloud + post-task survey | Moderated or remote-unmoderated sessions, recorded | human-run, this plan coordinates |

L1/L2 already have 14 test files — this plan does **not** re-litigate those; L3 is the current gap (no browser-level verification exists yet), L4 doesn't exist yet.

## 3. Test Case Matrix (L3 — System/E2E, by `tester` agent)

One `tester` invocation per spec file, each walking its FR/NFR/LR checklist end-to-end in a real browser. IDs reference `research/spec-inventory.md`.

| Run | Spec file | Priority checklist focus | Depends on |
|---|---|---|---|
| T01 | account-auth | AUTH-FR-01..06, AUTH-NFR-01/02/03 | none (gates everything else) |
| T02 | project-management | PROJ-FR-01/02/03, PROJ-NFR-01/02 | T01 (needs a session) |
| T03 | semantic-search | SRCH-FR-01/02/03, SRCH-NFR-01/02 | T01, T02 |
| T04 | search-low-confidence | SRCH-FR-04, SRCH-NFR-03 | T03 |
| T05 | search-quality-access | SRCH-FR-05/06, RELY-FR-01, SRCH-NFR-04 | T03 |
| T06 | resource-library | LIB-FR-01..04, LIB-NFR-01 | T03 (needs search results to save) |
| T07 | citation-formatting | CITE-FR-01/02, CITE-NFR-01/02 | T06 |
| T08 | citation-style-bibtex-export | CITE-FR-03/04, CITE-NFR-03/04 | T06 |
| T09 | outline-generation-core | GENC-FR-01/02, GENC-NFR-01/02 | T06 (needs saved sources), requires Ollama up |
| T10 | outline-generation-enhancements | GEN-FR-01/02 | T09 |
| T11 | project-switcher-regen-consent | PROJ-FR-03, GEN-FR-03, AUTH-FR-06, GEN-NFR-01, AUTH-NFR-03 | T09, T01 |
| T12 | outline-export | EXP-FR-01, EXP-NFR-01/02 | T09 |
| T13 | source-summarization | SUMM-FR-01..04, SUMM-NFR-01..04 | T06, requires Ollama up |
| T14 | compliance | COMP-FR-01/02, COMP-NFR-01/02 | cross-cutting — run last, inspect logs from T01–T13's traffic |

Run order matches dependency column (auth and project scoping first; compliance last since it audits log output from every prior run). Each run produces a PASS/FAIL table per the `tester` agent's standard output format (see `.claude/agents/tester.md`).

## 4. UAT Plan (L4)

### 4.1 Participants
- **n ≥ 10 sessions**, real students (target user group) who have an active research/writing assignment — not developers, not people who built the app.
- Recruit via university research-methods channels or similar; no compensation requirement stated, but a small incentive (e.g. gift card) improves completion/attention.
- Record informed consent for the session itself (recording, data use) — separate from the app's own AUTH-FR-06 consent flow; keep UAT consent records outside app data per PDPA data-minimisation (don't mix UAT research data into production tables).

### 4.2 Task script (golden path, timed, think-aloud)
1. Sign up for an account.
2. Create a project for a real or assigned research topic.
3. Search for papers on that topic using plain language (not exact titles).
4. Save 3–5 relevant papers to the project library; try to save a duplicate on purpose.
5. Switch citation style at least once; export BibTeX for one resource.
6. Generate an IEEE outline; regenerate one section.
7. Export the outline as PDF and Markdown.
8. Generate a source summary from 2+ selected resources; copy it.
9. Delete one resource from the library (confirm outline citations renumber).
10. Log out and log back in; confirm library/outline/project state persisted.
11. (Optional/stretch) Delete the account.

Each task gets: **completion (Y/N)**, **time on task**, **error count**, **moderator notes** (confusion points, verbatim quotes).

### 4.3 Session protocol
- Pre-session: brief consent, demographic/background questions (year of study, prior citation-tool use).
- During: think-aloud, moderator does not help unless participant is fully stuck (record the assist as a task failure/partial).
- Post-session: SUS questionnaire + TAM questionnaire (see §5) + 2–3 open debrief questions ("What was confusing?" "What would you change first?").

## 5. Metrics

### 5.1 Task performance (before/after)
"Before/after" = before vs. after a round of fixes driven by L3 findings and UAT round 1. Structure:
- Round 1 UAT (n≥10) against current build → baseline task completion rate, time-on-task, error count per task (from §4.2).
- Fix cycle informed by round 1 findings (owned by implementation agents, not `tester`).
- Round 2 UAT (n≥10, can reuse or refresh participants) on the same task script → compare completion rate, time-on-task, error count deltas per task.
- Report per-task and aggregate deltas; a task regressing between rounds is a flag, not noise — investigate before declaring the fix cycle done.

### 5.2 SUS (System Usability Scale)
- Standard 10-item SUS questionnaire, administered immediately post-session (recency).
- Score per participant (0–100 scale, standard SUS scoring: odd items score = response−1, even items score = 5−response, sum ×2.5).
- Report mean + SD per round; SUS ≥68 is the conventional "above average" bar — use it as the round-2 target, not a hard pass/fail gate for round 1.

### 5.3 Adoption model — TAM (recommended) or UTAUT2
**Recommendation: TAM.** At n≥10 per round, TAM's two core constructs (Perceived Usefulness, Perceived Ease of Use) plus Behavioral Intention to use give a reliable, interpretable signal without overfitting a 7-construct UTAUT2 model to a small sample. Use UTAUT2 only if a later, larger-sample study is planned (UTAUT2 adds Hedonic Motivation, Price Value, Habit, Facilitating Conditions — Price Value is irrelevant here since the tool is free/local, which further weakens the case for UTAUT2 at this scale).

- TAM items: standard 5-point or 7-point Likert, 3–4 items per construct (PU, PEOU, BI), administered alongside SUS post-session.
- Report mean per construct per round; compare round 1 vs. round 2 deltas alongside the SUS and task-performance deltas.

### 5.4 Roll-up report
One table per round: task completion %, mean time-on-task, mean errors, SUS mean, TAM PU/PEOU/BI means. Deltas round1→round2 in a second table.

## 6. Testing Schedule

| Phase | Activity | Depends on |
|---|---|---|
| 0 | Unblock environment: `.env` + Firestore service account key, Ollama install + model pull, Playwright MCP session restart/trust | none — **must complete before Phase 1** |
| 1 | L3 system/E2E runs T01–T14 via `tester` agent, in dependency order | Phase 0 |
| 2 | Triage L3 findings; fix cycle (implementation agents, not `tester`) | Phase 1 |
| 3 | Re-run any failed T0x checks to confirm fixes | Phase 2 |
| 4 | UAT round 1 (n≥10), task script + SUS + TAM | Phase 3 (app must be in a basically-working state before spending real user time on it) |
| 5 | Triage UAT round 1 findings; fix cycle | Phase 4 |
| 6 | UAT round 2 (n≥10), same script — before/after comparison | Phase 5 |
| 7 | Final roll-up report (task metrics, SUS, TAM, deltas) | Phase 6 |

No calendar dates assigned — each phase gates the next; durations depend on fix-cycle findings and UAT recruiting lead time, both unknown until Phase 1/4 run.

## 7. Current Blockers (must clear before Phase 1)

1. **No `.env`** — `GOOGLE_CLOUD_PROJECT` / `GOOGLE_APPLICATION_CREDENTIALS` unset.
2. **No Firestore service-account key** on disk.
3. **Ollama not installed** — required for GENC/GEN/SUMM spec runs (T09, T10, T11, T13).
4. **Playwright MCP not yet live in-session** — added to `.mcp.json` this session; a smoke-test run of the `tester` agent only had `Read`/`Bash` available, confirming the new MCP server needs a Claude Code restart (and MCP server trust approval) before any browser-level run can start.
5. **Port 8000 confirmed unreachable** (`curl` connection refused, nothing listening) — consistent with blockers 1–3, not a separate bug.

## 8. Deliverables

- This plan (`plan.md`) + spec inventory (`research/spec-inventory.md`).
- 14 `tester`-agent PASS/FAIL reports (Phase 1), filed under `phases/`.
- UAT raw data (task logs, SUS/TAM responses) — store outside app production tables (PDPA minimisation); redact participant PII before any report leaves this repo.
- Final roll-up report (Phase 7) with before/after deltas.
