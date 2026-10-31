---
id: ARCH-053-WOOCOMMERCE-002
architecture_id: ARCH-053
title: Restore products after customer-confirmed Woo checkout link
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-053-WOOCOMMERCE-001
- ARCH-053-API-002
enables:
- ARCH-053-SYSTEM-TEST-001
- ARCH-053-WOOCOMMERCE-005
created: 2026-10-29
updated: 2026-10-31
---

# ARCH-053-WOOCOMMERCE-002 — Restore products after customer-confirmed Woo checkout link

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Restore products after customer-confirmed Woo checkout link. One bounded outcome in `moda-interact-woocommerce` owned by `moda_woocommerce`.

## Context

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Create narrowly owned `includes/Checkout/CheckoutResumeController.php`, `CheckoutCartRestorer.php` and registration in `includes/Runtime.php` or existing plugin bootstrap; extend `includes/Api/ModaApiClient.php` with `resolveWooRecoveryLink()` sending only authenticated POST to `/v1/woocommerce/recovery-restore/resolve` (no browser-to-Moda credentials). Add dedicated PHP and LocalWP/WP-env integration tests.
- Route merchant-root GET `?moda_interact_resume=1&r=<recoveryId>&t=<43-char-token>` to a minimal customer-visible confirmation view. Send `Cache-Control: no-store` and `Referrer-Policy: no-referrer`, avoid third-party assets/analytics, mask token in diagnostics. GET and HEAD MUST NOT resolve/restore cart, set checkoutKey, enqueue activity, claim offer or confirm consent. A minimal guest session/CSRF nonce cookie may be established solely to authenticate the later POST; no cart/recovery changes are allowed. A clicked human action POST requires a Woo-session-tied nonce, same-origin safety and explicit **Replace current basket and continue** confirmation; double click is idempotent per visitor session.
- On valid POST, resolve via authenticated API and reject mismatched canonical installation, malformed response or unsupported snapshot; prevalidate all core simple/variation product IDs, parent-child relation, variation attributes, quantity bounds, stock/purchasability and extension item restrictions; no silently incomplete basket. For an expired/revoked/invalid link, preserve the visitor cart, privately record the reason and redirect to the normal merchant cart/checkout/home **without any Moda-generated error notice, banner, or query-string error marker**.
- Preserve existing cart until preflight passes; after explicit confirmation replace the whole basket with `WC()->cart->empty_cart()` and `add_to_cart($productId,$qty,$variationId,$attributes)`; suppress intermediate Moda checkout-capture hooks during mutation; on any mid-apply failure privately log the original failure, attempt restoration of the preexisting cart, record any rollback failure separately and return to a safe merchant cart/checkout/home **without displaying a Moda error or presenting partial restoration as success**. This task implements **products-only** restore for proven-empty `appliedCouponCodes: []` and must reject coupon-bearing snapshots without cart mutation until WOOCOMMERCE-005 owns actual coupon reapplication. Never restore old prices or totals.
- Rebind `CheckoutKey::SESSION_FIELD` to the original `checkoutKey` only after successful basket rebuild (do not restore customer billing/contact/consent), clear `moda_interact_checkout_last_capture_v1`, force fresh `CheckoutCapture::capture()` to enqueue a single durable resumption event; persist WC session/cookie, and `wp_safe_redirect(wc_get_checkout_url())`. Verify Classic and Checkout Blocks render the restored cart. Confirm failed enqueues are observable and retriable; do not claim that a redirect alone atomically closes old recovery.

## Out of Scope

