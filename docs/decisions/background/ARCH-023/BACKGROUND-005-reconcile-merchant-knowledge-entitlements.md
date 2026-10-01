---
id: ARCH-023-BACKGROUND-005
architecture_id: ARCH-023
title: Reconcile Merchant Knowledge entitlement changes
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 33
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-023-BACKGROUND-004
  - ARCH-023-DATABASE-006
enables:
  - ARCH-023-GATEWAY-001
created: 2026-09-29
updated: 2026-10-01
---

# Reconcile Merchant Knowledge entitlement changes

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Implement periodic current-plan entitlement reconciliation for Merchant Knowledge, respecting the merchant activation gate inherited from BACKGROUND-006/BACKGROUND-004.

The task must create `ENTITLEMENT_CHANGE` replacement revisions only when an ACTIVE, currently entitled source exceeds a newly lower `maxContentUnitsPerSource`.

Source-type and source-count downgrades remain non-destructive derived dormancy. They must not create replacement revisions or delete configuration/content.

## Scope

Authorized primary files:

```text
src/services/merchant-knowledge-entitlement-reconciliation.service.ts
src/entrypoints/merchant-knowledge.ts
src/runtime/background-runtime-lease.ts

tests/unit/services/merchant-knowledge-entitlement-reconciliation.service.test.ts
tests/integration/merchant-knowledge-entitlement-reconciliation.integration.test.ts
tests/unit/entrypoints/merchant-knowledge.test.ts
tests/unit/runtime/background-runtime-lease.test.ts
tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts
```

No new worker process or queue is created.

## Out of Scope

- plan changes themselves.
- Shopify billing materialisation.
- source deletion/reordering.
- automatic processing on allowance increases.
- re-fetch merely because source type entitlement returns.
- new database fields/statuses.
- new queue.
- Gateway deployment (next task).
- Commerce lookup.

## Requirements

### R1 — reconciliation cadence

Extend the existing dedicated `src/entrypoints/merchant-knowledge.ts` with one additional leased scheduler:

```text
leaseName: MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION
interval: 300_000 ms
runImmediately: true
```

Its run function calls:

```ts
merchantKnowledgeEntitlementReconciliationService.reconcileOnce({
  shopPageSize: 100,
});
```

After `ARCH-023-DATABASE-006` makes the lease identity representable in Prisma/PostgreSQL, extend the existing `BackgroundRuntimeLeaseService.tryAcquire()` cadence `CASE` with exactly:

```text
MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION -> 300 seconds
```

This is the runtime counterpart of the scheduler's `300_000 ms` interval. Preserve every existing lease branch, PostgreSQL-time gating and generation/owner fencing. Do not add a `BackgroundRuntimeConfig` column or another scheduler mechanism.

Do not add another process/entrypoint.

### R2 — bounded current-shop scan

`reconcileOnce` must scan at most:

```text
100 shops/subscriptions per invocation by default
500 maximum caller-supplied page size
```

Candidates are current subscriptions whose status is:

```text
ACTIVE
TRIALING
```

and whose current plan has an enabled active Feature:

```text
Feature.key = merchant_knowledge
Feature.activationMode = MERCHANT_OPT_IN
```

with C2-valid `BillingPlanFeature.configuration` **and an enabled ShopFeaturePreference for that shop/Feature**. Shops with missing/false preference are dormant and receive no entitlement-change work.

Pending next-cycle plans are ignored.

Order the bounded scan deterministically by:

```text
Subscription.shopId ASC
```

A later invocation continues through the normal bounded-scan strategy chosen by the repository (cursor/lease cadence); do not load every tenant into memory.

### R3 — derive current source eligibility using the existing service

For each candidate shop, use the activation-aware entitlement/eligibility semantics established by BACKGROUND-006 and consumed by BACKGROUND-004.

The effective source set exists only while Merchant Knowledge is explicitly enabled. Then it is:

