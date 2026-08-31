---
id: ARCH-002-MESSAGING-003
architecture_id: ARCH-002
title: Adopt shared observability runtime in messaging ingress
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
task_kind: implementation
status: complete
priority: 30
executor: codex
claimed_at: 2026-08-31 15:52:07+00:00
attempt: 1
depends_on:
- ARCH-002-GATEWAY-001
- ARCH-002-SHARED-010
enables:
- ARCH-002-MESSAGING-004
- ARCH-002-MESSAGING-005
created: 2026-08-31
updated: '2026-08-31'
---

# Adopt shared observability runtime in messaging ingress

## Objective

Install and preload the published shared Node observability runtime for the
Meta/WhatsApp ingress process.

## Scope

- use exact shared dependency `@modainteract/moda-interact-shared@0.4.0`;
- add a small repository-owned preload;
- initialize `.../observability/node` with:
  `serviceName=moda-interact-messaging` and
  `instrument={http:true, fetch:true, prisma:false}`;
- preload before the real React Router production entrypoint;
- ensure canonical resource/environment identity is used;
- ensure no competing local NodeSDK/provider/exporter/sampler runtime exists.

## Out of Scope

- Meta/WhatsApp semantic acceptance/latency metrics;
- BullMQ Queue telemetry;
- background consumer instrumentation;
- gateway OTLP wiring;
- business/webhook logic changes.

## Acceptance Criteria

- [x] shared runtime starts before React Router/framework imports;
- [x] canonical `service.name=moda-interact-messaging` is emitted;
- [x] only the shared generic runtime owns providers/exporters/sampling;
- [x] HTTP/fetch instrumentation is enabled and Prisma is disabled;
- [x] local/test hosted export remains disableable.

## Validation

- [x] focused preload/bootstrap tests;
- [x] affected repository tests;
- [x] repository-defined typecheck;
- [x] production build;
- [x] duplicate provider/exporter ownership review.

## Stop Condition

After shared-runtime adoption and required validation are complete, set this task
to `review`, write the Completion Report, return to `moda_architect`, and STOP.

Do not begin MESSAGING-004 or MESSAGING-005.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-messaging/package.json`
- `moda-interact-messaging/package-lock.json`
- `moda-interact-messaging/Dockerfile`
- `moda-interact-messaging/observability.mjs`
- `moda-interact-messaging/tests/startup-contract.test.mjs`
- `docs/decisions/messaging/ARCH-002/MESSAGING-003-adopt-shared-observability-runtime.md`

### Work Completed

- Installed the exact published shared dependency
  `@modainteract/moda-interact-shared@0.4.0` from npm.
- Added a repository-owned preload that initializes the shared Node runtime with
  canonical `serviceName=moda-interact-messaging`, HTTP and fetch enabled, and
  Prisma disabled.
- Changed the production command to preload observability before React Router
  8's actual `@react-router/serve/bin.cjs` entrypoint.
- Added focused Node built-in tests for production ordering, the exact shared
  package/profile, canonical runtime identity, and `OTEL_SDK_DISABLED` local/test
  behavior.
- Confirmed no service-local NodeSDK, provider, exporter, sampler, or BullMQ
  telemetry implementation was introduced.
- Corrected the final production Docker stage to copy `observability.mjs` to
  `/app/observability.mjs`, matching the path used by `npm start`.
- Extended the focused startup contract to verify the preload copy, `/app`
  workdir, and `npm start` command all coexist in the final Docker stage.

### Validation Results

- `npm ls @modainteract/moda-interact-shared --depth=0` passed and resolved the
  exact `0.4.0` release.
- `npm test` passed: 2 tests, 0 failures.
- `npm run typecheck` passed (`react-router typegen && tsc`).
- `npm run build` passed for both React Router client and server bundles.
- `OTEL_SDK_DISABLED=true PORT=4199 npm start` passed from the messaging
  repository; the preloaded production process reached the React Router
  listening state and was then stopped cleanly.
- Duplicate ownership and scope scans found no local NodeSDK, tracer/meter
  provider, OTLP exporter, span processor, sampler, or BullMQ telemetry wiring.
- `git diff --check` passed and editor diagnostics reported no errors in changed
  files.
- `npm install` reported zero vulnerabilities. It emitted an allow-scripts
  advisory for three transitive packages (`fsevents`, `msgpackr-extract`, and
  `protobufjs`); no install or validation failure resulted.
- Two preliminary npm invocations ran from the workspace root instead of the
  messaging repository and therefore did not execute repository validation;
  each required command was rerun from the normalized repository and passed.
- Correction validation: `npm test` passed 3 tests, including the new final
  production-stage packaging contract.
- Correction validation: `docker build -t moda-messaging-003-correction .`
  passed; the final stage copied `observability.mjs` into `/app`.
- Correction validation: the production image started with
  `OTEL_SDK_DISABLED=true` and `PORT=4201`; Docker reported the container
  running with exit code 0 and `GET /` returned HTTP 200.
- The correction test container and temporary image were removed after
  validation. Docker emitted only its legacy-builder deprecation notice and the
  existing npm transitive install-scripts advisories.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31 after the requested correction.

The correction-only pass stayed within scope:

- the final production Docker stage now copies `observability.mjs` to
  `/app/observability.mjs`, matching the preload path required by `npm start`;
- the focused startup-contract test now verifies the preload copy, final
  `/app` working directory and production `npm start` command together;
- `docker build -t moda-messaging-003-correction .` passed;
- the built production image was started with `OTEL_SDK_DISABLED=true` and
  `PORT=4201`;
- the container remained running with exit code 0 and `GET /` returned HTTP 200;
- no observability runtime profile, Meta semantic telemetry, BullMQ Queue
  telemetry or unrelated implementation was introduced.

Compared with the previous MESSAGING-003 submission, only the Dockerfile,
focused startup-contract test and coordination documents changed.

`ARCH-002-MESSAGING-003` is architecturally Complete.

`ARCH-002-MESSAGING-004` and `ARCH-002-MESSAGING-005` are now independently
unblocked and may move to `ready`.