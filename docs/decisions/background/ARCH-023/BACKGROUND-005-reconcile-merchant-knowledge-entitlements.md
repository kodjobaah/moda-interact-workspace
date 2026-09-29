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
status: pending
priority: 33
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-BACKGROUND-004
enables:
  - ARCH-023-GATEWAY-001
created: 2026-09-29
updated: 2026-09-29
---

# Reconcile Merchant Knowledge entitlement changes

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Implement periodic current-plan entitlement reconciliation for Merchant Knowledge.

The task must create `ENTITLEMENT_CHANGE` replacement revisions only when an ACTIVE, currently entitled source exceeds a newly lower `maxContentUnitsPerSource`.

Source-type and source-count downgrades remain non-destructive derived dormancy. They must not create replacement revisions or delete configuration/content.

## Scope

Authorized primary files:

```text
src/services/merchant-knowledge-entitlement-reconciliation.service.ts
src/entrypoints/merchant-knowledge.ts

tests/unit/services/merchant-knowledge-entitlement-reconciliation.service.test.ts
tests/integration/merchant-knowledge-entitlement-reconciliation.integration.test.ts
tests/unit/entrypoints/merchant-knowledge.test.ts
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
```

with C2-valid `BillingPlanFeature.configuration`.

Pending next-cycle plans are ignored.

Order the bounded scan deterministically by:

```text
Subscription.shopId ASC
```

A later invocation continues through the normal bounded-scan strategy chosen by the repository (cursor/lease cadence); do not load every tenant into memory.

### R3 — derive current source eligibility using the existing service

For each candidate shop, use BACKGROUND-001 entitlement/eligibility semantics.

The effective source set is:

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
- [ ] Add downgrade/increase/re-entitlement concurrency/integration tests.
- [ ] Preserve all non-destructive dormancy semantics.

## Interfaces / Contracts

Reuses:

```text
MerchantKnowledgeEntitlementService
merchantKnowledgeQueue
Shared C2/C4
ARCH-023 source/revision schema
```

Produces no new cross-repository contract.

## Dependencies

- `ARCH-023-BACKGROUND-004`

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

## Validation

- [ ] focused unit tests
- [ ] database concurrency/integration tests
- [ ] Merchant Knowledge entrypoint regression test
- [ ] `npm test`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

Do not start Gateway deployment.

## Completion Report

### Status
Not Started
### Files Changed
None.
### Work Completed
None.
### Validation Results
None.
### Deviations
None.
### Assumptions
None.
### Unresolved Issues
None.
### Architectural Concerns
None.

## Architect Review

### Review Status
Pending
### Review Notes
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