1. active globally supported Purpose/Data Format pairs;
2. exact pairs in current `allowedSourceTypes`;
3. ordered `(position ASC, id ASC)`;
4. first `maxKnowledgeSources`.

Do not duplicate a second entitlement algorithm.

### R4 — source-type downgrade behavior

When a persisted source pair is no longer in current `allowedSourceTypes`:

```text
no delete
no source mutation
no revision mutation
no R2 delete
no ENTITLEMENT_CHANGE
no processing enqueue
```

The source is simply dormant through derived current entitlement.

If the pair is later re-entitled, retained ACTIVE content may be used again by later runtime consumers when its embedding provenance is current. This task does not refetch/re-upload solely because entitlement returned.

### R5 — source-count downgrade behavior

Allowed sources beyond the first `maxKnowledgeSources`:

```text
remain persisted
remain historically ACTIVE if they already were
receive no new processing work
receive no ENTITLEMENT_CHANGE solely because they are beyond the count
are excluded by current entitlement at processing/lookup boundaries
```

Do not renumber/delete/reorder them.

### R6 — content-limit decrease detection

For each currently entitled source within the active source allowance:

1. find its current ACTIVE revision, if any;
2. if none -> no action;
3. compare:
   ```text
   activeRevision.contentUnits > current maxContentUnitsPerSource
   ```
4. only that condition requires `ENTITLEMENT_CHANGE`.

No replacement is created when content units equal the limit.

### R7 — exact idempotent ENTITLEMENT_CHANGE transaction

For each source requiring replacement, perform one transaction:

1. lock the source row;
2. reload current ACTIVE revision;
3. re-resolve/re-check the same current entitlement under the lock/transaction boundary sufficiently to prevent acting on stale source generation;
4. require source still currently entitled and ACTIVE revision still exceeds current limit;
5. detect any newer revision with:
   ```text
   generation > activeRevision.generation
   AND status IN (PENDING, PROCESSING)
   ```
   If present -> skip;
6. require:
   ```text
   source.currentGeneration == activeRevision.generation
   ```
   when no newer revision exists;
7. increment `source.currentGeneration` by exactly one;
8. insert one revision:
   ```text
   generation = new currentGeneration
   reason = ENTITLEMENT_CHANGE
   status = PENDING
   requestedAt = now
   ```
9. copy locator exactly:
   ```text
   WEB_PAGE -> requestedUrl = activeRevision.requestedUrl
               uploadedAssetId = null

   CSV/XLSX -> uploadedAssetId = activeRevision.uploadedAssetId
               requestedUrl = null
   ```
10. do not copy normalized content/chunks/embeddings into the new revision;
11. commit.

The prior ACTIVE revision remains ACTIVE.

### R8 — post-commit enqueue

After transaction commit, enqueue C4 using:

```text
MERCHANT_KNOWLEDGE_PROCESS_JOB_NAME
createMerchantKnowledgeProcessJobId
```

If enqueue fails:

```text
leave new revision PENDING
do not rollback committed revision
do not create another revision
```

BACKGROUND-001 PENDING reconciliation repairs the missed enqueue.

### R9 — no automatic increase processing

If:

```text
current maxContentUnitsPerSource > activeRevision.contentUnits
```

do nothing.

A merchant-triggered:

```text
WEB_PAGE Refresh
CSV/XLSX Reprocess
```

is required to use a higher allowance.

### R10 — source-type re-entitlement does not imply processing

When a dormant source becomes currently allowed again:

```text
do not create revision solely for re-entitlement
do not enqueue solely for re-entitlement
```

If its retained ACTIVE revision has current embedding provenance and fits the current limit, it remains reusable.

If its ACTIVE revision exceeds the new current content limit, the ordinary R6 rule creates `ENTITLEMENT_CHANGE`.

### R11 — observability

Log bounded counts only:

```text
shopsScanned
sourcesScanned
contentLimitRevisionsCreated
sourceTypeDormant
sourceCountDormant
enqueueFailures
```

