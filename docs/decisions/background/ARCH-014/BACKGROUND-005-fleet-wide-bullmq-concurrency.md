---
id: ARCH-014-BACKGROUND-005
architecture_id: ARCH-014
title: Enforce fleet-wide BullMQ concurrency from runtime configuration
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 66
executor: copilot
claimed_at: 2026-09-16T09:17:54Z
attempt: 1
depends_on:
- ARCH-014-BACKGROUND-002
- ARCH-014-BACKGROUND-003
- ARCH-014-BACKGROUND-004
enables:
- ARCH-014-SYSTEM-TEST-003
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-BACKGROUND-005

## Objective

Make worker throughput predictable under horizontal scaling.

Admin concurrency values represent a **fleet-wide queue cap across all replicas**, not a per-process multiplier.

## Controlled queues and exact config mapping

```text
checkout-events
  <- checkoutQueueGlobalConcurrency

order-events
  <- orderQueueGlobalConcurrency

pending-recovery-candidates
  <- pendingRecoveryQueueGlobalConcurrency

recovery-capacity-resume
  <- recoveryResumeQueueGlobalConcurrency

whatsapp-events
  <- whatsappQueueGlobalConcurrency

merchant-communications
  <- merchantCommunicationsQueueGlobalConcurrency

billing-subscription-reconcile
  <- billingSubscriptionQueueGlobalConcurrency
```

Use canonical queue-name constants where already available; do not duplicate string literals unnecessarily.

## BullMQ mechanism

The repository uses BullMQ 6.x.

Use the open-source BullMQ APIs:

```ts
await queue.setGlobalConcurrency(value);
await queue.getGlobalConcurrency();

worker.concurrency = value;
```

Do not implement a custom Redis semaphore.

Do not use per-replica Admin semantics.

## Shared global-concurrency reconciler

Create:

```text
src/runtime/queue-concurrency-controller.ts
tests/unit/runtime/queue-concurrency-controller.test.ts
```

Required behaviour:

1. every worker entrypoint may start the controller;
2. shared writes are protected by lease `QUEUE_CONCURRENCY_RECONCILIATION`;
3. after acquiring the lease, call `backgroundRuntimeConfigService.getFresh()`;
4. apply all seven queue limits in the exact mapping order above;
5. verify each value using `getGlobalConcurrency()`;
6. if one operation fails, log the queue and fail that reconciliation run; a future run retries;
7. trigger reconciliation:
   - once at startup;
   - whenever a newer config version is observed;
   - every 30 seconds as an internal healing check;
8. the 30-second healing period is system-managed and not an Admin control;
9. use recursive non-overlapping scheduling.

Because the lease winner re-reads the DB after acquisition, a stale replica cannot restore an older global value.

## Local Worker concurrency

Update all seven Worker constructions.

Initial local concurrency must use `backgroundRuntimeConfigService.current()` after entrypoint initialization.

Register a versioned config listener for each Worker:

```text
worker.concurrency = new desired queue concurrency
```

only for a strictly newer config version.

Setting local concurrency to the same desired fleet value ensures one replica is not a lower bottleneck. BullMQ global concurrency in Redis remains the authoritative aggregate cap.

No Worker needs to be recreated for a concurrency update.

## Startup ordering

Each affected entrypoint must:

1. start runtime config;
2. construct Workers using current config;
3. start/reuse queue-concurrency controller;
4. expose workers to readiness lifecycle.

Do not construct a controlled Worker before config initialization.

## Horizontal-scaling examples that MUST hold

With:

```text
whatsappQueueGlobalConcurrency = 20
```

one replica, three replicas or ten replicas must never intentionally process more than 20 `whatsapp-events` jobs concurrently across the fleet.

After Admin changes:

```text
20 -> 5
```

running jobs are allowed to finish; new acquisitions converge to the global cap 5 without a worker redeploy.

After:

```text
5 -> 30
```

all workers may increase local concurrency, but Redis still caps aggregate work to 30.

## Mandatory tests

1. controller maps every field to correct queue;
2. controller uses fresh DB config after lease acquisition;
3. stale cached version cannot write global concurrency;
4. lease contention permits one controller writer;
5. startup config is applied to local Worker concurrency;
6. newer version changes `worker.concurrency`;
7. older/equal version cannot change it;
8. mocked Redis global cap is verified after set;
9. failure causes future healing retry;
10. all prior literal Worker concurrency values are removed as runtime authority;
11. multi-worker integration test proves global cap across at least two workers for one queue;
12. runtime cap decrease does not cancel already active jobs.

## Validation

```bash
npm run test:unit
npm run test:integration --if-present
npm run build
git diff --check
```

## Stop conditions

STOP if installed BullMQ types do not expose `worker.concurrency`, `Queue.setGlobalConcurrency` or `Queue.getGlobalConcurrency`. Do not replace them with a home-grown Redis lock; return to architect review with exact installed API evidence.
