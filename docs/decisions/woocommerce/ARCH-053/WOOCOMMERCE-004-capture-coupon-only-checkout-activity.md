---
id: ARCH-053-WOOCOMMERCE-004
architecture_id: ARCH-053
title: Publish coupon additions and removals as Woo checkout activity
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 55
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-053-WOOCOMMERCE-001
enables:
- ARCH-053-SYSTEM-TEST-002
- ARCH-053-WOOCOMMERCE-005
created: 2026-10-29
updated: 2026-10-31
---

# ARCH-053-WOOCOMMERCE-004 — Publish coupon additions and removals as Woo checkout activity

## Architecture

Architecture: `ARCH-053`; document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. Materialised and claimed by the task launcher for Attempt 1.

## Objective

Publish coupon additions and removals as Woo checkout activity. This is a bounded, independently reviewable capability owned only by `moda_woocommerce` in `moda-interact-woocommerce`.

## Context

The 2026-10-29 snapshot captures products but lacks complete end-to-end original-coupon recovery. `ARCH-052` owns dynamic discount discovery and new offers, **not** previously applied Woo checkout coupons. The ARCH-053 complete restore contract is `woo.cart-restore.v1`, with `appliedCouponCodes: string[]` on the immutable snapshot. Do not design a separate coupon issuance engine or a new database coupon table.

## Scope

- Own changes to `moda-interact-woocommerce/includes/Checkout/CheckoutCapture.php` plus narrowly required `CheckoutSnapshot.php` and `tests/CheckoutCaptureTest.php`; add targeted `tests/integration/scenarios/checkout-coupons-wordpress.mjs` (or local equivalent), without changing API/Background code.
- Register `woocommerce_applied_coupon` and `woocommerce_removed_coupon` hooks with the correct Woo signature; use `captureExisting()` only when `CheckoutKey::SESSION_FIELD` contains an already observed valid checkout. Re-use the existing after-totals/Store API capture path for Checkout Blocks; do not create a new checkout key in the shopping-cart-only lifecycle.
- On each coupon change, call `WC()->cart->get_applied_coupons()` for the canonical *applied* list; preserve 0..10 valid codes in `checkout.restoration.appliedCouponCodes` exactly as validated for Shared. The resulting full snapshot fingerprint must include the list, including transitions from `[]` to `[code]` and back.
- Publish the existing `woo.activity.v1` CHECKOUT_UPDATED envelope via `CheckoutActivityPublisher::enqueue()`/Action Scheduler; preserve original `(shopId,checkoutKey)` and event IDs. Do not introduce a new event type, Redis queue or direct API call from a Woo frontend hook.

## Out of Scope

- No ARCH-052 dynamic discount selection, discount creation, extension of coupon expiry, or automatic coupon replacement.
- No changes in other repository-owned source, no Woo production WhatsApp enablement, no bypass of consent/STOP/order or final-send guards.
- No broad refactor, new Generic logger, direct WordPress access to Moda database/Redis, or continuation into enabled tasks.

## Requirements

- An applied code that leaves quantities and calculated total unchanged **still produces** a distinct checkout event. Removing it also produces an event. Duplicate hook/recalculation with identical canonical snapshot does not produce duplicate events.
- Code list is the customer-applied original state, not catalogue lookup, potential coupon eligibility or ARCH-052 newly offered discounts. Capture only coupons Woo has actually applied; invalid attempts which Woo never applied must not appear as historical coupons.
- For oversized/malformed/untrustworthy applied coupon lists the full restoration evidence is `kind:unsupported` with `COUPONS_UNAVAILABLE|LIMIT_EXCEEDED` instead of a falsely complete supported list. No silent truncation, no partial restore link.
- Coupon mutations can precede/follow totals calculation. Tests must verify the snapshot is read after Woo updates applied state, including Classic and Store API checkout; preserve checkout capture nonblocking behaviour with bounded safe diagnostics.
- Use exact shared schema from accepted `ARCH-053-SHARED-001` (PHP must match its JSON fixtures, not import Node code). Zod validates wire *shape*, never WooCommerce coupon policy. Preserve stable checkoutKey, tenant scoping and generation semantics.
- WooCommerce PHP executes on merchant-controlled WordPress servers and **must not import or implement** `@modainteract/moda-interact-shared/logging` (that npm export belongs only to hosted Moda Node processes). Use existing server-side plugin diagnostics (the current bounded `error_log()` pattern where applicable), not a new generic logger, `wc_add_notice()`, browser console output or shopper-visible HTML for Moda errors. Record a bounded event/reason and safe correlation identifier; preserve the original error message and relevant safe provider response details when available after redaction, without guessing a substitute cause. Never log bearer tokens, full restore URLs, coupon codes or customer PII. At storefront/controller boundaries catch and privately log unexpected errors, preserve or safely roll back the cart, and continue/redirect without Moda-originated error notices. At Action Scheduler and other retry-owning job boundaries, log and **propagate** retryable failures for durable retry/failure evidence; do not acknowledge them as success. Never globally suppress WordPress diagnostics or delete unrelated Woo notices.
- Honour launcher-prepared, dedicated synchronised task worktrees and `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`; the repository agent updates only its assigned task metadata and Completion Report. Never mark itself Complete or push main.

## Work Items

- [x] Add correct after-application and after-removal capture hook registration for an observed checkout.
- [x] Make the coupon list part of the dedup fingerprint and publish a new canonical v1 checkout snapshot for coupon-only change.
- [x] Create PHP and WordPress Classic/Blocks tests for apply/remove, unchanged total, duplicates, >10 codes, and malformed codes.

