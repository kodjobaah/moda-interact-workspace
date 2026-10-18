---
id: ARCH-043-COMMERCE-002
architecture_id: ARCH-043
title: Integrate database configuration into Commerce runtime consumers
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
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

## Objective

Replace all approved Commerce environment-backed policy and secret reads with the accepted `COMMERCE-001` database service while preserving authentication, connection encryption, authorisation, preview safety and no-caching rules.

## Context

Current consumers include `src/commerce/preview/run-budgets.ts`, `auth.ts`, `lib/auth/environment.ts`, `lib/server/config.ts`, `src/commerce/connections/security-config.ts`, `src/commerce/integration/backend.ts`, `lib/server/credential-keyring.ts`, `lib/preview/runtime.ts`, `src/commerce/merchant-knowledge/embedding-runtime.ts`, `src/studio/server-actions.ts` and `src/studio/tools/woocommerce-test-server-actions.ts`. Inspect all current equivalent consumers rather than assuming this list is exhaustive.

## Scope

- Replace `COMMERCE_PREVIEW_RUN_DEADLINE_MS` and `COMMERCE_PREVIEW_RUN_OUTPUT_TOKENS` reads with `readCommercePreviewPolicy()` for each new preview execution. Preserve existing preview reservation expiry, hard ceilings, `modelSteps`, `remoteCalls`, cancellation, timeouts and production conversation separation.
- Adapt Commerce Studio Google OAuth/NextAuth and session signing to `requireCommerceAuthConfiguration()`. Resolve `AUTH_SECRET`, `AUTH_GOOGLE_ID` and `AUTH_GOOGLE_SECRET` from the database on an authenticated/trusted server path. Keep `AUTH_URL`, deployment identity, `DATABASE_URL`, network bootstrap and external unseal identity as deployment configuration.
- Because `auth.ts` currently constructs `NextAuth(studioAuthConfig)` synchronously, **prove the actual supported framework approach** (e.g. supported request-scoped dynamic configuration or a verified load-before-serve mechanism). Do not inject an unresolved Promise, establish a temporary unauthenticated state, or claim credential hot reload without tests. If the installed framework cannot meet the no-cross-operation-cache requirement safely, return a documented architecture blocker instead of implementing a secret fallback.
- Replace `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` reads with `requireCommerceConnectionSecurity()` across integration/backend composition, connection tools, signature/proof verification, merchant-knowledge embedding credential readers and preview runtime. Preserve existing ciphertext/AAD of stored connection/provider credentials.
- Audit any process-level backend or Auth.js singleton that captures credential values (`getCommerceBackend()` currently memoises the composed backend). Refactor or inject **per-operation** validated secret inputs at security-sensitive entrypoints; keeping a reusable Prisma or HTTP client is allowed, but retaining configuration values across operations is not.
- Ensure missing, tampered, disabled, wrong-environment or unavailable required secrets fail closed, never fall back to deprecated environment values or silently permit connection commands, session verification or OAuth login.
- Verify operator/import ordering: `ADMIN-002` must have safely imported the relevant encrypted secrets before cutover. No automatic plaintext migration or removal of gateway variables in this task.
- Add focused tests proving that successive operations see committed updates, old/new credential rotation behaviour follows supported framework semantics, and protected operations cannot use stale secret material.

## Out of Scope

- No new configuration service, database migration, new Shared encryption functions or Commerce-specific Admin UI.
- No changes to Shopify/Background/API/MCP consumers or Messaging runtime.
- No Render Blueprint env-variable removal (Gateway-owned), OAuth provider changes unrelated to ARCH-043, new cross-operation cache or Redis-based configuration snapshot.

## Requirements
### Authentication-time source precedence amendment (2026-10-17)

For `auth.commerce`, resolve credentials lazily at authentication operations, not in app bootstrap. If and only if the environment-scoped `auth.commerce` row is **absent**, use the complete existing `AUTH_SECRET`/Google env bundle; disabled/invalid/undecryptable row or DB failure must fail closed. Retain `AUTH_URL` and auth fallback variables in Gateway. This amendment supersedes older DB-only/no-env-fallback sentences for Auth.js only, not for other migrated secret groups; prove session/key rotation with installed Auth.js.


