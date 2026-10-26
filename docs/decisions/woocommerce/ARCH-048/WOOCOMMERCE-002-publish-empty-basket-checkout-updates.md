---
id: ARCH-048-WOOCOMMERCE-002
architecture_id: ARCH-048
title: Publish complete Woo checkout updates including cleared baskets
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 25
executor: developer
claimed_at: 2026-10-26T14:25:37Z
attempt: 1
depends_on:
- ARCH-035-WOOCOMMERCE-007
- ARCH-035-API-008
enables:
- ARCH-048-BACKGROUND-003
- ARCH-048-SYSTEM-TEST-001
created: '2026-10-23'
updated: '2026-10-26'
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

In Progress — Developer Attempt 1. The developer explicitly took over this ready agent-owned task through `/moda_developer_create`. Dependencies ARCH-035-WOOCOMMERCE-007 and ARCH-035-API-008 are confirmed complete. Canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-WOOCOMMERCE-002` starts at `2624d6445e6d642568d521d18f3e277ea629950e`; canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-WOOCOMMERCE-002` starts at `fe0c9de7446082e276b589fc58756ea1ac9fb03a`. Both were clean and synchronized to their current `origin/main`; recursive implementation submodules were initialized and verified.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Implementation validation is outstanding. Start-of-attempt route, branch, worktree and submodule synchronization checks passed; no implementation tests have been run.

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

## Execution Ownership Amendment

- Date: 2026-10-26
- Change: The developer explicitly invoked `/moda_developer_create` for this ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_woocommerce`, coordinator, repository, task scope, acceptance criteria and validation requirements.
- Claim state: Developer Attempt 1 was claimed after confirming both dependencies complete and preparing the canonical parent and implementation worktrees.
