---
id: ARCH-021-COMMERCE-069
architecture_id: ARCH-021
title: Remove obsolete Storefront Tool architecture
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 76
executor: copilot
claimed_at: 2026-09-27T17:16:35Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-060
  - ARCH-021-COMMERCE-064
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Remove obsolete Storefront Tool architecture

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Complete the pre-production Shopify simplification by removing `SHOPIFY_STOREFRONT_QUERY` as a Moda Commerce Tool execution/authoring mode and deleting the Storefront-only compiler, transport, discovery/query-builder artifacts and tests that are no longer required after Admin execution and Admin Explore authoring are operational.

## Context

The platform is still in development and the user has explicitly approved breaking removal of the transitional Storefront Tool model rather than maintaining compatibility.

By this task:

```text
COMMERCE-060 -> Admin Tool runtime exists
COMMERCE-064 -> Explore Shopify uses Admin API and local authoring sessions
```

There is therefore no product reason to keep a parallel Storefront Tool execution kind.

This task removes the Moda Tool architecture, not legitimate Shopify concepts or schema fields that happen to contain the word `Storefront`.

## Scope

Expected implementation areas include:

```text
src/commerce/tool-definition/contracts.ts
src/commerce/execution/
src/commerce/query/                              # remove Storefront-only runtime
src/commerce/integration/backend/executors.ts
lib/discovery/compiler.ts                        # Storefront Tool compiler
lib/discovery/storefront-artifact.ts
lib/discovery/artifacts/storefront-2026-07.json  # if no remaining legitimate consumer
src/studio/discovery/storefront-*.ts(x)
legacy Storefront fixtures/seeds/tests
architecture-local validation scripts that exist only for Storefront Tool authoring
```

Exact removal must be evidence-driven: retain any file still required for a separate non-Tool capability and report it.

## Out of Scope

- Removing unrelated Shopify Storefront terminology/data from the repository.
- Migrating old development Storefront Tool definitions to Admin GraphQL.
- Building backwards-compatibility adapters.
- Result Template UI.
- General tab traversal/gating.
- Database migrations solely to preserve obsolete development Tool definitions.

## Requirements

### R1 — canonical execution union is Admin-only for Shopify

Remove `SHOPIFY_STOREFRONT_QUERY` from the Commerce Tool execution union and all mapping/type helpers that exist only to support that execution kind.

The Shopify Tool execution kind remaining in new canonical definitions is:

```text
SHOPIFY_ADMIN_GRAPHQL
```

alongside non-Shopify kinds such as External HTTP and policy operations.

### R2 — remove Storefront Tool runtime

Delete the Storefront query execution port/transport/compiler/runtime path and update executable-registry logic to use the Admin path from COMMERCE-060.

Do not leave dead production branches that can still execute a Storefront Tool definition.

### R3 — remove Storefront authoring/discovery implementation replaced by Admin

Delete Storefront-specific Explore schema browser/query builder/argument-binding modules and server discovery branches only after proving COMMERCE-064 no longer imports them.

The `/explore` product surface remains; it is Admin-backed.

### R4 — pre-production data strategy is reset/reseed, not conversion

Do not build automatic Storefront->Admin query conversion. Existing development definitions using the removed kind may be deleted/reseeded according to the existing development workflow.

If test fixtures/seeds contain Storefront definitions, replace them with truthful Admin or non-Shopify equivalents as appropriate.

### R5 — preserve legitimate Shopify concepts

Do not mechanically remove every identifier/string containing `storefront`. Shopify Admin schema fields, external documentation wording, or unrelated storefront concepts remain when they serve a real capability.

Removal decisions must be tied specifically to the obsolete Moda Tool execution/Explore implementation.

### R6 — final publication/runtime no longer accepts Storefront Tool definitions

Canonical parsing/publication/execution tests must prove a `SHOPIFY_STOREFRONT_QUERY` definition is no longer accepted as a Commerce Tool definition.

No compatibility parser is retained.

## Work Items

- [ ] Remove Storefront execution kind from canonical Tool contracts.
- [ ] Remove Storefront execution port/transport/runtime and availability branches.
- [ ] Remove Storefront Tool compiler/publication-specific code.
- [ ] Remove obsolete Storefront Explore/query-builder modules after import verification.
- [ ] Remove obsolete Storefront schema artifact/provenance only if no legitimate consumer remains.
- [ ] Replace/remove Storefront Tool fixtures, seeds and tests.
- [ ] Add negative canonical-contract test proving removed kind is rejected.
- [ ] Verify Admin runtime/Explore/Request/Response regressions remain green.

## Interfaces / Contracts

Removes the repository-local `SHOPIFY_STOREFRONT_QUERY` Tool execution contract.

No replacement cross-service contract is introduced; `SHOPIFY_ADMIN_GRAPHQL` is already canonical.

## Dependencies

- `ARCH-021-COMMERCE-060`
- `ARCH-021-COMMERCE-064`

## Enables

None.

## Acceptance Criteria

- [ ] `SHOPIFY_STOREFRONT_QUERY` is absent from the canonical Commerce Tool execution union.
- [ ] Production DefinitionExecutor has no Storefront Tool branch.
- [ ] Executable-registry availability no longer recognizes Storefront Tool definitions.
- [ ] Explore Shopify is Admin-backed and has no Storefront mode.
- [ ] Storefront Tool builder/browser modules are removed when no longer imported.
- [ ] Obsolete Storefront Tool fixtures/tests are removed or replaced.
- [ ] A Storefront Tool definition fails canonical parsing/publication.
- [ ] Admin Tool runtime and Admin Explore authoring remain green.
- [ ] No backwards-compatibility adapter or migration is introduced.
- [ ] Legitimate unrelated Shopify Storefront concepts are not removed mechanically.

## Validation

- [ ] canonical Tool contract tests
- [ ] Admin execution tests
- [ ] Admin Explore/query-builder tests
- [ ] Shopify authoring UI tests
- [ ] repository search proving no remaining production `SHOPIFY_STOREFRONT_QUERY` branch
- [ ] targeted lint
- [ ] changed-file TypeScript diagnostics
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin later traversal/coordination work.

## Implementation Notes

Because this is a pre-production breaking simplification, prefer deletion over compatibility shims. If a Storefront artifact remains for a legitimate separate capability, document that evidence rather than deleting it merely by name.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.
