---
id: ARCH-014-BACKGROUND-004
architecture_id: ARCH-014
title: Apply runtime configuration to messaging settle behaviour and WhatsApp abuse limits
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 65
executor:
claimed_at:
attempt: 1
depends_on:
- ARCH-014-BACKGROUND-002
- ARCH-014-BACKGROUND-003
enables:
- ARCH-014-BACKGROUND-005
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-014-BACKGROUND-004

## Objective

Make customer-turn settling and approved WhatsApp abuse thresholds tunable at runtime without weakening the fixed abuse-window design or fail-closed limiter behaviour.

## Messaging entrypoint

`src/entrypoints/messaging.ts` MUST start `backgroundRuntimeConfigService` before dynamically importing the WhatsApp worker and close it on shutdown.

There is one config service per process.

## Conversation settling

Modify:

```text
src/services/conversation-turn-processor.service.ts
```

Replace runtime authority from:

```text
QUIET_WINDOW_MS = 3_000
MAX_SETTLE_WINDOW_MS = 10_000
```

with:

```text
conversationQuietWindowMs
conversationMaxSettleWindowMs
```

`PROCESSING_LEASE_MS = 120_000` remains system-managed and unchanged.

At every enqueue/process settle calculation, use one current config snapshot.

The database guarantees:

```text
maxSettle >= quietWindow
```

The service must also fail closed if an injected test snapshot violates it.

Changing the setting does not alter already-sent replies. Pending jobs re-evaluate settle delay when processed, using current configuration.

## Abuse protection

Modify:

```text
src/services/inbound-whatsapp-abuse-admission.service.ts
```

Keep these window lengths fixed:

```text
raw sender/global:             60 seconds
turn sender short:             60 seconds
turn sender long:             600 seconds
turn conversation short:       60 seconds
turn conversation long:       600 seconds
turn shop/global:              60 seconds
product-discovery short:       60 seconds
product-discovery long:        600 seconds
```

Only replace numeric LIMIT constants with current config values:

```text
rawSenderLimitPerMinute
rawGlobalLimitPerMinute
turnSenderLimitPerMinute
turnSenderLimitPerTenMinutes
turnConversationLimitPerMinute
turnConversationLimitPerTenMinutes
turnShopLimitPerMinute
turnGlobalLimitPerMinute
discoverySenderLimitPerMinute
discoverySenderLimitPerTenMinutes
discoveryConversationLimitPerMinute
discoveryConversationLimitPerTenMinutes
```

Do not query DB on every inbound message. Use last-known-good in-memory config.

Redis remains shared across horizontally scaled messaging replicas; all replicas use the same key namespace/window semantics.

During the <=5s config propagation window different replicas may momentarily enforce old/new numeric limits; this is acceptable. Versions only move forward and all replicas converge automatically.

## Security behaviour that MUST NOT change

- limiter Redis error remains fail-closed with `LIMITER_UNAVAILABLE`;
- provider-message/idempotency duplicate handling is unchanged;
- discovery limits remain <= normal turn limits due DB + runtime validation;
- window lengths are not Admin-editable;
- Redis key namespace/version is not changed merely because limits are dynamic.

## Mandatory tests

1. quiet window reads runtime config;
2. maximum settle reads runtime config;
3. `max < quiet` injected config fails closed;
4. config 3s -> 1s affects a subsequent turn without restart;
5. raw sender limit reads config;
6. raw global limit reads config;
7. every settled-turn limit reads corresponding config field;
8. discovery limits remain distinct from general limits;
9. Redis failure still suppresses;
10. two service instances sharing Redis enforce the same committed limits after config convergence;
11. an older config version is ignored by the process config service;
12. fixed 60s/600s window values remain unchanged;
13. `PROCESSING_LEASE_MS` remains unchanged/system-managed.

## Validation

```bash
npm run test:unit
npm run build
git diff --check
```

## Stop conditions

STOP if implementation requires making abuse windows editable, querying PostgreSQL per WhatsApp message, or weakening fail-closed limiter behaviour.

## Completion Report

Status: Ready for Review

Implementation commit: `b3b65f8` on `task/ARCH-014-BACKGROUND-004`

Implementation mapping:

- `src/entrypoints/messaging.ts`: starts the singleton `backgroundRuntimeConfigService` before the dynamic WhatsApp worker import and closes it with worker resources.
- `src/services/conversation-turn-processor.service.ts`: reads one current runtime snapshot for each enqueue/process settle calculation, applies runtime quiet/max windows, rejects injected `max < quiet` snapshots before claiming work, and leaves `PROCESSING_LEASE_MS` unchanged.
- `src/services/inbound-whatsapp-abuse-admission.service.ts`: reads one last-known-good runtime snapshot per admission, maps all raw/settled/discovery numeric limits, and preserves fixed 60-second/600-second windows, Redis namespace, and fail-closed error handling.
- Focused tests cover runtime settle changes, invalid ordering, every abuse limit field, discovery/general separation, fixed windows, shared Redis enforcement, Redis suppression, version-forward config behavior, and the unchanged processing lease.

Validation evidence:

- `npx vitest run tests/unit/services/conversation-turn-processor.service.test.ts tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts`: passed, 2 files / 61 tests.
- `npm run test:unit`: passed, 62 files / 966 tests.
- `npm run build`: passed, Prisma generation and TypeScript compilation completed.
- `git diff --check`: passed.
- Editor diagnostics for all five changed files: no errors.

Limitations: npm install reported pre-existing audit warnings for three high-severity vulnerabilities and install-script approval notices; no dependency files were changed. No database, queue, schema, Redis key namespace, or Admin-editable window changes were made.
## Architect Review

### Review Status

Accepted

### Review Summary

Attempt 1 is accepted on functionality. The messaging entrypoint starts the shared runtime-config service before loading the WhatsApp worker; conversation settling uses one current runtime snapshot per settle calculation, re-evaluates pending work on processing, preserves the fixed 120-second processing lease and fails closed on an invalid max/quiet ordering. WhatsApp abuse admission reads one last-known-good in-memory runtime snapshot per admission, maps all twelve approved numeric limits, preserves the fixed 60-second/600-second windows, Redis namespace and duplicate semantics, and remains fail-closed on limiter errors. No per-message database query or Admin-editable abuse window was introduced.

Implementation commit `b3b65f8` is accepted. No further BACKGROUND-004 attempt is required.
