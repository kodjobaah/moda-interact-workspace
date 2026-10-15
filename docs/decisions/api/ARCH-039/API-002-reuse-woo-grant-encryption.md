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
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-039-SHARED-004
  - ARCH-039-API-001
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-15
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

- [x] Migrate envelope functions and related tests to Shared.
- [x] Prove API encrypt -> Background-compatible AAD/vector (through contract tests); tampering and tenant mismatch fail.
- [x] Confirm no `createCipheriv`/`createDecipheriv` duplicate remains for this grant path.

## Interfaces / Contracts

- Import `encryptCredential`, `decryptCredential` (only where the API reads grants), `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`; use published `createWooRestReadGrantAad` and stable Woo grant fields. No alternative `sealCredential` / `openCredential` implementation.

## Dependencies

- ARCH-039-SHARED-004
- ARCH-039-API-001

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Woo API credential paths only use the two canonical encryption variables; legacy-only configuration cannot enable the encrypted capability and command HMAC is never consumed.

- [x] API-produced grants call published `encryptCredential` with the validated Woo JSON-string payload and exact shared Woo AAD; any API reads use `decryptCredential`.
- [x] No competing Woo AES implementation or local AAD clone remains.
- [x] Grant authorisation, revocation and secret handling remain strict.

## Validation

- [x] Focused API Woo read-grant and authorisation tests
- [x] API integration tests using disposable Postgres where required/available
- [x] API typecheck/build, changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

The independent Background consumer task remains responsible for its own tenant/runtime checks.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Complete — Attempt 1 explicitly completed by the developer after the passing self-review. Attempt 0 review history is preserved below.

### Files Changed

- `moda-interact-api/src/woocommerce/rest-read/README.md`
- `moda-interact-api/src/woocommerce/rest-read/authorization-return-locale.test.ts`
- `moda-interact-api/src/woocommerce/rest-read/authorization.test.ts`
- `moda-interact-api/src/woocommerce/rest-read/config.test.ts`
- `moda-interact-api/src/woocommerce/rest-read/config.ts`
- `moda-interact-api/src/woocommerce/rest-read/envelope.ts`
- `moda-interact-api/src/woocommerce/rest-read/provider-connection.service.ts`
- `moda-interact-api/src/woocommerce/rest-read/provider-connection.test.ts`
- `moda-interact-api/src/woocommerce/rest-read/return-locale-proof.test.ts`
- `moda-interact-api/src/woocommerce/rest-read/return-locale-proof.ts`

### Work Completed

- Replaced local Woo grant AES-GCM and the duplicated grant AAD with Shared `encryptCredential`, `decryptCredential`, and `createWooRestReadGrantAad`; retained API-owned database-column mapping and JSON-array domain validation.
- Removed the raw AES-key map from runtime configuration. API Woo credential operations now use Shared keyring parsing and active-key resolution from only `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID`; command-HMAC configuration is not consumed.
- Replaced the return-locale proof's raw-key HMAC adapter with a randomized Shared AES-GCM v2 envelope bound to the authorization attempt, shop and locale. Invalid or old proof formats are ignored and the existing shop-locale fallback remains.
- Implementation commit `b02d6dda98b3c0f849edfc1e266c8b0a26be8f0c` is published on `task/ARCH-039-API-002`; the canonical implementation worktree is clean and synchronized with its remote.

### Validation Results

- Focused Woo REST-read configuration, envelope, authorization, provider-read and locale-proof tests: 25 passed, 0 failed.
- Disposable PostgreSQL authorization/provider integration: 4 passed, 0 failed; migration deployment and isolated test database completed successfully.
- `npm run typecheck`: passed.
- `npm run build`: passed.
- Changed-file ESLint on the nine changed TypeScript implementation/test files: passed.
- `git diff --check origin/main...HEAD`: passed; implementation worktree is clean.
- Contract evidence: API encryption output was independently decrypted using the documented AES-GCM envelope fields and `createWooRestReadGrantAad`; the test asserts the exact serialized AAD vector and verifies wrong-shop, wrong-attempt, tamper and missing-key failures. Shared `decryptCredential` is the consumer API required by the separate Background-002 migration; Background runtime-consumer validation remains that task's responsibility.

### Deviations

- The raw-key config adapter was also used by the return-locale proof. To remove raw key exposure, that proof changed from v1 derived HMAC to v2 randomized Shared AES-GCM. Old v1 presentation proofs are not accepted after cutover; the return page ignores invalid proofs and falls back to the persisted shop locale. This is recorded in the REST-read README and covered by tests.

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
- Result: Passed. The Woo grant envelope uses only the published Shared crypto and Woo AAD API; the API config consumes only the two permitted canonical encryption variables, and grant authorization/revocation behavior remains covered.
- Evidence: focused tests 25/25; disposable PostgreSQL integration 4/4; typecheck, build, changed-file ESLint and `git diff --check origin/main...HEAD` passed. Implementation commit `b02d6dda98b3c0f849edfc1e266c8b0a26be8f0c` is pushed, and its canonical implementation worktree is clean.
- Compatibility note: locale proof format is now v2; old proofs are ignored with the existing shop-locale fallback. This adjacent migration is documented above and in the API README.
- Lifecycle: `completion_mode: developer`; Attempt 1 passed self-review and is submitted as `review`. Explicit developer completion remains pending. Attempt remains 1.

## Developer Completion Decision

- Date: 2026-10-15.
- Decision: the developer explicitly invoked `/moda_developer_update ARCH-039-API-002 complete` and accepts Attempt 1 following the passing developer self-review above.
- Lifecycle: `status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`. The attempt number is unchanged.
- Implementation publication: commit `b02d6dda98b3c0f849edfc1e266c8b0a26be8f0c` is pushed to `origin/task/ARCH-039-API-002`; the implementation worktree is clean.
- Parent publication: this completion decision is committed and pushed on `task/ARCH-039-API-002`; no task branch is merged to `main`.
- Dependency frontier: `ARCH-039-GATEWAY-001` remains `pending` because `ARCH-024-GATEWAY-001` is `ready`, and `ARCH-039-BACKGROUND-002` and `ARCH-039-COMMERCE-002` are `ready` but not complete. `ARCH-039-SYSTEM-TEST-001` remains `pending` because those consumer tasks and `ARCH-039-GATEWAY-001` are incomplete; its manual gate remains in force. No downstream task is promoted by this completion.
