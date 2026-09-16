---
id: ARCH-016-BACKGROUND-002
architecture_id: ARCH-016
title: Expire checkout-recovery generations and restart after later checkout activity
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-016-DATABASE-001
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-016-BACKGROUND-002

## Objective

Implement the agreed `CheckoutRecovery` generation lifecycle: monotonic external activity, admin-controlled inactivity expiry, immutable EXPIRED generations and normal pending-recovery restart after later checkout updates.

## Authorized implementation surface

```text
src/services/checkout-recovery.service.ts
src/services/pending-recovery-candidate.service.ts only where expired restart uses existing scheduling
src/services/checkout-recovery-expiry.service.ts             # new
src/workers/checkout.worker.ts
src/workers/whatsapp.worker.ts                               # inbound activity update only
src/entrypoints/recovery.ts                                  # expiry scheduler
src/runtime/background-runtime-config.ts                     # lifetime field validation/read
src/runtime/background-runtime-lease.ts only if lease enum mapping requires it
tests/unit/services/checkout-recovery*.test.ts
focused worker/runtime tests
```

Do not change Conversation uniqueness or create a new worker service.

## Latest-generation lookup

Replace code paths that assume Prisma unique key `shopId_checkoutToken`.

Create one repository-local helper with deterministic semantics:

```text
findLatestRecovery(shopId, checkoutToken)
  orderBy generation DESC
  tie-break by id only as defensive measure; unique generation makes ties invalid
```

Create/materialize generation only under the existing checkout-scoped lock.

## Materializing a new generation

When matured PendingRecoveryCandidate is processed:

1. fetch latest historical recovery for shop+checkout inside existing checkout lock;
2. if none -> new generation = 1;
3. if latest status EXPIRED -> new generation = latest.generation + 1;
4. if latest status DETECTED/MESSAGE_SENT/ENGAGED -> no-op existing active recovery;
5. if latest status COMPLETED/CANCELLED -> preserve terminal discard; do not restart;
6. fetch current Shopify abandoned checkout using existing authoritative lookup;
7. if recoverable, create the new CheckoutRecovery generation with:

```text
status DETECTED
detectedAt = materialisation/recovery seed time
lastExternalActivityAt = max(candidate.lastActivityAt/current provider activity timestamp available)
generation calculated above
```

Do not `upsert` by shop+checkout anymore. Use create-after-locked decision and handle database unique conflict idempotently by re-reading the latest row.

## Checkout update behavior

Current `handleCheckoutUpdatedContract` first refreshes a PendingRecoveryCandidate and otherwise looks up Recovery.

Required behavior:

### Pending candidate exists

Keep existing activity-refresh/reschedule behavior.

### Latest recovery active

```text
DETECTED / MESSAGE_SENT / ENGAGED
```

Continue current provider re-fetch/basket refresh AND set:

```text
lastExternalActivityAt = max(current, event.activityAt)
```

Do not reset `detectedAt` or create a new generation.

### Latest recovery EXPIRED

Do NOT refresh/reopen it.

Instead call existing `PendingRecoveryCandidate` scheduling path using the checkout update's `activityAt` and normal merchant `recoveryDelayMinutes`.

Return a result identifying pending restart, not terminal ignore.

Further checkout updates refresh that candidate and reset its inactivity due time exactly as current pending-candidate semantics require.

### Latest recovery COMPLETED or CANCELLED

Keep terminal ignore. Do not schedule a new generation.

### No historical recovery

Preserve current architecture unless the existing checkout-update event is already defined to seed a pending candidate. ARCH-016 only authorizes restart specifically from latest EXPIRED. Do not broaden every arbitrary checkout update into recovery creation without existing evidence.

## Monotonic inbound customer activity

When an inbound WhatsApp message resolves to a recovery Conversation:

```text
conversation.checkoutRecoveryId != null
```

update that CheckoutRecovery:

```text
lastExternalActivityAt = max(current, inbound received/created timestamp)
```

Do this in the same bounded durable processing transaction where practical.

An inbound customer message received after a recovery already EXPIRED does NOT reopen the expired recovery and does not change it back to active. It may update conversation history under existing messaging behavior, but generation restart requires later Shopify checkout activity as agreed.

Do not update lifetime from outbound messages.

## Runtime config

Extend `src/runtime/background-runtime-config.ts` exact runtime shape/validator with:

```text
checkoutRecoveryLifetimeDays
```

Bounds:

```text
1..90
```

No hard-coded 21-day logic outside the default/config fallback.

## Expiry service

Create `CheckoutRecoveryExpiryService`.

Each run receives current runtime config and now.

```text
cutoff = now - checkoutRecoveryLifetimeDays days
```

Scan only active statuses:

```text
DETECTED
MESSAGE_SENT
ENGAGED
```

