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
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-055-BACKGROUND-001
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: '2026-11-02'
---

# ARCH-055-API-004: Correct recovery inbox and human-send persistence

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `pending` solely from the dependency graph below.

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

- [ ] Adopt the accepted persisted claim-key contract and update human send fixtures.
- [ ] Fix prepared-content moderation status and corresponding migrated regressions.
- [ ] Bind sender configuration to the transaction and test root-client nonuse plus configuration failures.
- [ ] Replace page-navigation counts and narrow page-only projections; preserve summary evidence.
- [ ] Exercise control, human send, same-Shop replay, two-Shop identical keys, cancellation/reclaim, unknown send and moderation outcomes.

## Interfaces / Contracts

Consumes ARCH-055-DATABASE-001/BACKGROUND-001 claim identity. Configuration factory must accept `Pick<Prisma.TransactionClient, "platformConfiguration">` through the existing ApiPlatformConfigurationDatabase port; a root client remains legal only outside a transaction. The public reader interface and Shared crypto exports remain unchanged. Do not add a new Shared release solely for passing a persisted ID.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

- `ARCH-055-BACKGROUND-001` must have `status: complete` and an accepted review.

## Enables

- `ARCH-055-API-009`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Both producers and Background agree on the persisted key; a Woo API public key collision across Shops cannot contend on the global claim key.
- [ ] Prepared-content assessments appear correctly and unrelated/missing assessments never become approval.
- [ ] No root Prisma configuration query is awaited from inside the follow-up transaction.
- [ ] First/latest message pages avoid two navigation counts; first related pages avoid two counts; the remaining navigation query is bounded existence.
- [ ] No history/query optimisation weakens final admission or evidence ownership.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npm run test:arch040-human-send:postgres`
- [ ] `npm run test:arch040-conversation-control:postgres`
- [ ] `node scripts/test-arch041-cross-domain-postgres.mjs`
- [ ] `npm run test:arch043-platform-configuration:postgres`
- [ ] `npx tsx --test "tests/unit/merchant/conversations/**/*.test.ts" "tests/unit/merchant/recoveries/**/*.test.ts"`
- [ ] `npm run typecheck`
- [ ] `git diff --check`
- [ ] Run the repository's declared linter against the exact changed source/test files; record any broader unchanged baseline failure separately.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

The configuration composition file is owned by this task within ARCH-055; ARCH-055-API-007 continues using its normal root reader before intent admission. Preserve that distinction rather than globally forcing transactions.

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
