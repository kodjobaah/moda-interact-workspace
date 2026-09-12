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
status: ready
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

Publication mechanics only:

- verify SHARED-007 is architect-accepted Complete;
- verify the implementation baseline is the accepted SHARED-007 commit;
- set package/release metadata to exactly `0.11.0` using repository conventions;
- create/inspect the package artifact using the normal npm pack/publication path;
- verify the artifact contains the accepted retained billing contract and omits the
  SHARED-007 removed names;
- publish exactly once;
- verify registry version, `latest` tag and `dist.shasum`;
- record immutable publication evidence in the Completion Report.

Do not rerun implementation validation merely to re-prove accepted code. If `npm pack`
or `npm publish` invokes the package's existing `prepack` build as part of normal
publication mechanics, that is allowed; do not run a separate build for revalidation.
## Out of Scope

Do not edit consumer repositories, change retained contract semantics, or republish 0.10.0.

## Requirements

1. SHARED-007 is Complete and its accepted implementation commit is the publication
   baseline;
2. package version is exactly `0.11.0`;
3. package artifact contains the retained ARCH-010 billing contracts;
4. package artifact contains none of the SHARED-007 removed symbols/values;
5. publish exactly once using the repository-approved npm release path;
6. registry reports `0.11.0`, expected `latest` tag and a recorded `dist.shasum`;
7. no consumer repository is changed;
8. do not publish twice to repair documentation-only metadata.
## Work Items

- [ ] Verify accepted SHARED-007 implementation commit is the release baseline.
- [ ] Set package/release metadata to `0.11.0`.
- [ ] Run `npm pack --dry-run --json` (or the repository-equivalent packaging command).
- [ ] Inspect packed runtime/declarations for retained and removed billing contracts.
- [ ] Publish exactly once.
- [ ] Verify registry version, `latest` and `dist.shasum`.
- [ ] Record package artifact/publication evidence and STOP.
## Interfaces / Contracts

Consumers should subsequently use `@modainteract/moda-interact-shared@0.11.0` (or the repository's exact compatible 0.11.x pin convention) when their ARCH-010 baseline-conformance task updates dependencies.

## Dependencies

`ARCH-010-SHARED-007` Complete.

## Enables

The clean release unblocks consumer cleanup tasks including ADMIN-010, BACKGROUND-001/BACKGROUND-012 and SHOPIFY-023.

## Acceptance Criteria

1. `0.11.0` is published exactly once;
2. npm registry reports version `0.11.0` and the recorded `dist.shasum`;
3. normal release tag is `latest` if that is the repository publication convention;
4. packed/published artifact retains reconciliation, generic capacity-exhausted,
   refund and purchased-credit billing contracts;
5. packed/published artifact omits every SHARED-007 removed symbol/value;
6. no source semantics are changed after SHARED-007 acceptance;
7. no consumer repository is changed.
## Validation

This is a `task_kind: publication` task. Do **not** run the implementation test suite,
typecheck, lint, Prisma validation or a standalone build to revalidate SHARED-007.

Before publication:

```text
1. verify git/branch/worktree baseline is the architect-accepted SHARED-007 commit
2. verify package.json/package-lock release metadata is 0.11.0
3. run npm pack --dry-run --json using repository conventions
4. inspect the packed file list and billing runtime/declaration contents
```

The packed artifact must contain the retained contract names:

```text
BILLING_SUBSCRIPTION_RECONCILE_QUEUE_NAME
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
BILLING_RECOVERY_CAPACITY_EXHAUSTED
BILLING_REFUND_REQUEST_RECEIVED
BILLING_REFUND_COMPLETED
BILLING_REFUND_REJECTED
createMerchantBillingSystemSourceKey
availablePurchasedRecoveryCredits
```

and must contain **none** of:

```text
SUBSCRIPTION_CANCELLATION_MODES
SubscriptionCancellationModeSchema
SubscriptionCancellationMode
ShopifySubscriptionCancellationArgs
SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS
BILLING_CANCELLATION_REQUEST_RECEIVED
BILLING_CANCELLATION_COMPLETED
BILLING_CANCELLATION_REJECTED
BILLING_FREE_ALLOWANCE_EXHAUSTED
BILLING_PLAN_CHANGE_ACTION_REQUIRED
```

Then publish once using the repository-approved npm command.

After publication verify and record the repository-equivalent outputs for:

```text
npm view @modainteract/moda-interact-shared@0.11.0 version dist.shasum
npm view @modainteract/moda-interact-shared dist-tags.latest
```

Expected:

```text
version = 0.11.0
latest = 0.11.0
dist.shasum = <record exact registry value>
```

If the release command's normal `prepack` lifecycle invokes a build, allow that lifecycle
to run. Do not invoke an additional test/typecheck/build cycle merely for revalidation.

If `0.11.0` already exists unexpectedly, the artifact differs from accepted SHARED-007,
or publication credentials are unavailable, STOP and return to `moda_architect`.
Do not increment the version or publish another version without architect direction.
## Implementation Notes

This is a publication-only task. Do not opportunistically alter source after SHARED-007 acceptance and do not rerun implementation validation merely to re-prove accepted code.

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
