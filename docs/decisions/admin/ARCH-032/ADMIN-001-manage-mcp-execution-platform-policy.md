---
id: ARCH-032-ADMIN-001
architecture_id: ARCH-032
title: Admin controls for required MCP execution policy
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-032-DATABASE-001
enables:
- ARCH-032-GATEWAY-002
- ARCH-032-SYSTEM-TEST-002
created: 2026-10-12
updated: '2026-10-15'
---

# ARCH-032-ADMIN-001 — Admin controls for required MCP execution policy

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Allow authorised platform administrators to create, update and clear each environment’s MCP execution policy within the existing Platform Policy page.

## Context

The MCP JSONB entry must be provisioned intentionally through Admin or an approved deployment operation. MCP must never create or silently replace it. Reuse the singleton `PlatformBillingPolicy` and its current audited admin controls.

## Scope

Extend the **existing System Controls > Platform Policy** page (`src/app/(protected)/system-controls/platform-policy/page.tsx`) with a bounded MCP Execution Policy section. Edit the selected canonical Commerce environment's entry inside `PlatformBillingPolicy.mcpExecutionPolicy`; no new policy page or table. Show field descriptions and units; distinguish missing environment entry from missing singleton, permit intentional create/update/clear, validate complete positive bounded integers and provider timeout <= total deadline. Perform whole-row optimistic concurrency using existing `PlatformBillingPolicy.version`, incrementing on every successful mutation (including clear). Preserve billing fields and all other environment entries, and use existing audited mutation patterns. Prevent double submit; show inline validation and stale-version conflicts.

## Out of Scope

No merchant-facing controls, no MCP execution runtime code, no policy defaults, no separate policy store, no _index.md changes.

## Requirements

Reuse platform-admin authorisation and audited `PlatformBillingPolicy` mutation infrastructure. Make environment and shared row version visible; ensure that concurrent billing and MCP writes, edits of separate environments, and create-clear-replay cannot silently overwrite each other. Treat JSON null/absent entry as unprovisioned. Changes become effective in MCP through its bounded refresh/re-read, without redeploying services.

## Work Items

- [ ] Inspect existing system-controls Admin pages and audit conventions.
- [ ] Implement server action, validation and scoped UI.
- [ ] Add focused authorisation/validation/concurrency regression tests.

## Interfaces / Contracts

Consumes the existing Prisma `PlatformBillingPolicy` row and `mcpExecutionPolicy` JSONB from ARCH-032-DATABASE-001; no local schema duplicate or second model. Audit environment, operation, previous/next version and actor without exposing private credentials.

## Dependencies

- ARCH-032-DATABASE-001

## Enables

- ARCH-032-GATEWAY-002
- ARCH-032-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Only authorised platform administrators may create/update/clear an MCP environment entry; other callers are denied.
- [ ] MCP controls appear on the existing Platform Policy page, with missing environment entries clearly visible and intentionally provisionable.
- [ ] Bounded validation, version-conflict feedback and double-submit protection work, including create-clear-replay and concurrent billing-policy updates.
- [ ] Existing billing fields, other environments, System Controls and merchant-facing UI remain unaffected.

## Validation

- [ ] Admin-focused server security tests
- [ ] npm run prisma:generate; npm run lint; npm run build
- [ ] Disposable PostgreSQL policy create/update race tests when feasible

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This is a **portable task definition**, `defined but not materialised`: no branches, commits, pushes, claims or worktrees have been created by this artifact. Run `/moda_developer_create ARCH-032-ADMIN-001` after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the user confirms architecture reconciliation.

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

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting. Earlier `depends_on`: `ARCH-032-DATABASE-001`. Earlier `enables`: `ARCH-032-MCP-015`.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-DATABASE-001`. Active `enables`: `ARCH-032-GATEWAY-002`, `ARCH-032-SYSTEM-TEST-002`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Active JSONB platform-policy storage correction

The user directs reuse of the existing `billing.PlatformBillingPolicy` singleton with an optional environment-keyed MCP JSONB field. This active storage/scope decision supersedes earlier references to a new MCP policy model/table or per-environment rows, while preserving the historical task record, review evidence and existing task dependencies. No task is marked Complete by this definition update.

## 2026-10-15 — Dependency Frontier Reconciliation

`ARCH-032-DATABASE-001` completed Attempt 1 with explicit developer completion and accepted review in parent commit `2d3dbcf9`. This task's sole declared dependency is now satisfied. Promote `pending` to `ready`; preserve `attempt: 0`, `executor: null`, and `claimed_at: null`. This is an eligibility update only, not an implementation claim or completion decision.
