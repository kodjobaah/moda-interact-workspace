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
  - ARCH-038-DATABASE-001
  - ARCH-038-COMMERCE-001
enables:
  - ARCH-038-SYSTEM-TEST-002
created: 2026-10-13
updated: 2026-10-13
---
# Execute immutable Studio test execution policies

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_commerce`
- Repository: `moda-interact-commerce`

## Objective

Resolve the selected Studio policy source at Test Conversation creation and execute all its turns using a fixed, validated budget with consistent logging and bounded run lifecycle.

## Context

Recent Preview debugging exposed separate logged versus actual output-token values and a 120-second Redis reservation lifetime. COMMERCE-001 adds saved PREVIEW, read-only effective LIVE and temporary CUSTOM policy selection; execution must remain consistent across these paths and follow-up turns.

## Scope

- At **Start Conversation**, validate the authorised selected Shop and selected source: (a) saved PREVIEW Shop-over-Platform, (b) explicit read-only effective LIVE Merchant-over-Price-Plan-over-Platform, or (c) temporary custom budget. Do not permit accidental fallback between LIVE and PREVIEW contexts; fail closed for missing/invalid policy and unknown persisted schema versions.
- For custom source validate `deadlineMs`, `outputTokens`, `modelSteps` and `remoteCalls` as supported positive safe integers and against actual provider, runner, Redis reservation and termination feasibility. Do not persist custom values in `CommerceModelPolicy`, `CommerceAuditEvent` or another permanent configuration store; bounded Preview session state may retain the snapshot for recovery.
- For PREVIEW/LIVE sources, resolve two policy-controlled fields (`deadlineMs`, `outputTokens`) and preserve current test-runner defaults for `modelSteps` and `remoteCalls` (these are **not** DB policy keys under schema version 1).
- Freeze exact effective `deadlineMs`, `outputTokens`, `modelSteps`, `remoteCalls`, mode, field sources and applicable policy versions in the isolated Test Conversation at creation; each admitted run consumes that frozen snapshot for execution, reservation/timeout control and structured logging. Changed UI inputs, saved policy rows and LIVE plan changes affect only newly created Test Conversations.
- Reconcile configured deadline with Redis reservation lifetime (currently 120 seconds) and cancellation/reconciliation/retry behaviour.
- Maintain existing adaptive status polling as presentation only, with no budget changes on polling.
- Add tests for page rerenders, conversation reuse, run duplication, custom input tampering, selected-Shop authorisation and policy/plan changes during a conversation.

## Out of Scope

- Do not perform LIVE customer workflow execution, LIVE policy writes or changes to the Background resolver; the **explicit read-only Studio simulation** may resolve the LIVE budget for a trusted Shop.
- Do not alter Shared budget constraints or Admin LIVE UI.

## Requirements

- No discrepancy between RUNNER_STARTED and Shared commerce.turn.started budget values.
- Invalid over-reservation deadline gives actionable validation, not a permanently RUNNING run.
- On retry/reconciliation and subsequent turns in the same Test Conversation, reuse the same effective budget snapshot. A new selection requires starting a new conversation.
- Preview policy cannot affect actual Background calls.

## Work Items

- [ ] Implement all three policy-source resolvers/validators and conversation-level immutable snapshot wiring, including authorised read-only LIVE inspection and temporary custom budget acceptance.
- [ ] Tie timeout/reservation checks to effective deadline.
- [ ] Add focused runtime, cross-context isolation, concurrent edit, long-lived conversation, custom no-persistence, error and polling regressions.

## Interfaces / Contracts

Consumes DATABASE-001 `CommerceModelPolicy` (PREVIEW persisted read and explicitly requested LIVE read-only resolution), COMMERCE-001 typed Start Conversation policy selection, existing Shared runner and Redis Preview session/run state. No new database field or Shared runner API.

## Dependencies

- `ARCH-038-DATABASE-001`
- `ARCH-038-COMMERCE-001`

## Enables

- `ARCH-038-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Exact effective values appear in logs and runner input.
- [ ] Run terminal status remains durable under timeout/cancel/retry.
- [ ] Changes to saved policy, merchant LIVE plan/policy or custom controls affect **new Test Conversations only**; existing conversation follow-ups, retries and run logs retain their original selected source and four runner limits.
- [ ] Custom mode never writes policy or audit rows; explicit LIVE mode reads effective policy only, remains inside Preview execution and never changes live customer turns.
- [ ] Invalid or impossible custom limits fail before a conversation starts, with a visible actionable error.

## Validation

- [ ] Focused Preview service/reservation/runner integration tests for saved PREVIEW, read-only LIVE and custom modes
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
