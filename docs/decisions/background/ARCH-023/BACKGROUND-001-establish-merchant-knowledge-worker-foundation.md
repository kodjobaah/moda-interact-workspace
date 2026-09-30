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
claimed_at: 2026-09-30T10:15:41Z
attempt: 3
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

- [x] Verify database submodule is at accepted ARCH-023-DATABASE-001 commit `2eb17ee910491e8f9df82736fc0a843844415947`; no database files or gitlink were changed.
- [x] Adopt exact published SHARED-002 package revision `@modainteract/moda-interact-shared@1.0.1`.
- [x] Add `moda-merchant-knowledge-worker` readiness identity.
- [x] Add the Merchant Knowledge queue resource.
- [x] Add internal acquisition interfaces.
- [x] Implement current-plan Merchant Knowledge entitlement resolution.
- [x] Implement source-type/source-count eligibility exactly.
- [x] Implement bounded PENDING reconciliation with deterministic job ids.
- [x] Add dedicated BullMQ worker factory with injected processing service.
- [x] Add focused unit tests and a disposable-database-gated integration test.
- [x] Record accepted database commit and Shared package version in Completion Report.

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

- [x] Merchant Knowledge has its own BullMQ worker factory and is not attached to an unrelated worker.
- [x] Current entitlement ignores pending next-cycle plans.
- [x] C2 malformed configuration fails closed.
- [x] Source-type filtering occurs before source-count limiting.
- [x] Dormant/disallowed/excess sources do not enqueue processing work.
- [ ] A committed eligible PENDING revision can be re-enqueued after simulated initial queue loss (integration test is authored but could not run without local PostgreSQL).
- [x] Repeated reconciliation uses the same deterministic job id.
- [x] Stale/non-current revision generations are skipped.
- [x] Existing Background workers/readiness identities remain unchanged.
- [x] No deployable Merchant Knowledge entrypoint exists yet.
- [x] No source acquisition/embedding/vector work is implemented in this task.

## Validation

- [x] `npm test -- --run tests/unit/services/merchant-knowledge-entitlement.service.test.ts` — 7 passed.
- [x] `npm test -- --run tests/unit/services/merchant-knowledge-reconciliation.service.test.ts` — 7 passed.
- [x] `npm test -- --run tests/unit/workers/merchant-knowledge.worker.test.ts` — 5 passed.
- [ ] Database-backed reconciliation integration test — skipped; no disposable database configured, and `pg_isready -h localhost -p 5432 -d moda_interact -U postgres` reported no response.
- [x] `npm run prisma:validate` — passed.
- [x] `npm run prisma:generate` — passed through the repository script.
- [x] `npm run build` — passed.
- [x] `git diff --check` — passed.
- [x] Changed-file diagnostics clean; `npx tsc --noEmit` passed.

## Stop Condition

After implementation/validation, set status to `review`, complete the Completion Report, clear the execution claim under the normal task protocol, return to `moda_architect` and STOP.

Do not start BACKGROUND-002 or BACKGROUND-003.

## Implementation Notes

The repository may use dependency injection/factories in tests, but do not create a generic worker framework or a general entitlement framework. These contracts exist only to allow the two format-specific acquisition tasks and the common processing task to remain bounded.

## Completion Report

### Status
Ready for Architect Review (`review`); Attempt 2 implementation is committed and pushed.

### Files Changed
Implementation task commit `06566f8` changes only `package.json`, `package-lock.json`, `src/runtime/readiness.ts`, `src/entrypoints/merchant-knowledge-resources.ts`, `src/services/merchant-knowledge-acquisition.ts`, `src/services/merchant-knowledge-entitlement.service.ts`, `src/services/merchant-knowledge-reconciliation.service.ts`, `src/workers/merchant-knowledge.worker.ts`, and the existing worker/queue telemetry name unions in `src/observability/worker-metrics.ts` and `src/observability/queue-performance.ts`, plus the three focused unit tests and the gated reconciliation integration test. The database submodule remains at accepted commit `2eb17ee910491e8f9df82736fc0a843844415947`; no database file or gitlink changed.

### Work Completed
Pinned `@modainteract/moda-interact-shared` exactly to `1.0.1` and regenerated Prisma Client through the repository script. Added the dedicated readiness identity, single shared-Redis BullMQ queue resource, and the three internal acquisition interfaces. Implemented current-plan-only entitlement resolution with strict Shared C2 parsing, active supported pair checks, allowed-pair filtering before deterministic source allowance counting, and a bounded PENDING revision reconciler using the Shared deterministic job ID. Added an isolated Merchant Knowledge worker factory using existing Redis, BullMQ telemetry and `observeWorkerJob`, with final-attempt failure marking based only on a bounded error-name code. No production startup entrypoint, acquisition implementation, embedding/vector work, or database schema change was added.

### Validation Results
The three task-required unit suites passed (entitlement 7/7, reconciliation 7/7, worker 5/5); the existing readiness suite passed 8/8. `npx tsc --noEmit`, `npm run prisma:generate`, `npm run prisma:validate`, `npm run build`, `git diff --check`, and changed-file diagnostics all passed. The database-backed integration test was added but skipped because neither disposable integration settings nor a local PostgreSQL service are available (`pg_isready` reported no response). `npm install` reported three high-severity audit advisories and install-script approval warnings; no unrelated audit remediation was attempted.

### Deviations
The database-backed integration test could not be executed in this environment; it is gated by the repository's disposable-database opt-in and is recorded as an unresolved validation item. The readiness/queue telemetry name unions were extended in their existing observability modules because the new worker's actual identity must be accepted by `observeWorkerJob` and queue-performance telemetry.

