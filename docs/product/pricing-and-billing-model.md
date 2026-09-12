# Moda Interact Pricing, Billing and Recovery-Capacity Model

> **Status:** Current product model for ARCH-010. Architecture is agreed and implementation-ready; implementation remains task-driven.
>
> **Canonical architecture:**
> [`ARCH-010 — Merchant lifecycle state transitions and behavioural access`](../architecture/ARCH-010-merchant-lifecycle-state-transitions.md)
>
> **Implementation frontier:**
> [`ARCH-010 implementation handoff`](../architecture/ARCH-010-implementation-handoff.md)
>
> **Supersession guide:**
> [`ARCH-010 billing/lifecycle supersession map`](../architecture/ARCH-010-supersession-map.md)

This document is the **single readable product-level description** of Moda Interact's current merchant billing, entitlement and recovery-capacity behaviour.

It deliberately does not preserve the superseded ARCH-007 commercial rules. ARCH-007 remains useful as implementation/review history and for cost/safety primitives that ARCH-010 did not replace, but it is **not** the current source for merchant subscription, capacity, top-up, refund or lifecycle semantics.

If this readable page ever conflicts with ARCH-010 architecture or an active ARCH-010 task, the following order applies:

```text
active ARCH-010 task contract
        ↑ exact bounded implementation scope/status
ARCH-010 canonical architecture
        ↑ complete cross-service behaviour
this product model
        ↑ readable product explanation
historical ARCH-007/008/009 records
        ↑ evidence/history only where superseded
```

---

## 1. Merchant commercial unit

Moda Interact's primary merchant-facing capacity unit is one admitted:

```text
RECOVERY_CONVERSATION
```

A recovery conversation is not the same thing as one WhatsApp message or one CommerceAgent turn. Multiple shopper messages can belong to one admitted recovery conversation.

Message counts, CommerceAgent limits and provider/AI safety controls remain operational cost/safety mechanisms. They do not create a second merchant recovery-credit unit.

---

## 2. Current plan catalogue and authority

The initial/current target catalogue is:

| Plan | Shopify recurring price* | Paid-plan monthly included recoveries | Shop-lifetime Free grant |
| --- | ---: | ---: | ---: |
| **Free** | $0 | none | 5 once per shop |
| **Starter** | $35/month | 200/current verified billing period | 5 once per shop |
| **Growth** | $75/month | 500/current verified billing period | 5 once per shop |
| **Scale** | $149/month | 1,200/current verified billing period | 5 once per shop |

\* Shopify App Pricing is authoritative for the live commercial plan, price, currency, billing cycle and pending plan change. Moda does not treat duplicated local price data as commercial truth.

There is **no automatic paid overage** in the ARCH-010 product model.

When all spendable recovery-credit sources are exhausted, Moda blocks **new recovery admission** until capacity is restored. It does not silently create billable overage.

---

## 3. The four recovery-capacity buckets

### 3.1 Paid monthly included credits

Paid-plan included credits:

- exist only while a verified paid plan is effective;
- belong to one exact Shopify billing period;
- do not roll over;
- are forfeited when that paid period closes;
- are replenished only when Shopify verifies the next paid billing period.

### 3.2 Promotional campaigns and credits

Promotional credits are optional Moda-funded merchant offers. Admin creates a `PromotionCampaign`; the merchant sees currently-running offers for which the Shop is eligible and chooses one. Multiple campaigns may run globally, but a Shop may have only one currently selected promotion for new recovery admission.

Campaign target scope is exactly one of:

```text
GLOBAL
PLAN  -> exact BillingPlan.id
SHOP  -> exact Shop.id
```

A campaign has a fixed credit quantity and expiry. It can be closed and later reopened under the **same campaign ID** by changing only the expiry/status with audit history; reopening never replenishes a merchant who already claimed it.

The merchant receives/reuses one `PromotionalCreditGrant` per `(campaignId, shopId)` when selecting the offer. Promotional campaign credits are:

- non-refundable;
- independent of Shopify billing/App Events;
- exact campaign grant-lot capacity, not an alias for the five lifetime Free credits;
- spendable only while the selected campaign is running and the merchant remains target-eligible/executable;
- preserved as history after expiry/close/plan change;
- never automatically granted merely because a campaign exists.

For PLAN campaigns, eligibility is rechecked against the merchant's current effective mapped plan for each new recovery reservation. A reservation admitted before expiry/eligibility loss may still commit afterward.

