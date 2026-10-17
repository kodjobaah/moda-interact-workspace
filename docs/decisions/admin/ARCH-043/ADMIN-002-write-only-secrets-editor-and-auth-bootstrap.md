---
id: ARCH-043-ADMIN-002
architecture_id: ARCH-043
title: Extend editor for write-only secrets and safe Admin authentication bootstrap
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-17T17:00:15Z
attempt: 1
depends_on:
  - ARCH-043-DATABASE-001
  - ARCH-043-ADMIN-001
enables:
  - ARCH-043-GATEWAY-001
  - ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: 2026-10-17
---
# Write-only Secret Contracts and Admin Auth Bootstrap

## Architecture

- `ARCH-043` parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Exact sealed-envelope, AAD and key-purpose rules: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Builds on the reusable field renderer, policy registry, privileged CAS/audit service and page from `ARCH-043-ADMIN-001`.
- Current source: `src/auth.ts` instantiates `NextAuth` at module load; `src/lib/auth/environment.ts` requires `AUTH_SECRET`, `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET`, `AUTH_URL`; `src/lib/admin/shared-credential-keyring.ts` loads ARCH-039 keyring from environment. Do not assume Auth.js accepts an asynchronous key load at module construction.
- Materialized on the canonical parent task branch; launcher-resolved paths remain authoritative.

## Developer Ownership Amendment

