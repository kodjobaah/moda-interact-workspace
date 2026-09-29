---
id: ARCH-021-DATABASE-003
architecture_id: ARCH-021
title: Simplify Feature capability and release persistence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 88
executor: copilot
claimed_at: 2026-09-29T11:07:26Z
attempt: 1
depends_on:
  - ARCH-021-DATABASE-002
enables:
  - ARCH-021-COMMERCE-088
  - ARCH-021-COMMERCE-089
  - ARCH-021-BACKGROUND-002
created: 2026-09-29
updated: 2026-09-29
---

# Simplify Feature capability and release persistence

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the ARCH-020 capability-revision/binding persistence model with the agreed direct `Feature -> CommerceCapability -> CommerceTool` model and immutable release snapshots, while preserving Admin-owned `billing.Feature` and Tool revision publication.

## Context

Capability authoring currently persists a `CommerceCapability` shell and then separately creates/publishes `CommerceCapabilityRevision` rows containing prompt text, arbitrary configuration and an array of Tool bindings. `CommerceCapability.selectionBinding` also encodes `BASE`, `FEATURE` and `RECOVERY_POLICY` special cases.

The agreed ARCH-021 refinement is intentionally smaller:

```text
billing.Feature                         Admin-owned identity
      |
      +-- commerce feature behaviour    one current shared prompt
      |
      +-- CommerceCapability            one Feature + one Tool
              |
              +-- CommerceTool          authoring identity
```

Capability rows are not revisioned. Release creation, not Capability authoring, freezes the exact published Tool revision and the current Feature behaviour prompt. `selectionBinding`, `maxSearchResults` and `maxRecommendations` are not durable capability concepts.

ARCH-021 is pre-production for this area. Do not build a data-conversion framework for obsolete development-only capability/release/grant state.

## Scope

Modify `moda-interact-database` only.

Primary files include:

```text
prisma/schema.prisma
prisma/migrations/<new ARCH-021 feature-capability simplification migration>/migration.sql
scripts/<focused ARCH-021 feature-capability schema validator>.mjs
scripts/<focused ARCH-021 feature-capability migration rehearsal>.mjs
package.json
```

Update generated ERD input/output only if that is part of the repository's normal schema-change validation contract.

## Out of Scope

- Admin Feature creation/editing or billing-plan/subscription policy.
- Commerce Studio services or React UI.
- Shared manifest/runner contracts.
- Background host changes.
- Tool-definition or Tool-revision authoring semantics.
- Platform/shop CommerceAgent model/prompt configuration from Phase 2.
- Preserving obsolete development-only Capability revision/release/grant rows through a compatibility layer.

## Requirements

### R1 — `billing.Feature` remains the canonical Feature

Do not move Feature ownership into the Commerce schema and do not add Commerce authoring fields to the Admin-owned Feature record.

`Feature` may gain only the inverse relations required by the new Commerce records.

### R2 — add one current Commerce Feature behaviour record

Persist one optional current Commerce configuration row per Feature. The canonical semantics are:

```text
featureId          exactly one billing.Feature
behaviourPrompt    current shared Feature instruction text; empty is valid
editVersion        monotonic CAS version
createdAt
updatedAt
```

Use a dedicated Commerce model such as `CommerceFeatureConfiguration`; do not create Feature prompt drafts/revisions/publication tables.

The row must be uniquely identified by `featureId`, use `ON DELETE RESTRICT`, and support safe create/update CAS without an ABA delete/recreate lifecycle. The supported lifecycle does not delete this row.

### R3 — make every Commerce Capability a direct Feature/Tool association

Replace the existing Capability persistence contract with a row containing, at minimum:

```text
id
key                 globally stable unique capability key
displayName
description
featureId            required FK to billing.Feature
toolId               required FK to CommerceTool
enabled
createdAt
updatedAt
```

`featureId`, `key` and `toolId` are immutable after creation. Display metadata and `enabled` may remain mutable through existing/new service actions.

A Tool may be reused by more than one Capability. Do not add a uniqueness rule that forbids that reuse.

### R4 — delete the obsolete capability binding/revision model

Remove the durable concepts:

```text
CommerceCapability.selectionBinding
CommerceCapabilitySelectionBinding
CommerceCapabilityRevision
CommerceCapabilityRevision.promptTemplate
CommerceCapabilityRevision.configuration
CommerceCapabilityRevision.toolBindings
capability draft/publish ownership FKs and indexes
```

