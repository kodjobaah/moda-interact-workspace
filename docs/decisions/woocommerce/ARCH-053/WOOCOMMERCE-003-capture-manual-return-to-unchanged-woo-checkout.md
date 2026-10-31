---
id: ARCH-053-WOOCOMMERCE-003
architecture_id: ARCH-053
title: Detect human return to an unchanged existing Woo checkout
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-053-WOOCOMMERCE-001
enables:
- ARCH-053-SYSTEM-TEST-001
- ARCH-053-SYSTEM-TEST-002
created: 2026-10-29
updated: 2026-10-31
---

# ARCH-053-WOOCOMMERCE-003 — Detect human return to an unchanged existing Woo checkout

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. The task is materialised. Launcher claim for Attempt 1 succeeded, but the prepared packet output was lost before handoff; implementation did not begin.

## Objective

Detect human return to an unchanged existing Woo checkout. One bounded outcome in `moda-interact-woocommerce` owned by `moda_woocommerce`.

## Context

The inspected dependency snapshot is dated 2026-10-30 07:59. This task was promoted to Ready on 2026-10-31 after ARCH-053-WOOCOMMERCE-001 was accepted Complete. ARCH-052 remains exclusively responsible for dynamic discount discovery, not checkout-URL implementation.

## Scope

- Extend `includes/Checkout/CheckoutCapture.php` by adding a dedicated user-engagement capture path; add only the minimum Classic/Blocks frontend script and WordPress action/REST handler registration needed for a **real interaction** on cart/checkout with a verified existing `CheckoutKey::SESSION_FIELD`. Add focused PHP + Classic/Blocks browser tests.
- On an explicit, browser-authenticated customer action after returning to an existing cart/checkout (not just passive page GET), publish an ordinary fresh `CHECKOUT_UPDATED` with current full snapshot even when `LAST_CAPTURE` fingerprint is unchanged. Reuse the existing Action Scheduler queue, identity, phone-normalization and shop installation; add a **narrow bypass only for this verified interaction**, not for automatic total recalculations.
- Require a server-verified Woo-session-tied nonce and existing checkout key; reject homepage navigation, unobserved visitor, missing cart, preview, admin crawler, repetitive AJAX calculations, invalid nonce and nonce replay. Bound repeated signals per real page visit without introducing an outreach cooldown or cross-generation message limit.
- Do not generate a new checkout key merely from visiting the cart page. If a customer has no original Woo session, direct website navigation cannot be bound to the old recovery; link restoration from WOOCOMMERCE-002 supplies that binding.

## Out of Scope

No restore URL rendering (WOOCOMMERCE-002), no new queue, API contract, Backend generation/business logic or changes to ARCH-052 discount functionality.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- Reuse canonical `woo.activity.v1` and existing `CHECKOUT_UPDATED` semantics: **do not** introduce another `CHECKOUT_RESUMED` event type or implement recovery closure in PHP. The accepted ARCH-048 Background generation logic owns closing an active recovery and beginning a fresh delayed candidate.
- Preserve no-change deduplication for machine-triggered cart calculation. Never infer human intent from passive `DOMContentLoaded`/bot GET alone. Record bounded success/failure without customer PII.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- WooCommerce PHP executes on merchant-controlled WordPress servers and **must not import or implement** `@modainteract/moda-interact-shared/logging` (that npm export belongs only to hosted Moda Node processes). Use existing server-side plugin diagnostics (the current bounded `error_log()` pattern where applicable), not a new generic logger, `wc_add_notice()`, browser console output or shopper-visible HTML for Moda errors. Record a bounded event/reason and safe correlation identifier; preserve the original error message and relevant safe provider response details when available after redaction, without guessing a substitute cause. Never log bearer tokens, full restore URLs, coupon codes or customer PII. At storefront/controller boundaries catch and privately log unexpected errors, preserve or safely roll back the cart, and continue/redirect without Moda-originated error notices. At Action Scheduler and other retry-owning job boundaries, log and **propagate** retryable failures for durable retry/failure evidence; do not acknowledge them as success. Never globally suppress WordPress diagnostics or delete unrelated Woo notices.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [x] Add intentional checkout engagement producer for Classic and Blocks and authenticated session-scoped handler.
- [x] Implement narrowly targeted fingerprint bypass for verified human return and keep all current passive dedupe paths.
- [x] Test unchanged return, changed quantity, no key, productless cart, homepage, replay, bot GET and two visits.