No ARCH-052 promotion selection/coupon issuance, no gateway rewrite, no background state transitions or new persisted link issue service inside WordPress.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- Protect merchant cart/session against GET scanning, cross-device old-link restoration, forged POST, direct WC mutations without confirmed visitor consent, third-party referrer leaks, open redirects and 2-shop link mixing.
- Reject unsupported product types/options rather than cloning arbitrary serialized item data. Restored prices, taxes and shipping come from current Woo configuration. Coupon-bearing snapshots must fail closed until WOOCOMMERCE-005 is integrated; neither silently drop coupons nor invent eligibility.
- No new WordPress long-lived bearer token/transient store; only the existing WC session and bounded nonce evidence for visitor confirmation. No PHP credentials or internal checkoutKey in browser-visible HTML. If the customer clicks an already superseded link, never replace a newer basket.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- WooCommerce PHP executes on merchant-controlled WordPress servers and **must not import or implement** `@modainteract/moda-interact-shared/logging` (that npm export belongs only to hosted Moda Node processes). Use existing server-side plugin diagnostics (the current bounded `error_log()` pattern where applicable), not a new generic logger, `wc_add_notice()`, browser console output or shopper-visible HTML for Moda errors. Record a bounded event/reason and safe correlation identifier; preserve the original error message and relevant safe provider response details when available after redaction, without guessing a substitute cause. Never log bearer tokens, full restore URLs, coupon codes or customer PII. At storefront/controller boundaries catch and privately log unexpected errors, preserve or safely roll back the cart, and continue/redirect without Moda-originated error notices. At Action Scheduler and other retry-owning job boundaries, log and **propagate** retryable failures for durable retry/failure evidence; do not acknowledge them as success. Never globally suppress WordPress diagnostics or delete unrelated Woo notices.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [x] Build no-mutation GET landing and explicit protected POST; test link preview / scanner.
- [x] Add server-side install-auth API resolve client with strict response validation and errors.
- [x] Implement all-or-nothing core product restoration for snapshots with no applied coupons, current totals recalculation, session rebind + exactly one activity enqueue + wc_get_checkout_url redirect; reject coupon-bearing restore until WOOCOMMERCE-005.
- [x] Exercise stale link, cross-device, existing-cart replace confirmation and rollback on failure, asserting no Moda error/notice appears on the storefront and real failure details remain in protected PHP diagnostics.

The API resolver response is the single `woo.restore.resolve.v1` contract from SHARED-001 and **already contains** mandatory `outreachOffer` (including `NONE`). Parse the exact complete v1 response; do not use a pre-offer v1 response or invent v2. This task restores the original basket only; interpreting or attempting confirmed recommended codes belongs to WOOCOMMERCE-007 and conflict UI to WOOCOMMERCE-008. Preserve the typed result for that later owning task but **do not silently deploy an end-to-end checkout flow that discards a confirmed recommended coupon**. No separate resolver endpoint or second checkout session may be created.

## Interfaces / Contracts

Guest URL uses ARCH-053-BACKGROUND-003 format; POST API resolve from API-002 only (installation credentials in server). `woo.restore.resolve.v1` positive response per Shared fixture. Reuse CheckoutKey and current CheckoutActivityPublisher. Product identity and discounts are Woo's authority; archived CheckoutRecovery remains unchanged by the plugin.

## Dependencies

- `ARCH-053-WOOCOMMERCE-001` (must be architect-accepted Complete)
- `ARCH-053-API-002` (must be architect-accepted Complete)

## Enables

- `ARCH-053-SYSTEM-TEST-001`
- `ARCH-053-WOOCOMMERCE-005`

## Acceptance Criteria

