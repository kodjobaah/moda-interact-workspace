# Resolution

**Resolved by `moda_architect`: Accepted / Complete — 2026-09-02.**

The changes requested below were satisfied by the submitted GATEWAY-006
revision. This file is retained as historical review evidence and is no longer
an executable instruction.

The authoritative task state is recorded in:

```text
docs/decisions/gateway/ARCH-002/GATEWAY-006-configure-otel-infrastructure.md
```

---

# ARCH-002-GATEWAY-006 Architect Review Amendment

## Task

```text
ARCH-002-GATEWAY-006
```

## Current state

```yaml
status: review
architect_review:
  status: changes_requested
```

The task remains the same task.

Do not create a replacement task.

Do not transition it to `complete` until the corrections below are returned for
architect review.

Do not start a downstream task automatically.

## Governing architecture amendment

Read and obey:

```text
docs/architecture/ARCH-002-observability-signal-routing-amendment.md
```

This amendment clarifies that traces, metrics and logs are independently
configurable signals.

## Required revision

### 1. Document the actual signal-specific transport model

Update the gateway observability documentation so it explicitly distinguishes:

```text
traces  -> OpenTelemetry -> OTLP -> current trace backend
metrics -> OpenTelemetry -> OTLP -> current metrics backend
logs    -> shared structured logging -> Loki-compatible transport
        -> current log backend
```

For the current ARCH-002 backend selection, record:

```text
traces  -> OTLP -> Grafana Cloud
metrics -> OTLP -> Grafana Cloud
logs    -> Loki-compatible transport -> Grafana Cloud / Loki
```

Do not describe all signals as one inseparable `OTLP -> Grafana Cloud` pipeline.

### 2. Preserve future backend independence

Document this invariant:

```text
Trace, metric and log destinations are independently configurable.
```

Changing the log backend must not require changing Moda-owned application logging
calls or trace/metric instrumentation.

### 3. Reconcile Loki and OpenTelemetry Logs

Inspect the accepted shared runtime and document the real deployed log behaviour.

Explicitly determine whether the same structured log record can currently be sent
to both:

```text
Loki
```

and:

```text
OTLP /v1/logs
```

For ARCH-002, the default deployment policy is:

```text
OTLP traces:   enabled
OTLP metrics:  enabled
Loki logs:     enabled
OTLP logs:     disabled unless explicitly justified
```

Do not remove shared OpenTelemetry Logs support merely to satisfy this task.

Do not modify another repository's logging implementation unless the architect
creates a separate owning-repository task.

If dual log persistence is genuinely required, stop and report the justification,
expected duplication and cost implications to `moda_architect`.

### 4. Document backend and collector decision

Record that:

- Grafana Cloud is the current trace/metric hosted backend;
- Grafana Cloud/Loki is the current log backend;
- application telemetry remains vendor-neutral;
- direct exporter transport is the initial ARCH-002 model;
- no OpenTelemetry Collector is introduced initially;
- a collector requires a future concrete architecture requirement.

Do not commit endpoint credentials.

### 5. Verify environment configuration against accepted runtime contracts

Do not invent a new cross-repository environment-variable contract.

Inspect the accepted implementations associated with:

```text
ARCH-002-SHOPIFY-006
ARCH-002-MESSAGING-003
ARCH-002-ADMIN-009
ARCH-002-BACKGROUND-005
```

Produce a small mapping in the Completion Report/documentation:

```text
Deployable                 Actual environment identity input
-------------------------  ---------------------------------
moda-interact              <inspected implementation>
moda-interact-messaging    <inspected implementation>
moda-interact-admin        <inspected implementation>
background workers         <inspected implementation>
```

The required output invariant remains:

```text
service.namespace=moda-interact
service.name=<canonical-logical-service-name>
deployment.environment.name=test|production
```

If `DEPLOYMENT_ENVIRONMENT_NAME` is actually consumed by all accepted runtimes,
document the evidence.

If it is not, correct GATEWAY-006 documentation/configuration rather than creating
a new implicit application contract.

### 6. Complete sampling / retention / cost documentation

Document actual assumptions without inventing precision.

At minimum record:

- trace sampling is configurable per environment;
- test may use higher sampling for validation;
- exact production sampling remains an assumption until measured;
- metrics should remain bounded/low-cardinality;
- high-volume full payload logging is prohibited;
- exact provider retention is `UNKNOWN`/deployment-defined until configured;
- observability cost is `ESTIMATED`/`UNKNOWN` until ingestion volume is measured;
- trace, metric and log costs must be considered independently.

### 7. Correct validation bookkeeping

The task validation record must match the work actually performed.

If already proven, mark:

```text
[x] configuration validation
[x] secret scan/review
[x] gateway logging/correlation test
```

Leave:

```text
[ ] hosted OTLP/Loki connectivity validation
```

unchecked when real credentials/endpoints were unavailable.

Do not claim hosted backend arrival without actual evidence.

### 8. Validation after revision

Re-run only the validation relevant to files modified by this revision.

Do not rerun unrelated repository implementation tasks.

At minimum:

- gateway observability configuration/static validation;
- gateway logging/correlation tests if affected;
- secret/configuration review;
- documentation consistency check.

## Ownership constraints

`moda_gateway` may modify:

- gateway repository observability/configuration/docs owned by the task;
- the GATEWAY-006 Completion Report/task record as allowed by the task protocol.

`moda_gateway` must not modify implementation owned by:

- `moda_app`;
- `moda_messaging`;
- `moda_admin`;
- `moda_background`;
- `moda_shared`;

unless separately assigned by `moda_architect`.

## Completion behaviour

When the revision is complete:

```text
status remains: review
```

Update the Completion Report with:

- files changed;
- exact signal-routing decision;
- Loki vs OTLP Logs result;
- environment-variable mapping evidence;
- sampling/retention/cost assumptions;
- validation commands/results;
- unresolved items, if any.

Then STOP and return the task to `moda_architect`.

Do not start:

```text
ARCH-002-GATEWAY-003
ARCH-002-ADMIN-004
ARCH-002-SYSTEM-TEST-002
```

automatically.
