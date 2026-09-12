# ARCH-010 Billing and Merchant-Lifecycle Supersession Map

Date: 2026-09-12
Owner: `moda_architect`

## Purpose

This document exists to prevent historical ARCH-007/008/009 billing assumptions from being mistaken for the current Moda Interact merchant contract.

The repository intentionally retains older architecture/task files as implementation and review evidence. Retention does **not** make superseded product semantics current.

For current merchant billing/lifecycle behaviour use, in order:

1. [`ARCH-010 first-production baseline`](ARCH-010-first-production-baseline.md);
2. the exact active `ARCH-010-*` task being implemented;
3. [`ARCH-010 — Merchant lifecycle state transitions and behavioural access`](ARCH-010-merchant-lifecycle-state-transitions.md);
4. [`Pricing, billing and recovery-capacity model`](../product/pricing-and-billing-model.md);
5. [`ARCH-010 implementation handoff`](ARCH-010-implementation-handoff.md).

## Superseded concepts

| Historical concept that may still appear | Current ARCH-010 rule |
| --- | --- |
| Paid included credits flow into normal automatic overage | **No automatic paid overage.** After all executable credit buckets are exhausted, block **new recovery admission**. |
| Free capacity order = lifetime Free → purchased → block | Free capacity order = **promotional → purchased → lifetime Free → BLOCK NEW RECOVERY ADMISSION**. |
| Paid capacity order = included → purchased → overage | Paid capacity order = **selected promotion → monthly included → purchased → lifetime Free → BLOCK NEW RECOVERY ADMISSION**. |
| “Block” means stop the whole app | Capacity exhaustion blocks **new recovery admission only**. Existing admitted conversations continue; dashboard/history/billing/support remain accessible. |
| Five Free credits are a Free-plan allowance | They are a **shop-lifetime grant**, issued once at first verified activation whether first plan is Free or Paid. |
| Returning/downgrading to Free grants another five | Never. Plan changes do not reset/regrant the shop-lifetime Free counter. |
| Testing/support should adjust the shop-lifetime Free entitlement | Never mutate the lifetime grant for discretionary credit. Use a merchant-selected campaign-linked `PromotionalCreditGrant`; `LIFETIME_FREE_RECOVERY_CREDITS` remains immutable apart from normal reservation/commit/release consumption. |
| Promotional/test credits are effectively extra Free allowance | Promotional credits are independent and non-refundable; **new first-release promos are expiring merchant-selected GLOBAL/PLAN/SHOP campaigns** governed by `ARCH-010-promotional-campaigns.md`. |
| Purchased credits are consumed before promotional credits | Promotional credits are consumed first, preserving merchant-funded refundable purchased capacity. |
| Free plan has no BillingPeriod | A `$0` App Pricing plan may still have a provider BillingPeriod because it carries the top-up usage meter. That period never resets lifetime Free credits. |
| Top-up should use `appPurchaseOneTimeCreate` | Under the current App Pricing design, use the dedicated **usage meter + App Event** and reconcile provider confirmation before activating credits. |
| A successful App Event HTTP response means credits are confirmed | Submission is asynchronous. Credits become spendable only after provider reconciliation/confirmation. |
| Purchased credits can be tracked only as one aggregate balance | ARCH-010 adds **FIFO purchase-lot accounting** so partial unused-credit refunds are provable. |
| Refund only a complete pack | Refunds can cover an explicit unused quantity from a purchase lot, subject to reservations/previous refunds/holds. |
| Use a negative App Event as the normal partial-refund mechanism | ARCH-010 uses human-verified Shopify provider refund/credit settlement plus exactly-once local finalisation. |
| `activeSubscription = null` proves cancellation | Not for an established merchant. Reconcile live Partner state with provider lifecycle/Historical Events; `FROZEN` is distinct from `CANCELED`. |
| Cancellation and downgrade-to-Free are equivalent | They are distinct. Downgrade retains an executable Free contract; effective cancellation produces `NO_CONTRACT`. |
| Moda should initiate App Pricing cancellation with `appSubscriptionCancel` | ARCH-010 observes/reconciles Shopify cancellation; it does not initiate cancellation through that mutation. |
| Plan change should use `appSubscriptionCreate` / `replacementBehavior` | Current App Pricing plan changes use Shopify-hosted plan selection plus Partner `activeSubscription` / `pendingUpdate`. |
| `APP_SUBSCRIPTIONS_UPDATE` drives App Pricing state | Current ARCH-010 App Pricing flow uses redirects for merchant plan selection and Partner reconciliation/Historical Events for out-of-band lifecycle changes. |
| Uninstall should clear subscription/credits/history | Uninstall is an **execution gate**. Owned balances/history are preserved and reinstall reconciles Shopify before execution resumes. |
| Frozen subscription is the same as capacity exhaustion | `FROZEN` blocks broad business execution; capacity exhaustion blocks only new recovery admission. |
| Stop Shopify webhooks at HTTP ingress for frozen shops | Ingress still authenticates/normalises/enqueues quickly. Background stops checkout/cart business processing after durable tenant/lifecycle resolution; `order.completed` may perform minimal terminal safety bookkeeping. |

