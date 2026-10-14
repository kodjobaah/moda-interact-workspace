---
id: ARCH-039-SHARED-001
architecture_id: ARCH-039
title: Define strict opaque Commerce credential keyring
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-039-SHARED-002
  - ARCH-039-SHARED-003
  - ARCH-039-SHARED-005
created: 2026-10-14
updated: 2026-10-14
---

# Define strict opaque Commerce credential keyring

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_shared` / `moda-interact-shared`

## Objective

Implement a single, fail-closed keyring parser and active-writer-key selector with a stable, precisely typed Node-only public API.

## Context

ARCH-039 standardises hosted credential security before consumer refactoring. The developer will clear non-production credential and command-audit state: this is a breaking pre-production cutover without historical compatibility. Interfaces established here are the binding contracts for downstream Shared and service tasks.

## Scope

- Add `src/security/credentials/keyring.ts` (and narrowly scoped internal helpers) and `src/security/credentials/node.ts`.
- Add the `./security/credentials/node` export to `package.json` and matching `security/credentials/node` entry to `tsup.config.ts` (types + ESM).
- Implement only parsing, key selection and reusable non-sensitive typed error handling. Tests in `src/security/credentials/*.test.ts`.

## Out of Scope

- AES encryption, decryption, envelopes, AAD construction, command HMAC, Render environment wiring and all consumer repositories.
- No `process.env` access, database reads, logging or dependency on the existing Admin/Commerce parsers.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- Shared is a **pure Node library** for ARCH-039 secrets: never read `process.env`, introduce or document another credential-security environment name, infer an environment variable by convention, or generate replacement keys. Callers inject parsed values sourced exclusively from the canonical `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and (for Commerce commands only) `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` via their authorised server adapters. Publication must not introduce alternate configuration.

**Public TypeScript contract:**

```ts
export interface CredentialKeyring {
  readonly keyIds: readonly string[];
  hasKey(keyId: string): boolean;
}
export function parseCredentialKeyring(raw: string | undefined): CredentialKeyring;
export function resolveActiveCredentialKey(
  keyring: CredentialKeyring,
  activeKeyId: string | undefined,
): string;
export type CredentialSecurityErrorCode =
  | 'INVALID_KEYRING' | 'KEY_UNAVAILABLE'
  | 'INVALID_CREDENTIAL' | 'INVALID_COMMAND_HMAC_KEY';
export class CredentialSecurityError extends Error {
  constructor(code: CredentialSecurityErrorCode);
  readonly code: CredentialSecurityErrorCode;
}
```

**Input contract:**
- `raw` is a JSON object, **not an array**, with 1–16 own string properties; reject undefined, empty and whitespace-only strings, `null`, other JSON types, empty objects, unknown value types and JSON with repeated *decoded* property names (including escaped equivalents). Do not rely on `JSON.parse` alone for duplicate detection.
- Key IDs must match `^[A-Za-z0-9_-]{1,64}$`, be unique, and must not equal `__proto__`, `prototype` or `constructor`.
- Values must match `^[A-Za-z0-9+/]{43}=$`, decode into exactly 32 bytes and round-trip byte-for-byte to the identical **standard, padded Base64** string; reject whitespace, unpadded, base64url and malformed encodings. Reject more than 16 keys and excessive raw input (>4096 UTF-8 bytes).
- Reader parsing never consults `COMMERCE_CONNECTION_ACTIVE_KEY_ID`. `resolveActiveCredentialKey()` validates the supplied ID exactly (no implicit trimming or fallback), checks presence, then returns that ID; an absent selector is invalid **only when writer selection is requested**.
- The public keyring is a frozen, nonmutating descriptor (stable sorted IDs + `hasKey()`), with private copied 32-byte keys held internally by Shared. Do **not** expose mutable key bytes, a writable Map or credential key material through any public export. The later AEAD module reads those keys through a package-internal helper only.
- Return copies rather than references to private IDs/keys where appropriate; prevent mutation of one caller's keyring from changing a subsequent seal/open operation.

**Failure contract:** malformed config -> `CredentialSecurityError('INVALID_KEYRING')`; missing/unknown writer key -> `CredentialSecurityError('KEY_UNAVAILABLE')`. Errors have static secret-free messages and no copied raw configuration or nested crypto `cause`.

## Work Items

- [ ] Add and type the export-map/build entry and Node-only keyring module.
- [ ] Parse strict JSON with duplicate-decoded-name rejection, whitelist key IDs, 1–16 entries and canonical 32-byte padded Base64.
- [ ] Expose opaque, read-only keyring descriptor plus `resolveActiveCredentialKey`; keep key bytes module-private for SHARED-002.
- [ ] Implement the shared typed-error contract without raw config or secret values in messages.
- [ ] Add table-driven positive/negative/immutability tests and a built-subpath import smoke test.

## Interfaces / Contracts

Canonical import (later tasks MUST reuse; no duplicate local parser):

```ts
import {
  parseCredentialKeyring, resolveActiveCredentialKey,
  CredentialSecurityError, type CredentialKeyring,
} from '@modainteract/moda-interact-shared/security/credentials/node';
const keys = parseCredentialKeyring(rawKeysFromHost);
const writerId = resolveActiveCredentialKey(keys, activeIdFromHost);
```

`rawKeysFromHost` is **only** `COMMERCE_CONNECTION_KEYS_JSON`. The writer ID is **only** `COMMERCE_CONNECTION_ACTIVE_KEY_ID`; Shared never calls `process.env`. Consumers retain explicit feature-enablement decisions, not silent parser fallbacks.

## Dependencies

None.

## Enables

- ARCH-039-SHARED-002
- ARCH-039-SHARED-003
- ARCH-039-SHARED-005

## Acceptance Criteria

- [ ] Shared code, published exports, fixtures and documentation introduce no service-local secret environment name, environment reads or fallback configuration for ARCH-039 credential security.

- [ ] 1–16 canonical entries accepted; 0/17 entries, invalid IDs, duplicate JSON names (including escape-equivalent names), wrong byte length and altered Base64 rejected.
- [ ] Reader-only use works with no active selector; writer fails for undefined, missing or invalid ID. No fallback to first available key.
- [ ] Caller cannot mutate the underlying encryption key by modifying a public return value.
- [ ] Error code is stable and does not contain configuration, keys, plaintext or a sensitive `cause`.
- [ ] Exact published Node subpath has usable .js/.d.ts outputs; no re-export into browser/root or generic `/commerce` entrypoints.

## Validation

- [ ] `npx tsx --test src/security/credentials/keyring.test.ts` (table-driven positive/negative + mutation matrix)
- [ ] `npm run typecheck`
- [ ] `npm run build` and Node ESM import smoke of `./dist/security/credentials/node.js` (export-map and declaration existence)
- [ ] Inspect root/browser entrypoints for accidental `node:crypto` imports
- [ ] `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. Developer completion requires an explicit developer decision after accepted review. Do not begin dependent tasks.

## Implementation Notes

No service-specific error strings or framework-only `server-only` import inside Shared. UI frameworks should enforce their own server boundary. Follow existing Shared Node-only entrypoint conventions (`src/merchant-communications.node.ts`, `src/commerce/model/node.ts`).

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
