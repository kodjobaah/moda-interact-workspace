---
id: ARCH-043-API-001
architecture_id: ARCH-043
title: Implement reusable hosted API platform configuration service
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 25
executor: developer
claimed_at: 2026-10-18T11:51:25Z
attempt: 2
depends_on:
  - ARCH-043-DATABASE-001
enables:
  - ARCH-043-API-002
created: 2026-10-17
updated: 2026-10-18
---

# Implement reusable hosted API platform configuration service

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Storage and sealed-secret envelope/AAD mechanism: `docs/architecture/ARCH-043-configuration-schema-review.md`, **subject to the authoritative 2026-10-18 ARCH-043 PostgreSQL key registry**. Where those older documents conflict with the registry, the registry wins. Do not implement legacy key aliases.
- The authoritative keys owned by this API reader are exactly `merchant.knowledge.r2`, `commerce.connectionKeys` and `messaging.meta`.
- Repository: `moda-interact-api`; logical owner `moda_api`; coordinator `moda_architect`.
- Database dependency `ARCH-043-DATABASE-001` is `complete` in the 2026-10-17 21:06 supplied snapshot. A live task launcher must still re-gate against authoritative task worktrees before claiming.

### Developer Ownership Amendment

On 2026-10-17, `/moda_developer_create ARCH-043-API-001` was invoked to take over this ready task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_api`, repository ownership, scope, dependencies and acceptance criteria are unchanged. Attempt 1 is claimed by the developer.

## Objective

Implement **one reusable, read-only API configuration service** for the three ARCH-043 API-owned configuration purposes, without switching any existing business routes or callers.

## Context

- `src/composition/merchant.ts` and `src/merchant/merchant-knowledge/upload-r2.ts` currently read Knowledge upload limits and R2 endpoint/bucket from environment.
- `src/woocommerce/rest-read/config.ts` currently parses the Commerce keyring and active key from environment; `src/runtime-config.ts` constructs it at startup.
- There is no current API private Meta secret resolver. `messaging.meta` remains managed in PostgreSQL without an ARCH-043 Messaging consumer.
- Existing ARCH-039 Shared Node-only functions already implement authenticated encryption/decryption and credential keyring validation. No new Shared task or crypto implementation is authorised.
- **Authoritative registry correction (2026-10-18):** `merchantKnowledge.upload` is NOT a supported key. Its replacement, `merchant.knowledge.r2`, maps `MERCHANT_KNOWLEDGE_R2_ENDPOINT`, `MERCHANT_KNOWLEDGE_R2_BUCKET`, `MERCHANT_KNOWLEDGE_R2_ACCESS_KEY_ID`, `MERCHANT_KNOWLEDGE_R2_SECRET_ACCESS_KEY`, `MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES`, and `MERCHANT_KNOWLEDGE_MAX_XLSX_UNCOMPRESSED_BYTES`. Both R2 credentials are in the registered purpose and must be protected as secrets rather than persisted as cleartext policy fields. The old schema-review and Admin contracts need separate architect-owned reconciliation; the API implementation must not create a fallback alias.
- The accepted D001 SQL schema in the supplied snapshot has sealed-only/check-and-audit restrictions for five named secret keys but **does not yet include `merchant.knowledge.r2`**. Its acceptance is not evidence that R2 credentials are protected at the database boundary. This is a separate Database/Admin correction gate before credential-writing or production cutover; it must not be silently fixed in this API reader task.

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
  requireMerchantKnowledgeR2Configuration(): Promise<MerchantKnowledgeR2Configuration>;
  requireCommerceConnectionSecurity(): Promise<CommerceConnectionSecurity>;
  requireMetaWebhookSecrets(): Promise<MetaWebhookSecrets>;
}
```

**`merchant.knowledge.r2` (canonical; sealed):** Look up **only** this key using the trusted `(environment,key)` unique index. Treat its configured value as an authenticated, sealed application-secret envelope, or as the strict disabled tombstone; **never** accept an unsealed policy object, the obsolete `merchantKnowledge.upload` key or an environment-variable fallback. Verify the exact ARCH-043 envelope shape, row version and AAD before decryption using existing ARCH-039 Shared crypto. After unsealing, validate a closed, purpose-specific six-field plaintext object:

```ts
{
  r2Endpoint: string;             // MERCHANT_KNOWLEDGE_R2_ENDPOINT
  r2Bucket: string;               // MERCHANT_KNOWLEDGE_R2_BUCKET
  r2AccessKeyId: string;          // MERCHANT_KNOWLEDGE_R2_ACCESS_KEY_ID
  r2SecretAccessKey: string;      // MERCHANT_KNOWLEDGE_R2_SECRET_ACCESS_KEY
  maxUploadBytes: number;         // MERCHANT_KNOWLEDGE_MAX_UPLOAD_BYTES
  maxXlsxUncompressedBytes: number; // MERCHANT_KNOWLEDGE_MAX_XLSX_UNCOMPRESSED_BYTES
}
```

The six camelCase names above are the **API-001 proposed plaintext field mapping** used by the current implementation candidate; the user-approved registry fixes the key/environment mappings but did not itself specify JSON member names. Freeze this shape with the architect/Admin writer **before configuration is written or consumers are switched**. Do not invent or silently accept an alternative shape.

- `readMerchantKnowledgeUploadPolicy()` must expose **only** `maxUploadBytes`, `maxXlsxUncompressedBytes`, `r2Endpoint` and `r2Bucket` to a trusted policy caller; it must not leak either credential. It may use the same internal purpose-scoped reader as the secret accessor, but each *public service method invocation* performs a fresh DB read.
- `requireMerchantKnowledgeR2Configuration()` supplies both access credentials **only to trusted server-side code**; never expose this object through an HTTP endpoint, ordinary API JSON, a browser bundle or logs. API-002 owns consumer wiring and access authorisation.
- Require HTTPS, the API's existing Cloudflare R2 endpoint-host/SSRF restrictions and bucket-name validation, and existing code-enforced transport and XLSX limits (including the current 25 MiB upload hard ceiling). Policy fields must be validated *after unsealing*. Endpoint/bucket remain **editable** in the Admin writer; no hardcoded location lock or object relocation belongs here.
- The unseal root/keyring is externally provisioned, purpose-scoped and never read from the configuration table itself; wrong or missing wrapping keys fail closed. Credential rotation is independent of R2 location editing. No raw secrets appear in exceptions, structured logs or tests' failure output.

**`commerce.connectionKeys`:** Query the sealed record, reconstruct only the documented `CredentialEnvelope`, construct exact AAD bytes `JSON.stringify(["moda-platform-config-v1", environment, key, record.version, 1])` after validation, decrypt with published ARCH-039 `decryptCredential`, then validate canonical `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` using existing Shared `parseCredentialKeyring` / `resolveActiveCredentialKey`. Preserve prior key IDs to decrypt existing Woo REST-read grants. The authoritative registry **also** maps `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` to this key: validate and surface it as a purpose-specific optional/required field according to the consuming operation, without weakening fail-closed protection for a consumer that requires it. Return typed security material to trusted server code only, never an HTTP response.

**`messaging.meta`:** Use the identical sealed-envelope/AAD validation with *this* key and its row version; validate the purpose-specific plaintext fields `META_APP_SECRET` and `WHATSAPP_VERIFY_TOKEN`. Provide the typed result to a trusted server caller only; do not provide a generic `getSecret(key)` public API. No caller or network endpoint in this task.

## Out of Scope

- No edits to `src/index.ts`, `src/runtime-config.ts`, `src/composition/*`, Woo REST-read services/routes, merchant upload/read services/routes or Meta private HTTP routes.
- No Admin editor, secret writer/import, service identity provisioning, Gateway changes, Messaging implementation or environment-variable removal.
- No R2 object relocation/migration, new database models or SQL constraints, new Shared publication or configuration caching. The missing D001 sealed-key/audit constraints for `merchant.knowledge.r2` are **reported to the architect**, not silently implemented by `moda_api`.
- No modifications to `docs/architecture/ARCH-043-*`, `docs/decisions/database/ARCH-043/*` or `docs/decisions/admin/ARCH-043/*` from this repository-owned task; those require their respective owners and review.
- No `_index.md` edits or follow-on task execution.

## Requirements

