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
status: blocked
priority: 53
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-SHARED-002
  - ARCH-032-DATABASE-002
enables:
  - ARCH-032-MCP-018
  - ARCH-032-COMMERCE-001
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-032-MCP-017 — Expose isolated remote Studio preview execution

## Execution hold — 2026-10-12

**DO NOT CLAIM OR IMPLEMENT IN THIS PHASE.** Deferred: standalone MCP remote preview-reference transport is not part of this phase. Earlier remote-first descriptions and dependencies are superseded by ARCH-032-COMMERCE-001 through COMMERCE-005. Reassess under a new approved future plan before unblocking.

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Make an authorised frozen Studio preview executable through standalone MCP without admitting drafts into published discovery.

## Context

The preview-execution core was delivered as an independent patch but is absent from the 16:07 workspace baseline. Reconcile and revise that core before transport integration; do not assume it is applied. Commerce currently freezes selections in a Commerce-only Redis aggregate, which is not a cross-service contract.

## Scope

Consume the published Shared preview-reference contract and immutable PostgreSQL snapshot from DATABASE-002. Implement a distinct private preview request/namespace that loads a short opaque reference server-side, verifies shop/environment/admin ownership and CLOSED status, validates exact frozen revision/hash/manifest, then dispatches using the existing MCP provider registry and renderer. Preserve normal published tools/list and tools/call unchanged. Reconcile the earlier preview core: remove its 30-minute TTL and preview-specific deadline, provider-request and response-size policy; MCP-015 will supply mandatory platform execution policy before cutover. Do not invent fixed fallback limits.

## Out of Scope

Do not add a second execution engine, a merchant-facing endpoint, a model-controlled arbitrary URL/schema payload, Commerce local fallbacks, or any additional preview-only budgets. Do not make calls from Background resolve draft references. No _index.md edits.

## Requirements

Trust the agreed private Render ingress, but require the Commerce server to establish the authenticated administrator and authorised shop before minting a reference. Extend only the private preview context to convey that server-established administrator identity, distinct from the existing Background assertion which must stay unchanged. MCP must independently compare the trusted preview context with persisted snapshot ownership, shop and environment; it must not use client-provided definitions or choose tenants from model arguments. Missing/CLOSED/revoked/mismatched references fail closed. Caller cancellation remains supported. No preview TTL or preview-only execution budget.

## Work Items

- [ ] Reconcile preview-core patch with current MCP baseline and remove preview-only TTL/limit duplication.
- [ ] Consume Shared-002 contract and DATABASE-002 immutable snapshot reader; reject unrecognised/closed/revoked references.
- [ ] Add isolated private preview protocol handler using the existing runtime registry, with no published catalogue mutations.
- [ ] Prove shop/environment/administrator isolation, no drafts in normal tools/list, cancellation and policy readiness gate.

## Interfaces / Contracts

Consume published SHARED-002 reference/snapshot types and DATABASE-002 immutable records; no Commerce-internal Redis schema dependency. Shared CommerceAgent runner stays unchanged. Published MCP discovery continues unchanged. Transport work may progress alongside MCP-015, but cannot be promoted before policy enforcement tests pass.

## Dependencies

- ARCH-032-SHARED-002
- ARCH-032-DATABASE-002

## Enables

- ARCH-032-MCP-018
- ARCH-032-COMMERCE-001

## Acceptance Criteria

- [ ] A frozen draft reference executes only in its original authorised Studio context without a TTL.
- [ ] Unpublished draft is not visible/callable through Background tools/list.
- [ ] Preview and published calls share provider execution and platform-policy enforcement when MCP-015 is integrated.
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
