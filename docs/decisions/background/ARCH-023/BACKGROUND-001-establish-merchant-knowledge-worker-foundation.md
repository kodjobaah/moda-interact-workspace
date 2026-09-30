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
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 4
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
- [x] A committed eligible PENDING revision can be re-enqueued after simulated initial queue loss (Attempt 4 disposable PostgreSQL integration passed).
- [x] Repeated reconciliation uses the same deterministic job id.
- [x] Stale/non-current revision generations are skipped.
- [x] Existing Background workers/readiness identities remain unchanged.
- [x] No deployable Merchant Knowledge entrypoint exists yet.
- [x] No source acquisition/embedding/vector work is implemented in this task.

## Validation

- [x] `npm test -- --run tests/unit/services/merchant-knowledge-entitlement.service.test.ts` — 7 passed.
- [x] `npm test -- --run tests/unit/services/merchant-knowledge-reconciliation.service.test.ts` — 7 passed.
- [x] `npm test -- --run tests/unit/workers/merchant-knowledge.worker.test.ts` — 5 passed.
- [x] Database-backed reconciliation integration test — passed against a fresh disposable `pgvector/pgvector:pg17` container; all repository Prisma migrations applied, including `20260929160000_arch023_merchant_knowledge_schema`.
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
Review requested after Attempt 4; awaiting `moda_architect`. No architect acceptance decision has been made by this agent.

### Files Changed
Attempt 4 made no implementation-source changes. The Attempt 3 correction remains at implementation commit `3ed6621`, pushed to `origin/task/ARCH-023-BACKGROUND-001`; the prior foundation is in implementation commit `06566f8`. This attempt updates only this task report in the parent worktree. The database submodule remains at `2eb17ee910491e8f9df82736fc0a843844415947`; no database files or gitlink were changed.

### Work Completed
Attempt 2 established the worker foundation. Attempt 3 addressed Architect Review corrections A2-R1 and A2-R3 and recorded A3-R1 as blocked because the repository integration wrapper's default PostgreSQL image lacked pgvector. Attempt 4 satisfies A3-R1 without changing the integration wrapper, Shared helper, Gateway, production Background code, database schema, or migration history.

Started a fresh task-unique `pgvector/pgvector:pg17` container with a random password, a dedicated database, and a dynamically assigned loopback-only host port. Waited for Docker health to become `healthy`, validated the Prisma schema, and applied every repository migration through `npx prisma migrate deploy --schema database/prisma/schema.prisma`, including `20260929160000_arch023_merchant_knowledge_schema`. The queue-loss integration test exercised the production reconciliation service against PostgreSQL while mocking queue publication: it verified that failed initial enqueue left the durable revision PENDING, then recovery enqueued it with a stable job ID. The EXIT cleanup trap removed the container; no volume or network was created. No production entrypoint, acquisition implementation, embedding/vector processing, or database schema change was added.

### Validation Results
Attempt 4 live integration evidence:

- Image: `pgvector/pgvector:pg17` (`sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`).
- Container: `arch023-background001-attempt4-1790766444-19077`; database `arch023_bg001_a4`; dynamically assigned loopback port `32776`; random password not retained in this report.
- Readiness: Docker health reached `healthy` before connecting.
- Schema validation: `npm run prisma:validate` passed.
- Migration command: `npx prisma migrate deploy --schema database/prisma/schema.prisma`; all migrations applied successfully, including `20260929160000_arch023_merchant_knowledge_schema`.
- Integration command: `TEST_DATABASE_URL="$database_url" DATABASE_URL="$database_url" MODA_DISPOSABLE_INTEGRATION=1 npx vitest run tests/integration/merchant-knowledge-reconciliation.integration.test.ts` — 1 test passed.
- Teardown: EXIT trap ran `docker rm -f arch023-background001-attempt4-1790766444-19077`; the terminal recorded `DISPOSABLE_CONTAINER_TORN_DOWN`. No container volume or network was created.

Attempt 3 focused unit suites passed: entitlement 7/7, reconciliation 7/7, and worker 5/5 (19 total). `npx tsc --noEmit` and `git diff --check` passed. Attempt 2's other passing validation remains recorded above. Attempt 4 made no implementation-source changes.

### Deviations
No implementation or shared test-infrastructure changes were required. Validation used only the task-authorized disposable container. No unrelated audit remediation was attempted.

### Assumptions
None.

### Unresolved Issues
None known. The generic wrapper's default image limitation remains unchanged; the required queue-loss proof passed using the explicitly authorized task-local pgvector container.

### Architectural Concerns
The generic integration wrapper still does not select a pgvector image, but this task-local validation requirement is satisfied without changing shared infrastructure. Architect Review remains owned by `moda_architect` and was not modified.

