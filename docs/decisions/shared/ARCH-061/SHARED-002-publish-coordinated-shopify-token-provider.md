---
id: ARCH-061-SHARED-002
architecture_id: ARCH-061
title: publish coordinated shopify token provider
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-061-SHARED-001"]
enables: ["ARCH-061-SHOPIFY-001", "ARCH-061-BACKGROUND-001", "ARCH-061-COMMERCE-001", "ARCH-061-MCP-001", "ARCH-061-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-06
---
# Publish coordinated shopify token provider

## Architecture
ARCH-061; docs/architecture/ARCH-061-shopify-offline-token-refresh-coordination.md. Coordinator moda_architect.

## Objective
Publish coordinated shopify token provider using the published injected-client Shared runtime.

## Context
Background bespoke refresh currently reads/refreshes/writes unlocked; App SDK refreshes before storage write. Consumers use the same persisted rotating offline credential.

## Scope
Task-owned moda-interact-shared changes and focused validation only. Cross-repository paths below are read-only baseline evidence unless owned by this task.

| Existing file | Symbol/surface | Required change |
|---|---|---|
| moda-interact-shared/package.json | version/exports | Publish accepted code with next approved available version; record receipt. |


## Out of Scope
Central token service, agent tools, sibling imports, credential UI, schema changes, node_modules patches, automatic execution, claims or main merges.

## Requirements
The entire parent architecture runtime/bounds/SDK/lifecycle/ambiguity matrix is normative. Factory accepts each service's local Prisma client at composition. Lock before read/decision/remote refresh; write-only locking is insufficient. No exactly-once remote guarantee across crash. Use the binding revision public-wrapper/ALS/lifecycle gate architecture; do not choose a different synchronization mechanism.

## Work Items
- [x] Publish accepted provider export and verify exact registry version and exports; release metadata only.

## Interfaces / Contracts
Shared Node-only factory and structural transaction interface/error categories defined by SHARED-001 and published by SHARED-002. Consumers inject local client/config/fetch and translate errors. No sibling source imports; no browser exports or raw token DTOs. App owns all SDK/lifecycle mutation entrypoints.

## Dependencies
- ARCH-061-SHARED-001

## Enables
- ARCH-061-SHOPIFY-001
- ARCH-061-BACKGROUND-001
- ARCH-061-COMMERCE-001
- ARCH-061-MCP-001
- ARCH-061-SYSTEM-TEST-001

## Acceptance Criteria
- [x] Publish accepted provider export and verify exact registry version and exports; release metadata only.
- [x] Exact approved registry export/version visible with release receipt and no implementation source changes.

## Validation
- [x] Verify prerequisite accepted Complete; release command succeeds; exact approved version/exports visible. Do not rerun unit/integration tests, lint/typecheck/build from accepted prerequisite.
- [x] Record boundary/gap evidence honestly; never infer SDK coordination from helper-only tests.

## Stop Condition
Submit completed report for authorized review and STOP after scoped criteria/validation. Explicit developer completion required. Do not start enabled tasks; system validation is terminal/manually invoked.


### Task-owned exact file changes and read-only inventory
NEW paths below are to be created RELATIVE TO THIS TASK REPOSITORY. Existing fully qualified paths are verified. Cross-repository evidence is read-only.

| Path | Exact existing/new surface | Required edit |
|---|---|---|
| moda-interact-shared/package.json | version/exports | Publish exact architect-accepted artifacts only; approve next available version in release report, verify registry tarball exports. |

### Task-specific deterministic assertions
- [x] Registry exact version/tarball exports ./shopify/node; no implementation source changes; prereq accepted.

## Implementation Notes
Release mechanics only. Package metadata is 5.2.0; published artifact contains the accepted SHARED-001 runtime. No implementation source changes or tests were made in this task.

## Completion Report

### Status

Submitted for architect review — Attempt 1. The approved public release and registry verification are complete. This developer-owned task remains in Review pending a durable passing review and explicit developer completion.

### Files Changed

Release metadata only: `package.json` and `package-lock.json` changed from 5.1.0 to 5.2.0. No implementation source, tests, dependencies, or export-map changes were made. The accepted SHARED-001 implementation is present through merged implementation-main commit `f083916`.

### Work Completed

Published `@modainteract/moda-interact-shared@5.2.0` from the inspected archive, built from the previously validated accepted SHARED-001 output. The Node-only `./shopify/node` export resolves to `./dist/shopify/node.js` and `./dist/shopify/node.d.ts`, both present in the published package.

The release is metadata-only relative to the accepted implementation. No task-owned source changes were introduced.

### Validation Results

- `npm view @modainteract/moda-interact-shared version dist-tags --json` before publication — latest was 5.1.0.
- `npm pack --dry-run --ignore-scripts --json` — passed for 5.2.0; 134 files, including `dist/shopify/node.js` and `dist/shopify/node.d.ts`; integrity `sha512-Px1+BwZOIyb/0jDd3euBEGbJZwgNX5B9Hcpbyonr/SqBMXmRhkIwSd1fX0V3/VuSl1PqmZt+pov3Xfk5SPXOHQ==`.
- Inspected the actual local archive manifest: name/version `@modainteract/moda-interact-shared@5.2.0`; `./shopify/node` maps to the expected JavaScript and declaration files.
- `npm publish ./modainteract-moda-interact-shared-5.2.0.tgz --access public --ignore-scripts` — succeeded; npm reported `+ @modainteract/moda-interact-shared@5.2.0`.
- Fresh `npm view @modainteract/moda-interact-shared@5.2.0 version dist.tarball dist.integrity exports --json` — returned version 5.2.0, public registry tarball URL, matching SHA-512 integrity, and the exact `./shopify/node` export map.
- Fresh `npm view @modainteract/moda-interact-shared version dist-tags --json` — latest is 5.2.0.
- No unit/integration tests, lint, typecheck, or build were rerun, as the accepted prerequisite task prohibits rerunning them for this release-only task.
- `git diff --check` — passed.

### Deviations

No source edits were made. The archive reused output built and validated for the exact accepted SHARED-001 source commit. Package lifecycle scripts were disabled during packing and publishing; no build or test scripts were run.

### Assistance

No agent assistance was used.

### Git / VCS

Task branch: `task/ARCH-061-SHARED-002`.

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-061-SHARED-002` / `task/ARCH-061-SHARED-002`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-061-SHARED-002` / `task/ARCH-061-SHARED-002`.
- Implementation commit `64737fa90cea1a64471277fc77fdd84704b7cf45` is pushed to `origin/task/ARCH-061-SHARED-002`; it contains only package version/lockfile changes.
- Parent task claim commit `548b038` is pushed to `origin/task/ARCH-061-SHARED-002`. The launcher initially stopped after writing the local claim because the task's Completion Report heading lacked the required blank line. The report was repaired and the unchanged Attempt 1 claim committed/pushed; no extra attempt was created.
- The implementation worktree was synchronized to accepted implementation `main` commit `f083916`. The accepted SHARED-001 feature had already been merged to implementation `main`; this task made no change to `main`.
- Recursive implementation submodules: none. No parent submodule gitlink was changed.

### Unresolved Issues

None for the publication acceptance criteria. Downstream ARCH-061 tasks remain pending because this task is in Review rather than Complete, and other dependencies remain incomplete or manually gated.

### Architectural Concerns

This task publishes the accepted Shared Node-only provider contract only. It does not certify consumer SDK coordination or production rollout behavior.

## Architect Review
### Review Status
Pending
### Review Notes
Definition only.
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending implementation.
### Follow-up
None

### Architecture definition review — 2026-11-05 revision 2
Definition reviewed against installed SDK control flow and current repository reads/writes. Public authenticate/unauthenticated wrapper + ALS storage and runtime setAbstractFetchFunc are the selected integration; no fictional SDK hook. Session row plus stable per-shop lifecycle advisory gate is selected for demonstrated deletion/recreation. Provider lost-response recovery is grounded in official Shopify August 28, 2026 policy. No implementation reviewed and no lifecycle status changed.

Publication exports the selected-Shop-ID API defined by revised SHARED-001. Do not publish the superseded host-argument API.