## Interfaces / Contracts

Plugin-only POST from same origin with Woo session + nonce; emits existing authenticated `woo.activity.v1` CHECKOUT_UPDATED through the consolidated publisher. `CheckoutKey::SESSION_FIELD` unchanged. No shared/API event type addition.

## Dependencies

- `ARCH-053-WOOCOMMERCE-001` (must be architect-accepted Complete)

## Enables

- `ARCH-053-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Add intentional checkout engagement producer for Classic and Blocks and authenticated session-scoped handler.
- [x] Implement narrowly targeted fingerprint bypass for verified human return and keep all current passive dedupe paths.
- [x] Test unchanged return, changed quantity, no key, productless cart, homepage, replay, bot GET and two visits.
- [x] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [x] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [x] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [x] `composer test` CheckoutCapture and customer-engagement cases
- [x] `npm run test:integration:wordpress` Classic/Blocks manual return tests with and without unchanged basket
- [x] `composer lint`, frontend JS lint if applicable; `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

A user reopening the checkout from the original computer with valid session must start a new inactivity window only after a captured interaction and Background reconciliation. Link previews or automated HTTP requests must never count.

## Completion Report

### Status

Attempt 2 implementation is complete and submitted for architect review. The launcher claimed Attempt 2 for Codex at `2026-10-31T14:24:28Z`, synchronized both dedicated task worktrees, passed the dependency gate, and pushed the durable parent claim. The implementation worktree started clean at `e5bc98b822f78be8ed01f3940627bc333eadd584`; the parent task worktree started at `1d5520a8646e795f0295e264b8e03275c89d3cfd`, identical to `origin/task/ARCH-053-WOOCOMMERCE-003` after synchronization. The checkout interaction now carries a one-time Woo-session-bound nonce and a WordPress REST nonce, so authenticated customer cookies are verified consistently on the custom REST request. The dedicated handler rejects passive, cross-origin, stale and replayed requests and forces exactly one current `CHECKOUT_UPDATED` snapshot for a verified visit, even when unchanged. No branch was merged into `main`.

### Files Changed

Implementation repository: `includes/Checkout/CheckoutCapture.php`, `assets/js/checkout-engagement.js`, `tests/CheckoutCaptureTest.php`, `tests/bootstrap.php`, `tests/integration/scenarios/checkout-wordpress.mjs`, and `tests/integration/checkout-engagement-client.test.mjs`.

Parent task worktree: this task definition only.

### Work Completed

Added a trusted-interaction-only frontend signal for Classic and Blocks cart/checkout surfaces. The REST handler loads the cookie-bound Woo session, verifies same-origin JSON, the one-time visit nonce, current session binding, checkout key and non-empty cart, then calls the forced snapshot path without changing normal passive fingerprint deduplication. The browser sends WordPress's REST nonce so logged-in customer sessions remain authenticated during cookie-based REST requests. Added PHP and browser-client tests for unchanged and changed baskets, missing key/cart, homepage, bot GET, invalid/cross-origin/stale/replayed signal, one-time delivery, and scheduler failure behavior. The real WordPress integration covers guest and customer Classic/Blocks returns, including a second visit with unchanged basket and replay rejection.

### Validation Results

Validation completed:

