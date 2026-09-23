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
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
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

- [ ] Implement a server-only production adapter covering `list`, `get`, `searchShops`, `getCredentialStatus`, `create`, `updateMetadata`, `createRevision`, `setEnabled`, `setCredential` and `removeCredential`.
- [ ] Add callable Studio server actions/exports for that adapter using the existing mutation-origin guard for writes.
- [ ] Reuse the accepted `backend.external.lifecycle` / `backend.external.credentials` composition or its canonical equivalent; do not instantiate competing engines.
- [ ] Add focused adapter tests covering read delegation, mutation delegation, forbidden/unavailable translation, unknown outcome retention and secret non-disclosure.
- [ ] Add one regression proving `developmentBypass: true` does not require a matching persisted caller id/role at this adapter boundary.

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

- [ ] Every `ConnectionPort` operation delegates to real Commerce services, not fixture state.
- [ ] Connection and credential mutations retain existing operation-id/CAS/unknown-outcome behaviour.
- [ ] Credential responses expose only configured/edit-version/timestamp status and never plaintext/ciphertext/key material.
- [ ] `searchShops` reads real shops and returns no Shopify session token.
- [ ] Non-bypass authorization remains enforced; development bypass short-circuits identity/role revalidation consistently with current Commerce auth.
- [ ] Production adapter tests contain no `createConnectionFixtures()` dependency.

## Validation

- [ ] focused production connection-adapter/server-action tests
- [ ] existing connection lifecycle/credential focused tests relevant to touched integration seams
- [ ] targeted lint/typecheck for changed files
- [ ] `git diff --check`

Do not require live third-party API calls for this task.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin ARCH-021-COMMERCE-002 or ARCH-021-COMMERCE-005.

## Implementation Notes

Prefer a thin adapter around the accepted external integration. If a required production export is genuinely missing from an accepted ARCH-020 producer, return that gap to `moda_architect`; do not duplicate the producer implementation in this task.

Keep fixture factories available for focused component tests. This task removes no deterministic test fixture infrastructure.

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
