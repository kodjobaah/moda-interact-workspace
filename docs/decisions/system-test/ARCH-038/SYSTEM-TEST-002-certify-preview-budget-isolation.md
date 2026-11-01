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
  - ARCH-038-DATABASE-001
  - ARCH-038-COMMERCE-001
  - ARCH-038-COMMERCE-002
  - ARCH-038-COMMERCE-003
enables: []
created: 2026-10-13
updated: 2026-10-16
---
# Certify Studio Preview policy isolation and run snapshots

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_system_test`
- Repository: `moda-interact-system-test`

## Objective

Independently certify all three Studio policy-source modes, conversation-level immutable budgets, terminal lifecycle and isolation from LIVE customer execution.

## Context

Studio Preview has its own Redis reservation and may run long model calls; display-only polling must not become an execution or policy mutation path.

## Scope

- Create `CommerceModelPolicy` rows for PREVIEW Platform/Shop and contrasting LIVE scopes; assert context-scoped reads/writes, JSONB validations and rejection of PREVIEW+PRICE_PLAN.
- Exercise Test Conversation creation for saved PREVIEW, explicit effective LIVE (read-only) and temporary CUSTOM modes, including Shop inheritance and mixed overrides. Confirm LIVE values are copied into Preview state without LIVE writes or live workflow execution.
- Validate terminal expiration/cancel/retry and logs, including reservation versus deadline consistency.
- Verify initial/max polling configuration does not appear in run-admission or execution policy payloads; validate intentional, authorised policy-source selection only at Test Conversation creation.
- Verify no live Preview runtime consumes either retired `COMMERCE_PREVIEW_RUN_DEADLINE_MS` or `COMMERCE_PREVIEW_RUN_OUTPUT_TOKENS`: setting them to conflicting values cannot change effective policy selection, stored snapshot or runner input.
- Exercise the dedicated `PreviewExecutionLimits` React component integrated beside the separate polling controls.
- Exercise Studio Preview policy UI: required Platform fields, Shop Override/Inherit, read-only effective-source summary, audit history, all three policy-source modes, custom field validation/reset, server-side auth, and the independent browser-only polling configuration.

## Out of Scope

- No modifications to LIVE policy or production-path workers.

## Requirements

- A Preview change must not affect a Background LIVE turn and vice versa.
- All runs within an already started Test Conversation keep its exact four-limit policy snapshot despite UI edits, saved PREVIEW policy changes, plan changes or LIVE policy changes.
- Run logs and execution show identical selected budgets and sources.

## Work Items

- [ ] Create isolated fixtures and run contract tests.
- [ ] Exercise long-running/terminal status, all three modes, custom no-persistence and polling cases.
- [ ] Record logs and evidence references with cleanup.

## Interfaces / Contracts

Terminal architecture certification of unified DATABASE-001 + COMMERCE-001/002/003.

## Dependencies

- `ARCH-038-DATABASE-001`
- `ARCH-038-COMMERCE-001`
- `ARCH-038-COMMERCE-002`
- `ARCH-038-COMMERCE-003`

## Enables

None

## Acceptance Criteria

- [ ] Platform/shop test inheritance and isolation pass.
- [ ] No orphan RUNNING states after terminal deadline or cancellation.
- [ ] Evidence is complete and reproducible.
- [ ] Studio Preview editor and audit history show correct per-field inherited/effective values and provenance; LIVE simulation is read-only, custom inputs do not write policy/audit rows, and polling settings never leak into execution.
- [ ] Legacy Preview budget environment variables are ignored even when set, and the separate React component controls only server-authorised, frozen test budgets; polling remains display-only.
- [ ] The three policy modes produce correctly labelled immutable conversation budgets, including `modelSteps`/`remoteCalls`, and existing conversations are unaffected by changes to saved PREVIEW/LIVE policies or UI controls.

## Validation

- [ ] Integrated PostgreSQL/Redis Preview matrix covering saved PREVIEW, read-only LIVE and temporary CUSTOM
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
