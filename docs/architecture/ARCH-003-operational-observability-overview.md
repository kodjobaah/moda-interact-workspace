# ARCH-003: Operational observability and tenant-aware pending recovery

## Purpose

ARCH-003 turns Moda Interact's asynchronous queue activity into a safe,
tenant-aware operational product surface.

The architecture began with the platform-admin queue observability experience
and expanded to cover the data needed to make queue activity and pending
recoveries understandable at both platform and merchant level.

## Main outcomes

ARCH-003 covers five related capabilities:

1. **Admin queue observability**
   - compact queue-health summaries;
   - a dedicated `Observability > Shopify Queues` operational surface;
   - bounded failed-job browsing;
   - protected failed-job detail;
   - read-only diagnostics only.

2. **Tenant attribution**
   - pending recovery jobs preserve internal `shopId` and normalized shop
     identity;
   - operational readers can attribute a relevant job to the correct tenant
     without global guessing;
   - unresolved/legacy job attribution is represented explicitly rather than
     inferred unsafely.

3. **Shop-scoped pending-recovery index**
   - Background maintains:
     ```text
     pending-recovery:index:shop:<shopId>
     ```
   - the index contains active pending candidate job IDs only;
   - score represents the candidate due time;
   - merchant and operational readers do not need a Redis keyspace or BullMQ
     global scan.

4. **Merchant pending-recovery visibility**
   - the Shopify Usage overview exposes a read-only `Pending recoveries` panel;
   - the panel is tenant-scoped;
   - pagination is bounded;
   - manual refresh updates only pending-recovery data;
   - missing/completed/failed jobs are omitted safely;
   - browser DTOs do not expose checkout/cart tokens, Redis keys, raw BullMQ
     data or stack traces.

5. **Queue performance telemetry**
   - the Background runtime emits queue depth, oldest-waiting age, queue wait,
     processing duration, throughput, failure/retry/stall signals;
   - waiting eligibility is transition-derived;
   - intentional delayed recovery scheduling is not misreported as worker
     backlog;
   - optional telemetry setup/runtime failures do not affect business-worker
     readiness;
   - stale queue snapshots are suppressed after failed sampling.

## Queue scope

The ARCH-003 operational baseline observes:

```text
checkout-events
order-events
pending-recovery-candidates
whatsapp-events
```

Later architectures may add queues by extending the accepted telemetry
contract rather than redesigning it.

## Core invariants

```text
tenant attribution is explicit
global Redis/keyspace scans are not required
read-only observability cannot mutate jobs
merchant UI receives only safe DTO fields
intentional delay != worker backlog
telemetry failure != worker failure
```

## Merchant pending-recovery flow

```text
checkout webhook
      |
      v
pending-recovery candidate
      |
      v
shop-scoped Redis ZSET
      |
      v
authenticated Shopify loader
      |
      v
Pending recoveries panel
```

The authenticated shop determines the only index that can be read.

## Admin operational flow

```text
platform admin
      |
      v
Observability > Shopify Queues
      |
      +--> queue summaries
      +--> bounded job lists
      +--> selected safe job detail
      +--> Grafana / operational telemetry
```

The Admin experience remains read-only.

## Relationship to ARCH-004

ARCH-003 establishes how pending candidates are listed, observed and measured.

ARCH-004 changes **when the same candidate is due** by introducing a
last-activity inactivity clock and cart/checkout rescheduling.

The ARCH-003 shop ZSET therefore remains operationally important under
ARCH-004: its score must continue to match the candidate's authoritative
`scheduledFor`.

## Task ownership

Implementation work is distributed under:

```text
docs/decisions/admin/ARCH-003/
docs/decisions/background/ARCH-003/
docs/decisions/shopify/ARCH-003/
docs/decisions/system-test/ARCH-003/
```

The task files remain authoritative for current execution/review state.
