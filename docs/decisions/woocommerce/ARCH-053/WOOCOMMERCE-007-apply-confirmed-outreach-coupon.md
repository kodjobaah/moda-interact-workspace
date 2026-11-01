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
status: in_progress
priority: 65
executor: codex
claimed_at: 2026-11-01T16:18:29Z
attempt: 2
depends_on:
- ARCH-052-SHARED-012
- ARCH-053-API-003
- ARCH-053-WOOCOMMERCE-005
- ARCH-053-WOOCOMMERCE-006
enables:
- ARCH-053-WOOCOMMERCE-008
created: 2026-10-30
updated: 2026-11-01
---

# ARCH-053-WOOCOMMERCE-007 — Apply confirmed outreach checkout coupon through native Woo validation

## Architecture

`ARCH-053` — `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`, coordinated by `moda_architect`. Defined but **not materialised**; no branch, worktree, commit, push or acceptance is claimed.

## Objective

On a customer-confirmed restore POST, consume the first and only offer-aware resolver v1 response and **attempt the checkout coupon actually promised in the initial WhatsApp outreach**, after original coupons, without overriding WooCommerce validation or silently removing a previously applied original coupon.

## Context

WOOCOMMERCE-002 restores products using the new single v1 server-to-server resolver; WOOCOMMERCE-005 reattempts original `snapshot.appliedCouponCodes`, and WOOCOMMERCE-006 privately handles original coupon rejections without storefront errors. SHARED-001 defines `outreachOffer` as mandatory in v1; API-003 supplies its verified confirmed-message value. This task **extends those**, not creates a second cart restore or discount engine. No older restoration resolver or pre-offer v1 consumer exists; do not create compatibility code.

## Scope

In `moda-interact-woocommerce`, update only:

- `includes/Api/ModaApiClient.php`: extend the existing server-side `resolveWooRecoveryLink` operation to submit `schemaVersion:'woo.restore.resolve.v1'`; make exactly one server-side v1 resolve call per confirmed POST. API bearer stays server-side.
- **Create** `includes/Api/WooRestoreOfferContracts.php`: strictly validate response v1 discriminator and fields against the SHARED-001 fixture; retain existing base snapshot verification from WooCommerce-002; no permissive success on missing `outreachOffer`.
- **Create** `includes/Checkout/CheckoutOutreachCouponRestorer.php`: implement the exact PHP interface and result below, calling only Woo native coupon/cart APIs.
- `includes/Checkout/CheckoutCartRestorer.php`: invoke recommended coupon application exactly once after products and the original-coupon operation, *before final capture*; preserve rollback and capture suppression from WOOCOMMERCE-002.
- `includes/Checkout/CheckoutResumeController.php`: pass the v1 result through the same confirmed-POST flow and hand off the typed offer outcome to the existing WOOCOMMERCE-006 presenter (WOOCOMMERCE-008 completes UI).
- Focused `tests/CheckoutOutreachCouponRestorerTest.php`, `tests/WooRestoreOfferContractsTest.php` and existing relevant controller/cart tests. Register new PHP source/tests in `composer.json` lint only if required by its existing explicit allowlist.

## Out of Scope

No discount discovery, coupon creation, modified expiry or usage constraints, original-cart URL encoding, new WordPress endpoint/bearer, API schema/business policy change, Meta template send, alternative-product insertion or customer-visible conflict-choice UI (WOOCOMMERCE-008 owns that).

## Requirements

### Confirmed multi-code group application — normative 30 October 2026

Consume the published `CHECKOUT_OFFERS` v1 branch (2..3 source-verified entries), as well as existing single-code/automatic variants. After explicit customer-confirmed restore, validate existing **original** applied coupons first using native Woo APIs; attempt each recommended CODE item in immutable sent order using `WC()->cart->apply_coupon()` (contain only Woo error notices originating from those **automatic** Moda attempts; no Moda error on the merchant checkout), never trust API's offer as proof of current Woo applicability. Automatic entries are informational and must never be forced into cart coupon state. If any recommended code fails/invalidates an original or any other recommended code, restore the original successfully applied coupon set, recalculate totals and return a typed **GROUP_CONFLICT / GROUP_REJECTED** outcome rather than persisting a partial advertised group. Do not silently remove originals or claim partial savings. Re-run live Woo validation after customer chooses any explicit alternative group in WOOCOMMERCE-008. Log bounded outcomes without coupon values.


