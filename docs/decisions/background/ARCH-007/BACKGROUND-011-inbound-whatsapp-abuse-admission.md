---
id: ARCH-007-BACKGROUND-011
architecture_id: ARCH-007
title: Add inbound WhatsApp abuse admission before routing and CommerceAgent work
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: in_progress
priority: 69
executor: copilot
claimed_at: 2026-09-08T16:40:50Z
attempt: 1
depends_on:
  - ARCH-007-BACKGROUND-010
enables:
  - ARCH-007-SYSTEM-TEST-005
created: 2026-09-08
updated: 2026-09-08T16:40:50Z
---
# ARCH-007-BACKGROUND-011: Add inbound WhatsApp abuse admission before routing and CommerceAgent work

## Why this task exists

Moda uses one public WhatsApp number across many merchants.

The accepted `ambiguous-tenant` routing rule protects tenant correctness, but it does NOT protect against abuse from:

- an unknown/random sender repeatedly messaging the public number;
- one valid known customer repeatedly generating settled turns;
- many senders targeting one merchant;
- many senders across merchants creating application-layer load.

This task adds operational abuse admission. It is NOT merchant billing.

Never add:

```text
INBOUND_CUSTOMER_MESSAGE
COMMERCE_AGENT_TURN
INBOUND_AUTOMATED_MESSAGE
```

to merchant-billable usage metrics in this task.

## Non-negotiable architecture

There are TWO different admission stages.

```text
Meta-signed message-received job
        |
        v
RAW INGRESS ABUSE ADMISSION
(sender + global)
        |
        +-- denied -> acknowledge/suppress cheaply
        |             no tenant lookup
        |             no ConversationMessage persistence
        |             no turn job
        |             no AI
        |             no WhatsApp provider call
        |
        v
accepted raw event
        |
        v
accepted BACKGROUND-004/BACKGROUND-010
routing + dedupe + durable per-message persistence
        |
        v
3s quiet / 10s max settled logical turn
        |
        v
SETTLED-TURN ABUSE ADMISSION
(sender + conversation + shop + global)
        |
        +-- denied -> persisted messages remain
        |             mark observed inboundVersion handled
        |             clear turn processing/pending state
        |             no outbound reservation
        |             no AI/tools
        |             no WhatsApp provider call
        |
        v
accepted turn
        |
        v
accepted BACKGROUND-004 outbound admission
        |
        v
CommerceAgent / provider
```

`authenticated Meta webhook` does NOT mean `authorised to consume AI/provider resources`.

## Existing architecture to preserve

- Messaging remains responsible for Meta webhook verification and canonical inbound contract publication.
- Background does not reimplement Meta signature verification.
- `providerMessageId` remains the durable inbound idempotency identity.
- BACKGROUND-004 remains the tenant-safe outbound boundary.
- BACKGROUND-010 remains the owner of:
  - 3-second quiet window;
  - 10-second maximum settle window;
  - 120-second conversation processing lease;
  - one live agent processor per conversation;
  - stale-response suppression.
- Unknown/ambiguous tenant routing remains fail closed.
- Customer inbound traffic does not consume `OUTBOUND_AUTOMATED_MESSAGE`.
- No new database migration is required by this task.
- No Shared contract change is required by this task.
- No new queue/service deployment is required.

## Exact initial limits

These are initial safety constants for this task. Do NOT make them environment variables in this task.

### Raw ingress limits

Count raw canonical `message-received` events using `providerMessageId` as the idempotent member.

```text
RAW_SENDER_WINDOW_MS = 60_000
RAW_SENDER_LIMIT = 60

RAW_GLOBAL_WINDOW_MS = 60_000
RAW_GLOBAL_LIMIT = 20_000
```

Meaning:

```text
one sender >60 raw messages in rolling 60s -> raw deny
all senders >20,000 raw messages in rolling 60s -> raw deny
```

The raw sender identity is the normalized `event.customerPhone`, hashed before it is used in Redis keys or abuse logs.

### Settled-turn standard limits

For recovery conversations, PRODUCT_SUPPORT, and context-bound replies:

