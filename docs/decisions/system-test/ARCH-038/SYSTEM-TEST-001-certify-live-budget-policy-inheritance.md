---
id: ARCH-038-SYSTEM-TEST-001
architecture_id: ARCH-038
title: Certify LIVE execution budget precedence and runtime
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-038-DATABASE-001
  - ARCH-038-ADMIN-001
  - ARCH-038-ADMIN-002
  - ARCH-038-ADMIN-003
  - ARCH-038-BACKGROUND-001
enables: []
created: 2026-10-13
updated: 2026-10-13
---
# Certify LIVE execution budget precedence and runtime

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_system_test`
- Repository: `moda-interact-system-test`

## Objective

Independently certify Admin-controlled LIVE Platform/Price Plan/Merchant limits through real Background CommerceAgent admission and Shared execution.

## Context

LIVE policy is cross-repository and must be verified after implementation acceptance and the developer manual checkpoint, rather than used to gate implementation.

## Scope

- Use disposable seeded shops, subscriptions, pricing plans and policy rows; exercise different effective deadline/token sources.
- Verify SUPER_ADMIN-only writes and no merchant-facing mutation; test cross-tenant isolation.
- Run Background black-box execution or the closest available integrated contract harness including timeout/snapshot behaviours.
- Capture evidence, exact commands, fixture IDs, failures and cleanup.

## Out of Scope

- Do not modify production business implementation while testing.
- No dependency from implementation tasks back to this task.

## Requirements

- Validate independent per-field precedence and missing/current/inactive/pending subscription cases.
- Check plan change and concurrent admin mutation do not alter in-flight turn budgets.
- Verify no silent deadline cap/lease mismatch; require corrected owning implementation if failing.

## Work Items

- [ ] Prepare disposable fixtures and integrated harness.
- [ ] Execute precedence, authorisation, isolation and deadline matrix.
- [ ] Record and review reproducible evidence.

## Interfaces / Contracts

Terminal architecture certification of DATABASE-001 + ADMIN-001/002/003 + BACKGROUND-001.

## Dependencies

- `ARCH-038-DATABASE-001`
- `ARCH-038-ADMIN-001`
- `ARCH-038-ADMIN-002`
- `ARCH-038-ADMIN-003`
- `ARCH-038-BACKGROUND-001`

## Enables

None

## Acceptance Criteria

- [ ] All mandated LIVE cases pass with reproducible evidence.
- [ ] No cross-tenant budget leakage; no unauthorised merchant edits.
- [ ] Effective value and provenance agree between policy, runtime and logs.

## Validation

- [ ] Integrated PostgreSQL/Background LIVE policy matrix
- [ ] Auth/isolation/plan-change regression
- [ ] Artifact and evidence audit
- [ ] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-SYSTEM-TEST-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

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
