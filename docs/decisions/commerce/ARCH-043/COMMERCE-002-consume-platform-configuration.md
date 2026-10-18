---
id: ARCH-043-COMMERCE-002
architecture_id: ARCH-043
title: Integrate database configuration into Commerce runtime consumers
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-18T15:16:27Z
attempt: 1
depends_on:
  - ARCH-043-COMMERCE-001
  - ARCH-043-ADMIN-002
enables:
  - ARCH-043-GATEWAY-001
  - ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-18'
---

# Consume platform configuration in Commerce

## Architecture

- `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Service prerequisite: `ARCH-043-COMMERCE-001`.
- Secure operator import/admin writer prerequisite: `ARCH-043-ADMIN-002`.
- Owner: `moda_commerce` / `moda-interact-commerce`.

## Developer Ownership Amendment

On 2026-10-18, `/moda_developer_create ARCH-043-COMMERCE-002` was invoked to take over this ready task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_commerce`, repository ownership, scope, dependencies and acceptance criteria are unchanged.

## Objective

Replace approved Commerce environment-backed policy and secret reads with the accepted database configuration service, preserving the **absence-only `auth.commerce` environment fallback**, connection encryption, authorisation, preview safety and fresh per-operation reads. Merchant Knowledge must not gate Commerce startup.

## Context

Current consumers include `src/commerce/preview/run-budgets.ts`, `auth.ts`, `lib/auth/environment.ts`, `lib/server/config.ts`, `src/commerce/connections/security-config.ts`, `src/commerce/integration/backend.ts`, `lib/server/credential-keyring.ts`, `lib/preview/runtime.ts`, `src/commerce/merchant-knowledge/embedding-runtime.ts`, `src/studio/server-actions.ts` and `src/studio/tools/woocommerce-test-server-actions.ts`. Startup is also affected by `instrumentation.node.ts`. Inspect current equivalent consumers rather than assuming this list is exhaustive.

## Scope

- Replace `COMMERCE_PREVIEW_RUN_DEADLINE_MS` and `COMMERCE_PREVIEW_RUN_OUTPUT_TOKENS` reads with `readCommercePreviewPolicy()` for each new preview execution. Preserve existing preview reservation expiry, hard ceilings, `modelSteps`, `remoteCalls`, cancellation, timeouts and production conversation separation.
- Adapt Commerce Studio Google OAuth/NextAuth and session signing to the accepted Commerce auth reader using a **per-authentication-operation database-first resolver**. When and only when the environment-scoped `auth.commerce` row is absent, use the **complete** legacy `AUTH_SECRET`, `AUTH_GOOGLE_ID` and `AUTH_GOOGLE_SECRET` environment bundle. Disabled, invalid, undecryptable, wrong-environment rows and database errors fail closed. Keep `AUTH_URL`, the intentional auth fallback bundle, deployment identity, `DATABASE_URL`, network bootstrap and external unseal identity as deployment configuration.
- Because `auth.ts` constructs `NextAuth(studioAuthConfig)` synchronously in the legacy code, **prove the installed Auth.js-supported per-operation approach** (such as an asynchronous configuration callback). Do not inject an unresolved Promise, establish a temporary unauthenticated state, or claim credential hot reload without tests. The approved absence-only environment fallback is an explicit exception, not a workaround for unsupported framework behaviour. If the framework cannot safely meet the required freshness, return an architectural blocker.
- Replace `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` reads with `requireCommerceConnectionSecurity()` across integration/backend composition, connection tools, signature/proof verification, merchant-knowledge embedding credential readers and preview runtime. Preserve existing ciphertext/AAD of stored connection/provider credentials.
- Audit any process-level backend or Auth.js singleton that captures credential values (`getCommerceBackend()` currently memoises the composed backend). Refactor or inject **per-operation** validated secret inputs at security-sensitive entrypoints; keeping a reusable Prisma or HTTP client is allowed, but retaining configuration values across operations is not.
- Ensure tampered, disabled, wrong-environment or unavailable required secrets fail closed, never silently permit connection commands, session verification or OAuth login. **Only an absent `auth.commerce` row permits the complete Auth.js environment bundle**; no other protected configuration group has an environment fallback.
- Verify operator/import ordering: `ADMIN-002` must have safely imported the relevant encrypted secrets before cutover. No automatic plaintext migration or removal of gateway variables in this task.
- Remove automatic Merchant Knowledge provisioning from Commerce startup (`instrumentation.node.ts`): startup succeeds without Merchant Knowledge configuration, an embedding row or `commerce.bootstrap` selection. Preserve an explicit operator-triggered provisioning path where supported, but never require it merely to start Commerce. Merchant Knowledge embedding lookups fetch the existing embedding configuration first, then the current `commerce.connectionKeys` on demand; do not capture a keyring at bootstrap or across operations. A missing embedding configuration must not cause a connection-key read solely for bootstrap.
- Add purpose-scoped structured logging through `@modainteract/moda-interact-shared/logging` for configuration source selection, bounded failures, and non-sensitive startup/embedding outcomes. Never create a second generic logger; never log secret values, key material, ciphertext, raw database errors, provider payloads or credentials. Logging failure must not change the outcome of authentication or business processing.
- Add focused tests proving that successive operations see committed updates, old/new credential rotation behaviour follows supported framework semantics, Merchant Knowledge starts without provisioning and resolves its keyring when needed, and protected operations cannot use stale secret material.
- Ensure the Commerce `database` submodule points to the accepted `ARCH-043-DATABASE-001` schema before Prisma generation and PostgreSQL tests; record any necessary gitlink update without changing database-owned source code.

