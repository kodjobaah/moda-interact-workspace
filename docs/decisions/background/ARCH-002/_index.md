# ARCH-002 Background Tasks

Architecture:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Assigned Agent:

`moda_background`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| BACKGROUND-001 | Create independently deployable worker entrypoints | Complete | GATEWAY-001 |
| BACKGROUND-002 | Add worker dependency readiness | Complete | BACKGROUND-001 |
| BACKGROUND-003 | Add OpenTelemetry to background workers | Superseded | Replaced by BACKGROUND-005/006/007/008/009 |
| BACKGROUND-004 | Use published shared package in background service | Complete | GATEWAY-001, SHARED-010 |
| BACKGROUND-005 | Adopt shared observability runtime in production workers | Complete | BACKGROUND-001, BACKGROUND-002, BACKGROUND-004, SHARED-010 |
| BACKGROUND-006 | Wire shared BullMQ telemetry in background processing | Complete | BACKGROUND-005 |
| BACKGROUND-007 | Add bounded background worker operational metrics | Complete | BACKGROUND-006 |
| BACKGROUND-008 | Integrate GenAI active spans in messaging worker | Complete | BACKGROUND-006, SHARED-013 |
| BACKGROUND-009 | Integrate bounded GenAI operational metrics in messaging worker | Complete | BACKGROUND-008 |

Canonical worker deployment units:

```text
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
```

These are Render background-worker services. They consume work through
Redis/BullMQ and do not require inbound HTTP routing.

The individual task file is authoritative for task state.

## Shared Observability Amendment

`BACKGROUND-003` is Superseded. The executable observability rollout is the
granular BACKGROUND-005/006/007/008/009 chain, with shared runtime mechanics
remaining in `moda-interact-shared` and worker/domain semantics in
`moda_background`.


## Current Observability Execution State

The accepted background observability chain is now:

```text
BACKGROUND-005   shared runtime                         Complete
BACKGROUND-006   BullMQ trace propagation               Complete
BACKGROUND-007   bounded worker operational metrics     Complete
BACKGROUND-008   GenAI active spans                     Complete
BACKGROUND-009   GenAI operational metrics              Complete
```

BACKGROUND-008 consumes the exact shared release published by SHARED-013:

```text
@modainteract/moda-interact-shared@0.5.0
```

The ARCH-002 background observability branch is now fully Complete.

The background prerequisite for `GATEWAY-006` and `SYSTEM-TEST-002` is now
satisfied. Their final readiness still depends on their remaining cross-domain
prerequisites and must be reconciled by `moda_architect` from the full ARCH-002
coordination state.
