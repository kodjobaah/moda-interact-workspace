---
id: ARCH-036-SHARED-003
architecture_id: ARCH-036
title: Publish the approved discount contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-SHARED-001", "ARCH-036-SHARED-002"]
enables: ["ARCH-036-API-001", "ARCH-036-API-002", "ARCH-036-API-003", "ARCH-036-COMMERCE-001", "ARCH-036-BACKGROUND-001", "ARCH-036-BACKGROUND-002", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-SHARED-003 — Publish the approved discount contracts

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Publish the two *accepted* Shared contracts: Woo coupon read-page and bounded send-time proof. There is no recovery-policy schema change.

## Context

SHARED-001 and SHARED-002 are distinct cross-service API/Background wire boundaries, not a database or merchant-selection storage contract. Publish only after both have been architect accepted.

## Scope

Version/publish accepted read-page and proof exports; verify exact version and no additional source changes. Existing Shopify `/recovery-policy` export must remain unchanged.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Publication only: no implementation, tests/lint/build repeats, rollout into consumers, or new provider/policy behavior inside this release task.

## Work Items

- [ ] Verify accepted prerequisite commit/version pair.
- [ ] Publish release with approved release commands.
- [ ] Verify expected version/exports are visible in npm registry.
- [ ] Record registry and dependency pin evidence.

## Interfaces / Contracts

Publish `@modainteract/moda-interact-shared` version with coupon read-page and coupon proof. Existing recovery-policy exports remain backward compatible.

## Dependencies

- `ARCH-036-SHARED-001`
- `ARCH-036-SHARED-002`

## Enables

- `ARCH-036-API-001`
- `ARCH-036-API-002`
- `ARCH-036-API-003`
- `ARCH-036-COMMERCE-001`
- `ARCH-036-BACKGROUND-001`
- `ARCH-036-BACKGROUND-002`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Expected exact package version is registry-visible.
- [ ] No unauthorised implementation changes and no consumer work.
- [ ] Published exports match the two accepted contract tasks.

## Validation

- [ ] Accepted prerequisite evidence and release metadata review
- [ ] Publish command plus registry version/export verification
- [ ] Diff limited to release metadata; `git diff --check`

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

Publication-only: do not rerun unit tests, lint, typecheck or build for already accepted implementations.

For developer execution, use the canonical `/moda_developer_create ARCH-036-SHARED-003` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-SHARED-003`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
