---
id: ARCH-007-BACKGROUND-010
architecture_id: ARCH-007
title: Coalesce fragmented inbound WhatsApp messages into one CommerceAgent turn
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 68
executor: null
claimed_at: null
attempt: 4
depends_on:
  - ARCH-007-DATABASE-006
  - ARCH-007-BACKGROUND-004
enables:
  - ARCH-007-BACKGROUND-011
  - ARCH-007-SYSTEM-TEST-005
created: 2026-09-08
updated: 2026-09-08
---
# ARCH-007-BACKGROUND-010: Coalesce fragmented inbound WhatsApp messages into one CommerceAgent turn

## Non-negotiable product behavior

Never use:
```text
1 inbound WhatsApp message = 1 CommerceAgent call = 1 outbound reply
```

Every raw inbound message admitted to this task is still accepted, deduplicated and persisted.

BACKGROUND-011 exception: after BACKGROUND-010 is Complete, the later abuse-admission task may suppress a raw event before ConversationMessage persistence when the explicit raw sender/global abuse gate denies it. BACKGROUND-010 itself must not implement that gate.

Nearby fragments from the same durable conversation are settled into ONE logical processing turn.

Initial constants are EXACTLY:

```text
QUIET_WINDOW_MS = 3000
MAX_SETTLE_WINDOW_MS = 10000
PROCESSING_LEASE_MS = 120000
```

Do not make these environment variables in this task.

## Existing architecture to preserve

- Messaging ingress continues publishing each verified inbound WhatsApp message individually.
- Background resolves stable durable conversation identity (including DATABASE-004/BACKGROUND-004 standalone conversations).
- `ConversationService.receiveMessage` remains providerMessageId-idempotent.
- `inboundVersion` increments once per newly persisted inbound message.
- customer inbound messages do NOT increment `OUTBOUND_AUTOMATED_MESSAGE`.
- outbound normal capacity is reserved BEFORE CommerceAgent execution.

No Messaging or Shared contract change is required.

## Exact receive path

For each `message-received` job:

1. resolve its stable conversation using the accepted routing lifecycle;
2. call `ConversationService.receiveMessage`;
3. duplicate -> return with NO new turn job;
4. for a newly persisted message, use one `now` timestamp for message `createdAt`, `lastInboundAt`, `lastMessageAt`;
5. if this was the first unprocessed inbound (`old inboundVersion == lastProcessedVersion`), set `pendingTurnStartedAt=now`;
6. increment `inboundVersion`;
7. DO NOT call CommerceAgent in the raw message job;
8. enqueue an INTERNAL delayed job on the existing `whatsapp-events` queue:
   ```text
   name = process-conversation-turn
   data = { conversationId, observedVersion }
   jobId = conversation-turn__<conversationId>__<observedVersion>
   ```
9. delay is:
   ```text
   min(
     pendingTurnStartedAt + 10000 - now,
     lastInboundAt + 3000 - now
   )
   ```
   bounded at minimum 0.

The external Messaging producer never emits `process-conversation-turn`; it is Background-internal.

Update worker metric job-name allowlist to include this internal job.

## Exact turn-job stale rules

When `process-conversation-turn` executes:

Read:
```text
inboundVersion
lastProcessedVersion
lastInboundAt
pendingTurnStartedAt
processingInboundVersion
processingStartedAt
```

No-op if:
- `observedVersion < inboundVersion` (a newer job exists);
- `observedVersion <= lastProcessedVersion`;
- `pendingTurnStartedAt` is null.

If current time is still before BOTH:
```text
lastInboundAt + 3000
pendingTurnStartedAt + 10000
```
then reschedule the same observed version for the earlier of those two deadlines and return.

## Conversation-scoped processing lease

Claim via conditional Prisma `updateMany`.

A claim succeeds only when:
- conversation still has expected `inboundVersion=observedVersion`;
- `lastProcessedVersion < observedVersion`;
- no live processor exists.

A processor is stale only when:
```text
processingStartedAt < now - 120000ms
```

On successful claim set:
```text
processingInboundVersion = observedVersion
processingStartedAt = now
```

If another live processor owns the conversation, do NOT run CommerceAgent. Return/reschedule a short retry through the existing queue mechanism.

Never serialize different conversations globally.

## Assemble one customer turn

Use `pendingTurnStartedAt` to query persisted INBOUND/CUSTOMER messages for this conversation with:
```text
createdAt >= pendingTurnStartedAt
```
ordered ascending.

