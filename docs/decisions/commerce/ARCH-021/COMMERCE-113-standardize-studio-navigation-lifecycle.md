---
id: ARCH-021-COMMERCE-113
architecture_id: ARCH-021
title: Standardize Studio navigation lifecycle
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-004
  - ARCH-025-COMMERCE-005
  - ARCH-025-COMMERCE-010
enables: []
created: 2026-10-04
updated: 2026-10-04
---

# Standardize Studio navigation lifecycle

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Introduce one shared Commerce Studio navigation lifecycle that preserves the accepted dirty/locked navigation guard, exposes reliable navigation progress/completion state, supports normal versus blocking transitions, prevents duplicate in-flight navigation, and removes the need for screen-local guesses about when a route/context switch has finished.

## Context

Manual validation of selected-shop switching exposed a general lifecycle gap in the existing `StudioComposerContext`: the shared boundary knows when navigation is requested and can gate it behind unsaved/locked-state confirmation, but it does not own a durable `idle -> pending -> committed/failed -> idle` lifecycle. A caller that needs to block interaction while tenant/shop context changes therefore has to invent local pending state and infer completion independently.

The implementation baseline is **post-ARCH-025**. ARCH-025-COMMERCE-001..005 already reduced `StudioWorkspace` behind its unchanged public boundary into the accepted controller/page/Release/Shop modules, and ARCH-025-COMMERCE-006..010 already reduced `ToolEditor` into the accepted persisted-authoring controller and execution-kind wrappers. This task must build on those boundaries rather than move routing/navigation state back into either shell, recreate either monolith, or introduce another generic controller around the extracted modules.

`components/studio-composer-context.tsx` remains the canonical cross-screen navigation/dirty-guard boundary. `StudioWorkspace`/`StudioPage`, the extracted ARCH-025 `components/studio-workspace/*` modules, `ToolEditor`, and the extracted persisted Tool editors remain their accepted public/local boundaries. The selected-shop provider may request a **blocking** navigation intent, but generic transition state and presentation must not remain owned by the selector itself.

This is a browser/navigation coordination change only. It does not alter server actions, durable state, publication/runtime semantics, Tool candidate state, Agent Configuration policy, selected-shop authorization, or database/shared contracts.

## Scope

- Add a typed shared Studio navigation lifecycle to `StudioComposerContext` (or the smallest equivalent shared boundary) with an explicit idle/pending state and bounded transition metadata.
- Preserve the existing dirty/locked confirmation gate and ensure navigation becomes pending only **after** navigation is actually admitted.
- Replace the positional `requestNavigation(...)` option pattern with a typed options contract for current direct callers, allowing staged compatibility only while the task is being implemented; the completed task must have one canonical call shape.
- Support at least two presentation/admission modes:
  - normal route navigation with lightweight progress feedback;
  - blocking context navigation where old-context controls must not remain interactive.
- Tie normal navigation completion to the actual Next/React route transition settling/committing rather than to the instant `router.push`/navigation invocation occurs.
- Allow a blocking context transition to require a stronger caller-owned readiness condition after route commit when necessary; selected-shop switching is the first required consumer.
- Move selected-shop switching onto the shared lifecycle and remove any selector-local generic navigation-pending implementation once the shared mechanism owns it.
- Preserve the selected-shop invariant: old-shop controls remain blocked until the requested `shopId` is represented by the committed URL **and** the server-resolved selected-shop context, or until the existing selection error path is committed and surfaced.
- Suppress duplicate/re-entrant controlled navigation while one admitted transition is pending so repeated clicks/changes do not cause multiple router dispatches.
- Centralize accessible transition presentation/focus behavior for shared normal/blocking navigation states.
- Migrate the current direct `StudioComposerContext.requestNavigation` callers needed to prove the shared contract, while preserving the one-argument `navigate(destination)` boundaries consumed by the ARCH-025 extracted StudioWorkspace and ToolEditor modules.
- Add focused regression coverage for navigation admission, completion, blocking semantics, duplicate suppression, accessibility and the selected-shop transition.

## Out of Scope

