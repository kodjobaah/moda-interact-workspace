---
id: ARCH-055-API-006
architecture_id: ARCH-055
title: Optimise commercial settings and reporting projections
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-03
---

# ARCH-055-API-006: Optimise commercial settings and reporting projections

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 2. API-owned workflow / forward-migration contract; supersedes definition revision 1 without claiming an implementation attempt.

**Definition state:** materialised. Attempt 2 was interrupted and has been reconciled by the architect to `ready`; its attempt number remains 2 until the normal launcher durably claims the next attempt.

## Objective

Reduce bounded commercial/reporting database work while preserving credit accounting, saved coupon settings, exact totals, locale completeness and snapshot evidence.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E43`, `E44`, `E45`, `E46`, `E47`, `E48`, `E52`, `E53`, `E57`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-api`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `src/merchant/promotions/`
- `src/merchant/discount-offers/`
- `src/merchant/usage-history/`
- `src/billing/presentation/`
- `src/billing/purchase-history/`
- `tests/unit/merchant/promotions/`
- `tests/unit/merchant/discount-offers/`
- `tests/unit/merchant/usage-history/`
- `tests/unit/billing/presentation/`
- `tests/unit/billing/purchase-history/`
- `tests/integration/merchant/promotions/`
- `tests/integration/merchant/discount-offers/`
- `tests/integration/merchant/usage-history/`
- `tests/integration/billing/presentation/`
- `scripts/test-arch035-promotions-postgres.mjs`
- `scripts/test-arch036-discount-offers-postgres.mjs`
- `scripts/test-arch035-usage-history-postgres.mjs`
- `scripts/test-arch041-billing-postgres.mjs [presentation/history registration only]`

### Exact edit map — definition revision 2

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `src/merchant/promotions/read.ts` | KEEP counts and snapshot; if offerCount/historyCount=0 return that empty page without corresponding findMany. Keep selected grant independent of page. |
| `src/merchant/discount-offers/service.ts` | Save validates full submitted ID set, computes removed/added set differences and updates only those flags with count checks. Reuse settings write return and locked onboarding value; retain final selected-set/override reads. Narrow GET catalogue/settings/override projections; no CURRENT gating for saved settings or Save. |
| `src/merchant/usage-history/history.service.ts; src/merchant/usage-history/periods.ts` | Combine count/_sum into one aggregate. Historical view skips unused current-linked period; retain internal period rows to reuse default/matching requested period. Preserve cursor-anchor validation and off-page explicit period lookup. |
| `src/billing/presentation/billing-read.service.ts` | Reuse pending catalogue row only on an exact operational-plan handle match. Keep latest versus unresolved purchases and confirmed cancellation evidence. |
| `src/billing/presentation/plan-catalogue-read.service.ts` | Build requested/base/default/base/en candidate set after Shop lookup; constrain both translation relations to it. Choose one complete locale for whole catalogue; preserve overflow101. |
| `src/billing/purchase-history/service.ts` | Skip page query only after zero count inside same snapshot; preserve refund overflow11 and latest/completed distinction. |

**Exact new implementation/test paths (not baseline files claimed to exist):**

- `tests/integration/billing/purchase-history/arch055-history.postgres.test.ts`
- `tests/integration/merchant/usage-history/arch055-query-shapes.postgres.test.ts`

**Test registration:** Append history to scripts/test-arch041-billing-postgres.mjs and usage to scripts/test-arch035-usage-history-postgres.mjs. Retain promotion/discount suites. Measure-first items below are evidence-only, not discretionary source changes.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Promotions are Moda promotional credits, not Woo coupon eligibility. Keep exact counts/snapshot, locked selection until expiry, original grant balances/reservations and current eligibility. Skip only zero-count offer/history page queries. Returned-row reuse on selection is allowed only when emitted SQL proves no native-upsert regression.

2. Discount Save remains full-set last-writer-wins without CURRENT-catalogue gating or revision precondition. Validate every submitted tenant/Woo ID, then update only selected-set differences. A 50-code mode-only change changes no coupon flags; replacing one changes two. Reuse actual settings write/read results and onboarding data from the locked Shop; retain selected-set and override checks initially.

