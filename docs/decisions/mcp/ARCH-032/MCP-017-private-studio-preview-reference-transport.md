---
id: ARCH-032-MCP-017
architecture_id: ARCH-032
title: Expose isolated remote Studio preview execution
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-032-COMMERCE-001
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-MCP-017 — Expose isolated remote Studio preview execution

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Make an authorised frozen Studio preview executable through standalone MCP without admitting drafts into published discovery.

## Context

The additive preview-execution core was delivered separately for local validation. Commerce Studio freezes drafts, but currently calls its own execution backend. This task wires the approved core through a private, short-reference transport.

## Scope

Inspect the actual current preview storage/contract and implement a private preview reference resolver which loads a frozen selected-shop/admin/environment definition from the authorised server-side store. Bind the reference to its owner, tenant and environment, prevent callers from supplying arbitrary executable definitions, and route execution through the same published-provider adapters/renderer with the same platform policy. Keep normal tools/list tied to active published release only. Reuse existing Studio preview lifecycle rather than adding an arbitrary 30-minute TTL.

## Out of Scope

Do not add a second execution engine, a merchant-facing endpoint, a model-controlled arbitrary URL/schema payload, Commerce local fallbacks, or any additional preview-only budgets. Do not make calls from Background resolve draft references. No _index.md edits.

## Requirements

Respect existing trusted Render private network; do not add new caller-auth mechanisms contrary to the agreed cutover scope. Enforce selected-admin/shop/environment isolation, fail on missing or revoked frozen definitions, and preserve user-requested cancellation. If a new cross-service contract or storage interface is required beyond existing Shared exports, stop and return that specific dependency to the architect for a Shared task before duplicating schemas.

## Work Items

- [ ] Confirm the previously delivered preview-execution core patch is applied and its focused tests pass before changing transport.
- [ ] Inspect current preview core and Studio storage/authoring contracts.
- [ ] Implement private preview reference resolution and request handler, using same execution registry as published tools.
- [ ] Add tenant isolation, draft invisibility, cancellation and parity tests.

## Interfaces / Contracts

Consume existing canonical Shared Commerce runner/descriptor schemas when sufficient. The frozen selection is the source of execution identity; Background continues using published tools/list and tools/call unchanged. The preview transport can be implemented while the policy tasks proceed independently, but Studio cutover requires policy enforcement acceptance.

## Dependencies

None

## Enables

- ARCH-032-COMMERCE-001

## Acceptance Criteria

- [ ] Draft reference can be executed only in its original authorised Studio context.
- [ ] Unpublished draft is not visible/callable through Background tools/list.
- [ ] Preview and published calls share provider execution and policy enforcement.
- [ ] Remote preview failures are visible to Studio; no local execution fallback.

## Validation

- [ ] Focused preview transport and HTTP protocol unit tests
- [ ] npm run typecheck; npm run lint; npm test; npm run build
- [ ] Disposable PostgreSQL/approved state-store integration and privacy tests

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This is a **portable task definition**, `defined but not materialised`: no branches, commits, pushes, claims or worktrees have been created by this artifact. Run `/moda_developer_create ARCH-032-MCP-017` after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the user confirms architecture reconciliation.

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
