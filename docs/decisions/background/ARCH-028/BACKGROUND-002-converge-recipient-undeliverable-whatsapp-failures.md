---
id: ARCH-028-BACKGROUND-002
architecture_id: ARCH-028
title: Converge recipient-undeliverable WhatsApp delivery failures
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-001
  - ARCH-028-MESSAGING-001
enables: []
created: 2026-10-03
updated: 2026-10-03
---

# Converge recipient-undeliverable WhatsApp delivery failures

## Architecture

Architecture ID:

`ARCH-028`

Architecture document:

`docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator:

`moda_architect`

## Objective

Classify the bounded Meta provider code `131026` as a **recipient-undeliverable** delivery outcome and idempotently converge a linked recovery outreach attempt from `WAITING_FOR_RESPONSE` to `FAILED` so an already-scheduled no-response follow-up cannot send another recovery message to the same currently unreachable recipient.

This task does **not** restore merchant credits, write recipient suppression/reachability state or notify the merchant. Those remain later ARCH-028 outcomes.

## Context

`ARCH-028-BACKGROUND-001` adopts the exact published dual-version Shared provider-status contract and persists bounded FAILED evidence on `ConversationMessage`. `ARCH-028-MESSAGING-001` then begins emitting canonical v3 events containing bounded provider error-code evidence.

The current provider-status consumer updates `ConversationMessage` monotonically, but it does not reconcile the linked `RecoveryOutreachAttempt`. The current recovery finalisation path can therefore leave:

```text
ConversationMessage = FAILED
RecoveryOutreachAttempt = WAITING_FOR_RESPONSE
CheckoutRecovery = MESSAGE_SENT
follow-upDueAt = set
```

The queued follow-up processor is protected by the attempt-state CAS in `markNoResponseIfWaiting(...)`, but the durable attempt still incorrectly says it is waiting for a customer response. This task makes that convergence explicit and testable.

Meta error `131026` is deliberately treated as a **bucket indicating that this message was undeliverable to the recipient**. It must **not** be persisted or presented as proof that the person permanently has no WhatsApp account. The recipient may become reachable later; temporary suppression/reachability policy is owned by a later task.

Current canonical implementation owners include:

```text
src/services/whatsapp-provider-status.service.ts
src/services/recovery-outreach-attempt.service.ts
src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts
```

New bounded owners may be introduced under those domains, for example:

```text
src/services/whatsapp-provider-failure-classifier.ts
src/services/checkout-recovery/recovery-whatsapp-delivery-failure.service.ts
```

The exact local filenames may vary when repository-local conventions justify it, but provider-code policy must have one canonical Background owner and recovery-specific convergence must not be duplicated inside multiple callers.

## Scope

Repository-owned changes in `moda-interact-background`:

- add one pure bounded WhatsApp provider-failure classifier;
- classify exact normalized provider code `131026` as `RECIPIENT_UNDELIVERABLE`;
- leave absent and all other provider codes unclassified by this task;
- integrate the classifier with `WhatsAppProviderStatusService` after the BACKGROUND-001 message-level failure evidence update has been resolved;
- when the resulting durable message is FAILED with provider code `131026` and is linked to a recovery outreach attempt currently `WAITING_FOR_RESPONSE`, atomically/guardedly transition that attempt to `FAILED` with one stable bounded failure code;
- make a due no-response follow-up for such a FAILED initial attempt explicitly non-actionable before any policy, billing or provider-send work;
- preserve duplicate/out-of-order status monotonicity and existing delivered/read usage semantics;
- add focused unit tests for classifier, provider-status convergence and follow-up suppression.

Expected implementation/test surface:

```text
moda-interact-background/src/services/whatsapp-provider-failure-classifier.ts                   # new, or equivalent bounded owner
moda-interact-background/src/services/whatsapp-provider-status.service.ts
moda-interact-background/src/services/checkout-recovery/recovery-whatsapp-delivery-failure.service.ts  # new, or equivalent bounded owner
moda-interact-background/src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts
moda-interact-background/tests/unit/services/whatsapp-provider-failure-classifier.test.ts       # new, or equivalent
moda-interact-background/tests/unit/services/whatsapp-provider-status.service.test.ts
moda-interact-background/tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts
```

## Out of Scope

- Any database schema or migration change.
- Any Shared or Messaging change.
- Synchronous HTTP/provider-send error classification; this task is the asynchronous provider-status convergence path only.
- Treating `131026` as proof that the person has no WhatsApp account.
- Classifying rate-limit, configuration, template, policy or other provider codes.
- `WhatsAppRecipientReachability` writes or `suppressUntil` policy.
- Releasing RESERVED recovery usage.
- Compensating already COMMITTED recovery usage.
- Restoring lifetime-free, paid-included, purchased or promotional capacity.
- Creating negative correction `UsageEvent` rows.
- Shopify usage correction publication.
- Merchant support/system notification.
- Changing `CheckoutRecovery.status`; it remains as currently represented until later ARCH-028 reconciliation work proves a different durable state is required.
- Physically deleting/cancelling the already-enqueued BullMQ follow-up job; this task makes it non-actionable through durable attempt state.
- Changing non-recovery outbound-message behaviour.
- `docs/architecture/_index.md` updates.

## Requirements

### R1 — One pure provider-failure classifier

Create one Background-owned pure classifier whose input is only bounded normalized provider failure evidence and whose result for this task is:

```text
providerCode == "131026"
    -> RECIPIENT_UNDELIVERABLE

