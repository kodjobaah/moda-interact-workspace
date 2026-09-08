---
id: ARCH-006-SHARED-004
architecture_id: ARCH-006
title: Publish corrected merchant-communications shared release
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 27
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-006-SHARED-003
enables:
  - ARCH-006-BACKGROUND-004
  - ARCH-006-ADMIN-001
  - ARCH-006-SHOPIFY-001
created: 2026-09-06
updated: 2026-09-06
---
# ARCH-006-SHARED-004: Publish corrected merchant-communications shared release

## Architecture

`docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Publish and consumer-verify the corrected merchant-communications Node entrypoint as patch release `@modainteract/moda-interact-shared@0.7.1`.

## Context

`0.7.0` is a real published release and must remain historical. Its new `merchant-communications/node` export is broken at runtime. `SHARED-003` corrects the package boundary without changing contract semantics. This task is the publication gate for that correction.

## Scope

Patch-version metadata, npm publication, registry verification, and exact-package consumer import verification.

## Out of Scope

- Contract implementation changes.
- Refactoring.
- Consumer repository changes.
- Re-running broad implementation work already accepted under SHARED-003 except what `prepack` requires.

## Requirements

Do not publish until `ARCH-006-SHARED-003` is architect-accepted Complete.

Publish patch version `0.7.1` using repository conventions. Registry metadata alone is **not sufficient** for acceptance. After publication, create a temporary clean consumer (or equivalent isolated verification), install the exact registry version `@modainteract/moda-interact-shared@0.7.1`, import:

```text
@modainteract/moda-interact-shared/merchant-communications/node
```

and call at least `createTranslationBatchSubmitJobId`. The verification must use the published artifact rather than the source working tree.

## Work Items

- [x] Confirm SHARED-003 is architect-accepted Complete.
- [x] Bump package/lock metadata from `0.7.0` to `0.7.1`.
- [x] Publish `@modainteract/moda-interact-shared@0.7.1`.
- [x] Verify registry version, tarball, integrity and `latest` tag.
- [x] Install the exact published `0.7.1` into an isolated temporary consumer and prove the Node subpath imports/executes.
- [x] Record the exact published version and verification evidence.

## Interfaces / Contracts

Corrected consumer dependency:

```text
@modainteract/moda-interact-shared@0.7.1
```

Public APIs remain those already accepted under SHARED-001.

## Dependencies

`ARCH-006-SHARED-003`

## Enables

`ARCH-006-BACKGROUND-004`, `ARCH-006-ADMIN-001`, `ARCH-006-SHOPIFY-001`

## Acceptance Criteria

- [x] `0.7.1` is published and retrievable from the intended registry.
- [x] `latest` points to the corrected release unless publication policy explicitly requires otherwise.
- [x] A clean consumer can import the exact published `merchant-communications/node` subpath.
- [x] `createTranslationBatchSubmitJobId` executes from the published artifact.
- [x] No runtime contract semantics changed beyond the accepted export correction.
- [x] No consumer repository was modified.

## Validation

Publication mechanics plus isolated consumer import/runtime verification and `git diff --check`.

## Implementation Notes

Stop after publication verification. Do not update Background/Admin/Shopify dependencies; `moda_architect` will review SHARED-004 and then unblock consumer corrections.

Repository-agent hard stop: execute only SHARED-004. After publication and isolated registry-consumer verification, set this task to `review`, write the Completion Report as `Ready for Review`, and STOP. Do not mark this task Complete or architect-accepted. Do not change Background/Admin/Shopify task status, dependencies, package versions, or source code. `moda_architect` alone will accept the publication and unblock consumers.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-shared/package.json` - bumped the package version from `0.7.0` to `0.7.1`.
- `moda-interact-shared/package-lock.json` - synchronized the root package version to `0.7.1`.
- This task document - claim, publication report and review status.

### Work Completed

- Confirmed `ARCH-006-SHARED-003` is architect-accepted Complete before publication.
- Published `@modainteract/moda-interact-shared@0.7.1` to the public npm registry with the `latest` tag.
- Verified the exact published package from an isolated temporary consumer rather than the source working tree.
- Did not modify any consumer repository or downstream task state.

### Validation Results

- `npm publish --access public` - passed; published `@modainteract/moda-interact-shared@0.7.1`.
- `npm view @modainteract/moda-interact-shared dist-tags --json` - passed; `latest` is `0.7.1`.
- Registry metadata - passed; version `0.7.1`, tarball `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-0.7.1.tgz`, integrity `sha512-8eg6WGs3CsrT2z3k/KJxgfuz1aOZaYvloeawLnTarsymYn1LFLQaQdc2NpCsYJLkYShjJeSdiGwU54Xh5ivy6A==`.
- Isolated consumer - passed; exact `@modainteract/moda-interact-shared@0.7.1` installation imported `@modainteract/moda-interact-shared/merchant-communications/node` and executed `createTranslationBatchSubmitJobId` successfully.
- `git diff --check` - passed.

### Deviations

None.

### Assumptions

The npm registry's transient visibility delay after publication resolved before the final exact-version consumer verification.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Complete

### Decision

`moda_architect` independently reviewed the SHARED-004 publication snapshot and accepts the task.

Evidence accepted:

- npm publication notification independently confirms `@modainteract/moda-interact-shared@0.7.1` was published;
- the task records `latest=0.7.1` and the registry SHA-512 integrity;
- the task records a clean isolated consumer installing the exact registry `0.7.1`, importing `@modainteract/moda-interact-shared/merchant-communications/node`, and executing `createTranslationBatchSubmitJobId`;
- comparison with the accepted SHARED-003 snapshot shows the package publication changed only `package.json` and `package-lock.json`; no contract/runtime source changed;
- no consumer repository was modified by the Shared publication task.

The broken `0.7.0` release remains historical. The corrected consumer dependency is exactly `@modainteract/moda-interact-shared@0.7.1`. `moda_architect` now owns downstream readiness recalculation.
