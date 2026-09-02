# ARCH-002 Shared Tasks

Architecture:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Assigned Agent:

`moda_shared`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| SHARED-002 | Implement reusable structured logging library | Complete | GATEWAY-001 |
| SHARED-003 | Document and publish shared logging package release | Complete | SHARED-002 |
| SHARED-004 | Add OpenTelemetry log emission to shared structured logger | Complete | SHARED-003 |
| SHARED-006 | Add direct Grafana Loki transport to shared logger | Complete | SHARED-004 |
| SHARED-005 | Publish OTel + Loki shared logger release | Complete | SHARED-004, SHARED-006 |

The individual task file is authoritative for task state.

## Shared Observability Runtime Extension

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| SHARED-005 | Publish accepted shared logging transports | Complete | SHARED-004, SHARED-006 |
| SHARED-007 | Add reusable base Node observability runtime | Complete | SHARED-005 |
| SHARED-008 | Add Prisma and BullMQ observability adapters | Complete | SHARED-007 |
| SHARED-009 | Add GenAI active-span helpers | Complete | SHARED-007 |
| SHARED-011 | Add bounded GenAI operational metrics | Complete | SHARED-009 |
| SHARED-010 | Publish complete shared observability runtime | Complete | SHARED-007, SHARED-008, SHARED-009, SHARED-011 |

## GenAI Composability Correction

BACKGROUND-008 exposed a published API boundary gap in `0.4.0`. The background
consumer must not duplicate shared span mechanics or start its dependent metric
task early.

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| SHARED-012 | Decouple GenAI span activation and add safe exception mapping | Complete | SHARED-010 |
| SHARED-013 | Publish composable GenAI observability release (`0.5.0`) | Complete | SHARED-012 |

Execution:

```text
SHARED-012
    |
    v
SHARED-013
    |
    v
BACKGROUND-008
```

SHARED-012 is implementation work. SHARED-013 is publication-only.

