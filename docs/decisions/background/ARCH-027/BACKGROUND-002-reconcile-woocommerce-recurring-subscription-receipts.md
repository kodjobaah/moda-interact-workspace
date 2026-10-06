---
id: ARCH-027-BACKGROUND-002
architecture_id: ARCH-027
title: Reconcile WooCommerce recurring subscription webhook receipts
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
  - ARCH-027-API-005
  - ARCH-027-BACKGROUND-001
enables:
  - ARCH-027-BACKGROUND-004
  - ARCH-027-BACKGROUND-006
created: 2026-10-03
updated: 2026-10-06
---

# Reconcile WooCommerce recurring subscription webhook receipts

## Architecture

Architecture ID: `ARCH-027`

Architecture document: `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator: `moda_architect`

## Objective

Consume authenticated durable Woo **subscription-wrapper** webhook receipts and idempotently reconcile provider financial/lifecycle evidence onto the Shop's one Moda `Subscription`, without treating webhook arrival order as provider causality and without making Woo financial renewal own Moda's exact-30-day included-recovery cadence.

Core separation:

```text
Woo financial/lifecycle evidence
    -> current provider contract
    -> ACTIVE/FROZEN
    -> providerCoverageEndAt
    -> cancelAtPeriodEnd / terminal end

Moda entitlement cadence
    -> BillingPeriod exact-30-day windows
    -> BACKGROUND-006 after the first paid period
```

This task opens the first paid entitlement period on verified activation. It does not roll later entitlement periods merely because `renewed` arrived.

## Context

ARCH-027 has already fixed:

- API-003: recurring create/switch/cancel intent is persisted before provider writes and the selected paid operational `BillingPlan` is materialised before provider I/O without changing merchant entitlement;
- API-005: Woo webhooks are HMAC-verified and durably stored without business mutation;
- BACKGROUND-001: paid included recovery accounting is Woo-safe and uses `currentAllowanceQuantity ?? grantedQuantity`;
- DATABASE-001: one Subscription per Shop, durable Woo operations/receipts, mutable current allowance and nullable `Subscription.providerCoverageEndAt`.

Woo recurring webhook payloads are durable authenticated **snapshots**. Woo does not provide ARCH-027 with a signed sequence/event ID that makes `WooCommerceBillingWebhookReceipt.receivedAt` a safe causal clock. Correctness must therefore survive duplicate, delayed, concurrent and out-of-order delivery.

The accepted product decisions are:

```text
canceled != entitlement ended
renewed != allowance reset
next_payment_date != currentPeriodEnd
receivedAt != provider event order
```

## Scope

Modify only `moda-interact-background` implementation/tests needed for:

1. bounded claiming of unprocessed Woo subscription-wrapper receipts;
2. trusted provider-contract/Shop correlation;
3. field-specific evidence reconciliation across durable receipts + recurring operations + current Subscription;
4. recurring Subscription lifecycle/financial projection;
5. first paid entitlement-period creation on verified activation;
6. receipt processed/error bookkeeping;
7. integration into the existing leased billing worker cycle.

Expected implementation areas are conceptually:

```text
src/services/woocommerce-billing/
  subscription-receipt-reconciliation.service.ts
  subscription-operation-resolution.ts
  subscription-evidence-reducer.ts
  subscription-transition.service.ts

