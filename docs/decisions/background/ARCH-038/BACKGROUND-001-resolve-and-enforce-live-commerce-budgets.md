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
status: review
priority: 20
executor: null
claimed_at: null
attempt: 2
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

Resolve the exact LIVE Platform/Price Plan/Merchant precedence for each Background CommerceAgent execution and enforce the selected limits for that invocation. A retry is a new execution and may use a newer policy.

## Context

The existing Background Commerce host sends a 90-second remaining envelope and no merchant-specific output-token budget to Shared; this must be replaced or reconciled, not masked by partial logging changes.

## Scope

- Load environment-scoped `CommerceModelPolicy` LIVE rows for trusted Shop and current Subscription; validate `budgetSchemaVersion`, overlay sparse JSON keys in Platform → Price Plan → Shop precedence, and resolve each value with independent source/edit-version details.
- Match eligible current ACTIVE/TRIALING Subscription.plan -> BillingPlan.shopifyPlanHandle -> MerchantPricingPlan.shopifyPlanHandle; ignore pending plans.
- Resolve the current policy at the start of each `executeCommerceHost` invocation (including retries); keep that invocation’s resolved values fixed while it runs and pass exact supported `deadlineMs`/`outputTokens` to `runCommerceTurn`. Do not persist a retry-wide budget snapshot.
- Reconcile worker lease, job timeout, cancellation and existing execution envelope with configured deadline; reject unsupported configuration explicitly rather than silently clipping.
- Use shared structured logging and focused database-backed integration tests. Test request orchestration through the real Shared `OpenRouterModelClient`/LangChain `ChatOpenRouter` against a local AI Mock HTTP server, never a paid AI provider.

## Out of Scope

- Do not alter Shopify/Woo merchant UI or edit Admin policy.
- Do not reimplement Shared runner or introduce a Background-local generic logger.
- Do not consult PREVIEW policy or Environment variables intended for Studio Preview.

## Requirements

- Merchant -> current Price Plan -> Platform per field; missing JSON budget key inherits, explicit null/invalid/unknown-version policy fails closed.
- No effective plan from pending/cancelled/unmatched plans. Preserve existing subscription lifecycle rules and Woo canonical plan mapping.
- A policy edit must not alter limits already resolved for an in-flight invocation. A later invocation, **including a retry of the same inbound turn**, resolves the then-current LIVE policy. No dedicated Redis key, cache, or durable per-retry budget snapshot is required; existing conversation ordering and fencing still apply.
- No hidden 90-second cap remaining when accepted configuration specifies a different supported deadline.
- Log chosen limits, sources, environment and bounded identifiers; no customer text or secrets. The disposable integration launcher must set `DEPLOYMENT_ENVIRONMENT_NAME=test` for its child process, and policy fixtures must resolve `TEST` through the same environment resolver as the host; do not inherit arbitrary developer/production environment values.

## Work Items

- [x] Implement indexed read + per-invocation precedence resolution (without a Redis or persisted retry snapshot).
- [x] Wire effective budgets to runtime and reconcile worker/timeouts.
- [x] Add per-field inheritance, plan-switch/race, tenant, provider and deadline integration cases, including an unchanged in-flight budget and a fresh-policy retry of the same inbound identity.
- [x] Add a local AI Mock HTTP orchestration integration exercising the real `OpenRouterModelClient` and `ChatOpenRouter` with test-only loopback `baseURL`, dummy key, request journal assertions and fail-closed provider egress. Keep test suites modular rather than extending a monolithic `host.test.ts`.

## Interfaces / Contracts

Consumes DATABASE-001 `CommerceModelPolicy` rows filtered to `context=LIVE`, with a versioned `budget` object and provenance, together with the published `@modainteract/moda-interact-shared` `runCommerceTurn` budget contract.

## Dependencies

