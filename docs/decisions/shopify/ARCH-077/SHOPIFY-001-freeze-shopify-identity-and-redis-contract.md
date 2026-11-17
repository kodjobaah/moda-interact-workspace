---
id: ARCH-077-SHOPIFY-001
architecture_id: ARCH-077
title: Freeze Shopify consent identity and Redis contract
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-11-17
updated: 2026-11-17
---

# Freeze Shopify consent identity and Redis contract

## Architecture

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Draft, pending architect review; definition work only, not executable implementation approval.**

## Objective

Freeze the Shopify cart, checkout and authenticated customer identities and exact Redis contract before any Shopify or Background writer/reader is built. This is a proof gate, not an invitation to infer a correlation mechanism.

## Existing touchpoints for inspection (do not change runtime in this draft)

- `shopify.app.moda-interact.toml` (current cart/checkout webhook subscriptions and Shopify API version).
- `app/services/webhooks/checkout-normalization.ts` (`checkoutToken` and `cartToken`).
- `app/services/webhooks/cart-activity-normalization.ts` (cart `token`, `isEmpty`).
- `app/services/webhooks/shopify-webhook-ingress.service.ts` and `app/services/webhooks/shopify-webhook-queue.server.ts` (authenticated producer and BullMQ publication).
- Background's `src/domain/pending-recovery-candidate.ts` and `src/services/pending-recovery-candidate/candidate-index.store.ts` (existing Redis index ownership).

## Requirements

### 1. Consent scope and decisions — frozen business rules

- [ ] **Merchant-scoped customer permission:** An explicit opt-in is the customer's permission to receive the merchant's WhatsApp shopping updates, reminders and offers. It is **not limited to the cart or checkout on which the customer selected the checkbox**. For a reliably identified Shopify customer, the permission can authorise later eligible checkouts at the same merchant without another selection. Do not extend permission across merchants.
- [ ] **Cart/checkout correlation, not permission ownership:** The cart and checkout tokens connect the initial selection to the correct recoverable checkout. They are not the permanent customer identity and must not become competing independent permission authorities.
- [ ] **Explicit action precedence:** Within the same authenticated merchant/customer scope, the latest *accepted deliberate* action determines the current decision. An explicit new `GRANT` after a `REVOKE` reauthorises subsequent eligible outreach; a later `REVOKE` withdraws permission notwithstanding any earlier grant on another checkout. A duplicate, replayed or delayed old grant must not overwrite a later accepted withdrawal. Ordinary cart/checkout webhooks, page loads and unchecked defaults are **not** consent actions.
- [ ] **Deferred recovery materialisation:** Store an acknowledged selection and, when customer identity is established, its current customer-level preference in Redis as soon as the user acts. Only when an abandoned checkout is independently verified as recoverable does Background link the verified current permission and selected recipient to recovery admission and existing `Customer`/`CustomerPhone` identity as appropriate. Materialisation must never manufacture a grant. Do not create consent by detecting a cart, checkout or phone number.
- [ ] **No new SQL contract:** Do not add a database model, field, enum value, migration or table; do not insert Moda-owned Shopify evidence into Woo-only `WhatsAppConsentEvidence`, or claim Shopify-native provider observation by writing `SHOPIFY_NATIVE`. Current shopper preference and checkout consent evidence are Shopify-owned Redis facts under this initiative; any interaction with existing SQL records must respect their current constraints and preserve STOP.

### 2. Shopify cart and checkout correlation — verified event identities

