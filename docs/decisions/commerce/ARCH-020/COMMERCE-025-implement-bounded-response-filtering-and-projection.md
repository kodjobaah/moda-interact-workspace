---
id: ARCH-020-COMMERCE-025
architecture_id: ARCH-020
title: Implement bounded response filtering and projection
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor: copilot
claimed_at: 2026-09-21T22:20:11Z
attempt: 1
depends_on:
  - ARCH-020-SHARED-002
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
  - ARCH-020-COMMERCE-030
  - ARCH-020-COMMERCE-031
created: 2026-09-21
updated: 2026-09-21
---

# Implement bounded response filtering and projection

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/external-response/** and focused pure tests only. Implement C21 section2.1 createResponseProcessor; no network, application factories, persistence, UI or arbitrary scripts.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/external-response/** and focused pure tests only. Implement C21 section2.1 createResponseProcessor; no network, application factories, persistence, UI or arbitrary scripts.

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

- [x] Implement deterministic OBJECT/LIST projection, AND filtering, stable sort, bounded limit and own-property paths exactly as section2.1.
- [x] Use supplied signal/clock/deadline, enforce row/field/value limits and return typed failures without copying raw data into output.
- [x] Expose reusable pure port for production executor and preview; document input/result fixtures used by021/023/024. Do not mutate caller objects or keep shared request state.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-SHARED-002

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024
- ARCH-020-COMMERCE-030
- ARCH-020-COMMERCE-031

## Acceptance Criteria

- [x] X10: golden samples prove output field removal/rename, type-strict comparisons, null/missing behavior, Unicode order and stable ties.
- [x] 1001 rows fail rather than truncate, abort/deadline checked, unsafe paths rejected; two concurrent invocations cannot contaminate results.
- [x] No networking, secrets or eval dependency; old response rendering unchanged because processor is a separate stage.

## Validation

Provide `test:arch020-response-processing` in the owning repository and document its exact scope.
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

- `moda-interact-commerce/src/commerce/external-response/index.ts`
- `moda-interact-commerce/tests/response-processing.test.ts`
- `moda-interact-commerce/package.json`
- `moda-interact-commerce/package-lock.json`

### Work Completed

- Implemented server-only `createResponseProcessor({now})` for C21 visual OBJECT/LIST processing.
- Added own-property-safe scalar projection, strict filters, code-point sorting with stable ties, null/missing handling, bounded rows/fields/filters/limits, and typed deadline/cancellation failures.
- Added focused tests for projection, strict filters, null/missing behavior, Unicode ordering, stable ties, unsafe paths, scalar validation, row bounds, cancellation and deadlines.
- Aligned the Commerce dependency with the accepted `@modainteract/moda-interact-shared@0.14.2` contract.

### Validation Results

Agent-executed validation:

- `npm run test:arch020-response-processing`: passed, 5/5 tests.
- `npm run lint`: passed with two pre-existing warnings in `scripts/code-runtime-manifest.mjs` and `src/commerce/code-response/runtime/kernel.ts`; no errors in changed files.
- `npm run typecheck`: repository baseline remains failing in unrelated Prisma/execution/integration files; no diagnostics remain for `src/commerce/external-response` or `tests/response-processing.test.ts`.
- `git diff --check`: passed.

Implementation repository commit: `44f9138` (`feat(ARCH-020-COMMERCE-025): add bounded response processor`), pushed to `origin/task/ARCH-020-COMMERCE-025`.

### Deviations

The canonical implementation worktree was absent and was recreated at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-025`; its recorded `database` submodule was initialized at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`. No unrelated source or parent gitlink was changed.

### Assumptions

C21 read-only visual processing only; the separate JavaScript processor remains out of scope. Missing and non-scalar filter fields do not match, including `NE`; `EQ`/`NE` use identical scalar types as specified by C21.

### Unresolved Issues

Repository-wide typecheck is blocked by the existing generated Prisma/client and execution/integration type errors outside this task. Focused behavior tests, lint, and touched-file type diagnostics pass.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Expected mirrored branch: `task/ARCH-020-COMMERCE-025`. Implementation commit `44f9138` is pushed. Parent task metadata is being returned on the same mirrored branch for architect review; no merge, self-acceptance, or main update performed.

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
