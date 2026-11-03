---
id: ARCH-055-API-005
architecture_id: ARCH-055
title: Correct knowledge-source and upload lifecycle
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-055-DATABASE-001
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-03
---

# ARCH-055-API-005: Correct knowledge-source and upload lifecycle

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 2. API-owned workflow / forward-migration contract; supersedes definition revision 1 without claiming an implementation attempt.

**Definition state:** materialised. Attempt 1 implementation is committed and pushed on the task branch. Required PostgreSQL validation could not start because Docker is unavailable, so the task is returned to `ready` without acceptance; the attempt is preserved.

## Objective

Make knowledge mutations safe against their actual Background writers and reduce repeated collection work without changing the best-effort read or durable pending-revision handoff.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E33`, `E34`, `E35`, `E36`, `E37`, `E38`, `E39`, `E40`, `E41`, `E42`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-api`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `src/merchant/merchant-knowledge/`
- `openapi/merchant-knowledge-v1.yaml`
- `tests/unit/merchant/merchant-knowledge/`
- `tests/integration/merchant/merchant-knowledge/`
- `scripts/test-arch035-merchant-knowledge-postgres.mjs`
- `scripts/test-arch035-knowledge-upload-postgres.mjs`

### Exact edit map — definition revision 2

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `src/merchant/merchant-knowledge/commands.service.ts` | RETURN locked principal fields rather than reread; use a writer entitlement projection without the unused preference lookup. For web PATCH/refresh/URL-change/DELETE mutations use id+shopId+currentGeneration=expectedGeneration and exact-one result; keep source/revision atomicity and existing no-op/replay rules. |
| `src/merchant/merchant-knowledge/read.service.ts` | REPLACE ACTIVE groupBy+fetch with direct ACTIVE findMany for the page source IDs. Preserve latest-vs-ACTIVE distinction and best-effort multi-query contract; no new encompassing transaction. |
| `src/merchant/merchant-knowledge/commands.service.ts` | ORDER/compact only rows whose final position changes; stage positive unique positions above current maximum, then final positions in deterministic order. Require safe integer range and no intermediate collision; full membership and atomic rollback remain. Untouched row updatedAt stays unchanged. |
| `src/merchant/merchant-knowledge/upload.service.ts` | INTENT: write intentPurposeKey once and compare it with all existing format/file/MIME/hash/size retry metadata. PENDING null legacy purpose conflicts; never infer/bind it. New key stays based on original Shop/request identity, not purpose. |
| `src/merchant/merchant-knowledge/upload.service.ts` | FINALISE: in committing transaction keep Shop/installation checks, then SELECT the same-Shop asset FOR NO KEY UPDATE, recheck state/expiry/purpose/file metadata/MIME after lock wait. For replacement next lock/revalidate the source generation. Hold asset/source coordination through AVAILABLE+original revision insert. Cleanup takes asset FOR UPDATE; the entitlement writer locks source and inserts a revision whose FK can take asset KEY SHARE. NO KEY UPDATE is selected to avoid an incompatible asset-key lock while waiting for that source; test this exact competing writer. Do not wait on provider/R2 under these locks. |
| `src/merchant/merchant-knowledge/upload.service.ts` | AVAILABLE replay: find original intake using uploadedAssetId + reason IN (CREATE,FILE_REPLACE), take2 and require exactly one valid same-Shop/source/format/purpose binding; return its persisted sourceId/revisionId/generation. Do not select arbitrary/latest REPROCESS. Legacy completed null-purpose assets require original source purpose to prove the request binding. |
| `src/merchant/merchant-knowledge/upload.service.ts; openapi/merchant-knowledge-v1.yaml` | Bound existing-upload eligibility to first K eligible sources with target fields, including web sources in rank; skip identical metadata after validation. Keep reprocess generation CAS/two writes and preflight contract; document existing 409 and sequential append, no new request field. |

**Exact new implementation/test paths (not baseline files claimed to exist):**

