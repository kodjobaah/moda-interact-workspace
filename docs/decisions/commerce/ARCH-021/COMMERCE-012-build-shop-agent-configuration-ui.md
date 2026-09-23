---
id: ARCH-021-COMMERCE-012
architecture_id: ARCH-021
title: Build shop Agent Configuration override surface
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 80
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-004
  - ARCH-021-COMMERCE-007
  - ARCH-021-COMMERCE-008
  - ARCH-021-COMMERCE-009
  - ARCH-021-COMMERCE-010
  - ARCH-021-COMMERCE-011
enables: []
created: 2026-09-23
updated: 2026-09-23
---

# Build shop Agent Configuration override surface

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Extend Agent Configuration so a platform admin can inspect effective configuration for the selected shop and independently manage that shop's model override and behavioural prompt override.

## Context

Phase 1 established server-validated `shopId` navigation context. Phase 2 now uses that context to configure one shop without making model/prompt feature-specific. Shop model and prompt fallback are independent, and removing an override returns only that dimension to platform inheritance.

## Scope

- Reuse the existing server-validated selected-shop Studio context.
- Show the selected shop's effective model and source (`PLATFORM` or `SHOP`).
- Allow SUPER_ADMIN to set/replace/clear the shop model override from enabled catalogue entries.
- Show the selected shop's effective prompt and source (`PLATFORM` or `SHOP`).
- Allow SUPER_ADMIN to create/edit/publish the shop prompt lineage and set/replace/clear its active override.
- Allow a shop prompt draft to be created from one exact published application-wide template revision.
- Clearly show inheritance when no override exists.
- Clearly show configuration error state when an explicit override is broken/disabled; do not present it as inherited.
- Preserve selected `shopId` across Agent Configuration navigation/refresh using the accepted Phase 1 mechanism.
- Extend the dedicated Agent Configuration domain component/module created by COMMERCE-011; do not add shop prompt/model editor state back into `StudioWorkspace`.
- ADMIN remains read-only.

## Out of Scope

- Merchant authentication/authorization.
- Merchant-owned prompt templates.
- Entitlement/tier policy for model overrides.
- Live chat/model execution.
- Grant/manifest/Background changes.
- Feature prompt removal.

## Requirements

- Model and prompt override actions are independent.
- `Clear model override` must not change prompt state.
- `Clear prompt override` must not change model state.
- Shop prompt operations must be scoped to the exact server-validated shop; a browser-supplied shop id must never bypass authorization/validation.
- A template creates a copied shop prompt draft; later template edits do not affect it.
- The UI must display effective ids/revisions/source so later preview work can prove what will be frozen.
- `StudioWorkspace` remains orchestration/navigation only for this surface; selected-shop authoring logic belongs to the Agent Configuration domain module.
- Broken explicit override state must remain visible and fail closed through the resolver.
- When an explicit shop model/prompt override exists, the UI must carry the opaque `generationId` and `editVersion` returned by the owning service and submit both on replace/clear. It must never synthesise/reset generation tokens client-side.

### Deterministic file boundary

Extend the Agent Configuration module created by COMMERCE-011; do not create a second shop-settings implementation elsewhere.

Primary locations:

```text
src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/shop-agent-configuration.tsx
app/agent-configuration/page.tsx
components/studio-workspace.tsx          # navigation/shop-context handoff only
tests/agent-configuration-shop-ui.test.tsx
```

Use the existing Phase 1 `shopId` query/navigation contract and `ShopExecutionContext`. Do not introduce another selected-shop store, cookie, localStorage key or database preference. Shop override editor state remains under `src/studio/agent-configuration/`.

## Work Items

- [ ] Extend the dedicated Agent Configuration domain module with the selected-shop sub-surface.
- [ ] Add selected-shop effective configuration summary.
- [ ] Add shop model override set/clear controls.
- [ ] Add shop prompt lineage/draft/publish/activate controls.
- [ ] Add create-from-template flow for shop prompt drafts.
- [ ] Add independent inheritance/reset controls and source labels.
- [ ] Preserve Phase 1 `shopId` navigation semantics.
- [ ] Add focused authorization/isolation/inheritance/error-state UI tests.

## Interfaces / Contracts

Consumes:

- selected-shop context from ARCH-021-COMMERCE-004;
- model configuration port from ARCH-021-COMMERCE-007 for shop model set/clear;
- prompt-template port from ARCH-021-COMMERCE-008 for selectable template discovery;
- prompt lifecycle port from ARCH-021-COMMERCE-009 for shop prompt draft/publish/active-pointer operations;
- effective configuration resolver from ARCH-021-COMMERCE-010;
- platform Agent Configuration domain surface from ARCH-021-COMMERCE-011 as the UI/module base.

Produces the selected-shop model/prompt override sub-surface within the shared Agent Configuration module. Platform template-library and platform prompt authoring remain independently owned by COMMERCE-013 and COMMERCE-014.

## Dependencies

- ARCH-021-COMMERCE-004
- ARCH-021-COMMERCE-007
- ARCH-021-COMMERCE-008
- ARCH-021-COMMERCE-009
- ARCH-021-COMMERCE-010
- ARCH-021-COMMERCE-011

## Enables

None. COMMERCE-013 and COMMERCE-014 are independent Phase 2 UI tasks and may still be incomplete when this task finishes.

## Acceptance Criteria

- [ ] Selected shop shows effective model and prompt with independent PLATFORM/SHOP source labels.
- [ ] A shop may override only model, only prompt, both, or neither.
- [ ] Clearing one override preserves the other.
- [ ] Existing override replace/clear commands round-trip the service-provided `generationId` + `editVersion` CAS tokens, including a stale-generation conflict regression after clear/recreate.
- [ ] Shop prompt authoring is isolated to the exact selected shop.
- [ ] Shop prompt may start from a published platform template as an independent copy.
- [ ] Broken explicit model/prompt overrides are displayed as configuration errors rather than silently inherited values.
- [ ] ADMIN is read-only and no secret/session token is rendered.
- [ ] Shop Agent Configuration logic does not re-accumulate inside `StudioWorkspace`.
- [ ] No live model/provider execution occurs.

## Validation

- [ ] focused shop Agent Configuration UI tests
- [ ] inheritance matrix UI tests
- [ ] cross-shop isolation/auth tests
- [ ] selected-shop navigation/refresh regressions
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-013, COMMERCE-014 or Phase 3.

## Implementation Notes

Use the existing selected-shop context; do not introduce a second independent shop selector. The future merchant-facing Studio will replace platform-admin shop selection with merchant authorization but should reuse the same shop-scoped configuration service boundary.

## Completion Report

### Status

Ready for Review

### Files Changed

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/commerce/agent-configuration/prompt-service.ts`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/prompt-contracts.ts`
- `src/studio/agent-configuration/prompt-server-actions.ts`
- `src/studio/agent-configuration/shop-agent-configuration.tsx`
- `tests/agent-configuration-production.test.tsx`
- `tests/agent-configuration-shop-ui.test.tsx`

### Work Completed

- Added the selected-shop Agent Configuration sub-surface under the dedicated domain module.
- Preserved server-validated `shopId` by forwarding only `shopSelection.selectedShop?.id`; unavailable or invalid query-string shops never enter the authoring surface.
- Loaded model/pointer/lineage raw state independently of effective resolution, keeping broken explicit overrides visible and clearable as configuration errors.
- Added the durable `getShopPrompt(shopId)` read so unactivated shop lineages and drafts survive refresh and shop changes clear stale local editor state.
- Resumed an existing shop lineage and allocated independent operation IDs for lineage creation and draft creation; template copies remain exact and independent.
- Reconciled publish results and activated the returned published revision using current pointer generation/edit CAS tokens; publication is disabled while visible text is dirty.
- Connected shop editor dirty state to the accepted Studio Composer navigation blocker, made ADMIN prompt text read-only, and retained model/prompt independent CAS replace/clear semantics.

### Validation Results

