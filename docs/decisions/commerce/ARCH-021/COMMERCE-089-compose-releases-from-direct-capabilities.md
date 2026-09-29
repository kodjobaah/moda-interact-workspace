---
id: ARCH-021-COMMERCE-089
architecture_id: ARCH-021
title: Compose releases and runtime manifests from direct Capabilities
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 92
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-DATABASE-003
  - ARCH-021-SHARED-002
  - ARCH-021-COMMERCE-088
enables:
  - ARCH-021-BACKGROUND-002
  - ARCH-021-COMMERCE-092
created: 2026-09-29
updated: 2026-09-29
---

# Compose releases and runtime manifests from direct Capabilities

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace Capability-revision release composition and runtime resolution with direct Capability membership, release-time Tool revision pinning and one immutable Feature behaviour snapshot per represented Feature.

## Context

Current release/runtime code walks `CommerceCapabilityRevision`, parses `toolBindings[]`, reads Capability configuration limits, handles `BASE`/`RECOVERY_POLICY` special cases and generates per-Capability prompt identities.

DATABASE-003 and SHARED-001/002 establish a smaller model. Release creation is now the versioning boundary: authors choose a Tool identity when creating the Capability, while a release freezes the exact published Tool revision and the Feature's current behaviour text.

This task is the Commerce producer/runtime cutover. It must not preserve the old revision model behind adapters.

## Scope

Primary areas include:

```text
package.json / lockfile                         # consume published SHARED-002 version
database/                                       # accepted DATABASE-003 gitlink
src/commerce/publication/* release creation/read models
src/commerce/integration/backend.ts
src/commerce/integration/backend/publication-storage.ts where still relevant
src/commerce/integration/studio/services.ts release methods/read models
src/studio release contracts/actions required to compile current release UI
focused lifecycle/backend/MCP/Studio tests
C20/integration fixture code that constructs releases/manifests
```

## Out of Scope

- New Feature/Capability creation UI.
- Background consumer changes.
- Billing/subscription entitlement policy redesign.
- Agent Configuration model/prompt runtime cutover beyond this Feature behaviour composition.
- Final removal of every obsolete UI/compatibility file; COMMERCE-092 is the deletion gate.

## Requirements

### R1 — consume canonical new contracts

Update to the exact `@modainteract/moda-interact-shared` version published by SHARED-002 and the accepted DATABASE-003 database submodule.

Do not copy Shared manifest schemas/types locally.

### R2 — release input names Capability identities, not Capability revisions

Release creation accepts ordered Capability IDs/positions. It must not accept or expose `capabilityRevisionId`.

Before writing the release, resolve every selected Capability's current immutable `toolId` and choose the highest `revisionNumber` PUBLISHED revision for that Tool using deterministic ordering.

If any selected Capability has no currently published Tool revision, release creation fails before durable release rows are written.

### R3 — snapshot Feature behaviour once per Feature

For every distinct Feature represented by the ordered release Capabilities, snapshot the current `behaviourPrompt` into exactly one release Feature row. An absent current Feature configuration resolves to the documented blank behaviour prompt.

Later edits to the current Feature behaviour must not change existing releases.

### R4 — runtime manifest derives from immutable release rows

Generate the Shared manifest directly from:

```text
CommerceRelease
CommerceReleaseFeature snapshots
CommerceReleaseCapability members
CommerceCapability stable identity/Feature
pinned CommerceToolRevision
```

Do not query `CommerceCapabilityRevision`, parse `toolBindings[]`, synthesize Capability prompt names or read Capability configuration.

### R5 — no BASE/RECOVERY_POLICY runtime branches

Remove producer-side branches based on `selectionBinding`, `conversation_core` or `RECOVERY_POLICY`.

All release Capabilities are ordinary Feature capabilities. Runtime eligibility may still filter them using Feature facts, but the authoring/release model has no Capability type discriminator.

A valid manifest may contain zero selected capabilities after Feature eligibility filtering.

### R6 — preserve Feature eligibility as a separate runtime concern