src/entrypoints/billing.ts
```

Exact repository-local filenames may differ where the accepted refactor provides a clearer bounded owner.

Update the nested `database/` gitlink to the newest compatible architect-accepted database main commit and regenerate Prisma before source changes.

Reuse the existing billing worker deployment, leased billing scheduler, Prisma transactions, current Shop/Subscription lock conventions, existing paid-period close/release semantics, `recoveryCapacityResumeService` and Shared structured logging. Do not add another worker deployment.

## Out of Scope

- Woo `charge` receipt processing.
- Top-up activation/refund settlement.
- Woo provider GET/POST/DELETE calls.
- Woo credentials.
- Time-driven entitlement rollover after the first paid period; owned by `ARCH-027-BACKGROUND-006`.
- Treating `next_payment_date` as the Moda allowance-reset boundary.
- Creating catch-up allowance periods while financial coverage was absent.
- Shopify Partner API reconciliation changes.
- Shopify same-cycle plan-change behavior.
- API webhook validation.
- API command initiation.
- Admin/Woo UI.
- Gateway changes.
- Prisma schema/migration edits other than advancing the accepted nested database gitlink.
- A Shared lifecycle-event contract.
- Updating `docs/architecture/_index.md` or any domain `_index.md`.

## Requirements

### R1 — Reuse the existing billing worker

Keep bounded PostgreSQL receipt claiming, `SKIP LOCKED` concurrency and atomic business-state/receipt completion transactions. Claim concurrency does not weaken the business-state lock: after a worker obtains the Shop/Subscription lock it must re-read the durable evidence required to derive the projection.

### R2 — Trusted tenant/contract correlation

Resolve the Shop only from trusted Woo operation/current-or-historical provider-contract evidence. Never use merchant/browser tenant input from the provider payload.

The current recurring contract may mutate the current Subscription. A historical provider contract may update only its own operation/receipt bookkeeping; it cannot pause, renew, switch, cancel, end or reactivate a newer current contract.

### R3 — Receipt arrival is not provider ordering

Do not order Woo lifecycle by:

```text
WooCommerceBillingWebhookReceipt.id
WooCommerceBillingWebhookReceipt.receivedAt
HTTP delivery order
worker claim order
```

Do not populate Shopify-oriented lifecycle watermark fields from those transport values merely to manufacture a Woo sequence.

For each claimed receipt, derive the current provider-contract projection from all relevant durable authenticated receipts for that contract, serialized Moda recurring operations, and the locked current Subscription.

### R4 — Reconcile independent evidence dimensions

Do not define one total lifecycle rank such as `updated < renewed < paused < canceled`. Reconcile these dimensions independently:

```text
contract identity
plan intent
financial health / provider coverage
termination
```

Termination is monotonic for one provider contract:

```text
NONE -> CANCEL_SCHEDULED -> PREPAID_TERM_ENDED
```

A causally valid plan update may still apply after cancellation was scheduled for the remaining prepaid term, but it must never clear the newer cancellation. A stale payment-pause observation must not overwrite newer successful renewal evidence. No non-terminal observation may resurrect a terminally ended provider contract.

### R5 — Moda recurring operations order merchant plan intent

API-003 serializes recurring merchant commands. Use the durable recurring-operation history to decide which `SUBSCRIPTION_CREATE` / `PLAN_SWITCH` target may become the current plan.

An `updated` receipt may project a plan switch only when it is compatible with the current provider contract and the causally current accepted switch intent/provider snapshot. A late/stale `updated` receipt from an earlier switch must not revert a later accepted merchant plan decision.

If the authenticated provider evidence cannot be correlated safely to a unique current plan intent, fail closed with bounded sync-attention evidence rather than guessing from receipt arrival.

### R6 — Financial health and provider coverage use authenticated provider evidence

Use provider financial evidence inside the authenticated contract snapshot (including documented billing-intent/transaction timestamps/identities where available) to determine causally current payment health/coverage.

`providerCoverageEndAt` may move earlier or later when causally newer evidence changes Woo `next_payment_date`; never compute it with `MAX()` over all observed dates.

If the payload does not provide sufficient evidence to decide between contradictory financial observations, fail closed; do not use `receivedAt` as a tiebreaker.

### R7 — Verified first paid activation opens the first exact-30-day Moda period

A trusted `SUBSCRIPTION_CREATE` activates only when the current Moda Subscription is local Free:

```text
Subscription.status = ACTIVE
current plan = FREE
providerSubscriptionId = NULL
billingPeriodId = NULL
```

Let `activationAt` be the verified provider activation/payment-completion time. Atomically project:

```text
Subscription.status = ACTIVE
Subscription.planId = already-materialised target paid plan
Subscription.providerSubscriptionId = new recurring contract
Subscription.providerCoverageEndAt = causally current provider financial boundary
Subscription.cancelAtPeriodEnd = false