On 2026-10-17, `/moda_developer_create ARCH-043-ADMIN-002` was invoked to take over this ready task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_admin`, repository ownership, execution ownership, active claim and task dependencies are unchanged. The eight-purpose scope and validation requirements are extended by this architectural amendment. The canonical launcher will create/reuse the implementation worktree, recheck dependencies and record Attempt 1 separately.

## Objective

Extend the **same** contract-driven Admin editor with eight write-only encrypted configuration-purpose contracts and a verified initial import path; securely bootstrap Admin's own authentication from the stored `auth.admin` record before removing legacy secret environment variables.

## Context

ADMIN-001 owns the reusable form framework and generic CAS/audit service; ADMIN-002 must reuse them, **not** create a second independent secrets form or another generic configuration engine. This same task retains Admin Auth.js cutover; no separate Admin auth task is authorised. Secret encryption reuses the already published ARCH-039 Node-only API. Initial import may use the existing *environment-backed* authenticated SUPER_ADMIN session. Only the DB-only cutover must avoid depending on authentication credentials that have not yet been imported and verified.

## Scope

1. Register all eight **sealed-purpose** contracts on the existing Admin registry and render them with the generic editor's `secret` field capability, including configured/unconfigured status and explicit Set/Rotate/Revoke actions.
2. Add a strictly authorised *server-only secret write path* on top of the same CAS/audit repository. Validate purposes and plaintext shapes, seal before DB persistence, write redacted audit metadata; never return stored envelopes to browser.
3. Provide a verified initial import for `auth.admin` while environment-backed Auth.js login is still available: an existing active `SUPER_ADMIN` may use the authenticated server-side editor to import the sealed record. If CLI-based bootstrap/recovery is needed without a browser session, require independently authenticated trusted deployment/operator identity and protected stdin; do not accept a bare `--actorId` as proof of authority. Do not require such CLI if the authenticated import path meets the verified cutover prerequisite.
4. Implement and validate, **within ADMIN-002**, a supported Admin Auth.js **load-before-use** mechanism for `auth.admin`, including cold start, missing/bad/wrong-environment secrets, session continuity and deliberate rotation.
5. Manage `commerce.bootstrap` as a sealed `{adminEmail}` selector; `merchant.knowledge.r2` as one sealed six-field JSON object containing `{endpoint,bucket,accessKeyId,secretAccessKey,maxUploadBytes,maxXlsxUncompressedBytes}` with integer limits; and `woocommerce.auth` as a sealed `{consumerKey,consumerSecret}` for a **platform-owned** integration only. Do not replace merchant-specific WooCommerce REST grants. Preserve R2 SSRF, bucket and size guards. The legacy `merchantKnowledge.upload` policy becomes non-authoritative only after its consumers migrate.
6. Tests for secret integrity/AAD interoperability, audit redaction, rotation, revocation, migration, eight-purpose registry and Auth.js fail-closed behaviour.

## Out of Scope

- No new Shared cryptography/AAD exports or package publication; no second configuration table, no direct public secret read API, no unauthorised remote bootstrap service, no Messaging/API/Shopify/Commerce consumers, no KMS infrastructure provisioning, no `_index.md` edits.
- Do not rewrite or re-encrypt existing Commerce/OpenRouter/embedding/translation stored credentials or change their established AAD bytes. Do not relocate database connection, service URLs, deployment identity, `AUTH_URL` or the external configuration-unseal root into this table.
- No plaintext/ciphertext in ordinary UI, audit, logs, browser payloads or error messages.

## Requirements

### Current scope clarification (2026-10-17 architect reconciliation)

This is an **amendment to the existing in-progress developer-owned ADMIN-002 task**, not an authorisation to reset its claim or create `ADMIN-003`. The previously written five-purpose/write-only/one-time-auth-bootstrap/DB-only wording below is historical and superseded by the developer-approved behaviour here. Preserve all prior Completion Report and Architect Review evidence.

- Retain the original five encrypted purposes and the three previously added purposes (`commerce.bootstrap`, `merchant.knowledge.r2`, `woocommerce.auth`), then register/validate five additional sealed purposes: `woocommerce.billing`, `shopify.partner`, `shopify.appEvents`, `messaging.sender`, `ai.providers`; count **thirteen** approved purposes plus existing nonsecret policies. `commerce.bootstrap` is validated nonsecret configuration rather than a stored password. Do not duplicate existing embedding models.
- The editor permits explicitly authorised *reveal of already stored credentials* and edit/save, not only write-only inputs. Never put plaintext or ciphertext into revision-audit data, logs, SSR initial props or ordinary policy responses. Audit successful Set/Update/Rotate/Revoke; log Reveal as a redacted structured security event without inventing a new revision.
- For first Set, assign `initial-setup` automatically; normal noncredential updates use `configuration-update`; Rotate requires `scheduled-rotation` or `credential-compromise`, and Revoke requires `decommission` or `credential-compromise`. Preserve CAS, redaction, atomic merging and no double-submit.
- **No authentication bootstrap command or pre-serve secret lookup.** Resolve `auth.admin` only when Auth.js needs authentication configuration: if the environment-scoped database row is absent, use the complete existing `AUTH_SECRET`/`AUTH_GOOGLE_ID`/`AUTH_GOOGLE_SECRET` env bundle; a disabled, invalid, undecryptable row or DB failure is never an absent-row fallback. Keep `AUTH_URL` external and test Auth.js session/key rotation. The Commerce consumer owns the same `auth.commerce` behaviour.
- Preserve development SUPER_ADMIN bypass for secret management **only in development**, as explicitly agreed; production denies synthetic principals. No additional DB schema or ARCH-043 Shared package task. Verify the already-created developer forward migration that removed per-secret-name SQL constraints before enabling the new names.

These explicit requirements supersede contradictory older Work Items, Acceptance Criteria and bootstrap instructions below until the developer updates their checkboxes/Completion Report in the canonical worktree.


### A. Eight sealed-purpose contracts reused by the generic editor

Expose only display-safe metadata and status for:

| Key | Write-only plaintext fields accepted by server | Status displayed to browser |
|---|---|---|
| `commerce.connectionKeys` | `connectionKeysJson` (existing keyring bytes), `activeKeyId`, optional `commandHmacKey` *only when existing runtime requires it* | configured, version, updatedAt; no key bytes or raw JSON |
| `auth.admin` | `authSecret`, `googleClientId`, `googleClientSecret` | configured, version, updatedAt; no token/session contents |
| `auth.commerce` | `authSecret`, `googleClientId`, `googleClientSecret` | configured, version, updatedAt |
| `shopify.oauth` | `apiKey`, `apiSecret` | configured, version, updatedAt |
| `messaging.meta` | `appSecret`, `verifyToken` | configured, version, updatedAt |
| `commerce.bootstrap` | `adminEmail` mapped from `COMMERCE_BOOTSTRAP_ADMIN_EMAIL` | configured, version, updatedAt; no fixed operator email in defaults |
| `merchant.knowledge.r2` | `endpoint`, `bucket`, `accessKeyId`, `secretAccessKey`, `maxUploadBytes`, `maxXlsxUncompressedBytes` | configured, version, updatedAt; sealed as one record |
| `woocommerce.auth` | `consumerKey`, `consumerSecret` (platform-owned credentials only) | configured, version, updatedAt |

- The `commerce.bootstrap.adminEmail` selector is a validated email only, **not** proof of an authenticated operator. Commerce must verify that it resolves to exactly one active `SUPER_ADMIN` when used. Never commit an actual operator address to fixtures/defaults.
- The six R2 fields are one atomic versioned plaintext JSON object sealed before DB persistence. Require validated HTTPS endpoint, bucket, closed credential shape and strict positive JSON integers for upload/uncompressed XLSX limits, retaining application hard caps and SSRF protections. A missing or invalid sealed value must not be replaced with a legacy policy/environment fallback after the cutover.
- `woocommerce.auth` is a platform-wide purpose, not a replacement for existing shop-specific WooCommerce REST grants; do not install a consumer or retire grant credentials without a separately approved integration.
- Map server input fields to the existing environment credential meanings. Each plaintext payload is **closed**: enforce required fields, bounded nonempty strings, allowed optional fields and existing provider-specific format constraints. Validate before encryption; reject unknown fields, invalid combinations, mixed ordinary-settings submissions, unsafe lengths and secret empty-string overwrite.
- `kind:'secret'`, `writeOnly:true` fields always display empty inputs; existing configured state is derived from a small status projection, never decrypted into React state. A blank submitted field means **unchanged only when the operation explicitly supports partial rotation**; otherwise reject missing input. Never use a blank value to delete a secret implicitly.
- A secret mutation requires an authenticated, active `SUPER_ADMIN` principal, explicit `set|rotate|revoke`, version (0 for first set), reason/confirmation and server-controlled environment. There is no separate credential-rotation role in current Admin model; do **not** invent a privilege. Deny development auth bypass for secret mutation or route it through the independently authenticated operator import in dev. Reuse existing Admin rate-limiting protections where present; prevent duplicate submit.
- `ADMIN-002` wires the same generic Editor and handler infrastructure with **distinct server-side secret permission and validation branches**. Never let the non-secret generic mutator persist secret-key input.

### B. Exact encrypted storage compatibility (no new crypto)

- Reuse installed published:

```typescript
import { encryptCredential, decryptCredential, parseCredentialKeyring,
  resolveActiveCredentialKey, type CredentialEnvelope }
  from '@modainteract/moda-interact-shared/security/credentials/node';
