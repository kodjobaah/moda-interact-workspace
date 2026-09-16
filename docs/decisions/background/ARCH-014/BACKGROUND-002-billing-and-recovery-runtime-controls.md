---
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
status: ready
priority: 64
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-BACKGROUND-001
enables:
- ARCH-014-BACKGROUND-004
- ARCH-014-BACKGROUND-005
created: 2026-09-16
updated: 2026-09-16
---

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
