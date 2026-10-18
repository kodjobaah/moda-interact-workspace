---
id: ARCH-043-API-001
architecture_id: ARCH-043
title: Implement reusable hosted API platform configuration service
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-043-DATABASE-001
enables:
  - ARCH-043-API-002
created: 2026-10-17
updated: 2026-10-17
---

# Implement reusable hosted API platform configuration service

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Storage and frozen sealed-secret contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository: `moda-interact-api`; logical owner `moda_api`; coordinator `moda_architect`.
- Database dependency `ARCH-043-DATABASE-001` is `complete` in the 2026-10-17 21:06 supplied snapshot. A live task launcher must still re-gate against authoritative task worktrees before claiming.

## Objective

Implement **one reusable, read-only API configuration service** for the three ARCH-043 API-owned configuration purposes, without switching any existing business routes or callers.

## Context

- `src/composition/merchant.ts` and `src/merchant/merchant-knowledge/upload-r2.ts` currently read Knowledge upload limits and R2 endpoint/bucket from environment.
- `src/woocommerce/rest-read/config.ts` currently parses the Commerce keyring and active key from environment; `src/runtime-config.ts` constructs it at startup.
- There is no current API private Meta secret resolver. `messaging.meta` remains managed in PostgreSQL without an ARCH-043 Messaging consumer.
- Existing ARCH-039 Shared Node-only functions already implement authenticated encryption/decryption and credential keyring validation. No new Shared task or crypto implementation is authorised.

## Scope

Create small, modular server-only files within `moda-interact-api/src/platform-configuration/`, preferably:

- `repository.ts`: indexed `PlatformConfiguration.findUnique({where:{environment_key:{environment,key}}})` lookup with read-only Prisma dependency injection. Never query `PlatformConfigurationAudit` for runtime values.
- `contracts.ts`: approved three keys, strict decoding and narrow typed outputs; don't duplicate generic Shared cryptographic primitives.
- `service.ts`: per-operation API methods with caller-injected Prisma access, trusted deployment environment and externally provisioned unseal/keyring dependency.
- `errors.ts`: explicit safe error codes for absent/disabled/invalid configuration, unseal failure and database unavailability.
- Focused unit tests and disposable PostgreSQL tests for the service only.

Export a cohesive interface (names may follow local repository style):

```ts
interface ApiPlatformConfigurationReader {
  readMerchantKnowledgeUploadPolicy(): Promise<MerchantKnowledgeUploadPolicy>;
  requireCommerceConnectionSecurity(): Promise<CommerceConnectionSecurity>;
  requireMetaWebhookSecrets(): Promise<MetaWebhookSecrets>;
}
```

**`merchantKnowledge.upload`:** Return validated `maxUploadBytes`, `maxXlsxUncompressedBytes`, `r2Endpoint` and `r2Bucket`. Require HTTPS and existing R2 endpoint host/bucket safety validation; enforce existing API absolute size ceilings. Endpoint and bucket **remain editable** in Admin. Never bake in a lock or implement storage relocation: other tasks own existing-asset/in-flight handling. Return no R2 secret access credentials; they retain the existing external source.

**`commerce.connectionKeys`:** Query the sealed record, reconstruct only the documented `CredentialEnvelope`, construct exact AAD bytes `JSON.stringify(["moda-platform-config-v1", environment, key, record.version, 1])` after validation, decrypt with published ARCH-039 `decryptCredential`, then validate canonical `COMMERCE_CONNECTION_KEYS_JSON` and active key using existing Shared `parseCredentialKeyring` / `resolveActiveCredentialKey`. Preserve legacy ciphertext/key-ID interpretation for Woo REST-read grants. Return typed keyring to trusted server code only, never an HTTP response.

**`messaging.meta`:** Use the identical sealed-envelope/AAD validation with *this* key and its row version; validate the purpose-specific plaintext fields `META_APP_SECRET` and `WHATSAPP_VERIFY_TOKEN`. Provide the typed result to a trusted server caller only; do not provide a generic `getSecret(key)` public API. No caller or network endpoint in this task.

## Out of Scope

