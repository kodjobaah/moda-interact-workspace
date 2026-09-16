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
status: ready
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

## Architect Review — Attempt 1

### Status

**Changes Requested — preserve the implemented generation/expiry design; correct four bounded lifecycle/activity defects**

Implementation commit reviewed: `da4ccbb`.
Parent Completion Report commit reported: `31eabe3f`.

This review prioritises runtime correctness over exhaustive test count. The following
Attempt-1 implementation is accepted in principle and MUST NOT be redesigned in
Attempt 2:

```text
generation-aware latest-recovery lookup
EXPIRED -> PendingRecoveryCandidate -> generation N+1 restart flow
COMPLETED/CANCELLED permanent terminal behavior
bounded 100-row expiry scanning
current runtime checkoutRecoveryLifetimeDays cutoff
CHECKOUT_RECOVERY_EXPIRY hourly leased scheduler in moda-recovery-worker
conditional lastExternalActivityAt monotonic writes
pending/unsent outreach cancellation on expiry
no Conversation uniqueness change
no new Render service
```

Four corrections remain.

### Finding 1 — inbound WhatsApp activity uses processing/transcription time instead of the provider event time

The canonical WhatsApp event already provides `event.occurredAt`. Attempt 1 instead
advances recovery lifetime with `new Date()` inside `ConversationService.receiveMessage`
and with transcription-completion `new Date()` inside
`InboundWhatsAppAudioService.complete`.

That is functionally wrong for the ARCH-016 inactivity clock: queue lag or audio
transcription latency can extend a recovery beyond the customer's actual activity time.
It also means an inbound audio message that is rejected or terminally fails transcription
never advances recovery activity at all, even though the customer did send an inbound
message.

#### Required Attempt-2 correction

Keep the external-activity mutation in the task-authorised recovery/WhatsApp boundary.
Implement exactly this behavior:

1. In `src/services/checkout-recovery.service.ts`, add/reuse one repository-local method
   that records an external activity timestamp for a known recovery ID with one guarded
   monotonic update:

   ```text
   WHERE id = recoveryId
     AND status IN (DETECTED, MESSAGE_SENT, ENGAGED)
     AND lastExternalActivityAt < activityAt
   SET lastExternalActivityAt = activityAt
   ```

   The method MUST NOT change recovery status and MUST no-op for
   `EXPIRED`, `COMPLETED`, and `CANCELLED`.

2. In `src/workers/whatsapp.worker.ts`, immediately after routing has resolved the
   inbound event, when `route.kind === "resolved"`, call that method with:

   ```text
   recoveryId = route.checkoutRecoveryId
   activityAt = new Date(event.occurredAt)
   ```

   Do this before branching on text/audio/unsupported content so every successfully
   routed inbound customer message counts as activity even when audio transcription is
   rejected/fails or content is unsupported. Duplicate delivery is safe because the
   write is monotonic.

3. Remove the ARCH-016-specific `checkoutRecovery.lastExternalActivityAt` writes added
   by Attempt 1 to:

   ```text
   src/services/conversation.service.ts
   src/services/inbound-whatsapp-audio.service.ts
   ```

   Do not otherwise redesign those services or revert unrelated pre-existing behavior.
   These files were outside the authorised ARCH-016-BACKGROUND-002 write surface; the
   recovery activity clock belongs in the authorised worker/recovery-service path above.

### Finding 2 — a qualifying checkout update can be lost from the inactivity clock when Shopify refresh does not succeed

For an active recovery, Attempt 1 advances `lastExternalActivityAt` only after the
Shopify abandoned-checkout lookup returns `found` and the basket refresh update succeeds.
But ARCH-016 defines the checkout update's `activityAt` itself as qualifying external
activity. A `not-found`, `ambiguous`, bounded lookup outcome, or provider failure must not
silently erase the fact that a valid checkout-update event occurred.

#### Required Attempt-2 correction

In `handleCheckoutUpdatedContract`, after the latest recovery is known to be active and
before the provider lookup, call the same monotonic activity method with:

```text
recovery.id
event.activityAt
```

Then perform the existing provider lookup/content refresh independently. Required
semantics:

```text
newer checkout activity + provider found       -> activity advances; basket refreshes
newer checkout activity + provider not-found   -> activity advances; existing discard result remains
newer checkout activity + provider ambiguous   -> activity advances; existing discard result remains
newer checkout activity + provider error       -> activity advances; provider error remains retryable
older checkout activity                         -> activity does not move backwards
expiry wins before activity update              -> guarded activity update count 0; EXPIRED remains immutable
activity update wins before expiry              -> expiry cutoff predicate no longer matches
```

