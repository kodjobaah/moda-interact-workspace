---
id: ARCH-057-SYSTEM-TEST-001
architecture_id: ARCH-057
title: Verify Shopify persistence, request composition and server diagnostics
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 100
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-057-SHOPIFY-012
enables: []
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-057-SYSTEM-TEST-001: Verify Shopify persistence, request composition and server diagnostics

## Architecture

Architecture ID: `ARCH-057`. Document: `docs/architecture/ARCH-057-shopify-application-database-correctness-and-simplicity.md`. Coordinator: `moda_architect`.

Mandatory contract: `docs/architecture/ARCH-057/task-contract.md`. **Defined but not materialised.** Terminal validation follows acceptance/integration of all twelve Shopify tasks through the dependency on SHOPIFY-012. No application implementation or acceptance is asserted here.

## Objective

Independently rerun the accepted boundary suites on the integrated Shopify revision and prove selected webhook behaviour through the built application, real PostgreSQL and real Redis. Produce six complete scenario results with truthful evidence classes, source/package provenance and original-message/privacy assertions at the actual logging output.

## Context

Functional tasks establish individual contracts. This task checks that their composition retains tenant isolation, current mutation admission, idempotent lifecycle/purchase identity, bounded request/queue work and useful server diagnostics. Existing system-test components already own command recording, disposable data planes, process management, evidence and cleanup. Reuse those components.

The latest snapshot also defines ARCH-056 System-Test work. Its runner/catalogue registrations overlap mechanically with this task. Preserve both additions; ARCH-056 is not an implementation prerequisite for Shopify, and this task does not change its scenario semantics or naming.

## Scope

One repository: `moda-interact-system-test`. Paths below are relative to it. Accepted application tests and modules are read/executed from the verified `moda-interact` worktree; they are not edited or replaced by a system-test model.

### Existing files to modify

| Path | Exact responsibility |
|---|---|
| `catalogue/scenarios.json` | Add exactly the six rows below with complete metadata, evidence classes and task traceability |
| `catalogue/historical-system-test-map.json` | Add this task's symmetric six-ID mapping, exact canonical task path and definition-baseline `historicalStatus: "pending"` |
| `docs/SHOPIFY-COVERAGE-MATRIX.md` | Regenerate with `npm run validate:catalogue -- --write` |
| `src/harness/selection.js` | Add `shopify-persistence`, selected by this task's `sourceRequirements`; never hide unimplemented rows |
| `src/harness/cli.js` | Add the suite name to existing help |
| `scripts/run-system-tests.js` | Merge `createShopifyPersistenceExecutors` using the duplicate guard; validate this suite's exact plan/results; preserve other suites and ordinary nonzero failure behaviour |
| `package.json` | Add only the two suite scripts below; existing `test:harness` discovers the new tests |

### New files

| Path | Responsibility |
|---|---|
| `src/harness/shopify-persistence/contracts.js` | Frozen six scenario IDs/classes/case IDs, source requirement and completeness validation |
| `src/harness/shopify-persistence/executors.js` | Six registrations through the existing runner; require cases/evidence/cleanup |
| `src/harness/shopify-persistence/runtime.js` | Compose existing data plane/process/command primitives, sealed OAuth fixture, actual app build and emitted logs |
| `src/harness/shopify-persistence/accepted-suites.js` | Exact accepted application commands, executed-test report parsing and case/evidence association |
| `src/harness/shopify-persistence/webhook-scenario.js` | Signed HTTP uninstall/ingress/Redis failure cases against the real built application |
| `src/harness/shopify-persistence/fixtures.js` | Small run-scoped synthetic Shop/subscription/session/webhook fixtures and bounded fault controls |
| `src/harness/shopify-persistence/observations.js` | Tenant-scoped durable/queue observations and safe log assertions before artifact redaction |
| `src/harness/shopify-persistence/evidence.js` | Case, source/package and logging sidecars in the existing evidence directory |
| `test/harness/shopify-persistence-contracts.test.js` | Exact scenario/case/class and result completeness rules |
| `test/harness/shopify-persistence-registration.test.js` | Catalogue/map/selector/executor symmetry and preservation of unrelated registrations |
| `test/harness/shopify-persistence-results.test.js` | Missing/skipped/duplicate/wrong-source evidence cannot pass; failure evidence and cleanup survive |
| `docs/SHOPIFY-PERSISTENCE-VALIDATION.md` | Commands, classifications, fixture limits, evidence and replay instructions |

Keep each new JavaScript/test source below 300 lines. Reuse existing helpers read-only; no new generic runner, logging serializer, container framework or application test endpoint.

## Out of Scope