3. Coupon browsing keeps exact code-safety filtering, complete cursors and bounded per-batch queries. Correct the 5,000-default versus 20,000-configurable-source-bound assumption. Measure smaller-first-batch versus fixed batching under clean and invalid-prefix distributions; retain fixed batches if the trade-off is not demonstrably favourable. Do not truncate at an assumed cap or treat provider commercial expiry as API deliverability.

4. Saved discount settings remain readable regardless of catalogue readiness. Narrow catalogue/settings/override fields and retain the selected-ID overflow sentinel, missing-state defaults and admin expiry. Read identity consolidation may not alter mutation locking or create a cache.

5. Usage history retains Repeatable Read, exact signed/Decimal accounting, versioned v1/v2 response shapes and evidence rules. Combine count and quantity sum into one aggregate. Avoid linked-current-period lookup on historical views and reuse internal period rows already loaded for default/within-page selection; retain signed-cursor anchor validation and arbitrary explicit-period lookup.

6. v2 attribution evidence consolidation is MEASURE-FIRST: preserve all distinct predicates for correction parents, committed/compensated reservations, legacy links and ambiguity. Never guess attribution from current subscription or a free-text label. Keep existing query paths unless a full shared evidence projection is proven equivalent.

7. Billing overview retains its snapshot, separate balances, unresolved operations versus latest purchase, and confirmed-cancellation evidence. Reuse pending catalogue target only after proving the operational plan handle matches the loaded catalogue handle. Plan catalogue fetches only candidate locales but must choose one complete locale across all plans/highlights and retain overflow sentinels.

8. Purchase history retains historical independence from current subscription and exact bounded refund meanings. Skip findMany after a same-snapshot zero count; add real migrated history-read fixtures to the existing billing runner.

9. Preserve original causes in promotions/discount wrappers and safe financial diagnostics. Measure targeted index plans (coupon, history, latest attempt evidence from ARCH-055-API-001 as needed) but apply no index DDL or generic caching.

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

- [x] Implement empty-page short circuits and projection narrowing.
- [x] Persist coupon selection differences and reuse settings/locked fields with migrated Save/read regressions.
- [x] Combine usage aggregates and reuse period projections.
- [x] Narrow plan locale relations and apply guarded pending-plan reuse.
- [ ] Add dedicated migrated purchase-history tests and complete before/after SQL/row metrics.
- [ ] Record measurements and retain-or-change decisions for batching, upsert result reuse and attribution evidence.

## Interfaces / Contracts

All current HTTP commercial/reporting contracts and Shared projections remain unchanged. The informational discount revision must not become a new command precondition. All performance decisions retain separately recorded client-call, SQL and rows-modified measures.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

None. The source baseline is context, not a fabricated dependency on historical review evidence.

## Enables

- `ARCH-055-API-009`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] No accounting balances, reservation semantics, correction quantities or public versioned schemas change.
- [ ] Same-snapshot zero-count branches issue no page lookup.
- [ ] Coupon mode-only change touches zero coupon rows; one-of-50 replacement touches two, with full identity validation retained.
- [x] One aggregate supplies count and sum; historical-period and cursor validation remain correct.
- [x] Settings remain available during coupon sync/outage; whole-catalogue locale fallback is unchanged.
- [x] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| F01 | Offers/history independently empty | Correct totals/page defaults; only corresponding page fetch omitted. |
| F02 | 50 unchanged coupons + mode change; one replaced coupon; invalid foreign ID | 0/2 flag row assignments; full validation/anchor/rollback unchanged. |
| F03 | Current/past/explicit period, signed negative corrections, v1/v2 ambiguity | Exact accounting/DTOs unchanged; aggregate one call; no lost cursor-anchor check. |
| F04 | Whole-catalogue fallback and no complete locale | One chosen locale or original failure; not mixed per-plan language. |
| F05 | Empty/nonempty history,>10refunds, concurrent refund changes | Same count/page snapshot, no silently truncated invalid refund evidence. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [x] `npm run test:arch035-promotions:postgres` (equivalent direct runner passed; npm alias not invoked)
- [x] `npm run test:arch036-discount-offers:postgres` (equivalent direct runner passed; npm alias not invoked)
- [x] `npm run test:arch035-usage-history:postgres`
- [x] `node scripts/test-arch041-billing-postgres.mjs`
- [x] `npx --no-install tsx --test "tests/unit/merchant/promotions/*.test.ts" "tests/unit/merchant/discount-offers/*.test.ts" "tests/unit/merchant/usage-history/*.test.ts" "tests/unit/billing/presentation/*.test.ts" "tests/unit/billing/purchase-history/*.test.ts"`
- [x] `npm run typecheck`
- [x] `git diff --check`
- [ ] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

