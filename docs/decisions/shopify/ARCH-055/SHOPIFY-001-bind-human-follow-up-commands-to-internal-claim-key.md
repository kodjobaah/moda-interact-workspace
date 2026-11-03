---
id: ARCH-055-SHOPIFY-001
architecture_id: ARCH-055
title: Keep the Shopify producer compatible with shared follow-up dispatch
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-055-BACKGROUND-001
enables:
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: '2026-11-03'
---

# ARCH-055-SHOPIFY-001: Keep the Shopify producer compatible with shared follow-up dispatch

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 2. API-owned workflow / forward-migration contract; supersedes definition revision 1 without claiming an implementation attempt.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `pending` solely from the dependency graph below.

## Objective

Update the existing Shopify human-follow-up producer to write the same new internal claim identity as Woo, without changing Shopify authentication, request payloads or merchant behaviour.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E29`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `app/services/recoveries/recovery-human-commands.server.ts`
- `tests/unit/arch040-shopify-command.test.ts`
- `tests/unit/arch047-shopify-follow-up-sender.test.ts`
- `tests/fixtures/arch047-shopify-follow-up.ts`

### Exact edit map — definition revision 2

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `app/services/recoveries/recovery-human-commands.server.ts` | AFTER matching replay resolution allocate randomUUID() for a new command. Template creates command.id=followUpClaimKey and attempt.initiationKey identical in existing transaction; HUMAN_TEXT null. Explicitly select no private new field into public response. Never replace public retry key/hash. |
| `tests/unit/arch040-shopify-command.test.ts; tests/unit/arch047-shopify-follow-up-sender.test.ts; tests/fixtures/arch047-shopify-follow-up.ts` | ASSERT created command ID and claim key and template/null differentiation; update mock return fields without pretending mocks prove shared DB constraints. Retain public fields/locale/template policy. |

**Test registration:** Existing two exact vitest files in task Validation; real cross-platform PostgreSQL/Background proof belongs to terminal system test, not an invented implementation prerequisite.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. This narrow compatibility task is necessary because the inspected Shopify producer also copies input.idempotencyKey into the shared attempt. It is not a new Shopify database audit and does not change unrelated Shopify routes.

2. After replay resolution and before a new sequence-two claim, allocate one globally unique command ID with the already approved Node primitive. Set new command.id and followUpClaimKey to that same ID and set attempt.initiationKey to the identical key, within the existing transaction.

3. For HUMAN_TEXT, followUpClaimKey remains null. Keep the original shopId/idempotencyKey uniqueness, payload hash, returned HTTP fields and same-Shop replay semantics. Never allocate a fresh claim on a replay.

4. Keep the existing recovery/window/template/restriction/entitlement validation and isolation. No live provider call or new Shared package dependency is introduced.

5. Consume the ARCH-055-DATABASE-001 migration and ARCH-055-BACKGROUND-001 contract. No schema edits, consumer code edits, UI changes or 20-locale copy changes are authorised because public behaviour/copy does not change.

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

- [ ] Update only the new-command identity construction and claim binding.
- [ ] Update affected fixtures with the persisted field and retain historical replay fixtures.
- [ ] Test same request key across two Shopify Shops and the producer-side shape expected by Background; leave cross-platform runtime exercise to ARCH-055-SYSTEM-TEST-001.

## Interfaces / Contracts

Producer of ARCH-055-DATABASE-001's persisted command contract; consumer acceptance dependency is ARCH-055-BACKGROUND-001. Cross-platform validation is terminal in ARCH-055-SYSTEM-TEST-001, not a prerequisite for this implementation.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

- `ARCH-055-BACKGROUND-001` must have `status: complete` and an accepted review.

## Enables

- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Every new Shopify template command and its claimed attempt share the generated internal key.
- [ ] Public retries retain their original command and request-key identity.
- [ ] HUMAN_TEXT and all existing window/entitlement/template behaviour remain unchanged.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| K01 | Two Shops submit same key and same-Shop exact/conflicting replay | Distinct internal identity across Shops; exact replay same command; conflicting payload unchanged rejection. |
| K02 | Template insert fails after claim; HUMAN_TEXT success | Transaction rollback; human text key null and unchanged behaviour. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npx vitest run tests/unit/arch040-shopify-command.test.ts tests/unit/arch047-shopify-follow-up-sender.test.ts`
- [ ] `npm run typecheck`
- [ ] `git diff --check`
- [ ] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

Add focused tests to the existing files/fixture rather than a new UI or a parallel send service. Record the accepted Database pin and actual generated-client version.

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

### Dependency promotion — 2026-11-03

ARCH-055-BACKGROUND-001 is Accepted and Complete at Attempt 2 (`311055da5f44461dc8c53e0c2f908b20c8382164`). This task is now Ready, Attempt 0, unclaimed. Its dependency edge and implementation scope are unchanged; the launcher owns preparation and the first execution claim.
