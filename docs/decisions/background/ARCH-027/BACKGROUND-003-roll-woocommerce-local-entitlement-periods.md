---
id: ARCH-027-BACKGROUND-003
architecture_id: ARCH-027
title: Roll WooCommerce local recovery entitlement periods every 30 days
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-BACKGROUND-002
enables:
  - ARCH-027-BACKGROUND-004
created: 2026-10-03
updated: 2026-10-03
---

# Roll WooCommerce local recovery entitlement periods every 30 days

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Advance ACTIVE Woo paid merchants through Moda's local `EVERY_30_DAYS` recovery-entitlement periods independently of Woo's provider financial/proration dates.

The bounded lifecycle is:

```text
ACTIVE Woo paid Subscription
currentPeriodEnd <= now
        |
        v
lock/revalidate the current local period
        |
        v
close the expired period using existing Moda close semantics
        |
        v
create the next exact 30-day local period
with the Subscription's current plan allowance
        |
        +-- if that successor is already expired, close it too
        |   and continue bounded catch-up
        |
        v
leave exactly one current OPEN period containing now
        |
        v
update Subscription.billingPeriodId/currentPeriodStart/currentPeriodEnd
        |
        v
after commit, schedule recovery-capacity resume
```

This task owns the **time-driven local entitlement cadence only**.

It MUST NOT:

- call WooCommerce.com;
- process Woo webhook receipts;
- use `next_payment_date`, `end_date` or any Woo proration date as a reset boundary;
- change the current plan;
- change `providerSubscriptionId`;
- unfreeze a FROZEN subscription;
- end prepaid access;
- apply plan-switch pricing;
- activate/refund top-up purchases;
- create another Subscription.

BACKGROUND-002 remains the provider-lifecycle owner. BACKGROUND-003 advances only the local Moda recovery period while that provider-backed subscription is currently ACTIVE.

## Context

ARCH-027 deliberately separates:

```text
Woo provider financial lifecycle
```

from:

```text
Moda recovery-entitlement cadence
```

BACKGROUND-002 creates the first Woo paid local period at verified activation:

```text
periodStart = activated receipt.receivedAt
periodEnd   = periodStart + exactly 30 days
```

It explicitly does **not** rotate that period on:

```text
renewed
updated
paused
canceled
```

The current Background source already contains strong reusable same-plan rollover mechanics in:

```text
src/services/same-plan-billing-period-rollover.service.ts
```

Those mechanics correctly:

- serialize on the Subscription;
- release `RESERVED` / `AMBIGUOUS` reservations with `PERIOD_CLOSED`;
- close the included-credit counter against `grantedQuantity`;
- move Shopify `PENDING` / `RETRYABLE` usage to `NEEDS_ATTENTION`;
- create a successor period/counter;
- update the current Subscription projection;
- schedule recovery-capacity resume after a paid rollover.

However, that service is provider-cycle driven and explicitly validates Shopify plan/meter/provider-cycle evidence. Woo local cadence MUST NOT fake a `PartnerSubscription` or reuse provider dates merely to call it.

The smallest safe implementation is therefore:

1. extract/reuse only the provider-neutral local-period finalization mechanics where that avoids duplication;
2. add one Woo-specific local-cadence service that derives successor boundaries only from the current Moda `BillingPeriod.periodEnd`.

The source also already blocks new paid recovery admission when the current period is `EXPIRED_RECONCILING`, so an overdue Woo period cannot continue spending expired included capacity while rollover catches up.

## Scope

Modify only `moda-interact-background` production/tests required for local Woo period rollover.

Expected primary production areas:

```text
src/services/
  same-plan-billing-period-rollover.service.ts
  woo-local-billing-period-rollover.service.ts

src/entrypoints/billing.ts
```

A small repository-local helper may be extracted from the existing Shopify same-plan rollover service for period finalization if needed. The extraction MUST preserve existing Shopify behavior byte-for-behavior and remain inside `moda-interact-background`.

Do not create a Shared package helper.

Reuse:

- existing billing reconciliation lease/scheduler;
- Prisma transactions;
- Subscription row locking;
- current BillingPeriod/counter invariants;
- `recoveryCapacityResumeService`;
- Shared structured logging.

## Out of Scope

