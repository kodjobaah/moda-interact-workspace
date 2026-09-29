---
id: ARCH-021-SYSTEM-TEST-003
architecture_id: ARCH-021
title: Validate simplified Feature capability authoring and runtime composition
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 120
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-DATABASE-003
  - ARCH-021-SHARED-002
  - ARCH-021-COMMERCE-088
  - ARCH-021-COMMERCE-089
  - ARCH-021-COMMERCE-090
  - ARCH-021-COMMERCE-091
  - ARCH-021-BACKGROUND-002
  - ARCH-021-COMMERCE-092
  - ARCH-021-COMMERCE-104
enables: []
created: 2026-09-29
updated: 2026-09-29
---

# Validate simplified Feature capability authoring and runtime composition

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Prove end to end that Commerce Studio configures existing Admin Features through one shared Feature behaviour prompt and local-first single-Tool Capabilities, and that release/Background runtime uses immutable Feature/Tool snapshots without the removed Capability revision/binding model.

## Context

This is terminal validation for the Feature Capability simplification. It intentionally runs only after every implementation/publication dependency is architect-accepted Complete and after the developer has had the opportunity to manually exercise the new authoring flow.

## Scope

Build/extend system-test fixtures and scenarios required to validate the integrated path across the existing deployed/test topology.

## Out of Scope

- Implementing missing application behavior in system-test code.
- Changing billing/subscription policy.
- Creating compatibility shims for defects found during validation.
- Executing before all declared implementation dependencies are Complete.

## Requirements

### R1 — Feature is pre-existing/Admin-owned

Create or use an existing Admin-owned Feature fixture before entering Commerce Studio. Validate that the Commerce flow does not create or mutate Feature identity/billing metadata.

### R2 — Capability authoring is local-first and directly navigable when ready

Exercise:

```text
Feature
 -> Add capability
 -> Capability
 -> Tool
 -> Review
```

Before pressing Capability `Next`, enter valid Capability metadata and prove the Tool phase button becomes directly usable. Enter Tool by direct phase click, select an eligible Tool, and prove Review becomes directly usable before pressing Tool `Next`. Directly enter Review.

Then invalidate an upstream field after Tool/Review have been unlocked and prove those phases remain navigable while final `Create capability` becomes unavailable until the current candidate is valid again.

Prove all phase/Previous/Next navigation remains browser-local and no Capability row exists after entering/editing/selecting/navigating/cancelling before final Create.

Then complete final Create and prove exactly one Capability exists with the selected Feature and Tool.

### R3 — Feature behaviour is shared

Set one Feature Behaviour prompt, create at least two Capabilities under that Feature, and prove the release/runtime representation contains the Feature behaviour once rather than once per Capability.

### R4 — exact Tool revision is release-owned

Create/publish a Tool revision, assign the Tool identity to a Capability, create a release, then publish a newer Tool revision. Prove the existing release/runtime manifest remains pinned to the original Tool revision while a newly created release may pin the newer revision.

### R5 — Feature behaviour is release-snapshotted

Create a release, edit the current Feature Behaviour prompt, and prove the existing release retains the prior snapshot while a later release can contain the new text.

### R6 — no BASE/RECOVERY_POLICY semantics

Prove runtime does not require a `conversation_core` BASE Capability and no selection-binding discriminator appears in the integrated contract.

A zero-selected-Capability manifest/turn must be handled according to the accepted Shared/Background contract rather than failing for absence of a base Capability.

### R7 — one Tool may serve multiple Capabilities

Assign one published Tool identity to two Capabilities and prove runtime grants/exposes one Tool with both Capability keys as provenance rather than duplicate executable Tool entries.

### R8 — removed limits/configuration are absent

Validate that Capability authoring, persisted Capability rows and runtime manifest do not contain author-configurable `maxSearchResults` or `maxRecommendations`.

### R9 — authoring does not depend on billing/subscription state

The Feature configuration and Add Capability flows must load and complete using the existing Feature/Tool records without requiring a shop subscription or billing-plan selection as an authoring prerequisite.

This does not waive runtime Feature entitlement enforcement where separately applicable.

## Work Items

- [ ] Add deterministic Feature + published Tool fixture setup.
- [ ] Validate direct ready-phase entry and monotonic post-unlock navigation without pre-Create persistence.
- [ ] Validate cancel-before-Create produces zero durable Capability rows.
- [ ] Validate final Create produces exactly one direct Feature/Tool Capability.
- [ ] Validate two Capabilities share one Feature Behaviour prompt/runtime entry.
- [ ] Validate release Tool revision pinning across later Tool publication.
- [ ] Validate release Feature behaviour snapshot immutability across later prompt edit.
- [ ] Validate zero-selected-Capability runtime without BASE requirement.
- [ ] Validate one Tool reused by two Capabilities is granted once with both provenance keys.
- [ ] Validate removed binding/revision/limit fields are absent from integrated payloads.
- [ ] Validate Capability authoring does not require subscription/billing-plan setup.

## Interfaces / Contracts

Validates the integrated outputs of all declared dependencies. System-test does not own any of those contracts.

## Dependencies

- ARCH-021-DATABASE-003
- ARCH-021-SHARED-002
- ARCH-021-COMMERCE-088
- ARCH-021-COMMERCE-089
- ARCH-021-COMMERCE-090
- ARCH-021-COMMERCE-091
- ARCH-021-BACKGROUND-002
- ARCH-021-COMMERCE-092
- ARCH-021-COMMERCE-104

## Enables

None

## Acceptance Criteria

- [ ] Existing Feature ownership remains with Admin/billing data.
- [ ] Tool/Review become directly clickable from current readiness before Next, then stay navigable once unlocked while Create remains current-candidate gated.
- [ ] Cancelling before final Create leaves zero new Capability rows.
- [ ] Final Create stores one Feature + one Tool Capability with no revision shell.
- [ ] One Feature Behaviour prompt applies once across sibling Capabilities.
- [ ] Existing releases are unaffected by later Tool publication.
- [ ] Existing releases are unaffected by later Feature Behaviour edits.
- [ ] No BASE/RECOVERY_POLICY/`conversation_core` requirement exists in the integrated runtime.
- [ ] A valid zero-selected-Capability turn is supported.
- [ ] Tool reuse across Capabilities produces one executable grant entry with complete provenance.
- [ ] No author-configurable Capability search/recommendation limits appear.
- [ ] Commerce authoring does not require subscription/billing-plan configuration.

## Validation

- [ ] system-test scenario suite for the new Feature Capability flow
- [ ] integrated database assertions for no-row-before-Create and release snapshots
- [ ] integrated Commerce -> Shared -> Background manifest/grant assertions
- [ ] repository-required system-test lint/typecheck/build checks

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Return all defects to the owning implementation task/repository; do not fix product code in system-test.

## Implementation Notes

The developer may intentionally leave this task Pending/Ready while manually validating the completed implementation. No implementation task may depend on this system-test task.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

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

### Architecture Conformance

Pending

### Follow-up

None