Keep individual messages separately in DB.

For language detection / turn text, join their content in order with newline:
```text
message1 + "\n" + message2 + ...
```

The CommerceAgent snapshot may continue to use bounded conversation history, but it must see all currently retained fragment messages in their persisted order.

Do not concatenate/overwrite stored ConversationMessage rows.

## Admission before AI

After claim and before `runCommerceAgent()`:

```text
reserve normal OUTBOUND_AUTOMATED_MESSAGE slot for conversation
```

If normal slot unavailable:
- DO NOT call CommerceAgent/LLM/tools;
- let accepted BACKGROUND-004 terminal-slot behavior send at most one deterministic terminal reply;
- mark the current inbound version processed/terminally handled as appropriate;
- release processing lease.

If terminal slot already used:
- suppress;
- no CommerceAgent;
- no WhatsApp provider call;
- mark current inbound version handled;
- release processing lease.

## New inbound while agent is running

A newly arriving raw message is persisted and increments `inboundVersion`, but its turn job must not run CommerceAgent while the processing lease is live.

After agent returns, check `hasChanged(conversationId, observedVersion)`.

If changed:
- DO NOT send stale agent response;
- release/fail the prepared outbound reservation according to accepted admission semantics;
- clear processing lease;
- DO NOT advance `lastProcessedVersion`;
- keep `pendingTurnStartedAt`;
- ensure the newest inbound version has/gets a delayed turn job.

If unchanged and send succeeds:
- set `lastProcessedVersion=observedVersion`;
- clear `pendingTurnStartedAt`;
- clear processing fields.

If send/agent throws:
- preserve existing definitive/ambiguous provider behavior;
- clear/recover processing lease so queue retry can continue safely.

## Required regression scenarios

1. fragments `"Hi I was looking at"`, `"the black jacket"`, `"sorry I mean blue"` arriving within 3 seconds:
   - 3 persisted inbound messages;
   - one settled turn;
   - one CommerceAgent call;
   - one outbound reservation;
   - one outbound response.
2. two messages >3 seconds apart create two turns.
3. continuous fragments every <3 seconds cannot postpone processing beyond 10 seconds from first unprocessed fragment.
4. duplicate providerMessageId creates no extra version/job/agent call.
5. stale version job no-ops when newer version exists.
6. two workers racing same conversation produce one processor/one agent call.
7. different conversations may process concurrently.
8. message arriving during agent execution prevents stale response send and is processed in the next settled turn.
9. outbound normal cap exhausted -> zero CommerceAgent calls and only accepted terminal behavior.
10. customer inbound messages never create `OUTBOUND_AUTOMATED_MESSAGE` usage themselves.
11. product-only stable standalone conversation fragments coalesce.
12. recovery conversation fragments coalesce.
13. clarification/support standalone conversation fragments coalesce.
14. processing lease older than 120s can be reclaimed; a live lease cannot.
15. raw messages remain individually stored and ordered; no content is lost by coalescing.

## Explicitly out of scope

- dropping/throttling authenticated inbound webhooks;
- adding an inbound billing metric;
- charging merchants per inbound fragment;
- changing Meta ingress validation;
- global conversation serialization;
- a new queue/service deployment.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Do not run `git commit` or `git push`.

## Completion Report

### Status
Ready for Review (Attempt 4)

