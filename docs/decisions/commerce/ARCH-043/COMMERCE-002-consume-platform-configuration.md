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
status: ready
priority: 40
executor: null
claimed_at: null
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

- [x] Inventory existing Commerce env consumers, including subprocess/preview runtime, embedding readers and proof signing.
- [x] Wire preview admission to the service without changing fixed hard limits.
- [x] Adapt Auth.js/Google OAuth/session using a verified framework-supported lazy resolver and absence-only complete environment fallback.
- [x] Replace connection-keyring/active-key/HMAC consumers and remove configuration-bearing singletons.
- [x] Remove automatic Merchant Knowledge provisioning as a Commerce startup gate; fetch embedding configuration and the necessary connection keys only when an embedding lookup requires them.
- [x] Add safe configuration-source, failure and startup/embedding event logging through the published Shared logging library.
- [x] Add negative tests for missing/disabled/corrupt secrets, DB outage, foreign environment and revoked/rotated material, including environment fallback **only** for an absent `auth.commerce` record.
- [x] Prove consecutive requests/runs observe new policy/secrets without a cross-operation cache or obsolete env fallback.
- [x] Add a disposable PostgreSQL Commerce **consumer** smoke (distinct from the configuration-reader suite) covering initial reads, a committed change on the next operation, Auth.js and connection-key rotation/revocation, database shutdown, zero skipped assertions and owned-container cleanup.
- [ ] Verify whether the consumer-smoke additions are committed on the implementation task branch; if not, commit and push only the validated task files, then record the actual full implementation commit SHA.
- [ ] Reconcile the accepted database submodule revision and actual framework/bootstrap/rollback behaviour with final worktree synchronization evidence; perform the developer self-review, update the Completion Report and submit for Review.

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
- [x] The disposable Commerce-consumer PostgreSQL smoke executed **4/4 consumer** tests and **1/1 database-outage** test with no skipped or incomplete tests; the owned database was shut down and cleaned up.
- [ ] Merchant Knowledge lookups fetch embedding credentials only when needed, see current connection-key rotation on subsequent operations and do not execute during Commerce startup.
- [ ] Shared structured logs cover bounded configuration-source/failure outcomes without secrets, and logger failures cannot affect the protected operation.

## Validation

- [x] Studio preview budget, reservation and tool-test tests (focused Commerce suites and isolated unit run).
- [x] Auth.js configuration/login/session tests, including supported runtime rotation semantics, absent-row environment fallback, and fail-closed handling of disabled/malformed rows and database outages (including direct Auth.js rotation tests).
- [x] Connection security and command HMAC proof tests; on-demand embedding/preview credential compatibility tests, startup without Merchant Knowledge provisioning, and Shared logging/redaction/failure-isolation tests (focused and isolated unit suites).
- [x] PostgreSQL-backed **Commerce consumer** end-to-end smoke with the accepted `ARCH-043-DATABASE-001` migration: initial import, first operation, committed update/next operation, revocation and database unavailable (4/4 plus 1/1, no skips, owned cleanup).
- [x] Applicable Commerce repository typecheck, lint, production build, and `git diff --check` (latest local results recorded below).

Note: the isolated unit run deliberately excluded seven infrastructure-gated test files; it is **not** evidence that the unfiltered `npm test` invocation passed. Those tests require their own disposable harnesses or an explicit review disposition.

## Stop Condition

Complete only the Commerce consumer integration and evidence, update Completion Report, set Review and stop. Do not modify `_index.md`, Gateway declarations or start follow-on tasks.

## Implementation Notes

Avoid blanket environment-removal scripts; Gateway owns final deployment cleanup after both Commerce tasks pass acceptance and secret cutover is verified. **Gateway retains the Auth.js environment bundle as an intentional absent-row fallback.** If Auth.js cannot support the agreed per-operation no-cache requirement, record the exact framework limitation and return to the architect rather than weakening authentication. `commerce.bootstrap.adminEmail` remains an explicitly invoked provisioning selector, never a precondition for Commerce startup or Merchant Knowledge embedding lookup.

## Completion Report

### Status

