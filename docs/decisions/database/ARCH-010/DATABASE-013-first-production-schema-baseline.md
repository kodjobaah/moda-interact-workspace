---
id: ARCH-010-DATABASE-013
architecture_id: ARCH-010
title: Materialise the clean ARCH-010 first-production database baseline
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 5
executor: copilot
claimed_at: '2026-09-12T13:57:00Z'
attempt: 2
depends_on:
- ARCH-010-DATABASE-001
- ARCH-010-DATABASE-002
- ARCH-010-DATABASE-003
- ARCH-010-DATABASE-004
- ARCH-010-DATABASE-005
- ARCH-010-DATABASE-006
- ARCH-010-DATABASE-007
- ARCH-010-DATABASE-008
- ARCH-010-DATABASE-009
- ARCH-010-DATABASE-010
- ARCH-010-DATABASE-011
enables:
- ARCH-010-ADMIN-002
- ARCH-010-ADMIN-004
- ARCH-010-ADMIN-006
- ARCH-010-ADMIN-008
- ARCH-010-ADMIN-010
- ARCH-010-BACKGROUND-001
- ARCH-010-BACKGROUND-002
- ARCH-010-BACKGROUND-003
- ARCH-010-BACKGROUND-006
- ARCH-010-BACKGROUND-007
- ARCH-010-BACKGROUND-009
- ARCH-010-BACKGROUND-010
- ARCH-010-BACKGROUND-011
- ARCH-010-BACKGROUND-012
- ARCH-010-BACKGROUND-014
- ARCH-010-BACKGROUND-016
- ARCH-010-BACKGROUND-019
- ARCH-010-SHOPIFY-003
- ARCH-010-SHOPIFY-004
- ARCH-010-SHOPIFY-006
- ARCH-010-SHOPIFY-007
- ARCH-010-SHOPIFY-009
- ARCH-010-SHOPIFY-017
- ARCH-010-SHOPIFY-018
- ARCH-010-SHOPIFY-021
- ARCH-010-SHOPIFY-022
- ARCH-010-SHOPIFY-023
- ARCH-010-SYSTEM-TEST-005
created: 2026-09-12
updated: '2026-09-12'
---

# ARCH-010-DATABASE-013: Materialise the clean ARCH-010 first-production database baseline

## Architecture

Read first:

```text
docs/architecture/ARCH-010-first-production-baseline.md
docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md
docs/architecture/ARCH-010-promotional-campaigns.md
```

ARCH-010 is explicitly `PRE-PRODUCTION / BREAKING ROLLOUT`. There is no production billing state to migrate. DATABASE-001 through DATABASE-011 remain immutable accepted task history; this task does not reopen or rewrite them.

`ARCH-010-DATABASE-012` is superseded. Its valid upgrade-economics target is part of this baseline task.

## Objective

Replace the accumulated development migration chain with one canonical first-production Prisma schema and one empty-database baseline migration representing the **final** ARCH-010 model.

The result of this task becomes the schema/migration starting point for future production migrations.

This is a rebaseline, not another compatibility migration.

## Context

The current development schema contains several constructs that existed only because ARCH-010 evolved incrementally while the product was not in production. Examples include:

```text
BillingPlan.freeLifetimeConversationAllowance
BillingAllowanceAdjustment
FREE_RECOVERY_LIFETIME
MIGRATION_RECONCILED
SubscriptionCancellationRequest and cancellation mode/status enums
RecoveryCreditPurchaseStatus.REFUNDED
negative-App-Event refund/correction fields and settlement mode
campaign-less direct PromotionalCreditGrant compatibility
ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS) compatibility accounting
```

Do not preserve those concepts in the first-production baseline.

Before editing, verify the implementation repository contains the architect-accepted DATABASE-001 through DATABASE-011 schema changes. If accepted work is missing from the implementation repository mainline/task baseline, STOP and report the exact missing accepted task/commit rather than reconstructing it from chat or silently omitting it.

