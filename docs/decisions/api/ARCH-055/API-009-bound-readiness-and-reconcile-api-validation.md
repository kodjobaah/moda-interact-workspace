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
status: review
priority: 60
executor: null
claimed_at: null
attempt: 2
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

**Definition revision:** 3. Adds a server-side PostgreSQL execution bound to readiness; it supersedes revision 2 for the unresolved readiness timeout requirement. API-008 remains complete and unchanged.

**Definition state:** materialised in the canonical parent task worktree and branch. All eight explicit API dependencies are Complete. Attempt 1 was returned with Changes Requested; the revision-3 server-side timeout amendment was implemented in Attempt 2. Attempt 2 is submitted for architect review with the claim cleared. API-008 remains complete and unchanged.

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
| `src/database.ts` | CREATE one dedicated readiness-only PrismaClient per process in addition to existing business client. Derive its URL without logging it; preserve all existing non-timeout/security arguments and override connection_limit=1, pool_timeout=1, connect_timeout=1, socket_timeout=1. Preserve any existing PostgreSQL `options` value and append the server-side per-session `statement_timeout=500ms` startup setting through Prisma's supported `options` URL argument. The server statement timeout must precede the 1-second socket timeout so server work is canceled before the client abandons the query. No extra driver package or global PostgreSQL setting. probe uses only parameter-free SELECT1. Disconnect both clients only on normal shutdown; never disconnect business client on readiness timeout. |
| `src/readiness-probe.ts; src/server.ts` | CREATE single-flight adapter around that one delegate. inFlight cleared only by actual delegate settlement, never observer HTTP timeout. Concurrent requests await same promise; new request after settlement starts fresh probe, not cached success. Existing 2000ms observer deadline and liveness response unchanged. |
| `scripts/test-arch055-readiness-postgres.mjs; tests/integration/http/arch055-readiness.postgres.test.ts` | CREATE canonical disposable PG runner and real HTTP failure/recovery suite. Assert the dedicated session's statement_timeout, then execute a real long query and prove PostgreSQL cancels it before the Prisma promise settles; verify no active orphan query remains before the next probe. Also test dedicated pool/query bounds, network/connect failure, at most1 physical connection/probe, recovery, and no business-client shutdown. |
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

- [x] Bound actual PostgreSQL execution server-side before the client socket timeout; prove cancellation with the pinned Prisma runtime and deterministic tests.
- [x] Implement bounded HTTP observer/single-flight behavior and deterministic unit tests.
- [x] Create the focused migrated PostgreSQL/HTTP runner using disposable pg17+pgvector.
- [x] Register all accepted focused runners and the previously omitted AI-delay suite in aggregate integration.
- [x] Run API typecheck/build/full integration and classify any unchanged documented baseline failures without weakening new acceptance.

## Interfaces / Contracts

Existing readiness HTTP contract is unchanged. The dedicated readiness URL must preserve its existing `options` value and append the internal server-controlled PostgreSQL `statement_timeout=500ms` using Prisma's supported `options` URL argument. Retain connection_limit=1, pool_timeout=1, connect_timeout=1 and socket_timeout=1 (seconds). Test that PostgreSQL actually applies the setting and cancels an overlong statement before the socket timeout; do not infer backend cancellation from a rejected Prisma promise. If the accepted connection topology drops or ignores the startup option, stop with the observed evidence and requested infrastructure requirement. No global PostgreSQL setting or business-client URL change is authorized.

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

- [x] Twenty or more concurrent timed-out health requests do not leave twenty independent probes outstanding; per-process outstanding probe count stays <=1.
- [x] Probe acquisition and server-side execution each have documented measured finite bounds; an overlong statement is canceled before client socket timeout, and readiness resumes without restarting/disconnecting the business client.
- [x] Liveness remains available during DB failure and performs zero probes.
- [x] Aggregate integration includes all accepted functional suites and canonical migration coverage; no silent skips or reduced-schema substitution.
- [x] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [x] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [x] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 3

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| I01 | 20+concurrent readiness requests with held delegate | One underlying probe; all observer deadlines bounded; no early guard clear or old-success cache. |
| I02 | Actual dedicated pool held; test query `pg_sleep(8)`; connection failure then restoration | Pool acquisition settles within the configured pool timeout. PostgreSQL applies `statement_timeout=500ms`, cancels the long query, and the server-side active query is gone before the client promise rejects at `socket_timeout=1s`. A subsequent real readiness probe succeeds; the business client remains unaffected. No accumulation of orphan backend queries. |
| I03 | Database outage with /health/live | Immediate200 and no DB/config/provider/queue call. |
| I04 | Shutdown after success, outage and in-flight deadline | Both clients cleaned once, no leaked resources/secret logs. |
| I05 | Run aggregate suite on current accepted migration pin | Every retained suite and new registration included; no db-push/reduced schema substitutes. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [x] `npx tsx --test tests/unit/http/server.test.ts tests/unit/http/arch055-readiness-single-flight.test.ts`
- [x] `node scripts/test-arch055-readiness-postgres.mjs` — proves PostgreSQL-side cancellation and no orphan query with Prisma 6.19.3.
- [x] `npm run typecheck`
- [x] `npm run build`
- [x] `npm run test:integration`
- [x] `git diff --check`
- [x] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [x] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

