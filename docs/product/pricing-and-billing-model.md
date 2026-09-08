# Moda Interact Pricing and Billing Model

> **Status:** Product model agreed; ARCH-007 implementation is in progress.
>
> **Architecture source of truth:**
> [`ARCH-007 — Shopify Billing, Usage and Cost Control`](../architecture/ARCH-007-shopify-billing-usage-cost-control.md)

This page explains the commercial pricing model and how Moda Interact maps that
model onto Shopify billing, durable platform state and internal cost controls.

For current execution state and pickup order, see the
[`ARCH-007 implementation handoff`](../architecture/ARCH-007-implementation-handoff.md).

It is intentionally more readable than the canonical ARCH-007 architecture
document. If this page and ARCH-007 ever disagree, ARCH-007 and the current task
files are authoritative for implementation.

---

## 1. What the merchant pays for

Moda Interact's primary merchant-facing commercial unit is a:

```text
RECOVERY_CONVERSATION
```

A recovery conversation represents an admitted abandoned-checkout recovery
workflow. It is deliberately different from counting every individual WhatsApp
message.

For example, a shopper might send several messages during one recovery:

```text
Customer: Is the blue version still available?
Moda:     Yes.

Customer: Can it arrive tomorrow?
Moda:     ...
```

That may still be one merchant recovery conversation even though it contains
multiple customer and Moda messages.

Moda's own costs can still vary with individual WhatsApp responses and
CommerceAgent/LLM work. Those costs are controlled separately through the
message-level safety model described below.

---

## 2. Current target plans

| Plan | Price | Included recovery conversations | Standard overage |
| --- | ---: | ---: | ---: |
| **Free** | $0 | 5 lifetime | No automatic overage |
| **Starter** | $35/month | 200/month | $0.05 per additional recovery |
| **Growth** | $75/month | 500/month | $0.04 per additional recovery |
| **Scale** | $149/month | 1,200/month | $0.03 per additional recovery |

Paid tiers combine predictable included capacity with continued service through
overage rather than hard-stopping a merchant when the monthly allowance is
exhausted.

### Free is different

Free has a **lifetime**, not monthly, recovery allowance:

```text
Free allowance = 5 lifetime recovery conversations
```

Once those five are consumed, the merchant must either buy prepaid recovery
credits or upgrade to a paid plan. Buying a pack never resets the original Free
lifetime allowance.

---

## 3. Free allowance adjustments for testing and support

The canonical Free plan remains **5 lifetime recovery conversations** for ordinary merchants.

A specific shop may have a different effective Free allowance for controlled testing, support credit or an operational exception. This uses the already-accepted signed allowance-adjustment ledger; it does **not** modify the plan or add test-only runtime branches.

```text
base Free allowance = 5
signed shop adjustments = SUM(BillingAllowanceAdjustment.quantity)

effective Free allowance = base + signed adjustments
```

Example test shop:

```text
base = 5
Admin adjustment = +95

effective allowance = 100
```

To test exhaustion quickly:

```text
base = 5
Admin adjustment = -4

effective allowance = 1
```

Historical committed/reserved usage is never rewritten when the effective allowance is lowered. Remaining capacity bottoms at zero.

Every adjustment is append-only, requires a reason/administrator audit trail and is exposed through the ARCH-007 Admin controls. Do not use an environment variable such as `FREE_RECOVERY_LIMIT`, a hard-coded shop domain or an `isTestShop` branch.

---

## 4. Repeatable recovery-credit packs

Every plan may buy **prepaid recovery-credit packs**. This is not limited to
Free.

```text
buy a pack
-> consume the pack
-> buy another pack
-> consume that pack
-> repeat
```

There is no architectural rule limiting the number of packs a merchant may buy.

### Why packs exist

Packs support merchants who want predictable prepaid capacity without changing
their subscription immediately. They also let paid merchants buy additional
recovery capacity at a plan-specific prepaid rate before ordinary overage is
used.

### Tier-sensitive pack pricing

The intended commercial rule is:

> Higher subscription tiers may receive cheaper recovery-credit pack rates.

For example, Shopify can be configured so that the same pack quantity costs
more on Free than on Starter, and less again on Growth or Scale.

The exact monetary pack prices are **not fixed in this document**. They are
configured in **Shopify App Pricing**, which remains authoritative for the
actual amount Shopify charges.

Moda stores only operational mapping such as:

```text
whether the plan supports packs
credits per pack
Shopify recovery-credit-pack meter/event handle
```

Moda does **not** duplicate the top-up monetary price in PostgreSQL.

---

## 5. Capacity consumption order

The order is deterministic.

### Free

```text
1. Remaining lifetime Free recovery allowance
2. Purchased recovery credits
3. Block new recovery
```

