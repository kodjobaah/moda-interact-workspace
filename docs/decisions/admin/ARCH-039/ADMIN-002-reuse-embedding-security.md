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
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-14T20:36:41Z
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

- [ ] Migrate embedding crypto and AAD to Shared.
- [ ] Update embedding credential round-trip/tamper/mismatched environment-purpose tests.
- [ ] Validate error isolation and no credential exposure.

## Interfaces / Contracts

- `encryptCredential`, `decryptCredential`, `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`, plus `createCommerceEmbeddingCredentialAad` from Shared. Do not retain local seal/open helpers or duplicate AES-GCM.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Admin credential paths consume only canonical `COMMERCE_CONNECTION_KEYS_JSON` / `COMMERCE_CONNECTION_ACTIVE_KEY_ID`, never the command HMAC or legacy/alternate encryption names; missing or legacy-only settings fail closed.

- [ ] An Admin `encryptCredential` embedding envelope is accepted by Commerce/MCP `decryptCredential` with identical AAD and rejects wrong AAD or corrupted envelope.
- [ ] Wrong environment/purpose/provider AAD is rejected.
- [ ] No local embedding crypto/AAD clone remains.

## Validation

- [ ] Focused Admin embedding tests
- [ ] Admin typecheck and build (where provided)
- [ ] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Coordinate via published Shared contracts; do not inspect/import MCP or Commerce private code.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-14T20:36:41Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

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
