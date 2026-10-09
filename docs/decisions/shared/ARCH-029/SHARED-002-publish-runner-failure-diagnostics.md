---
id: ARCH-029-SHARED-002
architecture_id: ARCH-029
title: Publish accepted Commerce runner failure diagnostics
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-029-SHARED-001
enables:
  - ARCH-029-BACKGROUND-001
  - ARCH-029-BACKGROUND-002
  - ARCH-029-COMMERCE-001
created: 2026-10-10
updated: 2026-10-10
---

# Publish accepted Commerce runner failure diagnostics

## Architecture

Architecture ID: `ARCH-029`.

Architecture document: `docs/architecture/ARCH-029-commerce-runner-failure-diagnostics.md`.

Coordinator: `moda_architect`.

## Objective

Publish exactly the architect-accepted Shared runner diagnostic implementation so Background and Commerce can consume the same package release.

## Context

Shared is consumed from `@modainteract/moda-interact-shared`; source changes in a local snapshot do not upgrade consumer installations. Shared diagnostic capability must be accepted before publication; this task is a release gate only.

## Scope

Shared release-specific version/package/lock metadata and approved publication command, according to current repository policy. Record exact published version and registry verification.

## Out of Scope

Any runtime/source implementation change, refactor, tests, lint, typecheck, build revalidation, consumer upgrade or repair of SHARED-001.

## Requirements

- All SHARED-001 changes are architect-accepted and on the approved publication source revision.
- Choose the correct forward version, publish to intended registry, and verify the exact version and `commerce/runner`/`commerce/model/node` entrypoints.
- Do not publish an unreviewed working tree or change runtime semantics here.
- Publication `prepack` lifecycle behaviour is permitted; do not independently rerun implementation validation merely as release validation.

## Work Items

- [ ] Verify SHARED-001 is Complete/accepted.
- [ ] Apply approved release metadata only.
- [ ] Publish accepted release and verify exact registry entrypoints.
- [ ] Record release version/commit and any issues in Completion Report.

## Interfaces / Contracts

Published package: `@modainteract/moda-interact-shared` with compatible `commerce/runner`, `commerce/model/node` and `logging` exports. Consumer tasks use the exact published version reported here, never an invented version.

## Dependencies

- `ARCH-029-SHARED-001`.

## Enables

- `ARCH-029-BACKGROUND-001`.
- `ARCH-029-BACKGROUND-002`.
- `ARCH-029-COMMERCE-001`.

## Acceptance Criteria

- [ ] Exact approved release is available from intended registry.
- [ ] No unauthorised implementation source changes.
- [ ] Published runner/model entrypoints and release identifier verified.

## Validation

- [ ] Approved publication succeeds.
- [ ] Verify published exact version/release/exports and expected commit.
- [ ] Verify source diff consists only of release-specific metadata.

## Stop Condition

Set `status: review`, submit release evidence to `moda_architect` and STOP. Do not start consumer integration.

## Implementation Notes

Do not rerun the accepted test suite/typecheck/build as an independent publication task. If the package's normal publish lifecycle invokes a build, report it as part of publication, not a separate implementation review.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending publication evidence.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
