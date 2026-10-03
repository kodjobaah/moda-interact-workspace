---
id: ARCH-026-API-003
architecture_id: ARCH-026
title: Expose the authenticated Woo merchant bootstrap read model
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-API-002
  - ARCH-026-DATABASE-002
enables:
  - ARCH-026-WOOCOMMERCE-005
created: 2026-10-02
updated: 2026-10-02
---

# Expose the authenticated Woo merchant bootstrap read model

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Expose the first authenticated, database-backed merchant read model from `moda-interact-api` for the WooCommerce application.

The completed task must allow an already-connected WooCommerce plugin to authenticate through the accepted API-002 installation principal and load one bounded merchant bootstrap document containing the shared Moda `Shop` identity/lifecycle milestone, provider-neutral merchant international context and the current Commerce store-profile selection state.

The runtime is:

```text
Woo PHP plugin
    |
    | X-Moda-Installation-Id + Bearer credential
    v
GET /v1/merchant/bootstrap
    |
    v
API-002 WooInstallationAuthenticator
    |
    v
server-resolved shopId
    |
    +-- commerce.Shop
    `-- commerce.CommerceShopProfile + category identities
    |
    v
bounded merchant bootstrap JSON
```

This is a read-only capability. It MUST NOT complete onboarding, select a plan, mutate Store Category state, create billing/subscription state or introduce another merchant lifecycle source of truth.

## Context

API-002 establishes the reusable authenticated Woo installation principal:

```ts
{
  installationId: string;
  shopId: string;
  canonicalSiteUrl: string;
  credentialVersion: number;
}
```

and requires all tenant identity to be resolved server-side from the installation credential rather than caller-supplied `shopId`.

DATABASE-001 establishes the provider-neutral one-time onboarding milestone:

```text
commerce.Shop.onboardingCompleted
```

while retaining `shopify.ShopSettings.onboardingCompleted` temporarily for current Shopify compatibility. Woo merchant APIs must consume the shared `Shop` field and MUST NOT read or create `shopify.ShopSettings` merely to determine onboarding state.

DATABASE-002 establishes provider-neutral merchant international context on the same shared Shop:

```text
commerce.Shop.storeLocale
commerce.Shop.defaultLanguageTag
commerce.Shop.defaultTimeZone
commerce.Shop.defaultCountryCode
```

`storeLocale` preserves provider-native store locale identity and is deliberately not constrained by a Moda locale allowlist. `defaultLanguageTag` is a separate normalized Moda/BCP-47-compatible value when one has been established. Woo bootstrap reads MUST NOT fall back to `shopify.ShopSettings` for language, time zone or country.

The existing Commerce store-profile model is already shared tenant state:

```text
commerce.CommerceShopProfile
    shopId
    activeCategoryId
    pendingCategoryId
    pendingPromptRevisionId
    pendingSelectionGeneration
    pendingSelectedAt
```

with category identity supplied by:

```text
commerce.CommercePromptTemplateCategory
    id
    slug
    displayName
```

API-003 is intentionally read-only because Store Category selection/activation has existing non-trivial transactional semantics in the Shopify application. ARCH-026 must not duplicate that mutation logic inside `moda-interact-api` merely to demonstrate a write endpoint. The existing WOO connection/reconnect flow already proves the browser -> PHP -> hosted API -> PostgreSQL mutation path; this task establishes the first reusable merchant business read boundary.

## Scope

Modify only `moda-interact-api` files required for the authenticated bootstrap read model, runtime validation/OpenAPI documentation, focused tests and bounded documentation.

Expected implementation areas are conceptually:

```text
src/
  merchant/
    bootstrap/
      bootstrap-read.service.ts
      routes.ts
      schema.ts
openapi/
  merchant-bootstrap-v1.yaml

tests/
  ... focused authenticated bootstrap tests
