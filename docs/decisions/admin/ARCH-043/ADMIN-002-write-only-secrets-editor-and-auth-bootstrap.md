---
id: ARCH-043-ADMIN-002
architecture_id: ARCH-043
title: Manage canonical sealed platform configuration with request-time Admin authentication
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

Extend the existing Admin Platform Configuration editor to provide one canonical, encrypted, authorised configuration record per approved secret purpose, including explicit saved-value reveal, CAS-protected changes, and lazy `auth.admin` resolution with absent-row-only environment fallback. Assume a **fresh pre-production database**: no configuration-data migration, legacy readers, reconciliation, retirement flags or compatibility layers.

## Context

ADMIN-001 already owns the generic registry, UI, CAS and revision audit. ADMIN-002 adds the approved secret purposes using the published ARCH-039 Node encryption implementation. No dedicated bootstrap import command, startup secret lookup, separate authentication task, or migration work is required. Platform Configuration uses one canonical R2 record; the existing System Controls → Translations remains the sole translation-credential/profile owner.

## Scope

1. Provide **thirteen** closed secret-purpose contracts on the existing editor and keep only canonical policy groups (`woo.couponSync`, `speech.transcription`, `commerce.preview`, `admin.grafana`). Never expose `merchantKnowledge.upload` or `support.translation` as selectable or writable policies.
2. Manage `merchant.knowledge.r2` as a single sealed `{endpoint,bucket,accessKeyId,secretAccessKey,maxUploadBytes,maxXlsxUncompressedBytes}` record. `ai.providers` contains **only** optional `groqSpeechApiKey` and `openAiSpeechApiKey`, with at least one required for setup. The existing `CommerceTranslationProviderCredential` and approved translation model/automatic default remain owned by System Controls → Translations.
3. Support Set/Edit/Rotate/Revoke and on-demand saved-field reveal for approved SUPER_ADMIN principals, including the approved development-only synthetic principal. Preserve authenticated-data binding, transactional revisions, audit redaction, no double-submit and explicit rotation/revocation reasons.
4. Resolve `auth.admin` **only on authentication operations**: use validated decrypted database credentials when configured, otherwise use the complete environment credential bundle **only when no database row exists**. Revoked/invalid rows, database errors or decryption failures fail closed. No startup credential query or operator bootstrap command.
5. Provide tests covering closed purpose/field schemas, absence of retired configuration keys and migration machinery, direct fresh-database setup, secret reveal and CAS, Auth.js precedence/failure behaviour, and existing translation ownership.

## Out of Scope

- Configuration-data migration, historical policy reconciliation, legacy tab visibility/write gates, retirement environment flags, migration acknowledgements, old `ai.providers` translation-key compatibility, and preservation of older configuration rows.
- No changes to the original database schema, published Shared crypto contracts, API/Shopify/Background consumers, merchant-specific WooCommerce grants, deployment/networking/bootstrap secrets or `_index.md` files.
- No changes to existing Commerce translation credentials, automatic model profiles or embedding configuration.

## Requirements

### Fresh-database design invariant

This feature has **not entered production** and is implemented against a fresh database. No code or acceptance condition may require inspecting/copying/deleting old `merchantKnowledge.upload` or `support.translation` values. Do not create or check migration status; remove the five `legacy-*` helpers, their related tests and UI notices, the `MODA_ARCH043_DISABLE_LEGACY_POLICY_EDITORS` flag, and all `translationMigrationAcknowledged` or `validateStoredAiProviderPayload` compatibility paths. The canonical registry rejects unknown/retired keys immediately.

### Canonical records and security

