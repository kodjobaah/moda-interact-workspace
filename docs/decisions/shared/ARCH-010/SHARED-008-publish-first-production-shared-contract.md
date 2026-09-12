---
id: ARCH-010-SHARED-008
architecture_id: ARCH-010
title: Publish the clean first-production Shared billing contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: automatic
status: complete
priority: 7
executor: null
claimed_at: null
attempt: 1
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

Publication gate for the breaking pre-production cleanup defined by SHARED-007 and
`ARCH-010-first-production-baseline.md`.

## Objective

Publish the architect-accepted SHARED-007 contract as:

```text
@modainteract/moda-interact-shared@0.11.0
```

This is a publication-only task. It does not reopen Shared implementation semantics.

## Scope

Publication mechanics only:

- verify SHARED-007 is architect-accepted Complete;
- set package/release metadata to exactly `0.11.0`;
- create/inspect the package artifact;
- prove the packed artifact retains required ARCH-010 contracts;
- prove the packed artifact omits all SHARED-007 removed names;
- publish exactly once;
- verify registry version, `latest` and `dist.shasum`;
- make the package-version metadata durable in Git.

## Out of Scope

Do not:

- redesign or refactor Shared implementation;
- add runtime behaviour;
- edit consumer repositories;
- publish another version to repair documentation;
- rerun implementation tests/typecheck/lint merely to re-prove accepted SHARED-007 code.

Normal `npm pack` / `npm publish` lifecycle `prepack` build execution is permitted as
publication mechanics.

## Requirements

1. SHARED-007 is Complete.
2. Package and lockfile version are exactly `0.11.0`.
3. Packed/published artifact contains retained ARCH-010 billing contracts.
4. Packed/published artifact contains none of the SHARED-007 retired contracts.
5. `0.11.0` is published exactly once.
6. npm `latest` resolves to `0.11.0`.
7. Registry `dist.shasum` matches the pre-publication packed artifact.
8. Final package metadata is durable on Git.
9. No consumer repository is changed by this task.

## Work Items

- [x] Verify SHARED-007 is architect-accepted Complete.
- [x] Confirm `0.11.0` was not already present in npm.
- [x] Set `package.json` and `package-lock.json` to `0.11.0`.
- [x] Run `npm pack --dry-run --json`.
- [x] Inspect packed runtime/declarations for removed and retained contracts.
- [x] Publish `0.11.0` exactly once.
- [x] Verify npm version, `latest`, tarball and `dist.shasum`.
- [x] Commit and push the `0.11.0` package metadata.
- [x] Return evidence to `moda_architect`.

## Interfaces / Contracts

Consumer repositories may now adopt:

```text
@modainteract/moda-interact-shared@0.11.0
```

or the repository's exact compatible `0.11.x` pin convention through their own
ARCH-010 conformance tasks.

## Dependencies

```text
ARCH-010-SHARED-007  Complete
```

## Enables

This publication satisfies the SHARED-008 dependency for the tasks listed in the YAML
frontmatter. A consumer task becomes Ready only when **all** of its individual
`depends_on` tasks are Complete.

## Acceptance Criteria

- [x] `0.11.0` was absent before publication.
- [x] `npm pack --dry-run --json` produced version `0.11.0`.
- [x] Dry-run artifact shasum was
      `fd096379901d4c454bf1cde575b48621c1c21b79`.
- [x] Removed-contract scan of built output produced no matches.
- [x] Required retained ARCH-010 contracts were present in built runtime/declarations.
- [x] `npm publish` published `@modainteract/moda-interact-shared@0.11.0`.
- [x] Registry subsequently resolved version `0.11.0`.
- [x] Registry `latest` resolved to `0.11.0`.
- [x] Registry `dist.shasum` matched the dry-run artifact exactly.
- [x] Final version metadata is committed and pushed to Shared `main`.
- [x] No source semantics or consumer repository were changed by this publication.

## Validation

Developer publication evidence:

```text
pre-publication:
npm view @modainteract/moda-interact-shared@0.11.0 version
=> E404 / version absent

package.json:
0.10.0 -> 0.11.0

package-lock.json:
0.10.0 -> 0.11.0
```

`npm pack --dry-run --json` invoked the package's normal `prepack` build and succeeded.

Dry-run package metadata:

```text
name:
  @modainteract/moda-interact-shared

version:
  0.11.0

filename:
  modainteract-moda-interact-shared-0.11.0.tgz

entryCount:
  58

shasum:
  fd096379901d4c454bf1cde575b48621c1c21b79
```

Removed-symbol scan against built `dist`/package metadata produced no output for:

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

Retained-contract scan confirmed:

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

Publication succeeded:

```text
+ @modainteract/moda-interact-shared@0.11.0
```

The first immediate post-publish `npm view` returned a transient registry E404 during
propagation. The subsequent registry checks succeeded:

```text
version = '0.11.0'
dist.shasum = 'fd096379901d4c454bf1cde575b48621c1c21b79'

latest = 0.11.0

name = '@modainteract/moda-interact-shared'
version = '0.11.0'
dist.tarball =
  'https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-0.11.0.tgz'
dist.shasum = 'fd096379901d4c454bf1cde575b48621c1c21b79'
```

Registry shasum exactly matches the dry-run package artifact.

GitHub verification of the final publication metadata commit confirms that it changes
only:

```text
package.json
package-lock.json
```

and both changes are:

```text
0.10.0 -> 0.11.0
```

## Implementation Notes

The developer manually executed this publication because the code implementation had
already been architect-accepted under SHARED-007 and the remaining work was a simple
one-time release.

Publication was performed from `moda-interact-shared/main`. No synthetic SHARED-008
feature branch is required after the release has already happened.

## Completion Report

### Status

Complete — manual developer publication verified and architect-accepted.

### Files Changed

Shared repository:

```text
package.json
package-lock.json
```

Architecture/task documentation is reconciled separately by `moda_architect`.

### Work Completed

1. Confirmed `0.11.0` did not already exist.
2. Updated package and lockfile version to `0.11.0`.
3. Produced and inspected the dry-run package artifact.
4. Proved retired SHARED-007 contracts are absent.
5. Proved retained ARCH-010 contracts remain present.
6. Published `0.11.0` exactly once.
7. Verified npm version, latest tag, tarball and shasum.
8. Committed and pushed package metadata to `main`.

### Validation Results

```text
npm pack --dry-run --json:
  passed

normal prepack build:
  passed

removed-symbol scan:
  clear

retained-contract scan:
  passed

npm publish:
  succeeded

registry version:
  0.11.0

registry latest:
  0.11.0

registry dist.shasum:
  fd096379901d4c454bf1cde575b48621c1c21b79
```

### Deviations

Publication was executed manually from Shared `main`, rather than through a dedicated
SHARED-008 task worktree.

Accepted because:

```text
SHARED-007 implementation was already architect-accepted
only version metadata changed
publication occurred exactly once
registry evidence is complete
final version metadata is durable on origin/main
```

### Assumptions

None remaining.

### Unresolved Issues

None within SHARED-008.

### Architectural Concerns

Consumer readiness must be reconciled from the latest individual task YAML. Some
workspace task/index snapshots are stale and must not be used to infer readiness.

### Git / VCS

Accepted SHARED-007 implementation baseline:

```text
f26ebad
```

Final Shared `main` publication metadata commit:

```text
0526de05dbddef4fde2e20b12bd6b9e7cc2664c4
```

GitHub verification confirms commit `0526de0` changes only:

```text
package.json
package-lock.json
```

with version-only changes `0.10.0 -> 0.11.0`.

Final local Shared working tree was clean and `origin/main` contains `0526de0`.

## Architect Review

### Review Status

Accepted — Developer Publication Attempt 1.

### Review Notes

The publication satisfies the complete SHARED-008 release contract.

The transient immediate post-publish E404 is non-blocking because subsequent registry
reads resolved the new version and the registry shasum exactly matches the dry-run
artifact.

No source semantics were changed after SHARED-007 acceptance.

### Reviewed Evidence

```text
pre-publication npm E404 for 0.11.0
package/lockfile version diff
npm pack --dry-run artifact metadata
removed-symbol scan
retained-contract scan
successful npm publish
registry version/latest/tarball/shasum
GitHub commit 0526de0
```

### Architecture Conformance

Conformant.

This publication made the already-accepted clean Shared contract consumable without
reopening implementation semantics.

### Follow-up

Reconcile downstream tasks against their latest individual task YAML and promote only
those whose entire dependency sets are Complete.

**Architect decision: Accepted — Publication Attempt 1. ARCH-010-SHARED-008 is Complete.**
