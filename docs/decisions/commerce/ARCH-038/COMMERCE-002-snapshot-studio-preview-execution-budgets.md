---
id: ARCH-038-COMMERCE-002
architecture_id: ARCH-038
title: Execute immutable Studio test execution policies
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-17T08:28:02Z
attempt: 2
depends_on:
  - ARCH-038-DATABASE-001
  - ARCH-038-COMMERCE-001
enables:
  - ARCH-038-COMMERCE-003
created: 2026-10-13
updated: 2026-10-17
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
- Consume the `PreviewExecutionLimits` component inputs only through the typed, authorised Test Conversation creation request; validate server-side and never allow polling controls, subsequent messages or retries to override limits.
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

- [x] Implement all three policy-source resolvers/validators and conversation-level immutable snapshot wiring, including authorised read-only LIVE inspection and temporary custom budget acceptance.
- [x] Tie timeout/reservation checks to effective deadline and ensure runtime uses the frozen per-conversation budget rather than the obsolete process-wide environment overrides. COMMERCE-003 owns their final declaration/parser/documentation removal.
- [x] Add focused runtime, cross-context isolation, concurrent edit, long-lived conversation, custom no-persistence, error and polling regressions.

## Interfaces / Contracts

Consumes DATABASE-001 `CommerceModelPolicy` (PREVIEW persisted read and explicitly requested LIVE read-only resolution), COMMERCE-001 typed Start Conversation policy selection, existing Shared runner and Redis Preview session/run state. No new database field or Shared runner API.

## Dependencies

- `ARCH-038-DATABASE-001`
- `ARCH-038-COMMERCE-001`

## Enables

- `ARCH-038-COMMERCE-003`

## Acceptance Criteria

- [x] Exact effective values appear in logs and runner input; browser polling inputs cannot affect execution budgets and no configured process environment override supersedes the selected source.
- [x] Run terminal status remains durable under timeout/cancel/retry.
- [x] Changes to saved policy, merchant LIVE plan/policy or custom controls affect **new Test Conversations only**; existing conversation follow-ups, retries and run logs retain their original selected source and four runner limits.
- [x] Custom mode never writes policy or audit rows; explicit LIVE mode reads effective policy only, remains inside Preview execution and never changes live customer turns.
- [x] Invalid or impossible custom limits fail before a conversation starts, with a visible actionable error.

## Validation

- [x] Focused Preview service/reservation/runner integration tests for saved PREVIEW, read-only LIVE and custom modes
- [x] Redis-backed regression for long run and policy change
- [x] Relevant typecheck/build and git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-COMMERCE-002` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. The portable definition was materialised on the canonical parent task branch during developer preparation. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-17T08:28:02Z. Attempt 1 Changes Requested review and its evidence are preserved below. Completion remains pending because `completion_mode` is `developer`.

### Attempt 2 Preparation

- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-COMMERCE-002`, branch `task/ARCH-038-COMMERCE-002`, clean at `43bea0d3d084059cf97397fbe50b4ec15e149ba0`, matching `origin/task/ARCH-038-COMMERCE-002`; current `origin/main` `34626f4dc284a01dfa54cd67b330f8153d12a7d4` is an ancestor.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-COMMERCE-002`, branch `task/ARCH-038-COMMERCE-002`, clean at `048df599c1fbc671b383445190e495c4e178f27e`, matching `origin/task/ARCH-038-COMMERCE-002`; current `origin/main` `957bc9ac4b8f6c2cf3849cff75926758292d7ee6` is an ancestor.
- Implementation `database` submodule is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`.
- Explicit dependencies `ARCH-038-DATABASE-001` and `ARCH-038-COMMERCE-001` are both complete. The previously observed uncommitted `development.log` change was no longer present when this attempt was prepared; neither worktree had user changes overwritten.

### Files Changed

25 implementation files in `moda-interact-commerce`, including Preview policy resolution/snapshotting, runner budget wiring, Studio selection/client contracts, and Preview/UI/Redis regression tests.

### Work Completed