```

- A dedicated, independently supplied `MODA_CONFIG_UNSEAL_KEY` or approved KMS-backed unwrap identity is the root for ARCH-043 envelopes; **do not** use the Commerce connection keyring as the key to unwrap itself. Configure an approved key ID/rotation mechanism and validate all unwrap configuration fail closed. PostgreSQL never contains the unwrap root.
- `encryptCredential` returns `CredentialEnvelope` (`keyId`, `nonce`, `ciphertext`, `authTag` as bytes); encode its bytes as **strict canonical base64** before storing the architecture's approved JSON shape:

```json
{"kind":"sealed","schemaVersion":1,"algorithm":"AES-256-GCM",
 "wrappingKeyId":"root-key-id","nonce":"base64","ciphertext":"base64","authTag":"base64"}
```

  The stored `wrappingKeyId` maps to Shared `CredentialEnvelope.keyId`. Readers must reconstruct the exact bytes (nonce 12, authTag 16, ciphertext bounded) and validate key ID/schema/encoding before passing to `decryptCredential`. Do not add a new encryption primitive.
- Canonical AAD **byte convention documented in architecture**, not a new Shared export:

```typescript
const aad = JSON.stringify([
  'moda-platform-config-v1', environment, key, resultingVersion, 1,
]);
```

  Validate canonical `environment`, `key` and positive resulting version before constructing it. The byte-for-byte format, order, UTF-8 encoding and `schemaVersion=1` are frozen across Admin writers and API/Commerce/Background/MCP/Shopify readers. Write deterministic independent vectors for version/key/environment mismatch and tamper. No generic new crypto/AAD library and no SHA/plaintext hash in audit.
- Shared encrypt/decrypt enforces a **maximum plaintext size of 8192 UTF-8 bytes**. Detect and reject oversized `connectionKeysJson` payloads; do not silently truncate or split the secret into incompatible fragments. If actual keyring exceeds this limit, report the concrete blocking gap to `moda_architect` before any migration.
- Compute encrypted AAD using **resultingVersion** (1 on create; expectedVersion+1 on successful rotate). CAS conflicts discard the sealed candidate; never commit a mismatched version/envelope pair.

### C. Secret status, transaction and audit

- Reuse ADMIN-001's trusted environment resolution and `PlatformConfiguration` CAS/audit transaction. Strict server-only writer selects contract by allowlisted purpose. `set` requires absent row and expected 0; `rotate` requires configured row and matching positive version; `revoke` writes `{ "kind":"disabled", "schemaVersion":1 }` with version increment. Re-enable from disabled must be a documented explicit `set`/`rotate` transition preserving monotonic version, never deleting/resetting it.
- Before/after audit for all eight sealed purposes must contain only `{ "redacted": true, "configured": boolean }` (and agreed harmless operation metadata). Never store sealed envelope, ciphertext, nonce, auth tag, plaintext, fingerprints or secret key IDs in audit/history, logs or network responses. No mutation on failed auth, validation, CAS or encryption.
- Browser statuses: `{key, configured, version, updatedAt, updatedBy}`. Do not return `PlatformConfiguration.value` or full Prisma secret row in JSON/Next.js page props. Secret history is metadata-only.
- A caller must not be able to query another environment, inspect a different service's raw secret, or cause authenticated errors to expose provider credentials. Secret updates must use explicit confirmation, reason and non-reentrant/pending form semantics.

### D. Initial auth bootstrap and migration

- Use the existing **environment-backed login** to authenticate an active SUPER_ADMIN who imports `auth.admin` through the Admin server-only secret writer before the DB-only cutover. An optional out-of-band CLI for disaster recovery may be provided only with a separate architecture-approved deployment/operator authentication mechanism and a verified operator actor ID; *a freeform `--actorId` option alone is not authentication*. A CLI is **not** a prerequisite when the authenticated transitional web import has been verified.
- For an optional CLI, input secrets via protected stdin/file descriptor or approved secrets manager interface; **never CLI arguments** (shell history/process listings), committed fixtures, stdout/stderr or structured logs. Validate the selected environment, expected version and payload; use the same sealing writer/CAS/audit as browser rotation. Repeated bootstrap with same expected revision fails safely; no creation of a development secret in production. Import all required `auth.admin` fields before enabling database-backed login.
- The current `src/auth.ts` calls `NextAuth(...)` at module initialization. Verify the installed Auth.js/Next.js runtime supports the intended asynchronous secret resolution lifecycle; **do not** introduce an unproven async module initialiser or unauthenticated auth callback. Acceptable implementation: a verified bounded startup preparation phase that loads/validates the sealed secret before registering/serving Auth.js, or an Auth.js-supported dynamic configuration factory with explicit before-request secret loading and fail-closed behaviour. If neither works with the deployed runtime, return the dependency to `moda_architect` instead of silently keeping or weakening the bootstrap.
- Validate `AUTH_URL` remains independently configured as routing/bootstrap metadata. Existing Google subject-binding/PlatformAdmin allowlist still applies; no new development bypass in hosted environments.
- Cutover is explicitly gated: import → decrypt/validate → start/login regression → rotate/session compatibility proof → toggle DB-only reads → remove obsolete env inputs only in `ARCH-043-GATEWAY-001`. Before cutover no removal of env secrets; after cutover no silent per-request plaintext-env fallback. Missing, revoked, wrong-environment, malformed, unavailable DB or wrong unlock key at **cold start** must fail closed, never allow unsigned/unverified login. Test session expiry/rotation against actual Auth.js support; no invented grace periods.

### E. Forward migration and additional purpose compatibility

- The developer has authored a forward migration removing the five-key-only SQL CHECK constraint. Verify the migration is present/applied before writing `commerce.bootstrap`, `merchant.knowledge.r2` or `woocommerce.auth`. **No additional database task is required**. Do not rewrite DATABASE-001's migration or remove remaining generic uniqueness, integrity and append-only audit protections.
- Without database-level per-key encryption enforcement, require closed allowlisted purpose validation, sealed-only persistence and strictly redacted audit on every authenticated writer; prohibit untrusted direct SQL writes to these tables. Record the changed security boundary in the architecture review.
- Auth.js cutover remains part of this ADMIN-002 task: successfully import `auth.admin` while existing login works, prove a supported load-before-use path, validate login/session/rotation/cold-start failures, then gate removal of obsolete auth env variables on ADMIN-002 acceptance and Gateway-001 deployment. No silent fallback after cutover.

## Work Items

- [ ] Extend ADMIN-001 contract registry and reusable editor with the eight sealed-purpose contracts; no bespoke second form.
- [ ] Implement write-only secret actions, server-only read-status projection and strict SUPER_ADMIN checks (deny dev bypass for secret changes).
- [ ] Implement ARCH-039 `CredentialEnvelope` base64 mapping, canonical AAD, encryption/decryption interoperability and length checks; no new Shared exports.
- [ ] Implement sealed set/rotate/revoke CAS for all eight purposes, with redacted audit events and monotonic versions, including revocation/re-enable.
- [ ] Verify initial `auth.admin` import with an existing active SUPER_ADMIN before cutover; an out-of-band recovery command, if present, must independently authenticate its operator.
- [ ] Implement and verify Admin Auth.js database read-before-use cutover inside ADMIN-002; fail closed and prove session compatibility/rotation.
- [ ] Run focused security/integration/bootstrap validation, record isolation/sync and real outputs, return to Review.

## Interfaces / Contracts

- `ARCH-043-DATABASE-001` owns the two Prisma tables and SQL shape constraints. `ARCH-043-ADMIN-001` owns registry/UI/CAS/audit framework reused here.
- Existing encryption package only: `@modainteract/moda-interact-shared/security/credentials/node`. The **canonical AAD format** is specified in ARCH-043 architecture, not a new Shared source file or publication task.
- Secrets are purpose-scoped by the eight keys above. Downstream service reader tasks reference this envelope/AAD specification; do not create a new generic public credential API.
- External unseal root/KMS identity, database connectivity, deployment environment and `AUTH_URL` remain independently supplied. No new Prisma migrations in ADMIN-002. Existing developer-owned forward migration must be verified before enabling additional purposes.

## Dependencies

- `ARCH-043-DATABASE-001`
- `ARCH-043-ADMIN-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] All eight sealed purposes use the same contract-driven editor and status/history widgets; no duplication of persistence or unauthorised plain JSON editor.
- [ ] Browser/HTTP output and audit never contain plaintext, ciphertext, nonce, authTag, unwrap keys or decrypted session/OAuth values.
- [ ] Tampered AAD/envelope, wrong environment/key/version, unknown unwrap key and oversize plaintext fail closed with no DB mutation.
- [ ] First set, concurrent rotate, stale replay, revoke/re-enable and actor audit are serialised and preserve the monotonic version.
- [ ] Secret writes (including initial auth.admin import) require verified SUPER_ADMIN; unauthenticated, non-admin and development-bypass callers cannot rotate/revoke.
- [ ] Initial auth.admin import is authenticated using the existing environment-backed SUPER_ADMIN login (or an independently verified operator if an optional CLI is supplied); repeated/wrong-environment import fails safely.
- [ ] Auth.js startup/login/session behaviour is demonstrated on actual installed framework and missing/wrong key cold start never admits an unauthenticated user.
- [ ] Existing credential ciphertext/AAD across other domains is unchanged; no new Shared code or dependency publishing.

