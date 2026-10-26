---
id: ARCH-050-BACKGROUND-001
architecture_id: ARCH-050
title: Classify and remediate Background test-suite failures
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-26
updated: 2026-10-26
---

# Classify and remediate Background test-suite failures

## Architecture

Architecture ID: `ARCH-050`

Architecture document: `docs/architecture/ARCH-050-background-test-suite-stabilisation.md`

Coordinator: `moda_architect`

## Objective

Establish a reproducible, dependency-correct baseline for the Background unit
and integration suites, classify the observed failures by owner and cause, and
remediate only confirmed Background-owned failures.

## Context

The prior full run initially failed to load `@modainteract/moda-interact-shared`
exports `./identity` and `./whatsapp-template-events`. The locally ignored
installed package was 2.4.3 while Background declares 2.5.1. Replacing the
installed package with the declared 2.5.1 artifact and supplying declared
`libphonenumber-js@1.12.30` made the full integration run pass (5 files, 13
tests). The full unit run still reported 17 failures and 2,996 passes across
291 files.

Known candidates, not established defects:

- An observability-startup test expects Shared version 2.5.0 while Background
  declares 2.5.1.
- An automated-template-input expectation omits null `textHeader` and
  `imageHeader` properties.
- Subprocess timeouts and checkout-recovery failures require same-revision
  reproduction and triage.

Existing baseline `ARCH025-BACKGROUND-TEST-001` is historical evidence only.
Establish the current baseline before modifying assertions or production code;
do not assume every reported failure is new or code-owned.

## Scope

- Reproduce the starting-revision results using the Background repository's
  declared dependency versions and documented install/test commands.
- Record runtime/tool versions, installed versus declared Shared package
  versions and exports, exact failing test/suite identities, and failure reasons.
- Separate dependency-install/export resolution, Shared-owned defects,
  workspace-installation conditions, Background-owned code/test failures,
  established baseline failures, and non-reproducible timeouts.
- Correct only confirmed Background-owned failures after classification.
- Run the complete Background unit and integration suites after correction and
  report the full results, including any failures that remain.

## Out of Scope

- Implementing or releasing changes in `moda-interact-shared`.
- Changing workspace-level package-install configuration or adding local Shared
  shims to make Background tests load.
- Weakening/skipping tests, changing expected values without checking the
  canonical contract, or expanding `ARCH025-BACKGROUND-TEST-001` without
  same-environment evidence and architect approval.
- Unrelated cleanup or fixing failures in another repository.

## Requirements

- Before code/test edits, run the relevant baseline on the exact task starting
  revision and capture the dependency state. Use the package manager and lockfile
  actually declared by the repository; do not infer ownership from the first
  failing command.
- For missing Shared exports, compare Background's declaration and lock state
  with the installed artifact and the published Shared package exports. If only
  the local install is stale, correct the task environment and rerun without
  Background source changes. If the published Shared implementation/release is
  missing or incorrect, stop the affected fix and return the evidence to
  `moda_architect`. Do not add a local export, duplicate contract, or import
  workaround.
- Treat the Shared-version assertion and nullable template-header expectation
  as hypotheses. Verify the version/serialization source of truth before
  changing either the assertion or production behavior.
- Compare each failure identity and reason against `ARCH025-BACKGROUND-TEST-001`
  and the same-revision run. Re-run intermittent subprocess failures in
  isolation and in the full suite; do not silently dismiss or baseline them.
- Modify Background production code or tests only for a demonstrated
  Background-owned defect, preserving intended runtime behavior and meaningful
  assertions.
- If a Shared-owned correction is required, leave this task blocked pending a
  separately architected Shared implementation/publication task and an explicit
  dependency update. Do not continue the dependent Background correction early.
- Keep dependency/package changes limited to a verified Background-owned
  manifest or lockfile defect. A workspace install mismatch is environment
  correction, not grounds for a Background source change.
