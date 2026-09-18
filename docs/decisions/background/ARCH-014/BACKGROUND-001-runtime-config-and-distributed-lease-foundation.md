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
status: complete
priority: 63
attempt: 3
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

## Completion Report

Status: Ready for Review

Implementation commit: `bd27cd0` on `task/ARCH-014-BACKGROUND-001`, pushed to `origin`.

Attempt 3 correction:

- Updated `startDynamicLeasedScheduler()` to execute every cycle through `BackgroundRuntimeLeaseService.runWithLease()`. The common lifecycle now owns guarded heartbeat, lease-loss fencing, and release; the scheduler no longer leaves successful leases valid until expiry or allows long work to outlive the heartbeat path.
- Preserved post-acquisition `config.getFresh()` ordering, immutable snapshot delivery, skipped-cycle behavior, non-overlap, interval-change rescheduling, in-flight update behavior, and idempotent stop.
- Added focused scheduler regression evidence for lifecycle ordering and completion release delegation. Existing lease tests cover the recursive heartbeat path, failed-heartbeat lease loss, cleanup, and fencing; the long-running scheduler case now runs inside the delegated lifecycle rather than raw acquisition.

Requirement mapping:

- Runtime-config startup, validation, monotonic refresh, last-known-good retention, listener isolation, recursive refresh timing, close behavior, immutable dates, and process owner token remain implemented in `src/runtime/background-runtime-config.ts` and its focused tests.
- PostgreSQL `NOW()` atomic acquisition, fixed lease constants, generation takeover, owner/generation heartbeat and release fencing, recursive heartbeat cleanup, and work-error propagation remain implemented in `src/runtime/background-runtime-lease.ts` and its focused tests.
- Dynamic scheduler lease lifecycle correction is implemented in `src/runtime/dynamic-leased-scheduler.ts`; focused tests verify acquisition-to-fresh-read-to-run-to-release ordering, unavailable-lease skipping, shared-lease exclusion, local non-overlap, interval rescheduling, in-flight updates, startup enforcement, and idempotent stop.
- No business wiring, queues, Redis/advisory locks, configurable lease constants, schema changes, or environment-based migrated runtime values were added.

Validation:

- Focused runtime tests: `npm run test -- --run tests/unit/runtime/background-runtime-config.test.ts tests/unit/runtime/background-runtime-lease.test.ts tests/unit/runtime/dynamic-leased-scheduler.test.ts`: passed, 3 files and 14 tests.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed with Prisma Client 6.19.3.
- `npm run test:unit -- --runInBand`: rejected because Vitest 4.1.11 does not support `--runInBand`.
- Repository-supported `npm run test:unit`: 60 files passed, 1 file failed; 944 tests passed and 2 unrelated baseline failures remained in `tests/unit/runtime/observability-startup.test.ts`.
- `npm run build`: passed.
- `git diff --check`: passed.

Evidence limitations and baseline:

- Lease unit tests use controlled database mocks. They verify SQL shape, PostgreSQL `NOW()` predicates, fencing decisions, takeover generations, and caller behavior, but do not claim to prove physical concurrent PostgreSQL execution. No task-scoped integration harness was available; no real PostgreSQL concurrency result is asserted.
- The two unrelated baseline failures are the observability startup test's outdated shared runtime expectation (`0.9.0` versus repository `0.11.2`) and outdated recovery-entrypoint source-shape expectation. No task-owned files are involved.

Worktree evidence:

- Implementation worktree is clean after commit and push. Parent changes are limited to this task file.
- Database submodule remains at `89dca92325cefc96fe2dff5021d1e5ee0e8f7fe1`.

Unresolved issues: none within task scope. Task is ready for architect review.

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

## Architect Review

### Review Status

Changes Requested

### Functional finding

The common runtime-config and fenced lease services are functionally sound after Attempt 2, including immutable published dates and reporting heartbeat loss discovered during cleanup. The dynamic leased scheduler still bypasses the lease lifecycle required for horizontally scaled periodic work.

`startDynamicLeasedScheduler()` currently calls `lease.tryAcquire(...)` directly and, after a successful acquisition, calls `config.getFresh()` and `run(...)`. It never heartbeats or releases the acquired handle. This creates two production failures:

1. a short successful cycle leaves the lease valid until its 120-second expiry, so later cycles can be skipped even when the configured interval is much shorter;
2. a run lasting beyond the 120-second lease duration receives no heartbeat, allowing another replica to take over while the original work is still running, violating the one-global-run invariant.

This is a runtime correctness defect, not a request for exhaustive test expansion.

### Required Attempt 3 correction

Keep the correction strictly inside the common scheduler/lease foundation.

1. In `src/runtime/dynamic-leased-scheduler.ts`, execute each global cycle through `BackgroundRuntimeLeaseService.runWithLease(...)` (or an exactly equivalent lifecycle that uses the existing guarded heartbeat and release semantics). The preferred deterministic shape is:
   - call `lease.runWithLease(leaseName, async (handle) => { ... })`;
   - inside the leased callback, call `config.getFresh()` **after acquisition**;
   - pass that immutable fresh snapshot and the exact lease handle to `run(snapshot, handle)`;
   - if `runWithLease` returns `{ kind: "skipped" }`, perform no work and treat it as a normal skipped cycle.
2. Do not add a second heartbeat/release implementation to the scheduler. Reuse the already-reviewed `runWithLease` fencing, recursive heartbeat, cleanup and release behavior.
3. Preserve all existing scheduler behavior:
   - no `setInterval`;
   - no local overlap;
   - `runImmediately` semantics unchanged;
   - config changes reschedule a waiting timer;
   - config changes do not interrupt running work;
   - next delay comes from latest in-memory config;
   - stop remains idempotent and waits for local in-flight work.
4. Add focused regression evidence that proves the scheduler uses the full lease lifecycle rather than raw acquisition. At minimum prove:
   - a completed scheduled cycle releases through the lease lifecycle so a subsequent interval is not artificially blocked for 120 seconds;
   - a long scheduled run is protected by the lease heartbeat path;
   - unavailable lease still skips without calling `run`;
   - fresh config is still read only after the lease has been acquired.
5. Do not modify DATABASE-004, business-specific billing/recovery/translation/messaging entrypoints, BullMQ concurrency, lease constants, runtime-config fields or environment-variable policy in this attempt.

### Acceptance boundary

Attempt 3 is acceptable when the dynamic scheduler cannot hold an idle lease until expiry after normal completion and cannot silently outlive the 120-second lease without the common heartbeat lifecycle. Existing unrelated baseline test failures do not block acceptance.
## Architect Review — Attempt 3

### Review Status

Accepted

### Acceptance finding

Attempt 3 closes the only remaining scheduler-lifecycle defect from the prior review. `startDynamicLeasedScheduler()` now executes each cycle through `BackgroundRuntimeLeaseService.runWithLease(...)`; the leased callback performs `config.getFresh()` only after successful acquisition and passes the exact lease handle plus immutable fresh snapshot to the scheduled work.

This reuses the already-reviewed recursive heartbeat, owner+generation fencing, lease-loss handling, normal release and cleanup behavior. Short scheduled runs therefore release promptly instead of waiting for the 120-second lease expiry, while long-running scheduled work remains protected by the heartbeat lifecycle.

The existing scheduler behavior is preserved: no local overlap, no `setInterval`, `runImmediately` behavior, unavailable-lease skipping, interval-change rescheduling, no interruption of in-flight work, latest-config scheduling after completion and idempotent stop.

Implementation commit `bd27cd0` is accepted. No Attempt 4 is required.