- Woo provider webhook receipt processing.
- Woo subscription activation/switch/pause/cancel/prepaid-end.
- Woo provider API calls or credentials.
- Shopify provider-cycle rollover redesign.
- Changing the 30-day product cadence.
- Changing `MerchantPricingAllowancePeriod`.
- Changing plan prices/features.
- Top-up charge reconciliation.
- Refund reconciliation.
- API/UI/Admin/Gateway changes.
- Prisma schema/migration changes.
- A new worker/queue/cron deployment.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Execute inside the existing leased billing cycle

Instantiate the Woo local rollover service in:

```text
src/entrypoints/billing.ts
```

Run it from the existing `BILLING_RECONCILIATION` leased cycle.

Ordering inside one leased cycle MUST be:

```text
1. Woo recurring receipt reconciliation (BACKGROUND-002)
2. Woo local entitlement-period rollover (BACKGROUND-003)
```

This allows a `renewed` receipt to unfreeze an overdue merchant before local rollover is evaluated, and allows `prepaid_term_ended` to return the merchant to Free before any further local period could be granted.

Do not create another scheduler or lease name.

### R2 — Exact scan bound

Define exactly:

```text
MAX_WOO_LOCAL_PERIOD_SUBSCRIPTIONS_PER_CYCLE = 50
```

Select at most 50 candidate subscriptions per leased cycle.

Candidate predicate:

```text
Shop.platform = WOOCOMMERCE
Shop.status = ACTIVE

Subscription.status = ACTIVE
Subscription.plan.kind = PAID_METERED
Subscription.plan.active = true

Subscription.providerSubscriptionId IS NOT NULL
Subscription.billingPeriodId IS NOT NULL
Subscription.currentPeriodStart IS NOT NULL
Subscription.currentPeriodEnd IS NOT NULL
Subscription.currentPeriodEnd <= now
```

`cancelAtPeriodEnd = true` does **not** exclude a subscription; Woo canceled contracts preserve prepaid access until `prepaid_term_ended`.

Exclude:

```text
FROZEN
NO_CONTRACT
UNMAPPED
SYNC_ERROR
TRIALING
```

from automatic Woo local rollover.

Order candidates by:

```text
currentPeriodEnd ASC,
id ASC
```

### R3 — One Subscription transaction at a time

Process each candidate in its own database transaction.

First lock the Subscription:

```sql
SELECT "id"
FROM "billing"."Subscription"
WHERE "id" = :subscription_id
FOR UPDATE;
```

Then re-read and revalidate the complete R2 predicate plus exact current period/counter identity.

Two concurrent rollover attempts for the same Subscription must serialize. After the first succeeds, the second must observe the new future `currentPeriodEnd` and return a no-op.

### R4 — Exact local period duration

Define:

```text
WOO_LOCAL_ENTITLEMENT_PERIOD_MS =
    30 * 24 * 60 * 60 * 1000
```

Successor boundaries are always:

```text
successorStart = currentPeriod.periodEnd
successorEnd   = successorStart + WOO_LOCAL_ENTITLEMENT_PERIOD_MS
```

Use absolute UTC instants / milliseconds.

Do not use:

```text
calendar month arithmetic
Woo next_payment_date
Woo end_date
provider renewal timestamp
current wall-clock time as successorStart
```

This prevents cadence drift.

### R5 — Exact current projection validation

After locking, require:

```text
Subscription.billingPeriodId = current BillingPeriod.id
Subscription.currentPeriodStart = BillingPeriod.periodStart
Subscription.currentPeriodEnd   = BillingPeriod.periodEnd

BillingPeriod.status = OPEN
BillingPeriod.shopId = Subscription.shopId
BillingPeriod.subscriptionId = Subscription.id

BillingPeriod.periodStart < BillingPeriod.periodEnd
BillingPeriod.periodEnd <= now
```

Require one current `INCLUDED_RECOVERY_CREDITS` counter and the BACKGROUND-001 invariants.

If current projection is inconsistent, fail closed for that candidate, emit a bounded semantic error log and do not mutate any billing rows.

Do not convert this local projection error into a Woo provider lifecycle error.

### R6 — Use the Subscription's **current** paid plan for every successor

Load the current `Subscription.plan`.

Require:

```text
plan.active = true
plan.kind = PAID_METERED
includedRecoveryConversationAllowance is a non-negative safe integer
```

The successor period uses that **current** plan, even if the expiring BillingPeriod's opening snapshot refers to an older plan because BACKGROUND-002 applied a Woo mid-period plan switch.

Successor snapshot:

```text
planId                         = current Subscription.planId
shopifyPlanHandleSnapshot      = current BillingPlan.shopifyPlanHandle
planNameSnapshot               = current BillingPlan.name
planKindSnapshot               = PAID_METERED
includedRecoveryCreditsGranted = current plan allowance
```

`shopifyPlanHandleSnapshot` remains current-schema operational audit data only; it is not Woo provider identity.

### R7 — Existing current period close uses the high-water grant

Close each expired OPEN period using the same provider-neutral mechanics already proven by Shopify rollover.

For its included counter:

1. aggregate `UsageReservation.quantity` where status is:
   ```text
   RESERVED
   AMBIGUOUS
   ```
2. require the aggregate equals `counter.reservedQuantity`;
3. release those reservations with:
   ```text
   status = RELEASED
   releaseReason = PERIOD_CLOSED
   ```
4. calculate:
   ```text
   forfeitableAfterRelease =
       grantedQuantity
       - committedQuantity
       - forfeitedQuantity
   ```
5. require `forfeitableAfterRelease >= 0`;
6. set:
   ```text
   reservedQuantity -> 0
   forfeitedQuantity += forfeitableAfterRelease
   version += 1
   ```
7. require the closed counter satisfies:
   ```text
   reservedQuantity = 0
   committedQuantity + forfeitedQuantity = grantedQuantity
   ```

Do **not** close against `currentAllowanceQuantity`.

`grantedQuantity` remains the high-water/audit grant even if a Woo downgrade made the current spend ceiling lower.

### R8 — Preserve usage-reporting close behavior

Before closing an expired period, move only usage rows in:

```text
shopifyReportState IN (PENDING, RETRYABLE)
```

to the existing:

```text
NEEDS_ATTENTION
providerErrorCode = PERIOD_CLOSED_BEFORE_REPORT
```

close state.

Do not modify:

```text
REPORTED
IN_FLIGHT
NOT_APPLICABLE
```

Woo paid included usage created by BACKGROUND-001 is `NOT_APPLICABLE` and therefore remains untouched.

Do not activate/fail `RecoveryCreditPurchase` rows merely because their acquisition period closes.

### R9 — Deterministic close reason

Set the expired period close reason as:

```text
if expired BillingPeriod.planId = current Subscription.planId:
    RENEWED_SAME_PLAN

else:
    PLAN_CHANGED
```

The second case captures a Woo plan switch that occurred mid-period while the opening BillingPeriod snapshot intentionally remained unchanged.

`RENEWED_SAME_PLAN` here means local Moda entitlement-period renewal. It does not assert a Woo provider renewal occurred at that instant.

Set:

```text
closedAt = expired BillingPeriod.periodEnd
```

not `now`.

### R10 — Exact successor included counter

Every successor paid period gets exactly one:

```text
counter = INCLUDED_RECOVERY_CREDITS

grantedQuantity          = current plan allowance
currentAllowanceQuantity = current plan allowance
committedQuantity        = 0
reservedQuantity         = 0
forfeitedQuantity        = 0
```

Do not carry committed/reserved/forfeited usage into the new period.

Do not carry a previous period's lower/higher `currentAllowanceQuantity`; the new period starts from the current plan's configured allowance.

### R11 — Preserve non-rollover balances

Period rollover MUST NOT mutate:

```text
ShopEntitlementCounter
PromotionalCreditGrant
RecoveryCreditPurchase
RecoveryCreditRefund
```

Purchased credits remain lifetime purchase lots.

Lifetime Free credits remain one-time Shop state.

Promotional semantics remain unchanged.

### R12 — Bounded multi-period catch-up

A Shop may be overdue by more than one local period after worker downtime or a long FROZEN interval.

Define exactly:

```text
MAX_WOO_LOCAL_PERIOD_TRANSITIONS_PER_SUBSCRIPTION = 12
```

Within one locked transaction:

```text
while currentPeriodEnd <= now
  and transitions < 12:
    close current expired period
    create/reuse next exact 30-day period
    make it the in-memory current period
```

If the new successor is itself expired, continue and immediately close it on the next loop iteration.

This means skipped full periods are still durably represented and their entire unused grant is forfeited through the normal close invariant rather than rolled forward.

### R13 — Catch-up never exposes an already-expired grant as usable capacity

If after 12 transitions:

```text
currentPeriodEnd <= now
```

commit the bounded catch-up progress but classify the result:

```text
CATCH_UP_INCOMPLETE
```

Update the Subscription to the latest created OPEN period even though it is still expired.

Do **not** schedule capacity resume yet.

