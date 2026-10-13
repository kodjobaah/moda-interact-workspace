---
id: ARCH-038-DATABASE-002
architecture_id: ARCH-038
title: Persist isolated Studio Preview budget policies
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: superseded
priority: 11
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-038-COMMERCE-001
  - ARCH-038-COMMERCE-002
  - ARCH-038-SYSTEM-TEST-002
created: 2026-10-13
updated: 2026-10-13
superseded_by: ARCH-038-DATABASE-001
---
# Persist isolated Studio Preview budget policies

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_database`
- Repository: `moda-interact-database`

## Objective

Persist an auditable Studio-only Platform test budget and optional selected-Shop test overrides without sharing LIVE policy rows.

## Context

Studio Preview uses its own run reservation lifecycle and must never modify or inherit Background LIVE policy. The development code currently supports execution budget environment variables.

## Scope

- Add a distinct Preview policy representation, migration and required Platform test default per CommerceEnvironment.
- Allow optional per-(environment, shopId) test overrides with independently nullable deadline/output-token fields.
- Enforce uniqueness, versioned CAS, audit attribution and safe relationship to Shop.
- Add fresh/upgrade schema tests and default migration evidence.

## Out of Scope

- Do not write LIVE policy or price-plan budget fields.
- Do not alter Commerce Studio UI, runtime or Redis reservation in this task.

## Requirements

- Default Preview Platform policy is 60000 milliseconds and 800 output tokens (independent values from LIVE).
- Shop Preview overrides are admin-owned, per environment and per Shop; NULL means inherit.
- Audit reason and author identity are durable; preserve existing database data.
- Avoid reusing live PlatformBillingPolicy or existing agent model-selection columns.

## Work Items

- [ ] Implement isolated Preview schema and migration.
- [ ] Add migration guarantee for defaults and audit/CAS invariants.
- [ ] Validate isolation, uniqueness and deletion behaviour.

## Interfaces / Contracts

Produces separate database-owned PREVIEW Platform and Shop test policy schema. No LIVE or Shared API contract changes.

## Dependencies

None

## Enables

- `ARCH-038-COMMERCE-001`
- `ARCH-038-COMMERCE-002`
- `ARCH-038-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Preview policy updates cannot modify LIVE policy rows.
- [ ] Per-shop values inherit independently and remain environment-scoped.
- [ ] Required Platform test fallback exists after empty-DB migration.

## Validation

- [ ] Prisma validate/generate
- [ ] Fresh and upgrade disposable PostgreSQL migrations
- [ ] Focused uniqueness/CAS/isolation tests
- [ ] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-DATABASE-002` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

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

### Supersession Record

Superseded before execution by the agreed ARCH-038 consolidation: DATABASE-001 persists both LIVE and PREVIEW contexts in one `CommerceModelPolicy` model. Do not claim or execute this historical definition; downstream Preview task dependencies now reference DATABASE-001.
