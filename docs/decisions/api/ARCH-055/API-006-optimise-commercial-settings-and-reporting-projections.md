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
status: complete
priority: 35
executor: null
claimed_at: null
attempt: 5
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

**Definition state:** materialised in the canonical dedicated worktrees. Attempt 5 is Accepted and Complete after architect review on 2026-11-03; executor and claim are cleared. Prior attempts and evidence remain historical below.

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
- `database [consumer gitlink only; Attempt 4 accepted/integrated pin reconciliation below; no nested schema/migration edits]`

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

**Task-local parent evidence exception — Attempt 3:** The executor may create, stage, commit and push only `docs/decisions/api/ARCH-055/evidence/API-006-attempt-3-commercial.jsonl` in addition to this task file on the dedicated parent task branch. Retain actual raw M11–M14 normalized SQL/client-call/transaction/row/timing records and descriptive summaries there. Include only bounded review metadata; exclude connection URLs, credentials, raw SQL parameter values and customer bodies. This is a directly task-owned review artifact, not a production metric or standalone benchmark framework; its measurements and limits must be identified in the Completion Report.



**Opt-in comparison orchestration exception — Attempt 3:** `scripts/test-arch041-billing-postgres.mjs` may additionally implement the explicit opt-in `ARCH055_COMMERCIAL_COMPARE_BASELINE=1` solely to execute fixed M11–M14 comparison cases in the existing exact authorized file `tests/integration/billing/purchase-history/arch055-history.postgres.test.ts`. These test cases may import the existing API-owned commercial services named in this task; no new implementation/test path or production benchmark utility is authorized. The runner may archive pinned baseline `fa2a857ed2ccfd629a7c9f2749ce4a38cc143ff0` to a temporary isolated checkout, copy identical test instrumentation, use the same installed dependencies, and clone equivalent disposable databases from one canonical migrated empty template. Preserve normal `initialSuites`, additional-suite path validation and every billing-command registration exactly; default execution and API-007 command ownership remain unchanged. Record both versions, matching fixtures, actual SQL/control/call/row evidence, two discarded warm-ups and five recorded samples per version/profile, cleanup and measurement limits. This narrow test-only exception supersedes the billing runner's presentation/history-registration-only qualifier solely for that opt-in orchestration.

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
- [x] Add dedicated migrated purchase-history tests and complete before/after SQL/row metrics.
- [x] Record measurements and retain-or-change decisions for batching, upsert result reuse and attribution evidence.

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
- [x] Same-snapshot zero-count branches issue no page lookup.
- [x] Coupon mode-only change touches zero coupon rows; one-of-50 replacement touches two, with full identity validation retained.
- [x] One aggregate supplies count and sum; historical-period and cursor validation remain correct.
- [x] Settings remain available during coupon sync/outage; whole-catalogue locale fallback is unchanged.
- [x] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication. Attempt 5 retains safe Prisma-formatted failure reasons and codes while excluding invocation context; both real Shared-sink route regressions pass.
- [x] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [x] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

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

- [x] `npm run test:arch035-promotions:postgres`
- [x] `npm run test:arch036-discount-offers:postgres`
- [x] `npm run test:arch035-usage-history:postgres`
- [x] `node scripts/test-arch041-billing-postgres.mjs`
- [x] `npx --no-install tsx --test "tests/unit/merchant/promotions/*.test.ts" "tests/unit/merchant/discount-offers/*.test.ts" "tests/unit/merchant/usage-history/*.test.ts" "tests/unit/billing/presentation/*.test.ts" "tests/unit/billing/purchase-history/*.test.ts"`
- [x] `npm run typecheck`
- [x] `git diff --check`
- [x] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [x] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

This task owns presentation/history test registration in the billing runner; ARCH-055-API-007 owns command fixtures. Both edits must remain narrow and be rebased normally rather than dropping the other suite.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report — Attempts 1–2 (historical)

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


## Completion Report — Attempt 3

### Status

Ready for Review. Both architect correction items are implemented: the complete M11–M14 paired evidence and F01–F05 outcomes are recorded, and broad failures are classified against the pinned start on the declared toolchain. Final focused units, all required PostgreSQL runners, typecheck and diff checks passed. Full unit/lint commands retain explicitly classified baseline or synchronized-main failures below. This executor does not accept the task or promote downstream tasks.

### Correction checklist

1. **Comparative protocol and regression matrix — implemented.** Added the architect-authorized opt-in comparison to the existing billing runner and its existing exact purchase-history test path. Both versions use identical copied test instrumentation and independently cloned canonical databases. All 29 profiles passed two discarded warm-ups and five recorded samples per version. Saved 406 actual samples, 58 descriptive summaries and four safe plan probes in [the authorized evidence artifact](evidence/API-006-attempt-3-commercial.jsonl). No values are inferred from source or correctness-only tests.
2. **Declared toolchain and broad failure classification — implemented.** Used Node 24.19.0/npm 11.17.0 via the repository bootstrap. Ran the full unit suite and lint from an isolated archive of the pinned baseline (linked accepted Database/client dependencies), then the candidate. The final candidate full-suite result reproduces the classified seven failures; no API-006-owned unit failure remains. Required focused and migrated checks were rerun. The final isolated complete billing runner passed 22 active tests without command-source or timeout changes.

### Attempt 3 files and bounded changes

- `scripts/test-arch041-billing-postgres.mjs`: explicit `ARCH055_COMMERCIAL_COMPARE_BASELINE=1` opt-in, pinned baseline archive, equivalent cloned databases and identical instrumentation. Default suites, additional-suite path checks and command registrations are preserved. The registered history path has one literal to avoid a new static-registration duplicate.
- `tests/integration/billing/purchase-history/arch055-history.postgres.test.ts`: paired profiles, test-local model/SQL/transaction observation, durable-state assertions, isolated batching experiment, safe query-plan nodes and real separate-connection refund snapshot/overflow case. No new production benchmark utility.
- `tests/integration/merchant/usage-history/arch055-query-shapes.postgres.test.ts`: corrected the preserved default-past expected count to31, added current/default v2 coverage, and kept current corrections before the injected clock while historical corrections remain after period close.
- `src/merchant/discount-offers/service.ts`: corrected only the stale5,000-only scan comment: the default is5,000 and configurable source bound20,000; catalogue pagination assumes neither cap. Production batching, authorization, public DTOs and accounting behavior were not further changed in Attempt 3.
- Preserved stranded test work first in implementation checkpoint `eb4fa9d`; no prior report, implementation or baseline history was discarded.

