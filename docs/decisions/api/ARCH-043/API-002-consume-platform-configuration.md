---
id: ARCH-043-API-002
architecture_id: ARCH-043
title: Apply database-managed configuration to hosted API consumers
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 35
executor: developer
claimed_at: 2026-10-18T15:16:59Z
attempt: 1
depends_on:
  - ARCH-043-API-001
  - ARCH-043-ADMIN-002
enables:
  - ARCH-043-GATEWAY-001
  - ARCH-043-SYSTEM-TEST-001
created: 2026-10-17
updated: 2026-10-18
---

# Apply database-managed configuration to hosted API consumers

## Developer Ownership Amendment

On 2026-10-18, `/moda_developer_create ARCH-043-API-002` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_api`, repository ownership, dependencies, scope and acceptance criteria are unchanged. The next canonical launcher preparation will claim Attempt 1 as `developer`.

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Contracts: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-api` / `moda_api`.
- This is a portable task definition; readiness is dependent on accepted `API-001` and `ADMIN-002` completions, not merely the existence of their source code.

## Objective

Connect the accepted `API-001` platform configuration reader to the existing Merchant Knowledge R2 and WooCommerce REST-read consumers, with bounded, secret-safe structured logging through the API's existing Shared logger.

## Context

- Merchant Knowledge reads/commands use `process.env.MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES` in `src/composition/merchant.ts`; upload signing/finalisation use `loadUploadR2Configuration()` in `src/merchant/merchant-knowledge/upload-r2.ts` and `upload.service.ts`.
- `src/runtime-config.ts` currently reads the Commerce keyring at process startup; `src/composition/woocommerce.ts` supplies it to `WooReadAuthorizationService`, which holds a single configuration object.
- The existing API has no caller for a private Meta secret-returning route. `messaging.meta` remains an Admin-managed configuration purpose, but no API endpoint, Gateway service-identity scheme or Messaging client is required by this task.
- The API entrypoint already creates a logger from `@modainteract/moda-interact-shared/logging`; the accepted implementation passes that logger to the lazy configuration reader.

## Scope

**A. Merchant Knowledge:**

- Compose the `API-001` reader once (as an object, not a cached value) and inject it into existing Merchant Knowledge read, command and upload pathways.
- For each upload intent/finalisation, retrieve the complete, current, sealed `merchant.knowledge.r2` configuration: `endpoint`, `bucket`, `accessKeyId`, `secretAccessKey`, `maxUploadBytes` and `maxXlsxUncompressedBytes`. Apply validated limits where consumed, and use a consistent decrypted snapshot **once per operation**; never read inside a transaction if external R2 calls would follow within that transaction.
- Replace environment-derived Knowledge and R2 credential reads in `src/composition/merchant.ts`, `src/merchant/merchant-knowledge/read.service.ts`, `src/merchant/merchant-knowledge/upload-r2.ts`, `upload.service.ts` and other confirmed API consumers, preserving installation authentication, tenant scoping, upload integrity and idempotency. Do not retain a separate source for R2 credentials.
- Keep `r2Endpoint` and `r2Bucket` **fully editable**. Do not implement separate asset relocation/in-flight safety workflows, which have other owners; do not silently lock the fields.

**B. Commerce connection keyring:**

- Replace `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` reads in the API REST-read credential path with `requireCommerceConnectionSecurity()` from API-001.
- Refactor `src/runtime-config.ts`, `src/composition/woocommerce.ts`, `src/woocommerce/rest-read/config.ts`, `authorization.service.ts` and directly related handlers as necessary so the current keyring is resolved at the relevant **start/callback/verification operation**, rather than captured only at process startup. Preserve configured public origin and connection-mode security as deployment settings; do not move unrelated variables.
- Preserve ARCH-039 grant ciphertext AAD, old-key decryption during rotation, signed return-locale proofs and callback replay protection. Never recompute a signature using an unrelated later config version within the same operation.
- Ensure a malformed or missing database keyring causes the protected operation to fail closed rather than silently disabling the entire REST-read route or switching back to environment credentials.

**C. Shared structured logging:**

- Reuse the API's existing logger from `@modainteract/moda-interact-shared/logging`, injected into the lazy platform configuration reader from `src/index.ts`. Do not introduce a service-local generic logger or duplicate JSON formatting/redaction logic.
- Emit `api.platform_configuration.read` for both successful and failed configuration reads. Log only the canonical configuration key, a bounded operation identifier, success/failure outcome and a bounded reason code on failure. Do not log decrypted or encrypted configuration values, tokens, keyrings, encryption material, R2 endpoint/bucket, credentials, exception messages or stack traces.
- Logging is diagnostic only: logger/sink failures must not turn successful configuration reads or business operations into failures. Preserve configuration-read failure semantics and avoid logging secrets on errors.
- Add focused tests for success, failure, lazy resolution and redaction using `tests/unit/platform-configuration/logging.test.ts` and the existing API-002 consumer tests.

**D. Explicit boundary:**

- Do not create a private Meta secret-returning endpoint or implement Gateway service identity for one. Do not change Messaging runtime verification or remove `META_APP_SECRET` / `WHATSAPP_VERIFY_TOKEN` deployment settings. The pre-existing server-side `API-001.requireMetaWebhookSecrets()` method is not a mandate to expose an HTTP route.

