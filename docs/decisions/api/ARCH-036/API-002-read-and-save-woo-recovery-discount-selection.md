---
id: ARCH-036-API-002
architecture_id: ARCH-036
title: "Read and save Woo coupon selections using existing discount flags"
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-BACKGROUND-001"]
enables: ["ARCH-036-WOOCOMMERCE-003", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-14
---

# ARCH-036-API-002 — Read and persist Woo merchant coupon selections

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Provide shop-authorised paginated **active** Woo coupon listing and revision-guarded multi-checkbox selection using existing `ShopifyDiscount.isAvailable` and the existing `ShopSettings.fixedShopifyDiscountId` FK. No database migration.

## Context


For **WooCommerce records only**, `isAvailable=true` means selected by the merchant; for Shopify it retains its existing provider-availability meaning. Provider status, fixedSelectable, dates and catalogue freshness decide which coupons appear. The API reads the existing catalogue maintained by BACKGROUND-001 and writes selected flags plus the **real internal** `ShopSettings.fixedShopifyDiscountId` anchor to satisfy unchanged FIXED SQL checks. The API does **not** retrieve Woo coupon pages from the provider, determine which coupon to offer, or prove checkout eligibility. Neither offer execution nor CommerceAgent is in this session.

## Scope

Implement versioned paginated GET `/v1/merchant/discount-catalogue` and GET/PUT `/v1/merchant/discount-offers` on existing models. Use authenticated Woo Shop, Shop-row lock, and an optimistic revision encompassing `ShopSettings.updatedAt` **and** the catalogue generation/status. Revalidate Shop/coupon eligibility under the transaction lock so a concurrent scan or provider-state change cannot silently overwrite a draft; atomically update **one Woo Shop's flags, mode and anchor**. Allow 1–50 selected coupon row IDs in FIXED; the bound is an API validation rule, not new DDL.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements


- Catalogue GET lists all shop-scoped CURRENT, ACTIVE, fixedSelectable, in-date, supported positive-value coupons with bounded stable pagination/search, **including unchecked** rows; checked state comes from `isAvailable`. A missing, stale or non-current catalogue is not an empty successful catalogue.
- Authenticated Woo installation uses the existing PHP privileged WordPress REST boundary; no browser-to-Moda hosted direct call and no new Shared data-schema dependency. Define the endpoint's own versioned OpenAPI contract in `moda-interact-api`.
- PUT validates complete selected same-Shop internal row IDs (1–50 for FIXED), rejects unsupported/expired/foreign/stale IDs, and performs a Shop-locked optimistic-revision transaction across Woo checkbox flags, catalogue generation/status and ShopSettings mode/FK. All writes are constrained to `Shop.platform=WOOCOMMERCE`. Only the merchant-selection API may set Woo selected flags through a manual Save; provider sync never auto-selects and cannot turn a stale catalogue into an apparently successful Save.
- For FIXED use one **deterministically chosen real selected same-Shop `ShopifyDiscount.id`** (e.g. minimum internal ID) as existing `fixedShopifyDiscountId` FK compatibility anchor; it is not the customer-facing coupon choice. For NONE/AI clear the anchor as the current SQL CHECK requires; dormant selected flags may be retained. Shopify's single-FK setting and Admin override are unchanged. A last-coupon removal while FIXED is rejected unless mode changes.
- Idempotent identical saves, conflicting concurrent saves (409), and denied/invalid/revoked installation (4xx/503) must preserve merchant edits and never partially update rows. A policy save is not coupon applicability proof.
- No additional HTTP proxy/proof API, Shared schema, Prisma migration, customer-sensitive data, or cross-tenant selection write.

## Work Items

- [ ] Implement shop-authorised CURRENT active-coupon catalogue read with cursor/page metadata and selected flags.
- [ ] Implement one transactional Woo-only full-set CAS Save updating `isAvailable`, mode and real-row FK anchor under Shop lock, with freshness/generation protection against concurrent catalogue changes.
- [ ] Test conflicting writes, concurrent scan/save, repeated calls, mode switching, last-coupon removal, invalid/foreign/unavailable IDs, Shopify isolation and unchanged delay/follow-up.
- [ ] Verify legacy SQL FIXED FK/CHECK constraints and existing Shopify API behavior using a migrated disposable PostgreSQL database.

## Interfaces / Contracts


API-owned versioned GET `/v1/merchant/discount-catalogue` and GET/PUT `/v1/merchant/discount-offers`, authenticated Woo installation and existing WordPress REST facade. Existing `ShopSettings` and `ShopifyDiscount` only. **No new Shared contract or provider REST read/proof endpoint.**

## Dependencies


- `ARCH-036-BACKGROUND-001` — complete, current normalized coupons needed for listing and selection.

## Enables


- `ARCH-036-WOOCOMMERCE-003`
- `ARCH-036-BACKGROUND-003`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Multiple Woo checkboxes persist via existing discount flags across pages/reloads.
- [ ] `FIXED` save satisfies existing SQL checks using a real referenced selected discount ID; no fake FK or new schema.
- [ ] NONE/AI clear the compatibility FIXED anchor and correctly persist the requested configuration; no outbound offer behaviour is implemented or asserted.
- [ ] Stale/foreign/inactive/unselectable writes are rejected atomically.
- [ ] Merchant conflict state and effective Admin override remain correct; Shopify settings untouched.

## Validation

- [ ] Focused API contract/route/unit tests and OpenAPI checks.
- [ ] Disposable PostgreSQL existing-constraint, shop lock, CAS and foreign-shop cases; verify no schema migration needed.
- [ ] Declared API typecheck/lint/test/build and `git diff --check`.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes


Implement only Woo merchant-facing catalogue read and selection persistence. Background owns the provider coupon-list sync; send-time proof and CommerceAgent are outside this session. Preserve current policy delay/follow-up and admin override without introducing false discount eligibility claims. Use the API repository's own contract tests and real existing-schema PostgreSQL concurrency/FK checks.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task not claimed.

### Deviations

None.

### Assumptions

The implementation executor will verify local checkout, dependencies and available toolchain at claim time.

### Unresolved Issues

None recorded by an implementation executor.

### Architectural Concerns

Report schema, cross-service or provider-proof deviations to `moda_architect` instead of silently expanding scope.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only, not implementation acceptance.

### Reviewed Files

Current 12 October 2026 source snapshot used to define ownership; implementation not yet reviewed.

### Validation Reviewed

None from this task.

### Architecture Conformance

To be determined after implementation inspection.

### Follow-up

Await canonical materialisation, execution and review.