- Recombining or materially refactoring the ARCH-025 `StudioWorkspace`, `ToolEditor`, Release, Shop, or persisted Tool editor boundaries.
- Migrating every ordinary anchor/link in the repository when it does not use the shared Studio navigation boundary.
- Introducing Redux, Zustand, another global state framework, or a generic routing/plugin framework.
- Replacing Next App Router.
- Intercepting native browser back/forward beyond the behavior already owned by the current Studio/navigation architecture.
- Changing selected-shop URL/server-resolution semantics or persisting selected shop outside the URL.
- Changing Tool/Capability phase navigation, validation, Test, Save or publication semantics.
- Changing server-action authorization, origin/CSRF policy, authentication, database schema, Shared contracts or Gateway topology.
- Adding new operational telemetry solely for route progress; existing shared application logging remains unchanged unless an unexpected navigation failure already passes through an existing logged error boundary.

## Requirements

- `StudioComposerContext` remains the single shared owner of dirty/locked navigation admission.
- The accepted navigation order is:

  ```text
  request
    -> preserve/construct destination context
    -> dirty/locked guard
    -> Stay / Discard decision when required
    -> admit exactly one navigation
    -> pending lifecycle
    -> committed/failed lifecycle completion
    -> idle
  ```

- `beforeNavigate`-equivalent callbacks execute at most once and only after navigation is admitted. Choosing `Stay` must not execute them.
- A locked unknown/unconfirmed operation remains non-discardable exactly as today.
- While an admitted controlled navigation is pending, a repeated activation must not dispatch a second router transition. The UI must communicate that navigation is already in progress rather than relying only on eventual React disabled-state propagation.
- Normal navigation must provide bounded progress feedback without unnecessarily blocking the entire Studio.
- Blocking navigation must prevent pointer/keyboard interaction with stale page controls until its completion condition is satisfied or its existing error state is committed.
- Blocking presentation must be accessible (`aria` semantics appropriate to a modal/busy transition, deterministic focus entry, no focus escape into stale controls while blocked).
- Normal progress feedback must be announced accessibly without forcing modal focus.
- Navigation must return to idle when the actual route transition settles; it must not remain pending merely because a caller forgot to clear local state.
- Selected-shop switching must not clear its blocking state on router invocation alone. Success requires the requested shop identity to be the server-resolved current context; invalid/not-found selection must clear the blocker and expose the existing selection error.
- Current `shopId` preservation, nested `returnTo`/`return` preservation and deliberate selected-shop replacement/clearing semantics from ARCH-021-COMMERCE-004 remain unchanged.
- Current `StudioWorkspace` and `ToolEditor` public/extracted boundaries established by ARCH-025 remain intact. Navigation state must not be moved into `use-studio-workspace-controller`, `studio-page-content`, Release/Shop modules, the persisted Tool controller, or execution-kind editor wrappers merely to avoid using the shared composer boundary.
- Existing local-only phase/tab navigation inside Tool/Capability editors remains local and must not be forced through route-level pending state.
- No server secret or additional shop/session data is introduced into browser state.

## Work Items

- [ ] Define the typed shared navigation intent/state/options contract.
- [ ] Add explicit pending/completion ownership to the shared Studio navigation provider/router adapter.
- [ ] Preserve dirty/locked confirmation ordering and migrate it onto the shared lifecycle without changing its accepted semantics.
- [ ] Add synchronous single-flight admission for controlled route transitions.
- [ ] Add shared normal-navigation progress presentation and blocking-transition presentation/accessibility.
- [ ] Migrate selected-shop switching to blocking shared navigation with server-resolved completion/error semantics; remove selector-local generic pending state.
- [ ] Migrate current direct `requestNavigation` callers to the canonical options shape while preserving the ARCH-025 one-argument navigation boundaries.
- [ ] Add focused lifecycle, accessibility, duplicate-dispatch and selected-shop completion/failure tests.
- [ ] Run the ARCH-025 StudioWorkspace/ToolEditor focused regression/source-boundary checks needed to prove the refactor is not being collapsed or bypassed.

## Interfaces / Contracts

Internal Commerce browser contract only.

Canonical owner:

- `components/studio-composer-context.tsx` (or a bounded module extracted immediately beside it if separation improves clarity without creating another framework).

Primary consumers/producers to preserve:

- `StudioAppProvider` — production Next-router adapter and route-transition lifecycle integration.
- `StudioComposerProvider` / `useStudioComposer` — shared navigation admission and lifecycle state.
- `StudioNavigationLink` — normal shared route navigation.
- `StudioSelectedShopProvider` / `StudioShopSelector` — selected-shop context and first blocking-navigation consumer.
- `StudioWorkspace` and ARCH-025 `components/studio-workspace/*` — retain their accepted public/extracted boundaries and one-argument navigation callbacks.
- `ToolEditor` and ARCH-025 persisted editor modules — retain their accepted boundaries; route lifecycle must not be reimplemented inside them.

