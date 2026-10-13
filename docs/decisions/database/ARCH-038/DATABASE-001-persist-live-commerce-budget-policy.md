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
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
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

- [ ] Add enums, `CommerceModelPolicy` Prisma model, reverse relations and five `CommerceAuditAction` values.
- [ ] Add SQL migration with scope/JSONB CHECK constraints, partial unique indexes, FK and Platform-row protection.
- [ ] Seed all required LIVE and PREVIEW Platform defaults using migration logic.
- [ ] Prove audit/CAS wiring and constraints, version/JSON validation and independent contexts with focused tests.
- [ ] Run disposable PostgreSQL fresh/upgrade migrations and Prisma validation/generation.

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

- [ ] One `CommerceModelPolicy` table supports both contexts; PREVIEW+PRICE_PLAN and incorrect/missing owner columns are rejected.
- [ ] Scope-specific uniqueness, FK constraints and JSONB shape/integer/version rules are enforced by PostgreSQL.
- [ ] Sparse overrides preserve independent key inheritance; no cross-context reads/writes in regression proofs.
- [ ] Required Platform rows are seeded per environment/context and protected from ordinary deletion.
- [ ] Atomic audited CAS mutations and actor/reason/version evidence are reproducible.
- [ ] Existing billing/Shop/subscription data survive upgrade; fresh empty DB receives required defaults.

## Validation

- [ ] Prisma validate/generate
- [ ] Disposable PostgreSQL fresh and upgrade migration rehearsals
- [ ] Scope/index/FK/JSONB/version and audit/CAS tests
- [ ] Isolation and required-default deletion tests
- [ ] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-DATABASE-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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
