---
id: ARCH-032-MCP-014
architecture_id: ARCH-032
title: Persist MCP operational failures as App Events and Admin Support messages
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 14
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-013
enables:
- ARCH-032-SYSTEM-TEST-002
created: 2026-10-11
updated: '2026-10-15'
---

# MCP-014 — Operational tool failures: support messages and application events

## Decision

An actionable MCP tool execution failure must generate: a structured Shared log
with an exact failure code and per-occurrence UUID; a durable App Event per
occurrence; and one deduplicated SYSTEM support message per shop, capability
and exact error cause. Other errors (bad model arguments, unauthorised capability
names, transient rate limits) do not generate support cases.

No feature-specific dispatch is added to MCP. The notification policy is based on
stable error reasons emitted by the existing provider connection adapters.

## Repository decomposition

- `moda-interact-database`: schema and migration for operational incidents and
  append-only events under `support`; must merge before MCP/ADMIN generated clients.
- `moda-interact-mcp`: operational reporter, Shared logger integration, focused
  unit tests and disposable PostgreSQL integration coverage.
- `moda-interact-admin`: show open operational issues on the existing Merchant
  Support dashboard, link to their SYSTEM support messages and allow verified
  Admin resolution with an application event.

This cross-repository dependency requires architect sequencing; it does not
transfer Database/Admin source ownership to the MCP agent.

## Acceptance criteria

- For `MCP_WOOCOMMERCE_REST_GRANT_REVOKED`, one failed invocation creates an
  App Event keyed by the original unique error ID plus one SYSTEM support message.
- Repeated failures create distinct App Events but do not flood messages.
- The incident can be resolved by an authenticated Admin and emits a resolution
  event, independent of merchant-originated `needsAdminResponse` state.
- Existing Shared structured logging is used; notification write failures are
  separately identifiable and do not mask the original tool failure.
- No credential material, arbitrary tool arguments or raw provider failures are
  stored in events or messages.
- All MCP unit tests, the disposable PostgreSQL suite, and Admin validation pass.

## Activation boundary

The standalone `/api/mcp` route remains disabled in production until the broader
ARCH-032 system-test and Gateway activation tasks are approved. This task does
not route CommerceAgent traffic to the new service.

## Validation

- [ ] MCP typecheck, lint, unit tests and build.
- [ ] Disposable PostgreSQL migration and operational-event integration test.
- [ ] Admin typecheck, build and support security tests.
- [ ] Exact-baseline patch application and whitespace checks.

## Completion Report

### Status
Pending local validation and architect reconciliation.

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting. Earlier `depends_on`: `ARCH-032-MCP-013`. Earlier `enables`: None.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-013`. Active `enables`: `ARCH-032-SYSTEM-TEST-002`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Developer-directed source completion (authoritative)

**Active disposition: Complete.** The developer explicitly directed that ARCH-032 MCP tasks whose implementation is already in the uploaded codebase be marked `complete`. This decision overrides the earlier 2026-10-15 dependency-reconciliation hold for this task, including any older body text describing it as Ready, Pending, Blocked, Not Started or awaiting historical evidence. The YAML `status: complete` is authoritative.

**Inspected implementation:** Operational failure handling, notification reporting and tests are present.

Source and test-file evidence from the 2026-10-15 12:08 workspace snapshot (`moda-interact-mcp/`):

- `src/operational/notifications.ts`
- `src/mcp/execution.ts`
- `tests/unit/operational/notifications.test.ts`

**Completion authority:** explicit developer decision (`completion_mode: developer`); retrospective source-based reconciliation. This records completion of the *original bounded task scope*, not certification of subsequently discovered system-level defects or unimplemented follow-up tasks. Existing `depends_on` and `enables` remain intact; downstream eligibility is determined from current task metadata.

**Evidence boundary:** the files above were inspected for presence in the uploaded snapshot, not executed as a fresh CI or integration run. Historical branch/worktree provenance, original commits, test command results, pushes and any prior architect acceptance not visible in the snapshot remain unverified; no such evidence is fabricated. The earlier Completion Report and Architect Review remain historical records and are not retrospectively rewritten. Original `attempt`, `executor` and `claimed_at` values are preserved.
