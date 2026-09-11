---
id: ARCH-010-DATABASE-004
architecture_id: ARCH-010
title: Strengthen recurring App Pricing BillingPeriod ownership and close/open lifecycle integrity
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 45
executor: copilot
claimed_at: 2026-09-11T23:41:32Z
attempt: 2
depends_on:
  - ARCH-010-DATABASE-002
enables:
  - ARCH-010-BACKGROUND-001
  - ARCH-010-BACKGROUND-003
  - ARCH-010-BACKGROUND-007
  - ARCH-010-BACKGROUND-010
  - ARCH-010-BACKGROUND-012
  - ARCH-010-SHOPIFY-002
  - ARCH-010-SHOPIFY-003
  - ARCH-010-SHOPIFY-007
  - ARCH-010-SHOPIFY-009
created: 2026-09-11
updated: 2026-09-11T23:43:19Z
---

# ARCH-010-DATABASE-004: Strengthen BillingPeriod ownership and close/open lifecycle integrity

## Objective

Make BillingPeriod a durable child of the shop's one Subscription for every exact Shopify App Pricing monthly billing cycle that Moda must reconcile, preserve historical periods after renewal, snapshot the mapped plan governing every newly-created Free or Paid period, snapshot included recovery allowance only where one actually exists, and enforce that a Subscription cannot have two OPEN periods.

This task provides database integrity only. It does not execute rollover or call Shopify.

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
scripts/validate-billing-lifecycle-schema.mjs
scripts/validate-recovery-credit-pack-schema.mjs
scripts/generate-erd.mjs
package.json
docs/generated/prisma-erd.puml
```

Read:

```text
docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md
ARCH-010-DATABASE-002 implementation/task result
```

Use the integrated DATABASE-002 model as authoritative if exact relation names differ from the portable definition.

## Current schema facts to correct

The inspected baseline has:

```prisma
model Subscription {
  shopId          String @unique
  billingPeriodId String?
  billingPeriod   BillingPeriod?
}

model BillingPeriod {
  id            String @id
  shopId        String
  periodStart   DateTime
  periodEnd     DateTime
  status        BillingPeriodStatus
  subscriptions Subscription[]
  usageEvents   UsageEvent[]

  @@unique([shopId, periodStart, periodEnd])
}
```

Current reconciliation can create a newly-observed OPEN period without closing the previous OPEN period. The migration must normalize this before adding the new one-OPEN-period invariant.

## Required enum

Add an enum equivalent to:

```prisma
enum BillingPeriodCloseReason {
  RENEWED_SAME_PLAN
  PLAN_CHANGED
  CONTRACT_ENDED
  MIGRATION_RECONCILED

  @@schema("billing")
}
```

`PLAN_CHANGED` and `CONTRACT_ENDED` are schema vocabulary for later ARCH-010 transitions. This task must not implement those transitions.

Add a release reason enum or equivalent durable field that supports at minimum:

```prisma
enum UsageReservationReleaseReason {
  PERIOD_CLOSED

  @@schema("billing")
}
```

The field on `UsageReservation` must be nullable so existing Free/purchased reservation semantics remain compatible. Do not retroactively invent release reasons for existing rows.

## Subscription -> BillingPeriod ownership

Keep `Subscription.billingPeriodId` as the current-period pointer for backwards compatibility during ARCH-010.

Add a second, explicit ownership relation so one Subscription owns many BillingPeriods.

Conceptual target:

```prisma
model Subscription {
  billingPeriodId String?
  billingPeriod   BillingPeriod? @relation("CurrentSubscriptionBillingPeriod", ...)

  billingPeriods BillingPeriod[] @relation("SubscriptionBillingPeriods")
}