## Interfaces / Contracts

Coupon-only updates use **the same canonical `woo.activity.v1` `CHECKOUT_UPDATED`** activity payload as WOOCOMMERCE-001, including full `checkout.restoration.appliedCouponCodes`; do not invent a coupon-specific event version or eventType. Recompute the checkout fingerprint when original coupon codes change even if line items and displayed total have not.

Consumes `WooCartRestoreSnapshotV1` / `checkout.restoration.appliedCouponCodes` from `ARCH-053-SHARED-001`; outbound producer is the existing `POST /v1/woocommerce/activity` v1 path. Reuse `CheckoutSnapshot::fromCart()`, `CheckoutCapture::captureExisting()` and `CheckoutActivityPublisher`; no new coupon protocol.

## Dependencies

- `ARCH-053-WOOCOMMERCE-001` — must be architect-accepted Complete

## Enables

- `ARCH-053-SYSTEM-TEST-002`
- `ARCH-053-WOOCOMMERCE-005`

## Acceptance Criteria

- [x] Apply/removal with unchanged products/total yields one fresh accepted activity, and background candidate will receive latest entire list.
- [x] Adding/removing/stacking coupons in Classic + Blocks yields an exact, bounded coupon list; no truncation, no invented codes.
- [x] Identical recalculation remains suppressed and cart-page visits without an existing checkoutKey do not spawn abandonment events.
- [x] All failing-hook paths are bounded/observable while Woo checkout itself remains operable.
- [x] No new discounts/coupon extension, no automatic replacement of a previously applied invalid coupon, no silent omission of declined original coupon.
- [x] Failed/invalid/replayed operations do not create duplicate recovery generations, outbound attempts or billings.
- [x] Only owning repository implementation and authorised task metadata are changed; ARCH-052 remains untouched.

## Validation

- [x] Run `composer test` focused `CheckoutCaptureTest` coupon cases
- [x] Run `npm run test:integration:wordpress` checkout coupon scenarios when environment available; report exact blocked prerequisites
- [x] Run declared plugin lint/checks and `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, record the exact commands/evidence, files, deviations and unresolved issues in `## Completion Report`, set the task to `review`, return to `moda_architect` and STOP. Do not implement another task.

## Implementation Notes

Preserve the original snapshot item projection from WOOCOMMERCE-001. No change to candidate logic or recovery-generation transitions here; these events feed the existing `ARCH-048` lifecycle after the background consumes them.

## Completion Report

### Status

Ready for Review

### Files Changed

`moda-interact-woocommerce/includes/Checkout/CheckoutCapture.php`; `tests/CheckoutCaptureTest.php`; `tests/integration/scenarios/checkout-wordpress.mjs`.

### Work Completed

Registered Woo's applied/removed coupon actions with the one-code hook signature. The callback ignores the individual code and calls `captureExisting()`, which requires an already valid checkout key; the snapshot reads Woo's full canonical applied-coupon list. Existing fingerprinting therefore publishes a new v1 event for real coupon-list changes and suppresses identical snapshots. Added focused PHP callback coverage plus genuine Classic and Blocks HTTP integration for application, removal, no-total-change, full code list, same checkout key, and duplicate unchanged snapshots. Existing PHP snapshot cases continue to cover malformed and over-limit lists with unsupported restoration rather than truncation.

### Validation Results

Passed:

- `composer test -- --filter CheckoutCaptureTest --do-not-cache-result` — 19 tests, 186 assertions. PHPUnit reports one unrelated existing warning from `tests/RecoveryPolicyControllerTest.php:14` (`$moda_interact_test_logger` is undefined), triggered by other pre-existing `CheckoutCaptureTest` cases; confirmed with `--display-warnings`.
- `composer lint` — all declared PHP syntax checks passed.
- `node --check tests/integration/scenarios/checkout-wordpress.mjs` — passed.
- `MODA_CHECKOUT_TEST_DISPOSABLE=1 npm run test:integration:wordpress -- --checkout-only` — `ARCH-035 checkout-only integration PASS`; includes real Classic and Blocks coupon add/remove with unchanged totals and duplicate suppression. Ran against the task-specific isolated wp-env after confirming its fixture ID/version; temporary API constants and test data were cleaned up.
- `git diff --check` — passed.

An initial full integration run reached the Classic coupon scenario and failed on an over-broad assertion that treated a new checkout-review contact snapshot as a duplicate. The integration assertion was narrowed to repeat the same coupon action; the subsequent checkout-only run passed. Colima's VM was initially in a stale/broken state; a graceful stop and restart recovered the existing VM. Bootstrap passed with Docker access to the Colima socket.

### Deviations

No scope change. The integration assertions were added to the existing checkout scenario file rather than a separate scenario module.

### Assumptions

The current shared restoration snapshot and fingerprint already include the complete applied coupon list; only the missing Woo action hooks needed implementation. Coupon hooks must not establish checkout identity on cart-only pages.

### Unresolved Issues

None.

### Worktree and Publication Evidence

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-WOOCOMMERCE-004`, branch `task/ARCH-053-WOOCOMMERCE-004`. Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-WOOCOMMERCE-004`, same task branch. Launcher claim commit: `2c96056db68b7bc4019833749ecf555e387d9aca`. Implementation began at `e5bc98b822f78be8ed01f3940627bc333eadd584`; implementation commit: `654fe7a` (`feat(woocommerce): capture checkout coupon changes`), pushed to the implementation task branch. Changes remain limited to the owning WooCommerce repository and this task record. Parent task report publication is pending; neither branch is merged to `main`.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet assessed.

### Follow-up

None.
