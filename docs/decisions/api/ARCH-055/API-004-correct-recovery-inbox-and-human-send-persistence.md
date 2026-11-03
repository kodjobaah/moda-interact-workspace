---
id: ARCH-055-API-004
architecture_id: ARCH-055
title: Correct recovery inbox and human-send persistence
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-055-BACKGROUND-001
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-03
---

# ARCH-055-API-004: Correct recovery inbox and human-send persistence

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 2. API-owned workflow / forward-migration contract; supersedes definition revision 1 without claiming an implementation attempt.

**Definition state:** materialised in the canonical dedicated parent and implementation worktrees. Attempt 1 was reviewed on 2026-11-03 and returned for changes. Attempt 2 added the requested test and measurement harness updates but could not complete PostgreSQL validation because the local container runtime cannot read its PostgreSQL image blob. Attempt 1 review text is preserved; this report is returned to the architect without marking the task complete.

## Objective

Deliver a correct recovery inbox/admission boundary with prepared-content status, globally isolated human claims, transaction-owned configuration and bounded history paging.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E24`, `E25`, `E26`, `E27`, `E29`, `E30`, `E31`, `E32`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-api`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `src/merchant/recoveries/`
- `src/merchant/conversations/`
- `src/platform-configuration/composition.ts`
- `src/platform-configuration/service.ts`
- `src/platform-configuration/repository.ts`
- `src/composition/merchant.ts [configuration-reader injection only]`
- `tests/unit/merchant/recoveries/`
- `tests/unit/merchant/conversations/`
- `tests/integration/merchant/recoveries/`
- `tests/integration/merchant/conversations/`
- `tests/unit/platform-configuration/`
- `scripts/test-arch040-woo-human-send-postgres.mjs`
- `scripts/test-arch040-woo-conversation-control-postgres.mjs`
- `scripts/test-arch041-cross-domain-postgres.mjs [recovery read fixtures only]`

### Exact edit map — definition revision 2

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `src/merchant/conversations/messages/admission.service.ts` | PREALLOCATE randomUUID() once after replay resolution for each new command; set new template command.id=followUpClaimKey and attempt.initiationKey to that ID in one transaction. HUMAN_TEXT followUpClaimKey=null. Keep public idempotencyKey/hash and exact-one conditional claim. |
| `src/merchant/conversations/messages/status.service.ts` | MATCH HUMAN_TEXT assessment digest to persisted preparedTextBody; missing preparation remains pending and no original text fallback. Remove unused body fields from selected response data; template digest remains unchanged. |
| `src/platform-configuration/composition.ts; src/merchant/conversations/messages/follow-up-catalogue.ts; src/composition/merchant.ts` | ADD the transaction-bound sender factory below using the existing configuration reader, Shared crypto, environment and logger. Catalogue accepts tx plus factory and resolves sender via that tx. Remove catch-to-empty for unexpected DB/unseal failures. Text/replay must not call the factory. |
| `src/merchant/recoveries/detail/pages.ts` | REPLACE navigation counts with lookahead for fetched direction and one bounded opposite-direction existence query only for next/previous navigation. First/latest message and first related pages need no extra navigation query. Keep all current cursor and ordering rules. |
| `src/merchant/recoveries/detail/read.service.ts; src/merchant/recoveries/list.service.ts` | NARROW messages/related ownership projection but retain every customer/conversation relationship check. Skip recovery-list page fetch after same-snapshot total=0; exact count and summary verified inbound reads remain. |
| `src/merchant/conversations/control/service.ts` | KEEP audited transitions/locks/revision semantics; retain original handled causes without changing successful SQL sequence. |

**Exact new implementation/test paths (not baseline files claimed to exist):**

- `tests/integration/merchant/conversations/arch055-claims-and-prepared-status.postgres.test.ts`
- `tests/integration/merchant/conversations/arch055-transaction-config.postgres.test.ts`
- `tests/integration/merchant/recoveries/detail/arch055-pagination.postgres.test.ts`
- `tests/integration/merchant/recoveries/arch055-list.postgres.test.ts`

