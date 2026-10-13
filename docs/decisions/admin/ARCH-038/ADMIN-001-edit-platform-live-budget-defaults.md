---
id: ARCH-038-ADMIN-001
architecture_id: ARCH-038
title: Manage Platform LIVE CommerceAgent budgets
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-038-DATABASE-001
enables:
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-13
---
# Manage Platform LIVE CommerceAgent budgets

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_admin`
- Repository: `moda-interact-admin`

## Objective

Expose centrally audited LIVE CommerceAgent Platform deadline/output-token defaults in System Controls → Platform Policy.

## Context

The existing Platform Policy page edits billing/recovery safeguards. CommerceAgent execution controls belong in a clearly separated section backed by distinct LIVE data storage.

## Scope

- Add two well-labelled LIVE CommerceAgent fields, effective environment and informative field descriptions to the existing Admin Platform Policy screen.
- Implement SUPER_ADMIN-only server reads and version-checked writes using DATABASE-001 schema.
- Record mandatory audit reason, actor and changed values in same durable mutation.
- Handle missing defaults, stale edits, validation errors and double-submit safely.

## Out of Scope

- Do not add LIVE budgets to PlatformBillingPolicy or change its validation rules.
- Do not expose these controls to merchants or edit Preview budgets.

## Requirements

- Deadline means total turn milliseconds, tokens means per model call; both required positive safe integers.
- Server validates operational feasibility against documented Background execution envelope; unresolved envelope limitations must be raised rather than silently clipped.
- Required default persists and is shown with provenance and version.

## Work Items

- [ ] Add Admin read/mutation path using accepted database schema.
- [ ] Extend existing Platform Policy UI with bounded fields and descriptions.
- [ ] Add authentication, audit, CAS, double-submit and error regression tests.

## Interfaces / Contracts

Consumes ARCH-038-DATABASE-001 LIVE Platform row. Does not modify Shared or merchant-facing applications.

## Dependencies

- `ARCH-038-DATABASE-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Only authorised SUPER_ADMIN can save; audit is transactional.
- [ ] Invalid/stale inputs render actionable errors without partial writes.
- [ ] Changing Platform default does not mutate Plan, Merchant or Preview overrides.

## Validation

- [ ] Focused admin action and component tests
- [ ] Relevant typecheck/lint/build scripts
- [ ] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-ADMIN-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

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
