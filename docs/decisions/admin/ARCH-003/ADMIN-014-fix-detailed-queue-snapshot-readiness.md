---
id: ARCH-003-ADMIN-014
architecture_id: ARCH-003
title: Fix detailed queue snapshot cold-connection readiness
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 41
executor: copilot
claimed_at: 2026-09-04T21:25:52Z
attempt: 2
depends_on:
  - ARCH-003-ADMIN-010
enables:
  - ARCH-003-ADMIN-011
created: 2026-09-04
updated: 2026-09-04
---

# Fix detailed queue snapshot cold-connection readiness

## Objective

Make the detailed `/api/admin/queues` snapshot path reliably establish bounded
BullMQ and raw Redis readiness before issuing its first queue/activity commands,
without weakening the Admin fail-fast connection policy.

This task exists so the Shopify Queues table can render reliably and the
ADMIN-011 right-hand drawer can be exercised with real queue rows.

## Context

The Tenant Directory overview path was previously corrected in ADMIN-008 to
wait for BullMQ Queue readiness before calling `getJobCounts('active')`.

The detailed reader still follows a different cold-start sequence:

```text
getQueueReaders()
  -> lazy BullMQ Queue readers
  -> lazy raw ioredis reader
  -> readQueueMonitorSnapshot()
       -> getJobCounts(...)
       -> getWorkersCount()
       -> XREVRANGE events
```

The detailed path does not explicitly establish readiness first. With:

```text
enableOfflineQueue: false
maxRetriesPerRequest: 1
lazyConnect: true
```

the first command can fail before the underlying stream is writable. The page
then receives the generic 503 and renders `No queue snapshot is available`.

The user-provided runtime screenshot demonstrates exactly that unavailable UI
state. The screenshot alone does not prove whether local Redis configuration is
also missing/unreachable, so this task must preserve truthful configuration
errors rather than substituting fake data.

## Scope

- inspect only the detailed queue snapshot path used by
  `GET /api/admin/queues`;
- ensure each cold BullMQ Queue reader reaches readiness before queue commands;
- ensure the raw Redis reader used for event-stream `XREVRANGE` is also ready
  before its first command;
- bound all readiness work with the existing queue-operation timeout contract;
- preserve cached/warm reader reuse;
- preserve generic unavailable behavior for genuinely missing/unreachable Redis;
- add focused regression coverage for cold Queue and cold raw-Redis readers;
- keep all UI code unchanged.

## Requirements

1. Preserve the accepted fail-fast policy:

   ```text
   enableOfflineQueue: false
   maxRetriesPerRequest: 1
   connectTimeout: 2500ms
   commandTimeout: 2500ms
   ```

2. Do not switch Admin readers to worker-style indefinite retry behavior.

3. Do not enable offline command buffering as the fix.

4. Before `getJobCounts`, `getWorkersCount`, or event-stream `XREVRANGE` can
   run on newly created readers, establish readiness through the library's
   supported connection mechanism.

5. The readiness mechanism must be safe for warm/cached readers; it must not
   throw merely because a reader is already connected.

6. Readiness must remain bounded by the existing operation timeout.

7. A missing or unreachable `REDIS_URL` must still result in the existing
   generic unavailable contract. Do not manufacture an empty/zero snapshot.

8. Do not change queue definitions, counts, failed-job APIs, selected-job APIs,
   or drawer UI.

9. Add a focused regression that fails if detailed queue commands execute
   before BullMQ readiness.

10. Add a focused regression that fails if raw Redis event activity is read
    before the raw Redis reader is ready.

## Attempt 2 Architect Correction — LIVE REDIS PROOF REQUIRED

Attempt 1 is **not accepted**.

The source-level readiness change and mocked regression test are insufficient
because the actual Admin screen still renders:

```text
Queue data is unavailable.
No queue snapshot is available.
```

The developer has independently proven, from the same development machine and
with the actual `REDIS_URL`, that Redis and BullMQ are reachable:

```text
redis-cli -u "$REDIS_URL" ping
PONG
```

and a direct BullMQ probe using `await queue.waitUntilReady()` returned:

```text
checkout-events:
  waiting: 0
  active: 0
  delayed: 0
  failed: 12
```

