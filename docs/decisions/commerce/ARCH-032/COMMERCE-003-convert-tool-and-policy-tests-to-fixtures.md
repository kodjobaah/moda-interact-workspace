---
id: ARCH-032-COMMERCE-003
architecture_id: ARCH-032
title: Support simulated saved-tool and policy tests without removing External HTTP live tests
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 25
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-032-COMMERCE-001
enables:
  - ARCH-032-COMMERCE-004
created: 2026-10-12
updated: 2026-10-13
---

# ARCH-032-COMMERCE-003 — Support simulated saved-tool and policy tests without removing External HTTP live tests

**Task state:** `complete` (developer-requested administrative closure on 2026-10-13). **Code review/certification:** evidence-limited; status is **not** a claim that every regression, integration test or live-provider check passed.

**Repository:** `moda-interact-commerce`. **Architecture:** `docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`.

## Completed scope — Saved-tool fixtures, policy simulation and External HTTP

Individual saved-tool/Policy Operation tests have explicit simulated-result support. External HTTP response-sample testing and the existing real External HTTP authoring observation/live test remain supported. This task did **not** prohibit provider-backed Local Preview introduced later.

### Implementation record

- Added a fixture-backed saved-tool execution adapter and a simulated Policy Operation test path.
- Preserved response-sample validation/rendering and labelled simulated results.
- After the later architectural clarification, **`createExternalIntegration()` and real External HTTP request execution, credential/connection management, authoring observation and live test are intentionally retained**.
- Removed only obsolete assertions expecting a `mockResult` argument on the unrelated Shopify Admin action.

### Validation evidence actually available

- C003 Attempt 1: typecheck PASS and build PASS; 111 of 112 focused tests passed.
- C003 Attempt 2 corrected one Shopify Admin test assertion. The subsequent uploaded terminal recording contained no new test results; that rerun is **not independently verified** here.

### Deviations, boundaries and outstanding verification

- Do not delete tests of the retained External HTTP live-test or connection-observation functionality.
- Individual tool tests and Policy Operation authoring remain subject to final full regression certification.

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
