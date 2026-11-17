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
enables: [ARCH-077-BACKGROUND-001, ARCH-077-SHOPIFY-002, ARCH-077-SHOPIFY-004]
created: 2026-11-17
updated: 2026-11-17
---

# Freeze Shopify consent identity and Redis contract

## Architecture

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Reconciled definition; remains `pending`. Contract/proof work only until architect acceptance; no downstream runtime implementation is authorised by this amendment.**

## Objective

Freeze the Shopify cart, checkout and authenticated customer identities and exact Redis contract before any Shopify or Background writer/reader is built. This is a proof gate, not an invitation to infer a correlation mechanism.

## Existing touchpoints for inspection (do not change runtime in this definition)

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
- [ ] **Deferred recovery materialisation:** Store only the acknowledged explicit selection against the *current cart/checkout* in temporary Redis; do not create a permanent customer-level Redis preference or consent history. For a verified returning customer, S002 reads existing customer permission from PostgreSQL. Only when an abandoned checkout is independently verified as recoverable does Background apply the latest accepted GRANT/REVOKE to the existing `Customer`/`CustomerPhone` permission and associate the selected recipient. Materialisation must never manufacture a grant. Do not create consent by detecting a cart, checkout or phone number.
- [ ] **No new SQL contract:** Do not add a database model, field, enum value, migration or table; do not insert Moda-owned Shopify evidence into Woo-only `WhatsAppConsentEvidence`. For ARCH-077 the **existing `SHOPIFY_NATIVE` enum value designates Moda-verified Shopify checkbox evidence** after eligible recovery materialisation; it must not trigger or imply a Shopify-native marketing-consent API read. The current durable customer permission resides in existing PostgreSQL records, and the active checkout selection remains temporary Redis state. Preserve all SQL constraints, revisions and STOP.

### 2. Shopify cart and checkout correlation — verified event identities

- [ ] **Cart-page action:** Bind the selection to the authenticated Shopify shop and the shopper's current cart token obtained through the supported Ajax Cart API. Verify the actual relationship among `/cart.js` token, authenticated `carts/create/update` webhook `token`, and authenticated `checkouts/create/update` webhook `cart_token` using real development-store evidence. Do not assume byte-identical token strings without proof; never log raw tokens.
- [ ] **Checkout transition:** A verified checkout event supplies `shopId + cartToken + checkoutToken`; associate the applicable cart selection with that checkout. Support `carts/create` arriving after an action, checkout-created arriving before a cart action, duplicated events and cart regenerations without losing the latest accepted decision. A token correlation may establish checkout association but may not silently override the current customer preference.
- [ ] **Conflict:** If a cart token appears to map to incompatible checkout identities, do not mint consent for multiple unrelated checkouts. Specify a deterministic bounded resolution using authenticated Shopify identity, or deny the ambiguous association. Do not match unrelated checkouts by email, phone, product contents or timestamps.
- [ ] **Shopify Plus:** Verify the supported Checkout UI Extension target, signed session token and checkout-token availability, then associate a selection directly with the checkout identity. No intermediate cart alias is needed. Record unsupported/accelerated checkout paths explicitly.

### 3. Returning customer on a new cart

- [ ] **Verified returning identity:** Obtain a shop-scoped authenticated Shopify customer ID through an appropriate verified Shopify context (e.g. signed App Proxy `logged_in_customer_id` where supplied, or verified checkout extension identity). Use `shopId + Shopify customer ID` to retrieve the existing preference even where the new cart token differs from the prior visit.
- [ ] **Status and opt-out:** A returning authenticated customer with a current verified PostgreSQL grant sees the checkbox checked on a new cart and may explicitly uncheck it. This records a temporary checkout/cart REVOKE; **it does not immediately modify PostgreSQL or earlier recoveries**. Only if the current checkout becomes recoverable does B002 materialise REVOKE. If it completes normally, temporary Redis is cleaned up and a later new cart reads the still-current SQL state. Do not silently regrant on page load.
- [ ] **Initial identity unknown:** A guest can select a checkbox tied to the current verified cart/checkout; establish customer identity later only from the authoritative checkout/customer association. A guest starting a separate new cart without verified continuity must not inherit a previous guest's permission from matching contact details. If a customer cannot be identified, preserve only the verified checkout-scoped evidence until identification or expiry.

### 4. Recipient selection at recoverable checkout

- [ ] **No phone field on cart:** Consent is collected before Shopify necessarily knows the customer's number. It is logically the customer's permission, not a checkbox grant for a hard-coded phone value. At recovery maturity, read the authoritative Shopify abandoned checkout using the existing lookup and resolve an available contact candidate in this priority: **customer phone → billing phone → shipping phone**.
- [ ] **Normalisation and association:** Normalise the chosen phone under the published Shared international phone contract and associate it with the correctly identified shop/customer/recovery using existing models when possible. An invalid first-preference number must not become an authorised recipient; document whether a lower-priority valid number can then be used. A shipping number supplied for a different person must not be treated as that person's opt-in solely because it appeared on the address; classify unsupported identity evidence and deny that recipient.
- [ ] **Multiple numbers:** Do not automatically reject a checkout merely because customer, billing and shipping phone fields differ; use the frozen priority to select the first eligible customer-associated number. No Shopify-native WhatsApp marketing-consent read, Shopify Messaging dependency, or `customer.defaultPhoneNumber.whatsAppMarketingConsent` requirement.
- [ ] **STOP:** Even a newly accepted checkbox `GRANT` must never clear an authoritative customer STOP, existing no-contact restriction or independently established outbound eligibility block.

