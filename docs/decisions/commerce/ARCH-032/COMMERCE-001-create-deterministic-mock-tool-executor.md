---
id: ARCH-032-COMMERCE-001
architecture_id: ARCH-032
title: Provide deterministic Studio fixture tool execution
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables:
- ARCH-032-COMMERCE-002
- ARCH-032-COMMERCE-003
created: 2026-10-12
updated: '2026-10-15'
---

# ARCH-032-COMMERCE-001 — Provide deterministic Studio fixture tool execution

**Task state:** `complete` (developer-requested administrative closure on 2026-10-13). **Code review/certification:** evidence-limited; status is **not** a claim that every regression, integration test or live-provider check passed.

**Repository:** `moda-interact-commerce`. **Architecture:** `docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`.

## Completed scope — Deterministic fixture executor

Implemented a deterministic, Shared-contract-compatible fixture executor. This is an **optional Fixture mode** for Studio; it is not the mock MCP client for provider-backed Local Preview.

### Implementation record

- Added `src/commerce/preview/mock-tool-executor.ts` and `tests/studio-mock-tool-executor.test.ts`.
- Match fixture results to shop, conversation, tool/revision and validated arguments. Missing or invalid fixtures fail rather than fabricate success.
- Fixture provenance is exposed separately from strict Shared tool-result data; fixture mode makes no provider or MCP requests.
- No changes to Shared `runCommerceTurn()` or the Background worker.

### Validation evidence actually available

- C001 Attempt 1 initially failed 5/5 tests due to an invalid test `providerModelId` containing `/`.
- C001 Attempt 2 corrected the fixture. The developer reported **all green** after rerunning validation; no per-command transcript or Git commit hashes were furnished for this task record.

### Deviations, boundaries and outstanding verification

- Real provider-backed Local Preview and remote Live Test are **not** provided by this fixture executor; they were implemented subsequently under C005 Attempt 4+.
- Keep the fixture-specific tests in future regression runs.

## Completion Report

### Status

`complete` — administrative closure requested by developer. This task definition was originally written for the **superseded mock-only phase** and has been reconciled to the later dual-client Studio architecture.

### Implementation attempts

2 patch attempt(s) were delivered for this task identifier. This documentation patch does not execute, merge, commit or push implementation code. Implementation commit hashes and final clean/upstream state were not supplied, so none are invented.

### Acceptance / validation distinction

The documented implementation milestone is closed at the developer's direction. Outstanding checks above remain genuinely **unverified or failing**, not silently waived. Any new regression correction should be tracked with explicit evidence; do not imply a complete passing full suite.

## Architect Review

### Review Status

Scope reconciled / administrative closure recorded. **Independent final production-readiness acceptance not asserted.**

### Review Notes

The authoritative target is: Commerce has no embedded MCP server; Local Preview can execute real tools directly; Live Test uses a thin standalone MCP client; Fixture mode is optional; Shared owns the CommerceAgent turn; External HTTP real execution is retained; and Commerce logs through Shared without incident persistence. Do not revive the older mock-only exclusions.

## 2026-10-15 — Architect dependency reconciliation

**Historical administrative completion retained:** this status records the existing developer-directed closure, not a new passing regression or integration certificate. Follow-up verification belongs to the new accepted dependency and terminal-system-test path.

Active `status`: `complete`. Active `depends_on`: None. Active `enables`: `ARCH-032-COMMERCE-002`, `ARCH-032-COMMERCE-003`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.
