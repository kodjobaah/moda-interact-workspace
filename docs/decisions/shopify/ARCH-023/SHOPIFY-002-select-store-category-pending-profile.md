---
id: ARCH-023-SHOPIFY-002
architecture_id: ARCH-023
title: Select Store Category and persist pending Shop profile
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-SHARED-002
enables:
  - ARCH-023-SHOPIFY-003
created: 2026-09-29
updated: 2026-09-29
---

# Select Store Category and persist pending Shop profile

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Implement one reusable merchant Store Category selection lifecycle and expose it on both:

```text
existing onboarding page
existing Recovery Settings -> Store Profile section
```

A selection must pin the selected category's exact current canonical-English default template into one pending Shop prompt DRAFT and persist `CommerceShopProfile` pending state.

Selection never directly activates a category or publishes a prompt.

## Context

Initial onboarding selection and later post-onboarding category changes are the same durable operation and must not be implemented twice.

The existing first-install CTA already targets:

```text
/app/billing/select
```

That route must remain the Managed Pricing destination. The onboarding page now requires a valid pending category selection before its plan CTA can continue.

Later category changes occur on Recovery Settings and remain pending until Admin publishes the exact DRAFT.

## Scope

Primary authorized implementation surface:

```text
database                         # gitlink update only
package.json
package-lock.json

app/services/store-profile/store-category.server.ts
app/services/store-profile/store-category-selection.server.ts
app/services/store-profile/shopify-taxonomy-suggestion.server.ts
app/services/store-profile/store-category-localization.ts

app/components/onboarding/Onboarding.jsx

app/routes/app/recovery-settings/route.tsx
app/routes/app/recovery-settings/RecoverySettingsView.tsx
app/components/settings/StoreProfileSection.tsx

app/routes/app/store-profile/category/route.ts       # exact action endpoint

app/i18n/locales/*.json
scripts/validate-arch023-store-category-locales.mjs

tests/unit/store-category-selection.test.ts
tests/unit/shopify-taxonomy-suggestion.test.ts
tests/unit/store-profile-section.test.tsx
tests/unit/onboarding-store-category.test.tsx
tests/integration/store-category-selection.integration.test.ts
```

Use the repository's existing authenticated Shopify route/session/access helpers.

## Out of Scope

- publishing/activating the pending Shop prompt.
- subscription activation.
- Admin category/template CRUD.
- capability-local prompt authoring.
- Merchant Knowledge source CRUD.
- database-backed category translations.
- a new onboarding route.
- changing `/app/billing/select` destination semantics.
- a second Store Profile page/navigation item.

## Requirements

### R1 — adopt exact dependencies

Advance the `database` gitlink to accepted `ARCH-023-DATABASE-001`, adopt exact `ARCH-023-SHARED-002` package version, and regenerate Prisma Client.

Do not edit database submodule schema/migrations.

### R2 — exact category eligibility read model

A category is merchant-selectable only when:

```text
category.enabled = true
category.defaultTemplateId != null
defaultTemplate exists
defaultTemplate.enabled = true
defaultTemplate.categoryId = category.id
defaultTemplate.promptText.trim() != ""
category slug has source-controlled merchant localization keys
```

Order selectable categories:

```text
displayOrder ASC
id ASC
```

Return only:

```ts
{
  id,
  slug,
  localizedDisplayName,
  localizedDescription,
  defaultTemplate: {
    id,
    key,
    displayName,
    editVersion
  }
}
```

Do not return `promptText` to the browser unless the UI explicitly displays a read-only preview. The server transaction always re-reads the authoritative template on selection.

### R3 — source-controlled localization gate

Use exact merchant-facing keys:

```text
storeProfile.categories.<slug>.displayName
storeProfile.categories.<slug>.description
```

The English catalogue is the canonical source-controlled slug manifest:

```text
app/i18n/locales/en.json
```

A database category slug absent from those English keys is not selectable.

Create:

```text
scripts/validate-arch023-store-category-locales.mjs
```

It must derive Store Category slugs from matching English key pairs and require the same two keys for every derived slug in all 20 ARCH-023 supported locale catalogues.