- No edits to `src/index.ts`, `src/runtime-config.ts`, `src/composition/*`, Woo REST-read services/routes, merchant upload/read services/routes or Meta private HTTP routes.
- No Admin editor, secret writer/import, service identity provisioning, Gateway changes, Messaging implementation or environment-variable removal.
- No R2 object relocation/migration, new database models, new Shared publication or configuration caching.
- No `_index.md` edits or follow-on task execution.

## Requirements

- Resolve `environment` from the deployment's trusted server configuration, never from a tenant, API request or public header. Query the precise `(environment,key)` unique record; never fall back across environments or to old env values after cutover.
- **No configuration caching:** execute a fresh PostgreSQL read for every method call/operation. No Redis, process-local snapshots, TTL, background refresher or last-known-good fallback; a caller may reuse its result within one operation only.
- Fail closed for missing rows, wrong JSON shapes, disabled tombstones, unsupported schema versions, wrong envelope algorithm, invalid AAD, missing root/decryption keys or a failed database read. Never log or return secrets, ciphertext, nonces, tags, keyrings or decrypted payloads.
- Use exact frozen ARCH-043 AAD bytes and the existing ARCH-039 security package. Support old key IDs in the unwrapped Commerce keyring for previously persisted grants. Test key rotation with old/new key preservation.
- Keep methods dependency-injectable for tests. Do not force a DB read during unrelated API health probes or module import.
- Existing structured logging must use `@modainteract/moda-interact-shared/logging`, with bounded safe reason codes and no secret material.

## Work Items

- [ ] Implement read-only, environment-scoped PostgreSQL repository.
- [ ] Implement typed Knowledge upload policy read/validation, including editable R2 endpoint/bucket.
- [ ] Implement Commerce keyring sealed-envelope/AAD verification, decryption and canonical keyring validation.
- [ ] Implement Meta webhook secret purpose-specific sealed-envelope reader, without HTTP exposure.
- [ ] Cover negative paths, cross-environment denial, per-operation fresh reads, credential tampering and key rotation.
- [ ] Record changed files, launcher-resolved worktree isolation/synchronisation, tests and the Completion Report.

## Interfaces / Contracts

- `PlatformConfiguration` unique `(environment,key)`, JSON value and row version from `ARCH-043-DATABASE-001`.
- Frozen `commerce.connectionKeys`, `messaging.meta` and `merchantKnowledge.upload` formats in `docs/architecture/ARCH-043-configuration-schema-review.md`; no new Shared contracts.
- Existing `@modainteract/moda-interact-shared/security/credentials/node` is the sole cryptographic/keyring implementation.
- Only server-side callers may obtain decrypted secret return values; `API-002` owns caller authorisation and private route exposure.

## Dependencies

- `ARCH-043-DATABASE-001` (Complete in supplied snapshot; re-check before execution)

## Enables

- `ARCH-043-API-002`

## Acceptance Criteria

- [ ] All three typed methods work against actual `PlatformConfiguration` rows in disposable PostgreSQL.
- [ ] A second call observes a changed database value without process restart or cache invalidation.
- [ ] Wrong environment, missing/malformed/disabled rows, altered AAD or ciphertext and incorrect unseal key fail closed without secret-bearing diagnostics.
- [ ] Merchant Knowledge endpoint and bucket remain validated and editable; size ceilings remain code-enforced.
- [ ] Commerce keyring reader preserves old key IDs and existing ARCH-039 keyring parsing compatibility.
- [ ] No pre-existing API consumer is switched, and no private Meta route is exposed.
- [ ] Source changes are confined to `moda-interact-api` plus its assigned task Completion Report; no `_index.md` files.

## Validation

- [ ] Focused unit tests for each service method, tamper/negative vectors and new-value-per-call behaviour
- [ ] Disposable PostgreSQL service integration (environment isolation, rotation and missing policy)
- [ ] API repository typecheck, lint and build
- [ ] `git diff --check`

## Stop Condition

After the work items and required validation are complete, update the Completion Report, set status `review`, return to `moda_architect` and **STOP**. Do not implement the consumers in API-002.

## Implementation Notes

- Prefer repository-standard TypeScript modules and `.js` import specifiers. Resolve Prisma delegate naming from the actual generated client.
- No feature-specific copy of `encryptCredential`/`decryptCredential`, no network secrets service and no background revalidation loop.
- Capture actual launcher-prepared canonical parent and implementation worktree evidence before implementation.

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
