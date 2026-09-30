---
id: ARCH-023-BACKGROUND-001
architecture_id: ARCH-023
title: Establish Merchant Knowledge worker foundation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-09-30T09:43:11Z
attempt: 2
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-SHARED-002
enables:
  - ARCH-023-BACKGROUND-002
  - ARCH-023-BACKGROUND-003
created: 2026-09-29
updated: 2026-09-30
---

# Establish Merchant Knowledge worker foundation

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Establish the Background-owned Merchant Knowledge processing foundation without implementing source acquisition or semantic processing yet.

This task must create the dedicated Merchant Knowledge BullMQ worker factory, readiness identity, authoritative current-plan/source-entitlement resolver, durable PENDING-revision queue reconciliation, and the internal acquisition/result contracts consumed by the following Background tasks.

The final deployed process will be:

```text
src/entrypoints/merchant-knowledge.ts
serviceName: moda-merchant-knowledge-worker
queue:       merchant-knowledge
job:         process-source-revision
```

`ARCH-023-BACKGROUND-004` will complete and start that entrypoint after both acquisition implementations and the common processing pipeline exist. This task MUST NOT attach Merchant Knowledge work to an unrelated existing worker.

## Context

ARCH-023 uses PostgreSQL as durable source of truth and BullMQ as retryable delivery. Shopify commits a source revision before best-effort queue publication. Therefore Background requires a deterministic repair path that can recover a committed PENDING revision when the initial enqueue is lost.

The current Background repository already provides:

```text
src/runtime/readiness.ts
src/runtime/worker-process.ts
src/runtime/dynamic-leased-scheduler.ts
src/runtime/background-runtime-lease.ts
src/observability/worker-metrics.ts
src/observability/queue-performance.ts
src/lib/redis.ts
src/lib/db.ts
```

Reuse those mechanisms. Do not create a second worker framework.

## Scope

Authorized primary implementation surface:

```text
database                         # gitlink update only; no schema edits
package.json
package-lock.json

src/runtime/readiness.ts

src/entrypoints/merchant-knowledge-resources.ts

src/services/merchant-knowledge-acquisition.ts
src/services/merchant-knowledge-entitlement.service.ts
src/services/merchant-knowledge-reconciliation.service.ts

src/workers/merchant-knowledge.worker.ts

tests/unit/services/merchant-knowledge-entitlement.service.test.ts
tests/unit/services/merchant-knowledge-reconciliation.service.test.ts
tests/unit/workers/merchant-knowledge.worker.test.ts
tests/integration/merchant-knowledge-reconciliation.integration.test.ts
```

No production `src/entrypoints/merchant-knowledge.ts` startup wiring is added in this task. BACKGROUND-004 owns final executable composition so the dedicated process is never presented as deployable before processing exists.

## Out of Scope

- WEB_PAGE networking, SSRF policy or HTML extraction.
- R2 access.
- CSV/XLSX parsing.
- normalization/truncation/chunking.
- embeddings.
- pgvector writes.
- source-revision promotion.
- entitlement-change revision creation.
- upload cleanup.
- Gateway/Render deployment.
- Commerce lookup.
- Shopify producer implementation.
- edits inside the `database/` submodule.
- any plan-name-specific rule.

## Requirements

### R1 — adopt accepted dependencies exactly

Before source work:

1. update the `database` submodule gitlink to the accepted/merged commit containing `ARCH-023-DATABASE-001`;
2. do not edit files inside the database submodule;
3. use exactly `@modainteract/moda-interact-shared@1.0.1`, the Architect-Accepted revision published by `ARCH-023-SHARED-002`;
4. pin `@modainteract/moda-interact-shared` to `1.0.1` exactly; do not substitute a range, `latest`, workspace link or later release without architect reconciliation;
5. regenerate Prisma Client through the repository's existing `prisma:generate` path.

If either accepted dependency is unavailable, STOP.

### R2 — add the dedicated readiness identity

Extend `WORKER_DEPENDENCIES` in `src/runtime/readiness.ts` with exactly:

