---
id: ARCH-048-BACKGROUND-002
architecture_id: ARCH-048
title: Reconcile Woo order events and fence terminal recoveries
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
  - ARCH-035-BACKGROUND-002
  - ARCH-035-API-019
enables:
  - ARCH-048-BACKGROUND-003
created: 2026-10-23
updated: 2026-10-23
---

# ARCH-048-BACKGROUND-002: Reconcile Woo order events and fence terminal recoveries

## Architecture

- Architecture ID: `ARCH-048`.
- Canonical architecture: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.
- Coordinator: `moda_architect`.
- **Lifecycle:** portable review definition based on the 23 October 2026 workspace snapshot, **defined but not materialised**. No branch/worktree, commit, claim, implementation or acceptance is implied. Re-gate against the developer's canonical workspace before execution.

## Objective

Extend the Woo order capture consumer so verified order events correlated by shop/checkout key cancel or update pending candidates and fence paid/cancelled checkout generations, including workers already running.

## Context

Woo emits `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED` through the same authenticated activity route. `ORDER_PLACED` does not mean paid; Woo events can be delayed, duplicated or arrive before checkout snapshots.

## Scope

- Correlate each order event by authenticated `shopId`, `checkoutKey` and `order.checkoutKey`, retaining the exact `orderId` and an ordering/identity guard for stale events.
- For paid or cancelled outcomes, remove the matching delayed candidate and write a checkout-scoped bounded terminal fence; cancel/suppress existing recoveries, attempts and any outstanding send work using existing lifecycle controls.
- Treat `ORDER_PLACED` as a correlated order that may be unpaid; do not automatically mark recovered/paid, and defer uncertain pending-order eligibility to authoritative provider lookup at maturity.
- Handle order-first, checkout-first, concurrent update vs terminal event, reopening/new checkout generation and duplicate messages.

## Out of Scope

- No Shopify order-path changes, provider order fetching inside every capture job or new order table.
- No direct SMS/WhatsApp sends, initial CheckoutRecovery creation or new billing mechanism.
- No `docs/decisions/**/_index.md` updates before the developer explicitly ends architecture reconciliation.

## Requirements

- Job deletion alone is not sufficient: running maturity/send workers must observe terminal fencing under checkout lock.
- Never infer payment from order creation/status text alone; verified `ORDER_PAID` is distinct and API-002 provider check remains mandatory before sends.
- Terminal decision cannot be undone by an older `CHECKOUT_UPDATED` on the same checkout key; new checkout keys may be admitted independently.

## Work Items

- [ ] Integrate order capture events with checkout lock, candidate cancel and terminal fence.
- [ ] Synchronise existing CheckoutRecovery/outreach lifecycle when an order becomes paid/cancelled.
- [ ] Add race, order-first, placed-unpaid, duplicate, replay, stale checkout and running-worker tests.

## Interfaces / Contracts

- Consume existing API-019 Woo order queue/event contract, `eventId`, orderId, status, occurredAt and checkoutKey.
- Coordinate through checkout-scoped transient keys with BACKGROUND-001/003 and existing recovery lifecycle/service guards.

## Dependencies

- `ARCH-035-BACKGROUND-002`
- `ARCH-035-API-019`

## Enables

- `ARCH-048-BACKGROUND-003`

## Acceptance Criteria

- [ ] Paid and cancelled orders suppress pending and in-flight initial recovery; existing row/status is updated safely if one exists.
- [ ] Unpaid placed orders are not falsely marked paid or wrongly sent without provider verification.
- [ ] Out-of-order/duplicate events cannot resurrect a terminal checkout generation or duplicate state changes.

## Validation

- [ ] Redis/BullMQ race and DB lifecycle integration tests, placed/paid/cancelled and retry idempotency.
- [ ] Existing Shopify order guard and Woo worker regressions; declared lint/build and `git diff --check`.

## Stop Condition

After the specified work, acceptance criteria and required validation are satisfied, record launcher-resolved **dedicated** parent/implementation task worktrees, start-of-attempt synchronization and recursive submodule evidence in the Completion Report. Change task state to `review`, return to `moda_architect` and **STOP**. Do not start an enabled task. The repo agent must not mark its own task Complete.

## Implementation Notes

Use the existing `CheckoutRecoveryStatusHistory` and status fields after first INSERT; pre-INSERT order fences are bounded transient state, with live provider reads as the defence against lost terminal events.

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