Changes Requested — Developer Self-Review of Attempt 1 did not pass. Task returned to `ready`; Attempt 1 is unchanged.

**2026-10-20 validation update:** The subsequent direct Auth.js tests, isolated unit run, PostgreSQL consumer/outage smoke, lint, typecheck and build have passed as recorded below. The task remains `ready` with `attempt: 1`, `executor: null` and no architect acceptance. Final implementation commit verification, developer claim/self-review and formal completion remain outstanding.

### Files Changed

Commerce implementation changes were previously published on `task/ARCH-043-COMMERCE-002` in commits `da76e49` and `df34338`. The implementation modifies the platform configuration consumers, startup/bootstrap behavior, preview/auth/connection paths, tests and `database` submodule pointer. The follow-up test commit updates Woo server-action fixtures for the DB-backed configuration readers and adds `tests/arch043-authjs-operation-config.test.ts`.

**2026-10-20 consumer-smoke additions applied and locally validated (commit not verified):** `package.json`, `scripts/run-arch043-platform-configuration-disposable.mjs`, `tests/arch043-commerce-consumer-postgres.test.ts`, and `tests/arch043-commerce-consumer-unavailable.test.ts`. These four files must be checked for committed/uncommitted changes in the actual implementation worktree; the older commit IDs above are **not** evidence that the new smoke tests have been committed.

### Work Completed

Migrated the in-scope Commerce preview, Auth.js, connection-security and Merchant Knowledge consumers to the platform configuration service; removed Merchant Knowledge provisioning from startup; added bounded Shared logging and task-focused regression coverage. Auth.js v5 beta.32's installed declaration accepts an async config callback and its runtime awaits it for handler operations. The accepted database submodule pointer reported by the implementation is `2a59fd1646404ba752ce30b15ea3eb1f78cb8f3d` (`ARCH-043-DATABASE-001`).

**2026-10-20 addition:** Implemented and locally exercised a disposable PostgreSQL **consumer** smoke using the real Commerce Auth.js, preview-policy and connection-key consumers, with committed-update visibility, credential rotation/revocation, owned-database shutdown and fail-closed outage behaviour. This evidence is separate from the `COMMERCE-001` configuration-reader PostgreSQL test.

### Validation Results

**Historical Attempt 1 results (before corrections):** Task-focused configuration/Auth.js/startup/preview/Woo REST tests passed (8 files, 69 tests); disposable PostgreSQL ARCH-043 reader integration passed (4/4, cleanup); typecheck, production build, changed-file lint and `git diff --check` passed. The then-unfiltered Vitest suite reported 65 failures across 22 files and repository-wide lint reported two `react-hooks/refs` errors. Those were the reasons for the previous Changes Requested review; the lines are retained as history, not as the most recent results.

**2026-10-20 post-correction validation (developer-provided terminal logs):**

- Direct Auth.js session signing/rotation and revocation regression: **2/2 passed**.
- Isolated Commerce unit suite: **1,477 passed, 0 failed**, 185 passing test files; four other files skipped (11 tests skipped). Seven infrastructure-gated test files were deliberately excluded from this unit-only command, **not** recorded as passing.
- ARCH-043 configuration-reader disposable PostgreSQL integration: **4/4 passed** (earlier local run).
- `npm run test:arch043-commerce-consumer:postgres`: accepted ARCH-043 D001 migration applied; **4/4 consumer tests executed/passed**, zero skipped/failed; owned disposable PostgreSQL shut down; **1/1 outage test executed/passed**, zero skipped/failed; owned-container cleanup passed.
- `npm run typecheck`: **passed**. `npm run lint`: **passed with 0 errors and 15 warnings**. `npm run build`: **passed**, with the non-fatal Nunjucks dynamic-dependency warning. `git diff --check`: **no whitespace errors reported**.

These are local validation results, **not** proof of a new implementation commit, a complete unfiltered infrastructure suite or an Accepted architect review.

### Deviations

None

### Assumptions

The canonical records for `ARCH-043-COMMERCE-001` and `ARCH-043-ADMIN-002` are Complete; both explicit dependencies passed the launcher dependency check before claim.