### Fixed-protocol provenance and limits

- Command: `ARCH055_COMMERCIAL_COMPARE_BASELINE=1 node scripts/test-arch041-billing-postgres.mjs`.
- Comparison baseline: `fa2a857ed2ccfd629a7c9f2749ce4a38cc143ff0`; Attempt 3 prepared implementation HEAD: `5ad3a0134957f8bf7f5176c08c61302184dc578f`; exact final source/test snapshot: `19a97ea4f3c3ce729042eacd486bd01d493f2df9`, committed/pushed during the frozen final run.
- Node 24.19.0, npm 11.17.0, Prisma Client 6.19.3. PostgreSQL 17 + pgvector, all 71 canonical migrations deployed from Database pin`5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. No migration, schema, trigger, index or gitlink change was authored by this attempt. Sorted relative migration paths plus each file SHA-256 yield manifest SHA-256 `78229b296aeea5037bd3efa6476eeb1e305ca93f31bfae523b9835fe28032db8`.
- Same migrated empty template cloned into independent baseline/candidate databases. Stable fixture IDs/order/clock per profile/trial in both versions; fresh fixture setup and snapshots outside each measured window. A warmed client is reused within each version and disconnected at shutdown. Clock: `2026-11-02T12:00:00.000Z`. M13 has one current and 30 closed periods with 31 signed events per period (29 × 2 plus two −1 corrections).
- Canonical READY pricing rows require the full 20-locale set, so both versions seed the same 20 translations per plan/highlight, including complete en/fr. Four plans and two highlights each are compared for fr-CA/default en. This compatibility setup does not weaken constraints or rewrite migrations.
- 350 executions measure service methods. The 56 `E-batch-*` executions explicitly measure an isolated, take-aware catalogue batch loop; authorization/reference projection runs outside that timer. Its full IDs/code/cursor/lookahead must equal the production reference. Do not compare those durations with complete service-method durations.
- Logical DB calls include observed model/raw methods plus transaction entry. SQL includes separately recorded BEGIN/isolation/COMMIT/ROLLBACK; relation SQL may exceed logical calls. Returned row counts describe materialized model results and nested arrays; scalar count-result SQL cardinality is not observable and remains null, not guessed. ORM updateMany counts and persisted snapshots separately establish assignments/net target rows.
- Transaction duration includes acquisition, callback and test-proxy overhead; it is not pure pool wait. All 406 executions observed zero callback retries; driver-internal retries, trigger-internal work, wire bytes and runtime provider/R2/queue invocation counts are not measured. Selected services use no provider/R2/queue port; this is static evidence, not a measured zero.
- Generated evidence IDs, DB-generated timestamps, cache/statistics and local scheduling differ between versions; no byte-identical whole-response or production latency/percentile/capacity claim is made. Five recorded samples are descriptive. Only the completed final run supplies the retained paired evidence.
- Artifact SHA-256: `c790ad66f5f911223c1af1bf1fa36d2508ddd24c091cceb87a7d926df46b2b63`.

### SQL, calls and affected rows

Every row below held across all five recorded samples per version. Values are baseline→candidate. Coupon assignments count actual updateMany affected rows; net target rows count distinct persisted changes, including settings and timestamps, not repeated assignments. Read/no-op snapshots remain identical. Expected billing mismatch and unavailable-locale errors account for 28 rolled-back operations; all other 378 operations commit.

| Profile | Logical DB calls | SQL statements | Coupon assignments | Net target rows |
|---|---:|---:|---:|---:|
| M11-promo-0-0 | 9→7 | 12→10 | 0→0 | 0→0 |
| M11-promo-0-7 | 9→8 | 15→14 | 0→0 | 0→0 |
| M11-promo-7-0 | 9→8 | 14→13 | 0→0 | 0→0 |
| M11-promo-7-7 | 9→9 | 17→17 | 0→0 | 0→0 |
| M11-purchase-0 | 4→3 | 6→5 | 0→0 | 0→0 |
| M11-purchase-5 | 4→4 | 9→9 | 0→0 | 0→0 |
| M12-mode | 13→10 | 14→11 | 100→0 | 51→1 |
| M12-replace | 13→12 | 14→13 | 100→2 | 52→3 |
| M12-noop | 10→10 | 11→11 | 0→0 | 0→0 |
| M12-first | 14→11 | 15→12 | 50→50 | 51→51 |
| M13-current-v1 | 10→9 | 13→12 | 0→0 | 0→0 |
| M13-current-v2 | 12→11 | 15→14 | 0→0 | 0→0 |
| M13-default-v1 | 12→9 | 15→12 | 0→0 | 0→0 |
| M13-default-v2 | 14→11 | 17→14 | 0→0 | 0→0 |
| M13-rank2-v1 | 12→9 | 15→12 | 0→0 | 0→0 |
| M13-rank2-v2 | 14→11 | 17→14 | 0→0 | 0→0 |
| M13-rank30-v1 | 12→10 | 15→13 | 0→0 | 0→0 |
| M13-rank30-v2 | 14→12 | 17→15 | 0→0 | 0→0 |
| M14-billing-match | 11→10 | 16→15 | 0→0 | 0→0 |
| M14-billing-mismatch | 11→11 | 16→16 | 0→0 | 0→0 |
| M14-catalogue-fr-CA | 3→3 | 8→8 | 0→0 | 0→0 |
| M14-catalogue-unavailable | 3→3 | 8→8 | 0→0 | 0→0 |
| M14-settings-CURRENT | 7→7 | 9→9 | 0→0 | 0→0 |
| M14-settings-ERROR | 7→7 | 9→9 | 0→0 | 0→0 |
| E-batch-clean-fixed | 2→2 | 4→4 | 0→0 | 0→0 |
| E-batch-clean-small | 2→2 | 4→4 | 0→0 | 0→0 |
| E-batch-invalid-fixed | 2→2 | 4→4 | 0→0 | 0→0 |
| E-batch-invalid-small | 3→3 | 5→5 | 0→0 | 0→0 |
| E-promotion-select | 10→10 | 18→18 | 0→0 | 2→2 |

M12 mode-only changes preserve all coupon flags, dropping 100 flag assignments and 50 timestamp-touched coupon rows. One replacement still changes exactly two flags, but avoids the baseline's redundant rewrites of the other 49 coupons. New settings still select 50 coupons and preserve locked Shop onboarding data. Invalid foreign IDs, anchors, rollback and last-writer behavior remain covered by the full migrated discount suite.

M13 combines count/sum and removes only unused/redundant period reads: current retains its one period lookup; default/within-page historical selection reuses loaded rows; rank 30 retains its explicit off-page lookup. All variants return 31 events and exact signed total 56 in v1/v2, with ambiguous evidence remaining UNATTRIBUTED. Existing cursor, negative-correction and cancellation regressions passed.

M14 matching pending-plan handles remove one lookup; mismatched handles preserve the original conflict and rollback. Catalogue SQL count stays 8 while materialized translation rows drop 240→24; all eight highlights remain. Mixed plan-level fr/en availability (opposing tab-only descriptions accepted by canonical SQL checks but rejected by application trim) must fail with `billing_catalogue_translation_unavailable`, rather than mix languages. Saved settings remain readable with CURRENT and ERROR catalogues.

### Evidence-only decisions and index probes

- **Retain fixed 100 coupon batching.** On 250 clean rows, a first 11 batch returns 11 rather than 100 rows with one query in either case. With an 11-unsafe-code prefix, fixed 100 returns 100 rows in one query; first 11 then 100 returns 111 rows in two queries. Both produce identical safe IDs/cursors/lookahead. No demonstrated universal advantage or production workload mix supports a runtime change; the prototype remains test-only.
- **Retain existing promotion upserts and final selection reread.** Fresh selection uses 10 logical calls/18 SQL statements in both versions and changes two target rows. Actual SQL shows grant upsert's SELECT/INSERT/SELECT plus grant update, and selection's native ON CONFLICT. No alternative write/result-reuse scheme is proven equivalent across accumulated balances/reselection, so no optional rewrite was applied.
- **Retain separate v2 attribution evidence paths.** Raw M13 v1/v2 records expose their additional correction-parent/reservation queries. The same exact signed totals and UNATTRIBUTED outcome hold; focused tests retain legacy, compensated and ambiguous evidence rules. No full consolidated projection was proven equivalent, so no new attribution guess/cache was introduced.
- **Retain indexes.** Safe EXPLAIN ANALYZE/BUFFERS node summaries cover bounded coupon ID/flag paging and purchase ID paging. These are narrow representative probes, not full request plans. The same schema produced different local plan/timing choices; small fixtures/cache/statistics do not justify index DDL or production capacity inference. Full method SQL remains in the samples.

### Descriptive elapsed milliseconds

Each cell is min/median/max over five recorded executions; raw warm-ups, samples and full-precision summaries remain in the artifact. Experimental batch-loop boundaries are distinct as described above.

| Profile | Baseline operation | Baseline transaction | Candidate operation | Candidate transaction |
|---|---:|---:|---:|---:|
| M11-promo-0-0 | 235.73/466.07/637.98 | 235.67/466.03/637.94 | 51.62/74.90/155.68 | 51.59/74.86/155.64 |
| M11-promo-0-7 | 178.88/532.11/1138.34 | 178.85/531.96/1138.29 | 78.04/86.58/133.72 | 77.96/86.36/133.70 |
| M11-promo-7-0 | 144.96/232.77/405.42 | 144.94/232.74/405.40 | 64.82/67.38/236.03 | 64.80/67.36/236.01 |
| M11-promo-7-7 | 271.33/381.90/1219.63 | 271.31/381.85/1219.60 | 101.16/134.03/193.08 | 101.14/134.01/193.05 |
| M11-purchase-0 | 85.70/135.81/376.34 | 85.66/135.77/376.30 | 20.24/21.73/27.38 | 20.17/21.70/27.35 |
| M11-purchase-5 | 218.18/648.15/8753.94 | 218.13/648.12/8753.89 | 24.92/34.64/39.00 | 24.90/34.61/38.97 |
| M12-mode | 211.46/213.31/315.26 | 211.40/213.26/315.22 | 46.43/47.91/66.96 | 46.20/47.88/66.93 |
| M12-replace | 399.24/1212.34/1414.19 | 399.19/1212.29/1414.14 | 49.55/54.83/64.03 | 49.52/54.80/64.00 |
| M12-noop | 81.65/414.59/807.60 | 81.61/414.54/807.56 | 40.71/43.81/50.88 | 40.64/43.77/50.85 |
| M12-first | 172.36/499.23/880.93 | 172.33/499.20/880.89 | 46.63/53.88/58.67 | 46.61/53.85/58.64 |
| M13-current-v1 | 154.06/796.17/1372.45 | 154.01/796.10/1372.39 | 38.17/40.87/57.47 | 38.13/40.84/57.42 |
| M13-current-v2 | 336.94/531.83/1468.02 | 336.68/531.78/1467.98 | 44.39/55.78/60.12 | 44.36/55.74/60.07 |
| M13-default-v1 | 371.76/855.94/2445.65 | 371.73/855.90/2445.62 | 46.32/46.86/74.35 | 46.30/46.84/74.32 |
| M13-default-v2 | 124.55/147.70/300.69 | 124.52/147.66/300.66 | 116.90/168.17/255.50 | 116.88/168.15/255.48 |
| M13-rank2-v1 | 64.33/71.82/86.11 | 64.30/71.79/86.08 | 100.76/408.29/845.80 | 100.73/408.24/845.78 |
| M13-rank2-v2 | 95.15/117.09/196.30 | 95.13/117.07/196.28 | 247.05/500.48/1885.81 | 247.02/500.45/1885.78 |
| M13-rank30-v1 | 55.29/61.21/84.17 | 55.25/61.19/84.14 | 105.06/455.32/2286.96 | 105.04/455.29/2286.93 |
| M13-rank30-v2 | 68.00/71.96/110.16 | 67.98/71.94/110.14 | 191.41/357.16/1966.48 | 191.32/357.09/1966.45 |
| M14-billing-match | 49.80/52.82/59.21 | 49.78/52.80/59.19 | 134.33/256.09/935.62 | 134.30/256.06/935.58 |
| M14-billing-mismatch | 47.29/60.47/77.91 | 47.24/60.33/77.86 | 388.09/507.23/640.40 | 388.02/507.15/640.34 |
| M14-catalogue-fr-CA | 28.10/33.14/39.05 | 28.03/33.08/38.98 | 42.71/104.48/676.71 | 42.64/104.40/676.64 |
| M14-catalogue-unavailable | 29.28/34.15/36.59 | 29.19/34.04/36.49 | 101.60/149.96/397.34 | 101.48/149.82/397.14 |
| M14-settings-CURRENT | 28.10/31.88/51.31 | 28.07/31.85/51.28 | 98.37/439.63/841.18 | 98.33/439.59/841.14 |
| M14-settings-ERROR | 33.00/34.08/37.91 | 32.97/34.05/37.88 | 119.37/285.61/852.78 | 119.33/285.57/852.71 |
| E-batch-clean-fixed | 15.21/21.88/68.99 | 15.19/21.87/68.97 | 105.32/191.25/402.41 | 105.29/191.22/402.33 |
| E-batch-clean-small | 9.14/13.42/90.49 | 9.12/13.41/90.47 | 34.65/56.07/133.31 | 34.56/55.43/133.29 |
| E-batch-invalid-fixed | 14.98/16.97/20.43 | 14.96/16.95/20.41 | 43.78/62.67/300.27 | 43.76/62.58/300.24 |
| E-batch-invalid-small | 20.72/23.33/33.05 | 20.70/23.31/33.03 | 74.34/265.62/740.42 | 74.32/265.60/740.39 |
| E-promotion-select | 63.40/82.26/98.99 | 63.36/82.23/98.93 | 172.02/228.17/2614.28 | 171.98/228.08/2614.24 |

### Validation and F01–F05 results

- `npm run test:arch035-promotions:postgres`: **1/1 passed**, canonical 71 migrations, including selection/replay/tenant/race safeguards.
- `npm run test:arch036-discount-offers:postgres`: **7/7 passed**, canonical 71 migrations, including concurrent Saves, Background-style overlap, failed authorization, outage and foreign-ID rollback.
- `npm run test:arch035-usage-history:postgres`: final **4/4 passed** (two query-shape/large-profile cases plus two existing API-022 cases), canonical 71 migrations.
- `node scripts/test-arch041-billing-postgres.mjs`: final isolated run **22 passed,1 opt-in measurement test skipped,0 failed**, canonical 71 migrations. The opt-in comparison separately passed both versions.
- Exact focused unit command from Validation over the five task domains: **103/103 passed**.
- `npm run typecheck`: final **passed** after canonical Prisma generation.
- `git diff --check`: **passed** on final implementation and parent report/evidence.
- `npm run lint`: only the proven baseline Support error remains, detailed below; task-owned paths have no lint errors.
- **F01:** all four independent promotion emptiness combinations and empty/five-row purchase history pass; only zero-count page methods disappear, counts/default pages/selection remain correct.
- **F02:** 51 coupons/50 selected, mode-only0 versus100 assignments, replacement2 versus100, identical Save0, first settings50; full identity/anchor/rollback/concurrency suite passed.
- **F03:** 30 closed +current periods,31 signed events each, current/default/rank2/rank 30 in both versions, exact56 quantity; migrated cursor/foreign-period/cancellation and focused ambiguity/legacy evidence checks passed.
- **F04:** four plans/two highlights choose one complete fr locale; opposing fr/en incompleteness fails closed on real canonical schema without disabling constraints.
- **F05:** empty/nonempty history,11-refund overflow rejection and separate-client refund insertion after the first RepeatableRead Shop read all passed. The in-flight read excludes the later committed refund, a fresh read observes it, and overflow raises the original integrity error instead of truncating evidence. Existing latest/completed refund projections remain under focused regression.
- An earlier concurrent validation run stalled in unchanged billing command tests with transaction-expiry symptoms. Only this task's verified test-child processes were stopped; the preserved runner caught failure and completed finally-block cleanup. The exact full runner subsequently passed in isolation without command-source or timeout changes. Timing alone does not establish the earlier root cause.

### Broad validation baseline classification

Both baseline and candidate use the declared Node 24.19.0/npm 11.17.0 toolchain and the same accepted canonical client/schema. The baseline ran from a temporary archive with Database/node_modules links; it was never run in the shared checkout.

| Run | Tests | Passed | Failed |
|---|---:|---:|---:|
| Pinned fa2a857 full npm test |657|648|9|
| Final candidate full npm test |669|662|7|

Six failures occur in both:
- `billing/commands/recovery-credit-routes.test.ts`: provider-error bounded-log assertion.
- `billing/commands/subscription-routes.test.ts`: provider-error bounded-log assertion.
- `composition/real-route-registration.test.ts`: route-registration expectation.
- `http/integration-runner-registration.test.ts`: aggregate registration expectation; this task's history suite remains registered once.
- Two `merchant/store-context/routes.test.ts` diagnostic-shape assertions.

Three baseline failures now pass: two merchant-knowledge route/upload diagnostic cases and the promotion-route diagnostic case. This report does not attribute other owners' synchronized fixes to API-006.

The candidate-only `platform-configuration/api-consumers.test.ts` return-proof/keyring case fails because its mock lacks `$transaction` after synchronized-main REST-read authorization changes. The affected authorization source and test are byte-identical to origin/main; no API-006 change touches them. Command source/tests are also unchanged from the pinned baseline and origin/main. No API-006-owned new broad-suite failure was established; these are recorded failures, not fabricated passes or permission for out-of-scope fixes.

Both full lint runs fail only at unchanged `src/merchant/support/routes.ts:75:17`, `no-empty`. Direct baseline execution proves this condition; no matching durable baseline ID was identified. The required lint command was executed and its limitation remains explicit.

### Git, worktree and cleanup evidence

- Mirrored branch: `task/ARCH-055-API-006`.
- Canonical root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent dedicated worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-006`.
- Implementation dedicated worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-006`.
- Architect recovery`d312fd6abe4c70e95375972937d53bafb9c178c7` preserved Attempt 2 and cleared the interrupted Copilot claim; test checkpoint`eb4fa9d` was published before new preparation.
- Prepared Codex Attempt 3 claim`1032f760368d3e8c3d4dd06ab4ed7968795eddc8` was committed/pushed by the launcher, dependency gate passed. Both dedicated worktrees were reused; both remote task branches needed no fast-forward and both already incorporated origin/main. Recursive submodule sync/update passed at the recorded Database pin above. Pre-preparation clean-checkout alignment repaired only the nested checkout, not its gitlink.
- Final implementation`19a97ea4f3c3ce729042eacd486bd01d493f2df9` is pushed to`origin/task/ARCH-055-API-006`; implementation worktree clean.
- This report's containing parent commit publishes only the current task and its architect-authorized JSONL artifact on parent`task/ARCH-055-API-006`; no implementation submodule gitlink staged.
- Shared checkouts were not switched for implementation; no other task worktree reused. No main merge/push, force push, schema edit, new index or downstream promotion.
- Successful runners completed cleanup; failed/stopped runner cleanup also completed. Paired baseline archives/comparison databases were removed by finally blocks. The task-owned full-unit baseline archive was removed after classification; diagnostic logs remain local. Unrelated pre-existing containers were left untouched.

### Remaining limits

Broad unit/lint baseline/main failures remain as classified; live provider certification and production capacity are not claimed. No task-owned required correctness or paired-measurement work remains knowingly incomplete. Await architect review; do not start API-009 or SYSTEM-TEST-001.

## Completion Report — Attempt 4

### Correction and review status

The Attempt 3 P2 is implemented in both route boundaries. The original wrapper and its immediate database Error cause pass through Shared sanitization as explicit `error`/`errorCause` fields; a validated Prisma/SQLSTATE code is retained as `databaseCode`. Shared owns serialization and bounds. Boundary redaction removes connection URLs, credentials, bearer values, customer contact details and unsafe Prisma invocation/query context before truncation. Raw stacks, metadata, query arguments and customer payloads are not projected. Exceptions are not mutated. This is an explicit immediate database-cause projection, not arbitrary-depth cause traversal or a new generic logging framework.

The direct discount-offers P2002/P2034 conflict branch now emits one safe diagnostic as well. HTTP status, public error body and private/no-store behavior remain unchanged. Changes are confined to the two route files, their two unit-test files and the architect-authorized API consumer `database` gitlink.

### Validation

- Real Shared-sink route regressions: **12/12 passed**. Wrapped safe original P2034/P2003 messages and codes survive GET/PUT; secret-bearing text, arbitrary metadata and truncation-boundary secrets are absent; original exceptions and public responses remain unchanged. Direct unwrapped conflict logging is covered.
- Required five-directory focused unit command: **108/108 passed**, no skips (103 prior tests plus five new cases).
- Final `npm run typecheck`: passed, explicitly confirmed exit 0 after regenerating the canonical client on the authorized integrated pin.
- Changed-file ESLint with `--max-warnings=0`: passed for both routes and both test files. Working and staged diff checks passed.
- No new full-suite/full-lint pass is claimed. Attempt 3's explicit baseline/main failure classification remains historical and preserved. The unchanged PostgreSQL correctness and commercial measurements were not rerun, as allowed by the Attempt 3 review and Attempt 4 pin amendment.

### Accepted consumer-pin reconciliation and retained evidence

Preparation restored the recorded Database `7c377282aa5819b3008b7d7f3018f44f4161523e`. Initial typecheck then reported 13 missing `intentPurposeKey` diagnostics in synchronized API-005 knowledge-upload source/tests. The architect authorized this task's consumer-only pin correction to integrated Database `8e74634ff92be9900f693c0c449ffce888e7d617` (PR #68). It has exactly the same Git tree `9a91d956274810aeedd168c83b72c50f6d7f29f8` as the accepted measurement version `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`; their diff is empty. Canonical Prisma Client 6.19.3 was regenerated on Node 24.19.0/npm 11.17.0. No Database schema/migration files or other owner's source were edited, and no validation waiver was used.

An attempted isolated prepared-baseline reproduction did not execute because temporary-file creation hit a full disk; it is not reported as a passed comparison or reproduced baseline. Only this task's redundant temporary raw measurement logs were removed after verifying their durable artifact. No global cleanup or unrelated container removal was performed.

The retained measurement artifact `evidence/API-006-attempt-3-commercial.jsonl` remains unchanged: SHA-256 `c790ad66f5f911223c1af1bf1fa36d2508ddd24c091cceb87a7d926df46b2b63`, 406 samples, 58 summaries and four plans. Attempt 3's protocol, measurement limits, F01–F05 results and broad-failure classifications remain preserved above. Route diagnostic changes do not alter the measured service-method boundaries; the final database pin has identical accepted schema/migration contents.

### Preparation, assistance and publication

- Canonical launcher claimed Codex Attempt 4 at `2026-11-03T10:18:24Z`; claim `fc66a1d9b9ff7c95b670676b6601f35f5ec00ead` was pushed. Dependency checks passed. Prepared implementation HEAD `fe7658a12f8780ebea89cfaa30b738aa107126f9`; parent pre-claim HEAD `93546f14a09db5afb40a30d88d79c25e351d577a`.
- Both canonical dedicated worktrees were reused; remote task branches needed no fast-forward and origin/main was already current. Recursive submodule sync/update passed. The prepared pin and final authorized pin are distinguished above.
- The user-requested `moda_architect` assistance established squash-equivalent Database tree evidence, authored the narrow consumer-pin scope amendment below and reviewed the diagnostic approach. It did not grant acceptance or waive checks.
- Mirrored branch `task/ARCH-055-API-006`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-006`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-006`.
- Final implementation `6757372ddc2b7cae7ab3e9714546ea309a53ff9a` is pushed to `origin/task/ARCH-055-API-006`; implementation worktree is clean. The containing parent report commit publishes only this task document, including the architect-authored amendment. No parent implementation gitlink, main merge/push, force push or downstream promotion.

Await architect review. API-009 and SYSTEM-TEST-001 remain pending; this executor does not mark API-006 Complete.

## Completion Report — Attempt 5

### Correction checklist and bounded implementation

**Attempt 4 P2 — implemented.** In `src/merchant/promotions/routes.ts` and `src/merchant/discount-offers/routes.ts`, the Prisma invocation redaction now retains the exact unindented final database-reason line for P2003 foreign-key, P2002 unique-constraint and P2034 write-conflict/deadlock errors. A recognized header and completed renderer boundary are required: no context, numbered source context, or a completed argument closure followed by a blank separator. Invocation headers, source locations, numbered/arrow code frames and rendered arguments are removed. The retained line still passes through the existing sensitive-span filters before Shared truncation. No guessed explanation replaces the source text; codes still come from the original exception. Unknown/incomplete invocation renderings remain `[REDACTED]` with their actual code, rather than exposing potentially unsafe context. This narrowly handles the known database failures at these routes; it is not a generic Prisma formatter/parser or recursive error serializer.

Both existing route test files now exercise actual handlers through the real Shared sink for GET and PUT. Eight fixtures per route cover a secret/customer-bearing pretty argument block longer than Shared's string limit, numbered source context immediately followed by the original reason, minimal formatting, CRLF unique-constraint formatting, source-context foreign-key formatting, combined source/arguments formatting ending in `})`, an unfinished argument block ending in a misleading reason line, and an incomplete invocation without a safe suffix. Misleading reason text inside a quoted argument/source line is excluded. Tests retain the safe source line/code, reject invocation/customer values, raw metadata/query/payload/stack, preserve original exception/cause identity, and assert unchanged public 409 bodies and cache headers. Existing simple-cause, privacy, truncation and direct unwrapped-conflict regressions remain in place.

### Actual validation

- Before the correction, the new route tests reproduced the issue: **12 passed, 2 failed** (both new multiline cases), exit 1; failure logs contained only `[REDACTED]` instead of the safe foreign-key reason.
- Final affected route command: **14 passed, 0 failed, 0 skipped**, exit 0.
- Required five-directory focused matrix: **110 passed, 0 failed, 0 skipped**, exit 0 (108 previous tests plus the two parameterized multiline cases).
- Changed-file ESLint on both routes and both route test files with `--max-warnings=0`: exit 0.
- Final `npm run typecheck`: passed, explicitly confirmed exit 0 on the final committed source. A superseded intermediate typecheck was explicitly stopped (exit 143) after the last renderer hardening; that interrupted run is not reported as a pass. The final-source run is tracked separately by its confirmed command exit.
- Working/staged and final implementation commit diff checks: passed.
- Commands used the repository bootstrap, Node 24.19.0/npm 11.17.0 and the canonical regenerated Prisma 6.19.3 client. Local validation logs use `/tmp/arch055-api006-*-attempt5.log`; no new evidence path or benchmark framework was introduced.

### Retained evidence and limits

Attempt 4's consumer pin remains `8e74634ff92be9900f693c0c449ffce888e7d617`, as prepared; no gitlink/schema/migration changes were authored in Attempt 5. The retained commercial JSONL remains SHA-256 `c790ad66f5f911223c1af1bf1fa36d2508ddd24c091cceb87a7d926df46b2b63`. Prior M11–M14/F01–F05 measurements, their limits and broad unit/lint failure classifications remain preserved. No new PostgreSQL, commercial measurement, full-unit or full-lint execution/pass is claimed. The latest review explicitly permits retaining that unaffected evidence for this route-diagnostic correction.

### Preparation, assistance and publication

- Deterministic launcher claimed Codex Attempt 5 at `2026-11-03T11:00:45Z`, pushed claim `a0eec3f6511d2eab43a9d22465662fa7bcb38a1b`; dependency gate passed with no explicit dependencies. Prepared parent head `c54169532d9ff3a2d067f4d64ec91492a1761ee3`; implementation head `6757372ddc2b7cae7ab3e9714546ea309a53ff9a`.
- Canonical root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; dedicated parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-006`; dedicated implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-006`; both branches `task/ARCH-055-API-006`.
- Both physical worktrees were reused. Both remote task branches needed no fast-forward; parent origin/main incorporation passed (`yes`), implementation was already current. Recursive submodule sync/update and recorded Database pin verification passed. Shared/default checkouts were not switched or used for implementation; no other task worktree was reused.
- The user-requested `moda_architect` assistance advised the narrow Prisma rendering boundary, safe reason projection and regression matrix; no implementation edits, lifecycle decisions or acceptance were delegated.
- Implementation `c78b6e5b137d04b1b56aedf853c654ebd9c46b23` is pushed to `origin/task/ARCH-055-API-006`; implementation worktree is clean. The containing parent report commit publishes only this task document. No parent implementation gitlink, main merge/push, force push, other task edits or downstream promotion.

Ready for Review. Required final validation passed. This executor does not accept API-006 or start API-009/SYSTEM-TEST-001; both enabled tasks remain pending.

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


## Architect Review — Evidence retention amendment, Attempt 3, 3 November 2026

Authorize the single parent task-owned JSONL artifact named in Scope for durable M11–M14 sample retention. This narrowly supersedes prior no-new-files wording only for that evidence artifact; it does not authorize additional implementation/test paths, runtime behavior, index DDL, another repository or broader runner registrations. The repository executor may publish the actual artifact and this report together on parent `task/ARCH-055-API-006`. Preserve explicit unmeasured fields and descriptive-only timing limits. This amendment does not accept the task, change its claim or promote dependants.


### Opt-in orchestration clarification — Attempt 3

The fixed M11–M14 evidence protocol may be orchestrated centrally by the existing billing runner only through the explicit opt-in exception now named in Scope. Keeping the cases in the exact existing authorized test file avoids adding a standalone benchmark framework or scattered duplicated orchestration. The opt-in may exercise only this task's named commercial services and profiles; it does not expand production ownership or alter the default billing-command suite list/path checks. No measurements are waived, no baseline history is rewritten, and actual baseline incompatibility must be reported rather than inferred. The authorized parent evidence filename is `API-006-attempt-3-commercial.jsonl`. No claim, acceptance or dependency state changes are made by this clarification.


## Architect Review — Attempt 3, 3 November 2026

### Review Status

**Changes Requested.** Implementation `19a97ea4f3c3ce729042eacd486bd01d493f2df9`, submitted parent `a8595845c7b3bd9a4bec27c1539865dc515ea1b4`. Return to `ready`, clear executor/claimed_at and preserve Attempt 3. No acceptance or downstream promotion.

### Review Finding

1. **[P2] Preserve original error causes and database codes through both route loggers.** `src/merchant/promotions/routes.ts:21–26` and `src/merchant/discount-offers/routes.ts:10–15` replace every Error with a plain `{ name, message }` object before passing it to Shared. This drops its cause, Prisma code and other safe originating details. Consequently the newly cause-preserving service wrappers still log only `promotion_revision_conflict` or `offers_conflict`, losing the actual database failure. This violates Requirement 9 and the explicit original-diagnostic acceptance criterion. The helpers were introduced by this task, so this is not a synchronized-main baseline failure. Preserve the original Error/cause through the approved Shared logger's bounded sanitization path, keeping secrets/URLs/customer contents out of logs and leaving public responses unchanged. Do not duplicate a generic error serializer or solve the issue by discarding the cause. Add route-level regressions for a wrapped Prisma-like error with a safe original message/code and for secret-bearing details; verify emitted private diagnostics retain the safe evidence and public responses remain bounded.

Independent reproduction invoked both actual route handlers with a wrapped database Error and capturing logger. Promotions returned HTTP 409 with a log containing only reason/message `promotion_revision_conflict`; discount settings returned HTTP 409 with only `offers_conflict`. Neither retained the injected safe original message or original `P2034`/`P2003` code. The service wrappers themselves already retain `cause`; the loss occurs at the changed route boundary.

### Previous Findings and Evidence Reviewed

- The Attempt 1 comparative-evidence gap is addressed by the retained artifact and authorized opt-in orchestration. Independently parsed all **468 JSONL records: 406 samples, 58 summaries and four plan probes**. All 58 version/profile groups contain exactly two warm-ups and five recorded samples; SQL-shape totals, logical-call totals and every min/median/max summary reconcile to the raw records. SHA-256 matches `c790ad66f5f911223c1af1bf1fa36d2508ddd24c091cceb87a7d926df46b2b63`.
- Reviewed identical copied instrumentation, isolated baseline archive and cloned canonical databases, fixture setup outside measurement windows, explicit measurement limits, M11–M14 assertions and retained/deferred options. The refund test uses a separate mutator connection and a read barrier; large signed usage fixtures and empty/nonempty history coverage address the previous F01–F05 evidence gaps. These recorded runs were not independently repeated in this review. Retain the artifact; the diagnostic correction does not require discarding or rerunning unaffected commercial measurements.
- The report now classifies full-suite baseline versus candidate/main failures using Node 24.19.0/npm 11.17.0. Independently confirmed the cited REST-read authorization source, platform-configuration test and Support route are unchanged from the available origin/main, and billing-command source/tests are unchanged from the prepared baseline. The reported full baseline/candidate runs were reviewed, not independently repeated. Their failures remain explicit; no full-suite or full-lint pass is claimed.

### Independent Validation and Scope

- Required focused five-domain unit matrix: **103 passed, 0 failed**, using Node 24.19.0.
- `git diff --check origin/main..HEAD`: passed.
- Both task worktrees were clean and local heads matched their published task refs before this overlay. Database pin remains accepted `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`.
- Inspected Attempt 3 runner/test changes, final task-owned source differences and the previous review. Main synchronization changes were distinguished from API-006 changes. No implementation source or evidence artifact was edited by this review; no implementation commit/push, parent gitlink update or main merge occurred.

### Follow-up

Correct the two diagnostic helpers and add meaningful safe-cause/code/redaction regressions on the same branch. Rerun affected route/focused tests, typecheck, changed-file lint and diff checks; update the report with actual results. Preserve the passing commercial evidence and historical baseline classifications, revisiting only evidence invalidated by subsequent code changes. `ARCH-055-API-009` and `ARCH-055-SYSTEM-TEST-001` remain Pending because API-006 is not Complete. The next launcher claim owns Attempt 4.


## Architect Review — Accepted Database consumer-pin reconciliation, Attempt 4, 3 November 2026

### Disposition

The prepared Attempt 4 packet correctly materialised its recorded Database gitlink `7c377282aa5819b3008b7d7f3018f44f4161523e`. Subsequent typecheck exposes the missing `intentPurposeKey` contract in synchronized API-005 knowledge code/tests; that older pin omits the accepted ARCH-055 persistence changes. This is synchronization/dependency drift, not authorization to edit API-005 source or a consumer's schema copy.

The current DATABASE-001 task is Complete and its Accepted decision explicitly names `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. Database `origin/main` commit `8e74634ff92be9900f693c0c449ffce888e7d617` is the developer's squash integration of that task (PR #68). Read-only comparison establishes identical Git trees for both commits: `9a91d956274810aeedd168c83b72c50f6d7f29f8`; `git diff 5907b4572ea9efc2a24c07e4c3bd3e107db4260b..8e74634ff92be9900f693c0c449ffce888e7d617` is empty. The accepted feature commit not being an ancestor of main is explained by squash integration; it does not mean its contract is unintegrated.