```text
TURN_SENDER_SHORT_WINDOW_MS = 60_000
TURN_SENDER_SHORT_LIMIT = 12

TURN_SENDER_LONG_WINDOW_MS = 600_000
TURN_SENDER_LONG_LIMIT = 60

TURN_CONVERSATION_SHORT_WINDOW_MS = 60_000
TURN_CONVERSATION_SHORT_LIMIT = 12

TURN_CONVERSATION_LONG_WINDOW_MS = 600_000
TURN_CONVERSATION_LONG_LIMIT = 60

TURN_SHOP_WINDOW_MS = 60_000
TURN_SHOP_LIMIT = 600

TURN_GLOBAL_WINDOW_MS = 60_000
TURN_GLOBAL_LIMIT = 5_000
```

### Standalone PRODUCT_DISCOVERY limits

A PRODUCT_DISCOVERY settled turn that has no fragment with `inReplyToProviderId` uses the lower sender/conversation limits:

```text
DISCOVERY_SENDER_SHORT_LIMIT = 4
DISCOVERY_SENDER_LONG_LIMIT = 12

DISCOVERY_CONVERSATION_SHORT_LIMIT = 4
DISCOVERY_CONVERSATION_LONG_LIMIT = 12
```

It still uses the same shop/global limits.

If any fragment in the settled PRODUCT_DISCOVERY turn has a non-null `inReplyToProviderId`, use the standard settled-turn limits.

Do not add heuristic scoring, IP reputation, CAPTCHA, ML abuse classification or phone-country rules in this task.

## Redis algorithm — atomic sliding windows

Use the existing `connectionRedis`. Do not create a second Redis connection solely for this feature.

Implement a service equivalent in responsibility to:

```text
src/services/inbound-whatsapp-abuse-admission.service.ts
```

Use one atomic Redis Lua/EVAL operation per admission decision.

For each configured scope/window:

1. remove members with score `< redisNow - windowMs`;
2. if the current idempotency member is already present, treat that scope as already admitted and do not count it twice;
3. otherwise read current cardinality;
4. if any required scope is already at its limit, reject the entire decision and add the member to NONE of the scopes;
5. if every scope has capacity, add the member to ALL required scopes with score `redisNow`;
6. set bounded expiry on touched keys.

Use Redis server time inside the Lua script. Do not use worker wall-clock time to define the rolling-window boundary.

### Required idempotency members

Raw stage:

```text
member = providerMessageId
```

Settled-turn stage:

```text
member = conversationId + ":" + observedVersion
```

A BullMQ retry/replay of the same raw event or same settled turn must not consume abuse capacity twice.

## Redis key privacy

Do not put raw phone numbers or message content in Redis keys.

Use:

```text
sha256(normalizedCustomerPhone)
```

for the sender component.

Example namespaces may be equivalent to:

```text
arch007:wa-abuse:v1:raw:sender:<senderHash>:60s
arch007:wa-abuse:v1:raw:global:60s

arch007:wa-abuse:v1:turn:sender:<senderHash>:60s
arch007:wa-abuse:v1:turn:sender:<senderHash>:600s
arch007:wa-abuse:v1:turn:conversation:<conversationId>:60s
arch007:wa-abuse:v1:turn:conversation:<conversationId>:600s
arch007:wa-abuse:v1:turn:shop:<shopId>:60s
arch007:wa-abuse:v1:turn:global:60s
```

The exact namespace string is local implementation detail, but it must be versioned and collision-safe.

## Raw ingress integration point

In the BACKGROUND-010 `message-received` path, run raw abuse admission:

```text
BEFORE recoveryRoutingService.resolveInboundMessage()
BEFORE any Prisma tenant/customer/conversation lookup
BEFORE ConversationService.receiveMessage()
```

Input:

```text
providerMessageId
customerPhone
```

If denied, return successfully from the job and perform NONE of:

```text
tenant lookup
ConversationMessage persistence
process-conversation-turn enqueue
CommerceAgent
outbound reservation
WhatsApp provider call
```

