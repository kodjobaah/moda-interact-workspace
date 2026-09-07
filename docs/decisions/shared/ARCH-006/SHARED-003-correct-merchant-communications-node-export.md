---
id: ARCH-006-SHARED-003
architecture_id: ARCH-006
title: Correct merchant-communications Node package export
task_kind: correction
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 26
executor: copilot
claimed_at: 2026-09-06T14:20:47Z
attempt: 1
depends_on:
  - ARCH-006-SHARED-002
enables:
  - ARCH-006-SHARED-004
created: 2026-09-06
updated: 2026-09-06T14:47:00Z
---

# ARCH-006-SHARED-003: Correct merchant-communications Node package export

## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

Detailed reliability: `docs/architecture/ARCH-006-translation-batching-reliability.md`

## Objective

Correct the published-package export mapping for `@modainteract/moda-interact-shared/merchant-communications/node` without changing any accepted ARCH-006 contract semantics.

## Context

`@modainteract/moda-interact-shared@0.7.0` was published successfully, but the new Node subpath is not runtime-resolvable. The package export points to flat files:

```text
./dist/merchant-communications.node.js
./dist/merchant-communications.node.d.ts
```

while the accepted `tsup` entry name `merchant-communications/node` produces the package files under:

```text
./dist/merchant-communications/node.js
./dist/merchant-communications/node.d.ts
```

A downstream Background consumer therefore cannot import the architect-accepted deterministic job-ID helpers from the registry package.

## Scope

Shared package export/build metadata and focused artifact-entrypoint validation only.

## Out of Scope

- Changing merchant-communications schemas, enums, queue names, job names, payloads, language rules or job-ID algorithms.
- Adding new shared behavior.
- Modifying any consumer repository.
- Publishing a new npm version; `ARCH-006-SHARED-004` owns publication.
- Refactoring unrelated package exports.

## Requirements

Use the smallest correction that makes the existing Node subpath resolve to the files actually emitted by the accepted build. Prefer correcting the `./merchant-communications/node` `types` and `import` export targets to the existing nested build output rather than changing accepted source/module naming.

Add a focused validation that would have failed for `0.7.0`. Build success alone is insufficient. After the package build, validate package-export resolution through the package name/subpath, not by directly importing a file path. The validation must prove at least one accepted helper such as `createTranslationBatchSubmitJobId` can be imported and called.

Also verify the packed artifact contains the exact runtime and declaration files targeted by `package.json` exports.

## Work Items

- [x] Inspect the current `tsup.config.ts` output layout and confirm the actual nested Node entrypoint files.
- [x] Correct only the `./merchant-communications/node` export mapping needed for runtime/type resolution.
- [x] Add a focused package-entrypoint validation that imports the subpath through package exports after build.
- [x] Verify the packed artifact includes the runtime and declaration targets referenced by the export.
- [x] Run focused tests, typecheck/build and `git diff --check`.

## Interfaces / Contracts

The public import remains unchanged:

```ts
import {
  createTranslationBatchSubmitJobId,
} from "@modainteract/moda-interact-shared/merchant-communications/node";
```

No consumer-facing API shape or helper semantics change.

## Dependencies

`ARCH-006-SHARED-002` is Complete but published a package with a broken Node subpath. This correction is additive to that historical release; do not rewrite SHARED-002 history.

## Enables

`ARCH-006-SHARED-004`

## Acceptance Criteria

- [x] `@modainteract/moda-interact-shared/merchant-communications/node` resolves after a clean package build.
- [x] The packed artifact contains the runtime and declaration files referenced by the export map.
- [x] At least `createTranslationBatchSubmitJobId` imports and executes through the package subpath.
- [x] No accepted merchant-communications runtime/contract semantics change.
- [x] No consumer repository is modified.
- [x] Repository tests/typecheck/build remain green and `git diff --check` passes.

## Validation

Run the focused merchant-communications tests, repository typecheck/build, the new package-entrypoint/artifact validation and `git diff --check`.

## Implementation Notes

This is a package-boundary correction, not a redesign. Do not change deterministic job-ID formats merely because the export is broken.

Repository-agent hard stop: execute only SHARED-003, return it to `review`, and STOP. Do not publish `0.7.1`, do not edit SHARED-004 state, and do not modify Background/Admin/Shopify consumers.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-shared/package.json` - corrected the `merchant-communications/node` `types` and `import` targets to the nested tsup output.
- `moda-interact-shared/scripts/validate-merchant-communications-node.mjs` - validates package-name import, helper execution, export target files, and packed artifact contents.
- This task document - claim, implementation report and review status.

### Work Completed

- Corrected only the broken Node subpath export mapping from flat `dist/merchant-communications.node.*` paths to emitted `dist/merchant-communications/node.*` paths.
- Preserved all merchant-communications schemas, enums, queue names, payloads, language rules and deterministic helper algorithms.
- Added focused validation that builds the package, imports `@modainteract/moda-interact-shared/merchant-communications/node` by public package name, executes `createTranslationBatchSubmitJobId`, and checks both export targets in `npm pack --dry-run` output.
- Did not publish a new package version or modify any consumer repository/task.

### Validation Results

- `npm run validate:merchant-communications-node` - passed; build, public subpath import/helper execution, export target existence, and packed artifact checks passed.
- `npm test` - 92 passed, 1 skipped because `TEST_REDIS_URL` is not configured.
- `npm run typecheck` - passed.
- `git diff --check` - passed.

### Deviations

The validator uses `npm pack --dry-run --json --ignore-scripts` after the explicit build so prepack build logs cannot corrupt the JSON artifact manifest.

### Assumptions

`ARCH-006-SHARED-004` will publish the corrected package metadata in the next release without changing the public subpath or helper semantics.

### Unresolved Issues

None within SHARED-003. The correction is not published by this task, as required by the hard stop.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Complete

### Architect Decision

`ARCH-006-SHARED-003` is architect-accepted Complete.

Independent review confirmed that the correction is limited to the package export boundary and focused artifact validation. Compared with the accepted pre-SHARED-003 package snapshot, the package implementation changed only:

- `package.json`, correcting `./merchant-communications/node` from the nonexistent flat `dist/merchant-communications.node.*` targets to the actual nested `dist/merchant-communications/node.*` build output and adding the focused validation script; and
- `scripts/validate-merchant-communications-node.mjs`, which validates the public package-name/subpath import, executes `createTranslationBatchSubmitJobId`, verifies both export targets exist after build, and confirms those targets are present in `npm pack --dry-run` output.

No merchant-communications schemas, enums, queue/job names, payloads, language rules, deterministic job-ID algorithms, or consumer repositories changed. The repository agent correctly returned this task to `review` and stopped without publishing the patch release or promoting downstream consumers.

The supplied review archive does not include `node_modules`, so the reported npm commands were not re-run by the architect; the implementation and validator were inspected directly and the package diff was independently compared with the prior accepted Shared snapshot.

### Dependency Decision

`ARCH-006-SHARED-004` is now Ready. It owns publication of `@modainteract/moda-interact-shared@0.7.1` and clean-registry-consumer verification. Background/Admin/Shopify consumers remain blocked until SHARED-004 is architect-accepted Complete.