### Narrow consumer authority

Under this task's existing Common execution contract and DATABASE-001's accepted consumer-pin handoff, the API repository owner may update only its own `database` gitlink on `task/ARCH-055-API-006` to integrated commit `8e74634ff92be9900f693c0c449ffce888e7d617`. This is the content-identical integrated form of the previously reviewed `5907b45` pin, not a new schema choice. Do not edit nested Prisma/schema/migration files, change Database branches, stage the parent workspace's implementation gitlink, merge/push main, or repair unrelated API source.

Record the prepared `7c37728` pin separately from the post-reconciliation `8e74634` pin, exact tree-equivalence evidence, regenerated canonical client and actual typecheck/affected validation results in the Completion Report. Keep any baseline comparison results obtained before adoption explicit; do not describe an unavailable check as passed. The commercial measurement artifact remains historical evidence against the identical accepted schema/migration tree; this gitlink correction and diagnostic-only rework do not themselves require rerunning unaffected commercial profiles.

The complete Attempt 3 diagnostic Changes Requested contract remains mandatory. This amendment grants no test waiver, acceptance, claim change or downstream promotion. A failed check after alignment must still be investigated and reported on its actual evidence.


## Architect Review — Attempt 4, 3 November 2026

### Review Status

**Changes Requested.** Reviewed implementation `6757372ddc2b7cae7ab3e9714546ea309a53ff9a` and parent submission `53f3b9ae482ecd2390820dd15b5b23b077a19b7a`. Return to Ready, clear executor/claimed_at and retain Attempt 4. No acceptance or downstream promotion.

