---
id: ARCH-038-DATABASE-001
architecture_id: ARCH-038
title: Persist LIVE CommerceAgent budget hierarchy
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
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
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-13
---
# Persist LIVE CommerceAgent budget hierarchy

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_database`
- Repository: `moda-interact-database`

## Objective

Persist auditable, environment-scoped LIVE CommerceAgent deadlines and output-token budgets at Platform, Merchant Pricing Plan and Shop override scopes.

## Context

The existing billing model distinguishes MerchantPricingPlan from BillingPlan, joined for current subscribers by canonical shopifyPlanHandle; PlatformBillingPolicy is billing-owned and must remain independent.

## Scope

- Add normalized LIVE policy storage and additive migration in database/prisma/schema.prisma and migrations.
- Represent one required Platform default per environment and optional Price Plan and Shop overrides with nullable independently inheritable fields.
- Add supporting uniqueness, indices, foreign keys and durable audit/CAS fields; seed Platform defaults on empty production migration.
- Add focused schema and fresh/upgrade migration proof without resetting existing billing state.

## Out of Scope

- Do not modify billing hard-limit policy or create a MerchantPricingPlan-to-BillingPlan FK.
- Do not build Admin UI or Background runtime logic.
- Do not add Preview test policy storage in this task.

## Requirements

- Scope uniqueness: platform by environment; plan by (environment, merchantPricingPlanId); shop by (environment, shopId).
- Required Platform defaults start at 60000 milliseconds / 800 output tokens; no missing default after fresh migration.
- NULL denotes inheritance only for optional scopes; reject zero, negatives, non-integers and missing required platform values.
- Admin audit and optimistic edit versions must permit atomic write + reason + actor attribution; existing data remains intact.
- Use CommerceEnvironment and existing MerchantPricingPlan and Shop identity; preserve referential integrity.

## Work Items

- [x] Implement Prisma schema and additive SQL migration.
- [x] Implement migration-backed Platform default guarantee.
- [x] Add relational/index/CAS/audit constraints and focused regression validation.
- [x] Run fresh/upgrade migration rehearsals and Prisma checks.

## Interfaces / Contracts

Produces database-owned LIVE execution policy schema keyed by CommerceEnvironment, MerchantPricingPlan.id and Shop.id, consumable by Admin and Background. Existing Shared runner budget contract unchanged.

## Dependencies

None

## Enables

- `ARCH-038-ADMIN-001`
- `ARCH-038-ADMIN-002`
- `ARCH-038-ADMIN-003`
- `ARCH-038-BACKGROUND-001`
- `ARCH-038-SYSTEM-TEST-001`

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

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-DATABASE-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. The task branches and worktrees were created from `origin/main` for developer attempt 1. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

Submitted for authorised review; developer self-review accepted.

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

Status: Accepted; implementation meets the current agreed ARCH-038 DATABASE-001 contract and is submitted for authorised review. Because `completion_mode: developer`, task status remains `review`; this is not a completion decision.

Reviewed files: all five implementation files listed above. The additive migration was exercised against the full ordered migration chain in fresh and populated-upgrade modes. The upgrade test was strengthened during review after identifying that its original protected-table count assertions were vacuous for three empty tables.

Scope conformance: one shared LIVE/PREVIEW policy model; PREVIEW+PRICE_PLAN and invalid owner combinations rejected; independent context keys and sparse per-field inheritance retained; no BillingPlan FK or changes to billing policy/model availability; audit uses the existing `CommerceAuditEvent` table.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation

### Follow-up

None