## Scope

Repository-owned files include, as applicable:

```text
prisma/schema.prisma
prisma/migrations/**
prisma/seed.mjs
scripts/validate-*.mjs
docs/generated/prisma-erd.puml
package.json only when a focused baseline validator script is required
```

Required work:

1. preserve all unrelated accepted schema outside the ARCH-010 billing/lifecycle cleanup;
2. apply the exact final billing schema below;
3. incorporate the valid upgrade-economics schema from superseded DATABASE-012;
4. remove the old development migration directories;
5. create exactly one first-production migration from an empty database to the final Prisma schema;
6. make seed/validators/ERD describe only the final schema;
7. prove the baseline migration and Prisma schema agree.

## Out of Scope

Do not:

- implement Admin, Background or Shopify runtime behaviour;
- preserve development-only rows/backfills;
- connect to or reset an unverified production database;
- create compatibility aliases for removed enums/models/fields;
- add a second schema source of truth;
- redesign unrelated commerce, support, translation, WhatsApp or observability models.

## Requirements

### 1. Migration history becomes one baseline

Delete the accumulated development migration directories and create exactly one canonical baseline migration directory:

```text
prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql
```

Keep the Prisma migration lock file required by the repository.

The migration must be generated/validated as an **empty database -> final schema** migration. It must not contain compatibility UPDATE/backfill logic for development rows.

There must be no second ARCH-010 migration after the baseline in this task.

### 2. Lifetime Free entitlement is canonical and plan-independent

`EntitlementCounter` must contain:

```prisma
LIFETIME_FREE_RECOVERY_CREDITS
PURCHASED_RECOVERY_CREDITS
```

`PROMOTIONAL_RECOVERY_CREDITS` is removed because exact campaign grant lots are first-release promotion authority.

Remove entirely:

```text
BillingPlan.freeLifetimeConversationAllowance
BillingAllowanceAdjustment
Shop.allowanceAdjustments
PlatformAdmin.billingAllowanceAdjustments
BillingAuditAction.FREE_ALLOWANCE_ADJUSTED
FREE_RECOVERY_LIFETIME enum value/alias
```

Keep:

```prisma
PlatformBillingPolicy.lifetimeFreeRecoveryAllowance Int @default(5)
```

No alias, view, compatibility model or seed field may recreate the removed plan-owned/adjustment model.

### 3. BillingPeriod contains only real product close reasons

`BillingPeriodCloseReason` keeps real lifecycle reasons such as:

```text
RENEWED_SAME_PLAN
PLAN_CHANGED
CONTRACT_ENDED
```

Remove:

```text
MIGRATION_RECONCILED
```

Do not replace it with another migration-only close reason.

### 4. Remove local subscription-cancellation state machine

Remove entirely:

```text
SubscriptionCancellationRequest
SubscriptionCancellationMode
SubscriptionCancellationStatus
Shop.subscriptionCancellationRequests
PlatformAdmin.approvedSubscriptionCancellations
MerchantSupportMessage.subscriptionCancellationSourceRequests
BillingAuditAction.SUBSCRIPTION_CANCELLATION
```

No replacement local cancellation request/approval/executor table is created. Shopify provider lifecycle evidence on `Subscription` remains the cancellation/freeze reconciliation evidence.

### 5. Purchased-credit purchase/refund baseline

`RecoveryCreditPurchaseStatus` must not contain `REFUNDED`.

Keep provider/purchase lifecycle values required by the final runtime, including:

```text
PENDING_BILLING
ACTIVE
NEEDS_ATTENTION
CANCELLED
```

A completed partial refund leaves the purchase provider-confirmed status `ACTIVE` and records refunded quantity/history on the purchase/refund models.

Remove automatic negative-App-Event refund schema:

