# Inbound WhatsApp Recovery and Multi-Basket Runtime Flow

## Purpose

This document is the canonical readable description of Moda Interact's inbound
shopper WhatsApp runtime flow.

It consolidates the architectural decisions that are otherwise distributed
across ARCH-007 database/background task files, especially:

- durable recovery and standalone conversation ownership;
- inbound routing and multiple-abandoned-basket clarification;
- fragmented-message coalescing;
- raw and settled-turn abuse admission;
- common outbound WhatsApp safety admission; and
- the relationship between recovery billing and operational message/AI safety.

The detailed architecture/task files remain authoritative for their individual
contracts and task state. This file explains how those contracts compose at
runtime. Where a referenced task is still in `ready`, `in_progress` or `review`,
its task metadata remains authoritative for implementation status; this document
does not by itself claim that the path is deployed in production.

## Core identities

Three identities must not be conflated.

### `CheckoutRecovery`

A `CheckoutRecovery` represents one abandoned-basket recovery lifecycle.

```text
abandoned basket
      |
      v
CheckoutRecovery
      |
      +--> DETECTED
      +--> MESSAGE_SENT
      +--> ENGAGED
      +--> COMPLETED / EXPIRED / CANCELLED
```

A customer may legitimately have more than one current recovery because they may
have more than one abandoned basket.

### `Conversation`

A `Conversation` is the durable conversational processing and outbound-safety
scope.

Recovery-linked conversations retain their `checkoutRecoveryId` identity.
Standalone `PRODUCT_DISCOVERY` / `PRODUCT_SUPPORT` conversations use explicit
shop/customer ownership and an expirable standalone scope.

Conversation-level automated-message safety is per durable `Conversation`, not
per merchant and not per raw inbound message.

### Customer / WhatsApp sender

The normalized customer phone/sender identity is an operational abuse boundary
that spans the customer's conversations and recoveries.

Therefore:

```text
Customer P
   |
   +--> Basket A -> CheckoutRecovery A -> Conversation A
   +--> Basket B -> CheckoutRecovery B -> Conversation B
   +--> Basket C -> CheckoutRecovery C -> Conversation C
```

means the customer may have three separate conversation scopes, but still one
shared sender-level abuse history.

## End-to-end flow

```text
Meta / WhatsApp webhook
        |
        v
moda-interact-messaging
verify signature + normalize inbound event
        |
        v
BullMQ: whatsapp-events / message-received
        |
        v
RAW ABUSE ADMISSION
sender + global
        |
        +-- denied/unavailable ----------------------------+
        |                                                  |
        |   acknowledge/suppress                           |
        |   no tenant/recovery routing                     |
        |   no ConversationMessage                         |
        |   no turn job                                    |
        |   no CommerceAgent                               |
        |   no outbound provider call                      |
        |                                                  |
        +--------------------------------------------------+
        |
        v
Background durable routing
        |
        +-- explicit reply/context identifies owned scope
        |
        +-- current recovery candidates
        |
        +-- standalone product/support ownership
        |
        v
persist/dedupe inbound ConversationMessage
providerMessageId idempotency
        |
        v
increment Conversation.inboundVersion
        |
        v
3s quiet / 10s maximum coalescing window
        |
        v
claim 120s conversation processing lease
        |
        v
assemble persisted inbound fragments for ONE logical turn
        |
        v
resolve CURRENT recovery / clarification context
        |
        v
SETTLED-TURN ABUSE ADMISSION
sender + conversation + shop + global
        |
        +-- denied/unavailable ----------------------------+
        |                                                  |
        |   keep persisted inbound fragments               |
        |   mark handled version safely                    |
        |   clear/reconcile processing state               |
        |   no outbound reservation                        |
        |   no CommerceAgent/tools                         |
        |   no provider call                               |
        |                                                  |
        +--------------------------------------------------+
        |
        v
COMMON OUTBOUND WHATSAPP ADMISSION
per durable Conversation
        |
        +-- normal slot unavailable
        |      -> accepted deterministic terminal/suppress path
        |      -> zero CommerceAgent
        |
        v
reserve normal outbound capacity
        |
        v
CommerceAgent / tools
        |
        v
stale-version check
        |
        +-- newer inbound version exists
        |      -> suppress stale response
        |      -> release/fail prepared reservation
        |      -> process newest settled turn later
        |
        v
WhatsApp provider send
        |
        v
durable provider lifecycle + usage/accounting updates
```

