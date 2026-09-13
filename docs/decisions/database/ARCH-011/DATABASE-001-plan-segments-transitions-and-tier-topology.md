---
id: ARCH-011-DATABASE-001
architecture_id: ARCH-011
title: Persist plan segments and upgrade transitions and enforce canonical tier topology
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-014
enables:
- ARCH-011-BACKGROUND-002
- ARCH-011-SHOPIFY-001
- ARCH-011-ADMIN-001
created: 2026-09-13
updated: '2026-09-13'
---

# ARCH-011-DATABASE-001: Persist plan segments and upgrade transitions and enforce canonical tier topology

## Objective

Implement the **complete database-owned ARCH-011 persistence contract in one task**. This task owns both:

1. durable provider-cycle plan history / upgrade-transition evidence; and
2. final commit-time validity of the existing `BillingUpgradeEconomicsEdge` tier-order topology.

Do not split either responsibility into another Database task. Do not edit accepted ARCH-010 migrations or completed task history.

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
scripts/validate-first-production-baseline.mjs
scripts/generate-erd.mjs
docs/generated/prisma-erd.puml

BillingPlan
BillingUpgradeEconomicsEdge
Subscription
BillingPeriod
BillingPeriodEntitlementCounter
RecoveryCreditPurchase
```

`ARCH-010-DATABASE-014` is accepted. Preserve its purchase/refund lifecycle and provenance exactly.

## A. Persist `BillingPlanSegment`

Add a model using repository naming conventions with at least:

```text
id
shopId -> Shop
billingPeriodId -> BillingPeriod
planId -> BillingPlan nullable only if current schema conventions require historical SetNull

shopifyPlanHandleSnapshot
planNameSnapshot
planKindSnapshot
includedAllowanceSnapshot Int

effectiveFrom DateTime
effectiveTo DateTime
sourceTransitionId -> SubscriptionPlanTransition nullable UNIQUE

createdAt
updatedAt
```

Required invariants:

```text
includedAllowanceSnapshot >= 0
effectiveFrom < effectiveTo
unique(billingPeriodId, effectiveFrom)
sourceTransitionId creates at most one segment
```

Semantics:

- one `BillingPeriod` remains one exact Shopify provider billing cycle;
- `BillingPeriod.plan*Snapshot` remains the **period-opening plan snapshot** and is not rewritten on each upgrade;
- `BillingPlanSegment` records the plan effective over a sub-range of that provider cycle;
- the current segment may initially end at `BillingPeriod.periodEnd`; a later same-cycle upgrade atomically shortens the prior segment to the provider effective time and creates the new segment through `periodEnd`;
- historical segment snapshots are immutable after their transition is APPLIED except for the single atomic closing adjustment required when the next provider-confirmed segment begins.

## B. Persist `SubscriptionPlanTransition`

Add enum `SubscriptionPlanTransitionStatus` with exactly these semantics:

```text
REQUESTED
  merchant selected a target; provider has not proven that target current.

PROVIDER_CONFIRMED
  exact provider current plan/cycle/effective-event evidence persisted;
  local segment/counter application has not completed.

APPLIED
  provider-confirmed transition applied exactly once.

SUPERSEDED
  REQUESTED target replaced after a fresh provider read proved it never became current.

FAILED
  provider definitively rejected/removed the request without making it current.

NEEDS_ATTENTION
  provider/local evidence is ambiguous or contradictory; fail closed.
```

Terminal states:

```text
APPLIED
SUPERSEDED
FAILED
```

Add enum `SubscriptionPlanTransitionApplicationMode`:

```text
SAME_CYCLE_PRORATED
NEW_PROVIDER_CYCLE_FULL_ALLOWANCE
```

`applicationMode` is nullable until provider-cycle relationship is proven.

Persist at minimum:

```text
id
shopId -> Shop
subscriptionId -> Subscription
billingPeriodId -> BillingPeriod nullable until provider cycle proven

fromPlanId -> BillingPlan
requestedToPlanId -> BillingPlan

fromPlanHandleSnapshot
requestedToPlanHandleSnapshot
fromPlanKindSnapshot
toPlanKindSnapshot
fromIncludedAllowanceSnapshot
toIncludedAllowanceSnapshot

requestKey UNIQUE
status
applicationMode nullable
version >= 0
requestedAt

providerSubscriptionIdSnapshot nullable
providerCycleStartSnapshot nullable
providerCycleEndSnapshot nullable
providerEffectiveAt nullable
providerLifecycleEventId nullable UNIQUE
providerConfirmedPlanHandle nullable
providerEvidence Json nullable
providerConfirmedAt nullable

# immutable same-cycle calculation evidence
targetEntitlementSnapshot nullable Int
alreadyGrantedSnapshot nullable Int
includedCreditDelta nullable Int

appliedAt nullable
supersededAt nullable
failedAt nullable
failureCode bounded nullable string

