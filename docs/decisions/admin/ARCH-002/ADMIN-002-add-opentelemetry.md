---
id: ARCH-002-ADMIN-002
architecture_id: ARCH-002
title: Add OpenTelemetry to admin runtime
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
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

# Add OpenTelemetry to Admin Runtime

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Add baseline vendor-neutral HTTP/database OpenTelemetry instrumentation to the
internal admin runtime while preserving test/production telemetry isolation and
admin/tenant data safety.

## Context

ARCH-002 deploys the admin service as part of the managed topology and accepted
discovery found no OpenTelemetry implementation.

The same logical admin service is deployed into isolated `test` and
`production` environments.

## Scope

- initialize OpenTelemetry once and early enough for supported instrumentation;
- instrument HTTP server/client activity where appropriate;
- instrument relevant PostgreSQL/Prisma operations where supported and safe;
- emit bounded operational latency/error telemetry;
- use canonical resource identity;
- preserve test/production telemetry isolation;
- validate telemetry failure isolation;
- validate sensitive-data/cardinality safety.

## Out of Scope

- internal Grafana UI/embedding;
- tenant-facing analytics/reporting;
- OTLP backend/credential provisioning;
- gateway routing/base-path implementation;
- exposing raw operational telemetry to tenants;
- recording admin business payloads or authentication/session values.

## Requirements

Canonical identity:

```text
service.namespace=moda-interact
service.name=moda-interact-admin
deployment.environment.name=<environment>
```

For deployed ARCH-002 environments:

```text
deployment.environment.name=test
deployment.environment.name=production
```

Do not encode the environment into `service.name`.

Test and production exporter endpoint/credentials must remain independently
configurable.

Local/unit-test hosted export must be disableable.

Telemetry backend failure must not break otherwise valid admin requests or
database transactions solely because export failed.

Telemetry retries/buffering must remain bounded.

Do not emit:

- admin/session credentials;
- cookies or authorization headers;
- database credentials/connection strings;
- cross-tenant sensitive data;
- complete admin request/response bodies;
- SQL parameter values containing tenant/customer/admin data;
- high-cardinality business identifiers as metric labels.

Database instrumentation must not turn SQL/query values into a cross-tenant data
leak.

Operational telemetry remains internal Moda Interact data and must not become a
tenant-facing analytics API.

## Work Items

- [ ] initialize OTel once/early;
- [ ] add baseline HTTP server/client instrumentation;
- [ ] add relevant safe database instrumentation;
- [ ] configure canonical resource identity;
- [ ] preserve test/production environment identity;
- [ ] add bounded request/database metrics where appropriate;
- [ ] add telemetry-backend failure-isolation tests;
- [ ] validate metric cardinality;
- [ ] validate sensitive/admin/tenant data handling;
- [ ] document required OTel variables for GATEWAY-006.

## Interfaces / Contracts

Emits OTel/OTLP telemetry consumed by:

```text
ARCH-002-GATEWAY-006
```

The logical service remains:

```text
moda-interact-admin
```

in both test and production.

This task owns instrumentation only. It does not own telemetry transport or an
admin observability presentation UI.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-GATEWAY-006`

## Acceptance Criteria

- [ ] canonical service identity is correct;
- [ ] test and production differ through deployment environment attributes, not
      service name;
- [ ] expected baseline HTTP/database telemetry is emitted;
- [ ] telemetry backend failure does not break admin requests/transactions;
- [ ] buffering/retry behaviour is bounded;
- [ ] prohibited admin/tenant/credential data is absent;
- [ ] database instrumentation does not expose sensitive parameter values;
- [ ] metric dimensions remain bounded;
- [ ] local/test hosted export can be disabled.

## Validation

- [ ] tests;
- [ ] typecheck/lint as applicable;
- [ ] production build;
- [ ] telemetry failure test;
- [ ] test/production resource-identity test;
- [ ] database telemetry data-safety review;
- [ ] metric-cardinality review;
- [ ] sensitive-data review.

## Implementation Notes

Keep telemetry collection separate from any future admin observability
presentation task.

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
