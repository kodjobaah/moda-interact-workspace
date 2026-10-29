---
id: ARCH-052-WOOCOMMERCE-001
architecture_id: ARCH-052
title: Expose read-only native Woo coupon eligibility proof
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-003
enables:
- ARCH-052-SYSTEM-TEST-002
- ARCH-052-API-003
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-WOOCOMMERCE-001: Expose read-only native Woo coupon eligibility proof

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Provide an authenticated provider-side coupon evaluation against the saved customer checkout, without mutating any cart or applying a coupon.

## Context

Woo coupon catalogue snapshots are not checkout-specific proof. WordPress/WooCommerce owns native usage, email/customer, product/category, exclusion, quantity/minimum and coupon restrictions. Existing WC REST coupon reads alone cannot certify redemption.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Register custom WooCommerce REST route `GET /wp-json/wc/v3/moda/recovery/coupon-proof` in `includes/Rest/RecoveryCouponProofController.php` and plugin existing bootstrap. Headers exactly `X-Moda-Checkout-Key` (<=128 chars), `X-Moda-Coupon-Id` (positive decimal integer), `X-Moda-Checkout-Fingerprint` (bounded hex digest), combined <=2048 bytes, with empty GET body and no query string; require authenticated Woo REST API consumer key with `read` permission for this **GET** endpoint, not browser nonce nor unauthenticated site origin. Reject requests by other merchants/sites or unverified install grants.
- Resolve original abandoned checkout using installed plugin checkoutKey capture and customer/session identity; verify supplied fingerprint against the fresh stored checkout captured values and currently required provider facts. Never trust caller-provided basket contents or prices. Native `WC_Coupon`/`WC_Discounts` validation must be run in isolated nonpersisting test context: quantity, product/variation, required/excluded products/categories, minimum/maximum cart spend, expiry, per-customer/usage and stacking/currency restrictions. If custom extension hooks or missing customer session make safe exact validation impossible, return `unavailable`, not approximate savings.
- Generate the strict Shared-005 result (same JSON validated by Node consumers) with current coupon id, exact currency, positive savings in minor units, UTC evaluated/expires <=5 min, coupon code when deliverable and checkout fingerprint. Verified `ineligible` only for proved negative outcome; unknown => `unavailable`. No generic coupon listing exposed.
- No persistent coupon application, no Woo cart/session mutation, no new checkout order, no merchant cart edits. Valid return is independent of the WhatsApp send; Meta send remains Background-owned.
- Add PHP unit/integration tests with actual Woo REST read-only key auth, checkout-session fixtures, customer restrictions and usage limits, unknown rule hooks, two-installation isolation, missing session and `WC_Discounts` no-mutation proof.

## Out of Scope

- No new Woo coupon catalogue, merchant settings UI, cart restoration, AI model, credit accounting or Meta send.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Eligibility evaluates the checkout as originally captured, customer identity and coupon restrictions as they exist at evaluation time; no application of coupon to live cart.
- A missing historical customer/session or incompatible Woo extension rule is `unavailable`, not qualifying.
- Woo REST read-only key uses a **GET** request with identity data in strictly validated HTTPS headers, not URI query params; `Cache-Control: no-store` on both request and response. Native provider route must never require write-scoped Woo API keys or mutate cart/coupon/order state on read.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement exact authenticated route and native isolated coupon proof.
- [ ] Add Woo checkout/session lookup, safe unsupported-rule classification.
- [ ] Run WooCommerce read-only key, two-installation and no-cart-write integration tests.

## Interfaces / Contracts

- Fixed read-only Woo endpoint `GET /wp-json/wc/v3/moda/recovery/coupon-proof`, strict three strictly validated request headers and Shared-005 response JSON fixtures; hosted API-003 is sole caller.

## Dependencies

- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-SYSTEM-TEST-002`
- `ARCH-052-API-003`

## Acceptance Criteria

- [ ] Read-only WooCommerce REST key can invoke verified coupon proof without write permission; never leaks coupon status to another merchant.
- [ ] No runtime Woo cart change or false promise on unsupported usage/custom rules.

## Validation

- [ ] PHP unit plus WordPress/WooCommerce integration harness for coupon rule combinations.
- [ ] PHP syntax/static analysis and plugin-declared tests; `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-woocommerce/includes/Rest/RecoveryCouponProofController.php (new)`
- `moda-interact-woocommerce/includes/Checkout/CheckoutSnapshot.php`
- `moda-interact-woocommerce/tests/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

- Native coupon `WC_Discounts` validation must be read-only and avoid mutating the live customer session. If validation requires mutation, use an isolated synthetic cart in memory with no save hooks, then discard; never cause Woo-side persistent cart changes.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Execution will verify its current workspace, source state, dependency versions and test harness.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Pending.

### Review Notes

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