This task owns final package.json integration-script changes so the functional tasks do not race to rewrite the same long aggregate command. It includes readiness implementation plus the directly associated operational acceptance wiring, not unrelated telemetry or infrastructure.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report — Attempt 1, 2026-11-04

### Status

Blocked on the required aggregate integration gate and final migrated readiness rerun. Implementation `301165eb5dd969cde1338d5b363aee963d7e08ea` is published on API `task/ARCH-055-API-009`. Attempt 1 is preserved and the claim is cleared. No downstream task is promoted.

### Implementation and measured boundaries

- `src/database.ts` creates a dedicated readiness Prisma 6 client. The URL keeps existing non-timeout options and sets connection_limit, pool_timeout, connect_timeout and socket_timeout to 1. The business client retains its original URL. Readiness submits parameter-free SELECT 1. Shutdown attempts both disconnects.
- `src/readiness-probe.ts` and `src/server.ts` share the actual pending delegate across requests and clear the guard only on settlement. The 2,000 ms HTTP observer deadline and live/ready response shapes are preserved. Shared readiness logs keep the original safe error message, code and nested cause with URLs redacted.
- The former installation runner delegates to the accepted installation and merchant-settings migration runners. All five prior fixture suites remain registered through those runners, plus the accepted installation races and category coherence cases. The aggregate preserves its prior commands and adds AI-delay and readiness exactly once. The existing restore, recovery-read, purchase-history and billing registrations already include their accepted tests.
- The readiness runner starts a fresh pg17+pgvector container, waits for the final TCP listener, applies the canonical migrations and runs the focused PostgreSQL tests. A test adapter holds the dedicated pool and injects a blocked statement. The HTTP fixture cuts only readiness traffic, preserves the existing business backend PID and measures the stalled handshake through actual delegate settlement.
- The one-second socket timeout bounds the client promise. The deliberately injected eight-second statement remained active on PostgreSQL until it finished. Recovery is asserted after that backend work ends. The test does not demonstrate server-side statement cancellation or capacity in the business pool. Prisma connector option reference: [Prisma v6 PostgreSQL connector](https://www.prisma.io/docs/orm/v6/overview/databases/postgresql).

### Validation

| Check | Observed outcome |
|---|---|
| Focused HTTP and single-flight units | 10 passed. Optional M17 profile ran separately on both versions. 24 timed-out HTTP observers left one delegate pending. A subsequent request still coalesced until settlement. Fresh requests then probed again. |
| M17 comparison | Baseline peak 20 vs candidate peak 1 in every five-sample group. Early release returned 20 HTTP 200s on each version. Held-through-deadline returned 20 HTTP 503s, leaving 20 baseline delegates vs one candidate delegate pending until release. |
| PostgreSQL readiness | Earlier canonical runner revision applied 71 migrations and passed both tests after recovery polling was added. A stricter cleanup assertion initially caught a paused proxy socket. The final test proxy drains handshake bytes and the exact final tests passed 2/2 in the separate pg17+pgvector driver diagnostic without migrations. Final canonical attempts stopped during Prisma migration deployment with a generic schema engine error. The diagnostic is retained separately and does not satisfy the final migrated gate. |
| Pool and connection diagnostic | One tagged physical readiness session under held acquisition. Pool failure 1043.08 ms, socket query failure 1009.36 ms, stalled handshake including delegate settlement 1017.06 ms. Initial outage 12.70 ms, injected backend recovery 8166.89 ms, liveness issued zero probes, both transports closed at shutdown. The test probe is a constant SELECT and affects zero target rows. No wire-level SQL or byte count is claimed for the controlled fake profiles. |
| Shutdown | Unit shutdown after a held observer deadline invokes disconnect once. Real recovered network fixture observes zero remaining sockets after repeated shutdown. |
| Typecheck and build | Passed on Node 24.19.0/npm 11.17.0 with generated Prisma 6.19.3. |
| Lint and whitespace | Changed-file lint and diff checks passed. Repository lint retains the existing Support routes line 75 `no-empty` error. |
| Aggregate integration, first run | Shop brand, installation, settings, REST-read authorization and billing groups passed. The unchanged discount-offers suite then failed five cases after its mapped PostgreSQL endpoint became unreachable. |
| Aggregate integration, serial retry | Shop brand, installation and settings passed. The unchanged REST-read overlap test returned two rejected callbacks where it expects two fulfilled outcomes. This same runner passed 9/9 on the first aggregate run. The retry did not reach the later suites. |
| Standalone follow-up | AI-delay passed 1/1 with canonical migrations. The unchanged discount-offers runner also failed independently. Its Save transaction expired after 29,517 ms against the existing 12,000 ms bound. The remaining standalone loop was stopped while the active runner completed cleanup. |

The differing failures in unchanged runners are observed validation failures, not waived baseline findings. The aggregate still needs a successful run through the complete registration sequence. No existing timeout or fixture contract was loosened.

### Worktree and provenance

- Workspace root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-009`, reused. Implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-009`, created. Both use `task/ARCH-055-API-009`. Shared checkouts were not switched.
- Parent incorporated main at `608f6a06a519df103b21cea55d6327fa806dc13a`. Implementation already included main at task-start `2384bac6cea135d5571bd9f771f9431cfb0c7b45`. Neither remote task branch required a fast-forward. All eight dependencies passed the launcher gate and claim `56ba640ee25c8a816fc99330908992448de6bbd7` was published.
- Recursive sync and initialization passed at Database `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. Migration tree manifest SHA-256 from `git ls-tree -r HEAD prisma/migrations` is `907ab05d3418e60f6862597b7a8e14e54987167f60eafd2d8fe1e99463606f94`.
- The M17 fixture used a temporary archive of task-start source and the locked candidate dependencies. It ran the same server test with `ARCH055_READINESS_MEASURE_VERSION=baseline` and `ARCH055_READINESS_SOURCE_ROOT` set to that archive, then with `ARCH055_READINESS_MEASURE_VERSION=candidate` and no source override. Command in both cases: `npx --no-install tsx --test --test-name-pattern=M17 tests/unit/http/server.test.ts`. Each sample starts a fresh local HTTP runtime, sends 20 requests and releases the held delegate before cleanup. Two warmups were discarded per scenario/version. No live database was loaded for baseline accumulation.

The temporary source archive was removed. Final container inventory showed no readiness, AI-delay or discount-offers containers from the runs, and the last runner had exited. The implementation checkout is clean.

### Retained measurements

Local elapsed times are descriptive.

| M17 case | Baseline min/median/max ms | Candidate min/median/max ms |
|---|---:|---:|
| Early release | 29.85 / 44.73 / 85.31 | 26.53 / 36.76 / 53.88 |
| Held through deadline | 2015.39 / 2019.42 / 2026.66 | 2016.79 / 2018.97 / 2084.24 |

```jsonl
{"profile":"M17","version":"baseline","scenario":"release-before-deadline","warmups":2,"samples":[{"requests":20,"probes":20,"peak":20,"pending":0,"elapsedMs":44.73381900000004,"status":200,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":20,"peak":20,"pending":0,"elapsedMs":29.8485169999999,"status":200,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":20,"peak":20,"pending":0,"elapsedMs":85.31228299999998,"status":200,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":20,"peak":20,"pending":0,"elapsedMs":47.105678000000125,"status":200,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":20,"peak":20,"pending":0,"elapsedMs":34.18605200000002,"status":200,"sql":"not applicable to fake delegate","affectedRows":0}]}
{"profile":"M17","version":"baseline","scenario":"held-through-deadline","warmups":2,"samples":[{"requests":20,"probes":20,"peak":20,"pending":20,"elapsedMs":2019.4204549999995,"status":503,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":20,"peak":20,"pending":20,"elapsedMs":2021.1524659999995,"status":503,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":20,"peak":20,"pending":20,"elapsedMs":2015.393637000001,"status":503,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":20,"peak":20,"pending":20,"elapsedMs":2018.6505510000006,"status":503,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":20,"peak":20,"pending":20,"elapsedMs":2026.6590180000003,"status":503,"sql":"not applicable to fake delegate","affectedRows":0}]}
{"profile":"M17","version":"candidate","scenario":"release-before-deadline","warmups":2,"samples":[{"requests":20,"probes":1,"peak":1,"pending":0,"elapsedMs":53.88422700000001,"status":200,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":1,"peak":1,"pending":0,"elapsedMs":26.525485000000003,"status":200,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":1,"peak":1,"pending":0,"elapsedMs":28.526264999999967,"status":200,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":1,"peak":1,"pending":0,"elapsedMs":37.53506100000004,"status":200,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":1,"peak":1,"pending":0,"elapsedMs":36.76398500000005,"status":200,"sql":"not applicable to fake delegate","affectedRows":0}]}
{"profile":"M17","version":"candidate","scenario":"held-through-deadline","warmups":2,"samples":[{"requests":20,"probes":1,"peak":1,"pending":1,"elapsedMs":2019.188236,"status":503,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":1,"peak":1,"pending":1,"elapsedMs":2084.238854,"status":503,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":1,"peak":1,"pending":1,"elapsedMs":2016.7924789999997,"status":503,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":1,"peak":1,"pending":1,"elapsedMs":2018.9661239999987,"status":503,"sql":"not applicable to fake delegate","affectedRows":0},{"requests":20,"probes":1,"peak":1,"pending":1,"elapsedMs":2017.43808,"status":503,"sql":"not applicable to fake delegate","affectedRows":0}]}
{"profile":"readiness-pool-and-socket","acquireMs":1043.0844579999998,"queryMs":1009.3611509999996,"backendRecoveryMs":8166.8903740000005,"physicalConnections":1,"probeSql":"SELECT 1","affectedRows":0}
{"profile":"readiness-http-outage","outageMs":12.700615000001562,"stalledHandshakeMs":1017.0581980000006,"liveProbes":0,"recovered":true,"socketsAfterShutdown":0}
```

## Attempt 1 validation resolution — 2026-11-04

Submitted for architect review. The final serial `npm run test:integration` on API commit `301165eb5dd969cde1338d5b363aee963d7e08ea` exited 0. This supersedes the earlier aggregate-integration failures and preserves their history.

- The command reached the end of all retained suites, including canonical installation/settings, REST-read authorization, discount offers, cross-domain recovery, billing, Woo consent, Redis/BullMQ, restore, AI-delay and readiness. It recorded 120 Node test passes, zero failures and four explicit opt-in measurement skips (M04/M05, M15, M11–M14 and M03). The separate platform-configuration runner passed 5/5.
- Before the successful aggregate, one retry passed REST-read and discount offers, then stopped at feature-preferences migration deployment. A temporary copy of that runner with a TCP startup check passed 2/2. The final aggregate passed the original tracked runner, so no fixture or timeout change was needed. The temporary copy was removed. The startup experiment does not establish a single cause for all earlier intermittent failures.
- The canonical focused readiness runner also exited 0 separately and the final aggregate repeated its 2/2 result after all 71 migrations. In the aggregate, pool acquisition failure settled in 1027.27 ms, query failure in 1252.39 ms and stalled handshake in 1010.03 ms. One physical readiness session was observed under the held pool. The business backend remained available, liveness issued zero probes and shutdown left zero sockets.
- The injected SQL finished on the backend after 8469.72 ms. The measured client bound is distinct from backend cancellation. The earlier paired M17 evidence and the unchanged repository lint finding remain applicable.
- Final container inventory showed no disposable API test containers. Attempt 1 remains unclaimed and awaits architect review.

```jsonl
{"profile":"readiness-pool-and-socket","acquireMs":1027.271401,"queryMs":1252.3935570000003,"backendRecoveryMs":8469.72139,"physicalConnections":1,"probeSql":"SELECT 1","affectedRows":0}
{"profile":"readiness-http-outage","outageMs":6.045367000000624,"stalledHandshakeMs":1010.0267589999985,"liveProbes":0,"recovered":true,"socketsAfterShutdown":0}
```

## Architect Review

### Review Status

Changes Requested — Attempt 1 (2026-11-04). Return the task to `ready`; no claim was active. Do not promote downstream work.

### Review Notes

The implementation and final aggregate validation were reviewed. One acceptance issue remains: `socket_timeout=1` settles the Prisma client promise, but the test report confirms PostgreSQL continues executing the timed-out statement for about 8.5 seconds. `createSingleFlightReadinessProbe` clears its in-flight guard when the client promise settles, so a later request can start another probe while the prior backend statement is still active. The task and ADR-08 require a finite bound on underlying acquisition/execution and one unresolved underlying probe; the current test waits for backend completion before checking recovery and does not prove a server-side execution bound or cancellation.

Architect amendment for Attempt 2: extend the same API-009 readiness scope with PostgreSQL per-session `statement_timeout=500ms`, passed in the dedicated Prisma 6 connection URL through `options`; preserve/append to existing `options`, all TLS parameters, and the separate business URL. The PostgreSQL server-side timeout must win before the 1-second `socket_timeout`. The real migration-backed test must verify `SHOW statement_timeout`, execute a long-running query, observe PostgreSQL cancel it (SQLSTATE 57014 or equivalent actual driver evidence), confirm the server no longer reports the test query active before the Prisma promise settles, and then prove a fresh readiness probe succeeds. Test connection topology limitations explicitly. If server cancellation is not observed, stop and return measured evidence plus the required infrastructure change; never state that a client socket timeout alone bounds database work. Keep the 2,000 ms HTTP deadline and existing single-flight behavior. This amendment is confined to API-009 and does not reopen API-008.

This amendment follows Prisma ORM v6's documented PostgreSQL `options` connection URL argument and PostgreSQL 17's per-session `statement_timeout` behavior. These references justify testing the selected mechanism; they do not replace the required runtime and connection-topology proof: [Prisma ORM v6 PostgreSQL connector](https://www.prisma.io/docs/orm/v6/overview/databases/postgresql), [PostgreSQL 17 client connection defaults](https://www.postgresql.org/docs/17/runtime-config-client.html#GUC-STATEMENT-TIMEOUT).

### Reviewed Files

- `src/database.ts`
- `src/readiness-probe.ts`
- `src/server.ts`
- `tests/unit/http/server.test.ts`
- `tests/unit/http/arch055-readiness-single-flight.test.ts`
- `tests/integration/http/arch055-readiness.postgres.test.ts`
- `scripts/test-arch055-readiness-postgres.mjs`
- `scripts/test-woocommerce-installation-postgres.mjs`
- `package.json`

### Validation Reviewed

Reviewed the reported typecheck/build, focused unit tests, standalone readiness diagnostic, targeted lint, diff check, and final aggregate integration result (120 Node tests passed; four opt-in measurement skips), plus 5/5 platform-configuration tests. These results were reported by the implementer and not rerun during review. The integration aggregate passed, but it does not resolve the backend-execution-bound finding above.

### Architecture Conformance

The dedicated client, single-flight observer behavior, response contract, test registration and business-client isolation conform to the original API-009 scope. ADR-08's finite backend-execution bound is not yet demonstrated because the server continues work after the client socket timeout. The revision-3 amendment assigns the bounded server-side setting and proof to this same task; API-008 remains unchanged.

### Follow-up

Continue on the same mirrored task branches at Attempt 2 using definition revision 3. `ARCH-055-SYSTEM-TEST-001` remains gated pending acceptance of its implementation dependencies.

### Mechanism source (not application validation)

Prisma ORM6 PostgreSQL connector documentation, checked2 November2026: `https://www.prisma.io/docs/orm/v6/overview/databases/postgresql` documents connection_limit, connect_timeout, pool_timeout and socket_timeout. These support the selected explicit settings; they do not prove deployed pooler/network behavior or the runtime recovery assertion. Do not use v7 driver-adapter instructions for this pinned6.19.3 repository.

## Dependency Promotion — 2026-11-04

ARCH-055-API-001 through API-008 are Complete. In particular, API-004 is Accepted and Complete at Attempt 3. API-009 was promoted to Ready at Attempt 0, then claimed for Attempt 1. This review returns it to Ready with the claim cleared. ARCH-055-SYSTEM-TEST-001 remains Pending until API-009 is Complete.

## Execution-bound investigation before Attempt 2

A disposable PostgreSQL 17.11 diagnostic used the pinned Prisma 6.19.3 client, the four existing one-second URL options, and a test-only startup option `options=-c statement_timeout=750`. This isolated the execution mechanism without changing the implementation or running domain migrations. The experiment verified the effective timeout with `current_setting('statement_timeout')`.

- With the connection intact, PostgreSQL cancelled `SELECT 1 FROM pg_sleep(8)` in 763.16 ms. Prisma retained SQLSTATE `57014`. A separate connection observed the original backend idle at rejection. A fresh `SELECT 1` succeeded.
- A loopback proxy cut the client transport only after a separate observer saw the same injected statement active on PostgreSQL. The proxy kept the server half open to model lost delivery of completion. Prisma rejected with `P1017` while the old backend was active. A fresh query on the same one-connection Prisma client used a different backend and completed while the old one was still active.
- The startup deadline is a server execution bound on the tested direct PostgreSQL connection. It does not make an ambiguous transport rejection proof that the original statement has ended. Clearing the single-flight guard on that rejection remains unsafe under the current ADR. Deployment pooler handling of startup options was outside this diagnostic.

Architect decision requested: authorize a readiness-specific server deadline and a mechanism that retains the guard after ambiguous transport failure until PostgreSQL confirms cancellation or termination of the original session. That mechanism needs an approved connection and authorization contract, including behavior when confirmation is unavailable. An alternative ADR would need to explicitly permit bounded overlap after transport loss.

The disposable container, proxy, clients and temporary experiment script were cleaned up. This is investigation evidence only. Attempt 1 remains Ready with the claim cleared. The Changes Requested review and production code are unchanged.

## Completion Report — Attempt 2, 2026-11-04

### Status

Submitted for Architect review. The claim is cleared and the task status is `review`. API-008 remains Complete and unchanged. `ARCH-055-SYSTEM-TEST-001` remains gated; no downstream task was promoted.

### Implementation

- `src/database.ts` appends `-c statement_timeout=500ms` to the dedicated readiness client's existing PostgreSQL startup `options`, preserving existing options. The dedicated client retains its one-second pool, connection, and socket limits; the business client URL is unchanged.
- `tests/integration/http/arch055-readiness.postgres.test.ts` now sends the readiness connection through a local TCP test proxy. While the eight-second `pg_sleep` is running, the proxy holds PostgreSQL response bytes. A second PostgreSQL connection confirms the server has canceled the statement and no tagged active query remains while the Prisma promise is still pending; then the test releases the response and confirms Prisma reports SQLSTATE `57014`. It also checks the effective `statement_timeout`, preservation of `lock_timeout=7s`, and a successful fresh query.

### Validation

| Check | Observed outcome |
|---|---|
| Final canonical readiness PostgreSQL runner | Passed 2/2 on PostgreSQL 17 with all 71 canonical migrations applied, Prisma 6.19.3. The test observed one dedicated session, pool acquisition at 1031 ms, server cancellation at 519 ms, and HTTP outage recovery at 1008 ms. No active `pg_sleep` query remained while Prisma's promise was held pending; the subsequent probe succeeded, the business backend remained available, and shutdown left zero sockets. |
| Focused readiness unit tests | Passed 10; one optional M17 profile was skipped by the focused command. |
| Aggregate integration | Passed 120 Node tests with four explicit opt-in measurement skips; the separate platform-configuration PostgreSQL runner passed 5/5. This aggregate run preceded the final integration-test-only proxy ordering assertion; the final migrated readiness runner above was rerun after that assertion was added. |
| Typecheck and build | `npm run typecheck` passed after the final test change. `npm run build` passed with generated Prisma Client 6.19.3. |
| Lint | Changed-file ESLint passed. Repository-wide `npm run lint` still reports the existing `no-empty` error in untouched `src/merchant/support/routes.ts:75`. |
| Diff and cleanup | `git diff --check` passed. The disposable PostgreSQL container, proxy sockets, and test clients were cleaned up. |

The PostgreSQL server-side timeout closes the gap found in Attempt 1: the readiness promise no longer settles while its timed-out statement continues running on the backend. This is the direct PostgreSQL 17 test topology; deployment pooler behavior is still bounded by the configured connection URL and should be covered by deployment verification. The mechanism is documented by [Prisma ORM v6 PostgreSQL connector](https://www.prisma.io/docs/orm/v6/overview/databases/postgresql) and [PostgreSQL 17 `statement_timeout`](https://www.postgresql.org/docs/17/runtime-config-client.html#GUC-STATEMENT-TIMEOUT).
