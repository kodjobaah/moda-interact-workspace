---
id: ARCH-052-WOOCOMMERCE-001
architecture_id: ARCH-052
title: Verify checkout and alternative-product coupon eligibility read-only in Woo plugin
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: '2026-10-29'
updated: '2026-10-30'
---

# ARCH-052-WOOCOMMERCE-001: Verify checkout and alternative-product coupon eligibility read-only in Woo plugin

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** No WooCommerce native coupon-proof endpoint is required for ARCH-052. MCP exposes current synced discount information and provider product reads; the agent makes the promotional decision.

The pre-existing description and completion-report placeholders elsewhere in this file remain historical only. No repository code or validation is authorised by this task.

## Context

Woo coupon catalogue snapshots are not checkout-specific proof. WordPress/WooCommerce owns native usage, email/customer, product/category, exclusion, quantity/minimum and coupon restrictions. Existing WC REST coupon reads alone cannot certify redemption.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

None. This task is withdrawn; do not start the original implementation, create new provider verification services or publish obsolete proof contracts.

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
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

## Work Items

None — superseded; retain this historical definition only for audit.

## Interfaces / Contracts

Native Woo authenticated **read-only** REST GET `/wp-json/wc/v3/moda/recovery/coupon-proof`, with bounded validated checkout/customer/discount identity in headers, `X-Moda-Promotion-Target` and optional exact product/variation identity for `ALTERNATIVE_PRODUCT`. Shared-005 provider proof discriminant. Caller is MCP-003's secure Woo transport, invoked by MCP-002/MCP-004; no hosted Moda API route or HTTP broker.

## Dependencies

None — superseded.

## Enables

None — superseded.

## Acceptance Criteria

None — superseded; no code is to be accepted under this task.

## Validation

Not applicable; the superseded implementation must not run.

## Stop Condition

This task is superseded. Do not claim, implement, run tests, publish, merge or unblock dependants from it.

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

**Architectural supersession (2026-10-30):** No WooCommerce native coupon-proof endpoint is required for ARCH-052. MCP exposes current synced discount information and provider product reads; the agent makes the promotional decision.

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