```text
RecoveryCreditRefundSettlementMode
RecoveryCreditRefund.settlementMode
RecoveryCreditRefund.correctionUsageEventId
RecoveryCreditRefund.correctionUsageEvent
UsageEvent.recoveryCreditRefundCorrectionEvent
```

The first-release `RecoveryCreditRefundStatus` set is exactly the states required by the human provider-settlement workflow:

```text
REQUESTED
PROVIDER_ACTION_REQUIRED
COMPLETED
REJECTED
WITHDRAWN
NEEDS_ATTENTION
```

Remove automatic worker retry/provider-call state that is not used by that human workflow, including fields whose only purpose is automated provider execution:

```text
attemptCount
nextAttemptAt
lastAttemptAt
processingStartedAt
providerErrorCode
providerResponseSummary
```

Retain the durable fields required by ADMIN-002/003:

```text
shop/purchase/source/sourceMessage/request identity
requested quantity
approved quantity and approving admin/time
holdAppliedAt
providerActionKind = REFUND | CREDIT
providerReference
providerAmount
providerCurrency
providerConfirmedByPlatformAdminId
providerConfirmedAt
creditsRefunded
completedAt
version/reason/timestamps
```

`RecoveryCreditProviderActionKind` remains `REFUND | CREDIT`.

### 6. Promotional campaigns use exact grant lots only

Preserve:

```text
PromotionCampaign
PromotionCampaignEvent
MerchantPromotionSelection
UsageReservation.promotionalCreditGrantId
```

`PromotionalCreditGrant` is campaign-owned first-release state. Its `campaignId` is required, not nullable.

The grant must preserve exact campaign/shop one-time allocation and usage history required by DATABASE-011:

```text
id
shopId
campaignId
quantity
reservedQuantity
committedQuantity
firstSelectedAt
lastSelectedAt
selectionCount
firstUsedAt
lastUsedAt
exhaustedAt
version
createdAt/updatedAt as required by the accepted model
```

Required integrity:

```text
UNIQUE(campaignId, shopId)
one current MerchantPromotionSelection row per Shop
selection cannot point to another Shop's grant
UsageReservation may point to the exact promotional grant
non-negative counters
reserved + committed <= quantity
```

Remove direct/campaign-less grant compatibility and its provenance-only fields when they exist solely for the old direct-grant model:

```text
PromotionalCreditGrantType
PromotionalCreditGrant.grantType
PromotionalCreditGrant.reason
PromotionalCreditGrant.campaignReference
PromotionalCreditGrant.platformAdminId
PlatformAdmin.promotionalCreditGrants
BillingAuditAction.PROMOTIONAL_CREDITS_GRANTED
```

Do not auto-create grants or selections in the baseline migration or seed.

Remove `ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)` compatibility accounting. Promotion spendability/accounting is exact-grant-lot state only.

### 7. Preserve final provider lifecycle and recovery-capacity state

Keep all accepted first-release state required for:

```text
Subscription current/pending projection
Subscription.nextReconcileAt
latest provider lifecycle state/id/time
FROZEN projection
Shop.reinstallPendingAt
BillingPeriod history and current pointer
BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)
CheckoutRecovery capacity-blocked reason/time
UsageReservation exact ownership
purchased-credit FIFO lot accounting
promotion campaign lifecycle/selection/grant history
```

Do not remove these merely because the migration history is being squashed.

### 8. Fold superseded DATABASE-012 into the baseline

Add:

```prisma
PlatformBillingPolicy.minimumUpgradePremiumBps Int @default(2000)
```

Enforce/validate:

```text
0 <= minimumUpgradePremiumBps <= 10000
```

Add explicit non-branching `BillingUpgradeEconomicsEdge`:

```text
id
lowerPlanId -> BillingPlan
higherPlanId -> BillingPlan
active
createdAt
updatedAt
```

Integrity:

```text
lowerPlanId != higherPlanId
one successor per lower plan
one predecessor per higher plan
plan deletion cannot silently destroy evidence
```

Add append-only `BillingEconomicsSnapshot` containing at minimum:

```text
id
billingPlanId
shopifyPlanHandleSnapshot
monthlyRecurringAmountMinor
currency
recoveryCreditPackEnabledSnapshot
recoveryCreditsPerPackSnapshot
shopifyRecoveryCreditPackEventHandleSnapshot
usagePricingSnapshot Json?
providerEvidence Json?
verifiedByPlatformAdminId
verificationReason
verifiedAt
createdAt
```

Use integer minor units and normalized 3-letter currency. Do not store tokens/secrets.

Add `BillingAuditAction.UPGRADE_ECONOMICS_EVALUATED`.

Do not add local BillingPlan price/rank authority and do not seed fake provider economics snapshots or infer plan edges from plan names.

### 9. Seed is first-production seed, not migration compatibility

Update `prisma/seed.mjs` so it:

- does not write `freeLifetimeConversationAllowance`;
- seeds/maintains the canonical platform lifetime default through `PlatformBillingPolicy`;
- includes the default `minimumUpgradePremiumBps = 2000` when creating policy;
- does not create allowance adjustments;
- does not create campaign-less promotional grants;
- does not create merchant promotion selections;
- does not create refund/cancellation compatibility rows;
- does not fabricate economics edges/snapshots.

Preserve unrelated existing seed behaviour.

### 10. Validators and ERD describe only the final baseline

Update/delete old validators so none assert the existence of removed compatibility constructs.

Add a focused baseline validator if needed. It must prove presence of final invariants and absence of all removed names.

Regenerate the Prisma ERD from the final schema.

## Work Items

- [x] Verify DATABASE-001 through DATABASE-011 accepted schema is integrated before rebaseline.
- [x] Apply the exact final schema removals/renames above.
- [x] Fold DATABASE-012 economics requirements into the schema.
- [x] Remove old development migration directories.
- [x] Create the single empty-database first-production baseline migration.
- [x] Update seed and deterministic schema validators.
- [x] Regenerate ERD.
- [x] Prove schema/migration drift is zero.
- [x] Prove removed compatibility names are absent from final schema/migration/seed/validators/ERD.

## Interfaces / Contracts

Database contracts consumed by other repositories after this task include:

```text
EntitlementCounter.LIFETIME_FREE_RECOVERY_CREDITS
ShopEntitlementCounter
BillingPeriod / BillingPeriodEntitlementCounter
RecoveryCreditPurchase / RecoveryCreditRefund
PromotionCampaign / PromotionalCreditGrant / MerchantPromotionSelection
UsageReservation exact purchase/promotion ownership
PlatformBillingPolicy including lifetimeFreeRecoveryAllowance and minimumUpgradePremiumBps
BillingUpgradeEconomicsEdge
BillingEconomicsSnapshot
```

There is deliberately no database compatibility contract for the removed development names.

## Dependencies

All DATABASE-001 through DATABASE-011 are Complete historical prerequisites.

DATABASE-012 is **not** a dependency because it is superseded; its valid target requirements are implemented directly here.

## Enables

This task unlocks the root baseline-conformance consumers:

```text
ARCH-010-ADMIN-010
ARCH-010-BACKGROUND-001
ARCH-010-BACKGROUND-011
ARCH-010-SHOPIFY-023
```

Other pending ARCH-010 tasks are gated directly or transitively by those roots and this final schema. `ARCH-010-BACKGROUND-015` is intentionally independent of DATABASE-013 because it owns provider I/O only and mutates no Prisma state.

## Acceptance Criteria

