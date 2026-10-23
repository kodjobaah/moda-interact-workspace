---
id: ARCH-048-SYSTEM-TEST-001
architecture_id: ARCH-048
title: Certify Woo abandoned checkout through first billed WhatsApp recovery
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 75
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-048-WOOCOMMERCE-001
  - ARCH-048-WOOCOMMERCE-002
  - ARCH-048-API-001
  - ARCH-048-API-002
  - ARCH-048-BACKGROUND-001
  - ARCH-048-BACKGROUND-002
  - ARCH-048-BACKGROUND-003
  - ARCH-048-BACKGROUND-004
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-004
  - ARCH-046-WOOCOMMERCE-003
  - ARCH-045-BACKGROUND-005
enables: []
created: 2026-10-23
updated: 2026-10-23
---

# ARCH-048-SYSTEM-TEST-001: Certify Woo abandoned checkout through first billed WhatsApp recovery

## Architecture

- Architecture ID: `ARCH-048`.
- Canonical architecture: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`.
- Coordinator: `moda_architect`.
- **Lifecycle:** portable review definition based on the 23 October 2026 workspace snapshot, **defined but not materialised**. No branch/worktree, commit, claim, implementation or acceptance is implied. Re-gate against the developer's canonical workspace before execution.

## Objective

Independently certify the complete authenticated Woo checkout/order event flow, current-state verification, first recovery admission and correct billing/WhatsApp delivery without rewriting implementations.

## Context

ARCH-035-SYSTEM-TEST-002 validates capture only; ARCH-046-SYSTEM-TEST-002 validates consent-specific scenarios. This task validates ARCH-048’s integrated Woo recovery lifecycle after all implementation, consent, infrastructure (if any) and developer manual checks are complete.

## Scope

- Provision disposable LocalWP/WooCommerce (Classic + Blocks and HPOS) with authenticated plugin/API, separate Woo capture and Background worker queues, current provider-read grant and isolated test database/Redis.
- Prove checkout->API queue->Background delayed maturity->live Woo state->first CheckoutRecovery->initial attempt->existing billing->Meta stub/sandbox delivery with persisted evidence.
- Inject updates, empty cart, order-first, order placed-unpaid, paid, cancelled, late/duplicate/unreceived events, checkout/contact change, provider session expiry, API read 403/5xx, worker crash, queue job loss and concurrency near send.
- Verify exact customer/phone/consent/STOP, no consent-triggered wakeup, merchant Support notice deduplication, verified Marketing category, and no send/charge on denial.
- Assert billing credit-source allocation (including purchased credits), idempotent UsageReservation/UsageEvent, credit release/compensation, correct recovery and conversation status.

## Out of Scope

- No production messages to real customers, provider billing purchases or merchant site mutations outside disposable fixtures.
- No feature implementation, schema migration, new reconciliation engine or additional system-test prerequisite for non-test tasks.
- No `docs/decisions/**/_index.md` updates before the developer explicitly ends architecture reconciliation.

## Requirements

- Use black-box contracts and real module boundaries where practical; distinguish mocked provider proof from real Woo guest-session integration evidence.
- System test is **terminal**: execute only after all prerequisite task statuses are complete and architect-accepted and after developer manual validation opportunity.
- Record environment, queue identities, provider state responses, row/attempt/credit evidence and timestamps without logging phone numbers, tokens, credentials or full customer payloads.

## Work Items

- [ ] Create/extend independently reviewable fixtures, executors, assertions and scenario orchestration in the system-test repo.
- [ ] Run positive and negative checkout/order/lookup/consent/STOP/billing cases, including failure injection.
- [ ] Collect reproducible evidence and Completion Report, stop for architect review.

## Interfaces / Contracts

- ARCH-035 existing Woo ingress/capture contracts; ARCH-048 plugin/API and Background state/maturity/outreach contracts.
- ARCH-046 first-creation current consent and final-send STOP/Marketing checks; ARCH-045 authoritative STOP precedence.
- Existing CheckoutRecovery, outreach/usage/conversation entities and billing attribution.

## Dependencies

- `ARCH-048-WOOCOMMERCE-001`
- `ARCH-048-WOOCOMMERCE-002`
- `ARCH-048-API-001`
- `ARCH-048-API-002`
- `ARCH-048-BACKGROUND-001`
- `ARCH-048-BACKGROUND-002`
- `ARCH-048-BACKGROUND-003`
- `ARCH-048-BACKGROUND-004`
- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-046-WOOCOMMERCE-003`
- `ARCH-045-BACKGROUND-005`

## Enables

None

## Acceptance Criteria

- [ ] Exactly one first CheckoutRecovery and eligible credited send for true abandoned nonempty checkout with verified grant.
- [ ] Paid, cancelled, empty, unavailable, ambiguous or unconsented checkout yields no improper row or send; lost `ORDER_PAID` is caught by fresh provider lookup.
- [ ] Replays, race windows, order-first and terminal in-flight worker cases do not duplicate row or charge.
- [ ] Complete billing/credit and merchant Support trace is reproducible from system-test evidence.

## Validation

- [ ] Execute full scenario suite on isolated local stack with actual Woo plugin provider state reader and real BullMQ/Postgres where possible.
- [ ] Record per-case proof and negative outcomes, run system-test repository validation and `git diff --check`.

## Stop Condition

After the specified work, acceptance criteria and required validation are satisfied, record launcher-resolved **dedicated** parent/implementation task worktrees, start-of-attempt synchronization and recursive submodule evidence in the Completion Report. Change task state to `review`, return to `moda_architect` and **STOP**. Do not start an enabled task. The repo agent must not mark its own task Complete.

## Implementation Notes

Do not treat completion of ARCH-035 capture testing as proof of live recovery, or mock state-query success as proof of guest Woo session lookup. No non-system-test task may depend on this terminal task.

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
