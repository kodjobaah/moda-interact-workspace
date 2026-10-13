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
status: in_progress
priority: 10
executor: developer
claimed_at: 2026-10-13T17:40:11Z
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

- [ ] Implement Prisma schema and additive SQL migration.
- [ ] Implement migration-backed Platform default guarantee.
- [ ] Add relational/index/CAS/audit constraints and focused regression validation.
- [ ] Run fresh/upgrade migration rehearsals and Prisma checks.

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

- [ ] Correct uniqueness, null inheritance and required Platform row enforced.
- [ ] CAS and audited mutation evidence support safe concurrent updates.
- [ ] Current billing and subscription rows survive migration.
- [ ] Fresh production-like database contains required Platform defaults without manual seed.

## Validation

- [ ] Prisma validation and generation
- [ ] Fresh and upgrade PostgreSQL migration rehearsals
- [ ] Focused schema/constraint/index regression tests
- [ ] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-DATABASE-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. The task branches and worktrees were created from `origin/main` for developer attempt 1. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

In Progress

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
