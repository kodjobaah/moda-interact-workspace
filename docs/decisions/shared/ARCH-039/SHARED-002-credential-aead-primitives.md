---
id: ARCH-039-SHARED-002
architecture_id: ARCH-039
title: Implement bounded AES-256-GCM credential envelope primitives
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-039-SHARED-001
enables:
  - ARCH-039-SHARED-004
created: 2026-10-14
updated: 2026-10-14
---

# Implement bounded AES-256-GCM credential envelope primitives

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_shared` / `moda-interact-shared`

## Objective

Provide a single, typed AES-256-GCM implementation with two public credential operations: encrypt UTF-8 credential text and decrypt it back to text.

## Context

ARCH-039 standardises hosted credential security before consumer refactoring. The developer will clear non-production credential and command-audit state: this is a breaking pre-production cutover without historical compatibility. Interfaces established here are the binding contracts for downstream Shared and service tasks.

## Scope

- Implement `src/security/credentials/aead.ts` and expose its exports through the established `src/security/credentials/node.ts` entrypoint.
- Operate only on a SHARED-001 validated opaque keyring and explicitly supplied AAD; add focused encryption/decryption and tamper tests.

## Out of Scope

- Domain storage fields, Prisma models, provider secret constraints, Woo credential JSON parsing, AAD construction, command digest/HMAC, historical ciphertext and other repositories.
- Do not add a second crypto entrypoint or read `process.env`.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- Shared is a **pure Node library** for ARCH-039 secrets: never read `process.env`, introduce or document another credential-security environment name, infer an environment variable by convention, or generate replacement keys. Callers inject parsed values sourced exclusively from the canonical `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and (for Commerce commands only) `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` via their authorised server adapters. Publication must not introduce alternate configuration.

**Exact public API:**

```ts
export type CredentialEnvelope = Readonly<{
  keyId: string;
  nonce: Uint8Array;       // 12 bytes
  ciphertext: Uint8Array;  // 1..8192 bytes
  authTag: Uint8Array;     // 16 bytes
}>;
export function encryptCredential(input: {
  keyring: CredentialKeyring;
  activeKeyId: string;
  plaintext: string;
  aad: string | Uint8Array;
}): CredentialEnvelope;
export function decryptCredential(input: {
  keyring: CredentialKeyring;
  envelope: CredentialEnvelope;
  aad: string | Uint8Array;
}): string;
```

**Cryptographic rules:**
- AES-256-GCM only, via `node:crypto`; 32-byte key selected from SHARED-001 private keyring by output `keyId`. `encryptCredential` verifies the active ID is configured; `decryptCredential` selects the envelope's own key ID and does not need an active selector (supports decryption of an older configured ID after changing active ID).
- A cryptographically random 12-byte nonce is generated for **every** encryption. Authentication tag exactly 16 bytes. Never accept caller-specified nonce/tag, deterministic nonce, arbitrary IV size or plaintext fallback.
- AAD is **required** and supplied unchanged by the caller; accept UTF-8 string or `Uint8Array`, copy/convert into bytes and reject zero length or >4096 bytes. Do not reconstruct/guess domain AAD in AEAD module.
- Plaintext must be a `string` containing valid Unicode (reject unpaired UTF-16 surrogates to prevent lossy replacement). Encode its UTF-8 bytes and require 1–8192 bytes (byte length, not character count) before allocating ciphertext. Do not accept a binary plaintext input. No implicit JSON parsing, trimming, CR/LF rules or provider token checks: these are domain-owned.
- Validate the envelope **internally** on every `decryptCredential` call: enforce proper property types, allowed key ID, nonce/tag lengths and ciphertext length; reject malformed envelopes (including array/null and invalid typed-array values). Do not export `isValidCredentialEnvelope` or introduce a separate public validation API. An envelope does **not** require a Prisma edit/rotation version: versions remain domain state, not crypto envelopes.
- `decryptCredential()` returns a `string` only after authenticated decryption and strict (`fatal: true`) UTF-8 decoding. Reject invalid UTF-8 plaintext rather than silently replacing bytes. No public raw-byte decrypt function or text wrapper is required. Never return/cache plaintext on any failure.
- Never mutate caller-owned nonce/ciphertext/tag buffers or the caller's keyring. Authenticated bytes must bind ciphertext, AAD and tag; no decryption results after any tampering.

