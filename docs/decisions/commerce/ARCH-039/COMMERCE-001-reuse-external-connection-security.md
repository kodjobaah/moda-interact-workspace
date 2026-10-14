---
id: ARCH-039-COMMERCE-001
architecture_id: ARCH-039
title: Migrate Commerce external-connection credentials and command key to Shared
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
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
  - ARCH-039-COMMERCE-002
  - ARCH-039-GATEWAY-001
created: 2026-10-14
updated: 2026-10-15
---


# Migrate Commerce external-connection credentials and command key to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_commerce` / `moda-interact-commerce`

## Objective

Migrate Commerce external-connection credentials and command key to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace `lib/server/credential-keyring.ts` duplicate parser and `src/commerce/connections/credentials/index.ts` local AES-GCM with published Shared keyring and AEAD.
- Import the SHARED-005 `parseCommerceConnectionCommandHmacKey(raw, aesKeyring)` decoder; pass its returned 32 bytes (not the encoded configuration text) to `createHmac` in the existing command digest implementation.

## Out of Scope

Preview/OpenRouter/embedding reader migration belongs to COMMERCE-002.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- Commerce may read `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` for credential writes; **only Commerce command-signing code** may additionally read `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`, through the published independent HMAC parser. Preview/embedding readers consume the keyring, not a command-HMAC key. No other credential-security setting name is permitted.

- For external connection writes, call published `encryptCredential({ keyring, activeKeyId, plaintext, aad })` on the validated credential **string**. For reads, map stored columns to `CredentialEnvelope` and call `decryptCredential({ keyring, envelope, aad }): string`; the stored key ID determines the decryption key, not the active selector.
- Preserve `canonicalJson` external-connection AAD, scoped revision/shop identity, super-admin permission and audit/transaction behaviour.
- Command-HMAC key must be independent from AES keyring; new byte-key digest is deterministic and tested with an independent HMAC-SHA256 golden vector after the planned non-production audit wipe. Require rejection of an HMAC key equal to any configured AES key.
- Malformed keyring/HMAC causes explicit unavailable response, not partial enablement or empty-keyring fallback.

## Work Items

- [x] Implement Shared parser/AEAD imports and typed adapters; remove duplicate crypto.
- [x] Update external-connection command idempotency and credential tests for decoded HMAC bytes, tamper, missing keys, wrong shop AAD.
- [x] Ensure `src/commerce/integration/backend.ts` respects all-or-nothing credential/HMAC config and safe errors.

## Interfaces / Contracts

- `encryptCredential`, `decryptCredential`, `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`, plus SHARED-005 `parseCommerceConnectionCommandHmacKey(raw, aesKeyring): Uint8Array`. Commerce retains external AAD construction, persisted-field mapping and command digest semantics; no service-local generic seal/open or alternate AES helper.
- The Commerce command-kernel dependency should accept HMAC **bytes**, not an encoded `string`; its canonical input serializer and replay/conflict rules remain unchanged.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-COMMERCE-002
- ARCH-039-GATEWAY-001

## Acceptance Criteria

- [x] Commerce uses only the three named canonical credential-security variables according to function; no service-local alternate, legacy alias, or fallback can enable credential or command signing.
- [x] Commerce external-connection writers/readers use published `encryptCredential` / `decryptCredential` and canonical keyring with unchanged domain AAD and database mapping.
- [x] HMAC key is decoded independently and deterministic replay checks work under new key.
- [x] Service does not silently substitute empty keyring on invalid config.

## Validation

- [x] Focused Commerce external credential/command kernel tests
- [x] Commerce typecheck and build
- [x] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Keep payment-independent connection operations and existing admin audit transaction boundaries untouched.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Review — Attempt 1 passed developer review; explicit developer completion is pending.

### Files Changed

