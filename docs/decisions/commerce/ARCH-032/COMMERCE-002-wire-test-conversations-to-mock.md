---
id: ARCH-032-COMMERCE-002
architecture_id: ARCH-032
title: Wire Shared Studio Test Conversations to selectable tool execution
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-032-COMMERCE-001
enables:
- ARCH-032-COMMERCE-004
created: 2026-10-12
updated: '2026-10-15'
---

# ARCH-032-COMMERCE-002 — Wire Shared Studio Test Conversations to selectable tool execution

**Task state:** `complete` (developer-requested administrative closure on 2026-10-13). **Code review/certification:** evidence-limited; status is **not** a claim that every regression, integration test or live-provider check passed.

**Repository:** `moda-interact-commerce`. **Architecture:** `docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`.

## Completed scope — Shared runner and mode-switchable Test Conversations

The selected-shop Test Conversation path continues using the actual Shared `runCommerceTurn()` and the existing model, Redis run/history and shop-feature selection. It initially used deterministic fixtures; C005 later added selectable Local Preview, Live Test and Fixture clients.

### Implementation record

- Created `src/commerce/preview/mock-conversation-executor.ts` and connected fixture results to frozen conversation state.
- Added visible simulation provenance and conversation tool traces.
- Subsequent C005 dual-tool-client integration allows the same run workflow to select local real provider execution, remote published MCP execution, or fixture results without changing Shared's runner.
- No embedded MCP HTTP server was reintroduced.

### Validation evidence actually available

- C002 Attempt 1: 70/70 focused tests passed; typecheck/build issues were found.
- C002 Attempt 2: local log showed TypeScript PASS, build PASS and **73/73 focused tests passed** across eight suites.
- No post-C005-Attempt-6 full-suite result has been supplied.

### Deviations, boundaries and outstanding verification

- Local Preview provider calls and Live Test private-service parity have not been certified end-to-end on the final assembled code; retain these as outstanding validation, not passed evidence.
- Live Test must never silently fall back to Local Preview if MCP is unavailable.

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

Active `status`: `complete`. Active `depends_on`: `ARCH-032-COMMERCE-001`. Active `enables`: `ARCH-032-COMMERCE-004`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.
