---
id: ARCH-032-COMMERCE-001
architecture_id: ARCH-032
title: Route Studio published and draft tests to private MCP
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-MCP-017
  - ARCH-032-MCP-016
  - ARCH-032-ADMIN-001
enables:
  - ARCH-032-COMMERCE-002
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-COMMERCE-001 — Route Studio published and draft tests to private MCP

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Replace Commerce Studio’s local tool-execution route with a thin server-only MCP client for published and draft tests.

## Context

Studio prepares and validates features, tools and releases. Its test workflows should exercise the same standalone execution engine as Background, preserving frozen draft preview and selected-shop semantics.

## Scope

Implement private MCP SDK client configured using Render MCP_PRIVATE_HOSTPORT/approved full private endpoint; forward trusted selected shop and opaque authorised preview reference, not model-created tenant identity. Route Studio published-capability tests via normal tools/list/tools/call and draft preview tests via MCP-017 private preview reference flow. Retain existing preview conversation runner/orchestration, fixtures, model test UI, status and cancellation; remove their dependency on local execution adapters. Report MCP unavailable rather than silently using Commerce local executor.

## Out of Scope

Do not delete authoring, publication, Studio runner, model testing or unrelated pricing/knowledge code. No new public MCP route, no Background code changes, no _index.md changes.

## Requirements

Keep existing private network trust assumption and MCP context/header semantics. Do not leak secrets or trusted identity to browser. The Studio interface must display accurate remote test status and failures. Private link changes must not redirect Background until its separate cutover checkpoint.

## Work Items

- [ ] Inventory Studio preview execution call sites and preserve UI orchestration.
- [ ] Introduce a thin server-only MCP transport/client and switch preview/test execution.
- [ ] Add parity tests for published and frozen draft scenarios plus MCP outage fail-closed.

## Interfaces / Contracts

Uses MCP-017 private preview transport and existing published MCP JSON-RPC contract; reference existing shared Commerce schemas rather than copying them.

## Dependencies

- ARCH-032-MCP-017
- ARCH-032-MCP-016
- ARCH-032-ADMIN-001

## Enables

- ARCH-032-COMMERCE-002

## Acceptance Criteria

- [ ] Studio published and draft tool tests execute through standalone MCP, never local provider executor.
- [ ] Cross-shop preview ownership and cancellation are preserved.
- [ ] MCP unavailability produces explicit Studio failure without fallback.
- [ ] Studio authoring, validation and publication still function.

## Validation

- [ ] Focused Studio preview/authoring and MCP client tests
- [ ] npm run lint; npm test; npm run build (where declared)
- [ ] Private MCP integration in Render test, no Background URL change

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This is a **portable task definition**, `defined but not materialised`: no branches, commits, pushes, claims or worktrees have been created by this artifact. Run `/moda_developer_create ARCH-032-COMMERCE-001` after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the user confirms architecture reconciliation.

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