This task owns presentation/history test registration in the billing runner; ARCH-055-API-007 owns command fixtures. Both edits must remain narrow and be rebased normally rather than dropping the other suite.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report

### Status

Changes Requested — Architect Review Attempt 1, 2026-11-03. The required baseline/candidate measurement protocol and validation-baseline classification remain incomplete; the task is returned to `ready` with the claim cleared.

### Files Changed

- `src/merchant/promotions/read.ts`
- `src/merchant/promotions/contract.ts`
- `src/merchant/promotions/routes.ts`
- `src/merchant/promotions/service.ts`
- `src/merchant/discount-offers/contract.ts`
- `src/merchant/discount-offers/routes.ts`
- `src/merchant/discount-offers/service.ts`
- `src/merchant/usage-history/history.service.ts`
- `src/merchant/usage-history/periods.ts`
- `src/billing/presentation/billing-read.service.ts`
- `src/billing/presentation/billing-snapshot.reader.ts`
- `src/billing/presentation/plan-catalogue-read.service.ts`
- `src/billing/purchase-history/service.ts`
- `tests/unit/billing/presentation/billing-projection.test.ts`
- `tests/unit/merchant/discount-offers/routes.test.ts`
- `tests/unit/merchant/usage-history/history.service.test.ts`
- `tests/integration/billing/purchase-history/arch055-history.postgres.test.ts`
- `tests/integration/merchant/usage-history/arch055-query-shapes.postgres.test.ts`
- `scripts/test-arch035-usage-history-postgres.mjs`
- `scripts/test-arch041-billing-postgres.mjs`

### Work Completed

- Promotion and purchase-history page queries are skipped only when their same-snapshot counts are zero. Promotion selection remains independent of page contents.
- Discount Save validates the submitted IDs, updates only removed/added coupon flags with exact count checks, and reuses the locked Shop onboarding state and settings write result. Read projections are narrowed while saved settings remain independent of catalogue readiness.
- Usage history combines count and signed sum in one aggregate, omits the linked-current-period lookup for historical views, and reuses loaded period rows while retaining cursor-anchor and off-page explicit-period checks.
- Billing overview reuses a pending catalogue row only for an exact handle match. Catalogue translations are fetched only for requested/base/default candidates while whole-catalogue locale completeness remains enforced.
- Promotion retry errors preserve their Prisma cause. Promotion and discount-offer route diagnostics redact sensitive terms and database connection URLs before emission; focused redaction tests pass.
- Added the two exact task-authorized migrated PostgreSQL suites and appended them to the existing billing and usage runners without replacing other registrations.
- Evidence-only alternatives remain unchanged: smaller-first coupon batching, promotion native-upsert/write-result reuse, and v2 attribution evidence consolidation.

### Validation Results