### Remaining Finding

1. **[P2] Preserve the safe failure reason after Prisma's invocation preamble.** Both route helpers now retain the immediate cause and database code, but their first redaction expression (`/\bInvalid[\s\S]*?\binvocation\b[\s\S]*/gi`) replaces everything from `Invalid` to the end of the message. Ordinary Prisma errors start with an invocation preamble and place the actual constraint/transaction failure after it. A safe message such as `Invalid prisma.example.update() invocation: ... Foreign key constraint violated on the constraint: safe_fk_constraint` therefore loses the entire originating reason. This is the remaining portion of the Attempt 3 original-message finding, not a request for a new diagnostic framework. Redact invocation arguments/query/customer context while retaining a bounded safe database failure description and code. Add a realistic multiline Prisma-format regression to both route tests, including a secret-bearing invocation section, through the real Shared sink. Continue excluding raw stacks/metadata/customer values and preserving the public response; do not merely remove the redaction wholesale.

Independent reproduction constructed a `PrismaClientKnownRequestError` with a normal multiline invocation preamble and safe foreign-key failure suffix, wrapped it in each existing domain error, and invoked the actual GET routes with the real Shared logger. Both returned their unchanged public 409, but emitted `errorCause: { name: "PrismaClientKnownRequestError", message: "\n[REDACTED]" }` and `databaseCode: "P2003"`; the original safe failure description was absent. The new tests use messages that start directly with `Original ... failure`, so they do not exercise this normal Prisma format.

