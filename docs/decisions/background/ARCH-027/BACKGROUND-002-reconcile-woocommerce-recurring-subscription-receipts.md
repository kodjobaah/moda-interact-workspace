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
created: 2026-10-03
updated: 2026-10-04
---

# Reconcile WooCommerce recurring subscription webhook receipts

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Consume authenticated durable Woo subscription webhook receipts and project the provider lifecycle onto the Shop's one Moda Subscription.

Core rule:

```text
provider owns money
Moda owns allowance
```

```text
activated -> initial paid activation OR replacement subscription after cancellation
updated -> active contract plan switch, same period/usage
renewed -> next uninterrupted paid period
paused -> FROZEN, preserve current period, no new paid allowance
canceled -> FROZEN immediately, preserve current period/usage, cancelAtPeriodEnd=true
prepaid_term_ended -> Free only if the canceled contract is still current
```

Replacement activation before the preserved current period ends resumes that period/usage. Replacement activation at or after its end creates a fresh period/full target-plan allowance.

## Context

ARCH-027 has already fixed:

- API-003: recurring create/switch/cancel intent is persisted before provider writes;
- API-005: Woo webhooks are HMAC-verified and durably stored without business mutation;
- BACKGROUND-001: paid included recovery accounting is Woo-safe and uses `currentAllowanceQuantity ?? grantedQuantity`;
- DATABASE-001: one Subscription per Shop plus durable Woo operations/receipts and current allowance.

### Source finding — freeze the operational paid BillingPlan before Woo checkout

The existing Shopify `BillingPlanResolutionService` copies durable catalogue feature/allowance state into an operational `BillingPlan`.

`WooCommerceBillingOperation` snapshots:

```text
merchantPricingPlanId
quotedAmountMinor
quotedCurrency
quotedBillingPeriod
```

but it does not snapshot every feature/configuration/included-allowance field that becomes part of the operational plan.

If paid BillingPlan materialisation waits until the webhook arrives, an Admin edit between:

```text
merchant initiates checkout
merchant confirms checkout
```

could change the operational entitlement/feature projection after plan selection.

Therefore the companion API-003 correction included with this definition requires API-003 to reuse/generalise API-001's bounded operational-plan resolver before provider I/O:

```text
MerchantPricingPlan
    -> resolve/reuse/materialise BillingPlan
    -> persist Woo command intent
    -> commit
    -> call Woo
```

This is **not** entitlement activation. API-003 still does not change `Subscription.planId`, BillingPeriod or counters before provider confirmation.

BACKGROUND-002 therefore resolves an already-materialised paid plan; it does not materialise one.

### Woo provider lifecycle facts

Woo's current SaaS Billing documentation states:

- `activated` means checkout/payment succeeded;
- `updated` means a plan switch was confirmed and provider proration may move `next_payment_date`;
- `renewed` is emitted when a recurring renewal payment succeeds;
- `paused` is emitted when a renewal is due but payment could not be processed; Woo retries and later emits `renewed` on success or cancellation/expiry lifecycle evidence;
- canceled subscriptions retain prepaid access until the provider term end;
- the canceled contract snapshot includes the prepaid end date and Woo later emits `prepaid_term_ended`;
- subscription webhook bodies include `next_payment_date`, `end_date`, billing intents and transactions.

Provider reference verified 4 October 2026:

`https://developer.woocommerce.com/docs/woo-marketplace/billing-api-saas`

ARCH-027 does not run an unconditional local 30-day Woo rollover. Cancellation preserves the current period; verified replacement activation/renewal plus the preserved period boundary determines resume versus fresh allowance.

## Scope

Modify only `moda-interact-background` implementation/tests needed for:

1. bounded claiming of unprocessed Woo **subscription-wrapper** receipts;
2. trusted external-contract correlation;
3. recurring subscription lifecycle projection;
4. receipt processed/error bookkeeping;
5. integration into the existing leased billing worker cycle.

Expected implementation areas are conceptually:

```text
src/services/woocommerce-billing/
  subscription-receipt-reconciliation.service.ts
  subscription-operation-resolution.ts
  subscription-transition.service.ts

src/entrypoints/billing.ts
```

Exact repository-local filenames may differ where the accepted refactor provides a clearer bounded owner.

Update the nested `database/` gitlink to the newest compatible architect-accepted database main commit and regenerate Prisma before source changes.

Reuse:

- the existing billing worker deployment;
- the existing leased billing scheduler;
- Prisma transactions;
- existing Shop/Subscription lock conventions;
- existing paid-period close/release semantics;
- `recoveryCapacityResumeService`;
- Shared structured logging.

Do not add another worker deployment.

## Out of Scope