providerCode absent or any other value
    -> UNCLASSIFIED
```

The comparison uses the canonical trimmed string persisted/parsed through the Shared v3 contract. Do not inspect raw Meta webhook payloads, titles, messages or `error_data` in Background.

Do not name the classification `NOT_ON_WHATSAPP`, `NO_WHATSAPP_ACCOUNT` or another permanent-account assertion.

### R2 — Preserve provider-status monotonicity

The existing `WhatsAppProviderStatusService` remains authoritative for message status ordering.

Only run recipient-delivery convergence when all of the following are true after applying the current event semantics:

- the incoming normalized status is `FAILED`;
- the durable message is / remains `FAILED` rather than `DELIVERED` or `READ` winning monotonic ordering;
- the durable bounded provider failure code resolves to `131026`;
- the message is outbound and belongs to a durable Shop exactly as required by the existing service.

A late `FAILED/131026` event must never regress a `DELIVERED` or `READ` message and must never fail its outreach attempt.

A legacy v2 FAILED message that is later enriched by an accepted v3 `131026` event must be eligible for convergence even when the message status was already `FAILED` before the v3 event.

### R3 — Converge only the linked waiting recovery attempt

If the failed message is linked through `RecoveryOutreachAttempt.outboundMessageId`, update only that exact attempt.

The guarded durable transition is:

```text
WAITING_FOR_RESPONSE
    -> FAILED