model BillingPeriod {
  subscriptionId String
  subscription   Subscription @relation("SubscriptionBillingPeriods", fields: [subscriptionId], references: [id], onDelete: Restrict)

  currentForSubscriptions Subscription[] @relation("CurrentSubscriptionBillingPeriod")
}
```

Use Prisma-valid relation names. Do not create a second Subscription record per billing period.

### Backfill subscriptionId

Because `Subscription.shopId` is unique, backfill each existing BillingPeriod by joining its `shopId` to that shop's durable Subscription.

Migration requirements:

1. add `subscriptionId` nullable;
2. backfill from `billing.Subscription.shopId`;
3. verify every BillingPeriod has exactly one matching Subscription;
4. if any BillingPeriod cannot be mapped unambiguously, fail/stop migration rather than guessing;
5. make `subscriptionId` NOT NULL only after successful verification;
6. add index `(subscriptionId, periodStart, periodEnd)`.

Do not delete historical periods.

## Period plan/allowance snapshot fields

Add nullable snapshot fields for historical compatibility:

```text
planId                              String?
shopifyPlanHandleSnapshot           String?
planNameSnapshot                    String?
planKindSnapshot                    BillingPlanKind?
includedRecoveryCreditsGranted      Int?
```

Add `planId -> BillingPlan` with `onDelete: SetNull` and an inverse relation on BillingPlan.

New Paid periods created after ARCH-010 must populate all five fields and set `includedRecoveryCreditsGranted` to the configured Paid monthly allowance.

New Free periods created after ARCH-010 must populate `planId`, `shopifyPlanHandleSnapshot`, `planNameSnapshot` and `planKindSnapshot = FREE`, and MUST set `includedRecoveryCreditsGranted = null`. A Free provider BillingPeriod exists to track Shopify's monthly commercial/usage-meter cycle; it MUST NOT create or imply a monthly Free recovery allowance. This schema task must not fabricate plan identity for historical CLOSED periods where the exact plan cannot be proven.

For the one current OPEN period pointed to by `Subscription.billingPeriodId`, the migration may backfill plan snapshot fields from the current Subscription/BillingPlan only when that identity is exact and unambiguous.

Do not copy today's plan onto every historical period.

## Close metadata

Add:

```text
closedAt    DateTime?
closeReason BillingPeriodCloseReason?
```

OPEN periods keep both null.

New ARCH-010 close transitions must write both fields. Historical periods may remain null unless the migration itself normalizes an orphaned OPEN row as described below.

## Normalize multiple legacy OPEN periods

Before adding the one-OPEN-period uniqueness rule, normalize the current baseline safely.

For each Subscription:

1. read `Subscription.billingPeriodId`;
2. if it points at one OPEN period, that row remains OPEN;
3. every other OPEN period owned by that same Subscription is changed to:

```text
status      = CLOSED
closedAt    = periodEnd
closeReason = MIGRATION_RECONCILED
```

4. if multiple OPEN periods exist and `billingPeriodId` is null, invalid, or does not identify one unambiguous current row, stop the migration and report the affected shop/subscription IDs. Do not pick the latest row heuristically.

If a Subscription has zero OPEN periods, do not fabricate one.


## Free-plan provider BillingPeriod invariant

A mapped active Free plan may have a Shopify monthly billing cycle even though its Moda recovery entitlement is lifetime. This distinction is mandatory when the Free Shopify App Pricing plan carries the recovery-credit-pack usage meter.

Database semantics:

```text
Free BillingPeriod
  = Shopify commercial / App Event billing-cycle record
  != Free recovery entitlement reset