Therefore Attempt 2 must diagnose and fix the **real production reader path**.
Passing mocked tests alone is explicitly NOT sufficient.

### Mandatory live diagnostic before editing

Using the current shell's `REDIS_URL`, run a temporary diagnostic against the
same four queue names and the same operations used by
`readQueueMonitorSnapshot()`.

The diagnostic must test and record PASS/FAIL independently for:

```text
checkout-events
order-events
pending-recovery-candidates
whatsapp-events
```

For each queue:

```text
1. Queue.waitUntilReady()
2. Queue.getJobCounts('waiting', 'active', 'delayed', 'failed')
3. Queue.getWorkersCount()
4. Queue.toKey('events')
5. raw Redis XREVRANGE <events-key> + - COUNT 1
```

Also test the raw ioredis connection readiness independently.

The diagnostic output may include:

- queue name;
- operation name;
- success/failure;
- safe count values;
- error class/name;
- a redacted/safe error message.

It MUST NOT print:

- `REDIS_URL`;
- Redis username/password;
- environment variable contents;
- tokens or provider credentials;
- job payloads.

Any temporary diagnostic file must be removed before returning the task to
review.

### Mandatory diagnosis

Do not guess at another connection fix.

Identify the exact real operation that causes the detailed snapshot to fail.

Examples of acceptable findings include:

```text
Queue.waitUntilReady          PASS
getJobCounts                  PASS
getWorkersCount               FAIL
XREVRANGE                     PASS
```

or:

```text
all queue operations          PASS
raw Redis readiness           FAIL
```

or:

```text
all individual operations     PASS
combined production reader    FAIL
```

The Completion Report must state the exact failing operation and the actual
bounded cause.

### Core versus optional telemetry

The Shopify Queues page must distinguish **core queue state** from optional
diagnostic metadata.

Core fields:

```text
waiting
active
delayed
failed
```

If `getJobCounts()` cannot be read for a queue, do NOT fabricate zero counts.
That is a genuine queue-read failure.

Optional fields:

```text
workers
last Redis activity
```

If the live probe proves that a managed-Redis restriction or isolated command
failure affects only `getWorkersCount()` or event-stream `XREVRANGE`, that
optional metric MUST NOT blank the entire four-queue page.

In that confirmed case only, Attempt 2 is authorised to degrade the affected
optional field truthfully, for example:

```text
workers: null          -> UI: Unavailable
lastActivity: null     -> UI: None observed / Unavailable as semantically correct
```

Do not convert an unavailable optional metric to numeric zero.

A tiny UI/type adjustment is authorised only if required to represent that
truthful unavailable metric.

### Production-reader integration proof

After the correction, the agent MUST prove the actual production reader works
against the live Redis service.

The proof must invoke the real `readQueueMonitorSnapshot()` implementation, or
an equivalently direct integration harness that uses the real production reader
factories rather than mocked `queueFactory` / `redisFactory`.

Required proof:

```text
snapshot.queues.length === 4
```

and the output must include a real `checkout-events` row.

At the time of the developer's independent probe,
`checkout-events.failed === 12`. The live value may legitimately change while
testing, so record the observed value rather than hard-coding 12 as a fixture.

### API proof

The task MUST also prove that the real local Admin endpoint no longer returns
the unavailable response.

With the development authentication/bypass mode already used by the Admin app,
verify:

```text
GET /api/admin/queues
```

returns:

```text
HTTP 200
```

with a four-queue snapshot.

If the route cannot be exercised because authentication is intentionally not
available in the diagnostic shell, record that exact limitation and provide the
successful real production-reader probe instead. Do not substitute a mocked
route test.

### Cache recovery

Inspect the detailed reader cache behavior as part of the diagnosis.

A transient failed/cold reader must not permanently poison:

```text
cachedQueues
cachedRedis
```

such that every later refresh continues returning 503 after Redis is healthy.

If live diagnosis demonstrates a poisoned cached reader, clear/dispose the
failed cached reader set on the unavailable path and recreate it on the next
request. Do not introduce an unbounded reconnect loop.

### Definition of done

ADMIN-014 may return to `review` only when ALL of the following are true:

1. mocked regression tests pass;
2. the live diagnostic identifies the actual failing operation;
3. the real production queue reader succeeds against the developer's
   `REDIS_URL`;
