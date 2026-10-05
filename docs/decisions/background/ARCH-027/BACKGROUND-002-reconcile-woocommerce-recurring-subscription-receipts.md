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

Consume authenticated durable Woo subscription webhook receipts and project the provider lifecycle onto the Shop's one Moda `Subscription`.

Core rule:

```text
provider owns money
Moda owns allowance
```

```text
activated
    -> current Subscription must be local Free
    -> ordinary Free -> paid activation
    -> prior paid usage may carry forward when an unexpired former paid period exists

updated
    -> active contract plan switch, same current period/usage

renewed
    -> next uninterrupted paid period

paused
    -> paid Subscription FROZEN, preserve current period, no new paid allowance

canceled
    -> current Subscription immediately returns to existing Free
    -> current paid period is detached/preserved as the resumable allowance window

prepaid_term_ended
    -> old-contract terminal evidence only after cancellation;
       current Subscription already remains Free unless a newer contract is current
```

There is no special canceled/FROZEN re-subscribe state. A later paid purchase is the existing Free -> paid API-003 path.

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

ARCH-027 does not run an unconditional local 30-day Woo rollover. Verified cancellation returns the current Subscription to Free but preserves the former paid period as detached allowance history. A later ordinary Free -> paid activation uses that former period only to decide carry-forward versus fresh allowance.

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

Resolve Shop only from Woo operations/current or historical trusted provider-contract evidence and keep deterministic lock order.

### R3 — Free -> paid activation is the only subscription-create projection

A trusted `SUBSCRIPTION_CREATE` activates only when the current Moda Subscription is local Free:

```text
Subscription.status = ACTIVE
current plan = FREE
providerSubscriptionId = NULL
billingPeriodId = NULL
```

This includes first-ever paid activation and a later paid purchase after an earlier verified cancellation.

Let `activationAt` be the verified new provider activation/payment-completion time.

Before creating a fresh paid period, inspect the Shop's one Subscription for a **single detached former paid BillingPeriod**:

```text
same subscriptionId
planKindSnapshot = PAID_METERED
status = OPEN
not referenced by Subscription.billingPeriodId
```

#### R3A — Carry forward prior-period usage when activation is before its end

If exactly one such period exists and:

```text
activationAt < formerPeriod.periodEnd
```

reattach/reuse that paid allowance accounting:

```text
Subscription.status = ACTIVE
Subscription.planId = target paid plan
Subscription.providerSubscriptionId = new contract
Subscription.billingPeriodId = formerPeriod.id
Subscription.currentPeriodStart = formerPeriod.periodStart
Subscription.currentPeriodEnd = formerPeriod.periodEnd
Subscription.cancelAtPeriodEnd = false

committed/reserved/forfeited = unchanged
currentAllowanceQuantity = target plan allowance
grantedQuantity high-water raised only when required
```

Same-plan example:

```text
10 granted
4 committed
verified cancellation -> Free
new paid activation before former periodEnd
    -> 6 included credits remain
```

If target plan differs, use the accepted same-period plan-change allowance rule; do not reset usage.

#### R3B — Fresh period when prior paid window has ended

If no unexpired detached former paid period exists, close any expired detached period under existing close invariants and create the normal new paid BillingPeriod/full target-plan allowance with zero usage.

This is still the ordinary Free -> paid activation path; allowance carry-forward is a Background projection detail, not a new command type.

### R4 — At most one detached resumable paid period

Under the Shop/Subscription lock, fail closed if more than one detached OPEN paid BillingPeriod could be considered resumable.

The current Free Subscription must never point at that row through `billingPeriodId`.

### R5 — Plan switch preserves current paid period usage

Trusted `updated`/PLAN_SWITCH on the current provider contract keeps the same BillingPeriod and committed/reserved/forfeited usage, updates plan/current allowance and high-water only when needed. Provider monetary proration is provider-owned.

### R6 — Renewed opens the next uninterrupted paid period

For verified `renewed` on the current provider contract, close the current paid period and open exactly one new period/full current-plan allowance with zero usage.

### R7 — Paused is the Woo FROZEN state

Verified `paused` on the current provider contract sets:

```text
Subscription.status = FROZEN
cancelAtPeriodEnd = false
```

Preserve current paid plan/provider contract/BillingPeriod/counters, create no new allowance, and rely on BACKGROUND-001 fallback.

### R8 — Verified cancellation immediately returns the current Subscription to Free

For verified:

```text
topic = canceled
current provider contract matches
```

resolve the existing Free BillingPlan and atomically project:

```text
Subscription.status = ACTIVE
Subscription.planId = Free
Subscription.providerSubscriptionId = NULL
Subscription.billingPeriodId = NULL
Subscription.currentPeriodStart = NULL
Subscription.currentPeriodEnd = NULL
Subscription.cancelAtPeriodEnd = false
```

Preserve onboarding and all lifetime-Free/purchased/promotional/history state.

Do **not** close, forfeit or delete the former current paid BillingPeriod solely because of cancellation. Detach it as the single resumable paid allowance window described in R3/R4.

Confirm a matching CANCEL operation atomically where applicable.

### R9 — Cancellation never re-grants Free allowance

Returning to Free uses the already-existing Free plan/lifetime counter.

Never recreate or reset lifetime Free credits on cancellation.

### R10 — Old canceled-contract lifecycle is historical after Free or a later subscription

