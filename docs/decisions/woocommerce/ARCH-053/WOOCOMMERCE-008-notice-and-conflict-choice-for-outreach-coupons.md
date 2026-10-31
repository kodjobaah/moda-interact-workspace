---
id: ARCH-053-WOOCOMMERCE-008
architecture_id: ARCH-053
title: Present outreach coupon outcomes and explicit stacking-conflict choice
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 68
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-053-WOOCOMMERCE-007
- ARCH-053-WOOCOMMERCE-006
enables:
- ARCH-053-SYSTEM-TEST-003
created: 2026-10-30
updated: 2026-10-30
---

# ARCH-053-WOOCOMMERCE-008 — Present outreach coupon outcomes and explicit stacking-conflict choice

## Architecture

`ARCH-053` — `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`, coordinated by `moda_architect`. Defined but **not materialised**; no branch, worktree, commit, push or acceptance is claimed.

## Objective

Make the outreach-coupon outcome visible after WooCommerce checkout restoration, and provide an **explicit, safe choice** when the promoted coupon cannot coexist with the shopper's original applied coupons. Work for both Classic Checkout and Checkout Blocks without showing an unearned discount.

## Context

WOOCOMMERCE-006 handles the **original** coupon notices. WOOCOMMERCE-007 returns the typed result of attempting the **sent outreach recommendation**. This task is solely the post-restore customer experience, one-time session-safe choice and native coupon revalidation. It must not become a second offer-selection engine or generic promotion editor.

## Scope

Only `moda-interact-woocommerce`:

- **Create** `includes/Checkout/CheckoutOutreachOfferNoticePresenter.php`: present offer outcome as one bounded, translated and escaped customer-facing notice using existing WooCommerce message primitives for Classic and an architect-approved supported Blocks mechanism.
- **Create** `includes/Checkout/CheckoutOutreachCouponChoice.php`: WC-session-scoped **one-time** conflict-choice state and an explicitly protected same-origin POST action on checkout; never expose server bearer or store the original WhatsApp URL in the browser.
- **Update** `includes/Checkout/CheckoutResumeController.php`: after successful restore only, pass WOOCOMMERCE-007 outcome into presenter/session choice state **before** safe checkout redirect.
- **Update** `includes/Checkout/CheckoutCouponNoticePresenter.php` from WOOCOMMERCE-006 only to prevent duplicate original vs recommended notices; original invalid-code messages must remain intact.
- **Update** `includes/Runtime.php` for the narrowly registered protected checkout choice route/hook and, if strictly needed, existing assets registration for Blocks UI. Add PHP/real-Woo integration tests. If a Blocks-native client extension is needed, implement only its bounded notice/choice UI assets, not a new checkout architecture.

## Out of Scope

No outreach code discovery, Meta message selection, discount creation, overriding original coupon rules, Woo custom pricing, API call at passive GET, link minting, DB state writes or alternate customer journey. Do not edit another domain or reopen ARCH-052.

## Requirements

### Multi-code group customer choice — normative 30 October 2026

Present neutral, source-grounded group results: all offered codes applied natively; one or more rejected/expired; group incompatible with original coupons; or unverifiable. A PARTIAL group must not appear as fully applied. Preserve original applied codes by default. The existing 10-minute, nonce-protected, cart-hash/session-bound choice remains, but session choice state now stores a bounded 1..3 **server-side code array** from the verified receipt (no codes in browser POST/URL). Shopper may explicitly choose `Try the offered set instead`; reapply the entire group natively and atomically from the customer's perspective, restoring the valid original set on any failed/partial attempt. Both Classic and Blocks must show actual recalculated totals and one escaped translated outcome. Do not invent additional checkout confirmation, price guarantees or new persistent storage.


