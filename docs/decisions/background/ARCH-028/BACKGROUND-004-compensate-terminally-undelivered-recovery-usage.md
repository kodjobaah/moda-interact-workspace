---
id: ARCH-028-BACKGROUND-004
architecture_id: ARCH-028
title: Compensate terminally undelivered recovery usage
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
  - ARCH-028-DATABASE-002
  - ARCH-027-BACKGROUND-001
  - ARCH-027-BACKGROUND-005
enables: []
created: 2026-10-05
updated: 2026-10-05
---

# Compensate terminally undelivered recovery usage

## Objective

Idempotently release or compensate the exact recovery allowance associated with a terminal recipient-undeliverable WhatsApp recovery, without creating provider monetary refunds or cross-period make-good credits.

ARCH-028 v1 uses **Option A**:

```text
source still spendable -> restore exact source
source expired/closed/terminal -> historical accounting correction only
```

## Context

BACKGROUND-002 marks the linked outreach attempt FAILED and suppresses its follow-up. DATABASE-002 supplies one durable compensation link/disposition.

ARCH-027 supplies provider-correct recovery UsageEvents and the final purchased-credit/refund state model.

Compensation authority is the exact `UsageReservation` source linkage, not the Shop's current Subscription/BillingPeriod.

This matters when a Woo merchant has already canceled to Free: the historical paid reservation/counter remains the compensation target even though current `Subscription.billingPeriodId` is null.

## Scope

Modify only Background recovery-accounting code/tests required to:

- release an eligible still-RESERVED reservation;
- compensate an eligible already-COMMITTED reservation exactly once;
- create the linked negative UsageEvent;
- restore/correct lifetime-Free, paid-included, promotional or purchased source accounting;
- persist compensation disposition;
- preserve ARCH-027 purchase-refund holds;
- return a bounded outcome for later reachability/merchant-notification work.

## Out of Scope

- Provider monetary refunds.
- Creating/reopening `RecoveryCreditRefund` because delivery failed.
- Cross-period make-good credits.
- Recipient suppression writes.
- Merchant support notification.
- Synchronous HTTP send rejection (later task).
- Missing-phone handling (later task).
- Changing CheckoutRecovery enum.

## Requirements

### R1 — Exact eligibility under lock

In one Serializable transaction, resolve the recovery attempt/message/reservation and revalidate:

```text
ConversationMessage.status = FAILED
providerFailureCode = 131026
RecoveryOutreachAttempt.status = FAILED
reservation belongs to same Shop/recovery source
```

If the message is now DELIVERED/READ, no compensation occurs.

### R2 — RESERVED means release, not compensation UsageEvent

If reservation is still `RESERVED`, call/reuse the exact source owner's release semantics so reserved quantity returns to the original source.

No negative UsageEvent/compensation link is created because no positive committed UsageEvent exists.

Return bounded outcome `RELEASED_RESERVED` for later notification/reachability work.

### R3 — COMMITTED retains original history

Do not rewrite `UsageReservation.status` or original `committedUsageEventId`.

Create exactly one negative correction UsageEvent:

```text
metric = RECOVERY_CONVERSATION
quantity = -reservation.quantity
correctionOfUsageEventId = original committedUsageEventId
idempotencyKey = "whatsapp-delivery-compensation:" + reservation.id
sourceType = "WHATSAPP_DELIVERY_COMPENSATION"
sourceId = reservation.id
provider = original UsageEvent.provider
billingPeriodId = original UsageEvent.billingPeriodId
```

### R4 — Provider reporting follows the original usage evidence

For original Woo/non-reportable usage:

```text
shopifyReportState = NOT_APPLICABLE
```

For a Shopify paid-included original that is externally reportable, create a reportable negative correction using the original Shopify event handle and a deterministic correction idempotency key through the accepted Shopify publisher path.

Do not turn Free/promotional/purchased local corrections into Shopify monetary refund events.

### R5 — Lifetime-Free source is always spendable restoration

For a committed lifetime-Free reservation:

```text
ShopEntitlementCounter.committedQuantity -= quantity
```

with existing counter invariants/CAS.

Disposition:

```text
RESTORED_SPENDABLE
```

### R6 — Paid-included open source restores spendable allowance

If the exact linked BillingPeriod is still OPEN and its allowance source remains current/spendable under accepted billing policy:

```text
BillingPeriodEntitlementCounter.committedQuantity -= quantity
```

Disposition `RESTORED_SPENDABLE`.

This includes a detached former Woo paid period still within its resumable allowance window after the current Subscription has moved to Free.

### R7 — Paid-included closed/expired source is historical-only

If the linked paid BillingPeriod is CLOSED/expired/otherwise no longer spendable:

```text
committedQuantity -= quantity
forfeitedQuantity += quantity
```

so close/high-water accounting remains coherent but no new spendable allowance is created.

Disposition `HISTORICAL_ONLY`.

Do not credit the current Free/new paid period.

### R8 — Promotional source restores only while the promotion is usable

Always decrement the exact grant's `committedQuantity` by the compensated quantity.

If the campaign/selection is still eligible under the existing promotion rules, clear/update exhaustion evidence as required and use `RESTORED_SPENDABLE`.