- `composer test -- --filter CheckoutCaptureTest --do-not-cache-result` — passed: 23 tests, 232 assertions. PHPUnit reports one warning from the shared test fixture: `RecoveryPolicyControllerTest.php:14` reads undefined global `$moda_interact_test_logger`; it is unrelated to this task's changes.
- `npm run test:integration:wordpress -- --checkout-only` on the task-specific disposable wp-env at port 8891 — passed (`ARCH-035 checkout-only integration PASS`). It covered guest and authenticated customer Classic and Blocks checkout, fresh return events, replay rejection, cart clear/refill, order lifecycle and HPOS. The customer REST cases initially exposed missing WordPress cookie-auth nonce verification; adding `X-WP-Nonce` fixed the mismatch and the integration passed on rerun.
- `composer lint` — passed; all declared PHP files reported no syntax errors.
- `node --test tests/integration/checkout-engagement-client.test.mjs` — passed: 2 tests.
- `npm run lint:js -- assets/js/checkout-engagement.js` — passed.
- `npm run build` — passed; strict translation compilation generated 38 assets from 558 source messages. Webpack emitted performance notices for the 300 KiB JS bundle and 450 KiB combined entrypoint.
- `git diff --check` — passed.
- Broader `npm run test:js:node` run — 7 existing i18n assertions failed across 7 tests because tests expect 557 translation keys while the checked-out source contains 558. The new engagement-client tests passed in that run; the i18n failures are outside this task's files.

### Deviations

Added the WordPress REST cookie-auth nonce to the same-origin request after integration evidence showed WordPress clears the current user on cookie-authenticated REST calls unless `X-WP-Nonce` is supplied. No event/API contract or normal passive deduplication behavior changed. Docker access required the authorized host test environment; an unrelated site on port 8888 was left untouched.

### Assumptions

Uses the accepted WOOCOMMERCE-001 `woo.activity.v1` and checkout snapshot contracts. The authenticated REST nonce supplements, and does not replace, the one-time Woo session binding.

### Unresolved Issues

No unresolved implementation issues. Architect review remains pending.

### Architectural Concerns

Return any cross-service schema/provider/transaction concern to `moda_architect` before improvising.

## Architect Review

### Review Status

Accepted — Attempt 2

### Review Notes

The implementation meets the task's security and behavior requirements. The
browser emits the signal only for trusted control interactions on cart/checkout
surfaces; the server requires a one-time, short-lived nonce bound to the current
Woo session and existing checkout key, plus same-origin request validation and
a non-empty cart. Only this verified route bypasses fingerprint deduplication;
passive capture continues to deduplicate as before. The route returns failure
when enqueueing fails, and diagnostics remain server-side.

The implementation branch is three commits behind `origin/main`, which now
contains WOOCOMMERCE-004 coupon-capture changes in overlapping files. Git's
merge analysis is clean, and the independent coupon hooks call the unchanged
deduplicating capture path; the new engagement route uses its explicit forced
capture path. The task remains scoped to its submitted implementation commit;
the subsequent main-branch integration is not part of this architect review.

Attempt 2 is accepted and this automatic-completion task is Complete. The two
enabled system-test tasks remain Pending behind their other prerequisites.

### Reviewed Files

- `includes/Checkout/CheckoutCapture.php`
- `assets/js/checkout-engagement.js`
- `tests/CheckoutCaptureTest.php`
- `tests/bootstrap.php`
- `tests/integration/checkout-engagement-client.test.mjs`
- `tests/integration/scenarios/checkout-wordpress.mjs`

### Validation Reviewed

Reviewed the Completion Report evidence: focused PHP tests (23 tests / 232
assertions), Classic and Blocks WordPress integration for guest and authenticated
customer sessions, two browser-client tests, PHP and JavaScript lint, build,
and `git diff --check` passed. The report also records seven unrelated i18n
assertion failures in the broader JavaScript suite and one unrelated PHPUnit
fixture warning. Tests were not rerun for this review.

### Architecture Conformance

Conforms to the existing `woo.activity.v1` / `CHECKOUT_UPDATED` contract and
Action Scheduler publisher. No new queue, checkout identity, API event, or
generation logic was added. Passive page loads and machine-triggered
recalculations cannot trigger the forced capture.

### Follow-up

No implementation correction is required. `ARCH-053-SYSTEM-TEST-001` and
`ARCH-053-SYSTEM-TEST-002` remain Pending because their other dependencies are
incomplete. No main-branch merge was performed.
