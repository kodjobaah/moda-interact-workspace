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
status: blocked
priority: 20
executor: codex
claimed_at: 2026-11-03T10:19:32Z
attempt: 1
depends_on:
- ARCH-055-BACKGROUND-001
enables:
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-03
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

- [x] Update only the new-command identity construction and claim binding.
- [x] Update affected fixtures with the persisted field and retain historical replay fixtures.
- [x] Test same request key across two Shopify Shops and the producer-side shape expected by Background; leave cross-platform runtime exercise to ARCH-055-SYSTEM-TEST-001.

## Interfaces / Contracts

Producer of ARCH-055-DATABASE-001's persisted command contract; consumer acceptance dependency is ARCH-055-BACKGROUND-001. Cross-platform validation is terminal in ARCH-055-SYSTEM-TEST-001, not a prerequisite for this implementation.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

- `ARCH-055-BACKGROUND-001` must have `status: complete` and an accepted review.

## Enables

- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Every new Shopify template command and its claimed attempt share the generated internal key.
- [x] Public retries retain their original command and request-key identity.
- [x] HUMAN_TEXT and all existing window/entitlement/template behaviour remain unchanged.
- [x] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [x] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [x] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| K01 | Two Shops submit same key and same-Shop exact/conflicting replay | Distinct internal identity across Shops; exact replay same command; conflicting payload unchanged rejection. |
| K02 | Template insert fails after claim; HUMAN_TEXT success | Transaction rollback; human text key null and unchanged behaviour. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [x] `npx vitest run tests/unit/arch040-shopify-command.test.ts tests/unit/arch047-shopify-follow-up-sender.test.ts`
- [x] `npm run typecheck`
- [x] `git diff --check`
- [x] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [x] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

Add focused tests to the existing files/fixture rather than a new UI or a parallel send service. Record the accepted Database pin and actual generated-client version.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report

### Status

Attempt 1 implementation is committed and all required executable checks pass. **Blocked on explicit publication authorization**: automatic approval review rejected pushing private implementation commit `9e3f0af51d307b82cb9b30b020c0aa3472db15e4` to the verified existing origin `https://github.com/kodjobaah/moda-interact.git`, branch `task/ARCH-055-SHOPIFY-001`, because the exact payload/destination lacks explicit approval. No push workaround was attempted. The parent report is local as well. This task has not been submitted for architect review or accepted; Attempt 1/Codex claim is preserved.

### Files Changed

- `app/services/recoveries/recovery-human-commands.server.ts`
- `tests/unit/arch040-shopify-command.test.ts`
- `tests/fixtures/arch047-shopify-follow-up.ts`

The authoritative sender suite is unchanged and was run as required. No new file, schema/migration, dependency, consumer, UI, locale, public schema, other implementation repository, parent gitlink or shared index/frontier was edited.

### Work Completed

- Allocates one Node `randomUUID()` only after exact/conflicting replay resolution for a new command. Template `command.id`, `command.followUpClaimKey` and the sequence-two `attempt.initiationKey` are identical.
- HUMAN_TEXT has an explicit generated ID and SQL-null `followUpClaimKey`. Its template-parameter SQL-null sentinel remains `Prisma.DbNull`.
- Public `shopId/idempotencyKey` uniqueness and original payload hash are unchanged. Exact retries reuse their original command; conflicting payloads retain idempotency_conflict. Historical templates with the backfilled public retry key are returned without allocation, claim or rewrite.
- Command create selects only id/state/kind; replay/status selection and explicit public DTOs exclude the private claim field. Existing recovery, service-window, entitlement, restriction, due-time, template/publication/WABA and control-revision checks and Serializable transaction are retained.
- Fixture creates echo the supplied ID/kind instead of returning a fabricated fixed ID or HUMAN_TEXT kind for every insert. New tests cover cross-Shop identity, current/historical template replay, conflicting reuse, text null claims and original insertion-error propagation after the claim.

### Validation Results

Executed from the canonical implementation worktree using the workspace Node bootstrap:

| Command | Observed outcome |
|---|---|
| `npm ci --ignore-scripts` | Successful locked install in the new worktree; no manifest/lock change. |
| `npm run prisma:generate` | Exit 0; generated Prisma Client **6.19.3** from the recorded Database schema. |
| `npx --no-install vitest run tests/unit/arch040-shopify-command.test.ts tests/unit/arch047-shopify-follow-up-sender.test.ts` | Exit 0; **2 files, 44 tests passed**, Vitest 4.1.11, no failures. |
| `npm run typecheck` | Exit 0; React Router type generation and TypeScript compilation. |
| `npm run lint` | Exit 0; no baseline exemption required. |
| `git -c core.fsmonitor=false diff --check` | Exit 0, also checked staged changes before commit. |

Node **24.19.0**, npm **11.17.0**. A read-only Git diff initially reported an fsmonitor IPC warning; subsequent Git checks used a command-local core.fsmonitor=false override, without changing repository configuration. No workspace doctor or unrelated baseline investigation was necessary.