This is an intentional exception to BACKGROUND-010's normal "persist every raw inbound" rule: only raw events denied by this abuse gate may be suppressed before ConversationMessage persistence.

Do not throw/retry a denied abuse event.

## Settled-turn integration point

Run settled-turn admission in `process-conversation-turn` only AFTER:

1. the conversation-scoped processing lease has been successfully claimed;
2. the current persisted fragment set for the settled turn has been assembled;
3. durable conversation ownership (`shopId`, `customerId`) is known;

and BEFORE:

```text
outboundWhatsAppAdmissionService.reserve(...)
runCommerceAgent(...)
language/tool execution
```

Required inputs:

```text
conversationId
observedVersion
shopId
normalized customer phone
conversation type
checkoutRecoveryId presence
settled fragment inReplyToProviderId values
```

If denied:

```text
- do not reserve OUTBOUND_AUTOMATED_MESSAGE;
- do not invoke CommerceAgent/LLM/tools;
- do not call WhatsApp provider;
- advance lastProcessedVersion to observedVersion using the accepted conditional/version-safe path;
- clear pendingTurnStartedAt for that handled version;
- clear processingInboundVersion / processingStartedAt;
- retain the individual persisted inbound ConversationMessage rows;
- return successfully.
```

A throttled settled turn is intentionally handled/suppressed, not rescheduled after the rate-limit window.

A later new inbound version may be admitted normally after the rolling window has capacity.

## Limiter failure behavior

If the abuse-admission Redis operation itself fails unexpectedly:

### Raw stage

Fail closed for application work:

```text
no routing
no DB message persistence
no turn enqueue
no AI/provider
```

Return successfully from the business handler after bounded error telemetry. Do not create a retry storm.

### Settled-turn stage

Fail closed for expensive work:

```text
no outbound reservation
no AI/provider
```

Use the same handled-version cleanup as an abuse denial so the turn does not retry forever.

This task prioritises cost/isolation safety over attempting AI work when its abuse gate cannot make a decision.

Do not alter worker Redis readiness requirements.

## Decision result

Use a Background-local bounded result equivalent to:

```ts
type InboundAbuseAdmission =
  | { kind: "allowed" }
  | {
      kind: "denied";
      stage: "raw" | "settled-turn";
      reason:
        | "RAW_SENDER"
        | "RAW_GLOBAL"
        | "TURN_SENDER_SHORT"
        | "TURN_SENDER_LONG"
        | "TURN_CONVERSATION_SHORT"
        | "TURN_CONVERSATION_LONG"
        | "TURN_SHOP"
        | "TURN_GLOBAL"
        | "LIMITER_UNAVAILABLE";
    };
```

Do not publish it through `@modainteract/moda-interact-shared`.

## Observability

Emit bounded operational telemetry for:

```text
raw admission allowed/denied
settled-turn admission allowed/denied
denial stage
denial reason/scope
```

Allowed dimensions:

```text
stage
reason
conversation type
recovery-linked yes/no
```

Do NOT emit customer phone, message body, provider access token, or raw Redis key.

A hashed sender identifier may be used only in structured diagnostic logs when necessary for correlation; it must not be a high-cardinality metric label.

## Required regression scenarios

### Raw stage

1. 60 distinct raw providerMessageIds for one sender inside 60s are allowed; the 61st is denied.
2. replay of an already-counted providerMessageId does not consume another slot.
3. raw sender denial occurs before any Prisma/routing call.
4. raw global limit denies traffic even when each sender is individually below 60/min.
5. raw denial performs no ConversationMessage persistence, no turn enqueue, no agent and no provider call.
6. raw limiter infrastructure failure fails closed without a BullMQ retry storm.
7. Redis keys/logs do not contain the raw phone number.

### Settled-turn stage