ordered by `lastExternalActivityAt ASC, id ASC` in bounded pages. Use a bounded page size constant (100 in v1) and loop until fewer than page size or a safety bound appropriate to existing scheduler convention. Do not load the full table.

For each candidate, use a conditional transaction/update:

```text
WHERE id = candidate.id
  AND status still active
  AND lastExternalActivityAt <= current cutoff
```

If condition no longer matches, skip as raced activity.

On successful expiry:

```text
CheckoutRecovery.status = EXPIRED
expiredAt = now
CheckoutRecoveryStatusHistory: from previous -> EXPIRED
reason = "checkout-recovery-inactivity-expired"
source = "ARCH-016"
```

Also cancel durable pending `RecoveryOutreachAttempt` rows for the recovery:

```text
PENDING -> CANCELLED
WAITING_FOR_RESPONSE -> CANCELLED only if its proactive send has NOT already occurred;
```

If WAITING_FOR_RESPONSE already has `sentAt`, it is a historical sent attempt; do not rewrite it. Its scheduled future follow-up job must be suppressed by runtime revalidation.

## Expiry scheduler

In existing `src/entrypoints/recovery.ts`, add a second `startDynamicLeasedScheduler`:

```text
leaseName: CHECKOUT_RECOVERY_EXPIRY
interval: fixed 60 * 60 * 1000
runImmediately: true
```

It uses current runtime lifetime value but no configurable interval field.

Register stop/close resource consistently with existing repair scheduler.

## Race conditions

Required proofs:

```text
expiry reads stale row
checkout update advances lastExternalActivityAt
expiry conditional update -> count 0
recovery remains active
```

and:

```text
duplicate matured candidates after EXPIRED
same checkout lock + DB partial unique index
-> exactly one generation N+1
```

Late event timestamp older than current activity:

```text
max() preserves current newer value
```

## Required tests

- generation 1 initial materialisation;
- active generation prevents duplicate materialisation;
- EXPIRED generation schedules pending restart on checkout update;
- restart does not immediately create recovery;
- further activity reschedules pending candidate;
- matured restart creates generation +1;
- new generation gets a fresh Conversation only through normal send flow, not at expiry;
- COMPLETED does not restart;
- CANCELLED does not restart;
- checkout update advances lastExternalActivityAt monotonically;
- late checkout update timestamp cannot move it backwards;
- inbound customer message advances activity;
- outbound/agent message does not extend lifetime;
- 21-day default cutoff;
- runtime change to another allowed lifetime changes next scan result without row rewrite;
- race with activity does not expire;
- expiry writes status history;
- expiry scheduler uses new lease and existing recovery process;
- no new Render service.

## Validation

```text
npm test
npm run build
npm run prisma:validate
git diff --check
```

Run focused checkout/expiry/worker tests and report counts.

## Stop conditions

STOP if:

- solution proposes deleting CheckoutRecovery/Conversation history;
- solution proposes reopening an EXPIRED row instead of a new generation;
- solution restarts COMPLETED/CANCELLED recoveries;
- solution needs `Conversation @@unique` changed;
- solution uses `updatedAt` as expiry activity clock;
- solution creates one 3-week BullMQ delayed job per recovery instead of the agreed sweep.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.

## Completion Report

Status: Ready for Review

Implementation commit: `da4ccbb9c91d64ba1e9aa4c1e045569600116483` on
`task/ARCH-016-BACKGROUND-002`, pushed to
`origin/task/ARCH-016-BACKGROUND-002`.

Implemented the expiry service and hourly leased scheduler, bounded conditional
expiry/status-history writes, pending restart from EXPIRED checkout activity,
generation-aware materialisation, monotonic checkout and inbound customer
activity timestamps, runtime lifetime validation, and focused restart/expiry
coverage. The direct checkout-refresh test proves an EXPIRED recovery schedules a
pending restart without Shopify refresh or mutation of the expired row.

Validation:

- Focused expiry/restart/generation/runtime/activity suites: 6 files, 69 passed.
- Post-repair task-local compatibility suites: 3 files, 51 passed.
- `npm test`: 67 files passed, 10 skipped; 1,025 passed, 19 skipped, 5 failed.
  The remaining failures are unrelated translation integration/runtime setup
  failures: four translation enum tests require runtime configuration startup,
  and the translation batch concurrency assertion does not produce the expected
  batch assignment in the current local database state.
- `npm run build`: blocked by the pre-existing accepted-schema/client mismatch;
  existing background code references `transcriptionStatus` and `contentType`,
  neither of which exists in the accepted generated Prisma client. No unrelated
  source or schema workaround was made.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.

Database evidence: the implementation worktree database gitlink resolves to the
accepted ARCH-016-DATABASE-001 commit
`9eb25ade30c878f0bb7376c90f0396eb3e66df3c`; the database submodule is clean and
no schema files were changed by this task. The implementation branch is clean
after push. No SYSTEM-TEST-001 work was started and no architect acceptance
decision was made.
