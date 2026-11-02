---
id: ARCH-055-API-002
architecture_id: ARCH-055
title: Streamline consent and recovery ingress without weakening STOP
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 25
executor: copilot
claimed_at: 2026-11-02T21:41:52Z
attempt: 1
depends_on: []
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-02
---

# ARCH-055-API-002: Streamline consent and recovery ingress without weakening STOP

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 2. API-owned workflow / forward-migration contract; supersedes definition revision 1 without claiming an implementation attempt.

**Definition state:** materialised and claimed. The launcher prepared the dedicated parent and implementation worktrees, passed the dependency gate, and recorded Attempt 1 for executor `copilot`.

## Objective
Keep the recovery-ingress safety boundary intact while separating duplicate/read-only work from mutation locking and retaining original database/queue errors.
Blocked. The required unit, Redis, consent PostgreSQL, restore PostgreSQL and typecheck validations now pass. Lint reports one unrelated existing `no-empty` error in `src/merchant/support/routes.ts:75`. The mandatory M03 paired baseline/candidate SQL and affected-row measurements have not been captured, so this is not Ready for Review.

## Context
Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E03`, `E04`, `E05`, `E06`, `E08`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.
### Files Changed

- `src/woocommerce/activity/routes.ts`
- `src/woocommerce/activity/redis-producer.ts`
- `src/woocommerce/consent/service.ts`
- `src/woocommerce/recovery-selection/service.ts`
- `src/woocommerce/recovery-restore/routes.ts`
- `scripts/test-arch046-woo-consent-postgres.mjs`
- `scripts/test-arch053-recovery-restore-postgres.mjs`
- `tests/unit/woocommerce/activity/routes.test.ts`
- `tests/integration/woocommerce/consent/races.postgres.test.ts`
- `tests/integration/woocommerce/consent/arch055-duplicate-and-selection.postgres.test.ts`
- `tests/integration/woocommerce/recovery-restore/service.postgres.test.ts`
- `tests/integration/woocommerce/recovery-restore/arch055-revalidation.postgres.test.ts`

## Scope
One owning repository: `moda-interact-api`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.
### Work Completed

- Consent event handling now checks immutable evidence after event-key coordination and before the recipient advisory lock; exact replay returns the prior acknowledgement without restoring later REVOKE/STOP state. New evidence still takes recipient coordination.
- Recovery-selection GET avoids recipient advisory and row-level write locks; mutation retains the existing locking path.
- Activity failures distinguish authentication/database and Redis connection/publication stages. Bounded diagnostics retain safe error code/cause details and redact connection URLs; Redis error events are attached as causes to readiness failures. Queue acceptance and retained-job verification were not intentionally changed.
- Restore diagnostics preserve bounded safe Prisma/SQL identifiers and causes. The restore runner deploys canonical migrations in its disposable database, and its fixture uses canonical schema fields/constraints.
- Added the exact named consent/selection PostgreSQL regression file and registered it in the consent runner. Added the named restore revalidation test to the restore runner.

- `src/woocommerce/activity/`
- `src/woocommerce/recovery-selection/`
### Validation Results

- `npm run test:arch035-woo-activity:unit`: passed, 25/25 tests.
- `npm run test:arch035-woo-activity:redis`: passed, 2/2 disposable Redis/BullMQ tests, including transport failure not returning HTTP 202. The runner reported successful disposable Redis validation and cleanup.
- `npm run test:arch046-woo-consent:unit`: passed, 6/6 tests.
- `npm run test:arch046-woo-selection:unit`: passed, 3/3 tests.
- `npm run test:arch046-woo-consent:postgres`: all 68 canonical migrations applied and all 13 PostgreSQL tests passed, including duplicate replay before recipient lock, GET through a held phone-row lock, concurrent GRANT/REVOKE and STOP, credential rotation, rollback, and tenant isolation. Runner cleanup completed. An earlier transient P1001 was resolved by retry.
- `npm run test:arch053-recovery-restore:postgres`: all 68 canonical migrations applied and both tests passed (2/2), including completion, generation, and lifetime changes between the two eligibility reads. Runner cleanup completed.
- `npm run typecheck`: passed after Prisma Client generation.
- `npm run lint`: one unrelated existing failure remains at `src/merchant/support/routes.ts:75` (`no-empty`). The task-local unused parameter/binding findings are fixed; no out-of-scope lint change was made.
- `git diff --check`: passed. The task correction commit is `a96bc83d0fd4715d73f575858a5b684d2d489552`, published to `origin/task/ARCH-055-API-002`; implementation worktree is clean.
- Docker engine reachability was verified with the configured `docker` CLI (`colima`; Docker Engine 29.7.2). PostgreSQL and Redis runners reported cleanup on completed runs.
- M03 baseline/candidate SQL, affected-row, timing, retry and invocation measurements were not captured. Existing consent-runner counters are explicitly labeled for ARCH-046-API-007 and do not measure M03's duplicate replay, new event, or recovery-selection GET profiles. No measurements are inferred from unrelated counters. The task-start baseline SHA is `fa2a857`; however, the required paired runs using identical restored fixtures, two discarded warm-ups and five recorded samples per version were not executed.
- No production p95 or capacity inference is made.
- `src/woocommerce/recovery-restore/`
- `tests/unit/woocommerce/activity/`
- `tests/unit/woocommerce/recovery-selection/`
### Worktree and Git Evidence

- Prepared launcher packet accepted: task `ARCH-055-API-002`, executor `copilot`, attempt 1, status `in_progress`, dependency gate passed.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-002`, branch `task/ARCH-055-API-002`. Launcher claim commit: `6e3b37698b72f31f747b4f33d21de952b28341fc`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-002`, branch `task/ARCH-055-API-002`, final implementation HEAD `a96bc83d0fd4715d73f575858a5b684d2d489552`, clean and published to `origin/task/ARCH-055-API-002`. The task includes implementation commit `903be9f4baf0fdecf56d5acc13db28ab051bd63d` and fixture/type correction commit `a96bc83d0fd4715d73f575858a5b684d2d489552`.
- Prepared Database submodule pin: `7c377282aa5819b3008b7d7f3018f44f4161523e`; no schema/migration edits made.
- The implementation branch contains the original implementation commit `903be9f` plus correction commit `a96bc83`; both are published on the task branch. This parent report update is limited to the current task file. No main merge/push was performed.
- `tests/unit/woocommerce/recovery-restore/`
- `tests/integration/woocommerce/consent/`
- `scripts/test-arch046-woo-consent-postgres.mjs`
### Deviations

- No schema or public contract changes were made. Fixture corrections supply canonical required timestamps, cast bound enum parameters, and mutate the existing recovery row for the generation race because canonical uniqueness prevents inserting another row for the same Shop/checkout token. Task lifecycle remains `blocked` because required M03 paired measurements are unavailable; the unrelated lint finding is recorded separately.
- `scripts/test-arch053-recovery-restore-postgres.mjs`
- `src/merchant/support/installation.ts [read-only dependency; ARCH-055-API-008 owns changes]`
### Exact edit map — definition revision 2
### Unresolved Issues

- M03 paired before/after SQL and affected-row measurements remain outstanding; existing consent benchmark counters cover a different task/profile and cannot stand in for M03 evidence. Capture the required success-path profiles using the same restored fixtures, baseline `fa2a857` and candidate `a96bc83`, including actual SQL shapes, affected rows, two warm-ups and five recorded samples per version.
- Full lint still reports the unrelated existing `src/merchant/support/routes.ts:75` `no-empty` finding. It was left unchanged because it is outside this task's edit map.
- All listed unit, Redis, consent PostgreSQL, restore PostgreSQL, typecheck and diff-check validations passed. Keep the task blocked until M03 evidence is captured and reviewed; no production p95 or capacity claim is made.

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `src/woocommerce/activity/routes.ts; src/woocommerce/activity/redis-producer.ts` | MODIFY failures to retain original causes and identify authentication/database versus connection/publication stage. Leave the queue acceptance path and producer retained-job verification unchanged. |
| `src/woocommerce/consent/service.ts` | MOVE existing immutable-evidence lookup after event lock but before recipient lock. Exact digest replay returns original acknowledgement; only new evidence proceeds to recipient lock/current-phone mutation/evidence insert. |
| `src/woocommerce/recovery-selection/service.ts` | SPLIT GET recipient lookup from mutation lookup: GET omits recipient advisory lock and FOR UPDATE; keep transaction-local Shop/installation checks. POST retains current lock and revision order. |
| `src/woocommerce/recovery-restore/service.ts; src/woocommerce/recovery-restore/routes.ts; scripts/test-arch053-recovery-restore-postgres.mjs` | KEEP the two deliberate eligibility reads; preserve bounded original SQL/Prisma identifiers in error diagnostics. Replace reduced schema setup in the restore fixture/runner with canonical migrations, not another local schema. |

**Exact new implementation/test paths (not baseline files claimed to exist):**

- `tests/integration/woocommerce/consent/arch055-duplicate-and-selection.postgres.test.ts`
- `tests/integration/woocommerce/recovery-restore/arch055-revalidation.postgres.test.ts`

**Test registration:** Register the first new file in scripts/test-arch046-woo-consent-postgres.mjs and the second in scripts/test-arch053-recovery-restore-postgres.mjs; preserve existing suite lists.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Activity remains authentication + queue durable acceptance, without a new PostgreSQL receipt/outbox or business-state write. Distinguish authentication/database failure from Redis connection/publication failure; preserve original cause and relevant redacted provider details. Keep the post-add retained-job check and downstream idempotency semantics.

2. Consent remains an atomic current-decision/evidence transaction. After principal validation and event-key coordination, check immutable existing evidence before acquiring the recipient advisory lock. An exact retry returns the original acknowledgement and must never restore a grant after a later REVOKE or clear authoritative STOP. A new event still acquires recipient coordination before recipient reads/writes and preserves the canonical triggers.

3. Adopt ADR-05 for recovery-selection GET: committed snapshot display plus revision, not outbound permission. Remove recipient advisory/FOR UPDATE locking from GET only. Keep transaction-local principal checks and existing Shop coordination; POST retains recipient locks, revision policy and STOP/merchant-suppression rules.

4. Do not assume API recipient advisory keys and Background STOP keys are identical. Preserve the Shop-level coordination identified in the report. Do not introduce a new cross-service locking scheme.

5. Restore retains both eligibility reads and confirmed offer evidence; do not wrap it in a repeatable snapshot that prevents the later-state check. Convert its hand-built reduced-schema runner to canonical migrations with appropriate fixtures.

6. Keep validation and public v1 contracts unchanged. Preserve original handled conflict causes in consent/selection and safe structured Prisma/SQL identifiers in restore diagnostics without logging tokens, coupons or customer payloads.

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

- [ ] Refactor duplicate consent and read-only selection branches separately from mutation code.
- [ ] Correct activity stage classification and error preservation.
- [ ] Extend existing migrated races for late STOP/REVOKE, credential rotation, concurrent GETs and stale POST.
- [ ] Run restore races against canonical migrations, including completion/generation/lifetime changes between the two reads.
- [ ] Record source-level and actual SQL counts for fresh, duplicate, GET and failure paths.

## Interfaces / Contracts

Preserves published consent, recovery selection, activity and restore v1 contracts. The snapshot-display policy is an ARCH-055 decision; no merchant response field or STOP scope changes.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

None. The source baseline is context, not a fabricated dependency on historical review evidence.

## Enables

- `ARCH-055-API-009`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Consent duplicate path drops one recipient-lock query without touching permission state.
- [ ] Selection GET no longer takes recipient write-style locks; POST/final send remain authoritative.
- [ ] Real Background STOP compatibility is preserved and included in terminal integrated scenarios.
- [ ] Restore can observe a disqualifying state change after offer resolution.
- [ ] No new external call occurs inside a database transaction and queue acceptance semantics are unchanged.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| B01 | Accepted GRANT retried after REVOKE and after real-equivalent STOP | Acknowledges historical evidence without changing current permission/STOP; duplicate path omits recipient lock. |
| B02 | Concurrent status GET and selection POST/STOP/reconnect | GET is a committed snapshot; stale POST still conflicts and final consent guard remains authoritative. |
| B03 | Authentication Prisma failure; Redis readiness failure; retained-job conflict | Correct stage and original redacted cause; no new PostgreSQL business writes. |
| B04 | Recovery completes or installation rotates between restore evidence reads | No restoration returned after failed final check; canonical constraints exercised. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npm run test:arch035-woo-activity:unit`
- [ ] `npm run test:arch035-woo-activity:redis`
- [ ] `npm run test:arch046-woo-consent:unit`
- [ ] `npm run test:arch046-woo-consent:postgres`
- [ ] `npm run test:arch046-woo-selection:unit`
- [ ] `npm run test:arch053-recovery-restore:postgres`
- [ ] `npm run typecheck`
- [ ] `git diff --check`
- [ ] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

