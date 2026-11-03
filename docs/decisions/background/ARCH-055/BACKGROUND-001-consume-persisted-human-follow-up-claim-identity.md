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
status: in_progress
priority: 15
executor: codex
claimed_at: 2026-11-03T03:09:27Z
attempt: 1
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

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `pending` solely from the dependency graph below.

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

- [ ] Update the command projection and all enumerated human claim-key call sites.
- [ ] Search the entire Background human-follow-up path for remaining comparisons/passes of idempotencyKey as initiationKey and account for every match.
- [ ] Add two-Shop identical-public-key, historical-key, replay/restart and cancelled-owner-versus-reclaimed-attempt cases.
- [ ] Retest provider uncertainty, permit acquisition, moderation denial, provisional-credit release and recovery after a crash between cancellation/release phases.

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

- [ ] New and migrated historical commands use the persisted ownership key consistently in every human dispatch/release path.
- [ ] No change to one-initial-plus-one-follow-up limits, billing outcomes, prepared-content bytes or automated follow-up identity.
- [ ] A malformed template command cannot dispatch or release another command's claim.
- [ ] All required focused real-database races pass with the accepted Database pin.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

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

- [ ] `npm run prisma:generate`
- [ ] `npm run test:arch040-recovery-conversation`
- [ ] `npm run test:arch040-background-runtime:postgres`
- [ ] `npm run test:arch040-moderation:postgres`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

Run task-focused lint on the exact changed files in addition to the listed suites. A deployment-safe contract requires both producers; acceptance of this consumer is not permission to resume an incomplete rollout.

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


## Dependency readiness — 3 November 2026

ARCH-055-DATABASE-001 is Accepted and Complete at Attempt 2. The accepted Database pin is `5907b4572ea9efc2a24c07e4c3bd3e107db4260b`; adopt it within this task's authorized consumer scope. The sole prerequisite is satisfied: Ready, Attempt 0, unclaimed. Prepare through the canonical launcher; no implementation, deployment or production migration is implied. Follow the Database task's coordinated migration/consumer rollout handoff.
