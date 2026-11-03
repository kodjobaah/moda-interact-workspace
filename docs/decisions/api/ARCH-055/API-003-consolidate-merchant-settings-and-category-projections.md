---
id: ARCH-055-API-003
architecture_id: ARCH-055
title: Consolidate merchant settings and category projections
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-11-03T06:09:52Z
attempt: 4
depends_on: []
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-03
---

# ARCH-055-API-003: Consolidate merchant settings and category projections

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 3. Small acceptance clarification over revision 2; execution metadata, dependencies and migration scope are unchanged.

**Definition state:** materialised in the dedicated matching parent and implementation task worktrees. Attempt 1 was implemented and published; architect review on 2026-11-03 returns Changes Requested and `ready`, with the claim cleared. The next launcher claim owns Attempt 2.

## Objective

Improve the coherent merchant-configuration boundary, keeping each existing revision/no-op policy and atomic category publication while reducing bounded duplicate reads and over-fetching.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E14`, `E15`, `E16`, `E17`, `E18`, `E19`, `E20`, `E21`, `E22`, `E23`, `E28`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-api`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `src/merchant/bootstrap/ [regression only]`
- `src/merchant/store-context/`
- `src/merchant/store-categories/`
- `src/merchant/feature-preferences/`
- `src/merchant/recovery-policy/`
- `src/merchant/ai-response-delay/`
- `src/merchant/recovery-summary/`
- `tests/unit/merchant/`
- `tests/integration/merchant/`
- `scripts/test-woocommerce-installation-postgres.mjs [category/bootstrap/context fixture registration only]`
- `scripts/test-arch035-feature-preferences-postgres.mjs`
- `scripts/test-arch041-cross-domain-postgres.mjs`
- `scripts/test-arch054-ai-response-delay-postgres.mjs`

Additional explicit registration/module paths for this revision:

- `scripts/test-arch055-merchant-settings-postgres.mjs`

### Exact edit map — definition revision 2

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `src/merchant/store-categories/store-categories-read.service.ts; src/merchant/store-categories/profile-read.ts` | MODIFY read(): choose a short RepeatableRead transaction (not an alternative design); include principal, catalogue, profile and environment configuration reads in that tx. Extend the local read database port with $transaction; no FOR UPDATE/FOR SHARE on category GET. |
| `src/merchant/store-categories/selection-publication.ts` | TRACK newly created lineage. Only that branch skips draft/latest reads and publishes revision=1. Pending-draft branch uses exact id/promptId/status=DRAFT update and requires count=1, removing its pre-read. Existing-lineage checks remain. |
| `src/merchant/feature-preferences/service.ts; src/merchant/feature-preferences/timing.ts` | NARROW selected scalar/relation fields without changing fingerprint inputs. Name first-load phases initial.subscriptionLookupMs/initial.featuresLookupMs/initial.preferencesLookupMs/initial.projectionMs and reload phases final.*. Preserve overall timers, sequential changed upserts and final reload. |
| `src/merchant/recovery-policy/service.ts; src/merchant/ai-response-delay/service.ts` | NARROW settings/override selections to projection/revision fields. Retain recovery-policy old-revision identical replay versus AI-delay revision-before-no-op; AI minutes 0..30 integers/default0. |
| `src/merchant/recovery-summary/recovery-summary.service.ts` | CONSOLIDATE principal/settings/override into one parameterised statement returning one joined tenant row (LEFT JOIN optional settings/override). Validate identity in the service and project the existing policy/default/expiry semantics. No reporting metrics or writes. |
| `scripts/test-arch055-merchant-settings-postgres.mjs` | CREATE canonical migration runner for existing bootstrap/store-context/category-read/category-write fixtures plus the new coherent-read race suite. Keep old aggregate runner untouched until API-009 reconciliation. |

**Exact new implementation/test paths (not baseline files claimed to exist):**

- `scripts/test-arch055-merchant-settings-postgres.mjs`
- `tests/integration/merchant/store-categories/arch055-coherent-read.postgres.test.ts`
- `tests/integration/merchant/feature-preferences/arch055-admin-interleaving.postgres.test.ts`

**Test registration:** Run the category test through the new settings runner; append the feature test to scripts/test-arch035-feature-preferences-postgres.mjs. API-009 alone updates aggregate package.json integration wiring.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Category GET must return a coherent profile/configuration selection: use the short read-only Repeatable Read transaction selected in the exact edit map below. Do not use FOR UPDATE to serialize GETs. Test publication between former reads. Do not transfer complete prompt text merely to calculate eligibility unless exact whitespace semantics cannot yet be preserved in a tested projection.

