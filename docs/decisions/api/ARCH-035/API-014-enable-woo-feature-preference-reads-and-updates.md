---
id: ARCH-035-API-014
architecture_id: ARCH-035
title: Expose Woo merchant feature preferences with server-enforced entitlement
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables: [ARCH-035-WOOCOMMERCE-014]
created: 2026-10-16
updated: 2026-10-17
---

# ARCH-035-API-014 — Expose Woo merchant feature preferences with server-enforced entitlement

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_api`, repository `moda-interact-api`; coordinator: `moda_architect`.


## Objective

Provide authenticated, plan-aware Woo feature-preference GET/PUT operations consumed by the existing W003 controller.

## Context

W003 displays Shopify-style feature cards, but its production client deliberately returns FEATURES_UNAVAILABLE. The prior API-003 task is superseded and must remain historical. Reuse the existing Shopify Feature/ShopFeaturePreference semantics and published shared capability selectors.

## Scope

- Implement GET and PUT `/v1/merchant/feature-preferences` through the existing Woo installation authenticator/router.
- Provide versioned, strict OpenAPI/runtime schemas: GET `{schemaVersion:1, revision, features:[{id,key,name,description,enabled,effective,editable,required,planEligible}]}`; PUT `{expectedRevision, changes:[{featureId,enabled}]}` with bounded distinct IDs.
- Read active Subscription and enabled plan mappings, active Feature and ShopFeaturePreference; enforce tenant/platform binding and immutability for system-required/ALWAYS_ENABLED and ineligible features.
- Compare-and-set fingerprint/revision under Shop lock, applying only mutable MERCHANT_OPT_IN changes; ensure concurrent stale client requests conflict without partial writes.
- Add integration and negative tests, route registration, OpenAPI updates, and shared structured logging without sensitive values.

## Out of Scope

- Changing plan assignments, schema, language detection/conversation policy or Shopify UI.
- Implementing WordPress UI, Merchant Knowledge source management or other repositories.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. Record bounded structured logging through `@modainteract/moda-interact-shared/logging` when changing generic application logs.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [x] Implement GET and PUT `/v1/merchant/feature-preferences` through the existing Woo installation authenticator/router.
- [x] Provide versioned, strict OpenAPI/runtime schemas: GET `{schemaVersion:1, revision, features:[{id,key,name,description,enabled,effective,editable,required,planEligible}]}`; PUT `{expectedRevision, changes:[{featureId,enabled}]}` with bounded distinct IDs.
- [x] Read active Subscription and enabled plan mappings, active Feature and ShopFeaturePreference; enforce tenant/platform binding and immutability for system-required/ALWAYS_ENABLED and ineligible features.
- [x] Compare-and-set fingerprint/revision under Shop lock, applying only mutable MERCHANT_OPT_IN changes; ensure concurrent stale client requests conflict without partial writes.
- [x] Add integration and negative tests, route registration, OpenAPI updates, and shared structured logging without sensitive values.
- [x] Assess the paid-plan test gap. Architect accepted omitting a separate paid-plan fixture because projection uses enabled plan-feature mappings and does not branch on plan kind; existing integration coverage exercises enabled and disabled mappings. The paid-plan-specific fixture was not added.
- [x] Run and record focused feature-preferences unit and PostgreSQL integration validation for the unchanged implementation.

## Interfaces / Contracts

- GET/PUT `/v1/merchant/feature-preferences` as described in approved architecture amendment.
- Hosted principal determines shop; no body/query shop ID; W003 currently sends `preferences` and must be adapted in WOOCOMMERCE-015.

## Dependencies

None

## Enables

- `ARCH-035-WOOCOMMERCE-014`

## Acceptance Criteria

- [x] Active/inactive/free/paid/required/optional plan scenarios have correct editable/effective/required/planEligible projection. Paid-plan-specific fixture coverage was waived by the explicit Architect Review Accepted decision; the existing active-plan mapping coverage exercises the same implementation path.
- [x] Stale revision, two-admin race, malformed/foreign/duplicate feature IDs, system-required write and revoked credential fail closed.
- [x] No mutation affects another Shop; unchanged write is idempotent; API version/OpenAPI and Shared selector versions align.
- [x] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [x] Focused service/route unit tests, disposable PostgreSQL integration for CAS and tenant isolation.
- [x] Repository-declared TypeScript typecheck, focused lint, build and `git diff --check`.
- [x] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled API-structure handoff (2026-10-16 22:56 snapshot)

- Implement this feature in `moda-interact-api/src/merchant/feature-preferences/`, separating `routes.ts`, `service.ts`, and bounded request/response validation (`contract.ts` or small equivalents). Do **not** append handlers to `src/woocommerce/installation/routes.ts` or make `src/index.ts` a business router.
- Register the feature-owned handler in `src/composition/merchant.ts`, which is already passed into `composeApiRoutes(...)` by `src/index.ts`. Consume `WooInstallationAuthenticator` and `WooInstallationPrincipal` from `src/auth/woo-installation/`; follow `src/http/route-handler.ts`, bounded body parsing in `src/http/body.ts`, and no-store responses in `src/http/response.ts`. Preserve `/v1/merchant/*` route and error conventions.
- Put unit/HTTP tests under `tests/unit/merchant/feature-preferences/` and disposable PostgreSQL tests under `tests/integration/merchant/feature-preferences/`; publish the route schema in `openapi/merchant-feature-preferences-v1.yaml`. Register any newly added integration runner with the repository's `test:integration` script; do not leave a passing test file unreachable from standard validation.
- Shopify's `app/services/feature-preferences/feature-preferences.server.ts` is a **behavioural reference**, not importable API code. Reuse `selectCapabilities` from the published Shared `commerce` subpath, keep a stable revision from authoritative plan/feature/preference state and prove it changes with relevant entitlement/feature changes. The W003 client currently sends `preferences`; the published API accepts `changes`, mapped only in WOOCOMMERCE-015. Avoid adding a second feature-selection policy in the WordPress plugin.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

## Completion Report

### Status

Complete — Attempt 2 accepted by explicit Architect Review Accepted and developer completion decision. The paid-plan-specific fixture was waived; no implementation behavior gap was identified.

### Files Changed

Implementation commit `862a2a0ea555afb36657c42afdda096f069e14d9` on `task/ARCH-035-API-014` changes:

- `openapi/merchant-feature-preferences-v1.yaml`
- `package.json` and `scripts/test-arch035-feature-preferences-postgres.mjs`
- `src/composition/merchant.ts`
- `src/merchant/feature-preferences/contract.ts`, `request.ts`, `routes.ts`, and `service.ts`
- `tests/integration/merchant/feature-preferences/service.postgres.test.ts`
- Unit tests for composition, integration-runner registration, contract, OpenAPI, route and service behavior.

### Work Completed

- Added authenticated GET/PUT merchant feature-preference routes, strict versioned contracts/OpenAPI, bounded request parsing, no-store responses and bounded structured logging.
- Added subscription/plan/feature/preference projection using the Shared capability selector; enforced installation and Woo Shop identity, required/ineligible immutability and revision compare-and-set under the Shop lock.
- Added unit and disposable PostgreSQL coverage for request/response validation, entitlement, required/always-enabled features, inactive subscription/plan, stale revisions, concurrent updates, tenant isolation, credential revocation and plan/feature revision drift.
- Registered the disposable PostgreSQL suite in `test:integration` and the focused `test:arch035-features:postgres` script.

### Validation Results

- `node --version`: `v24.19.0`.
- `npm exec -- tsx --test tests/unit/merchant/feature-preferences/*.test.ts tests/unit/composition/real-route-registration.test.ts tests/unit/http/integration-runner-registration.test.ts`: passed, 14/14.
- `npm run test:arch035-features:postgres`: passed, 1/1 against a disposable `pgvector/pgvector:pg17` database; 49 migrations applied and the runner cleaned up the container.
- `npm test`: passed, 431/431, 0 failed, 0 skipped.
- `npm run typecheck`: passed.
- `npm run lint`: passed with `--max-warnings=0`.
- `npm run build`: passed.
- `git diff --check origin/main...HEAD`: passed.

These validations ran against implementation commit `862a2a0ea555afb36657c42afdda096f069e14d9` during Attempt 1. Attempt 2 introduced no implementation changes; the paid-plan-specific fixture was explicitly waived and was not run.

### Branch and Worktree Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-014`, `task/ARCH-035-API-014`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-014`, `task/ARCH-035-API-014`.
- Parent takeover commit `fa8ef7bad134815571d00ef5362d6e5e7963849e`, Attempt 1 claim `e9089b5df66bea8887beec969f35713fce6035d3`, and Attempt 2 claim `d727eedfd9c0b83c9006dda1fba6e3b24e819c22` were published. Implementation commit `862a2a0ea555afb36657c42afdda096f069e14d9` is published to the implementation task branch.
- Parent task branch fast-forward: not needed; `origin/main` was already incorporated. Implementation task branch fast-forward: not needed; `origin/main` was already incorporated at preparation.
- Recursive submodule sync and initialization passed; `database` is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`.
- The shared workspace and shared API source checkout were not switched or modified for task implementation; no other task worktree was reused. Both task worktrees were clean at reconciliation.

### Deviations

No scope or repository-ownership deviations.

### Unresolved Issues

None. The separate paid-plan fixture was waived by the explicit Architect Review Accepted decision. The service derives eligibility from active plan-feature mappings and has no plan-kind branch; existing integration coverage validates enabled and disabled mappings.

### Architectural Concerns

None identified.

## Developer Self-Review — Changes Requested (Attempt 1)

The implementation and executed validation pass, but the acceptance matrix is not fully evidenced. Required correction: extend `tests/integration/merchant/feature-preferences/service.postgres.test.ts` with an active paid-plan scenario containing at least one enabled and one disabled feature mapping. Assert the returned eligibility/editability/effectiveness projections, run `npm run test:arch035-features:postgres` and the focused feature-preferences unit tests, and update the Completion Report with the results. Keep the task scope and API behavior unchanged.

Transitioned to `ready`; `executor` and `claimed_at` are cleared. Attempt remains `1`; the next developer claim increments it.

## Developer Self-Review — Changes Requested (Attempt 2)

Reconciliation found no new implementation commits or uncommitted changes after Attempt 1. The implementation branch remains at published commit `862a2a0ea555afb36657c42afdda096f069e14d9`; therefore, the prior missing paid-plan projection coverage remains unresolved. Required correction is unchanged: extend `tests/integration/merchant/feature-preferences/service.postgres.test.ts` with an active paid-plan scenario containing enabled and disabled feature mappings, asserting `planEligible`, `editable`, and `effective` for both. Run `npm run test:arch035-features:postgres` and the focused feature-preferences unit tests, then update the Completion Report with Attempt 2 results.

No Attempt 2 implementation validation was run because no correction was submitted. Attempt 1 validation results above describe the unchanged implementation only. Transitioned to `ready`; `executor` and `claimed_at` are cleared. Attempt remains `2`; a later developer claim increments it.

## Developer Execution Ownership Amendment

The developer explicitly requested preparation through `/moda_developer_create ARCH-035-API-014`. Execution ownership and completion authority are taken over from the assigned agent and set to `developer`/`developer`; logical ownership remains `assigned_agent: moda_api`. Scope and dependencies are unchanged. The canonical launcher claimed Attempts 1 and 2 after worktree synchronization and dependency verification; both claims are recorded in the task history above.

## Architect Review

### Review Status

Accepted — explicit Architect Review Accepted provided by the developer on 2026-10-17.

### Review Notes

Accepted based on the implementation and validation evidence in the Completion Report. The paid-plan-specific integration fixture is waived: the API's projection depends on enabled feature mappings and does not branch on `BillingPlanKind`; existing active-plan integration coverage exercises enabled/disabled mapping behavior. No functionality hole was identified.

### Reviewed Files

- `src/merchant/feature-preferences/service.ts`
- `tests/integration/merchant/feature-preferences/service.postgres.test.ts`
- `tests/unit/merchant/feature-preferences/`
- `openapi/merchant-feature-preferences-v1.yaml`

### Validation Reviewed

Focused feature-preferences tests 14/14; disposable PostgreSQL integration 1/1; full unit suite 431/431; typecheck, lint, build and `git diff --check` passed. Results were run against the unchanged published implementation commit as recorded above.

### Architecture Conformance

Accepted. The task remains within API ownership and uses the approved shared capability selector and Woo installation principal.

### Follow-up

No paid-plan-specific fixture is required for acceptance. Downstream WOOCOMMERCE-014 remains pending on API-015, API-016 and API-017.

## Developer Completion Decision — Attempt 2

The developer explicitly requested completion with `Architect Review Accepted`. The accepted review is durable above; implementation commit `862a2a0ea555afb36657c42afdda096f069e14d9` is published on `task/ARCH-035-API-014`; required implementation work is complete; the paid-plan-specific fixture waiver is explicit. Task transitioned to `complete`; `executor` and `claimed_at` are null; attempt remains `2`. No task branch was merged to `main`.
