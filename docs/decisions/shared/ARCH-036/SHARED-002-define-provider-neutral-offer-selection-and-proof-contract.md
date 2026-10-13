---
id: ARCH-036-SHARED-002
architecture_id: ARCH-036
title: "ARCH-036-SHARED-002 — Superseded: no new offer-proof Shared schema"
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-SHARED-002 — Superseded: no new offer-proof Shared schema


## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective


**SUPERSEDED.** Selection and proof are owned by existing API/Background/Commerce boundaries; no new published Shared proof contract is required. This task must not be claimed, materialised or implemented.

## Context


ARCH-036 Attempt 5 assigns this capability to `ARCH-036-BACKGROUND-003` and removes the earlier independent task or Shared/package boundary. The prior definition is retained only for historical traceability.

## Scope


None. Implementation ownership is `ARCH-036-BACKGROUND-003` under the revised parent architecture.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements


Do not implement any code, endpoint, package schema, publication, queue or configuration from this superseded task. No task depends on it.

## Work Items


None — superseded without execution.

## Interfaces / Contracts


None — the previous proposed contract/endpoint is no longer authorised.

## Dependencies


None — superseded.

## Enables


None — superseded.

## Acceptance Criteria


Not applicable — superseded task.

## Validation


Not applicable — no implementation.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes


Do not run `/moda-task` or `/moda_developer_create` for this task. Refer to `ARCH-036-BACKGROUND-003` and the ARCH-036 Attempt 5 architecture instead. No `_index.md` updates.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task not claimed.

### Deviations

None.

### Assumptions

The implementation executor will verify local checkout, dependencies and available toolchain at claim time.

### Unresolved Issues

None recorded by an implementation executor.

### Architectural Concerns

Report schema, cross-service or provider-proof deviations to `moda_architect` instead of silently expanding scope.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only, not implementation acceptance.

### Reviewed Files

Current 12 October 2026 source snapshot used to define ownership; implementation not yet reviewed.

### Validation Reviewed

None from this task.

### Architecture Conformance

To be determined after implementation inspection.

### Follow-up

Await canonical materialisation, execution and review.