1. exactly one first-production migration exists after the migration lock file;
2. that migration creates the final schema from empty without development backfills;
3. Prisma schema and migration are drift-free;
4. `LIFETIME_FREE_RECOVERY_CREDITS` exists and `FREE_RECOVERY_LIFETIME` does not;
5. `BillingPlan.freeLifetimeConversationAllowance` does not exist;
6. `BillingAllowanceAdjustment` and all relations/audit action do not exist;
7. `MIGRATION_RECONCILED` does not exist;
8. local subscription cancellation request/mode/status schema does not exist;
9. `RecoveryCreditPurchaseStatus.REFUNDED` does not exist;
10. automatic negative-App-Event refund/correction schema does not exist;
11. human refund workflow fields/statuses remain sufficient for ADMIN-002/003;
12. `PromotionalCreditGrant.campaignId` is required;
13. campaign-less/direct promotional grant schema does not exist;
14. aggregate promotional `ShopEntitlementCounter` source is absent;
15. exact campaign grant reservation/selection integrity is present;
16. accepted BillingPeriod, freeze, reinstall, purchased-lot and queue-reconstruction durability remains present;
17. upgrade-economics policy/edges/snapshots/audit action from DATABASE-012 are present;
18. seed contains no compatibility data creation;
19. ERD matches final schema;
20. no unrelated schema is removed or redesigned.

## Validation

Inspect repository `package.json` before running scripts. At minimum run the actual declared equivalents of:

```text
npm run format
npm run validate
npm run prisma:generate
all retained focused schema validators
npm run erd:puml
git diff --check
```

Additionally validate the baseline migration against a disposable/local test PostgreSQL database when the repository/environment provides one:

```text
empty database
  -> migrate deploy baseline
  -> Prisma validate/generate
  -> no pending migration/drift
```

Run an explicit text check proving these strings are absent from final schema/migration/seed/validators/ERD:

```text
freeLifetimeConversationAllowance
BillingAllowanceAdjustment
FREE_RECOVERY_LIFETIME
MIGRATION_RECONCILED
SubscriptionCancellationRequest
SubscriptionCancellationMode
SubscriptionCancellationStatus
RecoveryCreditPurchaseStatus ... REFUNDED
CURRENT_CYCLE_APP_EVENT_CORRECTION
PROMOTIONAL_RECOVERY_CREDITS
PromotionalCreditGrantType
```

Do not report a destructive reset against any environment unless it was explicitly verified as disposable/local/development/test.

## Implementation Notes

Do not manufacture a chain of cleanup migrations. The required output is one baseline migration.

Do not preserve a development row merely because an earlier accepted migration created it. Preserve **product state semantics**, not pre-production migration history.

The implementation agent does not reopen or edit DATABASE-001 through DATABASE-011 task files.

## Completion Report

### Status
In Progress.

### Files Changed
- `prisma/schema.prisma`
- `prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql`
- `prisma/migrations/**` old development migration SQL removed; `migration_lock.toml` retained
- `prisma/seed.mjs`
- `scripts/validate-first-production-baseline.mjs`; obsolete compatibility validators removed
- `docs/generated/prisma-erd.puml`
- `package.json`

### Work Completed
- Materialised the final ARCH-010 first-production Prisma schema, including DATABASE-001 through DATABASE-011 accepted state and the valid DATABASE-012 economics requirements.
- Removed development-only cancellation, allowance-adjustment, legacy entitlement, refund automation, and campaign-less promotional compatibility constructs.
- Replaced the accumulated migration chain with exactly one empty-database baseline migration and retained the PostgreSQL migration lock.
- Updated first-production seed behavior and replaced obsolete focused validators with a final baseline invariant validator.
- Regenerated the ERD and normalized generator-produced trailing whitespace for clean repository validation.

