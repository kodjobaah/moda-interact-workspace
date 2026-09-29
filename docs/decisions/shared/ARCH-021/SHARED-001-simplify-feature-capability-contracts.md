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
status: complete
priority: 88
executor: null
claimed_at: null
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

- [x] Remove `CommerceCapabilityBindingSchema` and special BASE/RECOVERY_POLICY selection branches.
- [x] Allow zero selected Feature capabilities/Tools.
- [x] Define the direct one-Tool Capability manifest shape.
- [x] Add one Feature behaviour entry per represented Feature.
- [x] Remove Capability `revisionId`, `promptName` and configuration from the manifest.
- [x] Remove `maxSearchResults` / `maxRecommendations` from exported contracts.
- [x] Update Tool deduplication/provenance helpers for one descriptor per Capability.
- [x] Update runner composition to apply Feature behaviour once per Feature.
- [x] Remove obsolete capability hash/Tool-binding helpers if no longer consumed by supported contracts.
- [x] Update deterministic fixtures and contract/runner tests.
- [x] Validate package Commerce entrypoints.

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

- [x] No Shared Commerce export contains the BASE/FEATURE/RECOVERY_POLICY binding union.
- [x] No Shared manifest/grant rule requires `conversation_core`.
- [x] A manifest with zero capabilities and zero granted Tools is valid when all other contract fields are valid.
- [x] Every manifest Capability has exactly one Feature and one Tool descriptor.
- [x] Feature behaviour text appears once per represented Feature, never once per Capability.
- [x] A reused Tool is emitted once in `grantedTools` with deterministic Capability provenance.
- [x] No exported Shared contract includes Capability `promptName`, Capability revision identity, `maxSearchResults` or `maxRecommendations`.
- [x] Runner tests prove one Feature prompt is applied once when two capabilities share that Feature.
- [x] Existing Tool authorization, exact revision provenance, response-contract and bounded-payload protections remain intact.

## Validation

- [x] `npm test`
- [x] `npm run typecheck`
- [x] `npm run build`
- [x] `npm run validate:commerce-entrypoints`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not publish the package or modify consumers.

## Implementation Notes

This is a breaking contract implementation task. Package publication is deliberately separate in ARCH-021-SHARED-002.

## Completion Report

### Status

Ready for Architect Review. Attempt 1 was prepared and claimed by the deterministic launcher; claim metadata is cleared for handoff.

### Files Changed

- `src/commerce/schemas.ts`: removed binding/configuration contracts and the mandatory base capability; defined direct Capability/Tool and per-Feature behavior manifest entries; allows empty selected/granted sets; retained strict size, identity, provenance, and ordering validation.
- `src/commerce/selection.ts`: selects direct Feature capabilities, permits empty selection, deduplicates one Tool descriptor per Capability, and preserves deterministic provenance/current-grant filtering.
- `src/commerce/definitions.ts`: removed obsolete Tool-binding and capability-hash helpers.
- `src/commerce/external.ts`: renamed exported generic processor limit `maxSearchResults` to `maxResults` so no exported Shared Commerce contract exposes a capability-owned search limit name.
- `src/commerce/fixtures.ts`, `src/commerce/contracts.test.ts`: migrated fixtures and contract tests; added empty manifest/grant, direct Feature selection, one-descriptor deduplication, and represented-Feature behavior coverage.
- `src/commerce/runner/index.ts`, `src/commerce/runner/runner.test.ts`: compose manifest Feature behavior once per represented Feature and resolve direct Tool descriptors; added shared-Feature/two-capability regression coverage.
- `scripts/validate-commerce-entrypoints.mjs`: removed per-capability prompt injection from clean-process entrypoint validation.

### Work Completed

- Implemented the direct Feature/Capability/Tool contracts without deprecated binding aliases or capability-owned prompt/configuration/revision fields.
- Removed the required `conversation_core` base behavior and validated zero-capability, zero-Tool manifests and grants.
- Kept Tool authorization and revision descriptors pinned, with reuse deduplicated by Tool identity and sorted capability provenance.
- Moved operational behavior into the manifest's bounded Feature snapshot, with exact represented-Feature coverage and once-per-Feature runner composition; blank behavior text remains valid and is omitted from instructions.
- Kept edits within the Shared package and its entrypoint validator. No Commerce or Background consumers were modified and the package was not published.

### Validation Results

