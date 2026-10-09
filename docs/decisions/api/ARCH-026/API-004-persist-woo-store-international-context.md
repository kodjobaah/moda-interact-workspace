---
id: ARCH-026-API-004
architecture_id: ARCH-026
title: Persist authenticated WooCommerce store international context
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
  - ARCH-026-DATABASE-002
enables:
  - ARCH-026-WOOCOMMERCE-007
created: 2026-10-09
updated: 2026-10-09
---

# Persist authenticated WooCommerce store international context

## Architecture

Architecture ID: `ARCH-026`

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator: `moda_architect`.

## Objective

Provide a bounded, authenticated, idempotent WooCommerce store-context command that writes the four existing provider-neutral `commerce.Shop` international-context columns without coupling the write to installation connection, Free-plan activation or category selection.

## Context

LocalWP integration has proven Connect, reconnect, credential rotation and lifetime Free credit preservation. The existing Woo connection request sends site identity, attempt identity and proof only. `InitialWooFreeActivationService`/`WooInstallationConnectionService` create the shared Shop without international context. `GET /v1/merchant/bootstrap` already reads `Shop.storeLocale`, `Shop.defaultLanguageTag`, `Shop.defaultTimeZone` and `Shop.defaultCountryCode`, and correctly returns null for unset fields. No writer exists for WooCommerce in the inspected 2026-10-08 23:55:59 snapshot.

ARCH-026 deliberately separates WordPress administrator UI locale from merchant/store locale and requires IANA time zones when present. A new context command must not modify the proven connection/Free subscription transaction.

## Scope

`moda-interact-api` only:

- Add a merchant-facing, installation-authenticated `PUT /v1/merchant/store-context` handler/service and a dedicated versioned OpenAPI contract.
- Validate and write only four international-context fields on the authenticated `commerce.Shop`.
- Add bounded structured outcome logging through the existing `@modainteract/moda-interact-shared/logging` logger.
- Add targeted unit, route-contract and PostgreSQL integration coverage.

## Out of Scope

- Prisma schema changes, migrations, subscription or credit changes.
- Shopify `ShopSettings` reads/writes or Shopify tenant updates.
- Connection proof, credential issuance/rotation, or modified Connect request fields.
- Commerce category picker, `CommerceShopProfile` creation or category activation.
- User-controlled Shop ID, WordPress Admin browser authentication, or Woo PHP/React code.
- A generic multi-provider settings update API or a new public gateway route.

## Requirements

1. **Authentication and tenant isolation:** Reuse `WooInstallationAuthenticator` and its authoritative `shopId` and `canonicalSiteUrl`. A missing, expired or revoked installation credential is not authorised. Before writing, require the Shop to be active, `platform = WOOCOMMERCE`, `shopifyShopId = null`, and `domain = principal.canonicalSiteUrl`; do not accept a caller-supplied `shopId` or site URL in the payload.
2. **Canonical command:** `PUT /v1/merchant/store-context`, request body exactly:

   ```json
   {
     "schemaVersion": 1,
     "storeLocale": "en_GB",
     "languageTag": "en-GB",
     "timeZone": "Europe/London",
     "countryCode": "GB"
   }
   ```

   Each of the four context values is independently nullable. Strictly reject unknown/missing keys, arrays, malformed JSON, query strings, unexpected bodies/media types and oversized requests. A valid context update returns `204 No Content`; `GET /v1/merchant/bootstrap` remains unchanged, read-only and the authoritative verification read.
