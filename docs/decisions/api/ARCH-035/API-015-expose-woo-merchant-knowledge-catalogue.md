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
attempt: 1
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
- [ ] Resolve Shop from installation principal only; verify Woo platform/status, redact storage keys, signed URLs and secrets.
- [ ] Add source-count, data-format and tenant/isolation tests, OpenAPI and log hygiene.
- [x] Add focused positive and negative coverage and complete the required validation/Completion Report.

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
- [ ] Current and historical revisions are accurately distinguishable; no unapproved storage metadata or signed URL leaks.
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

Changes Requested — Attempt 1. Implementation and required validation are present and published, but self-review found a failure-code disclosure that must be corrected before acceptance. Claim cleared; the next developer preparation invocation will claim Attempt 2.

### Files Changed

Implementation commit `59cb9db8caa877d8358e7f02311a7b141cd46838` on `task/ARCH-035-API-015` changes the OpenAPI document, merchant route composition, new Merchant Knowledge contract/projection/read service/routes, focused unit and PostgreSQL integration tests, integration runner registration, and package scripts. No schema, migration, `_index.md`, or unrelated domain changes.

### Work Completed

- Implemented authenticated, bounded GET `/v1/merchant/merchant-knowledge`, Shop-scoped source projection, entitlement/activation state, source catalogue and revision projection, and OpenAPI schema.
- Added positive/negative service and route tests, production route-composition coverage, and a disposable migration-backed PostgreSQL fixture covering tenant isolation, activation, entitlement changes, revision history, and redaction.
- Preserved source records when entitlement is absent and separated plan entitlement from merchant preference/effective activation.

### Validation Results

- `npm test` — passed, 431 tests; 431 passed, 0 failed.
- `npm run test:integration` — passed. The API-015 migration-backed Merchant Knowledge fixture passed 1/1; all integration runner summaries passed (53 tests total).
- `npm run typecheck` — passed; Prisma client generation and TypeScript check succeeded.
- `npm run lint` — passed.
- `npm run build` — passed; production TypeScript build succeeded.
- `git diff --check origin/main...HEAD` — passed.
- Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-015` is clean, synchronized from `origin/main`, and recursively initialized at database gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`; implementation commit `59cb9db8caa877d8358e7f02311a7b141cd46838` is published to `origin/task/ARCH-035-API-015`.
- Parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-015` contains the durable review state; its branch is `task/ARCH-035-API-015`.

### Deviations

None.

### Assumptions

The uploaded ZIP represents a portable design baseline, not the developer's current on-disk branches. Confirm source, task status and dependency state with the launcher before execution.

### Unresolved Issues

Changes Requested: `src/merchant/merchant-knowledge/projection.ts` accepts any string matching `/^[A-Z][A-Z0-9_]{0,63}$/` as a public `failureCode`. The Background worker persists a sanitized `Error.name`, not a trusted enum; its existing test demonstrates `Acquisition_Failure___secret` is a valid persisted value. Therefore identifier-shaped provider/exception text can escape despite the stated redaction guarantee. Replace the regex-only pass-through with an explicit allowlist of approved Merchant Knowledge failure codes (or omit unrecognized values), and add a projection/service regression proving `Acquisition_Failure___secret` and other unrecognized values produce `null` and are absent from serialized responses. Preserve documented safe codes such as `HTTP_5XX` and `UNSAFE_URL`.

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