- [x] Build no-mutation GET landing and explicit protected POST; test link preview / scanner.
- [x] Add server-side install-auth API resolve client with strict response validation and errors.
- [x] Implement all-or-nothing core product restoration for snapshots with no applied coupons, current totals recalculation, session rebind + exactly one activity enqueue + wc_get_checkout_url redirect; reject coupon-bearing restore until WOOCOMMERCE-005.
- [x] Exercise stale link, cross-device, existing-cart replace confirmation and rollback on failure, asserting no Moda error/notice appears on the storefront and real failure details remain in protected PHP diagnostics.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [x] `composer test` with targeted WC restore/controller tests
- [x] `npm run test:integration:wordpress` with WC Classic/Blocks cross-device and confirmed-POST/no-coupon conditions; report environment gaps
- [x] `composer lint`, plugin build if changed assets, `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

The WordPress confirmation endpoint must bind to `home_url('/')` including merchant subpath. For `/checkout-link/` native core behavior, do not delegate full restoration to it because it can replace cart automatically on GET, expose coupons and lose recovery identity. Use native `WC_Cart` methods; allow externally provided Woo extensions only after independently proven safe.

## Completion Report

### Status

Ready for Review

### Attempt 2 Resubmission

- Addressed the Architect's persistence-failure request. Checkout session values are snapshotted before the confirmed restore commit. If session persistence fails after cart replacement, the controller restores the previous session values, separately logs a failed rollback save, returns failure to `CheckoutCartRestorer`, and does not redirect as a successful restoration.
- Added `test_session_persistence_failure_rolls_back_cart_and_session_state`, exercising the POST restore route with a failing session save and verifying cart/session rollback and the safe failure redirect.
- `composer test -- --filter 'CheckoutCartRestorerTest|CheckoutResumeControllerTest|WooRestoreResolveResponseValidatorTest'`: PASS, 12 tests, 67 assertions, 1 existing test-harness warning.
- `composer lint`: PASS. `git diff --check`: PASS.
- Checkout-only WordPress integration on port 8887: PASS, including Classic and Blocks restore confirmation, safe redirects, cart replacement, replay protection, failure cases, and coupon lifecycle scenarios.
- Full `npm run test:integration:wordpress` on port 8887 started successfully and reached the checkout scenarios; `ARCH-053 confirmed Woo restore integration PASS` was reported. The command later exited non-zero in the unrelated shop-brand scenario because the persisted test site brand was `ARCH-053-WOOCOMMERCE-002` rather than its expected `ARCH049 Original Store`. A prior timed-out full run had interrupted fixture setup, so this is recorded as a contaminated-site full-suite failure, not a checkout restore failure.
- Port 8887 bound and started successfully. Ports 8886 and 8885 were not attempted because the requested fallback was for a startup/bind failure, which did not occur. No concurrent wp-env was started. The 8887 disposable environment was stopped after validation; no generated repository artifacts remain.
- The confirmation-page assertion was adjusted to allow same-origin absolute form actions while rejecting scripts and external origins. The Blocks rendering check now recognizes WooCommerce's emitted `blocks-checkout.js` asset.
- Attempt 2 implementation is committed and pushed on `task/ARCH-053-WOOCOMMERCE-002` at `333d8b5`; the task report is committed and pushed on the same-named parent branch at `56967b56`. Both worktrees were verified clean and synchronized with origin.

### Files Changed

Implementation repository files (commit `ceabf0ae24d9d9ced5f0f4beef0893828c81be73`):

- `composer.json`
- `includes/Api/ModaApiClient.php`
- `includes/Api/WooRestoreResolveResponseValidator.php`
- `includes/Checkout/CheckoutCapture.php`
- `includes/Checkout/CheckoutCartRestorer.php`
- `includes/Checkout/CheckoutResumeController.php`
- `includes/Runtime.php`
- `tests/CheckoutCartRestorerTest.php`
- `tests/CheckoutResumeControllerTest.php`
- `tests/WooRestoreResolveResponseValidatorTest.php`
- `tests/integration/run-wordpress.mjs`
- `tests/integration/scenarios/checkout-wordpress.mjs`
- `tests/integration/wordpress-api-fixture.mjs`

Parent repository: this task file only. Parent branch claim/base SHA before this report update: `be33164bde6162b7cfd3e6bd92f321483908e620`.

### Work Completed

- Added the no-mutation recovery-link landing and explicit same-origin, Woo-session/nonce-protected confirmation POST, with token-safe diagnostics and no shopper-facing Moda failure notices.
- Added installation-authenticated `woo.restore.resolve.v1` API resolution and strict complete-response validation.
- Added preflighted products-only basket restoration, coupon-bearing snapshot rejection, rollback on apply failure, checkout-key/session handling, capture suppression during mutation, and one fresh checkout activity capture after success.
- Added focused PHP coverage and real WordPress HTTP integration scenarios for Classic and Blocks checkout restore behavior.
- Committed and pushed the WooCommerce implementation branch at `ceabf0ae24d9d9ced5f0f4beef0893828c81be73`.

### Validation Results

- `source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-woocommerce.sh"`: PASS. Environment reported workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`, Node 24.19.0, PHP 8.5.11, Composer 2.10.3, Docker 29.7.2, and a reachable Docker daemon. Repository Node dependencies were restored with `npm ci` from `package-lock.json`; the lockfile remained unchanged.
- `composer lint`: PASS; all declared PHP syntax checks passed.
- `composer test -- --filter 'CheckoutCartRestorerTest|CheckoutResumeControllerTest|WooRestoreResolveResponseValidatorTest'`: PASS; 11 tests, 59 assertions, 1 unrelated test-harness warning.
- `composer test -- --display-warnings`: 234 tests, 1,779 assertions, 2 failures, 1 warning. The failures are `PluginTest::test_native_navigation_checks_merchant_capability_and_only_loads_app_assets` and `PluginTest::test_assets_load_only_on_the_woocommerce_admin_screen`; both expect built `build/index.js`/`build/index.css` assets. The `build/` directory is absent from `origin/main`, and both `tests/PluginTest.php` and `includes/Admin/Setup.php` are unchanged from `origin/main`. `Setup::register_scripts()` returns before enqueuing when those assets are absent, so no unrelated admin/build change was made.
- The single PHPUnit warning is the existing undefined `$GLOBALS['moda_interact_test_logger']` in the `wc_get_logger()` test stub at `tests/RecoveryPolicyControllerTest.php:14`, triggered across checkout/controller tests. That test file and the warning-producing stub are unchanged by this task.
- `npm run test:integration:wordpress`: BLOCKED before scenarios ran. The disposable wp-env image build succeeded, but startup failed with `Bind for :::8888 failed: port is already allocated`; exit code 1. No integration scenarios passed or were reached. The runner's stop/destroy calls reported that wp-env was not initialized.
- Integration cleanup: generated `tests/integration/.fixture-ca.pem` and isolated `WP_ENV_HOME` were removed. The run-created `wp-env-arch-053-woocommerce-002-a79a4f73_user-home` volume was removed. wp-env reported the project MySQL container running during startup, but the post-run filtered Docker inspection found no project containers; the `wp-env-arch-053-woocommerce-002-a79a4f73_mysql` data volume remains and was left untouched. Locally cached Docker images were retained.
- `git diff --check`: PASS.

