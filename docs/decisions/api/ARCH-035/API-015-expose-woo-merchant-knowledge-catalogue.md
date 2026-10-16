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
status: in_progress
priority: 42
executor: developer
claimed_at: 2026-10-16T23:20:41Z
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

- [ ] Implement authenticated GET `/v1/merchant/merchant-knowledge`, bounded versioned response and OpenAPI schema with explicit feature-off vs unentitled vs integration-error states.
- [ ] Read existing subscription/merchant_knowledge plan configuration, allowed purpose/format combinations, supported source languages and upload limits; project persisted source positions, latest and active revisions, processing status, failure reason and dormantReason.
- [ ] Allow plan-entitled read/configuration while preference is off, distinguishing `merchantEnabled` from `effectiveEnabled` and `processingEligible`. Retain existing sources in read when plan becomes ineligible.
- [ ] Resolve Shop from installation principal only; verify Woo platform/status, redact storage keys, signed URLs and secrets.
- [ ] Add source-count, data-format and tenant/isolation tests, OpenAPI and log hygiene.
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

- [ ] Feature-off entitled merchant sees existing sources/capacity without a false unavailable state.
- [ ] Different Shops cannot retrieve each other’s sources and inaccessible schema/config fails closed.
- [ ] Current and historical revisions are accurately distinguishable; no unapproved storage metadata or signed URL leaks.
- [ ] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [ ] Focused service/schema/route tests and disposable PostgreSQL entitlement/source fixtures.
- [ ] Repository-declared typecheck, changed-file lint, build, `git diff --check`.
- [ ] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

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

In Progress — Attempt 1. Developer takeover from the ready agent-executed task; implementation has not started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The uploaded ZIP represents a portable design baseline, not the developer's current on-disk branches. Confirm source, task status and dependency state with the launcher before execution.

### Unresolved Issues

None evidenced beyond the explicit implementation and test dependencies above.

### Architectural Concerns

Report any cross-repository contract, R2 identity, reconciliation or security mismatch to `moda_architect`.

## Developer Execution Ownership Amendment

On 2026-10-17, the developer invoked `/moda_developer_create ARCH-035-API-015`, explicitly taking over this ready agent-executed task. Execution and completion authority are now `developer`/`developer`; `assigned_agent: moda_api`, repository ownership, scope, dependencies, acceptance criteria and validation requirements are unchanged. Attempt 1 is claimed by `developer` after canonical parent and implementation worktree synchronization.

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
