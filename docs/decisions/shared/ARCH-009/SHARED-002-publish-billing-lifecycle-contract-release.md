---
id: ARCH-009-SHARED-002
architecture_id: ARCH-009
title: Publish the accepted ARCH-009 billing lifecycle contract release
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-009-SHARED-001
enables:
  - ARCH-009-SHOPIFY-001
  - ARCH-009-BACKGROUND-001
  - ARCH-009-BACKGROUND-002
  - ARCH-009-ADMIN-001
created: 2026-09-10
updated: 2026-09-10
---

# ARCH-009-SHARED-002: Publish the accepted ARCH-009 billing lifecycle contract release

## Architecture

Canonical: `docs/architecture/ARCH-009-merchant-billing-lifecycle-cancellations-refunds.md`

## Objective

Publish the architect-accepted `ARCH-009-SHARED-001` package so consumer
repositories can install one exact Shared release containing the billing
lifecycle, cancellation mapping, and purchased-credit availability contracts.

## Context

This is a publication gate only. `ARCH-009-SHARED-001` owns implementation and
implementation validation. Consumer repositories must not add local substitutes
while this release is pending.

The accepted package target is `@modainteract/moda-interact-shared@0.9.0`.

## Scope

Only release metadata, package publication, registry verification, and isolated
exact-version consumer verification are in scope:

- bump package publication metadata from the accepted baseline `0.8.0` to
  `0.9.0`, including the package-lock root metadata when present;
- preserve the accepted `ARCH-009-SHARED-001` runtime source and exports map;
- publish `@modainteract/moda-interact-shared@0.9.0` using the repository's
  established npm publication convention;
- verify the exact version and integrity metadata from the registry;
- install the exact published package in a temporary clean consumer and verify
  the lifecycle exports, cancellation mode mapping, and availability helper;
- record the exact published version, tarball/integrity evidence, and clean
  consumer result in this task's Completion Report and Architect Review section.

## Dependencies

Do not begin publication until `ARCH-009-SHARED-001` is architect-accepted
`complete`. The dependency gate is authoritative; do not change it to `ready`
merely because publication was requested.

## Out of Scope

- changing `ARCH-009-SHARED-001` implementation or tests;
- changing the package exports map;
- changing consumer repositories or dependency pointers;
- implementing Shopify, Background, Admin, database, or system-test behavior;
- rerunning the full implementation suite when publication validation does not
  require it;
- publishing any version other than the accepted `0.9.0` target.

## Work Items

- [ ] Confirm `ARCH-009-SHARED-001` is architect-accepted `complete`.
- [ ] Bump only required package and lockfile publication metadata to `0.9.0`.
- [ ] Verify package contents preserve the accepted public exports.
- [ ] Publish `@modainteract/moda-interact-shared@0.9.0`.
- [ ] Verify registry version, tarball, shasum/integrity, and exact-version
      clean-consumer imports/runtime behavior.
- [ ] Record the new published version and evidence in Completion Report and
      Architect Review.
- [ ] Return this task to `review` and stop.

## Acceptance Criteria

- [ ] The dependency is architect-accepted `complete` before publication.
- [ ] Local package and package-lock root metadata identify version `0.9.0`.
- [ ] The published package is exactly `@modainteract/moda-interact-shared@0.9.0`.
- [ ] Published exports include the accepted ARCH-009 lifecycle contracts.
- [ ] A clean consumer installs the exact registry version and successfully
      imports and exercises the cancellation mapping and availability helper.
- [ ] No consumer repository or runtime source outside release metadata changes.
- [ ] The exact published version and registry integrity evidence are recorded
      in the review record.

## Validation

Publication-only validation is required:

```bash
npm pack --dry-run --json
npm publish --access public
npm view @modainteract/moda-interact-shared@0.9.0 version dist.tarball dist.shasum dist.integrity --json
git diff --check
```

Use a temporary clean consumer for the exact-version install/import smoke test.
Do not rerun the complete SHARED-001 implementation suite unless the package
publication mechanism requires it. If npm publication is unavailable, do not
pretend the release exists; record the exact authentication or registry blocker
and return the task to review.

## VCS and Stop Rules

Follow `docs/agent-vcs-ownership-policy.md`. Commit and push only this task's
release metadata and task-owned evidence on the implementation and mirrored
parent task branches. Do not merge or push `main`, force-push, modify consumers,
or start an enabled task. Return only this task to `review` and stop.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Published Release

Version: Not published

Tarball: Not available

Shasum/integrity: Not available

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

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

### Published Version Recorded In Review

Not yet recorded

### Architecture Conformance

Pending

### Follow-up

None