**Errors:** unknown key => `KEY_UNAVAILABLE`; tampering, invalid nonce/tag/ciphertext, absent AAD, empty/oversized data or invalid UTF-8 => `INVALID_CREDENTIAL`. Return the same generic `INVALID_CREDENTIAL` for wrong AAD and failed GCM tag; never expose raw `node:crypto` errors, sensitive `cause`, plaintext or ciphertext in messages. Domain adapters map these errors to their existing safe responses.

## Work Items

- [ ] Implement internal `CredentialEnvelope` validation and the two public AES-256-GCM text encrypt/decrypt functions using SHARED-001 keyring internals.
- [ ] Encode plaintext strings as UTF-8 bytes; strictly decode authenticated plaintext using a fatal UTF-8 decoder within the single `decryptCredential` implementation.
- [ ] Test round-trip of ASCII and Unicode credential strings (including multibyte byte-length boundaries); reject unpaired surrogates and binary plaintext inputs; verify nonce/tag/ciphertext boundaries and input-buffer nonmutation.
- [ ] Test wrong key ID, incorrect AAD, altered key/nonce/tag/ciphertext, unsupported inputs, invalid envelope shape and missing active ID; craft authenticated non-UTF8 plaintext using independent `node:crypto` and confirm `decryptCredential` fails closed.
- [ ] Add interoperability test using independent `node:crypto` AES-GCM reference vectors for both directions, not only encrypt-then-decrypt using Shared on both sides.
- [ ] Confirm one Node-only package subpath compiles and imports.

## Interfaces / Contracts

Exports from `@modainteract/moda-interact-shared/security/credentials/node`:
`CredentialEnvelope`, `encryptCredential`, `decryptCredential`. Envelope validation stays an internal implementation detail and is not a public export.

Envelope/database adapter convention: Service code maps `credentialNonce`/`credentialAuthTag`/`credentialCiphertext`/`encryptionKeyId` (Woo) or `nonce`/`authTag`/`ciphertext`/`keyId` (Commerce) to this shared envelope, without changing schemas or repackaging ciphertext into a new opaque persisted format.

## Dependencies

- ARCH-039-SHARED-001

## Enables

- ARCH-039-SHARED-004

## Acceptance Criteria

- [ ] Shared code, published exports, fixtures and documentation introduce no service-local secret environment name, environment reads or fallback configuration for ARCH-039 credential security.

- [ ] Any authorised Node consumer can encrypt a `string` whose UTF-8 encoding occupies 1–8192 bytes and decrypt it to the identical string with exact AAD and the matching key ID; binary plaintext is not accepted, and independently crafted authenticated non-UTF8 plaintext fails closed.
- [ ] Fresh nonce on each encryption, 12-byte nonce, 16-byte tag and 1–8192 byte ciphertext enforced.
- [ ] All corrupt/forged data, unknown keys, wrong AAD and malformed envelope fail closed with typed secret-free errors; no raw crypto exception leaks.
- [ ] No new persistent envelope or editVersion field is introduced; consumers retain DB/domain mapping.
- [ ] Node entrypoint imports in ESM and .d.ts remains usable without leaking into browser entrypoints.

## Validation

- [ ] `npx tsx --test src/security/credentials/aead.test.ts`
- [ ] `npm run typecheck` and `npm run build`
- [ ] Built subpath ESM import test and type declaration inspection
- [ ] `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. Developer completion requires an explicit developer decision after accepted review. Do not begin dependent tasks.

## Implementation Notes

Include an independent known-format Node `createCipheriv` / `createDecipheriv` vector to catch matching bugs in encryption and decryption. Do not modify the existing service-local crypto until consumer tasks. The development-data wipe means compatibility with *persisted old ciphertext* is not required, but AEAD integrity/failure invariants still are.

Use the canonical dedicated parent/implementation task-worktree launcher and preserve initial synchronization evidence. Do not create/update `docs/decisions/**/_index.md` until the architecture session is explicitly confirmed complete. No implementation edits outside `moda-interact-shared`.

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