1. `COMMERCE-001` is the sole Commerce runtime source for the three database keys; no duplicate Prisma readers or configuration-specific service frameworks.
2. Every supported new operation uses fresh validated config; a single operation may reuse its local snapshot, but later operations must re-read. Auth.js bootstrap exceptions are *not assumed* and must be proven or escalated.
3. Existing preview budget ceilings remain enforced even under invalid, absent or adversarial stored values.
4. Existing stored Commerce connection credentials remain decryptable without rewriting their ciphertext or authenticated-data bytes.
5. Rotation and revocation must not silently preserve obsolete privileges through memoised config; session compatibility must be proven with the installed Auth.js version.
6. Secrets never reach client bundles, JSON route responses, ordinary logs, metrics or audit payloads.

## Work Items

- [ ] Inventory existing Commerce env consumers, including subprocess/preview runtime, embedding readers and proof signing.
- [ ] Wire preview admission to the service without changing fixed hard limits.
- [ ] Adapt Auth.js/Google OAuth/session and startup/route composition using a verified framework-supported mechanism.
- [ ] Replace connection-keyring/active-key/HMAC consumers and remove configuration-bearing singletons.
- [ ] Add negative tests for missing/disabled/corrupt secrets, DB outage, foreign environment and revoked/rotated material.
- [ ] Prove consecutive requests/runs observe new policy/secrets without a cross-operation cache or obsolete env fallback.
- [ ] Document actual framework/bootstrap constraints and rollback behaviour; record worktree/test evidence and submit for Review.

## Interfaces / Contracts

- `ARCH-043-COMMERCE-001` typed service: `readCommercePreviewPolicy()`, `requireCommerceAuthConfiguration()`, `requireCommerceConnectionSecurity()`.
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

- [ ] Preview, Auth.js login/session and connection/embedding/command consumers use only the accepted config service for in-scope values.
- [ ] A change between operations takes effect at the next supported operation, with no reusable configuration cache; framework-incompatible refresh is escalated rather than falsely reported as immediate.
- [ ] No stale environment fallback, bypass, unvalidated secret, client leak or sensitive logging exists.
- [ ] Auth/OAuth and connection-keyring startup works from imported encrypted database records; unavailable required credentials fail closed.
- [ ] Existing connection ciphertext/AAD, slot deadlines and preview ceilings remain valid.
- [ ] Rotation/revocation, credential tampering, missing rows, per-environment isolation, next-operation visibility and database-outage behaviour have focused tests.

## Validation

- [ ] Studio preview budget, reservation and tool-test tests.
- [ ] Auth.js configuration/login/session tests, including supported runtime rotation semantics.
- [ ] Connection security and command HMAC proof tests; embedding/preview credential compatibility tests.
- [ ] PostgreSQL backed end-to-end smoke: initial import, first request, config update, next request, revoke, DB unavailable.
- [ ] Applicable Commerce repository typecheck, lint, production build, and `git diff --check`.

## Stop Condition

Complete only the Commerce consumer integration and evidence, update Completion Report, set Review and stop. Do not modify `_index.md`, Gateway declarations or start follow-on tasks.

## Implementation Notes

Avoid blanket environment-removal scripts; Gateway owns final deployment cleanup after both Commerce tasks pass acceptance and secret cutover is verified. If Auth.js cannot support the agreed no-cache requirement, record the exact framework limitation and return to the architect before introducing a workaround that weakens authentication.

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

## 17 October 2026 ARCH-043 extension (architect-owned amendment)

Commerce Auth.js reads `auth.commerce` after verified load-before-serve cutover; Merchant Knowledge bootstrap reads `commerce.bootstrap.adminEmail`. Do not hardcode a real bootstrap email or treat this field as proof of principal identity. Both require ADMIN-002 import; no silent env fallback after cutover.