Never log source content/vectors/object keys.

### R12 — exact tests

Prove:

```text
disallowed source type -> no mutation/enqueue
allowed but beyond maxKnowledgeSources -> no mutation/enqueue
ACTIVE contentUnits == current limit -> no action
ACTIVE contentUnits < current limit -> no action
ACTIVE contentUnits > lower limit -> exactly one ENTITLEMENT_CHANGE
repeated reconciliation -> no duplicate while PENDING/PROCESSING newer revision exists
WEB_PAGE replacement copies requestedUrl only
CSV/XLSX replacement copies uploadedAssetId only
old ACTIVE remains ACTIVE until normal processing succeeds
enqueue failure leaves one durable PENDING revision
next B1 reconciliation can enqueue that revision
pending next plan never affects result
increase does not trigger processing
re-entitlement alone does not trigger processing
```

## Work Items

- [x] Implement bounded current-entitlement reconciliation.
- [x] Implement idempotent ENTITLEMENT_CHANGE transaction.
- [x] Enqueue after commit with deterministic job id.
- [x] Integrate leased scheduler into existing Merchant Knowledge entrypoint.
- [x] Add the exact 300-second entitlement-reconciliation lease cadence branch and regression.
- [x] Add downgrade/increase/re-entitlement concurrency/integration tests.
- [x] Preserve all non-destructive dormancy semantics.

## Interfaces / Contracts

Reuses:

```text
MerchantKnowledgeEntitlementService
merchantKnowledgeQueue
Shared C2/C4
ARCH-023 source/revision schema
BackgroundRuntimeLeaseName.MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION (DATABASE-006)
```

Produces no new cross-repository contract.

## Dependencies

- `ARCH-023-BACKGROUND-004`
- `ARCH-023-DATABASE-006`

## Enables

- `ARCH-023-GATEWAY-001`

Gateway may deploy the dedicated worker only after this task is architect-accepted.

## Acceptance Criteria

- [x] Source-type downgrades are derived/non-destructive.
- [x] Source-count downgrades are derived/non-destructive.
- [x] Only content-limit decreases create ENTITLEMENT_CHANGE.
- [x] Replacement creation is idempotent/concurrency-safe.
- [x] Prior ACTIVE remains available while replacement is PENDING/PROCESSING.
- [x] Missed enqueue is recoverable by B1 reconciliation.
- [x] Pending future plan is ignored.
- [x] Increases/re-entitlement do not cause automatic reprocessing.
- [x] Dedicated worker now contains all Background ARCH-023 runtime behavior required before deployment.
- [x] Entitlement reconciliation uses its own persisted lease identity with an exact 300-second global cadence; existing leases/cadences remain unchanged.

## Validation

- [x] focused unit tests
- [x] database concurrency/integration tests
- [x] Merchant Knowledge entrypoint regression test
- [x] entitlement-reconciliation lease cadence unit/PostgreSQL regression
- [x] `npm test` (run; unrelated existing failures recorded below)
- [x] `npm run build`
- [x] `git diff --check`
- [x] changed-file diagnostics clean

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

Do not start Gateway deployment.

## Completion Report

