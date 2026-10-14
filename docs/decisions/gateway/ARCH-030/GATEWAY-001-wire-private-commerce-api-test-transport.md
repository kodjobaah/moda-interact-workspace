---
id: ARCH-030-GATEWAY-001
architecture_id: ARCH-030
title: Wire private Commerce to API WooCommerce test transport
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-030-API-002
enables:
  - ARCH-030-COMMERCE-001
created: 2026-10-14
updated: 2026-10-14
---

# Wire private Commerce to API WooCommerce test transport

## Architecture

Architecture ID: `ARCH-030`.

Architecture document: `docs/architecture/ARCH-030-woocommerce-commerce-tool-authoring.md`.

Coordinator: `moda_architect`.

## Objective

Provide the required environment-isolated private API address and service-auth configuration to Commerce without exposing the internal Woo test endpoint publicly.

## Context

Gateway owns Render Blueprint topology/configuration. Commerce currently has no approved private API test transport connection; API-002 must first establish its exact runtime endpoint and authentication/config contract.

## Scope

- Inspect canonical gateway Blueprint for development/test/production Commerce and API private service topology.
- Supply environment-matched private API target/config names and secret placeholders required by API-002; preserve existing gateway public ingress policy.
- Document deployment sequence and private endpoint reachability/rollback.

## Out of Scope

- No API or Commerce application implementation.
- Do not place credentials in render.yaml, expose the internal endpoint publicly, or route cross-environment.

## Requirements

- API target must resolve to the matching environment only; existing public API routes and Commerce Studio routing remain intact.
- Only approved server runtimes receive private configuration and service-auth secrets; browser cannot access it.
- Use existing Blueprint mechanisms, avoid adding infrastructure unless inspection proves it necessary.

## Work Items

- [ ] Document actual API-002 endpoint and runtime variable needs.
- [ ] Update required Blueprint declarations without secrets.
- [ ] Extend Blueprint validation to reject cross-environment or public exposure.

## Interfaces / Contracts

Consumes exact runtime config agreed by API-002. Commerce will receive only a private service URL and service-auth runtime secret, never Woo REST consumer keys.

## Dependencies

- `ARCH-030-API-002`

## Enables

- `ARCH-030-COMMERCE-001`

## Acceptance Criteria

- [ ] Commerce can reach API privately with correctly scoped runtime configuration.
- [ ] Public gateway cannot reach internal Studio Woo test endpoint.
- [ ] No secrets committed or cross-environment target mismatches.

## Validation

- [ ] Run repository Blueprint validation suites covering all applicable environments.
- [ ] Run negative configuration / secret-leak tests and git diff --check.

## Stop Condition

After all required Work Items, Acceptance Criteria and Validation pass, record a truthful Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not start dependent tasks or mark this task Complete.

## Implementation Notes

If inspection proves existing Blueprint already provides the required private routing/configuration, document equivalence and return to architect for narrowing; do not create redundant infrastructure.

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