- For `APPLIED` or `ALREADY_APPLIED`, show current checkout and Woo's **actually applied** coupon without false savings claim; no error notice.
- For `REJECTED`, show one customer-readable offer notice. Display “expired” only when Woo supplies reliable expiry evidence; otherwise “The offered discount could not be applied. Your checkout total has been recalculated.” No automatic replacement or historical total.
- For `UNVERIFIABLE`, show a generic “We could not verify the promotional offer in your message; current checkout discounts apply” without exposing any private IDs. For `NONE/NO_CONFIRMED_OFFER`, no false coupon notice. `AUTOMATIC_NOT_FORCED` must not claim the automatic discount is active; Woo native totals remain authoritative. `NOT_APPLICABLE` must not claim an alternative-product offer applies to this basket.
- For `CONFLICT_REQUIRES_CHOICE`, show that the **original coupon remains applied**, and offer “Keep original coupon(s)” (default/no action) or “Try the offered code instead” (explicit shopper POST). No automatic removal of a valid original coupon. The switch must be performed by WooCommerce APIs, validated *again at that time*, and present the current total before payment.
- The choice is bound to the **current WC session, original resolved recovery ID, code and cart fingerprint** created after a successful confirmed POST. Use a bounded WC session key `moda_interact_outreach_coupon_choice_v1` holding only `{recoveryId,code,originalCodes,cartHash,createdAt}`; expire at **10 minutes** or on checkout/cart change, successful/failed choice, order completion or new restore. No durable WordPress option/transient or browser localStorage; never put code or link bearer in the choice POST/query string.
- Choice POST: require WC session, valid WordPress nonce, same-origin form target, one-time state not expired, matching current cart hash and checkout key, and unchanged generation-bound restored session context. If the cart changed, fail safely and ask customer to use normal coupon UI; **do not** fetch/reapply a stale recovery link. Ignore duplicate submits after state consumed.
- If customer selects “Try offered code”, remove incompatible originals using native WC API **only after explicit choice**; call `WC()->cart->apply_coupon()` for recommendation, recalculate, and if Woo rejects it, attempt safe restoration of originals with current Woo validation and show neutral notices. Unexpected errors must be logged safely, trigger guarded rollback, and never claim a discounted total. The offer may expire between first restoration and choice.
- `wc_add_notice` may be insufficient for Woo Checkout Blocks: prove supported persisted notice + interactive choice rendering in real Blocks; if impossible with existing hooks, report a scoped client-asset dependency to architect instead of claiming Blocks coverage via a Classic-only assertion. Escape/localise messages; never display raw provider proof, URL, customer details or internal token.
- GET/link previews must not create notices/choice state/checkout updates. Repeated POST/reload must not duplicate notices, coupon application, recovery generation or messages.

### Repository / execution safeguards

- Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the launcher preparation packet and the parent ARCH-053 architecture before claiming. Work from dedicated, synchronized mirrored task worktrees; record both physical paths, initial SHAs and validation in the Completion Report. A snapshot does not establish the developer's current branch/status.
- Only change the **permitted owning-repository files** in Scope and this task's own authorised task metadata/Completion Report. No `_index.md`, no unrelated code, no other agent's task, no production WhatsApp activation, no merge/push to `main`.
- Node services use `@modainteract/moda-interact-shared/logging`. Log bounded identifiers and event codes, not raw URLs, bearer tokens, coupon codes, full customer data, original message text or unbounded provider bodies. Log and propagate unexpected dependency errors to the owner; never silently swallow them. PHP uses existing plugin-safe diagnostics, not a new generic logger.
- Keep checkout restoration read-only in the hosted API and cart-local in WooCommerce. Never have PHP query Moda PostgreSQL/Redis or an API handler change a visitor cart. Never create a new discount, extend an expired coupon, use ARCH-052 discovery code, bypass merchant consent/STOP/order/final provider gates or impose a cross-generation outreach cap.
- When the specified receipt/provider contract is absent, conflicting or untestable, **stop and return the gap to moda_architect**; do not invent an approximation, copy a Shared schema locally or broaden the task to another repo. System-test tasks are terminal and may not gate implementation tasks.


## Work Items

- [ ] Wire the typed recommendation result from WOOCOMMERCE-007 into a durable-across-redirect, bounded WC-session notice for Classic and Blocks.
- [ ] Implement explicit original-versus-offered coupon choice with nonce, session binding, cartHash and one-time expiry.
- [ ] Reapply/reject offered code under Woo live policy on choice; preserve originals on failed attempt and show actual recalculated totals.
- [ ] Add real Classic and Blocks integration tests for notices, choice, expiry, double submit and changed cart; no scanner/GET effects.

