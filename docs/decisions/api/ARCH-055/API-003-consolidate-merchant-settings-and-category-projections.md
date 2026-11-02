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

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Category GET must return a coherent profile/configuration selection: use one actual statement or a short read-only Repeatable Read snapshot. Do not use FOR UPDATE to serialize GETs. Test publication between former reads. Do not transfer complete prompt text merely to calculate eligibility unless exact whitespace semantics cannot yet be preserved in a tested projection.

2. Category publication remains Serializable and atomic. For a newly created lineage, skip redundant draft/latest-history lookups and publish revision one; existing lineages keep their checks. Fold pending-draft ownership/status validation into an exact-one conditional update. Preserve subscription, generation, source-evidence and configuration guards.

3. Feature GET keeps its consistent snapshot/fingerprint and narrows unused relation fields. Feature PUT keeps current revision checking, entitlement/editability gates, Shop/installation coordination and persisted-timestamp final reload. Correct overwritten timing phase names using the existing timing facility; do not add a second generic telemetry layer.

4. Feature changed-row batching is MEASURE-FIRST. Record normal and large changed sets, emitted SQL, rollback and concurrent Admin eligibility changes; retain sequential upserts/final reload if no safe validated improvement is established. Do not use Promise.all as proof of parallel transaction SQL and do not remove the final reload speculatively.

5. Recovery-policy and AI-delay reads select only consumed fields, retaining settings/admin-override snapshots and read-only no-row defaults. PUTs keep their intentionally different replay rules: recovery-policy may acknowledge identical old-revision replay; AI-delay checks revision before same-value no-op. Keep integer 0..30 AI minutes, default zero, AI-only applicability and no new scheduling behaviour.

6. Store-context no-op suppression is MEASURE-FIRST and may only proceed with atomic distinction between changed, authorised-already-equal and invalid/stale principal. Do not turn legitimate no-ops into conflicts or stale-principal zero-row updates into success. Bootstrap retains its already narrow nonmutating projection.

7. Recovery summary remains policy presentation rather than metrics aggregation. Adopt a single tenant-bound statement snapshot for identity/settings/override if consolidating; retain defaults, override expiry/source and safe invalid-state handling. It does not become outbound permission.

8. Preserve original causes in all touched domain wrappers. Consolidate read-only identity queries locally only where every field/predicate survives; do not introduce a universal auth cache or weaken mutation locks. Migrate category/bootstrap/context fixtures rather than weakening canonical constraints. ARCH-055-API-009 owns package.json aggregate wiring for the existing AI-delay runner.

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

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npx tsx --test "tests/unit/merchant/store-categories/*.test.ts" "tests/unit/merchant/store-context/*.test.ts" "tests/unit/merchant/feature-preferences/*.test.ts" "tests/unit/merchant/recovery-policy/*.test.ts" "tests/unit/merchant/ai-response-delay/*.test.ts"`
- [ ] `node scripts/test-woocommerce-installation-postgres.mjs`
- [ ] `node scripts/test-arch035-feature-preferences-postgres.mjs`
- [ ] `node scripts/test-arch041-cross-domain-postgres.mjs`
- [ ] `node scripts/test-arch054-ai-response-delay-postgres.mjs`
- [ ] `npm run typecheck`
- [ ] `git diff --check`
- [ ] Run the repository's declared linter against the exact changed source/test files; record any broader unchanged baseline failure separately.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

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
