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
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-DATABASE-001
enables:
  - ARCH-032-MCP-015
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-ADMIN-001 — Admin controls for required MCP execution policy

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Allow authorised platform administrators to create and edit each environment’s mandatory MCP execution policy.

## Context

The policy must be provisioned intentionally through Admin or an approved deployment operation. MCP must never create or silently replace it.

## Scope

Add a Platform Settings > MCP Execution Policy management page using existing Admin auth, navigation and audit patterns. Show each policy field with description and units; create when missing, edit via version-safe conditional update, validate positive bounded integers and provider timeout <= total deadline. Show policy-missing as actionable. Prevent double submit and display inline validation and conflict errors.

## Out of Scope

No merchant-facing controls, no MCP execution runtime code, no policy defaults, no separate policy store, no _index.md changes.

## Requirements

Reuse platform-admin authorisation and existing audited mutation infrastructure. Make environment scope and version visible. Changes should be effective in MCP through its defined refresh/re-read, without redeploying services. Guard against cross-environment changes.

## Work Items

- [ ] Inspect existing system-controls Admin pages and audit conventions.
- [ ] Implement server action, validation and scoped UI.
- [ ] Add focused authorisation/validation/concurrency regression tests.

## Interfaces / Contracts

Consumes ARCH-032-DATABASE-001 Prisma policy model; no local schema duplicate. Audit changes without exposing private credentials.

## Dependencies

- ARCH-032-DATABASE-001

## Enables

- ARCH-032-MCP-015

## Acceptance Criteria

- [ ] Only authorised platform administrators may create/update; other callers are denied.
- [ ] Missing policies are clearly visible and can be intentionally created.
- [ ] Bounded validation, version-conflict feedback and double-submit protection work.
- [ ] Existing System Controls and merchant-facing UI remain unaffected.

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