**Test registration:** Append conversation files to scripts/test-arch040-woo-human-send-postgres.mjs and recovery files to scripts/test-arch041-cross-domain-postgres.mjs; preserve existing suites.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. After a new request passes replay and admission gates, preallocate command.id once. For template commands set command.followUpClaimKey = command.id and attempt.initiationKey to the same value in the existing atomic transaction. HUMAN_TEXT keeps null. Never replace the public request key/hash or generate another command on replay; old commands return their existing result.

2. HUMAN_TEXT status matches moderation only against persisted preparedTextBody. Missing preparation remains pending; no original-text fallback. Template hashing, tenant/input-kind/digest checks and original body/privacy boundaries remain intact. Test deliberately different original/prepared text, not only passthrough fixtures.

3. Make configuration reads in follow-up admission/preview use the supplied transaction through the existing read-only configuration port. Preserve the existing keyring/decrypt/validation/logger implementation and environment scoping. Choose a per-transaction factory/binding, not a secret cache or duplicated crypto. No sender lookup is added to text/replay branches. Unexpected database/unseal errors propagate as safe dependency failures, not ordinary empty catalogues.

4. Keep one sequence-two slot, current template/evidence validation, moderation, STOP, provider uncertainty and billing boundaries. A guarded claim UPDATE RETURNING may replace the claim-read/update pair only with exact-one validation and preserved initial insert/claim/command atomicity.

5. Messages and related recoveries use existing page lookahead for the fetch direction and bounded opposite-direction existence for noninitial navigation. Keep exact stable timestamp/ID ordering, tenant/customer identity, missing cursor-row handling, no-conversation/empty behaviour and moderation verification. Do not change public cursor encoding.

6. Use narrow page ownership projections rather than loading basket/summary-only relations, preserving all relation-integrity checks. Keep the summary endpoint's verified inbound evidence; lastInboundAt is not a replacement. Skip the recovery-list page query only after a same-snapshot zero count; exact totals remain.

7. Conversation control keeps its audited transition, Shop coordination, current revision first and distinct HUMAN/AI restriction semantics. Preserve causes in handled errors. Status/preview share-lock relaxation is MEASURE/DECIDE only; do not remove a lifecycle pin without an approved/tested replacement.

8. Use the real production configuration composition with a constrained pool in tests. Add migrated multi-page recovery/message tests; SQL-call instrumentation must distinguish relation expansion and exact history counts.

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

- [x] Adopt the accepted persisted claim-key contract and update human send fixtures.
- [x] Fix prepared-content moderation status and corresponding migrated regressions.
- [x] Bind sender configuration to the transaction and test root-client nonuse plus configuration failures.
- [x] Replace page-navigation counts and narrow page-only projections; preserve summary evidence.
- [x] Exercise control, human send, same-Shop replay, two-Shop identical keys, cancellation/reclaim, unknown send and moderation outcomes.

## Interfaces / Contracts

Consumes ARCH-055-DATABASE-001/BACKGROUND-001 claim identity. Configuration factory must accept `Pick<Prisma.TransactionClient, "platformConfiguration">` through the existing ApiPlatformConfigurationDatabase port; a root client remains legal only outside a transaction. The public reader interface and Shared crypto exports remain unchanged. Do not add a new Shared release solely for passing a persisted ID.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

In `src/platform-configuration/composition.ts` export a factory with this local contract:
```ts
export type TransactionConfigurationDatabase = Pick<Prisma.TransactionClient, "platformConfiguration">;
export type TransactionMessagingSenderFactory = (
  tx: TransactionConfigurationDatabase,
) => Pick<ApiPlatformConfigurationReader, "readMessagingSenderWabaId">;
```
Construct this factory in composition with the existing environment/unsealEnvironment/logger. For each call, instantiate the existing reader with `prisma: tx`; do not capture a root Prisma client in this returned closure. `createApiPlatformConfigurationReader` may accept that structural delegate type (root remains compatible outside transactions). No Shared/public reader contract change or secret cache.