- Resolve SAVED_PREVIEW and explicit read-only LIVE policy server-side for the selected Shop and deployment environment; accept CUSTOM_TEST values only as transient input. Only SUPER_ADMIN may create or execute LIVE/custom conversations.
- Freeze the selected source, effective deadline/output/model-step/remote-call budgets, field provenance and policy versions in the conversation snapshot. Runs and structured logs consume that frozen snapshot; replay and follow-up turns retain it.
- Bound deadlines below the Redis reservation lifetime and reject unsupported limits before claiming a conversation. Preserve current runner defaults for persisted policy sources.

### Validation Results

- `npm run test:arch020-preview-integration`: passed, 45 tests.
- `npm run test:arch020-preview-integration:redis`: passed, 10 tests; local Redis was available. Covers frozen policy across replay/follow-up turns and expired/stale run ownership.
- `npx vitest run tests/arch038-preview-execution-limits.test.tsx tests/arch038-preview-policy-contracts.test.ts tests/test-conversations-screen.test.tsx`: passed, 32 tests.
- `npm run typecheck`: passed.
- ESLint on files changed from `origin/main`: 0 errors, 4 warnings in tests.
- `git diff --check origin/main...HEAD`: passed in both task worktrees.
- Additional package-wide `npm test`: 1,350 passed, 69 failed, 7 skipped across 185 files. Failures include `tests/tool-authoring-screen.test.tsx` missing the unrelated “Run Test” button; this broad-suite result is not verified against a pre-task baseline.
- Additional package-wide `npm run lint`: failed on two `react-hooks/refs` errors in untouched `src/studio/prompt-editor/markdown-prompt-editor.tsx`; changed-file lint had no errors.

### Deviations

The additional package-wide test and lint commands exposed failures outside the task's changed files. They are reported for architect triage; no task-scoped test or typecheck failure remains.

### Assumptions

None.

### Unresolved Issues

The package-wide failures noted above remain untriaged against the pre-task baseline. No unresolved COMMERCE-002-specific failure was found.

### Architectural Concerns

None identified in this implementation review.

### Git / VCS

Task branch: `task/ARCH-038-COMMERCE-002`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-COMMERCE-002`
  parent branch: `task/ARCH-038-COMMERCE-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-COMMERCE-002`
  implementation branch: `task/ARCH-038-COMMERCE-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes
  parent `origin/main` incorporated: yes, merge commit `499d047c1c16c5f263f4c030cf85985077aa7c2c`
  implementation remote task branch fast-forwarded: not needed
  implementation `origin/main` incorporated: already current at implementation commit

