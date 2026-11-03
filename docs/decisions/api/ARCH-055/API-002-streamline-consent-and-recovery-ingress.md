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
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-03
---

# ARCH-055-API-002: Streamline consent and recovery ingress without weakening STOP

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 2. API-owned workflow / forward-migration contract; supersedes definition revision 1 without claiming an implementation attempt.

**Definition state:** materialised and claimed. The launcher prepared the dedicated parent and implementation worktrees, passed the dependency gate, and recorded Attempt 1 for executor `copilot`.

## Objective

Keep the recovery-ingress safety boundary intact while separating duplicate/read-only work from mutation locking and retaining original database/queue errors.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E03`, `E04`, `E05`, `E06`, `E08`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-api`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `src/woocommerce/activity/`
- `src/woocommerce/consent/`
- `src/woocommerce/recovery-selection/`
- `src/woocommerce/recovery-restore/`
- `tests/unit/woocommerce/activity/`
- `tests/unit/woocommerce/consent/`
- `tests/unit/woocommerce/recovery-selection/`
- `tests/unit/woocommerce/recovery-restore/`
- `tests/integration/woocommerce/consent/`
- `tests/integration/woocommerce/recovery-restore/`
- `scripts/test-arch046-woo-consent-postgres.mjs`
- `scripts/test-arch053-recovery-restore-postgres.mjs`
- `src/merchant/support/installation.ts [read-only dependency; ARCH-055-API-008 owns changes]`

### Exact edit map — definition revision 2

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

## Completion Report — submitted Attempt 1

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

## Completion Report — Attempt 2

### Status

Blocked. The B04 installation-rotation interleaving is implemented and passed the canonical restore PostgreSQL suite (2/2, all 68 migrations). The M03 harness completed candidate-only assertions for all three profiles with two warm-ups and five recorded samples each, but the required paired baseline `fa2a857` comparison did not complete. Do not use the candidate-only timing output as paired evidence.

### Rework

- Added test-local Prisma SQL/query and transaction observation for duplicate replay, new event for the same recipient, and recovery-selection GET in `tests/integration/woocommerce/consent/arch055-duplicate-and-selection.postgres.test.ts`.
- Added state/evidence snapshots and assertions for affected target rows, lock counts, SQL shapes, transaction-control statements, retries, and external invocations. The measurement clock is `2026-11-02T12:00:00.000Z`; consent evidence remains append-only, so samples use isolated fixtures in the disposable database.
- Added opt-in baseline/candidate execution to `scripts/test-arch046-woo-consent-postgres.mjs`, archiving the pinned baseline into a temporary directory and running the same M03 test without changing baseline history.
- The existing restore scenario covers a separate-connection installation credential rotation during offer resolution and verifies final denial for the original principal. Its test title now explicitly names credential rotation.

### Validation Results

- Candidate-only M03 profile test: passed its three profiles and emitted seven sample records per profile (two warm-ups and five recorded samples). This run is not a paired comparison and does not resolve Finding 1.
- Paired M03 runner: not completed. Earlier runner attempts failed with Prisma `P1001` against the published disposable PostgreSQL port; one invocation hung because TCP `psql` lacked the disposable password. The runner was corrected to probe PostgreSQL TCP readiness and pass `PGPASSWORD` to its TCP `psql` calls, but no successful post-correction paired result was captured.
- Restore PostgreSQL suite after adding credential rotation: passed 2/2 with all 68 canonical migrations, as recorded during this attempt. No restore logic changed in the final title-only edit.
- The changed M03 TypeScript test and runner reported no VS Code diagnostics. `git diff --check` passed before the final runner readiness/password edits; terminal execution became unavailable before those final edits could receive an executable check.

### Remaining Work

- Re-run `ARCH055_M03_COMPARE_BASELINE=1 npm run test:arch046-woo-consent:postgres` from the implementation worktree. Confirm both baseline and candidate complete every profile with two warm-ups and five recorded samples, then retain raw samples and report descriptive min/median/max.
- Run the canonical consent PostgreSQL suite, restore PostgreSQL suite, typecheck, and `git diff --check` after the runner corrections. Report any infrastructure failure without inferring paired values.
- Keep the task in progress; do not promote API-009 or SYSTEM-TEST-001 until the paired evidence is complete and reviewed.

## Architect Review

### Decision — Changes Requested, Attempt 1, 3 November 2026

Not accepted. Return to Ready for the next normal claim, preserving Attempt 1 and clearing executor/claimed_at. Missing task-owned evidence is actionable rework, not an unresolved architecture or infrastructure dependency. No downstream promotion. The submitted blocked report above is historical; this decision supersedes its lifecycle instructions.

### Findings