- `tests/integration/merchant/merchant-knowledge/arch055-generation-races.postgres.test.ts`
- `tests/integration/merchant/merchant-knowledge/arch055-upload-lifecycle.postgres.test.ts`
- `tests/integration/merchant/merchant-knowledge/arch055-ordering.postgres.test.ts`

**Test registration:** Add generation/order files to scripts/test-arch035-merchant-knowledge-postgres.mjs; add upload file to scripts/test-arch035-knowledge-upload-postgres.mjs. No schema copies/migrations in API.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Web PATCH/DELETE/refresh/URL change must put shopId, source ID and the expected generation in the actual conditional mutation and require exactly one changed row, as fixed in the exact edit map; do not substitute an ID-only mutation after an earlier read. Test against the real Background entitlement-generation writer, not only another API request. Preserve metadata-only versus ingestion changes, unique revision insertion rollback and current refresh duplicate semantics.

2. Upload intent must persist and compare intentPurposeKey with the already persisted retry metadata. The existing deterministic Shop/request-key asset ID is unchanged. Changed purpose conflicts even when both purposes accept the same format. Old pending assets with null purpose are not rebound: return a safe conflict requiring a new intent/key; they expire naturally. Do not delete storage or invent historical purpose.

3. Finalisation retains preliminary validation -> external HEAD/bounded GET/hash -> final transaction. In the final transaction coordinate with cleanup using the asset FOR NO KEY UPDATE lock selected below, held through revision insertion, recheck status, tenant, immutable metadata, purpose, expiry after waits, current MIME membership and target source/generation. Cleanup-wins must reject without resurrection; finalisation-wins must leave a committed reference cleanup respects.

4. AVAILABLE replay resolves the single original CREATE/FILE_REPLACE intake revision, never an arbitrary REPROCESS/ENTITLEMENT_CHANGE. Validate ownership/binding and return its original sourceId/revisionId/generation. Missing or ambiguous intake evidence fails closed; existing completed unbound legacy assets remain readable/reprocessable and may replay only where original-intake evidence proves the request binding.

5. Use the new original-intake partial uniqueness and preserve multiple reprocessing revisions per asset. Guard replacement's observed generation without adding a new public expectedGeneration field. Reprocess retains its current generation-CAS two-write unit and preflight boundary; document actual 409 and non-idempotent sequential append behaviour in OpenAPI, without inventing an idempotency key.

6. Reuse fields from locked principal rows and remove the web writer's unused preference lookup. Narrow per-operation peer-source projections. GET remains an explicit best-effort projection and directly fetches ACTIVE revision rows under the one-ACTIVE-per-source constraint; do not equate ACTIVE with latest.

7. Ordering and deletion compaction stage/update only rows whose final positions change. Keep complete membership, nonnegative/unique positions, deterministic order, safe positive staging, overflow handling, tenant predicates and atomic rollback. Retain no-op behaviour; untouched rows should retain updatedAt. Verify that no worker correctness relies on touching every survivor.

8. Bound existing-upload eligibility to the first K eligible sources with required fields in one query; web sources still occupy eligible positions. New-source allocation still sees all positions. Skip identical uploaded metadata updates after validation; keep metadata-only writes, no R2/config lookup and no generation append.

9. Preserve source/revision/asset atomicity and existing pending-revision reconciliation; no direct Redis handoff is added. Keep after-commit full-response behaviour of web commands and test/report commit success separately from projection failure. Do not silently change retry semantics or move the full refresh into the write transaction.

10. Preserve original exceptions through web-command wrappers; upload routes already retain original diagnostics and must not regress. Measure live/expired intent counts but do not add speculative indexes.

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

