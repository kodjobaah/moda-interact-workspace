---
id: ARCH-055-API-007
architecture_id: ARCH-055
title: Harden durable billing-command admission
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-055-API-001
enables:
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: '2026-11-02'
---

# ARCH-055-API-007: Harden durable billing-command admission

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition revision:** 3. Small acceptance clarification over revision 2; execution metadata, dependencies and migration scope are unchanged.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `pending` solely from the dependency graph below.

## Objective

Admit new financial commands only for the current installed principal while preserving durable intent/provider/outcome separation and bounded exact replay behaviour.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E54`, `E55`, `E56`, `E58`, `E59`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-api`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `src/billing/commands/`
- `src/woocommerce/billing/woo-billing-client.ts`
- `src/woocommerce/billing/webhooks/ [retain/regression only]`
- `src/composition/billing.ts`
- `tests/unit/billing/commands/`
- `tests/unit/woocommerce/billing/`
- `tests/integration/billing/commands/`
- `tests/integration/woocommerce/billing/webhooks/`
- `scripts/test-arch041-billing-postgres.mjs [commands only]`
- `src/auth/woo-installation/current-mutation-principal.ts [provided by accepted ARCH-055-API-001; consume only]`
- `src/woocommerce/billing/initial-free-activation.service.ts [consume reviewed helper; no unrelated Free policy change]`

### Exact edit map — definition revision 2

Paths are relative to the owning implementation repository. These steps are mandatory; they do not authorise schema/migration changes outside DATABASE-001. Existing broad directory entries above are bounded by these named operations and the checked-in deterministic-execution-map.json. Preserve every unrelated field, public DTO, predicate and script registration.

| File / symbol touchpoint | Deterministic edit |
|---|---|
| `src/billing/commands/recurring-intent.ts; src/billing/commands/recovery-credit-intent.ts` | CALL accepted API-001 current-principal helper at new/replay transaction admission before Subscription lock; reuse its locked Shop fields. Do not resolve credentials after persisting a new intent. Keep original expected revision/current quote comparisons. |
| `src/billing/commands/recurring-intent.ts` | Replace all recurring history load/sort with bounded findFirst over exact unresolved OR applicable confirmed cancellation predicate; include provider reference and Free-terminal-reset exception, not last-N history. |
| `src/billing/commands/recurring-outcome.ts; src/billing/commands/recovery-credit-outcome.ts` | Use guarded returning update for a winning outcome; retain zero-row reread and provider-reference advisory/collision guards. No post-admission rotation veto on valid evidence. |
| `src/billing/commands/recovery-credit-intent.ts; src/woocommerce/billing/initial-free-activation.service.ts` | Select purchase ID only from create. Reuse accepted materialisation contract from API-001, preserving warm/cold validation and no early paid/credit activation. |
| `src/woocommerce/billing/woo-billing-client.ts` | Preserve original transport/read/parse cause, HTTP status and bounded safe provider details through typed errors; public/durable codes unchanged; do not log headers/raw bodies/confirmation URLs or retry uncertain writes. |

**Exact new implementation/test paths (not baseline files claimed to exist):**

- `tests/integration/billing/commands/arch055-installation-admission.postgres.test.ts`

**Test registration:** Append to scripts/test-arch041-billing-postgres.mjs, which already owns billing migrations/outcomes. Fixture must create a real installation/authenticator, not a constructed principal only.

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Adopt ADR-04: inside the first intent transaction, use the ARCH-055-API-001 helper to require current installation binding/version, ACTIVE/unrevoked state and ACTIVE Woo Shop. Preserve Shop -> installation -> Subscription coordination. Test real authentication followed by rotation/revocation before admission for create, cancel, switch and credit purchase. Reject stale admission without provider call or durable intent.

2. After an intent has committed, later credential rotation must not discard verified provider outcome evidence. Provider I/O remains between transactions. Configuration is resolved before a new intent; do not move it after persistence and strand INITIATING records. Existing replays continue their exact current-quote/fingerprint policy.

