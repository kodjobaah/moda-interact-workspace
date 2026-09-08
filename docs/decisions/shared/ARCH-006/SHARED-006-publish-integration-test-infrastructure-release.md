---
id: ARCH-006-SHARED-006
architecture_id: ARCH-006
title: Publish reusable integration-test infrastructure release
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 75
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-006-SHARED-005
enables:
  - ARCH-006-BACKGROUND-008
created: 2026-09-06
updated: 2026-09-06T17:06:00Z
---
# ARCH-006-SHARED-006: Publish reusable integration-test infrastructure release

## Architecture

Canonical: `docs/architecture/ARCH-006-merchant-communications-support-inbox.md`

## Objective

Publish the architect-accepted SHARED-005 Node-only testing subpath as the next exact Shared release and prove it can be installed/imported from a clean consumer before application repositories adopt it.

## Context

Application repositories consume `@modainteract/moda-interact-shared` from the registry. Publication is therefore a separate bounded task from implementation.

## Scope

Version/package metadata, registry publication and clean-consumer verification only.

## Out of Scope

- changing SHARED-005 implementation;
- changing application repositories;
- running application integration suites;
- system-test execution.

## Requirements

- Publish the next architect-approved exact version after `0.7.1` (expected `0.7.2` unless the registry/version history requires another version).
- Verify the exact registry artifact from a clean isolated consumer.
- Import the Node-only testing subpath successfully.
- Execute at least one non-Docker deterministic helper/property from that import so verification proves runtime resolution, not only package metadata.
- Record registry version, tarball/integrity evidence and clean-consumer result.

## Work Items

- [x] Update version metadata only as required for publication.
- [x] Build/package and inspect the testing subpath export.
- [x] Publish the exact release.
- [x] Install exact published version into a clean temporary consumer.
- [x] Import/execute the testing Node subpath.
- [x] Return to review and STOP.

## Interfaces / Contracts

Published import:

```text
@modainteract/moda-interact-shared/testing/node
```

## Dependencies

Explicit dependencies are listed in YAML frontmatter.

## Enables

`ARCH-006-BACKGROUND-008`

## Acceptance Criteria

- [x] Registry latest/exact version identifies the intended release.
- [x] Clean consumer installs the exact release without workspace source fallback.
- [x] `testing/node` resolves at runtime from that clean consumer.
- [x] Published tarball contains the expected testing entrypoint files.
- [x] No SHARED-005 implementation changes are smuggled into the publication task.

## Validation

Publication-only validation per architect workflow: package build/pack metadata, registry evidence, clean-consumer import/execution and `git diff --check`.

## Implementation Notes

Publication task hard stop: do not adopt the helper into Background/Admin/Shopify in this invocation.

## Completion Report

### Status

Ready for Review.

### Files Changed

 - [moda-interact-shared/package.json](../../../../moda-interact-shared/package.json)
 - [moda-interact-shared/package-lock.json](../../../../moda-interact-shared/package-lock.json)

### Work Completed

Published `@modainteract/moda-interact-shared@0.7.2` with the existing architect-accepted `testing/node` implementation. The published package exposes the Node-only testing subpath and its tarball contains `dist/testing/node.js` and `dist/testing/node.d.ts`.

### Validation Results

 - `npm run typecheck`: passed.
 - `npm test`: 98 passed, 1 Redis-dependent test skipped because `TEST_REDIS_URL` is not configured.
 - `npm run build`: passed.
 - `npm run validate:testing-node`: passed, including packed-artifact validation.
 - `npm pack --dry-run --json --ignore-scripts`: passed for `0.7.2`; shasum `cf85f11f98f7aae92884281e9f0fdc52f23c4d61`.
 - `npm publish --access public`: published `0.7.2` successfully.
 - Registry evidence: tarball `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-0.7.2.tgz`; integrity `sha512-RRK1UJCfyFPS+bSBHP4QcraRI9OkmaUsSOUsK7v4b0Bed1jwb9GRYJw2vJgJompctcDGWMyWeBJg/9kaH+oJhQ==`.
 - Clean consumer installed exact `0.7.2`, imported `@modainteract/moda-interact-shared/testing/node`, and executed the command-runner helper successfully.
 - `git diff --check`: passed.

### Deviations

The required live Docker validation was not rerun because SHARED-006 is publication-only; SHARED-005 recorded the accepted live infrastructure validation.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted — Complete

### Decision

`moda_architect` independently reviewed ARCH-006-SHARED-006 Attempt 1 and accepts the publication.

Accepted evidence:

- `@modainteract/moda-interact-shared@0.7.2` was published successfully and the npm publication evidence reports shasum `cf85f11f98f7aae92884281e9f0fdc52f23c4d61`;
- the task-recorded registry integrity is `sha512-RRK1UJCfyFPS+bSBHP4QcraRI9OkmaUsSOUsK7v4b0Bed1jwb9GRYJw2vJgJompctcDGWMyWeBJg/9kaH+oJhQ==`;
- comparison with the architect-accepted SHARED-005 snapshot shows publication changed only `package.json` and `package-lock.json`, both from `0.7.1` to `0.7.2`; no SHARED-005 source/runtime implementation was changed;
- the published package retains the Node-only `./testing/node` export and packed-artifact validation passed;
- a clean isolated consumer installed exact `0.7.2`, imported `@modainteract/moda-interact-shared/testing/node`, and executed a helper successfully, proving registry/runtime resolution rather than workspace fallback;
- typecheck, build, export validation, 98 tests with the documented existing Redis-dependent skip, registry integrity verification and `git diff --check` passed;
- SHARED-006 remained publication-only and did not adopt the helper into application repositories.

`ARCH-006-BACKGROUND-008` is now Ready because both of its dependencies (`BACKGROUND-004` and `SHARED-006`) are architect-accepted Complete. This quality-infrastructure adoption remains non-gating for the translation product chain.
