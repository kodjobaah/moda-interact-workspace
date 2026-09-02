---
id: ARCH-002-GATEWAY-006
architecture_id: ARCH-002
title: Configure OpenTelemetry transport and environment wiring
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 35
executor: github-copilot
claimed_at: 2026-09-02T12:15:40Z
attempt: 1
depends_on:
- ARCH-002-GATEWAY-002
- ARCH-002-SHOPIFY-006
- ARCH-002-MESSAGING-003
- ARCH-002-ADMIN-009
- ARCH-002-BACKGROUND-005
enables:
- ARCH-002-GATEWAY-003
- ARCH-002-ADMIN-004
- ARCH-002-SYSTEM-TEST-002
created: 2026-08-29
updated: 2026-09-02
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

GATEWAY-006 is intentionally gated by each deployable process having adopted the shared observability runtime/exporter contract. It is not gated by every later Moda-specific semantic metric or span, because transport can be configured before those additional signals are validated end-to-end.

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

Application-owned telemetry remains vendor-neutral. Traces and metrics use OpenTelemetry/OTLP. Logs use the shared structured logging contract with the independently configurable Loki-compatible transport selected by the current ARCH-002 deployment policy.

Every instrumented service must emit `service.namespace=moda-interact` and explicit `deployment.environment.name`.

Production and non-production telemetry must be distinguishable.

Exporter/backend failure must not become a correctness dependency.

Secret values must use Render/provider secret mechanisms.

## Work Items

- [x] define OTEL env contract/placeholders;
- [x] configure environment isolation;
- [x] configure gateway request/correlation logging;
- [x] configure signal-specific OTLP/Loki/backend transport;
- [x] document sampling/retention/cost assumptions;
- [x] document failure isolation;
- [x] add infrastructure validation.

## Interfaces / Contracts

Consumes the accepted runtime/exporter contracts established by SHOPIFY-006, MESSAGING-003, ADMIN-009 and BACKGROUND-005, plus the accepted public-gateway implementation from GATEWAY-002. Produces signal-specific OTLP/Loki/backend/environment configuration consumed by GATEWAY-003, ADMIN-004 and SYSTEM-TEST-002.

Later semantic telemetry tasks such as SHOPIFY-007, MESSAGING-004, MESSAGING-005, BACKGROUND-007 and BACKGROUND-009 remain architecture-required signals validated by SYSTEM-TEST-002, but they do not block infrastructure transport configuration.

## Dependencies

- `ARCH-002-GATEWAY-002`
- `ARCH-002-SHOPIFY-006`
- `ARCH-002-MESSAGING-003`
- `ARCH-002-ADMIN-009`
- `ARCH-002-BACKGROUND-005`

## Enables

- `ARCH-002-GATEWAY-003`
- `ARCH-002-ADMIN-004`
- `ARCH-002-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] OTLP settings are standard/vendor-neutral at app boundary;
- [x] no exporter credentials committed;
- [x] production/non-production identity is explicit;
- [x] gateway logs/request IDs are operationally usable;
- [x] backend outage does not affect business correctness;
- [x] infrastructure configuration is documented/testable.

## Validation

- [x] configuration validation;
- [x] secret scan/review;
- [ ] OTLP connectivity test where credentials/environment are available;
- [x] gateway logging/correlation test.

## Implementation Notes

Do not require a specific hosted backend in application code. Backend-specific configuration belongs here.

## Completion Report

### Status

Accepted / Complete

### Files Changed

 - `moda-interact-gateway/docs/observability.md` — independent signal routing,
	Grafana Cloud/Loki backend selection, shared-runtime log capability,
	environment identity evidence, secret handling, cost assumptions and failure
	isolation.
 - `moda-interact-gateway/README.md` — observability contract link.
 - `moda-interact-gateway/docs/gateway.md` — GATEWAY-006 observability scope
	and GATEWAY-003 Blueprint boundary.
 - `moda-interact-gateway/tests/validate-observability-config.sh` — static
	contract and no-secret validation.
 - `docs/decisions/gateway/ARCH-002/GATEWAY-006-configure-otel-infrastructure.md`
	— completion report.

### Work Completed

 - Recorded traces and metrics as OpenTelemetry -> OTLP -> Grafana Cloud and
	logs as shared structured logging -> Loki-compatible transport -> Grafana
	Cloud/Loki, with each signal independently configurable.
 - Inspected the accepted shared runtime: the same record can reach Loki and
	OTLP Logs when both are enabled, but ARCH-002 enables Loki logs and disables
	OTLP Logs by default to avoid duplicate persistence and cost. Shared Logs
	capability remains intact.
 - Recorded the accepted runtime identity input: each preload supplies only its
	canonical service name; shared resolution consumes
	`DEPLOYMENT_ENVIRONMENT_NAME`, then `OTEL_DEPLOYMENT_ENVIRONMENT`, then
	`NODE_ENV`, with `development` fallback.
 - Documented separate test/production endpoint and credential wiring using
	Render secret mechanisms; Blueprint placement remains GATEWAY-003 scope.
 - Documented direct exporter transport with no initial OpenTelemetry Collector,
	NGINX structured logs, request/correlation IDs, bounded data policy and
	failure isolation.
 - Added revision-focused static validation without introducing a local
	telemetry provider, exporter, application instrumentation or committed secret.

### Validation Results

 - `tests/validate-observability-config.sh`: pass after revision; signal routing,
	deployment policy, collector policy, unknown retention and estimated cost
	assumptions are present.
 - `tests/run-tests.sh`: pass, 44 passed, 0 failed, including request/correlation
	IDs, structured logging, sensitive-query safety, upstream failure isolation and
	NGINX configuration rendering.
 - Secret/configuration review: pass; no OTLP or Loki credentials/token values
	committed.
 - Hosted OTLP/Loki connectivity test: not run and intentionally unchecked
	because real hosted credentials/endpoints were unavailable; no backend arrival
	is claimed.

### Deviations

Production sampling, provider retention and observability cost remain
deployment-defined or estimated until real traffic and backend configuration
are measured.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review
### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-GATEWAY-006` is architect-accepted.