The existing effective billing policy sees:

```text
phase = EXPIRED_RECONCILING
```

and continues to block new recoveries.

The next leased cycle resumes catch-up from that exact durable point.

This bounds transaction size without allowing credits from an already-expired period to become spendable.

### R14 — Exactly one current OPEN period after each transaction

After transition/catch-up, set the Subscription to the latest successor:

```text
billingPeriodId    = successor.id
currentPeriodStart = successor.periodStart
currentPeriodEnd   = successor.periodEnd
```

Preserve:

```text
planId
status = ACTIVE
providerSubscriptionId
cancelAtPeriodEnd
trialEndsAt
lastProviderLifecycle*
```

Do not update provider lifecycle ordering fields; this is a local time-driven transition, not provider evidence.

Do not modify `nextReconcileAt` for Woo.

At transaction commit there must be exactly one OPEN BillingPeriod referenced by the Subscription.

Historical catch-up periods created and immediately expired in the same transaction finish CLOSED.

### R15 — Existing successor rows are validated, never silently rewritten

For each exact successor range:

```text
(shopId, successorStart, successorEnd)
```

if a BillingPeriod already exists, require:

```text
shopId matches
subscriptionId matches
planId = current plan id
plan snapshot fields match
includedRecoveryCreditsGranted = current plan allowance
```

If it is the intended latest current successor, it may be OPEN.

If it is an intermediate already-expired catch-up successor, it may already be CLOSED only when its close invariants are also valid.

Any incompatible row is a bounded state conflict and the candidate transaction must roll back.

Do not reopen a CLOSED BillingPeriod.

### R16 — Recovery-capacity resume only after reaching a live period

After a successful transaction where:

```text
final currentPeriodEnd > now
```

schedule after commit:

```text
recoveryCapacityResumeService.schedule({
  shopId,
  trigger: "woo-billing-period-rollover"
})
```

This is required even when the new included allowance is zero because moving from `EXPIRED_RECONCILING` to a live period may make purchased/lifetime/promotional capacity usable again.

Failure to schedule resume does not roll back the committed period transition; log a bounded warning.

For `CATCH_UP_INCOMPLETE`, do not schedule resume.

### R17 — FROZEN does not grant new local periods

A FROZEN Woo paid Subscription is not eligible for BACKGROUND-003 rollover.

If its local period expires while FROZEN:

```text
no successor grant is created by this task
```

When a later verified Woo `renewed` receipt makes the Subscription ACTIVE, BACKGROUND-002 runs before BACKGROUND-003 in the same leased cycle. BACKGROUND-003 can then catch the local cadence up from the original period boundaries.

Skipped full periods are forfeited rather than granted retroactively.

### R18 — Scheduled cancellation does not stop paid local cadence

`cancelAtPeriodEnd = true` does not by itself block rollover while:

```text
Subscription.status = ACTIVE
providerSubscriptionId is still present
```

Woo cancellation preserves prepaid access until `prepaid_term_ended`.

Local 30-day periods therefore continue as necessary until BACKGROUND-002 receives verified prepaid-end evidence and returns the merchant to Free.

### R19 — Prepaid term end wins before local rollover in the same leased cycle

The billing entrypoint ordering from R1 is mandatory.

If a valid `prepaid_term_ended` receipt is already durable when the leased cycle starts:

```text
BACKGROUND-002
    -> returns Subscription to Free
    -> closes current paid period

then

BACKGROUND-003
    -> candidate no longer matches ACTIVE Woo paid predicate
    -> no successor period
```

Do not reverse this order.

### R20 — No provider/network dependency

BACKGROUND-003 must not:

```text
call Woo
read Woo API credentials
query Woo contract state
read webhook normalizedPayload
```

The current durable Moda Subscription/period state is sufficient.

### R21 — No new transport

Do not create:

```text
BullMQ job
Redis state
outbox event
new scheduled task
```

for local rollover.

The existing billing reconciliation scheduler is the trigger.

### R22 — Structured logging

Use the Shared structured logger.

Allowed bounded fields:

```text
shopId
subscriptionId
oldBillingPeriodId
newBillingPeriodId
transitions
result = TRANSITIONED | CATCH_UP_INCOMPLETE | NO_OP | CONFLICT
currentPeriodEnd
```

Do not log provider payloads/customer data.

Use existing database/framework telemetry; do not add duplicate generic worker metrics.

## Work Items

