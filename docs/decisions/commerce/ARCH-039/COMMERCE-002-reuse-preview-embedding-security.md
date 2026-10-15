---
id: ARCH-039-COMMERCE-002
architecture_id: ARCH-039
title: Migrate Commerce Preview and embedding credential readers to Shared
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
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
  - ARCH-039-COMMERCE-001
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-15
---


# Migrate Commerce Preview and embedding credential readers to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_commerce` / `moda-interact-commerce`

## Objective

Migrate Commerce Preview and embedding credential readers to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace Preview OpenRouter and Merchant Knowledge embedding AES-GCM implementations with published `decryptCredential` and the appropriate Shared AAD builders. Map existing stored fields to `CredentialEnvelope` at each service boundary.
- Fix `lib/preview/runtime.ts` malformed keyring handling so optional Preview disablement cannot mask invalid enabled configuration.

## Out of Scope

No Studio UX redesign or external connection command changes.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- Commerce may read `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` for credential writes; **only Commerce command-signing code** may additionally read `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`, through the published independent HMAC parser. Preview/embedding readers consume the keyring, not a command-HMAC key. No other credential-security setting name is permitted.

- Consume the canonical keyring from the Commerce server adapter established by COMMERCE-001. Both credential readers call `decryptCredential({ keyring, envelope, aad }): string`, which selects the envelope key ID (not the active key). Preserve existing domain validation of returned provider credential text.
- Wrong environment/provider/purpose/key ID/authentication and corrupted envelope fail closed.
- Preserve preview abort semantics, retriable versus non-retriable outcomes, logging redaction and embedding provider/model validation.

## Work Items

- [x] Migrate Preview resolver and Merchant Knowledge embedding runtime to published Shared APIs.
- [x] Remove duplicate local AAD/envelope/plaintext validation and unsafe empty-config fallback.
- [ ] Add producer-to-consumer vectors that create envelopes with Shared `encryptCredential` and decrypt them through both Commerce readers; current fixtures construct ciphertext directly with Node `createCipheriv`.

## Interfaces / Contracts

- `decryptCredential`, `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`, with existing Shared OpenRouter AAD and published `createCommerceEmbeddingCredentialAad`. No alternate `openCredential` or local AES implementation.

## Dependencies

- ARCH-039-SHARED-004
- ARCH-039-COMMERCE-001

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Commerce uses only the three named canonical credential-security variables according to function; no service-local alternate, legacy alias, or fallback can enable credential or command signing.

- [x] Preview/OpenRouter and embedding readers use the published `decryptCredential` text API with their correct Shared AAD, never a local decryptor.
- [x] Invalid configured keyring does not become a silent empty ring.
- [x] Preview/test conversation cancellation and provider selection semantics remain intact.

## Validation

- [x] Focused Commerce Preview and embedding runtime tests
- [x] Commerce typecheck and build
- [x] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Domain-specific safe error categorisation can remain as an adapter around Shared exceptions.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Changes Requested — Attempt 1 review completed; implementation and passing validation are recorded below.

### Files Changed

- `lib/preview/runtime.ts`
- `lib/server/credential-keyring.ts`
- `src/commerce/integration/preview/openrouter-credential.ts`
- `src/commerce/merchant-knowledge/embedding-runtime.ts`
- `tests/commerce-credential-keyring-runtime.test.ts`
- `tests/local-external-mcp-diagnostic.test.ts`
- `tests/merchant-knowledge-embedding-runtime.test.ts`
- `tests/preview-openrouter-postgres.test.ts`
- `tests/preview-openrouter-runtime.test.ts`

### Work Completed

- Replaced local Preview OpenRouter and Merchant Knowledge embedding decryptors with Shared `decryptCredential` and their Shared AAD builders. Credential envelopes are reconstructed at the database boundary; provider-token validation and bounded service error mappings remain local.
- Switched the server keyring adapter to Shared parsing of `COMMERCE_CONNECTION_KEYS_JSON` only and removed Preview's silent empty-keyring fallback.
- Implementation commits `ee73a6d1c8837c7cc94328bc6886345f49a41a77` and `214d0449dde8df5659828c42d358147a7c09328a` are published on `task/ARCH-039-COMMERCE-002`. Relative to current `origin/main`, the net tree delta is the nine files listed above; dependency changes already integrated by COMMERCE-001 are not part of the current net delta.

### Validation Results

- Focused Preview OpenRouter, embedding runtime, and canonical keyring tests: 14 passed across 3 files.
- Preview service, routes, and integration tests: 42 passed across 3 files, including cancellation and provider-selection behavior.
- `npm run typecheck`: passed.
- `npm run build`: passed; Next.js emitted the existing Nunjucks dynamic-dependency warnings.
- ESLint on task-changed TypeScript/JavaScript files: 0 errors, 1 warning for an unused `_onDiagnostic` binding in `tests/preview-openrouter-runtime.test.ts`.
- `git diff --check origin/main HEAD`: passed. Implementation worktree is clean and branch tip `214d0449dde8df5659828c42d358147a7c09328a` is synchronized with `origin/task/ARCH-039-COMMERCE-002`.
- Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-039-COMMERCE-002` on `task/ARCH-039-COMMERCE-002`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-039-COMMERCE-002` on the same task branch. Shared workspace and implementation checkouts were not switched; no other task worktree was reused.
- Start synchronization from the prepared execution packet: parent remote task fast-forward `not-needed`, parent `origin/main` incorporated `yes`; implementation remote task fast-forward `not-needed`, implementation `origin/main` incorporated `already-current`. Recursive submodule sync/update passed; database submodule was initialized at `d5497286f2575c8e0b2fd2453e9dbdba4fc1136a`.

### Deviations

None.

### Assumptions

None beyond the parent architecture.

### Unresolved Issues

The reader tests construct AES-GCM ciphertext directly with Node `createCipheriv`; they do not use Shared `encryptCredential` to produce envelopes for the Commerce readers. Add producer-to-consumer vectors for both Preview OpenRouter and Merchant Knowledge embedding using their canonical Shared AAD, and retain wrong-context/authentication rejection coverage. Until this explicit Work Item is complete, the task remains Changes Requested.

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

## Developer Self-Review - Changes Requested (Attempt 1)

The implementation is committed and pushed on `task/ARCH-039-COMMERCE-002`. The net implementation delta against current `origin/main` is confined to the nine Preview/keyring/embedding files listed in the Completion Report. Focused credential tests (14/14), Preview service/routes/integration tests (42/42), typecheck, production build, changed-file lint (0 errors; 1 unused-variable warning), and `git diff --check` passed. No implementation regression was found in the reviewed behavior.

Review remains Changes Requested because the explicit cross-service-vector Work Item is not met: current fixtures encrypt with direct Node crypto rather than Shared `encryptCredential`, so producer-to-consumer envelope compatibility is not exercised through the published producer API. Add vectors for both readers, rerun the focused tests and required validation, and resubmit. Attempt remains 1; task state is `ready`, with executor and claim metadata cleared. No branches were merged to `main`.
