---
id: ARCH-035-API-022
architecture_id: ARCH-035
title: Expose authoritative WooCommerce usage history and entitlement periods
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 35
executor: null
claimed_at: null
attempt: 3
depends_on: []
enables:
  - ARCH-035-WOOCOMMERCE-018
created: 2026-10-22
updated: 2026-10-22
---
# ARCH-035-API-022: Expose authoritative WooCommerce usage history and entitlement periods

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Historical `ARCH-035-API-007` remains Superseded; this contract matches the **completed** Usage History UI instead of its incompatible original query shape.
- Reference: `moda-interact/app/services/usage/history.server.ts`, `app/components/dashboard/UsageEvents.tsx`.

## Objective

Expose real, merchant-safe WooCommerce usage events and current/past Moda entitlement periods from existing billing records, with correct Free-plan behaviour and reliable paging.

## Context

`ARCH-035-WOOCOMMERCE-006` is Complete as UI-only. `src/usage-history/usage-history-client.js` explicitly sets `available:false`. Its controller expects `usageEvents`, `usagePagination` and `periodPage` with period cursors; the old superseded API-007 contract does not match that UI.

## Scope

- Implement authenticated GET route, request/response validation, service, OpenAPI, route registration, focused unit/integration tests and shared structured logging in `moda-interact-api`.
- Read existing `UsageEvent`, `BillingPeriod`, `Subscription`, `CheckoutRecovery` (for safe optional source link) and applicable purchased/promotional credit context. No new schema or usage-recording writes.
- Use provider-neutral period/cursor/paging semantics where appropriate. The new read boundary is WooCommerce installation-authenticated and does not depend on the Shopify application or its tests.

## Out of Scope

- Changes to payment/purchase-history behaviour, Woo subscription charging, new usage consumption or refunds, changes to UsageEvent writers, new migrations, WordPress proxy/UI implementation or `_index.md` files.
- Shopify application routes, Billing UI, source changes, and running any Shopify repository regression suites are **out of scope**. API-local regression validation may cover existing WooCommerce purchase-history and billing-read endpoints affected by shared API route composition.

## Requirements

1. Hosted `GET /v1/merchant/usage-history?view=current|past&periodId=<opaque>&kind=ALL|RECOVERY_CONVERSATION&page=1&pageSize=10&periodCursor=<opaque>` is installation-authenticated, tenant-derived and read-only; no `shopId` parameter. Supported page sizes **10, 25, 50, 100**; page 1–1000; period cursor ≤1024 URL-safe chars; period ID ≤128 bounded chars. Reject unknown/duplicate filter parameters, malformed dates/IDs, foreign periods and cursors with stable `400`/`409` responses rather than silently falling back.
2. Return `{schemaVersion:1,state:'ready'|'unavailable',usageView:'current'|'past',periodPage,usageEvents,usagePagination}` with ISO dates and authoritative numeric totals. `periodPage:{items:[{id,periodStart,periodEnd}],previousCursor:null|string,nextCursor:null|string}` (max 25 periods). `usagePagination:{page,pageSize,total,totalQuantity,billId:null|string,periodStart:null|string,periodEnd:null|string}`. `usageEvents:[{id,metric,quantity,occurredAt,sourceRecovery:null|{recoveryId,customerName}}]`. The optional `customerName` must be supplied **only** when the linked recovery and customer are confirmed to belong to the authenticated Shop; otherwise `sourceRecovery:null`.
3. `current` for a paid Shop selects the currently applicable Moda entitlement `BillingPeriod`/30-day entitlement window; `past` selects closed Shop-owned periods. Woo payment-provider billing month is not the Moda entitlement interval. Period list/cursor identity and sort use `(periodStart DESC,id DESC)`; usage rows use `(occurredAt DESC,id DESC)`. Cursors are scoped to Shop and view, and tampered/cross-Shop tokens are rejected. Correct offsets/caps prevent unbounded data retrieval.
4. **Free lifetime:** if no real BillingPeriod exists, `current` reads genuine Shop-owned unperiodised Free-plan recovery usage events without manufacturing a BillingPeriod ID; `past` is empty unless real historical periods exist. A paid Shop without a qualifying current period yields explicit empty/unavailable state rather than reading all history. No `0` invented for unavailable data.
5. Usage rows read only matching `shopId` and provider `WOOCOMMERCE` or explicitly valid provider-neutral history. Do not include another provider's Shop or Shopify-report-only data. Real correction/compensation records retain their semantics/sign; totalQuantity must reflect the selected event set. Never invent charges or omit compensating entries merely to make totals positive.
6. No raw provider billing IDs, idempotency keys, sensitive source payload, PSP event handles, Meta/Shopify secret data or cross-Shop customer details in response or logs. Use bounded selects, no-store response, runtime DTO validation, API-owned OpenAPI and shared logging.