- [ ] Reuse the accepted ARCH-027 database client/generated schema.
- [ ] Inspect/extract the existing provider-neutral period-finalization mechanics from Shopify same-plan rollover without changing Shopify behavior.
- [ ] Add one Woo local billing-period rollover service.
- [ ] Wire it into the existing leased billing cycle after BACKGROUND-002 recurring receipt reconciliation.
- [ ] Add the exact 50-subscription per-cycle scan.
- [ ] Add Subscription row locking and full predicate revalidation.
- [ ] Implement exact 30-day absolute successor boundaries.
- [ ] Use current Subscription plan for successor snapshots/allowance.
- [ ] Close expired period counters against high-water `grantedQuantity`.
- [ ] Release RESERVED/AMBIGUOUS reservations as `PERIOD_CLOSED`.
- [ ] Preserve existing Shopify pending/retryable usage close handling and leave Woo `NOT_APPLICABLE` rows untouched.
- [ ] Apply deterministic `RENEWED_SAME_PLAN` vs `PLAN_CHANGED` close reason.
- [ ] Create successor counter with grant/current allowance equal to the current plan allowance.
- [ ] Preserve lifetime/purchased/promotional state.
- [ ] Implement bounded 12-transition catch-up.
- [ ] Ensure already-expired catch-up periods cannot become usable capacity.
- [ ] Validate/reuse compatible existing successor rows and never reopen closed rows.
- [ ] Update Subscription current-period pointer/dates only.
- [ ] Schedule capacity resume only after reaching a live period.
- [ ] Prove FROZEN does not roll and renewed ACTIVE catches up later.
- [ ] Prove scheduled cancellation continues local cadence until prepaid-end.
- [ ] Add focused concurrency, catch-up and Shopify-regression tests.

## Interfaces / Contracts

### Trigger

Existing:

```text
BILLING_RECONCILIATION leased scheduler
```

Order:

```text
BACKGROUND-002 recurring Woo receipts
then
BACKGROUND-003 local Woo rollover
```

### Candidate durable state

```text
Shop.platform = WOOCOMMERCE

Subscription.status = ACTIVE
Subscription.plan.kind = PAID_METERED
Subscription.providerSubscriptionId != NULL
Subscription.currentPeriodEnd <= now
```

### Cadence

```text
period N+1 start = period N end
period N+1 end   = start + 30 * 24h
```

### Successor counter

```text
grantedQuantity          = current plan allowance
currentAllowanceQuantity = current plan allowance
committedQuantity        = 0
reservedQuantity         = 0
forfeitedQuantity        = 0
```

### Existing close helper

Provider-neutral close semantics may be extracted/reused from:

```text
SamePlanBillingPeriodRolloverService
```

but Shopify provider-cycle validation/inputs must remain in the Shopify service.

No cross-repository contract is introduced.

## Dependencies

- `ARCH-027-BACKGROUND-002`

BACKGROUND-002 must be architect-accepted Complete before BACKGROUND-003 becomes Ready because it owns:

- initial Woo paid local period creation;
- provider pause/renew ACTIVE/FROZEN lifecycle;
- cancellation/prepaid-end behavior;
- the required entrypoint ordering.

Through BACKGROUND-002, this task also depends on BACKGROUND-001's current allowance/provider-safe accounting.

## Enables

- `ARCH-027-BACKGROUND-004`

BACKGROUND-004 owns verified Woo one-time-charge acquisition receipt reconciliation after the shared Background billing-cycle ordering/cadence is accepted.

## Acceptance Criteria

