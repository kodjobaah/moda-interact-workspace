---
id: ARCH-010-DATABASE-010
architecture_id: ARCH-010
title: Persist opt-in promotional campaigns, targeting and lifecycle audit
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 82
executor: copilot
claimed_at: 2026-09-12T06:03:25Z
attempt: 1
depends_on:
  - ARCH-010-DATABASE-009
enables:
  - ARCH-010-DATABASE-011
  - ARCH-010-ADMIN-004
created: 2026-09-12
updated: 2026-09-12
---

# ARCH-010-DATABASE-010: Persist opt-in promotional campaigns, targeting and lifecycle audit

## Objective

Add the durable campaign catalogue for optional first-release promotional recovery-credit offers. A campaign has exactly one scope (`GLOBAL`, `PLAN` or `SHOP`), a fixed credit quantity, a running window, immutable targeting after activation, and append-only lifecycle evidence for close/reopen/expiry changes.

This task **does not grant credits to merchants**. Merchant claim/selection and exact grant-lot reservation ownership belong to DATABASE-011.

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
scripts/validate-billing-policy-schema.mjs
scripts/generate-prisma-erd.mjs
docs/generated/prisma-erd.puml
```

Read the implemented `ARCH-010-DATABASE-009` migration/model first. Preserve existing `PromotionalCreditGrant` rows and enum values.

## Required schema

Add canonical enums equivalent to:

```text
PromotionTargetScope
  GLOBAL
  PLAN
  SHOP

PromotionCampaignStatus
  DRAFT
  ACTIVE
  CLOSED

PromotionCampaignEventType
  CREATED
  ACTIVATED
  CLOSED
  REOPENED
  EXPIRY_CHANGED
```

Add `billing.PromotionCampaign` with durable fields equivalent to:

```text
id
name
merchantDescription?
scope
quantity

targetPlanId?   -> BillingPlan
targetShopId?   -> Shop

startsAt
expiresAt
status

createdByPlatformAdminId -> PlatformAdmin
createdAt
updatedAt
version
```

Add DB constraints so:

```text
quantity > 0
expiresAt > startsAt

GLOBAL => targetPlanId NULL AND targetShopId NULL
PLAN   => targetPlanId NOT NULL AND targetShopId NULL
SHOP   => targetPlanId NULL AND targetShopId NOT NULL
```

`PLAN` must reference the durable `BillingPlan.id`; never persist a plan display name/handle as the targeting authority when the relation is available.

Add indexes supporting:

- running-campaign query by `status/startsAt/expiresAt`;
- PLAN target lookup;
- SHOP target lookup;
- Admin catalogue ordering by created/updated time.

Add `billing.PromotionCampaignEvent` containing at minimum:

```text
campaignId
kind
oldExpiresAt?
newExpiresAt?
platformAdminId
createdAt
```

The event table is audit evidence, not the source of current campaign state.

## Lifecycle invariants

Database structure must support the application rule that after first activation:

- scope is immutable;
- targetPlanId/targetShopId are immutable;
- quantity is immutable;
- close/reopen/expiry changes are audited.

Do not use a destructive migration to enforce application-history facts that cannot be proven from pre-existing rows. There are no pre-existing `PromotionCampaign` rows, so new-table constraints may be strict from creation.

A campaign may remain `ACTIVE` after wall-clock expiry; `EXPIRED` is derived from `expiresAt`, not a required persisted enum value.

## Migration/compatibility

- Do not mutate or reclassify any existing `PromotionalCreditGrant` row.
- Do not create campaigns from `campaignReference` strings.
- Do not create balances or merchant selections during migration.
- Do not alter purchased or lifetime-Free counters.

Update Prisma validation scripts and ERD output/validation used by this repository.

## Required tests / validation

At minimum prove schema/migration support for:

1. valid GLOBAL campaign;
2. valid PLAN campaign with exact BillingPlan relation;
3. valid SHOP campaign with exact Shop relation;
4. invalid mixed/no target shapes rejected;
5. non-positive quantity rejected;
6. expiry not after start rejected;
7. event campaign/admin foreign keys use deliberate delete behaviour;
8. existing promotional grants survive unchanged;
9. no migration grants promotional capacity.

Run repository-standard Prisma format/validate/generate, billing schema validation, ERD validation/generation where required, migration checks and `git diff --check`.

## Non-goals

Do not add merchant selection, grant usage counters, UsageReservation linkage, Admin UI, merchant UI, Background consumption, campaign messaging or a scheduler.

## Stop conditions

Stop and return to `moda_architect` if the current `BillingPlan`, `Shop`, `PlatformAdmin` or DATABASE-009 models differ materially from the inspected contract in a way that changes target identity or audit ownership.

## Completion Report

### Status
In Progress.

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
