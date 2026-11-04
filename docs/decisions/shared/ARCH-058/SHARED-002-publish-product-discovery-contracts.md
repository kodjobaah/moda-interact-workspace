---
id: ARCH-058-SHARED-002
architecture_id: ARCH-058
title: Publish the accepted product-discovery contract version
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-11-04T06:56:54Z
attempt: 1
depends_on:
  - ARCH-058-SHARED-001
enables:
  - ARCH-058-MCP-001
  - ARCH-058-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-058-SHARED-002: Publish the accepted product-discovery contract version

## Architecture

`docs/architecture/ARCH-058-commerce-agent-product-discovery.md`; `docs/architecture/ARCH-058/contracts.md`, section 1. Coordinator: `moda_architect`.

**Defined but not materialised.** Materialise using `/moda-task ARCH-058-SHARED-002` only after its dependency is accepted. No branch, worktree, publication or execution claim exists in this definition.

## Objective

Publish the exact architect-accepted Shared product-discovery, shipping-information and answer-presentation contracts so MCP, Commerce and Background can install a verified immutable package. This is a release-only gate, separate from schema implementation and Commerce tool publication.

## Context

The snapshot package is3.1.0. SHARED-001 changes public inferred grant/output types and therefore requires a major version under the repository README release policy. Approved target is **4.0.0**, provided actual accepted source and registry baseline remain3.1.0 and4.0.0 is unoccupied. Runtime runner 1.1.0 is already part of accepted SHARED-001 code. If those assumptions no longer hold, reconcile with the architect before publication; do not invent or overwrite a version.

## Scope

- Confirm SHARED-001 is complete, architect-accepted, and its exact accepted commit is present in the isolated release worktree.
- Modify only required existing release metadata, normally `package.json` and `package-lock.json`, to 4.0.0 using the established release process.
- Publish the approved package using existing registry/authentication configuration and inspect the exact registry tarball and exported JavaScript/declarations.
- Record source commit, release metadata commit, exact registry version/integrity and verification result in this task report. Consumers pin that recorded version.

## Out of Scope

No schema/runner implementation, rerunning the implementation test suite, consumer upgrades, Database migration, provider calls, embedding, Commerce Studio publication, environment rollout, Admin changes, historical backfill or index edits. Do not duplicate SHARED-001's validation report.

## Requirements

This gate must not publish unreviewed source. The accepted commit and clean intended artifact are prerequisites, not a mutable local branch name. Inspect the existing release process; do not bypass registry access controls or print credentials. The publication command's required packaging/prepack build is allowed and must be recorded, but do not reopen implementation testing without evidence of a changed artifact.

Verify the new public schemas/types/constants/helper named in SHARED-001, including CommerceShippingInformationInputSchema, CommerceShippingInformationSchema, CommerceResponseDispositionSchema and CommerceAnswerPresentationSelectionSchema, the updated dictionary/grant types, and runnerVersion1.1.0 through the existing commerce/runner exports. A successful publish command alone is not proof that consumers can retrieve the intended artifact.

## Work Items

- [ ] Verify prerequisite complete/accepted status and exact source commit.
- [ ] Verify actual registry baseline and approved target availability; stop for reconciliation on conflict.
- [ ] Apply only approved release metadata and inspect the package artifact.
- [ ] Publish under the existing release workflow.
- [ ] Retrieve the exact registry package and verify version, integrity and required exports.
- [ ] Record the receipt and stop without upgrading consumers.

## Interfaces / Contracts

`@modainteract/moda-interact-shared@4.0.0` through existing `/commerce` and `/commerce/runner` entrypoints, subject to recorded architect reconciliation if the observed baseline changed. No new subpath. Subsequent ARCH-058 tasks must install this exact accepted version and committed lockfile; they must not use a sibling source path, unpublished tarball or assumed compatible range.

## Dependencies

- ARCH-058-SHARED-001

## Enables

- ARCH-058-MCP-001
- ARCH-058-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] SHARED-001 is complete and architect-accepted, with the published source commit recorded.
- [ ] Approved exact version is available from the intended registry with its integrity and required exports verified.
- [ ] Only permitted release metadata and this report changed.
- [ ] No consumer, runtime deployment or Commerce publication was performed.

## Validation

Use the workspace Node bootstrap prerequisite before Node/npm commands. Follow the existing release procedure and record the actual commands, normally:

```bash
npm view @modainteract/moda-interact-shared versions --json
npm version 4.0.0 --no-git-tag-version
npm pack --dry-run
npm publish --access public
npm pack @modainteract/moda-interact-shared@4.0.0 --prefer-online
```

These are execution instructions for the future authorized publication task, not commands run while defining it. Inspect downloaded package metadata, public declarations, descriptor hashes and runner version using a temporary artifact directory. Verify the registry package corresponds to the accepted source plus release metadata; record full integrity from registry metadata without secrets. `git diff --check` must pass. Treat transient registry propagation explicitly and do not report success until the exact version can be retrieved.

## Stop Condition

Set status to review, provide the immutable publication receipt and actual worktree/commit/push evidence, return to the architect and stop. Do not start MCP or update any consumer automatically in this task.

## Implementation Notes

Keep package publication distinct from COMMERCE-001's environment tool publication. One makes schemas available to source consumers; the other creates/pins four authorized tools and their behavior in an environment.

## Completion Report

### Status

Not started. Defined but not materialised; publication is blocked on SHARED-001 acceptance.

### Files Changed

None implemented.

### Work Completed

None.

### Validation Results

Not run; no registry lookup, version bump or publication has occurred in the task-definition session.

### Deviations

None recorded.

### Assumptions

Approved conditional target 4.0.0; observed snapshot baseline 3.1.0.

### Unresolved Issues

Actual registry baseline and accepted source are checked at execution, not assumed from the archive.

### Physical Worktree and Synchronization Evidence

Not materialised. Record real paths, branches, synchronized heads, accepted source/release commits and task-branch pushes only when they exist.

## Architect Review

### Review Status

Not reviewed; task definition only.

### Review Notes

Await publication evidence after SHARED-001 acceptance.


## Architect Dependency Handoff (2026-11-04)

SHARED-001 Attempt 2 is accepted and complete at implementation `0b5567c3e01748de1d5d8c7d3be0d84a55dfb139`. Its expanded browse, shipping and answer-presentation contract and original built-in/grant changes passed independent review. This publication task is ready, unclaimed and unexecuted. Use that accepted source and retain the existing registry/version/source checks before publishing 4.0.0; source acceptance alone is not registry publication. Do not advance consumer prerequisites until this task completes.