The existing source tests and the report are not a substitute for executing the changed migrated runners. Do not alter docs/decisions/**/_index.md or reopen ARCH-046/053 tasks.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report

### Status

Blocked. Required unit, Redis, canonical consent/restore PostgreSQL and typecheck checks pass. Lint has one unrelated existing failure at `src/merchant/support/routes.ts:75`; required M03 paired measurements remain outstanding.

### Files Changed

- `src/woocommerce/activity/routes.ts`
- `src/woocommerce/activity/redis-producer.ts`
- `src/woocommerce/consent/service.ts`
- `src/woocommerce/recovery-selection/service.ts`
- `src/woocommerce/recovery-restore/routes.ts`
- `scripts/test-arch046-woo-consent-postgres.mjs`
- `scripts/test-arch053-recovery-restore-postgres.mjs`
- `tests/unit/woocommerce/activity/routes.test.ts`
- `tests/integration/woocommerce/consent/races.postgres.test.ts`
- `tests/integration/woocommerce/consent/arch055-duplicate-and-selection.postgres.test.ts`
- `tests/integration/woocommerce/recovery-restore/service.postgres.test.ts`
- `tests/integration/woocommerce/recovery-restore/arch055-revalidation.postgres.test.ts`

### Work Completed

- Consent event handling checks immutable evidence after event-key coordination and before the recipient advisory lock. Exact replay returns the prior acknowledgement without restoring later REVOKE/STOP state; new evidence still takes recipient coordination.
- Recovery-selection GET avoids recipient advisory and row-level write locks; mutation retains the existing locking path.
- Activity failures distinguish authentication/database and Redis connection/publication stages. Bounded diagnostics retain safe error code/cause details and redact connection URLs; Redis error events are attached as causes to readiness failures. Queue acceptance and retained-job verification were not intentionally changed.
- Restore diagnostics preserve bounded safe Prisma/SQL identifiers and causes. The restore runner deploys canonical migrations in its disposable database, and its fixture uses canonical schema fields/constraints.
- Added the exact named consent/selection PostgreSQL regression file and registered it in the consent runner. Added the named restore revalidation test to the restore runner.