## Out of Scope

- No new configuration service, database migration, new Shared encryption functions or Commerce-specific Admin UI.
- No changes to Shopify/Background/API/MCP consumers or Messaging runtime.
- No Render Blueprint env-variable removal (Gateway-owned), OAuth provider changes unrelated to ARCH-043, new cross-operation cache or Redis-based configuration snapshot.

## Requirements
### Authentication-time source precedence amendment (2026-10-17)

For `auth.commerce`, resolve credentials lazily at authentication operations, not in app bootstrap. If and only if the environment-scoped `auth.commerce` row is **absent**, use the complete existing `AUTH_SECRET`/Google env bundle; disabled/invalid/undecryptable row or DB failure must fail closed. Retain `AUTH_URL` and auth fallback variables in Gateway. This amendment supersedes older DB-only/no-env-fallback sentences for Auth.js only, not for other migrated secret groups; prove session/key rotation with installed Auth.js. **The same precedence must appear in Scope, Acceptance Criteria and Validation; no later task addendum may reverse it.**


1. The accepted Commerce configuration service owns the three original runtime keys (`commerce.preview`, `auth.commerce`, `commerce.connectionKeys`). Its approved `commerce.bootstrap` admin selector may be used **only by explicit provisioning paths**, not as a Commerce or Merchant Knowledge startup prerequisite. No duplicate Prisma readers or configuration-specific service frameworks.
2. Every supported new operation uses fresh validated config; a single operation may reuse its local snapshot, but later operations must re-read. Auth.js bootstrap exceptions are *not assumed* and must be proven or escalated.
3. Existing preview budget ceilings remain enforced even under invalid, absent or adversarial stored values.
4. Existing stored Commerce connection credentials remain decryptable without rewriting their ciphertext or authenticated-data bytes.
5. Rotation and revocation must not silently preserve obsolete privileges through memoised config; session compatibility must be proven with the installed Auth.js version.
6. Secrets never reach client bundles, JSON route responses, ordinary logs, metrics or audit payloads.
7. Shared structured logs report only bounded key/source/reason identifiers; logging is best-effort and cannot change fail-closed configuration decisions.
8. Merchant Knowledge bootstrap/provisioning is optional for application startup; embedding credentials are read only on demand and subsequent operations observe rotation or revocation.

## Work Items

- [ ] Inventory existing Commerce env consumers, including subprocess/preview runtime, embedding readers and proof signing.
- [ ] Wire preview admission to the service without changing fixed hard limits.
- [ ] Adapt Auth.js/Google OAuth/session using a verified framework-supported lazy resolver and absence-only complete environment fallback.
- [ ] Replace connection-keyring/active-key/HMAC consumers and remove configuration-bearing singletons.
- [ ] Remove automatic Merchant Knowledge provisioning as a Commerce startup gate; fetch embedding configuration and the necessary connection keys only when an embedding lookup requires them.
- [ ] Add safe configuration-source, failure and startup/embedding event logging through the published Shared logging library.
- [ ] Add negative tests for missing/disabled/corrupt secrets, DB outage, foreign environment and revoked/rotated material, including environment fallback **only** for an absent `auth.commerce` record.
- [ ] Prove consecutive requests/runs observe new policy/secrets without a cross-operation cache or obsolete env fallback.
- [ ] Pin/verify the accepted database submodule revision and document actual framework/bootstrap constraints and rollback behaviour; record worktree/test evidence and submit for Review.

## Interfaces / Contracts