```

For a Free BillingPeriod:

- `BillingPeriodEntitlementCounter(INCLUDED_RECOVERY_CREDITS)` MUST NOT be created;
- `includedRecoveryCreditsGranted` MUST be null;
- `FREE_RECOVERY_LIFETIME` remains the shop-level lifetime counter and is never reset by Free period creation/rollover;
- purchased lifetime credits are unchanged;
- UsageEvents for `RECOVERY_CREDIT_PACK_PURCHASE` may reference the exact current Free BillingPeriod so App Event reporting/reconciliation is cycle-scoped exactly like Paid pack purchases.

The migration MUST NOT fabricate a missing current Free BillingPeriod from plan configuration alone. It may backfill Free period plan snapshot fields only when the existing `Subscription.billingPeriodId` and exact current period are already unambiguous. Runtime reconciliation tasks own creation of a missing provider-confirmed Free period.

## Backfill current paid-period entitlement without resetting merchants

Existing ARCH-007/008 paid merchants may already have a current `Subscription.billingPeriodId` and normal paid `RECOVERY_CONVERSATION` UsageEvents but no `BillingPeriodEntitlementCounter`, because DATABASE-002 introduces that model after those usages were recorded.

For each current OPEN period whose current Subscription maps exactly to an active `PAID_METERED` BillingPlan:

1. require a non-null non-negative safe-integer `includedRecoveryConversationAllowance`;
2. populate current-period plan snapshot fields from that exact current BillingPlan;
3. calculate the existing **net normal paid recovery usage** for that BillingPeriod using the same scope the pre-ARCH-010 effective policy used:

```text
shopId = subscription.shopId
billingPeriodId = current BillingPeriod.id
metric = RECOVERY_CONVERSATION
shopifyEventHandle = current plan.shopifyUsageEventHandle
sum(quantity)
```

4. require the resulting quantity to be a non-negative integer; do not silently clamp corrupted/ambiguous data;
5. if the unique `INCLUDED_RECOVERY_CREDITS` period counter is absent, create it with:

```text
grantedQuantity   = includedRecoveryConversationAllowance
committedQuantity = min(existingNormalPaidUsage, includedRecoveryConversationAllowance)
reservedQuantity  = 0
forfeitedQuantity = 0
version            = 0
```

6. if a counter already exists, validate it and do not reset any quantity;
7. legacy normal paid usage beyond the configured allowance, if present in pre-ARCH-010 data, is migration history only and must **not** make `committedQuantity` exceed the grant or imply that ARCH-010 permits future overage.

Purchased-credit recoveries are not counted in this backfill because the accepted ARCH-007 model does not emit the normal paid recovery meter event for purchased-credit-funded recoveries.

This backfill prevents deployment from granting a fresh current-period allowance to an already-using paid merchant.

If the current period's usage cannot be scoped unambiguously to the current plan/meter, stop migration rather than guessing.

## One OPEN period invariant

Prisma cannot express a partial unique index. Add raw PostgreSQL migration SQL equivalent to:

```sql
CREATE UNIQUE INDEX ...
ON "billing"."BillingPeriod" ("subscriptionId")
WHERE "status" = 'OPEN';
```

Use the exact generated enum/storage syntax and quote names correctly.

Preserve the existing exact period uniqueness (`shopId`, `periodStart`, `periodEnd`) unless the generated/integrated schema already has a stricter equivalent. Do not weaken it.

## Period boundary integrity

Add/retain checks where practical:

```text
periodStart < periodEnd
includedRecoveryCreditsGranted IS NULL OR includedRecoveryCreditsGranted >= 0
```

Do not add a CHECK that requires plan snapshot fields on every legacy CLOSED period.

## UsageReservation period-close support

Add nullable:

```text
releaseReason UsageReservationReleaseReason?
```

Do not change the DATABASE-002 XOR rule: exactly one of shop-level `counterId` or period-level `billingPeriodEntitlementCounterId` remains required.

No migration should change existing reservation status, quantity, counter ownership or sourceKey.

## ERD / validator requirements

Update repository-owned validators/ERD generation narrowly.

Required assertions include:

1. BillingPeriod has non-null `subscriptionId` ownership relation;
2. Subscription retains one current `billingPeriodId` pointer and has historical `billingPeriods` relation;
3. plan snapshot fields exist and are nullable for legacy history;
4. close metadata exists;
5. releaseReason exists and is nullable;
6. migration backfills subscriptionId before NOT NULL;
7. migration normalizes extra legacy OPEN rows only using the current pointer;
8. partial unique one-OPEN-period index exists;
9. exact period uniqueness remains;
10. periodStart < periodEnd integrity exists;
11. current OPEN paid periods receive snapshot/counter backfill without resetting consumed allowance;
12. backfill committed quantity equals `min(existing normal paid recovery usage, configured included allowance)`;
13. invalid/ambiguous current usage causes migration failure rather than a guessed reset;
14. DATABASE-002 period entitlement counter/XOR/quantity constraints remain unchanged.

## Validation

Run exactly:

```bash
npm run format
npm run validate
npm run prisma:generate
npm run test:recovery-credit-packs
npm run test:billing-lifecycle
npm run erd:puml
git diff --check
```

If the migration validator uses a shadow/test database, follow the repository's existing documented command only; do not invent a destructive production migration test.

## Non-goals

Do not implement:

- rollover worker/service;
- BullMQ;
- Shopify calls;
- merchant UI;
- upgrade/downgrade/cancellation execution;
- top-up refund lot accounting;
- promotional-credit model (owned separately by DATABASE-009);
- SubscriptionEvent history beyond BillingPeriod history;
- Admin changes.

## Stop conditions

STOP and return to `moda_architect` if:

- any existing BillingPeriod cannot be mapped to exactly one Subscription;
- current paid-period usage cannot be scoped to one exact plan/meter for entitlement backfill;
- multiple OPEN rows exist without an unambiguous current pointer;
- the integrated schema already contains a conflicting BillingPeriod ownership/history model;
- adding the partial unique index would require guessing historical current state;
- DATABASE-002 reservation/counter constraints would need destructive rewrite.

## Work Items

- [x] Extend the integrated Prisma schema with Subscription-owned BillingPeriod history, nullable plan/allowance snapshots, close metadata, and nullable reservation release reasons.
- [x] Add the guarded lifecycle migration with deterministic Subscription backfill, pointer-based legacy OPEN normalization, exact current-plan snapshots, paid usage/counter backfill, period integrity checks, and the partial unique OPEN-period index.
- [x] Preserve the DATABASE-002 period-counter/XOR/quantity constraints and update the repository billing lifecycle validator and generated ERD.
- [x] Run the complete declared validation sequence and publish both mirrored task branches.

## Acceptance Criteria

- [x] BillingPeriod is a non-null child of exactly one Subscription while Subscription retains its current-period pointer and historical relation.
- [x] Historical plan snapshots remain nullable; exact current Free/Paid plans are snapshotted without creating a Free monthly recovery allowance.
- [x] Legacy extra OPEN periods are closed only when the Subscription current pointer unambiguously selects the surviving OPEN row; ambiguous state raises a migration error.
- [x] Current paid periods backfill scoped normal usage with `committedQuantity = min(existing usage, configured allowance)` and preserve existing valid counter quantities; invalid or ambiguous usage raises a migration error.
- [x] PostgreSQL enforces one OPEN period per Subscription, valid period boundaries, non-negative included allowance, and OPEN close-metadata nullability.
- [x] UsageReservation release reason is nullable and the DATABASE-002 XOR/counter constraints remain unchanged.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `prisma/schema.prisma`
- `prisma/migrations/20260911200000_add_billing_period_lifecycle_history/migration.sql`
- `scripts/validate-billing-lifecycle-schema.mjs`
- `docs/generated/prisma-erd.puml`

### Work Completed
- Attempt 2 correction checklist: Correction 1 implemented in `prisma/migrations/20260911200000_add_billing_period_lifecycle_history/migration.sql` with an explicit `BEGIN`/`COMMIT` envelope; `scripts/validate-billing-lifecycle-schema.mjs` asserts both transaction boundaries.
- Attempt 2 correction checklist: Correction 2 implemented in the same migration by requiring the pointer-selected BillingPeriod to be owned and `OPEN` before closing any other OPEN row; the validator asserts the pointer, ownership, and OPEN survivor predicates.
- Added `BillingPeriodCloseReason` and nullable `UsageReservationReleaseReason` vocabulary.
- Added explicit `Subscription.billingPeriods` ownership, preserved `Subscription.billingPeriodId` as the current pointer, and added the inverse current/history relations.
- Added nullable BillingPeriod plan identity/handle/name/kind and included-credit snapshots, `closedAt`, `closeReason`, ownership/indexes, and BillingPlan inverse relation.
- Added a transactional migration that backfills every period through the unique shop Subscription, fails on unmappable pointers or ambiguous multiple OPEN rows, closes only non-current legacy OPEN rows with `MIGRATION_RECONCILED`, and does not fabricate periods or historical plan identity.
- Added exact current-plan snapshots and paid-period counter backfill using scoped `RECOVERY_CONVERSATION` usage and the configured meter handle; existing valid counters are preserved and invalid/mismatched state fails rather than resetting.
- Added the one-OPEN-period partial unique index, period boundary/included allowance checks, and OPEN close-metadata check. Existing DATABASE-002 reservation/counter constraints remain additive and unchanged.
- Regenerated the PlantUML ERD and extended the billing lifecycle validator with the ownership, migration-safety, snapshot, close/release, partial-index, and paid-counter assertions.

### Validation Results
- `npm ci` — passed in the isolated implementation worktree; npm reported three existing high-severity audit findings.
- `npm run format` — passed.
- `npm run validate` — passed.
- `npm run prisma:generate` — passed with Prisma Client 6.19.3.
- `npm run test:recovery-credit-packs` — passed.
- `npm run test:billing-lifecycle` — passed.
- `npm run erd:puml` — passed; generated ERD contains BillingPeriod ownership, snapshots, close metadata, and release reason.
- `git diff --check` — passed after removing four deterministic trailing spaces emitted by the ERD generator.
- Focused rework validation — direct lifecycle validator passed after the correction assertions were added; the full declared sequence also passed in the isolated implementation worktree.
- No migration was applied to a database; no destructive or production migration test was run.

### Git / VCS

Task branch: `task/ARCH-010-DATABASE-004`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-004`
  parent branch: `task/ARCH-010-DATABASE-004`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-004`
  implementation branch: `task/ARCH-010-DATABASE-004`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: already-current
  parent origin/main incorporated: merge commit `aa331a9`
  implementation remote task branch fast-forwarded: already-current
  implementation origin/main incorporated: merge commit `3c90780`

Implementation repository:
  repository: `moda-interact-database`
  commit: `835e777`
  remote branch: `origin/task/ARCH-010-DATABASE-004`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/database/ARCH-010/DATABASE-004-billing-period-lifecycle-history.md`
  claim commit: `763b1c9`
  review-report commit: `202bbdf`
  remote branch: `origin/task/ARCH-010-DATABASE-004`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Deviations

