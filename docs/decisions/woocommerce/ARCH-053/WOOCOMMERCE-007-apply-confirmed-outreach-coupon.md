---
id: ARCH-053-WOOCOMMERCE-007
architecture_id: ARCH-053
title: Apply confirmed outreach checkout coupon through native Woo validation
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-053-API-003
- ARCH-053-WOOCOMMERCE-005
- ARCH-053-WOOCOMMERCE-006
enables:
- ARCH-053-WOOCOMMERCE-008
created: 2026-10-30
updated: 2026-10-30
---

# ARCH-053-WOOCOMMERCE-007 — Apply confirmed outreach checkout coupon through native Woo validation

## Architecture

`ARCH-053` — `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`, coordinated by `moda_architect`. Defined but **not materialised**; no branch, worktree, commit, push or acceptance is claimed.

## Objective

On a customer-confirmed restore POST, request the opt-in v2 offer-aware resolver response and **attempt the checkout coupon actually promised in the initial WhatsApp outreach**, after original coupons, without overriding WooCommerce validation or silently removing a previously applied original coupon.

## Context

WOOCOMMERCE-002 restores products using the existing v1 server-to-server resolver; WOOCOMMERCE-005 reattempts original `snapshot.appliedCouponCodes`, and WOOCOMMERCE-006 presents original coupon rejection notices. API-003 adds v2 response with `outreachOffer`. This task **extends those**, not creates a second cart restore or discount engine. API v1 remains valid for old Woo plugin builds until rollout.

## Scope

In `moda-interact-woocommerce`, update only:

- `includes/Api/ModaApiClient.php`: extend the existing server-side `resolveWooRecoveryLink` operation to submit `schemaVersion:'woo.restore.resolve.v2'`; do not call both v1 and v2 on the same POST. API bearer stays server-side.
- **Create** `includes/Api/WooRestoreOfferContracts.php`: strictly validate response v2 discriminator and fields against the SHARED-003 fixture; retain existing base snapshot verification from WooCommerce-002; no permissive success on missing `outreachOffer`.
- **Create** `includes/Checkout/CheckoutOutreachCouponRestorer.php`: implement the exact PHP interface and result below, calling only Woo native coupon/cart APIs.
- `includes/Checkout/CheckoutCartRestorer.php`: invoke recommended coupon application exactly once after products and the original-coupon operation, *before final capture*; preserve rollback and capture suppression from WOOCOMMERCE-002.
- `includes/Checkout/CheckoutResumeController.php`: pass the v2 result through the same confirmed-POST flow and hand off the typed offer outcome to the existing WOOCOMMERCE-006 presenter (WOOCOMMERCE-008 completes UI).
- Focused `tests/CheckoutOutreachCouponRestorerTest.php`, `tests/WooRestoreOfferContractsTest.php` and existing relevant controller/cart tests. Register new PHP source/tests in `composer.json` lint only if required by its existing explicit allowlist.

## Out of Scope

No discount discovery, coupon creation, modified expiry or usage constraints, original-cart URL encoding, new WordPress endpoint/bearer, API schema/business policy change, Meta template send, alternative-product insertion or customer-visible conflict-choice UI (WOOCOMMERCE-008 owns that).

## Requirements

