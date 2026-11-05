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
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-061-SHARED-001"]
enables: ["ARCH-061-SHOPIFY-001", "ARCH-061-BACKGROUND-001", "ARCH-061-COMMERCE-001", "ARCH-061-MCP-001", "ARCH-061-SYSTEM-TEST-001"]
created: 2026-11-05
updated: 2026-11-05
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
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Definition only.
### Deviations
None
### Assumptions
Same canonical PostgreSQL database; exact identity, lifecycle lock, SDK wrappers and provider recovery are fixed by binding revision 2.
### Unresolved Issues
None blocking architecture definition. Revision-1 feasibility questions are superseded by binding revision 2 decisions.
### Architectural Concerns
Implement binding revision 2 exactly; report actual incompatibility with evidence instead of selecting alternate architecture.

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