- `merchant.knowledge.r2` owns all six R2 fields atomically. Enforce endpoint/bucket/hard-size constraints, seal with the approved keyring, and never expose credentials to general policy/browser metadata responses. Allow explicit authorised reveal of one stored field with a redacted security event, not a revision.
- `ai.providers` stores speech API credentials only. Translation API credentials stay in `CommerceTranslationProviderCredential` and model selection stays in the enabled automatic Commerce translation profile. `speech.transcription` continues to govern speech provider/model choice. The Background support translation reader is implemented in its owning task, without a second Admin policy.
- Preserve strict SUPER_ADMIN authorisation (development bypass only when the *real* deployment environment is development), environment-scoped reads/writes, CAS, and transactional redacted audit. First Set automatically records `initial-setup`; updates `configuration-update`; rotating requires a selected scheduled/compromise reason, revoking a decommission/compromise reason.
- On an authentication request, resolve `auth.admin` from PostgreSQL and validate/decrypt the *whole* bundle. An **absent** row allows fallback to `AUTH_SECRET`, `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET` together; a disabled/malformed/undecryptable row or database outage **does not**. Leave `AUTH_URL`, unseal root, deployment identity and database connectivity external. Do not read this credential during application boot. Verify Google login and session/rotation behaviour under installed Auth.js.
- Do not silently migrate any old data. Consumer tasks must directly adopt the single canonical record on their own execution boundaries; no implementation task depends on system-test or Gateway rollout tasks.

## Work Items

- [ ] Ensure the public registry exposes four canonical policy groups and thirteen approved secret purposes, without retired R2 or support-translation policy keys.
- [ ] Remove all five legacy reconciliation/assessment/retirement helpers and migration-specific tests/UI paths.
- [ ] Make `ai.providers` strict speech-only on all writes, reads and reveals, with no transitional decoder or operator acknowledgement.
- [ ] Retain saved secret reveal, partial edits, redacted audit, Set/Rotate/Revoke, CAS, and development-only SUPER_ADMIN support.
- [ ] Verify request-time Admin authentication lookup with absent-row-only complete-env fallback and fail-closed error paths.
- [ ] Run focused registry/UI/security/auth tests, repository validation and disposable PostgreSQL tests; report outcomes and evidence.

## Interfaces / Contracts

- Database source: `ARCH-043-DATABASE-001` (`PlatformConfiguration`, `PlatformConfigurationAudit`); no additional schema or data migration.
- Cryptography: published `@modainteract/moda-interact-shared/security/credentials/node`; the established environment/purpose/revision AAD remains unchanged.
- Canonical configuration: sealed `merchant.knowledge.r2`; strict speech-only `ai.providers`; existing Commerce translation credentials and model profile/automatic default.
- Authentication: `auth.admin` request-time database-first resolution with environment fallback **only for absent rows**. `AUTH_URL`, database connection, deployment identity and unseal keys remain external.
- Downstream reader integration belongs to API/Shopify/Background/Commerce task owners; not ADMIN-002.

## Dependencies

- `ARCH-043-DATABASE-001`
- `ARCH-043-ADMIN-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Four policy groups and thirteen approved sealed purposes; neither `merchantKnowledge.upload` nor `support.translation` can be selected or written.
- [ ] No legacy helper, rollout flag, migration notice, translation migration acknowledgement or backward-compatible AI provider decoder remains in Admin runtime code.
- [ ] All six R2 values use one sealed record with strict validation and no unsafe fallback to another policy key.
- [ ] Translation credential and automatic model authority remains unchanged under System Controls → Translations; `ai.providers` is speech-only.
- [ ] Secret reveal occurs only on explicit authorised request and logs a redacted access event; writes retain version checking and redacted audit history.
- [ ] Admin starts without an auth-credential read, and authentication operations use database credentials or the complete environment bundle **only when the row is absent**; database/validation/decryption/revocation errors fail closed.
- [ ] Existing legitimate SUPER_ADMIN and development-only synthetic SUPER_ADMIN paths pass; production bypass remains forbidden.

## Validation

- [ ] Focused policy/secret registry, UI, reveal/rotate/revoke, authorisation and clean-start unit tests.
- [ ] Authentication-time resolver tests including DB precedence, absent-row-only fallback, revocation, bad key and outages; manual Google OAuth/session-rotation evidence.
- [ ] Disposable PostgreSQL tests for transactional redacted audit, CAS conflict, environment isolation, sealed R2 and speech-only payloads.
- [ ] TypeScript, lint, production build and `git diff --check`; record baseline warnings and any unavailable validation honestly.

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