No application/Shared/Background/API/Database implementation, schema/migration, real provider credential or charge/refund, live Shopify store, privacy fulfilment/retention implementation, remote collector configuration, deployment or capacity certification. No claim that synthetic SDK/provider fixtures are full Shopify OAuth or provider acceptance. No `_index.md` or earlier task status changes.

## Requirements

### Source, execution and evidence integrity

1. Verify all transitive prerequisites are Complete and architect-accepted. Record the launcher-prepared parent/System-Test paths and SHAs plus the actual executed Shopify full SHA/cleanliness, nested Database recorded/working SHA, canonical schema/migration hashes and installed Shared/router/Prisma/BullMQ versions. The source ZIP hash is historical context, not a runtime Git revision.
2. Reuse `DisposableDataPlane`, `ManagedProcess`, `createPlatformConfigurationFixture`, existing Shopify signing/synthetic identity helpers and the runner's command/evidence/cleanup facilities. Canonical migrations run on PostgreSQL 17 + pgvector; Redis cases use disposable real Redis. A mocked Prisma/Queue implementation cannot satisfy runtime evidence.
3. Build/start the actual accepted application. Seed `shopify.oauth` with the existing fixture's `seedSecret(databaseUrl, "shopify.oauth", {apiKey, apiSecret})`; supply its `workerEnvironment` and the synthetic app environment to build/start with deployment environment `test`. Call `assertConfigured(databaseUrl, {"shopify.oauth": "sealed"})`. Current Shopify bootstrap reads sealed configuration; plain `SHOPIFY_API_KEY`/`SHOPIFY_API_SECRET` environment values alone are insufficient. Do not weaken production configuration or invent another encryption implementation.
4. Capture the actual app stdout/stderr and actual installed Shared output. Assert safe original messages/codes/causes, correlation and sensitive sentinel absence **before** generic evidence redaction. Store safe bounded assertion records, never credentials, signed URLs, connection strings or customer data. Attach actual available diagnostics; missing original messages are a failure, not permission to synthesize them.
5. Run application suites through recorded commands against the accepted application root, with their explicit opt-ins. They own their disposable containers. Append Vitest's existing JSON reporter/output-file options into a run-owned temporary directory where necessary, retaining ordinary readable output. Parse test outcomes: zero tests, skip/todo, absent mandatory cases, failed command or missing report cannot satisfy the scenario. Do not infer success from exit code alone or a historical Completion Report.
6. Label command-level mock/router assertions CONTRACT; real migrated database/service assertions INTEGRATION; the signed HTTP row BLACK_BOX at the app-to-queue boundary. The latter does not certify Background consumption or full reinstall OAuth. A row may attach lower-class supplementary evidence without upgrading it. Do not clone application policy into an integration driver.
7. Concurrency evidence comes from the accepted independently connected/barrier-controlled PostgreSQL cases. Record their actual execution and results. Plain concurrent promises, sleeps, mock counts or SQL that directly writes an expected business outcome are not substitute evidence.
8. Required cases, package provenance and diagnostic checks are explicit members of the result contract. Missing prerequisites/Docker/build/test opt-in produce BLOCKED or failure, not PASS. Every fault/barrier has bounded cleanup in `finally`; cleanup only run-owned processes, rows, queues and containers.
9. Preserve all ARCH-056 and other suite registrations, selectors, provenance descriptors and package scripts. This task adds a selector/factory through existing seams; it does not require ARCH-056 to run or approve its implementation. Existing Shopify provenance already includes the app and nested Database: extend only any missing consumed-package/evidence details without duplicate repository names.

### Six fixed scenarios

Use `domain: "SHOPIFY"`, `providers: ["shopify", "shared"]`, `automation: "automated"`, `liveAuthorizationRequired: false`, `requiredFor: []`, and `sourceRequirements: ["ARCH-057-SYSTEM-TEST-001"]` for each. `evidenceClass` and `requiredEvidenceClass` are the stated class. Populate ordinary purpose/preconditions/services/fixtures/actions/assertions/evidence/cleanup/implementation fields. Mark implemented only with a registered executable; missing runtime prerequisites still block execution.

| Scenario ID | Layer / class | Required case IDs |
|---|---|---|
| `SHOPIFY-PERSISTENCE-REQUESTS-001` | L2 / INTEGRATION | R1, R2, R3 |
| `SHOPIFY-PERSISTENCE-BILLING-001` | L2 / INTEGRATION | B1, B2, B3 |
| `SHOPIFY-PERSISTENCE-MERCHANT-001` | L2 / INTEGRATION | M1, M2, M3, M4 |
| `SHOPIFY-PERSISTENCE-REFRESH-001` | L1 / CONTRACT | F1, F2 |
| `SHOPIFY-PERSISTENCE-WEBHOOKS-001` | L3 / BLACK_BOX | W1, W2, W3, W4 |
| `SHOPIFY-PERSISTENCE-DIAGNOSTICS-001` | L1 / CONTRACT | D1, D2, D3 |