**Regression matrix**
- **K01 — pass (producer unit boundary):** Two distinct Shopify Shop/conversation/recovery fixtures submit the same public retry key and get different valid UUIDs. Each insert retains its Shop/public key/hash; its claim and persisted internal field equal its own command ID. Exact same-Shop replay returns the original response and allocates no UUID/claim/insert; a changed payload rejects. Historical template replay retains the original ID/state/backfilled key, performs no claim/insert and returns no private field.
- **K02 — pass (producer transaction/error boundary):** An injected original Prisma P2002 error from command insertion propagates by exact object identity after the sequence-two update. The claim and command insert execute within one Serializable callback, with claim invocation preceding insertion. HUMAN_TEXT succeeds with a null claim key and no sequence-two update. These assertions establish producer transaction placement/rejection, not physical PostgreSQL rollback or constraint behavior.

**Before/after write-shape evidence and limits**

| Branch | Starting producer | Candidate producer |
|---|---|---|
| New template | Database-default command ID; omitted/new-row-null followUpClaimKey; attempt initiationKey=public retry key | Explicit generated command ID; followUpClaimKey=same ID; initiationKey=same ID |
| New text | Database-default command ID; null private claim by default; no sequence-two claim | Explicit generated command ID; explicit null private claim; no sequence-two claim |
| Exact replay | Original command/public key and response; no new insert/claim | Same; UUID spy also confirms no ID allocation |

No query removal/batching or optional optimisation is selected by this task. Tests observe one logical command insert and one conditional claim update for the valid existing-PENDING template fixture; replay observes no new writes. These are **mock client invocations**, not emitted SQL or observed affected database rows. No SQL/bytes/latency/physical rollback measurement is claimed. The task's specific Test Registration assigns real cross-platform PostgreSQL/Background proof to terminal **ARCH-055-SYSTEM-TEST-001**, explicitly excluding an invented implementation prerequisite here. The public select/DTO shape is asserted separately. No provider, Redis or R2 I/O was introduced or executed; unit tests use deterministic mocked boundaries.

### Worktree and Git Evidence

Prepared launcher packet is the authoritative startup evidence:

- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-SHOPIFY-001`; `task/ARCH-055-SHOPIFY-001`, newly created.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-SHOPIFY-001`; same task branch, newly created. Starting SHA `a70cecad638fa634f14262978a6d0f3c2cb11e62`.
- Parent task fast-forward not-needed; origin/main already-current at prepared HEAD `53aecb45926ca3e33a56a0532bf6e618a55642fc`. Implementation task fast-forward not-needed; origin/main already-current.
- Dependency gate passed: ARCH-055-BACKGROUND-001 Complete. Attempt 1, executor codex, claimed `2026-11-03T10:19:32Z`. Launcher claim commit `8d2a0e24789010c67d0688c90a8cf3f1d6d54137` was committed/pushed. No second claim or startup synchronization.
- Recursive submodule sync/update passed; recorded Database pin `8e74634ff92be9900f693c0c449ffce888e7d617` ready. followUpClaimKey exists in its schema and generated client. No submodule pointer/schema/migration change.
- Shared workspace/source checkout switched or mutated for task work: no. Another task worktree reused: no.
- Implementation `9e3f0af51d307b82cb9b30b020c0aa3472db15e4` contains exactly the three listed files, with clean worktree. Its push was rejected before execution by automatic approval review, pending explicit authorization for `https://github.com/kodjobaah/moda-interact.git` / `task/ARCH-055-SHOPIFY-001`.
- Parent writes are limited to this current task file; Architect Review is preserved verbatim. No main push/merge, force-push, index/frontier edit, parent gitlink or downstream promotion.
- No disposable database/container, live provider connection or persistent runtime resource was created by this task. Prisma generation and unit workers completed normally; no container cleanup was needed.
- No remote review submission is claimed. On publication authorization, push implementation/report on their mirrored task branches, then transition to review and return for moda_architect review. Do not self-accept.

### Deviations

None in implementation scope or behavior. Actual SQL/physical rollback proof remains with the explicitly assigned terminal validation rather than being inferred from mocks. Publication is blocked by automatic approval review.

### Assumptions

The prepared dependency gate, pinned Database/client and ARCH-055 ADR-02 contract are authoritative. Unit tests establish producer arguments/control flow; they do not prove cross-platform database constraints or Background execution.

### Unresolved Issues

Explicit authorization to publish the private implementation and current task report to their existing GitHub repositories is outstanding. Preserve Attempt 1 and its claim while resolving publication; no new execution attempt, acceptance or enabled task is authorized by these test results.

### Architectural Concerns

No new cross-repository/schema/Shared/provider/UI contract gap found. Real cross-platform dispatch and migrated rollback remain terminal system-test responsibility under the task's existing contract.

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
