---
id: ARCH-021-COMMERCE-011
architecture_id: ARCH-021
title: Build Agent Configuration shell and platform model UI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 70
executor: copilot
claimed_at: 2026-09-23T17:52:51Z
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-006
  - ARCH-021-COMMERCE-007
enables:
  - ARCH-021-COMMERCE-012
  - ARCH-021-COMMERCE-013
  - ARCH-021-COMMERCE-014
created: 2026-09-23
updated: 2026-09-23
---

# Build Agent Configuration shell and platform model UI

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Create the dedicated production Agent Configuration Studio route/module and implement the platform model-catalogue/default-model UI against the accepted model configuration service.

## Context

Phase 2 introduces Agent Configuration as a dedicated Studio domain. The previous COMMERCE-011 definition bundled model management, prompt-template management and platform prompt authoring into one UI task even though those are independently useful capabilities with different service dependencies. This task establishes only the shared Agent Configuration shell plus the platform model surface. Template and prompt authoring are separate COMMERCE-013/014 tasks; shop overrides remain COMMERCE-012.

COMMERCE-006 remains an explicit dependency because it established the accepted Phase 1 production Studio shell/workspace composition extended by this route.

## Scope

- Add a clear `Agent Configuration` entry to production Studio navigation and a dedicated route/surface.
- Show the current environment as server-derived context, not a client-selectable authorization parameter.
- Establish the dedicated Agent Configuration domain screen/module used by later Phase 2 UI tasks.
- Model section only:
  - list catalogue entries and provider/model/display/enabled state;
  - create an entry;
  - update mutable display metadata;
  - enable/disable entries;
  - select/change the platform default model with accepted replay/conflict/unknown-outcome reconciliation.
- Display safe stable model ids/provider model ids useful for later preview validation.
- Keep `StudioWorkspace` as shell/navigation/orchestration only for this surface.
- ADMIN remains read-only; SUPER_ADMIN gets mutation controls outside development bypass.

## Out of Scope

- Prompt-template category/library UI; owned by ARCH-021-COMMERCE-013.
- Platform prompt authoring/history/activation UI; owned by ARCH-021-COMMERCE-014.
- Shop model/prompt override controls; owned by ARCH-021-COMMERCE-012.
- Feature prompt removal.
- Model execution/test chat.
- Live provider calls.
- Grant/manifest/Background changes.
- Merchant access.

## Requirements

- Production composition must use the COMMERCE-007 production server port, never fixture ports.
- Agent Configuration domain state, mutation orchestration and model dirty/CAS handling must live outside `StudioWorkspace`; the workspace may select/render the domain surface and pass shared navigation/shop context only.
- Refactoring is incremental: do not move unrelated existing Studio domain logic solely to reduce line count.
- Disabled models remain identifiable in current/historical state but cannot be chosen for new selections where COMMERCE-007 rejects them.
- Mutation UI must surface accepted replay/conflict/unknown outcomes without inventing another mutation state model.
- No provider API key, access token or secret configuration is rendered.

### Deterministic file boundary

Create/use these primary UI locations:

```text
app/agent-configuration/page.tsx
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/platform-model-configuration.tsx
components/production-studio-page.tsx
components/studio-shell.tsx
components/studio-workspace.tsx
tests/agent-configuration-model-ui.test.tsx
```

`components/studio-workspace.tsx` may only gain the `agent-configuration` surface discriminator/render handoff and shared navigation plumbing. Model editor state and mutation orchestration must live under `src/studio/agent-configuration/`. Additional helper components are permitted only under that directory. Do not opportunistically extract unrelated Tools/Releases/Explore/Features code.

## Work Items

- [x] Add production Agent Configuration route/navigation entry.
- [x] Establish the dedicated Agent Configuration page/domain component boundary outside `StudioWorkspace`.
- [x] Compose model catalogue/default UI against COMMERCE-007.
- [x] Add accepted replay/conflict/unknown-outcome presentation for model mutations.
- [x] Add focused route/UI/auth tests proving production ports rather than fixtures.

## Interfaces / Contracts

Consumes:

- model configuration port from ARCH-021-COMMERCE-007;
- accepted production Studio shell composition from ARCH-021-COMMERCE-006.

Produces the shared Agent Configuration UI/module shell and platform model surface that COMMERCE-012, COMMERCE-013 and COMMERCE-014 extend.

## Dependencies

