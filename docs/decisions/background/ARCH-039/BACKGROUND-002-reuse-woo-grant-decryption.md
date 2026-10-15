---
id: ARCH-039-BACKGROUND-002
architecture_id: ARCH-039
title: Migrate Background Woo REST-read grant decryption to Shared
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
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
  - ARCH-039-BACKGROUND-001
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-15
---


# Migrate Background Woo REST-read grant decryption to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_background` / `moda-interact-background`

## Objective

Migrate Background Woo REST-read grant decryption to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Update `src/services/woo-coupon-grant.service.ts` to use Shared keyring, AAD and authenticated opening of API-created Woo read grants.
- Keep per-call pre/post installation eligibility and grant version verification.

## Out of Scope

Unrelated Woo billing, coupon provider semantics and API authorisation are out of scope.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- This Background credential-reader task may read **only** `COMMERCE_CONNECTION_KEYS_JSON` from the closed set; it **must not** consume the active-key selector or the command-HMAC key. Decryption chooses the persisted envelope key ID.

- Consume `COMMERCE_CONNECTION_KEYS_JSON` only, without separate Woo keyring or active key selector.
- Reconstruct `CredentialEnvelope` from existing Woo grant fields; call `decryptCredential({ keyring, envelope, aad }): string` with published `createWooRestReadGrantAad`, then `JSON.parse` and validate the Woo key/secret array in Background domain code. Never attempt binary decryption or use an active key selector for reads.
- Do not weaken tenant, installation, revocation, rotation, credential-version, site URL or read-scope validation.

## Work Items

- [ ] Replace inline Woo AAD and generic crypto calls with published Shared functions; delete the now-unreferenced Background generic AES helper.
- [ ] Update Woo coupon grant tests to consume a fixed envelope emitted by the actual API-002 producer, and cover wrong tenant, stale version, revocation and tampering.
- [ ] Document canonical shared keyring without dual-encoding workaround.

## Interfaces / Contracts

- Published `createWooRestReadGrantAad` and `decryptCredential`/`CredentialEnvelope`/keyring from `@modainteract/moda-interact-shared/security/credentials/node`; API-002 uses `encryptCredential` with the matching JSON-string payload and AAD.

## Dependencies

- ARCH-039-SHARED-004
- ARCH-039-BACKGROUND-001

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Background credential reads require the canonical keyring only, never active-key/HMAC or a legacy alias; missing or legacy-only canonical configuration fails closed.

- [ ] A fixed envelope emitted by the actual API-002 `sealWooReadCredentials` producer decrypts through Background `decryptCredential` only for an authorised current installation and matching AAD; malformed credential JSON fails closed.
- [ ] No dual keyrings or base64url config workaround remains.
- [ ] Grant changes during paginated reads remain fenced.

## Validation

- [ ] Focused Woo grant/transport tests
- [ ] Background typecheck and build (where provided)
- [ ] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

No new encryption keys at worker startup; no database migration.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Changes Requested — Attempt 1 reviewed by the developer on 2026-10-15. The implementation branch is published and clean; corrections below are required before resubmission. Attempt remains 1; the next developer claim will increment it.

### Files Changed

- `docs/arch036-woo-coupon-sync-operations.md`
- `docs/commerce-host.md`
- `src/commerce/credential-keyring.ts`
- `src/providers/shopify-partner-billing.provider.ts` (unrelated to this task; remove from this task branch and preserve through its proper ownership path)
- `src/security/aes-gcm-credential.ts` (deleted)
- `src/services/woo-coupon-grant.service.ts`
- `tests/unit/security/aes-gcm-credential.test.ts` (deleted)
- `tests/unit/services/woo-coupon-grant.service.test.ts`

### Work Completed

- Background grant reads now parse only `COMMERCE_CONNECTION_KEYS_JSON` through Shared, decrypt with `decryptCredential`, and build AAD with `createWooRestReadGrantAad`; the old generic local AES helper was removed.
- Existing installation, tenant, scope, revocation, rotation-version and post-read fencing remains in the service.
- Canonical-keyring documentation was updated. These are recorded implementation facts, not acceptance of the current attempt.

### Validation Results

- `tests/unit/services/woo-coupon-grant.service.test.ts`: 19 passed.
- `npm run build` (Prisma generation and TypeScript compile): passed.
- Changed-file ESLint for `src/commerce/credential-keyring.ts`, `src/services/woo-coupon-grant.service.ts` and `tests/unit/services/woo-coupon-grant.service.test.ts`: passed.
- `git diff --check origin/main...HEAD`: passed.
- PostgreSQL integration was not required by the focused change and was not run.

### Deviations

- The published branch also changes `src/providers/shopify-partner-billing.provider.ts` to validate lifecycle states. This is outside BACKGROUND-002 scope and must be separated from this task branch; preserve the change through its appropriate task/owner.

### Assumptions

None beyond the parent architecture.

### Unresolved Issues

- The API-format test constructs ciphertext inside the Background test suite, and the immutable producer fixture is from ARCH-036/API-007. Neither is a fixed fixture emitted by the actual API-002 `sealWooReadCredentials` implementation. Add and consume such a fixture to establish producer-to-consumer interoperability for this cutover.
- The unrelated Shopify Partner billing change is included in the BACKGROUND-002 implementation diff and must be separated.

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

- Attempt: 1.
- Result: Not accepted for review yet. The Shared migration, reader-only keyring parsing, local AES helper removal, authorization fences and focused validation are present, but the published implementation branch contains an unrelated Shopify Partner billing change and lacks a fixed API-002-producer fixture consumed by Background.
- Required corrections:
  1. Remove `src/providers/shopify-partner-billing.provider.ts` from the BACKGROUND-002 task diff. Preserve that behavior change through its correct owner/task; do not discard or silently lose it.
  2. Add an immutable test fixture produced by the actual API-002 `sealWooReadCredentials` path with `encryptCredential` and the canonical Woo AAD, then have the Background service consume that fixture. Keep the existing wrong-tenant, malformed-payload, tampering and grant-fencing assertions.
- Validation observed on current published implementation commit `574e2c0`: focused tests 19/19, build, changed-file ESLint and `git diff --check origin/main...HEAD` passed. These checks do not clear the two contract/scope issues above.
- Worktree evidence: canonical parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-039-BACKGROUND-002`, branch `task/ARCH-039-BACKGROUND-002`, clean before this report update at `666c749`; canonical implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-039-BACKGROUND-002`, same task branch, clean and synchronized at `574e2c0`.
- Lifecycle: `completion_mode: developer`; transition to `ready`, clear executor/claim, retain Attempt 1. Do not increment here. No branch was merged to `main`.
