---
id: ARCH-021-SHARED-002
architecture_id: ARCH-021
title: Publish simplified Feature capability contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 89
executor: copilot
claimed_at: 2026-09-29T14:01:46Z
attempt: 1
depends_on:
  - ARCH-021-SHARED-001
enables:
  - ARCH-021-COMMERCE-089
  - ARCH-021-BACKGROUND-002
created: 2026-09-29
updated: 2026-09-29
---

# Publish simplified Feature capability contracts

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Publish the architect-accepted ARCH-021-SHARED-001 Commerce contract implementation as the next consumable `@modainteract/moda-interact-shared` package version.

## Context

Commerce and Background are pinned to published Shared package versions. Consumer tasks must use one canonical published contract rather than copying the new Feature/Capability/Tool types locally.

This is a release gate only. SHARED-001 already owns implementation validation.

## Scope

- Apply the approved package/release version required by the repository publication process.
- Publish the exact architect-accepted SHARED-001 implementation.
- Verify the expected package version is visible at the intended registry.
- Record the exact published version in the Completion Report.

## Out of Scope

- Source refactoring or contract changes.
- Unit/integration test reruns.
- Typecheck/build reruns solely to revalidate SHARED-001.
- Commerce or Background dependency updates.
- Consumer integration.

## Requirements

### R1 — publish only accepted SHARED-001 source

SHARED-001 must be Complete and architect-accepted before publication begins.

### R2 — no implementation changes

Only release-specific metadata required by the approved publication process may change. If source changes are required, stop and return to `moda_architect`.

### R3 — record exact publication identity

Record the exact package version and registry evidence consumed by later tasks.

## Work Items

- [x] Verify ARCH-021-SHARED-001 is Complete/Accepted.
- [x] Apply the approved next package version/release metadata.
- [x] Run the approved publication command.
- [ ] Verify the exact published package version is available.
- [x] Record publication evidence and confirm no unauthorised source changes.

## Interfaces / Contracts

Publishes:

`@modainteract/moda-interact-shared`

containing the accepted simplified Feature capability contracts from ARCH-021-SHARED-001.

## Dependencies

- ARCH-021-SHARED-001

## Enables

- ARCH-021-COMMERCE-089
- ARCH-021-BACKGROUND-002

## Acceptance Criteria

- [x] SHARED-001 was Complete/Accepted before publication.
- [x] The intended package version was published successfully.
- [ ] The exact version is visible at the target registry.
- [x] No implementation source changed beyond authorised release metadata.
- [x] The published version is recorded for consumers.

## Validation

- [x] prerequisite SHARED-001 acceptance confirmed
- [x] approved version/release identifier applied
- [x] publication command succeeded
- [ ] exact expected package version visible at target registry
- [x] no unauthorised implementation source changes

## Stop Condition

After publication validation is complete, set the task to `review`, complete the Completion Report and STOP. Do not update Commerce or Background.

## Implementation Notes

Do not rerun SHARED-001 implementation validation in this publication task.

## Completion Report

### Status

In Progress; npm accepted publication of version 1.0.0, but registry visibility is still pending.

### Files Changed

- `moda-interact-shared/package.json` and `package-lock.json`: release metadata only; implementation commit `abd1c65` is pushed to `task/ARCH-021-SHARED-002`.
- This task file: publication progress/evidence.

### Work Completed

- Confirmed `ARCH-021-SHARED-001` is Complete and Architect Review is Accepted. The accepted source commits are present in the prepared Shared task branch.
- Followed the Shared README SemVer policy for this breaking public API change and set package/lockfile version to `1.0.0`.
- `npm publish --access public --registry=https://registry.npmjs.org/` completed successfully. npm reported the tarball as `modainteract-moda-interact-shared-1.0.0.tgz`, 150.9 kB, SHA-1 `47a0ff85f6eed1b2c44f31407f291f5fbcf3f4f6`.
- No implementation source files changed.

### Validation Results

- Package and lockfile version consistency assertion passed; `git diff --check` passed; initial diff scope was only `package.json` and `package-lock.json`.
- The publish `prepack` build completed successfully and npm accepted the public publish.
- Public registry exact-version lookup returned HTTP 404 at 2026-09-29 14:05 UTC while npm reported the package was still being processed. Registry visibility and `latest` confirmation remain pending; do not consume until verified.

### Deviations

- The first publish attempt stopped before publication because `tsup` was absent. `npm ci --no-audit --no-fund` installed the exact lockfile dependencies; the subsequent publish and prepack build succeeded.

### Assumptions

- The package README's release policy defines breaking public API compatibility changes as major releases; the next unused major version was `1.0.0`.

### Unresolved Issues

- Confirm the exact `1.0.0` version, tarball integrity, and `latest` dist-tag at the public npm registry after publication processing completes.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