## Raw ingress abuse admission

Raw abuse admission exists to stop an authenticated Meta message from
immediately becoming authorised tenant/AI/provider work.

It runs before:

```text
recoveryRoutingService.resolveInboundMessage()
Prisma tenant/customer/conversation routing
ConversationService.receiveMessage()
```

Initial raw scopes are:

| Scope | Window | Initial limit |
| --- | ---: | ---: |
| sender | 60 seconds | 60 distinct provider messages |
| global | 60 seconds | 20,000 distinct provider messages |

The raw sender key uses a SHA-256 hash of the normalized customer phone. Raw
phone numbers and message bodies must not be embedded in Redis key names or
metric labels.

`providerMessageId` is the raw idempotency member. Replaying the same provider
message must not consume capacity again.

If raw admission is denied or cannot make a decision because the limiter is
unavailable, the job is handled without retry amplification and performs no
routing, DB message persistence, turn enqueue, AI or provider work.

## Durable routing and multiple abandoned baskets

After raw admission succeeds, Background resolves the durable conversational
scope.

The important case is one customer with several current abandoned baskets.
Current candidate routing is bounded and tenant-safe:

```text
0 current candidates
  -> standalone PRODUCT_SUPPORT

1 matching-owner candidate
  -> resolve to that current CheckoutRecovery context

2..10 matching-owner candidates
  -> reuse/create one deterministic clarification Conversation
  -> send deterministic basket choices
  -> zero CommerceAgent for the clarification response

11+ candidates (11th row is overflow sentinel)
  -> unresolved / fail closed

mixed shop/customer ownership
  -> unresolved / fail closed
```

The bounded `take: 11` lookup is intentional: rows 1..10 are the maximum
resolvable candidate set and row 11 means overflow. Overflow must fail closed
before exposing recovery references or creating a clarification scope.

### Clarification does not pretend to be a recovery conversation

When a durable standalone `PRODUCT_SUPPORT` clarification conversation later
resolves to one current recovery, the system combines:

```text
CURRENT selected recovery
  - recovery id
  - current status
  - checkout token
  - completion/price state
  - current shop/customer

WITH

EXISTING clarification Conversation
  - conversation id
  - language state
  - summary/version
  - individually persisted/coalesced inbound fragments
```

The standalone clarification Conversation is not retroactively rewritten as if
it belonged to the selected `CheckoutRecovery`.

If the current candidates no longer match the clarification conversation's
durable `shopId` and `customerId`, resolution fails closed.

## Fragmented inbound messages become one logical turn

Moda does not use:

```text
1 inbound message = 1 CommerceAgent call = 1 reply
```

Each admitted raw message remains individually persisted, but nearby fragments
from one durable Conversation settle into one logical turn.

Initial constants are:

```text
QUIET_WINDOW_MS = 3000
MAX_SETTLE_WINDOW_MS = 10000
PROCESSING_LEASE_MS = 120000
```

The turn job identity is deterministic:

```text
conversation-turn__<conversationId>__<observedVersion>
```

The turn processor:

1. no-ops stale/duplicate observed versions;
2. waits until the 3-second quiet deadline or 10-second maximum deadline;
3. conditionally claims the conversation-scoped processing lease;
4. assembles persisted `INBOUND/CUSTOMER` fragments since
   `pendingTurnStartedAt` in deterministic order;
5. keeps the individual `ConversationMessage` rows intact; and
6. proceeds to settled-turn abuse admission before outbound reservation or
   CommerceAgent execution.

Different conversations may process concurrently. Only one live processor may
own one Conversation version at a time.

## Settled-turn abuse admission

Settled admission protects expensive work after the customer's fragments have
been coalesced.

Standard scopes are:

| Scope | Window | Initial limit |
| --- | ---: | ---: |
| sender | 60 seconds | 12 turns |
| sender | 10 minutes | 60 turns |
| conversation | 60 seconds | 12 turns |
| conversation | 10 minutes | 60 turns |
| shop | 60 seconds | 600 turns |
| global | 60 seconds | 5,000 turns |

For `PRODUCT_DISCOVERY` with no reply context, only the sender/conversation
limits are lower:

| Scope | Window | Initial discovery limit |
| --- | ---: | ---: |
| sender | 60 seconds | 4 turns |
| sender | 10 minutes | 12 turns |
| conversation | 60 seconds | 4 turns |
| conversation | 10 minutes | 12 turns |

A `PRODUCT_DISCOVERY` turn with an `inReplyToProviderId` fragment uses the
standard limits. Recovery, product-support and other applicable conversational
work also use the standard limits.

The settled idempotency member is:

```text
<conversationId>:<observedVersion>
```

A replay of the same logical settled turn must not consume capacity twice or
refresh/reinsert that turn into an expired shorter scope while another longer
scope still proves that it was previously admitted.

## Multiple baskets do not multiply abuse allowance

This is a deliberate cross-scope invariant.

Suppose one customer has three abandoned baskets:

```text
Basket A -> Recovery A -> Conversation A
Basket B -> Recovery B -> Conversation B
Basket C -> Recovery C -> Conversation C
```

The limiter relationship is:

```text
                       A conversation   B conversation   C conversation
                            |                 |                 |
conversation scopes --------+-----------------+-----------------+
                            \                 |                /
                             \                |               /
sender scopes  ---------------------- customer P ----------------------
shop scope     ------------------------ merchant S --------------------
global scope   ----------------------- Moda platform ------------------
```

So if the customer generates:

```text
5 settled turns against Basket A
4 settled turns against Basket B
3 settled turns against Basket C
```

the sender-level 60-second usage is:

```text
5 + 4 + 3 = 12
```

not three separate allowances of 12.

The next standard settled turn from any of those conversations is constrained by
the shared sender scope.

At the same time:

- each durable Conversation has its own conversation-level counters;
- all of those conversations contribute to the same shop-level counter; and
- every shop contributes to the global counter.

`checkoutRecoveryId` must therefore **not** become an abuse-rate-limit scope.
Doing so would let a sender multiply their allowance by creating or switching
between abandoned baskets.

## Atomic multi-scope decision

One admission decision can involve several Redis keys/scopes. It is all-or-none.

```text
prune expired members from all applicable scopes
        |
        v
is this idempotency member already known in ANY surviving scope?
        |
        +-- yes -> already-admitted replay
        |          allow without adding/refreshing it in any scope
        |
        v
check capacity of ALL scopes
        |
        +-- any full -> deny and mutate NONE
        |
        v
add member to ALL applicable scopes with Redis server time
```

This prevents partial accounting when, for example, sender/conversation/shop
would allow a turn but the global scope is already full.

The Lua operation uses Redis server time so workers with different local clocks
do not disagree about rolling-window membership.

## Settled denial and later inbound versions

A denied settled turn is intentionally handled/suppressed rather than repeatedly
retried until the rate window opens.

The already-persisted inbound fragments remain durable. For the denied observed
version the processor must use the accepted conditional/version-safe cleanup
path to:

```text
advance lastProcessedVersion when still current
clear pendingTurnStartedAt when still current
clear processingInboundVersion / processingStartedAt
```

If a newer inbound version arrived while the older turn was being admitted, the
older version must not strand the 120-second processing lease. The obsolete
lease is released and the newest logical version remains eligible for its own
settled processing/admission.

A later genuinely new turn may be admitted normally once rolling-window capacity
is available.

## Common outbound admission and CommerceAgent safety

Settled abuse admission is not the merchant outbound safety cap.

After settled admission succeeds, all Moda-originated Background WhatsApp sends
cross the common outbound admission boundary.

The common outbound boundary:

- requires a durable `conversationId`;
- validates conversation ownership against `shopId`;
- counts automated `AUTOMATION` / `AGENT` outbound messages per Conversation;
- reserves normal capacity before CommerceAgent execution;
- supports at most one deterministic terminal response when normal capacity is
  exhausted; and
- keeps low-level provider transport behind the admission boundary.