1. **P2 — M03 mandatory paired measurements remain missing.** Passing correctness tests and pre-existing ARCH-046 counters do not establish the required before/after SQL and affected-row result. Use the existing named consent integration file/runner; no new production telemetry or benchmark framework is required. Compare prepared baseline `fa2a857` with candidate `a96bc83d0fd4715d73f575858a5b684d2d489552` (or the final correction SHA) against identical disposable canonical schema and restored fixtures. Measure separately: exact committed consent replay, new event for the same recipient, and recovery-selection GET. Apply the fixed comparison procedure in `docs/architecture/ARCH-055/task-definition-contract.md`: two discarded warm-ups and five recorded samples per version/profile; fixture restoration outside each measured window; warmed client; normalized emitted SQL plus transaction-control statements, client calls, returned/affected rows, timings, retries and external invocations. Prove replay removes the recipient-lock statement without changing permission/STOP, new events retain atomic coordination/evidence, and GET omits recipient advisory/FOR UPDATE. Preserve raw samples and descriptive min/median/max; no production percentile claim. Instrument both versions identically in isolated review/test checkouts; never rewrite baseline history or run baseline tests in the shared checkout. If actual incompatibility occurs, record the exact failing baseline invocation instead of inferring a numeric comparison.
2. **P2 — B04 installation-rotation interleaving is not covered.** `tests/integration/woocommerce/recovery-restore/arch055-revalidation.postgres.test.ts` mutates completion, recovery generation and lifetime, but never rotates the installation between the two reads. Existing restore fixtures have initial credential versions; consent's reconnect test exercises a different operation. Add a scenario to the existing restore file where the first read succeeds, a separate connection commits installation credential rotation during offer resolution, and the second read rejects restoration for the original principal. Keep canonical constraints and prove offer resolution was reached, so an initially ineligible fixture cannot give a false pass.

### Review and validation

- Inspected implementation changes from prepared baseline `fa2a857` through `a96bc83`: consent replay checks immutable evidence after event coordination and before recipient coordination; only selection GET drops recipient advisory/FOR UPDATE; mutation retains locking; both restore eligibility reads remain. Queue retained-job verification remains unchanged. No additional runtime correctness finding established in this review.
- Independently ran activity unit **25/25**, consent unit **6/6**, and selection unit **3/3**; `git diff --check` passed.
- Supplied Redis **2/2**, consent PostgreSQL **13/13**, restore PostgreSQL **2/2**, and typecheck results are recorded as executor evidence; not independently rerun for this review. The unrelated existing support-route lint error is not the reason for Changes Requested.
- No M03 measurements were captured by this review. Do not infer them from source or test counts.
- Canonical task route/worktrees inspected; no implementation changes, consumer pins, production operations or main merge performed.

### Task-definition reconciliation and next step

Removed duplicated Completion Report material that had been interleaved into Objective/Context/Scope, restoring the original authorized scope lists and deterministic edit map from the claim revision. Retained the submitted Completion Report and its validation limitations as history. No new files, production behavior or wider scope is authorized or needed. Capture M03 and B04 in the existing allowed test paths, reconcile the Work Items/Acceptance Criteria, and submit the next attempt on the same branch pair. API-009 and SYSTEM-TEST-001 remain gated on acceptance.


### Recovery decision — Changes Requested, stranded Attempt 2, 3 November 2026

Attempt 2 is not accepted. Preserve its report above as historical executor evidence, including its validation limitations. Its statement to keep the task in progress is superseded by this recovery decision. Return the same task to Ready, clear executor/claimed_at, and preserve `attempt: 2`; only the normal prepared launcher may claim Attempt 3.

The reported terminal loss and explicit remaining-work handoff establish an interrupted attempt rather than completed validation. Inspection found the parent report uncommitted and three uncommitted task-owned implementation files in the canonical dedicated implementation worktree: `scripts/test-arch046-woo-consent-postgres.mjs`, `tests/integration/woocommerce/consent/arch055-duplicate-and-selection.postgres.test.ts`, and `tests/integration/woocommerce/recovery-restore/arch055-revalidation.postgres.test.ts`. Preserve and publish those changes on the existing mirrored task branches before rerunning preparation; do not discard them, rewrite baseline history, or infer a passing measurement. The repository owner performs implementation checkpoint publication; this architect recovery performs no implementation edits or acceptance.

The route-only launcher confirms the canonical primary root, dedicated parent/implementation paths and mirrored `task/ARCH-055-API-002` branch already recorded above. Route-only output is topology evidence, not a prepared execution packet or a claim. Start new implementation only after successful normal `--prepare`.

The Attempt 1 Findings remain the correction contract: finish the paired M03 baseline/candidate evidence and verify B04 credential rotation with the canonical migrated runner. The stranded diff adds candidate/baseline measurement scaffolding, TCP readiness/password fixes, and a credential-rotation scenario, but no new executable validation was performed by this recovery. Re-run the required changed-runner checks, retain actual raw samples and descriptive summaries, and reconcile Work Items/Acceptance Criteria/Validation honestly before review. Candidate-only assertions cannot satisfy paired evidence. API-009 and SYSTEM-TEST-001 remain pending; no architecture scope, dependency or implementation contract changes are authorized.
