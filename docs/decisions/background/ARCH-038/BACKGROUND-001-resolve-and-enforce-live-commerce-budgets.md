---
id: ARCH-038-BACKGROUND-001
architecture_id: ARCH-038
title: Resolve and enforce LIVE per-turn CommerceAgent budgets
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-038-DATABASE-001
enables:
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-14
---
# Resolve and enforce LIVE per-turn CommerceAgent budgets

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_background`
- Repository: `moda-interact-background`

## Objective

Resolve the exact LIVE Platform/Price Plan/Merchant precedence on each admitted Background CommerceAgent turn and enforce the frozen effective limits.

## Context

The existing Background Commerce host sends a 90-second remaining envelope and no merchant-specific output-token budget to Shared; this must be replaced or reconciled, not masked by partial logging changes.

## Scope

- Load environment-scoped `CommerceModelPolicy` LIVE rows for trusted Shop and current Subscription; validate `budgetSchemaVersion`, overlay sparse JSON keys in Platform → Price Plan → Shop precedence, and resolve each value with independent source/edit-version details.
- Match eligible current ACTIVE/TRIALING Subscription.plan -> BillingPlan.shopifyPlanHandle -> MerchantPricingPlan.shopifyPlanHandle; ignore pending plans.
- Freeze policy for the admitted turn/retry and pass exact supported deadlineMs/outputTokens to runCommerceTurn.
- Reconcile worker lease, job timeout, cancellation and existing execution envelope with configured deadline; reject unsupported configuration explicitly rather than silently clipping.
- Use shared structured logging and focused database-backed integration tests.

## Out of Scope

- Do not alter Shopify/Woo merchant UI or edit Admin policy.
- Do not reimplement Shared runner or introduce a Background-local generic logger.
- Do not consult PREVIEW policy or Environment variables intended for Studio Preview.

## Requirements

- Merchant -> current Price Plan -> Platform per field; missing JSON budget key inherits, explicit null/invalid/unknown-version policy fails closed.
- No effective plan from pending/cancelled/unmatched plans. Preserve existing subscription lifecycle rules and Woo canonical plan mapping.
- Policy changes during an active turn cannot mutate its frozen limits; retry/resumption identity is explicit.
- No hidden 90-second cap remaining when accepted configuration specifies a different supported deadline.
- Log chosen limits, sources, environment and bounded identifiers; no customer text or secrets.

## Work Items

- [ ] Implement indexed read + precedence resolver and snapshot.
- [ ] Wire effective budgets to runtime and reconcile worker/timeouts.
- [ ] Add per-field inheritance, plan-switch/race, tenant, provider and deadline integration cases.

## Interfaces / Contracts

Consumes DATABASE-001 `CommerceModelPolicy` rows filtered to `context=LIVE`, with a versioned `budget` object and provenance, together with the published `@modainteract/moda-interact-shared` `runCommerceTurn` budget contract.

## Dependencies

- `ARCH-038-DATABASE-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Each turn uses exact effective limits and verified source labels.
- [ ] Plan changes affect only subsequently admitted turns.
- [ ] Wrong-shop or pending-plan override never applies.
- [ ] Deadline/lease mismatches produce a clear error rather than silent truncation.

## Validation

- [ ] Focused resolver unit tests
- [ ] Disposable PostgreSQL plan/policy integration
- [ ] Worker deadline/cancellation/retry regression
- [ ] Relevant typecheck/build and git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-BACKGROUND-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. The task is materialized on the published parent task branch. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

Changes Requested — Attempt 1 reviewed. Attempt remains 1; task is ready with no active claim. Implementation commit `7fb5c25bb2c6e2ab4ef14c55d78135d0c45613f6` is published on the matching implementation task branch.

### Files Changed

- `database` submodule pointer (to ARCH-038-DATABASE-001 commit `40674aea91527d5645aa922c9627af673b487223`)
- `package.json`
- `scripts/test-arch038-live-budget-contract.mjs`
- `scripts/test-arch038-live-budget-postgres.ts`
- `src/commerce/host-diagnostics.ts`
- `src/commerce/host.ts`
- `src/commerce/live-budget.ts`
- `tests/integration/commerce/host.test.ts`

### Work Completed

- Added a LIVE-only policy resolver that reads the trusted Shop's current ACTIVE/TRIALING subscription and canonical BillingPlan-to-MerchantPricingPlan handle, filters policy rows by environment and `LIVE`, validates schema v1, and overlays sparse deadline/token values by Platform → Price Plan → Shop in a RepeatableRead transaction.
- Added immutable per-invocation resolved budget/provenance, fail-closed diagnostics and structured budget logging; passes configured output tokens and deadline to Shared and uses the configured deadline for the host abort signal.
- Added processing-lease compatibility validation against the existing 120-second lease with a 2-second completion reserve; unsupported limits fail rather than being silently clipped.
- Added focused resolver contract tests, a disposable PostgreSQL migration/resolver proof, and host budget wiring assertions.