- [ ] **Cart-page action:** Bind the selection to the authenticated Shopify shop and the shopper's current cart token obtained through the supported Ajax Cart API. Verify the actual relationship among `/cart.js` token, authenticated `carts/create/update` webhook `token`, and authenticated `checkouts/create/update` webhook `cart_token` using real development-store evidence. Do not assume byte-identical token strings without proof; never log raw tokens.
- [ ] **Checkout transition:** A verified checkout event supplies `shopId + cartToken + checkoutToken`; associate the applicable cart selection with that checkout. Support `carts/create` arriving after an action, checkout-created arriving before a cart action, duplicated events and cart regenerations without losing the latest accepted decision. A token correlation may establish checkout association but may not silently override the current customer preference.
- [ ] **Conflict:** If a cart token appears to map to incompatible checkout identities, do not mint consent for multiple unrelated checkouts. Specify a deterministic bounded resolution using authenticated Shopify identity, or deny the ambiguous association. Do not match unrelated checkouts by email, phone, product contents or timestamps.
- [ ] **Shopify Plus:** Verify the supported Checkout UI Extension target, signed session token and checkout-token availability, then associate a selection directly with the checkout identity. No intermediate cart alias is needed. Record unsupported/accelerated checkout paths explicitly.

### 3. Returning customer on a new cart

- [ ] **Verified returning identity:** Obtain a shop-scoped authenticated Shopify customer ID through an appropriate verified Shopify context (e.g. signed App Proxy `logged_in_customer_id` where supplied, or verified checkout extension identity). Use `shopId + Shopify customer ID` to retrieve the existing preference even where the new cart token differs from the prior visit.
- [ ] **Status and opt-out:** A returning authenticated customer with a current verified grant must be able to see the already-selected state and explicitly uncheck to withdraw. The withdrawal updates the customer's current permission, not just the new cart, and applies to earlier checkouts with pending proactive messages. Do not silently regrant on page load.
- [ ] **Initial identity unknown:** A guest can select a checkbox tied to the current verified cart/checkout; establish customer identity later only from the authoritative checkout/customer association. A guest starting a separate new cart without verified continuity must not inherit a previous guest's permission from matching contact details. If a customer cannot be identified, preserve only the verified checkout-scoped evidence until identification or expiry.

### 4. Recipient selection at recoverable checkout

- [ ] **No phone field on cart:** Consent is collected before Shopify necessarily knows the customer's number. It is logically the customer's permission, not a checkbox grant for a hard-coded phone value. At recovery maturity, read the authoritative Shopify abandoned checkout using the existing lookup and resolve an available contact candidate in this priority: **customer phone → billing phone → shipping phone**.
- [ ] **Normalisation and association:** Normalise the chosen phone under the published Shared international phone contract and associate it with the correctly identified shop/customer/recovery using existing models when possible. An invalid first-preference number must not become an authorised recipient; document whether a lower-priority valid number can then be used. A shipping number supplied for a different person must not be treated as that person's opt-in solely because it appeared on the address; classify unsupported identity evidence and deny that recipient.
- [ ] **Multiple numbers:** Do not automatically reject a checkout merely because customer, billing and shipping phone fields differ; use the frozen priority to select the first eligible customer-associated number. No Shopify-native WhatsApp marketing-consent read, Shopify Messaging dependency, or `customer.defaultPhoneNumber.whatsAppMarketingConsent` requirement.
- [ ] **STOP:** Even a newly accepted checkbox `GRANT` must never clear an authoritative customer STOP, existing no-contact restriction or independently established outbound eligibility block.

### 5. Redis contract, isolation and retention

- [ ] Freeze the versioned Shopify-only key namespace and exact encoding for cart choice, checkout correlation, verified customer preference, immutable action/history evidence and revisions. Provide cross-application digest/key test vectors without exposing raw cart, checkout or customer IDs in keys or logs. Shopify and Background must use identical versioned semantics and safe deployment ordering.
- [ ] Use one current shop/customer decision and an ordered action history; cart/checkout records are association evidence, not contradictory separate customer-level current states. Define idempotent retries, monotonic accepted revisions, bounded atomic Redis updates and explicit behaviour when writes/read results arrive out of order. **Do not introduce a distributed-lock framework solely for checkbox selections.**
- [ ] Define retention of cart/checkout evidence through the configured recovery lifetime and all permitted outreach/follow-ups; define retention of the merchant/customer preference and consent evidence appropriate to ongoing permission, privacy and opt-out duties. Do **not** inherit short-lived pending-recovery index TTLs. Missing, corrupt or evicted proof must not be interpreted as `GRANTED`.
- [ ] Inspect current shared `REDIS_URL`/DB/ACL, memory budget, eviction/persistence/backup policies and worker cleanup. Introduce no new global Redis setting without an explicit impact assessment. Never repurpose, overwrite, delete, extend TTLs of or scan Background-owned `pending-recovery:index:*`, `pending-recovery:lock:*`, `pending-recovery:order-completed:*` or BullMQ-managed keys.
- [ ] Document shopper-side checkout-unavailable behaviour: accepting a choice requires successful Redis acknowledgement, but cart/checkout must remain usable when Moda or Redis is unavailable; unverified states do not authorise recovery.

