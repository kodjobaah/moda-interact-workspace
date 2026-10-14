---
id: ARCH-039-BACKGROUND-001
architecture_id: ARCH-039
title: Migrate Background runtime credential readers to Shared
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
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-15
---


# Migrate Background runtime credential readers to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_background` / `moda-interact-background`

## Objective

Migrate Background runtime credential readers to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace `src/commerce/credential-keyring.ts` parser and generic `src/security/aes-gcm-credential.ts` crypto usage for in-scope OpenRouter and translation/embedding provider credential consumers.
- Retain existing worker domain error taxonomy and model/provider retry behaviour.

## Out of Scope

Woo grant read is BACKGROUND-002; do not modify API sources.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- This Background credential-reader task may read **only** `COMMERCE_CONNECTION_KEYS_JSON` from the closed set; it **must not** consume the active-key selector or the command-HMAC key. Decryption chooses the persisted envelope key ID.

- Reader-only Background services consume canonical `COMMERCE_CONNECTION_KEYS_JSON`, never active-key selector or HMAC.
- Reconstruct `CredentialEnvelope` from existing provider-credential columns and call only published `decryptCredential({ keyring, envelope, aad }): string`, with existing Shared model AAD; do not require an active selector for reads. Malformed/missing keyring, invalid UTF-8 and authentication failures are unavailable, never plaintext/config fallback.
- No change to queue admission, billing, provider calls, stored versions or provider outcome behaviour.

## Work Items

- [x] Migrate parser and production credential readers to Shared.
- [x] Run focused Background credential tests including malformed env and tamper/missing key ID.
- [x] Leave Woo-specific grant mapping for BACKGROUND-002; the local generic AES helper remains only for the separately scoped Woo migration.

## Interfaces / Contracts

- `decryptCredential`, `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`; existing Shared OpenRouter/translation AAD builders. No local crypto/open implementation or binary-plaintext helper.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Background credential reads require the canonical keyring only, never active-key/HMAC or a legacy alias; missing or legacy-only canonical configuration fails closed.

- [x] Background credential readers call published `decryptCredential` and receive validated UTF-8 string plaintext; no local parser, decryptor or alternative old Shared function remains for the in-scope readers.
- [x] Read-only worker paths do not depend on active selector.
- [x] Worker business/queue behaviour unchanged by the migration.

## Validation

- [x] Focused Background credential/runtime tests
- [x] Background typecheck and build (where provided)
- [ ] Changed-file lint and `git diff --check` (diff check passed; lint unavailable because this package defines no lint script and has no installed/configured linter)

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Any local adapter remaining must be only a service-specific error mapping. Retain the local generic AES helper temporarily where Woo still imports it; delete it in BACKGROUND-002 after Woo migration.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Changes Requested (Attempt 1)

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/src/commerce/credential-keyring.ts`
- `moda-interact-background/src/commerce/openrouter-credential.ts`
- `moda-interact-background/src/commerce/provider-credential-validation.ts`
- `moda-interact-background/src/commerce/translation-provider-credential.ts`
- `moda-interact-background/src/services/merchant-knowledge-embedding-runtime.ts`
- `moda-interact-background/tests/unit/commerce/credential-keyring.test.ts`
- `moda-interact-background/tests/unit/commerce/openrouter-credential.test.ts`
- `moda-interact-background/tests/unit/commerce/translation-provider-credential.test.ts`
- `moda-interact-background/tests/unit/services/merchant-knowledge-embedding.test.ts`
- `moda-interact-background/src/providers/shopify-partner-billing.provider.ts` (latest task-branch commit)
- `moda-interact-background/src/services/woo-coupon-grant.service.ts` (latest task-branch commit)
- `moda-interact-background/src/services/woo-coupon-legacy-keyring.ts` (latest task-branch commit)
- `moda-interact-background/tests/unit/services/woo-coupon-grant.service.test.ts` (latest task-branch commit)

### Work Completed

- Background keyring parsing now delegates to Shared and reads only `COMMERCE_CONNECTION_KEYS_JSON`.
- OpenRouter, translation-provider, and Merchant Knowledge embedding readers reconstruct Shared `CredentialEnvelope` values and call `decryptCredential` with their domain-specific Shared AAD builders. Provider-domain validation and existing bounded error mappings are retained.
- Implementation commit `d2953b8f67c507b316357a2358c50ceb313e774b` is published on `task/ARCH-039-BACKGROUND-001`.

### Validation Results

- Focused keyring/OpenRouter/translation/embedding tests: 53 passed, 0 failed.
- `npm run build`: passed; Prisma Client generation and `tsc` completed successfully.
- Changed-file lint: passed with ESLint 10.12.0 and the task worktree's `eslint.config.ts` for the nine TypeScript files changed by the credential migration.
- `git diff --check`: passed for implementation and parent task branches.
- Implementation worktree is currently clean and synchronized with `origin/task/ARCH-039-BACKGROUND-001`; the previously reported untracked `.package.json.swp` is absent. The Background database submodule is initialized at `40674aea91527d5645aa922c9627af673b487223`.
- Current implementation branch tip `390a8a1944ebd56a4b5326a493bd58a755311830` also contains subsequent Woo grant/keyring changes and a Shopify billing-provider edit outside this task's scope; review is held for branch-scope correction.

### Deviations

None

### Assumptions

None beyond the parent architecture.

### Unresolved Issues

- Remove the Woo grant service, Woo legacy-keyring adapter, Woo grant test changes, and unrelated Shopify billing-provider edit from the BACKGROUND-001 task branch in a corrective commit; coordinate/rehome the Woo work under BACKGROUND-002 without rewriting published history.
- Restore the removed 128-character key-ID test in `tests/unit/commerce/credential-keyring.test.ts`, or document and verify equivalent coverage elsewhere.
- Re-run focused credential tests, build, changed-file lint, and `git diff --check` after correcting the branch scope. The prior untracked `.package.json.swp` issue is resolved.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Not yet reviewed.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending review.

### Follow-up

None

## Developer Self-Review - Changes Requested (Initial)

Attempt 1's implementation, focused tests and build pass. Review is held because required changed-file lint could not be run: `moda-interact-background` has no lint script and no installed/configured linter. In addition, final inspection found an untracked `.package.json.swp` in the implementation worktree. It was not opened, staged, or modified because it may be a user/editor artifact. Resolve that artifact and confirm the worktree is clean; then run changed-file lint with an approved tool or explicitly amend the validation requirement to accept the repository's lack of lint tooling, and resubmit Attempt 1. The implementation source commit is published; do not increment the attempt for this review decision.

## Developer Self-Review - Changes Requested (Reconciliation)

Attempt 1's focused credential tests (53 passed), build, changed-file lint (ESLint 10.12.0), and `git diff --check` pass. The previously reported `.package.json.swp` is absent and the implementation worktree is clean. Review remains Changes Requested because the current published BACKGROUND-001 branch tip `390a8a1944ebd56a4b5326a493bd58a755311830` includes Woo grant/keyring implementation and tests assigned to BACKGROUND-002, an unrelated Shopify billing-provider edit, and removal of the 128-character key-ID test. Remove/rehome the out-of-scope changes in a corrective commit without rewriting published history, restore or account for the removed test coverage, then rerun focused tests, build, lint, and diff check. Attempt remains 1; `status: ready`, `executor: null`, and `claimed_at: null` for correction and resubmission.
