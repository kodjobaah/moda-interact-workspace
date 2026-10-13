---
id: ARCH-032-GATEWAY-002
architecture_id: ARCH-032
title: Prepare and execute separately approved private MCP endpoint cutover and legacy Commerce MCP-route retirement
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: blocked
priority: 96
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-COMMERCE-002
  - ARCH-032-SYSTEM-TEST-001
  - ARCH-032-MCP-016
enables: []
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-GATEWAY-002 — Prepare and execute separately approved private MCP endpoint cutover and legacy Commerce MCP-route retirement

## Execution hold — 2026-10-12

**DO NOT CLAIM OR IMPLEMENT IN THIS PHASE.** Deferred: Background endpoint cutover is a separate approved operation; it is not a prerequisite for Commerce mock-first removal. Earlier remote-first descriptions and dependencies are superseded by ARCH-032-COMMERCE-001 through COMMERCE-005. Reassess under a new approved future plan before unblocking.

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Prepare and execute separately approved private MCP endpoint cutover and legacy Commerce MCP-route retirement.

## Context

Standalone MCP is already deployed privately in Render Test and live tools/list input-schema evidence passed; this alone does not certify the full Studio/Background cutover or production traffic.

## Scope

After explicit developer sign-off, validate Render private names/ports and configured COMMERCE_MCP_URL, move Background to the standalone private /api/mcp destination by environment configuration only, confirm Commerce Studio thin-client private endpoint, observe metrics/errors/incidents, verify public /api/mcp is inaccessible and Commerce route 404. Stage test first; production only after separate acceptance. Keep documented rollback to previous known-good environment wiring without reinstating local executors.

## Out of Scope

No runtime provider code, no alteration of Shared runner or Background job protocol, no public MCP service, no arbitrary Studio-auth network bypass and no `_index.md` changes.

## Requirements

Do not cut over on task creation or simply because a Render deployment exists. Gate each environment on SYSTEM-TEST-001 accepted, mandatory policy present/valid and explicit developer permission. An unavailable MCP should be clearly reported, never shadow-routed through Commerce.

## Work Items

- [ ] Verify accepted test evidence and developer cutover authorisation.
- [ ] Stage test environment-only URL/routing changes and smoke both Background and Studio.
- [ ] Record runbook, 404/public-denial proof, incident/health observation and production sign-off gate.

## Interfaces / Contracts

COMMERCE_MCP_URL retains the existing Background SDK protocol and trusted context; Commerce private client uses its own server-side full URL. No new external hostnames.

## Dependencies

- ARCH-032-COMMERCE-002
- ARCH-032-SYSTEM-TEST-001
- ARCH-032-MCP-016

## Enables

None

## Acceptance Criteria

- [ ] Background executes through standalone MCP with no job protocol changes.
- [ ] Commerce embedded /api/mcp cannot execute or proxy requests.
- [ ] Test evidence and production sign-off/rollback procedures recorded.

## Validation

- [ ] Gateway blueprint checks, Render Test smoke, system-test evidence, production deployment approval and git diff --check.

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This task is **defined but not materialised**: no branches, commits, pushes, claims or worktrees were created by this artifact. Run `/moda_developer_create ARCH-032-GATEWAY-002` only after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the developer explicitly closes architecture reconciliation.

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
