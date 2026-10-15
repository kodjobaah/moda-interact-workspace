---
id: ARCH-032-MCP-016
architecture_id: ARCH-032
title: Certify MCP policy failure handling on disposable PostgreSQL
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-MCP-015
enables:
- ARCH-032-GATEWAY-002
- ARCH-032-SYSTEM-TEST-002
created: 2026-10-12
updated: '2026-10-15'
---

# ARCH-032-MCP-016 — Certify MCP policy failure handling on disposable PostgreSQL

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Prove the actual policy-backed MCP execution and missing-policy incident path against migrated disposable PostgreSQL.

## Context

Source-level tests cannot certify transactional incident persistence, refresh semantics and readiness under missing policy. This task is validation-only unless tests expose a narrowly scoped defect owned by MCP-015.

## Scope

Extend disposable PostgreSQL integration harness to create/update/remove environment entries inside the existing `PlatformBillingPolicy.mcpExecutionPolicy` JSONB and execute real MCP protocol requests with injected bounded provider stubs. Test limit changes, missing/invalid/unavailable policy, readiness transitions, zero provider calls on missing policy, platform-wide generic incident creation and recurrence deduplication, plus incident-write outage isolation. Certify published standalone MCP invocation only; Commerce Local Preview is a direct Commerce execution mode and is not an MCP protocol fixture or prerequisite for this task.

## Out of Scope

No Docker image redesign, no Shopify credential use, no Admin/UI implementation, no _index.md changes.

## Requirements

Keep tests deterministic, isolated and disposable. Do not call Render or a real merchant. Preserve the existing billing singleton seed and fields; fixtures must intentionally provision only the selected MCP environment JSONB entry. Do not weaken missing-entry behaviour merely to make startup succeed.

## Work Items

- [ ] Add disposable PostgreSQL fixtures for the existing billing policy singleton, optional MCP JSONB environments and incident schema.
- [ ] Exercise HTTP readiness, policy enforcement, updates, missing-policy failure, and error/event correlation.
- [ ] Record exact test evidence and cleanup results.

## Interfaces / Contracts

Uses database policy, Shared generic incident models and standalone MCP published execution contracts. No new production event schema. Commerce Local Preview/Fixture paths remain Commerce-owned and outside MCP-016 certification.

## Dependencies

- ARCH-032-MCP-015

## Enables

- ARCH-032-GATEWAY-002
- ARCH-032-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Fresh integration fixture deliberately provisions only the required MCP JSONB environment entry; billing fields and singleton survive unchanged.
- [ ] Missing singleton, null/missing JSONB, missing environment entry, corrupt JSON/schema and database outage reject execution; deleting the required environment entry produces a platform-scoped incident.
- [ ] MCP JSONB environment changes and existing row-version increments affect subsequent execution; request/timeout/bytes budgets hold without redeploy.
- [ ] Concurrent billing-vs-MCP or cross-environment mutations never lose updates; stale create-clear-replay is rejected.
- [ ] A failed incident write does not conceal the original policy-failure code.

## Validation

- [ ] npm run typecheck:integration
- [ ] npm run test:integration:docker with disposable PostgreSQL
- [ ] npm run typecheck; npm run lint; npm test; npm run build

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. The parent task definition is now materialised on `task/ARCH-032-MCP-016`; the missing canonical parent worktree was created from `origin/main` for this dependency-frontier update. This eligibility update does not claim an implementation attempt. Keep all `docs/decisions/**/_index.md` unchanged until the user confirms architecture reconciliation.

## Completion Report

### Status
Not Started

### Files Changed
None

### Work Completed
None

### Validation Results
Not run

### Deviations
None

### Assumptions
None recorded

### Unresolved Issues
None recorded

### Architectural Concerns
None recorded

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed

### Reviewed Files
None

### Validation Reviewed
None

### Architecture Conformance
Pending

### Follow-up
None

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting. Earlier `depends_on`: `ARCH-032-MCP-015`. Earlier `enables`: `ARCH-032-COMMERCE-001`.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-MCP-015`. Active `enables`: `ARCH-032-GATEWAY-002`, `ARCH-032-SYSTEM-TEST-002`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Active JSONB platform-policy storage correction

The user directs reuse of the existing `billing.PlatformBillingPolicy` singleton with an optional environment-keyed MCP JSONB field. This active storage/scope decision supersedes earlier references to a new MCP policy model/table or per-environment rows, while preserving the historical task record, review evidence and existing task dependencies. No task is marked Complete by this definition update.


## 2026-10-15 — Active policy-certification scope clarification

This task certifies PostgreSQL-backed execution policy on the standalone MCP `tools/call` boundary only. It must not require direct Commerce Local Preview to call MCP, share its incident reporter, or use `PlatformBillingPolicy.mcpExecutionPolicy`. Standalone MCP callers, including Commerce Live Test, still require all four policy limits and fail-closed behaviour. This clarification supersedes historical preview-transport references without changing this task's dependencies, state, or acceptance requirements for published calls. No `_index.md` edits.