See [ARCH-010 promotional campaigns](../architecture/ARCH-010-promotional-campaigns.md).

### 3.3 Purchased lifetime top-up credits

Purchased top-up credits:

- are merchant-funded;
- survive monthly renewal and plan changes;
- survive uninstall/reinstall, cancellation and freeze as owned balance;
- use FIFO purchase-lot accounting;
- are refundable only to the extent that a specific purchased lot remains unused and is not reserved/held for another refund;
- become spendable only after provider billing confirmation/reconciliation.

### 3.4 Shop-lifetime Free credits

Every shop receives the Free lifetime grant **exactly once** at first verified subscription activation, whether its first verified plan is Free or Paid.

Current default:

```text
5 lifetime recovery conversations
```

The grant:

- belongs to the shop, not to the Free subscription;
- never resets on upgrade or downgrade;
- never resets on cancellation, uninstall or reinstall;
- never replenishes at a Shopify billing boundary;
- remains available on a Paid plan after higher-priority credit sources are exhausted;
- is non-refundable.

Example:

```text
first activation: Free
lifetime Free granted = 5
merchant consumes 2
remaining = 3

merchant upgrades to Growth
remaining lifetime Free = 3

merchant exhausts Growth monthly allowance
then promotional/purchased capacity is considered
then the same remaining 3 lifetime Free credits can be used
```

Returning to Free later does **not** grant another five.

---

## 4. Canonical capacity-consumption order

### Paid merchant

```text
selected promotional campaign
→ current-period monthly included
→ purchased lifetime top-ups
→ shop-lifetime Free
→ BLOCK NEW RECOVERY ADMISSION
```

### Free merchant

```text
promotional
→ purchased lifetime top-ups
→ shop-lifetime Free
→ BLOCK NEW RECOVERY ADMISSION
```

Selected promotional campaign credits supersede **every** other recovery-capacity source. Purchased credits remain ahead of lifetime Free after Paid included capacity (where applicable).

### What “BLOCK NEW RECOVERY ADMISSION” means

Capacity exhaustion is **not** a global application shutdown.

When every executable capacity bucket is empty:

- a newly eligible abandoned checkout is not admitted into a new recovery conversation;
- no new recovery WhatsApp send is started for that checkout;
- the recovery is durably marked as capacity-blocked/exhausted so it can be retried when capacity returns;
- the merchant can still open the dashboard, history, usage, billing/options and support;
- an already-admitted recovery conversation continues solely because capacity later reached zero.

Capacity exhaustion is intentionally different from `FROZEN`, `NO_CONTRACT` and inactive/uninstalled states, which stop broader business execution.

---

## 5. Free plan and Shopify billing periods

The Shopify Free plan is a `$0` App Pricing plan that can still carry the recovery-credit top-up usage meter.

Therefore a Free Shopify subscription may have a current provider billing cycle/BillingPeriod used to scope App Events.

That provider BillingPeriod **does not** replenish the five lifetime Free recovery credits.

```text
Free Shopify billing cycle rolls
        ↓
close/open provider billing-period scope
        ↓
NO lifetime Free regrant
NO promotional reset
NO purchased-credit reset
```

---

## 6. Top-up purchase semantics

### Merchant product meaning

A recovery-credit top-up is presented to the merchant as a one-off purchase of additional lifetime recovery capacity.

### Shopify App Pricing mechanism

Under the current Shopify App Pricing architecture, Moda implements that product through a dedicated usage meter + App Event.

```text
merchant chooses top-up
        ↓
Moda creates durable purchase intent
        ↓
App Event submitted on current plan's top-up meter
        ↓
provider confirmation/reconciliation
        ↓
exact purchase lot becomes ACTIVE
        ↓
credits become spendable
```

A successful HTTP submission alone is not treated as final purchase confirmation.

For ARCH-010 App Pricing flows, do **not** substitute:

- `appPurchaseOneTimeCreate`;
- a local payment system;
- a local hard-coded top-up price.

Shopify remains commercial billing authority; Moda owns durable purchase intent, reconciliation, entitlement activation and idempotency.

Every plan from which top-ups may be purchased must expose the configured top-up usage meter.

---

## 7. Recovery admission and reservation

Capacity is reserved before the recovery crosses the provider/business side-effect boundary.