- `ARCH-043-COMMERCE-001` typed service: `readCommercePreviewPolicy()`, `requireCommerceAuthConfiguration()`, `requireCommerceConnectionSecurity()`. The separately approved `commerce.bootstrap` selector is for explicit operator provisioning, never a startup prerequisite.
- Auth.js environment fallback is allowed **only** for an absent `auth.commerce` row, using the full authenticated-server environment bundle.
- Structured event logging uses `@modainteract/moda-interact-shared/logging`, not a local JSON logger.
- `ARCH-043-ADMIN-002`: write-only secret import and validation; no runtime reading of Admin UI state.
- `ARCH-043-DATABASE-001`: canonical `PlatformConfiguration` records; no new schema needed.
- Existing ARCH-039 `@modainteract/moda-interact-shared/security/credentials/node` implementation; reuse, do not change.
- Environment keys migrated: `COMMERCE_PREVIEW_RUN_DEADLINE_MS`, `COMMERCE_PREVIEW_RUN_OUTPUT_TOKENS`, `AUTH_SECRET`, `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET`, `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID`, `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` **only where consumed by Commerce**.

## Dependencies

- `ARCH-043-COMMERCE-001`
- `ARCH-043-ADMIN-002`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Preview, Auth.js login/session and connection/embedding/command consumers use the accepted configuration service for in-scope database values; **only an absent `auth.commerce` row** uses the full approved Auth.js environment fallback.
- [ ] A change between operations takes effect at the next supported operation, with no reusable configuration cache; framework-incompatible refresh is escalated rather than falsely reported as immediate.
- [ ] No environment fallback for invalid/disabled/undecryptable/DB-failed auth rows or any non-auth secret, bypass, unvalidated secret, client leak or sensitive logging exists.
- [ ] Auth/OAuth operations work with imported encrypted database records and, only when `auth.commerce` is absent, the complete environment credential bundle; disabled/corrupt records and DB errors fail closed. Commerce application startup is not blocked by missing Merchant Knowledge provisioning or embedding credentials.
- [ ] Existing connection ciphertext/AAD, slot deadlines and preview ceilings remain valid.
- [ ] Rotation/revocation, credential tampering, missing rows, per-environment isolation, next-operation visibility and database-outage behaviour have focused tests.
- [ ] Merchant Knowledge lookups fetch embedding credentials only when needed, see current connection-key rotation on subsequent operations and do not execute during Commerce startup.
- [ ] Shared structured logs cover bounded configuration-source/failure outcomes without secrets, and logger failures cannot affect the protected operation.

## Validation

- [ ] Studio preview budget, reservation and tool-test tests.
- [ ] Auth.js configuration/login/session tests, including supported runtime rotation semantics, absent-row environment fallback, and fail-closed handling of disabled/malformed rows and database outages.
- [ ] Connection security and command HMAC proof tests; on-demand embedding/preview credential compatibility tests, startup without Merchant Knowledge provisioning, and Shared logging/redaction/failure-isolation tests.
- [ ] PostgreSQL backed end-to-end smoke using the accepted `ARCH-043-DATABASE-001` submodule revision: initial import, first request, config update, next request, revoke, DB unavailable.
- [ ] Applicable Commerce repository typecheck, lint, production build, and `git diff --check`.

## Stop Condition

Complete only the Commerce consumer integration and evidence, update Completion Report, set Review and stop. Do not modify `_index.md`, Gateway declarations or start follow-on tasks.

## Implementation Notes

Avoid blanket environment-removal scripts; Gateway owns final deployment cleanup after both Commerce tasks pass acceptance and secret cutover is verified. **Gateway retains the Auth.js environment bundle as an intentional absent-row fallback.** If Auth.js cannot support the agreed per-operation no-cache requirement, record the exact framework limitation and return to the architect rather than weakening authentication. `commerce.bootstrap.adminEmail` remains an explicitly invoked provisioning selector, never a precondition for Commerce startup or Merchant Knowledge embedding lookup.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-18T15:16:27Z.

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

The canonical records for `ARCH-043-COMMERCE-001` and `ARCH-043-ADMIN-002` are Complete; both explicit dependencies passed the launcher dependency check before claim.

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

## 17 October 2026 ARCH-043 extension (architect-owned amendment)

Commerce Auth.js reads `auth.commerce` **per authentication operation**, with the complete `AUTH_SECRET`/Google environment bundle used only if the database row is absent. Existing but disabled, invalid or unavailable records fail closed. The independently sealed `commerce.bootstrap.adminEmail` is resolved only when an explicitly requested administrative provisioning operation needs a selector; it never gates Commerce startup or ordinary Merchant Knowledge embedding lookups. Never hardcode a real bootstrap email or treat the selector as proof of principal identity. Database-backed secret use requires the controlled ADMIN-002 writer/import; the approved absent-row Auth.js fallback remains available after cutover. Use only Shared structured logging for these configuration paths.
