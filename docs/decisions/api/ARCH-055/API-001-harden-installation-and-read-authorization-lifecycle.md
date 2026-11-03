---
id: ARCH-055-API-001
architecture_id: ARCH-055
title: Harden installation and REST-read authorisation lifecycle
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 15
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-055-DATABASE-001
enables:
- ARCH-055-API-007
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-03
---

# ARCH-055-API-001: Harden installation and REST-read authorisation lifecycle

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 3. Small acceptance clarification over revision 2; execution metadata, dependencies and migration scope are unchanged.

**Definition state:** materialised. Attempt 1 was accepted by the architect on 3 November 2026. The task is Complete; API-007 is Ready at Attempt 0 and unclaimed, while API-009 and SYSTEM-TEST-001 remain gated by other prerequisites.

## Objective

Deliver one coherent installed-merchant lifecycle boundary covering reconnect, REST-read attempt/grant transitions and the nearby brand write, with protected principal revalidation and bounded redundant reads.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E01`, `E02`, `E07`, `E09`, `E10`, `E11`, `E12`, `E13`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-api`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `src/auth/woo-installation/`
- `src/woocommerce/installation/`
- `src/woocommerce/billing/initial-free-activation.service.ts`
- `src/woocommerce/billing/free-plan-preparation.service.ts`
- `src/woocommerce/shop-brand/`
- `src/woocommerce/rest-read/authorization.service.ts`
- `src/woocommerce/rest-read/authorization.routes.ts`
- `src/woocommerce/rest-read/return-locale-proof.ts`
- `tests/unit/woocommerce/installation/`
- `tests/unit/woocommerce/rest-read/`
- `tests/unit/woocommerce/shop-brand/`
- `tests/integration/woocommerce/installation/`
- `tests/integration/woocommerce/rest-read/`
- `tests/integration/woocommerce/shop-brand/`
- `scripts/test-woocommerce-installation-postgres.mjs`
- `scripts/test-woocommerce-rest-read-authorization-postgres.mjs`
- `scripts/test-arch049-shop-brand-postgres.mjs`

Required new paths (only these are allowed to be absent at startup):

- `src/auth/woo-installation/current-mutation-principal.ts`

Additional explicit registration/module paths for this revision:

- `scripts/test-arch055-installation-postgres.mjs`

### Exact edit map — definition revision 2

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `src/auth/woo-installation/current-mutation-principal.ts` | CREATE the transaction-only helper and error/type exports below; lock Shop FOR UPDATE before installation FOR SHARE, validate exact principal fields and return the locked Shop/onboarding values. No root client or network dependency. |
| `src/woocommerce/installation/connection-service.ts; src/woocommerce/billing/initial-free-activation.service.ts` | MODIFY reconnect to load onboarding with its existing transaction-local Shop read; supply that loaded result to activation. Guard rotation by id/shopId/observed credentialVersion, use a returning update and require exactly one result. Preserve the original observed version over retries and proof outside the transaction. |
| `src/woocommerce/shop-brand/service.ts` | MODIFY first-row creation to use its returned brand fields; retain existing-row locking, source timestamps and media merge logic. |
| `src/woocommerce/rest-read/authorization.service.ts` | MODIFY begin/revoke and callback commit to call the current-principal helper inside their existing/new short transaction. Begin INSERT stays inside that transaction. Revoke updateMany filters installationId/shopId/credentialVersionSnapshot/status=PENDING, with no expiresAt exclusion, and sets FAILED/consumedAt/current existing failureCode; then revokes the current grant atomically. Old-generation attempts are not targeted. Callback constructs the expected principal from its original token-resolved installation snapshot, not from an unauthenticated request body; no network verification inside its commit transaction. |
| `src/woocommerce/rest-read/authorization.service.ts; src/woocommerce/rest-read/authorization.routes.ts` | MODIFY callback lost-consumption/P2034 handling: end the failed transaction, reload token-bound attempt and its currently selected grant; acknowledge only a matching SUCCEEDED attempt with matching selected authorizationAttemptId/shop/install binding. Do not rotate/mint on acknowledgement; a revoked matching grant may be acknowledged without reactivation. Superseded/missing/mismatched evidence remains the existing conflict. Recognised domain errors retain safe statuses; actual database/provider failures retain original causes. |
| `scripts/test-arch055-installation-postgres.mjs` | CREATE an installation-only canonical migrate-deploy runner using the existing disposable pg17 harness pattern; run existing connection-service suite plus the new principal race suite. Do not convert the shared db-push runner while API-003 fixtures are unfinished. |