## Validation

- [ ] Contract/secret-form tests: eight purposes, field redaction, no autofill and server validation of unknown/empty inputs.
- [ ] Secret crypto golden vectors: Admin write to consumer decode/decrypt for all eight purposes, tamper, environment/key/version mismatch, invalid keyring, plaintext >8192 bytes; R2 six-field JSON integer checks and Woo platform-vs-merchant separation.
- [ ] Disposable PostgreSQL tests: set/rotate/revoke/re-enable, CAS conflict, audit redaction and atomicity, environment isolation.
- [ ] Auth & initial import tests: active SUPER_ADMIN authenticated import, optional CLI secured stdin and independently verified operator, cold start failure, Google provider login, session rotation/expiry, production dev-bypass rejection.
- [ ] No-secret-output audit of logs, exceptions, serialized props and server action results.
- [ ] Repo-required typecheck, changed-file lint, build and focused/affected tests, `git diff --check`; record results and blockers.

## Stop Condition

After scoped implementation, validation and Completion Report, set task to `review` and return control to `moda_architect`. STOP; do not start consumers/Gateway work or edit `_index.md`.

## Implementation Notes

- Avoid exporting secret DB entities into React Client Components. Pull only the public display metadata and configured/version status through a narrow server projection.
- Prefer reusing `src/lib/admin/platform-configuration/` service from ADMIN-001, with `secrets.ts`/`seal.ts` or similar small modules. No second generic logger or crypto stack.
- Because config unseal depends on key management outside DB, document the exact deployment dependency for Gateway rather than introducing hidden Render changes inside Admin.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-17T17:00:15Z. Attempt 0 review history is preserved below.

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

Awaiting implementation and validation evidence.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not yet assessed.

### Follow-up

None
