---
id: ARCH-014-BACKGROUND-007
architecture_id: ARCH-014
title: Close runtime-config validation and authority gaps in background services
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 69
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-014-BACKGROUND-006
enables:
- ARCH-014-SYSTEM-TEST-003
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-BACKGROUND-007

## Objective

Close the remaining runtime-authority gaps identified in the post-implementation audit:

1. Background accepts structurally present but database-invalid runtime snapshots because its validator does not mirror the DATABASE-004 bounds/cross-field rules;
2. three production service adapters silently fall back to process-local test defaults if the shared runtime config service was not started;
3. the periodic billing scanner still schedules some retries using literal `5 min` / `60 min` values instead of the committed `billingProviderRetrySeconds` / `billingFrozenRecheckSeconds` snapshot.

After this task, a running process has exactly one runtime-policy authority: the last-known-good PostgreSQL `BackgroundRuntimeConfig` snapshot.

## Binding scope

Touch only `moda-interact-background`.

Primary files:

```text
src/runtime/background-runtime-config.ts
src/services/translation-runtime-config.ts
src/services/conversation-turn-processor.service.ts
src/services/inbound-whatsapp-abuse-admission.service.ts
src/services/billing-reconciliation.service.ts
```

Update affected tests and add a shared test fixture if useful. Do not change Prisma schema/migrations, Admin UI, Redis key formats, abuse window lengths, billing lifecycle tier policy, or provider credentials.

## Part A — exact Background validation parity

`BackgroundRuntimeConfigService` must validate the same persisted contract as DATABASE-004 before replacing its last-known-good snapshot.

Keep the existing checks for:

```text
id === "default"
version is safe integer >= 0
all required fields are present
createdAt/updatedAt are valid Dates
immutable returned snapshot/dates
```

Replace the current generic `>= 0` numeric check with exact per-field ranges:

```text
billingReconciliationIntervalSeconds        10..3600
billingReconciliationShopBatchSize          1..200
shopifyUsagePublishBatchSize                1..200
recoveryRepairIntervalSeconds               30..3600
recoveryRepairShopBatchSize                 1..500
recoveryResumeBatchSize                     1..100
translationReconciliationIntervalSeconds    30..3600
translationBatchMaxRequests                 1..500
conversationQuietWindowMs                   250..10000
conversationMaxSettleWindowMs               1000..30000
billingFrozenRecheckSeconds                 300..86400
billingProviderRetrySeconds                 30..3600
shopifyUsageRetryBaseSeconds                10..3600
shopifyUsageRetryMaxSeconds                 60..86400
translationReconciliationPageSize           1..500
translationClaimTimeoutSeconds              60..86400
translationSubmitRetrySeconds               30..86400
translationInitialPollSeconds               30..86400
translationPollIntervalSeconds              30..86400
translationResultRetrySeconds               30..86400
translationSubmitMaxAttempts                1..10
translationMaxAutoRetries                   0..10
checkoutQueueGlobalConcurrency              1..100
orderQueueGlobalConcurrency                 1..100
pendingRecoveryQueueGlobalConcurrency       1..100
recoveryResumeQueueGlobalConcurrency        1..100
whatsappQueueGlobalConcurrency              1..100
merchantCommunicationsQueueGlobalConcurrency 1..100
billingSubscriptionQueueGlobalConcurrency   1..100

rawSenderLimitPerMinute                     1..10000
rawGlobalLimitPerMinute                     1..1000000
turnSenderLimitPerMinute                    1..10000
turnSenderLimitPerTenMinutes                1..100000
turnConversationLimitPerMinute              1..10000
turnConversationLimitPerTenMinutes          1..100000
turnShopLimitPerMinute                      1..100000
turnGlobalLimitPerMinute                    1..1000000
discoverySenderLimitPerMinute               1..10000
discoverySenderLimitPerTenMinutes           1..100000
discoveryConversationLimitPerMinute         1..10000
discoveryConversationLimitPerTenMinutes     1..100000
```

Mirror all cross-field rules exactly:

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

Do not silently clamp invalid DB values.

Required behaviour:

```text
startup + invalid row
    -> start() rejects; process readiness fails

already running + newer invalid row
    -> log background.runtime_config.refresh_failed
    -> retain previous last-known-good snapshot/version
    -> do not notify listeners

newer valid row after the invalid read
    -> adopt it normally
```

