---
id: ARCH-007-BACKGROUND-011
architecture_id: ARCH-007
title: Add inbound WhatsApp abuse admission before routing and CommerceAgent work
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 69
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-007-BACKGROUND-010
enables:
  - ARCH-007-SYSTEM-TEST-005
created: 2026-09-08
updated: 2026-09-08T20:02:00+01:00
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

- [x] Raw sender/global admission happens before tenant/DB routing work.
- [x] Settled-turn admission happens after coalescing/lease claim and before outbound reservation/AI.
- [x] Redis decisions are atomic across all applicable scopes.
- [x] Rolling windows use Redis server time.
- [x] Raw/provider and settled-turn retries are idempotent.
- [x] No raw phone/message body appears in Redis key names or metric labels.
- [x] Ambiguous/unknown routing behavior remains fail closed.
- [x] Abuse denial never creates merchant billing usage.
- [x] Settled denial never creates `OUTBOUND_AUTOMATED_MESSAGE`.
- [x] Raw denial never creates ConversationMessage rows.
- [x] Settled denial retains already-persisted ConversationMessage rows.
- [x] Limiter failure fails closed for AI/provider work without retry amplification.
- [x] BACKGROUND-004 terminal/outbound safety behavior is unchanged.
- [x] BACKGROUND-010 coalescing/lease/stale-response behavior is unchanged.
- [x] Required regressions pass.
- [x] Full repository test suite is run and unrelated baseline failures are documented.
- [x] Build/typecheck, Prisma validation where repository convention requires it, diagnostics and `git diff --check` pass.

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
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-BACKGROUND-011` branch and the mirrored parent-workspace `task/ARCH-007-BACKGROUND-011` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status
Ready for Review (Attempt 3)

### Files Changed
- `src/services/inbound-whatsapp-abuse-admission.service.ts`
- `src/services/conversation-turn-processor.service.ts`
- `src/workers/whatsapp.worker.ts`
- `tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts`
- `tests/unit/services/conversation-turn-processor.service.test.ts`

### Work Completed
- Added a Background-local atomic Lua sliding-window limiter using `connectionRedis`, Redis server time, all-or-none scope insertion, bounded expiry, replay idempotency, and SHA-256 sender key hashing.
- Corrected mixed-window settled replay handling so a member remembered by any applicable scope is never re-added to naturally expired short scopes.
- Added raw admission before routing and persistence, including fail-closed limiter errors.
- Added settled-turn admission after claim/load and before outbound reservation or CommerceAgent work; denied and unavailable decisions use `completeTurn` cleanup.
- Preserved B004 outbound admission and B010 settle, lease, and stale-response paths.
- Strengthened the stateful Redis harness and focused service regressions to prove sender and conversation short/long limits independently, all six settled scopes, all-or-none rejection, and mixed-window replay idempotency.

### Validation Results
- `npx vitest run tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts tests/unit/services/conversation-turn-processor.service.test.ts`: passed, 50 tests.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- Diagnostics for all touched source/test files: no errors.
- `git diff --check`: passed.
- `npm test`: 397 passed, 7 skipped, 2 failed. The two failures remain unrelated baseline failures in `tests/unit/services/pending-recovery-candidate.service.test.ts` concerning stale/rescheduled candidate context behavior.

### Deviations
- The repository has no supported Redis integration harness; the Lua contract is unit-tested through the existing Vitest conventions, as permitted by the task.
- No dedicated worker test file exists in the accepted repository organization; raw ordering is covered by the production call path and settled handling by the processor regression.

### Assumptions
- `conversation.messages` is the accepted Prisma relation for the persisted inbound fragments of the settled turn.
- The loaded outbound customer phone is the normalized sender identity used by the settled-turn limiter.

### Unresolved Issues
- Full suite remains red only on the two documented unrelated pending-recovery-candidate baseline failures.
- Pending-recovery-candidate baseline status remains unchanged and is outside this task's allowed file surface.

### Architectural Concerns
None.

### Attempt 3 Correction Coverage
- Mixed-window settled replay no longer re-adds expired short-scope capacity.
- `B011-08` proves sender-short and conversation-short independently.
- `B011-09` proves sender-long and conversation-long independently.
- `B011-10` proves discovery sender and conversation short/long limits independently.
- `B011-17` is a settled new-observedVersion expiry regression.
- `B011-20` checks candidate absence from all six applicable scopes.
- `B011-21` checks all six scopes plus immediate and mixed-window replay.
- `B011-01` through `B011-21`: pass.
- `B011-R1`: pass; obsolete settled-turn leases are released and newer versions are re-enqueued without outbound or agent work.
- `B011-R2`: pass; limiter-unavailable cleanup follows the same race-safe newer-version path.
- Full-suite baseline: 397 passed, 7 skipped, 2 unrelated failures, unchanged in scope and documented above.

## Architect Review

### Review Status

Accepted

### Review Notes

#### Attempt 3 — Accepted

Attempt 3 is architect-accepted Complete.

The deterministic Attempt 2 correction contract is satisfied:

1. The Lua limiter now uses the required three-pass decision order. It prunes
   every applicable scope and checks replay presence across all scopes first.
   If the idempotency member is still present in any applicable scope, the
   decision returns allowed without `ZADD`, without score refresh and without
   expiry refresh. A mixed 60-second/600-second replay therefore cannot consume
   short-window capacity a second time.

2. Capacity rejection remains all-or-none. Cardinality is inspected only after
   replay detection completes across every scope, and a rejected candidate is
   inserted into none of the applicable windows.

3. Attempt 3 stayed within the exact allowed implementation surface. Direct
   comparison with the supplied Attempt 2 snapshot shows production changes
   only in `src/services/inbound-whatsapp-abuse-admission.service.ts` and test
   changes only in
   `tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts`.
   The accepted processor and worker behavior from Attempt 2 was not redesigned.

4. The stateful Redis harness now models the same three-pass contract and
   exposes exact settled-scope snapshots rather than ambiguous partial-key
   checks.

5. The focused regressions now prove the previously overstated cases:
   - B011-08 independently proves sender-short and conversation-short limits;
   - B011-09 independently proves sender-long and conversation-long limits;
   - B011-10 independently proves PRODUCT_DISCOVERY sender and conversation
     short/long limits;
   - B011-17 exercises a new settled member after short-window expiry;
   - B011-20 proves a rejected candidate is absent from all six settled scopes;
   - B011-21a proves immediate replay leaves all six scopes unchanged;
   - B011-21b proves mixed-window replay does not re-add expired 60-second
     scopes and preserves the original 600-second scores.

The accepted Attempt 2 behavior remains intact: raw admission precedes routing
and persistence; settled admission is mandatory before outbound
reservation/CommerceAgent work; limiter denial/unavailability uses the
version-safe suppression cleanup; durable conversation types are represented
correctly; lower discovery limits apply only to unbound PRODUCT_DISCOVERY;
sender keys are hashed; telemetry uses the Shared structured logger; B004
outbound admission and B010 coalescing/lease/stale-response semantics are
unchanged.

Attempt 3 Completion Report records 50 focused tests passing, build and Prisma
validation passing, diagnostics clean, `git diff --check` passing, and the full
suite at 397 passed / 7 skipped with the same 2 unrelated
`pending-recovery-candidate` baseline failures. The supplied archive contains no
`node_modules`, so the architect did not independently rerun those commands.

Current Background `main` was also inspected and contains the corrected
three-pass Lua implementation and the strengthened B011 focused regressions.

No further implementation changes are required for
`ARCH-007-BACKGROUND-011`.

#### Attempt 2 — Changes Requested (preserved)

Attempt 2 resolves the major architectural defects from Attempt 1. Preserve the following implementation unchanged unless a correction below explicitly requires otherwise:

- raw abuse admission remains before routing, Prisma persistence and turn enqueue;
- settled abuse admission remains mandatory after the B010 lease claim and before outbound reservation / CommerceAgent / provider work;
- `LoadedConversationTurn` keeps mandatory `customerPhone`, full durable conversation type, `checkoutRecoveryId` and `hasReplyContext`;
- `RECOVERY`, `PRODUCT_DISCOVERY`, `PRODUCT_SUPPORT` and `POST_PURCHASE` remain represented explicitly, with lower limits only for unbound `PRODUCT_DISCOVERY`;
- `finishSuppressedTurn()` remains the single version-safe denial / `LIMITER_UNAVAILABLE` cleanup path;
- Shared structured logging remains the B011 telemetry surface;
- thresholds, Redis `TIME`, one atomic `EVAL`, B004 outbound semantics and B010 quiet/max-settle/lease constants remain unchanged.

Attempt 3 is a narrow deterministic correction. Do not redesign the processor, worker topology, billing model, Redis namespaces, thresholds, database schema, Shared contracts or infrastructure.

#### Attempt 3 — exact correction contract

##### A. Allowed file surface

Modify only:

```text
src/services/inbound-whatsapp-abuse-admission.service.ts
tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts
```

`tests/unit/services/conversation-turn-processor.service.test.ts` may be touched only if a formatting/type-only adjustment is forced by compilation. Do not alter production processor or worker behavior in Attempt 3.

##### B. Fix replay idempotency when short scopes have expired but long scopes still remember the turn

Attempt 2 correctly stopped unconditional score refresh for a member that is still present in a given ZSET. One mixed-window replay case is still wrong.

For a standard settled turn at `t0`, the member is inserted into:

```text
sender 60s
sender 600s
conversation 60s
conversation 600s
shop 60s
global 60s
```

At `t0 + 60_001ms`, the 60-second scopes have expired/pruned but the 600-second sender/conversation scopes still contain the same `conversationId:observedVersion`.

The current script then treats the member as absent in the short scopes and re-adds it there with the new `nowMs`. That replay consumes short-window capacity a second time.

Change the Lua decision order exactly as follows:

```text
PASS 1
- get Redis TIME once;
- for EVERY scope:
    - prune expired members;
    - check ZSCORE(member);
    - if present in ANY scope, set seenAnywhere = true;
