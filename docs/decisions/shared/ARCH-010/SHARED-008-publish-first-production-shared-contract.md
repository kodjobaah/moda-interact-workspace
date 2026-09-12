---
id: ARCH-010-SHARED-008
architecture_id: ARCH-010
title: Publish the clean first-production Shared billing contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 7
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-SHARED-007
enables:
- ARCH-010-ADMIN-002
- ARCH-010-ADMIN-003
- ARCH-010-ADMIN-010
- ARCH-010-BACKGROUND-001
- ARCH-010-BACKGROUND-003
- ARCH-010-BACKGROUND-006
- ARCH-010-BACKGROUND-007
- ARCH-010-BACKGROUND-008
- ARCH-010-BACKGROUND-009
- ARCH-010-BACKGROUND-010
- ARCH-010-BACKGROUND-012
- ARCH-010-BACKGROUND-016
- ARCH-010-SHOPIFY-006
- ARCH-010-SHOPIFY-007
- ARCH-010-SHOPIFY-008
- ARCH-010-SHOPIFY-015
- ARCH-010-SHOPIFY-017
- ARCH-010-SHOPIFY-023
created: 2026-09-12
updated: '2026-09-12'
---

# ARCH-010-SHARED-008: Publish the clean first-production Shared billing contract

## Architecture

Publication gate for the breaking pre-production cleanup defined by SHARED-007 and `ARCH-010-first-production-baseline.md`.

## Objective

Publish one new `@modainteract/moda-interact-shared` release containing all retained 0.10.0 ARCH-010 contracts plus the SHARED-007 removals.

Target version:

```text
0.11.0
```

This publication is required because the package contents change. It is not a duplicate publication of SHARED-001/003/005; those contracts were already coordinated into 0.10.0 and remain present.

## Context

Current published ARCH-010 package baseline:

```text
@modainteract/moda-interact-shared@0.10.0
```

SHARED-007 removes pre-production exports, so a new package artifact is required before consumers intentionally adopt the clean contract.

## Scope

- verify SHARED-007 is architect-accepted Complete;
- set package version to 0.11.0 using repository conventions;
- run the full publication validation contract;
- inspect packed artifact contents/declarations;
- publish exactly once;
- verify registry version and shasum;
- record the immutable publication evidence in Completion Report.

## Out of Scope

Do not edit consumer repositories, change retained contract semantics, or republish 0.10.0.

## Requirements

1. publish only after SHARED-007 is Complete;
2. npm package version is exactly 0.11.0;
3. packed artifact contains retained ARCH-010 contracts;
4. packed artifact does not contain the removed cancellation compatibility symbols or `BILLING_FREE_ALLOWANCE_EXHAUSTED`;
5. registry `latest` becomes 0.11.0 if normal repository publication conventions use `latest`;
6. record registry shasum after publication;
7. never publish twice to repair documentation-only metadata.

## Work Items

- [ ] Verify SHARED-007 accepted commit is the implementation baseline.
- [ ] Set version 0.11.0.
- [ ] Run tests/typecheck/build/pack validation.
- [ ] Inspect public billing declarations/exports.
- [ ] Publish once.
- [ ] Verify npm version, dist.shasum and `latest`.

## Interfaces / Contracts

Consumers should subsequently use `@modainteract/moda-interact-shared@0.11.0` (or the repository's exact compatible 0.11.x pin convention) when their ARCH-010 baseline-conformance task updates dependencies.

## Dependencies

`ARCH-010-SHARED-007` Complete.

## Enables

The clean release unblocks consumer cleanup tasks including ADMIN-010, BACKGROUND-001/BACKGROUND-012 and SHOPIFY-023.

## Acceptance Criteria

1. 0.11.0 is published exactly once;
2. npm registry reports version 0.11.0 and a recorded shasum;
3. packed/published artifact retains reconciliation, capacity-exhausted and refund contracts;
4. packed/published artifact omits all SHARED-007 removed symbols, including `BILLING_FREE_ALLOWANCE_EXHAUSTED`;
5. full repository validation passes;
6. no consumer repository is changed in this publication task.

## Validation

Run actual package scripts, including at minimum:

```text
npm test
npm run typecheck
npm run build
npm pack --dry-run
git diff --check
```

Then verify published registry metadata using the repository-approved npm commands and record exact output/version/shasum.

## Implementation Notes

This is a publication-only task. Do not opportunistically alter source after SHARED-007 acceptance.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Deviations
None.

### Assumptions
Publishing credentials/permissions are available to the assigned release path.

### Unresolved Issues
None at task definition time.

### Architectural Concerns
Stop on package-version drift or if the packed artifact differs from the accepted SHARED-007 source.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push/publication evidence.

## Architect Review

### Review Status
Pending

### Review Notes
Pending publication.

### Reviewed Files
None yet.

### Validation Reviewed
None yet.

### Architecture Conformance
Pending.

### Follow-up
None yet.