Update `tests/unit/runtime/background-runtime-config.test.ts` so its normal fixture uses real DATABASE-004 defaults, not `1` for every numeric field.

Add focused tests for at least one violation in each class:

```text
below minimum
above maximum
conversation settle < quiet
usage retry max < base
raw global < raw sender
10-minute < 1-minute
turn global < shop
product-discovery limit > normal turn limit
```

## Part B — remove production test-default fallback authority

### Translation

In:

```text
src/services/translation-runtime-config.ts
```

remove `testDefaults` and the catch that converts:

```text
Background runtime configuration has not started.
```

into hard-coded values.

`currentTranslationRuntimeConfig(reader)` must simply return the supplied/default `reader.current()` snapshot. If production startup wiring is wrong, the error must surface rather than creating a second policy authority.

### Conversation settling

In:

```text
src/services/conversation-turn-processor.service.ts
```

remove its `testDefaults` fallback. Keep dependency injection:

```text
runtimeConfig?: RuntimeConfigReader
```

with production default `backgroundRuntimeConfigService`, but `currentConversationRuntimeConfig(...)` must not catch the not-started error.

### Abuse protection

In:

```text
src/services/inbound-whatsapp-abuse-admission.service.ts
```

remove its abuse `testDefaults` fallback. Keep production default injection, but runtime limits must come from `reader.current()` only.

Do not replace these fallbacks with environment variables or duplicated constants.

### Test fixtures

Tests that instantiate the above services without starting the shared config must inject an explicit fake reader.

Create one reusable test helper if it reduces repetition, for example:

```text
tests/helpers/background-runtime-config.ts
```

It must construct a **valid full snapshot using the real DATABASE-004 defaults**, permit explicit overrides, and expose a reader with `current()`.

Do not export/import that test helper from production code.

## Part C — periodic billing retry authority

`BillingReconciliationService.reconcileOnce(...)` already receives the cycle runtime snapshot in production. Use that same immutable snapshot consistently for retry scheduling.

### Scanner catch path

Change:

```text
markSyncError(shopId, error)
```

so the call receives the current cycle's runtime configuration (or the two resolved retry seconds).

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

The queued `nextReconcileAt` and BullMQ delay must therefore reflect the same committed cycle snapshot.

### Existing-subscription / no-provider path

Inside `applySubscription(...)`, replace the existing literal:

```text
now + 5 * 60 * 1000
```

with:

```text
now + billingProviderRetrySeconds * 1000
```

when a runtime snapshot is supplied by the production periodic scanner.

Preserve current test/backwards-compatible defaults for direct unit calls that intentionally omit a runtime snapshot if existing tests require that overload; do **not** let the production entrypoint omit the runtime snapshot.

Do not modify the separate billing lifecycle retry tier structure (`RETRY_TIERS`, rollover/free-cycle policy); those remain system-managed by architecture decision.

## Required tests

Add/update tests proving:

1. not-started translation runtime reader throws rather than returning defaults;
2. not-started conversation runtime reader throws rather than returning defaults;
3. not-started abuse runtime reader throws rather than returning defaults;
4. explicit injected test reader still makes isolated unit tests deterministic;
5. periodic frozen scanner error uses a non-default configured frozen interval;
6. periodic ordinary provider error uses a non-default configured provider retry interval;
7. existing-subscription/no-provider path uses configured provider retry interval;
8. one reconciliation call keeps one supplied snapshot even if an external fake config source changes during the call;
9. invalid newer config never replaces last-known-good or notifies listeners;
10. valid newer config after an invalid read is adopted.

## Required validation

Run:

```bash
npm run test:unit -- tests/unit/runtime/background-runtime-config.test.ts
npm run test:unit -- tests/unit/services/billing-reconciliation.service.test.ts tests/unit/services/conversation-turn-processor.service.test.ts tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts
npm run test:unit
npm run build
git diff --check
```

Also run focused translation service tests affected by the shared test reader changes.

## Stop conditions

STOP and return to architect if:

- this task appears to require new runtime-config columns;
- a production entrypoint intentionally starts one of these services before `BackgroundRuntimeConfigService.start()` and cannot be corrected without an architectural change;
- closing a fallback would require embedding Admin/database validation code from another repository rather than implementing the explicit contract above.