## Interfaces / Contracts

**Input:** the exact internal PHP result `CheckoutOutreachCouponRestorer::apply_outreach_offer()` from WOOCOMMERCE-007 (`outcome`, `recommendedCode`, `originalAppliedCodes`, `currentAppliedCodes`, `rejectionReason`, `totalsRecalculated`). The presenter has no API credentials and cannot call CommerceAgent.

**Session-only choice state (after confirmed restore, never on GET):**

```php
[
    'recoveryId' => 'recovery_456',
    'code' => 'EXTRA15',
    'originalCodes' => ['SAVE10'],
    'cartHash' => 'actual-WC-cart-hash-after-restoration',
    'createdAt' => 1793330000, // illustrative Unix timestamp
]
```

**Same-origin user action:**

```text
POST <store checkout page>
moda_interact_outreach_coupon_choice=try_offered
_wpnonce=<session-bound action nonce>
```

The `code`, `recoveryId`, original codes and timestamp come **only from server-side WC session state**, not POST fields. Validate `nonce` through WordPress standard `wp_verify_nonce` and bind the state to the active Woo session. The submitted action must not repeat the bearer link resolve.

**Display matrix:**

| Result | Shopper sees |
|---|---|
| APPLIED | Woo applied code + recalculated total |
| ALREADY_APPLIED | One applied coupon; no duplicate |
| REJECTED (confirmed expiry) | “Offered coupon has expired”; recalculated total |
| REJECTED (other/unknown) | “Offered coupon cannot be applied”; recalculated total |
| CONFLICT_REQUIRES_CHOICE | Original coupon still applied + opt-in “Try offered code instead” action |
| AUTOMATIC_NOT_FORCED | Normal recalculated totals; no claim of guaranteed automatic savings |
| NOT_APPLICABLE | Original checkout unaffected; no claim that alternative-product discount applies |
| UNVERIFIABLE | Neutral offer-unverifiable notice; no code applied |
| NO_OFFER | No promotional notice |

## Dependencies

- `ARCH-053-WOOCOMMERCE-007` — typed offer-restoration outcome implemented and accepted.
- `ARCH-053-WOOCOMMERCE-006` — existing original-coupon notice system accepted.

## Enables

- `ARCH-053-SYSTEM-TEST-003` — terminal integration certification.

## Acceptance Criteria

- [ ] Both Classic and Checkout Blocks display invalid/expired recommendation notices *after redirect* with correct current total.
- [ ] Multiple original coupons are never silently removed; a stacking conflict defaults to originals and offers an explicit nonce-protected choice.
- [ ] Choice may not be replayed, injected via query string, used after cart change/timeout or obtained from a GET scanner.
- [ ] An expired recommended code at switch-time does not replace the original coupon or claim successful discount.
- [ ] No customer-facing raw token, cross-tenant data, unapproved Meta text or HTML injection is possible; notices are escaped/translatable.
- [ ] No new discount engine, no merchant settings mutation, no recovery-generation creation from the UI alone.

## Validation

- [ ] `composer test` with choice and notice tests and declared `composer lint`
- [ ] Real WooCommerce Classic and Checkout Blocks UI integration with redirect/reload, WC session expiry, nonce failures and cart-change races
- [ ] Code injection/escape tests and `git diff --check`

## Stop Condition

When all defined Work Items, Acceptance Criteria and Validation are satisfied, update only this task's authorized metadata and Completion Report, set `status: review`, return to `moda_architect` and **STOP**. Do not begin Enabled tasks, self-accept, create new tasks, modify a sibling repository or merge/push main.

## Implementation Notes

Use Woo's native cart API for coupon changes and core Blocks-compatible extension surfaces, not ad hoc manipulation of its React DOM. If an extension adds unavoidable new assets, enumerate and test only these UI assets and report any broader dependency before implementation.

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