- after all scopes have been inspected:
    - if seenAnywhere == true:
        return allowed immediately;
        perform NO ZADD;
        perform NO EXPIRE refresh;
        do not reject because another currently-empty scope is at capacity.

PASS 2  (only when seenAnywhere == false)
- inspect cardinality of EVERY applicable scope;
- if any scope is at its limit:
    - return that scope index;
    - mutate NONE of the scope windows.

PASS 3  (only when new member has capacity everywhere)
- ZADD the member to ALL applicable scopes with the same Redis nowMs;
- set the existing bounded expiry for each touched key;
- return allowed.
```

This preserves one atomic `EVAL` and the existing ZSET design.

Do NOT add:

```text
a new replay-marker key
a database idempotency table
another Redis connection
an environment variable
a longer-lived persistent abuse history
```

The intended invariant is:

```text
while ANY applicable rolling-window scope still remembers this idempotency member,
a replay is an already-admitted decision and must not consume capacity again in scopes
that have naturally expired sooner.
```

Once every applicable scope has naturally forgotten the member, normal rolling-window state may treat a later call as new.

##### C. Strengthen the stateful Redis harness to prove every sender AND conversation scope

Keep the existing test-only stateful `RedisLike.eval` harness. Update it to model the corrected three-pass production contract above.

Add exact-key/snapshot helpers so tests can distinguish:

```text
turn:sender:<hash>:60s
turn:sender:<hash>:600s
turn:conversation:<id>:60s
turn:conversation:<id>:600s
turn:shop:<shopId>:60s
turn:global:60s
```

Do not use a helper that returns only the first key whose text contains `turn:sender` or `turn:conversation` when the assertion claims to cover all scopes.

##### D. Correct the overstated B011 test mappings

The following named tests currently do not prove the full scenario stated in the task.

###### B011-08 — independently prove both short scopes

Keep/extend B011-08 so it proves:

```text
sender short:
- same sender
- varying conversations
- 12 distinct settled members allowed
- 13th denied by TURN_SENDER_SHORT