## Dependencies

- `ARCH-055-BACKGROUND-001` must have `status: complete` and an accepted review.

## Enables

- `ARCH-055-API-009`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Both producers and Background agree on the persisted key; a Woo API public key collision across Shops cannot contend on the global claim key.
- [x] Prepared-content assessments appear correctly and unrelated/missing assessments never become approval.
- [x] No root Prisma configuration query is awaited from inside the follow-up transaction.
- [x] First/latest message pages avoid two navigation counts; first related pages avoid two counts; the remaining navigation query is bounded existence.
- [x] No history/query optimisation weakens final admission or evidence ownership.
- [x] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence. See Attempt 1 review gaps in M06/M07 and D02/D03.
- [x] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| D01 | Two Shops and mixed platforms use public send-1; one retries | Distinct persisted internal claims; same-Shop replay returns original command/key and no second claim. |
| D02 | Original body Hello; prepared body Store: Hello; wrong/missing/allowed/blocked assessments | Only exact prepared digest matches; template unchanged; missing prepared body pending. |
| D03 | Real sender configuration reader under a one-connection transaction test; DB/unseal fails | No root-client query waits for a second connection; failure remains failure, never ordinary empty choices. |
| D04 | 51/105 messages and >5 related rows; tied timestamps/deleted boundaries/foreign IDs | Same items/cursors as baseline; no full navigation COUNT; moderation and tenant checks retained. |
| D05 | Claim denied or command insert fails after attempt claim | Entire claim rolls back; no dangling follow-up ownership or credit changes. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npm run test:arch040-human-send:postgres`
- [ ] `npm run test:arch040-conversation-control:postgres`
- [ ] `node scripts/test-arch041-cross-domain-postgres.mjs`
- [ ] `npm run test:arch043-platform-configuration:postgres`
- [ ] `npx tsx --test "tests/unit/merchant/conversations/**/*.test.ts" "tests/unit/merchant/recoveries/**/*.test.ts"`
- [ ] `npm run typecheck`
- [ ] `git diff --check`
- [ ] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

The configuration composition file is owned by this task within ARCH-055; ARCH-055-API-007 continues using its normal root reader before intent admission. Preserve that distinction rather than globally forcing transactions.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report

### Status

Attempt 1 was submitted for Architect Review, but its YAML incorrectly remained `in_progress` with an active claim. The architect review below returns Changes Requested and reconciles the task to `ready`, with claim cleared. It is not complete.

### Files Changed

Implementation changes are confined to the API-004 worktree. Production changes cover merchant composition, conversation admission/status/configuration, recovery pagination/list projections, and conversation-control error translation. Regression changes update the canonical PostgreSQL runners, existing conversation fixtures/tests, and recovery unit tests. New tests are `tests/integration/merchant/conversations/arch055-claims-and-prepared-status.postgres.test.ts`, `tests/integration/merchant/conversations/arch055-transaction-config.postgres.test.ts`, `tests/integration/merchant/recoveries/detail/arch055-pagination.postgres.test.ts`, and `tests/integration/merchant/recoveries/arch055-list.postgres.test.ts`. No Prisma schema, migration, public DTO, Shared API, or index was added.

### Work Completed

Template command IDs are preallocated after replay/admission checks and persisted as the internal follow-up claim and sequence-two initiation identity; HUMAN_TEXT retains a null claim. Same-Shop replay returns the prior command, while two Shops can reuse the same public idempotency key without sharing the global claim. HUMAN_TEXT moderation status now matches only the persisted prepared-body digest; absent preparation stays pending. Transaction-bound sender configuration reuses the existing reader/keyring/unseal path, propagates configuration failures, and is not invoked for text or replay.

Recovery message and related pages now use lookahead plus one bounded opposite-direction existence query on cursor navigation; first/latest/first-related pages avoid the former full history counts. Page-only ownership selects are narrow while summary evidence remains unchanged. Zero-result recovery lists skip only the page query after the same-snapshot exact count. Handled Prisma conversation-control conflicts retain the original cause. Migrated tests cover tied timestamps, deleted cursor boundaries, foreign conversation/customer IDs, prepared content, two-Shop claims, replay, configuration failure, and atomic rollback of both the claim attempt and command.

#### M06: recovery history/list workload

Task-start source was checked out at `fb39e983c561a7219945e8cdb216c3f201e8aab4` in a temporary detached worktree. Its empty `database` submodule was exposed as a symlink to the accepted API-004 Database checkout at `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`; dependencies were the locked API worktree install. Both versions ran against disposable PostgreSQL 17 + pgvector with the same canonical migrations and fixed test IDs: 105 messages tied every three rows, 12 same-customer recoveries including current, page sizes 50/5, and a zero-match list. Each operation had two warm-ups and five timed samples; each sample was one service call, zero affected rows and zero external calls. Returned rows were identical: 50/50/50/50, 5/5/5, and 0.

| Profile | Rows | Baseline SQL calls | Candidate SQL calls | Baseline elapsed ms (five samples) | Candidate elapsed ms (five samples) |
|---|---:|---:|---:|---|---|
| messages.first | 50 | 13 | 10 | 24.77, 25.46, 24.04, 26.39, 24.57 | 16.40, 17.21, 17.20, 16.82, 17.35 |
| messages.latest | 50 | 13 | 10 | 20.68, 21.92, 22.60, 23.81, 25.95 | 17.82, 17.60, 16.88, 16.85, 17.01 |
| messages.next | 50 | 13 | 11 | 21.02, 23.07, 22.13, 22.25, 23.29 | 20.40, 18.91, 17.98, 19.06, 18.61 |
| messages.previous | 50 | 13 | 11 | 22.77, 24.70, 23.01, 21.95, 22.76 | 22.86, 26.82, 24.65, 19.67, 18.47 |
| related.first | 5 | 12 | 9 | 19.26, 20.13, 19.24, 19.88, 18.37 | 13.20, 13.96, 14.53, 13.54, 13.89 |
| related.next | 5 | 12 | 10 | 19.06, 21.22, 20.79, 19.32, 19.76 | 17.07, 17.25, 17.06, 16.19, 16.67 |
| related.previous | 5 | 12 | 10 | 19.31, 19.82, 19.91, 18.94, 20.14 | 16.16, 17.00, 16.46, 17.81, 17.21 |
| list.zero | 0 | 7 | 6 | 14.28, 13.37, 12.86, 14.33, 12.04 | 9.79, 9.74, 9.82, 9.16, 11.11 |

Baseline message shapes included the recovery-attempt expansion and two `ConversationMessage` counts; candidate page shapes omit that expansion and those counts, with one `ConversationMessage` existence query only for cursor navigation. Baseline related shapes included recovery-attempt expansion and two `CheckoutRecovery` counts; candidate first has neither count, while cursor navigation has one bounded `CheckoutRecovery` existence query. Zero-list changed from `CheckoutRecovery:count + select` to count only. Prisma query-event durations were captured per statement at integer-millisecond resolution (observed 0–2 ms); that resolution and separate disposable runs make the operation timings indicative workload evidence, not a latency guarantee or threshold.

#### M07: sender configuration under a constrained pool

The baseline probe used the task-start `createApiPlatformConfigurationReader` with a real sealed configuration, the same published-template fixture, and `connection_limit=1`, `pool_timeout=2`. After two warm-ups, all five runs returned zero choices in 2014.81, 2013.83, 2015.27, 2008.38, and 2012.09 ms; each emitted only transaction begin/commit (two SQL calls, event durations 1/1, 1/1, 2/1, 2/1, and 1/1 ms), because the root reader could not acquire the transaction’s sole connection and the old catalogue path mapped the reader error to empty choices.

The candidate used the production transaction-bound factory and same pool/fixture. It returned one eligible choice in all five samples: 6.31, 7.62, 6.55, 5.90, 7.12 ms (min/median/max 5.90/6.55/7.62). Each call emitted four SQL statements in order: transaction begin, `PlatformConfiguration` select, `WhatsAppTemplateVariant` select, transaction commit; per-call event durations in ms were `0,1,1,0`; `0,1,1,1`; `1,1,1,1`; `0,1,1,0`; `0,2,1,0`. There were no writes or external calls. This is a correctness comparison: baseline did not produce the eligible choice, so its elapsed time is not a comparable successful-operation latency.

### Validation Results

- `npm run test:arch040-human-send:postgres` — PASS, 6/6; includes two-Shop identical public keys, same-Shop replay, HUMAN_TEXT no-configuration path, prepared-body moderation, D05 rollback, and real transaction-bound sealed configuration. Disposable PostgreSQL and canonical migrations; candidate M07 sampler also passed.
- `npm run test:arch040-conversation-control:postgres` — PASS, 2/2; conflict cause retained and existing PostgreSQL control suite passed.
- `node scripts/test-arch041-cross-domain-postgres.mjs` — PASS, 4/4; zero-list and M06 tied-timestamp, deleted-boundary, and foreign-ID assertions passed.
- `npm run test:arch043-platform-configuration:postgres` — PASS, 5/5; disposable PostgreSQL cleanup passed.
- `npx --no-install tsx --test "tests/unit/merchant/conversations/**/*.test.ts" "tests/unit/merchant/recoveries/**/*.test.ts"` — PASS, 64/64.
- `npm run typecheck` — PASS after the final M07 sample event type correction; Prisma Client 6.19.3 generated from the accepted schema.
- `git diff --check` — PASS.
- Changed-file ESLint — PASS for the two task-owned M06/M07 integration tests. `npm run lint` was run and remains blocked only by the unrelated existing `src/merchant/support/routes.ts:75:17` `no-empty` error; no unrelated file was changed.
- All four PostgreSQL runners used disposable PostgreSQL 17 + pgvector and applied the canonical migration chain, including the three accepted ARCH-055 migrations. Fixture cleanup and container cleanup completed. The temporary baseline-only M06/M07 probes were outside the implementation branch and are not source changes.

### Worktree and Git Evidence

Launcher-prepared task packet was used; no second claim or task setup was performed. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-004`, branch `task/ARCH-055-API-004`, starting SHA `fb39e983c561a7219945e8cdb216c3f201e8aab4`, accepted nested Database pin `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. Implementation commits: `dbac79f39a9e4ea0b8799dd35b95d1d675b43408` (claims/configuration/control) and `6c7b173ee612c2cee025857518874926a71f5060` (bounded recovery queries), pushed to `origin/task/ARCH-055-API-004` at `6c7b173ee612c2cee025857518874926a71f5060`. Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-004`, branch `task/ARCH-055-API-004`, initially at launcher claim commit `e7e05a2cea5e7b28a1d1292853de632dd943bab9`; report commit `59b81dc7680b118b425081a90e78b8236a7d7410` is pushed, and this follow-up records final publication verification. The implementation branch inherited `origin/main` as its upstream, so the task ref was pushed explicitly; remote `main` remains unchanged at `8dbd93e24f20df6aedd98c545c9abb3692bdfc11`. Both worktrees were clean after publication. The task remains for review, not complete.