**Exact new implementation/test paths (not baseline files claimed to exist):**

- `src/auth/woo-installation/current-mutation-principal.ts`
- `scripts/test-arch055-installation-postgres.mjs`
- `tests/unit/auth/woo-installation/current-mutation-principal.test.ts`
- `tests/integration/woocommerce/installation/arch055-principal-races.postgres.test.ts`
- `tests/integration/woocommerce/rest-read/arch055-lifecycle-races.postgres.test.ts`

**Test registration:** Add principal-races to new scripts/test-arch055-installation-postgres.mjs and lifecycle-races to scripts/test-woocommerce-rest-read-authorization-postgres.mjs. Add the new unit file explicitly to this task Validation. Existing brand runner remains.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Implement ADR-01/04. Add the API-local current-mutation-principal port specified below. Lock Shop first, then the installation; validate canonical URL, shop binding, platform, Shop ACTIVE, installation ACTIVE/unrevoked and expected credential version. Return transaction-local Shop fields for callers; no root-client query or network operation is allowed in this helper. ARCH-055-API-007 consumes it later.

2. Reconnect: reuse the transaction-local Shop/onboarding result in Free activation, and use a guarded returning update for credential rotation. Keep the pre-proof observed-version CAS, Serializable retry policy, exact Free lifetime grant, paid-subscription preservation and site-control proof outside transactions. Narrow warm Free-plan feature projections to consumed fields; lazy extra cold-path loading is evidence-only until an architect amendment; do not remove transaction-local policy/catalogue rechecks.

3. Brand first creation: use the create result instead of immediately selecting it again. Preserve source ordering, worker-maintained media JSON, first-writer coordination, current installation check and writes that advance genuinely newer observation timestamps.

4. REST begin/revoke: validate the current principal in the mutation transaction. Revoke only the current generation's still-PENDING attempts; terminal FAILED cancellation must not fail solely because expiry elapsed while waiting. Leave already-unusable old-generation attempts out of the cancellation set. Cancel attempts and revoke the selected grant atomically; never claim provider-side key deletion.

5. Callback: provider verification remains outside the transaction. Revalidate lifecycle/version in API service code when committing; retain existing Database mint guards without adding new policy triggers; recognise a completed matching replay after a conditional-consumption or serialization race without issuing another grant or rotating a revoked one. Superseded/mismatched attempts remain conflicts. Correct overlap acknowledgement without returning success for all failures.

6. Begin/callback/revoke errors retain actual Prisma/provider causes and distinguish invalid/stale requests from unexpected dependency failures. Generic 409/503 output does not justify discarding diagnostics. Return-page impossible-proof preflight may avoid configuration reads only if it reuses existing parser rules.

7. Keep GET installation at one authenticated lookup and REST status non-locking. Measure latest-attempt ordering plans; do not add its proposed index without separate architect approval. Catalogue/status projections may be narrowed, not credential-cached.

8. Use the new installation-only canonical runner specified below and adjust its fixtures to actual constraints. Do not convert the shared old runner while category/bootstrap fixtures are unfinished; API-003 supplies its separate canonical runner and API-009 reconciles the aggregate.

### Evidence-only choices and exact scope precedence

The exact edit map selects the mandatory implementation pattern for this revision. All earlier wording such as MEASURE-FIRST, MEASURE/DECIDE, "may", "only after SQL validation" or optional batching/index/lock alternatives means **measure and retain the baseline in this task** unless the exact map explicitly selects that change. Return evidence/recommendation for a later architect amendment; the executor does not invent a third alternative or silently broaden the acceptance contract. Schema changes are authorised only by DATABASE-001's exact SQL. New source/test files are only the named additions; unexpected paths, missing pinned capabilities or migration-name conflicts are stop-and-report conditions.

### Common execution and safety contract

