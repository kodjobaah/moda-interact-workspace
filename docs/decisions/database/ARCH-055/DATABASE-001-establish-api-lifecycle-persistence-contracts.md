---
id: ARCH-055-DATABASE-001
architecture_id: ARCH-055
title: Establish the persistence contracts required by the API corrections
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-055-BACKGROUND-001
- ARCH-055-API-001
- ARCH-055-API-005
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: '2026-11-02'
---

# ARCH-055-DATABASE-001: Establish the persistence contracts required by the API corrections

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `ready` solely from the dependency graph below.

## Objective

Deliver one reviewed, data-preserving schema/guard change set for the three persistence contracts frozen in ARCH-055: REST-read lifecycle, internal human follow-up claim identity, and immutable upload-intent/original-intake identity.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E09`, `E11`, `E12`, `E29`, `E39`, `E40`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-database`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `prisma/schema.prisma`
- `prisma/migrations/20261010120000_arch026_woocommerce_rest_read_grant/migration.sql [read-only baseline]`
- `prisma/migrations/20261017120000_arch040_recovery_human_handover/migration.sql [read-only baseline]`
- `prisma/migrations/20261019133000_arch040_follow_up_reservation_release/migration.sql [read-only baseline]`
- `prisma/migrations/20261026080000_arch040_prepared_human_message_content/migration.sql [read-only baseline]`
- `prisma/migrations/20260929160000_arch023_merchant_knowledge_schema/migration.sql [read-only baseline]`
- `scripts/validate-arch026-woocommerce-rest-read-grant.mjs`
- `scripts/validate-arch040-human-prepared-schema.mjs`
- `scripts/test-arch040-human-prepared-postgres.mjs`

Required new paths (only these are allowed to be absent at startup):

- `scripts/test-arch055-database-contracts-postgres.mjs`
- `scripts/validate-arch055-database-contracts.mjs`
- `scripts/fixtures/arch055/`

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Implement ADR-01 exactly: strengthen attempt INSERT/SUCCEEDED and grant mint/rotation checks to require the current ACTIVE Woo Shop, ACTIVE unrevoked installation, matching generation and valid expiry. Keep immutable attempt/grant identities, monotonic sequence/rotation, same-transaction consumption and deferred successful-attempt/grant coupling. Terminal PENDING -> FAILED cancellation must remain possible after expiry; it cannot mint a grant. Do not impose active-generation mint requirements on safe terminalisation of old/expired attempts. API principal gating remains a separate requirement.

2. Add `MerchantConversationSendCommand.followUpClaimKey String? @db.VarChar(255)` (SQL nullable, no client-request field). Before installing the new guard, backfill every existing RECOVERY_FOLLOW_UP_TEMPLATE command from its own persisted idempotencyKey, including terminal commands. Leave HUMAN_TEXT null. Never rewrite RecoveryOutreachAttempt.initiationKey, command IDs, external request keys, provider permits, message evidence, balances or state. Do not assume an old cancelled command still owns its attempt.

3. Add an additive BEFORE INSERT/UPDATE guard and structural constraint: template commands require a nonempty followUpClaimKey; HUMAN_TEXT requires null; the field is immutable after insertion. A NEW template command must set followUpClaimKey = its own preallocated id and link a same-recovery HUMAN attempt claimed with that key. Historical backfilled keys may differ from command.id and remain valid on later updates. Do not add a unique command-key index: historical released claims can share a former public key. Keep the existing globally unique active attempt key and immutable command-attempt binding.

4. Add `MerchantKnowledgeUploadedAsset.intentPurposeKey String? @db.VarChar(64)` with a nonblank-if-present check and immutable-value guard. Preserve the existing asset identity, object-key uniqueness, format and metadata fields. Existing unbound assets remain null; do not guess their original intent purpose or destructively reset storage. New Woo API intent writes must provide the key; this is enforced by that owning API task rather than a blanket non-null requirement on unaffected Shopify writers.