After purchased credits reach zero, another recovery is blocked until the
merchant buys another pack or upgrades.

### Paid plans

```text
1. Current billing-period included recovery allowance
2. Purchased recovery credits
3. Normal plan overage
```

Example for Starter:

```text
Starter included = 200
Current period used = 200
Purchased credits = 25

next 25 recoveries
-> consume purchased credits

purchased balance = 0
-> later recoveries resume Starter overage
```

If the merchant buys another pack, subsequent recoveries can again consume the
new purchased balance before returning to ordinary overage.

---

## 6. Purchased credits do not expire monthly

Purchased recovery credits are separate from a subscription's included monthly
allowance.

```text
monthly included capacity
  -> resets with the relevant Shopify billing period

purchased recovery credits
  -> do not reset monthly
  -> do not disappear on plan upgrade
  -> do not disappear on plan downgrade
  -> remain attached to the same durable Shop
```

This makes a pack genuinely prepaid rather than another monthly allowance.

---

## 7. Shopify billing mechanism

Moda Interact uses **Shopify App Pricing**.

The target implementation models a recovery-credit-pack purchase through a
dedicated Shopify usage meter/App Event rather than maintaining a separate Moda
payment system.

```text
Merchant clicks "Buy recovery pack"
        |
        v
Moda creates durable purchase request
        |
        v
UsageEvent:
  metric = RECOVERY_CREDIT_PACK_PURCHASE
  quantity = 1
  state = PENDING
        |
        v
Background App Events publisher
        |
        v
Shopify App Pricing meter
        |
        v
Shopify reports/accepts billing event
        |
        v
Moda activates purchased credits exactly once
```

The Shopify meter associated with the current plan determines the monetary
price. This is also how higher plans can receive preferential pack rates without
embedding money values into application code.

---

## 8. Durable top-up state

The target ARCH-007 model uses explicit durable state rather than treating a UI
click as capacity.

### Recovery-credit purchase

One durable purchase row represents one merchant top-up request and records:

```text
purchase identity
shop
plan snapshot
Shopify pack meter snapshot
credits granted by the pack
linked UsageEvent
status
activation timestamp
```

A purchase becomes usable capacity only after its linked billing UsageEvent is
successfully reported.

### Purchased entitlement counter

Purchased capacity is tracked separately from the Free lifetime counter:

```text
grantedQuantity
- committedQuantity
- reservedQuantity
=
available purchased recovery credits
```

That permits safe reservation before provider work and prevents duplicate or
concurrent workers from spending the same final credit.

---

## 9. Purchase lifecycle and idempotency

The target lifecycle is:

```text
PENDING_BILLING
        |
        | Shopify App Event reported successfully
        v
ACTIVE
```

Definitive billing/configuration failure can instead require:

```text
NEEDS_ATTENTION
```

Credits are granted only when the billing event is successfully reported.

The same merchant purchase request must never create two Shopify billing events
or two credit grants. Reprocessing an already-active purchase must not increment
purchased capacity again.

---

## 10. Recovery admission and reservation

Recovery admission happens before provider send.

```text
check capacity
-> reserve capacity
-> perform provider/business action
-> commit or release/retain reservation according to outcome
```

Important outcomes:

```text
definitive provider failure
  -> release reserved capacity

provider accepted / recovery initiated
  -> commit capacity

ambiguous provider outcome
  -> do not blindly release and resend
  -> preserve ambiguous/non-terminal state for reconciliation
```

This protects the final available recovery credit against concurrency and
prevents blind duplicate sends across an uncertain provider boundary.

---

## 11. Paid overage is not the same as purchased credits

Purchased credits and overage are intentionally distinct:

```text
Purchased recovery credits
  prepaid
  durable balance
  consumed before paid overage

Paid overage
  metered recovery usage after included + purchased capacity
```

A recovery covered by purchased credits must not also be reported as a normal
overage recovery. That would double-charge the merchant.

---

## 12. Why merchant billing is not per WhatsApp message

Moda does not want every fragmented WhatsApp message to become a separate
merchant charge or CommerceAgent invocation.

A shopper may type:

```text
"Hi I was looking at"
"the black jacket"
"sorry I mean the blue one"
```

Those are three raw inbound messages but conversationally one customer turn.

The target Background design keeps all three messages durably while coalescing
nearby fragments before invoking CommerceAgent.

Initial settling rules:

```text
quiet window          = 3 seconds
maximum settle window = 10 seconds
```

```text
3 inbound messages
        |
        +--> persisted individually
        |
        v
3-second quiet period
        |
        v
1 logical customer turn
        |
        v
1 outbound-capacity reservation
        |
        v
1 CommerceAgent invocation
        |
        v
1 WhatsApp response
```

The maximum settle window prevents continuous typing from postponing processing
forever.

---

## 13. Message-level cost controls

