---
id: ARCH-048-WOOCOMMERCE-003
architecture_id: ARCH-048
title: Harden checkout-linked Woo paid and cancellation event coverage
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 26
executor: developer
claimed_at: '2026-10-26T14:25:27Z'
attempt: 1
depends_on:
- ARCH-035-WOOCOMMERCE-008
- ARCH-035-API-019
enables:
- ARCH-048-BACKGROUND-003
- ARCH-048-SYSTEM-TEST-001
created: '2026-10-23'
updated: '2026-10-26'
---

# ARCH-048-WOOCOMMERCE-003 — Harden checkout-linked Woo paid and cancellation event coverage

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **proposed** definition based on the uploaded 2026-10-23 18:50 snapshot; no branch, task worktree, implementation commit, accepted review or release is claimed. Check actual canonical task state before materialisation.

## Objective

Ensure every confirmed checkout-linked order placement, paid transition and cancellation observed by the plugin is reliably published using existing event kinds.

## Context

`OrderLifecycleCapture` attaches `_moda_checkout_key` and currently observes order-processed, `woocommerce_payment_complete` and status change (cancellation) hooks. Some gateways can transition to a paid Woo order state without exercising the specific payment-complete hook. A missed event remains possible even after bounded Action Scheduler retries.

## Scope

- Audit HPOS-compatible status transitions and cover confirmed paid statuses through appropriate WooCommerce-supported hooks without inventing payment when merely placed/on-hold/failed.
- Keep exact `_moda_checkout_key` correlation for Classic and Blocks; no phone/email order matching and no new order identifiers.
- Retain distinct `ORDER_PLACED`, `ORDER_PAID` and `ORDER_CANCELLED` kinds, stable eventId and deduplicated Action Scheduler retry payloads.
- Avoid silently losing known terminal events on transport exhaustion: provide bounded non-PII failure evidence and safe retry/replay handling within existing publisher facilities.
- Handle duplicate payment callbacks, cancellation repeats, and changed status after cancellation without falsely reversing an observed paid outcome.

## Out of Scope

- No new provider status-polling endpoint, local guest-session verification, new Woo database table, unbounded retry loop, new API route or third-party customer-data exposure.

## Requirements

- Do not equate order placement with payment. A placed unpaid order suppresses abandoned-checkout reminders by default, pending any separately approved unpaid-order policy.
- Use existing outbound event contract and Woo order metadata; idempotency and at-least-once transport assumptions remain explicit.
- Exhausted retries are visible operational failures, not evidence that Moda learned the paid outcome.

## Work Items

- [ ] Implement and verify paid-state webhook/status coverage through Woo order APIs.
- [ ] Extend HPOS/Classic/Blocks and gateway-specific placed→paid→cancelled/failed/refunded cases.
- [ ] Test duplicate callbacks, retry exhaustion and fixed eventId replay without losing customer checkout continuity.

## Interfaces / Contracts

- Existing `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED` payload shape and POST `/v1/woocommerce/activity`; consumer is ARCH-048-BACKGROUND-002.
- The source of truth for payment is the Woo order lifecycle, but Moda is aware only of authenticated events successfully delivered.

## Dependencies

- `ARCH-035-WOOCOMMERCE-008`
- `ARCH-035-API-019`

## Enables

- `ARCH-048-BACKGROUND-003`
- `ARCH-048-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Confirmed paid or cancelled Woo state transition with a Moda checkout key produces the correct existing bounded event, regardless of whether a particular gateway called `payment_complete`.
- [ ] No unproven `ORDER_PAID` signal, duplicate terminal action, unscoped order linkage or exposure of merchant WordPress checkout-reading routes.
- [ ] Bounded retry exhaustion produces actionable, privacy-safe diagnostics rather than being misclassified as successful delivery.

## Validation

- [ ] Woo PHPUnit/HPOS/Classic and Checkout Blocks lifecycle fixtures for diverse gateways/status transitions.
- [ ] Action Scheduler/API contract fixtures and relevant checkout regression checks plus `git diff --check`.

## Stop Condition

After only this task's work, criteria and required validation, complete the Completion Report with the launcher-resolved dedicated parent and implementation worktree paths, isolation, start-of-attempt synchronisation and repository revision evidence. Change to `review`, return to `moda_architect` and **STOP**. Do not start dependent work. Superseded tasks must not be claimed.

## Implementation Notes

- Do not promise detection of a completely lost event; ARCH-048 explicitly acknowledges that limitation without provider lookup.

- Use `/moda-task` preparation with the real developer workspace before code execution. Do not treat the snapshot as a Git branch; do not edit any `docs/decisions/**/_index.md` during this architecture session. Validate actual repository scripts rather than guessing commands. Respect assigned repository and task-document ownership.

## Completion Report

### Status

In Progress — developer Attempt 1 claimed after explicit takeover from agent execution.

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

## Developer Execution Ownership Amendment (Attempt 1)

- Invocation: `/moda_developer_create ARCH-048-WOOCOMMERCE-003` explicitly requested developer execution. `assigned_agent: moda_woocommerce` is unchanged; execution and completion modes are now `developer`.
- Claim: `status: in_progress`, `executor: developer`, `claimed_at: 2026-10-26T14:25:27Z`, `attempt: 1`.
- Dependency verification: `ARCH-035-WOOCOMMERCE-008` and `ARCH-035-API-019` both resolved `complete` before claim.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-WOOCOMMERCE-003`, branch `task/ARCH-048-WOOCOMMERCE-003`, clean at start revision `2624d6445e6d642568d521d18f3e277ea629950e`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-WOOCOMMERCE-003`, branch `task/ARCH-048-WOOCOMMERCE-003`, clean at start revision `fe0c9de7446082e276b589fc58756ea1ac9fb03a`.
- Synchronization: fetched `origin --prune` in both task worktrees. No remote task branch existed at preparation; both task branches start at current `origin/main`, which is an ancestor of each worktree HEAD. No implementation changes have been made in this attempt.
