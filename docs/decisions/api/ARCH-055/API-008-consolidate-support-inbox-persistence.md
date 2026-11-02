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
status: review
priority: 35
executor: null
claimed_at: null
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

**Definition state:** materialised and claimed for Attempt 1 by the canonical task launcher. Implementation is submitted for architect review; acceptance remains pending.

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

- [x] Implement coherent list/count projection and unique translation lookup.
- [x] Combine thread bookkeeping writes and add rollback plus concurrent Admin reply fixtures.
- [x] Log queue-emitted connection failures without changing durable repair semantics.
- [x] Add coordinated mark-read race tests; measure rather than automatically switch query order.

## Interfaces / Contracts

Public Support DTOs, idempotency keys, translation queue contract and suspended-Shop policy stay unchanged. The coherent list/count snapshot is an explicit ARCH-055 decision rather than a claim about the old implementation.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

None. The source baseline is context, not a fabricated dependency on historical review evidence.

## Enables

- `ARCH-055-API-009`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Message readAt and unread count are consistent under a controlled mark-read interleaving.
- [x] New composition saves one thread write while replay still performs no writes.
- [x] A queue outage leaves a durable pending translation that the existing reconciler can repair; the persisted PENDING row remains eligible for its existing repair scan.
- [x] Concurrent read markers return the same winning timestamp; foreign/unavailable messages remain ineligible.
- [x] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [x] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [x] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

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

- [x] `npm run test:arch035-woo-support:unit` — 15 tests passed.
- [x] `npm run test:arch035-woo-support:postgres` — candidate M16 and existing Support integration passed on final source; 68 canonical migrations applied to disposable PostgreSQL 17 + pgvector.
- [x] `npm run test:arch046-woo-selection:unit` — 3 tests passed.
- [x] `npm run typecheck` — Prisma Client generation and TypeScript check completed without diagnostics.
- [x] `git diff --check` — passed.
- [x] `npm run lint` was run; it reports one unchanged baseline issue in `src/merchant/support/routes.ts:75` (`no-empty`). No unrelated file was changed.
- [x] Before/after SQL, client-call, affected-row, sample timing, and deterministic concurrency/rollback/replay evidence is recorded below.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

Do not add a new translation worker or turn Redis into a correctness dependency. Any empty catch retained solely for logger failure isolation must remain narrowly documented and may not hide business exceptions.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report

### Status

Submitted for architect review. Attempt 1 remains in effect; task status is `review` and the execution claim is cleared.

### Files Changed

Changed in `moda-interact-api`:

- `src/merchant/support/read.service.ts`
- `src/merchant/support/commands.service.ts`
- `src/merchant/support/translation-queue.ts`
- `src/index.ts` (inject the Shared logger into the translation dispatcher)
- `tests/unit/merchant/support/translation-queue.test.ts`
- `tests/integration/merchant/support/arch055-snapshot-and-thread.postgres.test.ts`
- `tests/integration/merchant/support/service.postgres.test.ts`
- `scripts/test-arch035-woo-support-postgres.mjs`

### Work Completed

Implemented one parameterized page/count/unread statement with an empty-page aggregate and the unique AVAILABLE translation join. Compose now advances the thread metadata and version in its initial UPSERT, then inserts the message and optional PENDING translation in the same Read Committed transaction. Matching replay remains read-only. Mark-read keeps the conditional update and winner reread. Queue error events and enqueue failures log bounded, redacted original messages, codes and causes through the Shared logger; dispatch remains post-commit.

The captured baseline page SQL consisted of the bounded ascending message SELECT with its AVAILABLE translation LATERAL lookup, followed by the visible/unread COUNT SELECT. Candidate SQL is one `WITH scoped AS MATERIALIZED (...)`, with `aggregate` and `page` CTEs and a `LEFT JOIN support.MerchantMessageTranslation` on `(messageId,targetLanguageTag)` plus `status='AVAILABLE'`; `aggregate LEFT JOIN page` retains counts for an empty page. Baseline compose emitted the thread INSERT/`ON CONFLICT ... UPDATE updatedAt RETURNING id`, the message INSERT, then a thread UPDATE of last-message timestamps, version and `needsAdminResponse`. Candidate emitted one thread UPSERT that sets those fields and increments the existing version, followed by the same message INSERT and optional translation INSERT. The test captured normalized emitted statement text without parameters, and transaction-control statements separately.

H01 forces a commit between the returned Support data statement and response mapping; the candidate page/readAt and unread count remain from one snapshot. H02 checks pending translation body suppression and a foreign recovery link. H03 injects a message insert failure after the thread upsert and races an Admin-shaped message/version write against compose; rollback and final version assertions pass. H04 checks an emitted Queue error with credential-bearing message/cause and verifies redaction; the existing integration test verifies an enqueue rejection leaves its PENDING translation committed with no current batch and no retry deadline, which matches the existing reconciler's due-PENDING eligibility. It does not run the Background worker or a real Redis dispatcher end-to-end. H05 uses a held row lock and PostgreSQL activity barrier while two mark-read calls race, then verifies the winner timestamp and replay stability.

### Validation Results