- [ ] Existing billing worker executes Woo local rollover; no new deployable worker/scheduler/queue exists.
- [ ] BACKGROUND-002 recurring receipt reconciliation executes before local rollover in each leased cycle.
- [ ] At most 50 due Woo paid subscriptions are selected per cycle.
- [ ] Candidate selection requires active Woo Shop, ACTIVE paid Subscription, provider contract and expired current period.
- [ ] FROZEN/TRIALING/non-paid/non-Woo subscriptions are excluded.
- [ ] `cancelAtPeriodEnd=true` alone does not exclude an otherwise ACTIVE paid Woo subscription.
- [ ] Two concurrent rollover attempts serialize on Subscription and create one canonical successor chain.
- [ ] Every successor boundary is exactly previous period end + absolute 30 days.
- [ ] Successor boundaries never use Woo provider dates or `now` as the start.
- [ ] Successor uses current Subscription plan and its current allowance.
- [ ] Current-period close releases RESERVED/AMBIGUOUS reservations and closes against `grantedQuantity`.
- [ ] Lower `currentAllowanceQuantity` never changes the high-water close invariant.
- [ ] Woo `NOT_APPLICABLE` usage events are not rewritten on close.
- [ ] Shopify PENDING/RETRYABLE close regression remains unchanged.
- [ ] Same-plan close uses `RENEWED_SAME_PLAN`.
- [ ] A period whose opening plan differs from current Subscription plan closes with `PLAN_CHANGED`.
- [ ] New successor counter starts with grant/current allowance equal to current plan allowance and zero usage.
- [ ] Lifetime Free, purchased and promotional state is unchanged.
- [ ] Catch-up performs at most 12 period transitions for one Subscription in one transaction.
- [ ] Full skipped periods are durably represented and forfeit unused allowance instead of rolling it forward.
- [ ] If catch-up remains overdue after 12 transitions, current projection remains expired/reconciling and no capacity-resume job is scheduled.
- [ ] If catch-up reaches a live period, exactly one current OPEN period is referenced by Subscription and capacity resume is scheduled after commit.
- [ ] Existing compatible successor replay is idempotent; incompatible/closed successor is never silently reopened/rewritten.
- [ ] FROZEN period expiry creates no successor grant.
- [ ] Renewed -> ACTIVE can catch up from the original cadence without granting skipped periods retroactively.
- [ ] Prepaid-term-end processed earlier in the cycle prevents local rollover from creating a successor.
- [ ] No Woo network/credential/webhook-payload dependency exists.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect the accepted `moda-interact-background/package.json` before choosing exact commands.

Required validation categories:

- [ ] repository production build/typecheck;
- [ ] targeted lint/changed-file diagnostics;
- [ ] existing Shopify same-plan rollover focused tests remain green after any helper extraction;
- [ ] existing Shopify same-plan PostgreSQL concurrency test remains green;
- [ ] Woo one-period rollover unit test;
- [ ] Woo exact 30-day boundary test;
- [ ] Woo mid-period plan-switch successor-plan snapshot test;
- [ ] Woo downgrade/currentAllowance lower than grant close test;
- [ ] Woo reserved/ambiguous release test;
- [ ] Woo `NOT_APPLICABLE` usage close-preservation test;
- [ ] same-plan vs plan-changed close-reason tests;
- [ ] successor counter exact grant/current-allowance test;
- [ ] lifetime/purchased/promotional non-mutation test;
- [ ] 2-period/3-period catch-up tests;
- [ ] exact 12-transition catch-up bound test;
- [ ] catch-up-incomplete remains `EXPIRED_RECONCILING` test;
- [ ] catch-up-to-live schedules capacity resume test;
- [ ] resume-scheduler failure does not roll back committed rollover test;
- [ ] FROZEN no-rollover test;
- [ ] FROZEN-overdue -> renewed ACTIVE -> catch-up test;
- [ ] cancelAtPeriodEnd ACTIVE rollover test;
- [ ] prepaid-term-ended-before-rollover ordering test;
- [ ] incompatible successor rollback test;
- [ ] closed successor no-reopen test;
- [ ] two-worker Woo rollover PostgreSQL concurrency test;
- [ ] no Woo provider HTTP/secret access assertion;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization and pushed task-branch evidence.

No Woo sandbox/provider request is required.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin one-time-charge receipt reconciliation.

## Implementation Notes

Do not call `SamePlanBillingPeriodRolloverService` with a fabricated Woo `PartnerSubscription`.

Reuse only genuinely provider-neutral close mechanics.

The target design is:

```text
Shopify service
    provider cycle -> shared local close mechanics -> successor

Woo local service
    Moda periodEnd -> shared local close mechanics -> successor
```

not:

```text
Woo -> fake Shopify provider object
```

Keep the 30-day cadence deterministic and drift-free by deriving every successor from the previous durable period end.

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

- BACKGROUND-002 creates the first Woo paid local BillingPeriod and owns ACTIVE/FROZEN/prepaid-end lifecycle.
- BACKGROUND-001 has already made current allowance and Woo local usage accounting safe.
- BillingPeriodCloseReason `RENEWED_SAME_PLAN` is acceptable for local same-plan entitlement renewal and does not imply a Woo provider renewal happened at that instant.
- Existing recovery admission remains blocked while the current period is `EXPIRED_RECONCILING`.

### Unresolved Issues

None within this bounded local-cadence task.

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