- Read this task, the parent architecture, `docs/observability/shared-logging.md` and the four workspace VCS/worktree/developer/materialisation policies. Use the launcher-resolved dedicated parent and implementation worktrees; do not invent paths or start another task. A prepared launcher packet is accepted startup evidence.
- Use the existing Node/toolchain. Before the first Node command: `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`. Do not select/install a different Node version to make validation appear to pass.
- All workspace edits use repository-relative paths. Never edit another repository's implementation or a nested Database schema copy. A consumer records/updates only its own accepted nested Database pin under the task contract; never stage the parent workspace gitlink to an unmerged implementation commit.
- Shared logging is `@modainteract/moda-interact-shared/logging`. Preserve the actual original Prisma/SDK/provider message, code, cause and relevant safe response details through typed errors. Internal reason codes supplement, never replace, that evidence. Redact secrets, signed capabilities, customer content and connection URLs; public responses stay bounded. No generic local logger or duplicate framework telemetry.
- Preserve tenant scoping, canonical Shared schemas, immutable evidence, deliberate no-op/replay rules and original provider ambiguity. No provider/Redis/R2 I/O inside a database transaction. Read endpoints remain free of writes unless an explicitly unchanged contract says otherwise.
- Review baseline observations are static. Run regression tests against canonical migrations on disposable PostgreSQL 17 + pgvector, using separate connections and explicit barriers for races. Do not substitute mocks, `db push` or review-only Python models for lock/trigger proof.
- For each mandatory optimisation capture before/after actual SQL and affected rows on the same fixtures; distinguish client calls, SQL statements and row/byte changes. State workload and measurement limits. MEASURE-FIRST/MEASURE-DECIDE items are evidence-only in this revision: retain baseline behaviour, record the named experiment and recommend to the architect; do not implement an optional alternative without a separate scope amendment; mandatory correctness changes cannot be deferred this way.
- Existing baseline failures are handled through `docs/development-baseline.md` only when actually encountered and relevant. Do not waive new regressions. Record commands actually executed and leave unavailable validations unchecked.
- Do not edit any `docs/decisions/**/_index.md`, old task status, the parent architecture, another task or shared execution rollup from a repository implementation task. Parent report updates are confined to this task file. No merge or push to main.

## Work Items

- [x] Implement the transaction-only current-principal helper and integration tests.
- [x] Correct revoke/callback schedules and original-error boundaries before optional query changes.
- [x] Consolidate reconnect and brand create-result reads with full rollback/replay tests.
- [x] Use migrated installation/authorisation fixtures; test overlap callbacks, old pending attempt + reconnect + new grant + revoke, stale authenticated revoke, expiry while waiting, suspension during verification, and post-revoke replay.
- [x] Measure warm/cold connection paths and report latest-attempt query plans without speculative index DDL.

## Interfaces / Contracts

New API-local file `src/auth/woo-installation/current-mutation-principal.ts`: export `requireCurrentWooMutationPrincipal(tx: Prisma.TransactionClient, principal: WooInstallationPrincipal): Promise<CurrentWooMutationPrincipal>`. The returned readonly projection contains `shopId`, `installationId`, `credentialVersion`, `canonicalSiteUrl`, `shopDomain` and `onboardingCompleted`. It accepts only a transaction client and always requires ACTIVE mutation eligibility. Use an exported typed conflict error with original cause where applicable; callers map it to their existing safe public contract. This helper is not for suspended-Shop Support GETs, pure authentication probes or unauthenticated connect proof.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

```ts
export type CurrentWooMutationPrincipal = Readonly<{
  shopId: string;
  installationId: string;
  credentialVersion: number;
  canonicalSiteUrl: string;
  shopDomain: string;
  onboardingCompleted: boolean;
}>;
export declare class WooMutationPrincipalConflictError extends Error {
  readonly code: "woo_mutation_principal_stale";
  constructor(options?: ErrorOptions);
}
export declare function requireCurrentWooMutationPrincipal(
  tx: Prisma.TransactionClient,
  principal: WooInstallationPrincipal,
): Promise<CurrentWooMutationPrincipal>;
```
Validation is Shop.id=principal.shopId, domain=canonicalSiteUrl, platform=WOOCOMMERCE, shopifyShopId=null, status=ACTIVE; installation.id/shopId/canonicalSiteUrl/credentialVersion equal the principal, status=ACTIVE and revokedAt=null. Return only the listed fields. Known mismatch throws the typed conflict; unexpected Prisma errors propagate unchanged. Caller maps only this conflict according to the exact revision-3 table below; API-007 defines its billing mappings in its own task. Never use this helper for suspended-Shop Support reads or unauthenticated connection proof.

