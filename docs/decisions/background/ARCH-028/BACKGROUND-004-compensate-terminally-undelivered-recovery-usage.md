---
id: ARCH-028-BACKGROUND-004
architecture_id: ARCH-028
title: Compensate generic terminally undelivered recovery usage
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-002
  - ARCH-028-DATABASE-001
  - ARCH-027-BACKGROUND-001
enables:
  - ARCH-028-BACKGROUND-011
  - ARCH-028-BACKGROUND-009
created: 2026-10-05
updated: 2026-10-08
---

# Compensate generic terminally undelivered recovery usage

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Make the provider-status job idempotently release/compensate the exact terminally undelivered recovery source for every non-committed-purchased case, and remove the exact undelivered outbound automated-message hard-limit usage.

## Context

Compensation authority is durable FAILED/131026 `ConversationMessage` evidence plus the exact linked recovery/UsageReservation lineage. `RecoveryOutreachAttempt.status` is not an eligibility gate because it may already be `NO_RESPONSE`.

The provider-status job must call the compensation orchestrator after its status transaction on every relevant replay. If correction fails, the job fails/retries; if the message is already FAILED the retry still calls compensation.

Committed purchased-credit compensation is deliberately deferred to BACKGROUND-009 because it requires final ARCH-027 refund state. A still-RESERVED purchased source can be safely released here because no provider monetary refund exists yet.

ARCH-027-BACKGROUND-001 makes positive recovery `UsageEvent.provider` explicit for Shopify and Woo. Each new negative correction must preserve the *original committed UsageEvent* `shopId` and `provider` (and exact original correction lineage), not inherit Prisma's default `SHOPIFY` provider. Corrections must remain non-reportable to Shopify regardless of the positive source's reporting state.

## Scope

- Re-lock/re-read exact message/attempt/recovery/reservation after provider-status convergence.
- Eligibility: durable `ConversationMessage.status=FAILED`, provider code `131026`, exact recovery source; no attempt-status requirement.
- Release any eligible still-RESERVED reservation through its existing source owner.
- Compensate COMMITTED lifetime-Free, paid-included and promotional sources with one exact negative UsageEvent/counter correction and DATABASE-001 disposition. Write the correction's `shopId` and `provider` explicitly from the locked original committed recovery UsageEvent; keep its `shopifyReportState=NOT_APPLICABLE` and all Shopify-reporting identifiers null, including when the original was Shopify-reportable.
- For COMMITTED purchased source return a stable bounded `PURCHASED_COMPENSATION_REQUIRED`/equivalent result without suppression/notification side effects; BACKGROUND-009 completes it.
- Idempotently remove/delete the exact `OUTBOUND_AUTOMATED_MESSAGE` UsageEvent associated with the undelivered message so the hard limit is not consumed.
- Integrate this orchestrator into the provider-status job after the status transaction.

## Out of Scope

- COMMITTED purchased-credit source adjustment/refund holds (BACKGROUND-009).
- Provider monetary refunds.
- Reachability writes/pre-admission gate.
- Synchronous HTTP failure path.
- Missing phone.
- Merchant notification.

## Requirements

- [ ] Attempt status is not compensation eligibility authority.
- [ ] Message DELIVERED/READ before compensation prevents correction.
- [ ] RESERVED release creates no negative UsageEvent.
- [ ] COMMITTED lifetime-Free/paid-included/promotional correction is exact and idempotent.
- [ ] Every negative correction preserves the original committed recovery UsageEvent's Shop and `provider` (`SHOPIFY` or `WOOCOMMERCE`), rather than a schema default, and is never submitted for Shopify external reporting.
- [ ] Closed/expired source uses Option A historical-only semantics, never a cross-period make-good credit.
- [ ] COMMITTED purchased returns deferred bounded outcome and does not guess ARCH-027 monetary state.
- [ ] Terminally undelivered outbound message no longer consumes `OUTBOUND_AUTOMATED_MESSAGE` hard-limit usage.
- [ ] Provider-status replay always re-invokes the idempotent orchestrator when durable terminal evidence still exists.
- [ ] Late positive delivery after completed compensation does not claw compensation back.
- [ ] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [ ] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [ ] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [ ] Add generic compensation orchestrator using existing reservation source owners.
- [ ] Add post-status provider-job invocation and retry semantics.
- [ ] Implement RESERVED release all sources.
- [ ] Implement lifetime-Free, paid-included and promotional COMMITTED correction/disposition with explicit original Shop/provider lineage and non-reportable correction fields.
- [ ] Add committed-purchased deferred result.
- [ ] Add exact outbound hard-limit usage correction/removal.
- [ ] Add NO_RESPONSE eligibility, replay and late-delivery race tests.
- [ ] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes DATABASE-001 compensation lineage and ARCH-027 provider-correct recovery UsageEvent semantics. Produces bounded outcomes for later reachability/notification, including release/restoration/historical/deferred-purchased results.

## Dependencies

- `ARCH-028-BACKGROUND-002`
- `ARCH-028-DATABASE-001`
- `ARCH-027-BACKGROUND-001`

## Enables

- `ARCH-028-BACKGROUND-011`
- `ARCH-028-BACKGROUND-009`

## Acceptance Criteria

- [ ] WAITING/NO_RESPONSE/etc. attempt state cannot block otherwise eligible compensation.
- [ ] RESERVED source is released exactly once.
- [ ] Generic COMMITTED source creates exactly one negative correction and source adjustment.
- [ ] On both Shopify and Woo, negative compensation uses the exact original committed UsageEvent's `shopId` and `provider`; Woo corrections are never mislabelled SHOPIFY by default, and no correction enters Shopify publication.
- [ ] Closed/expired source is historical-only; no make-good credit is created.
- [ ] COMMITTED purchased source is not modified by this task and returns deferred outcome.
- [ ] Outbound automated-message hard-limit usage is removed exactly once for terminally undelivered message.
- [ ] Provider-status job retry after prior message convergence still executes compensation.
- [ ] Compensation failure makes the job retryable; duplicate retries cannot double-adjust accounting.
- [ ] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [ ] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [ ] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused unit/PostgreSQL integration for each generic source, RESERVED release, NO_RESPONSE race, replay, hard-limit correction, late-delivery race, **positive/negative UsageEvent Shop/provider parity on Shopify and Woo**, correction non-publication and duplicate replay, full Background tests/build and `git diff --check`.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not make the provider-status database transaction perform external/queue work. Commit message/attempt convergence first, then invoke the idempotent compensation owner; job failure/retry supplies recovery.

Prefer a thin compensation coordinator delegating to focused eligibility, usage-source correction and outbound-hard-limit correction modules. Source-specific accounting branches must not accumulate into one large switch-heavy service.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
