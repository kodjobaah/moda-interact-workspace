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
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-09-23T10:49:02Z
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

- [ ] Replace fixture-port construction in `ConnectionsRouteClient`/route composition with the production ConnectionPort.
- [ ] Preserve dependency injection for `ConnectionsPage` component tests.
- [ ] Add route/composition tests proving production list/detail reads come from the production adapter.
- [ ] Add a regression that fails if production route code imports/instantiates the fixture factory.
- [ ] Re-run existing U15/U16 frontend tests against fixture injection to prove no component behaviour regressed.

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

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

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

Pending

### Follow-up

None
