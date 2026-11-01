---
id: ARCH-026-API-005
architecture_id: ARCH-026
title: Read authenticated localized Woo Store Category options and profile
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-API-002
  - ARCH-026-API-003
enables:
  - ARCH-026-API-006
created: 2026-10-09
updated: 2026-10-16
---

# Read authenticated localized Woo Store Category options and profile

## Architecture

Architecture ID: `ARCH-026`.

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`.

Coordinator: `moda_architect`.

## Objective

Expose an authenticated, read-only Store Category catalogue and current shop-profile snapshot for connected WooCommerce merchants, consistent with Shopify Recovery Settings.

## Context

Shopify `listSelectableStoreCategories()` and `loadStoreProfile()` already read the canonical Commerce category/template/mapping records and current active/pending state. The Woo bootstrap API displays a small read-only category identity but does not expose selectable localized options, mapping IDs or prompt provenance. Do not duplicate taxonomy data or infer a category from Woo products.

## Scope

`moda-interact-api` only:

- Add `GET /v1/merchant/store-categories` using the accepted Woo installation principal authentication and existing Shop integrity checks.
- Return `schemaVersion: 1`, requested/resolved UI locale, eligible localized categories with optional mapping choices and current Shop active/pending category state, selected mapping IDs, `pendingSelectionGeneration`, pending-state information and provenance where available.
- Use the existing Commerce category translation fallback semantics, enabled category/template checks and ordering; add a versioned OpenAPI document and focused contract, service, route and PostgreSQL-read tests.
- Ensure `Cache-Control: no-store`, bounded queries, bounded locale input and Shared logger reuse where domain events genuinely add value.

## Out of Scope

- Category writes, prompt publication, category activation, adding taxonomy or schema/migrations.
- Mutating the Shop's store locale/language, onboarding or subscription on a GET.
- WordPress UI/REST handlers, Shopify-authentication changes, Gateway/Background modification.

## Requirements

- The bearer installation principal resolves the authoritative Shop; no `shopId` can be supplied or overridden by a query parameter.
- Only `WOOCOMMERCE`, active, unrevoked installation/Shop state can read its own profile. Preserve constant-time credential comparison and site URL binding.
- Selectable category requires an enabled category with a valid, enabled default prompt template and nonempty prompt text. Eligible taxonomy mapping has a valid condition key. Only bounded IDs, names, descriptions and mapping choices reach the merchant.
- Localize category/mapping names using the requested administrator UI locale and Shopify-equivalent published fallback. This must not rewrite `Shop.storeLocale`/`defaultLanguageTag` or restrict the store's provider-native locale.
- Preserve distinct `activeCategory`, `pendingCategory`, `pendingMappingIds`, `activeMappingIds`, pending-state/provenance and nonnegative generation, including the valid no-profile state.
- Missing/disabled catalogue entries do not fabricate data or silently assign a category; errors must not leak prompt text, credentials, or other tenants' state.

## Work Items

- [ ] Define and test the versioned localized category/profile read schema and OpenAPI contract.
- [ ] Implement authenticated read-only service using existing category, template, mapping, prompt and profile tables.
- [ ] Implement bounded API route and safe error mapping.
- [ ] Add focused route/service/contract and disposable PostgreSQL read tests.

## Interfaces / Contracts

- Producer/owner: `moda-interact-api`, versioned OpenAPI `GET /v1/merchant/store-categories`.
- Consumer: `ARCH-026-WOOCOMMERCE-008` PHP authenticated client and merchant Admin UI.
- Authentication owner: `ARCH-026-API-002` Woo installation authenticator; existing merchant bootstrap identity from `ARCH-026-API-003`.
- Data contract: existing Prisma `CommercePromptTemplateCategory`, default template, taxonomy mappings, `CommerceShopProfile`, per-shop prompt revisions/configuration. Shared package: `@modainteract/moda-interact-shared/commerce` for published reusable Commerce rendering/provenance semantics where required; no locally duplicated cross-service DTO type replaces the OpenAPI contract.
- This read response may be richer than API-003 bootstrap but **must not** change bootstrap v1 response shape.

## Dependencies

- `ARCH-026-API-002` — Complete.
- `ARCH-026-API-003` — Complete.

## Enables

- `ARCH-026-API-006`.

## Acceptance Criteria

- [ ] Authenticated Woo merchant can read the same selectable category identities, localized descriptions and mapping choices as Shopify for the equivalent locale and catalogue.
- [ ] An unselected Woo Shop receives generation zero and explicit null category state, without any writes.
- [ ] Existing active/pending states and selected mapping/provenance are accurately distinguished.
- [ ] Invalid/revoked/cross-tenant credentials cannot read another Shop's category/profile.
- [ ] Disabled or incomplete catalogue entries are not selectable; stable ordering and locale fallback are proven.
- [ ] Repeated GETs leave Shop, subscription, credits, credentials, profile and prompt state unchanged.

## Validation

- [ ] Run focused unit/route/OpenAPI tests and repository-declared typecheck/lint/build commands.
- [ ] Run focused disposable PostgreSQL read-model tests where test infrastructure is available.
- [ ] `git diff --check`; demonstrate canonical parent+implementation task worktree and start synchronization evidence in Completion Report.

## Stop Condition

After required work and validation, record results, set `status: review`, return Completion Report to `moda_architect` and STOP. Do not start API-006 or Woo work.

## Implementation Notes

Read the exact Shopify `store-category.server.ts` loader behaviour before writing implementation. The API cannot import Shopify-private server code; reuse canonical Prisma data and existing published Shared helpers rather than introducing a second taxonomy or mutable read side effect. The UI locale is independent of Woo store locale. Resolve Commerce environment using the approved deployment identity, not Shopify-specific runtime globals.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

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

Accepted — retrospective implementation-evidence reconciliation, 2026-10-16.

### Review Notes

The authenticated localized category/profile GET boundary is implemented, using the installation principal, validated locale, bounded response, canonical Commerce category/profile reads and registered API routing.

This is an explicit architecture-level retrospective closure based on the 2026-10-16 supplied code snapshot, **not** a reconstruction of an original task execution or CI run. The attached archive has no Git worktrees/commits or historical launcher packet, so mirrored-branch isolation, claim provenance, original attempts, historical test results and actual WordPress/HTTPS/provider execution cannot be independently certified here. Original `attempt: 0` and executor-owned Completion Report are preserved without manufacturing evidence. These provenance limitations do not establish process compliance. Terminal integrated Woo provider certification remains `ARCH-026-SYSTEM-TEST-001`.

### Reviewed Files

- `moda-interact-api/src/merchant/store-categories/routes.ts`
- `moda-interact-api/src/merchant/store-categories/store-categories-read.service.ts`
- `moda-interact-api/src/merchant/store-categories/catalogue-read.ts`
- `moda-interact-api/src/merchant/store-categories/profile-read.ts`
- `moda-interact-api/src/merchant/store-categories/schema.ts`
- `moda-interact-api/src/index.ts`

### Validation Reviewed

- `moda-interact-api/src/merchant/store-categories/routes.test.ts` (test present and inspected; not independently executed in this read-only archive)
- `moda-interact-api/src/merchant/store-categories/store-categories-read.service.test.ts` (test present and inspected; not independently executed in this read-only archive)
- `moda-interact-api/src/merchant/store-categories/store-categories-read.service.postgres.test.ts` (test present and inspected; not independently executed in this read-only archive)
- `moda-interact-api/src/merchant/store-categories/openapi-contract.test.ts` (test present and inspected; not independently executed in this read-only archive)
- Static cross-file wiring and source inspection: completed for this task's bounded implementation.
- No new API TypeScript, PHP unit, WordPress integration, PostgreSQL or live provider tests were executed as part of this reconciliation unless explicitly listed as PASS above.

### Architecture Conformance

Accepted for bounded code-level implementation reconciliation. Live/integrated runtime acceptance is reserved for terminal system-test evidence. No source-code change is authorised by this review.

### Follow-up

`ARCH-026-SYSTEM-TEST-001` — certify the integrated HTTPS callback, real Woo consent/read and credential/tenant/billing isolation. Recover missing Git/provenance records separately if full historical workflow certification is required; do not invent them.
