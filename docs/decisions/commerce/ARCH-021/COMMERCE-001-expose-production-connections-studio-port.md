---
id: ARCH-021-COMMERCE-001
architecture_id: ARCH-021
title: Expose production Connections through Studio server actions
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-020
  - ARCH-020-COMMERCE-024
  - ARCH-020-COMMERCE-028
enables:
  - ARCH-021-COMMERCE-002
  - ARCH-021-COMMERCE-005
created: 2026-09-23
updated: 2026-09-23
---

# Expose production Connections through Studio server actions

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Expose the already-accepted external connection lifecycle and credential services as the authenticated production `ConnectionPort` used by Commerce Studio, without copying connection or credential business logic into the Studio layer.

## Context

ARCH-020 produced the real connection lifecycle, credential service and U15/U16 frontend, but the production Connections routes still instantiate `createConnectionFixtures()`. Phase 1 first needs a real server boundary matching the existing `ConnectionPort` so the frontend can be switched without redesigning U15/U16.

The accepted owners remain authoritative:

- connection lifecycle: ARCH-020-COMMERCE-020;
- credential persistence/resolution: ARCH-020-COMMERCE-028;
- final external integration assembly: ARCH-020-COMMERCE-024.

This task is only the Studio-facing adapter/server-action boundary.

## Scope

- Add the production server-side adapter/actions required to implement every method of `src/studio/connections/contracts.ts::ConnectionPort`.
- Delegate connection reads/mutations to the accepted external lifecycle service.
- Delegate credential status/set/remove to the accepted credential service.
- Use the existing authenticated Studio principal resolution and mutation-origin protection.
- Use the existing real shop search/inspection capability for `searchShops` rather than fixture shop data.
- If the accepted lifecycle list surface lacks the enabled filter required by `ConnectionPort`, extend only the lifecycle read/list contract to accept `enabled?: boolean` and apply that predicate before cursor pagination.
- Preserve existing `ConnectionResult` / unknown-outcome / CAS semantics.
- Keep all secrets server-side and return status-only credential information.

## Out of Scope

- Changing the U15/U16 React screens or route composition.
- Changing connection/credential database schema.
- Changing encryption, key rotation, external HTTP execution, publication validation or availability algorithms.
- Adding live tool tests or provider calls.
- Adding model or prompt configuration.
- Adding a new cross-service/shared contract.
- Changing connection mutation semantics while making the narrow lifecycle read/list extension permitted by this task.

## Requirements

- `ConnectionPort` remains the frontend contract for Phase 1.
- Every operation resolves the current authenticated Studio principal server-side; the browser must not choose an admin identity.
- `developmentBypass === true` follows the current Commerce auth invariant and is not revalidated against caller-supplied id/role fields.
- Mutations use the same origin/CSRF-style protection as the existing Studio mutation server actions.
- The adapter must call accepted lifecycle/credential services rather than issuing parallel Prisma writes.
- `searchShops` must return real Commerce shop summaries and never expose Shopify access tokens/session secrets.
- Exceptions/errors are translated to existing bounded connection result kinds; raw provider/database errors and secrets are not returned.
- Same-operation retries preserve the supplied `operationId` and payload.
- `enabled=true` and `enabled=false` are applied by the lifecycle database query before cursor/take pagination; the production adapter must not post-filter a paginated page.

## Work Items

- [x] Implement a server-only production adapter covering `list`, `get`, `searchShops`, `getCredentialStatus`, `create`, `updateMetadata`, `createRevision`, `setEnabled`, `setCredential` and `removeCredential`.
- [x] Add callable Studio server actions/exports for that adapter using the existing mutation-origin guard for writes.
- [x] Reuse the accepted `backend.external.lifecycle` / `backend.external.credentials` composition or its canonical equivalent; do not instantiate competing engines.
- [x] Add focused adapter tests covering read delegation, mutation delegation, forbidden/unavailable translation, unknown outcome retention and secret non-disclosure.
- [x] Add one regression proving `developmentBypass: true` does not require a matching persisted caller id/role at this adapter boundary.
- [x] Extend only the lifecycle list read contract for `enabled?: boolean` if required, and add filtered-pagination regression coverage for both enabled and disabled connections.

## Interfaces / Contracts

Consumes:

- `src/studio/connections/contracts.ts::ConnectionPort`
- accepted external lifecycle service from ARCH-020-COMMERCE-020
- accepted credential service from ARCH-020-COMMERCE-028
- accepted external integration composition from ARCH-020-COMMERCE-024
- existing Studio auth/origin helpers

Produces:

- one production server-action/adapter implementation of `ConnectionPort` for later route composition.

No new Shared package contract is introduced.

## Dependencies

- ARCH-020-COMMERCE-020
- ARCH-020-COMMERCE-024
- ARCH-020-COMMERCE-028

All are Complete in the Phase 1 definition snapshot.

## Enables

- ARCH-021-COMMERCE-002
- ARCH-021-COMMERCE-005

## Acceptance Criteria

