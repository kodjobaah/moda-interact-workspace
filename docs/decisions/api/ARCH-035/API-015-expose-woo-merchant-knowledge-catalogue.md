---
id: ARCH-035-API-015
architecture_id: ARCH-035
title: Expose entitled Woo Merchant Knowledge catalogue and sources
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 42
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables: [ARCH-035-API-016, ARCH-035-API-017, ARCH-035-WOOCOMMERCE-014]
created: 2026-10-16
updated: 2026-10-17
---

# ARCH-035-API-015 — Expose entitled Woo Merchant Knowledge catalogue and sources

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_api`, repository `moda-interact-api`; coordinator: `moda_architect`.


## Objective

Expose a single authoritative Shop-scoped Merchant Knowledge read projection, including plan limits, source lifecycle and feature-activation status.

## Context

The current W004 UI foundation has only unavailable production data. Shopify already models MerchantKnowledgeSource/Revision, source-pair catalogue, entitlement and activation; no Woo-specific knowledge tables are required.

## Scope

- Implement authenticated GET `/v1/merchant/merchant-knowledge`, bounded versioned response and OpenAPI schema with explicit feature-off vs unentitled vs integration-error states.
- Read existing subscription/merchant_knowledge plan configuration, allowed purpose/format combinations, supported source languages and upload limits; project persisted source positions, latest and active revisions, processing status, failure reason and dormantReason.
- Allow plan-entitled read/configuration while preference is off, distinguishing `merchantEnabled` from `effectiveEnabled` and `processingEligible`. Retain existing sources in read when plan becomes ineligible.
- Resolve Shop from installation principal only; verify Woo platform/status, redact storage keys, signed URLs and secrets.
- Add source-count, data-format and tenant/isolation tests, OpenAPI and log hygiene.

## Out of Scope

- Creating/changing/deleting sources, R2 objects, background processing or feature preference write.
- Changing existing Shopify Merchant Knowledge storage records or Prisma schema.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. Record bounded structured logging through `@modainteract/moda-interact-shared/logging` when changing generic application logs.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [x] Implement authenticated GET `/v1/merchant/merchant-knowledge`, bounded versioned response and OpenAPI schema with explicit feature-off vs unentitled vs integration-error states.
- [x] Read existing subscription/merchant_knowledge plan configuration, allowed purpose/format combinations, supported source languages and upload limits; project persisted source positions, latest and active revisions, processing status, failure reason and dormantReason.
- [x] Allow plan-entitled read/configuration while preference is off, distinguishing `merchantEnabled` from `effectiveEnabled` and `processingEligible`. Retain existing sources in read when plan becomes ineligible.
- [x] Resolve Shop from installation principal only; verify Woo platform/status, redact storage keys, signed URLs and secrets.
- [x] Add source-count, data-format and tenant/isolation tests, OpenAPI and log hygiene.
- [ ] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- GET `/v1/merchant/merchant-knowledge` with `{schemaVersion:1, planEntitled, merchantEnabled, effectiveEnabled, maxKnowledgeSources, configuredCount, maxUploadBytes, defaultLanguageTag, supportedLanguageTags, catalogue, sources}`; align nested source/revision fields with Shopify projection.
- Strict schema validation using `@modainteract/moda-interact-shared/merchant-knowledge` and internationalization entrypoints where applicable.

## Dependencies

None

## Enables

- `ARCH-035-API-016`
- `ARCH-035-API-017`
- `ARCH-035-WOOCOMMERCE-014`

## Acceptance Criteria

- [x] Feature-off entitled merchant sees existing sources/capacity without a false unavailable state.
- [x] Different Shops cannot retrieve each other’s sources and inaccessible schema/config fails closed.
- [x] Current and historical revisions are accurately distinguishable; no unapproved storage metadata or signed URL leaks.
- [x] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [x] Focused service/schema/route tests and disposable PostgreSQL entitlement/source fixtures.
- [x] Repository-declared typecheck, changed-file lint, build, `git diff --check`.
- [x] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled API-structure handoff (2026-10-16 22:56 snapshot)

- Add a `src/merchant/merchant-knowledge/` read feature (`routes.ts`, `read.service.ts`, validation/DTO module as appropriate). Register the route in `src/composition/merchant.ts`; do not add it to `src/woocommerce/installation/routes.ts`, `src/index.ts`, or a generic top-level controller.
- Reuse `src/auth/woo-installation/authenticator.ts`, the canonical principal and `src/http/` helpers. Source data comes from existing `MerchantKnowledge*` Prisma models and plan/feature mappings; use the **published** `@modainteract/moda-interact-shared/merchant-knowledge` and internationalization exports available to the API, not imports from Shopify Remix `app/` code. Verify the installed Shared package actually exports every primitive used.
- Follow `src/merchant/store-categories/` and `src/merchant/discount-offers/` as existing patterns for bounded projections. Publish `openapi/merchant-knowledge-v1.yaml`; place focused unit tests in `tests/unit/merchant/merchant-knowledge/` and PostgreSQL evidence in `tests/integration/merchant/merchant-knowledge/`, registered in the standard integration chain.
- Reconcile `merchantEnabled`, `effectiveEnabled`, plan entitlement, eligible source pairs and counts with API-014's Shared-based feature semantics even though these two read tasks may execute independently. Include historical/stale revisions only in bounded, expressly documented projections. No object keys, R2 URLs or raw failure payloads cross this API.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

## Completion Report

### Status

Changes Requested — Attempt 2 was reviewed. The failure-code disclosure correction remains published and its focused service and PostgreSQL regressions pass, but the current synchronized branch has two failing unit tests. Attempt 1 review history and Attempt 2 claim/preparation evidence are preserved below; the task returns to `ready` without incrementing the attempt.

### Attempt 2 Preparation

- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-015`, branch `task/ARCH-035-API-015`; clean before claim.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-015`, branch `task/ARCH-035-API-015`; clean, merge conflicts resolved and committed before claim.
- Parent `origin/main` incorporated into the task branch at local merge `a412b351a78c994626d530e29fff61e400c7f3ae`.
- Implementation `origin/main` incorporated into the task branch at published merge-resolution commit `57440b6e6969319f6fbf17e4ef5d8fbaeb2acaa5`, matching `origin/task/ARCH-035-API-015`.
- Explicit dependencies: none. No shared checkout or another task worktree was used.

### Files Changed

Implementation commit `59cb9db8caa877d8358e7f02311a7b141cd46838` on `task/ARCH-035-API-015` changes the OpenAPI document, merchant route composition, new Merchant Knowledge contract/projection/read service/routes, focused unit and PostgreSQL integration tests, integration runner registration, and package scripts. No schema, migration, `_index.md`, or unrelated domain changes.

### Work Completed

- Implemented authenticated, bounded GET `/v1/merchant/merchant-knowledge`, Shop-scoped source projection, entitlement/activation state, source catalogue and revision projection, and OpenAPI schema.
- Added positive/negative service and route tests, production route-composition coverage, and a disposable migration-backed PostgreSQL fixture covering tenant isolation, activation, entitlement changes, revision history, and redaction.
- Preserved source records when entitlement is absent and separated plan entitlement from merchant preference/effective activation.
- Replaced syntax-based public failure-code projection with an explicit allowlist; added regressions for exception-name/provider-text disclosure and retained documented safe codes.

### Validation Results

- `npm test` — passed, 431 tests; 431 passed, 0 failed.
- `npm run test:integration` — passed. The API-015 migration-backed Merchant Knowledge fixture passed 1/1; all integration runner summaries passed (53 tests total).
- `npm run typecheck` — passed; Prisma client generation and TypeScript check succeeded.
- `npm run lint` — passed.
- `npm run build` — passed; production TypeScript build succeeded.
- `git diff --check origin/main...HEAD` — passed.
- Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-015` is clean, synchronized from `origin/main`, and recursively initialized at database gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`; implementation commit `59cb9db8caa877d8358e7f02311a7b141cd46838` is published to `origin/task/ARCH-035-API-015`.
- Parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-015` contains the durable review state; its branch is `task/ARCH-035-API-015`.

