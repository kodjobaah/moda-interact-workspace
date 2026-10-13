---
id: ARCH-038-DATABASE-001
architecture_id: ARCH-038
title: Persist unified LIVE and PREVIEW CommerceModelPolicy
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-038-ADMIN-001
  - ARCH-038-ADMIN-002
  - ARCH-038-ADMIN-003
  - ARCH-038-BACKGROUND-001
  - ARCH-038-COMMERCE-001
  - ARCH-038-COMMERCE-002
  - ARCH-038-SYSTEM-TEST-001
  - ARCH-038-SYSTEM-TEST-002
created: 2026-10-13
updated: 2026-10-13
---
# Persist unified LIVE and PREVIEW CommerceModelPolicy

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_database`
- Repository: `moda-interact-database`

## Objective

Add one generic, audited, environment-scoped `CommerceModelPolicy` table with a versioned JSONB `budget` supporting **LIVE** Platform/Price Plan/Shop and independently isolated **PREVIEW** Platform/Shop settings.


## Context

The accepted ARCH-038 design consolidates the previously separate LIVE and PREVIEW persistence tasks into a single Prisma model. `CommerceModelAvailability` controls model eligibility, not execution; `MerchantPricingPlan` and `Shop` already provide policy owner identities; `CommerceAuditEvent` provides a reusable audit mechanism. The existing BillingPlan↔MerchantPricingPlan relationship continues to resolve through canonical plan handles; do not introduce another FK.


## Scope

- Define `CommerceModelPolicy`, `CommerceModelPolicyContext` (`LIVE`,`PREVIEW`) and `CommerceModelPolicyScope` (`PLATFORM`,`PRICE_PLAN`,`SHOP`) in Prisma schema `commerce`, with owner relations to existing `MerchantPricingPlan`, `Shop` and `PlatformAdmin`.
- Persist `budget Json @db.JsonB`, required `budgetSchemaVersion Int @default(1)`, `editVersion`, creation/updater admin IDs and timestamps.
- Add an **additive** PostgreSQL migration with `CHECK` constraints enforcing valid context/scope/owner combinations, JSONB shape/inheritance, supporting foreign keys, indexes and partial uniqueness across nullable scope owners.
- Seed the required Platform policy for **each** LIVE/PREVIEW × CommerceEnvironment combination (10 rows for the current 5 environments); migration must work on fresh production-like and upgraded databases without deleting billing/subscription data.
- Reuse `CommerceAuditEvent` and add five budget-policy actions covering LIVE Platform/Plan/Shop and PREVIEW Platform/Shop; support transactionally audited edit-version CAS mutations.
- Add focused migration/constraint tests, including generation/upgrade and invalid policy combinations.


## Out of Scope

- Do not create separate LIVE/PREVIEW tables, edit `CommerceModelAvailability`, `PlatformBillingPolicy`, `BillingPlan` or model selection, or create a new policy audit table.
- Do not implement Admin/Commerce UI, Background execution resolution, Shared runner changes or merchant-facing settings.
- Do not create or edit any `docs/decisions/**/_index.md` files.


## Requirements

- Every row is uniquely identified by a stable ID, environment, context and scope, plus exactly one legal owner where applicable: `PLATFORM` owns neither Shop nor Plan; `PRICE_PLAN` owns only MerchantPricingPlan and is **LIVE-only**; `SHOP` owns only Shop and is valid in LIVE/PREVIEW.
- Partial unique indexes enforce at most one policy per `(environment,context)` PLATFORM, per `(environment,context,merchantPricingPlanId)` PRICE_PLAN, and per `(environment,context,shopId)` SHOP. Add owner lookup indexes.
- `budget` root is a JSON object, never an array/null. Schema version 1 allows **only** `deadlineMs` and `outputTokens`, each a positive safe integer; Platform rows require both; optional scope rows may omit either key but cannot be empty, use explicit JSON `null`, or use zero to represent inherit.
- Inheritance is by **absent property** rather than by nullable SQL column. For LIVE overlay Platform → Price Plan → Merchant; for PREVIEW overlay Platform → Shop. No JSON object replacement semantics that erase the other inherited field. Future keys require a new approved schema version and corresponding validators.
- No arbitrary product ceiling in database budget constraints: validate positive/int shape and implement operational feasibility in the authorised Admin and runtime layers. Unknown schema versions fail closed.
- Protect required Platform rows from ordinary deletes. Initial values are `{"deadlineMs":60000,"outputTokens":800}` for each context/environment independently, migration-guaranteed rather than app-seeded.
- Audited mutation records actor, reason, previous/new JSON, environment/context/scope, owner, schema/edit versions atomically with CAS; migration-created Platform defaults may have null creator, subsequent writes require authorised admins.
- Migration and Prisma-generated client preserve existing Shop, MerchantPricingPlan, Subscription and billing records and referential integrity. Include reverse relations and foreign-key delete behaviours consistent with existing schema.


## Work Items

- [x] Implement Prisma schema and additive SQL migration.
- [x] Implement migration-backed Platform default guarantee.
- [x] Add relational/index/CAS/audit constraints and focused regression validation.
- [x] Run fresh/upgrade migration rehearsals and Prisma checks.

## Interfaces / Contracts

Produces the **sole** database-owned `CommerceModelPolicy` schema for both LIVE and PREVIEW. Consumers filter `context` explicitly; Background consumes LIVE, Commerce Studio consumes PREVIEW, and Admin manages LIVE. Existing Shared `runCommerceTurn` budget contract is unchanged. Any genuinely new serialized cross-repository contract requires separate Shared ownership rather than duplicated ad hoc schemas.


## Dependencies

None

## Enables

- `ARCH-038-ADMIN-001`
- `ARCH-038-ADMIN-002`
- `ARCH-038-ADMIN-003`
- `ARCH-038-BACKGROUND-001`
- `ARCH-038-COMMERCE-001`
- `ARCH-038-COMMERCE-002`
- `ARCH-038-SYSTEM-TEST-001`
- `ARCH-038-SYSTEM-TEST-002`


## Acceptance Criteria

- [x] Correct uniqueness, sparse inheritance and required Platform row enforced for LIVE and PREVIEW.
- [x] CAS and transactional audited mutation evidence support safe concurrent updates.
- [x] Populated Shop, MerchantPricingPlan, Subscription and BillingPlan rows survive upgrade rehearsal.
- [x] Fresh production-like database contains all required Platform defaults without manual seed.

## Validation

- [x] `npm run validate` and `npm run prisma:generate` passed.
- [x] Disposable PostgreSQL fresh migration rehearsal passed; container cleanup confirmed.
- [x] Disposable PostgreSQL upgrade migration rehearsal passed with populated preservation fixtures; container cleanup confirmed.
- [x] `npm run test:arch038-model-policy-schema` passed, covering schema, constraints, indexes and migration fragments.
- [x] PostgreSQL harness exercised ownership/FK/JSON/version rejection, sparse inheritance, context isolation, uniqueness, CAS/audit rollback and Platform-delete protection.
- [x] `git diff --check` passed after the final implementation edit.

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-DATABASE-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

Completed by explicit developer decision after accepted self-review.

### Files Changed

Implementation repository (`moda-interact-database`):
- `package.json`
- `prisma/schema.prisma`
- `prisma/migrations/20261013183000_arch038_unified_model_policies/migration.sql`
- `scripts/test-arch038-model-policy-postgres.mjs`
- `scripts/validate-arch038-model-policy-schema.mjs`

### Work Completed

Added one environment-scoped `CommerceModelPolicy` model with LIVE and PREVIEW contexts, PLATFORM/PRICE_PLAN/SHOP scopes, sparse version-1 JSONB budgets, owner/admin relations, partial unique indexes, ownership/FK/budget/version constraints, immutable identity and edit-version guard, and protected Platform defaults.

Seeded all 10 context/environment Platform defaults at `{"deadlineMs":60000,"outputTokens":800}`. Added five policy audit actions and extended `CommerceAuditEvent` with indexed `modelPolicyId` and policy-action audit requirements. Added focused static and disposable PostgreSQL coverage.

The upgrade rehearsal now seeds non-empty Shop, MerchantPricingPlan, Subscription and BillingPlan tables before the target migration, compares table counts afterward, and verifies the fixture identities remain present.

### Validation Results

All commands ran in the canonical implementation worktree:
- `npm run test:arch038-model-policy-schema` — PASS.
- `npm run validate` — PASS; Prisma schema valid.
- `npm run prisma:generate` — PASS; Prisma Client v6.19.3 generated.
- `npm run test:arch038-model-policy:postgres:fresh` — PASS; disposable `pgvector/pgvector:pg17` container removed in `finally`.
- `npm run test:arch038-model-policy:postgres:upgrade` — PASS after adding populated preservation fixtures; Shop, MerchantPricingPlan, Subscription and BillingPlan counts and fixture identities preserved; container removed in `finally`.
- `git diff --check` — PASS after final implementation edit.

Physical isolation/publication: launcher-resolved parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-DATABASE-001` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-DATABASE-001` are separate registered Git worktrees on matching `task/ARCH-038-DATABASE-001` branches. Parent worktree was clean at claim commit `433f91304d8a2a36acc27eedd9038a10b59d2ceb`; implementation started synchronized at `8936f3b76a5e7f988c477032397de55de2b369de` and is now clean/up-to-date with origin at pushed commit `1a3eca20d8efab640d93f0113371c3d226345654`. `git submodule status` in the implementation worktree returned no nested submodules.

### Deviations

The routed task definition predates the agreed ARCH-038 consolidation and states Preview persistence is out of scope. The current agreed architecture change history assigns both LIVE and PREVIEW to this sole DATABASE-001 model and supersedes DATABASE-002. This implementation follows that explicit architecture decision; no architect-owned architecture or index files were edited.

### Assumptions

The current `CommerceEnvironment` enum has five values; the migration enumerates it and the PostgreSQL rehearsal verifies ten seeded rows (five environments × two contexts).

### Unresolved Issues

None within the database task. Operational feasibility and runtime policy resolution remain owned by the downstream Admin, Background and Commerce tasks.

### Architectural Concerns

None identified for this database scope.

### Developer Self-Review

Status: Accepted; implementation meets the current agreed ARCH-038 DATABASE-001 contract. The developer explicitly completed this accepted attempt on 2026-10-13; attempt remains 1.

Reviewed files: all five implementation files listed above. The additive migration was exercised against the full ordered migration chain in fresh and populated-upgrade modes. The upgrade test was strengthened during review after identifying that its original protected-table count assertions were vacuous for three empty tables.

Scope conformance: one shared LIVE/PREVIEW policy model; PREVIEW+PRICE_PLAN and invalid owner combinations rejected; independent context keys and sparse per-field inheritance retained; no BillingPlan FK or changes to billing policy/model availability; audit uses the existing `CommerceAuditEvent` table.

### Developer Completion Decision

On 2026-10-13 the developer explicitly accepted the durable passing self-review and completed ARCH-038-DATABASE-001, attempt 1. Implementation commit `1a3eca20d8efab640d93f0113371c3d226345654` and parent task/report commit `a9ab1b6ab7884e62fc488159133ad32b95d05420` are pushed to their respective mirrored task branches. No merge to `main` was performed.

## Architect Review

### Review Status

Accepted

### Review Notes

Developer completion was separately recorded; the authoritative task status remains `complete` (attempt 1).

Reviewed implementation commit `1a3eca20d8efab640d93f0113371c3d226345654` and parent Completion Report commit `a9ab1b6ab7884e62fc488159133ad32b95d05420`. The additive schema, migration, JSONB policy constraints, partial uniqueness, scope ownership, Plan/Shop/Admin foreign keys, Platform defaults, edit-version guard and audit extension conform to the consolidated LIVE/PREVIEW design. The audit target constraint preserves all pre-existing action branches. Developer self-review and physical worktree/synchronisation evidence are recorded.

### Reviewed Files

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20261013183000_arch038_unified_model_policies/migration.sql`
- `moda-interact-database/scripts/validate-arch038-model-policy-schema.mjs`
- `moda-interact-database/scripts/test-arch038-model-policy-postgres.mjs`
- `moda-interact-database/package.json`
- Parent task Completion Report and ARCH-038 architecture/decisions.

