---
id: ARCH-077
title: Shopify-owned WhatsApp checkout consent through cart and checkout Redis state
status: proposed
coordinator: moda_architect
created: 2026-11-17
updated: 2026-11-17
---

# ARCH-077 — Shopify-owned WhatsApp checkout consent

> **DRAFT 1 — definition-only patch for iterative architect review.** No implementation or production activation is authorised by applying these documents. Every task starts `pending`; review SHOPIFY-001 first, then reconcile dependants before moving any task to `ready`.

## Problem and agreed boundaries

In the production Shopify test, `AbandonedCheckout.customer.id` existed but `customer.phone` and `customer.defaultPhoneNumber` were null while both checkout address phone fields were populated. The current Background pipeline found the abandoned checkout but returned `deferred-no-recipient`. Its Shopify consent path depends on Shopify's **native WhatsApp marketing consent**, which the user does **not** want to use for Moda's own Meta sender integration.

- Shopify application `moda-interact` owns the storefront/cart, checkout and authenticated Shopify consent-producer implementation; `moda-interact-background` owns cart-to-checkout association, maturity, recipient verification and all outbound enforcement.
- `moda-interact-api` remains WooCommerce-facing; `moda-interact-woocommerce` remains unchanged. Do not create Shopify endpoints in the Woo API.
- No PostgreSQL schema change, migration, new consent table or enum change is authorised in ARCH-077. In particular, never claim a Moda checkbox is a `SHOPIFY_NATIVE` Shopify-provider observation or insert Shopify evidence into the Woo-installation-bound `commerce.WhatsAppConsentEvidence` table.
- Reuse **only the customer-facing wording and its translated meaning** from WooCommerce; implementation and translation catalogues are platform-owned. English: **Send me WhatsApp shopping updates, reminders and offers.** The consent purpose is checkout-recovery marketing, not unrestricted campaigns.
- The initial affirmative *choice* is made by the shopper on the cart or checkout. **Recovery-specific materialisation occurs only when the checkout becomes recoverable**; Background cannot create permission that was never affirmatively selected.
- No second phone field on the cart page. A shipping/billing number is a potential checkout recipient, **not** independent evidence that the number's user opted in. Identity and recipient-binding failures deny proactive sends.
- Returning **authenticated** Shopify customer on a *new* cart must be able to see an existing verified preference and opt out. Guests with a new cart are not identified by phone/email alone.
- Existing merchant inactivity delay, Shopify abandoned verification retries, payment/completion cancellation, STOP, billing, moderation, credits, ARCH-076 sender routing and normal two-proactive-message cap remain unchanged.

## Two presentation flows

**A — Non-Plus cart page:** Theme App Extension retrieves the current cart token, sends a deliberate choice to the authenticated Shopify backend, which writes separate Redis consent state. A *verified* `checkouts/create` event containing `shopId + cartToken + checkoutToken` associates cart consent with checkout consent. The webhook is not required to arrive before the checkbox action. On revisit, the app reads the current cart state; on a new cart with a verified logged-in customer, it may show the separately established customer preference and allow withdrawal under the frozen policy.

**E — Shopify Plus checkout:** Checkout UI Extension obtains verified checkout context; backend writes consent directly to checkout-keyed Redis state. No intermediate cart association required. The customer can revisit and withdraw.

Both flows MUST be verified against real Shopify plan/extension capabilities and tokens before implementation claims success. Express/accelerated checkout and unsupported routes are explicitly ineligible if the consent UI or verifiable identity association is absent.

## Redis ownership and cross-application invariant

Background already owns `pending-recovery:index:checkout:*`, `pending-recovery:index:cart:*`, `pending-recovery:index:shop:*`, `pending-recovery:lock:*`, `pending-recovery:order-completed:*`, BullMQ queue metadata and payloads. These indexes point to jobs, coordinate order completion and drive worker rescheduling/cancellation. **Never reuse or change their values/TTL/cleanup rules for consent.**

Proposal, **not yet frozen**: versioned `shopify:consent:v1:*` namespace for cart, checkout, customer preference, history and cart↔checkout association. All raw tokens/customer identifiers in Redis key names must use the same bounded keyed-digest algorithm in Shopify and Background; no raw token logging. Scope by verified shop. Source action identity, explicit GRANT/REVOKE, monotonic revision, displayed locale/text/version and customer/checkout binding evidence must be retained. A regular cart or checkout webhook is **not** a consent grant. Repeated/out-of-order actions, cross-tab races, cart token changes, customer transitions and checkout alias conflicts must not resurrect a revoked grant.

TTL and retention must be independent of pending-candidate TTL, at least cover checkout lifetime and permitted follow-ups, and address evidence retention for returning-customer preferences. Redis outages, eviction or missing evidence fail closed. Redis memory/persistence/backup impact on existing queues is a release criterion. Do not scan global keys.

## Existing PostgreSQL final-send constraint — mandatory gate

