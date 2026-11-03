---
id: ARCH-055-BACKGROUND-001
architecture_id: ARCH-055
title: Consume the persisted human follow-up claim identity
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 15
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-055-DATABASE-001
enables:
- ARCH-055-SHOPIFY-001
- ARCH-055-API-004
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: 2026-11-03
---

# ARCH-055-BACKGROUND-001: Consume the persisted human follow-up claim identity

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 2. API-owned workflow / forward-migration contract; supersedes definition revision 1 without claiming an implementation attempt.

**Definition state:** materialised on the canonical parent and implementation task worktrees. Attempt 1 was returned to `ready` after Changes Requested; Attempt 2 is Accepted and Complete after architect review on 2026-11-03.

## Objective

Make every Background human follow-up ownership check consume the command's immutable followUpClaimKey while preserving current dispatch, moderation, cancellation, uncertain-outcome and credit-release rules.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E29`, `E30`, `E31`, `E35`, `E36`, `E37`, `E40`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-background`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `src/services/recovery-conversation/merchant-send-command.service.ts`
- `src/services/recovery-conversation/human-command-dispatcher.service.ts`
- `src/services/recovery-conversation/outbound-send-fence.service.ts`
- `src/services/recovery-conversation/follow-up-claim-cancellation.service.ts`
- `src/services/recovery-conversation/recovery-follow-up-policy.service.ts [change only human-claim integration if needed]`
- `tests/unit/services/recovery-conversation/`
- `tests/integration/recovery-human-dispatch.integration.test.ts`
- `tests/integration/recovery-follow-up-claim-races.integration.test.ts`
- `src/services/merchant-knowledge-upload-cleanup.service.ts [read-only competitor]`
- `src/services/merchant-knowledge-entitlement-reconciliation.service.ts [read-only competitor]`

Additional explicit registration/module paths for this revision:

- `package.json [append new fixture to existing test command only]`

### Exact edit map — definition revision 2

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `src/services/recovery-conversation/merchant-send-command.service.ts` | ADD followUpClaimKey to command persistence projection/type; carry it unchanged to dispatch/cancel/fence/repair. Do not derive key from a request or command.id for historical records. |
| `src/services/recovery-conversation/human-command-dispatcher.service.ts; src/services/recovery-conversation/outbound-send-fence.service.ts; src/services/recovery-conversation/follow-up-claim-cancellation.service.ts` | REPLACE human attempt.initiationKey versus command.idempotencyKey ownership comparisons with stored followUpClaimKey; missing/blank template field is explicit fail-closed internal error before provider or release. HUMAN_TEXT does not require key. Every release CAS retains expected attempt/key/current owner/outcome predicates. |

**Exact new implementation/test paths (not baseline files claimed to exist):**

- `tests/unit/services/recovery-conversation/arch055-claim-key.test.ts`
- `tests/integration/arch055-follow-up-identity.integration.test.ts`

**Test registration:** Append new integration file to package.json test:arch040-background-runtime:postgres node scripts/test-integration.mjs file list; retain existing files. Existing unit directory command includes new unit test.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Adopt the accepted ARCH-055-DATABASE-001 nested database pin; do not edit nested schema or migrations locally. Include followUpClaimKey in the HumanCommand type and every command load/lease projection feeding the consumer.

2. For RECOVERY_FOLLOW_UP_TEMPLATE, require the persisted key to be present and nonblank. Pass that value to claimSequenceTwo, restart/replay lookup, send fences, cancellation-owner comparisons, repair scans and conditional claim release. Remove all human ownership comparisons to command.idempotencyKey. Do not derive a replacement key on a read, and do not change automation-initiated identities.

3. The public shop-scoped idempotencyKey remains used for HTTP replay/fingerprinting only. Historical migration-backfilled claim keys remain authoritative even when not equal to command.id. This preserves existing irreversible state without a dual lookup or attempt-key rewrite.

4. Keep Shop -> Conversation -> command -> attempt lock ordering, terminal pre-provider cancellation, durable billing-release evidence before reset, and permanent retention of dispatched/UNKNOWN/SENT claims. An old cancelled command must not release a newer owner of the same physical sequence-two attempt.

5. Preserve prepared-content moderation and current outbound fences. Do not expand this task into general cleanup/generation-worker optimisation; those existing writers are exercised as real competitors by ARCH-055-SYSTEM-TEST-001.

6. Log any malformed/missing durable claim key as an integrity failure with original cause and safe identifiers; no send or silent fallback to the public key. Keep provider errors and queue errors redacted and original.

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

- [x] Update the command projection and all enumerated human claim-key call sites.
- [x] Search the entire Background human-follow-up path for remaining comparisons/passes of idempotencyKey as initiationKey and account for every match.
- [x] Add two-Shop identical-public-key, historical-key, replay/restart and cancelled-owner-versus-reclaimed-attempt cases.
- [x] Retest provider uncertainty, permit acquisition, moderation denial, provisional-credit release and recovery after a crash between cancellation/release phases.
- [x] Preserve the original typed missing-key integrity error message/cause in private Shared-logger diagnostics and assert redaction of owner-key values.

## Interfaces / Contracts

Consumes ARCH-055-DATABASE-001's command field; keeps existing RecoveryOutreachAttempt.initiationKey semantics as the current owner's durable identity. No new queue contract, Shared helper, provider-facing identifier or worker is introduced. ARCH-055-API-004 and ARCH-055-SHOPIFY-001 are producer dependants and must not be enabled until this consumer task is accepted.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

- `ARCH-055-DATABASE-001` must have `status: complete` and an accepted review.

## Enables

- `ARCH-055-SHOPIFY-001`
- `ARCH-055-API-004`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] New and migrated historical commands use the persisted ownership key consistently in every human dispatch/release path.
- [x] No change to one-initial-plus-one-follow-up limits, billing outcomes, prepared-content bytes or automated follow-up identity.
- [x] A malformed template command cannot dispatch or release another command's claim.
- [x] All required focused real-database races pass with the accepted Database pin.
- [x] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [x] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [x] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| J01 | New Woo and Shopify key=command ID; legacy backfilled key differs | Both dispatch/cancel with their persisted key; never recompute legacy key. |
| J02 | Cancelled owner and reclaimed same attempt; old worker resumes | Old command cannot release or dispatch later owner. |
| J03 | Null/blank template key, UNKNOWN/provider-admitted/SENT command | Missing key blocks safely; no unsafe release/resend/double credit; preserve prepared-body moderation. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [x] `npm run prisma:generate` — passed using Prisma Client 6.19.3 from the accepted nested Database pin.
- [x] `npm run test:arch040-recovery-conversation` — 128 tests passed across 13 files on Attempt 2.
- [x] Focused integrity diagnostic suites (`arch055-claim-key.test.ts`, `follow-up-claim-cancellation.test.ts`, `human-synchronous-rejection.test.ts`) — 33 tests passed.
- [x] `npm run test:arch040-background-runtime:postgres` — 13 tests passed across 3 files on disposable PostgreSQL 17 + pgvector and Redis.
- [x] `npm run test:arch040-moderation:postgres` — 10 tests passed on disposable PostgreSQL 17 + pgvector and Redis.
- [x] `npm run build` — passed (includes Prisma generation and TypeScript compilation).
- [x] `git diff --check` — passed.
- [x] `npm run lint` — passed.
- [x] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

Run task-focused lint on the exact changed files in addition to the listed suites. A deployment-safe contract requires both producers; acceptance of this consumer is not permission to resume an incomplete rollout.

Implement in coherent internal commits/work packages (correctness first, bounded queries second, tests with each change). This reduces task count without creating one unreviewable all-API patch. Preserve ordinary task ownership; the architect reviews the completed unit.

## Completion Report

### Status

Accepted and Complete — Attempt 2, 2026-11-03. The Attempt 1 diagnostic finding is addressed. This implementation consumes the accepted `ARCH-055-DATABASE-001` pin `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`; no Database schema or migration was changed. Task status is `complete`; executor and claim remain cleared. SHOPIFY-001 and API-004 are promoted to Ready; SYSTEM-TEST-001 remains Pending on its other prerequisites.

### Files Changed

`src/services/recovery-conversation/merchant-send-command.service.ts`, `human-command-dispatcher.service.ts`, `outbound-send-fence.service.ts`, `follow-up-claim-cancellation.service.ts`; `tests/unit/services/recovery-conversation/` focused command and cancellation coverage; `tests/integration/fixtures/recovery-human-dispatch.fixture.ts`; new `tests/unit/services/recovery-conversation/arch055-claim-key.test.ts` and `tests/integration/arch055-follow-up-identity.integration.test.ts`; `package.json` integration-suite registration. The implementation commit also advances the nested Database gitlink to its accepted pin.

### Work Completed

Updated command reads retain `followUpClaimKey`; human sequence-two claim lookup, outbound admission, cancellation owner matching, reset CAS, and cancelled-claim repair use this stored key. `idempotencyKey` remains the public replay identity. Missing/blank template keys emit a bounded Shared-logger integrity event, durably cancel the command, and leave the attempt/credit held for repair. For the Attempt 1 correction, the dispatcher now forwards the caught typed integrity error to cancellation; cancellation and outbound-fence logs include the actual error message and Error object/cause with safe identifiers, while tests confirm the private owner key is excluded. HUMAN_TEXT and automated claim identities are unchanged.

### Validation Results

Validation was run from `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-BACKGROUND-001` on Node 24.19.0 with Prisma 6.19.3. The disposable integration runner applied canonical migrations, including `20261102121000_arch055_human_follow_up_claim_identity`, against PG17 + pgvector and Redis.

SQL and row evidence: the locked outbound projection now reads `followUpClaimKey`, and the attempt owner comparison uses that value. Cancellation repair joins `attempt.initiationKey=cmd.followUpClaimKey` and excludes null/blank keys. The reset CAS binds the persisted key; the historical-key integration case returns `released` only after the owner reset affects exactly one row. The old-owner-versus-reclaim test held a Shop lock, observed two PostgreSQL lock waiters via `pg_stat_activity`, then released the blocker; cancellation released the old owner, the next claim won the same attempt, and the resumed old worker left the new key unchanged. Two Shops with the same public idempotency key retained independent persisted owners. A null-key command ended `CANCELLED` with its attempt key and usage rows unchanged and no provider request.

No query-count/latency optimization was in scope; existing query and billing behavior was retained. No MEASURE-FIRST experiment was introduced or deferred.

Attempt 2 validation passed: the focused integrity diagnostic suites passed 33 tests; `npm run test:arch040-recovery-conversation` passed 128 tests across 13 files; Background PostgreSQL/Redis integration passed 13 tests across 3 files; moderation PostgreSQL/Redis integration passed 10 tests; `npm run build`, `npm run lint` and `git diff --check` passed. Initial attempts to start the test containers encountered a broken/slow Colima state; after the daemon recovered, the final runs above passed. The shared test runner performed disposable database/Redis cleanup. The one-off uniquely named PostgreSQL probe was removed. Other pre-existing Colima containers were left untouched.

### Worktree and Git Evidence

Launcher preparation created both task worktrees and branches. Attempt 1 review overlay was committed and pushed as `f5df0298`; the Attempt 2 claim is `984f550df8698ab855f82e43e180ea6e4261bba`. Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-055-BACKGROUND-001`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-055-BACKGROUND-001`. Both use branch `task/ARCH-055-BACKGROUND-001`. Implementation commits `46aa08c7a8fcb498a79d6b87f39e597d4c88a081`, `86747ce` and Attempt 2 correction `311055d` are pushed to `origin/task/ARCH-055-BACKGROUND-001` (head `311055d`). The nested Database checkout remains at accepted pin `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`; no new gitlink change was made. The submitted Attempt 2 parent report was published as `b117a947c4f6c6fa8a76c5da439d05b552bd14a9`; the architect acceptance overlay follows on the same branch.

### Deviations

No scope deviation. The test runner's installed Shared testing helper had its local Docker/readiness timeout temporarily increased to accommodate Colima startup latency; no dependency or source file was changed for this adjustment. A temporary probe container used to diagnose Docker startup was removed.

### Assumptions

Launcher evidence confirms the task is materialised in the canonical parent and implementation worktrees. The former portable-definition note has been reconciled; Attempt 1 review history is preserved, and Attempt 2 is submitted for review.

### Unresolved Issues

No blocking findings remain after Attempt 2 architect review. Both producer implementations and terminal system validation remain separate tasks.

### Architectural Concerns

No architectural contract, schema, provider, or transaction-boundary change was introduced. Consumer acceptance enables the producer tasks; it does not authorize deployment of an incomplete producer/consumer rollout.

## Architect Review — Attempt 1

### Review Status

Changes Requested — 2026-11-03. Task returned to `ready`; `executor` and `claimed_at` are null. Attempt 1 is preserved. No acceptance or downstream promotion.

### Review Notes

1. **[P2] Preserve the actual integrity error in private diagnostics.** `HumanCommandDispatcherService.processClaim()` catches `FollowUpClaimKeyIntegrityError` from `loadClaimedCommand()` and calls `rejectTerminal()` without logging or forwarding that error. The cancellation and outbound-fence paths emit `errorType` and `reasonCode`, but omit the error message/cause. This loses the actionable diagnostic for a malformed or missing persisted claim key despite Requirement 6 and the criterion that original diagnostic causes survive. Pass the original typed error to the existing Shared logger with safe identifiers and the bounded message; do not include the missing key value or alter fail-closed cancellation/credit-hold behavior. Add a regression asserting the emitted structured log contains the actual error type and message and excludes unsafe values.

### Reviewed Files