### 6. Background and outbound boundary — contract only

- [ ] Freeze the exact read inputs and outcomes required from Shopify's Redis consent service by `BACKGROUND-001` (cart↔checkout association) and `BACKGROUND-002` (maturity, recipient, STOP and proactive-send admission). Neither task may infer an opt-in from a webhook or copy consent data into an existing BullMQ job merely for convenience.
- [ ] Keep S001 focused: no new cross-store distributed locks or Redis calls inside the existing short PostgreSQL final-send transaction. Specify that `BACKGROUND-002` must recheck current permission before proactive dispatch, including retries and follow-ups, and test withdrawal versus send ordering. Acknowledged withdrawal must prevent later-initiated proactive sends; messages already accepted by Meta cannot be recalled. The detailed dispatch integration belongs to `BACKGROUND-002`, not to an S001 speculative infrastructure design.
- [ ] Record the existing incompatibility: Background's Shopify SQL final fence currently requires `SHOPIFY_NATIVE`, whereas Moda's new Redis evidence must not be mislabelled. `BACKGROUND-002` must implement a reviewed replacement Shopify-only consent admission that continues to enforce existing SQL STOP, shop/recipient ownership, credit/billing and send fences. Do not simply delete the current check.

## Deliverables

- [ ] Architect-reviewable, versioned shop/cart/checkout/customer identity contract with real Shopify test evidence (redacted tokens, plan, dates, code/version provenance).
- [ ] Exact Redis key/payload/write/read contract with cross-repository test vectors, action ordering, returning-customer lookup and withdrawal semantics, TTL/cleanup ownership and memory/eviction impact.
- [ ] Frozen recipient-priority and customer-association contract for Background (including `customer.phone = null`), plus bounded failure outcomes where identity/contact cannot be established.
- [ ] A downstream impact map for SHOPIFY-002/003/004/005 and BACKGROUND-001/002. Identify any conflicting wording in the unmodified parent ARCH-077 document or other task drafts for a **later** targeted reconciliation; this S001 amendment must not edit them.

## Out of scope

Runtime implementation of Redis, Shopify theme/checkout UI, Background workers or SQL; new migrations, schema changes, new Shopify Webhook contracts, changes to WooCommerce/API, release activation or Shopify-native consent retirement.

## Acceptance / stop

**Accept:** Architect approves one deterministic merchant/customer permission policy, two verified Shopify capture/correlation paths, exact Redis contract, returning-customer status/withdrawal rules, recipient priority and explicit Background read/final-send contract. Existing Redis job keys and WooCommerce boundaries are unchanged. S001 evidence distinguishes real Shopify/browser verification from static code review.

**Stop:** Unproven shop/cart/checkout correlation, unsupported Shopify plan, unverifiable customer-to-recipient association, incompatible Redis writer/reader contract or any proposed bypass of STOP/final outbound safety. Return the precise blocker to architect; do not make a guess or change the database to proceed. An S001 definition is not independent approval to deploy the new send path.

## Completion report / validation

Record inspected repository paths and SHAs, actual Shopify test date/plan, anonymised identity correlation results and Redis compatibility analysis. No implementation validation is claimed by this draft. Return for architect review before SHOPIFY-002 or BACKGROUND-001 begins.