### Status
Attempt 2 complete; submitted for architect review. Attempt 1's database prerequisite was accepted by ARCH-023-DATABASE-006.
### Files Changed
`moda-interact-background/src/services/merchant-knowledge-entitlement-reconciliation.service.ts`; `moda-interact-background/src/entrypoints/merchant-knowledge.ts`; `moda-interact-background/src/runtime/background-runtime-lease.ts`; `moda-interact-background/tests/unit/services/merchant-knowledge-entitlement-reconciliation.service.test.ts`; `moda-interact-background/tests/unit/entrypoints/merchant-knowledge.test.ts`; `moda-interact-background/tests/integration/merchant-knowledge-entitlement-reconciliation.integration.test.ts`; `moda-interact-background/tests/unit/runtime/background-runtime-lease.test.ts`; `moda-interact-background/tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts`.
### Work Completed
Preserved the Attempt 1 reconciliation implementation and resolved its database-owned enum prerequisite through accepted `ARCH-023-DATABASE-006`. Added the exact `MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION -> 300` seconds cadence branch to the existing PostgreSQL-time lease `CASE`, without changing other lease mappings, generation/owner fencing, or runtime configuration. The existing dedicated scheduler uses its distinct lease at 300,000 ms; unit and PostgreSQL concurrency regressions now verify the cadence boundary. The entitlement service and integration coverage retain the bounded preference-filtered scan, activation-aware eligibility, source-lock idempotency, locator-only replacement, queue recovery, and non-destructive downgrade/increase/re-entitlement behavior.
### Validation Results
Focused reconciliation/lease/entrypoint unit tests: 20 passed. Disposable pgvector PostgreSQL suites: 12 passed across entitlement reconciliation and lease-cadence concurrency. `npm run build` (including Prisma generation): passed. Changed-file diagnostics: clean. `git diff --check`: passed. `npm test` was run; it still reports unrelated existing failures: one ARCH-020 fixture suite cannot find `ARCH-020-evidence-contract-fixtures.json`, four translation enum integration tests cannot reach `localhost:5432`, three billing reconciliation expectations fail, one matured-candidate test fails, and one observability test expects shared package `0.12.1` while this branch declares `1.0.1`.
### Deviations
The standard Background integration wrapper selects plain `postgres:17.6-alpine`, which lacks the `vector` extension. Both task-specific PostgreSQL suites were run through the shared disposable infrastructure helper with its supported `pgvector/pgvector:pg17` image option; no wrapper or global Docker configuration was changed. The first cadence integration attempt used the stale generated Prisma client from before DATABASE-006; regenerating Prisma Client fixed the mismatch and the same suites then passed.
### Assumptions
The accepted DATABASE-006 enum contract is materialized in this Background worktree's recorded database submodule commit `15859f16a7b9a889df8f70e1ecc29b27df8e31de`. Cadence remains Background-owned as specified by the updated task.
### Unresolved Issues
The full repository `npm test` command remains non-green for the unrelated failures listed above. The task-specific focused unit, PostgreSQL integration, build, diagnostics, and diff checks pass; no task-specific implementation blocker remains.
### Architectural Concerns
None. The database-owned enum is consumed without modifying the database gitlink; the fixed cadence remains in the Background-owned lease service.

### Attempt 1 Review Follow-up
- Database-owned enum prerequisite: resolved by accepted `ARCH-023-DATABASE-006`; the generated Prisma client and Background build now accept the lease value.
- Exact 300-second lease cadence: implemented in `src/runtime/background-runtime-lease.ts`; asserted by `tests/unit/runtime/background-runtime-lease.test.ts` and `tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts`, both included in the passing focused validations.

### Attempt 2 Launcher Evidence
Prepared execution succeeded with dependency gate passed (`ARCH-023-BACKGROUND-004` and `ARCH-023-DATABASE-006` complete). Attempt 2 was claimed by `copilot` at `2026-10-01T12:01:08Z`; durable parent claim commit `beaee882bb8f20a8454a0417ae13b9bb4224dedb` was pushed. Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-BACKGROUND-005`, `task/ARCH-023-BACKGROUND-005`, head `e32cc9fa57d282695ddf1dfd225525038567b789`. Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-BACKGROUND-005`, `task/ARCH-023-BACKGROUND-005`, start head `26fa9cebc624473e79a56e228951bb24dfe520d7`; final implementation commit `99ef48f2db6e014bd155561732ad7f05b580f06f` pushed. Parent and implementation task branches required no remote task fast-forward and already incorporated `origin/main`. Both dedicated worktrees were reused; shared workspace and shared implementation checkout were not switched or mutated; no other task worktree was reused. Recursive submodule sync/update passed; database submodule was initialized at the recorded `15859f16a7b9a889df8f70e1ecc29b27df8e31de` commit.