Existing plan/subscription/preference/recovery state must not leak back into Capability authoring, but runtime Feature eligibility may continue to determine which release Capabilities are active for a shop.

Express eligibility only through the Capability's required `featureId`; do not recreate a Capability binding enum.

This task must not redesign billing policy.

### R7 — remove capability-owned result limits from runtime composition

Delete calculation/propagation of Capability `maxSearchResults` / `maxRecommendations`.

Where generic execution/result processing still requires safety bounds, use implementation-owned constants or generic execution-limit names that are not sourced from Capability data and are not exposed as Capability configuration.

### R8 — one Tool descriptor per Capability

Build exactly one Tool descriptor for each selected Capability from its release-pinned Tool revision.

When several capabilities reuse one Tool revision, Shared deduplication/grant provenance must still produce one granted Tool with all applicable Capability keys.

### R9 — release replay/immutability remains deterministic

Preserve existing create/activate/rollback authorization, exact operation replay and immutable release semantics while changing the composition payload.

Do not make current Feature behaviour or current Tool publication state affect an already-created release.

## Work Items

- [ ] Consume the SHARED-002 package version and DATABASE-003 schema.
- [ ] Replace release request/read models that carry Capability revision IDs.
- [ ] Resolve one exact latest PUBLISHED Tool revision per selected Capability at release creation.
- [ ] Persist one immutable Feature behaviour snapshot per represented Feature.
- [ ] Build the new Shared manifest from direct release rows.
- [ ] Remove `selectionBinding`, `conversation_core` and RECOVERY_POLICY producer branches.
- [ ] Remove per-Capability prompt/configuration/toolBindings resolution.
- [ ] Remove Capability-derived `maxSearchResults` / `maxRecommendations` calculation.
- [ ] Update release activation/rollback/inspection paths for the new member model.
- [ ] Update C20/backend/MCP deterministic fixtures to the direct model.
- [ ] Add release immutability regression tests for later Tool publication and Feature-prompt edits.
- [ ] Add zero-selected-capability and reused-Tool manifest tests.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-DATABASE-003 database model
ARCH-021-SHARED-002 published Shared Commerce contract
ARCH-021-COMMERCE-088 direct Capability records
```

Produces manifests consumed by ARCH-021-BACKGROUND-002.

## Dependencies

- ARCH-021-DATABASE-003
- ARCH-021-SHARED-002
- ARCH-021-COMMERCE-088

## Enables

- ARCH-021-BACKGROUND-002
- ARCH-021-COMMERCE-092

## Acceptance Criteria

- [ ] Release creation contains no Capability revision ID input/output.
- [ ] Each release Capability pins exactly one PUBLISHED Tool revision belonging to the Capability's assigned Tool.
- [ ] Each represented Feature has exactly one immutable behaviour snapshot per release.
- [ ] Changing current Feature behaviour after release creation leaves the old manifest unchanged.
- [ ] Publishing a newer Tool revision after release creation leaves the old manifest pinned to the older exact revision.
- [ ] Runtime manifest production does not query/parse Capability revisions, bindings or configuration.
- [ ] No producer branch depends on BASE/RECOVERY_POLICY/`conversation_core`.
- [ ] Runtime Feature eligibility remains separate from authoring and is expressed through `featureId` only.
- [ ] No Capability-derived `maxSearchResults` / `maxRecommendations` remain.
- [ ] Zero selected capabilities is handled deterministically without inventing a base Capability.
- [ ] Reused Tool identities deduplicate correctly in the grant contract.

## Validation

- [ ] focused publication lifecycle tests
- [ ] focused backend integration tests
- [ ] focused MCP manifest/inspection tests
- [ ] focused Studio release service tests
- [ ] deterministic C20 fixture tests affected by the changed model
- [ ] targeted ESLint
- [ ] changed-file TypeScript diagnostics / repository typecheck evidence per baseline policy
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not modify Background or begin final legacy deletion.

## Implementation Notes

This task may make the current release UI use Capability IDs instead of revision IDs where necessary for compilation and functional parity, but it must not implement the new Feature Capability authoring wizard owned by COMMERCE-090/091.

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