Once cancellation clears `Subscription.providerSubscriptionId`, later lifecycle receipts from that old contract MUST NOT change the current Free Subscription.

If a later Free -> paid activation installs a new provider contract, the old contract remains historical and cannot pause/renew/cancel/end the new current subscription.

### R11 — prepaid_term_ended may close only the detached former paid period

A delayed `prepaid_term_ended` for the canceled old contract never performs a Free transition because cancellation already did so.

When the current Subscription is still Free/no provider contract and there is exactly one detached former paid period whose allowance window has reached its end, the receipt may close that detached period through the existing close invariants.

If a newer recurring provider contract is current, the old terminal receipt is a business no-op.

### R12 — Subscription monetary refund does not touch purchase-refund allowance

Treat subscription `refunded` only through provider subscription lifecycle evidence. Never create/modify `RecoveryCreditRefund` top-up allowance state from subscription money.

### R13 — Provider dates/amounts are evidence, not allowance arithmetic

Use verified activation time to decide whether prior-period usage carries forward. Never derive credit quantity or refund money from provider amounts.

### R14 — No provider network dependency / bounded logging

Use durable signed receipts + Moda state only and bounded structured logs.

## Work Items

- [ ] Reuse bounded subscription receipt claiming/locking.
- [ ] Implement ordinary Free -> paid activation for both first and post-cancellation paid purchases.
- [ ] On verified cancellation, return current Subscription immediately to existing Free and clear current provider/period pointers.
- [ ] Preserve exactly one former paid OPEN BillingPeriod as detached resumable allowance history.
- [ ] Free -> paid activation before former periodEnd reattaches/carries prior usage rather than granting fresh usage.
- [ ] Free -> paid activation at/after former periodEnd closes old history and creates fresh full allowance.
- [ ] Preserve different-plan same-period current-allowance semantics on carried-forward activation.
- [ ] Renewed opens the next uninterrupted paid period.
- [ ] Paused remains FROZEN with no new allowance.
- [ ] Old canceled-contract lifecycle cannot mutate current Free or a later new contract.
- [ ] prepaid_term_ended may only close detached old allowance history when still applicable.
- [ ] Preserve purchased/lifetime-Free/promotional/onboarding state.
- [ ] Add cancel-to-Free and before/after-period Free->paid tests.

## Interfaces / Contracts

### Verified Woo cancellation

```text
current paid Subscription
    -> ACTIVE Free
    -> providerSubscriptionId = NULL
    -> billingPeriodId/currentPeriod* = NULL

former paid BillingPeriod
    -> remains durable/detached
    -> preserves usage for possible carry-forward
```

### Later paid purchase

Always uses the ordinary API-003 Free -> paid `SUBSCRIPTION_CREATE` flow.

```text
activationAt < detached former periodEnd
    -> reuse/carry prior usage

otherwise
    -> fresh paid period/full target allowance
```

### FROZEN

Reserved for Woo provider payment-pause/recovery state, not verified cancellation.

### Monetary boundary

Provider owns money. This task mutates Subscription/allowance projection only.

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

- [ ] Initial local Free -> paid creates/attaches paid allowance as specified.
- [ ] Verified Woo cancellation immediately makes the current Subscription ACTIVE Free with no recurring provider/current BillingPeriod pointers.
- [ ] Cancellation does not recreate/reset lifetime Free allowance.
- [ ] Former paid period/usage is preserved as exactly one detached resumable window.
- [ ] Purchased/lifetime-Free remain usable through normal Free policy after cancellation.
- [ ] There is no canceled/FROZEN re-subscribe state or command.
- [ ] A later paid purchase uses the ordinary Free -> paid SUBSCRIPTION_CREATE path.
- [ ] Activation before former periodEnd carries prior usage; 10 granted / 4 committed gives 6 remaining on same plan.
- [ ] Different target plan before former periodEnd preserves usage and applies target current allowance.
- [ ] Activation at/after former periodEnd creates a fresh full target-plan allowance.
- [ ] Old-contract delayed lifecycle cannot mutate current Free or a later current contract.
- [ ] Paused still produces FROZEN/no new allowance.
- [ ] Renewed on current active contract opens the next uninterrupted paid period.
- [ ] prepaid_term_ended never performs a second Free transition.
- [ ] Provider money is not calculated by Moda.
- [ ] No provider HTTP call occurs.
- [ ] `docs/architecture/_index.md` unchanged.

## Validation

- [ ] build/typecheck/lint/Prisma;
- [ ] first Free -> paid activation;
- [ ] active paid -> verified canceled -> ACTIVE Free/current pointers null;
- [ ] cancellation lifetime-Free anti-regrant test;
- [ ] detached former paid period uniqueness test;
- [ ] same-plan later Free -> paid before former periodEnd 10/4 -> 6;
- [ ] different-plan later Free -> paid before former periodEnd preserves usage;
- [ ] later Free -> paid at/after former periodEnd fresh full allowance;
- [ ] old canceled contract terminal event while current Free is no-op except safe detached-period closure;
- [ ] old canceled contract terminal event after a newer paid activation is no-op;
- [ ] paused -> FROZEN no-new-period;
- [ ] renewed current contract -> next full-allowance period;
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
- Verified cancellation returns current Moda state to Free immediately; prior paid usage carry-forward is handled only when a later ordinary Free -> paid activation occurs before the former paid period end.
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
