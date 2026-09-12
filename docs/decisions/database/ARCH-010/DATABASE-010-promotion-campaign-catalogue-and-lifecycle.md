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
status: complete
priority: 82
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-010-DATABASE-009
enables:
  - ARCH-010-DATABASE-011
  - ARCH-010-ADMIN-004
created: 2026-09-12
updated: 2026-09-12T06:17:29Z
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

## Work Items

- [x] Inspect the accepted DATABASE-009 schema/migration and preserve its promotional grant rows and enum values.
- [x] Add campaign and lifecycle-event Prisma enums/models, relations, constraints, and query-path indexes.
- [x] Add the additive PostgreSQL migration without campaign rows, grant rows, balance changes, or counter backfills.
- [x] Add deterministic campaign schema/migration validation and regenerate the ERD.
- [x] Run the repository-declared Prisma, billing-policy, ERD, migration-status, and diff checks; record the unavailable database limitation.

## Acceptance Criteria

- [x] GLOBAL, PLAN, and SHOP campaigns have mutually exclusive target shapes enforced by a database CHECK constraint.
- [x] PLAN targets reference `BillingPlan.id`, SHOP targets reference `Shop.id`, and creator/event provenance references `PlatformAdmin.id` with deliberate restrictive delete behavior.
- [x] Positive quantity and `expiresAt > startsAt` are database-enforced; lifecycle status remains `DRAFT`/`ACTIVE`/`CLOSED` with time-derived expiry.
- [x] Running, target lookup, catalogue ordering, and append-only event query paths have indexes.
- [x] Campaign lifecycle evidence includes close/reopen/expiry-change event kinds and old/new expiry fields; `version` supports optimistic application updates.
- [x] Existing DATABASE-009 promotional grants and enum values remain unchanged, and the migration creates no promotional capacity.
- [x] ERD and deterministic validation cover the new schema contract.

## Stop conditions

Stop and return to `moda_architect` if the current `BillingPlan`, `Shop`, `PlatformAdmin` or DATABASE-009 models differ materially from the inspected contract in a way that changes target identity or audit ownership.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `prisma/schema.prisma`
- `prisma/migrations/20260912090000_add_promotion_campaign_catalogue/migration.sql`
- `scripts/validate-promotion-campaign-schema.mjs`
- `package.json`
- `docs/generated/prisma-erd.puml`

### Work Completed
- Added `PromotionTargetScope`, `PromotionCampaignStatus`, and `PromotionCampaignEventType` with the exact `GLOBAL`/`PLAN`/`SHOP`, `DRAFT`/`ACTIVE`/`CLOSED`, and lifecycle vocabularies.
- Added `billing.PromotionCampaign` with fixed quantity, running window, optional merchant description, durable BillingPlan/Shop target relations, PlatformAdmin creator provenance, versioning, and catalogue/running/target indexes.
- Added `billing.PromotionCampaignEvent` with append-only lifecycle kind, expiry transition fields, campaign provenance, restrictive campaign/admin foreign keys, and audit lookup indexes.
- Added PostgreSQL checks for positive quantity, expiry after start, and exactly one valid scope-target shape. Expiry remains derived from `expiresAt`; no `EXPIRED` enum value or scheduler state was added.
- Preserved DATABASE-009 `PromotionalCreditGrant` rows and enums; the migration is additive and creates no grants, counters, selections, balances, or other promotional capacity.
- Added deterministic validator coverage for schema/migration enum alignment, exact target identity relations, checks, indexes, restrictive foreign keys, no-row migration behavior, and absence of persisted `EXPIRED` status.
- Regenerated the PlantUML ERD with both campaign models and their relations.

### Validation Results
- `npm ci`: passed in the isolated implementation worktree; repository dependencies restored from `package-lock.json`.
- `npm run format`: passed.
- `npm run validate`: passed.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed with Prisma 6.19.3.
- `npm run test:billing-policy`: passed; DATABASE-009 compatibility assertions remain green.
- `npm run test:promotion-campaign`: passed.
- `npm run erd:puml`: passed; `docs/generated/prisma-erd.puml` contains both campaign entities and all relations.
- `git diff --check`: passed.
- `DATABASE_URL="postgresql://postgres:postgres@localhost:5432/moda_interact" npm run status`: attempted against the documented localhost database; blocked by `P1001: Can't reach database server at localhost:5432`. No migration was applied.
- Database-backed valid/invalid row checks could not run for the same unavailable local PostgreSQL service; static migration assertions cover all required constraints and no-row guards.