```ts
"moda-merchant-knowledge-worker": ["redis", "postgresql"],
```

Do not add R2 or embedding-provider network probes to generic readiness. Their configuration is validated by the modules that use them; provider availability is not a process-readiness dependency.

Existing worker dependency lists must remain unchanged.

### R3 — create Merchant Knowledge queue resources

Create `src/entrypoints/merchant-knowledge-resources.ts`.

Export one BullMQ Queue:

```ts
export const merchantKnowledgeQueue: Queue<
  MerchantKnowledgeProcessSourceRevisionJob,
  void,
  typeof MERCHANT_KNOWLEDGE_PROCESS_JOB_NAME
>
```

It must use:

```text
MERCHANT_KNOWLEDGE_QUEUE_NAME
connectionRedis
```

from the published Shared contract/current Background Redis connection.

Also export:

```ts
export const closeMerchantKnowledgeResources:
  readonly (() => Promise<unknown>)[]
```

containing the queue close operation.

Do not create another Redis connection.

### R4 — define one internal acquisition result contract

Create `src/services/merchant-knowledge-acquisition.ts`.

Export exactly:

```ts
export interface AcquiredMerchantKnowledgeDocument {
  contentType: string;
  extractedText: string;
  resolvedUrl: string | null;
  fetchedAt: Date | null;
}

export interface MerchantKnowledgeWebPageAcquirer {
  acquire(input: {
    requestedUrl: string;
  }): Promise<AcquiredMerchantKnowledgeDocument>;
}

export interface MerchantKnowledgeUploadedAssetAcquirer {
  acquire(input: {
    shopId: string;
    assetId: string;
    dataFormatKey: "CSV" | "XLSX";
  }): Promise<AcquiredMerchantKnowledgeDocument>;
}
```

The contract contains extracted source text only. It must not contain normalized content, chunks, embeddings, R2 credentials, object keys or plan limits.

BACKGROUND-002 implements `MerchantKnowledgeWebPageAcquirer`.
BACKGROUND-003 implements `MerchantKnowledgeUploadedAssetAcquirer`.

### R5 — resolve current Merchant Knowledge entitlement from the current plan only

Create `src/services/merchant-knowledge-entitlement.service.ts`.

Export:

```ts
export interface MerchantKnowledgeEntitlement {
  shopId: string;
  billingPlanId: string;
  maxKnowledgeSources: number;
  maxContentUnitsPerSource: number;
  allowedSourceTypes: ReadonlyArray<{
    purposeKey: MerchantKnowledgePurposeKey;
    dataFormatKey: MerchantKnowledgeDataFormatKey;
  }>;
}

export interface MerchantKnowledgeSourceEligibility {
  entitlement: MerchantKnowledgeEntitlement | null;
  globallySupported: boolean;
  sourceTypeAllowed: boolean;
  withinSourceAllowance: boolean;
  eligible: boolean;
}
```

Provide:

```ts
resolveCurrentEntitlement(shopId: string):
  Promise<MerchantKnowledgeEntitlement | null>

resolveSourceEligibility(sourceId: string):
  Promise<MerchantKnowledgeSourceEligibility>
```

Algorithm for `resolveCurrentEntitlement`:

1. resolve the shop's unique current `Subscription`;
2. require `Subscription.status` exactly `ACTIVE` or `TRIALING`;
3. use `Subscription.planId` / current `plan`; ignore `pendingPlanId`, `pendingShopifyPlanHandle` and `pendingEffectiveAt`;
4. find the current `BillingPlanFeature` whose:
   - `enabled = true`;
   - related `Feature.key = "merchant_knowledge"`;
   - related `Feature.active = true`;
5. parse `BillingPlanFeature.configuration` with published `MerchantKnowledgeFeatureConfigurationSchema`;
6. return null if there is no qualifying current subscription/plan feature;
7. malformed C2 configuration is a configuration error and must fail closed; do not silently substitute defaults.

Algorithm for `resolveSourceEligibility`:

1. load the source, Purpose, Data Format and composite compatibility row;
2. resolve current entitlement for `source.shopId`;
3. `globallySupported = true` only when:
   - Purpose row exists and `active = true`;
   - Data Format row exists and `active = true`;
   - the composite `MerchantKnowledgePurposeDataFormat` row exists;
4. `sourceTypeAllowed = true` only when the exact `(purpose.key, dataFormat.key)` appears in current `allowedSourceTypes`;
5. if globally supported and source type allowed, load all source rows for the shop whose:
   - Purpose/Data Format rows are active;
   - exact pair appears in `allowedSourceTypes`;
6. order those candidate sources by:
   ```text
   position ASC, id ASC
   ```
7. `withinSourceAllowance = true` only if this source occurs within the first `maxKnowledgeSources`;
8. `eligible = entitlement != null && globallySupported && sourceTypeAllowed && withinSourceAllowance`.

Do not consult `ShopFeaturePreference`.
Do not infer entitlement from plan name, handle or kind.
Do not count disallowed source types against `maxKnowledgeSources`.

### R6 — create deterministic PENDING-revision reconciliation

Create `src/services/merchant-knowledge-reconciliation.service.ts`.

Export:

```ts
export class MerchantKnowledgeReconciliationService {
  reconcilePendingOnce(input?: {
    pageSize?: number;
  }): Promise<{
    scanned: number;
    enqueued: number;
    skippedStale: number;
    skippedDormant: number;
  }>;
}
```

Default page size:

```text
100
```

Maximum accepted page size:

```text
500
```

The service must:

1. scan `MerchantKnowledgeSourceRevision` rows with `status = PENDING`;
2. order by `requestedAt ASC, id ASC`;
3. process at most one bounded page per call;
4. load the owning source;
5. skip when:
   ```text
   revision.generation != source.currentGeneration
   ```
6. call `resolveSourceEligibility(source.id)`;
7. skip when not currently eligible; leave the revision PENDING/dormant;
8. enqueue exactly:
   ```text
   name = MERCHANT_KNOWLEDGE_PROCESS_JOB_NAME
   data = {
     schemaVersion: 1,
     shopId: source.shopId,
     sourceRevisionId: revision.id,
     generation: revision.generation,
     requestedAt: revision.requestedAt.toISOString()
   }
   ```
9. use:
   ```text
   jobId = createMerchantKnowledgeProcessJobId(data)
   ```
10. repeated reconciliation must converge through the same deterministic job id;
11. queue publication must not mutate source/revision content.

Do not turn ACTIVE revisions into refresh work.
Do not create `ENTITLEMENT_CHANGE` revisions here.

### R7 — create the dedicated worker factory

Create `src/workers/merchant-knowledge.worker.ts`.

Export:

```ts
export interface MerchantKnowledgeJobProcessor {
  processJob(input: MerchantKnowledgeProcessSourceRevisionJob): Promise<void>;
  markTerminalFailure?(input: {
    job: MerchantKnowledgeProcessSourceRevisionJob;
    failureCode: string;
  }): Promise<void>;
}

export function createMerchantKnowledgeWorker(
  processor: MerchantKnowledgeJobProcessor,
): Worker
```

The BullMQ processor must:

1. observe jobs using existing `observeWorkerJob`;
2. accept only `MERCHANT_KNOWLEDGE_PROCESS_JOB_NAME`;
3. parse `job.data` with `MerchantKnowledgeProcessSourceRevisionJobSchema`;
4. call `processor.processJob(parsed)`;
5. use existing `connectionRedis`;
6. use existing Shared BullMQ telemetry;
7. not create its own Redis client;
8. not implement source processing itself.

If the final BullMQ attempt fails and `markTerminalFailure` exists, call it with a bounded failure code derived from the thrown error name. Never include full page/file content in the failure code/log.

Do not bind this worker to any existing recovery, billing, messaging or translation entrypoint.

### R8 — no deployable entrypoint yet

This task intentionally does not add:

```text
start:merchant-knowledge-worker
src/entrypoints/merchant-knowledge.ts startup
Gateway service
```

The worker factory and reconciliation service are independently testable now. BACKGROUND-004 owns final composition after the production acquirers and common pipeline exist.

This prevents a partially implemented worker from being deployable.

### R9 — observability is bounded

Use existing Shared/background logging/worker metrics conventions.

Permitted log metadata includes identifiers and bounded outcomes:

```text
shopId
sourceId
sourceRevisionId
generation
purposeKey
dataFormatKey
status/failureCode
counts/durations
```

Never log:

```text
normalized/extracted content
spreadsheet rows
vectors
R2 object key
signed URL
embedding API key
customer messages
```

## Work Items

- [ ] Advance database submodule gitlink to accepted ARCH-023-DATABASE-001.
- [ ] Adopt exact published SHARED-002 package revision.
- [ ] Add `moda-merchant-knowledge-worker` readiness identity.
- [ ] Add the Merchant Knowledge queue resource.
- [ ] Add internal acquisition interfaces.
- [ ] Implement current-plan Merchant Knowledge entitlement resolution.
- [ ] Implement source-type/source-count eligibility exactly.
- [ ] Implement bounded PENDING reconciliation with deterministic job ids.
- [ ] Add dedicated BullMQ worker factory with injected processing service.
- [ ] Add focused unit/integration tests.
- [ ] Record accepted database commit and Shared package version in Completion Report.

## Interfaces / Contracts

Consumes:

```text
ARCH-023-DATABASE-001 schema
@modainteract/moda-interact-shared/merchant-knowledge
@modainteract/moda-interact-shared/merchant-knowledge/node
```

Produces internal Background contracts:

```text
AcquiredMerchantKnowledgeDocument
MerchantKnowledgeWebPageAcquirer
MerchantKnowledgeUploadedAssetAcquirer
MerchantKnowledgeEntitlementService
MerchantKnowledgeReconciliationService
createMerchantKnowledgeWorker
```

These are repository-internal and must not be added to Shared.

## Dependencies

- `ARCH-023-DATABASE-001`
- `ARCH-023-SHARED-002`

Both must be Complete/architect-accepted. SHARED-002 supplies the exact package version.

## Enables

- `ARCH-023-BACKGROUND-002`
- `ARCH-023-BACKGROUND-003`

## Acceptance Criteria

- [ ] Merchant Knowledge has its own BullMQ worker factory and is not attached to an unrelated worker.
- [ ] Current entitlement ignores pending next-cycle plans.
- [ ] C2 malformed configuration fails closed.
- [ ] Source-type filtering occurs before source-count limiting.
- [ ] Dormant/disallowed/excess sources do not enqueue processing work.
- [ ] A committed eligible PENDING revision can be re-enqueued after simulated initial queue loss.
- [ ] Repeated reconciliation uses the same deterministic job id.
- [ ] Stale/non-current revision generations are skipped.
- [ ] Existing Background workers/readiness identities remain unchanged.
- [ ] No deployable Merchant Knowledge entrypoint exists yet.
- [ ] No source acquisition/embedding/vector work is implemented in this task.

## Validation

- [ ] `npm test -- --run tests/unit/services/merchant-knowledge-entitlement.service.test.ts`
- [ ] `npm test -- --run tests/unit/services/merchant-knowledge-reconciliation.service.test.ts`
- [ ] `npm test -- --run tests/unit/workers/merchant-knowledge.worker.test.ts`
- [ ] database-backed reconciliation integration test
- [ ] `npm run prisma:validate`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

After implementation/validation, set status to `review`, complete the Completion Report, clear the execution claim under the normal task protocol, return to `moda_architect` and STOP.

Do not start BACKGROUND-002 or BACKGROUND-003.

## Implementation Notes

The repository may use dependency injection/factories in tests, but do not create a generic worker framework or a general entitlement framework. These contracts exist only to allow the two format-specific acquisition tasks and the common processing task to remain bounded.

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