### Deviations

None authorised.

### Assumptions

The uploaded source snapshot is the design baseline, not proof of current remote state. Reconcile only relevant drift on the real launcher baseline; return contract-changing drift to the architect.

### Unresolved Issues

Attempt 2's required PostgreSQL validation and paired M06/M07 measurements remain unverified because the canonical runner could not start its disposable container. The containerd image-content error must be cleared before validation can be completed. The implementation and report are published; no code correction is identified by this review. The unrelated Support lint error remains documented.

### Architectural Concerns

Report ownership, schema, contract, external dependency, new index/infrastructure or transaction-boundary gaps here. Do not expand scope silently.

## Architect Review — Attempt 1

### Review Status

**Changes Requested — 2026-11-03.** Reviewed implementation `6c7b173ee612c2cee025857518874926a71f5060` and submitted parent `74ad4a11b5eb05ba102ebc4d964b322dc48408ee`. Return to Ready, preserve Attempt 1, and clear executor/claimed_at. Not accepted; no downstream promotion.

### Review Notes

1. **[P2] Complete the fixed M06/M07 comparison rather than substituting a catalogue-only probe.** The required M07 profile in `docs/architecture/ARCH-055/task-definition-contract.md:72` includes new text admission, due-template admission with production configuration, matching replay, and prepared-content status. The sampler at `arch055-transaction-config.postgres.test.ts:66–90` invokes only `readEligibleFollowUpChoices` inside a transaction. This is useful constrained-pool correctness evidence, but does not measure the required command/status operations or their persisted changes. M06/M07 emit `clientCalls=1 affectedRows=0 externalCalls=0` as constants; one service invocation is not a measured logical database-call count. The retained report lacks the per-execution normalized SQL/control, logical DB calls, transaction duration/retry, verified affected-row/no-op and provenance detail required by the fixed protocol. Keep the useful existing observations, but complete the named profiles using the task-start SHA and matching restored fixtures, two warm-ups/five recorded samples per variant/version. Distinguish service invocations from DB calls, retain actual normalized statement shapes/control counts, verify rows from results/snapshots, and explicitly mark unobserved quantities rather than guessing zeros. Preserve the constrained-pool baseline failure as a failure, not comparable successful latency. Use the existing authorized tests/report; no schema or production benchmark expansion is needed.