BillingPeriod.periodStart = activationAt
BillingPeriod.periodEnd = activationAt + exact 30 days
Subscription.currentPeriodStart = same periodStart
Subscription.currentPeriodEnd = same periodEnd
full current-plan included allowance
committed/reserved/forfeited = 0
```

There is no detached former-period carry-forward. A new paid contract can be created only after any previous scheduled cancellation actually ended and the current Subscription is Free.

### R8 — Plan switch preserves the current Moda period/usage

For a causally current trusted `updated`/PLAN_SWITCH on the current provider contract:

```text
keep BillingPeriod id/start/end
keep committed/reserved/forfeited
update current plan
update currentAllowanceQuantity to target plan allowance
raise grantedQuantity high-water only when required by existing invariants
```

Provider monetary proration and `next_payment_date` are provider-owned. They may update `providerCoverageEndAt` only when the financial evidence is causally authoritative. They MUST NOT change `currentPeriodEnd`.

### R9 — Renewed updates financial coverage; it does not reset allowance

For a causally current verified `renewed` on the current provider contract:

```text
extend/re-establish providerCoverageEndAt from authoritative financial evidence
FROZEN -> ACTIVE when payment recovery is proven
keep current BillingPeriod/usage unchanged
do not grant a new included allowance merely because renewed arrived
```

After commit, the existing worker cycle may allow BACKGROUND-006 to reconcile a due entitlement boundary.

### R10 — Paused is the Woo payment-failure FROZEN state

For causally current verified `paused` on the current provider contract:

```text
Subscription.status = FROZEN
```

Preserve current paid plan/provider contract/BillingPeriod/counters and existing `providerCoverageEndAt`; do not invent future coverage and do not grant a new allowance. BACKGROUND-001 owns fallback to already-owned non-paid-included capacity.

A stale `paused` observation must not overwrite newer successful renewal evidence.

### R11 — Verified canceled schedules prepaid term end

For the current recurring contract, a trusted coherent `canceled` snapshot with signed `end_date` projects:

```text
Subscription.status = ACTIVE
paid plan remains current
providerSubscriptionId remains current contract
billingPeriodId/currentPeriod* remain current Moda allowance window
cancelAtPeriodEnd = true
providerCoverageEndAt = signed end_date
```

Confirm a matching `CANCEL` operation atomically where applicable. Do not return the Subscription to Free and do not recreate/reset lifetime-Free allowance.

If the signed `end_date <= now` when the receipt is processed, perform the terminal R12 transition immediately instead of creating a scheduled-cancel state in the past.

### R12 — prepaid_term_ended is terminal paid -> Free evidence

A coherent trusted `prepaid_term_ended` for the current provider contract may perform terminal transition even when the earlier `canceled` receipt was delayed/lost. Require provider evidence consistent with the prepaid term having ended within the accepted clock tolerance.

Atomically:

```text
close/truncate current paid BillingPeriod with CONTRACT_ENDED semantics
Subscription.status = ACTIVE
Subscription.planId = existing Free BillingPlan
Subscription.providerSubscriptionId = NULL
Subscription.providerCoverageEndAt = NULL
Subscription.billingPeriodId = NULL
Subscription.currentPeriodStart = NULL
Subscription.currentPeriodEnd = NULL
Subscription.cancelAtPeriodEnd = false
```

Preserve onboarding, lifetime-Free, purchased, promotional and historical state. Never recreate/reset lifetime-Free credits.

A later receipt from that historical contract cannot mutate the current Free state or a newer provider contract.

### R13 — Subscription monetary refund never mutates purchase-refund allowance

Treat subscription `refunded` only as recurring provider lifecycle/financial evidence when its authenticated snapshot establishes a relevant state. Never create or modify `RecoveryCreditRefund` top-up allowance state from subscription money.

### R14 — Authenticated but contradictory evidence is a bounded business conflict

A durable authenticated snapshot that cannot be reconciled safely is not retried forever as though PostgreSQL were unavailable. Record bounded safe sync-attention/error evidence, fail closed for new paid included entitlement where necessary, and mark the receipt processed when the contradiction is permanent.

Retryable infrastructure/transaction failures still leave the receipt retryable under the existing bounded mechanism.

### R15 — No provider network dependency / bounded logging

Use durable signed receipts + Moda state only. No Woo network calls occur during reconciliation. Use shared structured logging and never log credentials/full provider payloads.

## Work Items

- [ ] Advance the nested database gitlink to the accepted ARCH-027 schema and regenerate Prisma.
- [ ] Preserve bounded subscription-receipt claiming in the existing billing worker.
- [ ] Implement trusted Shop/current-vs-historical provider-contract correlation.
- [ ] Implement an evidence reducer that never uses receipt arrival time as provider causality.
- [ ] Reconcile plan intent from serialized recurring operations and compatible provider evidence.
- [ ] Reconcile financial health/`providerCoverageEndAt` from causally current authenticated provider evidence.
- [ ] Implement first paid activation with exact `activationAt + 30 days` Moda period.
- [ ] Implement same-period plan switch without moving `currentPeriodEnd`.
- [ ] Implement `renewed` as coverage/payment recovery without allowance reset.
- [ ] Implement causally current `paused -> FROZEN` without new allowance.
- [ ] Implement `canceled -> cancelAtPeriodEnd=true/providerCoverageEndAt=end_date` while keeping paid entitlement current.
- [ ] Implement terminal `prepaid_term_ended -> Free`, including when prior `canceled` delivery was missing.
- [ ] Ensure old-contract lifecycle cannot mutate Free or a newer current contract.
- [ ] Handle permanently contradictory authenticated evidence as bounded sync-attention rather than infinite retry.
- [ ] Preserve purchased/lifetime-Free/promotional/onboarding state.
- [ ] Add duplicate, delayed, concurrent and out-of-order reconciliation tests.

## Interfaces / Contracts

### Durable input

Owner: `ARCH-027-API-005` / database persistence from `ARCH-027-DATABASE-001`.

```text
WooCommerceBillingWebhookReceipt
    topic
    providerContractId?
    normalizedPayload (authenticated provider-shaped subscription wrapper)
    receivedAt (transport metadata only)
    processedAt?
    processingError?
