---
id: ARCH-039-MCP-001
architecture_id: ARCH-039
title: Migrate MCP Merchant Knowledge keyring and embedding decryption to Shared
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-039-SHARED-004
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---


# Migrate MCP Merchant Knowledge keyring and embedding decryption to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_mcp` / `moda-interact-mcp`

## Objective

Migrate MCP Merchant Knowledge keyring and embedding decryption to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace `src/execution/merchant-knowledge/credential-keyring.ts` clone and `embedding-runtime.ts` local AES-GCM/AAD with published Shared code.

## Out of Scope

No general MCP server refactor or tenant policy changes.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- This MCP credential-reader task may read **only** `COMMERCE_CONNECTION_KEYS_JSON` from the closed set; it **must not** read or receive the active-key selector or command-HMAC secret. Decryption selects the stored envelope key ID.

- MCP receives only `COMMERCE_CONNECTION_KEYS_JSON`; it is a reader, never an encryption-key writer or command HMAC owner.
- Keep MCP private execution, tool/resource boundaries, tenant separation and embedding provider gating unchanged.
- Build `CredentialEnvelope` from stored embedding credential columns and call published `decryptCredential({ keyring, envelope, aad }): string` with `createCommerceEmbeddingCredentialAad`; never require the active writer key ID. Failures (including invalid UTF-8) must be bounded unavailable, never secret exposure or fallback plaintext.

## Work Items

- [x] Migrate imports and remove local parser/AEAD/AAD.
- [x] Update unit/integration embedding tests and negative config paths.
- [x] Confirm no credential API is exposed through MCP tools.

## Interfaces / Contracts

- `decryptCredential`, `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`, plus `createCommerceEmbeddingCredentialAad`. Do not preserve local AEAD or reimplement the former binary open helper.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [x] MCP uses only `COMMERCE_CONNECTION_KEYS_JSON` for this capability, not an alternate keyring, active selector or command HMAC; missing/legacy-only canonical configuration fails closed.

- [x] MCP `decryptCredential` reads Admin `encryptCredential` embedding envelopes using identical Shared AAD, with credential text returned only inside the private authorised runtime.
- [x] No competing parser or crypto module remains for Merchant Knowledge.
- [x] MCP tools cannot expose key bytes.

## Validation

- [x] Focused MCP keyring/embedding unit and integration tests where supported
- [x] MCP typecheck/build
- [x] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Preserve private host registration and existing MCP `capabilities.tools` behaviour.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Complete — Attempt 1 explicitly completed by the developer after the passing self-review.

### Files Changed

`package.json`; `package-lock.json`; deleted `src/execution/merchant-knowledge/credential-keyring.ts`; `src/execution/merchant-knowledge/embedding-runtime.ts`; `tests/integration/embedding-runtime.integration.test.ts`; `tests/unit/execution/merchant-knowledge/credential-keyring.test.ts`; `tests/unit/execution/merchant-knowledge/embedding-runtime.test.ts`.

### Work Completed

Replaced MCP's local keyring parser and AES-GCM/AAD implementation with Shared `parseCredentialKeyring`, `createCommerceEmbeddingCredentialAad`, and `decryptCredential`; upgraded the Shared package to 2.4.1. MCP reads only `COMMERCE_CONNECTION_KEYS_JSON`, selects the stored envelope key ID, and maps configuration/decryption failures to bounded unavailable results. Added coverage for Shared keyring validation, Admin-compatible AAD/envelopes, invalid UTF-8 and malformed credential values, and absence of active-key/HMAC dependencies. Confirmed MCP tool boundaries do not expose key bytes. Implementation committed and pushed as `9422dbf` on `task/ARCH-039-MCP-001`.

### Validation Results

Passed: focused keyring/embedding unit tests (10/10); full unit suite (140/140); `npm run typecheck`; `npm run build`; `npm run typecheck:integration`; changed-file ESLint; `git diff --check`. The database-backed embedding integration test was attempted but could not run because `MODA_MCP_DISPOSABLE_POSTGRES` is not configured; its integration TypeScript project passed typecheck.

### Deviations

The disposable-PostgreSQL integration test remains unexecuted in this environment. The package-lock update also includes npm lockfile metadata normalization for two optional packages.

### Assumptions

Shared 2.4.1 is the published package version providing the required credential APIs. The existing stored embedding envelope format and Admin AAD contract remain unchanged.

### Unresolved Issues

No code-level issues identified. A disposable PostgreSQL environment is still needed to execute the database-backed integration test.

### Architectural Concerns

The implementation stays within MCP ownership and preserves private execution and tool/resource boundaries. No task branch was merged into `main`.

## Architect Review

### Review Status

Pending

### Review Notes

Not yet reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.

## Developer Self-Review - Passed

### Reviewed Attempt

Attempt 1. The implementation branch is `task/ARCH-039-MCP-001`, clean after commit `9422dbf`, and published to `origin/task/ARCH-039-MCP-001`. The parent task branch remains `task/ARCH-039-MCP-001`; this report is the only parent task record being updated.

### Review Result

The implementation satisfies the task scope and acceptance criteria. Shared owns keyring parsing, envelope decryption, and canonical AAD; MCP consumes only `COMMERCE_CONNECTION_KEYS_JSON`. Focused and full unit tests, typecheck, build, integration typecheck, lint, and whitespace validation passed. The database-backed integration test could not run because no disposable PostgreSQL configuration was available; this limitation is recorded above.

### Decision

Passing self-review is recorded. Because `completion_mode` is `developer`, this task transitions to `review` and explicit developer completion remains pending. No branch was merged into `main`.

## Developer Completion Decision

- Date: 2026-10-14.
- Decision: the developer explicitly invoked `/moda_developer_update ARCH-039-MCP-001 complete` and accepts Attempt 1 following the passing developer self-review above.
- Lifecycle: `status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`.
- Implementation publication: commit `9422dbf875272360e6bcb8d69353d976fae7401b` is pushed to `origin/task/ARCH-039-MCP-001`.
- Parent publication: this completion decision is committed and pushed on `task/ARCH-039-MCP-001`.
- Dependency frontier: `ARCH-039-GATEWAY-001` remains `pending` because `ARCH-024-GATEWAY-001` is `ready` but not complete, and `ARCH-039-BACKGROUND-001`, `ARCH-039-BACKGROUND-002`, `ARCH-039-COMMERCE-001`, `ARCH-039-COMMERCE-002`, and `ARCH-039-API-002` remain incomplete. `ARCH-039-SYSTEM-TEST-001` remains `pending` because its explicit dependencies remain incomplete and its manual gate remains in force. No downstream task becomes ready from this completion.
- Integration: no task branch was merged to `main`.