4. the snapshot contains all four queue definitions;
5. `checkout-events` returns real counts;
6. the Admin API returns HTTP 200 when locally exercisable;
7. no fake/sample queue data is introduced;
8. fail-fast settings remain bounded;
9. full Admin validation passes.

If the live production reader still fails, set the task to `blocked` with the
safe diagnostic evidence. Do NOT return it to `review`.

## Work Items

- [x] Reproduce the detailed cold-reader ordering problem in focused tests.
- [x] Extend the minimal raw Redis reader abstraction only as needed for safe,
      bounded readiness.
- [x] Establish BullMQ readiness before detailed queue commands.
- [x] Establish raw Redis readiness before event-stream reads.
- [x] Preserve all existing fail-fast settings and generic errors.
- [x] Run focused queue-monitor tests.
- [x] Run the full Admin test suite.
- [x] Run typecheck, lint, production build, and `git diff --check`.
- [x] Return this task to `review` and STOP.

- [x] Attempt 2: run the mandatory live per-operation Redis/BullMQ diagnostic.
- [x] Attempt 2: identify the exact operation causing the production snapshot failure.
- [x] Attempt 2: correct the real cause without weakening fail-fast policy.
- [x] Attempt 2: run a live integration probe through the real production reader.
- [x] Attempt 2: prove all four queue rows are returned from live Redis.
- [x] Attempt 2: verify `GET /api/admin/queues` returns HTTP 200 when locally exercisable.
- [x] Attempt 2: verify transient reader failure does not poison cached readers.
- [x] Attempt 2: delete temporary diagnostic code/files.
- [x] Attempt 2: rerun the complete Admin validation contract.

## Out of Scope

- UI/drawer changes;
- mock/sample queue data;
- retry/requeue/delete/pause/resume functionality;
- changing Redis environment configuration;
- background-worker Redis semantics;
- database or cross-service changes.

## Acceptance Criteria

- [x] Cold detailed BullMQ readers are ready before queue commands run.
- [x] Cold raw Redis reader is ready before `XREVRANGE` runs.
- [x] Warm/cached readers continue to work.
- [x] Admin fail-fast Redis settings are unchanged.
- [x] Genuine Redis configuration/connectivity failure remains a generic 503.
- [x] No fake empty queue snapshot is returned.
- [x] Focused regression tests pass.
- [x] Full Admin validation passes.

## Attempt 2 Acceptance Criteria

- [x] Real Redis `PING`/connectivity is treated as already proven; do not spend
      the task changing credentials without contrary evidence.
- [x] Exact failing production operation is identified and recorded.
- [x] Real non-mocked `readQueueMonitorSnapshot()` succeeds against live Redis.
- [x] Exactly four real queue rows are returned.
- [x] `checkout-events` returns real waiting/active/delayed/failed counts.
- [x] Optional worker/activity failures, if confirmed, degrade only that field
      rather than blanking the whole page.
- [x] A core count failure still fails truthfully; no zero fabrication.
- [x] `GET /api/admin/queues` returns HTTP 200 when locally exercisable.
- [x] Cached reader failure cannot permanently poison later healthy refreshes.
- [x] No secrets, payloads, or Redis URL are emitted in diagnostic output.
- [x] Full tests/typecheck/lint/build/`git diff --check` pass.
- [x] If live proof still fails, task is `blocked`, not `review`.

## Completion Report

### Status
Ready for Review.

### Files Changed

- `src/lib/admin/queue-monitor.ts`
- `tests/security/admin-queue-monitor.test.mjs`

### Work Completed

- Added bounded readiness to the raw ioredis reader abstraction, safely
   handling already-ready, lazy, ended, and in-progress connections.
- Established all detailed BullMQ queue readers and the raw Redis reader before
   the first detailed queue counts, worker counts, or event-stream commands.
- Preserved the existing fail-fast settings: offline queue disabled, one retry,
   2500ms connect timeout, and 2500ms command timeout.
- Added a regression test proving cold BullMQ and raw Redis readiness precede
   detailed queue commands and `XREVRANGE`.
- Updated the existing detailed snapshot fixture to implement the readiness
   contract.
