---
id: ARCH-021-SHARED-001
architecture_id: ARCH-021
title: Simplify Feature capability manifest and runner contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 88
executor: copilot
claimed_at: 2026-09-29T12:05:54Z
attempt: 1
depends_on:
  - ARCH-020-SHARED-001
enables:
  - ARCH-021-SHARED-002
created: 2026-09-29
updated: 2026-09-29
---

# Simplify Feature capability manifest and runner contracts

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the ARCH-020 selection-binding, per-Capability prompt/configuration and multi-Tool manifest contract with the direct Feature/Capability/Tool contract required by the simplified Commerce Studio model.

## Context

Shared currently defines `CommerceCapabilityBindingSchema` with `BASE`, `FEATURE` and `RECOVERY_POLICY`, requires `conversation_core`, carries per-Capability `promptName`, `configuration`, `revisionId` and `toolDescriptors[]`, and exposes capability configuration fields `maxSearchResults` / `maxRecommendations`.

The new model has only Feature-owned behaviour plus ordinary Feature capabilities, each backed by exactly one Tool. The immutable release already pins the exact Tool revision and Feature behaviour snapshot. Shared should describe that model directly.

The platform/shop CommerceAgent prompt remains a separate ARCH-021 concept. A Feature behaviour prompt is feature-scoped operational guidance and is applied once for each selected Feature; it is not another Agent Configuration prompt lineage.

## Scope

Primary files include:

```text
src/commerce/selection.ts
src/commerce/schemas.ts
src/commerce/definitions.ts
src/commerce/runner/index.ts
src/commerce/fixtures.ts
src/commerce/contracts.test.ts
src/commerce/runner/runner.test.ts
src/commerce/* relevant exports
scripts/validate-commerce-entrypoints.mjs
```

## Out of Scope

- Database schema/migrations.
- Commerce producer implementation.
- Background consumer implementation.
- Billing/subscription entitlement policy changes.
- Platform/shop Agent Configuration prompt/model ownership.
- Tool-definition authoring contracts unrelated to Capability association.

## Requirements

### R1 — remove the selection-binding union

Delete the Shared capability binding contract and special cases:

```text
CommerceCapabilityBindingSchema
CommerceCapabilityBinding
BASE
FEATURE binding discriminator
RECOVERY_POLICY
mandatory conversation_core base capability
discount_assistance recovery-policy branch
```

Do not introduce another discriminator that reproduces the same concept.

### R2 — select ordinary Feature capabilities only

Capability selection input must be expressible directly as:

```text
capability key
featureId
enabled
position
```

where Feature eligibility/facts may still determine whether that Feature's capabilities are selected at runtime.

There is no always-selected BASE capability. A valid selection may contain zero capabilities and zero granted Tools.

This task does not change how Feature eligibility facts are calculated by producers; it only removes Capability-type branching from the shared contract.

### R3 — one Tool descriptor per Capability

The manifest Capability entry must contain one exact Tool descriptor, not `toolDescriptors[]`.

The canonical conceptual shape is:

```ts
{
  capabilityId: string;
  key: string;
  featureId: string;
  position: number;
  toolDescriptor: ToolDescriptor;
}
```

A Tool may still be reused by multiple capabilities; `grantedTools` must deduplicate the union while retaining sorted `capabilityKeys` provenance.

### R4 — carry Feature behaviour once per selected Feature

Add a bounded manifest collection with one entry per selected Feature:

```ts
{
  featureId: string;
  behaviourPrompt: string;
}
```

Empty Feature behaviour text is valid and is ignored when composing model instructions.

The set of Feature behaviour entries must exactly match the distinct Feature IDs represented by the manifest's selected capabilities. Order must be deterministic by the first capability position for each Feature.

### R5 — remove per-Capability prompt/configuration/revision fields

Manifest Capability entries must no longer expose:

```text
revisionId
promptName
configuration
maxSearchResults
maxRecommendations
```