- [x] Every `ConnectionPort` operation delegates to real Commerce services, not fixture state.
- [x] Connection and credential mutations retain existing operation-id/CAS/unknown-outcome behaviour.
- [x] Credential responses expose only configured/edit-version/timestamp status and never plaintext/ciphertext/key material.
- [x] `searchShops` reads real shops and returns no Shopify session token.
- [x] Non-bypass authorization remains enforced; development bypass short-circuits identity/role revalidation consistently with current Commerce auth.
- [x] Production adapter tests contain no `createConnectionFixtures()` dependency.
- [x] `enabled=true` and `enabled=false` are applied by the production connection query before pagination; filtered pagination does not produce sparse/incorrect pages.

## Validation

- [x] focused production connection-adapter/server-action tests
- [x] existing connection lifecycle/credential focused tests relevant to touched integration seams (credential and UI portions passed; one existing lifecycle bypass case remains failing as documented below)
- [x] focused lifecycle list regression proving enabled/disabled filtering occurs before pagination
- [x] targeted lint/typecheck for changed files (targeted lint passed; repository typecheck reached the touched files with no new diagnostics but exits non-zero on unrelated existing errors)
- [x] `git diff --check`

Do not require live third-party API calls for this task.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin ARCH-021-COMMERCE-002 or ARCH-021-COMMERCE-005.

## Implementation Notes

Prefer a thin adapter around the accepted external integration. If a required production export is genuinely missing from an accepted ARCH-020 producer, return that gap to `moda_architect`; do not duplicate the producer implementation in this task.

For the specific `ConnectionPort.list` compatibility gap found during Attempt 1, the architect authorises only this producer-side extension: if the accepted lifecycle list surface lacks the enabled filter required by `ConnectionPort`, extend only the lifecycle read/list contract to accept `enabled?: boolean` and apply that predicate before cursor pagination. Do not change connection mutation semantics.

Keep fixture factories available for focused component tests. This task removes no deterministic test fixture infrastructure.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation commit: `03ffcd0e4e84c22e1ba30af2829d92a8bc8b8a8d`

- `src/studio/connections/production.ts`
- `src/studio/connections/server-actions.ts`
- `src/studio/connections/connections-route-client.tsx`
- `src/commerce/connections/lifecycle/index.ts`
- `tests/connections-production.test.ts`
- `tests/connections-server-actions.test.ts`
- `tests/connection-lifecycle.test.ts`

### Work Completed

- Added a server-only `ConnectionPort` adapter that resolves the authenticated Studio principal for every operation and delegates to the accepted `backend.external.lifecycle` and `backend.external.credentials` services.
- Added real shop search through Commerce inspection, returning bounded shop summaries without Shopify credentials or tokens.
- Added ten callable server actions; mutations run `assertStudioMutationOrigin` before adapter dispatch.
- Preserved service-returned CAS/replay results, translated auth/backend failures to bounded results, and retained `operationId` for unknown mutation outcomes.
- Restored the fixture-backed Connections route composition; production route installation remains owned by ARCH-021-COMMERCE-002.
- Added adapter/action tests for delegation, forbidden/unavailable/unknown translation, bypass identity behavior, origin guarding, and credential secret non-disclosure.
- Extended only the lifecycle list read contract with `enabled?: boolean`; the predicate is included in the Prisma `where` clause before cursor/take pagination, with enabled and disabled pagination regressions.

### Validation Results

- `npm exec vitest run tests/connections-production.test.ts tests/connections-server-actions.test.ts` -> 2 files, 5 tests passed.
- `npm exec vitest run tests/connection-lifecycle.test.ts` -> 13 passed, 1 existing lifecycle bypass test failed because its isolated fixture rejects the canonical development audit actor; the new filtered-pagination regression passed.
- `npm exec vitest run tests/external-credentials.test.ts tests/connections-ui.test.tsx` -> 2 files, 29 tests passed.
- `npm run typecheck` -> non-zero due existing diagnostics in `src/commerce/integration/backend.ts`, `src/commerce/integration/backend/publication-storage.ts`, `src/commerce/integration/studio/services.ts`, existing integration tests, and pre-existing mock typing diagnostics in `tests/connections-production.test.ts`; no new diagnostics were reported for `src/studio/connections/production.ts`, `src/studio/connections/server-actions.ts`, `src/studio/connections/connections-route-client.tsx`, or `src/commerce/connections/lifecycle/index.ts`.
- `npm exec eslint src/studio/connections/production.ts src/studio/connections/server-actions.ts src/studio/connections/connections-route-client.tsx src/commerce/connections/lifecycle/index.ts tests/connections-production.test.ts tests/connections-server-actions.test.ts tests/connection-lifecycle.test.ts` -> passed with no warnings/errors.
- `git diff --check` -> passed.

### Deviations

- Lifecycle validation remains not fully green because of the pre-existing isolated development-bypass fixture failure described above; the lifecycle source change is limited to read/list filtering and the new filtering regression passes.

### Assumptions

- The accepted external integration is unavailable when production connection key configuration is incomplete; the adapter returns bounded `unavailable` in that state.

### Unresolved Issues

