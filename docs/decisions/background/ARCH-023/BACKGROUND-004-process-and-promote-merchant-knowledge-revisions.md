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
status: ready
priority: 32
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-023-BACKGROUND-002
  - ARCH-023-BACKGROUND-003
  - ARCH-023-BACKGROUND-006
  - ARCH-023-DATABASE-005
  - ARCH-023-BACKGROUND-007
enables:
  - ARCH-023-BACKGROUND-005
created: 2026-09-29
updated: 2026-10-01
---

# Process and promote Merchant Knowledge revisions

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Complete the production Merchant Knowledge worker by implementing the common processing state machine after source acquisition: current-entitlement **and merchant-activation** guards, exact D3 normalization/content limiting, deterministic chunking, multilingual embedding, pgvector persistence, generation-safe promotion, retry/failure handling, observability and final dedicated entrypoint composition.

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

Call the BACKGROUND-006 activation-aware `resolveSourceEligibility(source.id)` contract (the accepted BACKGROUND-001 service extended by BACKGROUND-006).

Cases:

```text
globallySupported = false
  -> mark revision FAILED
     failureCode = SOURCE_TYPE_UNSUPPORTED
     do not acquire

entitlement null
or merchantEnabled = false
or sourceTypeAllowed = false
or withinSourceAllowance = false
  -> leave/reset revision PENDING
     clear processingStartedAt
     do not acquire
     return success (dormant, not retry failure)

eligible = true
  -> continue
```

Do not infer plan entitlement from purpose/data format alone. Do not process when the merchant preference is missing/false, even if the plan maps Merchant Knowledge.

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

1. re-resolve activation-aware source eligibility;
2. require source still current/eligible and Merchant Knowledge still explicitly enabled;
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
merchant-disabled or otherwise dormant source remains PENDING
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

- [x] Add exact embedding runtime config.
- [x] Implement pure D3 normalization/content-unit/truncation helpers.
- [x] Implement deterministic chunking/hashing.
- [x] Implement OpenAI embedding adapter and provenance validation.
- [x] Implement processing state machine and acquisition dispatch.
- [x] Implement pgvector persistence/promotion transaction.
- [x] Implement permanent/transient/terminal failure behavior.
- [x] Create final dedicated Merchant Knowledge entrypoint after DATABASE-005 and BACKGROUND-007 acceptance.
- [x] Wire PENDING reconciliation and upload cleanup schedules using the accepted lease contracts.
- [x] Add package start/readiness scripts.
- [x] Add focused unit/integration/entrypoint tests, including the dedicated worker entrypoint/readiness contract.

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
- `ARCH-023-BACKGROUND-006`
- `ARCH-023-DATABASE-005`
- `ARCH-023-BACKGROUND-007`

## Enables

- `ARCH-023-BACKGROUND-005`

## Acceptance Criteria

- [x] Dedicated Merchant Knowledge entrypoint is operational and independently startable.
- [x] Source processing is tenant/current-plan/current-generation scoped.
- [x] Exact D3 normalization/truncation and D17 chunking are implemented.
- [x] Vectors/provenance persist correctly with pgvector dimension validation and parameterized writes.
- [x] Prior ACTIVE revision remains usable until successful replacement.
- [x] Mid-flight entitlement changes cannot promote stale results.
- [x] Retry behavior does not corrupt durable lifecycle state.
- [x] PENDING queue-loss reconciliation and upload cleanup are scheduled.
- [x] No automatic URL refresh or entitlement-change revision generation is implemented here.

## Validation

- [x] all focused normalization/chunking/processing/embedding tests: 36 passed; the database integration case was skipped in this first focused run.
- [x] pgvector integration test: 1 passed against the disposable `pgvector/pgvector:pg17` fixture after applying all 21 committed database migrations.
- [x] final worker entrypoint/readiness unit tests: 4 passed, covering dedicated worker isolation, both fixed leased schedules, cleanup, start/readiness scripts and Redis/PostgreSQL readiness requirements. The live readiness command was not rerun in Attempt 2; the earlier disposable Redis/PostgreSQL readiness run passed.
- [ ] `npm test`: failed. With the disposable database configured, 12 files failed (22 tests), 94 files passed, and 2 files were skipped (1,321 tests passed, 4 skipped). Causes include missing ARCH-020 fixture, existing tests using Prisma fields absent from the pinned schema, unrelated billing/recovery expectation failures, observability timeout/version assertions, Merchant Knowledge reconciliation fixture interference under parallel execution, and upload-cleanup transaction timeout. Serial Merchant Knowledge processing and reconciliation integrations passed; upload cleanup had one test fail after its 5-second transaction expired.
- [x] `npm run build`
- [x] `npm run readiness:merchant-knowledge-worker` against disposable Redis/PostgreSQL fixture: ready.
- [x] `git diff --check`
- [x] changed-file diagnostics clean

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP. Do not start BACKGROUND-005 or Gateway.

## Completion Report

### Status
Blocked: implementation and validation are complete for processing, but the dedicated entrypoint and both leased schedules cannot be implemented safely within this task's authorized files. The pinned database schema's `BackgroundRuntimeLeaseName` enum lacks `MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION` and `MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP`; `src/runtime/background-runtime-lease.ts` also lacks cadence mappings. Database schema/migrations are owned by `moda-interact-database`, while changing the background lease runtime is outside this task's authorized file list. R14 is therefore not deployable and requires `moda_architect` to sequence the database/runtime contract work before this task can resume.
### Files Changed
Implementation commit `f1e6869` (`feat: process merchant knowledge revisions`), pushed to `task/ARCH-023-BACKGROUND-004` in `moda-interact-background`:
- `package.json`
- `src/services/merchant-knowledge-chunking.ts`
- `src/services/merchant-knowledge-embedding.ts`
- `src/services/merchant-knowledge-failures.ts`
- `src/services/merchant-knowledge-normalization.ts`
- `src/services/merchant-knowledge-processing.service.ts`
- `tests/integration/merchant-knowledge-processing.integration.test.ts`
- `tests/unit/services/merchant-knowledge-chunking.test.ts`
- `tests/unit/services/merchant-knowledge-embedding.test.ts`
- `tests/unit/services/merchant-knowledge-normalization.test.ts`
- `tests/unit/services/merchant-knowledge-processing.service.test.ts`
- This task report only.
### Work Completed
Implemented the embedding configuration/client, D3 normalization and code-point truncation, deterministic D17 chunking, activation-aware processing state machine, format-specific acquisition dispatch, transient/permanent/terminal retry handling, and transactional pgvector promotion with parameterized metadata/content values. Added processing/unit coverage and a real pgvector promotion integration test. Added only the two requested package scripts; no existing worker scripts or package dependencies changed.
### Validation Results
Passed: focused Merchant Knowledge unit tests (36 tests); `npm run build`; disposable pgvector promotion integration (1 test); `npm run readiness:merchant-knowledge-worker` against task-isolated Redis and PostgreSQL; changed-file diagnostics; and staged `git diff --check`.

Full suite: `npm test` did not pass. With the disposable database configured, Vitest reported 12 failed files / 22 failed tests, 94 passed files / 1,321 passed tests, and 2 skipped files / 4 skipped tests. Failures include a missing ARCH-020 evidence fixture, several unrelated integration fixtures using `defaultOutboundSoftLimit` absent from the pinned generated Prisma schema, unrelated promotion/billing/recovery expectations, observability timeouts and an expected shared-package version of `0.12.1` versus manifest `1.0.1`, plus parallel Merchant Knowledge fixture interference. A clean serial run passed processing and reconciliation integrations; upload cleanup had one test fail when its page-through transaction exceeded 5 seconds. These failures were not represented as baseline IDs or changed as part of this task.
### Deviations
R14 and the associated entrypoint/readiness test remain unimplemented because their required lease enum labels and lease cadence handling are unavailable under the pinned database/background runtime contracts. No type cast, unrelated lease name, local advisory-lock substitute, or cross-repository schema change was introduced.
### Assumptions
The local integration services were disposable containers on localhost with database `moda_interact`; only committed migrations were deployed. No shared/developer database was modified.
### Unresolved Issues
`moda_architect` must arrange the missing lease contract: database enum/migration support for both exact Merchant Knowledge lease names, plus corresponding background lease cadence mapping. The task can resume on the same mirrored task branches after that contract is available.
### Architectural Concerns
The required scheduler leases cross the database/runtime ownership boundary. Shipping the entrypoint before those enum values and cadence mappings exist would cause scheduler lease acquisition to fail or never become due, so this is a blocking dependency rather than a validation-only omission.

## Architect Review

### Review Status
Blocked — Attempt 1

### Review Notes
The blocker is valid and crosses repository ownership boundaries. The task-owned Merchant Knowledge entrypoint draft requires the exact lease identities `MERCHANT_KNOWLEDGE_PENDING_RECONCILIATION` and `MERCHANT_KNOWLEDGE_UPLOAD_CLEANUP`, but the pinned database `BackgroundRuntimeLeaseName` enum does not contain either value. The shared Background lease service also has no global cadence branch for either lease identity.

Do not work around this by casting strings, reusing an unrelated lease, introducing Redis/advisory locking, adding cadence columns, or editing the database/runtime lease implementation inside BACKGROUND-004. The already-agreed scheduler intervals remain 60 seconds for PENDING reconciliation and 3600 seconds for upload cleanup.

No acceptance decision is made on the partial processing implementation in this blocked review. No source correction is requested unless refreshed validation after the prerequisites exposes a regression.

### Reviewed Files

- `src/entrypoints/merchant-knowledge.ts` task-owned draft
- `src/runtime/background-runtime-lease.ts`
- `database/prisma/schema.prisma`
- `tests/unit/runtime/background-runtime-lease.test.ts`
- `docs/decisions/background/ARCH-023/BACKGROUND-004-process-and-promote-merchant-knowledge-revisions.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`

### Validation Reviewed

Reviewed the Completion Report evidence: focused Merchant Knowledge processing tests, pgvector promotion integration, build, readiness, diagnostics and whitespace checks passed as recorded; the repository-wide suite remains non-clean for the recorded mixed baseline/fixture failures. The final entrypoint/scheduler proof remains legitimately open because the required lease contract is unavailable.

### Architecture Conformance

The repository agent correctly stopped at the ownership boundary. The missing enum values belong to `moda_database`; the global lease cadence mapping belongs to `moda_background` runtime infrastructure but is outside BACKGROUND-004's authorised surface. Shipping R14 before both prerequisites exist would make lease acquisition invalid or cadence enforcement incomplete.

### Follow-up

1. `ARCH-023-DATABASE-005` adds exactly the two Merchant Knowledge lease enum values and its forward migration.
2. After DATABASE-005 is Complete/accepted, `ARCH-023-BACKGROUND-007` pins that database revision and adds the two fixed global cadence mappings (`60` and `3600` seconds) with focused/runtime PostgreSQL proof.
3. BACKGROUND-004 remains Blocked until both tasks are Complete/accepted and their accepted changes are available on its execution baseline. Preserve the current partial implementation. Before reclaim, ensure the task-owned untracked entrypoint draft is durably checkpointed on the implementation task branch or otherwise made clean without stashing, resetting or discarding it.
4. Then reconcile BACKGROUND-004 `blocked -> ready`; the next launcher claim becomes Attempt 2. Attempt 2 finishes R14 and the remaining entrypoint/full validation only; it must not begin BACKGROUND-005.

## Developer Override

### Decision
Reopened on 2026-10-01 by explicit developer request: `/moda_developer_update ARCH-023-BACKGROUND-004 reopen`.

### Previous Attempt
No attempt has been accepted. Attempt 1 remains the preserved blocked implementation attempt; this reopen does not increment the attempt number.

### Reason
The developer explicitly requested reopening after the prerequisite work completed. `ARCH-023-DATABASE-005` is now Complete / Accepted Attempt 2, and `ARCH-023-BACKGROUND-007` is Complete / Accepted Attempt 1. No additional reason was supplied.

### State Transition
`blocked -> ready`; `executor` and `claimed_at` remain null; `attempt` remains 1. The next `/moda-task ARCH-023-BACKGROUND-004` claim will be Attempt 2 and must follow the existing Architect Review constraints, preserve the partial implementation, and complete only the dedicated entrypoint, schedules and remaining required validation.

### Dependency Reconciliation
`ARCH-023-BACKGROUND-005` remains `pending` because it depends on BACKGROUND-004 being Complete. It is unclaimed and requires no regression. No downstream task already in progress, review or complete was changed.

### Blocker Resolution
DATABASE-005 is Complete / Accepted Attempt 2 and BACKGROUND-007 is Complete / Accepted Attempt 1. The exact enum identities and fixed 60-second / 3600-second global lease cadences are available. The task is `ready` with Attempt 1 preserved; the next normal claim becomes Attempt 2. Preserve the existing partial implementation and complete only R14 plus the remaining task-defined validation before returning to architect review.

## Attempt 2 Completion Report

### Status
Implementation and task-defined Attempt 2 validation are complete. Returned to `review` for `moda_architect`; this report makes no architect acceptance decision.

### Preparation Evidence
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-BACKGROUND-004`, branch `task/ARCH-023-BACKGROUND-004`; parent `origin/main` was already incorporated at `7e24ec7c15ac5db94b1e9677fb9477ff9c74682e`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-BACKGROUND-004`, branch `task/ARCH-023-BACKGROUND-004`; implementation `origin/main` was already incorporated at prepared HEAD `87cc3e03997ef1f7455e47f5241c72be9527e285`.
- Launcher dependency gate passed for BACKGROUND-002, BACKGROUND-003, BACKGROUND-006, DATABASE-005 and BACKGROUND-007.
- Recursive submodule sync/update passed; `database` was verified at the exact recorded DATABASE-005 commit `b34a563436bbc89b6ca3e26b43a0bd03116a1a66`.
- Attempt 2 was claimed by `copilot` at `2026-10-01T10:01:05Z`; parent claim commit `9e4c091284525f9ee7afeb20e7eb0f9bf8ebbdd3` was committed and pushed by the launcher.

### Files Changed
- `src/entrypoints/merchant-knowledge.ts`
- `tests/unit/entrypoints/merchant-knowledge.test.ts`

The previously untracked, task-owned entrypoint draft was preserved and checkpointed before preparation in implementation commit `75c8531`. Attempt 2 corrected its WEB_PAGE acquirer import to the existing `MerchantKnowledgeWebPageAcquirer` export.

### Work Completed
- Completed the dedicated `moda-merchant-knowledge-worker` entrypoint using the existing readiness lifecycle, configuration and lease services, processing worker, upload cleanup, queue telemetry and owned resource shutdown.
- Added the PENDING reconciliation lease at 60 seconds with immediate execution and page size 100; added upload cleanup at 3600 seconds with immediate execution.
- Added focused contract coverage for worker isolation, exact lease names/cadences, reconciliation and cleanup calls, queue telemetry, shutdown ownership, package commands and Redis/PostgreSQL readiness requirements.

### Validation Results
- `npm run test -- tests/unit/entrypoints/merchant-knowledge.test.ts tests/unit/runtime/entrypoint-isolation.test.ts tests/unit/workers/merchant-knowledge.worker.test.ts`: passed, 18 tests across 3 files.
- `npm run build`: passed, including Prisma generation against the accepted database pin and TypeScript compilation.
- Changed-file diagnostics: no errors in either changed file.
- `git diff --check`: passed.
- The live readiness CLI was not rerun in Attempt 2 because it performs external Redis/PostgreSQL probes. The focused readiness contract test passed; the prior disposable readiness command passed during Attempt 1 as recorded above.
- The repository-wide `npm test` is not repeated in Attempt 2. Its mixed failures from Attempt 1 remain recorded in the original Completion Report; they were not represented as caused or fixed by this bounded entrypoint change.

### Deviations and Unresolved Issues
No implementation scope deviation or new cross-repository requirement. No unresolved implementation blocker remains; the task awaits architect review.

### Architectural Concerns
None. The entrypoint consumes the accepted DATABASE-005 lease identities and BACKGROUND-007 cadence mappings without changing their ownership or contract.

## Architect Review — Attempt 2

### Review Status
Changes Requested — evidence-only workflow correction.

### Review Notes
The implementation is functionally conformant. No production or test-code correction is requested. The previously blocked processing pipeline was reviewed together with the new dedicated entrypoint because Attempt 1 was Blocked rather than partially accepted. The implementation conforms to R1-R17 by inspection and the recorded focused/pgvector validation: exact normalization and code-point truncation, deterministic chunking, bounded embedding configuration/vector checks, activation-aware current-source guards, acquisition dispatch, retry/permanent-failure handling, transactional pgvector promotion that supersedes the prior ACTIVE revision only after candidate persistence, and the final dedicated worker entrypoint with the exact 60-second PENDING reconciliation and 3600-second upload-cleanup leased schedules.

Attempt 2 also consumes the exact accepted DATABASE-005 pin `b34a563436bbc89b6ca3e26b43a0bd03116a1a66` and the accepted BACKGROUND-007 cadence contract without casts, substitute lease names or cross-repository changes. The bounded Attempt 2 validation is sufficient: 18 focused entrypoint/isolation/worker tests, production build, changed-file diagnostics and `git diff --check` passed. The live readiness CLI need not be rerun solely for this review because its Redis/PostgreSQL dependency contract was already proven with disposable infrastructure in Attempt 1 and the accepted DATABASE-005/BACKGROUND-007 work owns the subsequently added lease identities/cadences. The non-clean repository-wide suite remains documented from Attempt 1 and is not attributed to this bounded entrypoint correction.

The review cannot be accepted yet because the Attempt 2 Completion Report does not contain the mandatory physical-isolation/synchronization evidence required by `docs/agent-worktree-isolation-policy.md`. The report records the canonical paths, branches, `origin/main` incorporation, recursive submodule preparation and dependency gate, but it omits:

1. the three required physical-isolation attestations:
   - `shared workspace checkout switched/mutated for task work: no`;
   - `shared implementation checkout switched/mutated for task work: no`;
   - `another task worktree reused: no`;
2. the two missing explicit remote-task-branch synchronization outcomes, so all four required start-of-attempt values are not durably recorded in the required `yes|not-needed` / `yes|already-current` form;
3. the final submitted implementation and parent-report heads. The architect handoff identifies implementation `4f2b4ff` and parent report `69c020d7`, but those final heads must be written into the Completion Report rather than existing only in chat.

Branch cleanliness and successful pushes do not substitute for the missing physical-isolation evidence under the governing policy.

### Attempt 3 correction contract
Attempt 3 is evidence-only unless synchronization or refreshed validation exposes a genuine regression. Preserve the current implementation; do not begin BACKGROUND-005.

1. Reclaim this same task only through `/moda-task ARCH-023-BACKGROUND-004` so the canonical parent and implementation worktrees are reused and synchronized.
2. Record the complete launcher packet in the Completion Report, including exactly:

```text
Physical worktree isolation:
  canonical workspace root: <launcher path>
  parent worktree: <launcher path>
  parent branch: task/ARCH-023-BACKGROUND-004
  implementation worktree: <launcher path>
  implementation branch: task/ARCH-023-BACKGROUND-004
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

3. Record recursive submodule preparation and the exact DATABASE-005 gitlink, plus the final pushed implementation and parent-report commit IDs.
4. Rerun the bounded acceptance evidence from the canonical prepared implementation worktree: the 18 focused tests, `npm run build`, changed-file diagnostics and `git diff --check`. The repository-wide suite and live readiness CLI do not need to be repeated solely to manufacture evidence unless the synchronized baseline changes relevant code/contracts or the launcher/task validation policy requires them.
5. Return the task to `review` with `executor` and `claimed_at` cleared. No implementation-source change is expected.

### Architecture Conformance
Functionally conforms. The only outstanding issue is workflow evidence. `ARCH-023-BACKGROUND-005` remains gated until BACKGROUND-004 is architect-accepted Complete.