No cross-repository runtime contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-004
- ARCH-025-COMMERCE-005
- ARCH-025-COMMERCE-010

All dependencies are architect-accepted Complete in the supplied 2026-10-04 snapshot.

## Enables

None.

## Acceptance Criteria

- [ ] One shared Studio navigation lifecycle represents admitted route navigation; callers do not need screen-local generic route-pending state.
- [ ] Dirty/unconfirmed/unknown-operation navigation protection behaves exactly as before and happens before pending navigation begins.
- [ ] `Stay` leaves the route/context unchanged, clears the pending confirmation, restores appropriate focus and does not start navigation progress.
- [ ] `Discard unsaved changes` admits exactly one transition and executes its pre-navigation callback at most once.
- [ ] Repeated activation during an admitted transition causes no duplicate router dispatch.
- [ ] Ordinary Studio route navigation exposes accessible non-blocking progress and returns to idle when the route transition commits/settles.
- [ ] Blocking navigation prevents interaction with stale context and has accessible modal/busy focus semantics.
- [ ] Selected-shop switching remains blocking until the requested `shopId` and server-resolved selected shop agree; invalid/not-found selection releases the blocker and exposes the existing error.
- [ ] Selected-shop URL/query/`returnTo` preservation and explicit clearing behavior are unchanged from ARCH-021-COMMERCE-004.
- [ ] Direct shared-navigation callers use one typed options contract; the completed implementation does not retain ambiguous positional boolean arguments.
- [ ] ARCH-025 `StudioWorkspace` and `ToolEditor` remain thin accepted boundaries; no Release/Shop/editor behavior is folded back into either shell.
- [ ] No Tool/Capability local phase-navigation or server mutation semantics change.
- [ ] No new database, Shared, Gateway or secret/browser-state requirement is introduced.

## Validation

- [ ] focused new Studio navigation-lifecycle provider tests
- [ ] `tests/selected-shop-navigation.test.tsx`
- [ ] `tests/connections-ui.test.tsx` and/or the narrow Connections navigation suite covering direct composer navigation callers changed by the task
- [ ] `tests/add-capability-screen.test.tsx` if its direct composer call changes
- [ ] `tests/studio-workspace-controller.test.tsx`
- [ ] `tests/studio-page-content.test.tsx`
- [ ] `tests/tool-editor-dispatch.test.tsx`
- [ ] relevant ARCH-025 StudioWorkspace source-boundary/source-inspection assertions remain passing
- [ ] targeted lint for changed files
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `git diff --check`

Repository-wide baseline failures must be handled according to `docs/development-baseline.md`; this task may not expand the accepted baseline or classify a changed-file regression as pre-existing.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, leave the task in `review` for the developer completion workflow and STOP. Do not expand into unrelated route/UI refactors or migrate ordinary navigation that does not need the shared Studio lifecycle.

## Implementation Notes

Implement this task iteratively rather than as one broad rewrite. The expected patch sequence is:

1. **Contract/state patch** — add the shared typed lifecycle and tests while preserving current behavior.
2. **Completion/single-flight patch** — tie pending state to real route settling and suppress duplicate controlled navigation.
3. **Presentation/accessibility patch** — add shared normal/blocking transition UI and focus/ARIA semantics.
4. **Selected-shop migration patch** — move shop switching off selector-local generic pending state and onto the shared blocking lifecycle with server-resolved completion/error handling.
5. **Caller/regression patch** — finish the typed-options migration for current direct callers and run the ARCH-025 boundary regression packet.

Each patch must remain reviewable and leave the tree in a coherent state. Do not use the iterative sequence as permission to temporarily merge ARCH-025 extracted controllers/views back into their former monoliths.

The final implementation should prefer the existing Next/React transition capabilities over inventing a second router. Exact internal mechanics are repository-local, but `router.push()` invocation alone is not proof of completion.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- ARCH-025-COMMERCE-005 and ARCH-025-COMMERCE-010 are the accepted structural baseline and remain intact.
- The selected-shop blocking feedback developed during 2026-10-04 manual validation is treated as behavior to absorb into the shared lifecycle, not as a separate long-term navigation framework.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation.

### Follow-up

None.