- Woo `charge` receipt processing.
- Top-up activation/refund settlement.
- Woo provider GET/POST/DELETE calls.
- Woo credentials.
- Scheduled local Woo BillingPeriod rollover after the first period.
- Using `next_payment_date` as a Moda allowance-reset boundary.
- Shopify Partner API reconciliation changes.
- Shopify same-cycle plan-change behavior.
- API webhook validation.
- API command initiation.
- Admin/Woo UI.
- Gateway changes.
- Prisma schema/migration edits other than advancing the accepted nested database gitlink.
- A Shared lifecycle-event contract.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Reuse the existing billing worker

Keep bounded receipt claiming, SKIP LOCKED concurrency and atomic business/receipt transactions.

### R2 — Trusted tenant/contract correlation

Resolve Shop only from Woo operations/current Subscription provider contract and keep deterministic lock order.

### R3 — Initial Free -> paid activation

Trusted `SUBSCRIPTION_CREATE` from local Free creates one paid period/full target-plan allowance, makes the new provider contract current and preserves lifetime-Free/purchased/promotional state.

### R4 — Canceled/FROZEN re-subscribe activation

A trusted `SUBSCRIPTION_CREATE` may also target:

```text
status = FROZEN
cancelAtPeriodEnd = true
current paid plan/BillingPeriod retained
```

Let `activationAt` be verified provider activation/payment completion and `oldPeriodEnd` the preserved BillingPeriod end.

If `activationAt < oldPeriodEnd`:

```text
status -> ACTIVE
providerSubscriptionId -> new contract
cancelAtPeriodEnd -> false
same BillingPeriod/start/end
same committed/reserved/forfeited
currentAllowanceQuantity -> target plan allowance
```

Raise granted high-water only if required. Same-plan 10 granted / 4 committed resumes with 6 remaining.

If `activationAt >= oldPeriodEnd`, close the old period under existing invariants and create a fresh period/full target-plan allowance with zero usage.

### R5 — Replacement contract invalidates stale old-contract lifecycle

After the new contract becomes current, later lifecycle receipts for the replaced old contract are historical no-ops for Subscription/allowance state.

### R6 — Plan switch preserves current period usage

Trusted `updated`/PLAN_SWITCH keeps the same BillingPeriod and committed/reserved/forfeited usage, updates plan/current allowance and high-water only when needed. Provider monetary proration is provider-owned.

### R7 — Renewed opens the next uninterrupted paid period

For verified `renewed` on the current contract, close the old period and open exactly one new period/full current-plan allowance with zero usage. This is the normal new-period signal for uninterrupted Woo service.

### R8 — Paused freezes without granting a new period

Verified `paused` on the current contract sets `status=FROZEN`, `cancelAtPeriodEnd=false`, preserves plan/period/counters, creates no new allowance, and relies on BACKGROUND-001 fallback.

### R9 — Verified canceled freezes immediately

Verified `canceled` on the current contract sets:

```text
status = FROZEN
cancelAtPeriodEnd = true
```

Preserve current plan, provider contract, BillingPeriod/start/end and counters. Do not return to Free yet.

### R10 — Cancellation never mutates fallback balances

Do not mutate purchased, lifetime-Free or promotion records when freezing/canceling.

### R11 — prepaid_term_ended returns to Free only for the still-current canceled contract

Require current provider contract match, FROZEN + cancelAtPeriodEnd and reached provider terminal evidence. Close the paid period and return the same Subscription to existing Free.

If the merchant already re-subscribed and the current provider contract is different, the old contract's terminal receipt is a historical no-op.

### R12 — Subscription monetary refund does not touch purchase-refund allowance

Treat subscription `refunded` only through provider subscription lifecycle evidence. Never create/modify `RecoveryCreditRefund` top-up allowance state from subscription money.

### R13 — Provider dates/amounts are evidence, not allowance arithmetic

Use verified activation time only to decide before/after preserved periodEnd. Never derive credit quantity or refund money from provider amounts.

### R14 — No provider network dependency / bounded logging

Use durable signed receipts + Moda state only and bounded structured logs.

## Work Items

- [ ] Reuse bounded subscription receipt claiming/locking.
- [ ] Implement initial Free -> paid activation.
- [ ] Implement canceled/FROZEN replacement-contract activation.
- [ ] Same-period re-subscribe preserves period and usage.
- [ ] After-period re-subscribe creates fresh full allowance.
- [ ] Replace provider contract atomically and ignore stale old-contract lifecycle.
- [ ] Preserve same-period plan-switch usage semantics.
- [ ] Renewed opens the next uninterrupted paid period.
- [ ] Paused freezes with no new allowance.
- [ ] Canceled freezes immediately and preserves current period/counters.
- [ ] prepaid_term_ended -> Free only for still-current canceled contract.
- [ ] Preserve purchased/lifetime-Free/promotional state.
- [ ] Add before/after-period resubscribe tests.