#### Post-correction validation — implementation commit `5f744b4a2cd00164115e0e144aba612324b99041`

- `npx tsx --test tests/unit/merchant/merchant-knowledge/read.service.test.ts` — passed, 9/9.
- `npm test` — passed, 432/432.
- `npm run test:arch035-merchant-knowledge:postgres` — passed, 1/1.
- `npm run test:integration` — passed; all integration runner summaries reported zero failures, including the Merchant Knowledge PostgreSQL fixture.
- `npm run typecheck`, `npm run lint`, and `npm run build` — passed.
- `git diff --check origin/main...HEAD` — passed; implementation worktree clean and `HEAD` matches `origin/task/ARCH-035-API-015`.

#### Attempt 2 review validation — implementation HEAD `57440b6e6969319f6fbf17e4ef5d8fbaeb2acaa5`

- `npx tsx --test tests/unit/merchant/merchant-knowledge/read.service.test.ts` — passed, 9/9, including strict public failure-code allowlist regressions.
- `npm test` — failed, 442/444 passed. `tests/unit/composition/real-route-registration.test.ts` expects 10 merchant routes although the current composition registers 11, and `tests/unit/http/integration-runner-registration.test.ts` reports `scripts/test-arch035-feature-preferences-postgres.mjs` missing from `test:integration`.
- `npm run test:arch035-merchant-knowledge:postgres` — passed, 1/1.
- `npm run test:integration` — passed, 53 tests across the currently registered integration chain; this does not clear the separate runner-registration unit failure.
- `npm run typecheck`, `npm run lint`, `npm run build`, and `git diff --check origin/main...HEAD` — passed.
- Implementation worktree is clean at `57440b6e6969319f6fbf17e4ef5d8fbaeb2acaa5`, matching `origin/task/ARCH-035-API-015`; current `origin/main` is `3caefe765e49dfdb30f63448c3d6fa6524ff7fa1`. Parent task worktree is clean at `76cb9a6c23f9ae8cc49a361613fe3533a0721ecc`, matching `origin/task/ARCH-035-API-015`.