### Validation Results

- `npm run test:arch038-live-budgets` — **PASS**, 7/7 tests.
- `npm run test:arch038-live-budgets:postgres` — **PASS** against the ordered disposable PostgreSQL migrations; container cleanup completed.
- `npm run build` — **PASS**; Prisma Client generation and TypeScript compilation completed.
- `npm run test:integration -- tests/integration/commerce/host.test.ts` — **FAIL**, 12 passed / 49 failed. The host test helper injects a hard-coded `DEVELOPMENT` budget while the disposable integration harness resolves `TEST`; preflight rejects with `TEST_BUDGET_ENVIRONMENT_MISMATCH`, so most existing host assertions never exercise their intended behavior.
- A direct `npx vitest run tests/integration/commerce/host.test.ts` attempt did not run tests because repository Vitest configuration excludes `tests/integration/**`; the supported disposable integration harness was then used.
- `git diff --check origin/main...HEAD` — **PASS**.
- No changes were made to the implementation during review. The disposable integration harness removed its container; implementation, parent task and nested database worktrees are clean.

### Deviations

- The host integration test harness was not updated to inject a budget tagged with the harness's resolved `TEST` environment. The initial 49 failures are therefore validation-blocking fixture failures rather than 49 independently established runtime regressions.
- Budget snapshots are immutable only within one `executeCommerceHost` invocation. The task architecture requires policy to remain frozen for retries/resumptions of an admitted turn with explicit retry identity. Current failure handling releases the conversation lease; a later job can reclaim the same inbound version and `executeCommerceHost` rereads policy. The contract test explicitly proves the same identity can then observe changed policy. No persisted retry/snapshot identity currently binds these invocations.

### Assumptions

The implementation does not yet satisfy the ARCH-038 requirement that an admitted turn and its retry/resumption use one frozen budget snapshot. A post-failure retry can pick up policy edits despite retaining the same inbound version. The persisted/in-memory admission contract needs an explicit retry identity and a snapshot lifecycle that keeps these values stable without making the policy stale for new turns.

### Unresolved Issues

- A policy edit between a failed attempt and retry of the same inbound version changes the retry's effective budget; this violates the architecture's frozen per-admission/retry contract.
- All host integration assertions must execute under the disposable `TEST` environment. Update the injected test budget environment from the resolved harness configuration, then rerun the full host integration suite and confirm intended assertions reach model/MCP execution.
- Add retry/resumption regression coverage: resolve a turn budget, change policy, retry the same admitted identity and prove the frozen values and provenance are reused; then admit a new turn and prove it reads the new policy.
- Preserve and verify same-shop/current-plan precedence, tenant isolation, pending/cancelled-plan behavior, retry identity, and lease/deadline/cancellation behavior after snapshot changes.
- Rerun `npm run test:arch038-live-budgets`, `npm run test:arch038-live-budgets:postgres`, the host integration harness, `npm run build`, and `git diff --check`.

### Architectural Concerns

The implementation worktree is the launcher-resolved `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-BACKGROUND-001` on `task/ARCH-038-BACKGROUND-001`; its clean HEAD `7fb5c25bb2c6e2ab4ef14c55d78135d0c45613f6` matches `origin/task/ARCH-038-BACKGROUND-001` and contains current `origin/main`. The canonical parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-BACKGROUND-001` is clean on the same task branch and current mainline. Its database submodule is clean at published DATABASE-001 commit `40674aea91527d5645aa922c9627af673b487223`. The shared Background checkout has unrelated dirty `database` and untracked `typescript` entries; they were left untouched. No implementation changes or task-agent assistance occurred during this review.

## Developer Self-Review - Changes Requested

### Review Status

Changes Requested. Attempt 1 remains the reviewed attempt; do not increment it during reconciliation.

### Required Corrections

- Persist or otherwise durably associate the resolved LIVE budget/provenance with an explicit admitted-turn retry identity so failures, lease release/reacquisition and job resumption for the same inbound version reuse the snapshot. A subsequently admitted turn must resolve the then-current policy. Add the same-admission-retry versus new-admission regression described above.
- Make the host integration test fixture use the environment resolved by the disposable harness rather than hard-coding `DEVELOPMENT`. Rerun the host suite and verify it reaches its intended assertions; do not count the current 12/61 result as passing runtime validation.
- Rerun every required focused check after corrections: resolver contract, disposable PostgreSQL, host worker/deadline/cancellation/retry integration, build/typecheck and `git diff --check`.

### Decision

Return the task to `ready`, clear `executor` and `claimed_at`, and preserve `attempt: 1`. Do not create Attempt 2 here and do not merge either task branch into `main`.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation

### Follow-up

None
