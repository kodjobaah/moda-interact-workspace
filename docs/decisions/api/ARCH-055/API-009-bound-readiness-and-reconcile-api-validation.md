---
id: ARCH-055-API-009
architecture_id: ARCH-055
title: Bound readiness and reconcile API validation entrypoints
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 60
executor: codex
claimed_at: 2026-11-04T00:21:26Z
attempt: 1
depends_on:
- ARCH-055-API-001
- ARCH-055-API-002
- ARCH-055-API-003
- ARCH-055-API-004
- ARCH-055-API-005
- ARCH-055-API-006
- ARCH-055-API-007
- ARCH-055-API-008
enables:
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-04
---

# ARCH-055-API-009: Bound readiness and reconcile API validation entrypoints

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 2. API-owned workflow / forward-migration contract; supersedes definition revision 1 without claiming an implementation attempt.

**Definition state:** materialised in the canonical parent task worktree and branch. All eight explicit API dependencies are Complete, including API-004 at Attempt 3. The task is Ready at Attempt 0 with no executor or claim; no implementation worktree has been created.

## Objective

Finish the API's operational acceptance boundary: finite, bounded readiness work and one correctly wired migrated integration entrypoint for the accepted functional changes.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E60`, `E61`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-api`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `src/database.ts`
- `src/server.ts`
- `src/runtime-config.ts`
- `src/index.ts [readiness composition only]`
- `tests/unit/http/server.test.ts`
- `tests/unit/runtime-config.test.ts [if present; inspect exact path before editing]`
- `tests/integration/http/ [new bounded-readiness cases]`
- `scripts/test-arch055-readiness-postgres.mjs [new]`
- `package.json [integration scripts only]`
- `scripts/test-woocommerce-installation-postgres.mjs [final migration/fixture wiring]`
- `scripts/test-arch053-recovery-restore-postgres.mjs [final wiring]`
- `scripts/test-arch054-ai-response-delay-postgres.mjs [existing runner registration]`
- `scripts/test-arch041-cross-domain-postgres.mjs [accepted recovery-read registration]`
- `scripts/test-arch041-billing-postgres.mjs [accepted purchase-history/commands registration]`

Required new paths (only these are allowed to be absent at startup):

- `scripts/test-arch055-readiness-postgres.mjs`
- `tests/integration/http/readiness.postgres.test.ts`

Additional explicit registration/module paths for this revision:

- `src/readiness-probe.ts`
- `scripts/test-woocommerce-installation-postgres.mjs`

### Exact edit map — definition revision 2

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `src/database.ts` | CREATE one dedicated readiness-only PrismaClient per process in addition to existing business client. Derive its URL without logging it; preserve all existing non-timeout/security arguments and override connection_limit=1, pool_timeout=1, connect_timeout=1, socket_timeout=1. No extra driver package. probe uses only parameter-free SELECT1. Disconnect both clients only on normal shutdown; never disconnect business client on readiness timeout. |
| `src/readiness-probe.ts; src/server.ts` | CREATE single-flight adapter around that one delegate. inFlight cleared only by actual delegate settlement, never observer HTTP timeout. Concurrent requests await same promise; new request after settlement starts fresh probe, not cached success. Existing 2000ms observer deadline and liveness response unchanged. |
| `scripts/test-arch055-readiness-postgres.mjs; tests/integration/http/arch055-readiness.postgres.test.ts` | CREATE canonical disposable PG runner and real HTTP failure/recovery suite. Test dedicated pool/query bounds (blocking injected query only in test adapter), network/connect failure, at most1 physical connection/probe, and no business-client shutdown. |
| `scripts/test-woocommerce-installation-postgres.mjs; package.json` | AFTER API-001..008 acceptance, replace old db-push orchestration with calls to the accepted installation/settings canonical runners; preserve all previous suites. Append AI-delay and ARCH-055 readiness runners to test:integration exactly once, plus explicit script keys below. |

**Exact new implementation/test paths (not baseline files claimed to exist):**

- `src/readiness-probe.ts`
- `scripts/test-arch055-readiness-postgres.mjs`
- `tests/unit/http/arch055-readiness-single-flight.test.ts`
- `tests/integration/http/arch055-readiness.postgres.test.ts`

**Test registration:** Add exact script keys test:arch055-installation:postgres, test:arch055-merchant-settings:postgres, test:arch055-readiness:postgres, mapping respectively to node scripts/test-arch055-installation-postgres.mjs, node scripts/test-arch055-merchant-settings-postgres.mjs, node scripts/test-arch055-readiness-postgres.mjs. Preserve all existing script keys.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Liveness remains immediate process-only HTTP with zero DB/config/provider/queue calls. Readiness remains parameter-free SELECT 1 and safe 200/503 at the existing 2,000 ms HTTP deadline; it is not a migration, Redis or business-table audit.

2. Implement ADR-08: at most one unresolved underlying readiness probe per API process, with supported finite acquisition/execution bounds and recovery after outage. Coalesce concurrent requests around that in-flight probe without caching an old success. An HTTP timeout must not clear the in-flight guard while the underlying probe is still pending.

3. Use the pinned Prisma/runtime supported timeout/cancellation mechanism and demonstrate its bounds under real blocked acquisition and execution. Use the dedicated one-connection Prisma6 readiness client and exact connection URL overrides selected below; account for that extra physical connection and its finite lifecycle. Never disconnect the shared business client per readiness failure. If existing configuration cannot enforce the bound, return the specific infrastructure requirement for architect-owned Gateway scope rather than guessing settings.

4. Add the existing AI-delay migrated suite to aggregate integration; ensure accepted installation/category/restore/recovery/history fixtures use canonical migrations, not reduced hand-made schemas or db push where guards matter. Do not author another generic test framework or rewrite unrelated suites.