- ARCH-021-COMMERCE-006
- ARCH-021-COMMERCE-007

## Enables

- ARCH-021-COMMERCE-012
- ARCH-021-COMMERCE-013
- ARCH-021-COMMERCE-014

## Acceptance Criteria

- [x] Production Studio exposes an Agent Configuration surface backed by the real COMMERCE-007 model service.
- [x] Platform admins can list/create/update/enable/disable catalogue entries and select the platform default model.
- [x] ADMIN is read-only and secrets are never rendered.
- [x] Model mutation replay/conflict/unknown outcomes use accepted Studio behaviour.
- [x] Agent Configuration state/actions are not implemented inline inside `StudioWorkspace`; unrelated Studio domains are not opportunistically rewritten.
- [x] No prompt/template authoring or model/provider execution is introduced.

## Validation

- [x] focused Agent Configuration route/component tests
- [x] model/default mutation UI tests
- [x] production-port composition regression
- [x] targeted lint/typecheck
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-012, COMMERCE-013 or COMMERCE-014.

## Implementation Notes

Do not perform a wholesale `StudioWorkspace` rewrite. Extract only the Agent Configuration shell/model boundary introduced by this task.

Do not remove the legacy capability prompt field in this task; the current ARCH-020 preview/runtime still depends on it until later ARCH-021 runtime migration.

## Completion Report

### Status

Ready for architect review

### Files Changed

- `app/agent-configuration/page.tsx`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/platform-model-configuration.tsx`
- `components/production-studio-page.tsx`
- `components/studio-shell.tsx`
- `components/studio-workspace.tsx`
- `app/styles.css`
- `src/studio/agent-configuration/model-contracts.ts`
- `src/studio/agent-configuration/model-server-actions.ts`
- `tests/agent-configuration-model-ui.test.tsx`

### Work Completed

- Added the production Agent Configuration route and navigation entry.
- Added a dedicated Agent Configuration screen and platform model catalogue/default UI outside the legacy workspace state machine.
- Composed the real COMMERCE-007 server actions for catalogue listing, creation, metadata updates, enablement and platform default selection.
- Kept ADMIN read-only, preserved disabled current pointers, displayed stable provider/model identities, and rendered no credentials or secret configuration.
- Added accepted unknown-outcome replay using the original operation ID and CAS conflict messaging.
- Routed only the new surface discriminator through `StudioWorkspace`; unrelated Studio domains were left unchanged.

- Corrected the production handoff so `ProductionStudioPage` passes the real model server actions and trusted server-derived environment through `StudioWorkspace` to the dedicated screen.
- Preserved selected-shop context by accepting route `shopId`, resolving it through `resolveStudioShopSelection`, and passing `shopSelection` into the production shell.
- Added concrete trusted environment display to Agent Configuration.
- Reconciled serializable server-action failures and UI handling for forbidden, not-found, unavailable, stale-CAS, conflicting-replay, and unknown outcomes while preserving operation IDs for reconciliation.
- Kept model state and mutation orchestration under `src/studio/agent-configuration/`; no unrelated Studio domain rewrite or provider execution was introduced.

### Validation Results

- `npx vitest run tests/agent-configuration-model-ui.test.tsx tests/agent-configuration-model.test.ts`: 2 files, 11 tests passed.
- Targeted ESLint over changed route, composition, Agent Configuration, and UI test files: passed.
- `npx next typegen`: passed.
- Task-owned TypeScript paths: no new Agent Configuration diagnostics. Full repository typecheck still reports the pre-existing legacy `StudioWorkspace` diagnostics for duplicate `productionCodePanel`, missing `responseProcessing`, and `StudioFailure.message`.
- `git diff --check`: passed.

### Deviations

The full repository typecheck remains non-zero because of the existing legacy `StudioWorkspace` diagnostics listed above; they are outside the Attempt 2 correction path and were not changed.

### Assumptions

- The accepted COMMERCE-007 model service and Phase 1 shop-selection resolver remain the source of truth for server authorization, environment, and selected-shop context.

### Unresolved Issues

Existing legacy `StudioWorkspace` typecheck diagnostics remain for a later cleanup task.

### Architectural Concerns

None introduced by Attempt 2.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 2 implementation `085ab44` materially corrects the four source defects identified in Attempt 1. Static review confirms that `StudioWorkspace` now consumes the `agentConfigurationActions` handoff, `/agent-configuration` accepts and server-resolves `shopId`, the shared `StudioShell` receives the resolved shop selection, the concrete trusted environment is derived from server configuration and displayed, and the model server-action adapter serializes forbidden, stale-CAS and conflicting-replay lifecycle failures into the accepted model mutation result contract. The client also preserves the exact original `operationId` when reconciling an `unknown` outcome.

The task is not yet acceptable because the mandatory focused validation requested by the Attempt 1 Architect Review was not added. The submitted 11 focused tests are the existing seven COMMERCE-007 model-service tests plus four Agent Configuration UI tests. The new fourth UI test proves only the `StudioWorkspace` handoff and injected environment display; it does not exercise the production route/composition or the production server-action failure adapter.

Attempt 3 is therefore validation-focused. Do not redesign the corrected implementation unless one of these regressions exposes a defect.

1. **Add a production Agent Configuration route/composition regression.** Exercise the production composition boundary (not only `StudioWorkspace` directly) and prove that a URL `shopId` is forwarded/resolved into `StudioShell.shopSelection`, the environment comes from trusted server configuration rather than search/browser input, and the real COMMERCE-007 model server actions are handed to the Agent Configuration surface. This may use module mocks/fakes around the route/composition boundary; it must not require a live provider or external call.

2. **Add focused server-action failure serialization regressions.** Prove that the production model mutation boundary returns explicit serializable results for at least: unauthorized/forbidden mutation, stale CAS (`conflict` / `STALE_CAS`), and conflicting operation replay (`conflict` / `CONFLICTING_REPLAY`). The tests must exercise the server-action adapter or an extracted adapter helper used by those actions; service-only tests that assert thrown `LifecycleError` values are insufficient. Preserve the existing exact-original-operation `unknown` reconciliation regression.

3. **Reconcile the durable task record on resubmission.** Check the completed Work Items, Acceptance Criteria and Validation items and record the Attempt 3 validation commands/results plus launcher-prepared parent/implementation worktree, synchronization and recursive-submodule evidence in the Completion Report. The supplied Attempt 2 ZIP still shows `status: in_progress`, `executor: copilot`, and the older 10-test Completion Report, so the architect cannot treat the claimed parent report `d127379b` as present in this snapshot.

No changes are requested to COMMERCE-007 service semantics, prompt/template UI, shop override behavior, provider execution, or unrelated Studio domains.

### Reviewed Files

- `app/agent-configuration/page.tsx`
- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/platform-model-configuration.tsx`
- `src/studio/agent-configuration/model-contracts.ts`
- `src/studio/agent-configuration/model-server-actions.ts`
- `tests/agent-configuration-model-ui.test.tsx`
- `tests/agent-configuration-model.test.ts`
- Attempt 1 Architect Review correction contract