### Validation Reviewed

The Completion Report records passing `npm run validate`, `npm run prisma:generate`, static checks, fresh and populated-upgrade disposable PostgreSQL rehearsals, and `git diff --check`. The developer supplied a passing PostgreSQL upgrade trace with expected negative-case rejections. Code, migration and tests were independently inspected via the published GitHub commits; Prisma/Docker tests were **not rerun in this review environment**.

### Architecture Conformance

Accepted against the latest agreed ARCH-038 consolidation: one versioned JSONB policy model with isolated LIVE/PREVIEW contexts; LIVE supports Platform/Price Plan/Shop, PREVIEW supports Platform/Shop only; no BillingPlan foreign key, model-availability changes, new audit table, or merchant-owned policy settings. Initial task prose was stale; this architect-owned documentation reconciliation aligns the parent architecture and task frontier with the accepted implementation.

### Follow-up

Developer explicitly completed attempt 1 on 2026-10-13, as recorded under Developer Completion Decision. Preserve `status: complete`, `attempt: 1`, cleared executor/claim, and the accepted implementation commit. DATABASE-002 remains superseded; `ADMIN-001`, `BACKGROUND-001`, and `COMMERCE-001` are Ready because their sole prerequisite is Complete. Do not modify domain `_index.md` until the developer confirms this architecture session is complete.