### Git / VCS

Task branch: `task/ARCH-023-BACKGROUND-001` in both repositories.

Physical worktree isolation:
- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree and branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-BACKGROUND-001`, `task/ARCH-023-BACKGROUND-001`
- implementation worktree and branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-BACKGROUND-001`, `task/ARCH-023-BACKGROUND-001`
- shared workspace checkout switched or mutated: no
- shared implementation checkout used or mutated: no
- another task worktree reused: no; the canonical worktrees for this task were reused

Start-of-attempt synchronization from the prepared packet:
- parent remote task branch fast-forwarded: not-needed
- parent `origin/main` incorporated: already-current
- implementation remote task branch fast-forwarded: not-needed
- implementation `origin/main` incorporated: already-current

Implementation repository:
- repository: `moda-interact-background`
- current implementation commit: `3ed66214bf43ec7e882c28bbdef4c6b290a39734`; no Attempt 4 implementation commit was needed
- remote branch: `origin/task/ARCH-023-BACKGROUND-001`
- pushed: yes

Parent workspace:
- task file: `docs/decisions/background/ARCH-023/BACKGROUND-001-establish-merchant-knowledge-worker-foundation.md`
- Attempt 4 claim: launcher commit `6b5c0d2a01ce4b2057b61b0417b1bbbe960cdbb8`, timestamp `2026-09-30T11:05:58Z`; committed and pushed before execution
- prior report update: committed and pushed on `origin/task/ARCH-023-BACKGROUND-001` before Attempt 4
- Attempt 4 report update: this task report only; commit and push follow validation
- submodule gitlink staged: no

Recursive implementation submodule preparation from the prepared packet: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; status `ready`; database commit `2eb17ee910491e8f9df82736fc0a843844415947` initialized.

Merged to implementation `main`: no. Merged to workspace `main`: no.

## Architect Review

### Review Status
Accepted — Attempt 4

### Review Notes

#### Attempt 4 review — Accepted — 2026-09-30

Reviewed implementation correction `3ed66214bf43ec7e882c28bbdef4c6b290a39734`, the
existing foundation at `06566f8`, and the submitted Attempt 4 parent report at `3a4c41ba`
against the original BACKGROUND-001 contract and the complete Attempt 3 correction
contract. Attempt 4 is accepted.

The production implementation remains architecture-conformant. The repository consumes
exactly `@modainteract/moda-interact-shared@1.0.1`; readiness adds only
`moda-merchant-knowledge-worker -> [redis, postgresql]`; the queue resource uses the
canonical Shared queue/job contract and existing `connectionRedis`; and the acquisition
interfaces contain extracted source text only.

Current-plan entitlement resolution uses the unique current Subscription, accepts only
ACTIVE/TRIALING, reads the current plan Feature keyed `merchant_knowledge`, validates C2
with the published Shared schema, fails closed on malformed configuration, filters by
active/allowed Purpose/Data Format pairs before applying the deterministic
`(position ASC, id ASC)` source allowance, and does not consult pending-plan state or
`ShopFeaturePreference`.

PENDING reconciliation is bounded and ordered, skips stale generations and currently
ineligible sources, builds C4 jobs with Shared
`MERCHANT_KNOWLEDGE_PROCESS_SCHEMA_VERSION`, and uses Shared
`createMerchantKnowledgeProcessJobId()` for deterministic redelivery. Queue publication
does not mutate source/revision content. The dedicated worker validates the Shared job
schema, reuses the existing Redis/telemetry/worker-observation mechanisms, delegates
processing to the injected processor, and bounds terminal failure codes without logging
source content.

The final A3-R1 acceptance gate is now satisfied. Attempt 4 provisioned a fresh
`pgvector/pgvector:pg17` PostgreSQL container with isolated credentials and loopback host
port, waited for health, applied the repository's real Prisma migrations including
`20260929160000_arch023_merchant_knowledge_schema`, and ran the authored production-path
`merchant-knowledge-reconciliation.integration.test.ts` with
`MODA_DISPOSABLE_INTEGRATION=1`. The test passed 1/1 and proved that an enqueue failure
leaves the committed revision PENDING and that reconciliation subsequently republishes it
with a stable deterministic job id. The cleanup trap removed the disposable container;
no task-created volume/network or remote database was used.

Attempt 4 made no production-source, schema, migration, gitlink, Shared-helper,
integration-wrapper or Gateway change. The generic integration wrapper's default
non-pgvector image therefore remains outside this task and is not an acceptance blocker.
No deployable Merchant Knowledge entrypoint exists yet; final composition remains owned
by BACKGROUND-004.