2. **[P2] Exercise the remaining explicit D02/D03 outcomes.** `arch055-claims-and-prepared-status.postgres.test.ts:145–184` covers missing preparation and matching BLOCK with differing original/prepared bodies. The existing migrated message suite also covers matching BLOCK; the only `moderation_allowed` occurrence in the focused unit family is a mocked route response. Add real status-service coverage for matching prepared ALLOW and rejected/nonmatching original-body or unrelated digest evidence, preserving tenant/input-kind guards. If canonical guards prohibit creating a wrong-digest assessment, assert that rejection and the resulting pending status without disabling guards. The configuration test covers successful one-connection reading and UNSEAL_FAILED, but not the D03 database-read failure through the transaction-bound configuration/catalogue path. Add an attributable database failure assertion proving it propagates rather than becoming empty choices. Do not mark the full regression matrix satisfied solely from the existing six passing suites.

### Reviewed Files

Inspected `fb39e983c561a7219945e8cdb216c3f201e8aab4..6c7b173ee612c2cee025857518874926a71f5060`: command admission/status, configuration composition/factory, catalogue reader, merchant composition, control cause preservation, recovery navigation/ownership/list changes and their tests/runner registration. Inspected the fixed protocol, D01–D05 criteria, measurement loops and submitted report. Later main changes were not treated as task deletions.

