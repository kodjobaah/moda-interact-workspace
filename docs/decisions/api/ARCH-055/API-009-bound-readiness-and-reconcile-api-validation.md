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
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
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
updated: '2026-11-02'
---

# ARCH-055-API-009: Bound readiness and reconcile API validation entrypoints

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `pending` solely from the dependency graph below.

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

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Liveness remains immediate process-only HTTP with zero DB/config/provider/queue calls. Readiness remains parameter-free SELECT 1 and safe 200/503 at the existing 2,000 ms HTTP deadline; it is not a migration, Redis or business-table audit.

2. Implement ADR-08: at most one unresolved underlying readiness probe per API process, with supported finite acquisition/execution bounds and recovery after outage. Coalesce concurrent requests around that in-flight probe without caching an old success. An HTTP timeout must not clear the in-flight guard while the underlying probe is still pending.

3. Use the pinned Prisma/runtime supported timeout/cancellation mechanism and demonstrate its bounds under real blocked acquisition and execution. A dedicated bounded probe client/connection is allowed if necessary, but account for its one-connection budget and finite lifecycle. Never disconnect the shared business client per readiness failure. If existing configuration cannot enforce the bound, return the specific infrastructure requirement for architect-owned Gateway scope rather than guessing settings.

4. Add the existing AI-delay migrated suite to aggregate integration; ensure accepted installation/category/restore/recovery/history fixtures use canonical migrations, not reduced hand-made schemas or db push where guards matter. Do not author another generic test framework or rewrite unrelated suites.

5. Reconcile shared package.json/runner edits after ARCH-055-API-001..008 acceptance, preserving every accepted suite. This is why the task is pending behind those owners; it is not a separate task per test. No implementation task depends on ARCH-055-SYSTEM-TEST-001.

6. Capture real HTTP/pool recovery, emitted SQL counts, outstanding work bounds and resource cleanup. Reuse existing structured logger/framework instrumentation. Keep original probe failures internally, with safe public output and no credentials in logs.

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

- [ ] Implement bounded underlying readiness work and deterministic unit tests.
- [ ] Create the focused migrated PostgreSQL/HTTP runner using disposable pg17+pgvector.
- [ ] Register all accepted focused runners and the previously omitted AI-delay suite in aggregate integration.
- [ ] Run API typecheck/build/full integration and classify any unchanged documented baseline failures without weakening new acceptance.

## Interfaces / Contracts

Existing readiness HTTP contract is unchanged. Any introduced probe option must be internal/server-controlled, tested against the pinned runtime and listed in the completion report; no deployed pool limit or timeout is assumed from the static review.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

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

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npx tsx --test tests/unit/http/server.test.ts`
- [ ] `node scripts/test-arch055-readiness-postgres.mjs`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `npm run test:integration`
- [ ] `git diff --check`
- [ ] Run the repository's declared linter against the exact changed source/test files; record any broader unchanged baseline failure separately.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

This task owns final package.json integration-script changes so the functional tasks do not race to rewrite the same long aggregate command. It includes readiness implementation plus the directly associated operational acceptance wiring, not unrelated telemetry or infrastructure.

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