Unexpected runtime missing key uses existing English catalogue fallback and emits a bounded diagnostic.

Do not create translation rows/queue jobs.

### R4 — exact Shopify taxonomy evidence query

Create a bounded suggestion adapter using the authenticated Shopify Admin GraphQL client.

Query exactly one deterministic page:

```graphql
query ModaStoreCategorySuggestionProducts {
  products(first: 250, sortKey: ID) {
    nodes {
      category {
        id
      }
    }
  }
}
```

Do not paginate beyond 250 in v1.

Ignore products with null category.

A taxonomy evidence read failure must not block category selection; continue with no taxonomy evidence and use the fallback in R5.

Do not persist product/category evidence.

### R5 — exact category suggestion scoring

Load current `CommerceStoreCategoryTaxonomyMapping` rows for selectable categories.

For every product taxonomy `category.id` returned by R4:

- find the mapping with exact `shopifyTaxonomyCategoryId`;
- add its positive `weight` to that mapped Moda category's score.

Repeated products in the same Shopify taxonomy category contribute repeatedly.

Choose:

```text
highest total score
then category.displayOrder ASC
then category.id ASC
```

If no evidence matches any mapping, choose the first selectable category by:

```text
displayOrder ASC, id ASC
```

Suggestion is advisory. Merchant can select any selectable category.

### R6 — one reusable selection action/service

Implement:

```ts
selectPendingStoreCategory({
  shopId,
  categoryId,
  expectedPendingSelectionGeneration,
})
```

The browser never supplies prompt/template ids.

Run in one transaction.

### R7 — exact selection transaction

1. lock the Shop row for `shopId`;
2. load/create `CommerceShopProfile`;
3. require:
   ```text
   profile.pendingSelectionGeneration == expectedPendingSelectionGeneration
   ```
   on update; initial absent profile expects generation `0`;
4. re-read selected category + default template and re-validate R2 eligibility;
5. resolve the unique Shop prompt lineage:
   ```text
   scope = SHOP
   shopId = exact shop
   ```
6. if more than one lineage exists -> configuration conflict;
7. create lineage if absent;
8. resolve pending DRAFT:
   - if `profile.pendingPromptRevisionId` exists, load that exact revision and require same Shop lineage + `status=DRAFT`;
   - if no pending pointer, require there is no other DRAFT on the lineage; if an unrelated DRAFT exists, fail conflict rather than overwrite it;
   - otherwise create next revision number as one DRAFT;
9. write exact DRAFT content/provenance:
   ```text
   promptText                = exact current defaultTemplate.promptText
   sourceTemplateId          = defaultTemplate.id
   sourceTemplateEditVersion = defaultTemplate.editVersion
   ```
10. for an existing pending DRAFT, increment its `editVersion` by one;
11. write profile:
   ```text
   pendingCategoryId          = category.id
   pendingPromptRevisionId    = draft.id
   pendingSelectedAt          = now
   pendingSelectionGeneration = previous + 1
   ```
12. leave:
   ```text
   activeCategoryId
   activeCategoryActivatedAt
   CommerceAgentConfiguration.activePromptRevisionId
   ```
   unchanged;
13. commit.

Do not publish the DRAFT.

### R8 — repeat selection behavior

Selecting the same category again is allowed and is still a new explicit selection:

```text
pendingSelectionGeneration += 1
pendingSelectedAt = now
```

The exact current default template snapshot is re-pinned into the same pending DRAFT.

A stale `expectedPendingSelectionGeneration` rejects with conflict.

### R9 — onboarding UI

Modify the existing `Onboarding.jsx`; do not create a second onboarding route.

The page loads:

```text
selectable categories
current pending profile selection
taxonomy-based suggestion
merchant UI locale
```

Selection precedence:

```text
persisted pending category if still selectable
else taxonomy suggestion
else first selectable category
```

The merchant may change it.

Before navigation to `/app/billing/select`, persist the currently selected category through R6.

Both existing plan CTAs must use this behavior.

If no selectable category exists:

```text
disable Choose Plan
show bounded configuration unavailable message
```

Do not navigate to Shopify Managed Pricing without successful pending persistence.

