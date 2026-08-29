---
id: ARCH-002-GATEWAY-006
architecture_id: ARCH-002
title: Configure OpenTelemetry transport and environment wiring
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-002-GATEWAY-002
  - ARCH-002-SHOPIFY-003
  - ARCH-002-MESSAGING-002
  - ARCH-002-ADMIN-002
  - ARCH-002-BACKGROUND-003
enables: 
  - ARCH-002-GATEWAY-003
created: 2026-08-29
updated: 2026-08-29
---

# Configure OpenTelemetry transport and environment wiring

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Configure the infrastructure-side OTLP/exporter/environment model for ARCH-002 instrumented services and gateway operational visibility.

## Context

Application emitters are owner-specific. `moda_gateway` owns OTLP endpoint/auth wiring, environment-specific configuration, gateway request/correlation infrastructure and backend transport.

## Scope

- define standard OTEL environment-variable declarations;
- define production/development environment identity wiring;
- configure OTLP endpoint/auth secret placeholders;
- configure gateway request/correlation IDs and structured access/error logging;
- configure architecture-approved telemetry transport/backend integration;
- document sampling, retention/cost assumptions where applicable;
- document failure-isolation behaviour.

## Out of Scope

- implementing application instrumentation in other repositories;
- tenant analytics;
- exposing Grafana/raw telemetry to merchants;
- committing exporter credentials.

## Requirements

Applications remain vendor-neutral and use OTLP.

Every instrumented service must emit `service.namespace=moda-interact` and explicit `deployment.environment.name`.

Production and non-production telemetry must be distinguishable.

Exporter/backend failure must not become a correctness dependency.

Secret values must use Render/provider secret mechanisms.

## Work Items

- [ ] define OTEL env contract/placeholders;
- [ ] configure environment isolation;
- [ ] configure gateway request/correlation logging;
- [ ] configure OTLP/backend transport;
- [ ] document sampling/retention/cost assumptions;
- [ ] document failure isolation;
- [ ] add infrastructure validation.

## Interfaces / Contracts

Consumes telemetry emitted by SHOPIFY-003, MESSAGING-002, ADMIN-002 and BACKGROUND-003. Produces configuration consumed by GATEWAY-003.

## Dependencies

- `ARCH-002-GATEWAY-002`
- `ARCH-002-SHOPIFY-003`
- `ARCH-002-MESSAGING-002`
- `ARCH-002-ADMIN-002`
- `ARCH-002-BACKGROUND-003`

## Enables

- `ARCH-002-GATEWAY-003`

## Acceptance Criteria

- [ ] OTLP settings are standard/vendor-neutral at app boundary;
- [ ] no exporter credentials committed;
- [ ] production/non-production identity is explicit;
- [ ] gateway logs/request IDs are operationally usable;
- [ ] backend outage does not affect business correctness;
- [ ] infrastructure configuration is documented/testable.

## Validation

- [ ] configuration validation;
- [ ] secret scan/review;
- [ ] OTLP connectivity test where credentials/environment are available;
- [ ] gateway logging/correlation test.

## Implementation Notes

Do not require a specific hosted backend in application code. Backend-specific configuration belongs here.

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
