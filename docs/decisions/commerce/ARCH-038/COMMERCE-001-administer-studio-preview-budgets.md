---
id: ARCH-038-COMMERCE-001
architecture_id: ARCH-038
title: Manage isolated Studio Preview Platform and Shop test budgets
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
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
  - ARCH-038-COMMERCE-002
  - ARCH-038-SYSTEM-TEST-002
created: 2026-10-13
updated: 2026-10-13
---
# Manage isolated Studio Preview Platform and Shop test budgets

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_commerce`
- Repository: `moda-interact-commerce`

## Objective

Provide authorised Studio controls for persisted Platform Preview defaults and optional selected-Shop Preview overrides.

## Context

Current Test Conversations polling settings are browser-only; those are not execution budgets. Existing Preview deadline/output settings are environment-driven and must move to durable `CommerceModelPolicy` rows filtered by `context=PREVIEW`.

## Scope

- Extend Commerce Studio Agent Configuration/Test Conversations with a clearly labelled PREVIEW budget section for Platform and selected Shop test overrides.
- Add authorised server actions/API reading/updating only `context=PREVIEW` policy rows, validating `budgetSchemaVersion=1`, sparse JSON budget keys, audit reason and edit-version fencing.
- Show effective values and their independent source; allow clearing each Shop test override to inherit Platform.
- Preserve current polling interval controls as a separate browser-only configuration.

## Out of Scope

- No LIVE Admin Platform/Plan/Merchant edits, no Background or Shared changes.
- No merchant-facing capability to change execution budgets.

## Requirements

- Studio SUPER_ADMIN/authorised platform operator is required for mutation, with server-side check.
- Preview model authorisation and selected Shop tenant scope remain enforced.
- Values displayed are for testing only and never modify live customer budgets.
- Existing dev env vars are documented as migration/bootstrap defaults, not a permanent hidden extra precedence.

## Work Items

- [ ] Add scoped Preview policy read/mutation surface.
- [ ] Integrate UI and effective source/provenance labels.
- [ ] Add auditing, validation, CAS, auth and independent-field inheritance tests.

## Interfaces / Contracts

Consumes DATABASE-001 `CommerceModelPolicy` filtered to `context=PREVIEW` (PLATFORM/SHOP), versioned JSONB budget; leaves existing Studio run-admission payload contract and polling config independent.

## Dependencies

- `ARCH-038-DATABASE-001`

## Enables

- `ARCH-038-COMMERCE-002`
- `ARCH-038-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] A test-Shop override changes only the selected Shop Preview scope.
- [ ] Each budget key can be cleared independently by omission; no explicit JSON null or empty override row.
- [ ] Live policy remains unchanged and unauthorised writes are rejected.

## Validation

- [ ] Focused Studio configuration actions and UI tests
- [ ] Relevant typecheck/lint/build scripts
- [ ] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-COMMERCE-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

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
