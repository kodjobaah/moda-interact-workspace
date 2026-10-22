---
id: ARCH-035-API-021
architecture_id: ARCH-035
title: Expose real WooCommerce promotional recovery-credit offers, selection and history
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 35
executor: developer
claimed_at: 2026-10-22T09:37:14Z
attempt: 1
depends_on: []
enables:
  - ARCH-035-WOOCOMMERCE-017
created: 2026-10-22
updated: 2026-10-22
---
# ARCH-035-API-021: Expose real WooCommerce promotional recovery-credit offers, selection and history

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- This task resumes **functional Promotions parity** without reactivating historical superseded `ARCH-035-API-006`.
- Existing Shopify reference: `moda-interact/app/services/promotions/promotion.service.ts` and `app/routes/app/promotions/route.tsx`.

## Objective

Provide authenticated Woo merchants with real promotional recovery-credit offers, active selection and history, and a safe promotion-selection command using existing Moda billing records.

## Context

`ARCH-035-WOOCOMMERCE-005` is Complete as a UI-only screen. `src/promotions/promotions-screen.js` defaults to `UNAVAILABLE` because no Woo merchant Promotions API exists. The earlier `API-006` contract was superseded when ARCH-035 became UI-only and remains historical; do not reopen it or mark it implemented.

## Scope

- Add API-owned merchant Promotions contract, GET and PUT routes, business service(s), route registration, OpenAPI specification and focused tests in `moda-interact-api`.
- Reuse `PromotionCampaign`, `PromotionCampaignTranslation`, `PromotionalCreditGrant`, `MerchantPromotionSelection`, `Shop` and `Subscription` from the existing database; **no schema migration** is authorized.
- Reuse the documented Shopify promotion eligibility, grant, lock and history semantics without importing the Shopify application authentication/runtime.
- Use existing Woo installation authentication and resolved tenant Shop, and the shared structured logger.

## Out of Scope

- WooCommerce coupon codes, discount selection, new promotions/campaign creation, billing-provider charges, Shopify API changes, credit allocation by the plugin, WordPress UI integration, additional tables, `_index.md` files.

## Requirements

1. Hosted endpoints: `GET /v1/merchant/promotions?offerPage=1&historyPage=1&locale=<supported-locale>` and `PUT /v1/merchant/promotions/selection`. Both require the **active authenticated Woo installation**, not a Shopify session or browser-supplied Shop ID. `offerPage` and `historyPage` are integers 1–1000; offer/history page size is 6. `locale` is an optional validated merchant **display** locale; missing/unsupported translations fall back safely without changing shop/customer language.
2. GET returns a validated, versioned, no-store JSON response:
   ```json
   {"schemaVersion":1,"revision":"opaque","offers":[],"offersPagination":{"page":1,"pageSize":6,"totalEntries":0,"totalPages":1},"selection":null,"history":{"entries":[],"page":1,"pageSize":6,"totalEntries":0,"totalPages":1}}
   ```
   Each `offers[]` item has `id`, `merchantTitle`, `merchantDescription`, `quantity`, `expiresAt`, `exhausted`, `previouslyClaimed`, `currentlySelected` and any explicit eligibility/denial state needed by the existing UI. `selection` when present has `campaignId`, `merchantTitle`, `remainingQuantity`, `expiresAt`, `locked`, plus authoritative reserved/committed state if displayed. Each `history.entries[]` item has `campaignId`, `campaignTitle`, `status`, `quantityGranted`, `committedQuantity`, `remainingQuantity`, `lastSelectedAt`, `expiresAt`. History status must follow established lifecycle values; it must not be reduced to invented labels by the API.
