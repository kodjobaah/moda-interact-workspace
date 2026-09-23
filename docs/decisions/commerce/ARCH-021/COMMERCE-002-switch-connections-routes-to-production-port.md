---
id: ARCH-021-COMMERCE-002
architecture_id: ARCH-021
title: Switch Connections routes to the production port
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-001
  - ARCH-020-COMMERCE-022
enables: []
created: 2026-09-23
updated: 2026-09-23
---

# Switch Connections routes to the production port

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the production `/connections` and `/connections/[id]` fixture composition with the real production `ConnectionPort` while preserving the accepted U15/U16 behaviour and navigation semantics.

## Context

The U15/U16 frontend is already implemented and well covered through injected fixture ports, but `ConnectionsRouteClient` currently creates `createConnectionFixtures()` in the production route. ARCH-021-COMMERCE-001 provides the real server-backed port. This task installs that port; it does not redesign the Connections UI.

## Scope

- Replace production use of `createConnectionFixtures()` in `/connections` and `/connections/[id]` with the production port from ARCH-021-COMMERCE-001.
- Preserve the existing injectable `ConnectionsPage` component boundary so fixture-based component tests remain possible.
- Preserve list search, enabled filtering, pagination, detail revision selection, credential status, mutation replay, dirty-state guards and role presentation.
- Implement the missing Connections-side `returnTo` handoff required by ARCH-020 XN02. `/connections` and `/connections/[id]` must accept a validated internal Studio return destination from U06, carry it across U15/U16 navigation together with list return state, and expose a navigation-blocker-aware return action to that exact destination.
- Ensure fixture factories are imported only by tests/dev fixtures, not by production route composition.

## Out of Scope

- Connection lifecycle/credential business logic.
- Shop execution-context selection across the rest of Studio.
- Tool editor connection selection.
- Live external/Shopify requests.
- Prompt/model configuration.
- Changes to U06's existing `returnTo` producer; ARCH-020-COMMERCE-023 already owns and emits that handoff.
- Redesigning U15/U16 styling or fields.

## Requirements

- The production route must never instantiate `createConnectionFixtures()`.
- The route/client composition must use the exact production adapter from ARCH-021-COMMERCE-001.
- Server-authorised results remain authoritative; frontend role presentation is not security enforcement.
- Unknown mutation outcomes continue to retain the exact original operation/payload for reconciliation.
- Credential secret values must never be loaded back into the browser after save.
- Existing ADMIN read-only and SUPER_ADMIN mutation behaviour remains unchanged.
- Both Connections routes accept an optional `returnTo` query value and pass only a validated internal Studio-relative destination into client navigation state.
- A valid `returnTo` starts with exactly one `/`; protocol-relative (`//...`) and absolute/schemed destinations are not followed and fall back to normal Connections navigation.
- `returnTo` is navigation context only: do not persist it in browser storage or durable state.
- U15 -> U16 Open, successful Create -> U16, U16 -> U15, and U16 tab/navigation transitions must retain the exact validated `returnTo` while continuing to preserve `search`, `cursor` and `enabled` list state.
- When `returnTo` is present, U15/U16 must expose a navigation-blocker-aware return action that routes to that exact origin. The existing U16 Back-to-U15 behaviour remains list-state-preserving rather than being replaced by the origin return.

## Work Items

- [x] Replace fixture-port construction in `ConnectionsRouteClient`/route composition with the production ConnectionPort.
- [x] Preserve dependency injection for `ConnectionsPage` component tests.
- [x] Add route/composition tests proving production list/detail reads come from the production adapter.
- [x] Add a regression that fails if production route code imports/instantiates the fixture factory.
- [x] Re-run existing U15/U16 frontend tests against fixture injection to prove no component behaviour regressed.
- [x] Parse, validate and propagate the optional Connections `returnTo` through both route pages, `ConnectionsRouteClient` and `ConnectionsPage`.
- [x] Preserve `returnTo` across U15/U16 navigation without dropping `search`, `cursor` or `enabled`, and add the guarded return-to-origin action.
- [x] Add focused regressions for U06-style U15/U16 return handoff and rejection/fallback of non-internal return destinations.

## Interfaces / Contracts

Consumes:

- production `ConnectionPort` from ARCH-021-COMMERCE-001
- existing U15/U16 `ConnectionsPage` and `ConnectionPort` contract from ARCH-020-COMMERCE-022

Produces:

- production-backed Connections routes;
- the Connections-side consumer of the existing ARCH-020 U06 `returnTo` route handoff.

No new cross-service runtime contract is introduced. This task completes an existing Studio route/navigation contract that ARCH-020-COMMERCE-023 already produces.

## Dependencies

- ARCH-021-COMMERCE-001
- ARCH-020-COMMERCE-022

## Enables

None within Phase 1. This task may execute in parallel with the shop-context branch once ARCH-021-COMMERCE-001 is Complete.

## Acceptance Criteria

