---
id: ARCH-053-WOOCOMMERCE-006
architecture_id: ARCH-053
title: Display rejected original coupons and updated checkout totals
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
- ARCH-053-WOOCOMMERCE-005
enables:
- ARCH-053-SYSTEM-TEST-002
- ARCH-053-WOOCOMMERCE-007
- ARCH-053-WOOCOMMERCE-007
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-WOOCOMMERCE-006 — Display rejected original coupons and updated checkout totals

## Architecture

Architecture: `ARCH-053`; document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Defined but not materialised**; the author has not created or pushed a developer task branch or implementation worktree.

## Objective

Display rejected original coupons and updated checkout totals. This is a bounded, independently reviewable capability owned only by `moda_woocommerce` in `moda-interact-woocommerce`.

## Context

The 2026-10-29 snapshot captures products but lacks complete end-to-end original-coupon recovery. `ARCH-052` owns dynamic discount discovery and new offers, **not** previously applied Woo checkout coupons. The ARCH-053 complete restore contract is `woo.cart-restore.v1`, with `appliedCouponCodes: string[]` on the immutable snapshot. Do not design a separate coupon issuance engine or a new database coupon table.

## Scope

- Create `moda-interact-woocommerce/includes/Checkout/CheckoutCouponNoticePresenter.php` (or a focused equivalent using existing Woo notice facilities); connect the result of `CheckoutCouponRestorer` to `CheckoutResumeController.php`. Add PHPUnit and WordPress integration tests for Classic and Checkout Blocks.
- For each rejected original coupon produce one understandable, escaped, localisable customer-facing notice at the resumed checkout. Say a coupon is expired only if current Woo rejection reliably identifies expiry; otherwise explain that it cannot be applied and the current total has been recalculated.
- Use WooCommerce session-backed notices or a verified Blocks-compatible mechanism that remains visible after `wp_safe_redirect(wc_get_checkout_url())`; do not assume a Classic notice automatically appears in Checkout Blocks. Exercise both in an actual Woo runtime.
- Ensure valid original coupons remain visibly applied and the current payable total displayed by Woo exactly matches `WC()->cart` after recalculation. Avoid duplicating Woo core error notices or showing notices on GET/link preview.
- Do not expose resolver tokens, other generation IDs, historical customer identity, original internal discount proofs or sensitive payload in notices.

## Out of Scope

- No ARCH-052 dynamic discount selection, discount creation, extension of coupon expiry, or automatic coupon replacement.
- No changes in other repository-owned source, no Woo production WhatsApp enablement, no bypass of consent/STOP/order or final-send guards.
- No broad refactor, new Generic logger, direct WordPress access to Moda database/Redis, or continuation into enabled tasks.

## Requirements

- Never silently omit a rejected coupon or promise the old discounted total; never show “expired” without authoritative Woo rejection evidence.
- An expired original coupon must **not block** restoration of otherwise valid product lines. Shopper can continue with the updated total or choose another coupon through normal WooCommerce UI.
- Notices must be bounded, correctly escaped, translatable and visible after redirect in both Classic and Blocks; rejected codes remain unapplied.
- Preserve the confirmation GET no-mutation invariant, cross-device session and proper checkoutKey rebinding implemented in WOOCOMMERCE-002.
- Use exact shared schema from accepted `ARCH-053-SHARED-001` (PHP must match its JSON fixtures, not import Node code). Zod validates wire *shape*, never WooCommerce coupon policy. Preserve stable checkoutKey, tenant scoping and generation semantics.
- Never log original coupon codes, raw restoration URLs/tokens, customer contact details or unbounded exception content. PHP uses existing safe plugin diagnostics; Node uses `@modainteract/moda-interact-shared/logging` if edited. Unexpected errors must be observable without breaking the shopper checkout.
- Honour launcher-prepared, dedicated synchronised task worktrees and `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`; the repository agent updates only its assigned task metadata and Completion Report. Never mark itself Complete or push main.

## Work Items

- [ ] Wire applied/rejected coupon results to one notice per rejected code, plus current total display by Woo.
- [ ] Prove Classic and Checkout Blocks notice persistence across the checkout redirect, with no duplicate notice on retry.
- [ ] Test invalid/expired/usage exhausted/partial multi-coupon restoration and HTML-like coupon codes safely.

## Interfaces / Contracts

Internal input from WOOCOMMERCE-005 `appliedCodes/rejectedCodes` plus current native Woo cart total; no new Shared/API/DB schema. The redirect still uses `wc_get_checkout_url()` as the final destination.

## Dependencies

- `ARCH-053-WOOCOMMERCE-005` — must be architect-accepted Complete

## Enables

- `ARCH-053-SYSTEM-TEST-002`
- `ARCH-053-WOOCOMMERCE-007` — later separately applies confirmed recommended code after original-coupon notices.
- `ARCH-053-WOOCOMMERCE-007` — later separately applies confirmed recommended code after original-coupon notices.

## Acceptance Criteria

- [ ] A customer whose SAVE10 expired sees an intelligible coupon-unavailable notice and actual new payable total; valid basket lines remain present.
- [ ] For mixed original coupons, only rejected codes produce notices; valid coupons are shown applied; no stale prices, no duplicate notices.
- [ ] Customer-facing message works in both Classic and Checkout Blocks and never leaks URL tokens/PII.
- [ ] Unconfirmed link GET does not produce checkout notices, update cart, or close recovery.
- [ ] No new discounts/coupon extension, no automatic replacement of a previously applied invalid coupon, no silent omission of declined original coupon.
- [ ] Failed/invalid/replayed operations do not create duplicate recovery generations, outbound attempts or billings.
- [ ] Only owning repository implementation and authorised task metadata are changed; ARCH-052 remains untouched.

## Validation

- [ ] Run `composer test` focused coupon notice/controller tests
- [ ] Run `npm run test:integration:wordpress` Classic and Blocks notice persistence scenarios or record exact failure/blocker
- [ ] Run declared lint and `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, record the exact commands/evidence, files, deviations and unresolved issues in `## Completion Report`, set the task to `review`, return to `moda_architect` and STOP. Do not implement another task.

## Implementation Notes

Use WooCommerce’s built-in localisation and notice APIs wherever they can genuinely satisfy Classic + Blocks. If Blocks support requires new public assets or UI, stop and return an architectural dependency rather than silently suppressing the notice.

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
