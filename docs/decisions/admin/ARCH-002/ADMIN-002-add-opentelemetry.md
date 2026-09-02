---
id: ARCH-002-ADMIN-002
architecture_id: ARCH-002
title: Add OpenTelemetry to admin runtime
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: superseded
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-002-GATEWAY-001
- ARCH-002-SHARED-010
enables: []
created: 2026-08-29
updated: '2026-08-31'
---
# Add OpenTelemetry to Admin Runtime

## Superseded — Granular Replacement (2026-08-31)

This task must not be executed.

The broad admin observability task is replaced by shared-runtime adoption in
`ARCH-002-ADMIN-009`. `ARCH-002-ADMIN-010` was later Superseded after architect
review determined that its generic request metrics duplicated standard
Next.js/OpenTelemetry HTTP telemetry.

This change applies the current architect task-granularity policy. Historical
implementation/completion material below is retained only as evidence and does
not define executable scope.

## Current Architect Instruction — Shared Runtime

This task's executable architecture is the shared-runtime amendment in this
file plus `docs/observability/shared-observability-runtime.md`. Any earlier
service-local NodeSDK/provider/exporter/bootstrap instructions or completion
notes are historical implementation evidence and are superseded where they
conflict with the shared-runtime amendment. Service/domain semantic telemetry
remains owned by this repository.

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

## Architect Amendment — Shared Observability Runtime (2026-08-31)

**This amendment supersedes any conflicting service-local NodeSDK/provider/
exporter/bootstrap instructions earlier in this task.** Admin owns internal
request/database semantic telemetry; generic runtime plumbing is shared.

Do not resume implementation until `ARCH-002-SHARED-010` is architect-accepted
Complete.

Then:

1. consume the exact published shared version;
2. read `docs/observability/shared-observability-runtime.md`;
3. add a process preload with:

```js
initNodeObservability({
  serviceName: "moda-interact-admin",
  instrument: { http: true, fetch: true, prisma: true },
});
```

4. for the current Next.js production shape, preload before the Next CLI:

```text
node --import ./observability.mjs ./node_modules/next/dist/bin/next start
```

5. preserve admin-specific request/database semantic telemetry using the global
   provider installed by shared runtime;
6. remove obsolete local provider/exporter/bootstrap logic only after parity is
   proven;
7. do not put Grafana embedding/presentation code into the shared runtime;
8. validate tenant/admin data safety and database telemetry sensitivity.

Reference code:
`docs/decisions/shared/ARCH-002/reference-observability/services/moda-interact-admin/`.
