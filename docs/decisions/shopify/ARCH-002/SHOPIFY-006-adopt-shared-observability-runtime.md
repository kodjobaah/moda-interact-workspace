---
id: ARCH-002-SHOPIFY-006
architecture_id: ARCH-002
title: Adopt shared observability runtime in Shopify process
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 30
executor: codex
claimed_at: 2026-08-31T14:57:54Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-001
  - ARCH-002-SHARED-010
enables:
  - ARCH-002-SHOPIFY-007
created: 2026-08-31
updated: 2026-08-31
---

# Adopt shared observability runtime in Shopify process

## Objective

Replace the Shopify service's generic local OpenTelemetry bootstrap/provider/
exporter runtime with the published shared Node observability runtime.

## Context

`ARCH-002-SHARED-010` published:

`@modainteract/moda-interact-shared@0.4.0`

The earlier SHOPIFY-003 implementation already contains Shopify-owned webhook
semantic telemetry. Preserve those semantics; this task changes only the generic
runtime/bootstrap boundary.

## Scope

- use exact shared dependency `@modainteract/moda-interact-shared@0.4.0`;
- add a small repository-owned `observability.mjs` preload;
- initialize `.../observability/node` with:
  `serviceName=moda-interact` and
  `instrument={http:true, fetch:true, prisma:true}`;
- preload before the real React Router production entrypoint;
- remove obsolete service-local NodeSDK/provider/exporter/sampler lifecycle code
  only after equivalent shared behaviour is proven;
- preserve existing Shopify webhook semantic spans/metrics and shared logging.

## Out of Scope

- BullMQ Queue telemetry wiring;
- new Shopify business metrics/spans;
- queue payload/contract changes;
- background consumer instrumentation;
- OTLP infrastructure or credentials;
- Grafana configuration;
- unrelated cleanup/refactoring.

## Work Items

- [x] pin the exact shared package version;
- [x] add the Shopify observability preload/profile;
- [x] update the real production start command to preload before React Router;
- [x] migrate/remove obsolete generic local OTel runtime plumbing;
- [x] preserve existing Shopify semantic telemetry;
- [x] add focused preload/runtime ownership tests.

## Acceptance Criteria

- [x] shared runtime starts before React Router/framework imports;
- [x] only one generic tracer/meter provider runtime exists in the process;
- [x] canonical `service.name=moda-interact` is preserved;
- [x] existing Shopify semantic telemetry behaviour is preserved;
- [x] no BullMQ producer work is implemented;
- [x] no service-local exporter/sampler/provider stack remains active.

## Validation

- [x] focused preload/bootstrap tests;
- [x] affected repository tests;
- [x] repository-defined typecheck;
- [x] production build;
- [x] scan/review confirms no duplicate generic provider/exporter bootstrap.

## Stop Condition

After this runtime migration and required validation are complete, set the task
to `review`, write the Completion Report, return to `moda_architect`, and STOP.

Do not begin `ARCH-002-SHOPIFY-007`.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact/observability.mjs`
- `moda-interact/package.json`
- `moda-interact/package-lock.json`
- `moda-interact/app/entry.server.jsx`
- `moda-interact/app/services/otel/otel.bootstrap.ts` (deleted)
- `moda-interact/app/services/otel/otel.server.ts` (deleted)
- `moda-interact/app/services/otel/otel.constants.ts`
- `moda-interact/app/services/otel/otel.runtime.ts`
- `moda-interact/app/services/otel/shopify-webhook-telemetry.server.ts`
- `moda-interact/tests/unit/deploy/startup-contract.test.ts`
- `moda-interact/tests/unit/otel/otel-init.test.js` (deleted)
- `moda-interact/tests/unit/otel/shared-runtime-ownership.test.ts`
- `moda-interact/tests/unit/otel/shopify-webhook-ingress-traceid.test.js`
- `moda-interact/tests/unit/otel/shopify-webhook-telemetry.test.js`
- `docs/decisions/shopify/ARCH-002/SHOPIFY-006-adopt-shared-observability-runtime.md`

### Work Completed

- Pinned `@modainteract/moda-interact-shared@0.4.0` exactly.
- Added `observability.mjs` with the canonical `moda-interact` service profile
  and HTTP, fetch, and Prisma instrumentation enabled.
- Changed the production start command to preload shared observability before
  the real React Router serve entrypoint.
- Removed the local provider/exporter/instrumentation/bootstrap lifecycle and
  its direct production dependencies.
- Preserved Shopify webhook spans, metrics, bounded attributes, logging, and
  active trace-id propagation on the global providers installed by the shared
  runtime.
- Created Shopify semantic instruments once at module scope.
- Added focused executable preload/profile and runtime-ownership tests.
- Confirmed no BullMQ producer telemetry was added.

### Validation Results

- Exact dependency check: `npm ls @modainteract/moda-interact-shared --depth=0`
  passed with `@modainteract/moda-interact-shared@0.4.0`.
- Focused observability validation passed: 4 files, 16 tests.
- Full repository tests passed: 13 files, 75 tests.
- Repository typecheck ran using `npm run typecheck`; it reported the known
  TYPECHECK-001 baseline of 48 errors in 8 unrelated files and no errors in
  task-changed files.
- Production build passed using `npm run build`.
- Source and built-server scans found no service-local NodeSDK, tracer/meter
  provider, OTLP exporter, sampler, batch processor, or old bootstrap.
- Source scan found no shared BullMQ telemetry wiring.

### Deviations

The repository's established TYPECHECK-001 baseline remains unchanged.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted
