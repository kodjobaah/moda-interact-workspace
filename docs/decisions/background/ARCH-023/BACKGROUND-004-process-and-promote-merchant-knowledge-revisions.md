---
id: ARCH-023-BACKGROUND-004
architecture_id: ARCH-023
title: Process and promote Merchant Knowledge revisions
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 32
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-BACKGROUND-002
  - ARCH-023-BACKGROUND-003
enables:
  - ARCH-023-BACKGROUND-005
created: 2026-09-29
updated: 2026-09-29
---

# Process and promote Merchant Knowledge revisions

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Complete the production Merchant Knowledge worker by implementing the common processing state machine after source acquisition: current-entitlement guards, exact D3 normalization/content limiting, deterministic chunking, multilingual embedding, pgvector persistence, generation-safe promotion, retry/failure handling, observability and final dedicated entrypoint composition.

This is the task that makes:

```text
src/entrypoints/merchant-knowledge.ts
```

deployable.

## Scope

Authorized primary files:

```text
package.json
package-lock.json

src/entrypoints/merchant-knowledge.ts

src/services/merchant-knowledge-processing.service.ts
src/services/merchant-knowledge-normalization.ts
src/services/merchant-knowledge-chunking.ts
src/services/merchant-knowledge-embedding.ts
src/services/merchant-knowledge-failures.ts

src/workers/merchant-knowledge.worker.ts          # terminal-failure integration only if required
src/entrypoints/merchant-knowledge-resources.ts  # only if final composition requires it

tests/unit/services/merchant-knowledge-normalization.test.ts
tests/unit/services/merchant-knowledge-chunking.test.ts
tests/unit/services/merchant-knowledge-processing.service.test.ts
tests/unit/services/merchant-knowledge-embedding.test.ts
tests/integration/merchant-knowledge-processing.integration.test.ts
tests/unit/entrypoints/merchant-knowledge.test.ts
```

Also add package start/readiness scripts exactly as specified below.

## Out of Scope

- Shopify source CRUD/upload issuance.
- plan authoring/materialisation.
- Commerce lookup.
- automatic entitlement-change revisions (BACKGROUND-005).
- Gateway deployment.
- ANN index.
- another vector database.
- another queue.
- automatic scheduled URL refresh.

## Requirements

### R1 — exact embedding environment contract

Read exactly:

```text
EMBEDDING_PROVIDER
EMBEDDING_MODEL
EMBEDDING_DIMENSIONS
EMBEDDING_INDEX_VERSION
EMBEDDING_API_KEY
```

V1 supports:

```text
EMBEDDING_PROVIDER=openai
```

Any other value fails worker startup with `UNSUPPORTED_EMBEDDING_PROVIDER`.

Rules:

```text
EMBEDDING_MODEL: trimmed non-empty
EMBEDDING_DIMENSIONS: positive safe integer
EMBEDDING_INDEX_VERSION: trimmed non-empty <= 64
EMBEDDING_API_KEY: trimmed non-empty, never logged
```

Use the existing `openai` dependency.

Embedding provider/model are deployment configuration, not database/Admin configuration.

### R2 — worker job identity validation

`processJob` receives the parsed C4 payload from BACKGROUND-001 worker.

Before source acquisition:

1. load revision by `sourceRevisionId` with source, Purpose, Data Format and uploaded asset relation;
2. if missing -> bounded no-op diagnostic `REVISION_NOT_FOUND`;
3. require:
   ```text
   source.shopId == job.shopId
   revision.generation == job.generation
   revision.generation == source.currentGeneration
   ```
4. any mismatch is stale/invalid and MUST NOT mutate another revision;
5. terminal statuses:
   ```text
   ACTIVE
   SUPERSEDED
   FAILED
   ```
   are no-op;
6. PENDING may be claimed;
7. PROCESSING may be retried for the same current generation after a transient BullMQ failure.

### R3 — entitlement before acquisition

Call BACKGROUND-001 `resolveSourceEligibility(source.id)`.

Cases:

```text
globallySupported = false
  -> mark revision FAILED
     failureCode = SOURCE_TYPE_UNSUPPORTED
     do not acquire

entitlement null
or sourceTypeAllowed = false
or withinSourceAllowance = false
  -> leave/reset revision PENDING
     clear processingStartedAt
     do not acquire
     return success (dormant, not retry failure)

eligible = true
  -> continue
```

Do not infer plan entitlement from purpose/data format alone.

### R4 — claim processing atomically

For PENDING:

```text
UPDATE revision
SET status = PROCESSING,
    processingStartedAt = NOW(),
    failureCode = NULL
WHERE id = ?
  AND status = PENDING
  AND generation = current source generation
```

Only one caller may win the claim.

For PROCESSING retry of same generation, continue idempotently; later persistence must delete/rebuild any partial chunks for that same non-ACTIVE revision before insert.

### R5 — acquisition dispatch

Dispatch exactly:

```text
Data Format inputKind = REMOTE_URL
  -> require requestedUrl != null
  -> WEB_PAGE acquirer

Data Format inputKind = UPLOAD
  -> require uploadedAssetId != null
  -> require dataFormat.key IN CSV/XLSX
  -> uploaded-asset acquirer
```

Reject locator/input-kind mismatches permanently with bounded `LOCATOR_FORMAT_MISMATCH`.

Do not select acquisition behavior from filename alone.

### R6 — exact D3 normalization

Implement one pure function:

```ts
normalizeMerchantKnowledgeText(input: string): string
```

Algorithm in exact order:

1. Unicode NFC.
2. convert CRLF to LF.
3. convert remaining CR to LF.
4. replace every Unicode `White_Space` code point except LF with U+0020 SPACE.
5. collapse consecutive U+0020 SPACE to one SPACE.
6. remove SPACE immediately before or after LF.
7. collapse three or more consecutive LF to exactly two LF.
8. trim leading/trailing SPACE and LF.

Count Unicode code points by iteration, never UTF-16 `.length`.

Content units:

```text
ceil(normalizedCodePointCount / 4)
```

### R7 — exact entitlement truncation

After normalization, use the currently resolved:

```text
maxContentUnitsPerSource
```

Maximum normalized code points:

```text
maxContentUnitsPerSource * 4
```

If normalized content exceeds that count:

1. take exactly the first N Unicode code points;
2. set `truncated = true`;
3. calculate `contentUnits` from the resulting truncated string.

Otherwise:

```text
truncated = false
```

Do not truncate by bytes, words or UTF-16 code units.

`contentHash` is lowercase SHA-256 of exact UTF-8 bytes of the final normalized/truncated content.

### R8 — deterministic chunking

Implement:

```text
target chunk size = 1200 Unicode code points
overlap           = 200 Unicode code points
```

Rules:

```text
chunk 0 starts at code point 0
next chunk start = previous start + 1000
final chunk may be shorter
empty content -> zero chunks
empty chunk never stored
ordinal starts 0 and increments 1
```

For each chunk:

```text
contentUnits = ceil(chunkCodePoints / 4)
contentHash = lowercase SHA-256(UTF-8 exact chunk content)
```

Do not perform semantic paragraph splitting in v1.

### R9 — embeddings

For every non-empty chunk call OpenAI embeddings using:

```text
model = EMBEDDING_MODEL
input = exact chunk content
dimensions = EMBEDDING_DIMENSIONS
```

Require returned vector:

```text
array length == EMBEDDING_DIMENSIONS
every element is finite number
```

Do not persist/return provider response metadata beyond:

```text
embeddingProvider
embeddingModel
embeddingDimensions
embeddingIndexVersion
```

No embedding call for zero chunks.

### R10 — re-check current entitlement before promotion

After acquisition/normalization/embedding but before final persistence transaction:

1. re-resolve source eligibility;
2. require source still current/eligible;
3. require current `maxContentUnitsPerSource` equals the limit used for normalization.

If the source is now dormant or the content limit changed:

```text
revision -> PENDING
processingStartedAt -> NULL
do not persist candidate chunks
return success
```

B1 reconciliation will later re-enqueue when appropriate.

This prevents a mid-flight downgrade from promoting stale entitlement output.

### R11 — final promotion transaction

Within one database transaction:

1. lock/reload source and candidate revision;
2. require:
   ```text
   revision.generation == source.currentGeneration
   revision.status == PROCESSING
   ```
3. identify existing ACTIVE predecessor, if any;
4. delete any chunks already attached to the candidate revision from a retry;
5. persist candidate revision:
   ```text
   contentType
   resolvedUrl
   normalizedContent
   contentUnits
   contentHash
   truncated
   fetchedAt
   completedAt = NOW()
   failureCode = NULL
   ```
6. insert all candidate chunks/vectors/provenance;
7. if predecessor ACTIVE exists:
   ```text
   predecessor.status = SUPERSEDED
   predecessor.completedAt remains historical
   ```
8. set candidate:
   ```text
   status = ACTIVE
   completedAt = NOW()
   ```
9. delete predecessor semantic chunks;
10. commit.

Order step 7 before step 8 so the database one-ACTIVE partial unique index is never violated.

Do not delete predecessor normalized content or upload reference.

### R12 — pgvector write safety

Because Prisma exposes `embedding` as `Unsupported("vector")`, use parameterized raw SQL only for the vector column.

Before SQL serialization validate:

```text
vector length == EMBEDDING_DIMENSIONS
every value finite
```

Serialize only the validated numeric array to PostgreSQL vector literal form.

All ids/text/metadata use parameter binding; never concatenate source text or ids into raw SQL.

### R13 — transient vs permanent failures

Define bounded failure categories.

Permanent examples:

```text
SOURCE_TYPE_UNSUPPORTED
LOCATOR_FORMAT_MISMATCH
UNSAFE_URL
UNSUPPORTED_MEDIA_TYPE
UPLOAD_HASH_MISMATCH
UPLOAD_FORMAT_INVALID
XLSX_ACTIVE_CONTENT
CONTENT_INVALID
```

Permanent failure:

```text
revision.status = FAILED
failureCode = bounded code
completedAt = NOW()
prior ACTIVE revision unchanged
worker job resolves (no retry)
```

Transient examples:

```text
DNS_TEMPORARY
FETCH_TIMEOUT
HTTP_429
HTTP_5XX
R2_TEMPORARY
EMBEDDING_PROVIDER_TEMPORARY
DATABASE_TRANSIENT
```

Transient failure:

```text
leave status PROCESSING
throw to BullMQ
```

On the final BullMQ attempt, the BACKGROUND-001 worker's `markTerminalFailure` integration must mark that same current revision:

```text
FAILED
failureCode = RETRIES_EXHAUSTED
completedAt = NOW()
```

provided generation is still current and status is PROCESSING.

A later/stale revision is never changed by terminalization.

### R14 — final dedicated entrypoint

Create `src/entrypoints/merchant-knowledge.ts`.

Use existing:

```text
startReadyWorkerProcess
backgroundRuntimeConfigService
backgroundRuntimeLeaseService
startDynamicLeasedScheduler
startQueuePerformanceTelemetry
connectionRedis
closeWorkerObservability
```

Service name:

```text
moda-merchant-knowledge-worker
```

Start exactly one queue worker:

```text
createMerchantKnowledgeWorker(merchantKnowledgeProcessingService)
```

Start PENDING reconciliation scheduler:

```text
leaseName: MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION
interval: 60_000 ms
runImmediately: true
run: reconciliationService.reconcilePendingOnce({pageSize: 100})
```

Start upload cleanup scheduler:

```text
leaseName: MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP
interval: 3_600_000 ms
runImmediately: true
run: uploadCleanupService.cleanupOnce()
```

Add queue-performance telemetry for:

```text
merchant-knowledge
```

Close all workers/schedulers/queue resources/config/observability on shutdown using existing worker-process conventions.

### R15 — package scripts

Add exactly:

```json
"start:merchant-knowledge-worker": "node dist/entrypoints/merchant-knowledge.js",
"readiness:merchant-knowledge-worker": "node dist/readiness.js moda-merchant-knowledge-worker"
```

Do not change existing worker scripts.

### R16 — structured logs only

Log bounded state transitions/outcomes; never log:

```text
extracted/normalized source content
spreadsheet rows
vectors
R2 object keys
credentials
customer messages
```

### R17 — processing tests

At minimum prove:

```text
stale generation cannot acquire/promote
dormant source remains PENDING
globally unsupported source -> FAILED
valid WEB_PAGE uses web acquirer
valid CSV/XLSX uses upload acquirer
exact normalization cases
Unicode code-point counting (including supplementary characters)
truncation uses code points not UTF-16 units
chunk starts 0,1000,2000...
empty normalized content produces ACTIVE revision with zero chunks
embedding dimension mismatch rejects
mid-flight source-type downgrade resets PENDING/no promotion
mid-flight content-limit change resets PENDING/no promotion
old ACTIVE remains on permanent/transient failure
retry candidate does not duplicate chunks
successful promotion supersedes old ACTIVE then activates new revision
old predecessor chunks deleted; predecessor normalized content retained
terminal retry failure only marks current PROCESSING revision
```

## Work Items

- [ ] Add exact embedding runtime config.
- [ ] Implement pure D3 normalization/content-unit/truncation helpers.
- [ ] Implement deterministic chunking/hashing.
- [ ] Implement OpenAI embedding adapter and provenance validation.
- [ ] Implement processing state machine and acquisition dispatch.
- [ ] Implement pgvector persistence/promotion transaction.
- [ ] Implement permanent/transient/terminal failure behavior.
- [ ] Create final dedicated Merchant Knowledge entrypoint.
- [ ] Wire PENDING reconciliation and upload cleanup schedules.
- [ ] Add package start/readiness scripts.
- [ ] Add focused unit/integration/entrypoint tests.

## Interfaces / Contracts

Consumes:

```text
BACKGROUND-001 worker/entitlement/reconciliation contracts
BACKGROUND-002 WEB_PAGE acquirer
BACKGROUND-003 uploaded-asset acquirer + cleanup
ARCH-023 database schema
Shared C1-C4
```

Produces the deployable Background process required by Gateway.

## Dependencies

- `ARCH-023-BACKGROUND-002`
- `ARCH-023-BACKGROUND-003`

## Enables

- `ARCH-023-BACKGROUND-005`

## Acceptance Criteria

- [ ] Dedicated Merchant Knowledge entrypoint is operational and independently startable.
- [ ] Source processing is tenant/current-plan/current-generation scoped.
- [ ] Exact D3 normalization/truncation and D17 chunking are implemented.
- [ ] Vectors/provenance persist correctly with pgvector dimension enforcement.
- [ ] Prior ACTIVE revision remains usable until successful replacement.
- [ ] Mid-flight entitlement changes cannot promote stale results.
- [ ] Retry behavior does not corrupt durable lifecycle state.
- [ ] PENDING queue-loss reconciliation and upload cleanup are scheduled.
- [ ] No automatic URL refresh or entitlement-change revision generation is implemented here.

## Validation

- [ ] all focused normalization/chunking/processing/embedding tests
- [ ] pgvector integration test
- [ ] final worker entrypoint/readiness test
- [ ] `npm test`
- [ ] `npm run build`
- [ ] `npm run readiness:merchant-knowledge-worker` against disposable Redis/PostgreSQL fixture
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP. Do not start BACKGROUND-005 or Gateway.

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