- Resolve `environment` from the deployment's trusted server configuration, never from a tenant, API request or public header. Query the precise `(environment,key)` unique record; never fall back across environments or to old env values after cutover.
- **No configuration caching:** execute a fresh PostgreSQL read for every method call/operation. No Redis, process-local snapshots, TTL, background refresher or last-known-good fallback; a caller may reuse its result within one operation only.
- Fail closed for missing rows, wrong JSON shapes, disabled tombstones, unsupported schema versions, wrong envelope algorithm, invalid AAD, missing root/decryption keys or a failed database read. No fallback to `merchantKnowledge.upload`, a different environment or old environment variables. Never log secrets, ciphertext, nonces, tags, keyrings or decrypted payloads; only purpose-scoped trusted server return values may contain unsealed security material.
- Validate a sealed row's precise closed-shape envelope (`kind: sealed`, `schemaVersion: 1`, `algorithm: AES-256-GCM`, wrapping key ID, nonce, ciphertext, auth tag), or exactly `{ "kind": "disabled", "schemaVersion": 1 }`. Use the **row's positive version** and exact `JSON.stringify(["moda-platform-config-v1", environment, key, record.version, 1])` AAD bytes for all three sealed purposes. A tombstone never becomes a default configuration.
- For `merchant.knowledge.r2`, treat *all six* plaintext fields as one sealed purpose, not a separately persisted plaintext policy plus two environment-held credentials. Typed read-only policy projection must not expose access credentials; secret projection must be server-only.
- Use exact frozen ARCH-043 AAD bytes and the existing ARCH-039 security package. Support old key IDs in the unwrapped Commerce keyring for previously persisted grants. Test key rotation with old/new key preservation.
- Keep methods dependency-injectable for tests. Do not force a DB read during unrelated API health probes or module import.
- Existing structured logging must use `@modainteract/moda-interact-shared/logging`, with bounded safe reason codes and no secret material.

## Work Items

- [x] Implement read-only, environment-scoped PostgreSQL repository.
- [ ] Implement canonical `merchant.knowledge.r2` sealed-purpose read, exact six-field plaintext validation, API upload/XLSX ceilings and editable R2 endpoint/bucket validation; reconcile the proposed R2 JSON field names with the Admin writer contract before any data write or consumer cutover.
- [x] Implement separate policy-only and trusted-server R2 credential projections without exposing credentials in the policy result or over HTTP.
- [x] Implement Commerce keyring sealed-envelope/AAD verification, decryption and canonical keyring validation.
- [x] Implement Meta webhook secret purpose-specific sealed-envelope reader, without HTTP exposure.
- [ ] Cover negative paths, cross-environment denial, per-operation fresh reads, credential tampering, R2 credential non-disclosure and key rotation; add R2 disabled/malformed/missing-or-wrong-root cases and a regression that a legacy-only `merchantKnowledge.upload` row is **not** accepted.
- [x] Record the D001/Admin sealed-key/audit contract gap as an explicit architecture dependency before consumer cutover, without editing another owner's files.
- [x] Record changed files, launcher-resolved worktree isolation/synchronisation, tests and the Completion Report.

## Interfaces / Contracts

- `PlatformConfiguration` unique `(environment,key)`, JSON value and row version from `ARCH-043-DATABASE-001`.
- **Authoritative 2026-10-18 registry keys:** `merchant.knowledge.r2`, `commerce.connectionKeys` and `messaging.meta`. The registry supersedes `merchantKnowledge.upload` in older ARCH-043 documents; this task MUST NOT emit or query that obsolete key.
- Common `kind: sealed`/disabled envelope and frozen AAD from `docs/architecture/ARCH-043-configuration-schema-review.md` apply to **all three** keys; the precise R2 six-field decrypted payload shown in Scope is a **proposed reader/writer shape requiring an architect-owned Admin/Database reconciliation** before activation. Do not claim the old schema-review R2 plaintext policy shape remains approved.
- D001 currently omits `merchant.knowledge.r2` from its database-enforced sealed-secret and redacted-audit allowlists. This service must reject plaintext even while SQL can presently accept it; require separate Database correction and Admin writer alignment before enabling a writer or switching callers. Do not mark that cross-repository risk solved by reader-only unit tests.
- `commerce.connectionKeys` maps `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`; `messaging.meta` maps `META_APP_SECRET` and `WHATSAPP_VERIFY_TOKEN`. No new Shared contracts.
- Existing `@modainteract/moda-interact-shared/security/credentials/node` is the sole cryptographic/keyring implementation.
- Only server-side callers may obtain decrypted secret return values; `API-002` owns caller authorisation and private route exposure.

## Dependencies

- `ARCH-043-DATABASE-001` (Complete in supplied snapshot; re-check before execution)

## Enables

- `ARCH-043-API-002`

## Acceptance Criteria

