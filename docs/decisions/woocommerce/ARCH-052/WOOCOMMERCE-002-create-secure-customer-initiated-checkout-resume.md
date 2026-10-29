---
id: ARCH-052-WOOCOMMERCE-002
architecture_id: ARCH-052
title: Provide secure customer-initiated Woo checkout restoration link
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
- ARCH-052-SYSTEM-TEST-002
- ARCH-052-API-004
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-WOOCOMMERCE-002: Provide secure customer-initiated Woo checkout restoration link

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Enable a customer who taps the WhatsApp Resume checkout CTA to reconstruct an eligible abandoned Woo basket on their own Woo site.

## Context

Current Woo CheckoutRecovery.checkoutUrl is null and the authenticated Woo checkout event has no restoration URL. A plain store `/checkout` link does not restore basket items.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Use existing WordPress **Transients API** (no new custom table) to store a bounded `checkoutKey` indexed restore snapshot of <=50 product/variation IDs, quantities and required option data with absolute expiry at most 24h, never a customer telephone/name. This may consume existing WP options/object cache, but it is not an additional Moda product-image or merchant-discount table.
- Add authenticated plugin-owned REST link issuance `GET /wp-json/wc/v3/moda/recovery/restore-link` callable with installed Woo REST read-only key; request headers `X-Moda-Checkout-Key` and `X-Moda-Checkout-Fingerprint` (no query/body). Verify current captured checkout, not ordered/consumed/expired, and return `{url,expiresAt}` using a new 32-byte install-local signing key stored in WordPress options (non-autoload, never published). Link token contains no raw checkout key or customer personal data, is HMAC signed and expires <=30 minutes.
- Add browser GET handler at `/moda-recovery/restore/<opaque-token>` on the canonical shop host, validate signature, token expiry, installation binding and snapshot fingerprint before any restore; restore only valid sellable products/options into *the clicking visitor’s own cart session*, then 303 to `wc_get_checkout_url()`. Idempotent second visit does not duplicate cart lines; do not consume on HEAD or message-preview fetch.
- Recheck availability, stock, quantity, variation existence and price at restore time; disallowed/removed products are omitted with an explicit customer-facing notice (never silently replaced). Expired/redeemed/paid checkout presents expiry message and no transfer of another visitor’s cart/session.
- Register endpoint/rewrite rules on activation, flush only at activation, provide a bounded expiry cleanup path using normal WP transient expiry; no arbitrary redirect query or bearer URL logging.
- Add classic checkout + Blocks Store API tests, token tamper/expiry/HEAD, two-session isolation, refund/paid checkout suppression, product variants/options, price changes and redirect-only-after-success.

## Out of Scope

- No Moda-hosted checkout recreation, provider coupon application, customer order placement, credit recording, Meta template implementation or Woo event schema change.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Restoration is explicitly initiated by the customer visiting the link; Background/AI never mutates Woo cart.
- Signed token is scoped to one installation and recovery state, has an explicit expiry, and is revalidated before link issuance/use.
- Woo REST read-only key uses a **GET** request with identity data in strictly validated HTTPS headers, not URI query params; `Cache-Control: no-store` on both request and response. Native provider route must never require write-scoped Woo API keys or mutate cart/coupon/order state on read.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement WP transient restore snapshot and signed link issue route.
- [ ] Add customer-click restoring route/checkout redirect with idempotency.
- [ ] Run Woo classic/Blocks and two-session provider integration tests.

## Interfaces / Contracts

- `GET /wp-json/wc/v3/moda/recovery/restore-link`, fixed two request headers and `{url,expiresAt}`; GET `/moda-recovery/restore/<opaque-token>` on canonical Woo host.

## Dependencies

None.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-SYSTEM-TEST-002`
- `ARCH-052-API-004`

## Acceptance Criteria

- [ ] Valid customer click restores eligible basket at correct Woo store; merely issuing the link changes nothing.
- [ ] Expired/revoked/paid or foreign-installation link never restores or leaks customer data.
- [ ] No direct hosted DB, Redis or Moda private secret access from Woo plugin.

## Validation

- [ ] WordPress/Woo PHPUnit/integration for Classic and Blocks, HPOS-safe order state and token abuse.
- [ ] PHP syntax/unit integration suite and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-woocommerce/includes/Rest/RecoveryRestoreLinkController.php (new)`
- `moda-interact-woocommerce/includes/Checkout/RecoveryCartRestore.php (new)`
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
