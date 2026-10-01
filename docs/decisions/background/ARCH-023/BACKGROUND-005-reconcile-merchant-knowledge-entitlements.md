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
status: blocked
priority: 33
executor: null
claimed_at: null
attempt: 1
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

- [ ] Implement bounded current-entitlement reconciliation.
- [ ] Implement idempotent ENTITLEMENT_CHANGE transaction.
- [ ] Enqueue after commit with deterministic job id.
- [ ] Integrate leased scheduler into existing Merchant Knowledge entrypoint.
- [ ] Add the exact 300-second entitlement-reconciliation lease cadence branch and regression.
- [ ] Add downgrade/increase/re-entitlement concurrency/integration tests.
- [ ] Preserve all non-destructive dormancy semantics.

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

- [ ] Source-type downgrades are derived/non-destructive.
- [ ] Source-count downgrades are derived/non-destructive.
- [ ] Only content-limit decreases create ENTITLEMENT_CHANGE.
- [ ] Replacement creation is idempotent/concurrency-safe.
- [ ] Prior ACTIVE remains available while replacement is PENDING/PROCESSING.
- [ ] Missed enqueue is recoverable by B1 reconciliation.
- [ ] Pending future plan is ignored.
- [ ] Increases/re-entitlement do not cause automatic reprocessing.
- [ ] Dedicated worker now contains all Background ARCH-023 runtime behavior required before deployment.
- [ ] Entitlement reconciliation uses its own persisted lease identity with an exact 300-second global cadence; existing leases/cadences remain unchanged.

## Validation

- [ ] focused unit tests
- [ ] database concurrency/integration tests
- [ ] Merchant Knowledge entrypoint regression test
- [ ] entitlement-reconciliation lease cadence unit/PostgreSQL regression
- [ ] `npm test`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

Do not start Gateway deployment.

## Completion Report

### Status
In Progress (blocked on a database-owned lease prerequisite; implementation checkpoint `a8b04ee` is on `task/ARCH-023-BACKGROUND-005`).
### Files Changed
`moda-interact-background/src/services/merchant-knowledge-entitlement-reconciliation.service.ts`; `moda-interact-background/src/entrypoints/merchant-knowledge.ts`; `moda-interact-background/tests/unit/services/merchant-knowledge-entitlement-reconciliation.service.test.ts`; `moda-interact-background/tests/unit/entrypoints/merchant-knowledge.test.ts`; `moda-interact-background/tests/integration/merchant-knowledge-entitlement-reconciliation.integration.test.ts`.
### Work Completed
Implemented bounded, keyset-paged current-subscription reconciliation filtered by an enabled Merchant Knowledge preference; uses the existing activation-aware eligibility service and source-lock transaction to create idempotent `ENTITLEMENT_CHANGE` revisions only for content-limit decreases. Added deterministic post-commit queue publication, non-destructive dormant-source counts, the requested scheduler draft, and focused unit/entrypoint/PostgreSQL integration tests. The requested scheduler lease name is absent from the generated Prisma enum and PostgreSQL enum, so this checkpoint cannot compile until the database contract is extended.
### Validation Results
Focused unit and entrypoint tests: 15 passed. PostgreSQL integration: 8 passed using the shared disposable infrastructure helper with `pgvector/pgvector:pg17`. `npm run prisma:validate`: passed. Changed-file diagnostics: clean. `git diff --check`: passed. `npm run build`: blocked by TS2820 because `MERCHANT_KNOWLEDGE_ENTITLEMENT_RECONCILIATION` is not a `BackgroundRuntimeLeaseName`. `npm test`: failed in unrelated existing suites (billing reconciliation expectations, ARCH-020 fixture path, runtime shared-package version assertion, and PostgreSQL enum tests without a database at `localhost:5432`).
### Deviations
The repository's standard integration wrapper selected plain `postgres:17.6-alpine`, which lacks the required `vector` extension; the focused suite was rerun successfully with the shared helper's supported pgvector image override. No wrapper or global Docker configuration was changed.
### Assumptions
The task's no-database-schema/migration boundary remains binding. Reusing either existing Merchant Knowledge lease is not safe: the pending-reconciliation lease conflicts with its existing scheduler and the upload-cleanup lease has a different purpose/cadence.
### Unresolved Issues
The new lease requires a database-owned `BackgroundRuntimeLeaseName` enum value and a generated Prisma client contract before this Background branch can build. `moda_architect` confirmed this is a separate prerequisite and recommended defining `ARCH-023-DATABASE-006`, making this task depend on it, then resuming after acceptance. This task remains blocked; no architect review/acceptance is claimed.
### Architectural Concerns
The task requires a distinct persisted lease identity and a 300-second cadence but currently authorizes only Background files. The Background lease service also has a SQL cadence mapping keyed by the database enum. Adding the value here would cross the database ownership boundary; substituting another lease would break mutual exclusion or cadence semantics.

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
