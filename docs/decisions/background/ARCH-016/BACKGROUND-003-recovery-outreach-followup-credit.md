---
id: ARCH-016-BACKGROUND-003
architecture_id: ARCH-016
title: Implement chargeable recovery outreach attempts and one no-response follow-up
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 40
executor: copilot
claimed_at: 2026-09-16T16:49:47Z
attempt: 1
depends_on:
- ARCH-016-DATABASE-001
- ARCH-016-SHARED-001
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-016-BACKGROUND-003

## Objective

Refactor proactive recovery billing/send orchestration around durable `RecoveryOutreachAttempt` identity and implement exactly one merchant-configured no-response follow-up without changing the one-Conversation-per-Recovery invariant.

## Authorized implementation surface

```text
src/services/checkout-recovery.service.ts
src/services/recovery-billing.service.ts
src/services/free-recovery-reservation.service.ts
src/services/paid-included-recovery-reservation.service.ts
src/services/promotional-recovery-reservation.service.ts
src/services/purchased-recovery-reservation.service.ts only where sourceKey contract changes
src/services/recovery-outreach-attempt.service.ts             # new
src/services/recovery-policy.service.ts                       # new effective-policy resolver
src/services/outbound-whatsapp-admission.service.ts only to expose/link admitted message ID if needed
src/services/conversation.service.ts / whatsapp.worker.ts only for engagement marking
src/workers/recovery-outreach-follow-up.worker.ts              # new
src/entrypoints/recovery.ts                                    # register worker
src/entrypoints/resources.ts / queue resource files
focused tests
package.json/package-lock.json exact Shared version pin
```

Do not implement CommerceAgent AI discount selection.

## Effective policy snapshot

Before creating initial attempt #1 resolve effective policy:

```text
active unexpired ShopRecoveryPolicyOverride
  -> override complete snapshot
else
  -> ShopSettings
```

Validate FIXED reference against local catalogue at attempt creation time.

Snapshot on attempt:

```text
configuredOfferMode
fixedShopifyDiscountId when FIXED and currently usable
offerSnapshot when FIXED and usable
```

For `AI_BEST_APPLICABLE`:

```text
configuredOfferMode = AI_BEST_APPLICABLE
fixedShopifyDiscountId = null
offerSnapshot = null
```

Do not call AI.

If merchant configured FIXED but the discount has become unavailable/expired/catalogue non-CURRENT between configuration and send:

```text
fail soft for recovery messaging:
  create/send attempt with configuredOfferMode snapshot = FIXED
  fixedShopifyDiscountId may retain historical configured ID
  offerSnapshot = null and bounded failure/provenance metadata if schema permits
  send the normal recovery template without inventing a substitute discount
```

Do not suppress the entire recovery because an offer became stale.

## Attempt identity before billing

Create/reuse attempt before capacity admission so billing has a durable idempotency source.

Initial attempt:

```text
checkoutRecoveryId = recovery.id
sequence = 1
trigger = INITIAL
status = PENDING
```

Use unique `(checkoutRecoveryId, sequence)` as duplicate fence.

No-response follow-up:

```text
sequence = 2
trigger = NO_RESPONSE_FOLLOW_UP
```

V1 MUST NOT create sequence >2.

## Billing idempotency refactor

Current `RecoveryBillingService.admit({ shopId, recoveryId })` derives source from recovery identity. Refactor canonical admission input to include:

```text
shopId
recoveryId
outreachAttemptId
```

Reservation source key MUST be derived from attempt, for example canonical source string:

```text
recovery-outreach:<outreachAttemptId>
```

then pass through existing `createRecoveryIdempotencyKey(shopId, sourceKey)` reservation helpers.

Required result:

```text
attempt #1 -> one admission/credit
retry attempt #1 -> same admission, no second credit
attempt #2 -> different admission/credit
retry attempt #2 -> same admission, no second credit
```

Do not change which entitlement sources Free/Paid/promotional/purchased billing can choose. This task changes the source identity, not the allocation priority architecture.

Existing `CheckoutRecovery.admissionBlockedAt/admissionBlockReason` may remain as aggregate initial-recovery capacity state for backward compatibility. Attempt status is the new per-outreach truth.

## Initial send flow

Refactor existing `handleCheckoutCreated` send path into this exact ordering:

```text
upsert/create recovery generation          existing BACKGROUND-002-compatible behavior
resolve customer                           existing
if recovery not DETECTED                   no duplicate attempt
resolve effective policy
create/reuse attempt #1 PENDING
resolve recipient/template                 existing ARCH-012 path
admit billing by outreachAttemptId
get/create recovery Conversation            existing one Conversation
revalidate billing before provider          existing
send approved WhatsApp template             existing
link attempt.outboundMessageId to returned ConversationMessage id
commit billing                              existing
mark attempt WAITING_FOR_RESPONSE + sentAt
mark recovery MESSAGE_SENT                  existing behavior
if followUpEnabled schedule follow-up wake-up
```

If provider send fails:

```text
existing billing failure/release semantics
attempt FAILED with bounded failureCode
```

If capacity blocks:

```text
attempt CAPACITY_BLOCKED
initial recovery retains existing capacity-block/resume behavior
```

If initial capacity-resume later succeeds, it MUST reuse attempt #1; never create a second attempt/credit for the same initial outreach.

## Follow-up queue

Create dedicated queue/job following repository BullMQ conventions:

```text
queue: recovery-outreach-follow-up
job:   recovery-outreach-follow-up
jobId: recovery-outreach-follow-up:<checkoutRecoveryId>:2
```