- [x] Implement conditional web mutations and add a Background-generation barrier regression covering metadata PATCH, URL PATCH, refresh and DELETE.
- [x] Use the accepted Database purpose/original-intake contracts in intent/finalisation/replay; add purpose-change, unbound-pending and post-reprocess replay assertions.
- [ ] Execute the full migration-backed lifecycle matrix. Cleanup/finalisation order, expiry during lock wait, MIME changes during R2 verification, source-replacement generation races, rollback and original replay now have test code; Docker absence prevented execution.
- [x] Reduce writer entitlement rereads, use direct ACTIVE revision lookup, bound existing-upload eligibility and skip identical metadata writes.
- [ ] Measure changed-only compaction against PostgreSQL: assertions for four swap updates, zero tail-delete updates and unchanged timestamps are present, but Docker absence prevented measurement.
- [x] Add post-commit projection failure tests and document reprocess 409/sequential append semantics in OpenAPI.

## Interfaces / Contracts

Consumes Database intentPurposeKey and original-intake uniqueness. Background generation/cleanup ownership is unchanged. Use actual installed Background writer fixtures via the terminal system suite; local migrated tests reproduce the database schedules without importing unpublished sibling source into production.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

- `ARCH-055-DATABASE-001` must have `status: complete` and an accepted review.

## Enables

- `ARCH-055-API-009`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] A stale generation cannot mutate/delete newer Background source state.
- [ ] No finaliser can change a cleanup tombstone to AVAILABLE or attach an intake to a deleted object.
- [ ] Finalisation replay always returns original intake identity after later reprocessing.
- [ ] Purpose changes under one request key conflict; immutable object identity and signed URL redaction remain intact.
- [ ] 100-source adjacent reorder changes four staged/final rows instead of 200, and deleting an already-last row performs no survivor writes, subject to verified constraints.
- [ ] Knowledge GET remains best-effort and read-only; metadata-only and ingestion operations retain their different contracts.
- [x] Original diagnostic causes survive with redaction; the route regression verifies the committed outcome and redacted cause through the Shared logger.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| E01 | Pause API after source read, actual-equivalent worker advances generation | Metadata PATCH/DELETE reject stale; URL/refresh rollback; no deletion of newer revision. |
| E02 | Expired cleanup wins after pre-network read but before finalisation asset lock | No resurrection, no new revision; finalisation conflicts. Reverse schedule commits reference and cleanup skips deletion. |
| E03 | Wait for asset lock across expiry; policy MIME changes during R2 | Recheck rejects current invalid state, no forged expiry, all writes roll back. |
| E04 | Intent retry changes only purpose; legacy unbound pending; replay after REPROCESS | Changed purpose/unbound pending conflict; original source/revision/generation replay remains exact after later revisions. |
| E05 | Swap adjacent pair among100; delete last source; unchanged metadata | 4 position writes for swap,0 for delete-tail compaction,0 metadata update; untouched timestamps preserved. |
| E06 | Commit succeeds then response projection throws | Log committed outcome separately; no assumed rollback or blind new generation. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npm run test:arch035-merchant-knowledge:postgres` — stopped before container creation: `docker` executable is unavailable.
- [ ] `npm run test:arch035-knowledge-upload:postgres` — stopped before container creation: `docker` executable is unavailable.
- [x] `npx tsx --test "tests/unit/merchant/merchant-knowledge/*.test.ts"` — 41 passed, 0 failed.
- [ ] `npm run typecheck` — Prisma Client generation succeeded with the permitted cache access; the TypeScript check did not finish after several minutes and was interrupted. No pass is claimed.
- [x] `git diff --check` — passed.
- [ ] `npm run lint` — repository lint reports one error in untouched `src/merchant/support/routes.ts:75` (`no-empty`). Targeted lint on every changed TypeScript file passed.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results — test instrumentation and assertions are present, but no PostgreSQL instance was available; actual SQL/row results and lock timing remain unmeasured.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

This is one functional task because the ten routes share commands.service.ts, upload.service.ts, read.service.ts, entitlement/ordering helpers and one generation/asset lifecycle. Use explicit subcommits for web CAS, upload finalisation and collection queries; do not split them into one task per endpoint.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report

### Status

Ready — Attempt 1 preserved. Implementation is published for review, but the required PostgreSQL suites and complete typecheck remain unverified. No architect acceptance is recorded.

### Files Changed

Implementation branch commits `e9b16c0` and `674341e` (published as `origin/task/ARCH-055-API-005`); accepted Database pin `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`.

- Source: `src/merchant/merchant-knowledge/{commands.contract.ts,commands.routes.ts,commands.service.ts,diagnostics.ts,read.service.ts,routes.ts,upload.routes.ts,upload.service.ts}`
- Contract and harnesses: `openapi/merchant-knowledge-v1.yaml`, `scripts/test-arch035-knowledge-upload-postgres.mjs`, `scripts/test-arch035-merchant-knowledge-postgres.mjs`
- Tests: `tests/integration/merchant/merchant-knowledge/{arch055-generation-races.postgres.test.ts,arch055-ordering.postgres.test.ts,arch055-upload-lifecycle.postgres.test.ts,upload.postgres.test.ts}` and `tests/unit/merchant/merchant-knowledge/{commands.test.ts,upload-reprocess.test.ts,upload-timing.test.ts}`

### Work Completed

Implemented the web generation compare-and-set mutations and compact-only changed ordering writes; removed the web writer preference reread; changed the ACTIVE revision projection to one direct query; bounded upload-source eligibility and reused all source positions for new allocations; added purpose binding, final asset/source locks, post-lock metadata/MIME/expiry checks, original-intake replay, and safe post-commit exception classification. Added the three required ARCH-055 PostgreSQL test files and registered them in both migration harnesses. Added bounded/redacted exception fields through the Shared logger routes, retaining error name, message, code and cause. Updated the reprocess OpenAPI description and existing upload regression coverage.

### Validation Results

The 41 Merchant Knowledge unit tests passed. Targeted ESLint on all changed TypeScript files and `git diff --check` passed. Repository-wide ESLint reports only the existing untouched `src/merchant/support/routes.ts:75` empty block. Both PostgreSQL harnesses were invoked and stopped at `starting disposable PostgreSQL`; `docker info` returned `command not found: docker`. No container, migration, SQL, row-count, lock-wait or concurrency result was produced. The full typecheck generated Prisma Client successfully but the subsequent TypeScript compiler did not complete after several minutes; it was interrupted and is not recorded as passing. The new integration assertions remain unchecked until they execute against PostgreSQL 17 + pgvector.

### Worktree and Git Evidence

Launcher packet: Attempt 1, claim commit `e1b6074abd84502750b1a08c865171585c3ac311`, parent start `c09c5ddf68ebb1bf3f007bbcfccff38812754dc8`, implementation start `0156090e8d4e68ce5c593763206951aa44805587`; both were synchronized to `origin/main` before work. Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-005`, branch `task/ARCH-055-API-005`. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-005`, branch `task/ARCH-055-API-005`. API commits `e9b16c0` and `674341e` are pushed to `origin/task/ARCH-055-API-005`. The nested Database pin is accepted commit `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. The parent task report update is local pending its own commit/push. No parent workspace gitlink was staged.

### Deviations

No scope deviation. Validation was limited by the missing Docker executable and a non-completing repository TypeScript check; neither was waived.

### Assumptions

The task implementation was based on the launcher-synchronized branch and accepted Database pin. PostgreSQL behavior is intentionally not inferred from unit tests or static inspection.

### Unresolved Issues

The required migration-backed integration results, full typecheck, real SQL/update-count evidence, lock timing and resource-cleanup evidence remain outstanding. The implementation branch is reviewable; do not accept the task until these validations run and the remaining checks are reconciled.

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


## Dependency readiness — 3 November 2026

ARCH-055-DATABASE-001 is Accepted and Complete at Attempt 2. The accepted Database pin is `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`; adopt it within this task's authorized consumer scope. The sole prerequisite is satisfied: Ready, Attempt 0, unclaimed. Prepare through the canonical launcher; no implementation, deployment or production migration is implied. Follow the Database task's coordinated migration/consumer rollout handoff.