- `moda-interact-commerce/package.json`
- `moda-interact-commerce/package-lock.json`
- `moda-interact-commerce/src/commerce/connections/command-kernel.ts`
- `moda-interact-commerce/src/commerce/connections/credentials/index.ts`
- `moda-interact-commerce/src/commerce/connections/lifecycle/index.ts`
- `moda-interact-commerce/src/commerce/connections/security-config.ts`
- `moda-interact-commerce/src/commerce/integration/backend.ts`
- `moda-interact-commerce/src/commerce/integration/external/index.ts`
- `moda-interact-commerce/tests/connection-lifecycle-bearer-postgres.test.ts`
- `moda-interact-commerce/tests/connection-lifecycle.test.ts`
- `moda-interact-commerce/tests/connection-security-config.test.ts`
- `moda-interact-commerce/tests/external-availability.test.ts`
- `moda-interact-commerce/tests/external-credentials-postgres.test.ts`
- `moda-interact-commerce/tests/external-credentials.test.ts`
- `moda-interact-commerce/tests/external-tool-authoring-validation.test.ts`
- `moda-interact-commerce/tests/external-wiring.test.ts`
- `moda-interact-commerce/tests/local-external-mcp-diagnostic.test.ts`
- `moda-interact-commerce/tests/preview-runner-diagnostic-log-fields.test.ts`

### Work Completed

- Replaced the external connection credential path's local AES-GCM implementation with Shared `encryptCredential` and `decryptCredential`, preserving canonical JSON AAD and persisted envelope fields.
- Added canonical all-or-nothing keyring, active-key, and independent command-HMAC configuration; malformed or partial configuration leaves external integration unavailable.
- Passed decoded HMAC bytes into the command kernel, preserving canonical command digest and replay behavior; added fixed HMAC-SHA256 golden-vector coverage and rejection of AES/HMAC key reuse.
- Preserved existing authorization, audit, and transaction behavior. Implementation commit `a7b41ff131108b657a840e1587ab324774440b2b` is published on `task/ARCH-039-COMMERCE-001`.

### Validation Results

- Focused Commerce security, credential, lifecycle/idempotency, availability, and wiring suite: 39 tests passed across 5 files.
- `npm run typecheck`: passed.
- `npm run build`: passed; Next.js emitted existing Nunjucks dynamic-dependency warnings.
- Changed-file ESLint: passed.
- `git diff --check origin/main...HEAD`: passed; implementation worktree clean and implementation task branch synchronized with its remote.
- PostgreSQL-backed tests were not run; the task's focused behavior suite ran without a database dependency.

### Deviations

None.

### Assumptions

None beyond the parent architecture.

### Unresolved Issues

None. Explicit developer completion remains pending because `completion_mode: developer`.

### Architectural Concerns

None.

## Architect Review

### Review Status

Developer review passed; awaiting explicit developer completion.

### Review Notes

Attempt 1 conforms to the task scope. Shared AEAD is used for external credential writes/reads with preserved credential columns and shop/revision AAD. Command-HMAC configuration is decoded independently, key reuse is rejected, and a fixed HMAC-SHA256 vector verifies the byte-key digest. Backend config fails closed when canonical settings are missing or invalid. No known required work item or acceptance criterion remains incomplete.

### Reviewed Files

All implementation and test files listed in the Completion Report.

### Validation Reviewed

39 focused tests passed; Commerce typecheck, production build, changed-file ESLint, and `git diff --check` passed.

### Architecture Conformance

Passed for COMMERCE-001 scope.

### Follow-up

Developer may explicitly complete with `/moda_developer_update ARCH-039-COMMERCE-001 complete`.

## Developer Self-Review - Passed (Attempt 1)

The implementation branch is committed and pushed at `a7b41ff131108b657a840e1587ab324774440b2b`; the parent report update is task-owned and will be published separately. Focused tests, typecheck, build, lint, and diff-check all pass. No required work item remains incomplete. Since `completion_mode` is `developer`, the task is set to `review` and awaits explicit developer completion; no task branch was merged to `main`.
