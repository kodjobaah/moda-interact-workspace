# ARCH-014 background runtime controls

## Decision

Background operational tuning is durable platform configuration, editable by authorized Admin users without redeploying workers.

The implementation MUST remain safe under horizontal scaling of both Admin and Background services.

## Single source of truth

The single authoritative row is:

```text
public.BackgroundRuntimeConfig
id = "default"
```

No runtime control in this architecture may have a competing environment-variable override, process-local Admin mutation, Redis-only authoritative value, or duplicate table.

Environment variables remain authoritative only for deployment/credentials/provider identity that this architecture explicitly leaves system-managed.

## Update concurrency

`BackgroundRuntimeConfig.version` is a monotonically increasing integer.

Every Admin mutation:

1. renders/receives `expectedVersion`;
2. re-reads the singleton inside the mutation transaction;
3. requires `current.version === expectedVersion`;
4. performs `updateMany({ id: "default", version: expectedVersion })`;
5. increments `version` exactly once;
6. requires affected row count `1`;
7. writes the audit row in the same transaction.

If another Admin replica/user wins first, the losing mutation rolls back and returns a concurrency conflict. There is no automatic field merge.

## Worker observation

Each Background process starts one `BackgroundRuntimeConfigService`.

Initial configuration load is mandatory for readiness. After startup the service refreshes every 5 seconds using non-overlapping recursive `setTimeout`.

Rules:

- accept only a strictly greater version than the current in-memory version;
- equal/older versions are ignored;
- a transient refresh failure retains the last-known-good snapshot;
- a later successful read converges automatically;
- no worker writes configuration.

## Global periodic jobs

These jobs are globally singleton **and globally cadence-limited** across worker replicas:

```text
BILLING_RECONCILIATION
RECOVERY_CAPACITY_REPAIR
TRANSLATION_RECONCILIATION
```

Every replica may own a local scheduler timer, but a local timer is only a wake-up hint. Work executes only after PostgreSQL proves both that the lease is free and that the shared cadence is due.

`BackgroundRuntimeLease` retains one row per lease name and records:

```text
ownerToken
generation
acquiredAt
heartbeatAt
leaseUntil
lastFinishedAt
```

Lease/cadence correctness:

```text
lease TTL:        120 seconds (internal invariant)
heartbeat:         30 seconds (internal invariant)
clock:             PostgreSQL server time
owner:             process-lifetime random owner token
fencing:           monotonically increasing generation across every acquisition
normal release:    guarded UPDATE; row is retained, not deleted
cadence history:   lastFinishedAt = PostgreSQL NOW() when a valid owner finishes/releases
```

For the three periodic lease names, acquisition is eligible only when:

```text
leaseUntil <= PostgreSQL NOW()
AND
(lastFinishedAt IS NULL OR lastFinishedAt + latest configured interval <= PostgreSQL NOW())
```

The cadence interval is read from the authoritative `BackgroundRuntimeConfig(id="default")` row as part of the database acquisition decision. A stale replica cannot authorize an early run using an older process-local interval.

`QUEUE_CONCURRENCY_RECONCILIATION` is convergence/event driven and uses a zero-second cadence gate; it still uses lease ownership/fencing.

The winner fresh-reads `BackgroundRuntimeConfig` after acquisition and uses one immutable snapshot for the business cycle.

A process crash is recoverable after lease expiry. A stale/lost owner cannot heartbeat, release, or stamp `lastFinishedAt` on a newer generation.

These lease constants and cadence-history mechanics are correctness internals and are not Admin controls.

## Dynamic interval changes

Schedulers use recursive `setTimeout`, never `setInterval`. The local timeout controls only when a replica asks PostgreSQL whether work is due; it is never the cross-replica cadence authority.

When the config service observes a newer interval while a scheduler is waiting:

- cancel the old wait;
- schedule using the newly committed interval;
- do not interrupt work already running.

When work is running, the new value applies when that run completes.

## BullMQ concurrency and horizontal scaling

Admin-visible queue concurrency means **fleet-wide maximum active jobs for that queue across all replicas**.

The database stores the desired values. A lease-protected queue-concurrency reconciler:

1. acquires `QUEUE_CONCURRENCY_RECONCILIATION`;
2. re-reads fresh DB config after lease acquisition;
3. calls BullMQ `Queue.setGlobalConcurrency(...)` for every controlled queue in deterministic order;
4. verifies with `getGlobalConcurrency()`;
5. retries on the next reconciliation if any Redis operation fails.

Every local Worker also sets its mutable `worker.concurrency` to the desired fleet value so an individual replica cannot become an accidental lower bottleneck. Redis global concurrency remains the aggregate authority.

A stale replica may update its local concurrency only from monotonically newer config and MUST NOT write a stale global value because shared Redis writes occur only after lease acquisition + fresh DB read.

## Editable classifications

### Operational

- billing reconciliation interval
- billing shops per cycle
- Shopify usage-event publish batch
- recovery repair interval
- recovery shops per repair
- recoveries per resume job
- translation reconciliation interval
- translations per provider batch
- conversation quiet window
- conversation maximum settle window

### Advanced

- frozen-subscription recheck interval
- billing provider retry interval
- usage-event retry base/max
- translation reconciliation page size
- translation claim timeout
- translation submit retry
- translation initial poll
- translation provider poll
- translation result retry
- translation submit attempts
- translation automatic retries
- fleet-wide queue concurrency for each BullMQ queue

### Abuse protection

Only rate **limits** are editable. Window lengths stay fixed at 1 minute / 10 minutes.

### System-managed / intentionally not editable

- readiness probe timeout
- WhatsApp HTTP timeout
- abandoned-checkout lookup safety window and maximum candidate count
- database/Redis lock TTLs and low-level lock retry timings
- queue telemetry retention/sample mechanics
- translation output/file safety bounds
- provider credentials, provider identity and translation model
- billing lifecycle retry tier structure
- usage-event stale-claim recovery timeout
- recovery queue retry/backoff policy
- per-merchant `ShopSettings.recoveryDelayMinutes`

These remain code/deployment/merchant-level policy and are not columns in `BackgroundRuntimeConfig`.