- `node scripts/test-arch035-promotions-postgres.mjs`: PASS, 1 suite. Disposable PostgreSQL 17 + pgvector, canonical migrations deployed; runner cleanup completed.
- `node scripts/test-arch036-discount-offers-postgres.mjs`: PASS, 7 suites, including concurrent last-writer Save, Background overlap, unavailable catalogue and failed authorization cases. Disposable migrated database cleaned up.
- `npm run test:arch035-usage-history:postgres`: PASS, query-shape suite 1/1 and existing API-022 suites 2/2 on migrated PostgreSQL 17 + pgvector. The SQL assertion observed one aggregate SELECT containing COUNT and SUM, no count-only UsageEvent SELECT, and result total/quantity of 1/2. Runner cleanup completed.
- `node scripts/test-arch041-billing-postgres.mjs`: PASS, 20 suites including `arch055-history.postgres.test.ts`. Empty purchase history returned total 0 and no purchases; captured SQL contained one RecoveryCreditPurchase COUNT SELECT and no page SELECT. Runner cleanup completed.
- Focused task unit command (`npx --no-install tsx --test` over promotions, discount-offers, usage-history, billing presentation and purchase-history): PASS, 103/103.
- `npm run typecheck`: PASS.
- ESLint over all task-changed source, tests and runner files: PASS, zero warnings.
- `git diff --check`: PASS.
- `npm test`: FAIL, 650 passed and 8 failed in untouched billing-command routes, composition/runner registration, merchant-knowledge routes and store-context routes. The runner-registration failure also reports the separate `merchant/ai-response-delay/service.postgres.test.ts` suite is absent from the aggregate chain; that suite is outside this task's runner ownership. These failures have not been compared against the task-start commit and are not represented as proven baseline failures.
- `npm run lint`: FAIL only at untouched `src/merchant/support/routes.ts:75` (`no-empty`).
- The mandatory two-warm-up/five-recorded-sample comparison against task-start SHA `fa2a857ed2ccfd629a7c9f2749ce4a38cc143ff0` has not been run. No raw baseline/candidate samples, elapsed-time summaries, complete per-profile client-call/transaction/row evidence, refund-history overflow profile, or 30-period/31-event usage profile is claimed. The two passing SQL-shape tests provide candidate correctness evidence only, not the required comparative protocol. This gap blocks acceptance.
- Runtime observed: Node `v24.21.0`, npm `11.19.0`; repository declarations are Node `24.19.0`, npm `11.17.0`.

### Worktree and Git Evidence

- Launcher-prepared physical worktrees: parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-006`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-006`.
- Both branches are `task/ARCH-055-API-006`. Shared workspace and shared implementation checkout were not switched or used for implementation.
- Implementation start HEAD was the prepared SHA `fa2a857ed2ccfd629a7c9f2749ce4a38cc143ff0`; parent claim commit is `02de2a9d3d93246c1610b7db8fbb07e06dcf050c` and was already pushed by preparation.
- Nested Database pin: `7c377282aa5819b3008b7d7f3018f44f4161523e` (`heads/main`). Recursive submodule sync/update passed during launcher preparation.
- Implementation candidate commit `8c8558ae44315ccb4564169aad94e454c3074ec7` is published on `origin/task/ARCH-055-API-006`. This completion-report commit publishes the parent report on its existing task branch. No parent submodule gitlink was staged.

### Deviations

- The two new suite filenames and runner references follow the exact revision-2 deliverable paths. No schema, migration, public DTO, index, shared rollup or unrelated runner registration was changed.
- Review is requested with the comparative evidence gap explicitly blocking acceptance; no measurement values were inferred from correctness runs.

### Assumptions

The uploaded source snapshot is the design baseline, not proof of current remote state. Reconcile only relevant drift on the real launcher baseline; return contract-changing drift to the architect.

### Unresolved Issues

- Required baseline/candidate protocol: run the fixed profiles M11-M14 with two discarded warm-ups and five restored recorded samples per version, capturing the specified client calls, normalized SQL, transaction statements, row counts, timings, retries and external calls. Complete F01-F05 assertions and the larger M13 fixture as part of those suites.
- Eight full `npm test` failures and the untouched support-route lint error remain unclassified against the prepared SHA.
- Aggregate runner registration detects a missing AI-response-delay integration suite owned by later API-009 work; no out-of-scope runner change was made.

### Attempt 2 Progress — Blocked

