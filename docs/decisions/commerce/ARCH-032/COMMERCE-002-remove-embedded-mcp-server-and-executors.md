---
id: ARCH-032-COMMERCE-002
architecture_id: ARCH-032
title: Remove Commerce Studio embedded MCP runtime
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-COMMERCE-001
enables: []
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-COMMERCE-002 — Remove Commerce Studio embedded MCP runtime

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Remove obsolete Commerce-hosted MCP server/execution implementation after thin-client parity is verified.

## Context

The user explicitly requires no embedded MCP execution in Commerce Studio. MCP execution must reside solely in standalone moda-interact-mcp.

## Scope

Delete legacy app/api/mcp/route.ts and associated Commerce MCP service/authorization/runtime modules, local-only execution adapters, stale tests and obsolete dependencies after confirming no non-MCP features import them. Move still-used authoring/preview types to appropriate Commerce-owned modules. Keep publishing, draft freezing, preview conversation runner and new thin client. Keep public Gateway denial for /api/mcp.

## Out of Scope

Do not delete Studio authoring tools, validated publication pipeline, preview sessions, background caller implementation or public Gateway protection. No _index.md changes.

## Requirements

A deleted route must not be replaced with a proxy/public facade; it should return 404 through the application. No local fallback execution. Remove only code proven obsolete via import graph and tests; report architectural dependencies instead of deleting legitimate shared code.

## Work Items

- [ ] Perform import/call-site inventory and remove obsolete runtime modules.
- [ ] Update route tests and Studio preview/authoring regressions.
- [ ] Verify no server-side embedded MCP executor remains and public ingress remains blocked.

## Interfaces / Contracts

Commerce Studio uses the private MCP client from COMMERCE-001; standalone MCP remains execution authority.

## Dependencies

- ARCH-032-COMMERCE-001

## Enables

None

## Acceptance Criteria

- [ ] Commerce /api/mcp is unavailable and never handles live execution.
- [ ] Studio previews and publications remain healthy using the thin client.
- [ ] No remaining dead imports, unused config keys or copied MCP runtime in Commerce.

## Validation

- [ ] Route-level 404 and Gateway deny regression checks
- [ ] Commerce tests, lint and production build
- [ ] Render Test Studio to private MCP smoke test

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This is a **portable task definition**, `defined but not materialised`: no branches, commits, pushes, claims or worktrees have been created by this artifact. Run `/moda_developer_create ARCH-032-COMMERCE-002` after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the user confirms architecture reconciliation.

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