If normal outbound capacity is unavailable, CommerceAgent/LLM/tool work is not
performed merely to discover that the response cannot be sent.

## New inbound while CommerceAgent is running

If another inbound message arrives after a turn starts processing:

1. the new admitted raw message is persisted and increments `inboundVersion`;
2. the live processing lease prevents a second agent processor for that
   Conversation;
3. after the current CommerceAgent returns, the worker checks whether the
   Conversation changed;
4. if it changed, the prepared old response is not sent;
5. its prepared reservation is released/failed according to the common outbound
   semantics; and
6. the newest version receives/retains a delayed turn job.

This prevents a stale AI response from being sent after the customer has already
provided more context.

## Billing and cost-control relationship

Abuse admission and turn coalescing are operational safety mechanisms, not new
merchant billing units.

The merchant commercial unit remains the recovery conversation:

```text
RECOVERY_CONVERSATION
```

The following do not become new merchant-billable usage merely because this
runtime flow exists:

```text
raw inbound customer message
settled CommerceAgent turn
clarification fragment
abuse-admission decision
```

Multiple abandoned baskets may legitimately become separate `CheckoutRecovery`
workflows and therefore remain subject to the normal recovery billing/admission
rules when each recovery is actually admitted. The clarification mechanism does
not create an extra recovery charge merely for asking the customer which basket
they mean.

Message-level outbound/provider controls remain separate cost/safety accounting
from the merchant-facing recovery unit.

For the current commercial ordering, shop-lifetime Free grant, paid included
usage, promotional credits, purchased top-ups and capacity-exhaustion semantics,
see [`ARCH-010-merchant-lifecycle-state-transitions.md`](ARCH-010-merchant-lifecycle-state-transitions.md)
and [`../product/pricing-and-billing-model.md`](../product/pricing-and-billing-model.md).
ARCH-007 remains relevant to the message/provider safety primitives in this flow,
but its superseded merchant overage/capacity rules are historical.

## Failure and privacy rules

Across the flow:

- ambiguous tenant ownership fails closed;
- 11+ current recovery candidates fail closed;
- raw limiter failure fails closed before routing/DB/AI/provider work;
- settled limiter failure fails closed before outbound reservation/AI/provider
  work while safely resolving the processing lease/version state;
- individual inbound messages remain providerMessageId-idempotent;
- logical settled turns remain conversation/version-idempotent;
- raw phone numbers and message bodies must not appear in Redis keys or abuse
  metric labels;
- customer inbound traffic itself does not increment the automated outbound
  merchant usage metric; and
- persistent business state remains in PostgreSQL; Redis is operational
  coordination/rate-window state rather than the sole durable business record.

## Detailed source documents

This readable flow consolidates, but does not replace, the detailed contracts:

- [`ARCH-007-shopify-billing-usage-cost-control.md`](ARCH-007-shopify-billing-usage-cost-control.md)
- [`../decisions/database/ARCH-007/DATABASE-004-standalone-whatsapp-conversation-scope.md`](../decisions/database/ARCH-007/DATABASE-004-standalone-whatsapp-conversation-scope.md)
- [`../decisions/database/ARCH-007/DATABASE-006-conversation-turn-coalescing-state.md`](../decisions/database/ARCH-007/DATABASE-006-conversation-turn-coalescing-state.md)
- [`../decisions/background/ARCH-007/BACKGROUND-004-common-whatsapp-outbound-admission.md`](../decisions/background/ARCH-007/BACKGROUND-004-common-whatsapp-outbound-admission.md)
- [`../decisions/background/ARCH-007/BACKGROUND-010-coalesce-inbound-whatsapp-turns.md`](../decisions/background/ARCH-007/BACKGROUND-010-coalesce-inbound-whatsapp-turns.md)
- [`../decisions/background/ARCH-007/BACKGROUND-011-inbound-whatsapp-abuse-admission.md`](../decisions/background/ARCH-007/BACKGROUND-011-inbound-whatsapp-abuse-admission.md)

Use those task files for exact implementation constraints, review findings and
current task status. Use this document first when the question is how the whole
inbound WhatsApp / recovery / multi-basket flow fits together.