If campaign is CLOSED/expired/not usable, use `HISTORICAL_ONLY`; do not create another promotion/make-good credit.

### R9 — Purchased ACTIVE/COMPLETED lot without completed refund restores the lot

For the exact purchased lot when it has not been monetarily refunded and is not held by a live refund:

```text
counter.committedQuantity -= quantity
purchase.currentAmount += quantity
if purchase.status = COMPLETED -> ACTIVE
```

Preserve `creditsGranted`/provider acquisition evidence.

Disposition `RESTORED_SPENDABLE`.

### R10 — Purchased lot held by a live refund stays unavailable

If the exact purchase is `WITHDRAWN` with one live ARCH-027 refund:

```text
counter.committedQuantity -= quantity
purchase.currentAmount += quantity
```

Keep purchase `WITHDRAWN`.

If refund is still `REQUESTED`, leave existing refunding hold unchanged; BACKGROUND-005 will absorb the restored unused quantity when it freezes final allowance after reservations settle.

If refund is already `PROVIDER_ACTION_REQUIRED`, atomically:

```text
refund.finalCreditQuantity += quantity
counter.refundingQuantity += quantity
```

so the restored allowance remains held.

Disposition `HELD_FOR_REFUND`.

Never create a second refund attempt.

### R11 — Purchased REFUNDED source is historical-only

If provider monetary refund already completed and purchase is `REFUNDED`, do not reopen the lot or provider refund.

Correct aggregate history without creating availability:

```text
counter.committedQuantity -= quantity
counter.grantedQuantity -= quantity
purchase remains REFUNDED/currentAmount=0
```

Disposition `HISTORICAL_ONLY`.

This preserves aggregate availability while acknowledging that the undelivered recovery did not ultimately consume a spendable credit.

### R12 — Incoherent purchased/refund states fail closed

Unexpected combinations (for example WITHDRAWN without its unique live refund, REFUNDED with spendable currentAmount, provider-refunded state inconsistent with counters) must not be guessed. Leave compensation unset and surface bounded attention/error for operator review.

### R13 — Compensation linkage is atomic/idempotent

Source-counter/lot/refund adjustment, negative UsageEvent creation and:

```text
compensationUsageEventId
compensationReason = WHATSAPP_RECIPIENT_UNDELIVERABLE
compensationDisposition
compensatedAt
```

commit atomically.

Duplicate/replayed provider failure returns the persisted compensation outcome and never changes counters twice.

### R14 — Late DELIVERED/READ never claws back compensation

If delivery/read wins before the transaction, no compensation.

If compensation committed first and provider later reports DELIVERED/READ, keep the compensation. Later reachability work may clear suppression, but no positive re-charge/recommit occurs.

### R15 — No provider-money coupling

Do not inspect/calculate provider refund amount, tax or proration and do not call Shopify/Woo financial APIs.

## Work Items

- [ ] Add one compensation orchestrator using existing source owners/helpers rather than duplicate accounting.
- [ ] Add locked FAILED/131026 eligibility and duplicate replay.
- [ ] Add RESERVED release path.
- [ ] Add negative UsageEvent correction/provider-reporting lineage.
- [ ] Add lifetime-Free restoration.
- [ ] Add open vs closed paid-included Option-A behavior.
- [ ] Add active vs expired promotional Option-A behavior.
- [ ] Add purchased ACTIVE/COMPLETED restoration.
- [ ] Add purchased live-refund held restoration.
- [ ] Add purchased REFUNDED historical-only correction.
- [ ] Add late DELIVERED/READ race tests.
- [ ] Add cross-provider usage-event provider/reporting tests.

## Dependencies

- `ARCH-028-BACKGROUND-002`
- `ARCH-028-DATABASE-002`
- `ARCH-027-BACKGROUND-001`
- `ARCH-027-BACKGROUND-005`

## Enables

None yet. Later reachability/merchant-notification tasks consume its bounded durable outcome.

## Acceptance Criteria

- [ ] Exact source reservation is the accounting authority; current Subscription is never substituted.
- [ ] RESERVED path releases only.
- [ ] COMMITTED path creates one exact negative correction.
- [ ] Correction UsageEvent provider/reporting matches original provider semantics.
- [ ] Open paid period restores spendable allowance; closed period is historical-only with forfeited increase.
- [ ] Expired promotion produces no make-good credit.
- [ ] Lifetime-Free restore is spendable.
- [ ] Purchased non-refunded lot restores exact lot.
- [ ] Purchased live-refund lot keeps restored quantity held.
- [ ] Purchased REFUNDED lot remains closed and produces historical-only aggregate correction.
- [ ] No provider monetary refund state is created/reopened.
- [ ] Duplicate compensation cannot change allowance twice.
- [ ] Late delivery after compensation does not claw it back.
- [ ] `docs/architecture/_index.md` unchanged.

## Validation

Required focused unit + PostgreSQL integration for every source/disposition/race, provider-reporting correction, refund-held/REFUNDED purchase states, full Background tests/build and `git diff --check`.

## Stop Condition

Finish report -> review -> return to `moda_architect` -> STOP. Do not begin reachability/notification tasks.

## Completion Report

### Status

Not Started

## Architect Review

### Review Status

Pending