conversation short:
- same conversation
- varying senders
- unique observedVersion members
- 12 allowed
- 13th denied by TURN_CONVERSATION_SHORT
```

The shop/global scopes must remain below their limits.

###### B011-09 — independently prove both 10-minute scopes

Prove separately:

```text
TURN_SENDER_LONG = 60/10m
TURN_CONVERSATION_LONG = 60/10m
```

Use batches and `advanceTime(60_001)` so the corresponding 60-second scope reopens while the 600-second scope retains the previous members.

For the conversation-long case, keep one conversation and vary senders so no individual sender reaches its own long limit.

###### B011-10 — independently prove discovery sender AND conversation limits

For unbound `PRODUCT_DISCOVERY`, prove both:

```text
sender:       4/min and 12/10m
conversation: 4/min and 12/10m
```

Use varying conversations to isolate sender scope and varying senders to isolate conversation scope.

Do not infer conversation coverage merely because the production scope array contains conversation keys.

###### B011-17 — this must be a settled new observedVersion, not a raw event

Replace the current raw-window B011-17 test.

Required regression:

```text
- exhaust a settled short-window limit;
- prove a NEW settled member / observedVersion is denied;
- advance beyond the relevant 60-second window while remaining below the 600-second limit;
- submit another NEW observedVersion;
- prove it is allowed.
```

Use either a standard or discovery settled limit, but it must exercise `admitSettledTurn()`.

###### B011-20 — prove NONE means all applicable scopes

For a rejected multi-scope decision, snapshot every applicable key before the decision and verify the candidate member is added to none of:

```text
sender 60s
sender 600s
conversation 60s
conversation 600s
shop 60s
global 60s
```

Existing seeded members may remain. The rejected candidate itself must appear in zero scopes.

###### B011-21 — prove all six scopes and the mixed-window replay case

B011-21 must inspect all six actual settled scope keys, not four key-name categories.

Add two subcases (names may be `B011-21a` / `B011-21b`):

```text
immediate replay:
- admit one settled member;
- snapshot cardinality + member score in all six scopes;
- replay same member without advancing time;
- all six snapshots are unchanged.