- [x] `/connections` lists real persisted connections through the production port.
- [x] `/connections/[id]` reads and mutates the selected persisted connection through the production port.
- [x] PER_SHOP credential search/status/set/remove operates against real shop/credential services while exposing no secret values.
- [x] `createConnectionFixtures()` is absent from production route composition and remains available to tests.
- [x] Existing U15/U16 role, CAS, unknown-result and navigation behaviours remain passing.
- [x] `/connections?returnTo=<encoded internal Studio route>` and `/connections/[id]?returnTo=<encoded internal Studio route>` both retain and can return to the exact validated origin through the Studio navigation blocker.
- [x] U15 -> U16 -> U15 round trips preserve `returnTo` together with exact `search`, `cursor` and `enabled` state.
- [x] Absolute, schemed or protocol-relative `returnTo` values are not used as navigation destinations.

## Validation

- [x] existing `test:arch020-connections-ui` or current equivalent
- [x] focused production route/composition test
- [x] focused `returnTo` navigation/round-trip regression
- [x] targeted lint/typecheck for changed files
- [x] `git diff --check`

No live provider network call is required.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

## Implementation Notes

Do not collapse frontend fixture tests into database integration tests. Keep the existing component port injection and add only the production composition proof needed by this task.

ARCH-020 established the producer side of the Tool -> Connections handoff but did not implement the Connections consumer: COMMERCE-023 emits `/connections[/<id>]?returnTo=<encoded tool route>` and explicitly does not edit U15/U16 internals. Treat `returnTo` here as an internal navigation destination, not as arbitrary URL data. Preserve it independently from the U15 list-return tuple (`search`, `cursor`, `enabled`).

## Completion Report

### Status

Ready for architect review (Attempt 2 correction)

### Files Changed

- `src/studio/connections/connections-route-client.tsx`
- `app/connections/page.tsx`
- `app/connections/[id]/page.tsx`
- `src/studio/connections/navigation.ts`
- `src/studio/connections/connections-ui.tsx`
- `tests/connections-route-composition.test.tsx`
- `tests/connections-ui.test.tsx`
- `tests/connections-navigation.test.ts`

### Work Completed

- Replaced production fixture construction with a stable client-safe `ConnectionPort` whose operations invoke the production server actions.
- Preserved the `ConnectionsPage` port injection boundary used by fixture-based component tests.
- Added composition coverage for production list/detail delegation and a source regression excluding `createConnectionFixtures()` from the production route module.
- Kept fixture factories available to existing component tests and preserved U15/U16 behavior.
- Added validated internal `returnTo` parsing and propagation through both routes, the route client and U15/U16.
- Preserved `returnTo` independently from `search`, `cursor` and `enabled` across Open, detail, tabs, Back and error navigation.
- Added blocker-aware Return to tool actions for U15 and both loaded/error U16 states; loaded U16 Back now preserves list state and return context.
- Rejected protocol-relative, schemed and backslash-containing destinations and covered the U06-style round trip with focused tests.

### Validation Results

- `npx vitest run tests/connections-ui.test.tsx tests/connections-navigation.test.ts tests/connections-route-composition.test.tsx tests/connections-production.test.ts`: PASS, 31 tests.
- `npx eslint app/connections/page.tsx 'app/connections/[id]/page.tsx' src/studio/connections/navigation.ts src/studio/connections/connections-route-client.tsx src/studio/connections/connections-ui.tsx tests/connections-ui.test.tsx tests/connections-navigation.test.ts`: PASS.
- `git diff --check`: PASS.
- Changed-file diagnostics: no errors.
- `npm run typecheck`: existing repository failures remain in unrelated Prisma/backend/studio files; no errors were reported for the changed route or tests.
- `npm run test:arch020-external-connection-lifecycle`: 13/14 passed; the existing development-bypass test fails with `forbidden` in unrelated lifecycle code.

Physical worktree isolation:

- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-002`
- parent branch: `task/ARCH-021-COMMERCE-002`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-002`
- implementation branch: `task/ARCH-021-COMMERCE-002`
- shared workspace checkout switched/mutated for task work: no
- shared implementation checkout switched/mutated for task work: no
- another task worktree reused: no

Attempt 2 correction checklist:

- [x] Both route pages validate and pass `returnTo`.
- [x] `ConnectionsRouteClient`, U15 and U16 retain the validated destination.
- [x] U15 Open/create and U16 Back/tab/error transitions preserve list state and `returnTo`.
- [x] U15 and U16 expose blocker-aware Return to tool actions.
- [x] Invalid absolute, schemed, protocol-relative and backslash-containing values fall back safely.
- [x] Focused regressions cover direct U16, U15/U16 round trip, tab propagation and validator rejection.

Attempt 2 launcher evidence:

- parent head at claim: `46efc7c457b5ac1646856c0cf7f0b7568d12d499`
- implementation reused head: `267f3bd4e6bf23dbc03aac75b11a7c11a8127e82`
- claim commit: `cd0c14c0354db91d7e0e3636e18d68550f230eaa`
- recursive submodule `database`: `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`

Start-of-attempt synchronization:

- parent remote task branch fast-forwarded: not-needed
- parent `origin/main` incorporated: already-current
- implementation remote task branch fast-forwarded: not-needed
- implementation `origin/main` incorporated: already-current