### Validation Results
- Prerequisites: parent task records for DATABASE-001 through DATABASE-011 are all `status: complete`; implementation history reaches accepted DATABASE-011 commit `813626d`.
- `npm run format`: passed.
- `npm run validate`: passed.
- `npm run prisma:generate`: passed with Prisma Client `6.19.3`.
- `npm run test:first-production-baseline`: passed (`First-production baseline invariants passed.`).
- `npm run erd:puml`: passed; generated ERD then normalized; `git diff --check`: passed.
- `node --check prisma/seed.mjs`: passed; `node --check scripts/validate-first-production-baseline.mjs`: passed.
- Disposable local PostgreSQL database `moda_interact_arch010_database013_validation` at `localhost:5432`: `npm run migrate:deploy` applied `20260912000000_arch010_first_production_baseline`; `npm run status` reported `Database schema is up to date!`; corrected `prisma migrate diff --from-url ... --to-schema-datamodel ... --exit-code` reported `No difference detected.`
- Migration shape: exactly one migration directory and one `migration.sql`, plus `migration_lock.toml`; baseline contains no compatibility/backfill `UPDATE`, `INSERT`, or `DELETE` statements.
- Explicit removed-name scan across final schema, migration, seed, validators, and ERD returned no matches for the required removed compatibility names.

### Deviations
None.

### Assumptions
ARCH-010 billing/lifecycle state has not entered production.

### Unresolved Issues
None at task definition time.

### Architectural Concerns
Return any mismatch between accepted DATABASE-011 final schema and repository mainline to `moda_architect`; do not guess.

### Git / VCS
Implementation worktree: `moda-interact-workspace.worktrees/ARCH-010-DATABASE-013`; branch `task/ARCH-010-DATABASE-013`; commit `46a14c577dac0f0b2b59866b11c539f545b5aaab`; pushed to `origin/task/ARCH-010-DATABASE-013`. Parent report is being published on the mirrored parent branch `task/ARCH-010-DATABASE-013`.

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes

The clean-baseline direction is correct and the requested ARCH-010 compatibility removals are present. The task is not accepted because the baseline migration drops database-only integrity constraints that were part of the accepted schema before the rebaseline, and the absorbed DATABASE-012 economics snapshot contract is not fully materialised.

Prisma schema/migration drift being zero is not sufficient evidence for these constraints: several accepted PostgreSQL `CHECK` constraints are not represented in `schema.prisma`, so a schema-derived baseline can be drift-free while still weakening the durable database contract.

Do not create a new task. Reclaim this same task for Attempt 2 and make only the corrections below.

#### Correction 1 — restore retained database-only integrity in the single baseline migration

File:

```text
moda-interact-database/prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql
```

Keep exactly one migration directory. Do not restore the old migration chain and do not add a second migration.

Restore the following accepted PostgreSQL invariants because their underlying first-release product state still exists in the final baseline:

```text
Conversation_standalone_scope_invariant
BillingPlan_recovery_credit_pack_config
RecoveryCreditPurchase_creditsGranted_positive
CheckoutRecovery_admission_block_pair
PlatformBillingPolicy_lifetimeFreeRecoveryAllowance_non_negative
RecoveryCreditPurchase_lot_quantities_non_negative
RecoveryCreditPurchase_lot_quantities_within_grant
RecoveryCreditRefund_quantities_positive
BillingPeriodEntitlementCounter_grantedQuantity_non_negative
BillingPeriodEntitlementCounter_committedQuantity_non_negative
BillingPeriodEntitlementCounter_reservedQuantity_non_negative
BillingPeriodEntitlementCounter_forfeitedQuantity_non_negative
BillingPeriodEntitlementCounter_capacity
BillingPeriod_period_boundary
BillingPeriod_included_recovery_credits_non_negative
BillingPeriod_open_close_metadata_empty
PromotionCampaign_quantity_positive
PromotionCampaign_expiry_after_start
PromotionCampaign_scope_target_shape
MerchantPromotionSelection_version_non_negative
```

Use the accepted expressions from the pre-baseline migrations as the source, not reconstructed semantics from chat. They are still applicable to the final fields.

The new baseline already contains promotional-grant quantity checks, but it no longer enforces the accepted non-negative `PromotionalCreditGrant.version` invariant. Add:

```sql
ALTER TABLE "billing"."PromotionalCreditGrant"
ADD CONSTRAINT "PromotionalCreditGrant_nonnegativeVersion_check"
CHECK ("version" >= 0);
```

