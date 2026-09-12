---
id: ARCH-010-ADMIN-008
architecture_id: ARCH-010
title: Manage verified Shopify economics evidence, upgrade edges and guardrail policy
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 88
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-ADMIN-001
- ARCH-010-ADMIN-010
enables:
- ARCH-010-ADMIN-009
created: 2026-09-12
updated: '2026-09-12'
---

# ARCH-010-ADMIN-008: Manage verified Shopify economics evidence, upgrade edges and guardrail policy

## Objective

Add SUPER_ADMIN controls for the durable evidence consumed by the upgrade-economics guardrail while preserving Shopify App Pricing as monetary authority.

This task records **verified Shopify economics evidence**; it does not create/change Shopify prices.

## Inspect before editing

```text
src/app/(protected)/billing/**
src/components/admin/billing-*.tsx
src/app/actions/billing-controls.ts
src/app/actions/billing-plan.ts
src/lib/admin/billing-control-validation.ts
src/lib/admin/billing-plan*.ts
tests/security/admin-billing-*.test.mjs
database/prisma/schema.prisma
```

## Required Admin capabilities

### A. Platform policy

Expose:

```text
Minimum stay+top-up premium above next-plan upgrade
```

bound to:

```text
PlatformBillingPolicy.minimumUpgradePremiumBps
```

Default display = 20.00% for 2000 bps.

Server validation: integer bps `0..10000`. Audit through existing `PLATFORM_POLICY_CHANGED`; no second policy subsystem.

### B. Explicit upgrade ladder

SUPER_ADMIN can configure exact edges using durable plan IDs, e.g.:

```text
Free -> Starter
Starter -> Growth
Growth -> Scale
```

Do not infer next plan from name, price or creation order.

Server-side reject:

- self-edge;
- duplicate lower successor;
- duplicate higher predecessor;
- missing/inactive plan IDs where current conventions require active mappings.

### C. Record Shopify economics snapshot

Provide a bounded form/action to record the exact Shopify Partner Dashboard/App Pricing evidence verified by the SUPER_ADMIN:

```text
billingPlanId
shopifyPlanHandleSnapshot
monthlyRecurringAmountMinor
currency
recoveryCreditPackEnabledSnapshot
recoveryCreditsPerPackSnapshot
shopifyRecoveryCreditPackEventHandleSnapshot
usagePricingSnapshot
verificationReason
```

`usagePricingSnapshot` UI may use explicit fields rather than raw JSON, but server output must normalize to the DATABASE-013 shape.

Supported pricing:

```text
FIXED
GRADUATED
VOLUME
```

For tier modes, allow ordered tiers with:

```text
upTo?                 # final tier null/open-ended
amountPerUnitMinor
flatAmountMinor
```

The UI must label this evidence clearly:

> Verified Shopify App Pricing economics used by Moda's Admin guardrail. Shopify remains the charging authority.

Do not claim the snapshot itself changes merchant pricing.

### D. Drift checks

Before storing the snapshot, re-read local `BillingPlan` and require:

- exact `shopifyPlanHandle` match;
- pack-enabled flag/pack size match the local mapping;
- exact local pack-meter handle when packs enabled;
- no pack-pricing evidence when packs disabled unless retained as historical evidence outside the active snapshot flow.

Do not call Shopify Partner API in this task unless an already-approved Admin connector/service exists. Manual verification against Partner Dashboard is acceptable and must be audited.

## Required tests

Implement integration scenarios 43–47 plus snapshot-management portions of 61–64 from:

```text
docs/contracts/ARCH-010-upgrade-economics-guardrail-test-matrix.md
```

Also prove:

1. only SUPER_ADMIN can mutate threshold/edges/snapshots;
2. threshold before/after audit is durable;
3. snapshot creation is append-only;
4. existing snapshots cannot be silently overwritten;
5. normalized tiers reject malformed/non-open-ended configuration;
6. snapshot contains no secret/token fields;
7. no Shopify mutation/API call is introduced;
8. plan catalogue still does not own monetary price fields.

## Non-goals

Do not implement the guardrail calculation (ADMIN-007), hard enforcement (ADMIN-009), automatic Partner API price discovery, merchant UI, profitability checks or provider price changes.

## Stop conditions

Stop if DATABASE-013 is unavailable or if implementation would require putting monthly/top-up money columns back on `BillingPlan`.

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