### R10 — later Store Profile UI

Add a `Store Profile` section to the existing Recovery Settings page.

Show:

```text
active category localized label/description, if any
pending category localized label/description, if any
pending state indicator
template provenance metadata (displayName/key + edit version; never prompt text required)
Change category control
```

Submitting another category uses the same R6 service/action.

The currently active category and active Shop prompt remain effective until Admin publication.

### R11 — language behavior

Merchant-facing category labels use the current merchant UI locale/catalogue.

Prompt text copied into the DRAFT is always canonical English from:

```text
CommercePromptTemplate.promptText
```

Never translate template prompt text.

### R12 — no activation authority

This task must not inspect Subscription to decide whether a pending category becomes active.

It only persists pending selection.

`ShopSettings.onboardingCompleted` is not activation authority.

### R13 — ARCH-023 merchant localization foundation

In the same locale-catalogue change, add the exact key families required later by Merchant Knowledge UI for every Shared C3 key:

```text
merchantKnowledge.purposes.<PURPOSE_KEY>.label
merchantKnowledge.dataFormats.<DATA_FORMAT_KEY>.label
```

Required Purpose keys:

```text
COMPANY_INFORMATION
CUSTOMER_SUPPORT
POLICIES
FAQ
PRODUCT_INFORMATION
SHIPPING_AND_DELIVERY
PRICING
```

Required Data Format keys:

```text
WEB_PAGE
CSV
XLSX
```

All 20 supported locale files must contain every key.

Human-readable translations should follow the existing catalogue language conventions. This task fixes key identity/presence, not translation prose style.

Extend the validator to require these exact keys in all 20 catalogues.

### R14 — tests

Prove:

```text
category without valid default template excluded
slug missing from English localization manifest excluded
locale validator catches missing category/knowledge keys
taxonomy query is bounded to first 250 sorted by ID
weighted scoring + tie-break deterministic
taxonomy failure uses fallback
pending selection creates one Shop prompt lineage + one DRAFT
same pending DRAFT updated on category reselection
unrelated existing DRAFT blocks selection rather than being overwritten
stale selection generation rejects
active category/prompt pointer never changes
onboarding restores pending choice
onboarding persists before /app/billing/select
later Recovery Settings change uses same service
promptText copied exactly in canonical English
```

## Work Items

- [ ] Adopt database/Shared revisions.
- [ ] Add category eligibility/localization read model.
- [ ] Add locale catalogue keys + validator.
- [ ] Add bounded Shopify taxonomy suggestion adapter.
- [ ] Implement one transactional pending-category selection service.
- [ ] Integrate selection into existing onboarding CTAs.
- [ ] Add Store Profile section to Recovery Settings.
- [ ] Add route/action and focused tests.

## Interfaces / Contracts

Consumes ARCH-023 database models and Shared locale contract.

Writes:

```text
CommerceShopProfile pending fields
CommerceAgentPrompt
CommerceAgentPromptRevision DRAFT
```

Produces no queue/event.

## Dependencies

- `ARCH-023-DATABASE-001`
- `ARCH-023-SHARED-002`

Admin Store Category authoring may be implemented in parallel against the same database contract.

## Enables

- `ARCH-023-SHOPIFY-003`

## Acceptance Criteria

- [ ] Initial and later category selection use one service/transaction.
- [ ] Selection pins exact template text/editVersion into one pending Shop DRAFT.
- [ ] No selection directly changes active category/prompt.
- [ ] Taxonomy suggestion is bounded, deterministic and advisory.
- [ ] Existing onboarding route structure and `/app/billing/select` destination are preserved.
- [ ] Category and Merchant Knowledge localization keys exist across all 20 catalogues.
- [ ] No database translation lifecycle exists.

## Validation

- [ ] focused service/action/component tests
- [ ] locale-catalogue validator
- [ ] existing onboarding and Recovery Settings regressions
- [ ] `npm run typecheck`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin SHOPIFY-003.

## Implementation Notes

The Product GraphQL category field is Shopify Standard Product Taxonomy identity. Do not attempt to map product titles/types heuristically when `category.id` is absent.

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
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
