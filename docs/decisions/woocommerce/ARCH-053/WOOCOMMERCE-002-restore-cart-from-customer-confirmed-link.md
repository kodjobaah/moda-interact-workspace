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
status: in_progress
priority: 50
executor: copilot
claimed_at: 2026-10-31T14:15:41Z
attempt: 1
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

- [ ] Build no-mutation GET landing and explicit protected POST; test link preview / scanner.
- [ ] Add server-side install-auth API resolve client with strict response validation and errors.
- [ ] Implement all-or-nothing core product restoration for snapshots with no applied coupons, current totals recalculation, session rebind + exactly one activity enqueue + wc_get_checkout_url redirect; reject coupon-bearing restore until WOOCOMMERCE-005.
- [ ] Exercise stale link, cross-device, existing-cart replace confirmation and rollback on failure, asserting no Moda error/notice appears on the storefront and real failure details remain in protected PHP diagnostics.

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

- [ ] Build no-mutation GET landing and explicit protected POST; test link preview / scanner.
- [ ] Add server-side install-auth API resolve client with strict response validation and errors.
- [ ] Implement all-or-nothing core product restoration for snapshots with no applied coupons, current totals recalculation, session rebind + exactly one activity enqueue + wc_get_checkout_url redirect; reject coupon-bearing restore until WOOCOMMERCE-005.
- [ ] Exercise stale link, cross-device, existing-cart replace confirmation and rollback on failure, asserting no Moda error/notice appears on the storefront and real failure details remain in protected PHP diagnostics.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] `composer test` with targeted WC restore/controller tests
- [ ] `npm run test:integration:wordpress` with WC Classic/Blocks cross-device and confirmed-POST/no-coupon conditions; report environment gaps
- [ ] `composer lint`, plugin build if changed assets, `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

The WordPress confirmation endpoint must bind to `home_url('/')` including merchant subpath. For `/checkout-link/` native core behavior, do not delegate full restoration to it because it can replace cart automatically on GET, expose coupons and lose recovery identity. Use native `WC_Cart` methods; allow externally provided Woo extensions only after independently proven safe.

## Completion Report

### Status

Not Started

### Files Changed

None — portable task definition only.

### Work Completed

Not Started.

### Validation Results

Not Run — no implementation claimed.

### Deviations

None.

### Assumptions

Design reconciled against uploaded 2026-10-30 07:59 source snapshot; re-check source and prior task acceptance before implementation.

### Unresolved Issues

None asserted as executed; dependencies must be materialised/accepted.

### Architectural Concerns

Return any cross-service schema/provider/transaction concern to `moda_architect` before improvising.

## Architect Review

### Review Status

Pending

### Review Notes

Not Reviewed — task not executed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.
