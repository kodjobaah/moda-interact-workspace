---
id: ARCH-010-DATABASE-011
architecture_id: ARCH-010
title: Persist merchant promotion selection and exact promotional grant-lot accounting
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 83
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-010-DATABASE-009
  - ARCH-010-DATABASE-010
enables:
  - ARCH-010-ADMIN-006
  - ARCH-010-BACKGROUND-019
  - ARCH-010-SHOPIFY-009
  - ARCH-010-SHOPIFY-021
  - ARCH-010-SHOPIFY-022
created: 2026-09-12
updated: 2026-09-12T06:51:07Z
---

# ARCH-010-DATABASE-011: Persist merchant promotion selection and exact promotional grant-lot accounting

## Objective

Extend the completed DATABASE-009 promotional ledger so one merchant can claim a campaign exactly once, one promotion can be selected at a time per Shop, and Background can reserve/commit against the exact campaign grant rather than an undifferentiated lifetime aggregate.

## Inspect before editing

```text
prisma/schema.prisma
prisma/migrations/**
scripts/validate-billing-policy-schema.mjs
docs/generated/prisma-erd.puml
```

Read DATABASE-009 and DATABASE-010 in full before editing.

## 1. Extend PromotionalCreditGrant

Preserve all DATABASE-009 provenance fields. Add campaign-aware fields equivalent to:

```text
campaignId? -> PromotionCampaign
reservedQuantity   Int default 0
committedQuantity  Int default 0
firstSelectedAt?
lastSelectedAt?
selectionCount     Int default 0
firstUsedAt?
lastUsedAt?
exhaustedAt?
version            Int default 0
```

`campaignId` is nullable **only for compatibility with pre-DATABASE-010 direct grant history**.

Add a unique constraint/index equivalent to:

```text
UNIQUE(campaignId, shopId)
```

PostgreSQL NULL semantics may allow historical `campaignId=NULL` rows to coexist; do not invent campaigns for them.

Add quantity integrity checks equivalent to:

```text
quantity > 0
reservedQuantity >= 0
committedQuantity >= 0
reservedQuantity + committedQuantity <= quantity
selectionCount >= 0
```

## 2. One current merchant selection

Add `billing.MerchantPromotionSelection` with one row per Shop:

```text
shopId UNIQUE
promotionalCreditGrantId UNIQUE
selectedAt
updatedAt
version
```

Relations must make it impossible to point a Shop at another Shop's grant through normal service code; add DB-enforceable integrity where practical and require transactional identity checks where a composite FK would overcomplicate the existing schema.

The one-row-per-Shop shape is the durable invariant behind:

> one selected promotion per merchant at any one time.

The row may temporarily point to a grant whose campaign later expires/closes/becomes plan-ineligible; runtime eligibility decides spendability. Selection replacement is owned by SHOPIFY-021.

## 3. Exact reservation ownership

Extend `UsageReservation` with nullable:

```text
promotionalCreditGrantId
```

and relation/index support matching purchased-credit lot ownership.

A promotional reservation must identify the exact grant that funded it. Do not use only the aggregate `ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)` as reservation ownership.

Existing reservation rows migrate with NULL promo grant id.

## 4. Aggregate counter compatibility

Keep `PROMOTIONAL_RECOVERY_CREDITS` for aggregate accounting/reporting compatibility, but after this task it is **not sufficient authority for spendability** because campaign status/expiry/eligibility/current selection are grant-specific.

Do not delete the counter or rewrite DATABASE-009 history.

## 5. Merchant history

The campaign-linked grant must preserve enough durable fields to answer:

- which campaigns this merchant selected;
- which were actually used (`firstUsedAt != null`);
- total original allocation;
- committed usage;
- current held reservation;
- whether allocation is exhausted;
- whether the same campaign was selected again after reopen without replenishment.

No additional history table is required unless implementation proves the above cannot be answered durably without losing important selection events. Do not invent one merely for convenience.

## Required tests / validation

Prove at minimum:

1. one campaign+shop grant maximum;
2. one current selection row per Shop maximum;
3. grant counters cannot become negative/over-allocated;
4. reservation may point to exact promotional grant;
5. existing reservations/grants migrate safely;
6. historical campaign-less grant remains valid compatibility data;
7. no migration auto-selects a promotion;
8. no migration grants more capacity;
9. reopened campaign cannot create a second grant for the same shop because `(campaignId, shopId)` remains unique.