### Exact public outcomes for the new principal gate — revision 3

Scope: the `WooMutationPrincipalConflictError` introduced by this task, not a blanket change to unrelated domain-error mapping. Existing public vocabulary comes from `src/woocommerce/rest-read/authorization.service.ts` and `authorization.routes.ts:210–230` in the source snapshot. The mapping of the NEW transaction-local failure to that vocabulary is fixed here. Missing/mismatched Shop or installation, suspended/non-ACTIVE lifecycle, non-null revocation, wrong binding/domain/platform or credential-version mismatch all produce the same bounded gate response. Do not disclose which comparison failed to the caller.

| Operation / condition | Exact HTTP result | Commit and provider boundary |
|---|---|---|
| POST `/v1/woocommerce/read-authorizations`: helper rejects after successful HTTP authentication | `409`, JSON `{"error":"shop_unavailable"}` | Roll back; no new attempt; no provider verification call. Secret/configuration reads already made are not provider HTTP calls. |
| DELETE `/v1/woocommerce/read-authorization`: helper rejects | `409`, JSON `{"error":"shop_unavailable"}` | No attempt cancellation or grant revocation commits; no provider call. |
| POST callback: original token-bound principal fails the committing helper | `409`, JSON `{"error":"shop_unavailable"}` | No attempt consumption or grant rotation commits. One verification may already have completed outside the transaction; do not repeat it because admission failed. |
| An unexpected database exception originates in a helper read (not a typed principal mismatch or an already recognised retryable/domain conflict) | `500`, JSON `{"error":"internal_error"}` | Roll back admission. Propagate the actual exception unchanged to existing error logging; do not turn every database exception into `shop_unavailable` or `authorization_conflict`. |
| Installed request rejected by HTTP authentication before the service runs | `401`, JSON `{"error":"unauthorized"}` | No service mutation or provider verification. This row does not add installation-header authentication to the bearer-token callback. |
| Callback conditional-consumption loser resolves matching, durably SUCCEEDED attempt/current selected-grant binding as specified by revision 2 | `200`, empty body (NOT `204`) | Acknowledge persisted result only; no second grant/rotation. Matching revoked grant stays revoked; superseded/missing/mismatched binding remains `409`, JSON `{"error":"authorization_conflict"}`. |

Implement the three gate mappings in `authorization.service.ts`: catch only `instanceof WooMutationPrincipalConflictError` and wrap as `WooReadAuthorizationError(409, "shop_unavailable", { cause: error })`. Append an optional `ErrorOptions` argument to that existing domain-error constructor and pass it to `super`; preserve all existing two-argument callers. Keep the helper's internal `woo_mutation_principal_stale` code in its cause, not as a new public error code. Unexpected failures must not be swallowed by the callback's outer catch. Existing known expiry, token, permissions, provider-verification and bounded serialization-retry mappings remain unchanged; this clarification does not redefine them.

Extend `tests/unit/woocommerce/rest-read/authorization.routes.test.ts` for exact status/body and safe logging. In the already named principal/lifecycle PostgreSQL files, authenticate or resolve the valid callback token, pause before the helper, rotate/revoke/suspend using the other connection, then resume. Assert no new committed attempt/grant mutation and the table result. For the callback variant, release the verifier BEFORE the pause and assert exactly one verification, with none on acknowledgement/retry. Inject an unexpected helper-read exception separately and assert 500 plus preserved cause, not a guessed principal conflict. Keep request body/security headers and logging redaction unchanged; no new public DTO.

## Dependencies

- `ARCH-055-DATABASE-001` must have `status: complete` and an accepted review.

## Enables