```

### Merchant recurring intent

Owner: `ARCH-027-API-003`.

```text
WooCommerceBillingOperation
    SUBSCRIPTION_CREATE | PLAN_SWITCH | CANCEL
    serialized per Shop
    target MerchantPricingPlan / provider contract / operation state
```

### Durable projection

```text
Subscription.providerSubscriptionId
Subscription.providerCoverageEndAt
Subscription.status
Subscription.cancelAtPeriodEnd
Subscription.planId
Subscription.billingPeriodId
Subscription.currentPeriodStart/currentPeriodEnd
BillingPeriod / BillingPeriodEntitlementCounter
```

`providerCoverageEndAt` and `currentPeriodEnd` are intentionally different clocks.

## Dependencies

- `ARCH-027-API-005`
- `ARCH-027-BACKGROUND-001`

Both must be architect-accepted Complete before this task becomes Ready.

## Enables

- `ARCH-027-BACKGROUND-004`
- `ARCH-027-BACKGROUND-006`

The charge-acquisition path and time-driven entitlement reconciler may proceed independently after this task is accepted.

## Acceptance Criteria

- [ ] Woo receipt `receivedAt`, receipt ID, HTTP delivery order and worker claim order are never used as provider lifecycle causality.
- [ ] Historical provider-contract receipts cannot mutate a newer current contract.
- [ ] First paid activation opens exactly one Moda period ending `activationAt + 30 days`.
- [ ] Plan switch preserves BillingPeriod id/start/end and usage while applying the target allowance ceiling.
- [ ] Causally current provider financial evidence may change `providerCoverageEndAt` without changing `currentPeriodEnd`.
- [ ] `renewed` extends/re-establishes financial coverage and can recover FROZEN, but does not reset included allowance.
- [ ] A stale `paused` cannot regress newer successful renewal evidence.
- [ ] Verified `canceled` leaves the paid plan/current period active, sets `cancelAtPeriodEnd=true`, and sets provider coverage to signed `end_date`.
- [ ] A canceled snapshot already past `end_date` converges directly to terminal Free state.
- [ ] `prepaid_term_ended` can terminally end the current contract even when earlier canceled delivery is missing, when signed term evidence is coherent.
- [ ] Terminally ended old-contract events cannot resurrect or mutate the current Free/newer contract.
- [ ] Lifetime-Free allowance is never recreated/reset by cancellation/end transitions.
- [ ] Subscription `refunded` evidence never creates/modifies one-time purchase-refund allowance state.
- [ ] Permanently contradictory authenticated evidence fails closed and does not retry forever; retryable infrastructure failures remain retryable.
- [ ] All business projection + receipt completion transitions are atomic/idempotent under duplicate/concurrent delivery.
- [ ] No Woo provider network call occurs in reconciliation.
- [ ] No new worker deployment, Shared lifecycle contract or domain `_index.md` change is introduced.

## Validation

Required focused validation categories:

- [ ] unit tests for evidence reduction/field-specific merge;
- [ ] database-backed duplicate/concurrent receipt tests;
- [ ] first Free -> paid activation exact-30-day period test;
- [ ] updated same-period plan-switch test including provider `next_payment_date` movement with unchanged `currentPeriodEnd`;
- [ ] renewed-without-reset test;
- [ ] paused -> FROZEN then newer renewed -> ACTIVE test;
- [ ] renewed delivered before stale paused test;
- [ ] canceled -> paid scheduled-end test;
- [ ] canceled whose end_date is already past -> direct terminal Free test;
- [ ] prepaid_term_ended without previously processed canceled -> terminal Free test;
- [ ] late updated after canceled preserves cancellation while applying only causally valid plan dimension;
- [ ] old-contract lifecycle after newer contract/current Free is non-mutating;
- [ ] contradictory-evidence bounded-attention/no-infinite-retry test;
- [ ] receipt exact-duplicate/business-idempotency tests;
- [ ] targeted lint/typecheck/build required by repository/task instructions;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization and pushed task-branch evidence.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and STOP. Do not begin BACKGROUND-004 or BACKGROUND-006.

## Implementation Notes

Prefer one deterministic reconciliation reducer over topic handlers that independently overwrite shared Subscription fields. The reducer may retain topic-specific parsing, but the final projection must merge contract identity, plan intent, financial evidence and termination deliberately.

Do not query Woo during receipt processing to manufacture ordering. If SYSTEM-TEST-002 proves the signed provider snapshot is insufficient for a required causal comparison, return that provider capability gap to `moda_architect`.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- The real Woo sandbox will be used by SYSTEM-TEST-002 to certify that signed snapshots contain sufficient financial/order evidence for the reducer.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation.

### Follow-up

None.
