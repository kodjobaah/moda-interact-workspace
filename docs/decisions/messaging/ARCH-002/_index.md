# ARCH-002 Messaging Tasks

Architecture:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Assigned Agent:

`moda_messaging`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| MESSAGING-001 | Add messaging service health and readiness | Complete | GATEWAY-001 |
| MESSAGING-002 | Add OpenTelemetry to Meta ingress | Superseded | Replaced by MESSAGING-003/004/005 |
| MESSAGING-003 | Adopt shared observability runtime in messaging ingress | Complete | GATEWAY-001, SHARED-010 |
| MESSAGING-004 | Add bounded Meta ingress semantic telemetry | Complete | MESSAGING-003 |
| MESSAGING-005 | Wire shared BullMQ telemetry on inbound message queue | Complete | MESSAGING-003 |

Messaging tasks must preserve the same logical runtime contract in test and
production while infrastructure supplies isolated Redis, Meta and telemetry
configuration.

The individual task file is authoritative for task state.

## Shared Observability Amendment

`MESSAGING-002` is Superseded.

`MESSAGING-003` adopts the published shared HTTP/Undici runtime.
`MESSAGING-004` owns bounded Meta/WhatsApp ingress semantics.
`MESSAGING-005` owns BullMQ producer telemetry.

Meta/WhatsApp ingress semantics remain owned by `moda_messaging`.


## MESSAGING-001 architect acceptance

`ARCH-002-MESSAGING-001` is architect-accepted Complete.

Accepted runtime contract:

```text
GET /health
  -> dependency-free process liveness

GET /ready
  -> bounded Redis PING readiness
```

Repository tests use an injected Redis probe. Real Redis integration/outage
testing belongs to `ARCH-002-SYSTEM-TEST-003`.

The task's `GATEWAY-003` dependency edge is satisfied.