5. Add a partial unique index on MerchantKnowledgeSourceRevision(uploadedAssetId) WHERE uploadedAssetId IS NOT NULL AND reason IN ('CREATE','FILE_REPLACE'). This enforces at most one original intake revision, not one total revision per asset. REPROCESS and ENTITLEMENT_CHANGE remain legal. Before creation, detect duplicate original-intake rows and fail with bounded IDs/counts; never delete/relabel history to pass. A blocked upgrade returns to the architect.

6. Use new forward-only migrations, never edit recorded migrations. Use separate ordered migration directories within this one task for REST guards, command-claim metadata and upload metadata/index so rollback/deployment effects are auditable. Names: `20261102120000_arch055_rest_read_lifecycle`, `20261102121000_arch055_human_follow_up_claim_identity`, `20261102122000_arch055_upload_intake_identity`, unless a real migration-name collision is reported. Preserve all current prepared-content/moderation and release guards; add narrowly rather than copy an obsolete function body.

7. Do not remove speculative duplicate indexes or introduce performance indexes in this task. The report's index candidates require query-plan evidence and a later architect-approved scope amendment. No Shared publication is required: these are canonical Prisma/SQL persistence contracts.

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

- [ ] Implement the three ordered forward migrations and exact Prisma changes.
- [ ] Add fresh and upgrade fixtures, including historical cancelled/reclaimed/UNKNOWN/SENT human commands and assets with later reprocessing revisions.
- [ ] Test expired FAILED cancellation versus expired SUCCEEDED rejection, suspended-Shop mint rejection, same-transaction grant enforcement and no replay activation.
- [ ] Test new command-key binding, cross-Shop key independence, field immutability, historical backfill and untouched irreversible evidence.
- [ ] Test purpose metadata immutability, original-intake uniqueness, legal reprocessing and fail-closed duplicate-intake upgrade.
- [ ] Record migration hashes, application order, preflight results and consumer database-pin handoff; return for acceptance before consumers execute.

## Interfaces / Contracts

Owns ADR-01/02/03 persistence. Consumers: ARCH-055-API-001, ARCH-055-API-004, ARCH-055-API-005, ARCH-055-BACKGROUND-001 and ARCH-055-SHOPIFY-001. New fields are server-only; published public HTTP/queue schemas do not change. `followUpClaimKey` is read from the database by consumers, not recomputed from a public request key.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

None. The source baseline is context, not a fabricated dependency on historical review evidence.

## Enables

- `ARCH-055-BACKGROUND-001`
- `ARCH-055-API-001`
- `ARCH-055-API-005`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Fresh and upgrade canonical migrations pass on disposable PostgreSQL 17 + pgvector.
- [ ] All preserved triggers/constraints still enforce their original safety properties.
- [ ] Historical command claims remain usable with exactly their prior stored ownership identity; no attempt key is rewritten.
- [ ] Ambiguous original-intake history blocks safely with no data loss.
- [ ] Old unbound pending upload intents are explicitly documented as requiring a new client intent; completed assets/history remain intact.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npm run validate`
- [ ] `npm run prisma:generate`
- [ ] `node scripts/test-arch055-database-contracts-postgres.mjs --mode fresh`
- [ ] `node scripts/test-arch055-database-contracts-postgres.mjs --mode upgrade`
- [ ] `node scripts/validate-arch026-woocommerce-rest-read-grant.mjs`
- [ ] `node scripts/validate-arch040-human-prepared-schema.mjs`
- [ ] `git diff --check`
- [ ] Run the repository's declared linter against the exact changed source/test files; record any broader unchanged baseline failure separately.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

The two new ARCH-055 validator commands above are required deliverables, not commands claimed to exist in the baseline. The runner must provision/clean disposable pgvector/pgvector:pg17 databases itself (or reuse the existing explicitly guarded disposable harness), support fresh and baseline-upgrade modes, and refuse real/deployed database URLs. Update legacy schema assertions only where the new contract intentionally changes them; do not weaken unrelated tests.

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
