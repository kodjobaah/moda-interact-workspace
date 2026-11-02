---
id: ARCH-055-API-001
architecture_id: ARCH-055
title: Harden installation and REST-read authorisation lifecycle
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-055-DATABASE-001
enables:
- ARCH-055-API-007
- ARCH-055-API-009
- ARCH-055-SYSTEM-TEST-001
created: '2026-11-02'
updated: '2026-11-02'
---

# ARCH-055-API-001: Harden installation and REST-read authorisation lifecycle

## Architecture

Architecture: `ARCH-055`. Parent: `docs/architecture/ARCH-055-woocommerce-api-database-correctness-and-efficiency.md`. Coordinator: `moda_architect`.

**Definition state:** defined but not materialised. No developer worktree, branch, commit, push or execution claim has been created in this snapshot-only session. Initial status is `pending` solely from the dependency graph below.

## Objective

Deliver one coherent installed-merchant lifecycle boundary covering reconnect, REST-read attempt/grant transitions and the nearby brand write, with protected principal revalidation and bounded redundant reads.

## Context

Source: the 1 November 2026 workspace snapshot and the 2 November 2026 completed database review. Covered endpoint entries: `E01`, `E02`, `E07`, `E09`, `E10`, `E11`, `E12`, `E13`. Consult `docs/architecture/ARCH-055/review-ledger.md` for the original evidence; `docs/architecture/ARCH-055/endpoint-task-map.csv` fixes the primary owner of every route. New architectural choices are explicitly frozen in the parent's ADR sections; they are not retrospectively claimed as facts from the review.

## Scope

One owning repository: `moda-interact-api`. Paths below are relative to that repository. Directory entries are bounded to this task's requirements, not authority for unrelated refactoring.

- `src/auth/woo-installation/`
- `src/woocommerce/installation/`
- `src/woocommerce/billing/initial-free-activation.service.ts`
- `src/woocommerce/billing/free-plan-preparation.service.ts`
- `src/woocommerce/shop-brand/`
- `src/woocommerce/rest-read/authorization.service.ts`
- `src/woocommerce/rest-read/authorization.routes.ts`
- `src/woocommerce/rest-read/return-locale-proof.ts`
- `tests/unit/woocommerce/installation/`
- `tests/unit/woocommerce/rest-read/`
- `tests/unit/woocommerce/shop-brand/`
- `tests/integration/woocommerce/installation/`
- `tests/integration/woocommerce/rest-read/`
- `tests/integration/woocommerce/shop-brand/`
- `scripts/test-woocommerce-installation-postgres.mjs`
- `scripts/test-woocommerce-rest-read-authorization-postgres.mjs`
- `scripts/test-arch049-shop-brand-postgres.mjs`

Required new paths (only these are allowed to be absent at startup):

- `src/auth/woo-installation/current-mutation-principal.ts`

## Out of Scope

No unrelated platform redesign, generic repository-wide ORM/auth/cache rewrite, new microservice/queue, speculative index migration, live payment/refund certification, public schema version change, autonomous follow-on task, or implementation outside the owning repository. No `_index.md` edits. Keep retained endpoint behaviour under regression, rather than manufacturing source changes for every reviewed route.

## Requirements

1. Implement ADR-01/04. Add the API-local current-mutation-principal port specified below. Lock Shop first, then the installation; validate canonical URL, shop binding, platform, Shop ACTIVE, installation ACTIVE/unrevoked and expected credential version. Return transaction-local Shop fields for callers; no root-client query or network operation is allowed in this helper. ARCH-055-API-007 consumes it later.

2. Reconnect: reuse the transaction-local Shop/onboarding result in Free activation, and use a guarded returning update for credential rotation. Keep the pre-proof observed-version CAS, Serializable retry policy, exact Free lifetime grant, paid-subscription preservation and site-control proof outside transactions. Make feature-graph loading lazy or narrow on warm Free-plan reuse only after SQL validation; do not remove transaction-local policy/catalogue rechecks.

3. Brand first creation: use the create result instead of immediately selecting it again. Preserve source ordering, worker-maintained media JSON, first-writer coordination, current installation check and writes that advance genuinely newer observation timestamps.

4. REST begin/revoke: validate the current principal in the mutation transaction. Revoke only the current generation's still-PENDING attempts; terminal FAILED cancellation must not fail solely because expiry elapsed while waiting. Leave already-unusable old-generation attempts out of the cancellation set. Cancel attempts and revoke the selected grant atomically; never claim provider-side key deletion.

5. Callback: provider verification remains outside the transaction. Revalidate lifecycle/version when committing; use Database mint guards; recognise a completed matching replay after a conditional-consumption or serialization race without issuing another grant or rotating a revoked one. Superseded/mismatched attempts remain conflicts. Correct overlap acknowledgement without returning success for all failures.