The revision correctly separates traces, metrics and logs into independently
configurable signal paths:

```text
traces  -> OpenTelemetry -> OTLP -> Grafana Cloud
metrics -> OpenTelemetry -> OTLP -> Grafana Cloud
logs    -> shared structured logging -> Loki-compatible transport
        -> Grafana Cloud / Loki
```

The current deployment policy prevents unintended duplicate log persistence by
keeping OTLP Logs disabled unless a later explicit architecture decision
justifies dual export. Shared OpenTelemetry Logs capability remains available;
it is not removed from `moda-interact-shared`.

The gateway remains a thin NGINX infrastructure boundary. No second local
OpenTelemetry provider/exporter was introduced.

The accepted environment-identity mapping records the existing shared runtime
resolver rather than inventing a new application-level contract.

Sampling, retention and cost assumptions are correctly classified as
configurable, `UNKNOWN`, `ESTIMATED`, or deployment-defined where measurement is
not yet available.

Hosted OTLP/Loki connectivity is intentionally not claimed by this task because
real hosted credentials/endpoints were unavailable. End-to-end backend arrival
remains a deployment/system-validation concern.

### Reviewed Files

- `moda-interact-gateway/docs/observability.md`
- `moda-interact-gateway/README.md`
- `moda-interact-gateway/docs/gateway.md`
- `moda-interact-gateway/nginx/nginx.conf.template`
- `moda-interact-gateway/tests/validate-observability-config.sh`
- `docs/decisions/gateway/ARCH-002/GATEWAY-006-configure-otel-infrastructure.md`
- `docs/decisions/gateway/ARCH-002/GATEWAY-006-architect-review-amendment.md`

### Validation Reviewed

Architect independently ran:

```text
tests/validate-observability-config.sh
```

Result:

```text
observability contract validation passed
```

A bounded secret-literal scan of the reviewed gateway bundle returned no
committed OTLP/Loki credential values.

The implementation agent reported:

```text
tests/run-tests.sh
44 passed, 0 failed
```

The architect review environment did not provide Docker, so that Docker-backed
suite was not independently re-executed here.

Hosted OTLP/Loki connectivity was not run and remains unchecked by design.

### Architecture Conformance

Accepted.

The implementation conforms to the ARCH-002 signal-routing amendment:

- traces and metrics use vendor-neutral OpenTelemetry/OTLP;
- structured logs use the independently configurable Loki-compatible path;
- Grafana Cloud is the current hosted backend without becoming an application
  API dependency;
- signal destinations may diverge in a future architecture;
- duplicate Loki + OTLP log persistence is not the default;
- observability failure remains isolated from business correctness;
- secrets remain deployment-managed.

### Follow-up

`ARCH-002-GATEWAY-006` is Complete.

Its completion satisfies the GATEWAY-006 prerequisite for downstream tasks but
does not by itself make those tasks executable. Each downstream task must be
re-evaluated against its own complete `depends_on` list before being moved to
`ready`.

Do not automatically start `GATEWAY-003`, `ADMIN-004`, or
`SYSTEM-TEST-002` solely because this task is now Complete.
