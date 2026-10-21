---
id: ARCH-043-API-004
architecture_id: ARCH-043
title: Use database Woo billing credential pair
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 55
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-043-ADMIN-002
- ARCH-043-DATABASE-001
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-21'
---

# Use database Woo billing credential pair

## Architecture

- `ARCH-043`: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Current source evidence and boundary: controlling 17 October environment-variable reconciliation in that parent architecture.
- Logical owner: `moda_api` (`moda-interact-api`).
- **Materialised and claimed — developer Attempt 1, 2026-10-21.** The canonical parent and API implementation task worktrees were created from current `origin/main`; developer execution and completion authority were explicitly assumed while preserving `assigned_agent: moda_api`.

## Objective

Migrate hosted API WooCommerce billing provider key and secret to `woocommerce.billing`, separate from `woocommerce.auth` and merchant REST grants.

## Context

The canonical ARCH-043 inventory defines this as a newly scoped consumer task; do not revive identically numbered superseded proposal files or their retired dependencies. The generic database models and ARCH-039 published cryptography remain unchanged.

## Scope

- Resolve and decrypt `{apiKey,apiSecret}` together for each billing command without caching across operations.
- Continue to select `sandbox` versus `production` exclusively using deployment `WOO_BILLING_ENVIRONMENT`.
- Preserve billing idempotency, provider receipts and retry semantics. Do not expose credentials to WooCommerce plugin or browser.

## Out of Scope

- No new Prisma model, root cryptography, Shared package, gateway or cross-repository implementation.
- No `_index.md` changes, unrelated refactors or premature environment removal.

## Requirements

- Use the environment-scoped `PlatformConfiguration` sealed envelope with immutable AAD bytes and published ARCH-039 Node-only decryption.
- A configured, disabled, corrupt, undecryptable or unavailable database credential fails closed. Transitional env use requires an explicit gated cutover and must never mix credential bundle sources.
- Read once per relevant bounded operation; do not add a per-event hot-path query, a global indefinite cache or a network operation inside a transaction.
- Secrets never leave the trusted server or enter logs, audits, errors or browser output.
- Respect existing service ownership, launcher task-isolation, developer review and task-state claims.

## Work Items

- [x] Resolve and decrypt `{apiKey,apiSecret}` together for each billing command without caching across operations.
- [x] Continue to select `sandbox` versus `production` exclusively using deployment `WOO_BILLING_ENVIRONMENT`.
- [x] Preserve billing idempotency, provider receipts and retry semantics. Do not expose credentials to WooCommerce plugin or browser.
- [x] Add positive and negative unit/integration tests; record actual validation and isolated-worktree evidence.

## Interfaces / Contracts

- Configuration keys and decrypted field names: `docs/architecture/ARCH-043-database-managed-platform-configuration.md` (17 October reconciliation).
- Writer and sealed key lifecycle: `ARCH-043-ADMIN-002`; schema: `ARCH-043-DATABASE-001`.
- Shared cryptography: `@modainteract/moda-interact-shared/security/credentials/node` (existing published exports).

## Dependencies

- `ARCH-043-ADMIN-002`
- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Sandbox/production isolation and missing pair rejection
- [x] Provider billing lifecycle, receipt and retry regression
- [x] CAS rotation, revoked/wrong environment/decrypt failure, typecheck
- [x] No cross-environment secret leakage, duplicate provider credentials or stale revision reuse.
- [x] All prerequisite tasks were Complete before the implementation claim.

## Validation

- [x] Task-focused unit and integration tests using existing repository commands.
- [x] Typecheck, applicable lint/build, `git diff --check`.
- [x] Recorded launcher-resolved parent/implementation task worktree isolation and sync.

## Stop Condition

After required work and validation, record the Completion Report, mark Review and STOP. With `completion_mode: developer`, an Accepted review does not itself complete the task; explicit developer completion is required. Do not start enabled tasks.

## Implementation Notes

Inspect the actual target worktree before coding; this portable task is grounded in an earlier snapshot and is not a claim that a current deployed reader has changed.

## Completion Report

### Status

**Ready for Review — developer Attempt 1 (2026-10-21).** Implementation was committed and pushed on the canonical API task branch at `9d93afccebc0d3e597dc1ae37d0de750894e4739` (`feat(api)`). This is an implementation handoff, not an Architect Review or developer completion decision. The task remains `completion_mode: developer`.