### Deviations

None.

### Assumptions

The uploaded ZIP represents a portable design baseline, not the developer's current on-disk branches. Confirm source, task status and dependency state with the launcher before execution.

### Unresolved Issues

The Attempt 1 failure-code disclosure finding was corrected in implementation commit `5f744b4a2cd00164115e0e144aba612324b99041`; its explicit allowlist regression and PostgreSQL fixture pass at current HEAD. Attempt 2 has two outstanding unit-suite corrections recorded below.

### Architectural Concerns

Report any cross-repository contract, R2 identity, reconciliation or security mismatch to `moda_architect`.

## Developer Execution Ownership Amendment

On 2026-10-17, the developer invoked `/moda_developer_create ARCH-035-API-015`, explicitly taking over this ready agent-executed task. Execution and completion authority are now `developer`/`developer`; `assigned_agent: moda_api`, repository ownership, scope, dependencies, acceptance criteria and validation requirements are unchanged. Attempt 1 is claimed by `developer` after canonical parent and implementation worktree synchronization.

## Developer Self-Review - Changes Requested

### Review Status

Changes Requested — Attempt 1 is not accepted. The implementation branch is committed and pushed, all required repository checks passed, and the PostgreSQL fixture passed. A bounded data-disclosure defect remains in the public revision projection.

### Finding

In `src/merchant/merchant-knowledge/projection.ts`, `publicFailureCode` treats an identifier-shaped string as safe. This is not a trustworthy boundary: `moda-interact-background/src/workers/merchant-knowledge.worker.ts` derives the persisted failure code from `Error.name`, and `moda-interact-background/tests/unit/workers/merchant-knowledge.worker.test.ts` confirms the persisted value `Acquisition_Failure___secret`. Since that value matches the API regex, it can appear in the API response, contrary to the no-raw-failure-payload contract.

### Required Correction

Use a strict allowlist of approved Merchant Knowledge failure codes, returning `null` for all other persisted values. Add a regression test using `Acquisition_Failure___secret` and another unknown uppercase/underscore value; assert both are absent from the projection and serialized response while documented safe codes remain available. Rerun the focused Merchant Knowledge unit tests, full `npm test`, typecheck, lint, build, and `git diff --check`; rerun the PostgreSQL suite if the projection behavior or integration assertions change.

### Validation Reviewed

`npm test` passed 431/431; `npm run test:integration` passed, including the API-015 PostgreSQL fixture 1/1 and 53 integration tests in total; `npm run typecheck`, `npm run lint`, `npm run build`, and `git diff --check origin/main...HEAD` passed. These results do not override the unresolved disclosure finding.

### Attempt and Claim State

Attempt 1 is preserved as the reviewed cycle. The task returns to `ready` with `executor: null` and `claimed_at: null`; no new attempt is claimed here. `/moda_developer_create ARCH-035-API-015` will claim Attempt 2.

## Developer Self-Review — Changes Requested (Attempt 2)

### Review Status

Changes Requested. The strict failure-code allowlist correction is present, published, and passes its focused service and PostgreSQL regressions. Attempt 2 is not accepted because the current synchronized API branch has two failing unit tests.

### Findings and Required Corrections

1. `tests/unit/composition/real-route-registration.test.ts` fails because `createMerchantRoutes` now registers 11 route handlers while the assertion expects 10. Reconcile this assertion and the composed-handler count with the actual route composition, retaining explicit unauthenticated coverage for `GET /v1/merchant/merchant-knowledge`. The full unit suite must pass.
2. `tests/unit/http/integration-runner-registration.test.ts` requires `scripts/test-arch035-feature-preferences-postgres.mjs`, but the current `test:integration` script omits it. Register both the feature-preferences and Merchant Knowledge PostgreSQL harnesses so every discovered integration suite runs exactly once. The runner-registration test and full integration chain must pass.

### Validation Reviewed

At implementation HEAD `57440b6e6969319f6fbf17e4ef5d8fbaeb2acaa5`, the focused Merchant Knowledge service test passed 9/9, its PostgreSQL fixture passed 1/1, and the currently registered integration chain passed 53 tests. Typecheck, lint, build, and `git diff --check origin/main...HEAD` passed. `npm test` failed with 442/444 passing due to the two findings above. Rerun `npm test`, `npm run test:integration`, `npm run test:arch035-merchant-knowledge:postgres`, typecheck, lint, build, and diff check after correction.

### Attempt and Claim State

Attempt 2 is preserved as the reviewed cycle. The task returns to `ready` with `executor: null` and `claimed_at: null`; the next `/moda_developer_create ARCH-035-API-015` claim increments to Attempt 3. No implementation changes were made during this review.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation and validation evidence.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None until implementation submission.
