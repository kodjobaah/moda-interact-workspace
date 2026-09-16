---
id: ARCH-014-BACKGROUND-006
architecture_id: ARCH-014
title: Correct distributed runtime scheduling and configuration authority under horizontal scaling
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 68
executor:
claimed_at:
attempt: 1
depends_on:
- ARCH-014-DATABASE-005
- ARCH-014-BACKGROUND-001
- ARCH-014-BACKGROUND-002
- ARCH-014-BACKGROUND-003
- ARCH-014-BACKGROUND-004
- ARCH-014-BACKGROUND-005
enables:
- ARCH-014-SYSTEM-TEST-003
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-BACKGROUND-006

## Objective

Close the remaining Background runtime-control gaps as **one coherent horizontal-scaling correction**.

This task combines the former BACKGROUND-006 and BACKGROUND-007 scopes. After it is accepted:

1. PostgreSQL is authoritative for both distributed lease ownership and whether a global periodic cycle is due;
2. normal release preserves monotonic fencing generations across release/reacquire cycles;
3. `BackgroundRuntimeConfigService` validates the exact persisted DATABASE-004 contract before replacing last-known-good state;
4. production services never silently fall back to process-local test defaults when runtime configuration has not started;
5. the periodic billing scanner uses the committed runtime snapshot for the remaining configurable retry timings.

Do not split these corrections into another Background task. Implement and validate them together.

## Binding horizontal-scaling invariants

For these global periodic leases:

```text
BILLING_RECONCILIATION
RECOVERY_CAPACITY_REPAIR
TRANSLATION_RECONCILIATION
```

all replicas share one cadence history. Local JavaScript timers are **wake-up hints only**.

For:

```text
QUEUE_CONCURRENCY_RECONCILIATION
```

there is no periodic cadence gate; its due interval is zero. Existing queue-concurrency convergence remains event/config driven.

The PostgreSQL clock (`NOW()`) is authoritative for cross-replica lease/cadence decisions. Never use `Date.now()` to decide whether another replica may execute global work.

A running Background process has exactly one runtime-policy authority:

```text
last-known-good PostgreSQL BackgroundRuntimeConfig snapshot
```

Do not introduce Redis policy state, environment fallbacks, module-global defaults or another coordination store.

## Part A — global cadence and monotonic lease fencing

### Production files

Required primary files:

```text
src/runtime/background-runtime-lease.ts
src/runtime/dynamic-leased-scheduler.ts
```

Required tests:

```text
tests/unit/runtime/background-runtime-lease.test.ts
tests/unit/runtime/dynamic-leased-scheduler.test.ts
tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts
scripts/test-integration.mjs
```

### Acquisition semantics

Keep the public `tryAcquire(name)` call shape unless the current accepted code already exposes an equivalent typed API. Do not redesign unrelated queue-concurrency call sites.

For an existing lease row, acquisition succeeds only when both are true:

```text
leaseUntil <= PostgreSQL NOW()
AND
(lastFinishedAt IS NULL OR lastFinishedAt + authoritative cadence <= PostgreSQL NOW())
```

The authoritative cadence MUST be read in the acquisition transaction/SQL from:

```text
public.BackgroundRuntimeConfig(id = 'default')
```

using this exact mapping:

```text
BILLING_RECONCILIATION
    -> billingReconciliationIntervalSeconds

RECOVERY_CAPACITY_REPAIR
    -> recoveryRepairIntervalSeconds

TRANSLATION_RECONCILIATION
    -> translationReconciliationIntervalSeconds

QUEUE_CONCURRENCY_RECONCILIATION
    -> 0 seconds
```

Use fixed SQL/Prisma branches for that mapping. Do not dynamically construct a database column identifier from runtime text.

Do **not** use a process-local interval as the cross-replica due decision. This is required so a stale process cannot run early after a newer Admin change increases an interval.

The first acquisition for a name with no row is immediately eligible and inserts:

```text
generation = 1
lastFinishedAt = NULL
```

If `BackgroundRuntimeConfig(id='default')` is unexpectedly missing, scheduled periodic acquisition fails closed. Do not invent defaults in the lease service.

### Release semantics

Normal release MUST retain the lease row.

Do not `DELETE` it.

Perform one guarded `UPDATE` matching all of:

```text
name
ownerToken
generation
```

On successful normal release set using PostgreSQL time:

```text
leaseUntil     = NOW()
heartbeatAt    = NOW()
lastFinishedAt = NOW()
updatedAt      = NOW()
```

Do not reset `generation`.

Because the row remains, every later successful acquisition increments:

```text
generation = previous generation + 1
```

A stale older-generation heartbeat/release must affect zero rows.

A cycle that acquired the lease and then throws still counts as a completed scheduler attempt for cadence purposes, matching the existing non-overlapping scheduler behaviour. `runWithLease` therefore performs the guarded release in `finally` when the lease has not already been lost.

If `leaseLost === true`, the stale owner MUST NOT stamp `lastFinishedAt`.

### Dynamic scheduler semantics

Keep recursive non-overlapping `setTimeout`; do not introduce `setInterval`.

The scheduler must continue to:

1. require runtime config to be started;
2. react to a newer interval by rescheduling a waiting local timer;
3. never interrupt an in-flight local run;
4. acquire the distributed lease before business work;
5. fresh-read runtime config after successful acquisition and pass one immutable snapshot to that cycle;
6. schedule another local wake after skip/completion/error.

New binding rule:

> A local timer firing does not mean the global job is due. Only a successful cadence-aware PostgreSQL lease acquisition means the global job is due.

Never add process-local `lastRunAt` or per-replica cadence memory.

### Required PostgreSQL concurrency integration test

Add/update:

```text
tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts
```

Use the repository disposable PostgreSQL integration harness. Do not sleep for production intervals.

The test MUST:

1. capture and restore the runtime-config fields it changes;
2. set `billingReconciliationIntervalSeconds = 10` using direct test setup;
3. delete only the test `BILLING_RECONCILIATION` lease row;
4. construct two lease services with distinct explicit owner tokens;
5. race acquisition and prove exactly one obtains generation `1`;
6. release the winner;
7. prove the persisted lease row still exists with non-null `lastFinishedAt`;
8. immediately race both owners again and prove neither acquires inside the cadence window;
9. move only that row's `lastFinishedAt` into the past with PostgreSQL test setup, e.g. `NOW() - INTERVAL '11 seconds'`;
10. race again and prove exactly one owner acquires generation `2`;
11. prove the old generation-1 handle cannot heartbeat or release generation 2;
12. clean up and restore config in `finally`.

Add the integration test to the default integration test list in `scripts/test-integration.mjs`.

### Required scheduler skew regression

Use two scheduler instances with deliberately skewed local wake times and a shared fake cadence-aware lease.

Run multiple cadence periods. Business work should be deliberately short.

Required assertion:

```text
within each shared cadence window there is at most one completed global run,
even though both replica timers fire at different times
```

A one-time simultaneous acquisition race is insufficient.

## Part B — exact runtime-config validation parity

Primary file:

```text
src/runtime/background-runtime-config.ts
```

`BackgroundRuntimeConfigService` MUST validate the same persisted contract as DATABASE-004 before replacing last-known-good state.

Keep existing structural checks:

```text
id === "default"
version is a safe integer >= 0
all required fields are present
createdAt/updatedAt are valid Dates
returned snapshots/dates remain immutable
```

Replace generic non-negative validation with these exact bounds:

```text
billingReconciliationIntervalSeconds          10..3600
billingReconciliationShopBatchSize            1..200
shopifyUsagePublishBatchSize                  1..200
recoveryRepairIntervalSeconds                 30..3600
recoveryRepairShopBatchSize                   1..500
recoveryResumeBatchSize                       1..100
translationReconciliationIntervalSeconds      30..3600
translationBatchMaxRequests                   1..500
conversationQuietWindowMs                     250..10000
conversationMaxSettleWindowMs                 1000..30000
billingFrozenRecheckSeconds                   300..86400
billingProviderRetrySeconds                   30..3600
shopifyUsageRetryBaseSeconds                  10..3600
shopifyUsageRetryMaxSeconds                   60..86400
translationReconciliationPageSize             1..500
translationClaimTimeoutSeconds                60..86400
translationSubmitRetrySeconds                 30..86400
translationInitialPollSeconds                 30..86400
translationPollIntervalSeconds                30..86400
translationResultRetrySeconds                 30..86400
translationSubmitMaxAttempts                  1..10
translationMaxAutoRetries                     0..10
checkoutQueueGlobalConcurrency                1..100
orderQueueGlobalConcurrency                   1..100
pendingRecoveryQueueGlobalConcurrency         1..100
recoveryResumeQueueGlobalConcurrency          1..100
whatsappQueueGlobalConcurrency                1..100
merchantCommunicationsQueueGlobalConcurrency  1..100
billingSubscriptionQueueGlobalConcurrency     1..100
rawSenderLimitPerMinute                       1..10000
rawGlobalLimitPerMinute                       1..1000000
turnSenderLimitPerMinute                      1..10000
turnSenderLimitPerTenMinutes                  1..100000
turnConversationLimitPerMinute                1..10000
turnConversationLimitPerTenMinutes            1..100000
turnShopLimitPerMinute                        1..100000
turnGlobalLimitPerMinute                      1..1000000
discoverySenderLimitPerMinute                 1..10000
discoverySenderLimitPerTenMinutes             1..100000
discoveryConversationLimitPerMinute           1..10000
discoveryConversationLimitPerTenMinutes       1..100000
```

Mirror every cross-field rule exactly:

```text
conversationMaxSettleWindowMs >= conversationQuietWindowMs
shopifyUsageRetryMaxSeconds >= shopifyUsageRetryBaseSeconds
rawGlobalLimitPerMinute >= rawSenderLimitPerMinute
turnSenderLimitPerTenMinutes >= turnSenderLimitPerMinute
turnConversationLimitPerTenMinutes >= turnConversationLimitPerMinute
turnGlobalLimitPerMinute >= turnShopLimitPerMinute
turnShopLimitPerMinute >= turnSenderLimitPerMinute
discoverySenderLimitPerTenMinutes >= discoverySenderLimitPerMinute
discoveryConversationLimitPerTenMinutes >= discoveryConversationLimitPerMinute
discoverySenderLimitPerMinute <= turnSenderLimitPerMinute
discoverySenderLimitPerTenMinutes <= turnSenderLimitPerTenMinutes
discoveryConversationLimitPerMinute <= turnConversationLimitPerMinute
discoveryConversationLimitPerTenMinutes <= turnConversationLimitPerTenMinutes
```

Never silently clamp an invalid DB row.

Required behaviour:

```text
startup + invalid row
    -> start() rejects; readiness fails

running + newer invalid row
    -> log background.runtime_config.refresh_failed
    -> retain previous last-known-good snapshot/version
    -> do not notify listeners

newer valid row after invalid read
    -> adopt normally
```

Update normal runtime-config test fixtures to use valid DATABASE-004 defaults instead of assigning `1` to all numeric fields.

Focused tests must cover at least:

```text
below minimum
above maximum
settle < quiet
usage retry max < base
raw global < raw sender
10-minute < 1-minute
turn global < shop
discovery limit > normal turn limit
```

## Part C — remove production fallback authorities

Primary files:

```text
src/services/translation-runtime-config.ts
src/services/conversation-turn-processor.service.ts
src/services/inbound-whatsapp-abuse-admission.service.ts
```

### Translation

Remove production `testDefaults` and any catch that translates:

```text
Background runtime configuration has not started.
```

into hard-coded settings.

`currentTranslationRuntimeConfig(reader)` returns the supplied/default reader's current snapshot. If startup wiring is wrong, the error surfaces.

### Conversation settling

Keep dependency injection of a runtime-config reader for tests, with production default `backgroundRuntimeConfigService`, but remove the production fallback-to-test-default path.

### WhatsApp abuse admission

Keep dependency injection, but runtime abuse limits must come from `reader.current()` only. Remove production hard-coded fallback limits.

Do not replace any removed fallback with environment variables or duplicate constants.

### Test helper

Tests that instantiate these services without starting the global config MUST inject an explicit valid fake reader.

Create/reuse one test-only helper such as:

```text
tests/helpers/background-runtime-config.ts
```

It must build a full valid snapshot from the DATABASE-004 defaults, permit explicit overrides and expose `current()`.

Never import the test helper from production code.

Required focused assertions:

1. not-started translation reader throws;
2. not-started conversation reader throws;
3. not-started abuse reader throws;
4. explicit fake readers keep isolated tests deterministic.