- Launcher prepared Attempt 2 on the existing mirrored task branches. The implementation candidate began at `8c8558ae44315ccb4564169aad94e454c3074ec7`; the task-start comparison baseline `fa2a857ed2ccfd629a7c9f2749ce4a38cc143ff0` is present in the implementation repository.
- The repository-owned Node bootstrap resolved the declared toolchain successfully: Node `v24.19.0`, npm `11.17.0` (the initially observed `v24.21.0`/`11.19.0` shell was corrected before the latest validation attempt).
- Added a nonempty five-purchase case to `tests/integration/billing/purchase-history/arch055-history.postgres.test.ts`, complementing its empty-history query-shape case. The migrated billing runner passed both purchase-history cases. A separate complete runner invocation passed 21/21 suites; a later declared-toolchain invocation passed the two purchase-history cases but had one unrelated existing billing-command test timeout (`Free top-up commits exact purchase...`, Prisma transaction not found/closed).
- Added the M13 30-closed-period / 31-signed-events fixture and v1/v2 assertions to `tests/integration/merchant/usage-history/arch055-query-shapes.postgres.test.ts`. Editor diagnostics report no errors, but the migrated PostgreSQL suite has not executed in this attempt; the terminal stopped returning command output, and the workspace test adapter does not discover Node `node:test` files.
- No M11-M14 two-warm-up/five-sample baseline/candidate measurements or complete F01-F05 matrix results are claimed. M11's new nonempty purchase path is exercised, but independent promotion emptiness combinations, M12's 51-coupon row-assignment profiles, the migrated M13 run, and M14's full locale/handle/catalogue-state profiles remain unverified.
- Attempted to run the full baseline suite from a temporary `git archive` of the task-start SHA. The first run stopped before tests because the API archive omits its Database submodule (`database/prisma/schema.prisma` not found). A retry linked the launcher-pinned Database checkout, but the terminal returned no execution output, so baseline classification of the eight reported failures remains incomplete. No failure is represented as proven baseline.
- The current task report remains blocked and this progress update is local only. No commit or push was attempted after the previous automatic-review rejection of report publication; the eight-suite baseline classification, full F01-F05 evidence, M11-M14 comparative samples, and final review readiness remain outstanding.

### Architectural Concerns

No schema, transaction-boundary, public contract or ownership change was required. The documented evidence gap and unrelated broad-suite failures require architect disposition before acceptance.

## Architect Review — Attempt 1

### Review Status

Changes Requested — 2026-11-03. Attempt 1 remains unchanged; task returned to `ready`, with `executor` and `claimed_at` cleared. No acceptance or downstream promotion.

### Review Notes

1. **[P1] Complete the mandatory comparative evidence protocol.** The task's fixed M11–M14 profiles require two discarded warm-ups and five restored recorded samples per version against the prepared baseline `fa2a857ed2ccfd629a7c9f2749ce4a38cc143ff0`, with matching disposable PostgreSQL 17 + pgvector fixtures. The report explicitly says these samples and the required per-profile SQL/client-call/transaction/affected-row/timing evidence were not collected. The passing query-shape and correctness tests do not establish the required before/after evidence. Required F01–F05 outcomes are also left unchecked; the named 30-period/31-event usage profile and refund-history overflow/concurrent-refund profile are not evidenced. Record the fixed-protocol results and retain/defer decisions for M11–M14 and the evidence-only alternatives, or return a concrete baseline incompatibility with the failed command and evidence. Do not infer performance from target counts or mock call counts.

2. **[P2] Classify broad validation failures against the task-start baseline and declared toolchain.** The full `npm test` run has eight failures that were not compared with the prepared start SHA, and `npm run lint` fails at an untouched support route. The recorded runtime is Node 24.21.0/npm 11.19.0 while the repository declares Node 24.19.0/npm 11.17.0, despite the task's instruction to use the declared toolchain. Establish which failures are baseline versus candidate regressions, and rerun required checks using the repository toolchain (or record a specific toolchain blocker) before acceptance.

### Reviewed Files

- Task definition revision 2, its unchecked Work Items, Acceptance Criteria and Validation items.
- Attempt 1 Completion Report and declared fixed protocol in `docs/architecture/ARCH-055/task-definition-contract.md`.
- Implementation branch `task/ARCH-055-API-006` at `8c8558ae44315ccb4564169aad94e454c3074ec7`, relative to prepared start `fa2a857ed2ccfd629a7c9f2749ce4a38cc143ff0`; changed paths and SQL-shape regression coverage were inspected.
- Canonical parent and implementation worktree status and task-branch publication state.

### Validation Reviewed

The report records the focused migrated PostgreSQL suites, 103 focused unit tests, typecheck, and diff check passing. It also records the eight full-suite failures, the support-route lint error, missing comparative samples, and runtime-version mismatch. No tests or measurements were rerun during this architect review.

### Architecture Conformance

The source changes are within the revision-2 edit map, and the implementation branch is pushed and clean. Acceptance remains blocked by the mandatory comparative evidence and unresolved validation classification. The unchanged baseline behavior for evidence-only options is not enough by itself; the task requires measured retain/defer decisions.

### Follow-up

Keep the same task branch and Attempt 1. Complete M11–M14 with the fixed baseline/candidate procedure and F01–F05 regression outcomes, record raw samples and measured SQL/calls/rows/timings, classify broad validation failures against the task-start baseline using the declared runtime, and reconcile the unchecked task criteria. Do not begin API-009 or SYSTEM-TEST-001. Both remain Pending because API-006 is not Complete. No implementation source was changed by this review.


## Architect Review — Recovery of Attempt 2, 3 November 2026

### Review Status

Changes Requested. Attempt 2 is not accepted. Return the same task to Ready, clear executor/claimed_at, and preserve `attempt: 2`; only the normal prepared launcher may claim Attempt 3. No acceptance or downstream promotion.

### Recovery evidence

The developer explicitly requested architect reconciliation of the existing Copilot claim after the normal launcher returned `TASK_NOT_READY`. The durable Attempt 2 progress report states that terminal execution stopped returning output, Node test discovery through the alternate adapter was unavailable, and comparative measurements/baseline classification remained unfinished. This is an interrupted-attempt handoff, not successful completion. The report was preserved in parent commit `a0cba30ae10fbf06da2f7f315fc5307cb63f06d0`; no evidence of ongoing implementation was established by this recovery.

Route-only launcher output confirms canonical primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`, parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-006`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-006`, matching `task/ARCH-055-API-006` branches, agent execution and automatic architect completion. Route-only is topology evidence, not a prepared packet or claim.

Implementation HEAD `8c8558ae44315ccb4564169aad94e454c3074ec7` matches its remote task branch. Two uncommitted task-owned test changes were inspected: `tests/integration/billing/purchase-history/arch055-history.postgres.test.ts` adds the nonempty five-purchase case and fixture cleanup; `tests/integration/merchant/usage-history/arch055-query-shapes.postgres.test.ts` adds the 30-closed-period/31-signed-events M13 fixture and v1/v2 assertions. Both are exact authorized paths. Preserve and publish those changes through the repository owner before normal preparation; do not discard them or infer that unexecuted assertions pass. The nested Database checkout has no local modifications or gitlink difference. This recovery makes no implementation edits and performs no runtime validation.

### Mandatory correction contract

The complete Attempt 1 Review Notes remain authoritative. Finish M11–M14 with the fixed two-warm-up/five-recorded-samples-per-version procedure against `fa2a857ed2ccfd629a7c9f2749ce4a38cc143ff0`, retain actual raw SQL/client-call/transaction/row/timing evidence and descriptive summaries, complete F01–F05 including refund overflow/concurrent-refund and large signed-history cases, and record measured retain/defer decisions for evidence-only alternatives. Classify the broad-suite failures against that baseline using the declared Node/npm toolchain; record actual infrastructure or compatibility failures without inventing values or silently weakening gates.

The stranded tests are incomplete supporting work, not a replacement for those required measurements. Reconcile unchecked Work Items, Acceptance Criteria and Validation only from actual results. Keep the existing task branches, scope and contracts; do not change migrations, add discretionary optimisations or start API-009/SYSTEM-TEST-001. Parent task recovery publication is mechanically delegated for this current-task-only overlay; implementation checkpoint publication remains with the repository owner.
