---
id: ARCH-030-SHARED-001
architecture_id: ARCH-030
title: Define canonical WooCommerce GET-operation and test-result contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-030-SHARED-002
created: 2026-10-14
updated: 2026-10-14
---

# Define canonical WooCommerce GET-operation and test-result contract

## Architecture

Architecture ID: `ARCH-030`.

Architecture document: `docs/architecture/ARCH-030-woocommerce-commerce-tool-authoring.md`.

Coordinator: `moda_architect`.

## Objective

Own one versioned, runtime-validatable catalogue and private Woo test request/result contract shared by Commerce and API.

## Context

Commerce currently maintains the ARCH-030 authoring catalogue locally. The API supports only product reads. A private inter-service boundary needs one canonical operation/parameter vocabulary and explicit safe failure classification.

## Scope

- Define canonical versioned `wc/v3` GET operation descriptors matching every operation currently exposed by Commerce Request authoring; preserve stable operation IDs and parameter metadata.
- Define bounded shop-bound execution input (`operationId`, typed parameter/example values, request correlation) and discriminated safe success/failure result with explicit provider authorization outcomes.
- Expose published package validators/types and deterministic compatibility check to prevent Commerce authoring and API allowlist divergence.

## Out of Scope

- No credential storage, transport, service authentication, provider calls, UI changes or schema migrations.
- No generic arbitrary URL or non-GET operation authoring.

## Requirements

- All currently selectable Woo read methods remain expressible; operations unavailable at a given store are reported as provider failures at execution, not silently removed.
- Define strict path/query parameter types, bounds, normalization, content limits and source-compatible catalogue descriptors.
- Represent 401/403 denial vs reauthorization vs not found vs transient provider errors with safe, finite codes and no raw secrets/provider bodies.
- No independent duplicated operation catalogs are approved after consumers migrate.

## Work Items

- [ ] Extract/move shared descriptors and approve a stable versioned import path.
- [ ] Add strict request/result runtime validators and failure-code fixtures.
- [ ] Add catalogue parity and malformed/path-injection/size-bound tests.

## Interfaces / Contracts

Shared package owns both runtime validators and operation descriptors. API and Commerce must consume the **published** package after SHARED-002. Request fields carry only typed operation arguments and server-trusted shop context; no Woo Consumer Key/Secret is representable.

## Dependencies

None.

## Enables

- `ARCH-030-SHARED-002`

## Acceptance Criteria

- [ ] The full current Commerce Woo GET catalogue has an exact, testable canonical Shared representation.
- [ ] Malformed operation IDs, unbounded values, headers, URLs and non-GET requests are rejected.
- [ ] Safe error outcomes include operation permission denial with no automatic connection revocation.
- [ ] No secrets, unrestricted response bodies or credentials are introduced to the contract.

## Validation

- [ ] Focused Shared catalogue parity and Zod/type contract tests pass.
- [ ] Shared package typecheck/build and relevant repository checks pass.
- [ ] git diff --check passes.

## Stop Condition

After all required Work Items, Acceptance Criteria and Validation pass, record a truthful Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not start dependent tasks or mark this task Complete.

## Implementation Notes

Reference the existing Commerce `src/commerce/woocommerce/read-operation-catalogue.ts`; keep a clear one-time migration/re-export plan for the Commerce consumer. The test-result DTO must not become a public unauthenticated API contract.

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

None.

### Unresolved Issues

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed: portable task definition only.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending implementation.

### Follow-up

Await dependency-gated, launcher-materialised execution and independent review.
