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
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
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
- Preserve route return state and `returnTo` behaviour already accepted under ARCH-020.
- Ensure fixture factories are imported only by tests/dev fixtures, not by production route composition.

## Out of Scope

- Connection lifecycle/credential business logic.
- Shop execution-context selection across the rest of Studio.
- Tool editor connection selection.
- Live external/Shopify requests.
- Prompt/model configuration.
- Redesigning U15/U16 styling or fields.

## Requirements

- The production route must never instantiate `createConnectionFixtures()`.
- The route/client composition must use the exact production adapter from ARCH-021-COMMERCE-001.
- Server-authorised results remain authoritative; frontend role presentation is not security enforcement.
- Unknown mutation outcomes continue to retain the exact original operation/payload for reconciliation.
- Credential secret values must never be loaded back into the browser after save.
- Existing ADMIN read-only and SUPER_ADMIN mutation behaviour remains unchanged.

## Work Items

- [x] Replace fixture-port construction in `ConnectionsRouteClient`/route composition with the production ConnectionPort.
- [x] Preserve dependency injection for `ConnectionsPage` component tests.
- [x] Add route/composition tests proving production list/detail reads come from the production adapter.
- [x] Add a regression that fails if production route code imports/instantiates the fixture factory.
- [x] Re-run existing U15/U16 frontend tests against fixture injection to prove no component behaviour regressed.

## Interfaces / Contracts

Consumes:

- production `ConnectionPort` from ARCH-021-COMMERCE-001
- existing U15/U16 `ConnectionsPage` and `ConnectionPort` contract from ARCH-020-COMMERCE-022

Produces:

- production-backed Connections routes.

No new runtime contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-001
- ARCH-020-COMMERCE-022

## Enables

None within Phase 1. This task may execute in parallel with the shop-context branch once ARCH-021-COMMERCE-001 is Complete.

## Acceptance Criteria

- [ ] `/connections` lists real persisted connections through the production port.
- [ ] `/connections/[id]` reads and mutates the selected persisted connection through the production port.
- [ ] PER_SHOP credential search/status/set/remove operates against real shop/credential services while exposing no secret values.
- [ ] `createConnectionFixtures()` is absent from production route composition and remains available to tests.
- [ ] Existing U15/U16 role, CAS, unknown-result and navigation behaviours remain passing.

## Validation

- [ ] existing `test:arch020-connections-ui` or current equivalent
- [ ] focused production route/composition test
- [ ] targeted lint/typecheck for changed files
- [ ] `git diff --check`

No live provider network call is required.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

## Implementation Notes

Do not collapse frontend fixture tests into database integration tests. Keep the existing component port injection and add only the production composition proof needed by this task.

## Completion Report

### Status

Ready for architect review

### Files Changed

- `src/studio/connections/connections-route-client.tsx`
- `tests/connections-route-composition.test.tsx`
- `tests/connections-ui.test.tsx`

### Work Completed

- Replaced production fixture construction with a stable client-safe `ConnectionPort` whose operations invoke the production server actions.
- Preserved the `ConnectionsPage` port injection boundary used by fixture-based component tests.
- Added composition coverage for production list/detail delegation and a source regression excluding `createConnectionFixtures()` from the production route module.
- Kept fixture factories available to existing component tests and preserved U15/U16 behavior.

### Validation Results

- `npm run test:arch020-connections-ui`: PASS, 20 tests.
- `npx vitest run tests/connections-production.test.ts tests/connections-route-composition.test.tsx`: PASS, 6 tests.
- `npx eslint src/studio/connections/connections-route-client.tsx tests/connections-route-composition.test.tsx tests/connections-ui.test.tsx src/studio/connections/production.ts`: PASS.
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

- implementation: `267f3bd` (`Switch connections routes to production port`)

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

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
