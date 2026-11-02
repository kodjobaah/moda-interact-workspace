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
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: '2026-11-02'
---

# ARCH-055-API-003: Consolidate merchant settings and category projections

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 3. Small acceptance clarification over revision 2; execution metadata, dependencies and migration scope are unchanged.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `ready` solely from the dependency graph below.

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