Merchant billing and internal cost control are separate dimensions.

```text
Merchant commercial unit:
  RECOVERY_CONVERSATION

Internal provider/AI safety:
  OUTBOUND_AUTOMATED_MESSAGE
  per durable conversation
```

Customer inbound messages do **not** directly consume the outbound counter.
Instead, outbound capacity is reserved **before** CommerceAgent runs:

```text
customer inbound messages
        |
        v
persist + coalesce
        |
        v
reserve outbound slot
        |
        +--> available
        |      -> run CommerceAgent
        |      -> send response
        |
        +--> normal cap exhausted
               -> do NOT run LLM/tools
               -> use at most one reserved terminal response
```

This places a hard bound on the expensive inbound-to-agent-to-reply loop without
dropping authenticated inbound customer messages.

The limit is **per conversation**, not a shop-wide lifetime counter.

---

## 14. Conversation ordering

One durable conversation must not run multiple CommerceAgent turns concurrently.

If a correction arrives while the agent is processing:

```text
agent processing old turn
        |
new inbound message arrives
        |
        +--> persist it
        +--> do not start a second concurrent agent
        |
old agent completes
        |
        v
detect conversation changed
        |
        v
do not send stale answer
        |
        v
process the newer settled turn
```

Different conversations remain independently concurrent.

---

## 15. Repository ownership

| Repository | Pricing/billing responsibility |
| --- | --- |
| `moda-interact-database` | Billing plan fields, usage/audit state, entitlement counters, purchase persistence, constraints |
| `moda-interact-shared` | Canonical usage metrics and deterministic cross-service billing identifiers |
| `moda-interact` | Merchant billing UI, plan presentation, top-up request creation, Shopify plan verification |
| `moda-interact-admin` | Internal plan catalogue and Shopify meter mapping; no duplicate monetary price source |
| `moda-interact-background` | Recovery admission, reservations, usage commitment, App Events publication, purchased-credit activation, message-cost safety |
| `moda-interact-messaging` | Provider-status ingress/normalisation; does not decide merchant billing policy |
| `moda-interact-system-test` | Terminal/manual-gated integrated billing and message-safety validation |
| `moda_architect` | Cross-repository rules, dependency order, invariants and implementation review |

---

## 16. ARCH-007 implementation map

Implementation is decomposed under:

```text
docs/decisions/*/ARCH-007/
```

Capability groups include:

```text
billing policy / usage persistence
        |
Free reservation lifecycle
        |
recovery billing admission
        |
common outbound WhatsApp admission
        |
Shopify App Events publisher
        |
repeatable recovery-credit packs
        |
fragmented inbound-message coalescing
        |
terminal/manual-gated system validation
```

For exact current task states, use task YAML and domain `_index.md` files rather
than this readable page.

---

## 17. Worked examples

### Free merchant exhausts Free allowance

```text
Free lifetime allowance = 5
5 consumed
purchased credits = 0

new recovery
-> blocked
```

Merchant buys a pack:

```text
Shopify pack event reported
-> purchased credits activated

new recovery
-> purchased reserve
-> provider accepted
-> purchased commit
```

After the pack is exhausted, the merchant may buy another pack.

### Starter merchant with purchased credits

```text
Starter included = 200
current normal usage = 200
purchased remaining = 10

next recovery
-> purchased credit
```

After the 10 purchased credits are consumed:

```text
next recovery
-> normal Starter overage
```

### Fragmented WhatsApp typing

```text
"Can I get"
"the blue one"
"sorry, size medium"
```

All three messages remain stored. If they settle within the configured window,
they result in:

```text
1 logical customer turn
1 outbound safety reservation
1 CommerceAgent invocation
1 reply
```

---

## 18. Pricing values vs implementation values

### Commercial values

```text
subscription monthly price
overage rate
recovery-credit-pack monetary price
```

Shopify App Pricing is authoritative.

### Moda operational values

```text
included recovery allowance
Free lifetime allowance
credits per pack
Shopify meter handles
purchased credit balance
usage identities
reservation state
message safety limits
```

Moda persists these because they are required for deterministic operational
decisions.

---

## 19. Current implementation status

ARCH-007 is **in progress**.

Core billing-policy, Free reservation, recovery admission and Shopify App Events
capabilities are being implemented and architect-reviewed incrementally.

Repeatable recovery-credit packs and fragmented inbound-message coalescing are
part of the agreed target model and have been decomposed into bounded ARCH-007
implementation tasks.

This page therefore describes both the target product model and how the current
ARCH-007 implementation is converging on it. It should not be read as a claim
that every top-up or coalescing path is already deployed in production.

Authoritative current execution state lives in:

```text
docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md
docs/decisions/*/ARCH-007/_index.md
docs/decisions/*/ARCH-007/*.md
```