Run normal Prisma/migration/schema/ERD validations and `git diff --check`.

## Non-goals

Do not implement campaign eligibility, selection mutation, Background reserve/commit/release, Admin UI, merchant UI or expiry scheduling.

## Stop conditions

Stop if exact promo-grant reservation ownership cannot be added without conflicting with the already-accepted purchased/included UsageReservation ownership model; return the conflict to `moda_architect` rather than creating a parallel reservation table.

## Work Items

- [x] Extend `PromotionalCreditGrant` with campaign ownership, exact lot counters, selection/use history, exhaustion state, optimistic versioning, and the `(campaignId, shopId)` uniqueness boundary.
- [x] Add one-row-per-Shop `MerchantPromotionSelection` with unique grant ownership and a composite Shop/grant foreign key.
- [x] Add nullable exact promotional grant ownership to `UsageReservation` with an indexed relation, preserving existing rows as `NULL`.
- [x] Add the additive migration, ERD update, package script, and deterministic schema/migration validator without creating selections, grants, capacity, or rewriting historical rows.
- [x] Run the repository-declared Prisma, schema, compatibility, ERD, migration-status, and diff checks.

## Acceptance Criteria

- [x] `(campaignId, shopId)` is unique, while nullable campaign IDs preserve historical campaign-less grants and reopened campaigns cannot create a second grant.
- [x] `MerchantPromotionSelection.shopId` and `promotionalCreditGrantId` are individually unique, and the composite foreign key prevents cross-Shop grant pointers.
- [x] Promotional grant counters are database-constrained non-negative and within original quantity; the inherited DATABASE-009 positive quantity constraint remains validated.
- [x] `UsageReservation.promotionalCreditGrantId` identifies the exact promotional grant and existing reservations migrate safely with `NULL` ownership.
- [x] Migration validation proves no automatic selection, capacity grant, counter rewrite, campaign backfill, or historical grant rewrite occurs.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `prisma/schema.prisma`
- `prisma/migrations/20260912100000_add_promotion_selection_and_grant_lots/migration.sql`
- `scripts/validate-promotion-selection-schema.mjs`
- `package.json`
- `docs/generated/prisma-erd.puml`

### Work Completed
- Added campaign-aware promotional grant lot fields and durable lifecycle accounting while preserving DATABASE-009 provenance and campaign-less compatibility rows.
- Added unique campaign/shop claim enforcement, current merchant selection persistence, composite Shop/grant identity enforcement, and exact promotional reservation ownership.
- Added deterministic validation for uniqueness, quantity integrity, exact reservation ownership, compatibility migration behavior, and no automatic selection or capacity grant.
- Regenerated the PlantUML ERD and added the `test:promotion-selection` package command.

### Validation Results
- Passed: `npm run format`.
- Passed: `npm run validate`.
- Passed: `npm run prisma:validate`.
- Passed: `npm run prisma:generate` with Prisma 6.19.3.
- Passed: `npm run test:promotion-selection`.
- Passed: `npm run test:promotion-campaign`.
- Passed: `npm run test:billing-policy`.
- Passed: `npm run test:recovery-credit-packs`.
- Passed: `npm run test:checkout-recovery-capacity`.
- Passed: `npm run test:purchased-credit-lots`.
- Passed: `npm run test:billing-lifecycle`.
- Passed: `npm run erd:puml`.
- Passed: `git diff --check`.
- Blocked by environment: `DATABASE_URL="postgresql://postgres:postgres@localhost:5432/moda_interact" npm run status` returned Prisma `P1001` because PostgreSQL was unavailable at `localhost:5432`; no migration was applied.

### Git / VCS
- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-011`.
- Parent branch: `task/ARCH-010-DATABASE-011`; prior claim commit: `b9d8e1b`.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-011`.
- Implementation branch: `task/ARCH-010-DATABASE-011`; implementation commit: `f2d79da` (`feat(database): persist promotion selection and grant lots`).
- Implementation branch pushed to and tracking `origin/task/ARCH-010-DATABASE-011`.
- Parent task file is the only parent file staged; the implementation submodule gitlink was not staged.
- No merge to `main` and no push to `main` performed.

### Architect Review
Pending.