#### R — Authenticated request composition

- **R1:** Rerun the accepted SHOPIFY-001 canonical-PostgreSQL bootstrap/profile/no-op suite. Verify unique tenant identity, missing prerequisite repair, unchanged replay and original DB/provider diagnostics.
- **R2:** Rerun its actual-router suite for matched parallel loaders, direct resources and POST followed by document/SPA revalidation. Confirm one context per GET/HEAD, no cross-request/tenant sharing and post-action committed state. SDK simulation is explicitly described.
- **R3:** Reconcile its before/after database/provider observations on the same fixtures. Direct established resource access performs no routine profile GraphQL; independent capability checks remain. Keep SQL and mocked repository call counts in separate fields.

#### B — Billing correctness and bounded reads

- **B1:** Rerun accepted SHOPIFY-002 paid activation/lock-order/malformed-versus-absent provider evidence cases on migrated PostgreSQL. Observe rollback/no-op identity and independently connected contention results; never call a mocked lock test database proof.
- **B2:** Rerun SHOPIFY-003 purchase/refund cases, including duplicate/current admission, stale provider/local identity and provider/database failure. Confirm no provider call while the write transaction is open; preserved current purchase revalidation, accounting and refund receipt semantics.
- **B3:** Run the accepted bounded history/commercial projection fixtures and promotion concurrency case from SHOPIFY-003/004. Verify finite page reads and shared provider context, exact refund summaries, preserved translated promotion selection and ledger/balance semantics. The contract permits six service reads for a page's exact refund summaries; do not enforce a false five-read goal.

#### M — Merchant touchpoints

- **M1:** Support PostgreSQL tests prove the narrow badge, bounded visible-ID acknowledgment, tenant/visibility filtering, duplicate/already-read success and first-read timestamp preservation.
- **M2:** Recovery PostgreSQL tests prove one owned page context with necessary independent resource reads, preserved message pagination and fresh command admission; a read cache cannot authorize a stale mutation.
- **M3:** Settings PostgreSQL tests prove unchanged discount policy writes nothing and category activation checks ACTIVE under the existing Shop lock. Preserve intentional onboarding milestone/category order.
- **M4:** Knowledge PostgreSQL tests prove unchanged ordering, source/revision/asset ownership, upload lifecycle/entitlement, dependency-error classification and rollback. Dormant sources remain usable; no schema-policy expansion.

#### F — Browser framework behaviour

- **F1:** Rerun SHOPIFY-008's mounted router refresh suite. Fetcher success relies on framework revalidation; plain-fetch upload still refreshes; polling is bounded/stops at terminal/unmount and does not multiply requests. Use the actual installed React Router and label a simulated DOM as such.
- **F2:** Run the request-context router suite from R2 once per run, reusing its recorded result without claiming a second execution. Verify action/loader cache separation in document and SPA flows. This row is framework CONTRACT evidence, not live merchant-browser certification.

#### W — Real HTTP lifecycle and queue boundary

- **W1:** On two migrated fixture tenants, post a correctly signed uninstall to `/webhooks/app/uninstalled`. Verify the selected Shop transition and atomic session removal, with Subscription/billing projection unchanged by uninstall; the other tenant is unchanged. Seed a replacement offline session and valid pending marker as an explicit fixture for the already-uninstalled tenant, replay the callback and assert that neither replacement identity nor marker is removed/rewritten. This proves duplicate HTTP handling; the actual SDK store/uninstall/begin races are separately rerun from SHOPIFY-009's PostgreSQL suite and labelled INTEGRATION.
- **W2:** On an ACTIVE fixture tenant, post a valid signed checkout event to `/webhooks` twice with the same authenticated delivery identity. Inspect the real queue using the accepted Shared identity/schema; exactly one retained job with the expected tenant/payload exists. Leave consumers stopped for this assertion, so completed-job removal does not turn a late replay into a different test. Unsupported topics acknowledge without queue work; attach accepted source/instrumented CONTRACT evidence for their zero-Shop-lookup assertion, since the HTTP response alone cannot prove it. Invalid HMAC never queues; inactive/unknown-shop outcomes retain the selected ACK/discard semantics.
- **W3:** Make the run-owned Redis unavailable during publication. Assert a bounded retryable response and original safe queue/transport evidence; the application remains live and readiness reflects dependency failure. Restore Redis, retry the same identity and observe at most one retained job. An uncertain timeout may already have enqueued once; do not require false proof of cancellation or invent a provider rejection. Use the accepted SHOPIFY-010 publication deadline plus a documented small HTTP scheduling allowance, not an arbitrary long timeout.
- **W4:** Rerun SHOPIFY-009/010 configuration, actual SDK session-race and real Redis suites as supplementary CONTRACT/INTEGRATION evidence. Verify exact intended named configuration topics and app identity, current job-ID/replay semantics and error-emitter ownership. Repository TOML is intended configuration; do not claim remote deployment or subscription registration.