## Interfaces / Contracts

### Canceled state

```text
FROZEN + cancelAtPeriodEnd=true + preserved current BillingPeriod
```

### Same-period re-subscribe

```text
new SUBSCRIPTION_CREATE contract
activationAt < periodEnd
-> ACTIVE + new provider contract + same period/usage
```

### After-period re-subscribe

```text
activationAt >= periodEnd
-> close old + new period + full target allowance
```

### FROZEN fallback

```text
paid included unavailable
purchased/lifetime-Free usable
promotion follows existing eligibility
```

### Monetary boundary

Provider owns money. This task mutates Subscription/allowance only.

## Dependencies

- `ARCH-027-API-005`
- `ARCH-027-BACKGROUND-001`

Both must be architect-accepted Complete before this task becomes Ready.

API-005 supplies authenticated durable receipts.

BACKGROUND-001 guarantees that activated Woo paid merchants already have safe local included-usage accounting and cannot enter the Shopify App Event publisher.

Through API-005's dependency chain, API-003 recurring operations exist for target-plan correlation.

## Enables

- `ARCH-027-BACKGROUND-004`

## Acceptance Criteria

- [ ] Initial Free -> paid creates one paid period/full allowance.
- [ ] Verified cancellation before period end sets FROZEN and preserves current period/counter.
- [ ] Purchased/lifetime-Free remain usable while canceled/FROZEN.
- [ ] Canceled/FROZEN merchant may create a replacement provider subscription.
- [ ] Replacement activation before periodEnd reuses same period/usage.
- [ ] 10 granted / 4 committed resumes with 6 on same-plan resubscribe before period end.
- [ ] Different-plan same-period resubscribe preserves usage/current-allowance semantics.
- [ ] Replacement activation at/after periodEnd creates fresh full allowance.
- [ ] Old-contract late events cannot mutate the replacement current contract.
- [ ] Renewed opens next uninterrupted paid period.
- [ ] Paused freezes with no new period.
- [ ] prepaid_term_ended -> Free only for current canceled contract.
- [ ] Fallback balances/history survive cancel/resubscribe.
- [ ] Provider money is not calculated by Moda.
- [ ] No provider HTTP call occurs.
- [ ] `docs/architecture/_index.md` unchanged.

## Validation

- [ ] build/typecheck/lint/Prisma;
- [ ] Free -> paid activation;
- [ ] active -> canceled/FROZEN preserves period/counter;
- [ ] purchased/lifetime-Free fallback while canceled/FROZEN;
- [ ] same-plan re-subscribe before periodEnd 10/4 -> 6;
- [ ] different-plan same-period resubscribe preserves usage;
- [ ] re-subscribe at/after periodEnd fresh full allowance;
- [ ] old canceled contract terminal event after replacement is no-op;
- [ ] current canceled contract prepaid_term_ended -> Free;
- [ ] paused -> FROZEN no-new-period;
- [ ] renewed -> next full-allowance period;
- [ ] subscription refund does not touch top-up refund ledger;
- [ ] no provider network/credentials;
- [ ] `git diff --check` + worktree/submodule/push evidence.

## Stop Condition

After all Work Items, Acceptance Criteria and Validation are complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin local Woo period rollover or charge receipt reconciliation.

## Implementation Notes

Prefer a bounded Woo-specific collaborator around the refactored billing worker.

Do not fabricate a Shopify PartnerSubscription and do not run a local 30-day Woo timer.

For Woo v1:

```text
payment succeeded -> new included-credit period
payment failed    -> FROZEN, no new included period
```

The catalogue may still use `EVERY_30_DAYS` as the existing commercial price-unit abstraction mapped to Woo `month`; durable Woo period boundaries come from signed provider lifecycle evidence.

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

- API-003 is corrected/implemented to resolve/reuse/materialise the selected paid operational BillingPlan before provider I/O while leaving Subscription/BillingPeriod untouched.
- Woo paid local recovery entitlement uses an independent 30-day cadence.
- Woo refund approval also causes provider cancellation as documented.
- API-005 already authenticated the webhook raw body; Background consumes durable receipts only.

### Unresolved Issues

- Woo does not expose a separate signed webhook sequence/event ID. ARCH-027 uses durable receipt arrival ordering plus transition guards; arbitrary provider-causal reordering remains a sandbox/system-test concern.
- One-time charge receipt reconciliation is deliberately separate.

### Architectural Concerns

None beyond the recorded provider event-ordering limitation.

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
