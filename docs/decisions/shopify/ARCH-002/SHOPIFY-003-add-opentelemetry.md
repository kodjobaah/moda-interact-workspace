---
id: ARCH-002-SHOPIFY-003
architecture_id: ARCH-002
title: Add OpenTelemetry to Shopify ingress
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-002-GATEWAY-001
enables: 
  - ARCH-002-GATEWAY-006
created: 2026-08-29
updated: 2026-08-29
---

# Add OpenTelemetry to Shopify ingress

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Instrument the Shopify HTTP/webhook runtime with architecture-approved OpenTelemetry telemetry and correlation propagation.

## Context

Accepted discovery found no OpenTelemetry implementation in `moda-interact`; ARCH-002 requires production ingress visibility without making telemetry a correctness dependency.

## Scope

- initialize OpenTelemetry once and early enough for HTTP instrumentation;
- emit HTTP/webhook latency/error/acceptance telemetry;
- propagate trace/correlation context into produced asynchronous work where the shared/event boundary supports it;
- use canonical resource identity;
- support standard OTEL environment configuration;
- validate sensitive-data restrictions.

## Out of Scope

- OTLP backend/credential provisioning;
- Grafana dashboards;
- background consumer instrumentation;
- changing webhook business contracts unless an architect-approved trace-context contract is required.

## Requirements

Resource identity:
`service.namespace=moda-interact`
`service.name=moda-interact`
`deployment.environment.name=<environment>`.

Telemetry export failure must not reject Shopify webhooks or durable queue acceptance.

Do not emit access tokens, authorization headers or full sensitive webhook payloads.

## Work Items

- [ ] initialize OTel exactly once;
- [ ] add HTTP server/client instrumentation where required;
- [ ] add bounded Shopify ingress metrics/spans;
- [ ] propagate context to async publication where architecture-compatible;
- [ ] add resource attributes;
- [ ] add failure-isolation tests;
- [ ] add sensitive-data validation.

## Interfaces / Contracts

Emits OpenTelemetry/OTLP-compatible telemetry. Infrastructure transport is owned by `ARCH-002-GATEWAY-006`.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-GATEWAY-006`

## Acceptance Criteria

- [ ] expected service identity is emitted;
- [ ] webhook processing succeeds when telemetry backend is unavailable;
- [ ] HTTP/webhook telemetry is emitted;
- [ ] correlation/trace context is preserved where required;
- [ ] no prohibited secrets/payloads appear in telemetry;
- [ ] local/test export can be disabled.

## Validation

- [ ] unit/integration tests;
- [ ] typecheck;
- [ ] production build;
- [ ] telemetry failure test.

## Implementation Notes

Prefer standard OpenTelemetry environment variables. Keep application semantics vendor-neutral.

## Completion Report

### Status

Not Started

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

Pending

### Review Notes

Pending implementation.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
