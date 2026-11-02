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
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-055-DATABASE-001
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: '2026-11-02'
---

# ARCH-055-API-005: Correct knowledge-source and upload lifecycle

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `pending` solely from the dependency graph below.

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

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Web PATCH/DELETE/refresh/URL change must put shopId, source ID and the expected generation in the actual conditional mutation and require exactly one changed row, or revalidate under a correctly ordered source lock. Test against the real Background entitlement-generation writer, not only another API request. Preserve metadata-only versus ingestion changes, unique revision insertion rollback and current refresh duplicate semantics.

2. Upload intent must persist and compare intentPurposeKey with the already persisted retry metadata. The existing deterministic Shop/request-key asset ID is unchanged. Changed purpose conflicts even when both purposes accept the same format. Old pending assets with null purpose are not rebound: return a safe conflict requiring a new intent/key; they expire naturally. Do not delete storage or invent historical purpose.

3. Finalisation retains preliminary validation -> external HEAD/bounded GET/hash -> final transaction. In the final transaction coordinate with cleanup using a freshly locked asset (or equivalent exact guarded transition held through revision insertion), recheck status, tenant, immutable metadata, purpose, expiry after waits, current MIME membership and target source/generation. Cleanup-wins must reject without resurrection; finalisation-wins must leave a committed reference cleanup respects.

4. AVAILABLE replay resolves the single original CREATE/FILE_REPLACE intake revision, never an arbitrary REPROCESS/ENTITLEMENT_CHANGE. Validate ownership/binding and return its original sourceId/revisionId/generation. Missing or ambiguous intake evidence fails closed; existing completed unbound legacy assets remain readable/reprocessable and may replay only where original-intake evidence proves the request binding.

5. Use the new original-intake partial uniqueness and preserve multiple reprocessing revisions per asset. Guard replacement's observed generation without adding a new public expectedGeneration field. Reprocess retains its current generation-CAS two-write unit and preflight boundary; document actual 409 and non-idempotent sequential append behaviour in OpenAPI, without inventing an idempotency key.

6. Reuse fields from locked principal rows and remove the web writer's unused preference lookup. Narrow per-operation peer-source projections. GET remains an explicit best-effort projection and directly fetches ACTIVE revision rows under the one-ACTIVE-per-source constraint; do not equate ACTIVE with latest.

7. Ordering and deletion compaction stage/update only rows whose final positions change. Keep complete membership, nonnegative/unique positions, deterministic order, safe positive staging, overflow handling, tenant predicates and atomic rollback. Retain no-op behaviour; untouched rows should retain updatedAt. Verify that no worker correctness relies on touching every survivor.

8. Bound existing-upload eligibility to the first K eligible sources with required fields in one query; web sources still occupy eligible positions. New-source allocation still sees all positions. Skip identical uploaded metadata updates after validation; keep metadata-only writes, no R2/config lookup and no generation append.

9. Preserve source/revision/asset atomicity and existing pending-revision reconciliation; no direct Redis handoff is added. Keep after-commit full-response behaviour of web commands and test/report commit success separately from projection failure. Do not silently change retry semantics or move the full refresh into the write transaction.

10. Preserve original exceptions through web-command wrappers; upload routes already retain original diagnostics and must not regress. Measure live/expired intent counts but do not add speculative indexes.

### Common execution and safety contract

- Read this task, the parent architecture, `docs/observability/shared-logging.md` and the four workspace VCS/worktree/developer/materialisation policies. Use the launcher-resolved dedicated parent and implementation worktrees; do not invent paths or start another task. A prepared launcher packet is accepted startup evidence.
- Use the existing Node/toolchain. Before the first Node command: `command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"`. Do not select/install a different Node version to make validation appear to pass.
- All workspace edits use repository-relative paths. Never edit another repository's implementation or a nested Database schema copy. A consumer records/updates only its own accepted nested Database pin under the task contract; never stage the parent workspace gitlink to an unmerged implementation commit.
- Shared logging is `@modainteract/moda-interact-shared/logging`. Preserve the actual original Prisma/SDK/provider message, code, cause and relevant safe response details through typed errors. Internal reason codes supplement, never replace, that evidence. Redact secrets, signed capabilities, customer content and connection URLs; public responses stay bounded. No generic local logger or duplicate framework telemetry.
- Preserve tenant scoping, canonical Shared schemas, immutable evidence, deliberate no-op/replay rules and original provider ambiguity. No provider/Redis/R2 I/O inside a database transaction. Read endpoints remain free of writes unless an explicitly unchanged contract says otherwise.
- Review baseline observations are static. Run regression tests against canonical migrations on disposable PostgreSQL 17 + pgvector, using separate connections and explicit barriers for races. Do not substitute mocks, `db push` or review-only Python models for lock/trigger proof.
- For each mandatory optimisation capture before/after actual SQL and affected rows on the same fixtures; distinguish client calls, SQL statements and row/byte changes. State workload and measurement limits. Optional MEASURE-FIRST items can conclude 'retain', with evidence and rationale; mandatory correctness changes cannot be deferred this way.
- Existing baseline failures are handled through `docs/development-baseline.md` only when actually encountered and relevant. Do not waive new regressions. Record commands actually executed and leave unavailable validations unchecked.
- Do not edit any `docs/decisions/**/_index.md`, old task status, the parent architecture, another task or shared execution rollup from a repository implementation task. Parent report updates are confined to this task file. No merge or push to main.

## Work Items

- [ ] Implement conditional web mutations and Background-writer barrier regressions.
- [ ] Use Database purpose/original-intake contracts in intent/finalisation/replay.
- [ ] Test both cleanup/finalisation orders, expiry during waiting, changed MIME/purpose, replacement races and rollback.
- [ ] Reduce common helper reads, ACTIVE lookup, existing-upload eligibility and identical metadata writes.
- [ ] Optimise changed-only compaction/order with real constraints, then measure rows modified and lock duration.
- [ ] Add post-commit response-failure tests and reprocess OpenAPI conflict semantics.

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
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npm run test:arch035-merchant-knowledge:postgres`
- [ ] `npm run test:arch035-knowledge-upload:postgres`
- [ ] `npx tsx --test "tests/unit/merchant/merchant-knowledge/*.test.ts"`
- [ ] `npm run typecheck`
- [ ] `git diff --check`
- [ ] Run the repository's declared linter against the exact changed source/test files; record any broader unchanged baseline failure separately.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

This is one functional task because the ten routes share commands.service.ts, upload.service.ts, read.service.ts, entitlement/ordering helpers and one generation/asset lifecycle. Use explicit subcommits for web CAS, upload finalisation and collection queries; do not split them into one task per endpoint.

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