### 5. Redis contract, isolation and retention

- [ ] Freeze the versioned Shopify-only key namespace and exact encoding for **temporary cart choice, temporary checkout choice, verified cart-to-checkout association and bounded action/revision evidence**. Do not allocate permanent Redis customer-preference or history keys. Provide cross-application digest/key test vectors without exposing raw cart, checkout or customer IDs in keys or logs. Shopify and Background must use identical versioned semantics and safe deployment ordering.
- [ ] Use the latest explicit action per verified cart/checkout with idempotent ordering; prior customer-level permission is read from PostgreSQL, not maintained as a second Redis authority. Checkout and cart association must not introduce competing grants. Define idempotent retries, monotonic accepted revisions, bounded atomic Redis updates and explicit behaviour when writes/read results arrive out of order. **Do not introduce a distributed-lock framework solely for checkbox selections.**
- [ ] Define **temporary** cart/checkout state retention through the normal configured maturity and bounded provider-verification/materialisation retries. B001 removes it after successful B002 materialisation or definitive completion/ineligibility; an active cart without a checkout has separately bounded retention. Later follow-ups and long-term customer permission use PostgreSQL and must **not** extend temporary Redis retention. Do **not** blindly inherit short-lived candidate-index TTLs. Missing, corrupt or evicted proof must not be interpreted as `GRANTED`.
- [ ] Inspect current shared `REDIS_URL`/DB/ACL, memory budget, eviction/persistence/backup policies and worker cleanup. Introduce no new global Redis setting without an explicit impact assessment. Never repurpose, overwrite, delete, extend TTLs of or scan Background-owned `pending-recovery:index:*`, `pending-recovery:lock:*`, `pending-recovery:order-completed:*` or BullMQ-managed keys.
- [ ] Document shopper-side checkout-unavailable behaviour: accepting a choice requires successful Redis acknowledgement, but cart/checkout must remain usable when Moda or Redis is unavailable; unverified states do not authorise recovery.

### 6. Background and outbound boundary — contract only

- [ ] Freeze the exact read inputs and outcomes required from Shopify's Redis consent service by `BACKGROUND-001` (cart↔checkout association) and `BACKGROUND-002` (maturity, recipient, STOP and proactive-send admission). Neither task may infer an opt-in from a webhook or copy consent data into an existing BullMQ job merely for convenience.
- [ ] Keep S001 focused: **PostgreSQL remains authoritative after materialisation**, and B002 reuses the existing current-permission preflight and short SQL final-send check for initial sends, retries and follow-ups. No Redis read in the SQL transaction and no Redis/PostgreSQL distributed dispatch lock. A temporary REVOKE has no durable effect on existing recoveries until an eligible checkout materialises it, per the approved lifecycle; do not accidentally claim click-time SQL withdrawal. STOP remains immediately authoritative under its existing independent pathway.
- [ ] Freeze the B002 handoff: the existing `SHOPIFY_NATIVE` value represents Moda Shopify checkbox consent **once materialised**, not native provider consent. B002 must replace the old Shopify marketing-consent reader/writer while keeping the existing SQL final-send fence, STOP, shop/recipient ownership, credit and billing checks intact. Do not delete the current fence or call the retired Shopify native marketing API.

## Deliverables

- [ ] Architect-reviewable, versioned shop/cart/checkout/customer identity contract with real Shopify test evidence (redacted tokens, plan, dates, code/version provenance).
- [ ] Exact Redis key/payload/write/read contract with cross-repository test vectors, action ordering, returning-customer lookup and withdrawal semantics, TTL/cleanup ownership and memory/eviction impact.
- [ ] Frozen recipient-priority and customer-association contract for Background (including `customer.phone = null`), plus bounded failure outcomes where identity/contact cannot be established.
- [ ] A downstream impact map for SHOPIFY-002/003/004/005 and BACKGROUND-001/002. Verify the reconciled ARCH-077 parent and S002/B001/B002 contracts share the same **temporary Redis → eligible-recovery SQL materialisation → PostgreSQL final-send** sequence; report any execution-time contract drift to the architect before implementation.

## Out of scope

Runtime implementation of Redis, Shopify theme/checkout UI, Background workers or SQL; new migrations, schema changes, new Shopify Webhook contracts, changes to WooCommerce/API, release activation or Shopify-native consent retirement.

## Acceptance / stop

**Accept:** Architect approves one deterministic merchant/customer permission policy, two verified Shopify capture/correlation paths, exact Redis contract, returning-customer status/withdrawal rules, recipient priority and explicit Background read/final-send contract. Existing Redis job keys and WooCommerce boundaries are unchanged. S001 evidence distinguishes real Shopify/browser verification from static code review.

**Stop:** Unproven shop/cart/checkout correlation, unsupported Shopify plan, unverifiable customer-to-recipient association, incompatible Redis writer/reader contract or any proposed bypass of STOP/final outbound safety. Return the precise blocker to architect; do not make a guess or change the database to proceed. An S001 definition is not independent approval to deploy the new send path.

## Completion report / validation

Record inspected repository paths and SHAs, actual Shopify test date/plan, anonymised identity correlation results and Redis compatibility analysis. No implementation validation is claimed by this task definition. Return for architect review before SHOPIFY-002 or BACKGROUND-001 begins.