### Validation Results

- `npm run test:arch035-woo-activity:unit`: passed, 25/25 tests.
- `npm run test:arch035-woo-activity:redis`: passed, 2/2 disposable Redis/BullMQ tests; runner cleanup completed.
- `npm run test:arch046-woo-consent:unit`: passed, 6/6 tests.
- `npm run test:arch046-woo-selection:unit`: passed, 3/3 tests.
- `npm run test:arch046-woo-consent:postgres`: all 68 canonical migrations applied and 13/13 tests passed; runner cleanup completed.
- `npm run test:arch053-recovery-restore:postgres`: all 68 canonical migrations applied and 2/2 tests passed; runner cleanup completed.
- `npm run typecheck`: passed after Prisma Client generation.
- `npm run lint`: one unrelated existing `no-empty` error remains at `src/merchant/support/routes.ts:75`; task-local findings were corrected.
- `git diff --check`: passed.
- M03 baseline/candidate SQL, affected-row, timing, retry and invocation measurements remain outstanding. Existing ARCH-046 counters are not a substitute. No production p95 or capacity inference is made.

### Worktree and Git Evidence

- Prepared launcher packet accepted: task `ARCH-055-API-002`, executor `copilot`, attempt 1, status `in_progress`, dependency gate passed.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-002`, branch `task/ARCH-055-API-002`. Launcher claim commit: `6e3b37698b72f31f747b4f33d21de952b28341fc`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-002`, branch `task/ARCH-055-API-002`, final implementation HEAD `a96bc83d0fd4715d73f575858a5b684d2d489552`, clean and published to `origin/task/ARCH-055-API-002`.
- Prepared Database submodule pin: `7c377282aa5819b3008b7d7f3018f44f4161523e`; no schema/migration edits made.
- Implementation commit `903be9f` was not changed or rewritten during this resume; its task branch remains published. The parent task/report branch was clean at `a80d08a40` before this report update. Publish this report update only to the mirrored parent `task/ARCH-055-API-002` branch. No main merge/push was performed.