### Files Changed
- `moda-interact-background/src/services/conversation.service.ts`
- `moda-interact-background/src/services/recovery-routing.service.ts`
- `moda-interact-background/src/services/conversation-turn-processor.service.ts`
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/src/workers/whatsapp.worker.ts`
- `moda-interact-background/tests/unit/services/conversation.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-routing.service.test.ts`
- `moda-interact-background/tests/unit/services/checkout-refresh.test.ts`
- `moda-interact-background/tests/unit/services/conversation-turn-processor.service.test.ts`

### Work Completed
- Preserved the exact 3-second quiet window, 10-second maximum settle window, 120-second processing lease, stale-version no-ops, and changed deterministic queue IDs to the architect-corrected BullMQ-safe `conversation-turn__<conversationId>__<observedVersion>` form.
- Made first-unprocessed `pendingTurnStartedAt` initialization conditional inside the receipt transaction and added deterministic `(createdAt, id)` fragment ordering.
- Extracted the settled-turn processor and integrated it with the existing `whatsapp-events` worker; active jobs use BullMQ `moveToDelayed()` with the worker lock token for same-version resettles.
- Preserved provider ambiguity semantics by tracking provider-send ownership and avoiding an outer `failPrepared` after a provider attempt.
- Reconstructed current same-owner recovery candidates at settled-turn time and sent one deterministic clarification through outbound admission without invoking CommerceAgent.
- Kept normal outbound admission before CommerceAgent, terminal-cap handling without CommerceAgent, stale-response suppression, lease release, and newest-version scheduling.
- Added the focused processor regression suite covering all 15 required scenarios plus provider ambiguity, concurrent first-fragment CAS behavior, and repeated early scheduling.
- Replaced active-job `changeDelay()` with BullMQ `moveToDelayed(timestamp, token)` followed by `DelayedError`, preserving the deterministic job ID and preventing active-job completion.
- Made settled clarification reconstruction discriminated: zero candidates uses standalone support, one uses the current recovery, two through ten use deterministic clarification, and overflow or mixed ownership fails closed without CommerceAgent or provider send.
- Added a standalone clarification context helper that combines the current recovery's shop/customer/recovery state with the standalone conversation's settled fragments and language snapshot; resolved candidates now require ownership to match the durable clarification conversation.
- Added persisted duplicate-provider and three-fragment clarification harnesses, current-routing overflow/resolution regressions, deterministic recovery ordering coverage, and definitive-provider cleanup coverage.
- Added focused regressions for the exact no-colon job ID, resolved clarification context at the processor boundary, and mismatched clarification ownership fail-closed behavior.

### Validation Results
- `npm run build`: passed, including Prisma generation and strict TypeScript compilation.
- `npm run prisma:validate`: passed.
- Focused Attempt 4 processor, routing, recovery-context, and outbound-admission suites: 64 passed.
- Full unit suite: 359 passed, 7 skipped; 2 unrelated existing failures remain in `tests/unit/services/pending-recovery-candidate.service.test.ts`.
- Editor diagnostics for changed source files: no errors.
- Strict typecheck via `npm run build`, targeted Prettier check, and `git diff --check`: passed.

### Deviations
- No live Redis/PostgreSQL worker integration run was available in this validation pass; BullMQ active deferral is covered through the `moveToDelayed`/token/`DelayedError` seam, with durable queue/DB behavior covered by service tests and Prisma/type validation.

### Assumptions
- The existing `whatsapp-events` queue may carry both external `message-received` jobs and Background-internal `process-conversation-turn` jobs.

### Unresolved Issues
- The two unrelated pending-recovery candidate baseline failures remain.
- No commit or push was performed; this Attempt 4 task follows the legacy pre-feature-branch workflow and is returned for architect review.

### Architectural Concerns
No additional architectural concerns identified. Attempt 4 addresses the latest BullMQ identifier correction and resolved-clarification ownership/context corrections within the existing queue, durable state, and admission boundaries.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 4 is architect-accepted Complete.

The two final Attempt 3 corrections are implemented correctly.

#### BullMQ-safe deterministic turn job id

The original architect task contract was corrected in Attempt 3 because BullMQ
custom job ids must not contain `:`.

The implementation now consistently uses:

```text
conversation-turn__<conversationId>__<observedVersion>
```

for:

- initial delayed `process-conversation-turn` scheduling;
- active-job identity comparison;
- live-lease/early-execution resettling;
- deterministic duplicate logical job coverage.

The implementation contains no remaining colon-delimited B010 turn job id.

Active resettling continues to use BullMQ's supported pattern:

```text
job.moveToDelayed(timestamp, token)
throw new DelayedError()
```

so the Worker does not subsequently complete/fail the moved job.

#### Resolved clarification context

When a durable PRODUCT_SUPPORT clarification conversation now resolves to one
current recovery, the worker no longer pretends that the standalone
clarification Conversation belongs to that CheckoutRecovery.

`getAgentContextForStandaloneConversation()` correctly combines:

```text
current recovery:
  recovery id/status/checkoutToken/completedAt/totalPrice
  current shop
  current customer

with:

standalone clarification conversation:
  conversation id
  type
  language snapshot
  summary/version
  individually persisted settled inbound fragments
