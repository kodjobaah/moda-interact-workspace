---
id: ARCH-036-API-004
architecture_id: ARCH-036
title: Read Woo offer settings independently and list provider-identifiable coupons
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

# ARCH-036-API-004 — Decouple settings GET and remove Moda-only coupon eligibility filters

## Architecture

- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Bounded follow-up to complete `ARCH-036-API-002`; no new coupon ownership or Save/CAS design.
- Owner: `moda_api`, repository `moda-interact-api`; coordinator: `moda_architect`.
- Portable definition only; not materialised or claimed.

## Observed defect

API logs repeatedly show `merchant.discount_offers.access.denied` with `reason=catalogue_not_current`. `GET /v1/merchant/discount-offers` currently calls `currentCatalogue()` and fails when Background has marked the catalogue `SYNC_REQUIRED`, `SYNCING`, `ERROR` or `UNAVAILABLE`. This blocks merchants from **reading the already saved offer mode**, even when it is `NONE` and no coupon browsing is needed. Recovery summary/policy GET still succeeds, so the misleading WooCommerce screen is caused by the discount-offer read gate, not a general connection failure.

## Objective

Return persisted merchant recovery-offer mode and selected Woo coupon IDs **regardless of catalogue readiness**. For the separately paginated catalogue, list provider-observed, identifiable/code-usable Woo coupons from a completed `CURRENT` scan **without Moda-imposed commercial validity rules**. WooCommerce—not API-004—decides whether a coupon is redeemable.

## Scope and invariants

- `GET /v1/merchant/discount-offers` must use the existing shop/installation authentication and provider ownership checks; read `ShopSettings`, the existing merchant `ShopifyDiscount.isAvailable` flags, effective Admin override and optional catalogue metadata without invoking `currentCatalogue()`.
- Missing `ShopifyDiscountCatalogue` is valid for configuration reads and must not be misrepresented as a successful empty coupon catalogue. Keep the existing stable response shape and revision semantics (revision is informational, **not a PUT precondition**).
- `GET /v1/merchant/discount-catalogue` **must still** require `CURRENT` plus a successful complete scan, with shop, Woo identity, current observed generation, true provider presence and safely deliverable coupon code. **Remove** API eligibility gates based on `providerStatus=ACTIVE`, `fixedSelectable` as a *commercial* decision, `startsAt`/`endsAt`, usage, amount and a hardcoded provider discount-type allowlist. A real `REMOVED` coupon must not be presented as currently existing. Preserve pagination/search filters and tenant safety. Coordinate with BACKGROUND-005's storage-safe Woo provider marker; do not assume arbitrary discount types fit `providerType VARCHAR(128)`.
- Preserve `PUT /v1/merchant/discount-offers` as agreed: Shop-row-locked, atomic full-set replacement, no catalogue-generation CAS, no provider-eligibility validation; merchant owns Woo `isAvailable`, mode and FIXED FK anchor. NONE and AI modes must be writable even if the provider catalogue is down, subject to existing request/tenant constraints.
- Do not change recovery-delay/follow-up policy or Admin override effective semantics; do not alter Shopify API behaviour. Woo catalogue responses must not imply redemption is guaranteed: Woo validates coupon acceptance at checkout. A coupon with missing/unusable code needs an explicit non-sendable representation, never a fabricated code or a silently shortened one.
- No new database model/migration, Background edits, new Woo REST provider calls, Shared package changes or `_index.md` changes.

## Required scenarios

1. **No catalogue yet:** saved `NONE` and zero selected IDs returned by settings GET; coupon listing returns `catalogue_not_current` rather than `items: []` success.
2. **Catalogue not ready:** GET saved mode/IDs under `SYNC_REQUIRED`, `SYNCING`, `ERROR` and `UNAVAILABLE`, including FIXED selections that are now ineligible.
3. **Current catalogue:** settings and list responses retain their existing successful contracts; list provider-observed Woo codes **even when unknown type, zero amount, expired, usage-exhausted or unusual restriction**; selected flags reflect persisted `isAvailable` values. The Admin override is reported accurately. Preserve an untruncated >255-character code.
4. **Independent Save:** switching to `NONE` or `AI_BEST_APPLICABLE` succeeds even when catalogue is unavailable; don't reintroduce the superseded CAS/eligibility checks from the API-002 Attempt 1 review.
5. **Security:** unauthorized, cross-shop, revoked installation and Shopify-principal calls stay rejected without disclosing coupon IDs or shop settings.
6. **No broadening:** settings reads don't fetch remote Woo coupons and don't silently change `ShopifyDiscountCatalogue.status` or any merchant state. Catalogue filtering still excludes cross-tenant, not-observed, confirmed-removed and technically non-sendable identities, **not** coupons disliked by Moda business-rule checks.

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
                  +-- CURRENT + complete last scan? -- yes --> observed Woo codes
                  '-- not CURRENT -------------------------> 503
```

## Acceptance criteria

- [ ] `GET /discount-offers` returns valid persisted NONE/FIXED/AI config independently of catalogue presence and status.
- [ ] `GET /discount-catalogue` continues to fail closed when not CURRENT; **all observed code-usable Woo coupons** (including unselected, expired, zero amount, unknown type and exhausted) remain listed when CURRENT. Confirmed removed/no-code items are not misleadingly presented as sendable.
- [ ] Existing authentication, isolation, override projection, full-set PUT and Woo merchant-owned `isAvailable` semantics remain unchanged; long coupon codes are not truncated and unknown type is not a failure.
- [ ] No new client-facing `expectedRevision` requirement or unnecessary user Refresh for a saved NONE configuration.

## Required validation

- [ ] Unit/route/contract tests for `GET` under missing/SYNC_REQUIRED/SYNCING/ERROR/UNAVAILABLE/CURRENT; expected response shape unchanged.
- [ ] Disposable PostgreSQL tests with persisted FIXED selection/anchor and Admin override, including concurrent Background status changes and failed read-grant cases; catalogue fixtures with unknown Woo types, zero amount, expired/exhausted, >255-character codes, confirmed removal, and Shopify lookalikes must prove Woo-only inclusive results and isolation.
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
