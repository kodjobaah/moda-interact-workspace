---
id: ARCH-036-API-004
architecture_id: ARCH-036
title: Read Woo merchant offer settings independently of catalogue readiness
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-API-002"]
enables: ["ARCH-036-WOOCOMMERCE-004"]
created: 2026-10-15
updated: 2026-10-15
---

# ARCH-036-API-004 — Decouple offer-settings GET from coupon readiness

## Architecture

- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Bounded follow-up to complete `ARCH-036-API-002`; no new coupon ownership or Save/CAS design.
- Owner: `moda_api`, repository `moda-interact-api`; coordinator: `moda_architect`.
- Portable definition only; not materialised or claimed.

## Observed defect

API logs repeatedly show `merchant.discount_offers.access.denied` with `reason=catalogue_not_current`. `GET /v1/merchant/discount-offers` currently calls `currentCatalogue()` and fails when Background has marked the catalogue `SYNC_REQUIRED`, `SYNCING`, `ERROR` or `UNAVAILABLE`. This blocks merchants from **reading the already saved offer mode**, even when it is `NONE` and no coupon browsing is needed. Recovery summary/policy GET still succeeds, so the misleading WooCommerce screen is caused by the discount-offer read gate, not a general connection failure.

## Objective

Return the merchant's persisted recovery-offer mode and Woo coupon selection IDs to the authenticated shop **regardless of catalogue readiness**, while keeping the separately paginated selectable coupon list strictly gated by a completed `CURRENT` synchronisation.

## Scope and invariants

- `GET /v1/merchant/discount-offers` must use the existing shop/installation authentication and provider ownership checks; read `ShopSettings`, the existing merchant `ShopifyDiscount.isAvailable` flags, effective Admin override and optional catalogue metadata without invoking `currentCatalogue()`.
- Missing `ShopifyDiscountCatalogue` is valid for configuration reads and must not be misrepresented as a successful empty coupon catalogue. Keep the existing stable response shape and revision semantics (revision is informational, **not a PUT precondition**).
- `GET /v1/merchant/discount-catalogue` **must still** require `CURRENT` plus a successful completed scan and still filter selectable coupons by supported/current provider facts. Preserve pagination/search filters and tenant safety.
- Preserve `PUT /v1/merchant/discount-offers` as agreed: Shop-row-locked, atomic full-set replacement, no catalogue-generation CAS, no provider-eligibility validation; merchant owns Woo `isAvailable`, mode and FIXED FK anchor. NONE and AI modes must be writable even if the provider catalogue is down, subject to existing request/tenant constraints.
- Do not change recovery-delay/follow-up policy or Admin override effective semantics; do not alter Shopify API behaviour.
- No new database model/migration, Background edits, new Woo REST provider calls, Shared package changes or `_index.md` changes.

## Required scenarios

1. **No catalogue yet:** saved `NONE` and zero selected IDs returned by settings GET; coupon listing returns `catalogue_not_current` rather than `items: []` success.
2. **Catalogue not ready:** GET saved mode/IDs under `SYNC_REQUIRED`, `SYNCING`, `ERROR` and `UNAVAILABLE`, including FIXED selections that are now ineligible.
3. **Current catalogue:** settings and list responses retain their existing successful contracts; selected Woo coupon flags reflect actual persisted `isAvailable` values and active Admin override is reported accurately.
4. **Independent Save:** switching to `NONE` or `AI_BEST_APPLICABLE` succeeds even when catalogue is unavailable; don't reintroduce the superseded CAS/eligibility checks from the API-002 Attempt 1 review.
5. **Security:** unauthorized, cross-shop, revoked installation and Shopify-principal calls stay rejected without disclosing coupon IDs or shop settings.
6. **No broadening:** settings reads don't fetch remote Woo coupons and don't silently change `ShopifyDiscountCatalogue.status` or any merchant state.

## ASCII interaction

```text
Woo merchant UI
      |
      +-- GET /v1/merchant/discount-offers
      |           |
      |           +-- authenticated Shop + saved ShopSettings
      |           +-- selected Woo isAvailable IDs / Admin override
      |           '-- 200 even if coupon catalogue ERROR/missing
      |
      '-- GET /v1/merchant/discount-catalogue
                  |
                  +-- CURRENT + lastSuccessfulSyncAt? -- yes --> items
                  '-- not CURRENT -------------------------> 503
```

## Acceptance criteria

- [ ] `GET /discount-offers` returns valid persisted NONE/FIXED/AI config independently of catalogue presence and status.
- [ ] `GET /discount-catalogue` continues to fail closed when catalogue not CURRENT; unselected ACTIVE rows remain listed when CURRENT.
- [ ] Existing authentication, isolation, override projection, full-set PUT and `isAvailable` semantics remain unchanged.
- [ ] No new client-facing `expectedRevision` requirement or unnecessary user Refresh for a saved NONE configuration.

## Required validation

- [ ] Unit/route/contract tests for `GET` under missing/SYNC_REQUIRED/SYNCING/ERROR/UNAVAILABLE/CURRENT; expected response shape unchanged.
- [ ] Disposable PostgreSQL tests with persisted FIXED selection/anchor and Admin override, including concurrent Background status changes and failed read-grant cases.
- [ ] Negative tenant/authentication and Shopify-isolation regression tests; existing PUT concurrency tests remain passing.
- [ ] Typecheck, lint, full unit suite, build, PostgreSQL integration and `git diff --check`. List results and known baseline issues exactly.

## Stop condition

Return Completion Report in `review` status to `moda_architect` after implementation/validation. Do not start WOOCOMMERCE-004 automatically; do not modify `_index.md`.

## Completion Report

### Status

Not started; portable definition only.

### Files Changed

None in application source.

### Work Completed

None.

### Validation Results

Not run by implementation executor.

### Deviations

None recorded.

### Unresolved Issues

None yet.

## Architect Review

### Review Status

Pending implementation evidence.
