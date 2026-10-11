---
id: ARCH-032-MCP-011
architecture_id: ARCH-032
title: Extract the Admin-managed Merchant Knowledge embedding runtime
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 11
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-032-MCP-010
enables:
  - ARCH-032-MCP-012
created: 2026-10-11
updated: 2026-10-11
---

# Admin-managed Merchant Knowledge embedding runtime

## Objective

Extract the existing Commerce embedding configuration, encrypted credential
resolver and environment-scoped keyring contract into the standalone MCP
runtime. Wire that resolver into MCP-010's Merchant Knowledge policy adapter
without modifying the existing Commerce MCP server or enabling live traffic.

## Read first

- `moda-interact-commerce/src/commerce/merchant-knowledge/embedding-runtime.ts`
- `moda-interact-commerce/lib/server/credential-keyring.ts`
- `moda-interact-database/prisma/schema.prisma` (`CommerceEmbeddingConfiguration`)
- `moda-interact-mcp/src/execution/merchant-knowledge/{adapter,embedding}.ts`
- `moda-interact-mcp/src/runtime/prisma.ts`

## Scope

- Reuse the persisted `CommerceEmbeddingConfiguration` for the appropriate
  `CommerceEnvironment` and the `MERCHANT_KNOWLEDGE` purpose.
- Preserve Commerce's canonical JSON authenticated data for AES-256-GCM
  decryption, keyring parsing, secret validation and bounded failures.
- Re-read configuration for each invocation to observe Admin changes,
  credential replacement and deletion without restart.
- Obtain key material only from the existing private
  `COMMERCE_CONNECTION_KEYS_JSON` deployment secret.
- Wire the resolver into the prepared `openPrismaMcpPersistence()` runtime;
  preserve optional injected resolvers for isolated tests.
- Keep the existing `src/index.ts`, HTTP transport, OpenAPI, readiness,
  Commerce and Background unchanged; add no schema migrations.
- Add focused unit tests under `tests/unit/` and Docker-disposable PostgreSQL
  integration tests with synthetic encrypted credentials.

## Acceptance Criteria

- Valid TEST (and other supported environment) configuration decrypts using
  the original Commerce authenticated data and 32-byte keyring contract.
- Database/model/credential updates and revocation affect subsequent calls;
  no stale plaintext or credential cache survives Admin changes.
- Missing, invalid, mismatched, tampered and malformed configuration fails
  closed without exposing secrets. Database errors are retryable.
- No OpenAI calls are made by the credential-resolution tests; no live MCP
  endpoint is opened.
- Unit, typecheck, lint and build pass on the declared Node toolchain;
  disposable migrated PostgreSQL integration tests pass locally.
- No `docs/decisions/**/_index.md` changes or cross-service runtime edits.

## Validation

- [ ] `git apply --check --whitespace=error-all` against MCP-010 Attempt 1.
- [ ] `git apply --whitespace=error-all` and `git diff --check`.
- [ ] `npm run typecheck`, `npm run lint`, `npm test`, `npm run build`.
- [ ] `npm run typecheck:integration`, `npm run test:integration:docker`.
- [ ] Confirm standalone HTTP entry remains fail-closed.

## Completion Report

### Status

Not started. Developer-owned patch delivery, awaiting local validation and
architect review; no architect acceptance decision is implied.