- Removed `skipWaitingForReady: true` after live diagnosis showed it bypassed
   BullMQ's supported startup handshake and caused `Stream isn't writeable and
   enableOfflineQueue options is false` on every detailed queue reader.
- Reset detailed queue reader caches after an unavailable snapshot so a later
   healthy refresh recreates failed readers.
- Added a cache-recovery regression covering a failed refresh followed by a
   healthy four-queue refresh.

### Attempt 2 Live Evidence

- Raw Redis readiness: PASS; event-stream `XREVRANGE`: PASS for all four queues.
- BullMQ `Queue.waitUntilReady`, `getJobCounts`, and `getWorkersCount`: FAIL
   for all four queues with `Stream isn't writeable and enableOfflineQueue
   options is false` while `skipWaitingForReady: true` was configured.
- The live control probe with the same fail-fast settings and the default
   BullMQ startup wait passed for all four queues; `checkout-events` reported
   `waiting=0`, `active=0`, `delayed=0`, `failed=12`, `workers=1`.
- The real `readQueueMonitorSnapshot()` returned four rows, including the
   real `checkout-events` count.
- The local `GET /api/admin/queues` returned HTTP 200 with four rows and
   `checkout-events.failed=12`.

### Validation Results

- `node --test tests/security/admin-queue-monitor.test.mjs`: 13 passed.
- `npm test`: 59 passed.
- `npm exec tsc -- --noEmit`: passed.
- `npm run lint`: passed with two existing
   `react-hooks/exhaustive-deps` warnings in
   `src/components/admin/queue-monitor.tsx`.
- `npm run build`: passed with the existing multiple-lockfile workspace-root
   warning and optional BullMQ `@valkey/valkey-glide` warning.
- `git diff --check`: passed.

### Deviations

The live diagnostic emitted only queue names, operation outcomes, safe counts,
and sanitized error text. No temporary diagnostic file was added.

### Assumptions

- ioredis connection lifecycle events are the supported readiness mechanism for
   an in-progress lazy connection; the existing operation timeout bounds the
   complete readiness batch.

### Unresolved Issues

Lint retains two pre-existing `react-hooks/exhaustive-deps` warnings in
`src/components/admin/queue-monitor.tsx`. The live Redis service reports its
existing `volatile-lru` eviction-policy warning; this task does not change
Redis configuration.

### Architectural Concerns

None. Queue definitions, APIs, failed-job readers, drawer UI, and queue
semantics were not changed. The detailed reader now uses BullMQ's supported
readiness path while retaining bounded fail-fast settings.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is architect-accepted Complete.

The live runtime prerequisite is now proven rather than inferred from mocked
tests.

Accepted live evidence:

```text
raw Redis readiness / XREVRANGE    PASS
BullMQ live diagnosis              identified skipWaitingForReady defect
real readQueueMonitorSnapshot()    4 queues
checkout-events.failed             12 at test time
GET /api/admin/queues              HTTP 200, 4 queues
```

The correction removes `skipWaitingForReady: true`, allowing BullMQ's supported
startup handshake while retaining the accepted bounded Admin fail-fast policy.

The detailed reader also clears failed cached readers after an unavailable
snapshot so a transient cold failure cannot permanently poison subsequent
refreshes.

The developer-provided runtime screenshot after Attempt 2 confirms that the real
four-queue table now renders and that failed-job data can be opened.

### Reviewed Files / Evidence

- `moda-interact-admin/src/lib/admin/queue-monitor.ts`
- `moda-interact-admin/tests/security/admin-queue-monitor.test.mjs`
- ADMIN-014 Completion Report and live diagnostic evidence
- live runtime screenshot showing four queue rows and checkout-events failures

### Validation Reviewed

- live reader: four queues returned;
- live API: HTTP 200 with four queues;
- full Admin tests: 59 passed;
- TypeScript: pass;
- lint: pass with two existing warnings;
- production build: pass;
- `git diff --check`: pass.

### Architecture Conformance

Accepted.

The correction remains read-only, bounded, and confined to the existing Admin
Redis/BullMQ connection lifecycle.

### Follow-up

ADMIN-014 no longer blocks visual review.

`ARCH-003-ADMIN-011` is returned for a separate Attempt 2 visual correction:
the current drawer is an in-flow flex sibling and visibly compresses the queue
table. It must become a true overlay.
