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
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
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

- [x] Add and type the export-map/build entry and Node-only keyring module.
- [x] Parse strict JSON with duplicate-decoded-name rejection, whitelist key IDs, 1–16 entries and canonical 32-byte padded Base64.
- [x] Expose opaque, read-only keyring descriptor plus `resolveActiveCredentialKey`; keep key bytes module-private for SHARED-002.
- [x] Implement the shared typed-error contract without raw config or secret values in messages.
- [x] Add table-driven positive/negative/immutability tests and a built-subpath import smoke test.

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

- [x] Shared code, published exports, fixtures and documentation introduce no service-local secret environment name, environment reads or fallback configuration for ARCH-039 credential security.

- [x] 1–16 canonical entries accepted; 0/17 entries, invalid IDs, duplicate JSON names (including escape-equivalent names), wrong byte length and altered Base64 rejected.
- [x] Reader-only use works with no active selector; writer fails for undefined, missing or invalid ID. No fallback to first available key.
- [x] Caller cannot mutate the underlying encryption key by modifying a public return value.
- [x] Error code is stable and does not contain configuration, keys, plaintext or a sensitive `cause`.
- [x] Exact published Node subpath has usable .js/.d.ts outputs; no re-export into browser/root or generic `/commerce` entrypoints.

## Validation

- [x] `npx tsx --test src/security/credentials/keyring.test.ts` (10 table-driven positive/negative + mutation tests passed)
- [x] `npm run typecheck`
- [x] `npm run build` and Node ESM import smoke of the package subpath; `.js` and `.d.ts` outputs exist and import succeeds by package name.
- [x] Inspect root/browser entrypoints for accidental `node:crypto` imports; no keyring/crypto dependency was introduced into root or generic commerce entrypoints. Existing `node:crypto` use remains confined to the established Node-specific merchant-communications entrypoint.
- [x] `git diff --check origin/main...HEAD`

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. Developer completion requires an explicit developer decision after accepted review. Do not begin dependent tasks.

## Implementation Notes

No service-specific error strings or framework-only `server-only` import inside Shared. UI frameworks should enforce their own server boundary. Follow existing Shared Node-only entrypoint conventions (`src/merchant-communications.node.ts`, `src/commerce/model/node.ts`).

Use the canonical dedicated parent/implementation task-worktree launcher and preserve initial synchronization evidence. Do not create/update `docs/decisions/**/_index.md` until the architecture session is explicitly confirmed complete. No implementation edits outside `moda-interact-shared`.

## Completion Report

### Status

Complete — Attempt 1 passed developer self-review and the developer explicitly accepted completion on 2026-10-14. Implementation and parent task records are committed and published. Attempt remains 1.

### Files Changed

- `package.json`
- `tsup.config.ts`
- `src/security/credentials/errors.ts`
- `src/security/credentials/keyring.ts`
- `src/security/credentials/node.ts`
- `src/security/credentials/keyring.test.ts`

### Work Completed

- Added a Node-only published `security/credentials/node` subpath with typed declarations; the root, browser-facing and generic commerce entrypoints do not re-export it.
- Added strict JSON object parsing that rejects duplicate decoded property names, invalid/reserved IDs, excess entries and input bytes, non-string values, malformed or noncanonical Base64 and keys not exactly 32 bytes.
- Added an opaque frozen descriptor with sorted IDs and `hasKey`, plus exact active writer-key selection. Private key bytes are held behind a WeakMap and only package-internal code can request a defensive copy.
- Added static secret-free `CredentialSecurityError` codes/messages and positive, negative, duplicate-name, encoding, writer-selection, immutability and error tests.

### Validation Results

- `npx tsx --test src/security/credentials/keyring.test.ts`: 10 passed, 0 failed.
- `npm run typecheck`: passed.
- `npm run build`: passed; generated `dist/security/credentials/node.js` and `dist/security/credentials/node.d.ts`.
- Node ESM smoke imported `@modainteract/moda-interact-shared/security/credentials/node`, parsed a valid keyring and resolved its writer ID; root-package isolation assertion passed.
- Root/generic commerce entrypoint scan found no new keyring or `node:crypto` import; Shared keyring source has no `process.env` access or alternate credential environment name.
- `git diff --check origin/main...HEAD`: passed.

### Physical Worktree and Synchronization Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-039-SHARED-001`, branch `task/ARCH-039-SHARED-001`; created for this task, clean after report update.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-039-SHARED-001`, branch `task/ARCH-039-SHARED-001`; created for this task, clean after implementation commit.
- Parent task claim commit `cb569e8fc7b788a5a920e23053423d8f5cfd0c28` is published. Implementation commit `f06424da8ccffb17b2d25b7b4a20acc4a1b01ae7` is published and equals `origin/task/ARCH-039-SHARED-001`.
- Both branches started from their current `origin/main`; the launcher reported task-branch fast-forward not needed and `origin/main` already incorporated. Recursive submodule sync/update passed; there are no implementation submodule entries.
- Shared/default workspace and implementation checkouts were not switched or mutated for task implementation. No other task worktree was reused; no assigned-agent assistance was used.

### Deviations

None.

### Assumptions

None beyond parent architecture.

### Unresolved Issues

No SHARED-001 implementation or validation issues. The downstream dependency cycle among SHARED-002, SHARED-004 and SHARED-005 remains for architect resolution; see Dependency Frontier Reconciliation.

### Architectural Concerns

The existing dependency cycle blocks SHARED-002 and SHARED-005 until the task graph is corrected by the architect.

## Developer Self-Review Passed/Accepted

- Attempt: 1.
- Result: Passed. All Work Items, Acceptance Criteria and required Validation recorded above were checked against the implementation in `moda-interact-shared` commit `f06424da8ccffb17b2d25b7b4a20acc4a1b01ae7`.
- Evidence: 10/10 focused keyring tests passed; typecheck and build passed; package-name Node ESM import and `.d.ts` smoke passed; root/generic commerce entrypoint isolation passed; `git diff --check` passed.
- Publication: implementation commit is pushed to `origin/task/ARCH-039-SHARED-001`; parent task report commit `d8fa5ee809d8bba2906da088e3a4de6b2acbe2c5` was pushed before this completion decision.

## Developer Completion Decision

- Date: 2026-10-14.
- Decision: the developer explicitly invoked `/moda_developer_update ARCH-039-SHARED-001 complete` and accepts attempt 1 as complete following the passing review above.
- Lifecycle: `status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`.
- Integration: no task branch was merged to `main`.

### Dependency Frontier Reconciliation

- `ARCH-039-SHARED-003` is now `ready`: its only explicit dependency, SHARED-001, is complete.
- `ARCH-039-SHARED-002` and `ARCH-039-SHARED-005` remain `pending` because each depends on SHARED-004. SHARED-004 remains `pending` because it depends on SHARED-002, SHARED-003 and SHARED-005. This reveals an existing dependency cycle among SHARED-002, SHARED-004 and SHARED-005; dependency edges were not changed as part of SHARED-001 completion and require architect resolution before those tasks can be claimed.

## Architect Review

### Review Status

No separate Architect Review was requested; this developer-controlled task was accepted through the passing developer self-review and explicit completion decision recorded above.

### Review Notes

See the Developer Self-Review Passed/Accepted and Developer Completion Decision above.

### Reviewed Files

Implementation files listed in the Completion Report above.

### Validation Reviewed

Focused tests, typecheck, build, built-subpath ESM/declaration smoke, entrypoint isolation and diff check passed as recorded above.

### Architecture Conformance

The developer self-review found the implementation conformant to the task requirements; no separate Architect Review was performed.

### Follow-up

None.
