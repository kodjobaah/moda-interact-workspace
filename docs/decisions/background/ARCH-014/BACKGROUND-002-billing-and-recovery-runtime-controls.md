id: ARCH-014-BACKGROUND-002
architecture_id: ARCH-014
title: Apply runtime controls to billing and recovery background processing
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 64
executor: null
claimed_at: null
attempt: 2
depends_on:
enables:
created: 2026-09-16
updated: 2026-09-16

# ARCH-014-BACKGROUND-002

## Objective

Replace the identified billing/recovery operational hard-codes with `BackgroundRuntimeConfig` while preserving billing correctness and per-merchant recovery settings.

## Billing periodic reconciliation

Modify:

```text
src/entrypoints/billing.ts
src/runtime/billing-scheduler.ts
src/services/billing-reconciliation.service.ts
src/services/shopify-usage-event-publisher.service.ts
src/services/shopify-subscription-lifecycle-reconciliation.service.ts
```

### Entry-point sequence

Inside readiness loading:

1. start `backgroundRuntimeConfigService`;
2. construct/import worker resources only after initial config is available;
3. perform the initial billing cycle through the `BILLING_RECONCILIATION` distributed lease — do not run an unleased startup reconciliation;
4. replace `startBillingReconciliationScheduler(..., 60_000, ...)` with the common dynamic leased scheduler;
5. interval source is `billingReconciliationIntervalSeconds * 1000`;
6. close config service after schedulers/workers using normal resource ordering.

With N billing replicas, only one may execute a given global scan while a valid lease exists.

### Per-cycle fresh values

The fresh snapshot passed by the lease winner controls:

```text
billingReconciliationShopBatchSize
shopifyUsagePublishBatchSize
billingFrozenRecheckSeconds
billingProviderRetrySeconds
shopifyUsageRetryBaseSeconds
shopifyUsageRetryMaxSeconds
```

Do not re-read config mid-cycle. One cycle uses one version.

### Billing shop scan

Remove `DEFAULT_SHOP_PAGE_SIZE = 50` as runtime authority.

`reconcileOnce` must accept/use the configured shop batch size and preserve rotating-page behavior.

Do not exceed database range even if an injected test config is malformed; fail closed instead of silently clamping production config.

### Usage-event publisher

`publishDue` must accept/use configured `shopifyUsagePublishBatchSize`.

Replace runtime use of:

```text
DEFAULT_PAGE_SIZE
RETRY_BASE_MS
RETRY_MAX_MS
```

with snapshot values.

Keep these system-managed:

```text
IN_FLIGHT_RECOVERY_MS
MAX_RESPONSE_SUMMARY_LENGTH
provider retryability classification
```

The runtime relationship `retryMax >= retryBase` is guaranteed by DB but must also be asserted by runtime parsing.

### Subscription lifecycle retries

Replace only:

```text
FROZEN_RECONCILE_INTERVAL_MS
PROVIDER_RETRY_INTERVAL_MS
```

with:

```text
billingFrozenRecheckSeconds
billingProviderRetrySeconds
```

Do **not** migrate or expose:

```text
RETRY_WINDOW_MS
FREE_CYCLE_DISCOVERY_RETRY_MS
ROLLOVER_RETRY_MS
RETRY_TIERS
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
```

Those remain billing lifecycle/correctness policy.

## Recovery capacity repair

Modify:

```text
src/entrypoints/recovery.ts
src/services/recovery-capacity-resume.service.ts
src/workers/recovery-capacity-resume.worker.ts
```

Replace the entrypoint `setInterval(..., 5 * 60 * 1000)` with `RECOVERY_CAPACITY_REPAIR` dynamic leased scheduling.

The fresh cycle snapshot controls:

```text
recoveryRepairIntervalSeconds
recoveryRepairShopBatchSize
```

The resume worker uses current last-known-good:

```text
recoveryResumeBatchSize
```

for each job.

Remove runtime authority from:

```text
MAX_REPAIR_SHOPS = 100
MAX_RECOVERIES_PER_JOB = 25
```

The continuation semantics after a full resume batch remain exactly the same.

Keep queue retry attempts/backoff unchanged.

## Per-merchant recovery delay is NOT migrated

`ShopSettings.recoveryDelayMinutes` remains authoritative for an individual merchant's abandoned-cart delay.

`DEFAULT_RECOVERY_DELAY_MINUTES` remains only the domain default for missing shop configuration.

Do not create a global replacement.

## Failure behaviour

- Config refresh failure: use last-known-good.
- Lease unavailable: skip that global repair/reconciliation cycle.
- Billing/recovery work failure: existing error handling/logging; scheduler continues.
- No config mutation may occur from Background.

