---
id: ARCH-039-SHARED-003
architecture_id: ARCH-039
title: Define exact embedding and Woo credential AAD contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-039-SHARED-001
enables:
  - ARCH-039-SHARED-004
created: 2026-10-14
updated: 2026-10-14
---

# Define exact embedding and Woo credential AAD contracts

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_shared` / `moda-interact-shared`

## Objective

Create two deterministic, cross-service authenticated-data builders so credential writers and readers bind the same identities byte-for-byte.

## Context

ARCH-039 standardises hosted credential security before consumer refactoring. The developer will clear non-production credential and command-audit state: this is a breaking pre-production cutover without historical compatibility. Interfaces established here are the binding contracts for downstream Shared and service tasks.

## Scope

- Add `src/security/credentials/aad.ts` (or a narrow Shared commerce module re-exported through Node credentials entrypoint) with exactly two new public builders and input types.
- Reuse Shared `canonicalJson` and the existing `CommerceEnvironmentSchema`; add cross-service golden-byte tests.

## Out of Scope

- AES/keyring/HMAC implementation, consumer storage, domain token rules, DB queries, installations/grant status checks and user-request retries.
- Do not reimplement or change `createCommerceOpenRouterCredentialAad` or `createCommerceTranslationProviderCredentialAad` from `src/commerce/model/index.ts`.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- Shared is a **pure Node library** for ARCH-039 secrets: never read `process.env`, introduce or document another credential-security environment name, infer an environment variable by convention, or generate replacement keys. Callers inject parsed values sourced exclusively from the canonical `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and (for Commerce commands only) `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` via their authorised server adapters. Publication must not introduce alternate configuration.

**Exact function contracts:**

```ts
export function createCommerceEmbeddingCredentialAad(input: {
  environment: 'LOCAL' | 'TEST' | 'DEVELOPMENT' | 'STAGING' | 'PRODUCTION';
  purpose: 'MERCHANT_KNOWLEDGE' | 'REFERENCE_TAXONOMY';
  provider: string;
  keyId: string;
}): string;
export function createWooRestReadGrantAad(input: {
  shopId: string;
  installationId: string;
  authorizationAttemptId: string;
  credentialVersionSnapshot: number;
}): string;
```

**Embedding AAD — preserve the existing Admin/Commerce/MCP `canonicalJson` object semantics:**

```ts
canonicalJson({
  credentialType: 'EMBEDDING', environment, purpose, provider, keyId,
})
```

`canonicalJson` must be imported from existing Shared source; do not use unordered `JSON.stringify` for embedding. Valid environment/purpose enum values above, nonempty provider (<=128 characters; reject CR/LF/NUL) and canonical key ID (1–64 `[A-Za-z0-9_-]`). No trimming or lowercasing, because both sides must derive identical bytes from persisted values.

**Woo REST read AAD — preserve the API/Background array serialization semantics:**

```ts
JSON.stringify([
  'moda-woo-rest-read-v1', shopId, installationId,
  authorizationAttemptId, credentialVersionSnapshot,
])
```

Inputs must be nonempty bounded identifiers (1–128 characters, no CR/LF/NUL) and positive safe integer `credentialVersionSnapshot`. Avoid normalisation, extra tags/fields or `canonicalJson` for the Woo array. AAD builder accepts **trusted, validated IDs** but does not decide access to an installation or grant.

Functions return a UTF-8-compatible JS string, to be passed unchanged into SHARED-002 `aad`. Wrong environment, provider, purpose, shop, installation, attempt or version must produce different AAD (and therefore GCM authentication failure). No secret values should appear in AAD.

## Work Items

- [x] Implement the two validated, deterministic builders in the Shared Node credentials subpath.
- [x] Create fixed golden outputs for two embedding contexts and two Woo grants; compare exact UTF-8 bytes with the current source algorithms.
- [x] Test changed identity/version, invalid enum, malformed field, non-positive version and safe, non-sensitive errors.
- [x] Confirm the existing Shared OpenRouter and translation AAD APIs/bytes are unchanged.
- [x] Build/typecheck Node subpath with both exports.

## Interfaces / Contracts

Exports from `@modainteract/moda-interact-shared/security/credentials/node`:
`createCommerceEmbeddingCredentialAad`, `createWooRestReadGrantAad` and their input types.