3. Keep atomic operation/purchase creation, zero usable purchased credits until verified reconciliation, Free versus paid-period eligibility, same-provider-contract switch checks, cancellation grace/paid coverage and provider uncertainty. No immediate entitlement activation, proration or blind external retry is introduced.

4. Reuse the helper's locked Shop/onboarding fields. For recurring new-command blockers, replace all-history loading/sorting with a bounded exact predicate for unresolved operations or applicable confirmed cancellation. Keep the terminal-Free-create exception and provider-reference qualification; do not inspect only the latest few rows.

5. Use a conditional update returning the actual operation on the winning outcome branch. Keep the zero-row reread because another writer's newer durable result wins. Preserve create/purchase provider-reference advisory locking/collision checks and switch contract identity.

6. Narrow purchase create return to ID. For warm operational-plan reuse, avoid unnecessary target-feature graph loading while retaining pre-provider materialisation and exact quote checks. Coordinate with the reviewed ARCH-055-API-001 materialisation helper rather than copying it.

7. Preserve actual provider transport/response/parse failures, HTTP status and bounded safe response details through causes to the shared logger. Keep public and durable reason codes safe, never log raw bodies/credentials/confirmation capabilities, and never turn richer diagnostics into retries of uncertain writes.

8. Billing webhook remains the exact raw-body-digest receipt-only acceptance path. Do not add installed auth, Shop lookups, outbox, Redis publication or a duplicate-path preliminary read.

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

- [ ] Introduce transaction-local principal admission using the accepted helper.
- [ ] Bound recurring blocker history and reuse locked/write-return projections.
- [ ] Improve warm materialisation projections without moving its boundary.
- [ ] Preserve provider error causes and safe response evidence.
- [ ] Run real-auth rotation/revocation and post-admission outcome schedules plus existing financial race fixtures.

## Interfaces / Contracts

Consumes ARCH-055-API-001 current-mutation-principal port and existing canonical billing persistence. Provider-facing API and public command schemas remain unchanged. Additional correct authorization work is recorded separately from isolated query savings.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

### Exact billing admission errors — revision 3

This fixes the NEW helper-to-domain mapping without changing provider-facing operations or existing replay/quote errors. Source vocabulary/envelopes: `recurring-intent.ts:66–77`, `recovery-credit-intent.ts:38–57`, `commands/routes.ts:68–98,142–165` and `command-http.ts:96–112`.

| Operation / condition | Exact HTTP result | Persistence / external-operation result |
|---|---|---|
| POST `/v1/billing/subscription`: current-principal helper rejects | `409`, JSON `{"error":"billing_shop_invalid"}` | No new operation, materialised plan or subscription change commits; zero subscription-create provider calls. |
| DELETE `/v1/billing/subscription`: helper rejects | `409`, JSON `{"error":"billing_shop_invalid"}` | No new CANCEL operation; zero provider DELETE calls. |
| POST `/v1/billing/subscription/switch`: helper rejects | `409`, JSON `{"error":"billing_shop_invalid"}` | No new SWITCH operation or target materialisation commits; zero switch provider calls. |
| POST `/v1/billing/recovery-credit-purchases`: helper rejects | `409`, JSON `{"error":"billing_shop_invalid"}` | No new purchase/operation/credits; zero purchase provider calls. |
| Same stale gate on a request whose idempotency key already exists | Same endpoint-specific `409`/`billing_shop_invalid` result | Existing operation/purchase remains unchanged; no replay/provider call. This retains revision 2's gate before both new and replay admission. |
| Missing/invalid installed HTTP credentials | `401`, JSON `{"error":"unauthorized"}` | Admission is never called. |
| Unexpected helper-read database exception, distinct from the typed mismatch/recognised existing domain retry | `500`, JSON `{"error":"internal_error"}` | Roll back admission; no provider call; preserve original exception for existing internal-error logging. |