The review archive intentionally omits Git metadata and installed dependencies. The
Completion Report supplies the launcher-resolved dedicated parent/implementation
worktrees, matching task branches, Attempt 4 claim/synchronization evidence, recursive
submodule preparation, pushed implementation/report commits and clean handoff. The
submitted focused validation plus the live disposable-database proof close every task
Acceptance Criterion and required Validation item.

### Reviewed Files

Implementation repository:

- `package.json`
- `package-lock.json`
- `src/runtime/readiness.ts`
- `src/entrypoints/merchant-knowledge-resources.ts`
- `src/services/merchant-knowledge-acquisition.ts`
- `src/services/merchant-knowledge-entitlement.service.ts`
- `src/services/merchant-knowledge-reconciliation.service.ts`
- `src/workers/merchant-knowledge.worker.ts`
- `tests/unit/services/merchant-knowledge-entitlement.service.test.ts`
- `tests/unit/services/merchant-knowledge-reconciliation.service.test.ts`
- `tests/unit/workers/merchant-knowledge.worker.test.ts`
- `tests/integration/merchant-knowledge-reconciliation.integration.test.ts`
- `database/prisma/schema.prisma`

Parent workspace:

- `docs/decisions/background/ARCH-023/BACKGROUND-001-establish-merchant-knowledge-worker-foundation.md`
- `docs/decisions/background/ARCH-023/BACKGROUND-002-acquire-merchant-knowledge-web-pages.md`
- `docs/decisions/background/ARCH-023/BACKGROUND-003-acquire-merchant-knowledge-uploads.md`
- `docs/decisions/background/ARCH-023/_index.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`

### Validation Reviewed

- Attempt 3 focused unit suites passed **19/19**: entitlement 7/7, reconciliation 7/7 and worker 5/5.
- Attempt 3 `npx tsc --noEmit` and `git diff --check` passed.
- Confirmed package manifest and lockfile pin exact Shared `1.0.1`.
- Confirmed reconciliation source and focused regression use Shared `MERCHANT_KNOWLEDGE_PROCESS_SCHEMA_VERSION` rather than a duplicated local literal.
- Confirmed the integration test exercises production `MerchantKnowledgeReconciliationService` against PostgreSQL and mocks only queue publication.
- Attempt 4 disposable PostgreSQL proof used `pgvector/pgvector:pg17`; `npm run prisma:validate` passed and `npx prisma migrate deploy --schema database/prisma/schema.prisma` applied all migrations including the ARCH-023 pgvector migration.
- Attempt 4 production-path queue-loss integration passed **1/1** with `TEST_DATABASE_URL`/`DATABASE_URL` bound to the disposable database and `MODA_DISPOSABLE_INTEGRATION=1`.
- Attempt 4 teardown recorded `docker rm -f` and `DISPOSABLE_CONTAINER_TORN_DOWN`; no disposable volume/network remained.
- The archive has no installed `node_modules` or Docker runtime transcript beyond the durable report, so those commands were not independently re-run in this review container; the implementation and authored test path were inspected directly.

### Architecture Conformance

Conforms. BACKGROUND-001 establishes only the Background-owned worker/entitlement/repair
foundation over the accepted ARCH-023 database and Shared contracts. PostgreSQL remains
the durable source of truth, BullMQ publication remains retryable/repairable, current-plan
commercial entitlement is rechecked server-side, and deterministic job identity provides
at-least-once convergence without introducing exactly-once assumptions.

The implementation does not cross into WEB_PAGE/R2 acquisition, normalization,
embeddings/vector writes, revision promotion, entitlement-change revision creation,
Gateway deployment, Commerce lookup or Shopify producer ownership. It also does not make
the partial worker deployable before BACKGROUND-004 composition.

### Follow-up

`ARCH-023-BACKGROUND-001` is **Complete / Accepted at Attempt 4**.

Dependency reconciliation makes exactly these newly satisfied dependants Ready in
parallel:

```text
ARCH-023-BACKGROUND-002
ARCH-023-BACKGROUND-003
```

BACKGROUND-004 remains Pending until both are architect-accepted Complete. No downstream
implementation is started implicitly by this review.

#### Historical Attempt 3 — Changes Requested — 2026-09-30

##### Review Notes
Attempt 3 resolves the two source/report corrections that remained from the prior review:

1. **A2-R1 is satisfied.** The reconciliation producer now uses Shared `MERCHANT_KNOWLEDGE_PROCESS_SCHEMA_VERSION`, and the focused reconciliation test asserts the canonical Shared constant rather than a duplicated local literal.
2. **A2-R3 is satisfied.** The Completion Report now records the launcher-resolved parent/implementation worktrees, matching task branches, shared-checkout non-use, start-of-attempt synchronization and recursive submodule preparation evidence.

