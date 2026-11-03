---
id: ARCH-055-SYSTEM-TEST-001
architecture_id: ARCH-055
title: Validate the accepted database corrections end to end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-055-DATABASE-001
- ARCH-055-BACKGROUND-001
- ARCH-055-SHOPIFY-001
- ARCH-055-API-001
- ARCH-055-API-002
- ARCH-055-API-003
- ARCH-055-API-004
- ARCH-055-API-005
- ARCH-055-API-006
- ARCH-055-API-007
- ARCH-055-API-008
- ARCH-055-API-009
enables: []
created: '2026-11-02'
updated: '2026-11-02'
---

# ARCH-055-SYSTEM-TEST-001: Validate the accepted database corrections end to end

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 2. API-owned workflow / forward-migration contract; supersedes definition revision 1 without claiming an implementation attempt.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `pending` solely from the dependency graph below.

## Objective

Independently validate the accepted ARCH-055 persistence and query contracts across real service boundaries, with explicit correctness and performance evidence rather than source-count claims.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E01`, `E02`, `E03`, `E04`, `E05`, `E06`, `E07`, `E08`, `E09`, `E10`, `E11`, `E12`, `E13`, `E14`, `E15`, `E16`, `E17`, `E18`, `E19`, `E20`, `E21`, `E22`, `E23`, `E24`, `E25`, `E26`, `E27`, `E28`, `E29`, `E30`, `E31`, `E32`, `E33`, `E34`, `E35`, `E36`, `E37`, `E38`, `E39`, `E40`, `E41`, `E42`, `E43`, `E44`, `E45`, `E46`, `E47`, `E48`, `E49`, `E50`, `E51`, `E52`, `E53`, `E54`, `E55`, `E56`, `E57`, `E58`, `E59`, `E60`, `E61`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-system-test`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `catalogue/scenarios.json`
- `src/harness/runner.js [registration only]`
- `src/harness/selection.js [suite selection only if needed]`
- `src/harness/arch055/ [new modular executors/fixtures/assertions]`
- `test/harness/arch055-*.test.js [new]`
- `scripts/run-system-tests.js [reuse CLI; no parallel runner]`
- `package.json [new system:arch055 scripts only]`
- `docs/ [task-local evidence instructions]`

Required new paths (only these are allowed to be absent at startup):

- `src/harness/arch055/`
- `test/harness/arch055-contracts.test.js`

### Exact edit map — definition revision 2

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `catalogue/scenarios.json; src/harness/runner.js; src/harness/selection.js` | REGISTER arch055 suite and the twelve exact scenarios below; preserve runner/executor/evidence conventions. Scenario IDs ARCH055-IDENTITY-001, ARCH055-CONSENT-001, ARCH055-SETTINGS-001, ARCH055-INBOX-001, ARCH055-KNOWLEDGE-001, ARCH055-COMMERCIAL-001, ARCH055-BILLING-001, ARCH055-SUPPORT-001, ARCH055-READINESS-001, ARCH055-MIGRATION-001, ARCH055-CLAIM-001, ARCH055-COVERAGE-001. |
| `src/harness/arch055/executors.js; src/harness/arch055/fixtures.js; src/harness/arch055/assertions.js; src/harness/arch055/contracts.js` | CREATE modular router/fixtures/assertions/contracts. Add separate identity.js, consent.js, settings.js, inbox.js, knowledge.js, commercial.js, billing.js, support.js, readiness.js, migration.js, claim.js, coverage.js executor modules under same directory; do not build one monolith. Use actual services/HTTP; providers sandbox/emulated, never live payments. |
| `test/harness/arch055-contracts.test.js; package.json` | CREATE harness registration/strict failure tests. Add system:arch055:plan and system:arch055 keys already specified; no alternate runner. |

**Exact new implementation/test paths (not baseline files claimed to exist):**

- `src/harness/arch055/executors.js`
- `src/harness/arch055/fixtures.js`
- `src/harness/arch055/assertions.js`
- `src/harness/arch055/contracts.js`
- `src/harness/arch055/identity.js`
- `src/harness/arch055/consent.js`
- `src/harness/arch055/settings.js`
- `src/harness/arch055/inbox.js`
- `src/harness/arch055/knowledge.js`
- `src/harness/arch055/commercial.js`
- `src/harness/arch055/billing.js`
- `src/harness/arch055/support.js`
- `src/harness/arch055/readiness.js`
- `src/harness/arch055/migration.js`
- `src/harness/arch055/claim.js`
- `src/harness/arch055/coverage.js`
- `test/harness/arch055-contracts.test.js`

**Test registration:** Use existing runner suite selection. Exact package additions remain system:arch055:plan=node scripts/run-system-tests.js --suite arch055 --list and system:arch055=node scripts/run-system-tests.js --suite arch055 --execute.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. All twelve non-system prerequisites must be Complete and architect-accepted before execution. The developer may manually validate first; do not encode that optional checkpoint as a synthetic task dependency. This task never gates unfinished implementation.

2. Reuse the existing JavaScript system-test catalogue, runner, data-plane, provider emulators and provenance/redaction utilities. Keep black-box HTTP/service tests primary; test-only barriers or real competing worker invocations must be explicit and excluded from production code. Split executors/fixtures/assertions into focused files below 300 lines where practical.