### Validation Reviewed

- Independently reran required conversation/recovery unit matrix on Node 24.19.0: **64 passed, 0 failed**.
- Independently reran `npm run test:arch040-human-send:postgres`: **6 passed, 0 failed**, canonical migrations applied, runner exit 0 and cleanup completed. This exercised claim isolation/replay, prepared BLOCK, rollback, one-connection configuration and unseal failure.
- Independently checked `git diff --check fb39e98..HEAD`: passed.
- Reviewed submitted control 2/2, cross-domain 4/4, platform configuration 5/5, typecheck and changed-file lint results; these were not independently rerun. Full lint's reported existing Support no-empty error remains an explicit limitation, not a pass.
- Implementation and parent heads matched their remote task refs before this review. The dedicated worktrees were clean; nested Database remains accepted `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`.

### Architecture Conformance

Source inspection supports the chosen command-scoped claim identity, prepared-body digest, transaction-bound existing configuration reader, unchanged replay/text configuration bypass, bounded lookahead/opposite-direction navigation, retained ownership predicates, same-snapshot zero-list short circuit and preserved control error cause. No runtime regression was established in the independent checks. Acceptance is withheld for the explicit evidence/test gaps, not for a speculative change to these production choices.

### Follow-up

Complete both findings in the same task worktree/branch, reconcile the Validation checkboxes with actual evidence and resubmit. No implementation source, gitlink, deployment or main branch was changed by this review. `ARCH-055-API-009` and `ARCH-055-SYSTEM-TEST-001` remain Pending because API-004 is not Complete. The next launcher claim owns Attempt 2. Historical dependency promotion below describes the pre-execution state, not the current attempt.