Recursive implementation submodules:

- `git submodule sync --recursive`: passed
- `git submodule update --init --recursive`: passed
- recorded submodule commit: `database` at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`

Published commits:

- implementation base reused: `267f3bd` (`Switch connections routes to production port`)
- Attempt 2 launcher claim: `cd0c14c0354db91d7e0e3636e18d68550f230eaa`

### Deviations

- Full repository typecheck is currently blocked by pre-existing type errors in backend/studio persistence code outside this task. The focused changed-file diagnostics and targeted lint pass.
- The lifecycle validation retains one unrelated baseline failure in the development-bypass case.

### Assumptions

- Existing `src/studio/connections/server-actions.ts` is the ARCH-021-COMMERCE-001 production adapter bridge and remains the correct client/server boundary.

### Unresolved Issues

- None within this task scope.

### Architectural Concerns

- None. The route delegates authorization and persistence to the server-side production adapter; the browser receives only `ConnectionPort` results.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 was reviewed against the corrected COMMERCE-002 contract, ARCH-021 Phase 1, the supplied implementation snapshot, implementation handoff `b7bc0cd`, and parent report handoff `0bbb212e`.

The production U15/U16 composition remains correctly backed by the accepted COMMERCE-001 server-action `ConnectionPort`; production route code does not instantiate the fixture factory and the injectable `ConnectionsPage` boundary remains intact for deterministic component tests.

The Attempt 1 navigation gap is now functionally closed. Both Connections route entries read and validate optional `returnTo`, pass the validated internal destination through `ConnectionsRouteClient`, and preserve it independently from the U15 list-state tuple (`search`, `cursor`, `enabled`). U15 Open and successful Create carry the return destination into U16; U16 Back retains the list state and return context; U16 tab/navigation transitions retain the same context; and U15/U16 expose a return-to-origin action through `StudioComposerContext.requestNavigation(...)`, so existing dirty/locked navigation protection remains authoritative.

`validateConnectionsReturnTo(...)` rejects protocol-relative, schemed/non-relative and backslash-containing destinations before they can become a navigation target. No durable/browser-storage state is introduced and no provider/network behaviour is added.

The review is intentionally functionality-focused rather than requiring exhaustive navigation test enumeration. The focused regressions plus direct source inspection are sufficient to establish the corrected route handoff. A narrow TypeScript hygiene issue remains in the two Next route prop annotations: they read `query.returnTo` without declaring `returnTo?: string` in the local `searchParams` type. This does not change runtime navigation behaviour and is non-blocking for this functional acceptance; it should be corrected when those route annotations are next touched or when the existing repository typecheck baseline is reconciled.

The Completion Report's `Published commits` subsection still describes the reused Attempt 1 implementation base/launcher claim rather than the final submitted implementation/report hashes. The architect review records the submitted `b7bc0cd` / `0bbb212e` handoff above; no code-free rework attempt is required for that reporting discrepancy.

### Reviewed Files

- `app/connections/page.tsx`
- `app/connections/[id]/page.tsx`
- `src/studio/connections/navigation.ts`
- `src/studio/connections/connections-route-client.tsx`
- `src/studio/connections/connections-ui.tsx`
- `src/studio/connections/server-actions.ts`
- `src/studio/connections/production.ts`
- `components/studio-composer-context.tsx`
- `tests/connections-navigation.test.ts`
- `tests/connections-route-composition.test.tsx`
- `tests/connections-ui.test.tsx`
- `tests/connections-production.test.ts`
- `docs/architecture/ARCH-020-external-api-tools.md`
- `docs/decisions/commerce/ARCH-020/COMMERCE-022-build-connections-pages-u15-u16.md`
- `docs/decisions/commerce/ARCH-020/COMMERCE-023-build-external-tool-authoring-and-filter-editor.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

- Submitted focused Connections/navigation/production suite: 31 passed.
- Submitted targeted ESLint: passed.
- Submitted changed-file diagnostics: passed according to the executor report.
- Submitted `git diff --check`: passed.
- Submitted broad repository typecheck remains non-zero on the existing baseline; architect static inspection additionally identified the non-functional local `searchParams.returnTo` annotation mismatch noted above.
- Submitted lifecycle regression remains 13/14 with the previously reported unrelated development-bypass baseline failure.
- Architect source review confirms production fixture exclusion, validated return propagation, list-state preservation, blocker-aware return actions and unsafe-destination fallback.
- The supplied review archive does not contain `node_modules`, so the architect did not rerun the submitted Node test commands in the review container.

### Architecture Conformance

Conformant for the Phase 1 functional contract. COMMERCE-002 now installs the accepted production Connections port and completes the existing ARCH-020 U06 -> U15/U16 -> U06 navigation handoff without changing persistence, authorization, provider execution or cross-service contracts.

### Follow-up

No implementation correction is required for COMMERCE-002. The task is Complete. The only current executable Phase 1 task is ARCH-021-COMMERCE-004; COMMERCE-005 remains dependency-gated on COMMERCE-004.
