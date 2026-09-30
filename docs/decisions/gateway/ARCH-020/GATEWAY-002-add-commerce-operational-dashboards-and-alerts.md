---
id: ARCH-020-GATEWAY-002
architecture_id: ARCH-020
title: Add Commerce operational dashboards and alerts
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 190
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-020-GATEWAY-001
  - ARCH-020-COMMERCE-010
  - ARCH-020-BACKGROUND-002
enables: []

### Attempt 2 — Superseded by developer architecture decision (2026-09-22)

`moda_architect` records the developer's explicit decision that Commerce dashboards
and alerts will be created and maintained manually in the existing Grafana Cloud
workspace rather than version-controlled/provisioned by `moda-interact-gateway`.

This changes the architecture, so Attempt 2 is **not accepted** and no further rework
is requested. The task is:

```yaml
status: superseded
attempt: 2
executor: null
claimed_at: null
```

The submitted GATEWAY-002 implementation commits, including Attempt 1 `6fb2ac5` and
Attempt 2 `8bae447`, remain historical task-branch evidence only. They are **not
merge candidates** for gateway main because the repository-managed dashboard/alert
capability is no longer wanted.

The retained ARCH-020 observability ownership is:

```text
COMMERCE-010
  -> emit/document Commerce semantic telemetry

BACKGROUND-002
  -> emit/document Background host/evidence-refresh telemetry

GATEWAY-001 + existing platform observability configuration
  -> preserve OTLP/Loki connectivity and environment/service identity

Grafana Cloud Application Observability
  -> generic service rate/error/latency/traces from the existing pipeline

Developer
  -> create/change any custom Grafana dashboards manually
  -> create/change any Grafana alerts manually
```

There is no separate dashboard/alert provisioning implementation task and no hosted
Grafana dashboard/alert evidence gate for ARCH-020 implementation acceptance.

The developer may use C11's emitted signal inventory and previously documented alert
thresholds as operational guidance, but dashboard layouts, alert rules, datasource
UIDs and Grafana provisioning state are not source-controlled ARCH-020 deliverables.

Downstream dependency reconciliation:

- remove `ARCH-020-GATEWAY-002` from COMMERCE-012 dependencies;
- remove `ARCH-020-GATEWAY-002` from SYSTEM-TEST-001 dependencies;
- remove this task from producer/GATEWAY-001 `enables` lists;
- COMMERCE-012 remains Pending because COMMERCE-024 and GATEWAY-003 are still not
  Complete;
- SYSTEM-TEST-001 remains Pending because COMMERCE-012 and SYSTEM-TEST-002 are still
  incomplete/manual-gated.

No downstream task is automatically started.