2. Category publication remains Serializable and atomic. For a newly created lineage, skip redundant draft/latest-history lookups and publish revision one; existing lineages keep their checks. Fold pending-draft ownership/status validation into an exact-one conditional update. Preserve subscription, generation, source-evidence and configuration guards.

3. Feature GET keeps its consistent snapshot/fingerprint and narrows unused relation fields. Feature PUT keeps current revision checking, entitlement/editability gates, Shop/installation coordination and persisted-timestamp final reload. Correct overwritten timing phase names using the existing timing facility; do not add a second generic telemetry layer.

4. Feature changed-row batching is MEASURE-FIRST. Record normal and large changed sets, emitted SQL, rollback and concurrent Admin eligibility changes; retain sequential upserts/final reload if no safe validated improvement is established. Do not use Promise.all as proof of parallel transaction SQL and do not remove the final reload speculatively.

5. Recovery-policy and AI-delay reads select only consumed fields, retaining settings/admin-override snapshots and read-only no-row defaults. PUTs keep their intentionally different replay rules: recovery-policy may acknowledge identical old-revision replay; AI-delay checks revision before same-value no-op. Keep integer 0..30 AI minutes, default zero, AI-only applicability and no new scheduling behaviour.

6. Store-context no-op suppression is MEASURE-FIRST and may only proceed with atomic distinction between changed, authorised-already-equal and invalid/stale principal. Do not turn legitimate no-ops into conflicts or stale-principal zero-row updates into success. Bootstrap retains its already narrow nonmutating projection.

7. Recovery summary remains policy presentation rather than metrics aggregation. Adopt a single tenant-bound statement snapshot for identity/settings/override if consolidating; retain defaults, override expiry/source and safe invalid-state handling. It does not become outbound permission.

8. Preserve original causes in all touched domain wrappers. Consolidate read-only identity queries locally only where every field/predicate survives; do not introduce a universal auth cache or weaken mutation locks. Migrate category/bootstrap/context fixtures rather than weakening canonical constraints. ARCH-055-API-009 owns package.json aggregate wiring for the existing AI-delay runner.

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

- [ ] Implement coherent category read and the two publication query reductions.
- [ ] Narrow settings/entitlement projections and record which fields participate in revision fingerprints.
- [ ] Correct feature timing attribution and preserve final reload; measure batching/no-op candidates separately.
- [ ] Test every family's current no-op/replay/default/admin-override semantics.
- [ ] Run category tests on canonical migrations and leave the existing AI-delay runner ready for ARCH-055-API-009 registration.

## Interfaces / Contracts

Existing public settings/category/feature contracts remain v1. Shared continues to own canonical validators; consume the pinned published exports. Read-model consistency is strengthened only as explicitly stated above; knowledge GET and restore are not touched.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

None. The source baseline is context, not a fabricated dependency on historical review evidence.

## Enables

- `ARCH-055-API-009`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Category profile/generation/mapping results are wholly old or wholly new under a controlled publication race.
- [ ] First category publication avoids two history calls; pending draft avoids its redundant pre-read, with unchanged conflict/rollback.
- [ ] No read endpoint creates settings/profile/billing state.
- [ ] AI-delay, recovery-policy and feature-preference replay differences remain intact and tested.
- [ ] Any deferred batching/no-op candidate has measurements and an explicit retained-behaviour decision, not an unchecked mandatory criterion.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| C01 | Publish profile B/config B between the previous two profile/config reads | GET returns all A or all B, never old profile with new provenance. |
| C02 | First lineage, existing empty lineage, valid/foreign/published pending draft | Only genuinely new lineage uses revision1 shortcut; invalid draft affects zero rows and full rollback. |
| C03 | Mapping disabled after admission versus before admission; current/stale no-op controls | Follow exact C03a–c below: post-admission save returns 200 with enabled=true but planEligible/editable/effective=false; pre-admission old revision is 409 conflict, fresh disabled revision is 409 denied; no-op does not write/reload. |
| C04 | AI delay 0/1/30, negative/fraction/31; policy old-revision identical replay | Original allowed/rejected values and deliberately different replay rules unchanged. |
| C05 | No settings/override, active override, expired override, malformed row | Single summary statement keeps default, source and safe failure semantics. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