Do **not** restore the old `UsageReservation_counter_family_xor` unchanged. That two-family expression predates the first-production removal of aggregate promotional counters and would reject a valid promotion reservation.

Replace it with one final first-production source-shape constraint named:

```text
UsageReservation_capacity_source_shape
```

It must permit exactly these structural families:

```text
lifetime Free / purchased aggregate:
  counterId != NULL
  billingPeriodEntitlementCounterId == NULL
  promotionalCreditGrantId == NULL
  purchasedCreditPurchaseId may be NULL or non-NULL

paid included:
  counterId == NULL
  billingPeriodEntitlementCounterId != NULL
  purchasedCreditPurchaseId == NULL
  promotionalCreditGrantId == NULL

selected promotion:
  counterId == NULL
  billingPeriodEntitlementCounterId == NULL
  purchasedCreditPurchaseId == NULL
  promotionalCreditGrantId != NULL
```

Use this exact SQL shape:

```sql
ALTER TABLE "billing"."UsageReservation"
ADD CONSTRAINT "UsageReservation_capacity_source_shape"
CHECK (
  (
    "counterId" IS NOT NULL
    AND "billingPeriodEntitlementCounterId" IS NULL
    AND "promotionalCreditGrantId" IS NULL
  )
  OR (
    "counterId" IS NULL
    AND "billingPeriodEntitlementCounterId" IS NOT NULL
    AND "purchasedCreditPurchaseId" IS NULL
    AND "promotionalCreditGrantId" IS NULL
  )
  OR (
    "counterId" IS NULL
    AND "billingPeriodEntitlementCounterId" IS NULL
    AND "purchasedCreditPurchaseId" IS NULL
    AND "promotionalCreditGrantId" IS NOT NULL
  )
);
```

This deliberately allows a purchased reservation to carry both the aggregate purchased counter and `purchasedCreditPurchaseId`, while a promotion reservation is owned only by the exact campaign grant lot.

Do not add compatibility data/backfills. These are empty-database baseline constraints only.

#### Correction 2 — complete the absorbed DATABASE-012 economics snapshot contract

Files:

```text
moda-interact-database/prisma/schema.prisma
moda-interact-database/prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql
```

`BillingEconomicsSnapshot` currently indexes `createdAt`. DATABASE-012 required the latest verified evidence lookup by `verifiedAt`.

Replace:

```prisma
@@index([billingPlanId, createdAt])
@@index([verifiedByPlatformAdminId, createdAt])
```

with:

```prisma
@@index([billingPlanId, verifiedAt])
@@index([verifiedByPlatformAdminId, verifiedAt])
```

Regenerate/update the baseline SQL so the corresponding indexes use `verifiedAt`.

The task also requires a normalized three-letter currency, while `@db.Char(3)` enforces only length. Add a PostgreSQL constraint named:

```text
BillingEconomicsSnapshot_currency_normalized
```

with:

```sql
CHECK ("currency" ~ '^[A-Z]{3}$')
```

Do not add local `BillingPlan` price/rank authority. Do not seed economics edges or snapshots.

#### Correction 3 — make the final baseline validator prove the durable baseline, not only Prisma-visible shape

File:

```text
moda-interact-database/scripts/validate-first-production-baseline.mjs
```

Keep one consolidated first-production validator; do not restore obsolete compatibility validators.

Extend it to assert at minimum:

1. every retained CHECK constraint listed in Correction 1 is present in the baseline migration;
2. `UsageReservation_capacity_source_shape` is present and its SQL contains all four source columns;
3. `PromotionalCreditGrant_nonnegativeVersion_check` is present;
4. `BillingEconomicsSnapshot_currency_normalized` is present;
5. `BillingEconomicsSnapshot` uses `(billingPlanId, verifiedAt)` and `(verifiedByPlatformAdminId, verifiedAt)` indexes in both Prisma schema and migration;
6. `BillingEconomicsSnapshot` has no `updatedAt` field, preserving the append-only evidence shape;
7. the final refund model does not contain the removed automatic-settlement fields/status vocabulary;
8. the final promotional grant model has required `campaignId` and no direct-grant provenance fields;
9. the final cancellation request model/enums are absent;
10. the final lifetime-Free model uses only `LIFETIME_FREE_RECOVERY_CREDITS` and the platform policy default.