Schedule after attempt #1 is successfully sent:

```text
dueAt = attempt1.sentAt + effectivePolicy.followUpDelayMinutes
```

Persist `attempt1.followUpDueAt = dueAt` as durable evidence of the scheduled no-response check.

If follow-up disabled, no job and `followUpDueAt = null`.

Policy is snapshotted for the scheduled follow-up at initial attempt creation. Subsequent merchant setting changes apply to future recovery generations/attempt scheduling, not rewrite already-scheduled outreach. An explicit admin/platform cancellation/checkout terminal event still suppresses at wake-up.

## Follow-up wake-up reconciliation

When job wakes, perform one durable reconciliation. Do not poll repeatedly.

Under a checkout/recovery-scoped lock or transaction:

Require:

```text
CheckoutRecovery status in DETECTED/MESSAGE_SENT/ENGAGED as appropriate
not COMPLETED/EXPIRED/CANCELLED
attempt #1 exists and sentAt != null
attempt #2 does not already exist as successfully sent
followUpDueAt <= now
no customer engagement after attempt1.sentAt
shop execution eligibility allowed
```

Customer engagement test MUST use durable conversation/recovery state, not only job payload.

If customer has responded:

```text
attempt1 -> ENGAGED if not already
customerRespondedAt set monotonically to first qualifying inbound timestamp
no attempt2
job completes suppressed
```

If no response:

1. mark attempt1 `NO_RESPONSE` if still WAITING;
2. create/reuse attempt2 `PENDING`;
3. resolve current execution/shop state;
4. admit a new recovery credit using attempt2 identity;
5. if blocked -> attempt2 `CAPACITY_BLOCKED`, do NOT send, no automatic capacity-resume for v1 follow-up;
6. send through the existing approved template path using same existing Conversation;
7. link outbound message ID;
8. commit billing;
9. mark attempt2 `WAITING_FOR_RESPONSE`, `sentAt`.

Do not schedule attempt #3 in ARCH-016.

## Conversation invariant

Never call a "create new Conversation for follow-up" path.

For every attempt of one recovery generation use:

```text
conversationService.getOrCreateRecoveryConversation(recovery.id, ...)
```

which must continue returning the existing Conversation after attempt #1.

Do not add `conversationId` to RecoveryOutreachAttempt when it can be reached through CheckoutRecovery. The explicit proactive message link is enough.

## Inbound engagement

When inbound WhatsApp processing resolves a recovery Conversation:

1. find latest attempt for recovery with `status = WAITING_FOR_RESPONSE`, highest sequence;
2. if one exists and inbound timestamp >= attempt.sentAt, atomically mark:

```text
status = ENGAGED
customerRespondedAt = first inbound timestamp
closedAt optional only if consistent with status design
```

3. suppress/no-op the scheduled no-response follow-up when it later wakes.

If inbound `inReplyToProviderId` explicitly points to attempt #1's outbound message after attempt #2 was sent, preserve that reply context on ConversationMessage, but customer engagement still means the recovery conversation is engaged and no further no-response follow-up is authorized in v1.

Ordinary outbound agent responses do not create RecoveryOutreachAttempt rows and do not consume recovery credits.

## Meta 24-hour boundary

Do not add Moda billing conditions based on 24 hours.

ARCH-012/provider transport policy remains responsible for whether a free-form or approved template send is permitted. This task's proactive follow-up uses the existing approved-template path.

## Offer application boundary

For FIXED, persist/snapshot the selected offer facts. Do not invent Meta template parameter mappings. If the current approved template contract does not explicitly support offer parameters, send the existing base recovery template and preserve the offer snapshot for downstream recovery context.

For AI_BEST_APPLICABLE, do not select any discount in this task.

## Required tests

Billing/idempotency:

- initial attempt consumes exactly one credit;
- initial retry does not consume second credit;
- no-response follow-up consumes second credit;
- follow-up retry does not consume third credit;
- customer/agent continuation messages consume no new recovery credit;
- all existing Free/Paid/promotional/purchased allocation paths still work with attempt source key.

Conversation:

- attempts #1 and #2 use same Conversation ID;
- no change to `Conversation @@unique([checkoutRecoveryId])` behavior;
- proactive outbound message ID linked to correct attempt.

Follow-up:

- disabled => no job;
- due time from attempt1.sentAt + configured delay;
- customer reply before due => no attempt2/no credit;
- no reply => attempt2/new credit/send;
- <24h no reply still consumes new credit;
- >=24h no reply consumes new credit;
- completed/cancelled/expired before due suppresses;
- shop unavailable suppresses;
- no capacity => CAPACITY_BLOCKED, no send;
- exactly one follow-up; no sequence 3.

Offers:

- NONE snapshot;
- valid FIXED snapshot;
- fixed offer expired before send => recovery still proceeds without substituting another discount;
- AI mode persists/snapshots mode and performs zero LLM/CommerceAgent calls.

## Validation

```text
npm test
npm run build
npm run prisma:validate
git diff --check
```

Run focused checkout, billing, reservation, outbound admission, WhatsApp worker and new follow-up worker tests.

## Stop conditions

STOP if:

- implementation requires changing Conversation identity/creating a new Conversation per attempt;
- implementation charges a credit for ordinary customer/agent continuation messages;
- implementation treats `<24h` no-response follow-up as free;
- implementation creates sequence 3+;
- implementation performs AI discount selection;
- implementation invents a WhatsApp template variable contract;
- per-attempt billing cannot remain idempotent across retries.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
