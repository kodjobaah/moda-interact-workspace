---
id: ARCH-011-DATABASE-001
architecture_id: ARCH-011
title: Persist ARCH-011 plan segments and upgrade transitions
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
- ARCH-010-DATABASE-013
enables:
- ARCH-011-DATABASE-002
- ARCH-011-BACKGROUND-002
- ARCH-011-SHOPIFY-001
- ARCH-011-ADMIN-002
created: 2026-09-14
updated: 2026-09-14
---

# ARCH-011-DATABASE-001: Persist ARCH-011 plan segments and upgrade transitions

## Objective
Add only the durable segment/upgrade-transition schema required by ARCH-011, forward from DATABASE-013. Do not implement topology triggers here.

## Authorized implementation surface
Edit exactly:

```text
prisma/schema.prisma
prisma/migrations/20260914010000_arch011_plan_segments_and_upgrade_transitions/migration.sql
scripts/validate-arch011-upgrade-transition-schema.mjs   # new
```

Regenerate only the existing generated ERD output through `npm run erd:puml` after schema/migration validation. Do not edit any ARCH-010 migration.

## Exact Prisma contract
Add enums with these exact names/literals:

```text
SubscriptionPlanTransitionOrigin = MERCHANT_REQUEST | PROVIDER_OBSERVED
SubscriptionPlanTransitionStatus = REQUESTED | PROVIDER_CONFIRMED | APPLIED | SUPERSEDED | FAILED | NEEDS_ATTENTION
SubscriptionPlanTransitionApplicationMode = SAME_CYCLE_PRORATED | NEW_PROVIDER_CYCLE_FULL_ALLOWANCE
```

Add `BillingPlanSegment` with fields exactly named:

```text
id String @id @default(cuid())
shopId String
billingPeriodId String
planId String?
shopifyPlanHandleSnapshot String
planNameSnapshot String
planKindSnapshot BillingPlanKind
includedAllowanceSnapshot Int
effectiveFrom DateTime
effectiveTo DateTime
sourceTransitionId String? @unique
createdAt DateTime @default(now())
updatedAt DateTime @updatedAt
```

Relations: `shop -> Shop onDelete:Cascade`; `billingPeriod -> BillingPeriod onDelete:Cascade`; `plan -> BillingPlan onDelete:SetNull`; `sourceTransition -> SubscriptionPlanTransition onDelete:SetNull`. Add reverse relations on those models. Add `@@unique([billingPeriodId, effectiveFrom])` and `@@index([billingPeriodId, effectiveFrom, effectiveTo])`.

Add `SubscriptionPlanTransition` with exact field names:

```text
id String @id @default(cuid())
shopId String
subscriptionId String
billingPeriodId String?
origin SubscriptionPlanTransitionOrigin
fromPlanId String
fromPlanHandleSnapshot String
fromPlanKindSnapshot BillingPlanKind
fromIncludedAllowanceSnapshot Int
requestedToPlanId String?
requestedToPlanHandleSnapshot String?
requestedToPlanKindSnapshot BillingPlanKind?
requestedToIncludedAllowanceSnapshot Int?
requestKey String? @unique
requestedAt DateTime?
providerConfirmedToPlanId String?
providerConfirmedToPlanHandleSnapshot String?
providerConfirmedToPlanKindSnapshot BillingPlanKind?
providerConfirmedToIncludedAllowanceSnapshot Int?
status SubscriptionPlanTransitionStatus
applicationMode SubscriptionPlanTransitionApplicationMode?
version Int @default(0)
providerAppIdSnapshot String? @db.VarChar(256)
providerShopIdSnapshot String? @db.VarChar(256)
providerCycleStartSnapshot DateTime?
providerCycleEndSnapshot DateTime?
providerEffectiveAt DateTime?
providerLifecycleEventId String? @unique
providerEvidence Json?
providerConfirmedAt DateTime?
targetEntitlementSnapshot Int?
alreadyGrantedSnapshot Int?
includedCreditDelta Int?
appliedAt DateTime?
supersededAt DateTime?
failedAt DateTime?
failureCode String? @db.VarChar(128)
createdAt DateTime @default(now())
updatedAt DateTime @updatedAt
```

