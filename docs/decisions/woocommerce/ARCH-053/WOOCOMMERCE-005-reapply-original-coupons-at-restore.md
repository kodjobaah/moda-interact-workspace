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
status: review
priority: 55
executor: codex
claimed_at: 2026-10-31T22:10:13Z
attempt: 1
depends_on:
- ARCH-053-WOOCOMMERCE-002
- ARCH-053-WOOCOMMERCE-004
enables:
- ARCH-053-WOOCOMMERCE-006
created: 2026-10-29
updated: 2026-10-31
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
- Return a structured internal result to WOOCOMMERCE-006 private outcome handler, e.g. `appliedCodes: string[]`, `rejectedCodes: string[]`, `cartTotalRecalculated: boolean`; no new external API contract.

## Out of Scope

- No ARCH-052 dynamic discount selection, discount creation, extension of coupon expiry, or automatic coupon replacement.
- No changes in other repository-owned source, no Woo production WhatsApp enablement, no bypass of consent/STOP/order or final-send guards.
- No broad refactor, new Generic logger, direct WordPress access to Moda database/Redis, or continuation into enabled tasks.

## Requirements

- The saved coupons are *attempted*, not guaranteed. Coupon eligibility, stacking and current discount amount are solely WooCommerce’s authority; no custom PHP replica or Shared/Zod business policy.
- Do not create replacement coupons, extend their expiry, change usage limits, bypass Woo validation, grant discounts from the historical total, or call ARCH-052 agent/offer APIs.
- For one invalid code among multiple coupons, continue attempting remaining original codes in original order, subject to Woo stacking restrictions, and preserve successful codes. Record rejected outcomes for protected diagnostics and notice containment in WOOCOMMERCE-006, never for storefront error display.
- Until WOOCOMMERCE-005 is accepted, WOOCOMMERCE-002 must have rejected restoration of coupon-bearing baskets rather than silently skipping their coupons; this task removes that specific closed-gate only once native validation works.
- Use exact shared schema from accepted `ARCH-053-SHARED-001` (PHP must match its JSON fixtures, not import Node code). Zod validates wire *shape*, never WooCommerce coupon policy. Preserve stable checkoutKey, tenant scoping and generation semantics.
- WooCommerce PHP executes on merchant-controlled WordPress servers and **must not import or implement** `@modainteract/moda-interact-shared/logging` (that npm export belongs only to hosted Moda Node processes). Use existing server-side plugin diagnostics (the current bounded `error_log()` pattern where applicable), not a new generic logger, `wc_add_notice()`, browser console output or shopper-visible HTML for Moda errors. Record a bounded event/reason and safe correlation identifier; preserve the original error message and relevant safe provider response details when available after redaction, without guessing a substitute cause. Never log bearer tokens, full restore URLs, coupon codes or customer PII. At storefront/controller boundaries catch and privately log unexpected errors, preserve or safely roll back the cart, and continue/redirect without Moda-originated error notices. At Action Scheduler and other retry-owning job boundaries, log and **propagate** retryable failures for durable retry/failure evidence; do not acknowledge them as success. Never globally suppress WordPress diagnostics or delete unrelated Woo notices.
- Honour launcher-prepared, dedicated synchronised task worktrees and `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`; the repository agent updates only its assigned task metadata and Completion Report. Never mark itself Complete or push main.

## Work Items

- [x] Implement isolated `CheckoutCouponRestorer` and call it after restored products, before completion/redirect; ensure its automatic coupon attempts cannot leave Moda-triggered Woo error notices in the session.
- [x] Apply original coupons using Woo native APIs and recalculate totals; return independently testable applied/rejected outcomes.
- [x] Add tests for valid, expired, deleted, usage-exhausted, minimum spend, product-excluded, non-stackable and mixed multiple original coupons.

## Interfaces / Contracts

Input: `snapshot.appliedCouponCodes` from generation-bound API resolver (`ARCH-053-API-002`). Internal output is applied/rejected codes; Woo native `WC_Cart` owns actual discount values. Never use discount-proofs or dynamic-discount policy from ARCH-052.

## Dependencies

- `ARCH-053-WOOCOMMERCE-002` — must be architect-accepted Complete
- `ARCH-053-WOOCOMMERCE-004` — must be architect-accepted Complete

## Enables

- `ARCH-053-WOOCOMMERCE-006`

## Acceptance Criteria