- `ARCH-055-API-007`
- `ARCH-055-API-009`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Stale authenticated mutations cannot operate on a newer installed generation.
- [x] Current-generation revocation succeeds despite unusable old pending attempts and expiry during waiting; all writes still roll back together on genuine failure.
- [x] Matching concurrent successful callbacks acknowledge the same durable outcome without reactivation or duplicate grant.
- [x] Reconnect preserves subscription, lifetime balances and observed-version concurrency.
- [x] Baseline 5-call active reconnect -> 3 and 7-call first-brand -> 6 are verified as client-call targets, separately from SQL counts.
- [x] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [x] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [x] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| A01 | Authenticate/token-resolve, pause before the helper; rotate/revoke/suspend, then resume start/revoke/callback commit | Exact revision-3 table: 409 shop_unavailable, no new mutation; callback may have one prior verification but no repeat. Unexpected helper-read failure is 500 internal_error, not a principal mismatch. |
| A02 | Expired current-generation pending attempt + new current grant; revoke | Attempt FAILED and grant REVOKED commit together; failed timestamp is current, not forged to expiry; old-generation pending rows do not block. |
| A03 | Two callbacks both observe PENDING before verification | One grant/consumption; matching loser receives replay acknowledgement; no duplicate rotation. Superseded and mismatch losers remain conflict. |
| A04 | Reconnect active/onboarded and uninstalled/onboarded with late activation failure | One transaction-local Shop read and returning credential result; all original paid/free balances and rollback preserved. |
| A05 | First brand create, stale/exact/newer same-image observation | No immediate create reread; exact/stale writes suppressed as before, newer timestamp still advances. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [x] `npm run prisma:generate`
- [x] `npx tsx --test "tests/unit/woocommerce/installation/*.test.ts" "tests/unit/woocommerce/rest-read/*.test.ts" "tests/unit/woocommerce/shop-brand/*.test.ts"` (102 passed)
- [x] `node scripts/test-arch055-installation-postgres.mjs` (17 passed)
- [x] `node scripts/test-woocommerce-rest-read-authorization-postgres.mjs` (9 passed)
- [x] `node scripts/test-arch049-shop-brand-postgres.mjs` (4 passed)
- [x] `npx tsx --test tests/unit/auth/woo-installation/current-mutation-principal.test.ts` (3 passed)
- [x] `npm run typecheck`
- [x] `git diff --check`
- [x] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files. (One existing `src/merchant/support/routes.ts:75` `no-empty` error.)
- [x] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

- [x] Assert every revision-3 gate/replay row using the named route and migrated principal/lifecycle tests; record exact HTTP body, committed rows and verifier count.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

ARCH-055-API-007 must consume this reviewed helper rather than recreate it. Preserve existing original task acceptance/history; all corrections are recorded under ARCH-055.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report

### Status

Accepted — Attempt 1. Architect review found the implementation and required PostgreSQL evidence conform to this task's frozen contract. Required unit and PostgreSQL suites, Prisma generation, typecheck, changed-file lint, and diff checks pass. Repository-wide lint retains one unrelated existing error in untouched `src/merchant/support/routes.ts:75`. API-007 is promoted to Ready because API-001 was its only prerequisite; API-009 and SYSTEM-TEST-001 remain gated on other prerequisites.

### Files Changed

Implementation repository: `src/auth/woo-installation/current-mutation-principal.ts`; `src/woocommerce/installation/connection-service.ts`; `src/woocommerce/billing/initial-free-activation.service.ts`; `src/woocommerce/shop-brand/service.ts`; `src/woocommerce/rest-read/authorization.service.ts`; `scripts/test-arch055-installation-postgres.mjs`; `scripts/test-woocommerce-rest-read-authorization-postgres.mjs`; focused unit and PostgreSQL integration tests under `tests/unit/auth/woo-installation/`, `tests/unit/woocommerce/{billing,installation,rest-read,shop-brand}/`, and `tests/integration/woocommerce/{installation,rest-read}/`.

### Work Completed

Implemented transaction-only current-principal validation with Shop-then-installation lock ordering; reconnect now reuses the transaction-local Shop projection and guards credential rotation with `updateManyAndReturn`; first ShopBrand creation returns its selected projection without a second row read; REST start, revoke and callback commits revalidate the token/request-bound principal. Callback replay remains bound to the selected attempt/grant, including revoked grants. Revoke scopes pending cancellation to the current credential generation and terminalises expired attempts under the accepted ARCH-055 Database guard correction.

Added deterministic PostgreSQL race coverage for stale start/revoke, rotation and suspension during callback verification, overlapping callback replay, and expiry while revoke is observed waiting on a separately held attempt-row lock. Updated the installation Free-plan fixture to satisfy the canonical zero-based catalogue position and exact 20-locale translation invariant. The implementation worktree's nested Database dependency is pinned to accepted commit `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`.

