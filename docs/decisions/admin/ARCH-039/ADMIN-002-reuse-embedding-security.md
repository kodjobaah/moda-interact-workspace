---
id: ARCH-039-ADMIN-002
architecture_id: ARCH-039
title: Migrate Admin embedding credential writer and reader to Shared
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
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


# Migrate Admin embedding credential writer and reader to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_admin` / `moda-interact-admin`

## Objective

Migrate Admin embedding credential writer and reader to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Refactor `src/lib/admin/embedding-configuration-crypto.ts` and its service boundary to the published keyring, AEAD and embedding AAD helpers.

## Out of Scope

No embedding provider selection or index rebuild logic.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- This Admin credential-writer task may read **only** `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` from the closed set; it **must not** read or receive `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. Both inputs must be validated through published Shared helpers before an enabled credential write.

- All embedding config writes use `encryptCredential({ keyring, activeKeyId, plaintext, aad })` with UTF-8 credential **string**, canonical active key and published embedding AAD. All existing credential reads reconstruct a `CredentialEnvelope` from stored columns and call `decryptCredential({ keyring, envelope, aad }): string`, using the envelope key ID rather than an active selector.
- Retain provider/purpose/environment/tenant validation and existing admin permission checks.
- Delete duplicate local embedding AAD and crypto implementations, not the embedding service domain logic.

## Work Items

- [x] Migrate embedding crypto and AAD to Shared.
- [x] Update embedding credential round-trip/tamper/mismatched environment-purpose tests.
- [x] Validate error isolation and no credential exposure.

## Interfaces / Contracts

- `encryptCredential`, `decryptCredential`, `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`, plus `createCommerceEmbeddingCredentialAad` from Shared. Do not retain local seal/open helpers or duplicate AES-GCM.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Admin credential paths consume only canonical `COMMERCE_CONNECTION_KEYS_JSON` / `COMMERCE_CONNECTION_ACTIVE_KEY_ID`, never the command HMAC or legacy/alternate encryption names; missing or legacy-only settings fail closed.

- [x] An Admin `encryptCredential` embedding envelope is accepted by the published Shared `decryptCredential` contract with identical AAD and rejects wrong AAD or corrupted envelope.
- [x] Wrong environment/purpose/provider AAD is rejected.
- [x] No local embedding crypto/AAD clone remains.

## Validation

- [x] Focused Admin embedding tests
- [x] Admin typecheck and build (where provided)
- [x] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Coordinate via published Shared contracts; do not inspect/import MCP or Commerce private code.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Ready for Architect Review — Attempt 1 implementation is committed and pushed. Attempt remains 1; developer completion is not recorded.

### Files Changed

- `src/lib/admin/embedding-configuration.ts`
- `src/lib/admin/embedding-configuration-validation.ts`
- `src/app/actions/embedding-configuration.ts`
- `tests/security/admin-embedding-configuration.test.mjs`
- `tests/unit/embedding-credential-shared.test.ts`
- Minimal compatibility import/assertion updates in `src/app/actions/reference-taxonomy-index.ts`, `src/lib/admin/shopify-taxonomy.ts`, and `tests/security/admin-reference-taxonomy-index.test.mjs`, required after removing the local embedding crypto module.
- Shared Admin keyring/OpenRouter tests and helpers already owned by the completed ADMIN-001 predecessor commit `1f042b6feabfdc7668b51600012d0af4e2a0f986`; this commit is an ancestor of the ADMIN-002 branch, not part of ADMIN-002 commit `8251f9956120e701303e0ecf76b4c5e6717fd42e`.

### Work Completed

- Replaced local embedding AES-GCM/AAD logic with the published Shared `encryptCredential`, `decryptCredential`, `CredentialEnvelope`, keyring parsing and `createCommerceEmbeddingCredentialAad` APIs. Writes use validated UTF-8 secret strings, the canonical active key, and environment/purpose/provider/key-bound AAD; reads reconstruct the stored envelope and select its key ID without requiring the active writer key.
- Preserved domain secret validation, provider/purpose/environment scoping, authorization and safe error mapping. The existing embedding provider receives the decrypted runtime credential; browser/configuration status responses do not expose the stored envelope or secret.
- Deleted the duplicate `embedding-configuration-crypto.ts` implementation and its old local test. Updated the two taxonomy consumers to import the relocated validation error and use the Shared-backed configuration service, with a corresponding security-test expectation update.
- The implementation branch includes completed ADMIN-001 commit `1f042b6feabfdc7668b51600012d0af4e2a0f986` as its predecessor. ADMIN-001 is recorded `complete`; ADMIN-002's own commit is `8251f9956120e701303e0ecf76b4c5e6717fd42e`, pushed to `origin/task/ARCH-039-ADMIN-002`.

### Validation Results

- `node --test tests/security/admin-embedding-configuration.test.mjs`: passed, 5/5.
- `node --experimental-strip-types --test tests/unit/embedding-credential-shared.test.ts`: passed, 4/4. Covers Shared encryption/decryption interoperability, exact AAD identity binding, wrong environment/purpose/provider/key rejection, ciphertext/nonce/tag tampering, and missing/malformed keyring rejection.
- `node --test tests/security/admin-reference-taxonomy-index.test.mjs`: passed, 4/4.
- `npm run build`: passed, including Prisma generation and Next.js TypeScript checks. Non-blocking pre-existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` resolution warnings were emitted.
- `npx eslint` on all changed Admin embedding/taxonomy source files: passed with no diagnostics.
- Credential configuration scan found no command HMAC, legacy Woo keyring, or alternate key source in the changed Admin credential paths. The runtime embedding provider's `EMBEDDING_API_KEY` property is populated from the decrypted configuration and is not read from process environment as a credential source.
- `git diff --check` passed. Implementation worktree is clean; `HEAD` equals `origin/task/ARCH-039-ADMIN-002` at `8251f9956120e701303e0ecf76b4c5e6717fd42e`.
- Parent claim commit `25b8bcdbfab24f480852432af6f279ac5dd66b36` is pushed. Both canonical task worktrees are present; the parent worktree is clean before this review update.

### Deviations

- The initial review invocation encountered uncommitted mixed ADMIN-002 and taxonomy changes, so it stopped under the worktree isolation policy without modifying or discarding them. On this review invocation, the implementation changes were committed/pushed and the canonical worktree was clean. The taxonomy import/test adjustments are limited compatibility updates required by deletion/relocation of the embedding crypto module.

### Assumptions

None beyond the parent architecture.

### Unresolved Issues

None.

### Architectural Concerns

None.

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

## Developer Self-Review Passed/Accepted

- Attempt: 1.
- Result: Passed. All Work Items and Acceptance Criteria are satisfied by the committed implementation. Shared performs the credential cryptography; canonical key configuration fails closed; embedding AAD and envelope tampering are tested; existing authorization and safe-output boundaries remain covered.
- Evidence: focused Admin embedding tests 5/5, Shared adapter tests 4/4, taxonomy regression tests 4/4, Admin production build/TypeScript checks, changed-source lint, credential configuration scan and `git diff --check` passed. Implementation commit `8251f9956120e701303e0ecf76b4c5e6717fd42e` is pushed and the implementation worktree is clean.
- Lifecycle: `completion_mode: developer`; task transitioned to `review`, executor and claimed_at cleared, attempt remains 1. Explicit developer completion is pending review and a separate developer decision.