3. Exercise real authentication then reconnect/revoke before REST/billing admission; callback overlap and post-revoke replay; suspended mint; consent duplicates followed by REVOKE/STOP and current merchant-only/global STOP policy; coherent category/Support reads; prepared-content moderation differing from original.

4. Exercise Woo and Shopify human sends with identical public retry keys for two Shops and mixed platforms, legacy backfilled claim keys, same-Shop replay, cancellation/reclaim and uncertain provider outcomes. All providers use the same persisted claim contract and the existing single-follow-up limit.

5. Run API knowledge writes against the actual accepted Background entitlement-generation and cleanup writers using separate DB connections and deterministic barriers. Prove cleanup-wins/finalisation-wins, no resurrection, purpose/MIME rechecks, original-intake replay after reprocessing, stale metadata/delete rejection and full rollback.

6. Exercise provider calls only through the deterministic sandbox/emulator boundary. Verify financial intent survives uncertain outcome and post-admission rotation, no early credit/paid activation, exact quote replay, webhook durable receipt and concurrent raw-digest deduplication. Do not certify live payment/refund provider behaviour from emulation.

7. For every selected optimisation, compare same-fixture baseline and changed SQL, affected rows, bytes/projection sizes where observable, transaction/lock/pool waits and latency distribution under a declared local workload. Include success, empty, replay/no-op, stale/conflict and failure paths. No aggregate percentage speedup, production capacity claim or Shopify ingress figure may be substituted for Woo demand.

8. Run all 61 endpoint invariants through the coverage register, including retained routes. Record retained/changed/measure-first decisions and tested/not-run outcomes separately. A missing required scenario is blocked/failed, not silently skipped. Keep review-only models separate from runtime proof.

9. Validate migration fresh/upgrade and coordinated rollout preflight, bounded readiness under concurrent outage/recovery and original-error redaction. Record repo SHA/worktree/branch/submodule pins, fixture provenance, exact commands, runner outputs and complete container/resource cleanup.

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

- [ ] Register ARCH055-* scenarios and the arch055 suite in the existing catalogue/harness.
- [ ] Add modular test fixtures and barrier scheduling around the named cross-service writers.
- [ ] Execute the full correctness matrix after developer manual verification and collect real SQL/performance evidence.
- [ ] Produce a machine-readable 61-endpoint result register with every required scenario resolved.
- [ ] Return an independent completion report; leave architectural completion to the architect.

## Interfaces / Contracts

Add `system:arch055:plan` as `node scripts/run-system-tests.js --suite arch055 --list` and `system:arch055` as `node scripts/run-system-tests.js --suite arch055 --execute`, with the matching suite registration. These scripts are task deliverables, not baseline commands. Preserve existing suite selection, run IDs, evidence classifications and failure semantics.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

- `ARCH-055-DATABASE-001` must have `status: complete` and an accepted review.
- `ARCH-055-BACKGROUND-001` must have `status: complete` and an accepted review.
- `ARCH-055-SHOPIFY-001` must have `status: complete` and an accepted review.
- `ARCH-055-API-001` must have `status: complete` and an accepted review.
- `ARCH-055-API-002` must have `status: complete` and an accepted review.
- `ARCH-055-API-003` must have `status: complete` and an accepted review.
- `ARCH-055-API-004` must have `status: complete` and an accepted review.
- `ARCH-055-API-005` must have `status: complete` and an accepted review.
- `ARCH-055-API-006` must have `status: complete` and an accepted review.
- `ARCH-055-API-007` must have `status: complete` and an accepted review.
- `ARCH-055-API-008` must have `status: complete` and an accepted review.
- `ARCH-055-API-009` must have `status: complete` and an accepted review.

## Enables

No implementation task. Final architectural verification follows system validation.

## Acceptance Criteria

- [ ] Every required cross-service race has deterministic before/after evidence and no weakened safety invariant.
- [ ] Both human-send producers and all Background fences/cancellers consume the accepted persisted claim key.
- [ ] All 61 route decisions are accounted for, including retained behaviour and deferred measure-first choices.
- [ ] Performance claims are limited to measured fixtures/workloads, with raw SQL/client-call/row metrics distinguished.
- [ ] No new production secret/provider account or destructive external operation is used; all disposable resources are cleaned.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| L01 | All implementation dependencies accepted and developer elects to execute | Record accepted pins/migrations, real auth/races and cleanup; no production-performance certification. |
| L02 | Each scoped race with real competitors and barriers | Before-state reproduction where feasible, after-state expected outcomes; failures block, never silently skip. |
| L03 | All61 endpoint register entries including retained routes | Unique route coverage rows with method/path, owner, test ID, pass/fail/not-run, SQL/row evidence; no aggregate speedup claim. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npm run validate:catalogue`
- [ ] `npm run lint`
- [ ] `npm run test:harness`
- [ ] `npm run system:arch055:plan`
- [ ] `npm run system:arch055`
- [ ] `git diff --check`
- [ ] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

No application source correction is authorised in this task. Return defects to the owning task/architect. Do not replace real API/Background behaviour with a hand-written SQL-only model and describe it as integrated validation.

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


## Dependency reconciliation — 3 November 2026

DATABASE-001 is Accepted and Complete at Attempt 2. Other required implementation tasks are not all Complete, so this task remains Pending and manually gated. No end-to-end certification is claimed.