## Architect Review

### Review Status
Blocked — Attempt 1

### Review Notes
The blocked checkpoint is valid. The task-owned entrypoint requires the distinct persisted lease identity `MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION`, but the database contract pinned by this Background branch does not define that enum value, so the generated Prisma type rejects the scheduler with TS2820. The existing Merchant Knowledge leases are not safe substitutes because they represent different jobs and cadences.

The implementation checkpoint at `a8b04ee` is not rejected. Focused service/entrypoint tests and the pgvector-backed PostgreSQL entitlement-reconciliation integration tests are useful partial evidence, but the task cannot complete or build until the database-owned enum contract is extended.

A second bounded runtime consequence is recorded here so the task does not become compile-clean but operationally incorrect after the enum addition: the existing `BackgroundRuntimeLeaseService.tryAcquire()` cadence `CASE` must gain the exact `MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION -> 300` seconds branch. That Background runtime edit is inseparable from this task's own scheduler and remains in BACKGROUND-005 scope; it does not justify another Background task.

### Reviewed Files
- `docs/decisions/background/ARCH-023/BACKGROUND-005-reconcile-merchant-knowledge-entitlements.md`
- `moda-interact-background/src/entrypoints/merchant-knowledge.ts`
- `moda-interact-background/src/runtime/background-runtime-lease.ts`
- `moda-interact-background/src/services/merchant-knowledge-entitlement-reconciliation.service.ts`
- focused unit/integration tests named in the Completion Report
- current ARCH-023 database/background coordination state

### Validation Reviewed
Reviewed the recorded 15 focused unit/entrypoint passes, 8 pgvector PostgreSQL integration passes, Prisma validation, clean changed-file diagnostics and `git diff --check`. The production build is correctly blocked by TS2820 until the enum prerequisite exists. The broader suite failures are not used as the reason for this blocker.

### Architecture Conformance
The partial Background implementation respects repository ownership by stopping rather than modifying the database enum locally or reusing an unrelated lease. The required database change is representational only; cadence remains Background-owned. No new queue, worker process, lock mechanism or business schema is required.

### Follow-up
Materialise and complete `ARCH-023-DATABASE-006` first. It adds only `MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION` to `public.BackgroundRuntimeLeaseName` with a forward enum-only migration and disposable PostgreSQL proof. After DATABASE-006 is architect-accepted Complete, return this same BACKGROUND-005 task from Blocked to Ready with Attempt 1 preserved. The next launcher claim becomes Attempt 2. Attempt 2 must then add/prove the exact 300-second lease cadence branch, finish the entrypoint/build/full task validation and return to review. `ARCH-023-GATEWAY-001` remains gated.

Coordination update after DATABASE-006 acceptance: `ARCH-023-DATABASE-006` is now Complete / Accepted Attempt 1, so this same task is returned to Ready with Attempt 1 preserved. No implementation is started implicitly; the next authorized launcher claim is Attempt 2.

## Architect Review — Attempt 2

### Review Status
Accepted — Attempt 2

### Review Notes
Accepted. Attempt 2 resolves the database-owned lease prerequisite without broadening repository ownership and completes the bounded entitlement-reconciliation runtime. The implementation reviewed at `99ef48f2db6e014bd155561732ad7f05b580f06f` uses the accepted `MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION` enum identity and adds exactly the required 300-second branch to the existing PostgreSQL-time `BackgroundRuntimeLeaseService.tryAcquire()` cadence `CASE`; every pre-existing lease branch, generation increment, owner-token fencing and runtime-configuration surface remains unchanged.

