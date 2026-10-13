---
id: ARCH-038-COMMERCE-002
architecture_id: ARCH-038
title: Resolve and snapshot Studio Preview execution budgets
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-038-DATABASE-002
  - ARCH-038-COMMERCE-001
enables:
  - ARCH-038-SYSTEM-TEST-002
created: 2026-10-13
updated: 2026-10-13
---
# Resolve and snapshot Studio Preview execution budgets

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_commerce`
- Repository: `moda-interact-commerce`

## Objective

Execute every Studio Test Conversation against its immutable effective Preview policy, with consistent logging and bounded run lifecycle.

## Context

Recent Preview debugging exposed separate logged versus actual output-token values and a 120-second Redis reservation lifetime. Those invariants must be tested together.

## Scope

- Resolve selected Shop PREVIEW override > Preview Platform per field using trusted environment and Shop ID.
- Freeze exact effective `deadlineMs`, `outputTokens`, source/version at run admission/start and use the same values for execution, reservation/timeout control and structured logging.
- Reconcile configured deadline with Redis reservation lifetime (currently 120 seconds) and cancellation/reconciliation/retry behaviour.
- Maintain existing adaptive status polling as presentation only, with no budget changes on polling.
- Add tests for page rerenders, run duplication and policy changes during a run.

## Out of Scope

- Do not resolve LIVE Plan or Merchant policy.
- Do not alter Shared budget constraints or Admin LIVE UI.

## Requirements

- No discrepancy between RUNNER_STARTED and Shared commerce.turn.started budget values.
- Invalid over-reservation deadline gives actionable validation, not a permanently RUNNING run.
- On retry/reconciliation, reuse the same effective budget snapshot.
- Preview policy cannot affect actual Background calls.

## Work Items

- [ ] Implement Preview resolver and run snapshot wiring.
- [ ] Tie timeout/reservation checks to effective deadline.
- [ ] Add focused runtime, concurrent mutation, error and polling regressions.

## Interfaces / Contracts

Consumes DATABASE-002 PREVIEW schema and existing Shared runner, Redis run state and Test Conversation actions.

## Dependencies

- `ARCH-038-DATABASE-002`
- `ARCH-038-COMMERCE-001`

## Enables

- `ARCH-038-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Exact effective values appear in logs and runner input.
- [ ] Run terminal status remains durable under timeout/cancel/retry.
- [ ] Changes to test policy affect new runs only.

## Validation

- [ ] Focused Preview service/reservation/runner integration tests
- [ ] Redis-backed regression for long run and policy change
- [ ] Relevant typecheck/build and git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-COMMERCE-002` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

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
