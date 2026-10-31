---
id: ARCH-053-WOOCOMMERCE-001
architecture_id: ARCH-053
title: Capture original Woo cart coupons and restorable line data
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-053-API-001
- ARCH-053-BACKGROUND-001
enables:
- ARCH-053-WOOCOMMERCE-002
- ARCH-053-WOOCOMMERCE-003
- ARCH-053-WOOCOMMERCE-004
created: 2026-10-29
updated: 2026-10-31
---

# ARCH-053-WOOCOMMERCE-001 — Capture original Woo cart coupons and restorable line data

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Capture original Woo cart coupons and restorable line data. One bounded outcome in `moda-interact-woocommerce` owned by `moda_woocommerce`.

## Context

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Modify `includes/Checkout/CheckoutSnapshot.php`, `CheckoutCapture.php`, `CheckoutActivityPublisher.php` plus focused `tests/CheckoutCaptureTest.php` and `tests/integration/scenarios/checkout-*.mjs` (create targeted tests as needed).
- Capture verified `WC()->cart->get_applied_coupons()` exactly (0..10, each 1..128 safe characters), and for every supported line preserve integer parent product_id, variation_id, quantity and safe native `variation` attributes. Use `schemaVersion:'woo.cart-restore.v1'` and `kind:'supported'` only for complete 1..50-line core simple/variable carts; explicitly mark unsupported for composite/bundle/subscription/custom item data, invalid or missing product/variation, oversized lines/coupons/attributes, etc.; do not partially restore.
- Capture complete original applied codes as part of restoration projection, but do NOT implement separate coupon add/remove hook publishing here; that behaviour belongs exclusively to `ARCH-053-WOOCOMMERCE-004`. The canonical snapshot fingerprint must include restoration evidence; test snapshot serialization but leave coupon-only event admission/hook acceptance to WOOCOMMERCE-004.
- Emit **only `woo.activity.v1`** checkout activity with optional `checkout.restoration`. Consolidate existing `CheckoutActivityPublisher::enqueue()` HTTP v2 phone-proof branch into the canonical v1 checkout: when contact has a verifiable phone, include the same `canonicalPhone` and optional `verifiedCountryCode` proof used by the existing v2 producer; never emit a v2/v3 event. When a phone cannot be reliably normalized, omit the unverified phone and both proof fields while preserving the valid basket and any other allowed contact fields. Retain Action Scheduler job identity, acceptance, bounded retries, occurredAt and eventId. **Do not deploy this producer until API-001 and Background-001 have been accepted and the pre-production pair is coordinated.**

## Out of Scope

No custom restore endpoint or checkout URL, no new visitor resumption signal (WOOCOMMERCE-003), no Woo pricing/coupon proof from ARCH-052, no new consent checkbox.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- No PII or custom cart-item metadata inside restoration; do not copy arbitrary extension item metadata or silently invent variation selections. Existing display item snapshot and supported zero/oversized behaviour remain intact.
- Coupons applied by shoppers are **not** CommerceAgent/ARCH-052 promotional offers; do not create, extend or reprice Woo coupons. Capture empty array if none applied; omit `restoration` entirely only when no trustworthy cart evidence.
- All capture failures must be logged safely where possible, nonblocking to Woo shoppers, but never silently fabricate a supported restoration. Cart-removal and refill still cancel/restart candidates through existing activity flow. If valid phone proof cannot be produced, retain the product/coupon checkout event without a phone, not an unverified-phone HTTP v1 request.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [ ] Implement exact supported/unsupported cart projection and PHP parity tests for Shared fixture.
- [ ] Capture the complete original applied-coupon list within supported restoration JSON; a malformed/incomplete coupon list must mark restoration unsupported instead of silently dropping codes.
- [ ] Publish canonical v1 complete event using existing queued publisher and preserve existing phone/consent semantics.

## Interfaces / Contracts

PHP `checkout.restoration` must conform to the published ARCH-053-SHARED-001 v1 JSON fixture. HTTP checkout `schemaVersion` is exactly `woo.activity.v1`; API-001 verifies `contact.phone` with `canonicalPhone`/optional `verifiedCountryCode` and produces the existing normalized v1 queue job with restoration. No `woo.activity.v2` or `woo.activity.v3` producer branch. Do not import Node packages into PHP; validate parity with canonical fixtures and ensure new snapshot/coupon data remains under the 65,536-byte activity body limit.

## Dependencies

- `ARCH-053-API-001` (must be architect-accepted Complete)
- `ARCH-053-BACKGROUND-001` (must be architect-accepted Complete)

## Enables

- `ARCH-053-WOOCOMMERCE-002`
- `ARCH-053-WOOCOMMERCE-003`
- `ARCH-053-WOOCOMMERCE-004`

## Acceptance Criteria

- [ ] Implement exact supported/unsupported cart projection and PHP parity tests for Shared fixture.
- [ ] Capture the complete original applied-coupon list within supported restoration JSON; a malformed/incomplete coupon list must mark restoration unsupported instead of silently dropping codes.
- [ ] Publish canonical v1 complete event using existing queued publisher and preserve existing phone/consent semantics.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] `composer test` focused CheckoutCapture/CheckoutSnapshot tests
- [ ] `npm run test:integration:wordpress` targeted snapshot serialization for Classic/Blocks with original coupon list and variations when environment available
- [ ] `composer lint` and `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

The plugin already has `CheckoutKey::SESSION_FIELD`, Action Scheduler and the v2 canonical-phone helper. Reuse them rather than new cookies or queues; the v2 phone check is retained *inside v1*, not as a second HTTP version. Include a test that one valid v1 event contains both the normalised phone proof and supported `checkout.restoration`, and a second valid v1 event contains restoration but omits a non-normalisable phone. Snapshot must contain the original coupon list, while publishing events for coupon-only additions/removals is owned by WOOCOMMERCE-004. Do not duplicate its hooks in this task.

## Completion Report

### Status

Not Started

### Claim Release History

Attempt 1 was claimed by Copilot at `2026-10-31T09:12:48Z`, but implementation did not begin. At the user's request, the claim was released before a new executor was prepared. The dedicated implementation worktree was clean at baseline `b905dab`; it had no source edits or implementation commit. The task is Ready with `attempt: 1`, `executor: null`, and `claimed_at: null`; the next launcher claim will be Attempt 2.

### Files Changed

None — no implementation files changed.

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