The validator may contain removed symbol names as test data. For Attempt 2, the explicit removed-name source scan must therefore treat that validator file as test-only evidence rather than interpreting its assertion strings as reintroduced runtime/schema compatibility.

#### Correction 4 — rerun baseline validation with explicit custom-constraint evidence

After the changes above, rerun the task's existing required validation:

```text
npm run format
npm run validate
npm run prisma:generate
npm run test:first-production-baseline
npm run erd:puml
git diff --check
node --check prisma/seed.mjs
node --check scripts/validate-first-production-baseline.mjs
```

Then use a newly created disposable/local PostgreSQL database only:

```text
empty database
  -> npm run migrate:deploy
  -> npm run status
  -> prisma migrate diff --from-url ... --to-schema-datamodel prisma/schema.prisma --exit-code
```

In addition to the Prisma drift result, query PostgreSQL `pg_constraint` (or an equivalent deterministic catalogue query) and record evidence that the restored custom CHECK constraint names exist. This extra catalogue check is required because Prisma drift does not prove the presence of PostgreSQL-only CHECK constraints.

Also record that:

```text
exactly one migration directory exists;
no baseline INSERT/UPDATE/DELETE compatibility DML exists;
removed compatibility models/enums/fields remain absent from schema/migration/seed/ERD;
no unrelated schema/model was removed.
```

### Reviewed Files

```text
docs/decisions/database/ARCH-010/DATABASE-013-first-production-schema-baseline.md
docs/architecture/ARCH-010-first-production-baseline.md
docs/decisions/database/ARCH-010/DATABASE-002-paid-period-included-credit-reservations.md
docs/decisions/database/ARCH-010/DATABASE-006-shop-lifetime-free-grant.md
docs/decisions/database/ARCH-010/DATABASE-007-purchased-credit-lot-partial-refund-accounting.md
docs/decisions/database/ARCH-010/DATABASE-010-promotion-campaign-catalogue-and-lifecycle.md
docs/decisions/database/ARCH-010/DATABASE-011-merchant-promotion-selection-and-grant-lots.md
docs/decisions/database/ARCH-010/DATABASE-012-upgrade-economics-policy-and-snapshots.md
moda-interact-database/prisma/schema.prisma
moda-interact-database/prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql
moda-interact-database/prisma/seed.mjs
moda-interact-database/scripts/validate-first-production-baseline.mjs
moda-interact-database/docs/generated/prisma-erd.puml
moda-interact-database/package.json
```

### Validation Reviewed

Architect independently confirmed from the supplied Attempt 1 snapshot:

```text
exactly one baseline migration directory exists;
no INSERT/UPDATE/DELETE compatibility DML exists in that migration;
required removed compatibility names are absent from schema/migration/seed/ERD;
node --check passes for seed and baseline validator;
current baseline validator passes;
```

Those checks do not cure the missing database-only constraints described above.

### Architecture Conformance

Partially conformant.

The final Prisma model and compatibility cleanup are directionally aligned with `ARCH-010-first-production-baseline.md`, but Acceptance Criteria 16, 17, 19 and 20 are not yet fully satisfied because accepted durable PostgreSQL integrity was weakened during migration squashing and the verified-economics snapshot contract is incomplete.

### Follow-up

Return this same task through the normal `moda_database` execution path for Attempt 2. Preserve `attempt: 1` until the next authorized claim increments it. Do not unblock DATABASE-013 dependants until the corrected task is architect-accepted Complete.