## Mandatory tests

Billing:

1. two billing entrypoints/schedulers sharing lease produce one initial scan;
2. configured 15-second interval is used;
3. interval 60 -> 15 reschedules without restart;
4. configured shop batch passed to rotating page;
5. usage publish batch passed to publisher;
6. retry base/max use config;
7. frozen/provider retry uses config;
8. fixed billing retry tiers remain unchanged;
9. current cycle remains on its starting config version after a concurrent config update.

Recovery:

10. two recovery schedulers sharing lease execute one repair;
11. repair interval changes at runtime;
12. repair shop batch uses config;
13. resume job batch uses config;
14. continuation still schedules after a full batch;
15. `ShopSettings.recoveryDelayMinutes` behavior is unchanged;
16. queue retry/backoff remains unchanged.

Static search test must reject:

```text
startBillingReconciliationScheduler(...60_000...)
setInterval(...recoveryCapacityResumeService.repair...)
```

as runtime scheduling authority.

## Validation

```bash
npm run test:unit
npm run build
git diff --check
```

Run relevant integration tests if their dependencies are available.

## Stop conditions

STOP if applying runtime values would change billing retry-tier semantics, merchant recovery delay semantics, or require a second scheduler/lock implementation.

## Completion Report

Status: Ready for Review

### Attempt 2 correction mapping

- Captured exactly one `backgroundRuntimeConfigService.current()` snapshot at the start of each queued reconciliation job through an injectable reader; unit tests inject a minimal reader.
- Passed that snapshot into queued `ShopifySubscriptionLifecycleReconciliationService` construction, both queued pre-close usage flushes, and frozen provider-failure scheduling.
- Removed the queued frozen provider-failure hard-coded one-hour delay; it now uses `billingFrozenRecheckSeconds * 1000`.
- Added focused coverage for one snapshot read/reuse, configured lifecycle frozen timing, usage publisher runtime values, and configured frozen provider retry timing. Existing fixed retry-tier, merchant-delay, and queue-policy coverage remains unchanged.

- Implementation branch: `task/ARCH-014-BACKGROUND-002`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-BACKGROUND-002`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-BACKGROUND-002`
- Claim commit: `6d7f5db5d105bf277547c24031ff214cb4a0f15a`
- Background submodule commit: `89dca92325cefc96fe2dff5021d1e5ee0e8f7fe1`
- Implementation commits: `c11c387a678dfb7509adae93e607bf64cb568050`, `1977de5`, `4bfffc513fab987fc037f259c42d9a55f28e570b`, `a210715`
- Published branch head: `a210715`

Validation completed in `moda-interact-background`:

- Focused queued billing test: passed, 62 files and 952 tests.
- `npm run test:unit`: passed, 62 files and 952 tests.
- `npm run test:integration`: passed, 2 files and 3 tests.
- `npm run build`: passed, including Prisma client generation and TypeScript compilation.
- `git diff --check`: passed.

Launcher evidence preserved: prepared attempt 2, executor `copilot`, dependency `ARCH-014-BACKGROUND-001` complete, database submodule initialized at `47232f6876469f209c7efde4cefbb8a47d864e6a`, and canonical parent/implementation worktrees supplied by the launcher. No additional preparation or claim was performed.

The billing retry tiers, merchant recovery delay settings, and queue retry/backoff policies remain system-managed and unchanged. No queues, schema/models/statuses, or alternate settings sources were added. No unresolved validation blockers or infrastructure limitations remain.

## Architect Review

### Review Status

Changes Requested

### Functional finding

The global billing/recovery scheduler work is functionally sound, but the Admin-controlled billing publisher/lifecycle retry values are not yet authoritative across all production billing execution paths.

`src/services/billing-subscription-reconciliation.service.ts` still contains queued-job paths that bypass the runtime snapshot:

1. both pre-close usage flushes call `shopifyUsageEventPublisherService.publishDue({ billingPeriodId })` without `runtimeConfig`, so those production publishes still fall back to the publisher defaults (`50`, `60s`, `3600s`) instead of `shopifyUsagePublishBatchSize`, `shopifyUsageRetryBaseSeconds`, and `shopifyUsageRetryMaxSeconds`;
2. queued lifecycle reconciliation constructs `new ShopifySubscriptionLifecycleReconciliationService(this.database)` without the runtime snapshot, so its `billingFrozenRecheckSeconds` / `billingProviderRetrySeconds` decisions fall back to defaults;
3. `recordFrozenProviderFailure(...)` still schedules `now + 60 * 60 * 1000`, so a queued frozen-subscription provider failure ignores the configured frozen recheck interval.