6. Begin/callback/revoke errors retain actual Prisma/provider causes and distinguish invalid/stale requests from unexpected dependency failures. Generic 409/503 output does not justify discarding diagnostics. Return-page impossible-proof preflight may avoid configuration reads only if it reuses existing parser rules.

7. Keep GET installation at one authenticated lookup and REST status non-locking. Measure latest-attempt ordering plans; do not add its proposed index without separate architect approval. Catalogue/status projections may be narrowed, not credential-cached.

8. Convert installation tests to canonical migrations and adjust fixtures to actual constraints. Do not globally change unrelated category/bootstrap tests in the same shared harness; ARCH-055-API-003 owns their fixture changes and ARCH-055-API-009 performs final aggregate wiring.

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

- [ ] Implement the transaction-only current-principal helper and integration tests.
- [ ] Correct revoke/callback schedules and original-error boundaries before optional query changes.
- [ ] Consolidate reconnect and brand create-result reads with full rollback/replay tests.
- [ ] Use migrated installation/authorisation fixtures; test overlap callbacks, old pending attempt + reconnect + new grant + revoke, stale authenticated revoke, expiry while waiting, suspension during verification, and post-revoke replay.
- [ ] Measure warm/cold connection paths and report latest-attempt query plans without speculative index DDL.

## Interfaces / Contracts

New API-local file `src/auth/woo-installation/current-mutation-principal.ts`: export `requireCurrentWooMutationPrincipal(tx: Prisma.TransactionClient, principal: WooInstallationPrincipal): Promise<CurrentWooMutationPrincipal>`. The returned readonly projection contains `shopId`, `installationId`, `credentialVersion`, `canonicalSiteUrl`, `shopDomain` and `onboardingCompleted`. It accepts only a transaction client and always requires ACTIVE mutation eligibility. Use an exported typed conflict error with original cause where applicable; callers map it to their existing safe public contract. This helper is not for suspended-Shop Support GETs, pure authentication probes or unauthenticated connect proof.

The public API remains unchanged except documentation corrections explicitly authorised here. Database changes are consumed only after ARCH-055-DATABASE-001 acceptance/integration. Existing published Shared package exports remain authoritative; do not import sibling source.

## Dependencies

- `ARCH-055-DATABASE-001` must have `status: complete` and an accepted review.

## Enables

- `ARCH-055-API-007`
- `ARCH-055-API-009`
- `ARCH-055-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Stale authenticated mutations cannot operate on a newer installed generation.
- [ ] Current-generation revocation succeeds despite unusable old pending attempts and expiry during waiting; all writes still roll back together on genuine failure.
- [ ] Matching concurrent successful callbacks acknowledge the same durable outcome without reactivation or duplicate grant.
- [ ] Reconnect preserves subscription, lifetime balances and observed-version concurrency.
- [ ] Baseline 5-call active reconnect -> 3 and 7-call first-brand -> 6 are verified as client-call targets, or an explicitly justified extra correctness check is reported separately from SQL counts.
- [ ] Original diagnostic causes survive with redaction; no new swallowed business failures or generic telemetry duplication.
- [ ] Every mandatory requirement is tested; MEASURE-FIRST retained/deferred decisions are explicitly recorded with evidence.
- [ ] Worktree/branch/commit/submodule, validation and resource-cleanup evidence is recorded without invented execution claims.

## Validation

Run from the **implementation repository** in its launcher-resolved worktree, after its documented dependency setup. New commands are labelled as task deliverables in Implementation Notes/Interfaces.

- [ ] `npm run prisma:generate`
- [ ] `npx tsx --test "tests/unit/woocommerce/installation/*.test.ts" "tests/unit/woocommerce/rest-read/*.test.ts" "tests/unit/woocommerce/shop-brand/*.test.ts"`
- [ ] `node scripts/test-woocommerce-installation-postgres.mjs`
- [ ] `node scripts/test-woocommerce-rest-read-authorization-postgres.mjs`
- [ ] `node scripts/test-arch049-shop-brand-postgres.mjs`
- [ ] `npm run typecheck`
- [ ] `git diff --check`
- [ ] Run the repository's declared linter against the exact changed source/test files; record any broader unchanged baseline failure separately.
- [ ] Record before/after SQL/affected-row evidence and deterministic concurrent rollback/replay results for this task's selected changes.

## Stop Condition

After the Work Items, Acceptance Criteria and required Validation pass, finish this Completion Report, set the task to `review`, return to `moda_architect` and STOP. Do not mark the task Complete or begin an enabled task. A required validation/contract gap is a blocked return, not a fabricated pass or unapproved workaround.

## Implementation Notes

ARCH-055-API-007 must consume this reviewed helper rather than recreate it. Preserve existing original task acceptance/history; all corrections are recorded under ARCH-055.

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
