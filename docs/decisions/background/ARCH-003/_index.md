# ARCH-003 — Background Decisions

## Tasks

| Task | Title | Status | Depends On |
|---|---|---|---|
| ARCH-003-BACKGROUND-001 | Preserve tenant metadata on pending-recovery candidate jobs | Complete | ARCH-003-ADMIN-013 |
| ARCH-003-BACKGROUND-002 | Maintain shop-scoped active pending-recovery listing index | Complete | ARCH-003-BACKGROUND-001 |
| ARCH-003-BACKGROUND-003 | Emit complete BullMQ queue performance telemetry | Complete | ARCH-003-BACKGROUND-002 |

## Current executable work

No ARCH-003 Background implementation task is currently executable.

`ARCH-003-BACKGROUND-003` has been architect-accepted Complete.

The Background runtime now exposes the queue-performance metric contract needed
for operational Grafana monitoring across:

```text
checkout-events
order-events
pending-recovery-candidates
whatsapp-events
```

## Architect Amendment 001

`ARCH-003-BACKGROUND-003` returned to Ready.

Required corrections:

```text
1. eligibility-aware queue wait/oldest-waiting semantics must remain correct
   across changeDelay() and delayed retry/backoff;

2. telemetry-owned Queue / QueueEvents setup and error events must never affect
   business worker readiness or processing.
```


## Architect Amendment 002

Attempt 2 accepted the transition-derived eligibility correction.

`ARCH-003-BACKGROUND-003` remains Ready for one narrower correction:

```text
telemetry setup/runtime error isolation
stale-snapshot suppression after sampling failure
failure-mode regression tests
operator documentation correction
```

No eligibility redesign is requested in Amendment 002.


## Architect acceptance — BACKGROUND-003

Attempt 3 accepted.

```text
ARCH-003-BACKGROUND-003   Complete
```

Operational documentation:

```text
moda-interact-background/docs/observability/queue-performance.md
```

The repository README now links to that guide.