**Environment and fixture:** Node `24.19.0`; Prisma `6.19.3`; `pgvector/pgvector:pg17` (PostgreSQL `17.11`); canonical 68-migration schema from Database pin `7c377282aa5819b3008b7d7f3018f44f4161523e`. The test uses one thread with 105 visible messages, fixed `2026-11-02T12:00:00.000Z` fixture timestamps, current-language AVAILABLE translations, 21 pre-read rows and 84 unread. It also tests an empty page, translated and untranslated compose, replay, H01–H05, and cleans its Shops; the runner removed the disposable database container.

**Candidate validation:** `npm run test:arch035-woo-support:unit` passed 15/15; `npm run test:arch035-woo-support:postgres` passed 2/2 (M16 and existing Support integration) on the final candidate; `npm run test:arch046-woo-selection:unit` passed 3/3; `npm run typecheck` completed without diagnostics; `git diff --check` passed. `npm run lint` reports only the pre-existing empty block at unchanged `src/merchant/support/routes.ts:75`.

**M16 comparison protocol:** Baseline source is task-start SHA `fa2a857ed2ccfd629a7c9f2749ce4a38cc143ff0`; candidate source commit is `0b208f9` (the final repair-eligibility test assertion is in `28c9c52`). Each profile used the same disposable canonical migrations and fixture, two discarded warmups, then five measured service calls with the fixture reset outside the timing window. Client-call counts include the existing principal checks and transaction control. SQL event durations are summed per sample and are distinct from service elapsed time. Result rows and persisted thread/message state were verified after the measured boundary. Queue dispatch was a deterministic in-process port; network bytes, pool wait, trigger-internal work and execution plans were not measured. Five samples are descriptive only, and the noisy timings do not support a production latency claim.

| M16 profile | Baseline: five service ms / five SQL-event ms; client calls | Candidate: five service ms / five SQL-event ms; client calls | Rows / state evidence |
|---|---|---|---|
| First 50 | `[45.746,73.493,51.896,36.421,50.536]` / `[36,63,42,26,42]`; 7 each | `[67.740,190.473,34.075,255.453,71.923]` / `[58,177,25,248,60]`; 6 each | 50 rows each; 0 affected rows; candidate uses 1 page/count statement vs baseline 2. |
| Empty page | `[26.608,45.725,35.316,47.791,66.565]` / `[18,35,29,38,59]`; 7 each | `[38.361,30.132,33.234,37.432,34.415]` / `[33,23,28,32,28]`; 6 each | 0 rows each; aggregate still returned; 0 affected rows. |
| Compose translated | `[173.304,72.962,50.089,61.906,97.744]` / `[161,61,37,51,87]`; 10 each | `[62.841,57.632,104.234,66.226,67.872]` / `[53,47,94,57,58]`; 9 each | 1 message and 1 PENDING translation persisted; thread version 1; one dispatch-port call. Thread bookkeeping SQL: 2→1. |
| Compose without translation | `[57.147,62.494,101.632,75.627,58.747]` / `[48,52,92,66,49]`; 9 each | `[49.363,107.206,69.986,270.691,272.051]` / `[41,100,61,262,262]`; 8 each | 1 message persisted; thread version 1; 0 dispatch calls. Thread bookkeeping SQL: 2→1. |
| Matching replay | `[29.890,83.394,41.182,52.208,47.396]` / `[19,76,36,47,41]`; 6 each | `[109.864,485.385,130.307,87.022,86.580]` / `[105,478,124,81,81]`; 6 each | 1 existing message; 0 affected rows; version unchanged; 0 writes in both versions. |

Each service operation used one Read Committed transaction (BEGIN, isolation SET, COMMIT); no rollback occurred in measured profiles. Candidate SQL evidence is emitted by the named integration test as `ARCH055_M16_EVIDENCE`; the persisted checks above verify one thread version increment and one message/translation per new compose. The fixed correctness scenarios separately verify rollback and the two-reader winner schedule.

The task-start M16 comparison passed. The full baseline runner also ran the existing Support test, which failed only at the newly added redaction assertion because baseline code logged `redis://secret` verbatim; the candidate run passes that assertion. No baseline failure is represented as a candidate validation pass. Actual query plans were not collected, so no planner improvement is claimed.

### Worktree and Git Evidence

Canonical launcher packet: parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-008`, implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-008`; both use `task/ARCH-055-API-008`. Parent report branch was prepared at `9a6d634bc96f18568b786b5cb39196983a96f57c`; implementation task-start SHA was `fa2a857ed2ccfd629a7c9f2749ce4a38cc143ff0`. Candidate implementation commit `0b208f9` and final repair-eligibility assertion `28c9c52` were pushed to `origin/task/ARCH-055-API-008`. Database submodule remained at `7c377282aa5819b3008b7d7f3018f44f4161523e`; no schema, migration or submodule change was made. This task report is submitted on its matching parent task branch.

### Deviations

One minimal out-of-map caller edit was needed in `src/index.ts` to inject the Shared logger into `MerchantSupportTranslationDispatcher`; the exact edit map named the dispatcher implementation but omitted its sole construction site. No other scope was added. Reported explicitly for architect review.

### Assumptions

The uploaded source snapshot is the design baseline, not proof of current remote state. Reconcile only relevant drift on the real launcher baseline; return contract-changing drift to the architect.

### Unresolved Issues

No blocking implementation issue remains. Review notes: the task edit map did not name the necessary `src/index.ts` logger-injection caller; this one-line wiring is reported above. M16 timings are noisy and no latency improvement is claimed. The full lint command retains the unrelated baseline `no-empty` issue at `routes.ts:75`.

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
