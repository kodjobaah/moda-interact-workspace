# ARCH-011 Implementation Handoff

Date: 2026-09-13
Coordinator: `moda_architect`

## Architecture state

ARCH-011 is **Agreed / Ready for implementation** as a forward extension of ARCH-010.

Read in this order before implementing any ARCH-011 task:

1. [`ARCH-011-pro-rated-same-cycle-subscription-upgrades.md`](ARCH-011-pro-rated-same-cycle-subscription-upgrades.md)
2. the exact assigned `docs/decisions/<domain>/ARCH-011/<TASK>.md`
3. every dependency task listed in that task's YAML

The exact task file is the implementation contract. Do not implement from this handoff alone.

## Luna execution rule

Implementation agents may run on GPT-5.6 Luna. Every task is intentionally explicit.

```text
DO NOT infer missing billing rules.
DO NOT invent fallback provider timestamps or billing periods.
DO NOT infer plan direction from price, name, allowance, display order or UI order.
DO NOT treat adjacent topology edges as required merchant upgrade steps.
DO NOT use committed/reserved/remaining credits as proration inputs.
DO NOT replace an accepted ARCH-010 state machine with a simpler local implementation.
DO NOT cross repository ownership boundaries.
DO NOT weaken a STOP condition.
```

If a task precondition cannot be proven, stop and return deterministic evidence to `moda_architect`.

## Consolidated task count

```text
ARCH-011 tasks: 8
ready:           3
pending:         5
```

## Ready frontier

These three repository-owned tasks may start in parallel:

```text
ARCH-011-DATABASE-001
ARCH-011-SHARED-001
ARCH-011-BACKGROUND-001
```

`SHARED-002` is publication-only and starts only after `SHARED-001` is architect-accepted Complete.

## Consolidated ownership

```text
DATABASE-001
  complete ARCH-011 persistence model:
  BillingPlanSegment + SubscriptionPlanTransition + provider evidence fields
  + final database-enforced canonical tier topology

SHARED-001
  complete pure ARCH-011 domain contract:
  topology validator + direction classifier
  + whole-provider-period target entitlement/additional-grant calculator

SHARED-002
  package publication only

BACKGROUND-001
  exact Shopify plan-transition event/effective-time evidence only

BACKGROUND-002
  complete provider-confirmed upgrade lifecycle:
  same-cycle/new-cycle decision, segments, target grant, CAS/idempotency,
  repeated upgrades, rollover, delayed observations and deferred downgrades

SHOPIFY-001
  complete merchant feature:
  request/supersede upgrade, lower-plan deferral, top-up ambiguity gate,
  merchant billing UI and current-cycle history

ADMIN-001
  complete Admin feature:
  topology/economics configuration UI + transition/segment/entitlement audit
  DB + Shared remain topology authorities

SYSTEM-TEST-001
  one terminal/manual-gated lifecycle + concurrency + ARCH-010 regression suite
```

## Binding tier rule

Persisted adjacent chain example:

```text
Free -> Starter -> Growth -> Scale
```

The chain defines **order only**. Valid direct upgrades include:

```text
Free -> Growth
Free -> Scale
Starter -> Scale
```

Direction is determined only by transitive reachability in the validated active chain.

## Binding provider-cycle rule

```text
Shopify activeSubscription.currentBillingCycle
    = commercial/provider app-cycle authority

Moda BillingPeriod
    = exact local projection of that provider cycle
```

Never derive a cycle from store invoice dates, merchant click time, `createdAt + 30 days`, calendar month or worker observation time.

For Free -> paid:

```text
provider reports a new currentBillingCycle
  => NEW_PROVIDER_CYCLE_FULL_ALLOWANCE

provider preserves the current cycle and target becomes current inside it
  => SAME_CYCLE_PRORATED
```

Moda never chooses which provider behaviour occurred.

## Binding target-entitlement algorithm

Do **not** implement isolated `(newAllowance - oldAllowance) * remainingFraction` grants as the business algorithm.

For each provider-confirmed same-cycle upgrade:

1. construct the complete candidate `BillingPlanSegment` timeline from provider cycle start to provider cycle end;
2. require contiguous, non-overlapping segments covering the exact whole provider cycle;
3. use each segment's immutable included-allowance snapshot;
4. compute with integer/BigInt arithmetic:

```text
targetEntitlement = floor(
  SUM(segmentAllowance * segmentDurationMs)
  / totalProviderCycleDurationMs
)
```

5. read only:

```text
alreadyGranted = BillingPeriodEntitlementCounter.grantedQuantity
```

(or `0` when an existing provider Free cycle has no included counter before its first same-cycle paid upgrade);
6. require `targetEntitlement >= alreadyGranted`; otherwise fail closed;
7. calculate `additionalGrant = targetEntitlement - alreadyGranted`;
8. increment only `grantedQuantity += additionalGrant` using the accepted Serializable + versioned-CAS convention.

The following are **not** proration inputs:

```text
committedQuantity
reservedQuantity
forfeitedQuantity
current remaining/available credits
purchased credits
promotional credits
lifetime Free credits
```

Prior usage changes remaining availability, not the upgrade entitlement.

## Important ARCH-010 gates

Do not duplicate unfinished ARCH-010 capabilities just to unblock ARCH-011. Runtime tasks deliberately depend on the accepted ARCH-010 paths they extend, especially:

```text
ARCH-010-BACKGROUND-010
ARCH-010-SHOPIFY-014
ARCH-010-SHOPIFY-015
ARCH-010-ADMIN-009
```

## System-test rule

`ARCH-011-SYSTEM-TEST-001` is terminal/manual-gated. No implementation or publication task depends on it. It runs only after the user explicitly invokes the expensive integrated validation.
