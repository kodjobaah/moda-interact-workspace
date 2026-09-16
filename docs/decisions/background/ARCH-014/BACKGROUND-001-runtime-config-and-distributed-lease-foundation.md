---
id: ARCH-014-BACKGROUND-001
architecture_id: ARCH-014
title: Establish versioned runtime-config observation and distributed leased scheduling
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 63
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-DATABASE-004
enables:
- ARCH-014-BACKGROUND-002
- ARCH-014-BACKGROUND-003
- ARCH-014-BACKGROUND-004
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-BACKGROUND-001

## Objective

Create the common Background runtime-control foundation used by every later runtime-control task.

This task does **not** migrate business-specific constants yet.

## Binding horizontal-scaling invariants

1. PostgreSQL `BackgroundRuntimeConfig(id="default")` is authoritative.
2. Every process observes monotonically increasing config versions.
3. A failed refresh retains last-known-good configuration.
4. Global periodic work uses a distributed database lease.
5. A stale/lost lease owner cannot release or heartbeat a newer owner's lease.
6. Lease and refresh loops never use overlapping `setInterval`.

## Required files

Create:

```text
src/runtime/background-runtime-config.ts
src/runtime/background-runtime-lease.ts
src/runtime/dynamic-leased-scheduler.ts

tests/unit/runtime/background-runtime-config.test.ts
tests/unit/runtime/background-runtime-lease.test.ts
tests/unit/runtime/dynamic-leased-scheduler.test.ts
```

Names are binding.

## BackgroundRuntimeConfigService

Export one production singleton plus injectable class.

Required public contract:

```ts
type BackgroundRuntimeConfigSnapshot = {
  // exact DATABASE-004 fields, including id/version/updatedAt
};

type RuntimeConfigListener = (
  current: BackgroundRuntimeConfigSnapshot,
  previous: BackgroundRuntimeConfigSnapshot | null,
) => void | Promise<void>;

class BackgroundRuntimeConfigService {
  start(): Promise<void>;
  current(): BackgroundRuntimeConfigSnapshot;
  getFresh(): Promise<BackgroundRuntimeConfigSnapshot>;
  subscribe(listener: RuntimeConfigListener): () => void;
  close(): Promise<void>;
}
```

Implementation rules:

- `start()` performs a fresh DB read before returning.
- Missing singleton is fatal during startup. Exact error:
  `Background runtime configuration is missing.`
- Validate every row before storing it. Do not trust generated types alone.
- `current()` before successful `start()` throws.
- Refresh period is internal `5_000ms`.
- Implement refresh with recursive `setTimeout`; a new refresh is scheduled only after the previous refresh settles.
- On refresh success:
  - if `version > current.version`, replace snapshot then notify listeners;
  - if `version <= current.version`, do nothing.
- On refresh failure after startup:
  - keep last-known-good;
  - log structured warning;
  - continue refreshing.
- One listener failure must be logged and must not prevent other listeners receiving the change.
- `close()` cancels the timer and waits for any in-flight refresh.
- Do not read migrated runtime values from environment variables.

## Process owner token

Create one process-lifetime owner token:

```text
<hostname>:<pid>:<random UUID>
```

Do not use hostname/pid alone.

## Distributed lease

Lease constants are **not configurable**:

```text
LEASE_DURATION_MS = 120_000
LEASE_HEARTBEAT_MS = 30_000
```

Required lease API:

```ts
type BackgroundLeaseHandle = {
  name: BackgroundRuntimeLeaseName;
  ownerToken: string;
  generation: number;
};

class BackgroundRuntimeLeaseService {
  tryAcquire(name): Promise<BackgroundLeaseHandle | null>;
  heartbeat(handle): Promise<boolean>;
  release(handle): Promise<boolean>;
  runWithLease<T>(
    name,
    work: (handle: BackgroundLeaseHandle) => Promise<T>,
  ): Promise<
    | { kind: "skipped" }
    | { kind: "completed"; value: T; leaseLost: boolean }
  >;
}
```

### Acquire SQL semantics

Use PostgreSQL server `NOW()`.

Acquire must be one atomic SQL statement using `INSERT ... ON CONFLICT ... DO UPDATE ... WHERE` or equivalent.

A takeover is permitted only when:

```text
leaseUntil <= NOW()
```

Successful acquisition:

- writes the caller `ownerToken`;
- increments `generation` when taking over an existing row;
- sets `acquiredAt`, `heartbeatAt`;
- sets `leaseUntil = NOW() + 120 seconds`;
- returns the exact generation.

Two concurrent callers for the same lease must never both receive a valid handle for the same generation.

### Heartbeat

Update only where:

```text
name = handle.name
ownerToken = handle.ownerToken
generation = handle.generation
leaseUntil > NOW()
```

Set heartbeat + expiry from PostgreSQL `NOW()`.

Return `true` only for exactly one updated row.

### Release

Delete (or expire) only where name + owner + generation all match.

A stale handle MUST return `false` and MUST NOT affect a replacement owner.

### `runWithLease`

- starts heartbeat using non-overlapping recursive timeout;
- executes `work`;
- marks `leaseLost=true` after a failed guarded heartbeat;
- after lease loss, never heartbeat/release that handle again;
- work already in progress is not forcibly aborted;
- release on normal completion only if ownership has not been lost;
- errors from `work` propagate after cleanup.

## Dynamic leased scheduler

Required contract:

```ts
startDynamicLeasedScheduler({
  config,
  lease,
  leaseName,
  intervalMs,
  run,
  onError,
}): Promise<() => Promise<void>>
```

Rules:

- caller must have started config service;
- first cycle timing is chosen by caller through an explicit `runImmediately` option;
- no `setInterval`;
- no overlapping run in one process;
- before each run, acquire the lease;
- after acquisition, call `config.getFresh()` and pass that immutable snapshot to `run`;
- if lease unavailable, skip work without error;
- schedule next wait from the latest in-memory config;
- when a newer config changes the relevant interval while waiting, cancel and reschedule from notification time;
- if config changes while work is running, do not interrupt; use newest interval after completion;
- stop unsubscribes, clears timer and waits for an in-flight local run to settle.

## Tests

Mandatory tests include:

1. initial config load;
2. missing singleton fails startup;
3. refresh accepts version `N+1`;
4. equal/older version is ignored;
5. failed refresh retains last known good;
6. listener isolation;
7. two lease instances race and exactly one acquires;
8. expired lease takeover increments generation;
9. old owner heartbeat fails after takeover;
10. old owner release fails after takeover;
11. heartbeat extends expiry;
12. work error cleans up;
13. scheduler never overlaps local work;
14. two schedulers sharing lease execute only one global run;
15. interval update reschedules a waiting timer;
16. interval update does not interrupt running work;
17. lease winner receives a fresh config read after acquisition;
18. stop is idempotent.

## Validation

```bash
npm run prisma:validate
npm run prisma:generate
npm run test:unit -- --runInBand
npm run build
git diff --check
```

Use the repository's actual Vitest invocation if `--runInBand` is unsupported; do not change test semantics.

## Non-goals

Do not:

- wire billing/recovery/translation entrypoints yet;
- add Redis locks;
- use advisory locks whose session ownership cannot be guaranteed through Prisma pooling;
- add another config table;
- make lease duration/heartbeat Admin-editable;
- change BullMQ concurrency in this task.

## Stop conditions

STOP if DATABASE-004 is absent or if the implementation cannot guarantee owner+generation fencing with PostgreSQL server time.
