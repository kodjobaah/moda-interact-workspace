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
status: in_progress
priority: 50
executor: codex
claimed_at: 2026-10-31T14:20:28Z
attempt: 1
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

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

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

- [ ] Add intentional checkout engagement producer for Classic and Blocks and authenticated session-scoped handler.
- [ ] Implement narrowly targeted fingerprint bypass for verified human return and keep all current passive dedupe paths.
- [ ] Test unchanged return, changed quantity, no key, productless cart, homepage, replay, bot GET and two visits.

## Interfaces / Contracts

Plugin-only POST from same origin with Woo session + nonce; emits existing authenticated `woo.activity.v1` CHECKOUT_UPDATED through the consolidated publisher. `CheckoutKey::SESSION_FIELD` unchanged. No shared/API event type addition.

## Dependencies

- `ARCH-053-WOOCOMMERCE-001` (must be architect-accepted Complete)

## Enables

- `ARCH-053-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Add intentional checkout engagement producer for Classic and Blocks and authenticated session-scoped handler.
- [ ] Implement narrowly targeted fingerprint bypass for verified human return and keep all current passive dedupe paths.
- [ ] Test unchanged return, changed quantity, no key, productless cart, homepage, replay, bot GET and two visits.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] `composer test` CheckoutCapture and customer-engagement cases
- [ ] `npm run test:integration:wordpress` Classic/Blocks manual return tests with and without unchanged basket
- [ ] `composer lint`, frontend JS lint if applicable; `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

A user reopening the checkout from the original computer with valid session must start a new inactivity window only after a captured interaction and Background reconciliation. Link previews or automated HTTP requests must never count.

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
