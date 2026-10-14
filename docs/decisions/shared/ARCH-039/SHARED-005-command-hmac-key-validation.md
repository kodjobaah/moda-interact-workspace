---
id: ARCH-039-SHARED-005
architecture_id: ARCH-039
title: Validate independent Commerce command-HMAC secret bytes
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

# Validate independent Commerce command-HMAC secret bytes

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_shared` / `moda-interact-shared`

## Objective

Implement the strict separate command-signing key decoder without conflating an HMAC secret with AES encryption keys.

## Context

ARCH-039 standardises hosted credential security before consumer refactoring. The developer will clear non-production credential and command-audit state: this is a breaking pre-production cutover without historical compatibility. Interfaces established here are the binding contracts for downstream Shared and service tasks.

## Scope

- Implement `src/security/credentials/command-hmac-key.ts` and export one typed decoder through `src/security/credentials/node.ts`.
- Reuse the SHARED-001 opaque keyring internally to verify the HMAC key is not any AES key in the same configured keyring.

## Out of Scope

- Signing/verifying commands, HMAC payload canonicalisation, retry/idempotency semantics, audit-row migration, Commerce code changes and Gateway wiring.
- No HMAC secret distribution to Admin, Background, MCP or API.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- Shared is a **pure Node library** for ARCH-039 secrets: never read `process.env`, introduce or document another credential-security environment name, infer an environment variable by convention, or generate replacement keys. Callers inject parsed values sourced exclusively from the canonical `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and (for Commerce commands only) `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` via their authorised server adapters. Publication must not introduce alternate configuration.

**Public API:**

```ts
export function parseCommerceConnectionCommandHmacKey(
  raw: string | undefined,
  aesKeyring: CredentialKeyring,
): Uint8Array;
```

- `raw` comes exclusively from `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` at the **Commerce** service host boundary. No environment reads inside Shared.
- Require exact canonical, padded **standard Base64** encoding of a 32-byte value: `^[A-Za-z0-9+/]{43}=$` and round-trip equality. Reject undefined, empty, leading/trailing whitespace, base64url, wrong length/decoded bytes and malformed padding.
- Perform bytewise comparison with every secret AES key held by `aesKeyring` through a Shared-private accessor; reject key reuse. This check must not expose either AES keys or HMAC key material to the caller as an error message.
- Return a **new** `Uint8Array` containing decoded HMAC bytes for `createHmac('sha256', keyBytes)`. No string/base64 text is returned, and no generic encrypt/decrypt use is permitted.
- Invalid input or reused AES material throws `CredentialSecurityError` with code `INVALID_COMMAND_HMAC_KEY`, with static secret-free message and no `cause` exposing key material.
- **Current Commerce difference to be addressed downstream:** `src/commerce/connections/command-kernel.ts` currently calls `createHmac('sha256', commandHmacKey)` with a string. `ARCH-039-COMMERCE-001` must pass decoded bytes instead, update its command kernel input type and assert deterministic digests. Pre-production idempotency/audit evidence will be cleared by the developer.

## Work Items

- [x] Implement strict 32-byte canonical-base64 decoding and AES-key separation check.
- [x] Add invalid-encoding, wrong-size, whitespace, base64url and AES-key-reuse tests.
- [x] Verify the function returns byte values usable directly as HMAC input (not base64 text), and safe errors.
- [x] Export through the single Node credential-security subpath; add ESM build/typecheck coverage.

## Interfaces / Contracts

Export only `parseCommerceConnectionCommandHmacKey` from `@modainteract/moda-interact-shared/security/credentials/node`; caller retains command digest semantics. Accepts SHARED-001 `CredentialKeyring`, is not a replacement for `createHmac` and does not change the AES keyring configuration contract.

## Dependencies

- ARCH-039-SHARED-001

## Enables

- ARCH-039-SHARED-004

## Acceptance Criteria

- [x] Shared code, published exports, fixtures and documentation introduce no service-local secret environment name, environment reads or fallback configuration for ARCH-039 credential security.

- [x] 32-byte independent canonical padded Base64 key returns 32 actual bytes; known HMAC-SHA256 vector matches direct `node:crypto` invocation on decoded bytes.
- [x] Reused AES key bytes and malformed/missing/alternate encoding are rejected with one safe error code.
- [x] No signing/audit logic, DB change, secret logging or service environment access in Shared.
- [x] Public subpath and declaration compile.