### Unresolved Issues

**2026-10-20 outstanding procedural evidence:**

- **Implementation SHA not supplied:** The terminal logs confirm smoke execution but do not contain `git rev-parse HEAD`, `git log`, or a commit proving the four consumer-smoke files were committed. In the dedicated Commerce implementation worktree, inspect `git status --short`, commit/push the validated smoke additions **only if still uncommitted**, and record the resulting **full 40-character commit SHA**, branch and clean/diff status here. Do not substitute the earlier `da76e49`/`df34338` commit IDs.
- Record the final launcher-resolved parent/implementation worktree synchronization and `database` submodule/gitlink evidence; confirm the exact reviewed diff and the intended Auth.js fallback/rollback conditions.
- The unit-only suite intentionally excluded **seven infrastructure-gated** test files. The unfiltered full-suite pass is not claimed; preserve the guardrails and use each dedicated disposable test harness or obtain an explicit review disposition where required.
- Reclaim the task through the authorised developer workflow if still `ready`, finish developer self-review, update this Completion Report with actual commit/revision evidence, move to `review` through that workflow and **STOP**. Architect acceptance and explicit developer completion are not automatic.

Historical untracked `pnpm-lock.yaml` and `pnpm-workspace.yaml` from dependency setup remain outside the approved task commits unless their status is separately reconciled.

### Architectural Concerns

None newly identified from the 2026-10-20 validation.

### Final implementation revision and handoff (pending developer evidence)

- **Implementation commit SHA:** PENDING — not present in the supplied validation log.
- **Implementation branch:** `task/ARCH-043-COMMERCE-002` (reported worktree; verify before recording commit).
- **Smoke-test files committed/pushed:** NOT VERIFIED — inspect Git status/log and record the resulting commit here.
- **Database submodule:** `2a59fd1646404ba752ce30b15ea3eb1f78cb8f3d` as reported in the earlier Completion Report; verify the actual checked-out gitlink in the final implementation commit.
- **Developer review/explicit completion:** PENDING; the authoritative task YAML remains `status: ready`, `attempt: 1` and `completion_mode: developer`.

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

Developer Self-Review requires these corrections before another review submission. Keep Attempt 1 history; the next `/moda_developer_create ARCH-043-COMMERCE-002` claim will increment to Attempt 2.

## Developer Self-Review - Changes Requested

### Review Status

Changes Requested

### Corrections Required

- Establish and resolve the cause of the 65 failures in the full Commerce Vitest suite; do not label them baseline without a comparison against the unmodified baseline.
- Resolve or obtain an accepted exception for the two repository lint errors in `src/studio/prompt-editor/markdown-prompt-editor.tsx`; this file is outside the task diff, so do not modify it without task/owner authorization.
- Add direct Auth.js session/signing rotation and revocation regression coverage in addition to testing the async options factory; document the installed Auth.js semantics for sessions created under the previous secret.
- Re-run the full suite, repository lint, focused PostgreSQL integration, typecheck, production build and `git diff --check`; then update this report and submit for Review.

### Validation Reviewed

Task-focused 69/69 tests, disposable PostgreSQL 4/4, typecheck, production build, task-file ESLint and whitespace validation passed. Full-suite and full-repository lint results above remain blocking.

### Attempt

1 (unchanged; executor cleared and status returned to `ready`).

## 17 October 2026 ARCH-043 extension (architect-owned amendment)

Commerce Auth.js reads `auth.commerce` **per authentication operation**, with the complete `AUTH_SECRET`/Google environment bundle used only if the database row is absent. Existing but disabled, invalid or unavailable records fail closed. The independently sealed `commerce.bootstrap.adminEmail` is resolved only when an explicitly requested administrative provisioning operation needs a selector; it never gates Commerce startup or ordinary Merchant Knowledge embedding lookups. Never hardcode a real bootstrap email or treat the selector as proof of principal identity. Database-backed secret use requires the controlled ADMIN-002 writer/import; the approved absent-row Auth.js fallback remains available after cutover. Use only Shared structured logging for these configuration paths.
