# Test Plan — ScholarForge

Status: DRAFT — blocked on environment setup (see plan.md §7).

- `plan.md` — full test plan (scope, levels, test cases, UAT, metrics, schedule).
- `research/spec-inventory.md` — per-spec requirement inventory extracted from `.docs/01-requirements/01-spec/` (source of truth for test case IDs below).
- `phases/` — phase status logs, updated as execution proceeds.

Owner: tester agent (`.claude/agents/tester.md`) for all browser-level (system/E2E) checks. Unit/integration tests already exist under `tests/` (pytest, 14 files) — this plan does not duplicate those, it maps gaps and adds system/UAT layers on top.