### Assumptions
The accepted ARCH-023 database migration and catalogue are available in the prepared local integration environment when `TEST_DATABASE_URL` and `MODA_DISPOSABLE_INTEGRATION=1` are configured.

### Unresolved Issues
The database-backed enqueue-loss integration test still needs to run against an explicitly disposable PostgreSQL database before the pending acceptance criterion can be verified end to end.

### Architectural Concerns
None. Architect Review remains owned by `moda_architect` and was not modified.

## Architect Review

### Review Status
Changes Requested — Attempt 2

### Review Notes
The implementation is substantively aligned with the bounded BACKGROUND-001 objective: the dedicated readiness identity, single Shared-Redis queue resource, internal acquisition contracts, current-plan-only entitlement/eligibility resolver, bounded deterministic PENDING reconciliation and injected Merchant Knowledge worker factory all match the intended architecture. The exact Shared dependency is pinned to `@modainteract/moda-interact-shared@1.0.1`, no deployable Merchant Knowledge entrypoint has been introduced, and no acquisition/embedding/vector implementation has leaked into this task.

Acceptance is withheld for three bounded corrections:

1. **A2-R1 — use the canonical Shared C4 schema-version constant.** `src/services/merchant-knowledge-reconciliation.service.ts` constructs the cross-service C4 payload with a local literal `schemaVersion: 1` even though the accepted Shared contract exports `MERCHANT_KNOWLEDGE_PROCESS_SCHEMA_VERSION`. The architect cross-service contract rule requires the Shared schema-version constant when one exists. Import and use that constant in production code, and make the focused reconciliation test assert the Shared constant rather than a duplicated local literal.
2. **A2-R2 — close the required PostgreSQL integration acceptance check.** The task still has an unchecked Acceptance Criterion and unchecked Validation item for recovery of a committed eligible PENDING revision after simulated initial queue loss. The repository already has the canonical disposable integration wrapper in `scripts/test-integration.mjs`, backed by `withDisposableIntegrationInfrastructure`. Run `npm run test:integration -- tests/integration/merchant-knowledge-reconciliation.integration.test.ts` from the canonical implementation worktree and record the passing result. A localhost `pg_isready` failure does not satisfy or replace this repository-owned disposable test path. If the Docker-compatible disposable harness genuinely cannot run, return the task `blocked` rather than resubmitting with this required check open.
3. **A2-R3 — make the mandatory execution-provenance evidence durable.** The Completion Report does not record the launcher-resolved physical parent/implementation worktrees, both task branches, shared-checkout non-use, start-of-attempt fast-forward/mainline synchronization results, or recursive implementation-submodule preparation. Record the required evidence from the prepared execution packet/worktree state. Clean branches and pushed commit identifiers alone do not substitute for the mandated Completion Report evidence.

The task is returned to `ready` with `attempt: 2` preserved. The next authorized claim increments it to Attempt 3. `ARCH-023-BACKGROUND-002` and `ARCH-023-BACKGROUND-003` remain Pending until BACKGROUND-001 is architect-accepted Complete.

### Reviewed Files
- `docs/decisions/background/ARCH-023/BACKGROUND-001-establish-merchant-knowledge-worker-foundation.md`
- `docs/decisions/background/ARCH-023/_index.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`
- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/scripts/test-integration.mjs`
- `moda-interact-background/database/prisma/schema.prisma`
- `moda-interact-background/src/runtime/readiness.ts`
- `moda-interact-background/src/entrypoints/merchant-knowledge-resources.ts`
- `moda-interact-background/src/services/merchant-knowledge-acquisition.ts`
- `moda-interact-background/src/services/merchant-knowledge-entitlement.service.ts`
- `moda-interact-background/src/services/merchant-knowledge-reconciliation.service.ts`
- `moda-interact-background/src/workers/merchant-knowledge.worker.ts`
- `moda-interact-background/src/observability/worker-metrics.ts`
- `moda-interact-background/src/observability/queue-performance.ts`
- focused Merchant Knowledge unit/integration tests
- `docs/agent-worktree-isolation-policy.md`

### Validation Reviewed
- Reported focused validation is internally consistent: entitlement 7/7, reconciliation 7/7, worker 5/5 and readiness 8/8 (27 tests total).
- Reported `npx tsc --noEmit`, `npm run prisma:generate`, `npm run prisma:validate`, `npm run build`, changed-file diagnostics and `git diff --check` passed.
- `package.json` exposes the canonical `npm run test:integration` wrapper, and `scripts/test-integration.mjs` provisions disposable PostgreSQL/Redis, deploys the real Prisma migrations and supplies the opt-in integration environment to Vitest.
- The required Merchant Knowledge PostgreSQL integration test remains unexecuted in the submitted Completion Report, so its Acceptance Criterion/Validation item correctly remains unchecked and prevents acceptance.
- The supplied review archive does not itself provide verifiable Git worktree history; the mandatory execution-provenance evidence must therefore be present durably in the Completion Report before acceptance.

### Architecture Conformance
**Conformant in substance, not yet acceptable.** Repository ownership, PostgreSQL/BullMQ boundaries, current-plan entitlement semantics, deterministic PENDING repair, worker isolation, Shared 1.0.1 consumption and non-deployable foundation scope are aligned with ARCH-023. The remaining issues are one cross-service contract-consumption correction plus required validation/provenance evidence; no architecture redesign or new task is required.

### Follow-up
For Attempt 3, make only the bounded correction/evidence changes above. Preserve database submodule commit `2eb17ee910491e8f9df82736fc0a843844415947` and exact Shared `1.0.1`; do not start BACKGROUND-002 or BACKGROUND-003. After the source/test correction, rerun the task-required focused validation including the disposable PostgreSQL integration test, update the Completion Report and return this same task to `review`.