### Deviations

- The two unrelated PluginTest failures remain because the repository baseline has no built admin assets; fixing that would expand this task into the admin build surface.
- WordPress runtime integration remains unverified because Docker could not bind host port 8888. It was not retried on another port.

### Assumptions

The API response follows the complete `woo.restore.resolve.v1` contract, including `outreachOffer`; this task preserves the typed response but does not apply recommended outreach coupons.

### Unresolved Issues

Run the WordPress integration in a disposable environment where the configured host port 8888 is available, then review the two baseline admin asset failures and the pre-existing PHPUnit warning separately.

### Architectural Concerns

None identified. No cross-repository contract, database, queue, or deployment changes were made.

## Architect Review

### Review Status

Changes Requested

### Review Notes

The implementation needs a rollback path when WooCommerce session persistence fails after the cart has been changed. In `includes/Checkout/CheckoutResumeController.php` lines 116-118, ensure the visitor's pre-restore cart/session state is restored on persistence failure; record rollback failure separately and do not report or redirect as though the restored basket succeeded. Add a focused regression test for this failure path.

Retry `npm run test:integration:wordpress` using host ports in this order: 8887, 8886, then 8885. Record each attempt and its result in the Completion Report.

### Reviewed Files

`includes/Checkout/CheckoutResumeController.php`

### Validation Reviewed

The Completion Report records the focused PHP tests and lint as passing. WordPress integration did not reach scenarios because port 8888 was unavailable; retry on 8887, 8886, then 8885 as noted above.

### Architecture Conformance

Changes Requested: handle cart/session persistence failure atomically from the shopper's perspective, and complete the requested WordPress integration retry before resubmitting for review.

### Follow-up

Implement and test rollback when session persistence fails, then rerun the WordPress integration on ports 8887, 8886, and 8885 in that order. Update this same task's Completion Report and return it for architect review.