5. Reconcile shared package.json/runner edits after ARCH-055-API-001..008 acceptance, preserving every accepted suite. This is why the task is pending behind those owners; it is not a separate task per test. No implementation task depends on ARCH-055-SYSTEM-TEST-001.

6. Capture real HTTP/pool recovery, emitted SQL counts, outstanding work bounds and resource cleanup. Reuse existing structured logger/framework instrumentation. Keep original probe failures internally, with safe public output and no credentials in logs.

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

- [ ] Implement bounded underlying readiness work and deterministic unit tests.
- [ ] Create the focused migrated PostgreSQL/HTTP runner using disposable pg17+pgvector.
- [ ] Register all accepted focused runners and the previously omitted AI-delay suite in aggregate integration.
- [ ] Run API typecheck/build/full integration and classify any unchanged documented baseline failures without weakening new acceptance.

## Interfaces / Contracts

Existing readiness HTTP contract is unchanged. Any introduced probe option must be internal/server-controlled, tested against the pinned runtime and listed in the completion report; no deployed pool limit or timeout is assumed from the static review.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

New module `src/readiness-probe.ts`:
```ts
export declare function createSingleFlightReadinessProbe(
  delegate: () => Promise<void>,
): () => Promise<void>;
```
No constructor-side query or timer. Preserve original rejection cause. Observer timeouts remain in server.ts. Prisma6 connector URL option names were checked against official v6 documentation; this is a selected design, not runtime proof. Validate against pinned6.19.3 and the accepted deployment topology; unsupported pooling/timeout behavior is a blocked return, not permission to invent infrastructure settings. Existing application DB URL remains unchanged. Do not claim this dedicated-client probe measures free capacity in the business pool.

## Dependencies

- `ARCH-055-API-001` must have `status: complete` and an accepted review.
- `ARCH-055-API-002` must have `status: complete` and an accepted review.
- `ARCH-055-API-003` must have `status: complete` and an accepted review.
- `ARCH-055-API-004` must have `status: complete` and an accepted review.
- `ARCH-055-API-005` must have `status: complete` and an accepted review.
- `ARCH-055-API-006` must have `status: complete` and an accepted review.
- `ARCH-055-API-007` must have `status: complete` and an accepted review.
- `ARCH-055-API-008` must have `status: complete` and an accepted review.

## Enables

- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Twenty or more concurrent timed-out health requests do not leave twenty independent probes outstanding; per-process outstanding probe count stays <=1.
- [ ] Probe acquisition/execution has a documented measured finite bound, and successful readiness resumes after database recovery without restarting/disconnecting the business client.
- [ ] Liveness remains available during DB failure and performs zero probes.
- [ ] Aggregate integration includes all accepted functional suites and canonical migration coverage; no silent skips or reduced-schema substitution.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| I01 | 20+concurrent readiness requests with held delegate | One underlying probe; all observer deadlines bounded; no early guard clear or old-success cache. |
| I02 | Actual dedicated pool held or test query pg_sleep>timeout; connection failure then restoration | Underlying failure settles within asserted5s safety ceiling; next request recovers, business client unaffected. 5s is acceptance ceiling, not configured SQL timeout. |
| I03 | Database outage with /health/live | Immediate200 and no DB/config/provider/queue call. |
| I04 | Shutdown after success, outage and in-flight deadline | Both clients cleaned once, no leaked resources/secret logs. |
| I05 | Run aggregate suite on current accepted migration pin | Every retained suite and new registration included; no db-push/reduced schema substitutes. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npx tsx --test tests/unit/http/server.test.ts tests/unit/http/arch055-readiness-single-flight.test.ts`
- [ ] `node scripts/test-arch055-readiness-postgres.mjs`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `npm run test:integration`
- [ ] `git diff --check`
- [ ] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

This task owns final package.json integration-script changes so the functional tasks do not race to rewrite the same long aggregate command. It includes readiness implementation plus the directly associated operational acceptance wiring, not unrelated telemetry or infrastructure.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report

### Status

Implementation not started. The task is Ready at Attempt 0 and awaits its normal launcher claim.

### Files Changed

None.

### Work Completed

None. Task definition only.

### Validation Results

Not run. Record each command, outcome, fixture/migration identity, actual SQL/rows, concurrency schedule and resource cleanup here.

### Worktree and Git Evidence

Parent task worktree is materialised at `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-009` on `task/ARCH-055-API-009`. No implementation worktree or attempt claim was created for this promotion.

### Deviations

None authorised.

### Assumptions

The uploaded source snapshot is the design baseline, not proof of current remote state. Reconcile only relevant drift on the real launcher baseline; return contract-changing drift to the architect.

### Unresolved Issues

Required implementation/validation has not started. Do not pre-check acceptance items. The launcher may claim Attempt 1 after the canonical task branch is published.

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

### Mechanism source (not application validation)

Prisma ORM6 PostgreSQL connector documentation, checked2 November2026: `https://www.prisma.io/docs/orm/v6/overview/databases/postgresql` documents connection_limit, connect_timeout, pool_timeout and socket_timeout. These support the selected explicit settings; they do not prove deployed pooler/network behavior or the runtime recovery assertion. Do not use v7 driver-adapter instructions for this pinned6.19.3 repository.

## Dependency Promotion — 2026-11-04

ARCH-055-API-001 through API-008 are Complete. In particular, API-004 is Accepted and Complete at Attempt 3. API-009 is promoted from Pending to Ready at Attempt 0 with executor and claim cleared. This promotion does not start implementation or create an implementation worktree. ARCH-055-SYSTEM-TEST-001 remains Pending until API-009 is Complete.