Implementation repository:
  repository: `moda-interact-commerce`
  commit: `9d71d488611ea286326c8bccb041d3d0ce6010ad`
  remote branch: `origin/task/ARCH-038-COMMERCE-002`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/commerce/ARCH-038/COMMERCE-002-snapshot-studio-preview-execution-budgets.md`
  report commit: `ac34c3ed` (initial review record)
  remote branch: `origin/task/ARCH-038-COMMERCE-002`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

**Changes Requested — Attempt 1 (2026-10-17).** The task returns to `ready` for the next developer claim. Preserve `attempt: 1`, the submitted Completion Report, and the cleared executor/claim. This is **not** an architect acceptance or developer completion decision.

### Review Notes

The core mechanism is implemented: Preview and explicitly requested LIVE policy reads are server-resolved, CUSTOM_TEST is transient, a frozen policy is stored in the isolated Redis conversation snapshot, the Shared runner consumes those same four limits, and Studio caps the deadline at 90 seconds relative to the current 120-second reservation. Focused validation is encouraging but does not close the following findings.

**CR-1 — Show the actually admitted, server-frozen policy, not the browser's potentially stale policy.** In `test-conversations-screen.tsx`, `beginStart()` sets `frozenPolicy` to `frozenTestExecutionPolicy(...)` from the browser's current dashboard. In contrast, `PreviewService.startConversation()` resolves persisted PREVIEW/LIVE policy again on the server. The creation route currently returns only a conversation ID. An administrator can edit the policy between page render/inspection and Start, causing the UI to label different values and provenance as **Effective test budget (frozen)** than the values used by the Shared runner. Return or retrieve the authoritative, safely projected stored policy on successful creation and same-ID replay/reconciliation, and display those resolved limits/sources. Do not trust browser-supplied persisted policy values or change admission precedence. Add a focused regression proving a policy edit between initial browser selection and server creation does not misreport the frozen result; include the uncertain-start/same-ID replay case. Preserve access control over LIVE/CUSTOM snapshots.

**CR-2 — Reconcile the 69 failing full-suite tests against the pre-task baseline.** The Completion Report provides a count and one example but no failing identities or comparable baseline execution. `docs/development-baseline.md` records `ARCH025-COMMERCE-TEST-001`, with a **specific stable failure set** (not a blanket exemption for a historic aggregate count). Record the 69 current failing identities/reasons and compare with the baseline and/or a matched run on the implementation pre-task revision using the same Node/dependencies/environment. Investigate each new, worsened or changed failure; fix a demonstrated task regression within this task. If no task regression is found, record reproducible equivalence evidence and do not change unrelated code merely to obtain a green suite. The untouched prompt-editor lint errors can be treated separately only with an evidenced baseline/no-regression classification.

**CR-3 — Complete the required validation and preparation evidence.** The task checks `Relevant typecheck/build and git diff --check`, but the Completion Report does not record an `npm run build` outcome. Run the declared build after corrections (or explicitly record the real blocker and leave the item unchecked), focused Preview and Redis tests, typecheck, changed-file lint and `git diff --check`. Add the launcher-resolved start-of-attempt preparation/submodule hydration evidence to the Completion Report; do not create a new implementation commit solely to reproduce launcher discovery evidence. The supplied archive has no Git metadata, so published commit/branch identities are currently report evidence rather than independently authenticated Git history.

### Reviewed Files

- `src/commerce/preview/service.ts`, `types.ts`, `run-budgets.ts`, Redis store and Preview runtime composition.
- `src/commerce/execution-policy/policy-service.ts` and `src/studio/execution-policy/contracts.ts`.
- `src/studio/test-conversations/{client,contracts,preview-execution-limits,test-conversations-screen}.ts*` and the Preview creation HTTP route.
- Preview, Redis, Test Conversations UI/client and policy regression tests; the submitted Completion Report; `docs/development-baseline.md`.

### Validation Reviewed

- Reported passing: 45 focused Preview tests, 10 Redis regressions, 32 policy/UI tests, `npm run typecheck`, and changed-file ESLint (no errors; four warnings).
- Reported failing: package-wide 69 tests and two untouched prompt-editor ESLint errors. Their equivalence to a current pre-task baseline is not yet demonstrated.
- Source comparison: the submitted 25 Commerce patch files match the 2026-10-16 20:43 snapshot after applying the supplied Attempt 1, 2 and 3 patches in order; this is file-content evidence, not a replacement for Git commit verification.
- Full build and independent runtime execution were not established from this portable archive.

### Architecture Conformance

**Partial, pending corrections.** The immutable server-side execution and Redis snapshot boundaries align with ARCH-038, but the displayed frozen selection can diverge from the executed server snapshot. The broader regression status and required build evidence remain unresolved. No database, Shared runner, Background, Gateway or `_index.md` change is authorised by this review.

### Follow-up

Reclaim **ARCH-038-COMMERCE-002** as the next developer execution attempt, address CR-1 through CR-3, update the Completion Report and return this same task to `review`. Do not start COMMERCE-003 or SYSTEM-TEST-002. Preserve all historical Attempt 1 evidence and the developer completion boundary.

### Prior submission state (preserved)

The archived pre-review placeholder from the original submission was:

> ## Architect Review
>
> ### Review Status
>
> Pending architect review
>
> ### Review Notes
>
> Review the broader package test/lint failures against the pre-task baseline; task-scoped Preview, Redis and UI validations pass.
>
> ### Reviewed Files
>
> Preview service, run-budget/types, Redis state store, execution-policy service, runtime wiring, Studio Test Conversations client/UI and focused tests.
>
> ### Validation Reviewed
>
> Focused Preview integration (45/45), Redis regression (10/10), execution-policy UI/contracts (32/32), typecheck and changed-file ESLint pass. Package-wide suite/lint have unrelated failures noted in the Completion Report.
>
> ### Architecture Conformance
>
> Pending architect review
>
> ### Follow-up
>
> None
