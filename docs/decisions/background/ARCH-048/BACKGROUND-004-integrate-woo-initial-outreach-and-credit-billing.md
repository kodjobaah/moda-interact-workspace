---
id: ARCH-048-BACKGROUND-004
architecture_id: ARCH-048
title: Integrate first Woo recovery outreach with existing billing and send fences
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 48
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-048-BACKGROUND-003
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-004
  - ARCH-045-BACKGROUND-005
enables:
  - ARCH-048-SYSTEM-TEST-001
created: 2026-10-23
updated: 2026-10-23
---

# ARCH-048-BACKGROUND-004: Integrate first Woo recovery outreach with existing billing and send fences

## Architecture

- Architecture ID: `ARCH-048`.
- Canonical architecture: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.
- Coordinator: `moda_architect`.
- **Lifecycle:** portable review definition based on the 23 October 2026 workspace snapshot, **defined but not materialised**. No branch/worktree, commit, claim, implementation or acceptance is implied. Re-gate against the developer's canonical workspace before execution.

## Objective

Connect admitted first Woo `CheckoutRecovery` to existing initial-attempt, credit reservation/attribution, WhatsApp Marketing-template and compensation workflows without implementing separate Woo charging or consent systems.

## Context

ARCH-048-BACKGROUND-003 creates a verified first recovery but must not send. `ARCH-046-BACKGROUND-002` adds missing-consent admission notices; the developer confirmed `ARCH-046-BACKGROUND-004` final-send consent/STOP enforcement is complete after the uploaded snapshot. Background already has reusable recovery billing, credit-source tracking, outbound attempt and failure-compensation services.

## Scope

- Enter the existing `INITIAL` recovery outreach path using an idempotent attempt identity and current eligible shop/recipient; reuse reservation, credits (included-plan, lifetime and purchased), usage attribution and correct release/commit-on-delivery boundaries.
- Immediately before submitting the initial provider send, query API-002 **again** for the exact current checkout/order state and apply BACKGROUND-002 checkout terminal fence; if paid/cancelled/empty/expired/unknown, prevent the send and safely compensate/release any reservation.
- Invoke rather than recreate completed ARCH-046-BACKGROUND-004 current-consent/STOP/merchant opt-out and Meta-approved **Marketing**-template fence. Recheck installation, customer phone and merchant entitlement before final handoff.
- Preserve existing retry, idempotency, attempt status, conversation/recovery linkage, terminal transitions, capacity-block handling and partial-failure compensation.
- Keep first-send feature disabled until complete review and the ARCH-048 + ARCH-046 terminal validation plan passes.

## Out of Scope

- Do not change prior completed ARCH-046-BACKGROUND-004 task, implement consent collection or invent Woo-only billing ledgers.
- No proactive later follow-up scheduling beyond integration with existing independently approved paths; no Shopify billing rewrite.
- No new database schema, new provider service or direct PHP billing logic.
- No `docs/decisions/**/_index.md` updates before the developer explicitly ends architecture reconciliation.

## Requirements

- A recovery record is not a billable send: charge only at the established outbound delivery/admission accounting boundary, not on captured checkout or candidate creation.
- Keep exact credit source/purchase allocation, reservation compensation and usage event attribution; avoid double charge and leaked reserved credits.
- Final provider state + exact consent + authoritative local STOP + Marketing template must all pass even on retry or queue delay; unchecked conditions fail closed.
- Prevent terminal order race between last query and delivery as far as narrow locks/fences permit; test race explicitly and document remaining provider time-of-check/time-of-use limitation.

## Work Items

- [ ] Wire Woo `INITIAL` outreach into existing reservation/send/compensation services.
- [ ] Add API-002 final-state verification and reuse completed ARCH-046-BACKGROUND-004 consent/STOP/template guards.
- [ ] Add retries, terminal, missing credits, wrong tenant/recipient, provider failure and exact attribution tests.

## Interfaces / Contracts

- Existing CheckoutRecovery, RecoveryOutreachAttempt, usage reservation/event, outbound message, provider status and compensation contracts.
- Current provider state via ARCH-048-API-002 and Woo order fences via BACKGROUND-002.
- `ARCH-046-BACKGROUND-002` admission/merchant notice and user-confirmed completed `ARCH-046-BACKGROUND-004` final send fence; do not embed duplicate consent-check implementations.

## Dependencies

- `ARCH-048-BACKGROUND-003`
- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-045-BACKGROUND-005`

## Enables

- `ARCH-048-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Exactly one eligible first attempt/send and correct credit-source attribution for a verified checkout.
- [ ] No Meta send/charge if payment/cancellation/empty/cart expiry/consent withdrawal/STOP occurs before final handoff.
- [ ] Duplicates and failures do not overcharge or leave credit reservations stuck; consumed credits correspond to the existing successful-delivery rules.
- [ ] All outgoing initial recovery templates are Meta-approved Marketing; Utility/Authentication/unknown templates cannot send or consume credit.

## Validation

- [ ] Unit/integration tests for credit bucket attribution, reservation, compensation, retries and first-send idempotency.
- [ ] Provider-state/consent/order-fence races and existing Shopify/billing/Meta regression tests; repository declared lint/build and `git diff --check`.

## Stop Condition

After the specified work, acceptance criteria and required validation are satisfied, record launcher-resolved **dedicated** parent/implementation task worktrees, start-of-attempt synchronization and recursive submodule evidence in the Completion Report. Change task state to `review`, return to `moda_architect` and **STOP**. Do not start an enabled task. The repo agent must not mark its own task Complete.

## Implementation Notes

Before claiming, verify the user-reported post-snapshot completion of ARCH-046-BACKGROUND-004 against the canonical branch and actual shipped code. A task status in the older zip is not proof that the guard is present in the current implementation worktree.

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
