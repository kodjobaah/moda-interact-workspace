---
id: ARCH-048-WOOCOMMERCE-002
architecture_id: ARCH-048
title: Publish empty basket updates for existing Woo checkout keys
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
created: 2026-10-23
updated: 2026-10-23
---

# ARCH-048-WOOCOMMERCE-002: Publish empty basket updates for existing Woo checkout keys

## Architecture

- Architecture ID: `ARCH-048`.
- Canonical architecture: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.
- Coordinator: `moda_architect`.
- **Lifecycle:** portable review definition based on the 23 October 2026 workspace snapshot, **defined but not materialised**. No branch/worktree, commit, claim, implementation or acceptance is implied. Re-gate against the developer's canonical workspace before execution.

## Objective

Make clearing a Woo basket produce an ordinary, deduplicated `CHECKOUT_UPDATED` event so Background can cancel its existing checkout-keyed recovery timer.

## Context

`CheckoutSnapshot::fromCart()` currently returns `null` for `array() === $lines`; `CheckoutCapture::capture()` therefore publishes nothing when a previously nonempty cart is emptied. `woo.activity.v1` already permits `checkout.items: []`; no new transport event kind is needed.

## Scope

- Modify Classic and Blocks checkout observation so transition from a previously published nonempty basket to empty emits a bounded `CHECKOUT_UPDATED` with the **same existing checkoutKey**, `items: []`, appropriate zero total, a fresh event ID and timestamp.
- Reuse the existing `CheckoutActivityPublisher`/Action Scheduler retry semantics, stable event ID on retries and snapshot fingerprint deduplication.
- Do not generate a new checkout key solely for an empty initial cart; prevent repeated empty hooks creating extra messages. Ensure subsequent genuine nonempty additions can schedule a new evaluation.

## Out of Scope

- New activity schema, new database row, separate cancel API endpoint or direct queue manipulation from PHP.
- Modification of ARCH-035 task definition, hosted API business policy, billing/consent.
- No `docs/decisions/**/_index.md` updates before the developer explicitly ends architecture reconciliation.

## Requirements

- Use the currently assigned checkout generation; no implicit generation reset or order-key reassignment.
- `items: []` means an actually empty cart; a basket with >50 items or an incomplete snapshot must **not** be represented as empty.
- Classic/Blocks capture must not interrupt customer checkout or payment if queuing fails.

## Work Items

- [ ] Capture genuine empty-cart transition and send v1 `CHECKOUT_UPDATED` through existing publisher.
- [ ] Keep fingerprint/retry semantics; test initial-empty, nonempty->empty, repeated-empty, and empty->nonempty transitions.
- [ ] Run focused PHP/Woo/JS regression validation.

## Interfaces / Contracts

- Uses `woo.activity.v1` `CHECKOUT_UPDATED` and existing validated `checkout.items: []` API payload.
- Keeps existing Action Scheduler publish credentials, idempotency and checkoutKey.

## Dependencies

- `ARCH-035-WOOCOMMERCE-007`
- `ARCH-035-API-008`

## Enables

- `ARCH-048-BACKGROUND-003`

## Acceptance Criteria

- [ ] One empty event for a real basket-clear transition; repeat hooks do not flood the API.
- [ ] No empty event on first never-active cart, a >50-item basket, or invalid current cart.
- [ ] Existing checkout/order capture behaviour and shopper checkout continuity remain intact.

## Validation

- [ ] Unit/integration PHPUnit with guest/customer Classic + Blocks, and 503/retry unchanged event identity.
- [ ] Existing plugin lint, build/test scripts required by changed files and `git diff --check`.

## Stop Condition

After the specified work, acceptance criteria and required validation are satisfied, record launcher-resolved **dedicated** parent/implementation task worktrees, start-of-attempt synchronization and recursive submodule evidence in the Completion Report. Change task state to `review`, return to `moda_architect` and **STOP**. Do not start an enabled task. The repo agent must not mark its own task Complete.

## Implementation Notes

The Woo producer publishes state, not a recovery decision. Background-001 must interpret `items: []` as candidate removal and suppress racing matured jobs.

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