### Deviations

- Fixture/type corrections were made within the task's named implementation/test paths. No schema or public contract changes were made. Task lifecycle remains `blocked` because M03 measurement evidence is unavailable; the unrelated lint failure is recorded separately.

### Assumptions

The uploaded source snapshot is the design baseline, not proof of current remote state. Reconcile only relevant drift on the real launcher baseline; return contract-changing drift to the architect.

### Unresolved Issues

- M03 paired before/after SQL and affected-row measurements remain outstanding; existing consent benchmark counters cover a different task/profile and cannot stand in for M03 evidence.
- Full lint still reports the unrelated existing `src/merchant/support/routes.ts:75` `no-empty` finding; this file is outside the task edit map and remains unchanged.
- Unit, Redis, consent PostgreSQL, restore PostgreSQL, typecheck and diff-check validations passed. Task remains blocked pending M03 evidence.

### Architectural Concerns

Report ownership, schema, contract, external dependency, new index/infrastructure or transaction-boundary gaps here. Do not expand scope silently.

## Architect Review

### Review Status

Pending.

### Review Notes

Implementation report updated after validation; architect review is pending. Task remains blocked pending M03 paired measurement evidence.

### Reviewed Files

Implementation commits `903be9f` and `a96bc83` are submitted on the task branch for review when the measurement gate is satisfied.

### Validation Reviewed

Unit, Redis, canonical consent/restore PostgreSQL, typecheck and diff-check results are recorded above; M03 paired measurements remain outstanding.

### Architecture Conformance

To be assessed against ARCH-055 and this task's frozen contract.

### Follow-up

Only the authorised review may accept this task and promote dependants.
