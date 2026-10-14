---
id: ARCH-039-API-001
architecture_id: ARCH-039
title: Replace Woo REST-read API-specific keyring configuration
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
enables:
  - ARCH-039-API-002
created: 2026-10-14
updated: 2026-10-14
---


# Replace Woo REST-read API-specific keyring configuration

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_api` / `moda-interact-api`

## Objective

Replace Woo REST-read API-specific keyring configuration. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Migrate `src/woocommerce/rest-read/config.ts`, relevant runtime configuration typing/startup/dev scripts and operator documentation to `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID`.
- Preserve `MODA_WOO_REST_READ_PUBLIC_ORIGIN` as a *non-keyring* Woo-specific configuration input.

## Out of Scope

No changes to WooCommerce merchant PHP/plugin secret storage.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- API Woo credential operations may read **only** `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` from the closed set; they **must not** read or receive `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. `MODA_WOO_REST_READ_KEYRING` and `MODA_WOO_REST_READ_ACTIVE_KEY_ID` are forbidden even as fallback aliases.

- Remove `MODA_WOO_REST_READ_KEYRING` and `MODA_WOO_REST_READ_ACTIVE_KEY_ID` from the API runtime and documentation; no dual-read or base64url compatibility mode.
- Parse strict Shared keyring/active selector only; partial configuration fails closed.
- The endpoint remains explicitly disabled when Woo authorisation is intentionally not configured, but malformed/incomplete enabled config must fail.
- Preserve public-origin SSRF/security checks and API authorisation rules.

## Work Items

- [x] Change API config parser/typing, tests and dev startup examples.
- [x] Remove old env var references in API source/scripts/docs, excluding unavoidable historical task docs.
- [x] Verify enable/disable/configuration negative test matrix.

## Interfaces / Contracts

- Published Shared keyring and active-key helpers; canonical key IDs and padded Base64.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-API-002

## Acceptance Criteria

- [x] Woo API credential paths only use the two canonical encryption variables; legacy-only configuration cannot enable the encrypted capability and command HMAC is never consumed.

- [x] API only reads the canonical keyring and active selector for Woo REST-read encryption.
- [x] No Woo-specific duplicate keyring config remains in runtime.
- [x] Public-origin validation and strict authorisation are unchanged.

## Validation

- [x] Focused API config + authorisation tests
- [x] API typecheck and build
- [x] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

API-002 separately migrates grant envelope crypto; do not change database schema.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Complete — Attempt 1 explicitly completed by the developer after the passing self-review.

### Files Changed

`package.json`; `package-lock.json`; `src/woocommerce/rest-read/README.md`; `src/woocommerce/rest-read/authorization.postgres.test.ts`; `src/woocommerce/rest-read/authorization.test.ts`; new `src/woocommerce/rest-read/config.test.ts`; `src/woocommerce/rest-read/config.ts`; `src/woocommerce/rest-read/provider-connection.postgres.test.ts`; `src/woocommerce/rest-read/provider-connection.test.ts`; `start-dev.sh`.

### Work Completed

Migrated Woo REST-read configuration to Shared `parseCredentialKeyring` and `resolveActiveCredentialKey`, using only `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID`; the API does not consume `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. Removed old Woo-specific keyring variables from runtime, startup examples and operator documentation, changed key encoding to canonical padded standard Base64, and removed generated startup key defaults. Preserved `MODA_WOO_REST_READ_PUBLIC_ORIGIN`, its SSRF/origin restrictions, and disabled-versus-incomplete configuration behavior. Added Shared keyring validation, legacy-only and malformed-config negative cases, and command-HMAC non-requirement coverage. A temporary validated raw-key adapter remains for the existing local grant cipher and return-locale proof; API-002 owns migrating those consumers. Implementation commit `13544f6269a0f92c4f6031ae4ca17ab4bb405a13` is pushed to `task/ARCH-039-API-001`.

### Validation Results

Passed: focused config/authorization/provider unit tests (18/18); `npm run typecheck`; `npm run build`; changed-TypeScript ESLint; `git diff --check`. The PostgreSQL authorization/provider fixtures were not run because `WOO_INSTALLATION_TEST_DATABASE_URL` is not configured; the unrelated `DATABASE_URL` was not used.

### Deviations

PostgreSQL-backed fixtures remain unexecuted without their dedicated disposable test database. The temporary raw-key adapter is intentionally bounded to the existing grant cipher and return-locale proof and is assigned to follow-on API-002.

### Assumptions

Shared 2.4.1 provides the canonical keyring and active-key helpers. API-002 will replace the still-local grant cipher and remove the temporary raw-key adapter.

### Unresolved Issues

No outstanding issue within API-001 scope. API-002 remains responsible for grant-envelope cryptography migration.

### Architectural Concerns

The API remains a keyring/active-key writer and does not read or receive the command-HMAC secret. The compatibility adapter is limited to existing API-owned consumers and does not introduce another environment variable or keyring parser. No task branch was merged into `main`.

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

Attempt 1. The implementation branch is `task/ARCH-039-API-001`, clean after commit `13544f6269a0f92c4f6031ae4ca17ab4bb405a13`, and published to `origin/task/ARCH-039-API-001`. The parent task branch remains `task/ARCH-039-API-001`; only this task record is being updated.

### Review Result

The implementation satisfies the API-001 scope and acceptance criteria. Runtime and operator documentation no longer use the legacy Woo keyring variables; they remain only in negative tests proving they cannot enable the feature. Shared validates the canonical keyring and active selector, the command-HMAC secret is not consumed, and public-origin checks are preserved. Focused tests, typecheck, build, changed-file lint, and whitespace checks passed. PostgreSQL-backed fixtures were unavailable because the dedicated test database variable is unset.

### Decision

Passing self-review is recorded. Because `completion_mode` is `developer`, this task transitions to `review` and explicit developer completion remains pending. No branch was merged into `main`.

## Developer Completion Decision

- Date: 2026-10-14.
- Decision: the developer explicitly invoked `/moda_developer_update ARCH-039-API-001 complete` and accepts Attempt 1 following the passing developer self-review above.
- Lifecycle: `status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`.
- Implementation publication: commit `13544f6269a0f92c4f6031ae4ca17ab4bb405a13` is pushed to `origin/task/ARCH-039-API-001`.
- Parent publication: this completion decision is committed and pushed on `task/ARCH-039-API-001`; the API-002 eligibility promotion is committed and pushed on its canonical `task/ARCH-039-API-002` parent branch.
- Dependency frontier: `ARCH-039-API-002` is promoted from `pending` to `ready` at Attempt 0 because both declared dependencies, `ARCH-039-SHARED-004` and `ARCH-039-API-001`, are complete. `ARCH-039-SYSTEM-TEST-001` remains `pending` because its other implementation dependencies remain incomplete and its manual gate remains in force.
- Integration: no task branch was merged to `main`.
