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

# Add OpenTelemetry to Shopify Ingress

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Instrument the Shopify HTTP/webhook runtime with architecture-approved,
vendor-neutral OpenTelemetry telemetry and correlation propagation.

## Context

Accepted discovery found no OpenTelemetry implementation in `moda-interact`.

ARCH-002 requires operational visibility in both test and production without
making telemetry a correctness dependency.

## Scope

- initialize OpenTelemetry once and early enough for supported HTTP
  instrumentation;
- instrument inbound/outbound HTTP where required;
- emit bounded Shopify webhook latency/error/acceptance telemetry;
- propagate trace/correlation context into produced asynchronous work where the
  accepted queue/shared boundary supports it;
- use canonical resource identity;
- support standard OTel environment configuration;
- preserve test/production telemetry isolation;
- validate telemetry failure isolation;
- validate sensitive-data and metric-cardinality restrictions.

## Out of Scope

- OTLP backend/credential provisioning;
- Grafana dashboards;
- background consumer instrumentation;
- changing webhook business contracts unless an architect-approved
  trace-context contract is required;
- logging/storing complete Shopify webhook payloads;
- tenant-facing analytics.

## Requirements

Canonical resource identity:

```text
service.namespace=moda-interact
service.name=moda-interact
deployment.environment.name=<environment>
```

For deployed ARCH-002 environments:

```text
deployment.environment.name=test
deployment.environment.name=production
```

Do not encode the environment into `service.name`.

Test and production exporter endpoint/credentials must remain independently
configurable through infrastructure.

Local/unit-test hosted export must be disableable.

Telemetry export failure must not reject Shopify webhooks, prevent durable queue
acceptance or change business success/failure semantics.

Telemetry buffering/retries must remain bounded.

Do not emit:

- Shopify access tokens;
- authorization/cookie headers;
- OAuth authorization codes;
- complete webhook payloads;
- customer PII;
- high-cardinality business identifiers as metric labels.

If async trace propagation requires a shared contract change, return the required
change to `moda_architect` rather than modifying cross-service business contracts
inside this task.

## Work Items

- [ ] initialize OTel exactly once/early;
- [ ] add HTTP server/client instrumentation where required;
- [ ] add bounded Shopify ingress metrics/spans;
- [ ] add canonical resource attributes;
- [ ] propagate context to async publication where architecture-compatible;
- [ ] preserve test/production resource isolation;
- [ ] add exporter-failure isolation tests;
- [ ] add metric-cardinality validation;
- [ ] add sensitive-data validation;
- [ ] document required OTel variables for GATEWAY-006.

## Interfaces / Contracts

Emits OTel/OTLP-compatible telemetry.

Infrastructure transport/credentials are owned by:

```text
ARCH-002-GATEWAY-006
```

The logical service name remains:

```text
moda-interact
```

in both test and production.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-GATEWAY-006`

## Acceptance Criteria

- [ ] expected canonical service identity is emitted;
- [ ] test and production differ through deployment environment attributes rather
      than service name;
- [ ] webhook processing succeeds when telemetry backend is unavailable;
- [ ] HTTP/webhook telemetry is emitted with bounded cardinality;
- [ ] correlation/trace context is preserved where architecture-compatible;
- [ ] any required cross-service contract change is returned to the architect;
- [ ] no prohibited secrets/payloads appear in telemetry;
- [ ] telemetry buffering/retry behaviour is bounded;
- [ ] local/test hosted export can be disabled.

## Validation

- [ ] unit/integration tests;
- [ ] typecheck;
- [ ] production build;
- [ ] telemetry failure test;
- [ ] test/production resource identity test;
- [ ] sensitive-data review;
- [ ] metric-cardinality review.

## Implementation Notes

Prefer standard OpenTelemetry environment variables and backend-neutral APIs.

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