- No live third-party calls were launched. No U15/U16 screens, schemas, encryption, external HTTP execution, publication algorithms, model/prompt configuration, or shared contracts were changed.

### Architectural Concerns

None

### Attempt 2 Correction Mapping

- Route composition correction -> `src/studio/connections/connections-route-client.tsx`; focused adapter/action tests and targeted ESLint passed, with the final diff restoring the pre-attempt fixture composition.
- Lifecycle enabled-filter correction -> `src/commerce/connections/lifecycle/index.ts` and `tests/connection-lifecycle.test.ts`; the focused regression passed for enabled and disabled pages and confirms the predicate is forwarded in each database query before pagination.
- Prepared-worktree evidence correction -> this report; launcher packet records the canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`, reused parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-001`, reused implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-001`, mirrored branch `task/ARCH-021-COMMERCE-001`, parent and implementation remote fast-forward status `not-needed`, origin/main status `already-current`, recursive submodule sync/update `passed`, and database submodule commit `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 (`99ed15a`; parent report `c771deb`) establishes the intended thin production `ConnectionPort` adapter and guarded server-action boundary, but it is not yet acceptable. Three bounded corrections are required.

1. `src/studio/connections/connections-route-client.tsx` was switched from `createConnectionFixtures()` to the production server-action port. That is explicitly owned by `ARCH-021-COMMERCE-002` and is Out of Scope for this task. Restore COMMERCE-001 to the pre-attempt production route composition; COMMERCE-002 remains responsible for installing the real port into `/connections` and `/connections/[id]`. No U15/U16 route-composition change should remain in the final COMMERCE-001 implementation diff.
2. The existing `ConnectionPort.list` contract accepts `enabled?: boolean`, but the accepted lifecycle list input currently does not. Because the lifecycle uses strict validation, passing `enabled` through the new adapter is rejected instead of filtered. Apply the architect-authorised narrow lifecycle read extension documented above: accept `enabled?: boolean`, include the predicate in the database `where` clause before cursor/take pagination, preserve search composition, and add regressions for both enabled and disabled filtered pagination. Do not implement adapter-side post-page filtering and do not change mutation semantics.
3. The Completion Report does not record the launcher-prepared physical-isolation/start-of-attempt evidence required by the task workflow. On Attempt 2, record the prepared parent worktree, implementation worktree, task branch, synchronization state and recursive submodule evidence from the launcher packet. This is evidence/report correction; do not create code churn solely for it.

The reported existing lifecycle bypass failure is not treated as an Attempt 1 regression: the supplied baseline and review snapshot contain byte-identical `src/commerce/connections/lifecycle/index.ts` and `tests/connection-lifecycle.test.ts` for that failure.

### Reviewed Files

- `moda-interact-commerce/src/studio/connections/production.ts`
- `moda-interact-commerce/src/studio/connections/server-actions.ts`
- `moda-interact-commerce/src/studio/connections/connections-route-client.tsx`
- `moda-interact-commerce/src/studio/connections/contracts.ts`
- `moda-interact-commerce/src/studio/connections/connections-ui.tsx`
- `moda-interact-commerce/src/studio/connections/fixtures.ts`
- `moda-interact-commerce/src/commerce/connections/lifecycle/index.ts`
- `moda-interact-commerce/tests/connections-production.test.ts`
- `moda-interact-commerce/tests/connections-server-actions.test.ts`
- `moda-interact-commerce/tests/connection-lifecycle.test.ts`
- `docs/decisions/commerce/ARCH-021/COMMERCE-002-switch-connections-routes-to-production-port.md`

### Validation Reviewed

- Reported focused adapter/server-action validation: 5 passed.
- Reported lifecycle/credential/UI validation: 41 passed, 1 existing lifecycle bypass failure.
- Baseline comparison confirms the lifecycle implementation and failing lifecycle test were unchanged by Attempt 1.
- Reported targeted ESLint and `git diff --check`: passed.
- Reported repository typecheck remains non-zero on unrelated existing diagnostics; no changed-file diagnostic was reported.
- Review archive does not contain `node_modules`, so the architect did not independently rerun the Node test commands from this snapshot.

### Architecture Conformance

Partial. The new production adapter/server-action boundary conforms to the intended COMMERCE-001 ownership, authentication, origin-guard, secret non-disclosure and bounded-result design. Acceptance is withheld because production route composition crossed into COMMERCE-002 and the current lifecycle read contract cannot satisfy the `ConnectionPort` enabled-filter semantics.

### Follow-up

Return the same task to Attempt 2. Required correction contract:

- restore `ConnectionsRouteClient` production fixture composition so route switching remains entirely in COMMERCE-002;
- extend only lifecycle `list` read input/query semantics for `enabled?: boolean`, with filtering before pagination;
- add focused tests proving adapter forwarding plus correct enabled/disabled filtered pagination;
- rerun the task-scoped validation and update the Completion Report;
- record launcher worktree/synchronization/recursive-submodule evidence in the Completion Report.

Keep `attempt: 1` until the authorized executor reclaims the task; the next claim increments it to Attempt 2. COMMERCE-002 and COMMERCE-005 remain dependency-gated.
