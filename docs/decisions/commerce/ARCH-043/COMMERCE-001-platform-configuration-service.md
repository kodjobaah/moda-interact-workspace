---
id: ARCH-043-COMMERCE-001
architecture_id: ARCH-043
title: Create Commerce database-backed platform configuration service
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-043-DATABASE-001
enables:
  - ARCH-043-COMMERCE-002
created: '2026-10-17'
updated: '2026-10-17'
---

# Create reusable Commerce platform configuration service

## Architecture

- `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Configuration payloads, security envelope and frozen AAD: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_commerce` / `moda-interact-commerce`.
- Database prerequisite: `ARCH-043-DATABASE-001` (developer reports implementation completed; formally re-gate against its canonical task status before execution).

## Objective

Provide one reusable, server-only, read-only service that retrieves and validates Commerce platform configuration from `PlatformConfiguration`, without changing any existing Commerce runtime consumer.

## Context

Commerce currently has separate environment readers for preview budgets (`src/commerce/preview/run-budgets.ts`), Google/NextAuth secrets (`lib/auth/environment.ts`, `lib/server/config.ts`, `auth.ts`) and the connection keyring/HMAC (`src/commerce/connections/security-config.ts`, `lib/server/credential-keyring.ts`). The service centralises database access and validation only; `COMMERCE-002` performs the replacement at actual call sites.

## Scope

- Introduce a small Commerce-owned `src/platform-configuration/` service/repository module (names may match existing repository conventions) with injected Prisma and trusted deployment environment.
- Implement **three typed server-only operations**: `readCommercePreviewPolicy()`, `requireCommerceAuthConfiguration()` and `requireCommerceConnectionSecurity()`. They may share one private, strictly allowlisted `readPlatformConfiguration(key)` repository function.
- Read `PlatformConfiguration` through `findUnique({ where: { environment_key: { environment, key } } })` or the schema's equivalent unique selector; trust deployment environment, never request/browser input.
- Validate the closed `commerce.preview` object (`deadlineMs`, `outputTokens`) and the `auth.commerce` / `commerce.connectionKeys` encrypted envelopes and decrypted purpose-specific payloads against the exact ARCH-043 schema. Unknown fields, types, environment, key, version and ciphertext tampering fail safely.
- Use existing `@modainteract/moda-interact-shared/security/credentials/node` decryption/keyring functions and the architecture's frozen AAD bytes `JSON.stringify(["moda-platform-config-v1", environment, key, version, 1])`. Preserve pre-existing connection-credential ciphertext/AAD; unseal wrapping material stays outside PostgreSQL.
- Define typed outputs that give existing consumers the complete required auth (`AUTH_SECRET`, Google provider ID/secret) and connection material (keyring, active key ID, command HMAC key) **on trusted server paths only**. Never return sealed envelopes, decrypted secrets or key material to client components or public JSON.
- Support a code-owned safe default for a *missing* `commerce.preview` row only (60,000 ms / 1,200 tokens); preserve `PREVIEW_SLOT_MS - 30,000` and 32,768 hard ceilings. Invalid existing rows must be rejected, not replaced silently. Missing/disabled/corrupt auth or connection secrets fail closed.
- **No cache:** each call performs a fresh database read of the requested key, with no process-global singleton values, TTL, Redis snapshot, polling, or stale-last-good fallback. A single business operation may pass its validated result to its own downstream steps.
- Test through an injectable repository and disposable PostgreSQL integration where task validation requires it; do not change runtime routes or environment readers in this task.

## Out of Scope

- Do not modify `auth.ts`, preview admission, connection executors, server actions, Studio route composition, deployment configuration or existing domain credential records. These belong to `COMMERCE-002` or other owners.
- Do not write Admin configuration, create UI, add database schema/migrations, introduce Shared encryption code or a new publication task.
- No tenant/browser access to the configuration store; no support for arbitrary configuration keys or Messaging integration.

## Requirements