None.

### Assumptions

- The integrated DATABASE-002 period counter model and its migration constraints are authoritative; this task adds only lifecycle ownership/backfill behavior around them.
- A unique `Subscription.shopId` makes each existing BillingPeriod-to-Subscription backfill deterministic.

### Unresolved Issues

None.

### Architectural Concerns

None.

### Architect Review

Pending.

#### Attempt 1 — Changes Requested

The schema direction, current-plan snapshot model, paid-period usage/counter backfill,
DATABASE-002 preservation, ERD and workflow evidence are substantially correct.
Two migration-safety defects must be corrected before acceptance.

##### Accepted portions — do not redesign

Architect review verified:

- `BillingPeriodCloseReason` contains exactly the required four lifecycle reasons;
- nullable `UsageReservationReleaseReason.PERIOD_CLOSED` is additive and does not
  rewrite existing reservations;
- `Subscription.billingPeriodId` remains the backwards-compatible current pointer;
- `Subscription.billingPeriods` and non-null `BillingPeriod.subscriptionId`
  implement durable one-Subscription-to-many-BillingPeriods history;
- `BillingPeriod.planId` uses `onDelete: SetNull`, with the required nullable plan
  handle/name/kind/included-credit snapshots;
- close metadata is nullable for historical compatibility;
- exact `(shopId, periodStart, periodEnd)` uniqueness is preserved;
- `(subscriptionId, periodStart, periodEnd)` access indexing is added;
- the partial unique index enforces at most one OPEN BillingPeriod per Subscription;
- period boundary, non-negative included allowance and OPEN-close-metadata checks
  are present;