createdAt
updatedAt
```

At `REQUESTED`, snapshot the effective source plan and selected target plan from server-resolved state. Canonical included allowance snapshot:

```text
FREE => 0
PAID_METERED => includedRecoveryConversationAllowance; null is invalid
```

After `PROVIDER_CONFIRMED`, source/target/provider/calculation snapshots are immutable historical evidence. Never recalculate an APPLIED transition from later `BillingPlan` configuration.

For `SAME_CYCLE_PRORATED + APPLIED`, require application/service validation that these are non-null:

```text
billingPeriodId
providerSubscriptionIdSnapshot
providerCycleStartSnapshot
providerCycleEndSnapshot
providerEffectiveAt
providerLifecycleEventId
providerConfirmedPlanHandle
targetEntitlementSnapshot
alreadyGrantedSnapshot
includedCreditDelta
providerConfirmedAt
appliedAt
```

For `NEW_PROVIDER_CYCLE_FULL_ALLOWANCE`, `targetEntitlementSnapshot`, `alreadyGrantedSnapshot` and `includedCreditDelta` remain null because ARCH-010 opening-period logic owns the full allowance.

## C. One unresolved transition per subscription

Enforce at database level with a PostgreSQL partial unique index (or an equivalent stronger repository-supported mechanism):

```text
at most one transition for subscriptionId where status in
  REQUESTED, PROVIDER_CONFIRMED, NEEDS_ATTENTION
```

Do not rely only on Shopify UI checks.

## D. Canonical active tier topology

The existing `BillingUpgradeEconomicsEdge` graph is the ordering authority. It defines **adjacent ordering only**, not allowed merchant transition steps.

For ARCH-011 release 1, catalogue plans are exactly active `BillingPlan` rows. If inspection finds active internal/non-merchant plans that make this definition invalid, STOP and return exact rows/model evidence to `moda_architect`; do not invent a hidden filter.

Let:

```text
P = active BillingPlan rows
E = active BillingUpgradeEconomicsEdge rows
N = |P|
```

Valid final topology:

```text
N = 0:
  E must contain no active edge referencing an active catalogue plan.

N = 1:
  |E| = 0.

N > 1:
  |E| = N - 1
  every active edge endpoint belongs to P
  exactly one plan has in-degree 0
  exactly one plan has out-degree 0
  every other plan has in-degree 1 and out-degree 1
  following higher edges from the lowest plan visits every active plan exactly once
  no self edge
  no cycle
  no disconnected active plan
```

Preserve existing unique predecessor/successor constraints:

```text
@@unique([lowerPlanId])
@@unique([higherPlanId])
```

Do **not** add `tierRank`, price ordering, name ordering or allowance ordering as a second authority.

Example persisted chain:

```text
Free -> Starter -> Growth -> Scale
```

This does **not** require direct `Free -> Scale` or `Starter -> Scale` edges. Runtime transitive reachability classifies those as upgrades.

## E. Database enforcement of topology

Implement commit-time PostgreSQL enforcement where Prisma cannot express whole-graph validity. Binding design:

1. schema-qualified validation function reads `BillingPlan` + `BillingUpgradeEconomicsEdge`;
2. function raises a bounded identifiable database error/code when final active topology is invalid;
3. `DEFERRABLE INITIALLY DEFERRED` constraint-trigger coverage runs after mutations that can change topology:
   - `BillingPlan` INSERT/DELETE/update of `active`;
   - `BillingUpgradeEconomicsEdge` INSERT/DELETE/update of `lowerPlanId`, `higherPlanId`, `active`;
4. validation sees **final transaction state**, so Admin may atomically replace several edges;
5. migration explicitly invokes validation after installation so existing invalid data fails migration visibly.

If the repository/PostgreSQL version cannot safely implement deferred final-state enforcement, STOP and return exact evidence. Do not silently move final authority to Admin.

## F. Relations, indexes and migration

Add all reverse relations required by Prisma. Add indexes for expected access patterns at minimum:

```text
BillingPlanSegment: billingPeriodId + effectiveFrom/effectiveTo
SubscriptionPlanTransition: subscriptionId + status + requestedAt
SubscriptionPlanTransition: billingPeriodId + status
SubscriptionPlanTransition: providerLifecycleEventId unique when present
```

Create one additive ARCH-011 migration after the accepted ARCH-010 baseline. Do not rewrite completed migrations. Regenerate ERD.

## Required tests / validation

Add database-focused validation proving at minimum:

1. segment `effectiveFrom < effectiveTo`;
2. duplicate segment start in one BillingPeriod rejected;
3. one transition creates at most one source segment;
4. only one unresolved transition per subscription;
5. duplicate provider lifecycle event rejected;
6. valid 4-plan chain accepted;
7. cycle rejected;
8. branch rejected;
9. disconnected active plan rejected;
10. self edge rejected;
11. multiple-row atomic edge replacement succeeds when final state is valid;
12. same intermediate edits fail when committed in an invalid final state;
13. no tier-rank/price/name ordering field introduced;
14. Prisma validate/generate and first-production baseline validation remain green;
15. generated ERD includes new models/relations.

Run repository-declared equivalents of:

```text
npm run prisma:validate
npm run prisma:generate
node scripts/validate-first-production-baseline.mjs
<focused database tests / migration validation>
npm run build   # if declared
git diff --check
```

## Non-goals

No Shared implementation, no provider API call, no merchant UI, no entitlement mutation, no Admin UI, no cash-proration logic.

## Stop conditions

STOP and return evidence if:

- active BillingPlan rows are not a valid merchant-catalogue definition;
- a deferred final-state topology constraint cannot be implemented safely;
- implementing the new models would require mutating accepted ARCH-010 migration history;
- current Prisma/PostgreSQL constraints make the unresolved-transition uniqueness impossible without weakening it.

## Completion Report

### Status
Not started.

### Architect Review
Pending.
