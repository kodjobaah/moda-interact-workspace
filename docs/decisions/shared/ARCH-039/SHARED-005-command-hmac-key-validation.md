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

- [ ] Implement strict 32-byte canonical-base64 decoding and AES-key separation check.
- [ ] Add invalid-encoding, wrong-size, whitespace, base64url and AES-key-reuse tests.
- [ ] Verify the function returns byte values usable directly as HMAC input (not base64 text), and safe errors.
- [ ] Export through the single Node credential-security subpath; add ESM build/typecheck coverage.

## Interfaces / Contracts

Export only `parseCommerceConnectionCommandHmacKey` from `@modainteract/moda-interact-shared/security/credentials/node`; caller retains command digest semantics. Accepts SHARED-001 `CredentialKeyring`, is not a replacement for `createHmac` and does not change the AES keyring configuration contract.

## Dependencies

- ARCH-039-SHARED-001

## Enables

- ARCH-039-SHARED-004

## Acceptance Criteria

- [ ] Shared code, published exports, fixtures and documentation introduce no service-local secret environment name, environment reads or fallback configuration for ARCH-039 credential security.

- [ ] 32-byte independent canonical padded Base64 key returns 32 actual bytes; known HMAC-SHA256 vector matches direct `node:crypto` invocation on decoded bytes.
- [ ] Reused AES key bytes and malformed/missing/alternate encoding are rejected with one safe error code.
- [ ] No signing/audit logic, DB change, secret logging or service environment access in Shared.
- [ ] Public subpath and declaration compile.

## Validation

- [ ] `npx tsx --test src/security/credentials/command-hmac-key.test.ts`
- [ ] `npm run typecheck` and `npm run build`
- [ ] `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. Developer completion requires an explicit developer decision after accepted review. Do not begin dependent tasks.

## Implementation Notes

The HMAC key is a separate 32-byte random secret, not the UTF-8 Base64 configuration string and never one of the encryption keys. Caller must not log its bytes or send them to other services. Do not change Commerce application code as part of this Shared task.

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
