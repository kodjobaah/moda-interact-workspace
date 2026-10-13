---
id: ARCH-032-COMMERCE-004
architecture_id: ARCH-032
title: Remove embedded Commerce MCP server and legacy editor-specific live-test pathway
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 35
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-032-COMMERCE-002
  - ARCH-032-COMMERCE-003
enables:
  - ARCH-032-COMMERCE-005
created: 2026-10-12
updated: 2026-10-13
---

# ARCH-032-COMMERCE-004 — Remove embedded Commerce MCP server and legacy editor-specific live-test pathway

**Task state:** `complete` (developer-requested administrative closure on 2026-10-13). **Code review/certification:** evidence-limited; status is **not** a claim that every regression, integration test or live-provider check passed.

**Repository:** `moda-interact-commerce`. **Architecture:** `docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`.

## Completed scope — Embedded MCP removal, not real-provider removal

Removed Commerce's obsolete embedded MCP HTTP endpoint/server and its runtime/authorisation assembly. The old Shopify Admin editor-specific Run Test checkpoint was removed; Shopify tool authoring and tool execution through Local Preview/Live Test remain part of the target product.

### Implementation record

- Deleted `app/api/mcp/route.ts` and the embedded `src/commerce/mcp/` server modules.
- Removed the old `CommerceBackend.mcp/runtime/execution` public assembly and fixed dependent imports.
- Removed the Shopify Admin editor-specific live-test server action and made draft saving/authoring validation work without its old gating checkpoint.
- Preserved capability authoring, publication and Shared-powered Studio runs. Provider-backed Local Preview was subsequently reintroduced in C005 through separate tool-client interfaces, **not** by restoring the embedded MCP server.

### Validation evidence actually available

- C004 Attempt 1: 26/26 focused tests and build PASS, but TypeScript errors remained.
- C004 Attempt 2: reported typecheck PASS, build PASS, lint 0 errors/12 warnings, **18/18 focused tests passed**; the C20 integration suite was blocked by its disposable-target safety guard.
- The blocked C20 suite is **not** recorded as passing.

### Deviations, boundaries and outstanding verification

- Ensure the Commerce `/api/mcp` route stays absent; the remote MCP client is not the embedded server.
- No change to Background's `CommerceMcpClient` or standalone MCP.

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
