---
id: ARCH-048-BACKGROUND-003
architecture_id: ARCH-048
title: Mature eligible Woo candidates and create the first CheckoutRecovery
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-048-API-002
  - ARCH-048-BACKGROUND-001
  - ARCH-048-BACKGROUND-002
  - ARCH-048-WOOCOMMERCE-002
  - ARCH-046-BACKGROUND-001
enables:
  - ARCH-048-BACKGROUND-004
  - ARCH-046-BACKGROUND-002
created: 2026-10-23
updated: 2026-10-23
---

# ARCH-048-BACKGROUND-003: Mature eligible Woo candidates and create the first CheckoutRecovery

## Architecture

- Architecture ID: `ARCH-048`.
- Canonical architecture: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.
- Coordinator: `moda_architect`.
- **Lifecycle:** portable review definition based on the 23 October 2026 workspace snapshot, **defined but not materialised**. No branch/worktree, commit, claim, implementation or acceptance is implied. Re-gate against the developer's canonical workspace before execution.

## Objective

Turn a matured Woo candidate into exactly one first `CheckoutRecovery` only after authoritative checkout/order verification, exact customer linkage, current consent and existing capacity/policy admission.

## Context

Shopify materialisation uses a live abandoned-checkout lookup before recovery creation; ARCH-035 Woo consumers have no such path. ARCH-046-BACKGROUND-001 owns the exact-recipient current-consent reader; ARCH-046-BACKGROUND-002 later adds missing-consent merchant notices at this newly approved seam.

## Scope

- Consume only the current checkout-keyed delayed Woo candidate; recheck indexed job generation, last-activity maturity, latest order fence, shop installation and merchant policy/entitlement under the narrow checkout lock.
- Call API-002 for fresh Woo current cart and verified linked order; reject empty, paid, cancelled, expired, ambiguous and unverified states. Apply explicit merchant policy to unpaid placed orders rather than assuming checkout abandonment.
- Resolve/store the correct **shop-scoped** Customer and current CustomerPhone from provider-backed shopper linkage; do not trust mutable event contact as a verified identity or conflate same phone across shops.
- Use ARCH-046-BACKGROUND-001 exact-recipient consent/STOP and merchant suppression reader before **first** CheckoutRecovery INSERT, attempt or billing. Expose a bounded admission seam for ARCH-046-BACKGROUND-002 missing-consent SYSTEM Support notice integration.
- Reuse existing `CheckoutRecovery` data, status history, generation uniqueness and service-level idempotent creation/normalised basket mapping. Do not send or charge in this task.

## Out of Scope

- No initial send or credits (BACKGROUND-004 owns those).
- No missing-consent Support notifier implementation (ARCH-046-BACKGROUND-002 owns it).
- No new CustomerPhone consent write or consent-driven wakeup; no database migration.
- No `docs/decisions/**/_index.md` updates before the developer explicitly ends architecture reconciliation.

## Requirements

- Without authoritative provider verification, return a bounded deferred/unavailable decision, not `abandoned`. Retry infrastructure failure with limits; no stale snapshot fallback.
- Current valid customer-authorised marketing consent must be positive for the exact shop+phone; customer STOP overrides any grant. No first recovery row/attempt on unknown/revoked/ambiguous permission.
- Concurrent workers, duplicate delayed jobs, paid/order-first races and reopened checkout keys must not create duplicates; `CheckoutRecovery` `(shopId, checkoutToken, generation)` uniqueness remains authoritative.
- Generation and lastExternalActivityAt reflect genuine same-checkout activity; respect existing eligible merchant settings and billable capacity without consuming credits yet.

## Work Items

- [ ] Implement Woo matured candidate adapter using API-002 live state and BACKGROUND-002 fence.
- [ ] Resolve exact customer/phone, check existing consent and entitlement, idempotently materialise row using existing services.
- [ ] Expose consent denial/notification seam for ARCH-046-BACKGROUND-002 and add tests for all denial, race, retry and success cases.

## Interfaces / Contracts

- Input: bounded Woo matured-candidate envelope from BACKGROUND-001; provider observations from ARCH-048-API-002.
- Output: existing CheckoutRecovery, status history and handoff to existing outreach workflow; consent policy from ARCH-046-BACKGROUND-001.
- Future ARCH-046-BACKGROUND-002 composes this seam for idempotent shop-scoped missing-consent merchant notifications, without implementing checkout engine twice.

## Dependencies

- `ARCH-048-API-002`
- `ARCH-048-BACKGROUND-001`
- `ARCH-048-BACKGROUND-002`
- `ARCH-048-WOOCOMMERCE-002`
- `ARCH-046-BACKGROUND-001`

## Enables

- `ARCH-048-BACKGROUND-004`
- `ARCH-046-BACKGROUND-002`

## Acceptance Criteria

- [ ] A genuinely mature, verified nonempty unpaid checkout with correct customer, grant and entitlement yields exactly one first recovery.
- [ ] Empty/paid/cancelled/expired/inactive/unavailable/ambiguous/not-consented cases create zero recovery rows, attempts, charges and messages.
- [ ] A later consent grant by itself does not schedule a recovery; only a subsequent ordinary checkout event can initiate evaluation.
- [ ] No duplicate recovery across racing jobs or event replays; no accidental Shopify path changes.

## Validation

- [ ] Focused integration/unit tests for maturity, customer/phone, provider errors, consent, duplicates, order-first and concurrent paid race.
- [ ] Existing recovery materialisation/Shopify admission regressions and declared lint/build checks, `git diff --check`.

## Stop Condition

After the specified work, acceptance criteria and required validation are satisfied, record launcher-resolved **dedicated** parent/implementation task worktrees, start-of-attempt synchronization and recursive submodule evidence in the Completion Report. Change task state to `review`, return to `moda_architect` and **STOP**. Do not start an enabled task. The repo agent must not mark its own task Complete.

## Implementation Notes

Deliver engine and fail-closed admission seam first. Do not turn on Woo initial sends until `ARCH-046-BACKGROUND-002`, confirmed completed final-send fence and BACKGROUND-004 are integrated. If no exact canonical phone/CustomerPhone can be identified, defer instead of inventing a customer.

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
