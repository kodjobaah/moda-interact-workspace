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
status: blocked
priority: 40
executor: codex
claimed_at: 2026-10-31T09:44:59Z
attempt: 2
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

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. Task materialised in dedicated parent and implementation worktrees. Attempt 2 is claimed by Codex; no producer deployment is claimed.

## Objective

Capture original Woo cart coupons and restorable line data. One bounded outcome in `moda-interact-woocommerce` owned by `moda_woocommerce`.

## Context

ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. The launcher freshly gated both dependencies as Complete before claiming Attempt 2.

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

- [x] Implement exact supported/unsupported cart projection and PHP parity tests for Shared fixture.
- [x] Capture the complete original applied-coupon list within supported restoration JSON; a malformed/incomplete coupon list must mark restoration unsupported instead of silently dropping codes.
- [x] Publish canonical v1 complete event using existing queued publisher and preserve existing phone/consent semantics.

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

Attempt 2 implementation is prepared, but required PHP and WordPress integration validation is blocked because `scripts/bootstrap-woocommerce.sh` reports that Docker is installed but its daemon is unavailable. The implementation is not ready for architect review until validation can run successfully.

### Claim Release History

Attempt 1 was claimed by Copilot at `2026-10-31T09:12:48Z`, but implementation did not begin. At the user's request, that claim was released. The launcher claimed Attempt 2 for Codex at `2026-10-31T09:44:59Z`, re-gated both dependencies, synchronized the dedicated parent and implementation task worktrees, and pushed the durable parent claim (`f92db4455fe861fda3a04b16a083cd7fcd654a55`). Implementation baseline was `b905dab216f8598269ebd32e8d70af150524d274`. Implementation commit `5f679b6` is pushed to `origin/task/ARCH-053-WOOCOMMERCE-001`. Attempt 2 remains active and is marked Blocked pending the developer-managed Docker daemon and required validation.

### Files Changed

Implementation repository files: `includes/Checkout/CheckoutSnapshot.php`, `includes/Checkout/CheckoutCapture.php`, `includes/Checkout/CheckoutActivityPublisher.php`, `tests/CheckoutCaptureTest.php`, `tests/fixtures/woo-restore-v1.json`, and `tests/integration/scenarios/checkout-wordpress.mjs`.

Parent task worktree: this task definition only.

### Work Completed

Implemented the bounded `woo.cart-restore.v1` snapshot with the complete original coupon list and supported simple/variation lines; unsupported evidence carries a reason and no partial line data. Added Shared fixture parity and focused unsupported-cart cases. Checkout activity remains `woo.activity.v1`; verified phone proof stays in that envelope, and unverifiable phone values are omitted while other contact fields remain. Added Classic and Blocks integration coverage for a native variation with an applied coupon. No producer deployment was performed.

### Validation Results

`git diff --check` — passed in the implementation worktree.

`composer test -- tests/CheckoutCaptureTest.php` — blocked. Before PHP/Composer commands, the required `scripts/bootstrap-woocommerce.sh` reported: `ERROR: Docker is installed but the Docker daemon is not available. Start the configured Docker runtime, then rerun the bootstrap.` The subsequent Composer invocation confirmed `vendor/bin/phpunit` is absent. No PHP runtime command was run after bootstrap failed.

`composer lint` — not run because the same bootstrap prerequisite is unavailable.

`npm run test:integration:wordpress -- --checkout-only` — not run because the canonical WooCommerce bootstrap reports no Docker daemon. No integration runtime was started or substituted.

### Deviations

Validation is incomplete because the canonical WooCommerce bootstrap cannot find a running Docker daemon. The requested PHP test could not execute because its vendor PHPUnit binary is absent. No substitute runtime was installed or selected.

### Assumptions

The canonical launcher packet supplied the authoritative worktree paths and dependency gate for Attempt 2.

### Unresolved Issues

The configured Docker daemon is unavailable. The developer must start the configured runtime (Colima) and rerun the task so the canonical bootstrap, PHP tests/lint and targeted WordPress integration validation can run. Do not bypass the bootstrap or start/replace the runtime from this task.

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
