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
claimed_at: 2026-10-17T10:29:14Z
attempt: 1
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

- [ ] Remove the two environment-variable reads/declarations and the legacy environment-budget parser/test fixtures.
- [ ] Keep approved default and reservation validation constants while removing process-wide `runBudgets` precedence from Preview composition and service execution.
- [ ] Add saved PREVIEW, read-only LIVE simulation and CUSTOM tests proving supplied legacy variables are ignored in actual runner input, including subsequent turns and retry.
- [ ] Validate existing `PreviewExecutionLimits`/polling separation and update configuration documentation without introducing alternative variables.

## Interfaces / Contracts

Consumes the typed authorised Test Conversation policy source input from `ARCH-038-COMMERCE-001` and the immutable budget snapshot/runner handoff from `ARCH-038-COMMERCE-002`. Uses existing `CommerceModelPolicy` (PREVIEW and explicitly requested LIVE reads only) without schema changes. Removes `COMMERCE_PREVIEW_RUN_DEADLINE_MS` and `COMMERCE_PREVIEW_RUN_OUTPUT_TOKENS` as runtime configuration contracts.

## Dependencies

- `ARCH-038-COMMERCE-002`

## Enables

- `ARCH-038-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] No production Commerce Preview code reads either retired variable; no supported `.env.example`/deployment configuration advertises them.
- [ ] Setting either retired variable changes neither resolved Preview budgets nor Shared runner inputs in any of the three modes.
- [ ] Persisted PREVIEW and explicit LIVE simulation cannot silently fall back to legacy defaults when mandatory configuration is invalid or missing.
- [ ] CUSTOM values and selected source are frozen at conversation start and remain stable through subsequent turns, retries, cancellation and reconciliation; no new policy/audit row is written for custom values.
- [ ] Server-side deadline/reservation feasibility, cancellation, terminal state and output-token limits remain enforced; no UI control circumvents validation.
- [ ] Polling interval controls remain browser-only and independent of the `PreviewExecutionLimits` component.

## Validation

- [ ] Preview runtime, source selection, retry/snapshot and negative configuration regression tests
- [ ] Existing Test Conversations component/screen and polling tests
- [ ] Repository-prescribed typecheck, changed-file ESLint and production build
- [ ] `rg` evidence for retired variable names (only explicit negative tests or historical documentation may remain)
- [ ] `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and Validation are complete, set the task to `review`, update its Completion Report, return control for authorised review and STOP. Do not implement any enabled follow-on task.

## Implementation Notes

- Use a launcher-resolved dedicated parent and implementation worktree; record task isolation, synchronisation, recursive submodule and validation evidence in the Completion Report.
- Check the actual installed Commerce scripts and task prerequisites before running validation.
- This task is **defined but not materialised** in the developer's Git environment; this portable patch does not create task branches or commits.
- No `docs/decisions/**/_index.md` edits until the developer explicitly ends the architectural session.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-17T10:29:14Z. Attempt 0 review history is preserved below.

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