Do not use `updatedAt`, `detectedAt`, or provider-processing time as the replacement
activity clock.

### Finding 3 — expiry can be followed by an unconditional MESSAGE_SENT write, reopening an EXPIRED generation

`markRecoveryMessageSent()` still uses an unconditional Prisma `update` by ID. After
ARCH-016 introduces asynchronous expiry, this race is possible:

```text
recovery is DETECTED and a provider send is in flight
expiry sweep conditionally transitions DETECTED -> EXPIRED
provider flow returns
markRecoveryMessageSent(id)
current Attempt-1 code writes EXPIRED -> MESSAGE_SENT
```

That violates the architecture rule that an `EXPIRED` generation is immutable history
and only a later Shopify checkout update may create generation N+1.

#### Required Attempt-2 correction

Change `markRecoveryMessageSent()` to a guarded transition using `updateMany` (or an
equivalent conditional mutation) with:

```text
WHERE id = recoveryId
  AND status = DETECTED
```

Only a successful `DETECTED -> MESSAGE_SENT` transition may set:

```text
messageSentAt
admissionBlockedAt = null
admissionBlockReason = null
```

If the row is already `EXPIRED`, `COMPLETED`, `CANCELLED`, `MESSAGE_SENT`, or `ENGAGED`,
the method must not rewrite status. Do not reopen an expired row merely because a
provider call completed after the expiry race.

### Finding 4 — expiry history can record a stale fromStatus

`CheckoutRecoveryExpiryService` reads `candidate.status`, but its conditional update
currently allows *any* active status. If the row changes from (for example) `DETECTED`
to `MESSAGE_SENT` between the read and update, expiry can succeed while history is still
written as `DETECTED -> EXPIRED`.

#### Required Attempt-2 correction

Make the terminal update prove the same status that supplies the history row. The
smallest correction is:

```text
WHERE id = candidate.id
  AND status = candidate.status
  AND lastExternalActivityAt <= cutoff
```

where `candidate.status` was selected from the active-status query. If the status
changed, `count = 0`; write no history/outreach cancellation in that transaction and
allow a later sweep to reconsider the row. An equivalent transaction-local re-read is
acceptable only if it guarantees the history `fromStatus` is the actual status replaced
by that exact terminal update.

### Required focused validation for Attempt 2

Add/update only the tests needed to prove these functional corrections:

```text
1. routed text inbound uses event.occurredAt, not worker processing time
2. routed audio inbound advances activity even when transcription is rejected/terminally fails
3. older inbound occurredAt cannot move lastExternalActivityAt backwards
4. active checkout update advances activity even when provider lookup returns not-found
5. active checkout update advances activity before a retryable provider error is rethrown
6. expiry/activity race still leaves an activity-winner recovery active
7. markRecoveryMessageSent cannot change EXPIRED back to MESSAGE_SENT
8. expiry status race cannot write history with a stale fromStatus
```

Preserve the already-passing restart/generation/scheduler behavior. Do not expand this
into exhaustive unrelated test work.

Run the task's existing validation commands and focused suites. The pre-existing Prisma
schema/generated-client build mismatch may remain documented if observation is unchanged;
do not workaround an unrelated baseline inside this task.

### Completion Report / execution evidence

Attempt 1 states that both branches are clean/pushed and the user supplied dedicated
worktree execution. The task record, however, does not contain the mandatory prepared
launcher packet evidence required by the architect contract.

On Attempt 2, add the existing launcher-resolved evidence to the Completion Report:

```text
canonical primary workspace_root
dedicated parent task worktree + task/ARCH-016-BACKGROUND-002 branch
dedicated implementation worktree + task/ARCH-016-BACKGROUND-002 branch
start-of-attempt parent/implementation synchronization evidence
recursive implementation-submodule preparation evidence
Attempt-2 launcher claim commit
```

Do not manufacture a code change solely for execution evidence; source changes are
already required by Findings 1-4.

### Reclaim state

`ARCH-016-BACKGROUND-002` returns to:

```text
status: ready
attempt: 1
executor: null
claimed_at: null
```

The deterministic launcher owns the increment to Attempt 2 when the task is reclaimed.
`ARCH-016-SYSTEM-TEST-001` remains Pending and MUST NOT start automatically.
