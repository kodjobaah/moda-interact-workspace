---
id: ARCH-021-DATABASE-001
architecture_id: ARCH-021
title: Persist Phase 2 CommerceAgent configuration schema
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-DATABASE-001
enables:
  - ARCH-021-COMMERCE-007
  - ARCH-021-COMMERCE-008
created: 2026-09-23
updated: 2026-09-23
---

# Persist Phase 2 CommerceAgent configuration schema

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Persist the complete Phase 2 durable data model for CommerceAgent model selection, prompt-template categorisation/versioning, platform/shop prompt revisioning, and independent platform/shop active configuration pointers.

## Context

ARCH-021 defines model and configurable behavioural prompt as independent CommerceAgent configuration axes resolved per shop with platform fallback. Phase 2 also introduces reusable application-wide prompt templates as copy-on-use authoring assets. These concepts form one cohesive Commerce configuration schema and should be introduced in one migration/task so ownership, foreign keys, uniqueness, indexes and audit vocabulary are designed together.

Prompt-template classification is data-driven rather than a code enum. A category such as `Clothing & Fashion` may contain any number of prompt templates, and new categories must not require a schema or application-code release.

## Scope

- Add the Moda-controlled Commerce model catalogue with stable provider/model identity, display metadata, enabled state and audit metadata.
- Support the initial model providers `OPENAI` and `GROQ` through a canonical constrained representation.
- Add environment-scoped platform model default selection and optional environment+shop model override with independent edit-version/CAS state.
- Add a platform-wide prompt-template category/classification entity with stable id/slug, display name, optional description, enabled state, display order and audit metadata.
- Model category -> templates as one-to-many: every template belongs to exactly one category; one category may contain multiple templates.
- Add platform-wide prompt-template identities and versioned draft/published template revisions with immutable published content, revision number and content hash.
- Add the singleton platform behavioural-prompt lineage and at-most-one prompt lineage per shop with versioned draft/published prompt revisions.
- Allow prompt revisions to retain optional `sourceTemplateRevisionId` provenance only; there is no live inheritance from a template.
- Add environment-scoped platform active-prompt pointer and optional environment+shop prompt override pointer with independent edit-version/CAS state.
- Enforce scope integrity: platform pointers target platform prompt revisions; shop pointers target published prompt revisions belonging to the exact shop.
- Extend Commerce audit-action vocabulary as required for model, category, template, prompt and pointer lifecycle operations.
- Add the indexes/constraints required for deterministic catalogue/category/template/revision listings and exact platform/shop resolution.
- Create one coherent Prisma migration and focused schema/migration validation for the entire Phase 2 model.

## Out of Scope

- Provider API keys or credentials.
- OpenAI/Groq calls or model discovery from provider APIs.
- Live Shopify/external Tool execution.
- CommerceConversationGrant or manifest model/prompt pins.
- Background/runtime changes.
- Feature/capability prompt removal.
- Shop-owned reusable prompt-template libraries.
- Merchant authentication/authorization.

## Requirements

- Model catalogue provider + providerModelId is unique and cannot be repurposed to another provider model under the same stable id; this durable identity immutability must be database-enforced rather than only a Commerce-service convention.
- Disabling a model prevents normal new selection but does not delete historical identity or rewrite existing pointers.
- Platform model default and shop model override are durable independent selections; clearing a shop override is represented by absence, not a copied platform row.
- Prompt-template categories are durable data, not an enum. Category slug is unique/stable and must not be repurposed under the same category identity; display metadata may be changed without rewriting template revisions.
- A category may contain multiple templates; each template must belong to one category.
- Disabling a category or template must not delete historical template identities/revisions or invalidate prompt provenance.
- Published template revisions and published prompt revisions are immutable.
- There is exactly one logical platform prompt lineage and at most one prompt lineage per shop.
- Prompt active pointers reference published prompt revisions, never template revisions.
- `sourceTemplateRevisionId` is provenance only and must not create cascade behaviour that mutates/deletes copied prompt content when a template changes.
- Model pointer edit versions and prompt pointer edit versions are independent; mutating one configuration axis must not advance the other.
- Relations to PlatformAdmin and Shop use deletion behaviour consistent with preserving authored/audit history and tenant integrity.
- No model/provider credential or secret is persisted in these entities.

