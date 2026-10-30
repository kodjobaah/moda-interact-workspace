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
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-053-WOOCOMMERCE-001
enables:
- ARCH-053-SYSTEM-TEST-002
- ARCH-053-WOOCOMMERCE-005
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-WOOCOMMERCE-004 — Publish coupon additions and removals as Woo checkout activity

## Architecture

Architecture: `ARCH-053`; document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Defined but not materialised**; the author has not created or pushed a developer task branch or implementation worktree.

## Objective

Publish coupon additions and removals as Woo checkout activity. This is a bounded, independently reviewable capability owned only by `moda_woocommerce` in `moda-interact-woocommerce`.

## Context

The 2026-10-29 snapshot captures products but lacks complete end-to-end original-coupon recovery. `ARCH-052` owns dynamic discount discovery and new offers, **not** previously applied Woo checkout coupons. The ARCH-053 complete restore contract is `woo.cart-restore.v1`, with `appliedCouponCodes: string[]` on the immutable snapshot. Do not design a separate coupon issuance engine or a new database coupon table.

## Scope

- Own changes to `moda-interact-woocommerce/includes/Checkout/CheckoutCapture.php` plus narrowly required `CheckoutSnapshot.php` and `tests/CheckoutCaptureTest.php`; add targeted `tests/integration/scenarios/checkout-coupons-wordpress.mjs` (or local equivalent), without changing API/Background code.
- Register `woocommerce_applied_coupon` and `woocommerce_removed_coupon` hooks with the correct Woo signature; use `captureExisting()` only when `CheckoutKey::SESSION_FIELD` contains an already observed valid checkout. Re-use the existing after-totals/Store API capture path for Checkout Blocks; do not create a new checkout key in the shopping-cart-only lifecycle.
- On each coupon change, call `WC()->cart->get_applied_coupons()` for the canonical *applied* list; preserve 0..10 valid codes in `checkout.restoration.appliedCouponCodes` exactly as validated for Shared. The resulting full snapshot fingerprint must include the list, including transitions from `[]` to `[code]` and back.
- Publish the existing `woo.activity.v3` CHECKOUT_UPDATED envelope via `CheckoutActivityPublisher::enqueue()`/Action Scheduler; preserve original `(shopId,checkoutKey)` and event IDs. Do not introduce a new event type, Redis queue or direct API call from a Woo frontend hook.

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
- Never log original coupon codes, raw restoration URLs/tokens, customer contact details or unbounded exception content. PHP uses existing safe plugin diagnostics; Node uses `@modainteract/moda-interact-shared/logging` if edited. Unexpected errors must be observable without breaking the shopper checkout.
- Honour launcher-prepared, dedicated synchronised task worktrees and `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`; the repository agent updates only its assigned task metadata and Completion Report. Never mark itself Complete or push main.

## Work Items

- [ ] Add correct after-application and after-removal capture hook registration for an observed checkout.
- [ ] Make the coupon list part of the dedup fingerprint and publish a new v3 checkout snapshot for coupon-only change.
- [ ] Create PHP and WordPress Classic/Blocks tests for apply/remove, unchanged total, duplicates, >10 codes, and malformed codes.

## Interfaces / Contracts

Consumes `WooCartRestoreSnapshotV1` / `checkout.restoration.appliedCouponCodes` from `ARCH-053-SHARED-001`; outbound producer is the existing `POST /v1/woocommerce/activity` v3 path. Reuse `CheckoutSnapshot::fromCart()`, `CheckoutCapture::captureExisting()` and `CheckoutActivityPublisher`; no new coupon protocol.

## Dependencies

- `ARCH-053-WOOCOMMERCE-001` — must be architect-accepted Complete

## Enables

- `ARCH-053-SYSTEM-TEST-002`
- `ARCH-053-WOOCOMMERCE-005`

## Acceptance Criteria

- [ ] Apply/removal with unchanged products/total yields one fresh accepted activity, and background candidate will receive latest entire list.
- [ ] Adding/removing/stacking coupons in Classic + Blocks yields an exact, bounded coupon list; no truncation, no invented codes.
- [ ] Identical recalculation remains suppressed and cart-page visits without an existing checkoutKey do not spawn abandonment events.
- [ ] All failing-hook paths are bounded/observable while Woo checkout itself remains operable.
- [ ] No new discounts/coupon extension, no automatic replacement of a previously applied invalid coupon, no silent omission of declined original coupon.
- [ ] Failed/invalid/replayed operations do not create duplicate recovery generations, outbound attempts or billings.
- [ ] Only owning repository implementation and authorised task metadata are changed; ARCH-052 remains untouched.

## Validation

- [ ] Run `composer test` focused `CheckoutCaptureTest` coupon cases
- [ ] Run `npm run test:integration:wordpress` checkout coupon scenarios when environment available; report exact blocked prerequisites
- [ ] Run declared plugin lint/checks and `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, record the exact commands/evidence, files, deviations and unresolved issues in `## Completion Report`, set the task to `review`, return to `moda_architect` and STOP. Do not implement another task.

## Implementation Notes

Preserve the original snapshot item projection from WOOCOMMERCE-001. No change to candidate logic or recovery-generation transitions here; these events feed the existing `ARCH-048` lifecycle after the background consumes them.

## Completion Report

### Status

Not Started

### Files Changed

None — task is defined but not materialised.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

Codebase snapshot dated 2026-10-29; inspect actual HEAD after launcher preparation before implementing.

### Unresolved Issues

None asserted until work is claimed.

### Architectural Concerns

Return schema, lifecycle and multi-repository discrepancies to `moda_architect` rather than improvising.

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