## What remains valid from ARCH-007

ARCH-007 is not discarded. It contains completed implementation/review evidence and primitives that remain useful unless a later task explicitly replaces them, including areas such as:

- durable/idempotent usage infrastructure;
- outbound WhatsApp cost/safety admission;
- fragmented inbound-message coalescing;
- abuse admission and provider-status handling;
- historical migrations and accepted task evidence.

The supersession boundary is specifically the **merchant subscription, entitlement, recovery-capacity, top-up, refund and lifecycle contract** now owned by ARCH-010.

## Historical-document rule

Historical ARCH-007 architecture, handoff, task and review files are retained. They carry an ARCH-010 supersession notice so a reader knows their old billing semantics are context/history only.

Do not rewrite their accepted Completion Reports as though ARCH-010 had existed at the time. Use the current ARCH-010 architecture/task files to implement new behaviour.


## Promotional campaign amendment (2026-09-12)

| Earlier ARCH-010 promotional rule | Current first-release rule |
|---|---|
| Direct Admin promotional grant becomes lifetime shop capacity | Admin creates optional GLOBAL/PLAN/SHOP `PromotionCampaign`; merchant must select it before a campaign-linked allocation becomes spendable. |
| Paid included → promotional → purchased → lifetime Free | **Selected promotional campaign → Paid included → purchased → lifetime Free**. |
| Promotional credits do not expire | Campaign offer/allocation is spendable only while campaign is running and merchant remains target-eligible; existing admitted reservations may commit afterward. |
| Repeating campaign means another grant | Reopen keeps the **same campaign ID** and only changes expiry/status; an existing merchant claim is never replenished. |

## First-production baseline amendment (2026-09-12)

The following intermediate development concepts are now removed rather than preserved for compatibility:

| Intermediate development concept | First-production ARCH-010 rule |
|---|---|
| `BILLING_FREE_ALLOWANCE_EXHAUSTED` historical renderer/parser | Removed before first production. Use `BILLING_RECOVERY_CAPACITY_EXHAUSTED` for both Free and Paid full-capacity exhaustion. |
| `BillingPlan.freeLifetimeConversationAllowance` | Removed. `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` is snapshotted once into `ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS)`. |
| `BillingAllowanceAdjustment` / signed Free adjustments | Removed. No compatibility arithmetic or discretionary grant path exists. |
| `FREE_RECOVERY_LIFETIME` enum/name | Removed; canonical enum is `LIFETIME_FREE_RECOVERY_CREDITS`. |
| aggregate `ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)` | Removed. Exact selected campaign `PromotionalCreditGrant` lot is promotional accounting/spendability authority. |
| campaign-less/direct `PromotionalCreditGrant` | Removed from first-production schema; `campaignId` is required. |
| `MIGRATION_RECONCILED` | Removed. DATABASE-013 is generated from an empty database; development BillingPeriod normalization is not production migration history. |
| local `SubscriptionCancellationRequest` state machine | Removed. Shopify lifecycle evidence + reconciliation is cancellation authority. |
| `RecoveryCreditPurchaseStatus.REFUNDED` | Removed. Partial refund keeps purchase `ACTIVE` and records refunded quantity/history. |
| negative/fractional App Event refund correction | Removed. Human Shopify Partner Dashboard `REFUND | CREDIT` settlement plus local exactly-once finalisation is canonical. |

Completed DATABASE-001..011 and other completed task files remain accepted development history; these removals are implemented by DATABASE-013 and dependent runtime conformance work rather than reopening those completed task records.
