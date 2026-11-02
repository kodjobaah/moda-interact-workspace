---
id: ARCH-055-API-008
architecture_id: ARCH-055
title: Consolidate Support-inbox persistence
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 35
executor: codex
claimed_at: 2026-11-02T21:53:14Z
attempt: 1
depends_on: []
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-02
---

# ARCH-055-API-008: Consolidate Support-inbox persistence

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 2. API-owned workflow / forward-migration contract; supersedes definition revision 1 without claiming an implementation attempt.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `ready` solely from the dependency graph below.

## Objective

Provide a coherent Support inbox projection and one atomic thread/message write without weakening translation repair, suspended-Shop read access or mark-read replay semantics.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E49`, `E50`, `E51`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-api`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `src/merchant/support/`
- `tests/unit/merchant/support/`
- `tests/integration/merchant/support/`
- `scripts/test-arch035-woo-support-postgres.mjs`

### Exact edit map — definition revision 2

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `src/merchant/support/read.service.ts` | CHOOSE one parameterised data statement (CTEs allowed) for page plus total/unread after existing principal checks; the empty page still returns aggregate. Keep transaction ReadCommitted and existing share locks. Join AVAILABLE translation using unique messageId/targetLanguageTag, not latest-row lateral query. |
| `src/merchant/support/commands.service.ts` | Compose combines thread create/conflict bookkeeping/version into initial UPSERT RETURNING id, then message/translation writes inside same tx. Replay check remains before write. Mark-read remains unchanged conditional-write/winner-reread algorithm. |
| `src/merchant/support/translation-queue.ts` | Replace empty Queue error listener with safe original-error logging through injected shared logger. Queue add stays after commit and existing durable repair unchanged. |

**Exact new implementation/test paths (not baseline files claimed to exist):**

- `tests/integration/merchant/support/arch055-snapshot-and-thread.postgres.test.ts`

**Test registration:** Append to scripts/test-arch035-woo-support-postgres.mjs. Existing selection callers using installation.ts must pass unchanged tests; no global helper-policy rewrite.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Adopt ADR-05: page items and total/unread count must represent one statement/snapshot. Use the single parameterised support-data statement including the empty-page aggregate selected below; preserve existing transaction isolation and principal/share-lock semantics. Keep all existing visibility, language, tenant and system-message recovery-link checks.

2. Replace latest-row lateral translation machinery with the unique messageId/targetLanguageTag left join, preserving AVAILABLE filtering, missing-translation visibility and body suppression. Measure the emitted plan; do not add an index already supplied by uniqueness.

3. Compose: combine thread creation/conflict bookkeeping and merchant-message-version increment into the initial UPSERT result. Replay lookup remains first. Preserve current thread-owner fields, monotonic version, Admin concurrent-reply rules and complete rollback if message/translation insert fails.

4. Queue dispatch remains after commit with the existing PENDING translation repair worker. The Queue error event must log the original redacted error via shared logging; enqueue failures must not roll back a successfully committed message or expose Redis URLs/message bodies.

5. Mark-read keeps conditional readAt IS NULL update, original read timestamp on replay and winner reread after a lost update. Update-first is MEASURE-FIRST only: document first-use versus replay/missing-call trade-off and retain current behaviour unless justified. Never use an unconditional COALESCE update to hide replay writes.

6. Suspended Shops retain approved read/mark access but not compose access. ARCH-055-API-002 consumes the installation helper for its existing checks; any shared-helper edit must preserve those callers and their focused regressions. No global mutation-policy rewrite is authorised.

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

- [ ] Implement coherent list/count projection and unique translation lookup.
- [ ] Combine thread bookkeeping writes and add rollback plus concurrent Admin reply fixtures.
- [ ] Log queue-emitted connection failures without changing durable repair semantics.
- [ ] Add coordinated mark-read race tests; measure rather than automatically switch query order.

## Interfaces / Contracts

Public Support DTOs, idempotency keys, translation queue contract and suspended-Shop policy stay unchanged. The coherent list/count snapshot is an explicit ARCH-055 decision rather than a claim about the old implementation.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

None. The source baseline is context, not a fabricated dependency on historical review evidence.

## Enables

- `ARCH-055-API-009`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Message readAt and unread count are consistent under a controlled mark-read interleaving.
- [ ] New composition saves one thread write while replay still performs no writes.
- [ ] A queue outage leaves a durable pending translation that the existing reconciler can repair.
- [ ] Concurrent read markers return the same winning timestamp; foreign/unavailable messages remain ineligible.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| H01 | Pause former page/count boundary while message is marked read | One data-statement old or new coherent page/unread result, including empty pages. |
| H02 | Translation missing/pending/AVAILABLE and system recovery link foreign | Existing visibility/body suppression/tenant link rules unchanged. |
| H03 | Message/translation insertion fails after thread upsert; Admin concurrent reply | Entire transaction rolls back; reply version coordination preserved. |
| H04 | Redis error event/add timeout after durable compose | Message stays committed; original bounded cause logged; repair can dispatch. |
| H05 | Two readers mark same message; already-read replay; suspended/foreign message | Winner timestamp returned, no timestamp rewrite, existing permitted/denied policies retained. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npm run test:arch035-woo-support:unit`
- [ ] `npm run test:arch035-woo-support:postgres`
- [ ] `npm run test:arch046-woo-selection:unit`
- [ ] `npm run typecheck`
- [ ] `git diff --check`
- [ ] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

Do not add a new translation worker or turn Redis into a correctness dependency. Any empty catch retained solely for logger failure isolation must remain narrowly documented and may not hide business exceptions.

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