Relations: Shop Cascade; Subscription Cascade; BillingPeriod SetNull; all plan relations SetNull **except `fromPlanId` must remain Restrict/non-null because it is the source identity**. Add reverse relations with explicit relation names where Prisma requires them. Add indexes `[subscriptionId,status,createdAt]`, `[billingPeriodId,status]`, `[providerConfirmedToPlanId,status]`.

Do not add any ARCH-011 `legacySubscriptionId*` or `providerSubscriptionIdSnapshot` field.

## Exact SQL constraints in the migration
Create named CHECK constraints:

```text
ck_billing_plan_segment_range
  effectiveFrom < effectiveTo
ck_billing_plan_segment_allowance_nonnegative
  includedAllowanceSnapshot >= 0
ck_subscription_plan_transition_from_allowance_nonnegative
ck_subscription_plan_transition_requested_allowance_nonnegative
ck_subscription_plan_transition_provider_allowance_nonnegative
ck_subscription_plan_transition_calculation_nonnegative
```

Create partial unique index exactly named:

```text
uq_subscription_plan_transition_one_unresolved
ON billing."SubscriptionPlanTransition"("subscriptionId")
WHERE status IN ('REQUESTED','PROVIDER_CONFIRMED','NEEDS_ATTENTION')
```

Create DB CHECK logic so `PROVIDER_OBSERVED` has all requested/requestKey fields null; `MERCHANT_REQUEST` + `REQUESTED` requires all requested snapshots/key/time; `SAME_CYCLE_PRORATED` + `APPLIED` requires billing period, provider target/app/shop/cycle/effective/event/calculation/applied evidence; `NEW_PROVIDER_CYCLE_FULL_ALLOWANCE` + `APPLIED` requires provider target/cycle/applied evidence and requires target/alreadyGranted/delta null.

## Required validator
Create `scripts/validate-arch011-upgrade-transition-schema.mjs`. It must read `prisma/schema.prisma` and the exact migration file and fail non-zero unless all exact enum literals, models, fields, named constraints and partial unique index above exist; it must also fail if the migration contains `legacySubscriptionIdSnapshot` or `providerSubscriptionIdSnapshot`.

## Work Items
- [ ] Add exact enums/models/relations/indexes to Prisma schema.
- [ ] Add exact forward migration directory/file.
- [ ] Add named CHECK constraints and unresolved-transition partial unique index.
- [ ] Add static schema/migration validator.
- [ ] Regenerate Prisma client and ERD source.

## Acceptance Criteria
- [ ] Migration is forward-only from DATABASE-013 and no ARCH-010 migration changed.
- [ ] Requested Scale and provider-confirmed Growth can coexist on one MERCHANT_REQUEST row.
- [ ] PROVIDER_OBSERVED requires no requested fields.
- [ ] One unresolved transition per subscription is database-enforced.
- [ ] SAME_CYCLE_PRORATED APPLIED cannot exist without complete provider/calculation evidence.
- [ ] No ARCH-011 legacy/provider subscription ID requirement exists.

## Validation
Run exactly from `moda-interact-database/`:

```text
npm run prisma:validate
npm run prisma:generate
npm run test:first-production-baseline
node scripts/validate-arch011-upgrade-transition-schema.mjs
npm run erd:puml
git diff --check
```

STOP on any failure; do not substitute another validation contract.

## Out of scope
Canonical topology DB trigger, provider calls, Shared algorithms, entitlement mutation, merchant/Admin UI.

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass: update the Completion Report, set task status to `review`, clear the active claim according to the normal launcher protocol, return control to `moda_architect`, and **STOP**. Do not start an enabled/follow-on task.