### Exact C03 schedule and expected response — revision 3

This is a preservation test, not a new feature-admission policy. The inspected `service.ts:52–106,141–168` checks editability/revision against its initial load, performs changed upserts, then reloads under ReadCommitted; `routes.ts:45–81` maps successful updates to 200 and domain conflicts to 409. The published Shared selector requires an enabled plan mapping for effective activation. Retain those choices, sequential upserts and the final reload.

Use the existing fixture pattern in `tests/integration/merchant/feature-preferences/service.postgres.test.ts`. In the already authorised `arch055-admin-interleaving.postgres.test.ts`, seed one ACTIVE Woo Shop/installation, ACTIVE subscription/plan, and target feature F with `active=true`, `activationMode=MERCHANT_OPT_IN`, `systemRequired=false`, enabled plan mapping and a persisted merchant preference `enabled=false`. Keep all other records static. Obtain initial revision R0 using the real read service. No production hook or Admin-repository edit is required.

**C03a — Admin mapping disable after admission, before the write:**

1. Start the real update with `expectedRevision=R0` and one change `{ featureId: F.id, enabled: true }`.
2. A test-only transaction-client wrapper pauses at the FIRST `shopFeaturePreference.upsert` invocation, before forwarding it to the real client. All initial loads, revision/editability checks and change selection have therefore finished. All other client operations pass through to real migrated PostgreSQL.
3. On a second independent connection execute `billingPlanFeature.update({ where: { planId_featureId: { planId, featureId: F.id } }, data: { enabled: false } })` and await COMMIT. Do not change Feature.active, Subscription status, Plan.active, or take the API's Shop lock. This isolates the mapping-change case.
4. Release the barrier, allow the real upsert and complete final reload to finish, then commit. A failed Admin commit fails the test; do not release on a sleep or assume it committed.
5. Require successful service return / HTTP **200**. The stored preference is `enabled=true`, the mapping remains `enabled=false`, and F's returned fields are exactly `enabled=true`, `planEligible=false`, `editable=false`, `effective=false`, `required=false`. Other response fields keep their baseline shape. R1 differs from R0 and equals the revision from a fresh GET after both commits with no intervening writes; do not hardcode a digest containing generated timestamps.
6. Both `initial.subscriptionLookupMs`, `initial.featuresLookupMs`, `initial.preferencesLookupMs`, `initial.projectionMs` and the four corresponding `final.*` values exist as finite non-negative numbers. Each phase is recorded once; use call/phase assertions rather than requiring unequal durations. No effective capability is granted by the accepted preference alone.

**C03b — Admin mapping disable before admission:** reset the same fixture, capture R0, commit mapping disable BEFORE starting PUT, then submit the old R0. Require HTTP **409**, `{"error":"feature_preferences_conflict"}` and unchanged preference/timestamp. Read fresh disabled revision Rd and submit the same enable change using Rd: require **409**, `{"error":"feature_preferences_denied"}` with no preference write. Initial expected-revision failure takes precedence over editability failure. A separate route test can assert the envelope from the real service result/error; it must not replace the two-connection persistence assertion.

**C03c — No-op/stale controls:** reset with mapping enabled and preference=false. Current R0 with change=false returns **200**, R0 unchanged, no upsert and no `final.*` load timings. After a normal successful change advances the revision, an empty or identical-value request with old R0 returns **409**/`feature_preferences_conflict`, with no additional write. Unexpected infrastructure errors retain the existing 500/internal_error path.

