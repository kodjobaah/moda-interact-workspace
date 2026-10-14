---
id: ARCH-039-ADMIN-001
architecture_id: ARCH-039
title: Migrate Admin OpenRouter and translation credential writers to Shared
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
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


# Migrate Admin OpenRouter and translation credential writers to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_admin` / `moda-interact-admin`

## Objective

Migrate Admin OpenRouter and translation credential writers to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace `src/lib/admin/openrouter-credential-keyring.ts` independent parser and AES sealing in OpenRouter/translation helpers with published Shared exports.
- Preserve Admin authorisation, audit, edit-version and Secret-specific validation/errors.

## Out of Scope

Embedding credentials are handled by ADMIN-002.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- This Admin credential-writer task may read **only** `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` from the closed set; it **must not** read or receive `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. Both inputs must be validated through published Shared helpers before an enabled credential write.

- Read canonical `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` in server-only Admin adapter; malformed settings fail closed.
- Use the published Node-only `encryptCredential({ keyring, activeKeyId, plaintext, aad }): CredentialEnvelope` for every in-scope credential write. `plaintext` is the existing validated credential **string**; use the canonical active selector and the existing Shared OpenRouter/translation AAD builders unchanged. Map the returned envelope to existing persisted columns in Admin-owned code.
- If an in-scope Admin read path needs plaintext, build the stored `CredentialEnvelope` and use `decryptCredential({ keyring, envelope, aad }): string`; decryption selects the stored envelope key ID, not the active selector.
- No copied AES code, local key parser or secrets in response/logs.

## Work Items

- [ ] Migrate imports/adapters and remove duplicated crypto/parsing logic.
- [ ] Update OpenRouter/translation tests for malformed configuration and envelope tamper cases.
- [ ] Prove already accepted Admin business validation and permissions are unchanged.

## Interfaces / Contracts

- Import `encryptCredential` (and `decryptCredential` only for existing read paths), `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`, plus existing Shared `createCommerceOpenRouterCredentialAad` and `createCommerceTranslationProviderCredentialAad`. Do not use obsolete `sealCredential` / `openCredential` / `openCredentialText` helpers or create a second generic crypto wrapper.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Admin credential paths consume only canonical `COMMERCE_CONNECTION_KEYS_JSON` / `COMMERCE_CONNECTION_ACTIVE_KEY_ID`, never the command HMAC or legacy/alternate encryption names; missing or legacy-only settings fail closed.

- [ ] OpenRouter/translation credential writers call the published `encryptCredential` with string plaintext and domain-exact AAD; any existing reader calls `decryptCredential`.
- [ ] Invalid configuration rejects writes; audit/authorisation remain correct.
- [ ] No local competing generic crypto/parsing implementation.

## Validation

- [ ] Focused Admin OpenRouter and translation credential tests
- [ ] Admin typecheck and build (where provided)
- [ ] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Map common Shared exceptions to established domain-safe Admin error messages.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Changes Requested (Attempt 1)

### Files Changed

- `moda-interact-admin/package.json`
- `moda-interact-admin/package-lock.json`
- `moda-interact-admin/src/lib/admin/openrouter-credential-crypto.ts`
- `moda-interact-admin/src/lib/admin/openrouter-credential.ts`
- `moda-interact-admin/src/lib/admin/shared-credential-keyring.ts`
- `moda-interact-admin/src/lib/admin/translation-credential-crypto.ts`
- `moda-interact-admin/src/lib/admin/translation-provider-credential-service.ts`
- `moda-interact-admin/tests/security/admin-translation-configuration.test.mjs`
- `moda-interact-admin/tests/unit/openrouter-credential-crypto.test.ts`
- `moda-interact-admin/tests/unit/shared-credential-keyring.test.ts`
- `moda-interact-admin/tests/unit/translation-credential-crypto.test.ts`
- `moda-interact-admin/database` (submodule gitlink)

### Work Completed

- OpenRouter and translation credential writers now use Shared `encryptCredential` and their existing domain AAD builders; Admin parses the canonical Shared keyring and active key ID.
- Credential crypto tests cover Shared interoperability, AAD tampering, and malformed keyring configuration. Existing service-level permission, CAS, and audit behavior was exercised.
- Implementation commit `1f042b6feabfdc7668b51600012d0af4e2a0f986` is published on `task/ARCH-039-ADMIN-001`.

### Validation Results

- Focused credential and translation security tests: 18 passed, 0 failed.
- OpenRouter service/security and translation validation tests: 18 passed, 0 failed.
- `npm run build`: passed, including Prisma generation and Next.js TypeScript checks; Next emitted existing BullMQ warnings for a dynamic dependency and missing optional `@valkey/valkey-glide`.
- Changed Admin source-file ESLint: 0 errors; configured ESLint ignores the changed test files.
- `git diff --check`: passed for implementation and parent task branches.
- Implementation worktree is clean, on the canonical task branch, and synchronized with `origin/task/ARCH-039-ADMIN-001`; recursive database submodule is initialized.

### Deviations

- The implementation commit advances the `database` submodule gitlink from `40674aea91527d5645aa922c9627af673b487223` to `12c3bee13cabeb3c8b9cb0ac602d836700702413`. No ADMIN-001 requirement or rationale for this database change was found.

### Assumptions

None beyond the parent architecture.

### Unresolved Issues

- Remove the unrelated `database` gitlink change from the Admin task branch, or provide an explicit approved scope amendment and evidence that this database revision is required for ADMIN-001. Re-run the Admin build after removing the gitlink change.

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

## Developer Self-Review - Changes Requested

Attempt 1 implementation behavior and focused validation pass. The review is not accepted because the published implementation commit includes an unexplained database submodule update outside the bounded Admin credential migration. Remove the gitlink delta (`40674aea91527d5645aa922c9627af673b487223` to `12c3bee13cabeb3c8b9cb0ac602d836700702413`) from `task/ARCH-039-ADMIN-001`, or record an explicit approved scope amendment with evidence that ADMIN-001 requires it; then rerun `npm run build` and resubmit this attempt for review. No attempt increment is made here.