1. The service is a **read-only** trusted server facility, with a fixed three-key allowlist and strict environment isolation.
2. Each invocation retrieves a current row; subsequent invocations observe committed updates without refresh mechanisms or redeployment, subject to transaction visibility.
3. Preserve separate security layers: the external unseal key protects ARCH-043 secret envelopes; decoded Commerce connection key material still decrypts existing Commerce credential records using their original AAD.
4. Optional *absent* preview settings may use only current code defaults. Required secret settings fail closed when missing, disabled, tampered, wrong-environment or not decryptable.
5. Secret errors/logs expose only bounded key/status/reason identifiers; never secret values, keys, ciphertext, nonce, tags or request payloads.

## Work Items

- [ ] Inspect current Commerce Prisma client and existing Shared credential entrypoints before editing.
- [ ] Implement typed, injectable environment-scoped repository and strict three-key reader.
- [ ] Implement preview policy validation/defaults and existing safety ceilings.
- [ ] Implement sealed auth + connection-key decryption, purpose validation and AAD compatibility.
- [ ] Add tests for fresh reads (update observed on next invocation), no cache/fallback, missing rows, malformed policies, wrong environment, revoked/tampered secrets, rotation and existing credential compatibility.
- [ ] Complete focused validation and record source files, commands, results and launcher-resolved worktree isolation evidence in Completion Report.

## Interfaces / Contracts

- Existing DB models: `PlatformConfiguration` and `PlatformConfigurationAudit`, owned by `ARCH-043-DATABASE-001`. This service reads only `PlatformConfiguration`.
- Keys and shapes: `commerce.preview`, `auth.commerce`, `commerce.connectionKeys` in the ARCH-043 configuration schema review.
- Existing Shared cryptography: `@modainteract/moda-interact-shared/security/credentials/node` (ARCH-039), without changes.
- Proposed methods (exact signatures may be adapted to existing Commerce repository style):

```ts
readCommercePreviewPolicy(deps): Promise<{ deadlineMs: number; outputTokens: number }>;
requireCommerceAuthConfiguration(deps): Promise<{ authSecret: string; googleClientId: string; googleClientSecret: string }>;
requireCommerceConnectionSecurity(deps): Promise<{ keyring: CredentialKeyring; activeKeyId: string; commandHmacKey: Uint8Array }>;
```

## Dependencies

- `ARCH-043-DATABASE-001` (canonical status must be Complete).

## Enables

- `ARCH-043-COMMERCE-002`

## Acceptance Criteria

- [ ] One common server-side database reader supplies all three approved Commerce keys, with strict runtime schema checks and isolation.
- [ ] A committed change is visible to the *next call*; no cross-operation cache or stale fallback.
- [ ] Preview missing-row defaults are safe and hard ceilings cannot be weakened.
- [ ] Wrong-environment, invalid, revoked, absent or undecryptable secret rows fail closed and leak no material.
- [ ] Shared crypto/AAD interoperability is proven with Admin-owned canonical test vectors; pre-existing Commerce credential ciphertext remains compatible.
- [ ] No existing Commerce consumer has been changed in this task.

## Validation

- [ ] Focused repository/service unit tests (success, default, expiry-free fresh read, invalid rows, isolation).
- [ ] PostgreSQL integration tests for unique environment-key lookup and post-update visibility when supported by test infrastructure.
- [ ] Secret decrypt/AAD tampering and credential rotation compatibility tests.
- [ ] Applicable repository typecheck, lint and build per actual `package.json`.
- [ ] `git diff --check`.

## Stop Condition

Finish only the service and its tests; update Completion Report, set status Review and return to `moda_architect`. Do not start `COMMERCE-002`, modify `_index.md` or change existing runtime consumers.

## Implementation Notes

Avoid a competing generic logger; use approved shared logging if additional operational logging is necessary. Use the existing Prisma client and task-isolated parent/implementation worktrees. The downstream integration task owns adapting synchronous Auth.js and backend initialisation and must verify framework behaviour rather than assume async credentials can be inserted into synchronous configuration.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation and validation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not assessed.

### Follow-up

None
