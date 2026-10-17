---
id: ARCH-038-COMMERCE-003
architecture_id: ARCH-038
title: Retire environment-based Studio Preview execution budgets
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-17T12:10:03Z
attempt: 2
depends_on:
  - ARCH-038-COMMERCE-002
enables:
  - ARCH-038-SYSTEM-TEST-002
created: 2026-10-16
updated: 2026-10-17
---
# Retire environment-based Studio Preview execution budgets

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_commerce`
- Repository: `moda-interact-commerce`

## Objective

Remove the two obsolete server-side Preview execution-budget environment overrides after Studio's dedicated Preview execution controls and immutable conversation budget snapshots are accepted, leaving one authoritative selection path.

## Context

ARCH-038-COMMERCE-001 already owns `src/studio/test-conversations/preview-execution-limits.tsx`, composed beside the existing Test Conversations browser polling controls. ARCH-038-COMMERCE-002 owns the server-side source resolution, per-conversation immutable snapshot and actual runner limits. The remaining legacy `readPreviewRunBudgets()` parser currently reads `COMMERCE_PREVIEW_RUN_DEADLINE_MS` and `COMMERCE_PREVIEW_RUN_OUTPUT_TOKENS` at Preview service initialisation. Those names must not silently override the approved Preview policy selection.

## Scope

- Remove `COMMERCE_PREVIEW_RUN_DEADLINE_MS` and `COMMERCE_PREVIEW_RUN_OUTPUT_TOKENS` from Commerce runtime reads, `.env.example`, deployment/configuration documentation and relevant environment-configuration tests. Do not add aliases or alternative environment names.
- Remove obsolete `readPreviewRunBudgets()`/environment parsing and the tests dedicated solely to that parsing. Keep or relocate the canonical `DEFAULT_PREVIEW_RUN_BUDGETS` and reservation-compatible limit constants where still used by validated server/runtime policies and tests; do not delete execution budget enforcement itself.
- Update `lib/preview/runtime.ts` and relevant `PreviewService` construction so a process-wide environment budget can no longer override the selected Test Conversation snapshot. Preserve authorised policy-source resolution, immutable per-conversation budgets, and the configured Preview runner, cancellation, retry and terminal reservation behaviour.
- Add regression tests setting both retired environment variables to values that differ sharply from saved PREVIEW, read-only LIVE simulation and CUSTOM selections. Each must prove the environment is ignored and the selected source/limits reach the actual runner unchanged.
- Confirm that `PreviewExecutionLimits` remains the separate React component integrated with the existing Test Conversations controls, and polling intervals still affect only browser reconciliation.
- Update only Commerce-owned documentation and tests relevant to this removal. No `docs/decisions/**/_index.md` changes in this session.

## Out of Scope

- Do not implement or duplicate the UI/editor/server snapshot mechanism owned by COMMERCE-001 and COMMERCE-002.
- Do not modify Background LIVE budget policies, Admin policy editing, `CommerceModelPolicy` schema/migrations, merchant-facing configuration, provider credentials or Shared runner APIs.
- Do not turn execution budgets into browser-only limits; server validation remains authoritative.

## Requirements

- The only supported Studio Preview execution-budget sources remain **Saved Studio Preview** (default), explicitly selected **Effective LIVE policy (read-only simulation)**, and **Custom test policy**, as implemented by the predecessor tasks. No implicit LIVE fallback or extra environment precedence.
- `deadlineMs` and `outputTokens` use the exact values validated at Test Conversation creation, with `modelSteps` and `remoteCalls` frozen for that conversation. Retry, follow-up messages and polling do not read the deleted environment variables.
- Maintain existing defaults (`60_000` ms, `1200` tokens, four model steps, four remote calls) only where appropriate for runner defaults/advanced test input. A mandatory persisted PREVIEW default missing or invalid must remain an explicit failure; do not mask it with process defaults.
- Preserve server-enforced feasibility for Redis reservation, cancellation and provider/model limits. No silent clamping or unbounded custom execution.
- No change to LIVE customer execution, merchant policy access or tenant isolation.

## Work Items

- [x] Remove the two environment-variable reads/declarations and the legacy environment-budget parser/test fixtures.
- [x] Keep approved default and reservation validation constants while removing process-wide `runBudgets` precedence from Preview composition and service execution.
- [ ] Add saved PREVIEW, read-only LIVE simulation and CUSTOM tests proving supplied legacy variables are ignored in actual runner input, including subsequent turns and retry.
- [x] Validate existing `PreviewExecutionLimits`/polling separation and update configuration documentation without introducing alternative variables.

## Interfaces / Contracts

Consumes the typed authorised Test Conversation policy source input from `ARCH-038-COMMERCE-001` and the immutable budget snapshot/runner handoff from `ARCH-038-COMMERCE-002`. Uses existing `CommerceModelPolicy` (PREVIEW and explicitly requested LIVE reads only) without schema changes. Removes `COMMERCE_PREVIEW_RUN_DEADLINE_MS` and `COMMERCE_PREVIEW_RUN_OUTPUT_TOKENS` as runtime configuration contracts.

## Dependencies

- `ARCH-038-COMMERCE-002`

## Enables

- `ARCH-038-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] No production Commerce Preview code reads either retired variable; no supported `.env.example`/deployment configuration advertises them.
- [x] Setting either retired variable changes neither resolved Preview budgets nor Shared runner inputs in all three modes, as verified by the added runner-input/log assertions.
- [x] Persisted PREVIEW and explicit LIVE simulation fail closed when mandatory policy is missing or unsafe; regression tests verify admission is not claimed.
- [ ] CUSTOM values and selected source are frozen at conversation start and remain stable through subsequent turns, retries, cancellation and reconciliation; no new policy/audit row is written for custom values. Retry-specific legacy-environment regression remains outstanding.
- [x] Server-side deadline/reservation feasibility, cancellation, terminal state and output-token limits remain enforced; no UI control circumvents validation.
- [x] Polling interval controls remain browser-only and independent of the `PreviewExecutionLimits` component.