- `npm exec -- tsx --test src/commerce/contracts.test.ts`: PASS, 14/14 tests.
- `npm exec -- tsx --test src/commerce/runner/runner.test.ts`: PASS, 17/17 tests.
- `npm test`: PASS, 165 passed, 0 failed, 1 skipped. The BullMQ Redis telemetry case skipped because `TEST_REDIS_URL` was not configured.
- `npm run typecheck`: PASS (`tsc --noEmit`).
- `npm run build`: PASS (ESM and DTS builds).
- `npm run validate:commerce-entrypoints`: PASS; clean-process commerce and runner imports, schema, scripted finalResponse, and R1/R2 regressions.
- `npm ci`: PASS; installed 185 packages from the lockfile for this prepared implementation worktree.

### Deviations

No scope deviation. As required, consumer repositories and package publication were left untouched. The generic exported external processor limit was renamed from `maxSearchResults` to `maxResults` to satisfy R8; existing Commerce consumer call sites still use the old name and must be coordinated with the dependent consumer migration before consuming the published breaking package.

### Assumptions

The task's deterministic launcher preparation evidence is recorded as follows: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; dedicated parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-SHARED-001` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-SHARED-001`, both on `task/ARCH-021-SHARED-001`; origin/main was current at preparation; recursive submodule sync/update passed in both worktrees with ready status and zero entries; durable launcher claim commit `7d3aa1150d264aa5458e88ca3da05c09a51b7c7e`.

### Unresolved Issues

The required cross-repository consumer updates remain for their owning tasks. In particular, Commerce currently passes `maxSearchResults` to generic Shared external processors and must adopt `maxResults` as part of the coordinated breaking-contract rollout; no consumer edits were included here.

### Architectural Concerns

The existing ARCH-021-SHARED-002 publication gate and downstream Commerce/Background consumer tasks must remain sequenced after Architect acceptance of this breaking contract. Implementation commit `ab28522` (`feat(ARCH-021-SHARED-001): simplify commerce capability contracts`) was pushed to `origin/task/ARCH-021-SHARED-001`.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted after direct review of implementation commit `ab28522460f9b62403ca2b56e6009ca9fa9e473d` and the documentation-only correction commit `c70584ade2e684f6c498ec765cc61897870ec030`. The implementation removes the selection-binding union, mandatory `conversation_core`, per-Capability prompt/configuration/revision fields and multi-Tool bindings; it defines ordinary Feature Capabilities with one exact Tool descriptor, permits empty selections, preserves deterministic Tool provenance and applies Feature behaviour once per represented Feature.

The only review defect was stale Shared documentation describing removed APIs. The correction commit changes only `README.md` and `src/commerce/README.md`; the removed names are no longer documented. No runtime source changed after the validated implementation commit.

### Reviewed Files

- `src/commerce/schemas.ts`
- `src/commerce/selection.ts`
- `src/commerce/definitions.ts`
- `src/commerce/external.ts`
- `src/commerce/fixtures.ts`
- `src/commerce/contracts.test.ts`
- `src/commerce/runner/index.ts`
- `src/commerce/runner/runner.test.ts`
- `scripts/validate-commerce-entrypoints.mjs`
- `README.md`
- `src/commerce/README.md`

### Validation Reviewed

Reviewed the recorded passing implementation validation: focused Commerce contract tests 14/14, runner tests 17/17, `npm test` 165 passed / 1 skipped for missing `TEST_REDIS_URL`, `npm run typecheck`, `npm run build`, `npm run validate:commerce-entrypoints`, and `npm ci`. The final correction was documentation-only, so the implementation validation was not required to be rerun. GitHub comparison confirms `c70584a` is exactly one commit ahead of `ab28522` and changes only the two README files.

### Architecture Conformance

Conforms to the agreed breaking pre-production Feature -> Capability -> Tool contract. Shared no longer models BASE/FEATURE/RECOVERY_POLICY bindings, Capability-owned prompts/configuration, Capability revision identity, `maxSearchResults` or `maxRecommendations`. The runner consumes Feature behaviour from the manifest once per Feature and exact Tool authorization/provenance remains pinned. Consumer migration and package publication remain correctly separated.

### Follow-up

ARCH-021-SHARED-002 is now Ready as the publication-only gate. Commerce and Background consumer changes remain gated on the published Shared version. Commerce must adopt the renamed generic processor limit `maxResults` in its owning consumer task; no compatibility alias should be introduced.