Delete `CommerceConfigurationSchema` and capability hash/binding helpers whose only purpose is the removed revision contract.

### R6 — preserve immutable release/grant identity without a base capability

`CommerceConversationGrant.selectedCapabilityKeys` remains the frozen Capability provenance for a conversation but may be empty.

Remove schema/refinement rules requiring `conversation_core`.

`manifestMatchesGrant`, current-grant Tool filtering and related helpers must continue to verify exact release, selected keys and granted Tool provenance without relying on a base key.

### R7 — runner consumes Feature behaviour, not Capability prompt names

Remove the runner invariant that `input.prompts.length === manifest.capabilities.length` and the lookup by per-Capability `promptName`.

The runner must apply each non-blank Feature behaviour prompt exactly once, regardless of how many capabilities under that Feature are selected.

Keep code-owned runner/protocol/security instructions separate and immutable.

Do not add model/provider selection to this contract.

### R8 — remove capability-owned search/recommendation limit concepts

No exported Shared Commerce contract may expose fields named:

```text
maxSearchResults
maxRecommendations
```

If bounded array/result safety remains necessary inside generic helpers, use implementation-owned generic bounds rather than author-configurable Capability settings.

### R9 — maintain bounded manifest/grant validation

Keep bounded JSON/array sizes and deterministic ordering. Adjust bounds for the new shapes without weakening existing protection against oversized grants/manifests, duplicate Tool identities or conflicting Tool descriptors.

## Work Items

- [ ] Remove `CommerceCapabilityBindingSchema` and special BASE/RECOVERY_POLICY selection branches.
- [ ] Allow zero selected Feature capabilities/Tools.
- [ ] Define the direct one-Tool Capability manifest shape.
- [ ] Add one Feature behaviour entry per represented Feature.
- [ ] Remove Capability `revisionId`, `promptName` and configuration from the manifest.
- [ ] Remove `maxSearchResults` / `maxRecommendations` from exported contracts.
- [ ] Update Tool deduplication/provenance helpers for one descriptor per Capability.
- [ ] Update runner composition to apply Feature behaviour once per Feature.
- [ ] Remove obsolete capability hash/Tool-binding helpers if no longer consumed by supported contracts.
- [ ] Update deterministic fixtures and contract/runner tests.
- [ ] Validate package Commerce entrypoints.

## Interfaces / Contracts

Produces the next Shared Commerce contract consumed by:

```text
moda-interact-commerce    producer
moda-interact-background  consumer
```

The exact exported schema/type names should remain concise and domain-owned. Do not keep deprecated aliases for `CommerceCapabilityBinding` or capability configuration merely to reduce consumer changes during this pre-production breaking rollout.

## Dependencies

- ARCH-020-SHARED-001

## Enables

- ARCH-021-SHARED-002

## Acceptance Criteria

- [ ] No Shared Commerce export contains the BASE/FEATURE/RECOVERY_POLICY binding union.
- [ ] No Shared manifest/grant rule requires `conversation_core`.
- [ ] A manifest with zero capabilities and zero granted Tools is valid when all other contract fields are valid.
- [ ] Every manifest Capability has exactly one Feature and one Tool descriptor.
- [ ] Feature behaviour text appears once per represented Feature, never once per Capability.
- [ ] A reused Tool is emitted once in `grantedTools` with deterministic Capability provenance.
- [ ] No exported Shared contract includes Capability `promptName`, Capability revision identity, `maxSearchResults` or `maxRecommendations`.
- [ ] Runner tests prove one Feature prompt is applied once when two capabilities share that Feature.
- [ ] Existing Tool authorization, exact revision provenance, response-contract and bounded-payload protections remain intact.

## Validation

- [ ] `npm test`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `npm run validate:commerce-entrypoints`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not publish the package or modify consumers.

## Implementation Notes

This is a breaking contract implementation task. Package publication is deliberately separate in ARCH-021-SHARED-002.

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