```

Exact filenames may follow the accepted API-001/API-002 repository structure.

### Database dependency

API-003 consumes the accepted database schema already pinned by API-002.

Before implementation, verify the API repository's nested `database/` gitlink contains the accepted DATABASE-001 schema with:

```text
commerce.Shop.platform
commerce.Shop.onboardingCompleted
woocommerce.WooCommerceInstallation
```

Do not modify Prisma schema/migrations in this task.

If the accepted API-002 branch/main integration already advanced the nested database gitlink beyond DATABASE-001, preserve that newer architect-approved compatible commit rather than moving the gitlink backwards.

### Route

Expose exactly:

```text
GET /v1/merchant/bootstrap
```

The route requires the reusable API-002 Woo installation authenticator.

It MUST NOT accept tenant identity through query parameters, request body, custom `shopId` headers or URL path parameters.

Authenticated identity is exclusively:

```text
installation credentials
        ->
WooInstallationAuthenticator
        ->
principal.shopId
```

### Response contract

Return one strict versioned logical response:

```json
{
  "schemaVersion": 1,
  "shop": {
    "id": "<Shop.id>",
    "platform": "WOOCOMMERCE",
    "domain": "https://merchant.example",
    "onboardingCompleted": false,
    "installedAt": "2026-10-02T10:00:00.000Z"
  },
  "internationalContext": {
    "storeLocale": "pt_BR",
    "languageTag": "pt-BR",
    "timeZone": "America/Sao_Paulo",
    "countryCode": "BR"
  },
  "storeProfile": {
    "activeCategory": null,
    "pendingCategory": null,
    "pendingSelectionGeneration": 0,
    "pendingSelectedAt": null
  }
}
```

When a profile/category exists, category identity is bounded to:

```json
{
  "id": "...",
  "slug": "fashion",
  "displayName": "Fashion"
}
```

International-context fields are independently nullable. A valid `storeLocale` may be returned even when `languageTag` is null because provider-native locale support and Moda translation/language-tag coverage are separate concepts. API-003 must not normalize/rewrite the stored provider locale on read and must not reject a valid stored provider locale because it is absent from a translation catalogue.

The response MUST NOT expose:

- `shopifyShopId`;
- Shopify Session or ShopSettings state;
- installation credential/digest;
- billing/subscription rows;
- entitlement counters;
- customer/recovery/conversation data;
- prompt text or prompt revision IDs;
- provider secrets;
- internal audit/logging metadata.

`domain` is returned as the current canonical Moda Shop domain and must agree with the authenticated installation's canonical site identity. A mismatch is an integrity error, not a second tenant identity choice.

### Shop invariants

The read service MUST require the authenticated Shop to remain compatible with the API-002 principal:

```text
Shop.id               = principal.shopId
Shop.platform         = WOOCOMMERCE
Shop.shopifyShopId    = NULL
Shop.status           = ACTIVE
Shop.domain            = principal.canonicalSiteUrl
```

API-002 already authenticates these conditions for normal use; API-003 must not weaken or bypass that boundary. If an impossible mismatch is observed between the authenticated principal and the subsequently loaded read model, return a bounded server-side integrity failure rather than silently serving cross-tenant or stale data.

Do not fall back to lookup by `domain` when `shopId` loading fails.

### Onboarding milestone

Return:

```text
shop.onboardingCompleted
```

from `commerce.Shop.onboardingCompleted` only.

Do not:

- read `shopify.ShopSettings.onboardingCompleted`;
- create `ShopSettings` for Woo;
- infer onboarding completion from connection status;
- infer onboarding completion from subscription/billing state;
- write the onboarding flag in this task.

`false` means the merchant has not yet crossed Moda's one-time onboarding milestone. It does not mean the Woo installation is disconnected or unauthenticated.

### International context projection

Return international context only from shared `commerce.Shop` fields introduced by DATABASE-002:

```text
internationalContext.storeLocale  <- Shop.storeLocale
internationalContext.languageTag  <- Shop.defaultLanguageTag
internationalContext.timeZone     <- Shop.defaultTimeZone
internationalContext.countryCode  <- Shop.defaultCountryCode
```

Do not:

- query `shopify.ShopSettings.defaultLanguageTag/defaultTimeZone/defaultCountryCode`;
- create ShopSettings for Woo;
- maintain an API-owned locale allowlist;
- infer `storeLocale` from `defaultLanguageTag`;
- substitute English into durable/read state merely because Moda lacks translation coverage.

The endpoint may return nulls exactly as durable shared state records them. Validation/canonicalization belongs to the provider-owned writer, not this read model.

### Store profile projection

Load at most one `CommerceShopProfile` by the authenticated `shopId`.

If no profile exists, return the canonical empty profile projection:

```json
{
  "activeCategory": null,
  "pendingCategory": null,
  "pendingSelectionGeneration": 0,
  "pendingSelectedAt": null
}
```

Do not create a profile as a side effect of reading.

When `activeCategoryId` or `pendingCategoryId` exists, return only the referenced category's `id`, `slug`, and `displayName`.

Do not return default prompt content, prompt revisions, taxonomy mappings, Admin metadata or translation internals.

If the stored profile references an unavailable/deleted category in a way that contradicts database integrity, fail with a bounded integrity error rather than converting it to `null` and masking corruption.

### Read consistency

The route is read-only and should use a bounded number of database queries.

Prefer one Prisma query/select graph where practical. If repository/client limitations require multiple reads, ensure every query is scoped by the already-authenticated `shopId` and document the weak/read-committed consistency semantics rather than introducing a long-running transaction merely for display data.

No locks, writes or external provider calls are required.

### Caching

Do not add Redis or process-global merchant bootstrap caching in this task.

The bootstrap state is small and must reflect newly completed onboarding/profile transitions without an undocumented cache invalidation mechanism.

Normal HTTP/private response headers may prevent intermediary/browser caching of tenant data where appropriate.

### HTTP / browser boundary

This hosted endpoint remains server-to-server for the Woo plugin PHP client.

Do not enable permissive browser CORS and do not expose the installation credential to JavaScript.

WOO-005 must consume this route through a later privileged local WordPress REST façade rather than calling it directly from the browser.

### Logging and sensitive data

Use the Shared structured logger already established by API-001.

Do not log complete bootstrap responses or whole Shop/Profile objects.

Operational logs may contain bounded identifiers such as:

```text
installationId
shopId
route outcome
hasProfile
onboardingCompleted
duration
```

Do not log customer data, credentials or prompt text.

## Out of Scope

- Merchant bootstrap mutation endpoints.
- Completing onboarding.
- Creating `ACCOUNT_PENDING_ACTIVATION` as a stored state.
- Store Category selection/update/activation commands.
- Extracting Shopify Store Category mutation services into Shared.
- `shopify.ShopSettings` writes or reads, including legacy international-context fields.
- Billing/subscription projection.
- Pricing-plan selection.
- Feature/entitlement queries.
- Recovery configuration/listing.
- Usage reporting.
- Merchant Knowledge.
- Promotions.
- Products/coupons/discounts.
- CommerceAgent prompt/configuration mutation.
- WhatsApp.
- Cart/checkout/order event ingestion.
- Redis/BullMQ/Background.
- Woo installation connection/reconnect implementation; owned by API-002/WOO-003.
- Gateway/Render deployment.
- Browser-direct hosted API calls.
- A generic GraphQL merchant API.
- Pagination framework creation.

## Requirements

### R1 — Authentication is reused, not reimplemented

The route uses the accepted API-002 Woo installation authenticator and does not create another credential parser/verifier.

### R2 — Tenant identity is server-resolved

Every database read is scoped from `principal.shopId`; caller-supplied tenant identity cannot influence the Shop/profile selected.

### R3 — Shared onboarding milestone is authoritative

Woo onboarding state is read only from `commerce.Shop.onboardingCompleted`. `shopify.ShopSettings` is not queried or created.

### R4 — Shared international context is authoritative

Woo merchant bootstrap international context is projected only from DATABASE-002 shared Shop fields. The API has no fixed locale allowlist and does not require ShopSettings.

### R5 — Provider locale and translation coverage are separate

A valid stored provider-native locale is returned even when normalized language-tag/translation coverage is absent.

### R6 — Read means read

`GET /v1/merchant/bootstrap` performs zero database writes, profile creation, billing/provider operations or queue publication.

### R7 — Connection and account lifecycle remain separate

A valid installation principal can return `onboardingCompleted = false`; authenticated connection must not be presented as completed onboarding.

### R8 — Store profile projection is bounded

Only category identity required for merchant setup presentation is returned; prompt text/revisions and Admin-only category metadata remain private.

### R9 — Empty profile is not materialised

Missing `CommerceShopProfile` returns a deterministic empty read model without creating a row.

### R10 — Integrity mismatch fails closed

Authenticated principal/Shop identity mismatch or impossible referenced profile/category state is a bounded integrity failure, not a fallback lookup or silently-normalized success.

### R11 — No new cache correctness boundary

No Redis/process-global merchant bootstrap cache is introduced.

### R12 — Contract is PHP-consumable and versioned

A version-controlled OpenAPI 3.1 document describes the exact response/error contract that WOO-005's PHP/local REST layer will consume.

## Work Items

- [ ] Verify the API repository consumes an architect-accepted database gitlink containing DATABASE-001 and DATABASE-002.
- [ ] Add the strict merchant-bootstrap response/runtime schema.
- [ ] Implement a bounded read service scoped exclusively by authenticated `shopId`.
- [ ] Load the shared Shop lifecycle fields required by the bootstrap response.
- [ ] Project shared provider-neutral international context from Shop without a locale allowlist or ShopSettings fallback.
- [ ] Project optional active/pending Commerce Store Category identity without returning prompt internals.
- [ ] Return the deterministic empty store-profile shape without creating a database row.
- [ ] Implement `GET /v1/merchant/bootstrap` through the existing API-002 authenticator.
- [ ] Add fail-closed principal/Shop/profile integrity handling.
- [ ] Add private/no-permissive-CORS response behavior appropriate to PHP server-to-server use.
- [ ] Add `openapi/merchant-bootstrap-v1.yaml` matching runtime validators.
- [ ] Add focused unit/integration/security tests.
- [ ] Add bounded structured route logging without complete domain-object payloads.
- [ ] Document the contract and its deliberate read-only scope for WOO-005.

## Interfaces / Contracts

### Contract owner

`ARCH-026-API-003`

### Public API owner

`moda-interact-api`

### Consumer

Future `ARCH-026-WOOCOMMERCE-005` through PHP/server-side WordPress code.

### Authentication owner

`ARCH-026-API-002`

### Route

```text
GET /v1/merchant/bootstrap
```

### Authentication

```text
X-Moda-Installation-Id: <installationId>
Authorization: Bearer <raw installation credential>
```

The route receives the resolved principal from the reusable API-002 authenticator; it does not parse/verify credentials independently.

### Portable contract

```text
openapi/merchant-bootstrap-v1.yaml
```

### Database contract

Owners:

`ARCH-026-DATABASE-001`
`ARCH-026-DATABASE-002`

Read models:

```text
commerce.Shop
commerce.CommerceShopProfile
commerce.CommercePromptTemplateCategory
```

The task does not own or modify those models.

## Dependencies

- `ARCH-026-API-002`
- `ARCH-026-DATABASE-002`

Both tasks must be architect-accepted `complete` before API-003 becomes Ready.

API-003 must consume an accepted database gitlink containing both DATABASE-001 and DATABASE-002. Do not execute against an in-review database task branch.

## Enables

- `ARCH-026-WOOCOMMERCE-005`

WOO-005 may build the first real DB-backed merchant overview/setup presentation only after both WOO-004 and API-003 are architect-accepted Complete.

## Acceptance Criteria

- [ ] `GET /v1/merchant/bootstrap` requires valid API-002 Woo installation authentication.
- [ ] The route has no caller-controlled `shopId`, domain or tenant-selection input.
- [ ] Every durable read is scoped from `principal.shopId`.
- [ ] Shop platform/status/domain invariants are verified and mismatch fails closed.
- [ ] `onboardingCompleted` comes only from `commerce.Shop.onboardingCompleted`.
- [ ] `internationalContext` comes only from DATABASE-002 shared Shop fields.
- [ ] A provider-native `storeLocale` is not rejected because it lacks Moda translation coverage.
- [ ] The API does not infer/rewrite `storeLocale` from `languageTag`.
- [ ] The API does not query or create `shopify.ShopSettings` for Woo bootstrap reads, including international context.
- [ ] Connection/authentication state is not interpreted as onboarding completion.
- [ ] Missing `CommerceShopProfile` returns the deterministic empty profile projection with zero write.
- [ ] Existing active/pending category projection returns only category `id`, `slug`, and `displayName` plus bounded profile generation/timestamp state.
- [ ] Prompt text, prompt revision IDs, taxonomy mappings and Admin-only category metadata are not exposed.
- [ ] The route performs zero database writes, external provider calls, Redis/BullMQ operations or Background publication.
- [ ] The route does not expose `shopifyShopId`, installation credentials/digests, billing/subscription rows, entitlements, customer/recovery/conversation data or secrets.
- [ ] No permissive browser CORS is introduced.
- [ ] OpenAPI 3.1 and runtime request/response/error schemas agree.
- [ ] Structured logs contain bounded identifiers/outcomes only and not complete Shop/Profile response payloads.
- [ ] No billing, onboarding mutation, recovery, Merchant Knowledge, product/discount or event-ingress capability is introduced.

## Validation

Run the API repository's declared validation commands and record exact commands/results.

Required validation categories:

- [ ] clean dependency install from lockfile;
- [ ] required Node bootstrap before repository validation;
- [ ] Prisma generation from the accepted nested database gitlink;
- [ ] typecheck;
- [ ] lint;
- [ ] focused runtime-schema/OpenAPI contract tests;
- [ ] authentication middleware integration test proving the route reuses API-002 rather than accepting caller tenant identity;
- [ ] disposable PostgreSQL integration test for Woo Shop with `onboardingCompleted = false`;
- [ ] international-context projection tests covering WordPress-style locale such as `pt_BR`, regional BCP-47 language tag, time zone/country and nullable language tag;
- [ ] test proving an unrecognised-but-bounded provider locale is returned without a locale allowlist rejection;
- [ ] disposable PostgreSQL integration test for Woo Shop with `onboardingCompleted = true`;
- [ ] integration test proving no `ShopSettings` row is required for a Woo Shop;
- [ ] missing-profile test proving zero `CommerceShopProfile` insertion/update;
- [ ] active-category projection test;
- [ ] pending-category projection/generation test;
- [ ] integrity-mismatch tests for platform/domain/profile category state;
- [ ] test proving zero database mutation across successful bootstrap reads;
- [ ] sensitive-field exclusion tests;
- [ ] no-permissive-CORS/private-response test;
- [ ] structured-log bounded-data test;
- [ ] production build;
- [ ] `git diff --check`;
- [ ] clean task-worktree/branch evidence required by the task protocol.

No live WordPress/WooCommerce instance is required for API-003 validation; WOO-005/system validation owns the PHP/UI integration.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
        ->
set status: review
        ->
return control to moda_architect
        ->
STOP
```

Do not begin WOO-005.

## Implementation Notes

Keep this endpoint deliberately small. It establishes the first authenticated merchant-domain read boundary, not a generic API catalogue.

Do not duplicate the Shopify application's Store Category selection transaction inside `moda-interact-api`. A later architecture task can decide whether that mutation should be extracted to a reusable owner or implemented behind another provider-neutral service boundary.

Do not use the retained Shopify compatibility field as a fallback. ARCH-026 intentionally establishes `Shop.onboardingCompleted` as the cross-platform source that Woo consumes.

Prefer Prisma `select` clauses that make accidental expansion of the public response difficult.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- API-002 is complete and exposes the accepted reusable Woo installation authenticator.
- The accepted DATABASE-001 schema includes `Shop.platform` and `Shop.onboardingCompleted` while retaining the legacy Shopify onboarding field.
- The accepted DATABASE-002 schema includes shared Shop international-context fields while retaining legacy Shopify compatibility fields.
- WOO-005 will consume this route only through the PHP/server-side plugin boundary and will not receive the installation credential in browser code.

### Unresolved Issues

- Store Category mutation remains intentionally outside API-003 because the existing transactional owner is currently inside the Shopify application and should not be duplicated casually.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