## Part D — periodic billing retry authority

Primary file:

```text
src/services/billing-reconciliation.service.ts
```

`BillingReconciliationService.reconcileOnce(...)` already receives one immutable runtime snapshot in production. Use that exact cycle snapshot consistently.

### Scanner catch path

Change `markSyncError(...)` so it receives the current cycle runtime snapshot or the already-resolved two retry values.

Replace literals:

```text
FROZEN -> 60 * 60 * 1000
other  -> 5 * 60 * 1000
```

with:

```text
FROZEN -> billingFrozenRecheckSeconds * 1000
other  -> billingProviderRetrySeconds * 1000
```

Queued `nextReconcileAt` and BullMQ delay must therefore use the same committed cycle snapshot.

### Existing-subscription/no-provider path

Replace the existing literal:

```text
now + 5 * 60 * 1000
```

with:

```text
now + billingProviderRetrySeconds * 1000
```

when invoked by the production periodic scanner.

If direct unit-level overloads intentionally omit a snapshot, preserve only the minimum backward-compatible test seam needed by existing isolated tests; production entrypoints MUST always provide the snapshot.

Do not alter system-managed billing lifecycle tier policy such as `RETRY_TIERS`, free-cycle retry policy or rollover policy.

Required tests:

1. frozen scanner error uses a non-default configured frozen interval;
2. ordinary provider error uses a non-default configured provider retry interval;
3. existing-subscription/no-provider path uses configured provider retry interval;
4. one reconciliation call keeps one supplied immutable snapshot even if an external fake config source changes during the call.

## Part E — required validation

Run from `moda-interact-background`:

```bash
npm run test:unit -- tests/unit/runtime/background-runtime-lease.test.ts tests/unit/runtime/dynamic-leased-scheduler.test.ts tests/unit/runtime/background-runtime-config.test.ts
npm run test:unit -- tests/unit/services/billing-reconciliation.service.test.ts tests/unit/services/conversation-turn-processor.service.test.ts tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts
npm run test:integration -- tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts
npm run test:unit
npm run build
git diff --check
```

Also run every focused translation-service test affected by the runtime-reader/test-helper changes.

If the disposable PostgreSQL harness cannot apply the current migration chain, record the exact migration blocker. Do not replace the required PostgreSQL concurrency integration test with a mock and do not repair unrelated migration history in this task.

## Non-goals

Do not change:

```text
Prisma schema or migrations
Admin UI/actions
lease TTL = 120 seconds
heartbeat interval = 30 seconds
runtime-config refresh interval = 5 seconds
BullMQ fleet-wide concurrency architecture
Redis abuse key/window formats
fixed abuse window lengths
provider/model/credential configuration
billing lifecycle RETRY_TIERS
merchant recoveryDelayMinutes
business reconciliation algorithms other than the exact retry scheduling paths above
```

## Completion report requirements

The completion report MUST include:

```text
implementation commit
parent report commit
changed production files
changed/additional tests
exact focused/unit/integration/build commands and outcomes
lease generation evidence (1 -> 2 after normal release/reacquire)
retained-row + lastFinishedAt evidence
skewed-replica multi-window cadence evidence
invalid-newer-config last-known-good evidence
not-started runtime-reader failure evidence
non-default billing retry interval evidence
confirmation that Prisma schema/migrations were not changed by this task
```

Set the task to `status: review`, clear `executor`/`claimed_at`, publish the completion report, return to `moda_architect`, and STOP.

## Stop conditions

STOP and return to architect if:

- `DATABASE-005` / `BackgroundRuntimeLease.lastFinishedAt` is absent;
- implementing global cadence appears to require a second coordination store;
- an implementation would make local clocks authoritative for cross-replica eligibility;
- `QUEUE_CONCURRENCY_RECONCILIATION` would become cadence-delayed instead of zero-cadence;
- any new runtime-config column appears necessary;
- production startup intentionally invokes one of the affected services before `BackgroundRuntimeConfigService.start()` and correcting the order requires an architectural change;
- closing a fallback appears to require copying executable validation logic from another repository instead of implementing the explicit contract above.

## Completion Report

Status: Ready for Review

