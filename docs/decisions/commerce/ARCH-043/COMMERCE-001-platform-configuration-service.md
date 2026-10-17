---
id: ARCH-043-COMMERCE-001
architecture_id: ARCH-043
title: Create Commerce database-backed platform configuration service
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-043-DATABASE-001
enables:
  - ARCH-043-COMMERCE-002
created: '2026-10-17'
updated: 2026-10-17
---

# Create reusable Commerce platform configuration service

## Architecture

- `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Configuration payloads, security envelope and frozen AAD: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_commerce` / `moda-interact-commerce`.
- Database prerequisite: `ARCH-043-DATABASE-001` is Complete in its canonical task record.

## Developer Ownership Amendment

On 2026-10-17, `/moda_developer_create ARCH-043-COMMERCE-001` was invoked to take over this ready task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_commerce`, repository ownership, scope, dependencies, requirements and acceptance criteria are unchanged.

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

- [x] Inspect current Commerce Prisma client and existing Shared credential entrypoints before editing.
- [x] Implement typed, injectable environment-scoped repository and strict three-key reader.
- [x] Implement preview policy validation/defaults and existing safety ceilings.
- [x] Implement sealed auth + connection-key decryption, purpose validation and AAD compatibility.
- [x] Add tests for fresh reads (update observed on next invocation), no cache/fallback, missing rows, malformed policies, wrong environment, revoked/tampered secrets, rotation and existing credential compatibility.
- [x] Complete focused validation and record source files, commands, results and launcher-resolved worktree isolation evidence in Completion Report.

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

- [x] One common server-side database reader supplies all three approved Commerce keys, with strict runtime schema checks and isolation.
- [x] A committed change is visible to the *next call*; no cross-operation cache or stale fallback.
- [x] Preview missing-row defaults are safe and hard ceilings cannot be weakened.
- [x] Wrong-environment, invalid, revoked, absent or undecryptable secret rows fail closed and leak no material.
- [ ] Shared crypto/AAD interoperability is proven with Admin-owned canonical test vectors; pre-existing Commerce credential ciphertext remains compatible. Existing credential AAD compatibility is tested; Admin-owned deterministic writer vectors are not yet available.
- [x] No existing Commerce consumer has been changed in this task.

## Validation

- [x] Focused repository/service unit tests (success, default, expiry-free fresh read, invalid rows, isolation).
- [x] PostgreSQL integration tests for unique environment-key lookup and post-update visibility when supported by test infrastructure.
- [x] Secret decrypt/AAD tampering and credential rotation compatibility tests.
- [x] Applicable repository typecheck, lint and build per actual `package.json`.
- [x] `git diff --check`.

## Stop Condition

Finish only the service and its tests; update Completion Report, set status Review and return to `moda_architect`. Do not start `COMMERCE-002`, modify `_index.md` or change existing runtime consumers.

## Implementation Notes

Avoid a competing generic logger; use approved shared logging if additional operational logging is necessary. Use the existing Prisma client and task-isolated parent/implementation worktrees. The downstream integration task owns adapting synchronous Auth.js and backend initialisation and must verify framework behaviour rather than assume async credentials can be inserted into synchronous configuration.

## Completion Report

### Status

Changes Requested — Attempt 1 developer self-review found one unmet acceptance criterion: cross-service crypto/AAD interoperability has not been checked against deterministic vectors produced by the Admin writer. The attempt number is unchanged; the task is Ready for correction and has not been claimed again.

### Files Changed

`package.json`; `scripts/run-arch043-platform-configuration-disposable.mjs`; `src/platform-configuration/service.ts`; `tests/platform-configuration-postgres.test.ts`; `tests/platform-configuration-service.test.ts`.

### Work Completed

Implemented a server-only Commerce platform-configuration service with an injectable Prisma read port, trusted-environment scoping, and a fixed allowlist for `commerce.preview`, `auth.commerce`, and `commerce.connectionKeys`. Preview policy values are strictly validated against existing ceilings, use the approved default only when the row is absent, and are re-read on each call. Required auth and connection secrets are checked for exact sealed-envelope and payload shapes, decrypted with the existing Shared credential functions and frozen AAD, and fail closed with bounded errors. Existing Commerce consumers were not modified. Unit tests cover fresh reads, defaults, environment isolation, malformed rows, tampering, key rotation, bounded errors, and compatibility with existing connection-credential AAD. PostgreSQL tests exercise the actual D001 migration and database constraints using an owned disposable container.

### Validation Results

Passed focused service tests: `node node_modules/vitest/vitest.mjs run tests/platform-configuration-service.test.ts` (9 passed).

Passed PostgreSQL integration: `node scripts/run-arch043-platform-configuration-disposable.mjs` (accepted D001 migration applied; 4/4 tests passed; owned disposable container removed).

Passed `npm run typecheck` and scoped ESLint for the four task-added source/test/runner files. Passed production compilation with `node node_modules/next/dist/bin/next build --webpack`; build emitted two existing Nunjucks dynamic-dependency warnings and completed successfully. This direct build command avoids the package build script's `prisma:generate` step, which runs `git submodule update` and could overwrite the existing local database submodule state. Passed `git diff --check origin/main...HEAD`.

Implementation evidence: canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-COMMERCE-001`, branch `task/ARCH-043-COMMERCE-001`, commit `0aca4710d7c5518bbe22d2cae66b3a50935bc147`, equal to `origin/task/ARCH-043-COMMERCE-001`. The only worktree modification is the `database` submodule pointer at `aa3fd02`, advanced from the task branch's recorded pointer `1397650`; it was not committed or reverted. The canonical parent task worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-COMMERCE-001` on `task/ARCH-043-COMMERCE-001`; this report update is the only intended parent-branch change.

### Deviations

The Admin-owned deterministic crypto/AAD vectors required by the acceptance criterion are not yet available. `ARCH-043-ADMIN-002` is currently `in_progress`; its task definition specifies the byte contract but no writer-produced vector is present in the current Admin artifacts. Existing Commerce tests construct ciphertext using the Commerce reader's own AAD helper, so they are not independent cross-service evidence.

### Assumptions

The local `database` submodule advancement to `aa3fd02` is preserved as pre-existing worktree state and is not part of this Commerce implementation commit.

### Unresolved Issues

Add deterministic writer-produced Admin test vectors, then add a Commerce reader interoperability test that consumes those vectors and verifies successful decryption plus fail-closed rejection for environment, key, version, and ciphertext tampering. Re-run the focused service tests, typecheck, and `git diff --check`; record the Admin vector source and test result before requesting review again.

### Architectural Concerns

No runtime consumer changes or scope deviations were found. The shared AAD contract remains unverified across the Admin-writer/Commerce-reader boundary until the correction above is completed.

## Developer Self-Review - Changes Requested (Attempt 1)

The implementation and listed validations pass, but the acceptance criterion requiring interoperability with Admin-owned canonical vectors is not satisfied. The in-progress Admin task has no writer-produced vectors available, and the Commerce test helper calls the same AAD function as the reader; that proves the local format string, not cross-service interoperability.

Correction required: consume deterministic ciphertext/AAD test vectors produced by the actual Admin writer; assert Commerce decrypts the expected purpose payload; and assert environment, key, version, and ciphertext tampering are rejected. Record the canonical vector location and focused test result. Do not change the production reader contract or existing Commerce credential AAD.

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