```text
resolve executable subscription/shop state
        ↓
resolve capacity source in canonical priority
        ↓
reserve exactly one credit
        ↓
perform recovery/provider work
        ↓
commit or safely release/reconcile reservation
```

Concurrency must not let two workers spend the same final credit.

Purchased capacity additionally identifies the exact FIFO purchase lot that funded the reservation so unused/refundable quantity remains provable.

---

## 8. Capacity restoration

A capacity-blocked recovery can become eligible again when, for example:

- a paid plan opens a new verified monthly allowance;
- a purchased top-up becomes active;
- Admin grants promotional credits;
- an appropriate verified plan change provides executable capacity.

Blocked recoveries remain durable in PostgreSQL. Redis/BullMQ wake-up jobs are coordination only and can be reconstructed.

Recovery retry always revalidates current checkout and lifecycle state before sending anything.

---

## 9. Plan changes

Plan selection/change uses Shopify's hosted App Pricing flow and Partner subscription state.

Moda distinguishes:

```text
current effective plan
pending Shopify plan update
pending effective boundary
```

Entitlements change only when Shopify verifies the effective provider state.

Upgrade/downgrade does not:

- reset lifetime Free credits;
- discard promotional credits;
- discard purchased credits;
- invent local proration;
- create automatic paid overage.

Paid monthly allowance remains period-scoped to the verified plan/cycle that granted it.

---

## 10. Cancellation and `NO_CONTRACT`

A Shopify cancellation scheduled for the end of cycle does not end current entitlement early.

When Shopify ultimately verifies that the contract has ended:

- the final provider BillingPeriod closes;
- unused paid monthly allowance is forfeited;
- promotional, purchased and lifetime Free balances are preserved;
- local subscription projection becomes `NO_CONTRACT`;
- dashboard/history/billing/support remain available;
- new shop business execution stops until another Shopify contract is verified.

A returning merchant with historical activity is not treated as a brand-new onboarding merchant merely because the current contract ended.

---

## 11. Freeze/unfreeze

`FROZEN` is a temporary Shopify/provider billing hold, not cancellation.

While frozen:

- balances and current billing-period state are preserved;
- dashboard/history/usage/billing/support remain visible;
- top-up and plan mutations are disabled;
- new recovery/WhatsApp/CommerceAgent/business execution stops;
- queued checkout/cart events terminate early after durable shop/subscription resolution;
- `order.completed` may perform only minimal terminal safety bookkeeping on already-existing recovery state.

Moda continues provider reconciliation. Access is restored only after usable live Shopify subscription state is verified again.

If the provider cycle advanced during the freeze, Moda reconciles directly to the provider-current cycle. It does not synthesize missed monthly allowances.

---

## 12. Uninstall and safe reinstall

Uninstall is an execution gate, not a billing-history reset.

On uninstall Moda preserves:

- subscription projection/history;
- BillingPeriods;
- lifetime Free usage/balance;
- promotional balance;
- purchased balance and purchase/refund history.

Reinstall does not immediately mark the shop executable. Shopify subscription truth is reconciled first.

Reinstall never regrants lifetime Free credits.

---

## 13. Partial purchased-credit refunds

Only **unused purchased top-up credits** are refundable through the ARCH-010 refund workflow.

Promotional and lifetime Free credits are not refundable.

Refundability is purchase-lot based:

```text
refundable from purchase lot
= granted
- committed
- currently reserved
- already refunded
- currently held for refund
```

ARCH-010 uses human-verified Shopify provider settlement for partial refund/credit actions. It does not automatically use negative App Events as the refund mechanism.

The local refund flow holds approved unused credits before provider settlement so concurrent recovery cannot spend the same quantity.

---

## 14. Promotional campaign operations

Admin creates optional GLOBAL/PLAN/SHOP campaigns; campaign activation itself grants no merchant credits. Merchants view currently-running eligible offers and select one. Selection creates/reuses exactly one campaign+shop allocation; the same campaign can never grant the same Shop twice.

Only one still-usable promotion can be selected per Shop. After it is exhausted, expires, closes or becomes target-ineligible, the merchant may select another eligible campaign.

Admin retains a catalogue of all campaigns and may close/reopen the same campaign. Reopen changes only expiry/status and preserves campaign ID, targeting, quantity and merchant usage history.

Merchant and Admin history are derived from campaign-linked `PromotionalCreditGrant` records, not the aggregate promotional entitlement counter. Promotional usage generates no Shopify App Event and is excluded from purchased-credit refundability.