#### D — Diagnostic and naming completeness

- **D1:** Rerun `test:server-diagnostics` against the actual installed Shared package. For request/render/bootstrap/configuration/health/fallback paths, require original distinct marker/message/cause/code assertions, truthful origin and absence of the exercised sensitive sentinels. Review `docs/server-error-coverage.md` against the integrated server inventory: no unexplained catch/error-event/propagation gap is accepted.
- **D2:** Execute the real Shared throwing-sink cases. Original business failure, rollback/retry or successful best-effort outcome is unchanged. A failed sink need not somehow retain its own log; the assertion is isolation. Expected redirects/business validation remain documented normal outcomes.
- **D3:** Run `lint:runtime-names` and `test:billing-identity`. Require zero architecture/task-labelled matches in Shopify runtime scope and the three new canonical namespaces selected by SHOPIFY-012. Fixed vectors use the new preimages; replay starts from a newly created canonical operation and preserves one operation/receipt. Old development identities require no compatibility, migration or backfill. Architecture labels in tests/docs remain allowed; no hidden spelling/encoding bypass or legacy allowlist.

## Work Items

- [ ] Confirm accepted implementation/package/source provenance and freeze the six scenario/case contracts.
- [ ] Add minimal selector/catalogue/executor registration through the existing runner.
- [ ] Record and classify accepted application suite executions, including required non-skipped cases.
- [ ] Add actual signed HTTP lifecycle/queue cases with disposable PostgreSQL/Redis and sealed OAuth fixture.
- [ ] Capture original diagnostic/privacy/sink evidence and exact naming/identity results.
- [ ] Run the complete suite, preserve failure evidence, verify cleanup and return review.

## Interfaces / Contracts

Suite selector: `scenario => scenario.sourceRequirements.includes("ARCH-057-SYSTEM-TEST-001")`. Test-catalogue traceability may contain the architecture ID; runtime modules, selector, exported factory and events use domain names.

```json
{
  "system:shopify-persistence:plan": "node scripts/run-system-tests.js --suite shopify-persistence --list",
  "system:shopify-persistence": "node scripts/run-system-tests.js --suite shopify-persistence --execute"
}
```

`createShopifyPersistenceExecutors({workspaceRoot, systemTestRoot, appRoot, databaseRoot})` returns the ordinary existing executor map. It does not register a second runner. Freeze the exact accepted application commands in `accepted-suites.js` from the Validation sections of SHOPIFY-001–012. Required entrypoints include:

```sh
npm run test:merchant-request:unit
npm run test:merchant-request:router
npm run test:merchant-request:postgres
MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/billing-activation.postgres.integration.test.ts
MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/recovery-credit-refunds.postgres.integration.test.ts tests/integration/recovery-credit-purchases.postgres.integration.test.ts
MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/promotion-selection.concurrency.integration.test.ts
npm run test:merchant-support:unit
npm run test:merchant-support:postgres
npm run test:recovery-readers:unit
npm run test:recovery-readers:postgres
npm run test:merchant-settings:unit
npm run test:merchant-settings:postgres
npm run test:merchant-knowledge:unit
npm run test:merchant-knowledge:router
npm run test:merchant-knowledge:postgres
npm run test:shopify-lifecycle
npm run test:shopify-lifecycle:postgres
npm run test:shopify-webhooks
npm run test:shopify-webhooks:redis
npm run test:server-diagnostics
npm run lint:runtime-names
npm run test:billing-identity
```

The additional focused billing/history/commercial commands are:

```sh
npm test -- tests/unit/services/shopify-billing.provider.test.ts tests/unit/services/billing/provider-diagnostics.test.ts tests/unit/services/billing/subscription-activation.service.test.ts tests/unit/services/billing/subscription-sync.service.test.ts tests/unit/services/billing/billing-period-projection.test.ts tests/unit/services/billing/shopify-billing-operation.service.test.ts tests/unit/routes/billing-callback.test.ts tests/unit/routes/onboarding-resume.test.ts
npm test -- tests/unit/recovery-credit-history-budget.test.ts tests/unit/routes/recovery-credit-purchases.test.ts tests/unit/routes/billing-options-action.test.ts tests/unit/services/recovery-credit-purchase-management.service.test.ts tests/unit/services/billing/recovery-credit-purchase-request.service.test.ts
npm test -- tests/unit/services/billing/merchant-billing-presentation.test.ts tests/unit/commercial-read-budget.test.ts tests/unit/routes/billing-options-loader.test.ts tests/unit/services/promotion.service.test.ts tests/unit/routes/promotion-route.test.ts tests/unit/usage-route.test.ts
```

Record one execution per unique command/file group and reference its evidence from every consuming case. If an accepted prerequisite legitimately amended a path/command, reconcile this explicit table before execution; never silently omit the case or substitute a broad whole-app test run.

Attach `shopify-persistence-cases.json`, `shopify-persistence-provenance.json` and `shopify-persistence-logging.json` through the existing evidence facility. They record scenario/case status and class; actual command/test artifact linkage; source/build/consumed package identity; tested marker/code/cause/privacy assertions and safe correlation; cleanup outcome. They contain no raw secret-bearing records. Missing sidecars or mismatched case/source provenance fail the suite.

## Dependencies

- ARCH-057-SHOPIFY-012

Transitively all SHOPIFY-001–011. Every required implementation must be architect-accepted and integrated. Developer manual validation may happen before invocation but is not encoded as a synthetic dependency. ARCH-056 implementation is not required; preserve any integrated shared runner edits.

## Enables

None. Terminal architectural validation; it does not gate unfinished implementation.

## Acceptance Criteria

- [ ] Exactly six planned/registered/executed scenario results with every named case and truthful class; no skipped case counted as pass.
- [ ] Executed Shopify/build/Database/installed-package provenance is complete and matches accepted source.
- [ ] Required real PostgreSQL, actual-router, real Redis and HTTP cases execute with the selected preserved outcomes.
- [ ] Billing replay/conflict behaviour uses the new canonical namespaces and fresh fixtures; session/tenant identity and fresh mutation admission remain correct.
- [ ] Actual emitted original safe diagnostics and privacy/sink assertions pass; no synthetic upstream explanations.
- [ ] Zero-exception domain naming gate, new canonical billing vectors and fresh same-format replay pass; no old-identity compatibility is required.
- [ ] ARCH-056/unrelated registrations remain intact; no copied policy model or application implementation edits.
- [ ] Safe evidence survives failures and all task-owned resources are cleaned.

## Validation

From `moda-interact-system-test`, after the mandatory Node bootstrap check:

- [ ] `npm run typecheck`
- [ ] `npm run lint`
- [ ] `npm run validate:catalogue -- --write`
- [ ] `npm run validate:catalogue`
- [ ] `npm run test:harness`
- [ ] `npm run system:shopify-persistence:plan` — exact six-ID set
- [ ] `npm run system:shopify-persistence` — all cases, required classes and three sidecars
- [ ] `git diff --check`

Do not claim implementation tests ran while authoring this definition. Missing accepted suites, source provenance, Docker or configuration is a real blocker. Fix a system-test-owned harness defect within the selected paths; application defects return to their owning task for correction and review.

## Stop Condition

Return review with complete evidence or precise blocked/failed cases. Do not accept the architecture, edit implementation to make assertions pass, start unrelated tasks, publish/deploy or claim global production readiness. A changed cross-repository contract or need for additional test-only application hooks returns to the architect.

## Implementation Notes

This suite certifies the selected Shopify contracts at named boundaries. Privacy fulfilment, durable subscription-ended notices, remote log collection/retention and production capacity remain outside its result. The evidence class and tested fixture boundary are part of every reported conclusion.

## Completion Report

### Status

Not Started. Defined but not materialised; no execution claim or worktree is asserted.

### Files Changed

None. Definition only.

### Work Completed

None.

### Validation Results

Not run. Record exact commands, fixture/case results, source/build/installed-package provenance, original diagnostic assertions, SQL/provider counts where required, and task-owned resource cleanup.

### Deviations

None.

### Assumptions

The launcher will verify actual dependency status and the accepted integrated source before claiming this task.

### Unresolved Issues

Implementation and required validation are outstanding.

### Architectural Concerns

Return changed ownership, persisted identity, schema, queue, transaction or external contract requirements to the architect.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition only; no implementation accepted.

### Reviewed Files

Definition and current snapshot touchpoints only.

### Validation Reviewed

Definition checks only. Implementation evidence is outstanding.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

Return the completed task for architect review; do not start enabled tasks.