3. PUT accepts **only** `{ "campaignId": "opaque-id", "expectedRevision": "opaque" }` with bounded IDs/revision. It returns an authoritative `{schemaVersion:1,revision,selection}` on success. A stale revision or competing differing selection yields `409` with a stable error code; invalid input `400`; invalid/revoked installation `401`; ineligible, expired, closed, exhausted, mismatched plan/shop or locked different selection yields bounded denied/conflict responses. Do not leak other-shop records.
4. Implement concurrency-safe single-selection semantics using existing `MerchantPromotionSelection` uniqueness/version and grant keys. Repeated identical selection must **not** issue a second credit grant, reset quantity or bypass consumption/reservations. Only server-side eligible campaigns can be selected. The revision is derived from authoritative shop selection state and checked atomically; no client-generated credit state.
5. Effective quantity is `quantity - reservedQuantity - committedQuantity`; eligibility respects `GLOBAL`/`PLAN`/`SHOP` scope, Shop state, active plan, campaign active window and previously claimed/exhausted semantics, consistent with the existing Shopify service. Historical grants remain visible according to tenant ownership after expiry, even when they are not selectable.
6. Response validation and OpenAPI are owned by this API. Return dates in ISO-8601, numeric non-negative counts, stable `(createdAt DESC,id DESC)` history ordering, bounded Prisma selects, `Cache-Control: private, no-store` and logs through `@modainteract/moda-interact-shared/logging` without secrets/customer PII. Preserve existing Shopify promotion behaviours.

## Work Items

- [ ] Inspect Shopify `promotion.service.ts` and existing database model/constraint semantics; record any discovered incompatibility before implementation.
- [ ] Implement read endpoint with offers, locked selection, history and locale fallback.
- [ ] Implement concurrency-safe selected-campaign write, error mapping and idempotent retry.
- [ ] Add schema validators, OpenAPI and merchant route composition.
- [ ] Add comprehensive focused and integration tests; record exact evidence.

## Interfaces / Contracts

- API owner: `moda-interact-api`; canonical published interface is the new API OpenAPI file plus runtime request/response schemas. Woo plugin consumes this through server-side `ModaApiClient`, never browser-to-hosted requests.
- Existing schemas: `billing.PromotionCampaign`, `PromotionalCreditGrant`, `MerchantPromotionSelection`; no new cross-service queue contract.
- Consumer task: `ARCH-035-WOOCOMMERCE-017`; avoid a second Woo-specific credit accounting implementation.

## Dependencies

None. Existing ARCH-026/027 Woo installation/billing foundations are already recorded Complete; reverify schema/package pins when claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-017`.

## Acceptance Criteria

- [ ] A connected merchant sees only eligible current offers and its own current/history grants; localization falls back correctly.
- [ ] Two concurrent selection attempts, repeated identical requests and stale revision produce at most one valid grant/selection and no credit reset.
- [ ] Shop/plan mismatch, inactive shop/subscription, expired/closed/exhausted campaigns, no selection, bad input, unauthenticated/revoked installation and cross-shop requests have verified bounded outcomes.
- [ ] Grant reserved/committed counts and historical status remain intact; existing Shopify Promotions tests stay passing.
- [ ] Versioned contract, OpenAPI, shared structured logging, no-store response and no secrets/customer PII are verified.

## Validation

- [ ] Focused service/route and disposable PostgreSQL concurrency/tenant tests using repository-provided commands.
- [ ] Repository-declared typecheck/lint/build and relevant Shopify regression evidence where available.
- [ ] `git diff --check` plus launcher-resolved canonical parent/implementation task worktree and Completion Report evidence.

## Stop Condition

Set `status: review`, complete the report, return to `moda_architect` and STOP. Do not start the Woo consumer task.

## Implementation Notes

Prefer small route/contract/read/command modules and injected persistence/test seams. Do not copy Shopify app auth or reimplement promotional-credit accounting in the Woo plugin. If a contract field is inconsistent with the actual billing service, document it and return it to the architect; do not invent state.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-22T09:37:14Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

No Git worktree, branch, implementation commit, provider credentials, deployment or acceptance is created by this task definition.

### Unresolved Issues

None recorded at definition time; report concrete schema/contract gaps to the architect rather than broadening scope.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed. This is a new task definition, not an accepted implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed from implementation and test evidence.

### Follow-up

Architect acceptance required before enabling dependants.

## Developer Takeover Amendment — 2026-10-22

The developer explicitly invoked `/moda_developer_create ARCH-035-API-021` for this ready agent-owned task. Execution and completion ownership are transferred to the developer (`execution_mode: developer`, `completion_mode: developer`); logical ownership remains `assigned_agent: moda_api`, and task scope, dependencies, acceptance criteria, and validation requirements are unchanged. The canonical launcher will record the developer claim after worktree preparation and dependency verification.