### Resolved Items and Validation

- Explicit cause projection, code retention, direct unwrapped discount conflict logging, original-exception immutability, public response stability and tested secret/truncation handling are improved and supported by the new real-sink tests.
- Independently reran the full required five-directory focused matrix on Node 24.19.0: **108 passed, 0 failed, 0 skipped**.
- Independently checked `git diff --check fe7658a..HEAD`: passed.
- Confirmed the authorized Database pin `8e74634ff92be9900f693c0c449ffce888e7d617` has no tree difference from accepted `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. The pin correction is accepted scope and introduces no schema change.
- Measurement artifact remains unchanged at SHA-256 `c790ad66f5f911223c1af1bf1fa36d2508ddd24c091cceb87a7d926df46b2b63`. The previous M11–M14/F01–F05 evidence and broad failure classifications remain applicable; unaffected measurements do not need repeating for this diagnostic correction.
- Reviewed reported final typecheck and changed-file lint passes; these were not independently rerun. No new full-suite/full-lint or PostgreSQL execution is claimed in this review.
- Both task branches matched their published revisions and worktrees were clean before this overlay. Review scope was the correction commit, its tests, accepted pin amendment and retained evidence.

### Follow-up

Apply the bounded message-preservation correction in the existing two routes and tests, run affected/focused regressions, typecheck, changed-file lint and diff checks, and resubmit with actual results. Preserve historical reports and commercial evidence. API-009 and SYSTEM-TEST-001 remain Pending because API-006 is not Complete. The next launcher claim owns Attempt 5. No implementation edits/commits/pushes, parent gitlink changes, deployment or main merge were made by this review.


## Architect Review — Attempt 5, 3 November 2026

### Review Status

**Accepted.** Implementation `c78b6e5b137d04b1b56aedf853c654ebd9c46b23`, submitted parent `1ca913bb7127ffce809b01524cb9d1d5493f3135`. Automatic-completion task moves to Complete, preserving Attempt 5 and clearing executor/claimed_at. No blocking findings remain.

### Findings Resolved

The remaining Attempt 4 P2 is resolved in both route boundaries. For the handled P2002/P2003/P2034 Prisma formats, the final safe source reason is retained only after a recognized invocation/header and completed rendering boundary. Invocation arguments, code/source context, arbitrary metadata and stacks remain excluded; the retained reason passes through the existing sensitive-span filters before Shared bounds. Original exception/cause identity and the source database code are preserved, with unchanged public response/status/cache behavior. Unknown or incomplete invocation layouts remain redacted with their code; this explicit privacy fallback does not invent a database explanation.

Inspected both route changes and real Shared-sink GET/PUT regressions covering argument blocks beyond the string bound, source frames, minimal/CRLF formats, combined source/arguments and misleading or incomplete renderings. The tests verify retained safe reasons and exclusion of private/customer/invocation values. The code remains scoped to this diagnostic correction; no commercial service method or query behavior changed in Attempt 5.

The earlier M11–M14/F01–F05 evidence and baseline classifications remain accepted supporting evidence from the previous reviews. Independently reconfirmed the unchanged artifact SHA-256 `c790ad66f5f911223c1af1bf1fa36d2508ddd24c091cceb87a7d926df46b2b63`. No repeated commercial measurements are required for this diagnostic-only correction or the already-approved content-identical integrated Database pin.

### Validation Reviewed

- Independently reran the required five-directory focused unit matrix with Node 24.19.0: **110 passed, 0 failed, 0 skipped**, exit 0, including both new parameterized multiline Prisma regressions.
- Independently checked `git diff --check 6757372..HEAD`: passed.
- Reviewed reported final-source typecheck and changed-file ESLint passes. These were not independently rerun; no new full-suite/full-lint or PostgreSQL execution is claimed here.
- Previously recorded broader baseline/main failures remain explicit limitations, not a claimed full-suite pass. This review establishes no new task-owned failure.
- Both dedicated task worktrees were clean and their published task refs matched the reviewed implementation and submitted parent heads before this overlay. The accepted integrated Database pin is retained; no schema or migration change was authored by this attempt.

### Architecture Conformance and Dependencies

All prior blocking findings are closed. Commercial accounting, public contracts, snapshot/cursor semantics and optional retain/defer decisions remain as previously reviewed. API-009 still has incomplete API-004 and API-007 prerequisites in the canonical task records; it stays Pending. SYSTEM-TEST-001 likewise stays Pending on remaining implementation prerequisites. Acceptance of API-006 satisfies its dependency edges but does not claim either dependent ready or the architecture implemented. No implementation source/commit/push, parent implementation gitlink, main merge or deployed environment was changed by this review.
