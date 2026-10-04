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

Consume authenticated durable Woo **subscription** webhook receipts and project the recurring provider lifecycle onto the Shop's one Moda `Subscription`.

Woo paid `BillingPeriod` is provider-renewal driven:

```text
activated
    -> Free -> paid
    -> open first provider-backed BillingPeriod
       start = verified payment completion
       end   = signed next_payment_date

updated
    -> same BillingPeriod / same usage
    -> plan/current allowance changes
    -> period end follows signed updated next_payment_date

renewed
    -> successful provider renewal
    -> close prior period
    -> open exactly one new provider-backed BillingPeriod
    -> grant current plan included allowance
    -> unfreeze when needed

paused
    -> FROZEN
    -> NO successor BillingPeriod
    -> paid included unavailable
    -> fallback capacity remains usable through BACKGROUND-001

canceled
    -> cancelAtPeriodEnd = true
    -> preserve prepaid access through signed end_date

prepaid_term_ended
    -> require signed end_date to have been reached
    -> close paid period
    -> same Subscription -> existing Free
```

This task does not process charge receipts, call Woo, settle top-ups/refunds or create another Subscription.

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

ARCH-027 therefore no longer runs an independent 30-day Woo rollover. `EVERY_30_DAYS` remains the catalogue price-unit compatibility value mapped by API-003 to Woo `month`; actual Woo entitlement-period boundaries come from verified provider lifecycle evidence.

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

### R1 — Existing leased billing worker

Reuse the existing billing reconciliation cycle. No new worker/queue/cron.

### R2 — Bounded receipt scan

Keep the accepted 50-per-cycle subscription-wrapper scan, `(receivedAt,id)` ordering and bounded retry behavior.

### R3 — SKIP LOCKED claim / one transaction per receipt

Reuse `FOR UPDATE SKIP LOCKED`; business transition and `processedAt` commit atomically.

### R4 — Bounded reconciliation errors

Readiness errors may retry. Integrity/tenant/provider-evidence conflicts fail closed and never mutate business state.

### R5 — Revalidate signed subscription evidence

Require contract ID/status consistency and strictly parse provider fields used by this task:

```text
next_payment_date
end_date
billing_intents[].updated_at
transactions[].completed_at
```

Invalid required period evidence uses a bounded `PROVIDER_PERIOD_EVIDENCE_INVALID` error.

### R6 — Trusted tenant correlation only

Resolve Shop from Woo operation/current Subscription contract evidence only.

### R7 — Deterministic business lock order

Lock Shop -> Subscription -> relevant operations -> current BillingPeriod -> included counter and revalidate.

### R8 — Receipt arrival order is audit metadata, not sole provider ordering

Continue to record receipt receivedAt/id in lifecycle audit, but never let later HTTP arrival alone regress signed provider financial state. Topic-specific guards below determine staleness.

### R9 — Target paid plan already materialised

Keep accepted trusted operation -> MerchantPricingPlan -> existing BillingPlan resolution.

### R10 — Verified provider payment completion timestamp

For `activated`/`renewed`, identify the newest completed transaction tied to a completed billing intent, ordered by parsed completed_at then transaction ID. Call it `providerPaymentCompletedAt`.

### R11 — Signed next_payment_date is required for active paid periods

For activated/updated/renewed require parseable `subscription.next_payment_date`.

For activation/renewal:

```text
providerNextPaymentAt > providerPaymentCompletedAt
```

For updated, require a valid provider next-payment boundary and fail closed if the signed provider state is incoherent.

### R12 — Activated requires trusted create operation

Keep exact unresolved SUBSCRIPTION_CREATE correlation and historical-contract no-reactivation guards.

### R13 — Initial paid activation opens provider-backed period

Create one OPEN period:

```text
periodStart = providerPaymentCompletedAt
periodEnd   = providerNextPaymentAt
planId      = target BillingPlan
includedRecoveryCreditsGranted = target allowance
```

Create a fresh included counter with grant/current allowance equal to target and zero usage.

Update the existing Free Subscription in place to paid ACTIVE, set provider contract/current period fields, preserve lifetime/purchased/promotional/onboarding, and confirm the create operation atomically.

### R14 — Updated requires one unresolved PLAN_SWITCH

Keep exact trusted PLAN_SWITCH correlation. Never infer target plan from Woo JSON.

### R15 — Plan switch keeps period identity/usage

Do not reset BillingPeriod ID/start or committed/reserved/forfeited. Change plan/current allowance and raise grant high-water only when necessary.

### R16 — Plan switch follows signed next-payment movement

Update:

```text
BillingPeriod.periodEnd = providerNextPaymentAt
Subscription.currentPeriodEnd = providerNextPaymentAt
```

Confirm PLAN_SWITCH atomically. Resume blocked recovery only when spendable capacity increases.

### R17 — Provider-period close helper

When renewal or terminal end closes a period:

- release RESERVED/AMBIGUOUS reservations;
- close included counter against grantedQuantity high-water;
- preserve Woo NOT_APPLICABLE usage events;
- use existing Shopify report-attention close behavior only for Shopify rows;
- close the BillingPeriod after invariants hold.

### R18 — Renewed opens the next paid period

For renewed/active current contract:

- signed next payment date lower than current boundary -> stale no-op;
- duplicate already represented -> no-op;
- real renewal -> close prior period, create exactly one new period from provider payment completion to next_payment_date, create fresh current-plan allowance counter, set ACTIVE/current period fields, schedule capacity resume.

A successful provider renewal is the only event that creates the next Woo included-credit period after activation.

### R19 — Paused freezes and creates no period

