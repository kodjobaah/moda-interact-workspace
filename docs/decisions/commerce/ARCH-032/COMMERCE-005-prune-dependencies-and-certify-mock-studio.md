---
id: ARCH-032-COMMERCE-005
architecture_id: ARCH-032
title: Complete Commerce MCP-server extraction and restore selectable real tool clients
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 45
executor: null
claimed_at: null
attempt: 6
depends_on:
  - ARCH-032-COMMERCE-004
enables: []
created: 2026-10-12
updated: 2026-10-13
---

# ARCH-032-COMMERCE-005 — Complete Commerce MCP-server extraction and restore selectable real tool clients

**Task state:** `complete` (developer-requested administrative closure on 2026-10-13). **Code review/certification:** evidence-limited; status is **not** a claim that every regression, integration test or live-provider check passed.

**Repository:** `moda-interact-commerce`. **Architecture:** `docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`.

## Completed scope — Final cleanup and dual tool-client architecture

Removed dead embedded-MCP and obsolete execution modules, then incorporated the user-directed correction: Local Preview must make **real provider requests** without MCP server load, Live Test must use a thin private MCP client, and Fixture mode remains optional. Studio only logs failures through the Shared logger; it does not create incidents.

### Implementation record

- Removed embedded MCP runtime packages and obsolete server diagnostics/tests. `@shopify/dev-mcp` remains only as a development-time Admin GraphQL schema source; it is **not** a runtime MCP client.
- Restored provider-backed local execution adapters (Shopify GraphQL, External HTTP, supported policy operations and Merchant Knowledge) through a **Local Preview** tool client.
- Added a **Remote Live Test** client for private standalone MCP `tools/list` and `tools/call`, and a tool-client selection seam without changing Shared `runCommerceTurn()`.
- Preserved real External HTTP connection management, authoring observation, execution and live tests. Studio-local execution must not emit ARCH-033 incidents: use the Shared logger.
- Added/retained a negative embedded-server boundary test; removed obsolete Shopify Admin editor-specific live-test assertions only, not retained authoring, publication, CAS or provider test coverage.

### Validation evidence actually available

- C005 Attempt 2: typecheck, lint (0 errors/12 warnings), build and 13/13 focused tests PASS.
- C005 Attempt 4: 31/31 focused tests PASS; typecheck, lint and full suite still had failures.
- Attempt 5: delivered incremental TypeScript/lint corrections for the new dual clients. **No post-Attempt-5 passing typecheck/build/full-suite result is in the supplied evidence.**
- Attempt 6: delivered test-only removal of seven assertions for the old Shopify Admin editor live-test/checkpoint. **No local rerun results for Attempt 6 have been supplied.**
- Last full regression evidence before Attempts 5–6: **1,295 passed, 37 failed, 7 skipped**. It is not a green certification.

### Deviations, boundaries and outstanding verification

- **Certification outstanding:** rerun typecheck, lint, full test suite and build on the complete Attempt-6 codebase; investigate all retained authoring regressions, do not delete valid tests merely to turn the suite green.
- Run local real Shopify/External HTTP provider smoke and published MCP Live Test, including capability catalogue, grant/tenant isolation, failures and no local fallback.
- Infrastructure-gated suites require disposable PostgreSQL/Redis; maintain their fail-safe target guards.
- MCP Platform Execution Policy and its incident reporter remain independent MCP-side work; Commerce itself logs through Shared only.

## Completion Report

### Status

`complete` — administrative closure requested by developer. This task definition was originally written for the **superseded mock-only phase** and has been reconciled to the later dual-client Studio architecture.

### Implementation attempts

6 patch attempt(s) were delivered for this task identifier. This documentation patch does not execute, merge, commit or push implementation code. Implementation commit hashes and final clean/upstream state were not supplied, so none are invented.

### Acceptance / validation distinction

The documented implementation milestone is closed at the developer's direction. Outstanding checks above remain genuinely **unverified or failing**, not silently waived. Any new regression correction should be tracked with explicit evidence; do not imply a complete passing full suite.

## Architect Review

### Review Status

Scope reconciled / administrative closure recorded. **Independent final production-readiness acceptance not asserted.**

### Review Notes

The authoritative target is: Commerce has no embedded MCP server; Local Preview can execute real tools directly; Live Test uses a thin standalone MCP client; Fixture mode is optional; Shared owns the CommerceAgent turn; External HTTP real execution is retained; and Commerce logs through Shared without incident persistence. Do not revive the older mock-only exclusions.
