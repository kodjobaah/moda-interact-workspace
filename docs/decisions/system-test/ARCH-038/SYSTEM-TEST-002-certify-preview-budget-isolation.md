---
id: ARCH-038-SYSTEM-TEST-002
architecture_id: ARCH-038
title: Certify Studio Preview policy isolation and run snapshots
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 71
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-038-DATABASE-002
  - ARCH-038-COMMERCE-001
  - ARCH-038-COMMERCE-002
enables: []
created: 2026-10-13
updated: 2026-10-13
---
# Certify Studio Preview policy isolation and run snapshots

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_system_test`
- Repository: `moda-interact-system-test`

## Objective

Independently certify Studio Preview policy inheritance, immutable run-budget snapshots, terminal lifecycle and isolation from LIVE budgets.

## Context

Studio Preview has its own Redis reservation and may run long model calls; display-only polling must not become an execution or policy mutation path.

## Scope

- Create isolated test Platform/Shop PREVIEW policies and contrasting LIVE rows.
- Exercise Preview run admissions with Shop inheritance and mixed overrides, including an in-flight policy change.
- Validate terminal expiration/cancel/retry and logs, including reservation versus deadline consistency.
- Verify UI polling configuration does not appear in run-admission payload.

## Out of Scope

- No modifications to LIVE policy or production-path workers.

## Requirements

- A Preview change must not affect a Background LIVE turn and vice versa.
- Runs launched before a policy change keep their exact snapshot.
- Run logs and execution show identical selected budgets and sources.

## Work Items

- [ ] Create isolated fixtures and run contract tests.
- [ ] Exercise long-running/terminal status and polling cases.
- [ ] Record logs and evidence references with cleanup.

## Interfaces / Contracts

Terminal architecture certification of DATABASE-002 + COMMERCE-001/002.

## Dependencies

- `ARCH-038-DATABASE-002`
- `ARCH-038-COMMERCE-001`
- `ARCH-038-COMMERCE-002`

## Enables

None

## Acceptance Criteria

- [ ] Platform/shop test inheritance and isolation pass.
- [ ] No orphan RUNNING states after terminal deadline or cancellation.
- [ ] Evidence is complete and reproducible.

## Validation

- [ ] Integrated PostgreSQL/Redis Preview matrix
- [ ] UI/HTTP polling and terminal-run tests
- [ ] Isolation/correlation evidence audit
- [ ] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-SYSTEM-TEST-002` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

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
