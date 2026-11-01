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
status: complete
priority: 65
executor: null
claimed_at: null
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

- [x] Full `composer test -- --do-not-cache-result` ran 325 tests, 2467 assertions, with 2 errors, 4 failures and 3 warnings. All six failures are the same consent/navigation test identities recorded in the untouched baseline during Attempt 1; the changed task tests passed. The focused post-fix coupon/cart suite also passed (13 tests, 68 assertions). Details are below.
- [x] `composer lint`, PHP syntax checks for changed PHP files, Node syntax checks for both changed integration files, and `git diff --check` passed. The lint script no longer references the absent `tests/integration/checkout-consent-saved-block-variant.php`.
- [x] The focused real WordPress Classic+Blocks restore integration passed, including expired/rejected originals, stackable offer application, group-conflict rollback, and a v1 resolver HTTP 503. The disposable task-owned WordPress environment was stopped after the run.

## Stop Condition

When all defined Work Items, Acceptance Criteria and Validation are satisfied, update only this task's authorized metadata and Completion Report, set `status: review`, return to `moda_architect` and **STOP**. Do not begin Enabled tasks, self-accept, create new tasks, modify a sibling repository or merge/push main.

## Implementation Notes

The controller/restorer should have **one** final cart state for `CheckoutCapture` to snapshot. Reuse established suppression/rollback functionality; do not add a second status transition in the plugin. UI on expired/offered-code and opt-in replacement choices belongs to WOOCOMMERCE-008.

## Completion Report

### Status

Implementation complete for Attempt 2 and submitted for formal architect review. The integration-discovered coupon-state defect is fixed and the focused real WordPress restore scenarios pass. The full PHP suite still has the unrelated baseline errors and failures listed below; the task-specific tests pass.

### Files Changed

`composer.json`; `includes/Api/WooRestoreOfferContracts.php`; `includes/Api/WooRestoreResolveResponseValidator.php`; `includes/Checkout/CheckoutOutreachCouponRestorer.php`; `includes/Checkout/CheckoutCartRestorer.php`; `includes/Checkout/CheckoutCouponRestorer.php`; `includes/Checkout/CheckoutCouponOutcomeHandler.php`; `includes/Checkout/CheckoutResumeController.php`; `tests/WooRestoreOfferContractsTest.php`; `tests/CheckoutOutreachCouponRestorerTest.php`; `tests/CheckoutCartRestorerTest.php`; `tests/CheckoutCouponOutcomeHandlerTest.php`; `tests/CheckoutResumeControllerTest.php`; `tests/integration/run-wordpress.mjs`; `tests/integration/scenarios/checkout-wordpress.mjs`.

### Work Completed

Added strict offer-union validation while retaining the existing strict v1 response and cart-snapshot checks. The confirmed POST passes the validated offer to the existing cart restore operation after original coupons. Native Woo coupon application is used for code offers; automatic offers are never forced, alternatives leave coupons/products unchanged, and rejected/conflicting groups roll back to the successfully applied original set. The restored coupon state is recalculated once before the existing final capture. Typed offer results are handed to the existing private outcome handler, which logs bounded categories/counts without coupon values. Controller/provider failures leave the current cart protected by the existing rollback boundary.

Attempt 2 fixed a real WooCommerce rollback edge case found by the WordPress integration. `remove_coupon()` unsets numeric entries from Woo's applied-coupon array, leaving sparse numeric indexes. The offer restorer now normalizes the live values before validating the state, so a rejected group can remove tentative codes, reapply the original coupon, and keep the restored snapshot basket. A focused unit regression covers sparse indexes. The integration runner also has a restore-only mode to execute this task's real scenarios without waiting on unrelated order-lifecycle checks; its 503 case verifies that a v1 provider error preserves the visitor's basket.

Paired task worktrees and synchronization evidence:

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-WOOCOMMERCE-007`; branch `task/ARCH-053-WOOCOMMERCE-007`; attempt-start HEAD `9c5022d70c610836729e37da1653e094575c0a1a`; launcher claim commit `cab705ca196172dd7e6b1f4108a896d387dd99c6` was pushed before implementation began.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-WOOCOMMERCE-007`; branch `task/ARCH-053-WOOCOMMERCE-007`; attempt-start HEAD `df3a1ae2e0b0d65759cdb597af5e753441aeec28`; no submodules were required. The prepared launcher synchronized both task branches before claiming Attempt 1.

Attempt 2 synchronization:

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-WOOCOMMERCE-007`; branch `task/ARCH-053-WOOCOMMERCE-007`; synchronized attempt-start HEAD `ea1c30dfc0ea9f0f070e562f418bb556cf7290fe`; launcher claim commit `6e73db94f3adf6eac7ff4b0b53aa1776ca6e0029` was pushed before implementation began.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-WOOCOMMERCE-007`; branch `task/ARCH-053-WOOCOMMERCE-007`; synchronized attempt-start HEAD `08ed62f2854a65d7570644462a0a2cbcfdec6276`, including current `origin/main`; no submodules were required.

