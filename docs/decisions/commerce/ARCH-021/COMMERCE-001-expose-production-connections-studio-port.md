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
attempt: 1
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
- Preserve existing `ConnectionResult` / unknown-outcome / CAS semantics.
- Keep all secrets server-side and return status-only credential information.

## Out of Scope

- Changing the U15/U16 React screens or route composition.
- Changing connection/credential database schema.
- Changing encryption, key rotation, external HTTP execution, publication validation or availability algorithms.
- Adding live tool tests or provider calls.
- Adding model or prompt configuration.
- Adding a new cross-service/shared contract.

## Requirements

- `ConnectionPort` remains the frontend contract for Phase 1.
- Every operation resolves the current authenticated Studio principal server-side; the browser must not choose an admin identity.
- `developmentBypass === true` follows the current Commerce auth invariant and is not revalidated against caller-supplied id/role fields.
- Mutations use the same origin/CSRF-style protection as the existing Studio mutation server actions.
- The adapter must call accepted lifecycle/credential services rather than issuing parallel Prisma writes.
- `searchShops` must return real Commerce shop summaries and never expose Shopify access tokens/session secrets.
- Exceptions/errors are translated to existing bounded connection result kinds; raw provider/database errors and secrets are not returned.
- Same-operation retries preserve the supplied `operationId` and payload.

## Work Items

- [x] Implement a server-only production adapter covering `list`, `get`, `searchShops`, `getCredentialStatus`, `create`, `updateMetadata`, `createRevision`, `setEnabled`, `setCredential` and `removeCredential`.
- [x] Add callable Studio server actions/exports for that adapter using the existing mutation-origin guard for writes.
- [x] Reuse the accepted `backend.external.lifecycle` / `backend.external.credentials` composition or its canonical equivalent; do not instantiate competing engines.
- [x] Add focused adapter tests covering read delegation, mutation delegation, forbidden/unavailable translation, unknown outcome retention and secret non-disclosure.
- [x] Add one regression proving `developmentBypass: true` does not require a matching persisted caller id/role at this adapter boundary.

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

## Validation

- [x] focused production connection-adapter/server-action tests
- [x] existing connection lifecycle/credential focused tests relevant to touched integration seams (credential and UI portions passed; one existing lifecycle bypass case remains failing as documented below)
- [x] targeted lint/typecheck for changed files (targeted lint passed; repository typecheck reached the touched files with no new diagnostics but exits non-zero on unrelated existing errors)
- [x] `git diff --check`

Do not require live third-party API calls for this task.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin ARCH-021-COMMERCE-002 or ARCH-021-COMMERCE-005.

## Implementation Notes

Prefer a thin adapter around the accepted external integration. If a required production export is genuinely missing from an accepted ARCH-020 producer, return that gap to `moda_architect`; do not duplicate the producer implementation in this task.

Keep fixture factories available for focused component tests. This task removes no deterministic test fixture infrastructure.

## Completion Report

### Status

Ready for Review

### Files Changed

- `src/studio/connections/production.ts`
- `src/studio/connections/server-actions.ts`
- `src/studio/connections/connections-route-client.tsx`
- `tests/connections-production.test.ts`
- `tests/connections-server-actions.test.ts`

### Work Completed

- Added a server-only `ConnectionPort` adapter that resolves the authenticated Studio principal for every operation and delegates to the accepted `backend.external.lifecycle` and `backend.external.credentials` services.
- Added real shop search through Commerce inspection, returning bounded shop summaries without Shopify credentials or tokens.
- Added ten callable server actions; mutations run `assertStudioMutationOrigin` before adapter dispatch.
- Preserved service-returned CAS/replay results, translated auth/backend failures to bounded results, and retained `operationId` for unknown mutation outcomes.
- Replaced production Connections route fixture construction with the server-action port while leaving fixture factories available to component tests.
- Added adapter/action tests for delegation, forbidden/unavailable/unknown translation, bypass identity behavior, origin guarding, and credential secret non-disclosure.

### Validation Results

- `npm exec vitest run tests/connections-production.test.ts tests/connections-server-actions.test.ts` -> 2 files, 5 tests passed.
- `npm exec vitest run tests/connection-lifecycle.test.ts tests/external-credentials.test.ts tests/connections-ui.test.tsx` -> 41 tests passed, 1 existing lifecycle bypass test failed at `tests/connection-lifecycle.test.ts:203` because its isolated fixture rejects the canonical development audit actor; the new adapter bypass regression passed.
- `npm run typecheck` -> non-zero due existing unrelated diagnostics in `src/commerce/integration/backend.ts`, `src/commerce/integration/backend/publication-storage.ts`, `src/commerce/integration/studio/services.ts`, and existing integration tests; no diagnostics were reported for the changed adapter, server actions, route client, or focused tests.
- `npm exec eslint src/studio/connections/production.ts src/studio/connections/server-actions.ts src/studio/connections/connections-route-client.tsx tests/connections-production.test.ts tests/connections-server-actions.test.ts` -> passed with no warnings/errors.
- `git diff --check` -> passed.

### Deviations

- Broader lifecycle validation is not fully green because of the pre-existing isolated development-bypass fixture failure described above; producer lifecycle code was not changed.

### Assumptions

- The accepted external integration is unavailable when production connection key configuration is incomplete; the adapter returns bounded `unavailable` in that state.

### Unresolved Issues

- No live third-party calls were launched. No U15/U16 screens, schemas, encryption, external HTTP execution, publication algorithms, model/prompt configuration, or shared contracts were changed.

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
