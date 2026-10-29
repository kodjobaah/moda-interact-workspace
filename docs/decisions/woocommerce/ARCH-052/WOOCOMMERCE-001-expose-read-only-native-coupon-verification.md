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
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-BACKGROUND-003
- ARCH-052-SYSTEM-TEST-002
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

- Add a narrowly scoped server-to-server REST endpoint in the plugin (under its authenticated installed route) for `checkoutKey`, bounded candidate coupon IDs and an expected checkout fingerprint.
- Use a fresh authoritative Woo cart/checkout or safe isolated `WC_Discounts`-equivalent provider evaluation; reject when checkout snapshot/session has expired or necessary rules cannot be faithfully evaluated.
- Return an exact coupon ID/code, current relevant restrictions, eligible/ineligible/unavailable, positive savings/currency, validation times and checkout fingerprint; never reveal other customers or perform a Woo checkout mutation.
- Enforce existing installation identity/grant auth, canonical site binding, minimal response fields, bounded rate/deadline and no cross-installation lookup.

## Out of Scope

- No new Woo coupon catalogue, merchant settings UI, cart restoration, AI model, credit accounting or Meta send.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Unknown discount semantics, customer restrictions, stacking, free shipping, tax rounding or usage state fail closed as unavailable.
- PHP errors are reported via existing plugin operational logging without raw customer data, coupon credentials or swallowed unexpected exceptions.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement authenticated read-only evaluator/controller.
- [ ] Cover native Woo eligible, ineligible, unknown and expired state fixtures in WordPress integration tests.
- [ ] Document exact credential and response scope for Background consumer.

## Interfaces / Contracts

- Suggested `GET/POST /wp-json/moda-interact/v1/recovery/coupon-eligibility` behind existing approved server-to-server permission/grant, versioned documented request/response. Background BG003 is the only intended service consumer.

## Dependencies

None.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-003`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Correct coupon/customer/checkout restrictions can produce safe proof, unsupported state cannot.
- [ ] No Woo cart/session/order state is modified by provider verification.
- [ ] Unauthorized, wrong-shop and revoked credentials cannot reveal coupon/customer information.

## Validation

- [ ] PHP unit plus WordPress/WooCommerce integration harness for coupon rule combinations.
- [ ] PHP syntax/static analysis and plugin-declared tests; `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-woocommerce/includes/Rest/ (new eligibility controller)`
- `moda-interact-woocommerce/includes/Api/ (auth/client contracts)`
- `moda-interact-woocommerce/tests/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

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