mixed-window replay:
- admit one standard settled member at t0;
- capture both 600-second scores;
- advance 60_001ms;
- replay the SAME conversationId:observedVersion;
- 60-second scopes are allowed to be pruned naturally but MUST NOT re-add the member;
- sender-600s and conversation-600s member scores remain exactly the original t0 score;
- no scope receives a new score for that replay.
```

This mixed-window regression must fail against the current Attempt 2 Lua and pass after correction B.

##### E. Preserve the already-passing Attempt 2 corrections

Do not weaken or remove:

```text
B011-01..07
B011-11..16
B011-18..20 (except strengthen B011-20 as above)
B011-19 final-slot race
B011-R1
B011-R2
RECOVERY conversation-type regression
structured logging privacy assertions
mandatory settled admission in every processor harness
```

No new worker test is required in Attempt 3 unless an existing test stops compiling.

##### F. Validation and Completion Report

Run:

```text
npx vitest run tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts tests/unit/services/conversation-turn-processor.service.test.ts
npm run build
npm run prisma:validate
git diff --check
npm test
```

In the Attempt 3 Completion Report state explicitly:

```text
- mixed-window settled replay no longer re-adds expired short-scope capacity;
- B011-08 proves sender-short AND conversation-short independently;
- B011-09 proves sender-long AND conversation-long independently;
- B011-10 proves discovery sender AND conversation short/long limits independently;
- B011-17 is a settled new-observedVersion expiry regression;
- B011-20 checks candidate absence from all six applicable scopes;
- B011-21 checks all six scopes plus mixed-window replay;
- B011-01 through B011-21: pass;
- B011-R1: pass;
- B011-R2: pass;
- exact focused test count;
- full-suite pass/fail/skip count;
- whether the two unrelated `pending-recovery-candidate` baseline failures remain unchanged.
```

Return only `ARCH-007-BACKGROUND-011` to `review` and STOP. Do not start SYSTEM-TEST-005. Continue on the same existing B011 task branches/worktree; the next claim increments `attempt` from 2 to 3.

### Reviewed Files

Attempt 2 supplied workspace:

- `src/services/inbound-whatsapp-abuse-admission.service.ts`
- `src/services/conversation-turn-processor.service.ts`
- `src/workers/whatsapp.worker.ts`
- `tests/unit/services/inbound-whatsapp-abuse-admission.service.test.ts`
- `tests/unit/services/conversation-turn-processor.service.test.ts`
- `docs/decisions/background/ARCH-007/BACKGROUND-011-inbound-whatsapp-abuse-admission.md`

### Validation Reviewed

- Focused suite reported 49 passing tests.
- `npm run build` reported passed.
- `npm run prisma:validate` reported passed.
- diagnostics reported no errors.
- `git diff --check` reported passed.
- Full suite reported 396 passed, 7 skipped, with the same 2 unrelated `pending-recovery-candidate` baseline failures.
- The supplied archive contains no `node_modules`, so those commands could not be independently re-run in this review environment.
- Attempt 2 was intentionally uncommitted/unpushed; review was performed from the supplied task-worktree snapshot.

### Architecture Conformance

Accepted. B011 now satisfies the two-stage inbound abuse-admission architecture,
atomic Redis scope semantics, replay idempotency, privacy constraints,
fail-closed behavior and B004/B010 integration boundaries.

### Follow-up

`ARCH-007-BACKGROUND-011` is Complete.

`ARCH-007-SYSTEM-TEST-005` now has its B011 implementation prerequisite
satisfied, but it remains `pending` / manual-terminal-gated. Do not auto-start
or auto-promote the system-test task solely because its implementation
dependencies are complete.