For paused/current contract, set `Subscription.status=FROZEN`, preserve plan/provider/current historical period and balances, create no successor period.

If signed provider boundary clearly predates a newer accepted renewal boundary, treat paused as stale no-op.

BACKGROUND-001 keeps paid included unavailable while fallback capacity may still be used.

### R20 — Wall-clock expiry never auto-renews Woo

Passing currentPeriodEnd without a renewed receipt creates no new period and no included allowance reset.

BACKGROUND-001 may use owned fallback capacity while lifecycle evidence converges.

### R21 — Canceled aligns signed prepaid end

Require parseable signed `subscription.end_date`.

Set `cancelAtPeriodEnd=true`.

When a current paid period exists, align its periodEnd/currentPeriodEnd to the accepted provider prepaid end, provided it does not precede the period start/current verified entitlement boundary.

Confirm matching CANCEL operation as already defined.

### R22 — Subscription refunded is cancellation evidence only

Keep `cancelAtPeriodEnd=true`; do not create purchased-credit refund state or switch to Free. Valid signed end_date may align the prepaid end boundary.

### R23 — prepaid_term_ended requires signed reached term end

Require:

```text
signed end_date parseable
end_date <= receipt.receivedAt + bounded clock tolerance
current provider contract matches
```

Then close any open paid period with CONTRACT_ENDED, return the same Subscription to the existing Free plan, clear recurring/current-period fields, preserve onboarding/lifetime/purchased/promotional/history, and schedule capacity resume.

### R24 — Stale/replayed receipts cannot regress current state

Use trusted operation state plus signed provider period/end evidence. Arrival order alone cannot reactivate an old contract, re-freeze a newer renewal period, or end paid access before the signed prepaid end.

### R25 — No provider network dependency

Use durable signed receipts + Moda durable state only.

### R26 — Logging

Use Shared structured logging and bounded identifiers only.

## Work Items

- [ ] Update database gitlink / Prisma.
- [ ] Reuse bounded subscription receipt claiming.
- [ ] Add strict `next_payment_date`, `end_date`, billing-intent and transaction timestamp parsing.
- [ ] Add deterministic provider payment completion extraction.
- [ ] Keep trusted contract-to-Shop and target-operation correlation.
- [ ] Open initial period from provider payment completion -> next_payment_date.
- [ ] Keep same period on plan switch while moving periodEnd/currentPeriodEnd from signed next_payment_date.
- [ ] Preserve switch usage/current-allowance semantics.
- [ ] Close/open the next paid period only on verified renewed.
- [ ] Set FROZEN on paused with no successor period.
- [ ] Add stale paused/renewed provider-boundary guards.
- [ ] Align canceled prepaid end from signed end_date.
- [ ] Require reached signed end_date before prepaid-term-ended Free fallback.
- [ ] Remove all dependency on local exact-30-day rollover.
- [ ] Add provider-period/frozen-fallback/cancellation ordering tests.

## Interfaces / Contracts

### Durable input

WooCommerceBillingWebhookReceipt from API-005; only subscription-wrapper rows.

### Woo provider period

```text
activated/renewed:
    periodStart = verified completed provider payment timestamp
    periodEnd   = signed next_payment_date

updated:
    same periodStart
    periodEnd = signed updated next_payment_date

canceled:
    prepaid end = signed end_date
```

### FROZEN

```text
paid included -> unavailable
no successor period
fallback capacity -> BACKGROUND-001
```

### Trusted correlation

Provider contract maps only through Woo operation/current Subscription; target plan maps through the trusted operation to already-materialised BillingPlan.

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

- [ ] Existing worker/receipt claiming remains bounded and atomic.
- [ ] Activated uses signed provider payment completion and next_payment_date rather than local +30 days.
- [ ] Plan switch keeps period ID/start and usage but updates current allowance and signed period end.
- [ ] Renewed closes old period and creates exactly one new paid period/counter.
- [ ] Included usage resets only when verified renewal opens a new period.
- [ ] Paused sets FROZEN and creates no successor period.
- [ ] FROZEN fallback capacity remains usable through BACKGROUND-001.
- [ ] Passing currentPeriodEnd without renewed creates no new paid period.
- [ ] Canceled keeps paid access and aligns end from signed end_date.
- [ ] prepaid_term_ended with future signed end_date cannot switch to Free.
- [ ] Reached signed prepaid term end closes paid period and returns same Subscription to Free.
- [ ] Delayed stale evidence cannot regress a newer provider period using receipt arrival alone.
- [ ] No provider network request occurs.
- [ ] BACKGROUND-003 is not required.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Required categories:

- [ ] Prisma generate/validate;
- [ ] build/typecheck/lint;
- [ ] receipt scan/concurrency/retry tests;
- [ ] provider payment completion + next_payment_date parsing;
- [ ] Free -> paid provider-period activation;
- [ ] updated switch same period/start + moved provider end;
- [ ] upgrade/downgrade usage preservation;
- [ ] renewed close/open/reset included allowance;
- [ ] paused FROZEN no-successor;
- [ ] FROZEN fallback integration with BACKGROUND-001;
- [ ] wall-clock expiry without renewed no-new-period;
- [ ] delayed old paused stale-no-op where provider boundary proves it;
- [ ] canceled signed end_date projection;
- [ ] prepaid_term_ended future end rejection;
- [ ] prepaid_term_ended reached end paid -> Free;
- [ ] stale activation after Free fallback;
- [ ] no provider HTTP/credentials;
- [ ] `git diff --check`;
- [ ] dedicated worktree/submodule/push evidence.

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