Architect acceptance remains withheld only for the required database-backed enqueue-loss proof. The Attempt 3 failure is an integration-environment limitation, not evidence of a Merchant Knowledge implementation defect: the repository wrapper delegates to Shared's disposable helper without selecting a PostgreSQL image, so its default `postgres:17.6-alpine` image cannot apply migration `20260929160000_arch023_merchant_knowledge_schema` because pgvector is unavailable.

**A3-R1 — run the existing reconciliation integration test against a task-local disposable pgvector PostgreSQL container.** This task is explicitly authorised to create and destroy its own one-off Docker PostgreSQL environment for validation. Do not modify Shared's disposable helper, `scripts/test-integration.mjs`, Gateway infrastructure, the database schema, or production Background source merely to provision the test database.

The Attempt 4 validation must:

1. start a fresh disposable PostgreSQL 17 container whose image includes the pgvector extension (for example `pgvector/pgvector:pg17`);
2. use a task-unique container name and isolated database credentials/host port so no existing local or remote database is touched;
3. wait until the disposable PostgreSQL instance is ready;
4. point `DATABASE_URL` at that disposable database and apply the repository's real Prisma migrations, including `20260929160000_arch023_merchant_knowledge_schema`;
5. run only `tests/integration/merchant-knowledge-reconciliation.integration.test.ts` with `TEST_DATABASE_URL` pointing at the same disposable database and `MODA_DISPOSABLE_INTEGRATION=1` so the authored production-path integration test actually executes;
6. confirm the queue-loss scenario passes and then check the previously open Acceptance Criterion/Validation item;
7. always remove the disposable container (and any task-created disposable volume/network, if used) after validation, whether the test passes or fails;
8. record the Docker image, database/migration command, test command/result, and teardown evidence in the Completion Report.

The integration test mocks queue publication, so Redis is not required for this bounded proof. Do not use the configured remote database. No production source change is requested unless this stronger live proof exposes a genuine defect; if it does, correct only that defect within BACKGROUND-001 scope and rerun the focused validation.

If a Docker-capable local environment is genuinely unavailable, return the same task `blocked` with the concrete Docker failure rather than substituting a remote database or marking the acceptance item complete.

The task is returned to `ready` with `attempt: 3` preserved. The next authorised claim increments it to Attempt 4. `ARCH-023-BACKGROUND-002` and `ARCH-023-BACKGROUND-003` remain Pending until BACKGROUND-001 is architect-accepted Complete.

##### Reviewed Files
- `docs/decisions/background/ARCH-023/BACKGROUND-001-establish-merchant-knowledge-worker-foundation.md`
- `docs/decisions/background/ARCH-023/_index.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`
- `moda-interact-background/scripts/test-integration.mjs`
- `moda-interact-background/tests/integration/merchant-knowledge-reconciliation.integration.test.ts`
- `moda-interact-background/src/services/merchant-knowledge-reconciliation.service.ts`
- accepted ARCH-023 database migration surface referenced by the integration failure

##### Validation Reviewed
- Attempt 3 focused unit validation passed 19/19: entitlement 7/7, reconciliation 7/7 and worker 5/5.
- `npx tsc --noEmit` and `git diff --check` passed.
- A2-R1 code/test correction is present and uses Shared `MERCHANT_KNOWLEDGE_PROCESS_SCHEMA_VERSION`.
- The required integration command reached disposable infrastructure setup but failed before Vitest because `postgres:17.6-alpine` does not contain `vector.control`; therefore the queue-loss Acceptance Criterion correctly remains unchecked.
- The existing integration test exercises the production `MerchantKnowledgeReconciliationService` against PostgreSQL while mocking only queue publication, so a standalone pgvector-capable PostgreSQL container is sufficient to close the missing proof.

##### Architecture Conformance
**Conformant in implementation; acceptance pending one required live validation.** The worker foundation remains within the intended Background boundary, consumes the canonical Shared schema-version constant, preserves the accepted database contract, and records the required execution provenance. Creating a disposable pgvector-capable PostgreSQL container solely for task validation does not introduce runtime infrastructure or alter repository ownership.

##### Follow-up
Reclaim this same task for Attempt 4 and perform the bounded disposable-Docker PostgreSQL validation above. Do not start BACKGROUND-002 or BACKGROUND-003. If the migration and queue-loss integration test pass, update the Completion Report, check the remaining Acceptance Criterion/Validation item, return the task to `review`, clear the claim and STOP.
