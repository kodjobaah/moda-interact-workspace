# ARCH-002 Background Tasks

Architecture:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Assigned Agent:

`moda_background`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| BACKGROUND-001 | Create independently deployable worker entrypoints | Ready | GATEWAY-001 |
| BACKGROUND-002 | Add worker dependency readiness | Pending | BACKGROUND-001 |
| BACKGROUND-003 | Add OpenTelemetry to background workers | Pending | BACKGROUND-001 |
| BACKGROUND-004 | Use published shared package in background service | Ready | GATEWAY-001 |

Canonical worker deployment units:

```text
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
```

These are Render background-worker services. They consume work through
Redis/BullMQ and do not require inbound HTTP routing.

The individual task file is authoritative for task state.