- the migration backfills `subscriptionId` from unique `Subscription.shopId` and
  verifies unmapped BillingPeriods before making ownership NOT NULL;
- current-period plan snapshots are not copied onto every historical period;
- current active `PAID_METERED` periods scope normal recovery usage by shop,
  BillingPeriod, metric and exact current usage-event handle;
- invalid negative/fractional usage and usage under another/null meter handle fail
  rather than being clamped or guessed;
- absent included-credit counters are seeded with
  `committedQuantity = LEAST(existing usage, allowance)`;
- existing valid period counters are preserved rather than reset;
- Free current periods receive no included monthly allowance snapshot from this
  migration;
- DATABASE-002 counter/XOR/quantity constraints are not destructively rewritten;
- all declared static/schema validation commands are reported as passing;
- the canonical parent/implementation worktrees, negative isolation assertions and
  all four start-of-attempt synchronization outcomes are durably recorded;
- implementation commit `7d20c4a` is the reviewed Attempt 1 head;
- external handoff identifies final parent report commit `941ddca`.

Do not churn those accepted surfaces.

##### Correction 1 — make the guarded migration atomic

The Completion Report describes the migration as transactional, but the submitted
migration has no explicit transaction envelope.

It performs schema/data mutations before later `RAISE EXCEPTION` stop guards,
including:

```sql
CREATE TYPE ...
ALTER TABLE ...
UPDATE "billing"."BillingPeriod" ...
```

and later can fail for:

```text
unmapped BillingPeriod ownership
invalid current pointer
ambiguous multiple OPEN periods
invalid paid allowance
missing/mismatched paid usage meter
invalid paid usage totals
invalid existing entitlement counters
```

The task contract requires these states to **fail/stop rather than leave a guessed
or partially converted lifecycle model**.

Wrap the migration in an explicit PostgreSQL transaction:

```sql
BEGIN;

... complete guarded migration ...

COMMIT;
```

so any guard failure rolls back all DDL/DML from this migration.

Extend `validate-billing-lifecycle-schema.mjs` to assert that this lifecycle
migration has the transaction envelope. Do not rely on deployment tooling to make
an unwrapped migration atomic.

##### Correction 2 — do not close a lone OPEN period when the pointer is not OPEN

The submitted normalization currently performs:

```sql
UPDATE "billing"."BillingPeriod" AS period
...
WHERE period."subscriptionId" = subscription."id"
  AND period."status" = 'OPEN'
  AND period."id" <> subscription."billingPeriodId";
```

The preceding ambiguity guard only rejects an invalid/non-OPEN pointer when a
Subscription has **more than one** OPEN row.

Therefore this valid legacy shape reaches the UPDATE:

```text
Subscription.billingPeriodId -> owned historical CLOSED period
BillingPeriods:
  old-period   CLOSED
  current-ish  OPEN       <-- only OPEN row
```

and the UPDATE closes `current-ish`, leaving zero OPEN rows while the current
pointer still references the old CLOSED row.

That violates the task contract:

```text
normalize extra legacy OPEN rows only using the current pointer
```

and the acceptance criterion that extra OPEN periods are closed only when the
pointer unambiguously selects the surviving OPEN row.

Correct the normalization so an OPEN row is closed **only** for a Subscription
whose `billingPeriodId` identifies an owned OPEN survivor.

Acceptable forms include gating the close UPDATE with an `EXISTS` check for the
pointer-selected owned OPEN BillingPeriod, or performing the normalization inside
a guarded CTE that has the same invariant.

Required behavior:

```text
multiple OPEN + pointer selects one owned OPEN
  -> selected row stays OPEN
  -> all other OPEN rows become CLOSED / MIGRATION_RECONCILED

multiple OPEN + pointer null / foreign / CLOSED / otherwise non-OPEN
  -> migration fails, no rows converted

exactly one OPEN + pointer selects that OPEN
  -> remains OPEN

exactly one OPEN + pointer null or points to an owned CLOSED historical row
  -> do not close that lone OPEN row merely to satisfy the pointer
     (leaving the legacy pointer inconsistency for runtime reconciliation is safer
      than destructively inventing a close)

zero OPEN
  -> do not fabricate one
```

If you prefer to fail the `exactly one OPEN + pointer references CLOSED` case
instead of preserving it, return that design choice to `moda_architect` before
implementation. Do not silently close the lone OPEN row.

Extend the billing-lifecycle validator so this pointer-safe normalization cannot
regress. The current checks merely assert that the migration mentions the pointer
and `MIGRATION_RECONCILED`; they do not prove the survivor must itself be OPEN.

##### Validation for Attempt 2

After the two corrections, rerun exactly the task contract:

```bash
npm run format
npm run validate
npm run prisma:generate
npm run test:recovery-credit-packs
npm run test:billing-lifecycle
npm run erd:puml
git diff --check
```

No shared/production migration application is required.

Retain and refresh the canonical worktree/isolation/synchronization evidence for
Attempt 2 and record the new implementation and parent-report commits.

##### Scope guard

Do not redesign:

- BillingPeriod plan snapshot vocabulary;
- current paid-period usage scoping;
- period entitlement counter quantities;
- DATABASE-002 reservation XOR/counter-family constraints;
- Free lifetime entitlement semantics;
- purchased/promotional credits;
- runtime rollover;
- Shopify calls;
- Background/Admin/merchant UI behavior.

Return the same task to `review`.

