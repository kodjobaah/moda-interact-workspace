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
status: complete
priority: 70
executor: null
claimed_at: null
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

Attempt 3 complete; returned to `moda_architect` for review.

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
- `tests/agent-configuration-production.test.tsx`
- `tests/agent-configuration-server-actions.test.ts`

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
- Added a production route/composition regression proving URL `shopId` forwarding, server-validated shop selection, trusted environment derivation, and real action handoff.
- Added server-action adapter regressions for forbidden, stale-CAS, and conflicting-replay outcomes, with JSON serialization assertions.

### Validation Results

- `npx vitest run tests/agent-configuration-production.test.tsx tests/agent-configuration-server-actions.test.ts tests/agent-configuration-model-ui.test.tsx tests/agent-configuration-model.test.ts`: 4 files, 15 tests passed.
- Targeted ESLint over changed route, composition, Agent Configuration, and UI test files: passed.
- `npx next typegen`: passed.
- Task-owned TypeScript paths: no new Agent Configuration diagnostics. Full repository typecheck still reports the pre-existing legacy `StudioWorkspace` diagnostics for duplicate `productionCodePanel`, missing `responseProcessing`, and `StudioFailure.message`.
- `git diff --check`: passed.
- Launcher Attempt 3 preparation: claimed with commit `3a79cc5ea4b36528b1c2180d0b8f1b0e7c3c0fb7`; dependency gate passed; parent and implementation task worktrees synchronized; recursive submodule status ready at database commit `98fdf715e54fe6df92ac6951facd104e410068f2`.

### Deviations

The full repository typecheck remains non-zero because of the existing legacy `StudioWorkspace` diagnostics listed above; they are outside the Attempt 3 validation path and were not changed.

### Assumptions

- The accepted COMMERCE-007 model service and Phase 1 shop-selection resolver remain the source of truth for server authorization, environment, and selected-shop context.

### Unresolved Issues

Existing legacy `StudioWorkspace` typecheck diagnostics remain for a later cleanup task.

### Architectural Concerns

None introduced by Attempt 3.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 implementation `d2d67dd` with parent report `b90718b` satisfies the validation-only correction contract from Attempt 2. No runtime implementation was changed between the submitted Attempt 2 and Attempt 3 snapshots; the Commerce diff adds only `tests/agent-configuration-production.test.tsx` and `tests/agent-configuration-server-actions.test.ts` plus ignored/generated `tsconfig.tsbuildinfo` state.

The production composition regression exercises the real `/agent-configuration` page and `ProductionStudioPage` boundary. It proves URL `shopId` is forwarded to the accepted server-side shop resolver, the resolved selection reaches `StudioShell`, the environment comes from trusted server configuration and is normalized to `STAGING`, and the actual COMMERCE-007 model server-action exports are handed to the Agent Configuration surface.

The server-action regressions exercise `model-server-actions.ts` directly with the production error types. They prove authorization failure serializes to `forbidden`, `CAS_CONFLICT` serializes to `conflict / STALE_CAS`, and `CONFLICTING_REPLAY` serializes to `conflict / CONFLICTING_REPLAY`; each result survives JSON serialization. The existing UI regression continues to prove that an `unknown` mutation is reconciled using the exact original `operationId`.

### Reviewed Files

- `app/agent-configuration/page.tsx`
- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/agent-configuration/model-contracts.ts`
- `src/studio/agent-configuration/model-server-actions.ts`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/platform-model-configuration.tsx`
- `tests/agent-configuration-model-ui.test.tsx`
- `tests/agent-configuration-production.test.tsx`
- `tests/agent-configuration-server-actions.test.ts`
- Attempt 2 Architect Review correction contract

### Validation Reviewed

- Attempt 3 focused validation: 4 files, 15 tests passed.
- Production route/composition regression covers server-resolved `shopId`, trusted environment derivation and real action handoff.
- Production server-action regressions cover forbidden, stale-CAS and conflicting-replay serialization, including JSON round-trip assertions.
- Existing exact-original-operation `unknown` reconciliation regression remains present.
- Targeted ESLint: passed.
- `npx next typegen`: passed.
- Task-owned TypeScript paths reported no new Agent Configuration diagnostics; repository-wide typecheck remains non-zero only for documented legacy `StudioWorkspace` diagnostics outside this task.
- `git diff --check`: passed.
- Attempt 3 Completion Report records launcher-prepared parent/implementation worktree synchronization, dependency gating and recursive submodule readiness.
- The supplied archive has no installed `node_modules`, so the submitted test commands were not independently rerun in this review environment; source/test inspection and the Attempt 2 -> Attempt 3 diff support the reported results.

### Architecture Conformance

Conforms. Agent Configuration remains a dedicated production Studio domain outside unrelated `StudioWorkspace` state, uses the accepted COMMERCE-007 production model service, preserves the server-validated selected-shop context, displays trusted server-derived environment context, keeps ADMIN read-only, serializes the accepted mutation failure/reconciliation outcomes, renders no secrets, and introduces no provider execution or prompt/template/shop-override work owned by later tasks.

### Follow-up

Mark ARCH-021-COMMERCE-011 Complete. No dependant becomes Ready from this acceptance alone: COMMERCE-013 remains gated on COMMERCE-008; COMMERCE-014 remains gated on COMMERCE-008 and COMMERCE-009; COMMERCE-012 remains gated on COMMERCE-008, COMMERCE-009 and COMMERCE-010. COMMERCE-008 remains the current Ready Phase 2 Commerce frontier.
