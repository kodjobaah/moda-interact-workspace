---
id: ARCH-023-DATABASE-002
architecture_id: ARCH-023
title: Persist localised store-category and prompt configuration
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 11
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-023-ADMIN-001
  - ARCH-023-ADMIN-002
  - ARCH-023-ADMIN-003
  - ARCH-023-SHOPIFY-001
  - ARCH-023-SHOPIFY-002
  - ARCH-023-BACKGROUND-001
  - ARCH-023-BACKGROUND-002
  - ARCH-023-COMMERCE-001
  - ARCH-023-COMMERCE-003
  - ARCH-023-SYSTEM-TEST-001
created: 2026-09-27
updated: 2026-09-27
---

# Persist localised store-category and prompt configuration

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Extend the existing Commerce prompt/template schema with localised category/template/prompt state and a shop-scoped Commerce profile that can hold active and pending store-category selections.

## Context

ARCH-021 already persists categories, templates, platform/shop prompt lineages and revisions. ARCH-023 keeps those concepts but adds an explicit default template per category, Shopify taxonomy mapping, immutable per-source-version translations, and pending-vs-active shop category state used during onboarding.

## Scope

- Extend `CommercePromptTemplateCategory` with explicit default-template/fallback and translation-readiness state.
- Add category translation history keyed by category/source edit version/locale.
- Add Shopify taxonomy-to-category mapping with deterministic uniqueness.
- Extend `CommercePromptTemplate` with source language and translation-readiness state; add immutable translation history keyed by template/source edit version/locale.
- Extend `CommerceAgentPromptRevision` with source language/template edit-version provenance and add immutable prompt-revision translations.
- Add `CommerceShopProfile` with active category plus pinned pending category/template edit version/language/prompt revision state.
- Add required Shop/PlatformAdmin/Audit relations and indexes consistent with the existing Commerce schema.

## Out of Scope

- Merchant Knowledge content/vector tables.
- Translation provider execution.
- Admin/Shopify UI.
- Changing model-selection override semantics.

## Requirements

- Each enabled category can reference exactly one explicit default template from that same category; no implicit first-template selection.
- At most one enabled/fallback category is designated platform-wide for unmatched Shopify taxonomy evidence.
- A Shopify taxonomy category identifier maps to at most one Moda Store Category.
- Translation history is retained by exact source edit version/revision and locale; a newer edit cannot treat older translations as current.
- All locale tags use the existing canonical 20-locale set/application validation rather than a new database enum.
- `CommerceShopProfile` is one-to-one with Shop and cascades on Shop deletion.
- Pending onboarding state pins the exact template identity/edit version and language previewed before external Shopify navigation.
- Existing ARCH-021 prompt/template rows migrate without semantic loss.

## Work Items

- [ ] Update Prisma schema and one bounded migration.
- [ ] Add database triggers/checks/partial uniqueness needed for same-category default template and single fallback category.
- [ ] Add fresh and upgrade migration fixtures covering existing ARCH-021 data.
- [ ] Regenerate repository-standard Prisma/ERD artifacts if required.

## Interfaces / Contracts

Provides durable state consumed by Admin, Shopify, Background and Commerce. Runtime localisation/queue contracts are owned by ARCH-023-SHARED-001 and runner composition by ARCH-023-SHARED-003.

## Dependencies

None

## Enables

- ARCH-023-ADMIN-001
- ARCH-023-ADMIN-002
- ARCH-023-ADMIN-003
- ARCH-023-SHOPIFY-001
- ARCH-023-SHOPIFY-002
- ARCH-023-BACKGROUND-001
- ARCH-023-BACKGROUND-002
- ARCH-023-COMMERCE-001
- ARCH-023-COMMERCE-003
- ARCH-023-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Existing platform/shop prompts and templates survive upgrade.
- [ ] Default-template cross-category assignment is rejected.
- [ ] A second fallback category is rejected.
- [ ] Duplicate Shopify taxonomy mapping is rejected.
- [ ] Historical translations for older edit versions remain queryable after a source edit.
- [ ] Shop profile active/pending state round-trips and deletes with its Shop.

## Validation

- [ ] Prisma validation.
- [ ] Fresh migration validation.
- [ ] Upgrade migration preserving representative ARCH-021 prompt/template/configuration data.
- [ ] Constraint/trigger fixtures for default/fallback/mapping invariants.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

Use the existing `commerce` schema. Do not replace first-class tables with JSON blobs.

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

Pending.

### Follow-up

None