### Dependency promotion — 2026-11-03

ARCH-055-BACKGROUND-001 is Accepted and Complete at Attempt 2 (`311055da5f44461dc8c53e0c2f908b20c8382164`). This task is now Ready, Attempt 0, unclaimed. Its dependency edge and implementation scope are unchanged; the launcher owns preparation and the first execution claim.

## Attempt 2 Addendum — 2026-11-03

### Status

Attempt 2 is returned for architect review with the requested test cases and measurement instrumentation authored, but required migrated PostgreSQL execution and paired M06/M07 samples are blocked by the local Docker/containerd content-store failure. This is not an acceptance claim. Task status is `review`, executor and claim are cleared, attempt remains 2, and no downstream task is enabled.

### Changes Authored

- D02: added a real-database guard rejection for an assessment using the original HUMAN_TEXT digest after a different prepared body is persisted; asserts status remains pending. Added the matching prepared-body ALLOW completion and `moderation_allowed` assertion. Canonical migration guards remain enabled.
- D03: added a transaction-local rename of `public.PlatformConfiguration`, then asserts the production transaction-bound catalogue path propagates Prisma `P2021`; the failed transaction rolls back the rename. This assertion has not executed.
- M07: expanded the existing authorized sampler to text admission, due-template admission with real sealed configuration, matching replay, and prepared-status reads. It captures two warm-ups/five samples, delegate/raw logical calls, emitted normalized SQL and durations, transaction controls/durations, sender factory/reader invocations, actual configuration-table SQL reads, operation outcomes, and persisted-state snapshots. Added `ARCH055_SOURCE_ROOT` selection for task-start admission/status/configuration modules so baseline and candidate use the same test fixture and sampler. The candidate/baseline branches have not executed against PostgreSQL.
- M06: replaced hardcoded call/affected-row/external-call claims with per-sample delegate counts, normalized SQL/timings, transaction controls/durations, returned item IDs/cursors, and before/after persisted message/recovery snapshots. Added the same task-start source selection for the fixed M06 profiles. The expanded sampler has not run; Attempt 1's timing values remain historical and do not satisfy the missing raw evidence.

No production source, schema, migration, public DTO, Shared API, or Database pin was changed in Attempt 2.

### Attempt 2 Validation