Only the precise schedules above are frozen here. Subscription cancellation, Feature deactivation or Admin changes during individual statements are not silently declared equivalent to C03a. Keep existing tests for those other facts and return any discovered policy gap rather than introducing stronger locks or new rejection rules under this clarification.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npx tsx --test "tests/unit/merchant/store-categories/*.test.ts" "tests/unit/merchant/store-context/*.test.ts" "tests/unit/merchant/feature-preferences/*.test.ts" "tests/unit/merchant/recovery-policy/*.test.ts" "tests/unit/merchant/ai-response-delay/*.test.ts"`
- [ ] `node scripts/test-arch055-merchant-settings-postgres.mjs`
- [ ] `node scripts/test-arch035-feature-preferences-postgres.mjs`
- [ ] `node scripts/test-arch041-cross-domain-postgres.mjs`
- [ ] `node scripts/test-arch054-ai-response-delay-postgres.mjs`
- [ ] `npm run typecheck`
- [ ] `git diff --check`
- [ ] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

- [ ] Execute C03a, C03b and C03c with the exact barrier/commit order and HTTP/state/revision/timing outcomes above.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

The broad tests directories are bounded by the seven named families and bootstrap regression. Do not modify knowledge, commercial or Support implementation. A task may use multiple commits/work packages but has one owner and one acceptance report.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report

### Status

Attempt 1 submission: blocked, with implementation committed and pushed but required final executable validation incomplete. Architect disposition on 2026-11-03: Changes Requested; returned to `ready` with the claim cleared. Attempt 2 corrected the canonical fixtures and C01 schedule and published commit `d39246f`, but is returned as `blocked`: a stable full canonical run and mandatory paired M04/M05 measurements were not obtained. The submitted Attempt 1 evidence and Architect Review below are retained unchanged as history. Attempt 2 is not submitted for acceptance.

### Files Changed

See implementation commits `b3e2b80` and `e20cecc` in `moda-interact-api`. The follow-up commit fixes strict types for narrowed projection payloads and the PostgreSQL race-test harnesses. Changes are limited to the exact API source, test and runner paths in this task's edit map, including the two named ARCH-055 PostgreSQL suites and the new settings runner. No schema/migration, package aggregate wiring, parent architecture, other repository, or gitlink was changed.

### Work Completed

- Category GET now verifies principal, catalogue, profile and environment configuration inside a read-only RepeatableRead transaction; profile/catalogue helpers accept the transaction client.
- Category publication tracks new lineage, assigns revision 1 without lineage-history reads only for that branch, and conditionally publishes a pending draft by id/promptId/DRAFT with exactly one affected row.
- Feature preference reads use narrowed selections while preserving all current revision hash inputs; `initial.*` and `final.*` timings are separately captured. Sequential upserts, persisted timestamp reload and current no-op behavior are retained.
- Recovery-policy and AI-delay reads select their consumed fields while preserving distinct replay behavior and AI-delay validation/defaults.
- Recovery summary uses one parameterized tenant-bound LEFT JOIN statement and retains identity checks, defaults, override expiry/source, and cause-preserving invalid-policy errors.
- Added canonical migration-backed settings runner, coherent-category race suite, C03a/b/c feature interleaving suite, and SQL/affected-row measurements for retained batching/context no-op candidates. The ARCH-035 runner now includes the C03 suite; package aggregate wiring and the ARCH-054 runner remain unchanged.
- Database conflict wrappers touched by the implementation retain original Prisma causes. Bootstrap projection and store-context behavior were not broadened.

### Validation Results

- PASS: `npx --no-install tsx --test tests/unit/merchant/store-categories/*.test.ts` — 24 passed after the category read/publication changes.
- PASS: focused category-read unit suite — 6 passed after moving reads into RepeatableRead.
- PASS: focused `feature-preferences`, `recovery-policy`, and `ai-response-delay` unit suites — 43 passed after projection/timing edits.
- PASS: recovery-summary service unit suite — 6 passed after consolidating the query.
- PASS: focused feature-preference timing/no-op unit suite — 3 passed; verifies all eight initial/final timing fields for changed updates and absence of final phases for no-op.
- PASS: focused follow-up ESLint over the six changed type-fix files and `git diff --check`.
- PARTIAL: complete task unit command ran 87 tests: 85 passed and 2 failed in the unchanged Store Context route log assertions. The failures observe additional original-error metadata emitted by the shared logger (`errorName`, `errorMessage`, `errorStack`, `errorCause`) compared with the assertions' expected payload. No Store Context route or unit-test file was changed by this task.
- FAIL (unchanged baseline): `npm run lint` reports only `src/merchant/support/routes.ts:75` (`no-empty`); this file is outside the task's changed-file set. Focused lint on the changed files passes.
- INCOMPLETE: `npm run typecheck` generated Prisma Client 6.19.3. Its first completed compiler result listed 26 errors in feature-preference narrowing and the new/existing query-event integration harnesses. Follow-up fixes were committed in `e20cecc`; a rerun remained active for several minutes without a compiler exit result and was stopped. A direct `npx --no-install tsc --noEmit -p tsconfig.json` produced no diagnostics in the tool response, but no explicit exit status was captured, so no final typecheck pass is claimed.
- NO RESULT: `node scripts/test-arch055-merchant-settings-postgres.mjs` advanced through canonical migrations into the five-suite test process on its first launch, but the terminal did not return its test output or cleanup result. A rerun also returned no attributable result while other ARCH-055 API tasks were concurrently running migration validation. `node scripts/test-arch035-feature-preferences-postgres.mjs`, `node scripts/test-arch041-cross-domain-postgres.mjs`, and `node scripts/test-arch054-ai-response-delay-postgres.mjs` were not run to a recorded result. The new PostgreSQL suites therefore have no recorded migration/fixture identity, SQL result, race outcome, rollback proof, or resource-cleanup confirmation.
- Evidence encoded in the tests but not yet observed on PostgreSQL: first lineage expects zero revision-history SELECTs; existing lineage expects two; pending draft expects zero pre-read SELECTs and one conditional UPDATE; context equal-value writes retain one UPDATE/one affected row each and stale principal yields zero rows; a 20-preference changed set retains 20 sequential upsert statements/rows; C03a/b/c use an upsert barrier and a second Prisma client. These are assertions, not claimed measurements.
- Measurement limitation retained by design: category prompt eligibility still reads `promptText` because the current JavaScript `trim()` whitespace semantics do not have a verified equivalent narrow projection in this task. Existing unit coverage includes whitespace-only prompt text. Feature batching and store-context no-op suppression remain unchanged pending actual SQL/workload validation.

### Worktree and Git Evidence

- Used prepared launcher packet: parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-003`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-003`; both on `task/ARCH-055-API-003`. No preparation, claim, dependency or submodule setup was repeated.
- Launcher evidence: Attempt 1, executor `copilot`, dependency gate passed, nested Database pin `7c377282aa5819b3008b7d7f3018f44f4161523e`.
- Implementation commit `b3e2b80` (`feat(api): consolidate merchant settings projections`) was pushed to `origin/task/ARCH-055-API-003`.
- Follow-up implementation commit `e20cecc` (`fix(api): type narrowed settings projections and race tests`) was pushed to `origin/task/ARCH-055-API-003`.
- Parent task/report blocker commit `fba966a` is pushed to `origin/task/ARCH-055-API-003`. No parent implementation gitlink was changed or staged.

### Deviations

Required final validation could not be completed because PostgreSQL runner output was not captured and TypeScript compilation did not provide a final exit result while other ARCH-055 task validations were running concurrently. The task remains blocked; no unverified PostgreSQL behavior or typecheck result is represented as passing. Full lint and the complete task unit matrix have the failures recorded above; unrelated baseline files were not edited.

### Assumptions

Prepared launcher state and the stated accepted Database pin are authoritative. Canonical migration/test behavior and disposable-container cleanup remain unverified because the runner did not produce an attributable final result.

### Unresolved Issues

- Resolve the two Store Context unit log-shape failures only if they are determined to be new regressions; otherwise record the verified baseline comparison. Do not edit unrelated Support code solely to clear the existing lint failure.
- Capture a final `npm run typecheck` result and run the complete unit command, all four PostgreSQL runners, full lint, and final `git diff --check` with attributable exit results.
- Specifically observe C01/C02 and exact C03a/b/c state, HTTP/service outcomes, revision comparisons, SQL/rows, rollback, migration identity and resource cleanup. Only then may the task move to review.

### Architectural Concerns

None identified. Optional changed-row batching, store-context no-op suppression and prompt-text narrowing remain evidence-only/retained as required by the task.

### Attempt 2 Correction Evidence — 2026-11-03

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-API-003`; parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-API-003`; both use `task/ARCH-055-API-003`. Attempt 2 launcher claim commit: `df4320abd9d998e44e6a4c6274de42f644b75839`. Task-start implementation SHA: `e20ceccafeade2c53bdb5ec5942b65a9ccffcc43`. Nested Database pin: `7c377282aa5819b3008b7d7f3018f44f4161523e`.
- Commit `d39246f` (`fix(api): correct canonical ARCH-055 fixtures and read race`) was created and pushed. It corrects slug/key prefixes, the active-category timestamp field and pending draft tuple, uses a valid revoked installation status/timestamp pair, leaves trigger-protected immutable category/template/revision rows to disposable database teardown, isolates C01 reader SQL, and awaits the gated reader during teardown. No migration or schema edit was made.
- Canonical command `node scripts/test-arch055-merchant-settings-postgres.mjs` applied all 68 migrations on repeated runs. The latest delivered run passed 6/8 tests: both bootstrap cases, store-context, and all three category-selection cases. C01 and the following category-read test failed after the C01 read transaction exceeded Prisma's default 5-second interactive timeout (14,631 ms elapsed); the C01 failure caused runner teardown, so the following test then lost connectivity to mapped port `127.0.0.1:32841`. An earlier run passed 7/8 tests; the remaining bootstrap fixture's missing `pendingPromptRevisionId` was corrected in `d39246f`. Earlier intermediate runs were 2/8 and 5/8 while fixture corrections were still in progress. Commit `de096e2` increases only the C01 test wrapper's transaction timeout to 30 seconds; editor diagnostics report no errors, but this adjustment has not been run. There is therefore no clean final canonical-suite pass or verified final runner cleanup result.
- `get_errors` reported no editor diagnostics in the five changed integration files. This is not a substitute for `npm run typecheck`. No attributable Attempt 2 full typecheck, unit matrix, lint, final `git diff --check`, feature-preferences PostgreSQL, cross-domain PostgreSQL, or AI-delay PostgreSQL result was captured. C03a/b/c were not rerun in Attempt 2.
- The C01 test passed in a canonical-run attempt after changing the order to pause the RepeatableRead reader before publication B, commit B through the writer, release the read, and assert old A plus fresh B. Writer SQL counting now excludes by-ID lineage validation and the independent reader connection. The test's `finally` releases and awaits the reader.
- **M04/M05 paired measurement evidence remains outstanding.** The measurement baseline is `e20ceccafeade2c53bdb5ec5942b65a9ccffcc43`; the current corrected candidate is commit `de096e2`. No baseline/candidate two-warm-up plus five-restored-sample set was captured for any mandatory variant, and there are no recorded raw SQL/transaction/row/timing/retry/external-port tables. Do not infer metrics from test assertions or partial suite durations.
- The terminal became unresponsive during a bounded rerun attempt; after it recovered, a rerun exposed the exact 5-second C01 transaction timeout above. The test-only timeout correction is committed and pushed but remains unvalidated. Required paired measurements and remaining validations are outstanding. The architect reviewed this Attempt 2 evidence on 2026-11-03 and returned the task to `ready`, with executor and claim cleared for Attempt 3. This is not acceptance; no downstream task was started, no main merge or gitlink update occurred.

## Architect Review

### Review Status

**Changes Requested — Attempt 1, 2026-11-03.** Not accepted. Return to `ready`, preserve Attempt 1 and clear `executor`/`claimed_at` so the launcher can prepare the correction attempt.

### Review Notes

1. **P2 — Repair canonical migration-backed fixtures and cleanup.** Independent `node scripts/test-arch055-merchant-settings-postgres.mjs` applied all 68 migrations but finished with **1 passed, 7 failed**. Bootstrap/category fixtures use bare UUID slugs/keys that can violate `CommercePromptTemplateCategory_slug_check` / `CommercePromptTemplate_key_check`. Store-context's revocation fixture sets `revokedAt` on an ACTIVE installation, violating `WooCommerceInstallation_status_revoked_at_check`. The new coherent-read test's finally block deletes protected prompt revisions (`arch055-coherent-read.postgres.test.ts:184`), raising `ARCH021 agent prompt revisions cannot be deleted` and masking its original failure. Adapt the task-owned fixtures and teardown to canonical constraints without weakening migrations or triggers; preserve the primary failure if cleanup also fails. These fixtures are this task's explicit migration-runner responsibility, not an unrelated baseline waiver.
2. **P2 — Correct the C01 publication/read barrier order.** In `arch055-coherent-read.postgres.test.ts:93`, category B is fully committed before `read.read()` starts at line 114. The gate at lines 115–116 performs no concurrent publication, yet line 118 expects category A. RepeatableRead cannot return pre-transaction state in that schedule. Start the read while A is current, pause after its snapshot is established, commit B through an independent transaction, release the read and assert coherent A; a fresh read must return coherent B. Keep independent query-count cases separate if needed and reach the later pending-draft rollback assertions.
3. **P2 — Supply required M04/M05 paired evidence and completed validation.** The submission has test assertions but no executed baseline/candidate comparison for the fixed profiles in `docs/architecture/ARCH-055/task-definition-contract.md:69–70`. Capture the task-start SHA and candidate SHA, matching schema/fixtures, two warm-ups and five restored-fixture samples per version/variant, actual SQL/transaction shapes, returned/affected rows, timings, retries and external-port counts. Retaining batching/context no-op behavior and prompt text is allowed; it does not waive required measurements. Record successful remaining PostgreSQL runners including C03a–c, and verify any claimed unit/lint baseline failures with attributable results.

### Reviewed Files

Reviewed the `fa2a857..e20ceccafeade2c53bdb5ec5942b65a9ccffcc43` implementation diff: category read/publication, feature preference selections/timing/routes, recovery policy and AI-delay projections, recovery summary join, changed unit/integration tests and PostgreSQL runner registration. Reviewed the canonical definition, frozen evidence protocol and Completion Report at parent `d1992a5da6b3ac093b5ca519fb7be1a2a1809efe`. Both published task refs matched their local heads before this overlay; implementation was clean.

### Validation Reviewed

- Independent **PASS**: `npm run typecheck`, including Prisma Client 6.19.3 generation and TypeScript compilation, exit 0 with Node 24.19.0. This resolves the submission's missing final compiler result for the reviewed candidate.
- Independent **FAIL**: canonical merchant-settings PostgreSQL runner, **8 tests: 1 passed, 7 failed, 0 skipped**, after all 68 migrations applied. The runner reported failure during its test phase. The uniquely named disposable container was removed; a subsequent Docker inventory contained no matching settings-runner containers.
- Independent **PASS**: `git diff --check fa2a857..HEAD`.
- Independent required unit matrix: **87 tests, 85 passed, 2 failed**, matching the reported Store Context route logger assertions. Store Context runtime and unit-test files are unchanged from `fa2a857`; a separate baseline execution was not performed, so this is not a claimed verified baseline pass. Submitted focused unit results and documented lint failure were reviewed. The other three required PostgreSQL runners have no recorded passing result and were not independently rerun after the concrete settings-suite failures were established.

### Architecture Conformance

Source inspection supports the chosen read-only RepeatableRead category boundary, conditional pending-draft update, genuinely-new-lineage shortcut, preserved feature fingerprint inputs/sequential upserts, separate initial/final timing names, narrowed policy/AI-delay reads and tenant-bound summary join. Acceptance is withheld for the concrete validation defects and missing evidence above. No schema, product-policy or discretionary optimisation change is requested.

### Follow-up

Correct the three findings on the same implementation branch, run the required validation and attach observed evidence to this report before resubmission. Keep historical submission limitations distinguishable from new results. `ARCH-055-API-009` and `ARCH-055-SYSTEM-TEST-001` remain `pending`; API-003 is not complete, so no downstream promotion is justified. No implementation changes, implementation commits/pushes, gitlink changes or main merges were made during this review.

### Attempt 2 Disposition — 2026-11-03

**Changes Requested — Attempt 2.** Return to `ready` for Attempt 3; preserve Attempt 1 and Attempt 2 evidence, and clear `executor`/`claimed_at`. This is not acceptance. The fixture corrections and reordered C01 race remain in scope, but the latest recorded canonical run is 6/8: C01 exceeded Prisma's default interactive-transaction timeout and the subsequent category-read test lost its database connection during runner teardown. The test-only 30-second timeout correction (`de096e2`) has not been validated. Required paired M04/M05 evidence and the remaining task validation matrix are still outstanding. Do not mark the task Complete, promote downstream tasks, change the Architect Review history above for Attempt 1, merge to main, or update a gitlink. The next executor must obtain a fresh launcher claim and complete the remaining evidence before resubmission.

### Executor Reassignment — 2026-11-03

At the developer’s explicit request, moda_architect reviewed the stranded Attempt 3 Copilot claim and returned this task to `ready` for a fresh Codex launcher claim. Both canonical task worktrees were clean. Implementation history retains `de096e2` and the existing mainline synchronization merge `3f6ae2b`; no uncommitted implementation was discarded. The parent worktree retains its launcher synchronization merge `6ba66d183`. Clear `executor` and `claimed_at`, preserve `attempt: 3`, all prior implementation/report evidence and the Changes Requested correction contract. The next successful `/moda-task` preparation increments to Attempt 4 with `executor: codex`. This reassignment is not acceptance; all outstanding validation and M04/M05 evidence remain required, and no dependent task is promoted. No implementation source, implementation commit/push, parent gitlink or main branch was changed by this reassignment.