As a result, changing these values in Runtime Controls affects the periodic global billing scan but not every production billing path that performs the same operational decisions.

### Required Attempt 2 correction

Keep this correction narrowly scoped to queued billing-subscription reconciliation. Do not redesign the scheduler, lease implementation, billing lifecycle, or recovery flow.

#### 1. Capture one runtime snapshot per queued reconciliation job

File:

`moda-interact-background/src/services/billing-subscription-reconciliation.service.ts`

Add an injectable runtime-config reader whose production default is `backgroundRuntimeConfigService`. The injected contract only needs `current()`.

At the start of `reconcileJob(...)`, after parsing the job and before any runtime-controlled decision, capture exactly one snapshot:

```ts
const runtimeConfig = this.runtimeConfig.current();
```

Use this same immutable snapshot for the entire job. Do not call `current()` repeatedly during the same job and do not query PostgreSQL directly from this service.

The billing entrypoint already starts `backgroundRuntimeConfigService` before constructing/importing the billing worker, so the production default is valid. Unit tests may inject a minimal `{ current: () => snapshot }` reader.

#### 2. Pass that snapshot into lifecycle reconciliation

Replace the queued-job construction:

```ts
new ShopifySubscriptionLifecycleReconciliationService(this.database)
```

with construction that receives the same captured `runtimeConfig` in the existing runtime-config constructor slot.

Do not change `ShopifySubscriptionLifecycleReconciliationService` policy semantics. Its existing mapping remains:

- `billingFrozenRecheckSeconds` -> frozen recheck timing;
- `billingProviderRetrySeconds` -> provider retry timing.

#### 3. Pass that snapshot into both queued pre-close usage flushes

Every production `publishDue(...)` call in `billing-subscription-reconciliation.service.ts` must pass:

```ts
{
  billingPeriodId,
  runtimeConfig,
}
```

This applies to both pre-close usage-flush paths in the file.

After the correction, a source scan of production `src/` must not find a billing-subscription reconciliation `publishDue({ billingPeriodId ... })` call that omits `runtimeConfig`.

Do not remove the publisher's constructor/test defaults if existing unit tests still need them; the requirement is that all production billing paths pass runtime configuration explicitly.

#### 4. Remove the remaining hard-coded frozen recheck delay

Change `recordFrozenProviderFailure(...)` to receive the same captured runtime snapshot (or the exact required `billingFrozenRecheckSeconds` value) and replace:

```ts
60 * 60 * 1000
```

with:

```ts
runtimeConfig.billingFrozenRecheckSeconds * 1000
```

This preserves the existing semantic: a provider failure while reconciling a FROZEN subscription schedules the next frozen recheck using the Admin-controlled frozen interval.

#### 5. Preserve fixed billing correctness policy

Do NOT migrate, rename, or change:

```text
RETRY_WINDOW_MS
FREE_CYCLE_DISCOVERY_RETRY_MS
ROLLOVER_RETRY_MS
RETRY_TIERS
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
```

Do not change plan-transition retry behavior, recovery-delay semantics, queue retry/backoff, provider retryability classification, or billing-period correctness logic.

### Required focused validation

Add/adjust only enough focused tests to prove the corrected production behavior:

1. one queued reconciliation job captures one runtime snapshot and reuses it;
2. queued lifecycle reconciliation receives that snapshot and a frozen lifecycle/recheck outcome uses `billingFrozenRecheckSeconds`;
3. queued pre-close usage publishing receives `shopifyUsagePublishBatchSize`, `shopifyUsageRetryBaseSeconds`, and `shopifyUsageRetryMaxSeconds` through the same snapshot;
4. the frozen provider-failure path schedules with `billingFrozenRecheckSeconds`, not a hard-coded hour;
5. existing `RETRY_TIERS`, `FREE_CYCLE_DISCOVERY_RETRY_MS`, and `ROLLOVER_RETRY_MS` behavior remains unchanged.

Then run the task's existing validation commands:

```bash
npm run test:unit
npm run build
git diff --check
```

Do not broaden Attempt 2 into exhaustive test expansion. Stop once the production runtime-control bypasses above are removed and focused regressions pass.

### Architecture Conformance

Not yet accepted. The implementation is otherwise aligned with ARCH-014-BACKGROUND-002, including dynamic leased billing/recovery scheduling, per-cycle billing scan config, recovery repair/runtime batch controls, last-known-good resume batch sizing, and preservation of merchant recovery delay and fixed billing retry policies.