Current `commerce.CustomerPhone` is the sole durable consent-state authority in ARCH-045/046 and accepts only `SHOPIFY_NATIVE` / `WOO_MODA_CHECKBOX`. The existing Shopify `RecoveryStoredConsentService` and `checkFinalStoredRecoveryConsent` in `recovery-stored-consent.service.ts` demand a `SHOPIFY_NATIVE` row and revisions. Redis-only Moda checkbox consent is therefore **not compatible with the current final SQL permit as-is**. The new design deliberately changes the Shopify *proactive* consent authority to verified checkout Redis evidence, with PostgreSQL still authoritative for STOP, shop/recipient ownership, suppression and other final checks. This cross-store boundary **is not yet proven safe**.

**Architect acceptance gate:** Define and integration-test a concrete coordination protocol such that an acknowledged withdrawal prevents any provider send initiated afterward; a send already irreversibly accepted by Meta cannot be recalled. Never fetch Redis while holding the current short SQL final-send transaction; also never simply remove that SQL consent fence without an equivalent reviewed safety protocol. If that guarantee cannot be proven with the unchanged schema, report the blocker rather than ship a weaker guard.

Consent record ownership across Redis and PostgreSQL must be kept explicit. Do not use `SHOPIFY_NATIVE` as a false synonym for a Moda checkbox; do not silently mutate legacy Shopify native records. STOP remains authoritative regardless of checkbox selection.

## Open decisions for sequential review (not delegated to agents)

1. Exact cart token normalisation/alias proof between `/cart.js`, authenticated cart webhooks and checkout webhooks; handling Shopify cart regeneration and accelerated paths.
2. Checkout-scoped grant versus ongoing merchant/customer preference: scope and whether a verified earlier grant authorises a **new** checkout without a fresh action, while still showing an opt-out control. Do not decide by implication.
3. Verified checkout recipient when opt-in occurs before a number is entered; address-phone ownership and mismatched shipping/billing phone behaviour.
4. Shopify authenticated session/proof design for guest cart actions, and signed checkout-extension context for Plus.
5. Redis record and evidence retention, eviction policy, persistence guarantees, privacy/erasure and verifiable returning-customer status.
6. Atomic revision/withdrawal coordination with pending jobs and SQL/provider dispatch, including preflight and multipart/follow-up delivery.
7. Native-consent retirement and treatment of preexisting `SHOPIFY_NATIVE` PostgreSQL projections and queued sync jobs.

## Task register

| Task | Owner | Draft dependency | Scope |
| --- | --- | --- | --- |
| [SHOPIFY-001](../decisions/shopify/ARCH-077/SHOPIFY-001-freeze-shopify-identity-and-redis-contract.md) | Shopify | none | Freeze identity, Redis contract and review gates |
| [SHOPIFY-002](../decisions/shopify/ARCH-077/SHOPIFY-002-capture-checkout-consent-in-redis.md) | Shopify | S001 | Shopify-authenticated writer/read/status/withdrawal |
| [SHOPIFY-003](../decisions/shopify/ARCH-077/SHOPIFY-003-render-cart-page-consent.md) | Shopify | S002 | Theme App Extension cart UI |
| [SHOPIFY-004](../decisions/shopify/ARCH-077/SHOPIFY-004-render-plus-checkout-consent.md) | Shopify | S002 | Plus Checkout UI Extension |
| [SHOPIFY-005](../decisions/shopify/ARCH-077/SHOPIFY-005-returning-customers-withdrawal-and-locales.md) | Shopify | S003/S004 | Returning customers, merchant settings, 20 locales |
| [BACKGROUND-001](../decisions/background/ARCH-077/BACKGROUND-001-associate-cart-consent-with-checkout.md) | Background | S001/S002 | Cart↔checkout Redis association |
| [BACKGROUND-002](../decisions/background/ARCH-077/BACKGROUND-002-gate-recovery-and-final-dispatch-by-consent.md) | Background | B001 | Admission, recipient and final-send gates |
| [SYSTEM-TEST-001](../decisions/system-test/ARCH-077/SYSTEM-TEST-001-certify-shopify-consent-and-redis-isolation.md) | System test | implementations | Provider/browser, Redis race and worker regression certification |
| [SHOPIFY-006](../decisions/shopify/ARCH-077/SHOPIFY-006-retire-native-whatsapp-consent-integration.md) | Shopify + Background | certification | Remove obsolete native consent ingress/sync |

## Implementation/review protocol

- These are **architect-owned task-definition files** only, all `pending`; no automatic worktree launch, code change, database change or production rollout.
- Agents must inspect the then-current repository and pinned Shared contracts before implementation; paths below are verified touchpoints from the 2026-11-16 snapshot and may change by execution.
- Preserve original provider/SDK error messages and structured details in redacted server-side logs; no swallowed exceptions or new Redis queries just for diagnostics.
- Tests must state static/code-review evidence separately from executed disposable PostgreSQL/Redis, browser/Shopify and Meta provider evidence. No fabricated test results.
- No edits to `docs/decisions/**/_index.md` until the final reconciliation is requested. Only after a task is accepted should coordinator modify dependency/status metadata and authorise implementation.