### Validation Results

Passed:

- `npm run prisma:generate` (also executed by `npm run typecheck`) and `npm run typecheck`.
- Required installation, REST-read and ShopBrand unit command: 102 passed, 0 failed. Principal-helper unit suite: 3 passed, 0 failed. Additional reconnect/activation focused suites: 22 passed, 0 failed.
- `node scripts/test-arch055-installation-postgres.mjs`: 17 passed, 0 failed on disposable PostgreSQL 17 + pgvector with canonical `migrate deploy` and the accepted Database pin.
- `node scripts/test-woocommerce-rest-read-authorization-postgres.mjs`: 9 passed, 0 failed on canonical migrations, including actual expiry-during-row-lock-wait and injected atomic-rollback cases plus 256-attempt plan capture.
- `node scripts/test-arch049-shop-brand-postgres.mjs`: 4 passed, 0 failed on canonical migrations.
- Changed-file ESLint, `npm run typecheck`, Prisma generation, and `git diff --check` passed. Full `npm run lint` was run and reports only the unrelated existing `src/merchant/support/routes.ts:75` `no-empty` error; that out-of-scope file was not changed.

Revision-3 public gate/replay evidence: route tests assert stale-principal `POST /v1/woocommerce/read-authorizations`, `DELETE /v1/woocommerce/read-authorization`, and callback responses are exactly HTTP `409` with `{"error":"shop_unavailable"}`. Unexpected service/helper failure is HTTP `500` with `{"error":"internal_error"}` and its original diagnostic is retained in logs; stale callback token and provider secrets are absent from logs. Successful callback response is HTTP `200` with an empty body. The migrated principal-race tests assert stale start/revoke/callback commits leave attempts and grants unchanged; callback verification occurs exactly once before a stale callback gate rejects. Concurrent matching callbacks both complete after one verification per invocation (two total), but only one durable grant/rotation is created. Duplicate callback after local revoke leaves the matching grant REVOKED; superseded attempts conflict. Current-generation expiry while waiting commits FAILED with a current cancellation timestamp alongside grant revocation; injected second-write failure leaves attempt PENDING and grant ACTIVE, proving transaction rollback. Exact final REST runner result: 9 passed, 0 failed.

Measured same-fixture SQL evidence (Prisma query events, parameterized SQL only; BEGIN/COMMIT and transaction setup excluded):

| Operation | Baseline SQL statements | Current SQL statements | SQL delta | Baseline affected/returned rows | Current affected/returned rows |
|---|---:|---:|---:|---|---|
| Already-onboarded ACTIVE reconnect | 6 | 4 | -2 | Credential UPDATE affected 1; follow-up SELECT returned 1 | Guarded UPDATE RETURNING returned 1 |
| First ShopBrand creation | 8 | 7 | -1 | INSERT returned 1; immediate lock reread returned 1; brand UPDATE affected 1 | INSERT projection returned 1; brand UPDATE affected 1 |

Baseline and current paths ran sequentially against the same disposable migrated PostgreSQL fixture per test, restoring the original installation digest/version and deleting the temporary brand row between paths. The reconnect SQL output shows the baseline relation projection split into two statements; source-level Prisma model-call counts are separately 5 to 3, not SQL round trips. ShopBrand source-level client calls are 7 to 6, while actual SQL is 8 to 7. No transaction-control, trigger-internal or network work is included. Both paths preserve one credential row update and one ShopBrand row insert/update; the improvement removes only the redundant result fetch, with no affected-row reduction claimed.

Client-call acceptance evidence: ACTIVE reconnect unit assertions verify the current 3 model calls against the review-ledger baseline of 5; first ShopBrand creation verifies 6 against baseline 7. The measured SQL counts are separately 6 to 4 and 8 to 7, respectively, because a Prisma relation projection expands to multiple SQL statements. Reconnect activation also asserts no duplicate Shop lookup when given the current projection.