Do not rename these into equivalent structures.

`CommerceToolRevision` must stop using the capability-named revision-status enum. Give Tool revision status its own correctly named enum and migrate the Tool rows without changing Tool DRAFT/PUBLISHED semantics.

### R5 — release rows pin the actual immutable inputs

Replace `CommerceReleaseCapability.capabilityRevisionId` with direct immutable release membership that records enough information to prove:

```text
release
capability
feature
Tool identity
exact PUBLISHED Tool revision
position
```

Database integrity must prevent a release member from pairing a Capability with a Tool different from that Capability's assigned Tool or pairing a Tool revision with a different Tool identity.

Add one release Feature snapshot row per `(releaseId, featureId)` containing the exact `behaviourPrompt` text used by that release. Multiple capabilities belonging to the same Feature must share that one snapshot rather than duplicating Feature prompt text per capability.

Release Feature/member rows are immutable after creation.

### R6 — release snapshot does not reintroduce capability revisions

The immutable release boundary is sufficient. Do not create replacement entities such as:

```text
CommerceCapabilityVersion
CommerceCapabilityDraft
CommerceFeatureBehaviourRevision
CommerceCapabilityToolBinding
```

unless returned to `moda_architect` as a blocker before implementation.

### R7 — remove capability-level search/recommendation configuration

No new or retained database column/JSON contract may persist:

```text
maxSearchResults
maxRecommendations
```

Tool/result safety bounds, if still required by runtime code, are implementation limits owned outside this schema.

### R8 — remove special BASE/RECOVERY_POLICY database semantics

Remove database constraints/indexes/triggers whose purpose is to enforce:

```text
conversation_core as BASE
discount_assistance as RECOVERY_POLICY
one BASE capability
selectionBinding-specific featureId rules
```

All persisted Capabilities after this migration belong to an Admin Feature.

### R9 — simplify audit actions consistently

Retain Capability create/update/enable/disable actions that remain meaningful. Add one audit action for Feature behaviour changes.

Remove Capability-only audit actions whose operations no longer exist, including generic Capability draft/update/publish actions, provided they are not consumed by another still-supported entity.

Do not remove Tool-specific draft/publication audit actions.

### R10 — explicitly recreate obsolete pre-production capability state

The migration must treat existing ARCH-020 Capability revision/release/pointer/grant composition as development-only state to recreate, rather than attempting lossy inference from arbitrary multi-Tool bindings.

It may clear the affected Commerce capability/release/grant records in dependency-safe order before replacing the schema, but must preserve unrelated durable data, including:

```text
billing.Feature
Billing/Merchant pricing/subscription records
CommerceTool and CommerceToolRevision
Connections and credentials
Agent Configuration/model/prompt/template records
Shops, conversations and recovery records
```

The migration rehearsal must prove this preservation boundary on a seeded upgrade database.

## Work Items

- [x] Add the one-row-per-Feature Commerce behaviour configuration model.
- [x] Replace Capability persistence with required Feature + Tool FKs.
- [x] Remove `selectionBinding` and its enum/guards/indexes.
- [x] Remove `CommerceCapabilityRevision` and all revision-owned prompt/configuration/binding persistence.
- [x] Rename/separate Tool revision status from the removed Capability revision enum without changing Tool semantics.
- [x] Replace release membership with direct Capability + exact Tool revision pinning.
- [x] Add immutable per-release Feature behaviour snapshots.
- [x] Remove Capability-level `maxSearchResults` / `maxRecommendations` persistence.
- [x] Reconcile Commerce audit enum/FKs with the new lifecycle.
- [x] Implement the explicit pre-production recreate strategy for obsolete Capability/release/grant rows.
- [x] Add focused schema validation.
- [x] Add fresh and seeded-upgrade PostgreSQL migration rehearsals.

## Interfaces / Contracts

Produces the database contract consumed by later ARCH-021 tasks:

```text
billing.Feature
commerce.CommerceFeatureConfiguration
commerce.CommerceCapability
commerce.CommerceReleaseFeature
commerce.CommerceReleaseCapability
commerce.CommerceTool
commerce.CommerceToolRevision
```

Exact Prisma-generated names may follow the canonical schema names selected above; do not expose a compatibility representation of removed Capability revisions.

## Dependencies

- ARCH-021-DATABASE-002

## Enables