- `ARCH-038-DATABASE-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Each turn uses exact effective limits and verified source labels.
- [x] Policy or plan changes affect subsequent **executions**, including retries of the same inbound turn; an invocation already running retains the budget it resolved.
- [x] Wrong-shop or pending-plan override never applies.
- [x] Deadline/lease mismatches produce a clear error rather than silent truncation.
- [x] Automated model orchestration exercises the production SDK against loopback AI Mock only, with dummy credentials, zero real AI-provider calls, and assertions for request model, tool definitions, output-token limit, call ordering and tool-result propagation.

## Validation

- [x] Focused resolver unit tests
- [x] Disposable PostgreSQL plan/policy integration
- [x] Worker deadline/cancellation/retry regression: a second invocation of the same inbound identity may resolve updated policy; an already-running invocation remains unchanged
- [x] Disposable Commerce host integration under `DEPLOYMENT_ENVIRONMENT_NAME=test` with matching `TEST` policy fixtures
- [x] Local AI Mock + real `OpenRouterModelClient`/LangChain HTTP request-orchestration tests; verify fail-closed behavior without any external AI-provider requests
- [x] Compatible published Shared runner budget contract (no obsolete product-level 800-output-token ceiling); relevant typecheck/build and git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-BACKGROUND-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. The task is materialized on the published parent task branch. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Architect decision reconciliation (2026-10-14)

The original Attempt 1 self-review below is historical evidence against the **previous** frozen-across-retries contract. The subsequently agreed LIVE semantics supersede that particular acceptance requirement: resolve the current policy at the beginning of **each execution**, including retry/resumption; keep its resolved limits stable only while that invocation runs. Do not add Redis or PostgreSQL snapshot storage solely for this feature. This change does **not** waive tenant isolation, ordering/fencing, lease validation, test coverage or any other review issue.

Background disposable orchestration tests run with `DEPLOYMENT_ENVIRONMENT_NAME=test`, with matching TEST policy fixtures. Automated model calls use the actual Shared runner and `OpenRouterModelClient`/LangChain SDK against a local AI Mock HTTP server using dummy credentials and fail-closed network isolation. No paid or external model inference is permitted in these tests. Studio PREVIEW conversation-snapshot semantics remain unchanged.

This reconciliation does not change `status`, `attempt`, `executor`, `claimed_at`, developer completion mode, the historical Completion Report, or the pending Architect Review. Current implementation results must still be validated and reported by the developer.

## Completion Report

### Status

Review — Attempt 2 developer self-review passed on 2026-10-14. Task remains in `review` because `completion_mode: developer`; explicit developer completion is pending. Attempt 1 review history is preserved below.

### Files Changed

- `database` submodule pointer (to ARCH-038-DATABASE-001 commit `40674aea91527d5645aa922c9627af673b487223`)
- `package.json`
- `scripts/test-arch038-live-budget-contract.mjs`
- `scripts/test-arch038-live-budget-postgres.ts`
- `src/commerce/host-diagnostics.ts`
- `src/commerce/host.ts`
- `src/commerce/live-budget.ts`
- `tests/integration/commerce/host.fixture.ts` and modular `host-suites/` test files (`ai-mock`, `authority`, `budgets`, `diagnostics`, `evidence`, `grants`, `language`, `lifecycle`)
- `tests/integration/commerce/host.test.ts`
- `vitest.config.ts`

### Work Completed

- Added a LIVE-only policy resolver that reads the trusted Shop's current ACTIVE/TRIALING subscription and canonical BillingPlan-to-MerchantPricingPlan handle, filters policy rows by environment and `LIVE`, validates schema v1, and overlays sparse deadline/token values by Platform → Price Plan → Shop in a RepeatableRead transaction.
- Added per-invocation resolved budget/provenance, fail-closed diagnostics and structured budget logging; passes configured output tokens and deadline to Shared and uses the configured deadline for the host abort signal. Each new execution, including a retry of the same inbound identity, resolves the current LIVE policy; values remain fixed for that invocation.
- Added processing-lease compatibility validation against the existing 120-second lease with a 2-second completion reserve; unsupported limits fail rather than being silently clipped.
- Added focused resolver contract tests and disposable PostgreSQL migration/resolver proof.
- Split the Commerce host integration into focused suites and corrected fixtures to use the disposable harness's `DEPLOYMENT_ENVIRONMENT_NAME=test` policy namespace.
- Added a local AI Mock HTTP orchestration test using the real Shared `OpenRouterModelClient` and LangChain `ChatOpenRouter`, dummy credentials, loopback-only URL enforcement, request-journal assertions and tool-result propagation checks.

### Attempt 1 Validation and Review History

Attempt 1's host integration run reported 12 passed / 49 failed because fixtures supplied `DEVELOPMENT` budgets while the disposable harness resolved `TEST`. The old retry-frozen snapshot concern was superseded by the Architect decision recorded above: policy is resolved once per execution, including retries, and is stable during that invocation. Both corrections were addressed and revalidated in Attempt 2; the previous results remain historical, not current blockers.

### Attempt 2 Validation Results

- `npm run test:arch038-live-budgets` — **PASS**, 7/7 contract tests, including per-invocation policy resolution and fail-closed deadline/lease bounds.
- `npm run test:arch038-live-budgets:postgres` — **PASS** against disposable PostgreSQL migrations; disposable container cleanup completed.
- `npm run test:integration -- tests/integration/commerce/host.test.ts` — **PASS**, 62/62 tests under the harness-provided `DEPLOYMENT_ENVIRONMENT_NAME=test`, including same-inbound subsequent execution policy refresh and the local AI Mock SDK orchestration suite.
- `npm run build` — **PASS**; Prisma Client generation and TypeScript compilation completed.
- `git diff --check origin/main...HEAD` — **PASS**.
- Implementation worktree is clean and `HEAD` matches `origin/task/ARCH-038-BACKGROUND-001` (0/0 divergence). Parent claim/report worktree was clean before this report update; its claim commit is published.
- No paid or external AI provider was used. AI orchestration used the local loopback AI Mock with a dummy credential.

### Attempt 2 Execution Evidence

Physical worktree isolation:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-BACKGROUND-001`, branch `task/ARCH-038-BACKGROUND-001`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-BACKGROUND-001`, branch `task/ARCH-038-BACKGROUND-001`
- Both worktrees reused; remote task fast-forwards were not needed; `origin/main` was already incorporated.
- Recursive submodule sync and update passed; `database` initialized at `40674aea91527d5645aa922c9627af673b487223`.
- Shared workspace and shared Background checkout were not switched for this attempt; the pre-existing Background `database` modification was left untouched.

### Attempt 2 Deviations and Unresolved Issues

None known. The host suite, disposable PostgreSQL test, focused contract suite and build passed. No task-owned implementation changes remain uncommitted.

## Developer Self-Review - Changes Requested (Attempt 1 Historical)

### Review Status

Changes Requested. Attempt 1 remains the reviewed attempt; do not increment it during reconciliation.

### Required Corrections

- Persist or otherwise durably associate the resolved LIVE budget/provenance with an explicit admitted-turn retry identity so failures, lease release/reacquisition and job resumption for the same inbound version reuse the snapshot. A subsequently admitted turn must resolve the then-current policy. Add the same-admission-retry versus new-admission regression described above.
- Make the host integration test fixture use the environment resolved by the disposable harness rather than hard-coding `DEVELOPMENT`. Rerun the host suite and verify it reaches its intended assertions; do not count the current 12/61 result as passing runtime validation.
- Rerun every required focused check after corrections: resolver contract, disposable PostgreSQL, host worker/deadline/cancellation/retry integration, build/typecheck and `git diff --check`.

### Decision

Return the task to `ready`, clear `executor` and `claimed_at`, and preserve `attempt: 1`. Do not create Attempt 2 here and do not merge either task branch into `main`.

## Developer Self-Review - Passed (Attempt 2)

### Review Status

Passed. The Attempt 1 corrections were addressed: the disposable host suite now uses the harness-resolved TEST environment, and the updated LIVE policy contract resolves current values at each execution while keeping the budget fixed during that invocation. Focused contract and disposable PostgreSQL tests, the 62-test host integration suite (including the local AI Mock orchestration), the Background build and `git diff --check` all passed.

### Remaining Work

No known required Work Item or Acceptance Criterion remains incomplete. The implementation branch is committed, pushed and clean. Because `completion_mode: developer`, this review submits the task in `review`; explicit developer completion remains pending via `/moda_developer_update ARCH-038-BACKGROUND-001 complete`.

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
