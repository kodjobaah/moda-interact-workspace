---
id: ARCH-036-WOOCOMMERCE-003
architecture_id: ARCH-036
title: Implement three offer modes and multi-coupon checkbox UI
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-API-002"]
enables: ["ARCH-036-BACKGROUND-003", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-WOOCOMMERCE-003 — Implement three offer modes and multi-coupon checkbox UI

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Enable the agreed three Recovery Offer modes using the existing Woo coupon catalogue, real multi-select checkboxes, and a manual Save action backed by API-002's existing discount selection flags.

## Context

ARCH-035-WOOCOMMERCE-011 provides a preview-only catalogue picker. Under the final architecture, `ShopifyDiscount.isAvailable=true` means selected by the merchant. Coupon provider availability comes from ACTIVE status, fixedSelectable, date and catalogue freshness. The actual offer mode comes from ShopSettings, with one real selected-FK compatibility anchor for FIXED.

## Scope

Modular React recovery offer cards, accessible checkbox list with bounded search/pagination, selected-state persistence across result pages, Save/Cancel/conflict feedback and privileged WordPress REST proxy to API-002. Preserve existing Store Category/Recovery Behaviour save and two-stage WordPress menus. Use all 20 locales.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

- Top-level NONE/FIXED/AI mutually exclusive. NONE never offers coupons, FIXED exposes multiple **checkboxes** for ACTIVE/current/supported coupons, AI considers supported ACTIVE catalogue coupons without checkbox restriction.
- The checkbox checked state comes from `isAvailable` and is not a separate preview radio control. Search/filter/page changes preserve the draft set. Disabled/removed/expired coupons never appear as selectable; show a count/notice if previously selected choices became unavailable.
- Save only on click; changes remain unsaved until success. FIXED with zero checked rows is blocked with inline explanation. Save `expectedRevision` and complete internal discount row ID set through API-002; no fake Shopify GraphQL IDs, no direct browser-to-hosted access.
- Retain state on 400/409/503, disable repeat submissions, and keep settings/configuration distinct from send-time proof. Preloading not ready => controls nonpersistent/unavailable, not a false saved offer.

## Work Items

- [ ] Replace preview-only second radio group with multiple coupon checkboxes within FIXED; preserve the three separate mode cards.
- [ ] Read selected flags and active catalogue from API-002 with server-side pagination, returning to same filter after navigation.
- [ ] Persist mode+checkbox set manually through the WordPress proxy with CAS/conflict handling.
- [ ] Test NONE/FIXED/AI, multiple coupons, mode switch, 0 selections, stale records, 20 languages and responsive UI.

## Interfaces / Contracts

Woo plugin WordPress REST proxy to API-002. Actual selection is stored in existing `ShopifyDiscount.isAvailable`; ShopSettings has existing mode + one real FK anchor. No selected-ID JSON storage.

## Dependencies

- `ARCH-036-API-002`

## Enables

- `ARCH-036-BACKGROUND-003`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Selected Woo coupon checkboxes correctly reflect `isAvailable` and survive reload/pagination.
- [ ] `NONE` never sends an offer; FIXED is bound to selected ACTIVE coupons; AI allows supported ACTIVE candidates, unchecked included.
- [ ] Save updates actual persistent selection only after successful request; no automatic saves or double clicks.
- [ ] Existing native menus and 20-language UI remain intact.

## Validation

- [ ] Woo PHP proxy validation, React hook/component/controller tests, LocalWP UX.
- [ ] Mobile/desktop wireframe checks, 20-language translation checks, JS/CSS lint/build/plugin ZIP, `git diff --check`.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

Do not put API calls in presentation components. Keep the existing `WOOCOMMERCE-011` preview work as historical UI foundation.

For developer execution, use the canonical `/moda_developer_create ARCH-036-WOOCOMMERCE-003` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-WOOCOMMERCE-003`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

## ASCII Page Design

```text
WordPress Admin > WooCommerce > Moda Interact > Recovery settings
+-----------------------------------------------------------------------+
| RECOVERY OFFER                                                        |
|                                                                       |
| ( ) No discount   (x) Specific discount   ( ) AI-selected discount     |
|                                                                       |
| Specific discount — select one or more coupons                        |
| Search coupons [_______________________] [Search]                      |
|                                                                       |
| [x] SAVE10      10% off                ACTIVE                          |
| [ ] SAVE20      GBP 20 fixed cart      ACTIVE                          |
| [x] WELCOME5    GBP 5 fixed cart       ACTIVE                          |
|                                                                       |
| [Previous]             Page 1 of N                   [Next]             |
|                                                                       |
| 2 coupons selected                        [Save recovery behaviour]   |
+-----------------------------------------------------------------------+
| Only ACTIVE, supported, in-date coupons appear.                       |
| An expired/removed coupon is not selectable.                          |
+-----------------------------------------------------------------------+

At tablet width the offers wrap; on mobile the three mode cards,
search and each coupon checkbox row stack with full-width Save action.
Selecting the UI never changes a coupon until Save succeeds.
```

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