## Work Items

- [x] Confirm `UsageEvent`/`BillingPeriod` schema, legitimate provider-neutral rows and Free lifecycle behaviour in current code.
- [x] Implement tenant-scoped period selection, pagination and current/Free rules.
- [x] Implement usage event read and same-Shop recovery linking, with safe correction handling.
- [x] Add strict request/response schema, API route registration, OpenAPI and error mapping.
- [x] Test negative, period, provider, Free, billing-cadence, paging and correction paths.

## Interfaces / Contracts

- Contract owner: `moda-interact-api`; consumer is `ARCH-035-WOOCOMMERCE-018` via the approved WordPress PHP client/proxy.
- Existing database: `billing.UsageEvent`, `billing.BillingPeriod` and `commerce.CheckoutRecovery`. No Shared queue/writer contract changes.
- Controller/view model must match `src/usage-history/{usage-history-controller,usage-history-toolbar,usage-history-results}.js`.

## Dependencies

None. Existing Woo installation and Billing schema foundations are recorded Complete; verify repository pins when claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-018`.

## Acceptance Criteria

- [x] Real Free-lifetime, paid current/past, cancellation/history, empty, correction/compensation and period pagination cases return correct event sets and totals. (Attempt 2 developer run: 15/15 focused unit tests and 2/2 disposable PostgreSQL integration tests, including cancellation and late signed corrections.)
- [x] Shop crossover, tampered cursor, foreign period, malformed filters, incorrect platform and disabled/revoked installation produce safe nonleaking errors.
- [x] Correct same-Shop recovery links, stable chronological ordering, 10/25/50/100 paging and 25-period cursor semantics.
- [x] Existing WooCommerce **API** purchase-history and billing-read routes remain unaffected; the new endpoint retains OpenAPI, shared logging and no-store handling. Attempt 3 `npm test` passed **570/570**, including purchase-history, billing-read, route-composition, integration-runner and usage-history route/contract coverage. **No Shopify application regression suite is required.**

## Validation

- [x] Focused unit/route and disposable DB tests including period-boundary/Free/correction/tenant/provider cases.
- [x] Repository-declared typecheck, lint, build and **API-local** regression tests (`npm test`), including WooCommerce purchase-history and route-registration coverage. Attempt 3: unit **15/15**, PostgreSQL **2/2**, full API **570/570**, typecheck, lint (zero warnings) and build all passed. No Shopify repository tests are required.
- [x] `git diff --check`, launcher-resolved worktree/commit evidence and Completion Report. Attempt 3 launcher preparation passed: canonical worktrees were reused, both branches were already current with `origin/main`, recursive submodule sync/update passed, and the claim was committed and pushed. Current implementation and parent branches are clean and identical to their remotes.

## Stop Condition

Set `status: review` with real tests and stop; API-022 does not implement the Woo plugin consumer.

## Implementation Notes

Prefer small route, period-cursor, query and projection modules. Distinguish `occurredAt` from database insertion time; never mislabel a Woo billing cycle as a 30-day entitlement period. If genuine Free usage storage contradicts the historical task description, report exact evidence before altering domain accounting.

## Completion Report

### Status

Ready for Architect Review — developer Attempt 3 (2026-10-22). All task-specific validations pass, the canonical launcher preparation packet is recorded, and implementation/parent branches are clean and published. Attempt 1/2 review history is preserved below.

### Files Changed

Implementation files in `moda-interact-api` (original implementation plus incremental cancellation coverage; the latest synced API snapshot already contains the registration corrections, so the attempted stale Attempt 3 patch was not applied):

- `openapi/merchant-usage-history-v1.yaml`
- `package.json`
- `scripts/test-arch035-usage-history-postgres.mjs`
- `src/composition/merchant.ts`
- `src/merchant/usage-history/contract.ts`
- `src/merchant/usage-history/cursor.ts`
- `src/merchant/usage-history/history.service.ts`
- `src/merchant/usage-history/periods.ts`
- `src/merchant/usage-history/routes.ts`
- `src/merchant/usage-history/schema.ts`
- `src/merchant/usage-history/sources.ts`
- `tests/integration/merchant/usage-history/usage-history.postgres.test.ts`
- `tests/unit/composition/real-route-registration.test.ts`
- `tests/unit/merchant/usage-history/contract.test.ts`
- `tests/unit/merchant/usage-history/cursor.test.ts`
- `tests/unit/merchant/usage-history/history.service.test.ts`
- `tests/unit/merchant/usage-history/openapi.test.ts`
- `tests/unit/merchant/usage-history/periods.test.ts`
- `tests/unit/merchant/usage-history/routes.test.ts`

Parent workspace update: **only this task definition / Completion Report**. No migrations, WooCommerce UI/proxy code, Shopify usage route, purchase-history implementation or domain `_index.md` file is changed by these patches.

### Work Completed

- Added read-only, installation-authenticated `GET /v1/merchant/usage-history` with strict filter/query parsing, response validation, no-store handling, privacy-safe errors, OpenAPI, route registration and shared structured logging.
- Added Shop-scoped Free lifetime reads for genuine unperiodised usage, paid current/past Moda entitlement-period selection, signed and scoped keyset cursors (25 historical periods per page), and stable event paging (10/25/50/100).
- Added WooCommerce-only usage filtering, purchased/promotional credits, signed correction inclusion and authoritative quantity totals, and same-Shop-only recovery/customer details.
- Added focused unit, contract, route, cursor, OpenAPI and disposable PostgreSQL tests.
- **Attempt 2 correction authored and executed:** added an explicit cancelled-subscription unit test and PostgreSQL scenario. Both assert historical CLOSED entitlement-period visibility and signed totals after the recurring contract ends; the database scenario additionally tests cancellation scheduled while the paid period remains valid and a correction recorded after period close.
- Applied the incremental patch revision to resolve overlapping historical test fixtures, nullable/response TypeScript issues and test ESLint errors. Git commits/review attempts do not map 1:1 to patch revision numbers.
- **Attempt 3 registration reconciliation:** the supplied current API snapshot already expects 18 merchant route factories and 25 composed handlers, includes `/v1/merchant/usage-history` in protected-route assertions, and registers the WooCommerce Support and usage-history integration runners once each. The obsolete 17-route / 24-handler correction patch failed context checks and was **not** applied. No extra production code changes were needed for these corrections.

### Validation Results

**Attempt 3 evidence:** developer transcript `typescript(20261022-113400)` (recording of 22 October 2026, approximately 12:28–12:33 UK time):

- `npm run test:arch035-usage-history:unit`: **15/15 passed**, including cancelled-subscription history.
- `npm run test:arch035-usage-history:postgres`: **2/2 passed** on disposable PostgreSQL, with **58 migrations** applied.
- `npm test`: **570/570 passed**, including existing WooCommerce purchase-history/billing-read tests, route-composition registration and `every integration suite is registered once in the default disposable runner chain`. These assertions verify runner registration; the log does **not** show execution of the entire `npm run test:integration` chain.
- `npm run typecheck`: **passed**, after Prisma Client generation.
- `npm run lint`: **passed** (`eslint . --max-warnings=0`).
- `npm run build`: **passed**, including Prisma Client generation and TypeScript compilation.
- `npm run test:integration`: **completed successfully** on the synchronized Attempt 3 worktree; disposable PostgreSQL runner output reported all executed tests passing, including the usage-history runner.
- `git status --short`: **no entries printed** after removing a generated terminal recording; `git diff --check`: **no diagnostics printed**. Implementation `HEAD` and remote both resolve to `70a7642edbdbcfbe714bc9555b190759bb39fb62`; parent report `HEAD` and remote both resolve to `86857aed42001ec36008d59470d887bb11089b00`.
- The two failed registration assertions from Attempt 2 no longer fail. There is no remaining code/test failure in this transcript. The Shopify application was not tested because it is out of scope.

**Historical Attempt 2 evidence:** developer transcript `typescript(20261022-105614)`, 22 October 2026:

- `npm run test:arch035-usage-history:unit`: **15/15 passed**, including cancellation-history coverage.
- `npm run test:arch035-usage-history:postgres`: **2/2 passed**, including historical CLOSED periods and signed late corrections; 58 migrations applied to the disposable test database.
- `npm test`: **557/559 passed; 2 failed**, both in the API repository: `tests/unit/composition/real-route-registration.test.ts` expects 16 routes but observes 17, and `tests/unit/http/integration-runner-registration.test.ts` reports that the default runner does not register every discovered integration suite, including usage-history. These failures were resolved in the later Attempt 3 validation above; figures retained as historical review evidence.
- Existing WooCommerce purchase-history tests shown within `npm test` passed, but they do not make the complete API test command successful.
- `npm run typecheck`, `npm run lint`, and `npm run build` completed without reported errors.
- **Scope clarification:** Shopify application regression testing is not required by API-022. Any earlier statement in this report requesting such a suite is superseded. The remaining regression gate is the API's own suite and declared focused validation.

Evidence: supplied developer terminal transcript `typescript(20261022-100057)`, 22 October 2026, after both implementation patch revisions.

- `git diff --check`: passed (no diagnostics).
- `npm run test:arch035-usage-history:unit`: **passed, 14/14**.
- `npm run test:arch035-usage-history:postgres`: **passed, 1/1**, against disposable PostgreSQL; **58 migrations** applied to fixture database.
- `npm run typecheck`: **passed**, including Prisma Client generation.
- `npm run lint`: **passed**, with `eslint . --max-warnings=0`.
- `npm run build`: **passed**, including Prisma Client generation and TypeScript production build.
- Prior transcript `typescript(20261022-094854)` had one failing integration assertion, two type errors, eight ESLint errors and blocked build; the later run passed all the repeated checks.
- Earlier Attempt 1 evidence predates cancelled-subscription coverage and the full API suite. Attempt 2 executed its new cancellation tests against real disposable PostgreSQL; Attempt 3 later passed the full API regression suite. Shopify application regressions are explicitly out of scope.
- **Attempt 2 isolated validation (not a repository-script substitute):** TypeScript 5.8 `transpileModule` reported no syntax diagnostics for the two affected tests and service; `node --test tests/unit/merchant/usage-history/history.service.test.js` using the supplied isolated Prisma stub passed **7/7** history-service tests, including the new cancellation case.
- **Attempt 2 snapshot environment:** attempting `npm run test:arch035-usage-history:unit` exits 127 (`tsx` missing); `npm run test:arch035-usage-history:postgres` exits 1 (Docker cannot start); `npm run typecheck`, `npm run lint`, `npm run build`, and `npm run test` each exit 127 (missing local Prisma/ESLint toolchain). `npm view tsx@4.20.6` failed with DNS `EAI_AGAIN`; no dependencies were installed. **None of these repository validations is claimed as passing for Attempt 2.**
- **Attempt 3 launcher and publication evidence:** the prepared packet records parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-022` at pre-claim head `ec88a56c21431091ae7b19438533adf77f2ec631`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-022` at `70a7642edbdbcfbe714bc9555b190759bb39fb62`, both `origin/main` incorporation `already-current`, recursive submodule sync/update `passed`, database submodule `807af3393f992c8a19bc9ef278d7e7e05f41799d`, and parent claim commit `2f4ccc16597a9a02961c697df12c688d042b0f2d` pushed successfully.

### Branch and Worktree Evidence

- **Implementation worktree** from developer `pwd`: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-022`.
- **Implementation branch** from developer command: `task/ARCH-035-API-022`; **local HEAD:** `6d71148f3f50d0936acef0b3724b85d459520bcd`.
- **Implementation working tree:** clean (`git status --short` emitted no entries). The provided `git worktree list` includes this dedicated implementation worktree and separately lists the main checkout and other task worktrees.
- **Implementation recursive submodule snapshot:** `database` at `807af3393f992c8a19bc9ef278d7e7e05f41799d` (`heads/main`) in the supplied `git submodule status --recursive` output; this alone does not prove launcher-time synchronisation.
- **Parent task worktree** from developer `pwd`: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-022`; branch from developer output: `task/ARCH-035-API-022`.
- **Original claim metadata** recorded in the supplied attempt snapshot: `execution_mode: developer`, `completion_mode: developer`, `status: in_progress`, `executor: developer`, `attempt: 1`, `claimed_at: 2026-10-22T09:40:33Z`. This is historical claim evidence; current lifecycle metadata is shown in the front matter and Developer Self-Review below.
- **Attempt 2 reconciliation state** verified the implementation worktree clean at `6d71148f3f50d0936acef0b3724b85d459520bcd`, identical to `origin/task/ARCH-035-API-022`; the parent task was clean at `b4b439ee8247d2002163c34488884bed140b1438`, identical to its remote branch. `git diff --check origin/main...HEAD` passed.
- **Attempt 3 run:** terminal transcript confirms command execution in the dedicated API implementation path and an empty `git status --short` and `git diff --check`. It does **not** identify the current implementation or parent commit/remote after the Attempt 3 validation.
- Attempt 3 preparation and start-of-attempt synchronization are evidenced by the launcher packet recorded above; no preparation rerun was used to manufacture history.

### Deviations

- No implementation scope expansion identified in the delivered changes.
- Documentation-only patch rebased onto the developer-claimed parent task file; no modification to `Developer Takeover Amendment` or `Architect Review`.
- No implementation or parent VCS publication deviation remains. The generated terminal recording was removed from the implementation worktree before review submission.

### Assumptions

- The uploaded `moda-interact-workspace-ARCH-035-API-022.zip` represents the developer's current parent task file and API source snapshot. It does not itself attest remote Git state.
- The previously delivered `attempt1-implementation`/`attempt2-implementation` patch **filenames** were revisions within canonical developer Attempt 1. The current task metadata records a **separate, developer-claimed Attempt 2** at 2026-10-22T10:36:55Z, and the cancellation-test correction belongs to this new lifecycle attempt. Patch revision numbers must not be treated as launcher claim numbers.

### Unresolved Issues

- No outstanding task-owned validation or publication issue remains. With `completion_mode: developer`, final completion still requires an explicit developer decision after an Accepted review.

### Architectural Concerns

No new schema migration, shared queue contract, cross-repository implementation or altered repository ownership was introduced by the supplied API changes. Final architecture conformance remains subject to authorised review.

## Developer Takeover Amendment — 2026-10-22

The developer explicitly invoked `/moda_developer_create ARCH-035-API-022` for this agent-owned task. The task is transferred to developer execution with developer-controlled completion while preserving the assigned agent `moda_api`, repository ownership, task scope, dependencies, acceptance criteria and validation requirements. The canonical launcher will record the Attempt 1 claim after this amendment is published.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed. This is a new task definition, not an accepted implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed from implementation and test evidence.

### Follow-up

Architect acceptance required before enabling dependants.

## Developer Self-Review - Changes Requested

- Attempt reviewed: 1. Implementation commit `98f0c9ee0fb32d77ed75f3e9285057f5dbd8b45b` is published and clean on `origin/task/ARCH-035-API-022`; parent task report commit is published at `b6a5229d0bcc08afd8902f22afff04fcaca4250e`.
- Verified during reconciliation: implementation and parent remote refs match their local task branches; implementation is based on current `origin/main`; `git diff --check origin/main...HEAD` passes. The supplied attempt evidence records focused tests, PostgreSQL integration, typecheck, lint and build as passing.
- Correction 1: add and run a focused cancelled-subscription/history test that asserts the expected closed entitlement periods and usage event totals; reconcile the related acceptance criterion from actual behavior.
- Correction 2 (**scope clarified 2026-10-22; supersedes the original cross-repository request**): run and record relevant **`moda-interact-api`** regression checks for WooCommerce usage-history integration, existing WooCommerce purchase-history/billing reads, and route/test-runner registration. The previous instruction to run Shopify application usage-history or billing regression suites is **withdrawn as out of scope**. Do not modify or test the Shopify application repository for API-022.
- Correction 3: provide the original launcher prepared-execution packet and start-of-attempt synchronization evidence, or obtain an explicit architect amendment replacing/waiving that historical evidence requirement. Current branch state is not a substitute, and preparation must not be rerun solely to manufacture history.
- State transition: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. No new attempt was created; completion was not accepted.

## Developer Self-Review - Changes Requested — Attempt 2

- Attempt 2 implementation and parent branches are clean and synchronized with their remotes at `6d71148` and `b4b439e` respectively; no implementation changes are requested for the focused usage-history behavior.
- Focused validation passes: usage-history unit tests `15/15`, disposable PostgreSQL tests `2/2`, typecheck, lint, build, and existing WooCommerce purchase-history tests within the API suite.
- Full `npm test` remains failing at `557/559`: `tests/unit/composition/real-route-registration.test.ts` expects 16 merchant routes but the implemented API correctly registers 17 including usage history; `tests/unit/http/integration-runner-registration.test.ts` does not include the discovered usage-history integration suite in the default runner chain.
- Correction 1: update the route-registration expectation and protected-route coverage for the 17-route composition, then rerun the full API suite.
- Correction 2: register `tests/integration/merchant/usage-history/usage-history.postgres.test.ts` exactly once in the default disposable integration runner chain, then rerun the integration-runner registration test and full API suite.
- Correction 3: retain the focused and repository validation evidence in the Completion Report after both registration corrections pass. Shopify regression testing remains out of scope for API-022.
- State transition: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 2`. Do not create Attempt 3 in this review; the next developer claim increments exactly once.