- Launcher evidence: prepared execution was supplied with canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-012`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-012`, synchronized task branch `task/ARCH-021-COMMERCE-012`, initialized database submodule at `98fdf715e54fe6df92ac6951facd104e410068f2`, claim commit `3b642241d94ac77854d5a82904735d676883070c`, parent head `b0ce775f2d36f68c511336f9b0a9684324ae7bc2`, and implementation head `fb5558ab454070c879454a86d2f659e9e35c58ab` at handoff.
- VCS: implementation correction commit `f252484` pushed to `origin/task/ARCH-021-COMMERCE-012`; parent report commit follows this update.
- Focused Attempt 2 validation: `npm run test -- tests/agent-configuration-shop-ui.test.tsx tests/agent-configuration-production.test.tsx tests/agent-configuration-prompts.test.ts`: passed, 3 files and 11 tests.
- Broader targeted validation: 7 of 8 selected files passed, 30 tests passed. The existing `tests/agent-configuration-effective.test.ts` mock path remains failing 9 tests because its Prisma mock exposes no `Prisma.TransactionIsolationLevel.RepeatableRead`; this is the documented baseline incompatibility and is outside the changed behavior.
- `npx eslint` over all changed TypeScript/TSX files: passed with no warnings.
- `git diff --check`: passed.
- `npm run typecheck`: exit 2 with 248 errors across 18 files. Changed-file diagnostics are limited to the pre-existing three `components/studio-workspace.tsx` errors (duplicate `productionCodePanel`, `responseProcessing` union access, and `StudioFailure.message` union access) plus four pre-existing generated-client/type diagnostics in `src/commerce/agent-configuration/prompt-service.ts`; no diagnostics remain in the new Agent Configuration screen/contracts or focused tests.

### Correction Checklist

- [x] Validated shop boundary: `components/production-studio-page.tsx` forwards only `shopSelection.selectedShop?.id`; `tests/agent-configuration-production.test.tsx` proves unavailable raw IDs are suppressed.
- [x] Broken override recovery: `shop-agent-configuration.tsx` loads raw model/pointer/lineage state alongside effective resolution; focused UI coverage proves a disabled model remains clearable with its service CAS tokens.
- [x] Durable lineage and isolation: `prompt-contracts.ts`, `prompt-server-actions.ts`, and `prompt-service.ts` add `getShopPrompt`; the component clears shop-local state on identity/load changes and resumes existing lineages; tests cover distinct operation IDs and no duplicate lineage creation.
- [x] Publication/activation: the component blocks publication while visible text is dirty, publishes the current draft, and activates the returned revision with current pointer CAS; focused UI coverage proves the no-pointer activation path.
- [x] Composer dirty guard and ADMIN read-only: `agent-configuration-screen.tsx`/`studio-workspace.tsx` pass accepted Composer dirty state; the editor is read-only for ADMIN and the focused UI test covers it.
- [x] Accepted model CAS behavior preserved: existing model controls remain unchanged; focused UI coverage continues to verify generation/edit token round-trip.

### Deviations

- The locked dependency tree was restored with `npm ci` because the prepared worktree had an incomplete `node_modules` tree and could not resolve the declared Vitest binary. The install emitted existing peer/engine/deprecation warnings and did not modify tracked files.

### Assumptions

- Existing prompt/template server actions and resolver contracts are authoritative; no new persistence, provider, or network path was introduced.
- Template selection is resolved server-side with `selectable: true`, and only the returned published revision text/provenance is copied into a shop draft.

### Unresolved Issues

- Full repository typecheck remains blocked by 248 documented/pre-existing baseline diagnostics described above; no new focused-file diagnostics remain.
- The broader effective-configuration test mock still requires the generated Prisma enum surface and remains a baseline test-environment failure; it was not changed because it is outside this bounded UI correction.

### Architectural Concerns

None.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 2 resolves the Attempt 1 selected-shop handoff and durable prompt-discovery defects: production composition forwards only `shopSelection.selectedShop?.id`; raw model/pointer/lineage reads are no longer suppressed by an unavailable effective resolver; `getShopPrompt(shopId)` makes an unactivated lineage/draft durable across refresh; lineage creation and draft creation use separate operation ids; publication activates the returned published revision using the current pointer CAS tokens; ADMIN prompt text is read-only; and the shared Studio Composer dirty blocker is wired through the Agent Configuration screen.

The underlying COMMERCE-007/009 CAS services remain accepted. The remaining issues are UI state-isolation/recovery problems inside this task:

1. `ShopAgentConfiguration.load()` has no load-generation/token guard. If Shop A is still loading when the selected shop changes to Shop B, the slower Shop A Promise can resolve after the Shop B load and repopulate `model`/`pointer`/`lineage`/`draft` state while the component now renders Shop B. A later draft save uses only the stale revision id, so this can mutate Shop A from the Shop B surface. Attempt 3 must ignore stale asynchronous loads after `shopId` changes (for example, with a monotonically increasing load token or equivalent cancellation guard) and include a regression where the old-shop load resolves last.
2. A dirty prompt draft can still be silently discarded by successful independent controls. Model replace/clear, `Create shop prompt draft`, and `Clear prompt override` can all invoke a mutation followed by `load()`, which resets text and clears the shared dirty blocker. Because model and prompt overrides are independent, a model mutation must not discard unsaved prompt text. While prompt text is dirty, actions that would reload/replace the prompt editor must be blocked or explicitly pass through a discard decision; they must never clear dirty state implicitly.
3. `Create shop prompt draft` remains available when a DRAFT already exists. The service permits another DRAFT revision, while `load()` resumes the first DRAFT it finds, so a second draft can be created and immediately become non-visible/unmanageable. When a durable DRAFT already exists, the UI must resume it rather than create another. New draft creation is allowed only when the lineage has no DRAFT (for example after publication).
4. Publish + activate is not reconciled when the publish succeeds but the pointer CAS fails. In that case the revision is durably PUBLISHED, but local state still presents it as the old DRAFT and the newly published revision is absent from the published-revision selector until a manual refresh. Attempt 3 must reload/reconcile lineage + current pointer after activation failure so the immutable published revision is visible and can be activated with refreshed CAS tokens; do not retry publication of the already-published revision.
5. `load()` records the effective-resolver failure message and then unconditionally clears `message`. Preserve the configuration-error message while still loading/displaying the raw override state, so a broken explicit override is visibly an error rather than only an empty alert/status shell.

Do not redesign the accepted model/prompt services, CAS tokens, selected-shop URL contract or Studio Composer blocker. This is a bounded final UI-state correction.

### Reviewed Files

- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/agent-configuration/shop-agent-configuration.tsx`
- `src/studio/agent-configuration/prompt-contracts.ts`
- `src/studio/agent-configuration/prompt-server-actions.ts`
- `src/commerce/agent-configuration/prompt-service.ts`
- `tests/agent-configuration-shop-ui.test.tsx`
- `tests/agent-configuration-production.test.tsx`

### Validation Reviewed

- Submitted Attempt 2 focused validation: 3 files / 11 tests passed.
- Submitted broader targeted validation: 30 tests passed; 9 documented pre-existing Prisma-mock failures remain outside the changed behavior.
- Submitted changed-file ESLint: passed.
- Submitted `git diff --check`: passed.
- Repository-wide TypeScript baseline remains non-blocking; no new diagnostic was reported in the new Agent Configuration files/tests.
- Direct source review confirms the Attempt 1 server-validated shop handoff, raw broken-override recovery, durable lineage read, separate operation ids, exact published-revision activation and Composer dirty integration, while exposing the remaining async-shop and dirty/reconciliation defects above.

### Architecture Conformance

Partial. Attempt 2 satisfies the original selected-shop validation, durable lineage discovery, exact publication target and ADMIN/navigation boundaries, but the selected-shop surface can still accept stale old-shop asynchronous state, independent mutations can discard unsaved prompt text, duplicate DRAFTs can be created, and a publish-success/activation-conflict outcome is not reconciled. Those defects violate shop isolation, independent override behavior and durable authoring recovery.

### Follow-up

Attempt 3 must preserve the accepted Attempt 2 work and correct only the bounded UI-state issues above. Add focused regressions proving:

- Shop A load resolving after a Shop B selection cannot repopulate or mutate Shop A state from the Shop B surface;
- dirty prompt text is not discarded by model mutations, prompt inheritance clear, or draft creation/reload paths;
- an existing durable DRAFT is resumed and a second DRAFT is not created;
- publish success followed by pointer CAS failure reconciles the now-PUBLISHED revision and refreshed pointer state without republishing it;
- an effective-resolution failure remains visibly reported while raw broken overrides stay clearable.

After these corrections, reconcile the executor-owned Work Items / Acceptance Criteria / Validation checkboxes with the final implementation evidence, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin another task from this branch.