### Files Changed

Implementation commit `9d93afc` changes the following paths in `moda-interact-api` (the parent task record is updated separately):

- Runtime and configuration: `src/platform-configuration/{composition,contracts,errors,service}.ts`, `src/woocommerce/billing/woo-billing-config.ts`, `src/woocommerce/billing/webhooks/woo-billing-webhook-route.ts`, `src/runtime-config.ts`, `src/composition/{billing,woocommerce}.ts`, `src/index.ts`, `src/billing/commands/{recovery-credit-purchase-command,recurring-subscription-command}.service.ts`.
- Tests: `tests/integration/platform-configuration/service.postgres.test.ts`, `tests/unit/platform-configuration/{logging,service,woo-billing}.test.ts`, `tests/unit/runtime-config.test.ts`, `tests/unit/woocommerce/billing/{woo-billing-client,woo-billing-resolution}.test.ts`, `tests/unit/woocommerce/billing/webhooks/webhook-route.test.ts`, `tests/unit/composition/real-route-registration.test.ts`.
- Integration runner: `scripts/run-arch043-platform-configuration-postgres.mjs` (ARCH-043 billing credential scenario, within scope). Separately, `package.json` and `tests/unit/http/integration-runner-registration.test.ts` contain default integration-runner inventory changes beyond this task's billing-credential scope and require explicit review.

### Work Completed

- Replaced Woo billing environment key/secret reads with an environment-scoped, sealed PostgreSQL `woocommerce.billing` pair, decrypted through the approved published Shared Node credential API; no legacy billing-key or billing-secret environment fallback.
- Resolved the current credential pair at the billing operation boundary and passed it to the provider client; `WOO_BILLING_ENVIRONMENT` alone continues to select sandbox versus production. No indefinite cross-operation credential cache was introduced.
- Kept existing idempotency and committed billing-intent/provider-outcome semantics. New one-time and recurring commands reject unavailable credentials before creating an intent; replays do not issue duplicate provider requests.
- Updated signed Woo billing webhook handling to resolve the current sealed secret per delivery. An unsigned request receives 401 before configuration access; a signed request with unavailable configuration fails closed with 503. No provider secrets are exposed in responses or logs.
- Extended the disposable ARCH-043 PostgreSQL configuration test suite to cover billing credentials, rotation, revocation and wrong-environment/corrupt configuration; added focused unit and route tests.
- Reconciled the unrelated default integration-runner registration inventory so the full API unit suite passes; this scope expansion is explicitly disclosed below for review.

### Validation Results

Evidence supplied from the canonical API task implementation worktree on 2026-10-21:

- `npm ci` — **PASS** (dependencies installed; warnings recorded below).
- `node --import tsx --test tests/unit/composition/real-route-registration.test.ts` — **PASS**, 1/1.
- `npm test` (which runs Prisma generation before `tsx --test "tests/unit/**/*.test.ts"`) — **PASS**, 535/535, 0 failures, after the webhook assertion and integration registration test corrections. The earlier 533/535 run and its two failures are superseded by this final run.
- `npm run typecheck` — **PASS**, including Prisma Client generation and `tsc --noEmit -p tsconfig.json`.
- `npm run lint` — **PASS**, `eslint . --max-warnings=0`.
- `npm run build` — **PASS**, earlier validation on this implementation series.
- `npm run test:arch043-platform-configuration:postgres` — **PASS**, 5/5 disposable PostgreSQL scenarios; fixture cleanup also **PASS**.
- `git diff --check` — **PASS**, no output; `git status --short` and `git diff --stat` — clean/no output in the developer's final check.
- Task-start physical isolation and synchronization are recorded in `## Developer Claim — Attempt 1` below. Parent and implementation task branches have distinct dedicated worktrees; both dependencies were Complete before the claim.

The published implementation branch head inspected for this handoff is `9d93afccebc0d3e597dc1ae37d0de750894e4739` (parent `0d97176e8caec860a67142708dae734565d3547d`). The sealed-credential PostgreSQL integration uses a disposable local database; no live external WooCommerce provider charge was claimed.

### Deviations