### Validation Reviewed

- Submitted Attempt 2 report: 11 focused tests passed, targeted ESLint passed, Next type generation passed and `git diff --check` passed.
- Attempt 1 -> Attempt 2 source diff is narrowly scoped to the requested Agent Configuration corrections plus the focused UI test; ignored `tsconfig.tsbuildinfo` is not treated as implementation scope.
- Static inspection verifies the four requested source corrections described above.
- Focused test inventory shows four Agent Configuration UI tests and seven model-service tests; no production route/composition regression exercises `shopId`/trusted environment/real action handoff.
- No focused regression exercises `model-server-actions.ts` serialization of forbidden, stale-CAS or conflicting-replay outcomes.
- The supplied archive contains no installed dependency tree suitable for independently rerunning the submitted test commands in this review environment.

### Architecture Conformance

Source implementation is now directionally conformant with the ARCH-021/COMMERCE-011 boundaries: the dedicated Agent Configuration domain remains outside unrelated Studio state, production uses COMMERCE-007, ADMIN remains read-only in the UI, selected-shop context is preserved, trusted environment context is server-derived, and secrets/provider execution remain out of scope. Acceptance is withheld only because the explicit production-boundary validation contract from Attempt 1 has not been satisfied and the durable task/report state in the supplied snapshot is unreconciled.

### Follow-up

Return the same task to `ready` with `attempt: 2` preserved and no active claim. The next authorized claim becomes Attempt 3. COMMERCE-012, COMMERCE-013 and COMMERCE-014 remain dependency-gated until COMMERCE-011 is architect-accepted Complete.
