---
id: ARCH-030-API-001
architecture_id: ARCH-030
title: Execute all catalogued WooCommerce read operations through the existing grant
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-API-008
  - ARCH-030-SHARED-002
enables:
  - ARCH-030-API-002
created: 2026-10-14
updated: 2026-10-14
---

# Execute all catalogued WooCommerce read operations through the existing grant

## Architecture

Architecture ID: `ARCH-030`.

Architecture document: `docs/architecture/ARCH-030-woocommerce-commerce-tool-authoring.md`.

Coordinator: `moda_architect`.

## Objective

Extend the API-owned shop-scoped outbound Woo connector from products-only to the canonical full WooCommerce GET catalogue.

## Context

The ARCH-026 API-008 connector already owns grant decryption, canonical site identity, pinned outbound transport, neutral credential re-verification and result fail-closed behavior. Its scope explicitly stopped at products, so extending it requires this separate task.

## Scope

- Consume published Shared catalogue/validation (no local independent operation enumeration).
- Resolve every catalogued `GET` operation into a bounded, canonical `wc/v3` path/query and execute with existing shop-bound grant and hardened transport.
- Return bounded, safe result data and granular provider permission/connection outcomes for consumers.

## Out of Scope

- No public proxy endpoint, service-to-service route, Commerce UI, credential change, `POST`/`PUT`/`DELETE`, or arbitrary merchant URL.
- No assumption that Woo keys have permission to all endpoints.

## Requirements

- Do not pre-reject a catalogued GET solely because its category may need additional Woo provider privileges; actually executed denied operations return `provider_forbidden`/approved safe classification.
- Validate integer/string IDs, path segments, allowed query keys, `context`, pagination and result-size bounds; never follow redirects.
- Keep grants selected exclusively from authenticated Shop installation state. Re-check current revocation/rotation around I/O.
- A specific endpoint 403 must not automatically revoke a working read grant. Reauthorization requires established proof of credential invalidity.
- Sensitive Woo responses must be bounded and projected/redacted consistently; never log raw personal data, credentials or provider responses.

## Work Items

- [ ] Build catalogue-driven typed GET preparation with hostile-input tests.
- [ ] Reuse/extend the existing API-008 transport/grant resolver rather than creating a second credential reader.
- [ ] Implement safe output projection/error classification and operation coverage tests.
- [ ] Exercise all advertised operation IDs against a deterministic Woo fixture including `403`, revoked grant, network, 404 and malformed response.

## Interfaces / Contracts

Consumes SHARED-001 contract published by SHARED-002. Uses API-008 internal grant/transport; outputs typed API-local results ready for API-002 private caller boundary.

## Dependencies

- `ARCH-026-API-008`
- `ARCH-030-SHARED-002`

## Enables

- `ARCH-030-API-002`

## Acceptance Criteria

- [ ] Every currently selectable catalogue GET is handled or returns a truthful provider denial; none is silently skipped or downgraded to unrestricted GET.
- [ ] Tenant A cannot use Tenant B grant; rotation/revocation during I/O cannot leak a successful response.
- [ ] 403 on a restricted endpoint is visible and does not revoke an otherwise valid grant.
- [ ] No write operation, arbitrary path, redirect or credential leakage is possible.

## Validation

- [ ] Focused API provider unit/fixture tests, including full-catalogue parity, fail-closed authorization and adverse responses.
- [ ] PostgreSQL integration where required by API-008 grant semantics; report environment blockers rather than claiming a pass.
- [ ] API build/typecheck/lint as available in package scripts, plus git diff --check.

## Stop Condition

After all required Work Items, Acceptance Criteria and Validation pass, record a truthful Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not start dependent tasks or mark this task Complete.

## Implementation Notes

Inspect API-008 Completion Report/review and claim status before execution. Treat the mainline product-only implementation as a baseline, not proof that API-008 has been architect-accepted.

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