- **Separate scope-review item:** Commit `9d93afc` includes `package.json` and `tests/unit/http/integration-runner-registration.test.ts` adjustments to register existing ARCH-040 integration runners and recognise the Woo Redis runner. They resolved an existing complete-suite inventory failure but are not necessary to implement `woocommerce.billing` credential consumption. Reviewer must explicitly approve this inclusion or request separation in a follow-up correction; do not silently treat these changes as accepted API-004 scope.
- The implementation intentionally has **no legacy Woo billing key/secret fallback**. `WOO_BILLING_ENVIRONMENT` remains deployment-owned for provider endpoint selection.

### Assumptions

- The currently published Shared credential library and `ARCH-043-ADMIN-002` writer use the canonical sealed-record AAD contract; successful disposable PostgreSQL tests verify consumer compatibility for the exercised cases.
- Environment-secret removal applies to the Woo billing API key and secret, not to provider environment selection or unrelated API authentication configuration.

### Unresolved Issues

- Approval or separation of the unrelated integration-runner-registration changes remains a **review decision**. No additional task-specific test failure is outstanding in the supplied validation evidence.

### Architectural Concerns

- No new database schema, shared contract, or provider-retry architecture change was introduced. The unrelated integration-test registration modification is explicitly flagged under Deviations rather than being silently folded into billing scope.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not evaluated.

### Follow-up

None

## Developer Execution Ownership Amendment

On 2026-10-21, the developer invoked `/moda_developer_create ARCH-043-API-004`, explicitly taking over this ready agent-owned task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_api`, repository ownership, scope, dependencies, acceptance criteria, and validation requirements are unchanged.

## Developer Claim — Attempt 1

**Claimed — 2026-10-21T13:04:14Z.** The task transitioned from `ready`, Attempt 0, null executor to `in_progress`, Attempt 1, `executor: developer`.

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-API-004`, branch `task/ARCH-043-API-004`, created from current parent `origin/main` at `d3f61398`. The task-specific branch was not present locally/remotely before preparation; publication follows this claim commit.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-API-004`, branch `task/ARCH-043-API-004`, created from current API `origin/main` at `0d97176`. The task-specific branch was not present locally/remotely before preparation; implementation work remains unstarted.
- Start synchronization: both worktrees were created from fetched current `origin/main`; no task-branch fast-forward or mainline merge was needed. Both worktrees are clean. Shared workspace and API source checkouts were not switched or modified for task execution; their pre-existing unrelated/generated changes were left untouched.
- Dependency readiness was verified through the canonical launcher before claim: `ARCH-043-ADMIN-002` and `ARCH-043-DATABASE-001` both resolve `complete`.
- Required implementation validation remains: task-focused positive/negative unit and integration tests; typecheck; applicable lint/build; and `git diff --check`. No implementation or test changes were made as part of this claim operation.

## Developer Self-Review - Changes Requested

**Outcome: Changes Requested — Attempt 1 remains open.** The billing credential
reader implementation, focused validation evidence, and publication are
acceptable for this review. The task branch also changes the default
`test:integration` chain and its runner-inventory test to register three
unrelated runners: ARCH-040 conversation control, ARCH-040 human send, and
ARCH-035 Woo activity Redis. This broadens API-004's default integration-run
behavior beyond its Woo billing credential scope and its stated prohibition on
unrelated changes.

### Required Corrections

- Keep the ARCH-043 platform-configuration PostgreSQL runner and its direct registration, which are required to validate this task.
- Remove the ARCH-040 conversation-control, ARCH-040 human-send, and ARCH-035 Woo-activity Redis runner additions from this task's `test:integration` chain and runner-inventory changes. If those registrations are required repository maintenance, obtain explicit architect approval and track them in a separate scoped task instead of bundling them here.
- Re-run the focused integration-runner registration unit test, disposable ARCH-043 PostgreSQL credential suite, `npm test`, `npm run typecheck`, and `git diff --check`; update the report with actual results and the revised implementation commit.

### Review Evidence

- Reviewed implementation diff from `origin/main` to `9d93afc`; implementation worktree was clean and the task branch was published.
- Focused validation on 2026-10-21: billing credential, command-preflight, and webhook tests passed 14/14; `git diff --check origin/main...HEAD` passed.
- The remaining correction is limited to unrelated integration-runner scope;
	billing credential acceptance criteria otherwise appear satisfied.

The task returns to `ready` for correction. Attempt remains 1; executor and
claim timestamp are cleared. Do not claim Attempt 2 in this reconciliation.