failureCode = WHATSAPP_RECIPIENT_UNDELIVERABLE
```

Required protections:

- include the message/attempt binding in the guard where practical;
- never regress or overwrite `ENGAGED`, `NO_RESPONSE`, `CANCELLED`, `CAPACITY_BLOCKED` or an existing `FAILED` attempt;
- an exact duplicate/replayed terminal failure is idempotent;
- do not overwrite a different pre-existing `failureCode` on an already-terminal attempt;
- if no RecoveryOutreachAttempt is linked, preserve the message-level FAILED evidence and do not invent a recovery association.

Do not clear `sentAt`, `outboundMessageId` or `followUpDueAt`; they remain historical evidence. Attempt status is the authority that makes the no-response work non-actionable.

### R4 — Keep message + attempt convergence in the existing provider-status transaction

When an eligible linked attempt exists, apply the guarded attempt transition inside the same existing Serializable provider-status transaction as the message FAILED/evidence application.

Do not introduce Redis/BullMQ operations or external provider calls inside that transaction.

A concurrent customer-engagement transition is allowed to win: if the attempt is no longer `WAITING_FOR_RESPONSE`, recipient-failure convergence must not overwrite that later durable state.

### R5 — Make due follow-up suppression explicit

Update the recovery follow-up processor so an initial attempt whose durable status is already `FAILED` is suppressed before:

- customer-response lookup beyond what is necessary to load the recovery;
- `markNoResponseIfWaiting(...)`;
- policy resolution;
- execution eligibility;
- template selection;
- billing admission/revalidation;
- any outbound provider call.

Use one stable internal suppression reason such as `initial-delivery-failed`. This is not a Shared/public contract.

Do not physically delete the queued follow-up job in this task. A retained/delivered BullMQ job must safely no-op from durable state.

### R6 — Preserve non-terminal failure behaviour

Provider codes other than exact `131026`, including absent codes, remain message-level evidence only in this task.

They must not:

- fail the recovery attempt through this new classifier;
- suppress the recipient;
- restore/compensate recovery capacity;
- notify the merchant;
- change retry policy.

Future ARCH-028 tasks may extend the classifier only through explicit architecture review.

### R7 — Preserve existing delivered/read accounting

Do not alter:

- `DELIVERED_WHATSAPP_MESSAGE` usage-event idempotency;
- `deliveredUsageKey(...)`;
- provider response summary bounds;
- SENT / DELIVERED / READ ordering;
- the current rule that a later DELIVERED/READ may advance an earlier FAILED message;
- existing provider-status transaction retry behaviour.

Historical `providerFailureCode` / `failedAt` evidence added by BACKGROUND-001 may remain when a later delivery succeeds; this task does not erase historical evidence.

### R8 — Bounded logging only

If new logs are required, use the canonical Shared structured logger already used by `WhatsAppProviderStatusService`.

Allowed fields are bounded identifiers/outcomes such as:

```text
messageId
outreachAttemptId
providerCode
classification
outcome
```

Do not log phone numbers, message content, provider webhook bodies, provider error detail strings or customer data.

## Work Items

- [ ] Add the pure provider-failure classifier with exact `131026` / unclassified behaviour.
- [ ] Add focused classifier tests.
- [ ] Add one bounded recovery delivery-failure convergence owner rather than embedding duplicate attempt policy in multiple callers.
- [ ] Extend provider-status resolution to make the linked recovery attempt available for guarded convergence.
- [ ] Converge eligible `WAITING_FOR_RESPONSE` attempts to `FAILED` in the existing Serializable transaction.
- [ ] Preserve v2 FAILED -> v3 evidence enrichment convergence.
- [ ] Preserve DELIVERED/READ monotonicity and concurrent ENGAGED winner semantics.
- [ ] Add explicit failed-initial-attempt suppression before follow-up policy/billing/provider work.
- [ ] Add focused provider-status and follow-up suppression tests.
- [ ] Confirm no billing, reachability, merchant-notification or CheckoutRecovery-status changes were introduced.

## Interfaces / Contracts

Consumes the exact Shared package version adopted by:

`ARCH-028-BACKGROUND-001`

Canonical normalized evidence consumed:

```text
NormalizedWhatsAppStatus v2 | v3
v3 failure.providerCode?: string
```

Canonical classification introduced locally:

```text
RECIPIENT_UNDELIVERABLE
UNCLASSIFIED
```

Stable recovery failure code written by this task:

```text
WHATSAPP_RECIPIENT_UNDELIVERABLE
```

No new cross-repository runtime contract is introduced.

## Dependencies

- `ARCH-028-BACKGROUND-001`
- `ARCH-028-MESSAGING-001`

Both must be Complete and architect-accepted before this task becomes Ready.

## Enables

None yet. The next ARCH-028 Background task will be defined after this convergence boundary is implemented/accepted and the then-current billing/reachability code is re-inspected.

## Acceptance Criteria

- [ ] Exact provider code `131026` classifies as `RECIPIENT_UNDELIVERABLE`; missing/other provider codes remain unclassified.
- [ ] No code path asserts that `131026` proves a permanent absence of a WhatsApp account.
- [ ] A linked recovery attempt in `WAITING_FOR_RESPONSE` becomes `FAILED` with `WHATSAPP_RECIPIENT_UNDELIVERABLE` when its durable outbound message receives/retains FAILED + `131026` evidence.
- [ ] A legacy v2 FAILED message can be enriched by later v3 `131026` evidence and then converge the linked waiting attempt.
- [ ] Duplicate/replayed terminal failure evidence is idempotent.
- [ ] DELIVERED/READ message state and ENGAGED/other non-waiting attempt state are never regressed.
- [ ] A due follow-up for a FAILED initial attempt performs no policy, billing or provider-send work.
- [ ] Existing SENT/DELIVERED/READ provider-status and delivered-usage behaviour remains unchanged.
- [ ] No recipient reachability, billing compensation, merchant notification or CheckoutRecovery-status mutation is introduced.

## Validation

- [ ] `npm run prisma:generate`
- [ ] `npm run prisma:validate`
- [ ] focused classifier tests pass
- [ ] `npx vitest run tests/unit/services/whatsapp-provider-status.service.test.ts`
- [ ] `npx vitest run tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts`
- [ ] `npm run test:unit`
- [ ] `npm test`
- [ ] `npm run build`
- [ ] `git diff --check`

Before validation, inspect the current `package.json`; do not invent separate lint/typecheck scripts that the repository does not provide. `npm run build` is the repository TypeScript compilation gate.

If a documented baseline condition is encountered unchanged, record its baseline ID rather than weakening this task's validation contract.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect`, and STOP. Do not implement usage compensation, reachability suppression, merchant notification or another ARCH-028 task.

## Implementation Notes

Keep provider-code policy small. This task intentionally recognizes only exact bounded `131026` evidence because that is the recipient-undeliverable condition ARCH-028 currently needs. Do not build a speculative general Meta-error framework.

Keep the existing `WhatsAppProviderStatusService` as the queue-facing provider-status boundary. A small pure classifier and a recovery-specific convergence collaborator are preferable to making the provider-status service own recovery/billing policy directly.

Do not use an asynchronous queue publication from inside the provider-status database transaction. Recovery-attempt convergence is a same-database guarded write and should stay atomic with the FAILED evidence application.

The existing `RecoveryOutreachAttempt.outboundMessageId` relation is the authoritative recovery-attempt association. Do not correlate by phone number, customer identity or timestamps.

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