## 15. Lifecycle states are not interchangeable

The following states have deliberately different behaviour:

| State | New recovery admission | Existing admitted conversation | Merchant dashboard/history | Owned lifetime balances |
| --- | --- | --- | --- | --- |
| **Capacity exhausted** | blocked | continues | available | preserved |
| **FROZEN** | blocked | business execution paused | available/read-only where required | preserved |
| **NO_CONTRACT** | blocked | business execution stopped | available | preserved |
| **UNINSTALLED/inactive** | blocked | business execution stopped | not normal merchant execution | preserved |
| **Billing-period DRAINING** | period-bound/billable mutations restricted; non-period lifetime sources may still be usable per ARCH-010 | existing admitted work handled under boundary rules | available | preserved |

Never use a generic `blocked` flag as a substitute for these distinct lifecycle states.

---

## 16. Shopify event handling while non-executable

Webhook ingress remains thin:

```text
Shopify webhook
→ authenticate / validate / normalise
→ enqueue
→ acknowledge
```

The subscription/shop execution gate belongs in Background after tenant identity is known.

For a frozen shop specifically:

- checkout/cart business events no-op early before recovery/candidate work;
- `order.completed` may only close/cancel already-existing recovery state as terminal safety bookkeeping;
- no new recovery, conversation, billing reservation, CommerceAgent turn or outbound WhatsApp work may be created.

---

## 17. Repository ownership

| Repository | Current ARCH-010 responsibility |
| --- | --- |
| `moda-interact-database` | subscription/lifecycle state, BillingPeriods, entitlement counters, purchase lots, refunds, promotional grants, constraints/indexes |
| `moda-interact-shared` | versioned cross-service reconciliation/refund contracts and shared primitives |
| `moda-interact` | merchant onboarding, dashboard, billing/options UI, Shopify hosted plan-selection integration, current/pending provider read model |
| `moda-interact-admin` | internal policy/configuration, promotional grants/campaigns, partial-refund triage/settlement evidence |
| `moda-interact-background` | subscription reconciliation, BillingPeriod transitions, capacity reservation, recovery gates, App Event publication/reconciliation, resume logic |
| `moda-interact-gateway` | runtime Redis/environment wiring required by billing workers |
| `moda-interact-messaging` | provider ingress/normalisation only; does not decide merchant entitlement |
| `moda-interact-system-test` | terminal/manual-gated cross-service lifecycle validation |
| `moda_architect` | cross-repository invariants, task sequencing and architectural acceptance |

---

## 18. Retired/superseded billing concepts

The following concepts can still appear in historical ARCH-007 records, but they are **not current ARCH-010 product rules**:

```text
automatic paid recovery overage
Free lifetime allowance owned/reset by the Free plan
Free allowance adjustments as campaign/test credits
Free capacity order: lifetime Free -> purchased
Paid capacity order: included -> purchased -> overage
activeSubscription=null automatically means canceled
uninstall clears owned entitlement/history
full-pack-only purchased-credit refund
negative App Event as the normal partial-refund mechanism
Moda-initiated App Pricing cancellation
```

For an exact old→new mapping, see:

[`ARCH-010 billing/lifecycle supersession map`](../architecture/ARCH-010-supersession-map.md).

---

## 19. Implementation status

ARCH-010 architecture is **Agreed / implementation-ready**, not yet fully implemented.

Exact task state lives in:

```text
docs/decisions/*/ARCH-010/_index.md
docs/decisions/*/ARCH-010/*.md
docs/architecture/ARCH-010-implementation-handoff.md
```

System-test tasks are terminal/manual-gated and do not block implementation work from starting.

Historical ARCH-007 task files remain valid evidence of what was implemented/reviewed at that stage, but their superseded merchant billing semantics must not override ARCH-010.


### Upgrade economics Admin guardrail

Moda Admin applies a structural commercial guardrail before activating economics-affecting plan/top-up configuration. By default, staying on a lower tier and buying the cheapest required recovery-pack capacity to reach the explicitly configured next tier's **monthly included recovery allowance** must cost at least 20% more than upgrading. Shopify remains pricing/charging authority; Moda stores audited verified economics snapshots only for Admin validation.

This calculation never includes one-time lifetime-Free credits, promotional campaigns, purchased-credit balances, refunds or merchant-specific current usage. `FAIL` and `UNVERIFIED` both block the Admin mutation server-side.