Latest-attempt plan evidence: on 256 seeded historical attempts in the canonical disposable database, `EXPLAIN (ANALYZE, BUFFERS)` selected a backward scan of the existing unique `attemptSequence` index with `installationId` and `shopId` filters, returned one row, reported 2 shared-buffer hits and 0.110 ms execution time in the final run. No index was added. This small disposable workload is not a production benchmark. No latency or write-byte reduction is inferred from these local captures.

### Worktree and Git Evidence

Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-001`, branch `task/ARCH-055-API-001`. The report submission commit was `0adb22a31`; the architect acceptance update is being committed on this branch. Before acceptance, the parent task branch incorporated `origin/main` through merge commit `57d498b1a`, including the intervening Background-001 and API-005 task updates. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-001`, branch `task/ARCH-055-API-001`, implementation commit `9aa3c3d7f9cc21f646181c9d30b69b7c692c8a38` pushed to `origin/task/ARCH-055-API-001`. At review, the implementation branch was four commits behind current `origin/main`; the intervening API-005 merge changed no files overlapping this task's lifecycle edits, so no unrelated merge was introduced. Nested Database worktree is clean at accepted pin `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. Disposable PostgreSQL runners remove their containers in `finally`; final installation, REST, and ShopBrand runs all exited successfully. No merge to main was attempted.

### Deviations

None. The additional latest-attempt plan test is within the named REST lifecycle integration file and adds no schema/index change. The full-lint Support error is outside this task and was not modified.

### Assumptions

The uploaded source snapshot is the design baseline, not proof of current remote state. Reconcile only relevant drift on the real launcher baseline; return contract-changing drift to the architect.

### Unresolved Issues

No implementation or acceptance gap remains. The unrelated full-repository Support lint failure remains with its owning task. The task is submitted for architect review; no merge to main is authorised.

### Architectural Concerns

No schema, ownership, or transaction-boundary concern identified. The latest-attempt plan's backward unique-index scan is evidence for this 256-row disposable fixture only; retain the current schema and defer index decisions pending representative-volume evidence.

## Architect Review

### Review Status

Accepted — Attempt 1. Task status is Complete; attempt number remains 1.

### Review Notes

The implementation uses the transaction-only Shop-then-installation principal lock, preserves the existing Free/paid lifecycle boundaries, guards reconnect by the observed credential version, cancels only current-generation pending attempts, and acknowledges only a matching durable callback/grant outcome. It preserves provider verification outside transactions and original error causes. ShopBrand uses its create projection and retains newer observation timestamps. No material deviation from the selected architecture was found.

### Reviewed Files

`src/auth/woo-installation/current-mutation-principal.ts`; `src/woocommerce/installation/connection-service.ts`; `src/woocommerce/billing/initial-free-activation.service.ts`; `src/woocommerce/shop-brand/service.ts`; `src/woocommerce/rest-read/authorization.service.ts`; the new installation runner; and the named unit/PostgreSQL race suites and runner registrations.

### Validation Reviewed

Reviewed submitted results: 102 required unit tests, 3 principal-helper tests, PostgreSQL suites 17/17, 9/9 and 4/4, Prisma generation, typecheck and changed-file lint passed. Same-fixture SQL counts fell from 6 to 4 for reconnect and 8 to 7 for first ShopBrand creation, with rows preserved. Repository-wide lint reports one existing error at untouched `src/merchant/support/routes.ts:75`. These commands were not rerun during architect review.

### Architecture Conformance

Accepted against ARCH-055 revision 3 and this task's definition revision 3. No schema/migration changes or speculative indexes were added. The accepted Database pin is recorded. No deployment or live-provider certification is implied.

### Follow-up

ARCH-055-API-007 is Ready at Attempt 0, unclaimed, because API-001 was its only prerequisite. API-009 remains Pending on API-002/003/004/005/006/007/008; SYSTEM-TEST-001 remains Pending on its remaining implementation prerequisites. No other downstream task is promoted.


## Dependency readiness — 3 November 2026

ARCH-055-DATABASE-001 is Accepted and Complete at Attempt 2 with pin `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`; API-001 consumed that pin within its authorized scope. API-001 is Complete at Attempt 1. API-007 is Ready at Attempt 0, unclaimed. API-009 remains Pending on API-002/003/004/005/006/007/008, and SYSTEM-TEST-001 remains Pending on the remaining cross-service implementation dependencies. Acceptance does not imply deployment, production migration or integrated system-test completion.
