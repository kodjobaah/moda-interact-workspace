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
status: ready
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
updated: 2026-09-12T07:00:00Z
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

#### Review Status

Changes Requested

#### Attempt 1 — Changes Requested

The DATABASE-011 data model is substantively aligned with the ARCH-010 promotion architecture, but Attempt 1 cannot be accepted yet because one schema/migration alignment defect and one mandatory workflow-evidence defect remain.

##### Accepted implementation findings

Architect review verified and does not request redesign of the following:

- `PromotionalCreditGrant` preserves the DATABASE-009 provenance fields and adds nullable campaign ownership, reserved/committed lot quantities, first/last selection and use evidence, exhaustion state, selection count and optimistic versioning;
- `(campaignId, shopId)` is unique, while PostgreSQL NULL semantics preserve historical campaign-less DATABASE-009 rows;
- the inherited positive `quantity` CHECK remains in the DATABASE-009 migration and DATABASE-011 adds non-negative/within-grant lot checks;
- `MerchantPromotionSelection` enforces one row per Shop and one current grant pointer, with a composite `(promotionalCreditGrantId, shopId)` foreign key that prevents a Shop from persisting a selection for another Shop's grant;
- `UsageReservation.promotionalCreditGrantId` provides exact promotional grant ownership and existing reservations remain `NULL` during migration;
- the migration is additive and contains no `INSERT`/`UPDATE` that would auto-select a promotion, grant capacity, backfill campaign IDs, rewrite historical grants or mutate aggregate counters;
- the implementation repository differs from the accepted DATABASE-010 baseline only in the expected schema, one DATABASE-011 migration, focused validator, package script and generated ERD;
- focused static promotion-selection, promotion-campaign and billing-policy validators passed during architect review;
- the reported local PostgreSQL `P1001` is not itself a product defect and does not require applying the migration to a shared database solely for architect review.

##### Correction 1 — remove Prisma schema/migration index drift

The DATABASE-011 migration creates:

```sql
CREATE INDEX "PromotionalCreditGrant_campaignId_createdAt_idx"
ON "billing"."PromotionalCreditGrant"("campaignId", "createdAt");
```

but `prisma/schema.prisma` does not declare the equivalent index.

Keep the index and declare the canonical Prisma equivalent on `PromotionalCreditGrant`:

```prisma
@@index([campaignId, createdAt])
```

This keeps the schema aligned with the migration and preserves the useful campaign-history/reporting access path already introduced by the migration.

Strengthen `scripts/validate-promotion-selection-schema.mjs` so it deterministically proves the index exists in both:

1. `prisma/schema.prisma`; and
2. the DATABASE-011 migration.

Do not redesign the grant model or add unrelated indexes.

##### Correction 2 — record mandatory worktree isolation and synchronization evidence

The Completion Report currently records the canonical parent/implementation paths and branches, but it does not record the complete evidence required by `docs/agent-worktree-isolation-policy.md`.

Attempt 2 must record, explicitly:

```text
Physical worktree isolation:
  canonical workspace root: <launcher-resolved workspace root>
  parent worktree: <canonical parent task worktree>
  parent branch: task/ARCH-010-DATABASE-011
  implementation worktree: <canonical implementation task worktree>
  implementation branch: task/ARCH-010-DATABASE-011
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Because Attempt 1 did not durably record that mandatory evidence, begin Attempt 2 through the canonical `/moda-task` execution path, synchronize both task worktrees, make the focused correction above in the canonical implementation worktree, and rerun the required validation there. Do not create a new task or new branch pair.

The already-published Attempt-1 implementation commits do not need to be rewritten. Append the correction commit(s) to the same mirrored `task/ARCH-010-DATABASE-011` branches.

##### Scope guard

Attempt 2 is limited to:

- declaring the already-created `(campaignId, createdAt)` Prisma index;
- focused validator coverage for schema/migration index alignment;
- generated ERD refresh if the repository generator changes it;
- complete physical-worktree/start-of-attempt evidence;
- normal Completion Report/VCS reconciliation.

Do not implement merchant eligibility/selection mutation, Background reserve/commit/release logic, Admin UI/reporting, merchant UI/history, expiry scheduling, aggregate-counter runtime behaviour or another repository's work.

##### Attempt 2 validation

From the canonical implementation task worktree, rerun the repository/task validation contract:

```text
npm run format
npm run validate
npm run prisma:validate
npm run prisma:generate
npm run test:promotion-selection
npm run test:promotion-campaign
npm run test:billing-policy
npm run test:recovery-credit-packs
npm run test:checkout-recovery-capacity
npm run test:purchased-credit-lots
npm run test:billing-lifecycle
npm run erd:puml
git diff --check
```

If PostgreSQL remains unavailable at the configured local endpoint, record the resulting `P1001` for migration-status/application validation and continue; do not apply DATABASE-011 to a shared database solely for architect review.

Return the same task to `review` with Attempt 2 evidence and both mirrored task branches published.

**Architect decision: Changes Requested — Attempt 1.**