The reconciliation path is architecture-conformant by inspection. It scans only current `ACTIVE`/`TRIALING` subscriptions with an active `merchant_knowledge` plan feature and explicit enabled merchant preference, ignores pending next-cycle plans, reuses `MerchantKnowledgeEntitlementService` for source eligibility, and keeps source-type/source-count downgrades non-destructive. For an entitled source whose current ACTIVE revision exceeds the current content-unit limit, the transaction locks the source row, re-resolves eligibility, rejects newer PENDING/PROCESSING work or stale generations, advances exactly one generation and creates one locator-only `ENTITLEMENT_CHANGE` PENDING revision while leaving the previous ACTIVE revision intact. Queue publication occurs only after commit; a failed enqueue leaves the durable PENDING revision for the existing BACKGROUND-001 reconciliation path.

The exact fixed scheduler/lease pairing is now coherent: the dedicated Merchant Knowledge entrypoint runs entitlement reconciliation every `300_000` ms and the persisted lease cadence is 300 seconds. The disposable PostgreSQL concurrency proof demonstrates in-cadence suppression, a single generation-2 winner after the cadence elapses and stale-owner heartbeat/release rejection for the new lease identity.

The Attempt 2 Completion Report contains the required launcher-resolved parent and implementation worktrees, branch synchronization results, dependency gate, recursive submodule state and final implementation head. No workflow/evidence correction remains.

### Reviewed Files
- `moda-interact-background/src/services/merchant-knowledge-entitlement-reconciliation.service.ts`
- `moda-interact-background/src/services/merchant-knowledge-entitlement.service.ts`
- `moda-interact-background/src/entrypoints/merchant-knowledge.ts`
- `moda-interact-background/src/runtime/background-runtime-lease.ts`
- `moda-interact-background/tests/unit/services/merchant-knowledge-entitlement-reconciliation.service.test.ts`
- `moda-interact-background/tests/integration/merchant-knowledge-entitlement-reconciliation.integration.test.ts`
- `moda-interact-background/tests/unit/entrypoints/merchant-knowledge.test.ts`
- `moda-interact-background/tests/unit/runtime/background-runtime-lease.test.ts`
- `moda-interact-background/tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts`
- `docs/decisions/background/ARCH-023/BACKGROUND-005-reconcile-merchant-knowledge-entitlements.md`

### Validation Reviewed
Accepted the recorded canonical-worktree validation: 20 focused reconciliation/lease/entrypoint unit tests passed; 12 disposable `pgvector/pgvector:pg17` PostgreSQL tests passed across entitlement reconciliation and lease-cadence concurrency; the production build (including Prisma generation), changed-file diagnostics and `git diff --check` passed.

The repository-wide `npm test` remains non-green for the separately recorded ARCH-020 fixture absence, local-PostgreSQL-dependent translation-enum tests, billing/matured-candidate expectations and a stale shared-package-version assertion. None is in the BACKGROUND-005 changed surface or contradicted by the focused/live proofs, so those failures do not block this bounded task.

### Architecture Conformance
Conforms. DATABASE-006 owns only the persisted lease identity; BACKGROUND-005 owns its scheduler, fixed 300-second runtime cadence and entitlement-reconciliation behavior. The implementation reuses the accepted merchant opt-in/entitlement service and existing C4/B1 contracts, introduces no new queue or worker process, preserves durable ACTIVE knowledge during replacement processing, and does not mutate source configuration for plan downgrades.

### Follow-up
`ARCH-023-BACKGROUND-005` is Complete / Accepted at Attempt 2. All three declared prerequisites of `ARCH-023-GATEWAY-001` (`BACKGROUND-005`, `SHOPIFY-005`, `COMMERCE-002`) are now Complete/architect-accepted, so GATEWAY-001 becomes Ready with Attempt 0 preserved. Do not start Gateway work implicitly; its normal `/moda-task ARCH-023-GATEWAY-001` launcher must claim it. Terminal system-test tasks remain Pending until their complete implementation/deployment dependency sets are satisfied. The separately recorded Background billing-reconciliation activation hook remains a required follow-up before final ARCH-023 system acceptance and is not folded into this task.