- Do not update durable baseline documentation directly. Submit classification
  evidence and any proposed baseline delta to `moda_architect` for reconciliation.

## Work Items

- [ ] Capture exact starting revision, runtime/tool versions, declared and
  installed dependency state, and full unit/integration failure identities.
- [ ] Establish a reproducible baseline after resolving local dependency
  installation mismatches without masking package/export defects.
- [ ] Classify each reported failure and identify its owning repository or
  environment boundary before source/test edits.
- [ ] Report any confirmed Shared/workspace-owned issue to `moda_architect` and
  stop affected work until the correct dependency is accepted.
- [ ] Correct confirmed Background-owned defects and add/adjust focused tests
  without weakening behavioral coverage.
- [ ] Run complete Background unit and integration validation on the final
  task revision; update this Completion Report with exact totals and remaining
  failures.

## Interfaces / Contracts

Consumes the published `@modainteract/moda-interact-shared` package and the
Background repository's declared dependency contract. No cross-service contract
change is authorized. Any required Shared contract/export correction must be
owned and published by Shared, then referenced through an architect-managed
dependency update.

## Dependencies

None. Baseline reproduction and ownership classification can begin independently.
If classification finds a required Shared-owned fix, `moda_architect` must create
the appropriate Shared task and publication gate if needed, then update this
task's dependency before affected Background remediation resumes.

## Enables

None.

## Acceptance Criteria

- [ ] Starting-revision unit and integration outcomes are reproducible or
  explicitly classified as intermittent with supporting rerun evidence.
- [ ] Every failure from the reported run is classified as install/export,
  workspace environment, Shared-owned, Background-owned, established baseline,
  or non-reproducible; no failure is assumed to be a code regression solely
  because it appeared in the full run.
- [ ] The `./identity` and `./whatsapp-template-events` resolution is proven to
  be either a stale local installation or a Shared package/release defect; no
  Background workaround duplicates or hides the Shared export.
- [ ] Any Shared-owned work is separately task-tracked and explicitly gated by
  architect-managed dependencies before the corresponding Background fix.
- [ ] Confirmed Background-owned failures are corrected without weakening
  unrelated assertions or changing behavior to match an unverified expectation.
- [ ] Full `npm run test:unit` and `npm run test:integration` pass on the final
  task revision. If an external owner/environment blocker prevents completion,
  the task is returned as blocked with exact evidence rather than reported as
  complete.
- [ ] No new or worsened failure identity is left unexplained; full-suite
  results and any proposed baseline changes are reported to `moda_architect`.

## Validation

- [ ] Baseline `npm run test:unit` on the exact starting revision after dependency
  state is recorded.
- [ ] Baseline `npm run test:integration` on the exact starting revision after
  dependency state is recorded.
- [ ] Final full `npm run test:unit`.
- [ ] Final full `npm run test:integration`.
- [ ] Focused reruns for corrected Background-owned failures and any intermittent
  failures, with exact commands and outcomes recorded.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are
complete, set the task to `review`, finish the Completion Report, return control
to `moda_architect` and STOP. If a Shared/workspace-owned blocker is found, set
the task to `blocked`, record exact evidence and return control to
`moda_architect`; do not begin or simulate the external task.

## Implementation Notes

The Background repository declares `@modainteract/moda-interact-shared` 2.5.1.
The supplied run's integration suite passed after replacing a local installed
2.4.3 package and supplying declared `libphonenumber-js@1.12.30`; verify current
manifests, lockfiles and package contents rather than treating those local
repairs as committed code changes. The task author did not run the remediation or
modify production/test code.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run. Task authoring does not execute remediation or Background tests.

### Deviations

None

### Assumptions

None

### Unresolved Issues

Failure ownership and same-revision baseline remain to be established by the
assigned agent.

### Architectural Concerns

Any actual Shared export defect or workspace-level installation defect must be
returned to `moda_architect` for cross-repository ownership and dependency
coordination.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed; this is the initial task definition.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation and review.

### Follow-up

None