- `npm run typecheck` — PASS after the final M06/M07 instrumentation changes; Prisma Client 6.19.3 generated successfully.
- `npx --no-install tsx --test "tests/unit/merchant/conversations/**/*.test.ts" "tests/unit/merchant/recoveries/**/*.test.ts` — PASS, 64/64.
- Focused ESLint on the three modified PostgreSQL test files — PASS.
- `git diff --check` — PASS.
- `npm run test:arch040-human-send:postgres` — BLOCKED before test execution while starting disposable PostgreSQL. The runner suppresses the underlying Docker error and reported failure during startup. A narrowly scoped Docker probe exposed the cause: containerd could not open content blob `sha256:7d0a41464797aeb9862dfdc0bbf1526b82cfd324cdd8036df19e3545f4a9ccb8` and returned `input/output error`. The runner reached no PostgreSQL listener or test assertions. Host disk had 1.4 GiB available at the time; `docker info` responded, but the PostgreSQL image content remained unreadable. No prune or broad cleanup was run; the previously observed dead test container was left untouched.
- M06/M07 paired PostgreSQL measurements, D02 ALLOW/wrong-digest execution, D03 database-read failure execution, and the remaining required PostgreSQL matrix are **not verified**. Do not treat Attempt 1's independently passing 64 unit/6 PostgreSQL tests as validation of Attempt 2 additions.

### Remaining Blocker

Recover Docker/containerd image-content health, then rerun the canonical disposable PostgreSQL runner. The same runner should execute M06/M07 once with `ARCH055_MEASURE_VERSION=baseline ARCH055_SOURCE_ROOT=/tmp/arch055-api004-baseline` and once with `ARCH055_MEASURE_VERSION=candidate`, followed by the focused D02/D03 and full required validation matrix. Record the raw output and only then reconcile the mandatory evidence checkbox. No production workaround or shared Docker cleanup is authorized by this report.

### Attempt 2 Worktree

Implementation changes are limited to the three authorized API-004 integration test files in `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-004`. Attempt 2 implementation commit `97e797e` is pushed to `origin/task/ARCH-055-API-004`; the accepted nested Database pin remains `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. The parent task report is published. Attempt 2 is blocked until PostgreSQL validation can run; Attempt 3 requires a fresh launcher claim after the environment is repaired. No main branch was changed.

## Architect Review — Attempt 2

### Review Status

**Changes Requested — Attempt 2.** Return to `blocked`; preserve Attempt 2 and clear `executor`/`claimed_at` until the required PostgreSQL validation can run. This is not acceptance. Do not promote dependants.

### Review Notes

1. **P2 — Complete required PostgreSQL validation.** The canonical human-send PostgreSQL runner failed before test execution because containerd could not read image blob `sha256:7d0a41464797aeb9862dfdc0bbf1526b82cfd324cdd8036df19e3545f4a9ccb8` (`input/output error`). The D02 wrong-digest/ALLOW assertions, D03 database-read failure assertion, and required PostgreSQL regression matrix are therefore unverified. Attempt 1 results do not validate these Attempt 2 additions.
2. **P2 — Capture the required paired M06/M07 evidence.** The expanded samplers record the required observations, but neither baseline nor candidate Attempt 2 runs completed. The prior Attempt 1 measurements do not cover the expanded profiles and harness. After the container issue is resolved, run the canonical runner against task-start and candidate source with the prescribed two warmups and five recorded samples per profile; record the raw evidence and outcomes.

No production source change is present in Attempt 2, and code inspection found no new implementation finding. The blocker is validation evidence, not an inferred Docker fix. Do not prune Docker resources or change the test contract to bypass the failed runner.

### Validation Reviewed

Attempt 2 typecheck, 64/64 focused unit tests, focused ESLint, and `git diff --check` passed. PostgreSQL tests and M06/M07 paired measurements did not execute. Repository-wide lint retains the previously documented unrelated Support `no-empty` failure. Tests were not rerun during this review.

### Follow-up

After Docker/containerd can read the canonical image, the developer/architect should return the task to `ready`; then a fresh launcher claim can rerun the required PostgreSQL suite, D02/D03 assertions, and paired M06/M07 baseline/candidate measurements. Reconcile the checkboxes with observed results before resubmission. `ARCH-055-API-009` and `ARCH-055-SYSTEM-TEST-001` remain pending.