### Git / VCS
- Task branch: `task/ARCH-010-DATABASE-010`.
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-010`.
- Parent branch: `task/ARCH-010-DATABASE-010`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-010`.
- Implementation branch: `task/ARCH-010-DATABASE-010`.
- Shared workspace checkout switched/mutated for task work: no.
- Shared implementation checkout switched/mutated for task work: no.
- Another task worktree reused: no.
- Start-of-attempt synchronization: parent remote task branch `not-needed` (created from current `origin/main`); parent `origin/main` `already-current`; implementation remote task branch `not-needed` (created from current `origin/main`); implementation `origin/main` `already-current`.
- Parent claim commit: `ab36376`, pushed to `origin/task/ARCH-010-DATABASE-010`.
- Implementation commits: `82e91b3` and `bd79e7f`, pushed to `origin/task/ARCH-010-DATABASE-010`; `bd79e7f` is the clean implementation head.
- Parent report commit: this final evidence commit is pushed to `origin/task/ARCH-010-DATABASE-010`; its SHA is reported in the handoff because a commit cannot embed its own hash.
- Submodule gitlink staged: no.
- Merged to implementation main: no. Merged to workspace main: no.

### Architect Review

#### Review Status

Accepted

#### Attempt 1 — Accepted

Architect review verified:

- the implementation diff against the supplied pre-task workspace baseline is bounded to the declared database task surface: `prisma/schema.prisma`, the new promotion-campaign migration, `scripts/validate-promotion-campaign-schema.mjs`, the package script, and regenerated ERD;
- `PromotionTargetScope`, `PromotionCampaignStatus` and `PromotionCampaignEventType` exactly preserve the agreed `GLOBAL/PLAN/SHOP`, `DRAFT/ACTIVE/CLOSED`, and lifecycle-event vocabularies;
- `billing.PromotionCampaign` stores exact durable `BillingPlan.id` / `Shop.id` targeting, positive fixed quantity, bounded start/expiry times, PlatformAdmin creator provenance, optimistic `version`, and the required running/target/catalogue indexes;
- PostgreSQL CHECK constraints enforce positive quantity, `expiresAt > startsAt`, and exactly one valid scope-target shape;
- campaign target, creator, event campaign, and event administrator foreign keys all use deliberate `ON DELETE RESTRICT` behaviour;
- `billing.PromotionCampaignEvent` provides append-only lifecycle evidence shape for activation, close, reopen and expiry change, with old/new expiry values and acting administrator provenance;
- the schema supports the post-activation application invariant that scope/target/quantity remain immutable, while ADMIN-004/005 own mutation authorization and lifecycle transitions;
- the migration is additive and contains no `INSERT`, no conversion from `campaignReference`, no merchant selection, no grant creation, and no purchased/lifetime-Free counter mutation;
- existing DATABASE-009 `PromotionalCreditGrant` structure and enum values remain unchanged;
- `scripts/validate-promotion-campaign-schema.mjs` deterministically asserts enum/schema/migration alignment, constraints, indexes, restrictive provenance relations, no-row migration behaviour, and absence of persisted `EXPIRED`;
- the promotion-campaign validator and existing billing-policy validator both pass in the architect review copy;
- the Completion Report records successful Prisma format/validate/generate, billing-policy validation, promotion-campaign validation, ERD regeneration and `git diff --check`;
- the reported local `npm run status` failure is Prisma `P1001` because no PostgreSQL server was listening on `localhost:5432`. This is an environment-availability limitation rather than evidence of a schema defect; as with previously accepted additive ARCH-010 database work, applying the migration to a shared database is not required solely for architect acceptance;
- the submitted handoff identifies implementation commits `82e91b3` and `bd79e7f`, with `bd79e7f` as the clean implementation head, and parent report commits `6231b3d` and `08b950e`;
- the Completion Report records the canonical dedicated parent/implementation worktrees and start-of-attempt synchronization evidence. The submitted review archive does not carry usable Git metadata, so commit ancestry/push state is accepted from that durable handoff evidence rather than re-derived in the review container;
- the reported external modification to the parent task document was preserved. The architect acceptance overlay is based on the supplied final task document and does not require implementation-code churn.

**Architect decision: Accepted.**

Because `completion_mode: automatic`, this task is now `complete`. `executor` and `claimed_at` are cleared while `attempt: 1` is preserved.

Dependency reconciliation:

- `ARCH-010-DATABASE-011` is promoted from Pending to Ready because its two prerequisites, DATABASE-009 and DATABASE-010, are now Complete;
- `ARCH-010-ADMIN-004` is promoted from Pending to Ready because DATABASE-010, its sole prerequisite, is now Complete;
- no other dependant becomes Ready solely from this acceptance.