Recurring intents map only `instanceof WooMutationPrincipalConflictError` to `RecurringBillingCommandError(409, "billing_shop_invalid", undefined, undefined, { cause: error })`. Purchase intents map it to `RecoveryCreditPurchaseCommandError(409, "billing_shop_invalid", undefined, undefined, undefined, { cause: error })`. Append optional `ErrorOptions` after the existing constructor parameters in `recurring-command-error.ts` and `recovery-credit-command-error.ts`, and pass it to `super`; preserve existing callers. For these pre-admission errors omit `operationId`, `purchaseId` and `providerErrorCode` entirely, not null. Do not map arbitrary Prisma/provider failures to this mismatch. Domain wrappers retain the internal helper and its cause without exposing diagnostic details in JSON.

Provider configuration resolution stays BEFORE new-intent persistence as already defined: unavailable configuration still returns `503`/`billing_provider_unavailable`, with no intent/provider call. Gate-race tests therefore provide valid configuration; they must not accidentally test configuration failure instead. Configuration reads/unsealing are not external financial operations. Rotation only AFTER intent commit retains G02: persist the provider outcome, not a new admission error.

Extend the existing `tests/unit/billing/commands/subscription-routes.test.ts` and `recovery-credit-routes.test.ts` for exact envelopes; the named `arch055-installation-admission.postgres.test.ts` must exercise real authentication and barrier-controlled rotation/revocation/suspension for all four routes, including one existing-key replay. Assert unchanged row counts/balances and zero provider-method invocations on rejection. No new files, public schemas or retry semantics are introduced by this mapping clarification.

## Dependencies

- `ARCH-055-API-001` must have `status: complete` and an accepted review.

## Enables

- `ARCH-055-API-009`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] A request authenticated before rotation cannot admit a new financial intent after rotation wins.
- [ ] An admitted operation still converges from valid provider evidence after later rotation.
- [ ] Exact replay fingerprint/quote behaviour, cancellation grace and credits remain unchanged.
- [ ] Returning-update zero-row losers return the newer persisted outcome rather than overwrite it.
- [ ] Receipt webhook fresh/duplicate behaviour remains unchanged and all required concurrent-insert regressions pass.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

### Required regression matrix — definition revision 2

Tests extend the named existing suites and the exact new files listed in Scope. Every row must have an assertion and a recorded outcome. Use two independent connections and explicit barriers for interleavings; a sleep or mocked call count is not proof of locking.

| Case | Fixture / operation | Required result |
|---|---|---|
| G01 | Real auth then reconnect/revoke/suspend before create/cancel/switch/purchase admission; repeat with an existing key | Exact revision-3 table: 409 billing_shop_invalid without IDs, no new durable rows/provider calls; unchanged existing rows. Unknown helper-read failure is 500 internal_error. Current principal still works. |
| G02 | Rotate only after admitted intent commits, then provider outcome arrives | Persist valid outcome; no credit/paid activation before verified reconciliation. |
| G03 | No matching operation/older unresolved/confirmed cancellation/different contract/Free reset | Bounded blocker exactly equivalent to original policy; never latest-only. |
| G04 | Outcome conditional update loses to newer durable result | Return winner by reread; no downgrade or invented success. |
| G05 | Transport/HTTP/parse/config failure and repeated request | Original redacted diagnostics; existing safe output and no blind provider resend. |

No new Prisma models/fields/constraints/indexes or migrations are authorised in this repository task. Consume the accepted Database pin only where required. All migration corrections, including changes to installed functions/CHECKs, belong in new forward scripts owned by DATABASE-001 or a later explicit Database scope amendment. Never edit an applied migration, reset schema or supply an automatic down migration.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `node scripts/test-arch041-billing-postgres.mjs`
- [ ] `npx tsx --test "tests/unit/billing/commands/*.test.ts" "tests/unit/woocommerce/billing/*.test.ts" "tests/unit/woocommerce/billing/webhooks/*.test.ts"`
- [ ] `npm run typecheck`
- [ ] `git diff --check`
- [ ] Run `npm run lint`; record any broader unchanged baseline failure separately without changing unrelated files.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

- [ ] Assert all four billing gate mappings, existing-key rejection and unchanged post-admission outcomes; record zero financial provider calls on rejected admission.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

No provider sandbox/payment/refund certification is claimed by local tests. Do not call live providers with fixture credentials; use the approved deterministic provider boundary and preserve any outstanding external certification requirement.

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