Callers: embedding Admin (writer), Commerce (reader), MCP (reader); Woo API (writer) and Background (reader). Existing OpenRouter/translation callers continue importing from `@modainteract/moda-interact-shared/commerce/model`.

## Dependencies

- ARCH-039-SHARED-001

## Enables

- ARCH-039-SHARED-004

## Acceptance Criteria

- [x] Shared code, published exports, fixtures and documentation introduce no service-local secret environment name, environment reads or fallback configuration for ARCH-039 credential security.

- [x] Embedding golden-vector UTF-8 bytes exactly match canonical JSON currently produced by Admin, Commerce and MCP.
- [x] Woo golden-vector UTF-8 bytes exactly match current API and Background JSON array encoding.
- [x] Every identity field and Woo version affects AAD and fails validation if invalid; no opaque tenant-agnostic AAD permitted.
- [x] Existing OpenRouter and translation exports are unchanged, with regression tests passing.
- [x] Types/build support imports through the agreed Node entrypoint.

## Validation

- [x] `npx tsx --test src/security/credentials/aad.test.ts` (9 passed, 0 failed)
- [x] `npx tsx --test src/commerce/model/model-contracts.test.ts` (7 passed, 0 failed)
- [x] `npm run typecheck` and `npm run build` (both passed)
- [x] `git diff --check` (passed)

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. Developer completion requires an explicit developer decision after accepted review. Do not begin dependent tasks.

## Implementation Notes

Keep byte-level format tests independent of the SHARED-002 seal/open implementation; a broken common AAD builder must not be able to prove itself correct using its own output on both sides. The no-migration decision does not remove the requirement for deterministic AAD.

Use the canonical dedicated parent/implementation task-worktree launcher and preserve initial synchronization evidence. Do not create/update `docs/decisions/**/_index.md` until the architecture session is explicitly confirmed complete. No implementation edits outside `moda-interact-shared`.

## Completion Report

### Status

Implemented; developer self-review passed, explicit developer completion pending.

### Files Changed

- `src/security/credentials/aad.ts`
- `src/security/credentials/aad.test.ts`
- `src/security/credentials/node.ts`

### Work Completed

Added validated deterministic embedding and Woo REST grant AAD builders. Embedding uses Shared `canonicalJson` with the established object fields; Woo grants preserve the existing five-element JSON-array serialization. Added golden-byte, identity binding, validation, safe-error and non-normalisation tests, and exported both builders and their input types through the Node-only credentials entrypoint.

### Validation Results

- `npx tsx --test src/security/credentials/aad.test.ts`: 9 passed, 0 failed.
- `npx tsx --test src/commerce/model/model-contracts.test.ts`: 7 passed, 0 failed.
- `npm run typecheck`: passed.
- `npm run build`: passed; generated the Node credentials subpath JavaScript and declarations.
- Built package self-reference ESM import of both AAD builders: passed; generated declarations expose both functions and input types through the Node subpath.
- Compared the embedding format with Admin's current `canonicalJson` AAD builder and Woo format with API/Background's current five-element JSON-array serializers; formats match byte-for-byte.
- New credential AAD source, tests and exports contain no `process.env` access or service-local credential environment names; the root/browser entrypoint does not export these builders.
- `git diff --check`: passed.
- Implementation branch `task/ARCH-039-SHARED-003` is clean and pushed at `bd25fa551a8ae88020dc66d21c8f6754458107d2`, based on Shared `origin/main` `1a6ee8c18391524b8efd073eb4be11a4d7a8e010`; recursive submodule status is clean (no submodules).

### Deviations

None.

### Assumptions

None beyond parent architecture.

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

## Developer Self-Review - Passed/Accepted

Attempt 1 satisfies the task scope and acceptance criteria. Both required test suites, typecheck, build, built Node-subpath import/declaration inspection and whitespace validation passed. The embedding and Woo AAD bytes match their existing cross-service serializers. The implementation is committed and pushed on the canonical Shared task branch; this review record is on the canonical parent task branch. No required work item or acceptance criterion remains incomplete. Because `completion_mode: developer`, the task remains in `review` pending the explicit developer completion decision.
