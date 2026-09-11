---
id: ARCH-010-DATABASE-008
architecture_id: ARCH-010
title: Persist Shopify subscription freeze projection and lifecycle evidence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 19
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-010-BACKGROUND-016
  - ARCH-010-SHOPIFY-018
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-DATABASE-008: Persist Shopify subscription freeze projection and lifecycle evidence

## Objective

Add the minimum durable vocabulary needed to distinguish a temporary Shopify App Pricing freeze from cancellation and to retain the latest provider lifecycle evidence used by reconciliation.

This task is schema/migration only. It does not query Shopify and does not implement runtime transitions.

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
existing SubscriptionProjectionStatus
billing.Subscription
DATABASE-001 nextReconcileAt task definition
DATABASE-004 BillingPeriod lifecycle task definition
package.json validation scripts
```

## Required schema changes

### 1. Subscription projection status

Extend the existing enum exactly with:

```prisma
FROZEN
```

Do not rename/remove existing values:

```text
ACTIVE
TRIALING
NO_CONTRACT
UNMAPPED
SYNC_ERROR
```

`FROZEN` means Shopify has temporarily frozen the merchant's app subscription because of a provider/store billing lifecycle event. It is not cancellation and not a shop-installation status.

### 2. Provider lifecycle evidence

Add one provider-lifecycle enum equivalent to Shopify's persisted states:

```prisma
enum ProviderSubscriptionLifecycleState {
  CREATED
  UPDATED
  CANCELLATION_SCHEDULED
  CANCELED
  FROZEN
  UNFROZEN

  @@schema("billing")
}
```

Add nullable fields to `Subscription` equivalent to:

```prisma
lastProviderLifecycleState   ProviderSubscriptionLifecycleState?
lastProviderLifecycleEventId String?
lastProviderLifecycleEventAt DateTime?
```

Use repository naming conventions if needed, but keep one clear state/id/time triplet. Do not store arbitrary provider JSON.

These fields are evidence/audit inputs for reconciliation. `Subscription.status` remains the operational local projection.

## Migration rules

1. Existing Subscription rows keep their current `status` unchanged.
2. Do NOT infer/backfill `FROZEN` from `NO_CONTRACT`, `SYNC_ERROR`, historical BillingPeriods, or timestamps.
3. New lifecycle evidence fields are null for existing rows unless exact evidence already exists in a durable provider-event table (none is assumed).
4. Do not modify current plan, BillingPeriod, counters, pending plan state or cancellation flags.
5. Do not create a BillingPeriod.
6. Do not reset `nextReconcileAt`.

## Constraints

No uniqueness constraint is required on provider lifecycle event ID. The runtime must use event ID/time idempotently but historical Shopify event IDs are provider identifiers, not Moda business keys.

No new status index is required solely for `FROZEN`; DATABASE-001's scheduling/index work owns `nextReconcileAt`. Add an index only if the final Prisma query plan demonstrably requires it and document why.

## Required tests / validation

At minimum prove:

1. Prisma accepts `SubscriptionProjectionStatus.FROZEN`;
2. the provider lifecycle enum contains exactly the required states;
3. existing rows migrate without status changes;
4. lifecycle fields are nullable and preserve null for legacy rows;
5. no entitlement/counter/BillingPeriod data is changed by the migration;
6. generated Prisma client exposes the new enum/fields;
7. `prisma format`, `prisma validate`, repository-declared migration/schema tests and `git diff --check` pass.

## Non-goals

No Shopify API query, no Background transition, no merchant UI, no Admin UI, no billing-period rollover and no cancellation implementation.

## Stop conditions

STOP if another accepted/integrated migration has already introduced an equivalent frozen projection or provider lifecycle fields with different names. Report the exact overlap to `moda_architect`; do not create duplicate state.

## Completion Report

### Status
Not started.
