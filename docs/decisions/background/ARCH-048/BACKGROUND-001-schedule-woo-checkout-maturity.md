---
id: ARCH-048-BACKGROUND-001
architecture_id: ARCH-048
title: Schedule and reschedule Woo checkout maturity from captured events
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 32
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-BACKGROUND-001
  - ARCH-035-API-008
enables:
  - ARCH-048-BACKGROUND-003
created: 2026-10-23
updated: 2026-10-23
---

# ARCH-048-BACKGROUND-001: Schedule and reschedule Woo checkout maturity from captured events

## Architecture

- Architecture ID: `ARCH-048`.
- Canonical architecture: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.
- Coordinator: `moda_architect`.
- **Lifecycle:** portable review definition based on the 23 October 2026 workspace snapshot, **defined but not materialised**. No branch/worktree, commit, claim, implementation or acceptance is implied. Re-gate against the developer's canonical workspace before execution.

## Objective

Extend the Woo checkout capture consumer to create, advance, replace or remove a checkout-keyed delayed evaluation from existing BullMQ/Redis candidate facilities without creating a `CheckoutRecovery`.

## Context

ARCH-035-BACKGROUND-001 is deliberately capture-only. Shopify already has `pending-recovery-candidates` and checkout-scoped indexes/locks. Woo events are on a separate capture queue and require Woo-specific bounded payloads, not a Shopify event disguise.

## Scope

- On valid `CHECKOUT_UPDATED`, use authenticated `(shopId, checkoutKey)` plus event timestamp/activity watermark to create or replace one delayed Woo maturity candidate according to existing ShopSettings recovery delay; newer real activity resets maturity.
- On `items: []` or explicit zero-eligible-basket outcome, cancel and fence the pending candidate for the same checkout generation.
- Reuse BullMQ delay/index/lock/error handling and bounded TTL, but retain a Woo-specific candidate payload/schema and independent worker/entrypoint semantics; no Shopify queue poisoning.
- Deduplicate same event ID/content; prevent older/out-of-order checkout updates from resurrecting a cleared or terminal generation, with an order fence defined by BACKGROUND-002.

## Out of Scope

- No current Woo provider fetch per event, CheckoutRecovery creation, WhatsApp or billing.
- No new Postgres candidate table or permanent event history.
- Do not change ARCH-035 capture task history or Shopify candidate schema unnecessarily.
- No `docs/decisions/**/_index.md` updates before the developer explicitly ends architecture reconciliation.

## Requirements

- A captured event is acknowledged only once scheduling/cancellation is durable in the approved Redis/BullMQ boundary; retry infrastructure errors.
- Candidate/last-activity/index consistency must survive repeat job delivery, worker restart, stale delayed workers and concurrent checkout/order processing.
- Avoid logging contact/cart content; never use captured phone as marketing consent.

## Work Items

- [ ] Wire checkout capture event to Woo-specific maturity/index lifecycle and merchant delay.
- [ ] Handle empty cart, repeated updates, out-of-order activity, order fence interaction and bounded queue cleanup.
- [ ] Add BullMQ worker/integration and Shopify isolation regression tests.

## Interfaces / Contracts

- Consume the existing API-008 `woo.activity.v1` checkout queue and original `eventId`, authenticated `shopId`, checkoutKey, `occurredAt` and bounded snapshot.
- Produce bounded Woo maturity jobs consumed by BACKGROUND-003; share narrow order-lock/fence helper with BACKGROUND-002, not a distinct event contract clone.

## Dependencies

- `ARCH-035-BACKGROUND-001`
- `ARCH-035-API-008`

## Enables

- `ARCH-048-BACKGROUND-003`

## Acceptance Criteria

- [ ] One active delayed candidate per shop/checkout generation; newer activity moves its maturity time.
- [ ] Empty basket cancels the candidate and a stale job cannot create a recovery.
- [ ] Scheduling failures retry, and no recovery/billing/send side effects occur in the hot path.

## Validation

- [ ] Focused Redis/BullMQ concurrency and retry tests; checkout event parser/entrypoint regression.
- [ ] Shopify candidate/queue isolation tests, declared lint/build and `git diff --check`.

## Stop Condition

After the specified work, acceptance criteria and required validation are satisfied, record launcher-resolved **dedicated** parent/implementation task worktrees, start-of-attempt synchronization and recursive submodule evidence in the Completion Report. Change task state to `review`, return to `moda_architect` and **STOP**. Do not start an enabled task. The repo agent must not mark its own task Complete.

## Implementation Notes

A lost candidate means missed outreach, not permission to reconstruct stale carts. The live authoritative read is required in BACKGROUND-003 before first INSERT.

Respect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and `docs/developer-task-workflow.md`. Prepare through `/moda-task` or `/moda_developer_create` in the developer's actual workspace. Use service-owned existing runtime facilities; reuse `@modainteract/moda-interact-shared/logging` for new generic Node application logs, not an alternate logger. Follow the actual owning repository's declared checks; no unrelated refactors or cross-repository edits.

## Completion Report

### Status

Not Started — portable task definition; implementation execution not claimed.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run. Required validation is listed above for the future assigned executor.

### Deviations

None.

### Assumptions

The uploaded snapshot is not the current remote/branch authority. Dependencies and task paths must be rechecked on materialisation.

### Unresolved Issues

None recorded at task-definition stage beyond the review gates in the parent architecture.

### Architectural Concerns

Escalate missing cross-repository contracts, Woo guest-session read impossibility, authentication or deployment requirements to `moda_architect` before inventing a workaround.

## Architect Review

### Review Status

Pending — not yet reviewed as an implementation.

### Review Notes

Awaiting future repository implementation and evidence.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet assessed.

### Follow-up

None.
