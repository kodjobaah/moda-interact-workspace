---
id: ARCH-048-WOOCOMMERCE-002
architecture_id: ARCH-048
title: Publish complete Woo checkout updates including cleared baskets
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-035-WOOCOMMERCE-007
- ARCH-035-API-008
enables:
- ARCH-048-BACKGROUND-003
- ARCH-048-SYSTEM-TEST-001
created: '2026-10-23'
updated: '2026-10-23'
---

# ARCH-048-WOOCOMMERCE-002 — Publish complete Woo checkout updates including cleared baskets

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **proposed** definition based on the uploaded 2026-10-23 18:50 snapshot; no branch, task worktree, implementation commit, accepted review or release is claimed. Check actual canonical task state before materialisation.

## Objective

Make every meaningful checkout basket-clear/refill transition observable through the existing authenticated outbound activity route, without exposing a WordPress read endpoint.

## Context

`CheckoutSnapshot::fromCart()` currently returns null for an empty cart, and `CheckoutCapture` then publishes no checkout update. API ingress already accepts `CHECKOUT_UPDATED` containing `items: []`. The publisher queues a stable event ID for retries through Action Scheduler.

## Scope

- Publish `CHECKOUT_UPDATED` with explicit `items: []` for an observed nonempty-to-empty transition of an already keyed checkout.
- Capture relevant cart/checkout changes through existing supported Classic/Blocks hooks, including checkout-origin basket changes where supported.
- Avoid false empty events for never-active carts and preserve Woo checkoutKey across legitimate clear/refill of the same checkout.
- Emit well-formed millisecond UTC occurrence times without inventing a new contract field.
- Preserve queued eventId and exact payload across retry; limit repeat no-op empty notifications.
- Distinguish unknown/oversized items (absent `items`, including more than 50 rows) from verified empty (`items: []`).

## Out of Scope

- No new WordPress REST routes, guest-session lookup, server-initiated remote reads, background scheduling, database schema or consent mutation.

## Requirements

- Only observed meaningful activity changes affect abandonment timing; missing `items` must never be interpreted as empty.
- Out-of-order/timestamp tie safety is owned by BACKGROUND-001; this task does not claim that timestamps alone provide perfect causal ordering.
- Use approved existing Woo API activity schema; no arbitrary new JSON fields or event types.

## Work Items

- [ ] Cover Classic and Blocks empty/refill transitions and cart changes after checkout starts.
- [ ] Add 51+ item, invalid snapshot, unchanged empty and transport retry/idempotency cases.
- [ ] Verify actual Woo hooks and existing API payload validator integration.

## Interfaces / Contracts

- Produces existing `woo.activity.v1` / HTTP `woo.activity.v2` checkout payload through `CheckoutActivityPublisher` and existing POST `/v1/woocommerce/activity`.
- Consumes existing checkoutKey/session state only locally in event capture; no remote guest read.

## Dependencies

- `ARCH-035-WOOCOMMERCE-007`
- `ARCH-035-API-008`

## Enables

- `ARCH-048-BACKGROUND-003`
- `ARCH-048-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Genuine empty basket publishes `items: []`, once per meaningful transition, and no unexpected recovery is scheduled from a vanished/oversized snapshot.
- [ ] Empty-to-refilled checkout creates a newer ordinary event; Woo and Moda existing checkout identity remain consistent.
- [ ] Existing valid checkout/order publisher and 20-locale UI behaviour are unchanged; no HTTP endpoint is introduced.

## Validation

- [ ] Focused PHPUnit/plugin Classic/Blocks/cart mutation and Action Scheduler retry tests.
- [ ] API event-parser fixture validation for empty vs absent items, plugin declared lint/build scripts and `git diff --check`.

## Stop Condition

After only this task's work, criteria and required validation, complete the Completion Report with the launcher-resolved dedicated parent and implementation worktree paths, isolation, start-of-attempt synchronisation and repository revision evidence. Change to `review`, return to `moda_architect` and **STOP**. Do not start dependent work. Superseded tasks must not be claimed.

## Implementation Notes

- Do not write UI or session restoration functionality as a side effect.
- Security boundary: all new behaviour is outbound Woo → existing Moda API only.

- Use `/moda-task` preparation with the real developer workspace before code execution. Do not treat the snapshot as a Git branch; do not edit any `docs/decisions/**/_index.md` during this architecture session. Validate actual repository scripts rather than guessing commands. Respect assigned repository and task-document ownership.

## Completion Report

### Status

Not Started — proposed portable definition only.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run by repository implementer; no task worktree or Git remote is accessible in this review package.

### Deviations

None.

### Assumptions

The latest uploaded workspace ZIP is a source snapshot, not necessarily the developer's latest task branches. The developer reports `ARCH-046-BACKGROUND-004` complete after the ZIP; verify its accepted implementation for consumer integration, without reopening it.

### Unresolved Issues

None at definition time. Raise concrete cross-repository contract gaps with the architect before implementation.

### Architectural Concerns

See the parent architecture for the explicitly acknowledged event-only missed-event limitation.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