## Developer Self-Review Passed/Accepted — Attempt 3

- Attempt 3 implementation branch `task/ARCH-035-API-022` is clean and synchronized with its remote at `70a7642edbdbcfbe714bc9555b190759bb39fb62`; the parent report branch is clean and synchronized at `86857aed42001ec36008d59470d887bb11089b00`.
- The canonical launcher prepared and claimed Attempt 3 with dependency gate passed, parent worktree reused at `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-022`, implementation worktree reused at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-022`, `origin/main` already incorporated, recursive submodule sync/update passed, database submodule `807af3393f992c8a19bc9ef278d7e7e05f41799d`, and claim commit `2f4ccc16597a9a02961c697df12c688d042b0f2d` pushed.
- Required validation passes: usage-history unit `15/15`, PostgreSQL `2/2`, full API `570/570`, full `npm run test:integration`, typecheck, lint with zero warnings, build, and `git diff --check`. Existing WooCommerce purchase-history and billing-read coverage passed within the API checks; Shopify tests remain out of scope.
- Review confirms the registration corrections are present and no task-owned implementation or publication issue remains. The generated terminal recording was removed before review submission, leaving both worktrees clean.
- **Review outcome:** accepted for architect review. Because `completion_mode: developer`, the task is now `status: review` with `executor: null`, `claimed_at: null`, and `attempt: 3`; explicit developer completion remains pending. No downstream task was launched.
