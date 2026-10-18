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
status: ready
priority: 30
executor: null
claimed_at: null
depends_on:
  - ARCH-043-DATABASE-001
  - ARCH-043-ADMIN-001
enables:
  - ARCH-043-GATEWAY-001
  - ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: 2026-10-18
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

- `ARCH-043` parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Exact sealed-envelope, AAD and key-purpose rules: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Builds on the reusable field renderer, policy registry, privileged CAS/audit service and page from `ARCH-043-ADMIN-001`.
- Current source: `src/auth.ts` instantiates `NextAuth` at module load; `src/lib/auth/environment.ts` requires `AUTH_SECRET`, `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET`, `AUTH_URL`; `src/lib/admin/shared-credential-keyring.ts` loads ARCH-039 keyring from environment. Do not assume Auth.js accepts an asynchronous key load at module construction.
- Materialized on the canonical parent task branch; launcher-resolved paths remain authoritative.

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
- On an authentication request, resolve `auth.admin` from PostgreSQL and validate/decrypt the *whole* bundle. An **absent** row allows fallback to `AUTH_SECRET`, `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET` together; a disabled/malformed/undecryptable row or database outage **does not**. Leave `AUTH_URL`, unseal root, deployment identity and database connectivity external. Do not read this credential during application boot. Verify database precedence, absent-row-only fallback, and fail-closed behaviour with automated resolver tests; verify JWT expiry and signing-secret rotation with automated Auth.js tests. A live Google OAuth login or manual session-rotation demonstration is not required for this task.
- Do not silently migrate any old data. Consumer tasks must directly adopt the single canonical record on their own execution boundaries; no implementation task depends on system-test or Gateway rollout tasks.


## Work Items

- [x] Ensure the public registry exposes four canonical policy groups and thirteen approved secret purposes, without retired R2 or support-translation policy keys.
- [x] Remove all five legacy reconciliation/assessment/retirement helpers and migration-specific tests/UI paths.
- [x] Make `ai.providers` strict speech-only on all writes, reads and reveals, with no transitional decoder or operator acknowledgement.
- [x] Retain saved secret reveal, partial edits, redacted audit, Set/Rotate/Revoke, CAS, and development-only SUPER_ADMIN support.
- [x] Verify request-time Admin authentication lookup with absent-row-only complete-env fallback and fail-closed error paths.
- [x] Run focused registry/UI/security/auth tests, repository validation and disposable PostgreSQL tests; report outcomes and evidence.


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

- [x] Four policy groups and thirteen approved sealed purposes; neither `merchantKnowledge.upload` nor `support.translation` can be selected or written.
- [x] No legacy helper, rollout flag, migration notice, translation migration acknowledgement or backward-compatible AI provider decoder remains in Admin runtime code.
- [x] All six R2 values use one sealed record with strict validation and no unsafe fallback to another policy key.
- [x] Translation credential and automatic model authority remains unchanged under System Controls → Translations; `ai.providers` is speech-only.
- [x] Secret reveal occurs only on explicit authorised request and logs a redacted access event; writes retain version checking and redacted audit history.
- [x] Admin starts without an auth-credential read, and authentication operations use database credentials or the complete environment bundle **only when the row is absent**; database/validation/decryption/revocation errors fail closed.
- [ ] Existing legitimate SUPER_ADMIN and development-only synthetic SUPER_ADMIN paths pass; production bypass remains forbidden.


## Validation

- [x] Focused policy/secret registry, UI, reveal/rotate/revoke, authorisation and clean-start unit tests.
- [ ] Automated authentication-time resolver tests covering database precedence, absent-row-only fallback, revocation, invalid keys and outages, plus automated Auth.js JWT expiry/signing-secret rotation tests. (Resolver tests passed; record the final automated JWT test result before checking this item. Live Google OAuth or manual rotation evidence is not required.)
- [x] Disposable PostgreSQL tests for transactional redacted audit, CAS conflict, environment isolation, sealed R2 and speech-only payloads.
- [x] TypeScript, lint, production build and `git diff --check`; record baseline warnings and any unavailable validation honestly. (Lint had one warning and zero errors; build emitted existing dependency warnings; broader test failures are recorded below.)


## Stop Condition

After scoped implementation, validation and Completion Report, set task to `review` and return control to `moda_architect`. STOP; do not start consumers/Gateway work or edit `_index.md`.

## Implementation Notes


## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-17T17:00:15Z. Attempt 0 review history is preserved below.

### Files Changed

33 implementation files across `.env.example`, `package.json`, `src/app`, `src/components/admin/platform-configuration`, `src/lib/admin/platform-configuration`, `src/lib/auth`, `tests/integration`, `tests/security`, and `tests/unit`; the `database` submodule pointer also advances in the implementation task branch.

