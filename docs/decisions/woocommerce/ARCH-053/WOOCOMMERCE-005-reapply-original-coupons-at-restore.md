---
id: ARCH-053-WOOCOMMERCE-005
architecture_id: ARCH-053
title: Reapply original basket coupons through native WooCommerce validation
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
- ARCH-053-WOOCOMMERCE-002
- ARCH-053-WOOCOMMERCE-004
enables:
- ARCH-053-WOOCOMMERCE-006
created: 2026-10-29
updated: 2026-10-29
---

# ARCH-053-WOOCOMMERCE-005 — Reapply original basket coupons through native WooCommerce validation

## Architecture

Architecture: `ARCH-053`; document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Defined but not materialised**; the author has not created or pushed a developer task branch or implementation worktree.

## Objective

Reapply original basket coupons through native WooCommerce validation. This is a bounded, independently reviewable capability owned only by `moda_woocommerce` in `moda-interact-woocommerce`.

## Context

The 2026-10-29 snapshot captures products but lacks complete end-to-end original-coupon recovery. `ARCH-052` owns dynamic discount discovery and new offers, **not** previously applied Woo checkout coupons. The ARCH-053 complete restore contract is `woo.cart-restore.v1`, with `appliedCouponCodes: string[]` on the immutable snapshot. Do not design a separate coupon issuance engine or a new database coupon table.

## Scope

- Create `moda-interact-woocommerce/includes/Checkout/CheckoutCouponRestorer.php` and focused PHP tests; integrate it only at the confirmed-POST cart restoration boundary in `includes/Checkout/CheckoutCartRestorer.php`, with minimal adjustments to the caller/controller if necessary.
- After product/variation/quantity restoration succeeds, iterate `WooCartRestoreSnapshotV1.appliedCouponCodes` in captured order. Invoke `WC()->cart->apply_coupon($code)` for each under current Woo rules; inspect actual applied coupons to record `appliedCodes` and `rejectedCodes`, with bounded reason/category where Woo reliably supplies one.
- Recalculate Woo cart totals *after* coupon attempts using `WC()->cart->calculate_totals()`; do not carry over historical discounted total, historical price, coupon amount, original shipping/tax or order totals. Preserve all successfully applied original coupons and the correctly calculated price.
- Expected business rejection (expired, usage exhausted, product restriction, min subtotal, not combinable, disabled/deleted code) must not cancel product restoration. Unexpected internal error must be logged safely and fail according to the existing protected cart restore/rollback path; never claim an unverified coupon succeeded.
- Return a structured internal result to WOOCOMMERCE-006 notice presenter, e.g. `appliedCodes: string[]`, `rejectedCodes: string[]`, `cartTotalRecalculated: boolean`; no new external API contract.

## Out of Scope

- No ARCH-052 dynamic discount selection, discount creation, extension of coupon expiry, or automatic coupon replacement.
- No changes in other repository-owned source, no Woo production WhatsApp enablement, no bypass of consent/STOP/order or final-send guards.
- No broad refactor, new Generic logger, direct WordPress access to Moda database/Redis, or continuation into enabled tasks.

## Requirements

- The saved coupons are *attempted*, not guaranteed. Coupon eligibility, stacking and current discount amount are solely WooCommerce’s authority; no custom PHP replica or Shared/Zod business policy.
- Do not create replacement coupons, extend their expiry, change usage limits, bypass Woo validation, grant discounts from the historical total, or call ARCH-052 agent/offer APIs.
- For one invalid code among multiple coupons, continue attempting remaining original codes in original order, subject to Woo stacking restrictions, and preserve successful codes. Record rejected outcomes for display in WOOCOMMERCE-006.
- Until WOOCOMMERCE-005 is accepted, WOOCOMMERCE-002 must have rejected restoration of coupon-bearing baskets rather than silently skipping their coupons; this task removes that specific closed-gate only once native validation works.
- Use exact shared schema from accepted `ARCH-053-SHARED-001` (PHP must match its JSON fixtures, not import Node code). Zod validates wire *shape*, never WooCommerce coupon policy. Preserve stable checkoutKey, tenant scoping and generation semantics.
- Never log original coupon codes, raw restoration URLs/tokens, customer contact details or unbounded exception content. PHP uses existing safe plugin diagnostics; Node uses `@modainteract/moda-interact-shared/logging` if edited. Unexpected errors must be observable without breaking the shopper checkout.
- Honour launcher-prepared, dedicated synchronised task worktrees and `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`; the repository agent updates only its assigned task metadata and Completion Report. Never mark itself Complete or push main.

## Work Items

- [ ] Implement isolated `CheckoutCouponRestorer` and call it after restored products, before completion/redirect.
- [ ] Apply original coupons using Woo native APIs and recalculate totals; return independently testable applied/rejected outcomes.
- [ ] Add tests for valid, expired, deleted, usage-exhausted, minimum spend, product-excluded, non-stackable and mixed multiple original coupons.

## Interfaces / Contracts

Input: `snapshot.appliedCouponCodes` from generation-bound API resolver (`ARCH-053-API-002`). Internal output is applied/rejected codes; Woo native `WC_Cart` owns actual discount values. Never use discount-proofs or dynamic-discount policy from ARCH-052.

## Dependencies

- `ARCH-053-WOOCOMMERCE-002` — must be architect-accepted Complete
- `ARCH-053-WOOCOMMERCE-004` — must be architect-accepted Complete

## Enables

- `ARCH-053-WOOCOMMERCE-006`

## Acceptance Criteria

- [ ] Valid original coupon appears as an applied Woo coupon after restoration; payable total is recalculated under current shop state.
- [ ] Expired or otherwise rejected coupon never appears as applied, product restoration succeeds, recalculated current total has no invalid discount, and rejection is returned for notice display.
- [ ] Multiple codes with a mix of valid/invalid/stacking rules produce the actual Woo-approved subset and a full rejection list.
- [ ] Cannot force the original coupon discount or silently mint another coupon; unexpected errors remain visible and cannot produce false success.
- [ ] No new discounts/coupon extension, no automatic replacement of a previously applied invalid coupon, no silent omission of declined original coupon.
- [ ] Failed/invalid/replayed operations do not create duplicate recovery generations, outbound attempts or billings.
- [ ] Only owning repository implementation and authorised task metadata are changed; ARCH-052 remains untouched.

## Validation

- [ ] Run `composer test` focused CouponRestorer and CartRestorer cases
- [ ] Run available Woo integration tests for live coupon validity, price and totals; report environment blockers
- [ ] Run declared PHP lint/static checks and `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, record the exact commands/evidence, files, deviations and unresolved issues in `## Completion Report`, set the task to `review`, return to `moda_architect` and STOP. Do not implement another task.

## Implementation Notes

Only restoring to the shopper’s **current** cart is allowed; preserve safe transaction-like rollback pattern from WOOCOMMERCE-002 for unexpected restore failures. Coupon business rejection is an expected outcome, not an exception requiring full cart rollback.

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