## Validation

- [x] `npx tsx --test src/security/credentials/command-hmac-key.test.ts` (10 passed, 0 failed)
- [x] `npm run typecheck` and `npm run build` (both passed)
- [x] Built Node subpath ESM import, known HMAC vector, root-export isolation, declaration inspection and `git diff --check` (passed)

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. Developer completion requires an explicit developer decision after accepted review. Do not begin dependent tasks.

## Implementation Notes

The HMAC key is a separate 32-byte random secret, not the UTF-8 Base64 configuration string and never one of the encryption keys. Caller must not log its bytes or send them to other services. Do not change Commerce application code as part of this Shared task.

Use the canonical dedicated parent/implementation task-worktree launcher and preserve initial synchronization evidence. Do not create/update `docs/decisions/**/_index.md` until the architecture session is explicitly confirmed complete. No implementation edits outside `moda-interact-shared`.

## Completion Report

### Status

Review ready — Attempt 1 implementation is committed and published; all Work Items, Acceptance Criteria and required Validation pass. Submitted for architect review. Completion mode is `developer`; explicit developer completion is pending.

### Files Changed

- `src/security/credentials/command-hmac-key.ts`
- `src/security/credentials/command-hmac-key.test.ts`
- `src/security/credentials/node.ts`

### Work Completed

- Added `parseCommerceConnectionCommandHmacKey` to decode exactly 32 bytes of canonical padded standard Base64, rejecting malformed, alternate or noncanonical input.
- Compared the decoded HMAC key against every private AES key using timing-safe equality and defensive keyring copies; rejects forged keyring descriptors and AES-key reuse with the static `INVALID_COMMAND_HMAC_KEY` error.
- Returns independent `Uint8Array` bytes for direct HMAC use and exports the decoder only through the existing Node credentials subpath.
- Added tests for the independent HMAC-SHA256 known vector, malformed encodings, wrong sizes, whitespace, base64url, AES-key reuse, forged keyrings, error secrecy and returned-byte independence.

### Validation Results

- `npx tsx --test src/security/credentials/command-hmac-key.test.ts`: 10 passed, 0 failed.
- `npm run typecheck`: passed.
- `npm run build`: passed; generated `dist/security/credentials/node.js` and `.d.ts`.
- Node ESM smoke imported the package-name Node subpath, decoded the known key, matched the expected HMAC-SHA256 vector and confirmed the root package does not export the decoder.
- Declaration inspection confirmed the decoder and `CredentialKeyring` type are exported in the Node subpath declaration.
- Credential implementation scan found no `process.env` reads or service-local credential environment variables.
- `git diff --check origin/main...HEAD`: passed.

### Deviations

None.

### Assumptions

None beyond parent architecture.

### Unresolved Issues

None.

### Architectural Concerns

None.

### Physical Worktree and Synchronization Evidence

- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-039-SHARED-005`, branch `task/ARCH-039-SHARED-005`; synchronized with current parent `origin/main` at `c78c0345abf1cd77415fa75281d7f1628c7e64a0`, clean after claim/report updates.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-039-SHARED-005`, branch `task/ARCH-039-SHARED-005`; created from implementation `origin/main` at `92e17fed999a0c194dcbfa3669a63c48ce82cf05`, clean after build (generated output ignored).
- Parent claim commit `1917f282e959e3d2dcfc6f5faa76d89ade0f39cf` is pushed. Implementation commit `3cb4dbc` is published to `origin/task/ARCH-039-SHARED-005`.
- Launcher dependency gate passed for the only declared prerequisite, `ARCH-039-SHARED-001` (`complete`). Recursive submodule sync/update passed with no entries.
- The primary workspace contained unrelated dirty submodules/untracked files; they were not modified. No other task worktree was reused, and no assigned-agent assistance was used.

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

## Developer Self-Review Passed/Accepted

- Attempt: 1.
- Result: Passed. Work Items, Acceptance Criteria and required Validation are complete and match implementation commit `3cb4dbc` on the Shared task branch.
- Evidence: focused tests 10/10 passed; typecheck and build passed; package-name ESM smoke, known HMAC vector, declaration and root isolation checks passed; credential environment scan and diff check passed.
- Lifecycle: submitted as `status: review`, with `executor: null`, `claimed_at: null` and attempt unchanged at 1. Because `completion_mode: developer`, explicit developer completion remains pending.