```

The outbound turn therefore uses the current resolved recovery state while
preserving the customer's coalesced clarification fragments.

#### Tenant ownership safety

Current clarification candidates must now match the durable clarification
conversation's:

```text
shopId
customerId
```

in addition to agreeing with one another.

Therefore:

```text
durable clarification: shop-A/customer-A
current candidate:      shop-B/customer-B
```

fails closed as `unresolved` with:

```text
zero CommerceAgent work
zero provider send
```

The previously accepted routing behavior is retained:

```text
0 candidates
  -> standalone support

1 matching-owner candidate
  -> resolved current recovery context

2..10 matching-owner candidates
  -> one deterministic clarification
  -> zero CommerceAgent

11-row overflow
  -> unresolved / fail closed

mixed ownership
  -> unresolved / fail closed
```

### Accepted B010 architecture

The complete accepted capability now provides:

- every raw inbound message persisted individually;
- providerMessageId dedupe;
- exact 3-second quiet window;
- exact 10-second maximum settle window;
- exact 120-second processing lease;
- first-unprocessed `pendingTurnStartedAt` established conditionally;
- deterministic job id per conversation/version;
- one processor lease per conversation;
- concurrent processing across different conversations;
- active BullMQ resettling without duplicate logical jobs;
- deterministic `(createdAt, id)` retained-fragment ordering;
- recovery and standalone fragment coalescing;
- same-owner multi-recovery clarification without CommerceAgent;
- cross-owner/overflow fail-closed routing;
- outbound admission before CommerceAgent;
- zero CommerceAgent when normal outbound capacity is exhausted;
- stale response suppression when a newer inbound arrives during agent work;
- provider ambiguity preserved by leaving provider-send classification in the
  accepted outbound-admission service;
- no inbound merchant billing metric;
- no new queue, worker service, database table or Shared contract.

### Pre-feature-branch workflow exception

The developer explicitly requested that ADMIN-001 and BACKGROUND-010 be fully
architect-accepted before switching to the mirrored feature-branch workflow.

BACKGROUND-010 Attempt 4 was therefore correctly completed with:

```text
no task feature branch
no commit
no push
```

This is accepted as the final legacy-workflow implementation task.

`ARCH-007-ADMIN-001` Attempt 2 is already architect-accepted Complete.

Therefore the transition gate is now satisfied:

```text
ADMIN-001 Complete
BACKGROUND-010 Complete
        ↓
new mirrored feature-branch workflow may now be enabled
```

Do not reopen B010 merely to manufacture feature-branch history.

### Reviewed Files

- `moda-interact-background/src/services/conversation-turn-processor.service.ts`
- `moda-interact-background/src/services/conversation.service.ts`
- `moda-interact-background/src/services/recovery-routing.service.ts`
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/src/workers/whatsapp.worker.ts`
- `moda-interact-background/tests/unit/services/conversation-turn-processor.service.test.ts`
- `moda-interact-background/tests/unit/services/conversation.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-routing.service.test.ts`
- `moda-interact-background/tests/unit/services/checkout-refresh.test.ts`
- accepted BACKGROUND-004 outbound-admission behavior
- `docs/decisions/background/ARCH-007/BACKGROUND-010-coalesce-inbound-whatsapp-turns.md`

### Validation Reviewed

Repository-agent Completion Report records:

```text
focused Attempt 4 suites: 64 passed
build: passed
typecheck: passed
Prisma validation: passed
formatting: passed
git diff --check: passed
full suite: 359 passed, 7 skipped
2 unrelated baseline pending-recovery-candidate failures remain unchanged
```

Architect comparison against Attempt 3 verified that Attempt 4 is bounded to:

- BullMQ-safe turn job ids;
- resolved standalone/recovery context composition;
- durable-owner matching;
- focused regressions for those corrections.

Architect static inspection verified:

- no colon-delimited B010 custom job id remains in implementation/tests;
- `moveToDelayed(..., token)` + `DelayedError` is retained;
- the resolved context uses the current recovery plus standalone settled
  fragments;
- mismatched durable/current ownership fails closed.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-BACKGROUND-010` is Complete.

`ARCH-007-BACKGROUND-011` is now Ready because its only dependency is Complete:

```text
ARCH-007-BACKGROUND-010 Complete
```

`ARCH-007-SYSTEM-TEST-005` remains Pending/manual-gated because B011 is not yet
Complete.

The developer may now apply/enable the new mirrored task feature-branch
workflow. The next newly claimed task should follow that workflow.