### Validation Results

Validation was run in an environment with PHP, Composer, Node dependencies and Docker available.

- Focused post-fix command `composer test -- --do-not-cache-result --filter 'CheckoutOutreachCouponRestorerTest|CheckoutCartRestorerTest'` — passed, 13 tests and 68 assertions.
- Full `composer test -- --do-not-cache-result` — 325 tests, 2467 assertions, 2 errors, 4 failures and 3 warnings. The same two errors and four failures identified against the untouched origin/main baseline in Attempt 1 remain in unchanged consent/navigation tests: `CheckoutConsentCheckboxTest::test_classic_uses_only_native_checkbox_without_a_withdrawal_button` and `CheckoutConsentCheckboxTest::test_blocks_registers_native_field_at_woocommerce_init_on_checkout` (errors); `CheckoutConsentCaptureTest::test_native_checkout_field_changes_cannot_create_consent_hooks`, `CheckoutConsentPresentationTest::test_request_scoped_local_decision_is_shared_without_blocking_checkout`, `PluginTest::test_native_navigation_checks_merchant_capability_and_only_loads_app_assets`, and `PluginTest::test_assets_load_only_on_the_woocommerce_admin_screen` (failures). No task-owned test failed.
- `composer lint` — passed after removing the stale allowlist entry for `tests/integration/checkout-consent-saved-block-variant.php`, which is absent from both the task branch and `origin/main`.
- Direct PHP lint passed for changed/new PHP source and tests. `git diff --check` passed. Node `--check` passed for `tests/integration/scenarios/checkout-wordpress.mjs`.
- `MODA_CHECKOUT_TEST_DISPOSABLE=1 WP_ENV_PORT=8891 npm run test:integration:wordpress -- --restore-only` — passed with `ARCH-053 restore-only integration PASS`. This exercised live Woo Classic and Blocks restore paths, expired and rejected original coupons, confirmed offer application, group conflict rollback preserving the snapshot and original coupon, and v1 resolver HTTP 503 preserving the current visitor basket. The task-owned WordPress site was stopped after validation.
- The repository-wide WordPress runner was also attempted but stalled in an unrelated order-lifecycle setup before reaching coupon restoration; the new restore-only mode isolates the required task scenarios. It passed.

### Deviations

Two narrow support changes extend the existing original-coupon restorer with an optional deferred totals calculation and the existing coupon outcome handler with bounded offer-outcome logging. These are needed to run exactly one totals calculation after both original and outreach coupon processing and to hand the typed offer outcome to the existing private presenter. The lint allowlist also dropped one pre-existing entry for a nonexistent integration file. Attempt 2 added sparse-array normalization, its regression test, and a restore-only WordPress runner mode with an explicit provider-outage case.

### Assumptions

Defined from the 2026-10-30 uploaded snapshot. Re-read current task and repository HEAD after launcher preparation.

### Unresolved Issues

The full PHP suite retains the known baseline errors and failures listed above. No task-specific test failures remain. WOOCOMMERCE-008 remains pending until architect review and acceptance.

### Architectural Concerns

Escalate contract or ownership gaps instead of inventing a new transport or persistence location.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 resolves the previous rollback defect: WooCommerce may leave sparse numeric indexes in its applied-coupon list after removing tentative offer codes. The restorer now normalizes live coupon values before validating and restoring the original set. The regression covers sparse indexes, and the focused live WordPress scenarios verify confirmed offer application, group-conflict rollback preserving the original basket and coupon, expired/rejected original coupons, and a v1 resolver 503 preserving the visitor basket. The implementation otherwise follows the strict v1 response, native Woo validation, one totals recalculation, and private bounded diagnostics requirements.

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
- `tests/integration/run-wordpress.mjs`
- `tests/integration/scenarios/checkout-wordpress.mjs`

### Validation Reviewed

Reviewed Attempt 2's reported focused coupon/cart suite (13 tests, 68 assertions), full suite with only the six documented baseline failures, `composer lint`, PHP syntax checks, `git diff --check`, Node syntax checks, and the restore-only WordPress Classic+Blocks run covering expiry/rejection, stackable offer application, group rollback, and v1 HTTP 503. No tests were rerun during this review.

### Architecture Conformance

Accepted. Attempt 2 fixes the integration-discovered sparse-array rollback defect and provides the required live restore integration evidence. The documented full-suite failures match the untouched baseline.

### Follow-up

The Attempt 1 validation finding is resolved in Attempt 2. `ARCH-053-WOOCOMMERCE-008` is Ready now that this dependency is Complete; `ARCH-053-SYSTEM-TEST-003` remains Pending on its other prerequisites.
