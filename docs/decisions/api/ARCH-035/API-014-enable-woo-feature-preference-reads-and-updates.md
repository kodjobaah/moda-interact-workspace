---
id: ARCH-035-API-014
architecture_id: ARCH-035
title: Expose Woo merchant feature preferences with server-enforced entitlement
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: [ARCH-035-WOOCOMMERCE-014]
created: 2026-10-16
updated: 2026-10-16
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

- [ ] Implement GET and PUT `/v1/merchant/feature-preferences` through the existing Woo installation authenticator/router.
- [ ] Provide versioned, strict OpenAPI/runtime schemas: GET `{schemaVersion:1, revision, features:[{id,key,name,description,enabled,effective,editable,required,planEligible}]}`; PUT `{expectedRevision, changes:[{featureId,enabled}]}` with bounded distinct IDs.
- [ ] Read active Subscription and enabled plan mappings, active Feature and ShopFeaturePreference; enforce tenant/platform binding and immutability for system-required/ALWAYS_ENABLED and ineligible features.
- [ ] Compare-and-set fingerprint/revision under Shop lock, applying only mutable MERCHANT_OPT_IN changes; ensure concurrent stale client requests conflict without partial writes.
- [ ] Add integration and negative tests, route registration, OpenAPI updates, and shared structured logging without sensitive values.
- [ ] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- GET/PUT `/v1/merchant/feature-preferences` as described in approved architecture amendment.
- Hosted principal determines shop; no body/query shop ID; W003 currently sends `preferences` and must be adapted in WOOCOMMERCE-015.

## Dependencies

None

## Enables

- `ARCH-035-WOOCOMMERCE-014`

## Acceptance Criteria

- [ ] Active/inactive/free/paid/required/optional plan scenarios have correct editable/effective/required/planEligible projection.
- [ ] Stale revision, two-admin race, malformed/foreign/duplicate feature IDs, system-required write and revoked credential fail closed.
- [ ] No mutation affects another Shop; unchanged write is idempotent; API version/OpenAPI and Shared selector versions align.
- [ ] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [ ] Focused service/route unit tests, disposable PostgreSQL integration for CAS and tenant isolation.
- [ ] Repository-declared TypeScript typecheck, focused lint, build and `git diff --check`.
- [ ] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

## Completion Report

### Status

Not Started.

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