### Work Completed

Implemented the amended Admin Platform Configuration scope: the registry exposes four canonical policy groups and thirteen closed secret purposes; retired migration/reconciliation helpers and compatibility paths are absent; `ai.providers` is speech-only; and R2 is stored as one sealed record. Added explicit authorized secret reveal with redacted security logging, Set/Update/Rotate/Revoke with version checks and transactional redacted audit, and request-time `auth.admin` resolution with complete-environment fallback only on confirmed row absence. Added tests for auth precedence/fail-closed behavior, role boundaries, contracts, UI, reveal, mutations, clean-start wiring and database-backed CAS/audit behavior. No material `moda_admin` assistance is recorded; this was a developer-owned attempt.

### Validation Results

Passed focused ARCH-043 auth/lazy-wiring tests (7/7), secret/access tests (12/12), registry/UI tests (10/10), and component tests (2/2).

Passed disposable PostgreSQL integration (10/10 executed; CAS conflict, audit rollback/redaction, environment isolation, secret reveal/rotation/revocation, and R2 behavior). The test runner created and removed its disposable PostgreSQL container. It prints a legacy `PASS ARCH-043 ADMIN-001 disposable PostgreSQL` label; the recorded count is from the ADMIN-002 secret integration cases actually executed.

Passed `node node_modules/typescript/bin/tsc --noEmit`; `npm run lint` completed with one warning in `database/eslint.config.mjs` and zero errors; `npm run build` completed successfully. Build emitted existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` resolution warnings. `git diff --check origin/main...HEAD` passed.

Broader validation was not clean: `npm run test:unit` reported 468 passed and 5 failed (including two ARCH-043 test files under the generic runner, two unrelated Commerce drawer harness failures, and the Shopify taxonomy test failing to resolve the `@/lib` alias). `npm test` reported failures in `Admin stages Store Category translation work without publishing to BullMQ` and `Tenant Directory KPIs are derived from durable business state`; these remain reported and were not modified as unrelated areas. Manual Google OAuth and session-rotation behavior were not exercised.

### Deviations

Required manual Google OAuth/session-rotation validation was not performed. The broad test commands also reported failures detailed above; no claim is made that those failures are caused by this task or that they are baseline failures.

### Assumptions

The request to complete this task does not waive its stated manual authentication validation or required passing review.

### Unresolved Issues

Run the Admin application against an approved local/test environment with valid test Google OAuth credentials; verify login, JWT/session behavior and key-rotation/expiry behavior using the installed Auth.js version, then record reproducible evidence. Re-run the failed broad test targets with their correct harness or establish an accepted baseline; retain passing focused ARCH-043 and disposable PostgreSQL evidence. After a passing durable review, invoke the explicit developer completion action.

### Architectural Concerns

No implementation-scope deviation was found during the code and focused validation review. Completion remains blocked by missing manual auth evidence and the current broader test failures.

## Developer Self-Review - Changes Requested (Attempt 1, 2026-10-18)

*Historical record:* The earlier manual Google OAuth/session-rotation request below is superseded by the 2026-10-18 acceptance-contract amendment above. It remains recorded as the contemporaneous review finding, not a current completion prerequisite. The unrelated broad-test findings are not waived.

### Review Status

Changes Requested

### Findings

- Complete and record Google OAuth login plus session/key-rotation/expiry validation against the installed Auth.js version using an approved test environment.
- Investigate the failed broad test targets with their correct harness or establish an accepted baseline. Current failures include unrelated Commerce drawer harness tests, the Shopify taxonomy alias-resolution test, and two Admin tests under broad runner invocations; `npm test` also reports the Store Category translation and Tenant Directory KPI failures. These are reported, not presumed to be baseline failures.
- Re-run the relevant validations and update evidence. Do not transition this task to `complete` until these gaps are resolved and the durable review is passing.

### Reviewed Files

Implementation changes on `task/ARCH-043-ADMIN-002` (commit `54cbbf8984d4be6cf7e779bfa2fdbe742b943705`) and this task definition.

### Validation Reviewed

Focused test suites, disposable PostgreSQL integration, TypeScript no-emit, lint, production build, and reported broad test results listed above.

### Follow-up

Address findings above, then request a fresh review. Keep status `ready` and attempt 1 until then.

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation and validation evidence. On 2026-10-18 the acceptance contract was amended: live Google OAuth login and manual session-rotation evidence are no longer prerequisites for this task. Automated resolver, fail-closed and JWT rotation/expiry tests remain required. The historical developer self-review is retained; its non-authentication findings still require disposition.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not yet assessed.

### Follow-up

None
