# ARCH-010 — Shopify

| Task | Status | Purpose |
|---|---|---|
| ARCH-010-SHOPIFY-001 | Complete | Establish fresh-install `NO_CONTRACT` state, render merchant onboarding at `/app`, and fail closed on product/usage surfaces until plan activation. |
| ARCH-010-SHOPIFY-002 | Ready | Persist Free-plan selection intent, verify current Shopify subscription, preserve/create exact provider Free BillingPeriod when available, and publish durable-reconstructable reconciliation work when activation/cycle verification is unresolved. |
| ARCH-010-SHOPIFY-003 | Pending | Activate a first verified paid plan only with exact Shopify cycle/meter state and atomically create the first paid BillingPeriod plus included-credit counter. |
| ARCH-010-SHOPIFY-004 | Pending | Present current paid-period included entitlement and lifetime top-ups on merchant billing/usage surfaces without exposing Admin. |
| ARCH-010-SHOPIFY-005 | Superseded | Replaced by SHOPIFY-006 so uninstall preservation and fail-closed reinstall entry cannot be deployed as an unsafe split change. |
| ARCH-010-SHOPIFY-006 | Pending | Preserve billing state on uninstall, keep reinstall execution-disabled, publish reconciliation work, and expose only the merchant restoration/support surface until Background verifies Shopify truth. |
| ARCH-010-SHOPIFY-007 | Pending | Present Free/Paid App Pricing drain/reconciliation state and block new top-up purchase in the closing/expired provider cycle; Free lifetime recovery entitlement does not reset or pause solely for cycle rollover. |
| ARCH-010-SHOPIFY-008 | Pending | Present recovery-capacity exhaustion on the normal dashboard/history and route merchants to the real capacity screen without restricting read access. |
| ARCH-010-SHOPIFY-009 | Pending | Add the PostgreSQL-only recovery-capacity projection using selected-campaign spendability first: Paid promo -> included -> purchased -> lifetime Free / Free promo -> purchased -> lifetime Free. |
| ARCH-010-SHOPIFY-010 | Pending | Present the real SHOPIFY-014 recovery top-up lifecycle in `TopUpPurchasePanel` without mock/local price authority or legacy one-time-charge APIs. |
| ARCH-010-SHOPIFY-011 | Pending | Present Shopify-authoritative current/pending subscription state and route plan management through the SHOPIFY-015 hosted plan-change flow. |
| ARCH-010-SHOPIFY-012 | Pending | Integrate `/app/billing/options` by composing Shopify commercial truth, Moda capacity, real top-up lifecycle and real Shopify-hosted plan-change actions; remove mock authority. |
| ARCH-010-SHOPIFY-013 | Complete | Extend provider/service contract to expose Shopify-authoritative current/pending flat-rate state plus active usage-item pricing/usage needed by top-up billing. |
| ARCH-010-SHOPIFY-014 | Pending | Expose the server-side top-up purchase lifecycle for both Free and Paid using the exact current provider/local BillingPeriod and accepted App Events mechanism. |
| ARCH-010-SHOPIFY-015 | Pending | Handle Shopify-hosted plan-change return, classify current vs pending provider state, schedule reconciliation, and never mutate effective entitlement in the HTTP callback. |
| ARCH-010-SHOPIFY-016 | Pending | Present scheduled/effective Shopify cancellation, keep onboarded NO_CONTRACT merchants on dashboard/history, disable top-ups/business execution, and never expose local cancellation authority. |
| ARCH-010-SHOPIFY-017 | Pending | Present unused purchased-credit refund policy and route merchants to support without self-service provider money movement. |
| ARCH-010-SHOPIFY-018 | Ready | Expose Shopify-authoritative subscription lifecycle state by combining activeSubscription with latest bounded Partner subscription-status event. |
| ARCH-010-SHOPIFY-019 | Pending | Keep frozen merchants on dashboard/history, show Shopify billing-pause guidance and disable top-up/plan/product mutations until restoration. |
| ARCH-010-SHOPIFY-020 | Pending | Present the currently selected promotion, expiry/remaining allocation and promo-first capacity ordering without exposing internal Admin provenance. |
| ARCH-010-SHOPIFY-021 | Pending | List every currently-running GLOBAL/PLAN/SHOP promotion available to the merchant and transactionally select one campaign exactly once. |
| ARCH-010-SHOPIFY-022 | Pending | Show tenant-safe merchant promotion selection/use history, including exhausted/expired/closed/reopened states. |

Authority split:

- Shopify Partner `activeSubscription` is commercial subscription authority.
- `BillingPlan` is a Moda entitlement/configuration mapping keyed by Shopify plan handle, not the Shopify plan catalogue.
- `SHOPIFY-009` reads local counters only for runtime/dashboard recovery capacity.
- `SHOPIFY-013` reads Shopify current/pending commercial subscription state for billing-management UI.
- `SHOPIFY-012` composes both; it must not fall back to local `BillingPlan` as live Shopify commercial truth when Partner verification fails.

`SHOPIFY-010` and `SHOPIFY-011` deliberately isolate the prototype child components before `SHOPIFY-012` integrates them into the real route. `SHOPIFY-008` waits for `SHOPIFY-012` so an exhaustion warning never sends a merchant to a mock capacity page.

`SHOPIFY-003` deliberately depends on paid Background admission/reconciliation readiness and DATABASE-004 period history so a merchant is not opened onto paid product access before rollover semantics exist. `SHOPIFY-006` supersedes SHOPIFY-005 and must be deployed only after DATABASE-003 and BACKGROUND-006 are available. `SHOPIFY-007` is the merchant-only presentation/server guard for the five-minute drain and overdue rollover state; it does not perform rollover itself.

Billing-action ownership:

- Recovery top-ups are merchant-semantic one-off capacity purchases but remain Shopify App Pricing **App Events**, not Billing API `appPurchaseOneTimeCreate`.
- SHOPIFY-014 owns merchant-server top-up lifecycle/read/action semantics; Background remains activation authority after provider confirmation.
- SHOPIFY-015 owns hosted plan-change initiation/return classification; BACKGROUND-010 owns effective entitlement transition.
- Neither child UI component computes Shopify proration, creates subscriptions, or directly calls provider billing APIs.

Free top-up invariant: a Free plan may carry the recovery-credit-pack usage meter and therefore has a Shopify usage-billing cycle. Its local BillingPeriod is commercial/App-Event scope only; the five Free recoveries remain lifetime and never reset.

Cancellation authority: SHOPIFY-016 reads Shopify commercial cancellation state through SHOPIFY-013 and local NO_CONTRACT/capacity state through SHOPIFY-009. It MUST NOT call `appSubscriptionCancel`; BACKGROUND-012 owns provider reconciliation and BACKGROUND-013 owns post-cancellation execution blocking.
Refund ownership: SHOPIFY-017 is informational/support-only. Merchant UI never performs provider money movement or accesses Admin. ADMIN-002/003 own human triage/settlement; DATABASE-007/BACKGROUND-014 own lot/accounting safety.


Freeze authority: `SHOPIFY-018` augments commercial `SHOPIFY-013` truth with Partner Historical Events. FROZEN is not cancellation, exhaustion or onboarding. `SHOPIFY-019` owns merchant presentation; server actions in SHOPIFY-014/015 remain fail-closed while frozen.

Final merchant capacity order is Paid **selected promotion -> included -> purchased -> lifetime Free**, or Free **selected promotion -> purchased -> lifetime Free**. Campaign/selection state is local Moda entitlement state, never Shopify commercial authority.
