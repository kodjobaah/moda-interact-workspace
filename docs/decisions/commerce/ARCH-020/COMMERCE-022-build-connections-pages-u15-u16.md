---
id: ARCH-020-COMMERCE-022
architecture_id: ARCH-020
title: Build Connections pages U15 and U16
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 155
executor: copilot
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-002
  - ARCH-020-COMMERCE-008
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-21
---

# Build Connections pages U15 and U16

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Frontend only: src/studio/connections/**, app/connections/page.tsx, app/connections/[id]/page.tsx and one sidebar item. Follow exact C21 U15/U16 screens and section4 ports with fixtures. No U06 or backend edits.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Frontend only: src/studio/connections/**, app/connections/page.tsx, app/connections/[id]/page.tsx and one sidebar item. Follow exact C21 U15/U16 screens and section4 ports with fixtures. No U06 or backend edits.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [ ] Implement exact fields, tabs, dialogs, search/pagination/return navigation and permission presentation specified in section6. Add Connections after Explore Shopify.
- [ ] Credential controls use status-only reads, replace/remove dialogs, explicit reason/CAS and no reveal or browser persistence. Do not claim frontend masking is server authorization.
- [ ] Apply immediate guards to every mutation, retain operation/payload on unknown outcomes and reconcile same command. Revision selection never silently changes to latest.
- [ ] Document component port mapping and XN01 evidence. Use existing styles/components; provide narrow and keyboard validation with populated fixtures.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-002
- ARCH-020-COMMERCE-008

## Enables
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024


## Acceptance Criteria

- [ ] X05/XN01: new connection -> exact revision -> credential status -> list, plus revision creation without copied secret, all against strict port fixtures.
- [ ] ADMIN read-only, pending/double-click, stale/unknown, cancellation/unsaved navigation, missing key and revoked-session states work without secret leakage.
- [ ] No backend or network implementation; component builds with fixture ports before020/021 complete.

## Validation

Provide `test:arch020-connections-ui` in the owning repository and document its exact scope.
Run focused changed-boundary tests, then existing repository typecheck/build
and lint where defined. Inspect package scripts first; do not invent a claim that
an absent script passed. Use C21 controlled transports and isolated stores.
Follow current developer-owned live/container validation policy; clearly separate
actual agent results from required unrun developer checks. No arbitrary screenshot
quota or repeated full-suite runs without new changes/failures.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Ready for Review.

### Files Changed

Implementation branch contains the nine task-scoped files listed below.

### Work Completed

Implemented U15/U16 Connections pages using typed fixture ports, added the
Connections sidebar item after Explore Shopify, and added the declared focused
test script. The UI supports search, enabled filtering, pagination, detail tabs,
immutable revision selection/creation, credential status-only reads, explicit
SUPER_ADMIN reason acknowledgements, duplicate-click guards, same-operation
credential retry retention, unknown-outcome messaging, ADMIN read-only controls,
and return navigation retaining search.

The launcher claim step was attempted but could not repair durable claim state
because the existing implementation worktree was already dirty. The dirty files
matched this task scope exactly, so the implementation was preserved and
submitted with `attempt: 0` and no claimed timestamp.

### Validation Results

Agent-executed validation:

- `npm run test:arch020-connections-ui`: passed, 1 file and 4 tests.
- `npm run lint`: passed with 0 errors and 2 existing warnings outside the task
  (`scripts/code-runtime-manifest.mjs` and
  `src/commerce/code-response/runtime/kernel.ts`).
- `git diff --check`: passed.
- VS Code diagnostics for the changed Connections UI and focused test: no
  errors.

`npm run typecheck` was run but is blocked by existing repository-wide Prisma
and publication typing failures: 188 errors in 7 files, outside the task files.
No typecheck error was reported for the changed Connections UI or focused test.

### Deviations

The canonical launcher could not complete its claim phase because the isolated
implementation worktree was already dirty. No dirty file was discarded or reset.
The implementation was validated in place and the parent report was updated on
the mirrored task branch for architect review.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox.
The implementation uses shared package `@modainteract/moda-interact-shared@0.14.2`
for the approved commerce view/input types.

### Unresolved Issues

Repository-wide typecheck remains unresolved outside this task; focused tests,
lint, diagnostics and whitespace checks pass. No live, deployment, database or
backend validation was required or run.

### Architectural Concerns

No architectural contradiction identified. The repository-wide typecheck
failures are pre-existing and outside the owned frontend boundary.

### Git / VCS

Expected mirrored branch: `task/ARCH-020-COMMERCE-022`.

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-022`.
Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-022`.
The implementation worktree was physically isolated and contained only the
task-scoped dirty files at continuation. Dependency pin: shared `0.14.2`.
Implementation commit: `dd0164b` (`feat(commerce): build connections studio pages`).
Parent report commit and both remote push results are recorded in the final
submission after publication.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation acceptance.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.
