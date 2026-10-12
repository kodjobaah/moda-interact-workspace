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
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-MCP-015
enables:
  - ARCH-032-COMMERCE-001
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-MCP-016 — Certify MCP policy failure handling on disposable PostgreSQL

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Prove the actual policy-backed MCP execution and missing-policy incident path against migrated disposable PostgreSQL.

## Context

Source-level tests cannot certify transactional incident persistence, refresh semantics and readiness under missing policy. This task is validation-only unless tests expose a narrowly scoped defect owned by MCP-015.

## Scope

Extend disposable PostgreSQL integration harness to create/update/remove an environment policy and execute real MCP protocol requests with injected bounded provider stubs. Test limit changes, missing/invalid/unavailable policy, readiness transitions, zero provider calls on missing policy, platform-wide generic incident creation and recurrence deduplication, plus incident-write outage isolation. Cover same policy for published and preview invocation where preview transport is available.

## Out of Scope

No Docker image redesign, no Shopify credential use, no Admin/UI implementation, no _index.md changes.

## Requirements

Keep tests deterministic, isolated and disposable. Do not call Render or a real merchant. Avoid weakening missing-policy behaviour merely to make startup succeed; fixtures must intentionally create a valid policy.

## Work Items

- [ ] Add disposable PostgreSQL fixtures for policy and incident schema.
- [ ] Exercise HTTP readiness, policy enforcement, updates, missing-policy failure, and error/event correlation.
- [ ] Record exact test evidence and cleanup results.

## Interfaces / Contracts

Uses database policy, Shared generic incident models and MCP published/preview execution contracts. No new production event schema.

## Dependencies

- ARCH-032-MCP-015

## Enables

- ARCH-032-COMMERCE-001

## Acceptance Criteria

- [ ] Fresh integration fixture deliberately provisions the policy.
- [ ] Removing required policy rejects execution and produces a platform-scoped incident.
- [ ] Policy changes affect subsequent execution and enforce timeout/request/bytes budgets.
- [ ] A failed incident write does not conceal the original policy-failure code.

## Validation

- [ ] npm run typecheck:integration
- [ ] npm run test:integration:docker with disposable PostgreSQL
- [ ] npm run typecheck; npm run lint; npm test; npm run build

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This is a **portable task definition**, `defined but not materialised`: no branches, commits, pushes, claims or worktrees have been created by this artifact. Run `/moda_developer_create ARCH-032-MCP-016` after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the user confirms architecture reconciliation.

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
