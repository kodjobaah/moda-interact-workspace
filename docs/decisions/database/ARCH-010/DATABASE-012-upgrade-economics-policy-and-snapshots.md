---
id: ARCH-010-DATABASE-012
architecture_id: ARCH-010
title: Persist upgrade economics policy, plan edges and audited Shopify pricing snapshots
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 86
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-006
enables: []
created: 2026-09-12
updated: '2026-09-12'
superseded_by: ARCH-010-DATABASE-013
---

# ARCH-010-DATABASE-012: Persist upgrade economics policy, plan edges and audited Shopify pricing snapshots

## Supersession

**Superseded by `ARCH-010-DATABASE-013`.** ARCH-010 is now the clean first-production database baseline. The valid upgrade-economics target requirements in this task are absorbed into DATABASE-013; this task must not be implemented independently.


## Objective

Add durable **Admin-only commercial evidence** for the upgrade-economics guardrail without making Moda's `BillingPlan` monetary authority. Shopify App Pricing remains the charging authority; this task stores audited snapshots of the Shopify prices/configuration that a SUPER_ADMIN verified for commercial-policy validation.

The guardrail policy is:

```text
lower plan monthly recurring price
+ cheapest top-up route needed to reach the next plan's MONTHLY included capacity
>= next plan monthly recurring price * (1 + minimumUpgradePremium)
```

Default `minimumUpgradePremium = 20%` (`2000` basis points).

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
scripts/validate-billing-policy-schema.mjs
docs/generated/prisma-erd.puml
```

Read the implemented ARCH-010 DATABASE-006/009 migrations first. Do not reintroduce local merchant-facing plan price authority.

## Required schema contract

### Platform policy

Extend `PlatformBillingPolicy` with:

```prisma
minimumUpgradePremiumBps Int @default(2000)
```

Constraint/validation contract:

```text
0 <= minimumUpgradePremiumBps <= 10000
```

Do not use floating percentages in durable policy.

### Explicit upgrade edge

Add an explicit ladder relation rather than inferring order from names/prices:

```text
BillingUpgradeEconomicsEdge
  id
  lowerPlanId
  higherPlanId
  active
  createdAt
  updatedAt
```

Required integrity:

- `lowerPlanId != higherPlanId`;
- one active/declared successor per lower plan;
- one active/declared predecessor per higher plan for release 1 (no branching ladder);
- both references use durable `BillingPlan.id`;
- deleting a referenced plan must not silently destroy economics evidence; prefer Restrict.

This allows:

```text
Free -> Starter
Starter -> Growth
Growth -> Scale
```

without a local `rank` field.

### Audited Shopify economics snapshot

Add append-only `BillingEconomicsSnapshot` (exact naming may follow repository conventions) containing at minimum:

```text
id
billingPlanId
shopifyPlanHandleSnapshot
monthlyRecurringAmountMinor
currency
recoveryCreditPackEnabledSnapshot
recoveryCreditsPerPackSnapshot
shopifyRecoveryCreditPackEventHandleSnapshot
usagePricingSnapshot Json?       # normalized FIXED/GRADUATED/VOLUME evidence
providerEvidence Json?           # bounded non-secret evidence/audit representation
verifiedByPlatformAdminId
verificationReason
verifiedAt
createdAt
```

Rules:

- snapshots are append-only evidence; editing creates a new snapshot;
- monetary values are integer minor units after Admin verification;
- `currency` is a normalized 3-letter currency code;
- `usagePricingSnapshot` may represent:

```json
{ "mode": "FIXED", "currency": "GBP", "unitAmountMinor": 500 }
```

or:

```json
{
  "mode": "GRADUATED",
  "currency": "GBP",
  "tiers": [
    { "upTo": 10, "amountPerUnitMinor": 500, "flatAmountMinor": 0 },
    { "upTo": null, "amountPerUnitMinor": 400, "flatAmountMinor": 0 }
  ]
}
```

with `VOLUME` using the same tier shape;
- when packs are disabled, usage pricing may be null;
- snapshot must preserve the local plan handle and configured pack-meter handle at verification time so later drift is detectable;
- no Partner API token, secret, cookie or raw credential may be stored.

Add indexes for latest snapshot lookup by `(billingPlanId, verifiedAt)` and Admin audit lookup.

### Audit action

Add a specific billing-audit action equivalent to:

```text
UPGRADE_ECONOMICS_EVALUATED
```

`BillingAuditEvent` remains the audit sink; do not create a parallel generic audit table.

## Free/lifetime/promotion invariant

For upgrade economics only:

```text
FREE monthly included recovery allowance = 0
```

The one-time `FREE_RECOVERY_LIFETIME` grant is **not** recurring monthly capacity.

Never store or calculate economics from:

- promotional campaign credits;
- purchased-credit balances;
- lifetime-Free remaining balance;
- current merchant usage;
- refund state.

## Required migration tests/validation

At minimum prove:

1. default policy threshold is exactly 2000 bps;
2. invalid threshold bounds fail schema/action validation;
3. self-edge cannot be persisted;
4. a lower plan cannot have two successors;
5. a higher plan cannot have two predecessors;
6. snapshot is append-only by application contract;
7. snapshot supports FIXED/GRADUATED/VOLUME JSON evidence;
8. snapshot references exact BillingPlan and PlatformAdmin;
9. no existing BillingPlan monetary authority is introduced;
10. existing ARCH-010 data migrates without synthetic edges or fake monetary snapshots.

Run Prisma format/validate, migration validation, schema-policy scripts, ERD generation/check and `git diff --check`.

## Non-goals

Do not implement evaluator code, Admin UI, Shopify Partner API calls, merchant UI, top-up purchase, promotions, profitability guardrail or automatic price discovery.

## Stop conditions

Stop if the current schema already contains a competing monetary-plan authority or if adding the relation would require guessing an upgrade ladder from plan names/prices.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