- Keep the existing no-mutation GET and explicit nonce-protected confirmation POST. V1 resolver is called **after confirmation only**, using the original signed recovery link; no browser-side installation credentials, no external visitor contact/discount parameters.
- Restore product lines first. Reapply original coupons in their persisted order using WOOCOMMERCE-005. Only then process `outreachOffer`.
- `CHECKOUT_CODE`: attempt the exact code **once** through `WC()->cart->apply_coupon($code)` if not already applied (use Woo's canonical code comparisons). Inspect the resulting actual `WC()->cart->get_applied_coupons()` and recalculated totals. Never treat API `providerDiscountId` or the WhatsApp text as proof of current eligibility; the code may expire, be disabled, be limited or become inapplicable.
- `CHECKOUT_AUTOMATIC`: **never** call `apply_coupon`, fabricate a coupon, force a fee/price, add a WC filter, or assert savings. Recalculate native Woo totals and return a neutral `AUTOMATIC_NOT_FORCED` result; if the installed provider gives no reliable discount evidence, do not claim it applied.
- `ALTERNATIVE_PRODUCT`: do not insert promoted items or apply its discount to the abandoned basket; return `NOT_APPLICABLE` with original basket untouched. `NONE/NO_CONFIRMED_OFFER` is a no-op; `NONE/UNVERIFIABLE` produces a private diagnostic outcome for WOOCOMMERCE-008 without inventing a code.
- If the recommended code is **already present** in original applied codes, do not apply twice or show a duplicate rejection; return `ALREADY_APPLIED` only after Woo confirms it is still in the cart.
- If Woo applying the recommendation removes one or more previously successful original coupons due to stacking/individual-use rules, **undo the tentative recommendation**, restore the original applied set under Woo validation, recalculate, and return `CONFLICT_REQUIRES_CHOICE` with current original basket intact. An irrecoverable mid-apply/rollback error must take the existing protected cart rollback path; do not declare success after losing an original coupon.
- Business rejections (expired, minimum spend, usage limits, excluded product, non-stackable) return typed `REJECTED`, but do not block checkout when product restoration succeeds. Do not infer `EXPIRED` unless Woo reliably distinguishes it. Recalculate with `WC()->cart->calculate_totals()` once after coupon processing. Do not restore historic prices, shipping or tax.
- Suppress intermediate checkout capture during every mutation. Emit **one** fresh checkout activity after the final cart and coupon state is settled; preserve checkout key/generation and the existing ARCH-048 resumption flow. No second outreach, charge or new recovery inside WordPress.

### Repository / execution safeguards

- Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the launcher preparation packet and the parent ARCH-053 architecture before claiming. Work from dedicated, synchronized mirrored task worktrees; record both physical paths, initial SHAs and validation in the Completion Report. A snapshot does not establish the developer's current branch/status.
- Only change the **permitted owning-repository files** in Scope and this task's own authorised task metadata/Completion Report. No `_index.md`, no unrelated code, no other agent's task, no production WhatsApp activation, no merge/push to `main`.
- WooCommerce PHP executes on merchant-controlled WordPress servers and **must not import or implement** `@modainteract/moda-interact-shared/logging` (that npm export belongs only to hosted Moda Node processes). Use existing server-side plugin diagnostics (the current bounded `error_log()` pattern where applicable), not a new generic logger, `wc_add_notice()`, browser console output or shopper-visible HTML for Moda errors. Record a bounded event/reason and safe correlation identifier; preserve the original error message and relevant safe provider response details when available after redaction, without guessing a substitute cause. Never log bearer tokens, full restore URLs, coupon codes or customer PII. At storefront/controller boundaries catch and privately log unexpected errors, preserve or safely roll back the cart, and continue/redirect without Moda-originated error notices. At Action Scheduler and other retry-owning job boundaries, log and **propagate** retryable failures for durable retry/failure evidence; do not acknowledge them as success. Never globally suppress WordPress diagnostics or delete unrelated Woo notices.
- Keep checkout restoration read-only in the hosted API and cart-local in WooCommerce. Never have PHP query Moda PostgreSQL/Redis or an API handler change a visitor cart. Never create a new discount, extend an expired coupon, use ARCH-052 discovery code, bypass merchant consent/STOP/order/final provider gates or impose a cross-generation outreach cap.
- When the specified receipt/provider contract is absent, conflicting or untestable, **stop and return the gap to moda_architect**; do not invent an approximation, copy a Shared schema locally or broaden the task to another repo. System-test tasks are terminal and may not gate implementation tasks.


## Work Items

- [x] Parse the single strict v1 response with required `outreachOffer` exactly as SHARED-001 defines; no alternate version request.
- [x] Implement isolated outreach coupon restorer; preserve verified original coupons under stacking conflict and native totals.
- [x] Integrate it after WOOCOMMERCE-005 without another restore pipeline, capture event, cart replacement or URL issuer.
- [x] Add tests for all five offer kinds, valid/invalid code, original+recommended conflict, duplicate code, failed rollback and provider/API outage.

## Interfaces / Contracts

**Inputs from API-003, parsed on the PHP server:**

```json
{
  "schemaVersion": "woo.restore.resolve.v1",
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
 * @param array<string,mixed> $validatedOffer  Strict v1 outreachOffer union
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

The reason is **bounded native Woo evidence** only: known `EXPIRED` when reliably identified, otherwise general `NOT_APPLICABLE`; no claim from guesswork. `rejectionReason` is strictly for private server-side diagnostics and decision flow, not customer notice presentation; log only bounded categories, not raw provider or coupon content. The `recommendedCode` may be used only in transient **WC-session-only** offer-choice state (never customer-facing error notices); it must not be copied into recovery URL/query params or logging.

**Examples:**

| Original | Outreach | Woo current outcome | Result |
|---|---|---|---|
| `SAVE10` valid | `EXTRA15` valid and stackable | Both remain applied | `APPLIED` |
| `SAVE10` expired | `EXTRA15` valid | Only `EXTRA15` applied | `APPLIED`; original rejection privately recorded; no generated storefront notice |
| `SAVE10` valid | `EXTRA15` expired | Only `SAVE10` applied | `REJECTED`; offered rejection privately recorded; no generated storefront notice |
| `SAVE10` valid | `EXTRA15` individually used | Original retained, offer not applied | `CONFLICT_REQUIRES_CHOICE` |
| `EXTRA15` original and valid | recommended `EXTRA15` | One copy remains | `ALREADY_APPLIED` |
| `SAVE10` valid | `CHECKOUT_AUTOMATIC` | Native totals only | `AUTOMATIC_NOT_FORCED` |
| Any | `ALTERNATIVE_PRODUCT` | No new product or coupon | `NOT_APPLICABLE` |

## Dependencies

- `ARCH-053-API-003` — accepted v1 offer-aware read with provenance.
- `ARCH-053-WOOCOMMERCE-005` — accepted original coupon reapplication.
- `ARCH-053-WOOCOMMERCE-006` — accepted original-coupon private diagnostics and targeted error-notice containment.

## Enables

- `ARCH-053-WOOCOMMERCE-008`

## Acceptance Criteria

- [x] Code advertised in a **confirmed checkout** message is attempted on the shopper's current restored cart, but never guaranteed.
- [x] Valid original coupons remain applied unless shopper expressly chooses a different combination; Woo still applies all current restrictions.
- [x] An invalid recommended code cannot block otherwise valid basket restoration or replace/extend an expired coupon.
- [x] Automatic and alternative-product offers never force a discount/coupon on the original checkout.
- [x] GET previews do not resolve offers, mutate a cart or create new recovery activity; confirmed restore produces exactly one final update.
- [x] No new persisted offer table, no new provider-send, no checkout URL token/coupon logging.

## Validation

- [x] Focused PHPUnit source+controller tests passed: 25 tests, 153 assertions. The full `composer test -- --do-not-cache-result` suite ran 315 tests (2 errors, 4 failures, 3 warnings); the same failure identities and warning/error counts occur on the untouched baseline (313 tests, 2 errors, 4 failures, 3 warnings), so no new suite regressions were observed. Details are below.
- [x] `composer lint` passed after removing its entry for the absent `tests/integration/checkout-consent-saved-block-variant.php`; PHP lint passed for changed/new PHP files. `git diff --check` and Node syntax validation of the modified integration scenario passed.
- [ ] WordPress Classic+Blocks integration and the real expiry/stacking/rollback/v1-HTTP integration scenarios remain unverified. Docker started the task-owned environment, but its host endpoint at `localhost:8891` did not respond during initial setup; the run was interrupted and the task-owned containers were stopped.

## Stop Condition

When all defined Work Items, Acceptance Criteria and Validation are satisfied, update only this task's authorized metadata and Completion Report, set `status: review`, return to `moda_architect` and **STOP**. Do not begin Enabled tasks, self-accept, create new tasks, modify a sibling repository or merge/push main.

## Implementation Notes

The controller/restorer should have **one** final cart state for `CheckoutCapture` to snapshot. Reuse established suppression/rollback functionality; do not add a second status transition in the plugin. UI on expired/offered-code and opt-in replacement choices belongs to WOOCOMMERCE-008.

## Completion Report

### Status

Implementation complete for Attempt 1 and submitted for formal architect review. Focused PHPUnit and lint now run successfully. The full suite's failures match the untouched baseline, and WordPress integration remains unverified because the task environment's host endpoint did not respond during setup.

### Files Changed

`composer.json`; `includes/Api/WooRestoreOfferContracts.php`; `includes/Api/WooRestoreResolveResponseValidator.php`; `includes/Checkout/CheckoutOutreachCouponRestorer.php`; `includes/Checkout/CheckoutCartRestorer.php`; `includes/Checkout/CheckoutCouponRestorer.php`; `includes/Checkout/CheckoutCouponOutcomeHandler.php`; `includes/Checkout/CheckoutResumeController.php`; `tests/WooRestoreOfferContractsTest.php`; `tests/CheckoutOutreachCouponRestorerTest.php`; `tests/CheckoutCartRestorerTest.php`; `tests/CheckoutCouponOutcomeHandlerTest.php`; `tests/CheckoutResumeControllerTest.php`; `tests/integration/scenarios/checkout-wordpress.mjs`.

### Work Completed

Added strict offer-union validation while retaining the existing strict v1 response and cart-snapshot checks. The confirmed POST passes the validated offer to the existing cart restore operation after original coupons. Native Woo coupon application is used for code offers; automatic offers are never forced, alternatives leave coupons/products unchanged, and rejected/conflicting groups roll back to the successfully applied original set. The restored coupon state is recalculated once before the existing final capture. Typed offer results are handed to the existing private outcome handler, which logs bounded categories/counts without coupon values. Controller/provider failures leave the current cart protected by the existing rollback boundary.

Paired task worktrees and synchronization evidence:

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-WOOCOMMERCE-007`; branch `task/ARCH-053-WOOCOMMERCE-007`; attempt-start HEAD `9c5022d70c610836729e37da1653e094575c0a1a`; launcher claim commit `cab705ca196172dd7e6b1f4108a896d387dd99c6` was pushed before implementation began.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-WOOCOMMERCE-007`; branch `task/ARCH-053-WOOCOMMERCE-007`; attempt-start HEAD `df3a1ae2e0b0d65759cdb597af5e753441aeec28`; no submodules were required. The prepared launcher synchronized both task branches before claiming Attempt 1.

### Validation Results

Validation was run in an environment with PHP, Composer, Node dependencies and Docker available.

- Focused PHPUnit command `composer test -- --do-not-cache-result --filter 'WooRestoreOfferContractsTest|CheckoutOutreachCouponRestorerTest|CheckoutCartRestorerTest|CheckoutCouponOutcomeHandlerTest|CheckoutResumeControllerTest'` — passed, 25 tests and 153 assertions.
- Full `composer test -- --do-not-cache-result` — 315 tests, 2394 assertions, 2 errors, 4 failures and 3 warnings. A scratch checkout of the untouched implementation `origin/main` baseline had 313 tests, 2408 assertions and the same 2 errors, 4 failures and 3 warnings. The unchanged baseline identities are `CheckoutConsentCheckboxTest::test_classic_uses_only_native_checkbox_without_a_withdrawal_button` and `CheckoutConsentCheckboxTest::test_blocks_registers_native_field_at_woocommerce_init_on_checkout` (errors); `CheckoutConsentCaptureTest::test_native_checkout_field_changes_cannot_create_consent_hooks`, `CheckoutConsentPresentationTest::test_request_scoped_local_decision_is_shared_without_blocking_checkout`, `PluginTest::test_native_navigation_checks_merchant_capability_and_only_loads_app_assets`, and `PluginTest::test_assets_load_only_on_the_woocommerce_admin_screen` (failures). No additional test failures were observed relative to baseline.
- `composer lint` — passed after removing the stale allowlist entry for `tests/integration/checkout-consent-saved-block-variant.php`, which is absent from both the task branch and `origin/main`.
- Direct PHP lint passed for changed/new PHP source and tests. `git diff --check` passed. Node `--check` passed for `tests/integration/scenarios/checkout-wordpress.mjs`.
- WordPress integration runner — attempted with task-owned containers on port 8891. The initial site setup stalled because the local host endpoint did not respond. The runner was stopped and only this task's containers were cleaned up. The updated integration scenario therefore has syntax validation only; its current-expiry, stacking, rollback and v1 HTTP assertions have not run.

### Deviations

Two narrow support changes extend the existing original-coupon restorer with an optional deferred totals calculation and the existing coupon outcome handler with bounded offer-outcome logging. These are needed to run exactly one totals calculation after both original and outreach coupon processing and to hand the typed offer outcome to the existing private presenter. The lint allowlist also dropped one pre-existing entry for a nonexistent integration file. The checkout integration scenario now covers the confirmed code-offer and group-conflict cases, but could not be executed because local WordPress setup did not become reachable.

### Assumptions

Defined from the 2026-10-30 uploaded snapshot. Re-read current task and repository HEAD after launcher preparation.

### Unresolved Issues

WordPress integration remains unverified because the task-owned local site endpoint did not respond during setup. The full PHP suite has known baseline failures listed above; focused task tests and lint pass. WOOCOMMERCE-008 remains pending until architect review and acceptance.

### Architectural Concerns

Escalate contract or ownership gaps instead of inventing a new transport or persistence location.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Static review found the implementation consistent with the specified v1 offer handling: native Woo coupon validation is used, recommended groups are not left partially applied, original successful coupons are restored after conflicts, and coupon values are excluded from the offer outcome diagnostics. No implementation defect was identified in the inspected paths.

The task's Validation section still has the WordPress Classic+Blocks integration and real current-expiry, stacking, rollback, and v1-HTTP scenarios unchecked. The report confirms the integration scenario only passed syntax validation because the task-owned WordPress host did not respond. Those integration scenarios are an explicit validation item, so the task cannot be accepted yet.

### Reviewed Files

- `includes/Api/WooRestoreOfferContracts.php`
- `includes/Api/WooRestoreResolveResponseValidator.php`
- `includes/Api/ModaApiClient.php`
- `includes/Checkout/CheckoutOutreachCouponRestorer.php`
- `includes/Checkout/CheckoutCartRestorer.php`
- `includes/Checkout/CheckoutCouponRestorer.php`
- `includes/Checkout/CheckoutCouponOutcomeHandler.php`
- `includes/Checkout/CheckoutResumeController.php`
- `tests/WooRestoreOfferContractsTest.php`
- `tests/CheckoutOutreachCouponRestorerTest.php`
- `tests/CheckoutCartRestorerTest.php`
- `tests/CheckoutCouponOutcomeHandlerTest.php`
- `tests/CheckoutResumeControllerTest.php`
- `tests/integration/scenarios/checkout-wordpress.mjs`

### Validation Reviewed

Reviewed the report of 25 focused PHPUnit tests (153 assertions), baseline-matched full-suite failures, `composer lint`, PHP syntax checks, `git diff --check`, and Node syntax validation. The WordPress integration and its live expiry/stacking/rollback/v1-HTTP assertions were not run. No tests were rerun during this review.

### Architecture Conformance

The implementation conforms based on static inspection. Acceptance is blocked only on the explicitly required integration validation, which remains unverified.

### Follow-up

Keep Attempt 1 recorded and return the task to Ready. Run the task-owned WordPress Classic+Blocks integration scenario, including current expiry, stackable offer application, group conflict/rollback preserving original coupons, and v1 HTTP error handling. Confirm the runner reaches the local site and that cleanup leaves no task-owned containers running. Update the unchecked Validation item and resubmit for review after the required scenarios pass.