Implementation commit: `602cfed` (`fix(background): enforce global cadence and runtime config authority`)
Parent report commit: `c380e70` (superseded locally by the final amended report commit below).

Changed production files:

- `scripts/test-integration.mjs`
- `src/runtime/background-runtime-config.ts`
- `src/runtime/background-runtime-lease.ts`
- `src/services/billing-reconciliation.service.ts`
- `src/services/conversation-turn-processor.service.ts`
- `src/services/inbound-whatsapp-abuse-admission.service.ts`
- `src/services/translation-runtime-config.ts`

Changed and additional tests:

- `tests/helpers/background-runtime-config.ts`
- `tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts`
- `tests/unit/runtime/background-runtime-config.test.ts`
- `tests/unit/runtime/dynamic-leased-scheduler.test.ts`
- `tests/unit/services/conversation-turn-processor.service.test.ts`
- `tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts`
- affected translation assembly, poll, submit, and reconciliation tests

Validation:

- `npm run test:unit -- tests/unit/runtime/background-runtime-lease.test.ts tests/unit/runtime/dynamic-leased-scheduler.test.ts tests/unit/runtime/background-runtime-config.test.ts` passed: 64 files, 984 tests.
- `npm run test:unit -- tests/unit/services/billing-reconciliation.service.test.ts tests/unit/services/conversation-turn-processor.service.test.ts tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts` passed: 64 files, 984 tests.
- `npm run test:unit -- tests/unit/services/translation-batch-assembly.service.test.ts tests/unit/services/translation-batch-poll.service.test.ts tests/unit/services/translation-batch-submit.service.test.ts tests/unit/services/translation-reconciliation.service.test.ts` passed: 64 files, 984 tests.
- `npm run test:integration -- tests/integration/background-runtime-lease-cadence.concurrency.integration.test.ts` passed: 1 file, 1 test, using the disposable PostgreSQL harness.
- `npm run test:unit` passed: 64 files, 984 tests.
- `npm run build` passed, including `prisma generate` and TypeScript compilation.
- `git diff --check` passed.

Behavioural evidence:

- PostgreSQL cadence-aware acquisition raced two explicit owners, produced exactly one generation `1`, retained the lease row after release with non-null `lastFinishedAt`, rejected both immediate reacquisitions inside the cadence window, then produced exactly one generation `2` after moving only `lastFinishedAt` behind the cadence boundary. The generation-1 handle could not heartbeat or release generation 2.
- The dynamic scheduler regression uses deliberately skewed replica wake times across multiple cadence windows and asserts at most one completed global run per shared window.
- Runtime-config tests cover invalid below-minimum and above-maximum values, cross-field limit violations, startup rejection, and invalid newer rows retaining the prior last-known-good snapshot/version without listener notification.
- Translation, conversation, and abuse readers now fail with `Background runtime configuration has not started.` when not started; isolated tests inject explicit valid readers.
- Billing reconciliation tests verify non-default `billingFrozenRecheckSeconds` and `billingProviderRetrySeconds` are used consistently from one immutable cycle snapshot, including the existing-subscription/no-provider path.
- No Prisma schema or migration files were changed by this task.

## Architect Review

### Review Status

Accepted

### Review Summary

Attempt 1 is accepted on functionality. The implementation now makes PostgreSQL authoritative for both lease ownership and shared global cadence, retains lease rows on normal release, stamps `lastFinishedAt` with PostgreSQL `NOW()`, and preserves monotonic fencing generations across release/reacquire cycles. The real PostgreSQL integration test proves generation `1 -> 2`, retained-row cadence blocking, and stale-handle fencing.

The combined runtime-authority scope is also complete: Background validates the DATABASE-004 min/max and cross-field contract before adopting newer snapshots; invalid newer rows retain last-known-good state without listener notification; production translation, conversation-settling and abuse-admission readers no longer fall back to compiled defaults; and the periodic billing scanner uses the supplied cycle snapshot for configurable frozen/provider retry timing. The remaining literal fallback values in `BillingReconciliationService` are confined to the explicitly preserved direct-test seam because the production periodic entrypoint always supplies the runtime snapshot.

`ARCH-014-BACKGROUND-007` remains superseded because its full scope was merged into this task. Implementation commit `602cfed` is accepted. No further BACKGROUND-006 attempt is required.
