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
attempt: 0
depends_on: []
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: '2026-11-02'
---

# ARCH-055-API-006: Optimise commercial settings and reporting projections

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `ready` solely from the dependency graph below.

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

### Common execution and safety contract

- Read this task, the parent architecture, `docs/observability/shared-logging.md` and the four workspace VCS/worktree/developer/materialisation policies. Use the launcher-resolved dedicated parent and implementation worktrees; do not invent paths or start another task. A prepared launcher packet is accepted startup evidence.
- Use the existing Node/toolchain. Before the first Node command: `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`. Do not select/install a different Node version to make validation appear to pass.
- All workspace edits use repository-relative paths. Never edit another repository's implementation or a nested Database schema copy. A consumer records/updates only its own accepted nested Database pin under the task contract; never stage the parent workspace gitlink to an unmerged implementation commit.
- Shared logging is `@modainteract/moda-interact-shared/logging`. Preserve the actual original Prisma/SDK/provider message, code, cause and relevant safe response details through typed errors. Internal reason codes supplement, never replace, that evidence. Redact secrets, signed capabilities, customer content and connection URLs; public responses stay bounded. No generic local logger or duplicate framework telemetry.
- Preserve tenant scoping, canonical Shared schemas, immutable evidence, deliberate no-op/replay rules and original provider ambiguity. No provider/Redis/R2 I/O inside a database transaction. Read endpoints remain free of writes unless an explicitly unchanged contract says otherwise.
- Review baseline observations are static. Run regression tests against canonical migrations on disposable PostgreSQL 17 + pgvector, using separate connections and explicit barriers for races. Do not substitute mocks, `db push` or review-only Python models for lock/trigger proof.
- For each mandatory optimisation capture before/after actual SQL and affected rows on the same fixtures; distinguish client calls, SQL statements and row/byte changes. State workload and measurement limits. Optional MEASURE-FIRST items can conclude 'retain', with evidence and rationale; mandatory correctness changes cannot be deferred this way.
- Existing baseline failures are handled through `docs/development-baseline.md` only when actually encountered and relevant. Do not waive new regressions. Record commands actually executed and leave unavailable validations unchecked.
- Do not edit any `docs/decisions/**/_index.md`, old task status, the parent architecture, another task or shared execution rollup from a repository implementation task. Parent report updates are confined to this task file. No merge or push to main.

## Work Items

- [ ] Implement empty-page short circuits and projection narrowing.
- [ ] Persist coupon selection differences and reuse settings/locked fields with all selection regressions.
- [ ] Combine usage aggregates and reuse period projections.
- [ ] Narrow plan locale relations and apply guarded pending-plan reuse.
- [ ] Add dedicated migrated purchase-history tests and before/after SQL/row metrics.
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

- [ ] No accounting balances, reservation semantics, correction quantities or public versioned schemas change.
- [ ] Same-snapshot zero-count branches issue no page lookup.
- [ ] Coupon mode-only change touches zero coupon rows; one-of-50 replacement touches two, with full identity validation retained.
- [ ] One aggregate supplies count and sum; historical-period and cursor validation remain correct.
- [ ] Settings remain available during coupon sync/outage; whole-catalogue locale fallback is unchanged.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npm run test:arch035-promotions:postgres`
- [ ] `npm run test:arch036-discount-offers:postgres`
- [ ] `npm run test:arch035-usage-history:postgres`
- [ ] `node scripts/test-arch041-billing-postgres.mjs`
- [ ] `npx tsx --test "tests/unit/merchant/promotions/*.test.ts" "tests/unit/merchant/discount-offers/*.test.ts" "tests/unit/merchant/usage-history/*.test.ts" "tests/unit/billing/presentation/*.test.ts" "tests/unit/billing/purchase-history/*.test.ts"`
- [ ] `npm run typecheck`
- [ ] `git diff --check`
- [ ] Run the repository's declared linter against the exact changed source/test files; record any broader unchanged baseline failure separately.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

This task owns presentation/history test registration in the billing runner; ARCH-055-API-007 owns command fixtures. Both edits must remain narrow and be rebased normally rather than dropping the other suite.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None. Task definition only.

### Validation Results

Not run. Record each command, outcome, fixture/migration identity, actual SQL/rows, concurrency schedule and resource cleanup here.

### Worktree and Git Evidence

Not materialised. Record launcher packet, physical parent/implementation worktrees, both task branches, synchronized SHAs, accepted nested Database pin, commits/pushes and any exact publication failure.

### Deviations

None authorised.

### Assumptions

The uploaded source snapshot is the design baseline, not proof of current remote state. Reconcile only relevant drift on the real launcher baseline; return contract-changing drift to the architect.

### Unresolved Issues

Required implementation/validation has not started. Do not pre-check acceptance items.

### Architectural Concerns

Report ownership, schema, contract, external dependency, new index/infrastructure or transaction-boundary gaps here. Do not expand scope silently.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition issued; implementation has not been reviewed or accepted.

### Reviewed Files

No implementation submitted for this task.

### Validation Reviewed

No implementation validation submitted.

### Architecture Conformance

To be assessed against ARCH-055 and this task's frozen contract.

### Follow-up

Only the authorised review may accept this task and promote dependants.
