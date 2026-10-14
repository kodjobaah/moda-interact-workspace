---
id: ARCH-039-API-002
architecture_id: ARCH-039
title: Migrate Woo REST-read grant AES-GCM implementation to Shared
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-039-SHARED-004
  - ARCH-039-API-001
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---


# Migrate Woo REST-read grant AES-GCM implementation to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_api` / `moda-interact-api`

## Objective

Migrate Woo REST-read grant AES-GCM implementation to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace crypto and duplicated Woo grant AAD in `src/woocommerce/rest-read/envelope.ts` with published `encryptCredential` / `decryptCredential` and the Woo AAD builder. Map the shared envelope to the existing Woo grant database columns; keep that mapping API-owned.
- Keep the existing Woo grant database fields and API business validation.

## Out of Scope

No database schema migration or provider API redesign.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- API Woo credential operations may read **only** `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` from the closed set; they **must not** read or receive `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. `MODA_WOO_REST_READ_KEYRING` and `MODA_WOO_REST_READ_ACTIVE_KEY_ID` are forbidden even as fallback aliases.

- AES key/ID comes only from API-001 canonical configuration.
- Serialize the existing validated Woo consumer key/secret **JSON array as a string**, and pass it to `encryptCredential({ keyring, activeKeyId, plaintext, aad })`. For any API-local read, call `decryptCredential({ keyring, envelope, aad }): string` and validate the resulting JSON in API domain code. The API retains value validation, cleanup, tenant/installation binding and safe error mapping.
- No backwards reader or re-encryption migration: pre-production encrypted grants are developer-cleared before cutover.

## Work Items

- [ ] Migrate envelope functions and related tests to Shared.
- [ ] Prove API encrypt -> Background-compatible AAD/vector (through contract tests); tampering and tenant mismatch fail.
- [ ] Confirm no `createCipheriv`/`createDecipheriv` duplicate remains for this grant path.

## Interfaces / Contracts

- Import `encryptCredential`, `decryptCredential` (only where the API reads grants), `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`; use published `createWooRestReadGrantAad` and stable Woo grant fields. No alternative `sealCredential` / `openCredential` implementation.

## Dependencies

- ARCH-039-SHARED-004
- ARCH-039-API-001

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Woo API credential paths only use the two canonical encryption variables; legacy-only configuration cannot enable the encrypted capability and command HMAC is never consumed.

- [ ] API-produced grants call published `encryptCredential` with the validated Woo JSON-string payload and exact shared Woo AAD; any API reads use `decryptCredential`.
- [ ] No competing Woo AES implementation or local AAD clone remains.
- [ ] Grant authorisation, revocation and secret handling remain strict.

## Validation

- [ ] Focused API Woo read-grant and authorisation tests
- [ ] API integration tests using disposable Postgres where required/available
- [ ] API typecheck/build and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

The independent Background consumer task remains responsible for its own tenant/runtime checks.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Not Started

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
