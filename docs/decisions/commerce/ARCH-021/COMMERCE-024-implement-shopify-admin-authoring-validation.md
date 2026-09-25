---
id: ARCH-021-COMMERCE-024
architecture_id: ARCH-021
title: Implement Shopify Admin GraphQL authoring validation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-018
  - ARCH-021-COMMERCE-019
enables:
  - ARCH-021-COMMERCE-022
created: 2026-09-24
updated: 2026-09-25
---

# Implement Shopify Admin GraphQL authoring validation

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Implement the authoritative zero-provider-I/O validation boundary for canonical `SHOPIFY_ADMIN_GRAPHQL` Tool definitions using the pinned COMMERCE-018 compiler, independently of External HTTP request-JavaScript work.

## Context

COMMERCE-018 owns the pinned Admin 2026-07 compiler and schema provenance. COMMERCE-019 owns the common validation result/auth/publication gate. This task composes those boundaries for the Shopify Admin authoring UI without resolving a shop session or calling Shopify.

## Scope

Primary files:

```text
src/commerce/tool-authoring/admin-validation.ts
src/studio/tools/admin-validation-server-actions.ts
tests/shopify-admin-authoring-validation.test.ts
package.json
```

## Out of Scope

- External HTTP/request JavaScript validation.
- Shopify offline-session/token lookup.
- Admin API execution.
- Dev MCP invocation from normal Studio requests.
- Live-test receipts.
- Tool editor UI.

## Requirements

### R1 — full Admin definition validation

For a candidate full definition:

1. parse through COMMERCE-016 `CommerceToolDefinitionSchema`;
2. require `execution.kind === 'SHOPIFY_ADMIN_GRAPHQL'`;
3. invoke the COMMERCE-018 local compiler with the exact Tool `inputSchema`;
4. require the compiler's pinned `schemaHash` to equal `definition.execution.schemaHash`;
5. validate responseTemplate against the declared/proved resultSchema;
6. return COMMERCE-019 `ToolAuthoringValidation`.

The normal validation path performs no Dev MCP call, shop/session lookup or Admin API request.

### R2 — schema metadata for authoring UI

Expose the pinned authoring metadata needed by COMMERCE-022 through the named Server Action `src/studio/tools/admin-validation-server-actions.ts`. Every action in that module MUST call `requireStudioPlatformRole('ADMIN')`; do not create a duplicate auth helper or function-valued production port. Return metadata through COMMERCE-019 `ToolAuthoringActionResult`.

The metadata is:

```text
apiVersion = 2026-07
schemaHash = exact committed COMMERCE-018 artifact SHA-256
```

The browser cannot choose a schema path, package version or arbitrary hash.

### R3 — explicit errors and deterministic diagnostics

Compiler syntax/schema/operation/variable/result-shape failures are translated into the common bounded issue form with deterministic paths under `/execution/...`. No raw session/token/provider payload may appear in diagnostics.

Validation/metadata actions are non-mutating. `FORBIDDEN`, `INVALID_INPUT`, `NOT_FOUND`, `DATABASE_UNAVAILABLE` and `INTERNAL_ERROR` remain explicit COMMERCE-019 action results; they MUST NOT become `unknown`/`UNCONFIRMED`. Unexpected errors are logged server-side through the approved shared structured logger.

### R4 — publication relationship

This task proves authoring validity only. It MUST NOT create a live-test receipt. After successful validation, publication remains blocked by COMMERCE-019 `LIVE_TEST_REQUIRED`.

### R5 — focused validation

Add `test:arch021-shopify-admin-authoring-validation` proving:

- valid named Admin query is accepted locally;
- mutation/subscription is rejected;
- wrong schema hash is rejected;
- bounded-query failures from COMMERCE-018 propagate deterministically;
- stale/invalid inputSchema variable mapping is rejected;
- schemaHash metadata is server supplied;
- no Dev MCP/shop session/Admin transport is called;
- common issue/auth contract comes from COMMERCE-019.

## Work Items

- [ ] Add Shopify Admin full-definition validation boundary.
- [ ] Expose pinned API version/schemaHash metadata for authoring UI.
- [ ] Translate compiler diagnostics to the common validation result.
- [ ] Use COMMERCE-019 explicit action results and COMMERCE-027 `requireStudioPlatformRole('ADMIN')`.
- [ ] Add focused zero-provider-I/O tests.

## Interfaces / Contracts

Consumes COMMERCE-016 Tool contracts, COMMERCE-018 compiler and COMMERCE-019 common validation/auth contract.

Produces the authoritative Shopify Admin authoring-validation boundary consumed by COMMERCE-022.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-018
- ARCH-021-COMMERCE-019

## Enables

- ARCH-021-COMMERCE-022

## Acceptance Criteria

- [ ] Shopify Admin authoring validation is server authoritative and zero-provider-I/O.
- [ ] Only compiler-proved pinned Admin 2026-07 query definitions can validate.
- [ ] API version/schemaHash metadata is server owned and not user-selectable.
- [ ] Validation creates no evidence that can satisfy the Phase 3 publication gate.
- [ ] PLATFORM_ADMIN and PLATFORM_SUPER_ADMIN are admitted through hierarchy; merchant roles are denied.
- [ ] Validation/metadata failures remain explicit and never become mutation UNCONFIRMED state.

## Validation

- [ ] `npm run test:arch021-shopify-admin-authoring-validation`
- [ ] `npm run test:arch021-shopify-admin-compiler`
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

Set to `review`, return Completion Report and STOP. Do not build Tool UI or execute Admin GraphQL against a shop.

## Implementation Notes

Shopify Dev MCP remains an explicit developer oracle owned by COMMERCE-018; it is not part of this runtime validation path.

## Completion Report

### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
None
### Deviations
None
### Assumptions
None
### Unresolved Issues
None
### Architectural Concerns
None

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
Pending
### Follow-up
None