## Out of Scope

- No new database schema, Shared cryptography, Admin editor, Messaging runtime change, new secret import mechanism, R2 storage relocation, private Meta secret-returning route, Gateway identity mechanism or arbitrary secret-list endpoint.
- No Woo billing credential migration: legacy `API-003-woo-billing-credential-reader.md` belongs to an obsolete prior proposal and is not in the canonical 15-task architecture.
- No environment variable removal from Gateway, unrelated route refactors or `_index.md` changes.

## Requirements

- Every business operation retrieves the required current PostgreSQL row via API-001. No process/Redis cache, TTL snapshots, refresh loop or stale fallback; reuse one read only within the same operation.
- Database/unseal failure, disabled secret tombstone, wrong environment and invalid configuration must fail closed with bounded safe errors. Neither authentication credentials nor R2 signing secrets may appear in merchant/API output or logs.
- Required Admin-managed sealed R2 and Commerce keyring records must be configured before DB-only consumer activation; API-002 depends on architect-accepted `ADMIN-002`. The architecture assumes a fresh pre-production database and does not require legacy configuration-data migration.
- Preserve deployment-origin validation, Woo tenant boundaries, webhook callback integrity, upload transaction boundaries and existing API readiness behaviour.
- Log configuration read outcomes using the already-composed Shared logger, with redacted, bounded metadata and failure-isolated logging. No Meta HTTP resolver is in scope.

## Work Items

- [ ] Integrate fresh six-field `merchant.knowledge.r2` reads into upload, finalisation, read projection and other actual limit consumers.
- [ ] Integrate per-operation Commerce keyring retrieval into REST-read authorization and callback/return proof paths; remove only superseded local env reads.
- [ ] Inject the existing Shared logger into the API-001 reader and emit safe read success/failure events; add structured logging and redaction tests.
- [ ] Add focused consumer, structured logging and disposable PostgreSQL regression tests including credential rotation, tenant security and fail-closed errors.
- [ ] Record actual files, source branch/worktree evidence, validation results and Completion Report; stop at Review.

## Interfaces / Contracts

- `API-001` server-only typed configuration reader; no duplicate Prisma key lookup, envelope decoder or decryption logic at individual consumers.
- `ADMIN-002` owns sealed configuration writes and authorised secret reveal/edit; existing `@modainteract/moda-interact-shared/security/credentials/node` owns cryptographic implementations.
- Existing Woo and Merchant route/auth contracts remain authoritative; add no public generic configuration endpoint.
- `@modainteract/moda-interact-shared/logging` owns generic structured logging; API-002 uses the existing API logger and owns only domain event names, operation identifiers and bounded outcome/reason metadata.

## Dependencies

- `ARCH-043-API-001`
- `ARCH-043-ADMIN-002`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Merchant Knowledge read, upload intent/finalisation and both size limits use the validated `merchant.knowledge.r2` six-field sealed record, without any remaining `merchantKnowledge.upload` consumer; existing API-017 lifecycle tests remain green.
- [ ] Woo REST-read start/callback/return authentication and key rotation work without process restart or configuration cache; invalid database keyring does not enable insecure behaviour.
- [ ] Configuration read success/failure emits `api.platform_configuration.read` through the existing Shared logger; tests verify bounded key/operation/outcome/reason metadata, no credential or ciphertext leakage, and no newly introduced generic logger.
- [ ] No private Meta endpoint, Messaging integration or Messaging environment credential cutover is implemented; `messaging.meta` remains an Admin-managed purpose with no new API consumer.
- [ ] Missing/invalid configuration fails closed without falling back to retired env values; health/live and readiness remain unaffected when their own dependencies are healthy. Logging failures must not change business operation outcomes.
- [ ] No unrelated source or `_index.md` files modified; task worktree and start-of-attempt evidence present.

## Validation

- [ ] API-017 Merchant Knowledge focused and disposable PostgreSQL upload tests
- [ ] Woo REST-read authorization callback/rotation/locale tests
- [ ] Shared logging regression tests for read success/failure, lazy composition, bounded metadata, failure isolation and sensitive-value redaction
- [ ] End-to-end API integration against database with changed settings visible on the next operation
- [ ] Full API typecheck, lint, unit tests and production build
- [ ] `git diff --check`

## Stop Condition

After the scoped implementation is validated, fill the Completion Report, set status `review`, return to `moda_architect` and **STOP**. Do not implement Gateway, Messaging or System Test.

## Implementation Notes

- Use existing API handler composition in `src/index.ts`, `src/composition/routes.ts` and `src/composition/woocommerce.ts` without bypassing route auth.
- Provider and cryptographic operations must not run inside a PostgreSQL transaction purely to align secrets; use explicit per-operation snapshots where required.
- The private Meta route and Gateway identity scheme are deliberately removed from this task because no Messaging or other approved consumer needs them. Do not implement them as speculative follow-up work.
- Physical parent and implementation worktree isolation with launcher synchronisation evidence is required; no commits or pushes are made by this task definition.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-18T15:16:59Z. Attempt 0 review history is preserved below.

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