- [ ] Valid original coupon appears as an applied Woo coupon after restoration; payable total is recalculated under current shop state.
- [ ] Expired or otherwise rejected coupon never appears as applied, product restoration succeeds, recalculated current total has no invalid discount, and rejection is returned privately to the WOOCOMMERCE-006 outcome handler; the checkout displays only Woo-approved applied coupons and current totals.
- [ ] Multiple codes with a mix of valid/invalid/stacking rules produce the actual Woo-approved subset and a full rejection list.
- [ ] Cannot force the original coupon discount or silently mint another coupon; unexpected errors remain visible to protected server diagnostics and cannot produce false success or a Moda storefront error notice.
- [ ] No new discounts/coupon extension, no automatic replacement of a previously applied invalid coupon, and no silent omission from **private outcome reporting**. No Moda-generated coupon-error notice on the storefront.
- [ ] Failed/invalid/replayed operations do not create duplicate recovery generations, outbound attempts or billings.
- [ ] Only owning repository implementation and authorised task metadata are changed; ARCH-052 remains untouched.

## Validation

- [x] Run `composer test` focused CouponRestorer and CartRestorer cases
- [ ] Run available Woo integration tests for live coupon validity, price and totals; report environment blockers
- [x] Run changed-file PHP lint and `git diff --check`; repository-wide Composer lint reports the pre-existing missing test file.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, record the exact commands/evidence, files, deviations and unresolved issues in `## Completion Report`, set the task to `review`, return to `moda_architect` and STOP. Do not implement another task.

## Implementation Notes

Only restoring to the shopper’s **current** cart is allowed; preserve safe transaction-like rollback pattern from WOOCOMMERCE-002 for unexpected restore failures. Coupon business rejection is an expected outcome, not an exception requiring full cart rollback.

## Completion Report

### Status

Ready for Review

### Files Changed

- `includes/Checkout/CheckoutCouponRestorer.php` — applies original coupon codes through `WC_Cart::apply_coupon`, verifies actual applied coupons, contains coupon error notices, recalculates current totals and returns a private applied/rejected result.
- `includes/Checkout/CheckoutCartRestorer.php` — permits validated coupon-bearing snapshots, runs coupon restoration after item restoration under capture suppression, returns the structured private result and redacts exact coupon values from failure logs.
- `includes/Checkout/CheckoutResumeController.php` — removes the previous empty-coupon rejection while retaining the confirmed `NONE` offer guard.
- `includes/Runtime.php` — loads the coupon restorer.
- `tests/CheckoutCartRestorerTest.php` — covers coupon-bearing restore, valid/rejected mixed codes, continued attempts, error-notice containment, totals and unexpected-error rollback.
- `tests/CheckoutResumeControllerTest.php` — isolates the test logger for restore failure coverage.
- `tests/integration/scenarios/checkout-wordpress.mjs` — exercises one valid and one deleted original coupon, current discounted total and absence of a shopper-visible rejected code.
- `composer.json` — includes the new class in declared PHP lint.

### Work Completed

- Implemented native Woo coupon application in the captured order after products and variations are restored.
- Coupon rejection remains nonfatal; later original codes are attempted and only codes present in Woo's actual applied-coupon state are reported as applied.
- Totals are recalculated after coupon attempts. Historical totals and discount values are not reused.
- Scoped Woo coupon-error filters contain coupon validation errors during each automatic attempt; unrelated existing notices are preserved. Unexpected failures use the existing rollback path and diagnostics redact coupon values.
- The controller continues to reject confirmed outreach offers and now accepts coupon-bearing restore snapshots.
- The restorer returns `{appliedCodes, rejectedCodes, cartTotalRecalculated}` internally for the next task's private outcome handling; no public API or shopper-facing coupon outcome was added.

### Validation Results

- `composer test -- --filter 'CheckoutCartRestorerTest|CheckoutResumeControllerTest' --do-not-cache-result --display-warnings` — passed: 11 tests, 68 assertions, no warnings.
- PHP lint for all changed PHP files — passed.
- `composer lint` — reached all changed PHP files successfully, then failed because the repository script references the absent `tests/integration/checkout-consent-saved-block-variant.php`.
- `git diff --check` — passed.
- `node --check tests/integration/scenarios/checkout-wordpress.mjs` — passed.
- Full `composer test -- --do-not-cache-result` — 292 tests passed; four unrelated existing failures remain in `CheckoutConsentCaptureTest`, `CheckoutConsentPresentationTest`, and two `PluginTest` cases.
- Full `npm run test:js:node` with host loopback access — 112/113 passed; one unrelated existing `wordpress-api-fixture.test.mjs` assertion rejects a six-digit fractional timestamp (`.000000Z`) where its fixture expects three digits.
- `npm run test:integration:wordpress` — blocked before scenarios run: wp-env images built but the task-specific temporary MySQL container exited during startup. The failed run left no task-specific containers. The existing developer test sites were not changed.

### Deviations

None.

### Assumptions

Codebase snapshot dated 2026-10-29; inspect actual HEAD after launcher preparation before implementing.

### Unresolved Issues

- Live Woo coupon acceptance, rejection and total recalculation remain unverified in wp-env because its task-specific MySQL container failed to start under the current Colima environment. Focused unit tests and code checks pass.
- Repository-wide PHP and Node suites retain the unrelated failures listed above.

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