## Work Items

- [ ] Add model-provider constrained representation and model-catalogue model.
- [ ] Add platform/shop model-selection models/constraints with independent edit versions.
- [ ] Add prompt-template category/classification model and category/template one-to-many relation.
- [ ] Add prompt-template identity and revision models with draft/published lifecycle.
- [ ] Add platform/shop prompt lineage and prompt-revision models with optional template provenance.
- [ ] Add platform/shop prompt active-pointer models/constraints with independent edit versions.
- [ ] Add required Commerce audit-action values.
- [ ] Add uniqueness, durable-identity immutability guards, scope-integrity and listing/resolution indexes.
- [ ] Create the Prisma migration.
- [ ] Add focused ARCH-021 schema/migration validation covering the complete Phase 2 model.

## Interfaces / Contracts

Produces durable concepts consumed by Phase 2 Commerce tasks:

- model catalogue entry;
- environment platform model selection;
- environment+shop model override;
- prompt-template category/classification;
- prompt template and immutable published template revision;
- platform/shop prompt lineage and immutable published prompt revision;
- optional copied-template provenance;
- environment platform active prompt pointer;
- environment+shop active prompt override pointer.

No Shared package/runtime contract is created in Phase 2. Cross-service grant/manifest contracts remain deferred until the runtime phase.

## Dependencies

- ARCH-020-DATABASE-001

## Enables

- ARCH-021-COMMERCE-007
- ARCH-021-COMMERCE-008

## Acceptance Criteria

- [ ] One migration/schema coherently represents the complete Phase 2 model/prompt configuration domain.
- [ ] An OpenAI or Groq catalogue entry can be stored without any credential.
- [ ] Once created, a model catalogue entry's provider/providerModelId cannot be changed under the same catalogue-entry identity, while mutable presentation/enabled fields remain independently editable.
- [ ] Platform/shop model selections are environment scoped, independently versioned and constrained to catalogue identities.
- [ ] A data-driven category such as `Clothing & Fashion` can own multiple prompt templates without a code/schema change.
- [ ] A category's stable slug/identity cannot be repurposed by a metadata update, while mutable display metadata remains editable.
- [ ] Every prompt template belongs to exactly one category and category/template history survives disablement.
- [ ] Template and prompt revision numbering is deterministic and published revision content is immutable.
- [ ] Exactly one platform prompt lineage and at most one prompt lineage per shop are enforceable under concurrency.
- [ ] Platform/shop prompt pointers target only the correct published lineage scope.
- [ ] Template provenance does not create live linkage or cascade mutation of copied prompts.
- [ ] Model and prompt pointer CAS/edit-version state is independent.
- [ ] Migration/schema validation proves expected columns, constraints, uniqueness and indexes and existing ARCH-020 Commerce schema remains valid.

## Validation

- [ ] `npm run prisma:validate`
- [ ] `npm run prisma:generate`
- [ ] focused ARCH-021 Phase 2 schema validator
- [ ] durable model provider/providerModelId identity-mutation rejection test
- [ ] durable prompt-template category slug/identity mutation rejection test
- [ ] migration rehearsal against disposable PostgreSQL where available/required by repository policy
- [ ] concurrency/constraint rehearsal for platform/shop singleton and pointer scope where repository practice supports it
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin a Commerce task.

## Implementation Notes

Keep the schema data-driven. Do not encode prompt-template categories such as `Clothing & Fashion` as a Prisma enum. Do not introduce provider execution/runtime fields merely because model identities are now durable.

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