8. 12 standard settled turns/min for one sender/conversation are allowed; 13th is denied.
9. long-window sender/conversation limit rejects sustained traffic even when the short window has reopened.
10. PRODUCT_DISCOVERY with no reply context uses 4/min and 12/10m limits.
11. PRODUCT_DISCOVERY with an `inReplyToProviderId` fragment uses standard limits.
12. many senders under sender limits can still trip the 600/min shop limit.
13. traffic across shops can trip the 5,000/min global settled-turn limit.
14. one sender using multiple conversations is still bounded by sender scope.
15. one conversation cannot evade its limit by BullMQ retry/replay of the same `observedVersion`.
16. denied settled turn keeps persisted fragments, marks the observed version handled, clears processing/pending state, creates zero outbound reservation, invokes CommerceAgent zero times, and invokes provider zero times.
17. a later new turn after window expiry can be admitted.
18. limiter infrastructure failure at settled-turn stage fails closed and clears the processing lease/version state safely.

### Concurrency / atomicity

19. two workers racing for the final slot cannot both be admitted.
20. a rejected multi-scope decision increments NONE of its scope windows.
21. retries of the same idempotency member remain idempotent across all scopes.

Use a real disposable Redis integration test if this repository already has a supported Redis test harness. If not, unit-test the Lua contract using current project conventions. Do not introduce Docker/Testcontainers solely for this task.

## Explicitly out of scope

- merchant billing for inbound messages or agent turns;
- a new Shared usage metric;
- changing Meta webhook verification;
- blocking a WhatsApp account at Meta;
- network/firewall/WAF DDoS mitigation outside the application;
- persistent database abuse-history tables;
- Admin UI for changing abuse thresholds;
- environment-variable tuning of the initial thresholds;
- reputation scoring / country rules / CAPTCHA;
- adding another worker service;
- changing BACKGROUND-004 outbound cap semantics;
- changing BACKGROUND-010 quiet/max-settle/lease constants.

## Expected implementation surface

Inspect current code first. Expected files include:

```text
src/services/inbound-whatsapp-abuse-admission.service.ts        NEW
src/workers/whatsapp.worker.ts
src/lib/redis.ts                                                inspect/reuse
src/observability/worker-metrics.ts                             only if needed
tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts
tests/unit/workers/whatsapp.worker.test.ts or current equivalent
```

Do not create files merely because they are listed if the accepted post-BACKGROUND-010 repository has a different test organisation.

## Acceptance criteria

- [ ] Raw sender/global admission happens before tenant/DB routing work.
- [ ] Settled-turn admission happens after coalescing/lease claim and before outbound reservation/AI.
- [ ] Redis decisions are atomic across all applicable scopes.
- [ ] Rolling windows use Redis server time.
- [ ] Raw/provider and settled-turn retries are idempotent.
- [ ] No raw phone/message body appears in Redis key names or metric labels.
- [ ] Ambiguous/unknown routing behavior remains fail closed.
- [ ] Abuse denial never creates merchant billing usage.
- [ ] Settled denial never creates `OUTBOUND_AUTOMATED_MESSAGE`.
- [ ] Raw denial never creates ConversationMessage rows.
- [ ] Settled denial retains already-persisted ConversationMessage rows.
- [ ] Limiter failure fails closed for AI/provider work without retry amplification.
- [ ] BACKGROUND-004 terminal/outbound safety behavior is unchanged.
- [ ] BACKGROUND-010 coalescing/lease/stale-response behavior is unchanged.
- [ ] Required regressions pass.
- [ ] Full repository test suite is run and unrelated baseline failures are documented.
- [ ] Build/typecheck, Prisma validation where repository convention requires it, diagnostics and `git diff --check` pass.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- This task starts only after BACKGROUND-010 is architect-accepted Complete.
- Do not add database migrations or Shared contracts.
- Do not make the initial thresholds configurable in this task.
- Do not broaden scope into infrastructure/WAF/Meta account blocking.
- Before editing, inspect the exact current worker after BACKGROUND-010; do not implement against the pre-BACKGROUND-010 flow.
- Use only repository scripts/dependencies that actually exist.
- Do not start SYSTEM-TEST-005.
- Return only BACKGROUND-011 to `review` and STOP.
- Do not run `git commit` or `git push`.

## Completion Report

### Status
In Progress (Attempt 1)

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
None.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status
Pending

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending

### Follow-up
None.