## Validation

- [ ] Preview runtime, source selection, retry/snapshot and negative configuration regression tests
- [x] Existing Test Conversations component/screen and polling tests
- [x] Repository-prescribed typecheck, changed-file ESLint and production build
- [x] `rg` evidence for retired variable names (only explicit negative tests or historical documentation may remain)
- [x] `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and Validation are complete, set the task to `review`, update its Completion Report, return control for authorised review and STOP. Do not implement any enabled follow-on task.

## Implementation Notes

- Use a launcher-resolved dedicated parent and implementation worktree; record task isolation, synchronisation, recursive submodule and validation evidence in the Completion Report.
- Check the actual installed Commerce scripts and task prerequisites before running validation.
- At initial authorship this was a portable definition and made no claim to create Git branches or commits. It was materialised before Attempt 1 in the canonical parent task worktree recorded below.
- No `docs/decisions/**/_index.md` edits until the developer explicitly ends the architectural session.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-17T12:10:03Z. Attempt 1 review history is preserved below.

### Files Changed

- `.env.example`
- `lib/preview/runtime.ts`
- `src/commerce/preview/run-budgets.ts`
- `src/commerce/preview/service.ts`
- `tests/arch038-retired-preview-env.test.ts`
- `tests/preview-run-budgets.test.ts`
- `tests/preview-service.test.ts`

### Work Completed

- Removed the retired `COMMERCE_PREVIEW_RUN_DEADLINE_MS` and `COMMERCE_PREVIEW_RUN_OUTPUT_TOKENS` settings from the supported example configuration and replaced them with documentation of server-side policy selection and browser-only polling.
- Removed `readPreviewRunBudgets()` and process-wide `runBudgets` injection from Preview runtime/service composition. Preserved default runner inputs and reservation/provider feasibility limits; selected saved Preview, LIVE simulation, and CUSTOM policies remain validated and frozen per conversation.
- Added three-mode regressions asserting exact frozen budgets reach runner input/logging despite conflicting environment values, same-ID replay/policy edits do not re-resolve policy, later turns and replay do not change limits, and missing/unsafe persisted policies fail closed. Added CUSTOM cancellation coverage.
- One required case is not implemented: a failed run followed by retry while the legacy environment values change. The existing tests exercise additional turns and cancellation, but do not establish this retry path.

### Validation Results

- `npm run test -- tests/arch038-retired-preview-env.test.ts tests/preview-run-budgets.test.ts tests/preview-service.test.ts tests/preview-integration.test.ts tests/preview-routes.test.ts`: passed, 5 files and 54 tests.
- `npm run test -- tests/test-conversations-component-boundaries.test.ts tests/arch038-preview-execution-limits.test.tsx tests/test-conversations-client.test.ts tests/test-conversations-screen.test.tsx`: passed, 4 files and 38 tests. The screen/component assertions cover polling separation.
- `npm run typecheck`: passed.
- Changed-file ESLint (`lib/preview/runtime.ts`, `src/commerce/preview/run-budgets.ts`, `src/commerce/preview/service.ts`, and the three changed Preview test files): passed with no output/errors.
- `npm run build`: passed, including schema/manual/runtime packaging and smoke checks, Prisma generation, and Next.js production compilation. Existing Nunjucks dynamic-dependency warnings remain.
- Repository scan for both retired environment names and `readPreviewRunBudgets`/`runBudgets`: only explicit negative-environment tests in `tests/arch038-retired-preview-env.test.ts` matched.
- `git diff origin/main...HEAD --check`: passed.
- Retry-specific environment-invariance coverage is not present; review is therefore Changes Requested despite the passing checks above.

### Deviations

The task's third Work Item and the retry portion of the CUSTOM immutability Acceptance Criterion remain incomplete. No unrelated changes were made.

### Assumptions

None

### Unresolved Issues

Add a focused regression that causes a run to fail, retries within the same frozen conversation using the supported retry flow, changes both retired environment variables between attempts, and asserts the original selected source and exact limits reach the actual Shared runner unchanged. Cover a policy-backed mode and CUSTOM if the retry path distinguishes them; otherwise table-drive all three modes. Then rerun the focused Preview tests and update this report.

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

## Developer Self-Review - Changes Requested (Attempt 1)

### Review Status

Changes Requested. The implementation and required focused validations are otherwise sound, but the explicit requirement to prove that a retry retains the conversation's selected policy despite changes to both retired environment variables is not covered by the submitted regression tests. The current test covers later turns, replay, and CUSTOM cancellation, which do not substitute for a failed-run retry.

### Required Correction

Add the retry regression described under `Unresolved Issues`: first complete a run as failed, then retry through the supported same-conversation flow after changing both environment values. Assert the retry's actual runner inputs and policy-source diagnostics still match the original frozen snapshot. Keep the change within this task's Commerce-owned files and rerun the focused Preview tests.

### Attempt and Claim State

Attempt 1 remains recorded. The task returns to `ready` with `executor: null` and `claimed_at: null`; the next developer claim increments to Attempt 2. No implementation source or test file was changed during this reconciliation.

### Worktree and Publication Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-COMMERCE-003`, branch `task/ARCH-038-COMMERCE-003`; launcher claim commit `b446bed146cceb541745100de05d01eca744867d` is pushed. Parent was clean before this report update.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-COMMERCE-003`, branch `task/ARCH-038-COMMERCE-003`; implementation commit `c6ec79b9a1151fc5334e464748e71fd04c73c673` matches `origin/task/ARCH-038-COMMERCE-003` and is pushed. Worktree was clean after validation.
- Implementation start base was `origin/main` commit `c83835463d303ed36b3c4d2f9b96a79435c58c81`; recursive submodule sync/init passed and `database` is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`.
- No merge to `main` was performed. No assigned-agent assistance was used.