3. **Provider-native locale:** A non-null `storeLocale` is a nonempty bounded WordPress/WooCommerce locale identity (maximum 128 characters), preserved verbatim without a fixed Moda supported-locale/translation allowlist. Avoid control characters and invalid/unbounded text. Never use the WordPress administrator's user locale as store identity.
4. **Normalized values:** A non-null `languageTag` must be a well-formed bounded BCP-47-compatible value (maximum 64 characters); do not derive it from the stored `storeLocale` on the API. A non-null `timeZone` must be a valid named IANA time zone (maximum 255 characters); a bare UTC offset is not an IANA location identifier and must be rejected. A non-null `countryCode` is uppercase ISO-3166 alpha-2 form (`^[A-Z]{2}$`), matching the existing Shop database constraint. Invalid values fail without any database mutation.
5. **Write semantics:** Treat the payload as a complete current snapshot: explicit nulls clear outdated values. Persist the four fields in one atomic Shop update, scoped to the authenticated Woo shop. Repeated identical `PUT`s are semantically idempotent and cannot create new Shop, installation, `Subscription`, `BillingPlan`, entitlement counter or category state. No network call or redundant interactive transaction is needed for this single-record update.
6. **Failure handling:** Return bounded 400 for invalid input, 401 for authentication failures, 409 for an inconsistent/stale tenant, and 500 for unexpected persistence errors without disclosing secrets, SQL, raw payloads, or sensitive stack traces. The write does not invalidate an already-connected merchant installation.
7. **Observability:** Emit `merchant.store_context.sync` with shop/installation identifiers and success outcome, or `merchant.store_context.sync.failed` with bounded reason. Reuse the existing structured logger; never log request values, credentials or Authorization headers. Ordinary HTTP metrics belong to the existing instrumentation.
8. **Contract and gateway:** `openapi/merchant-store-context-v1.yaml` is the HTTP source of truth for the plugin/PHP consumer. This is a new endpoint on the already-approved API host; the gateway routes `API_PUBLIC_HOST/*` to the API, so no gateway configuration change is required on the inspected topology.

## Work Items

- [ ] Add a validated request schema/type and the versioned OpenAPI contract.
- [ ] Implement a single-tenant store-context writer using the authenticated installation principal.
- [ ] Register the bounded HTTP handler, response mapping and shared-logger semantic events.
- [ ] Verify read-after-write via the existing `MerchantBootstrapReadService` without changing the read API.
- [ ] Add negative authentication/tenant/integrity/bounds coverage and idempotency/nullable-field coverage.
- [ ] Add a disposable PostgreSQL integration test confirming only the four Shop fields change.

## Interfaces / Contracts

**Canonical HTTP owner:** `moda_api`, via `openapi/merchant-store-context-v1.yaml`, version `v1`.

**Producer/consumer:** WooCommerce PHP plugin (`ARCH-026-WOOCOMMERCE-007`) produces the authenticated store snapshot; the hosted API validates and writes it. PHP consumes the versioned OpenAPI contract, not an independently invented duplicate.

**Read-after-write:** `GET /v1/merchant/bootstrap` remains the established API-003 projection, exposing exactly the persisted `Shop` fields.

**Database owner:** DATABASE-002's provider-neutral `commerce.Shop` columns. No new schema needed.

## Dependencies

- `ARCH-026-API-002` — accepted installation-principal authentication.
- `ARCH-026-API-003` — accepted merchant bootstrap read model.
- `ARCH-026-DATABASE-002` — accepted Shop international-context columns/constraints.

## Enables

- `ARCH-026-WOOCOMMERCE-007`.

## Acceptance Criteria

- [ ] A connected WooCommerce installation can update its own four Shop context fields; a different, revoked or invalid installation cannot update the Shop.
- [ ] Empty/unknown/invalid context values return a bounded failure with zero writes; valid nulls round-trip as null.
- [ ] Valid WordPress-native locale identities are preserved exactly without a fixed locale allowlist.
- [ ] The time zone is an actual named IANA identifier when non-null; a UTC-offset-only input cannot be misrepresented as such.
- [ ] Repeating the same update does not allocate credits, create subscription/installation/category state or rotate credentials.
- [ ] Existing connection/reconnect and Free activation behaviour remains unchanged; the bootstrap GET remains read-only.
- [ ] The API contract, validation logic and test cases agree; no secrets or raw context payloads are logged.

## Validation

- [ ] `npm run typecheck`
- [ ] `npm run lint`
- [ ] Focused API route/service/contract tests using the repository's declared test tooling.
- [ ] `npm run test:integration` against its disposable PostgreSQL environment (or explicitly report a prerequisite gap).
- [ ] `git diff --check` and a targeted proof that no files outside API ownership changed except the assigned task's Completion Report.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation are satisfied, set the task to `review`, complete the Completion Report, return to `moda_architect` and STOP. Do not implement WooCommerce PHP, category selection, or a dependent task.

## Implementation Notes

The caller is already authenticated by the accepted `WooInstallationAuthenticator` and may be reading a WordPress site that is not public on LocalWP. Do not require another HMAC site-proof or place an HTTP callback inside the Shop update. The command should work for an **already connected** Woo installation, without forcing credential rotation/reconnection. Preserve the pre-production nature of this change but do not weaken the production public-mode security boundary.

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

Pending.

### Review Notes

Pending implementation review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Await repository implementation and Completion Report.
