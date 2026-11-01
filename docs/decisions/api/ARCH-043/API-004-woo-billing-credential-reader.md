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
status: complete
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
- **Approved, bounded test-harness exception (2026-10-21):** retain the two existing ARCH-040 PostgreSQL integration runners newly added to the default API `test:integration` chain and the corresponding registration-test inventory reconciliation. The ARCH-035 Woo activity Redis runner was already in that chain; the change only adds explicit recognition of its npm-script delegation. This approval does not extend to production ARCH-040/ARCH-035 code or other test-suite changes.

## Out of Scope

- No new Prisma model, root cryptography, Shared package, gateway or cross-repository implementation.
- No `_index.md` changes, unrelated application refactors or premature environment removal. The specific test-harness exception recorded under Scope is authorised; no other unrelated work is authorised.

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

**Complete — developer Attempt 1 (2026-10-21).** Implementation was committed and pushed on the canonical API task branch at `9d93afccebc0d3e597dc1ae37d0de750894e4739` (`feat(api)`). The bounded integration-runner scope exception was explicitly approved, the developer self-review was accepted, and the developer explicitly completed the task. The complete expanded `test:integration` chain was not run and is not reported as passing.

### Files Changed

Implementation commit `9d93afc` changes the following paths in `moda-interact-api` (the parent task record is updated separately):

- Runtime and configuration: `src/platform-configuration/{composition,contracts,errors,service}.ts`, `src/woocommerce/billing/woo-billing-config.ts`, `src/woocommerce/billing/webhooks/woo-billing-webhook-route.ts`, `src/runtime-config.ts`, `src/composition/{billing,woocommerce}.ts`, `src/index.ts`, `src/billing/commands/{recovery-credit-purchase-command,recurring-subscription-command}.service.ts`.
- Tests: `tests/integration/platform-configuration/service.postgres.test.ts`, `tests/unit/platform-configuration/{logging,service,woo-billing}.test.ts`, `tests/unit/runtime-config.test.ts`, `tests/unit/woocommerce/billing/{woo-billing-client,woo-billing-resolution}.test.ts`, `tests/unit/woocommerce/billing/webhooks/webhook-route.test.ts`, `tests/unit/composition/real-route-registration.test.ts`.
- Integration runners: `scripts/run-arch043-platform-configuration-postgres.mjs` (ARCH-043 credential validation, within scope); `package.json` and `tests/unit/http/integration-runner-registration.test.ts` (bounded exception explicitly approved on 2026-10-21; see Scope and the accepted review below).

### Work Completed

- Replaced Woo billing environment key/secret reads with an environment-scoped, sealed PostgreSQL `woocommerce.billing` pair, decrypted through the approved published Shared Node credential API; no legacy billing-key or billing-secret environment fallback.
- Resolved the current credential pair at the billing operation boundary and passed it to the provider client; `WOO_BILLING_ENVIRONMENT` alone continues to select sandbox versus production. No indefinite cross-operation credential cache was introduced.
- Kept existing idempotency and committed billing-intent/provider-outcome semantics. New one-time and recurring commands reject unavailable credentials before creating an intent; replays do not issue duplicate provider requests.
- Updated signed Woo billing webhook handling to resolve the current sealed secret per delivery. An unsigned request receives 401 before configuration access; a signed request with unavailable configuration fails closed with 503. No provider secrets are exposed in responses or logs.
- Extended the disposable ARCH-043 PostgreSQL configuration test suite to cover billing credentials, rotation, revocation and wrong-environment/corrupt configuration; added focused unit and route tests.
- Reconciled the API integration-runner inventory: registered two existing ARCH-040 disposable PostgreSQL runners in the default chain, and taught its registration test to recognise the pre-existing ARCH-035 Redis runner. This bounded exception was explicitly approved on 2026-10-21.

### Validation Results

Evidence supplied from the canonical API task implementation worktree on 2026-10-21:

- `npm ci` — **PASS** (dependencies installed; warnings recorded below).
- `node --import tsx --test tests/unit/composition/real-route-registration.test.ts` — **PASS**, 1/1.
- `npm test` (which runs Prisma generation before `tsx --test "tests/unit/**/*.test.ts"`) — **PASS**, 535/535, 0 failures, after the webhook assertion and integration registration test corrections. The earlier 533/535 run and its two failures are superseded by this final run.
- `npm run typecheck` — **PASS**, including Prisma Client generation and `tsc --noEmit -p tsconfig.json`.
- `npm run lint` — **PASS**, `eslint . --max-warnings=0`.
- `npm run build` — **PASS**, earlier validation on this implementation series.
- `npm run test:arch043-platform-configuration:postgres` — **PASS**, 5/5 disposable PostgreSQL scenarios; fixture cleanup also **PASS**.
- The **entire expanded** `npm run test:integration` chain was **not** run as part of the supplied evidence. The two ARCH-040 suites and the already-registered ARCH-035 Redis suite remain independently runnable; their inclusion in the default command is an approved registration change, **not** a claim that they passed end-to-end on this attempt.
- `git diff --check` — **PASS**, no output; `git status --short` and `git diff --stat` — clean/no output in the developer's final check.
- Task-start physical isolation and synchronization are recorded in `## Developer Claim — Attempt 1` below. Parent and implementation task branches have distinct dedicated worktrees; both dependencies were Complete before the claim.

The published implementation branch head inspected for this handoff is `9d93afccebc0d3e597dc1ae37d0de750894e4739` (parent `0d97176e8caec860a67142708dae734565d3547d`). The sealed-credential PostgreSQL integration uses a disposable local database; no live external WooCommerce provider charge was claimed.

### Deviations

- **Explicitly approved scope exception (2026-10-21):** Commit `9d93afc` also changes `package.json` and `tests/unit/http/integration-runner-registration.test.ts`. It adds `test:arch040-conversation-control:postgres` and `test:arch040-human-send:postgres` to the default chain. `test:arch035-woo-activity:redis` was already in that chain; its recognition in the registration test is new. Following inspection of the exact commit and discussion of test coverage, runtime and isolation, the developer explicitly authorised retaining these test-only changes **in API-004**, superseding the previous request to separate them. No ARCH-040/ARCH-035 production behaviour was changed; no additional scope is authorised.
- The implementation intentionally has **no legacy Woo billing key/secret fallback**. `WOO_BILLING_ENVIRONMENT` remains deployment-owned for provider endpoint selection.

### Assumptions

- The currently published Shared credential library and `ARCH-043-ADMIN-002` writer use the canonical sealed-record AAD contract; successful disposable PostgreSQL tests verify consumer compatibility for the exercised cases.
- Environment-secret removal applies to the Woo billing API key and secret, not to provider environment selection or unrelated API authentication configuration.

### Unresolved Issues

- **None outstanding for ARCH-043-API-004** on the supplied evidence. The test-harness scope exception was approved on 2026-10-21. The complete expanded integration chain was not executed here and must not be reported as a passing validation.

### Architectural Concerns

- No new database schema, shared contract, or provider-retry architecture change was introduced. The non-billing integration-runner registration adjustment is retained only under the explicit, bounded approval recorded in this document.

## Architect Review

### Review Status

Accepted — scope-approval reconciliation of developer Attempt 1, 2026-10-21. Task remains `review`, with `completion_mode: developer`.

### Review Notes

- The developer explicitly approved retaining the bounded API test-harness additions after reviewing their purpose, changed files, and operational cost. This supersedes the sole outstanding scope objection in the previous Changes Requested review, without rewriting that review history or creating a new implementation attempt.
- The implementation remains published at `9d93afccebc0d3e597dc1ae37d0de750894e4739`; no further implementation change is required for this approval. Two ARCH-040 runner registrations are new; the ARCH-035 Redis runner existed before this commit and was only added to the registration-test accounting.
- This approval is not an assertion that the complete expanded `test:integration` chain has passed. The API-004-specific integration and unit evidence is recorded in the Completion Report.

### Reviewed Files

- `package.json` and `tests/unit/http/integration-runner-registration.test.ts` — exact API task commit `9d93afc` compared with parent `0d97176`, plus existing ARCH-040/ARCH-035 disposable runner scripts.
- API-004 billing command, configuration reader, webhook and task-specific test files listed in the Completion Report, together with the previous developer self-review.

### Validation Reviewed

- Reported passing `npm test` 535/535, `npm run typecheck`, `npm run lint`, `npm run build`, and disposable ARCH-043 PostgreSQL integration 5/5; Git whitespace and clean published implementation branch.
- The integration-runner registration unit test passed. No independent rerun of the complete expanded default integration chain was represented as performed.

### Architecture Conformance

- Accepted for ARCH-043-API-004, including **only** the expressly approved test-harness scope exception. Core database-only `woocommerce.billing` credential consumption, environment isolation, rotation and fail-closed webhook handling remain consistent with the parent architecture.

### Follow-up

- Developer must explicitly complete the task through `/moda_developer_update ARCH-043-API-004 complete`; do not auto-complete or promote dependants on acceptance alone.

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

## Developer Self-Review — Accepted (2026-10-21 Scope Reconciliation)

**Outcome: Accepted — developer Attempt 1.** The preceding Changes Requested
review is retained above as historical evidence. Its only outstanding issue was
the scope of the integration-runner inventory changes. After inspection of the
actual `9d93afc` diff, the developer explicitly approved keeping that bounded
exception within this task: two new ARCH-040 PostgreSQL runners in the default
integration command and registration-test recognition of the pre-existing
ARCH-035 Redis runner.

No production change, new validation claim, new worktree claim or Attempt 2 is
needed to reconcile this scope-only objection. Earlier recorded API-004 unit,
PostgreSQL, typecheck, lint, build and Git evidence is preserved. The complete
expanded `test:integration` command was not executed as part of this evidence.

This review supersedes the earlier Changes Requested **outcome** without deleting
its history. The task returns to `review`, retaining `attempt: 1`, clearing no
new claim (executor and claimed_at are already null), and awaiting explicit
developer completion under `completion_mode: developer`. No downstream task is
promoted by this reconciliation.

## Developer Completion Decision

**Completed — developer Attempt 1, 2026-10-21.** The developer explicitly
completed the task after the durable Accepted self-review. All required Work
Items and Acceptance Criteria are complete; implementation commit
`9d93afccebc0d3e597dc1ae37d0de750894e4739` is published on
`task/ARCH-043-API-004`. Attempt remains 1; `executor` and `claimed_at` are
cleared. No merge to `main` was required or performed.

### Dependency-Frontier Reconciliation

The canonical resolver reports duplicate definitions for both enabled task IDs:
`ARCH-043-GATEWAY-001` has two task files and `ARCH-043-SYSTEM-TEST-001` has two
task files. The definitions have different dependency sets and no unique
resolver-authoritative record, so no downstream task was changed or promoted.
The architect must resolve the duplicate definitions and recalculate the
ARCH-043 frontier. This ambiguity does not change API-004's completed state.