- [x] The three canonical purpose readers (four methods, with separate R2 policy/credential projections) work against actual `PlatformConfiguration` rows in disposable PostgreSQL; **no** `merchantKnowledge.upload` key read is performed.
- [ ] A plaintext `merchant.knowledge.r2` object, legacy-only `merchantKnowledge.upload` row, disabled tombstone, malformed sealed envelope and missing/wrong wrapping key all fail closed. R2 credentials never appear in the policy projection or error/log output.
- [x] A second call observes a changed database value without process restart or cache invalidation.
- [ ] Wrong environment, missing/malformed/disabled rows, altered AAD or ciphertext and incorrect unseal key fail closed without secret-bearing diagnostics.
- [ ] Merchant Knowledge endpoint and bucket remain validated and editable; both size ceilings remain code-enforced. All six mapped fields are validated after authenticated decryption and the trusted-server R2 credential projection is not exposed as HTTP JSON.
- [x] Explicitly report the still-missing `merchant.knowledge.r2` SQL sealed-envelope/audit-redaction enforcement and older Admin/schema-review key references as cross-repository cutover blockers rather than treating reader tests as proof of end-to-end safety.
- [x] Commerce keyring reader preserves old key IDs and existing ARCH-039 keyring parsing compatibility.
- [x] No pre-existing API consumer is switched, and no private Meta route is exposed.
- [x] Source changes are confined to `moda-interact-api` plus its assigned task Completion Report; no `_index.md` files.

## Validation

- [ ] Focused unit tests for all four methods, sealed R2 field validation/projection, legacy-key rejection, R2 disabled/malformed/missing-or-wrong-root vectors, tamper/negative vectors and new-value-per-call behaviour
- [ ] Disposable PostgreSQL service integration with real D001 migration (environment isolation, R2 credential protection/read, key rotation, R2 malformed/disabled rows, and missing policy); fail test command on skipped or incomplete execution
- [x] API repository typecheck, lint and build
- [x] `git diff --check`

## Stop Condition

After the work items and required validation are complete, update the Completion Report, set status `review`, return to `moda_architect` and **STOP**. Do not implement the consumers in API-002.

## Implementation Notes

- Prefer repository-standard TypeScript modules and `.js` import specifiers. Resolve Prisma delegate naming from the actual generated client.
- No feature-specific copy of `encryptCredential`/`decryptCredential`, no network secrets service and no background revalidation loop.
- Align the API implementation candidate with the authoritative registry before acceptance. Do not imply the old `merchantKnowledge.upload` task text or any plaintext Knowledge configuration remains authoritative.
- **Cross-repository prerequisite, not API-001 scope:** moda_architect must arrange D001/Database SQL secret-key and audit-redaction enforcement and Admin writer/schema-review alignment for `merchant.knowledge.r2` before writing the credentials or cutting API consumers over. Preserve this task's existing developer claim/attempt history; do not silently mark the downstream work Complete.
- Capture actual launcher-prepared canonical parent and implementation worktree evidence before implementation.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-18T11:51:25Z. Attempt 1 review history is preserved below.

### Files Changed

`moda-interact-api/package.json`; `scripts/run-arch043-platform-configuration-postgres.mjs`; `src/platform-configuration/contracts.ts`; `src/platform-configuration/errors.ts`; `src/platform-configuration/repository.ts`; `src/platform-configuration/service.ts`; `tests/integration/platform-configuration/service.postgres.test.ts`; `tests/unit/http/integration-runner-registration.test.ts`; `tests/unit/platform-configuration/service.test.ts`.

### Work Completed

Implemented fresh trusted-environment reads for `merchant.knowledge.r2`, `commerce.connectionKeys` and `messaging.meta`; strict sealed-envelope/AAD validation; separate R2 policy-only and trusted-server credential projections; Commerce keyring/HMAC validation and old-key retention; Meta-purpose typed results; and unit/PostgreSQL tests. No existing API consumer or HTTP route was switched.

### Validation Results

Passed focused unit tests: `./node_modules/.bin/tsx --test tests/unit/platform-configuration/service.test.ts` (4/4).

Passed disposable PostgreSQL runner: `node scripts/run-arch043-platform-configuration-postgres.mjs` (real D001 migrations deployed; 4/4 integration tests passed; no tests skipped; disposable container cleanup passed).

Passed `npm run typecheck`, `npm run lint`, `npm run build`, and `git diff --check origin/main...HEAD` from the canonical API implementation worktree.

These successful checks do not satisfy the missing R2-specific regressions listed under Unresolved Issues and in the Changes Requested review.

### Deviations

