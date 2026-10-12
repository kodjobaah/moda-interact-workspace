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
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-SHARED-003", "ARCH-036-BACKGROUND-001"]
enables: ["ARCH-036-WOOCOMMERCE-003", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
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

`isAvailable=true` now means **merchant selected for Moda recovery**, not provider availability. `providerStatus`, `fixedSelectable`, dates/restrictions and catalogue currency determine whether a row may appear/select. Existing ARCH-016 `FIXED` policy CHECK requires a valid FK; for Woo FIXED save, the API writes one real selected same-Shop `ShopifyDiscount.id` as the compatibility anchor. The full set is the selected discount rows, never a JSON selected-ID array.

## Scope

Implement versioned paginated GET `/v1/merchant/discount-catalogue` and GET/PUT `/v1/merchant/discount-offers` on existing models. Use authenticated Woo Shop, Shop-row lock + `ShopSettings.updatedAt` revision, and a transaction updating **one Shop's flags, mode and anchor**. Allow 1–50 selected coupon row IDs in FIXED; the bound is an API validation rule, not new DDL.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

- Catalogue GET returns only rows with `providerStatus='ACTIVE'`, `fixedSelectable=true`, in-date, supported/positive-valued rules, belonging to the active Shop's CURRENT/fresh catalogue. Return both checked (`isAvailable=true`) and unchecked (`false`) coupons, with stable bounded server-side pagination. Otherwise a merchant cannot check an unselected coupon.
- `isAvailable=true` marks a merchant selection. Multiple true flags are allowed; the offer mode controls whether they are used. `NONE` sends no coupons; `AI_BEST_APPLICABLE` considers eligible ACTIVE catalogue rows independently of the flags.
- PUT accepts complete desired selected row ID set (not provider codes or arbitrary shopId), validates same Shop, ACTIVE, fixedSelectable, freshness and unique count, and updates checked flags atomically **only for the authenticated Woo Shop**. No partial saves if one ID is invalid, foreign, stale or unsupported.
- `FIXED` requires at least one checked coupon. Write `fixedShopifyDiscountId` to one **actual** selected `ShopifyDiscount.id` chosen deterministically (e.g. sorted smallest internal ID) in the same transaction; never `woo:coupon:<providerId>`, because this field is a PostgreSQL FK. `NONE`/`AI_BEST_APPLICABLE` require `fixedShopifyDiscountId=NULL` while flags may remain as remembered preferences.
- Unchecking the last coupon while the mode remains FIXED is a validation error; the merchant can switch to NONE/AI to clear the FK. For a successful write, advance the `ShopSettings.updatedAt` revision even if only checkboxes changed; replay of an identical write is idempotent, and a stale revision is 409.
- Distinguish saved merchant mode from effective admin override without modifying the override row. Do not add columns, constraints, enums or migrations. No write to Shopify rows through Woo credentials. 400/401/403/404/409/503 distinct, no secret/provider PII leakage.

## Work Items

- [ ] Implement shop-authorised CURRENT active-coupon catalogue read with cursor/page metadata and selected flags.
- [ ] Implement one transactional full-set CAS save updating `isAvailable`, mode, and real-row FK anchor under Shop lock.
- [ ] Test conflicting writes, repeated calls, mode switching, last-coupon removal, invalid/foreign/unavailable IDs and unchanged delay/follow-up.
- [ ] Verify legacy SQL FIXED FK/CHECK constraints and existing Shopify API behavior using a migrated disposable PostgreSQL database.

## Interfaces / Contracts

API-owned versioned GET `/v1/merchant/discount-catalogue`, GET/PUT `/v1/merchant/discount-offers`; existing Prisma `ShopSettings` + `ShopifyDiscount` only. Shared coupon proof is **not** a selected-ID storage contract; existing `/recovery-policy` remains unchanged.

## Dependencies

- `ARCH-036-SHARED-003`
- `ARCH-036-BACKGROUND-001`

## Enables

- `ARCH-036-WOOCOMMERCE-003`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Multiple Woo checkboxes persist via existing discount flags across pages/reloads.
- [ ] `FIXED` save satisfies existing SQL checks using a real referenced selected discount ID; no fake FK or new schema.
- [ ] NONE/AI never offer the selected FIXED set, regardless of flags.
- [ ] Stale/foreign/inactive/unselectable writes are rejected atomically.
- [ ] Merchant conflict state and effective Admin override remain correct; Shopify settings untouched.

## Validation

- [ ] Focused API contract/route/unit tests and OpenAPI checks.
- [ ] Disposable PostgreSQL existing-constraint, shop lock, CAS and foreign-shop cases; verify no schema migration needed.
- [ ] Declared API typecheck/lint/test/build and `git diff --check`.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

Provider discount eligibility at message-send time is a separate capability; saving an ID does not assert it is redeemable.

For developer execution, use the canonical `/moda_developer_create ARCH-036-API-002` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-API-002`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

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
