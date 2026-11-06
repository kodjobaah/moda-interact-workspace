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
status: in_progress
priority: 50
executor: developer
claimed_at: 2026-11-06T02:24:26Z
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
- [ ] Publish accepted provider export and verify exact registry version and exports; release metadata only.

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
- [ ] Publish accepted provider export and verify exact registry version and exports; release metadata only.
- [ ] Exact approved registry export/version visible with release receipt and no implementation source changes.

## Validation
- [ ] Verify prerequisite accepted Complete; release command succeeds; exact approved version/exports visible. Do not rerun unit/integration tests, lint/typecheck/build from accepted prerequisite.
- [ ] Record boundary/gap evidence honestly; never infer SDK coordination from helper-only tests.

## Stop Condition
Submit completed report for authorized review and STOP after scoped criteria/validation. Explicit developer completion required. Do not start enabled tasks; system validation is terminal/manually invoked.


### Task-owned exact file changes and read-only inventory
NEW paths below are to be created RELATIVE TO THIS TASK REPOSITORY. Existing fully qualified paths are verified. Cross-repository evidence is read-only.

| Path | Exact existing/new surface | Required edit |
|---|---|---|
| moda-interact-shared/package.json | version/exports | Publish exact architect-accepted artifacts only; approve next available version in release report, verify registry tarball exports. |

### Task-specific deterministic assertions
- [ ] Registry exact version/tarball exports ./shopify/node; no implementation source changes; prereq accepted.

## Implementation Notes
No execution started. Use launcher isolated/synchronized task worktrees when requested. Use the installed SDK surfaces and official recovery policy identified in revision 2. Node recovery uses workspace bootstrap. No new schema or alternative lock primitive is authorized. Publication is release mechanics only.

## Completion Report

### Status

In Progress — Attempt 1. Release metadata and the exact local archive are prepared. Public publication of `@modainteract/moda-interact-shared@5.2.0` is awaiting explicit user approval after automatic approval review rejected the publication action. No npm release has occurred.

### Files Changed

Release metadata only: `package.json` and `package-lock.json` changed from 5.1.0 to 5.2.0 in implementation commit `64737fa`. No implementation source, tests, dependencies, or export-map changes were made. The accepted SHARED-001 implementation is present through its merge to implementation `main` at `f083916`.

### Work Completed

Verified the public registry's latest version was 5.1.0, selected the next minor 5.2.0, and prepared the package from accepted build output. The existing `./shopify/node` export points to `dist/shopify/node.js` and `dist/shopify/node.d.ts`; both files contain the coordinated provider exports.

The local archive is `modainteract-moda-interact-shared-5.2.0.tgz` in the implementation task worktree. It was created with package lifecycle scripts disabled from the previously validated accepted build output. Its package manifest identifies `@modainteract/moda-interact-shared@5.2.0`, and its tarball contains the Node JavaScript and declaration entrypoints. No source changes were included in this release task.

### Validation Results

- `npm view @modainteract/moda-interact-shared version dist-tags --json` — registry reported version/latest 5.1.0.
- `npm pack --dry-run --ignore-scripts --json` — passed for 5.2.0; 134 files, including `dist/shopify/node.js` and `dist/shopify/node.d.ts`; integrity `sha512-Px1+BwZOIyb/0jDd3euBEGbJZwgNX5B9Hcpbyonr/SqBMXmRhkIwSd1fX0V3/VuSl1PqmZt+pov3Xfk5SPXOHQ==`.
- `npm pack --ignore-scripts --json` — created the archive; inspected its embedded package manifest and confirmed the exact `./shopify/node` export.
- `npm view @modainteract/moda-interact-shared@5.2.0 version --json` — returned E404, confirming that 5.2.0 was not listed at the registry at check time.
- Public publish attempt was rejected by automatic approval review because the authorization did not identify this exact package payload and public destination. The publish command did not run; no npm release receipt exists.
- No unit/integration tests, lint, typecheck, or build were rerun, as the accepted prerequisite task prohibits rerunning them for this release-only task.

### Deviations

No source edits were made. The archive reuses build output produced and validated for the exact accepted SHARED-001 source commit; lifecycle scripts were disabled during packing and are not needed when publishing the verified archive.

### Assumptions

The user authorizes the SHARED-002 implementation workflow. Public registry publication of the exact prepared 5.2.0 archive remains pending explicit approval.

### Git / VCS

Task branch: `task/ARCH-061-SHARED-002`.

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-061-SHARED-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-061-SHARED-002`.
- Both worktrees use the route-resolved task branch; SHARED-002 Attempt 1 developer claim is pushed in parent commit `548b038`; release metadata is pushed in implementation commit `64737fa`.
- Implementation task branch starts from accepted SHARED-001 code now merged to implementation main at `f083916`; SHARED-002 made no change to main.
- No parent submodule gitlink, implementation source, or main branch change was made by this task.

### Unresolved Issues

Explicit approval is required to publish the prepared archive publicly to npm. Automatic review rejected the first publication request for lack of authorization identifying the exact package and destination. Do not rerun publication unless that approval is received.

### Architectural Concerns

This is a release-only task. Its local archive contains the accepted Node-only provider export; the package has not been published and no downstream task is started until registry visibility is verified after authorization.

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