The implementation report was stale after the task's contract amendment. The implementation contains service and test changes only; no consumer wiring, route or deployment changes were made, and no production configuration write or cutover was attempted. The proposed six-field R2 names differ from ADMIN-002's current payload names.

### Assumptions

No additional implementation assumptions. The API R2 payload shape remains a proposal until confirmed by the architect/Admin owner.

### Unresolved Issues

The API expects `r2Endpoint`, `r2Bucket`, `r2AccessKeyId` and `r2SecretAccessKey`, while ADMIN-002 documents `endpoint`, `bucket`, `accessKeyId` and `secretAccessKey`. Freeze the shared shape with the architect/Admin owner and add an interoperability fixture before activation. D001 does not yet enforce this key as sealed-only or guarantee its audit redaction, and older Admin/schema-review references still name `merchantKnowledge.upload`; both remain cutover blockers.

### Architectural Concerns

The R2 plaintext field mapping must be reconciled with ADMIN-002 before activation. Database sealed-only/audit-redaction enforcement and removal of stale Admin/schema references are cross-repository prerequisites, not API-001 implementation changes.

## Architect Review

### Review Status

Pending

### Review Notes

No architect acceptance has been recorded. Developer Self-Review returned Attempt 1 as Changes Requested; the listed contract and regression-test corrections remain open.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not assessed.

### Follow-up

None

### Physical Worktree Isolation and Synchronization
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-API-001`, `task/ARCH-043-API-001`
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-API-001`, `task/ARCH-043-API-001`
- Shared workspace checkout switched/mutated for task work: no; existing ARCH-043 staged changes were preserved
- Shared API source checkout switched/mutated for task work: no
- Another task worktree reused: no
- Parent remote task branch fast-forwarded: not applicable; no remote task branch existed at preparation
- Parent `origin/main` incorporated: already current at `0d5b43bc4fd801fd627a108c7df90ded9e0f13de`
- Implementation remote task branch fast-forwarded: not applicable; no remote task branch existed at preparation
- Implementation `origin/main` incorporated: already current at `28a806db24e8b4ef0ee3061e4f00b0fcdadcfa68`
- Recursive implementation submodules: initialized and verified against recorded gitlinks; `database` is at `aa3fd024db3a1484f72f8033b87f56ad27f4640d`

## Physical Worktree Isolation and Synchronization at Self-Review

- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-API-001`, `task/ARCH-043-API-001`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-API-001`, `task/ARCH-043-API-001`.
- Implementation branch commit: `e6a428e0e7415dfaf69f8ff0f27d670120644f30`, equal to `origin/task/ARCH-043-API-001`; implementation worktree clean.
- Parent task worktree was clean and synchronized with its remote before this review update; this task-record change is the only intended parent worktree modification.
- The primary-workspace route-only resolver found two `ARCH-043-API-001` definitions. The selected parent task branch contains the deduplication change, but the primary `main` checkout still needs that architecture reconciliation before a future launcher invocation can route this ID unambiguously.
- No shared/default checkout, other task worktree, submodule pointer or `_index.md` was changed by this review.

## Developer Self-Review - Changes Requested (Attempt 1, 2026-10-18)

The implementation passes the focused unit suite (4/4), disposable PostgreSQL suite (4/4), typecheck, lint, production build and `git diff --check`. The review does not pass because the amended acceptance contract has unresolved coverage and cross-service shape issues:

- Freeze the R2 six-field decrypted shape with the architect/Admin owner. The API currently validates `r2Endpoint`, `r2Bucket`, `r2AccessKeyId` and `r2SecretAccessKey`, while ADMIN-002 documents `endpoint`, `bucket`, `accessKeyId` and `secretAccessKey`. Add an approved deterministic interoperability fixture or implement the approved shape before any configuration write or consumer cutover.
- Add a legacy-only `merchantKnowledge.upload` regression proving there is no alias, fallback query or environment fallback.
- Add focused R2 tests for disabled rows and missing/wrong wrapping keys; extend the real PostgreSQL harness for malformed and disabled R2 envelopes and secret-free policy projection/diagnostics.
- Preserve the documented cutover blockers: D001 lacks R2 sealed-only/audit-redaction enforcement, and older Admin/schema-review references still use the retired key. Do not change those other owners' files here.

Attempt 1 remains unchanged. The task is returned to `ready` with `executor` and `claimed_at` cleared; do not create Attempt 2 in this review. No source implementation changes were made during review.