- ARCH-021-COMMERCE-088
- ARCH-021-COMMERCE-089
- ARCH-021-BACKGROUND-002

## Acceptance Criteria

- [x] Every persisted Commerce Capability has exactly one non-null Feature and exactly one non-null Tool.
- [x] No `CommerceCapabilitySelectionBinding` type or `selectionBinding` column remains.
- [x] No `CommerceCapabilityRevision` table/model remains.
- [x] No Capability persistence stores prompt text, arbitrary configuration, Tool-binding arrays, `maxSearchResults` or `maxRecommendations`.
- [x] Tool revision DRAFT/PUBLISHED status remains intact under a correctly owned enum.
- [x] A release pins one exact published Tool revision per member Capability.
- [x] A release stores Feature behaviour prompt text once per represented Feature.
- [x] Release Feature/member rows cannot be mutated after creation.
- [x] Existing obsolete Capability/release/grant development state is deliberately recreated, not heuristically converted.
- [x] The seeded upgrade preserves Tools, Features and all unrelated billing/agent-configuration data proved by the migration validator.
- [x] Prisma validation and focused fresh/upgrade rehearsals pass.

## Validation

- [x] `npm run prisma:validate`
- [x] `npm run prisma:generate`
- [x] focused ARCH-021 feature-capability schema validator added by this task
- [x] focused fresh PostgreSQL migration rehearsal added by this task
- [x] focused seeded-upgrade PostgreSQL migration rehearsal proving the preservation boundary

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not begin Commerce, Shared or Background work.

## Implementation Notes

This is a deliberate breaking simplification. Prefer deleting obsolete SQL guards/functions/triggers over adapting them to concepts that no longer exist.

Do not modify billing Feature semantics merely because Commerce now requires a Feature FK.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

`moda-interact-database/prisma/schema.prisma`, `moda-interact-database/prisma/migrations/20260929120000_arch021_feature_capability_simplification/migration.sql`, `moda-interact-database/scripts/validate-arch021-feature-capability-schema.mjs`, `moda-interact-database/scripts/validate-arch021-feature-capability-migration.mjs`, `moda-interact-database/package.json`, `moda-interact-database/docs/generated/prisma-erd.puml`

### Work Completed

Added `CommerceFeatureConfiguration` as a permanent one-row-per-Feature CAS record. Capabilities now have immutable required Feature and Tool identities and no selection-binding or revisioned authoring model. Release members pin the exact published Tool revision, with composite foreign keys enforcing Capability/Feature/Tool and Tool/Revision identity. Added a single immutable Feature prompt snapshot per represented release Feature. Tool status now uses `CommerceToolRevisionStatus`; obsolete capability audit actions and special BASE/RECOVERY_POLICY guards were removed. The migration clears only pre-production Capability/release/pointer/grant composition and obsolete composition audits, preserving Tool and ToolRevision history and unrelated data. Implementation commit `b648b86` is pushed to `task/ARCH-021-DATABASE-003`.

### Validation Results

`npm run prisma:validate` passed. `npm run prisma:generate` passed. `npm run test:arch021-feature-capability-schema` passed. `npm run test:arch021-feature-capability-migration` structural checks passed. Fresh PostgreSQL rehearsal passed on isolated local PostgreSQL 15 database `arch021_feature_capability_test_fresh`. Seeded-upgrade PostgreSQL rehearsal passed on isolated local PostgreSQL 15 database `arch021_feature_capability_test_upgrade`; 18 protected data tables were byte-for-byte unchanged, including Feature, billing plans/subscriptions, Merchant pricing, Tools/revisions, connection revisions/credentials, model/prompt/template configuration, Shop, CheckoutRecovery and Conversation. Ten database behavior checks passed for CAS, immutability, one shared Feature snapshot, exact Tool identity, and published Tool revision requirements. `npm run erd:puml` passed. `git diff --check` passed.

### Deviations

No scope deviation. PostgreSQL upgrade rehearsal required an explicit deletion of legacy Capability rows because existing BASE rows have no Feature and arbitrary revision bindings cannot be losslessly converted; this is the task's approved pre-production recreate strategy.

### Assumptions

The obsolete ARCH-020 Capability/release/pointer/grant composition is development-only and may be recreated as specified. The standard local Docker PostgreSQL 15 container and uniquely named test databases were disposable task-owned resources.

### Unresolved Issues

None.

### Architectural Concerns

None.

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