- `src/services/recovery-conversation/merchant-send-command.service.ts`
- `src/services/recovery-conversation/human-command-dispatcher.service.ts`
- `src/services/recovery-conversation/outbound-send-fence.service.ts`
- `src/services/recovery-conversation/follow-up-claim-cancellation.service.ts`
- `tests/unit/services/recovery-conversation/arch055-claim-key.test.ts`
- `tests/integration/arch055-follow-up-identity.integration.test.ts`
- Attempt 1 Completion Report, launcher worktree evidence, and accepted Database pin.

### Validation Reviewed

Reviewed the reported 126 unit tests, 13 Background PostgreSQL/Redis integration tests, 10 moderation integration tests, build, lint and diff checks. The barrier test uses PostgreSQL lock-wait observations and verifies a resumed old worker leaves the new persisted owner unchanged. No tests were rerun during this review.

### Architecture Conformance

The persisted key is used independently of the public idempotency key in dispatch, cancellation, repair and outbound fencing. Historical-key handling, same-public-key cross-Shop isolation, held-credit behavior for malformed keys, and the old-worker/reclaimed-owner race are supported by the submitted tests. Acceptance remains blocked by the missing original integrity-error diagnostic detail. The portable-definition paragraph has been corrected to reflect launcher materialisation.

### Follow-up

Keep the same mirrored task branches and Attempt 1. Log/forward the original typed integrity error and add the structured-log regression, rerun the focused affected checks, update the Completion Report, and resubmit. `ARCH-055-SHOPIFY-001`, `ARCH-055-API-004` and `ARCH-055-SYSTEM-TEST-001` remain gated; no dependent status is changed by this review. No implementation source was changed by the architect review.

## Architect Review — Attempt 2

### Review Status

**Accepted — 2026-11-03.** Implementation `311055da5f44461dc8c53e0c2f908b20c8382164`. Automatic-completion task moves to `complete`, retaining Attempt 2 and null executor/claim. Attempt 1 review remains historical above.

### Review Notes

The Attempt 1 P2 finding is resolved. The dispatcher forwards the original `FollowUpClaimKeyIntegrityError` through terminal cancellation. Cancellation logs that same Error object with its message and cause; direct cancellation and outbound fencing construct the typed integrity error when no originating error exists. The fields use the existing Shared logger and contain safe command/shop identifiers without the persisted owner key or attempt contents. ErrorOptions preserves the originating cause. No release, provider-admission or billing policy was relaxed.

The regression suite verifies original-error forwarding, original cause identity, bounded diagnostic message/type, private owner-key omission and held attempt/credit behavior. The outbound test's negative-string assertion alone is not a standalone redaction proof; code inspection and the cancellation test's populated private owner fixture establish omission. Shared remains responsible for serialization/redaction rather than these services introducing another logger.

### Reviewed Files and Evidence

Reviewed all seven files changed by `86747ce..311055d`, including the four runtime modules and three unit suites. Rechecked stored-key call sites across command load, dispatcher claim/restart, cancellation/repair/CAS and outbound fences. The accepted Database pin is unchanged at `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`. Both dedicated worktrees were clean, and their published task refs matched implementation `311055da5f44461dc8c53e0c2f908b20c8382164` and parent report `b117a947c4f6c6fa8a76c5da439d05b552bd14a9` before this review overlay.

### Validation Reviewed

- Independently reran `npm run test:arch040-recovery-conversation` on Node 24.19.0: **128 tests passed across 13 files**, exit 0, including the affected diagnostic regressions.
- Independently checked `git diff --check 86747ce..HEAD`: passed.
- Reviewed the submitted Attempt 2 results: 33 focused tests, 13 Background PostgreSQL/Redis integration tests, 10 moderation integration tests, Prisma generation, build and lint passed. Those integration/build/lint runs were not repeated by the architect; the reported temporary installed-helper startup-timeout adjustment affects test infrastructure only and is not a source/dependency change or production validation claim.
- Earlier persisted-key, historical-key, cross-Shop and cancelled-owner/reclaimed-attempt evidence remains applicable; this correction changes diagnostic propagation, not ownership predicates or transaction ordering.

### Architecture Conformance and Follow-up

The original diagnostic is retained while malformed keys continue to fail closed and hold claims/credits. No blocking findings remain. `ARCH-055-SHOPIFY-001` and `ARCH-055-API-004` each depend only on this task and are promoted from Pending to Ready, Attempt 0, unclaimed. `ARCH-055-SYSTEM-TEST-001` remains Pending because its remaining producer/API prerequisites are incomplete. No implementation source, implementation commit, parent gitlink, main branch or deployed environment was changed by this review. Consumer acceptance does not waive the coordinated Database/consumer/producer rollout contract.