- Keep the existing no-mutation GET and explicit nonce-protected confirmation POST. V2 resolver is called **after confirmation only**, using the original signed recovery link; no browser-side installation credentials, no external visitor contact/discount parameters.
- Restore product lines first. Reapply original coupons in their persisted order using WOOCOMMERCE-005. Only then process `outreachOffer`.
- `CHECKOUT_CODE`: attempt the exact code **once** through `WC()->cart->apply_coupon($code)` if not already applied (use Woo's canonical code comparisons). Inspect the resulting actual `WC()->cart->get_applied_coupons()` and recalculated totals. Never treat API `providerDiscountId` or the WhatsApp text as proof of current eligibility; the code may expire, be disabled, be limited or become inapplicable.
- `CHECKOUT_AUTOMATIC`: **never** call `apply_coupon`, fabricate a coupon, force a fee/price, add a WC filter, or assert savings. Recalculate native Woo totals and return a neutral `AUTOMATIC_NOT_FORCED` result; if the installed provider gives no reliable discount evidence, do not claim it applied.
- `ALTERNATIVE_PRODUCT`: do not insert promoted items or apply its discount to the abandoned basket; return `NOT_APPLICABLE` with original basket untouched. `NONE/NO_CONFIRMED_OFFER` is a no-op; `NONE/UNVERIFIABLE` produces the diagnostic/UI outcome for WOOCOMMERCE-008 without inventing a code.
- If the recommended code is **already present** in original applied codes, do not apply twice or show a duplicate rejection; return `ALREADY_APPLIED` only after Woo confirms it is still in the cart.
- If Woo applying the recommendation removes one or more previously successful original coupons due to stacking/individual-use rules, **undo the tentative recommendation**, restore the original applied set under Woo validation, recalculate, and return `CONFLICT_REQUIRES_CHOICE` with current original basket intact. An irrecoverable mid-apply/rollback error must take the existing protected cart rollback path; do not declare success after losing an original coupon.
- Business rejections (expired, minimum spend, usage limits, excluded product, non-stackable) return typed `REJECTED`, but do not block checkout when product restoration succeeds. Do not infer `EXPIRED` unless Woo reliably distinguishes it. Recalculate with `WC()->cart->calculate_totals()` once after coupon processing. Do not restore historic prices, shipping or tax.
- Suppress intermediate checkout capture during every mutation. Emit **one** fresh checkout activity after the final cart and coupon state is settled; preserve checkout key/generation and the existing ARCH-048 resumption flow. No second outreach, charge or new recovery inside WordPress.

### Repository / execution safeguards

- Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the launcher preparation packet and the parent ARCH-053 architecture before claiming. Work from dedicated, synchronized mirrored task worktrees; record both physical paths, initial SHAs and validation in the Completion Report. A snapshot does not establish the developer's current branch/status.
- Only change the **permitted owning-repository files** in Scope and this task's own authorised task metadata/Completion Report. No `_index.md`, no unrelated code, no other agent's task, no production WhatsApp activation, no merge/push to `main`.
- Node services use `@modainteract/moda-interact-shared/logging`. Log bounded identifiers and event codes, not raw URLs, bearer tokens, coupon codes, full customer data, original message text or unbounded provider bodies. Log and propagate unexpected dependency errors to the owner; never silently swallow them. PHP uses existing plugin-safe diagnostics, not a new generic logger.
- Keep checkout restoration read-only in the hosted API and cart-local in WooCommerce. Never have PHP query Moda PostgreSQL/Redis or an API handler change a visitor cart. Never create a new discount, extend an expired coupon, use ARCH-052 discovery code, bypass merchant consent/STOP/order/final provider gates or impose a cross-generation outreach cap.
- When the specified receipt/provider contract is absent, conflicting or untestable, **stop and return the gap to moda_architect**; do not invent an approximation, copy a Shared schema locally or broaden the task to another repo. System-test tasks are terminal and may not gate implementation tasks.


## Work Items

- [ ] Add server-side v2 request/strict response parity with SHARED-003 (v1 remains supported by the API, not required by this upgraded plugin path).
- [ ] Implement isolated outreach coupon restorer; preserve verified original coupons under stacking conflict and native totals.
- [ ] Integrate it after WOOCOMMERCE-005 without another restore pipeline, capture event, cart replacement or URL issuer.
- [ ] Add tests for all five offer kinds, valid/invalid code, original+recommended conflict, duplicate code, failed rollback and provider/API outage.

## Interfaces / Contracts

**Inputs from API-003, parsed on the PHP server:**

```json
{
  "schemaVersion": "woo.restore.resolve.v2",
  "status": "eligible",
  "recoveryId": "recovery_456",
  "checkoutKey": "woo-example-checkout",
  "snapshot": {
    "schemaVersion": "woo.cart-restore.v1",
    "kind": "supported",
    "appliedCouponCodes": ["SAVE10"],
    "lines": [{"productId":"101","quantity":2}]
  },
  "outreachOffer": {
    "kind": "CHECKOUT_CODE",
    "code": "EXTRA15",
    "providerDiscountId": "woo-discount-915"
  }
}
```

**Exact internal PHP input/output shape for `CheckoutOutreachCouponRestorer`:**

```php
/**
 * @param array<string,mixed> $validatedOffer  Strict v2 outreachOffer union
 * @param list<string> $appliedOriginalCoupons Actual Woo-applied original codes
 * @param WC_Cart $cart                        Current restored visitor cart
 * @return array{
 *   outcome: 'NO_OFFER'|'UNVERIFIABLE'|'NOT_APPLICABLE'|
 *            'AUTOMATIC_NOT_FORCED'|'APPLIED'|'ALREADY_APPLIED'|
 *            'REJECTED'|'CONFLICT_REQUIRES_CHOICE',
 *   recommendedCode: ?string,
 *   originalAppliedCodes: list<string>,
 *   currentAppliedCodes: list<string>,
 *   rejectionReason: ?string,
 *   totalsRecalculated: bool
 * }
 */
public function apply_outreach_offer(
    array $validatedOffer,
    array $appliedOriginalCoupons,
    WC_Cart $cart
): array;
```

The reason is **bounded native Woo evidence** only: known `EXPIRED` when reliably identified, otherwise general `NOT_APPLICABLE`; no claim from guesswork. `rejectionReason` is for the customer notice presenter, not logged raw. The `recommendedCode` may be used in an escaped customer-facing notice or transient **WC-session-only** offer-choice state; it must not be copied into recovery URL/query params or logging.

**Examples:**

| Original | Outreach | Woo current outcome | Result |
|---|---|---|---|
| `SAVE10` valid | `EXTRA15` valid and stackable | Both remain applied | `APPLIED` |
| `SAVE10` expired | `EXTRA15` valid | Only `EXTRA15` applied | `APPLIED`; original rejection notice still shown |
| `SAVE10` valid | `EXTRA15` expired | Only `SAVE10` applied | `REJECTED`; offer notice later |
| `SAVE10` valid | `EXTRA15` individually used | Original retained, offer not applied | `CONFLICT_REQUIRES_CHOICE` |
| `EXTRA15` original and valid | recommended `EXTRA15` | One copy remains | `ALREADY_APPLIED` |
| `SAVE10` valid | `CHECKOUT_AUTOMATIC` | Native totals only | `AUTOMATIC_NOT_FORCED` |
| Any | `ALTERNATIVE_PRODUCT` | No new product or coupon | `NOT_APPLICABLE` |

## Dependencies

- `ARCH-053-API-003` — accepted v2 offer-aware read with provenance.
- `ARCH-053-WOOCOMMERCE-005` — accepted original coupon reapplication.
- `ARCH-053-WOOCOMMERCE-006` — accepted original-coupon notices, so no notices silently disappear.

## Enables

- `ARCH-053-WOOCOMMERCE-008`

## Acceptance Criteria

- [ ] Code advertised in a **confirmed checkout** message is attempted on the shopper's current restored cart, but never guaranteed.
- [ ] Valid original coupons remain applied unless shopper expressly chooses a different combination; Woo still applies all current restrictions.
- [ ] An invalid recommended code cannot block otherwise valid basket restoration or replace/extend an expired coupon.
- [ ] Automatic and alternative-product offers never force a discount/coupon on the original checkout.
- [ ] GET previews do not resolve offers, mutate a cart or create new recovery activity; confirmed restore produces exactly one final update.
- [ ] No new persisted offer table, no new provider-send, no checkout URL token/coupon logging.

## Validation

- [ ] `composer test` / focused PHPUnit source+controller tests (actual declared `composer.json` scripts)
- [ ] `composer lint`, `php -l` for all newly created PHP files, and existing WordPress Classic+Blocks integration runner if available
- [ ] Integration tests for Woo current expiry, stacking, rollback and v2 HTTP error; `git diff --check`

## Stop Condition

When all defined Work Items, Acceptance Criteria and Validation are satisfied, update only this task's authorized metadata and Completion Report, set `status: review`, return to `moda_architect` and **STOP**. Do not begin Enabled tasks, self-accept, create new tasks, modify a sibling repository or merge/push main.

## Implementation Notes

The controller/restorer should have **one** final cart state for `CheckoutCapture` to snapshot. Reuse established suppression/rollback functionality; do not add a second status transition in the plugin. UI on expired/offered-code and opt-in replacement choices belongs to WOOCOMMERCE-008.

## Completion Report

### Status

Not Started — portable task definition, not claimed.

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not run. Report exact commands, results and any environment blockers after execution.

### Deviations

None.

### Assumptions

Defined from the 2026-10-30 uploaded snapshot. Re-read current task and repository HEAD after launcher preparation.

### Unresolved Issues

None claimed resolved. See explicit dependency/receipt gates above.

### Architectural Concerns

Escalate contract or ownership gaps instead of inventing a new transport or persistence location.

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

To be assessed after implementation.

### Follow-up

None.
