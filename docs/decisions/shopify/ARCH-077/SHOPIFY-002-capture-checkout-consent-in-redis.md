---
id: ARCH-077-SHOPIFY-002
architecture_id: ARCH-077
title: Capture temporary Shopify checkout consent and read existing customer permission
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-SHOPIFY-001, ARCH-077-SHARED-001]
enables: [ARCH-077-BACKGROUND-001, ARCH-077-SHOPIFY-003, ARCH-077-SHOPIFY-004, ARCH-077-SHOPIFY-005]
created: 2026-11-17
updated: 2026-11-17
---

# Capture temporary Shopify checkout consent and read existing customer permission

## Architecture / status

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Ready for implementation after architect acceptance of SHARED-001 (17 November 2026).** S001's cart-to-checkout proof and identity contract are accepted; Shared's optional V2/V3 event fields are implemented and contract-reviewed. The agent must verify that Shared `6.2.0` is published and pin the same compatible build expected by BACKGROUND-001 before emitting new fields. Runtime cart ownership, marker issuance and consent capture still require this task's tests. Do not repeat the browser-only propagation experiment or invent an alternative authentication contract.

## Objective and scope

The Shopify application captures explicit checkbox selections temporarily against the *current cart/checkout* in Redis. It reads an existing, verified customer's permission from the **existing PostgreSQL `commerce.Customer` and `commerce.CustomerPhone` records** to initialise the checkbox on a new cart. **It does not persist a checkbox GRANT or REVOKE to PostgreSQL when the customer clicks.** When the checkout is independently determined to be recoverable, Background consumes the latest relevant temporary choice and applies it to existing customer consent records during its normal recovery processing.

The checked/unchecked wording must remain exactly the existing WooCommerce wording: **“Send me WhatsApp shopping updates, reminders and offers.”** No additional consent language, second phone input, Shopify native WhatsApp marketing consent, Shopify Messaging, WooCommerce code or WooCommerce-facing API is part of this task.

## Owning touchpoints

- New Shopify-only `app/services/shopify-consent/` module and authenticated request handlers selected in accepted SHOPIFY-001 (do not invent routes before contract approval).
- Existing Shopify authentication and Prisma access; resolve a returning customer using the authenticated shop + verified Shopify customer ID, never a browser-asserted customer ID.
- `app/services/webhooks/shopify-webhook-queue.server.ts` is **reference-only** for Redis configuration. Do not change its connection or BullMQ settings. The **only** approved event payload change is the two optional checkout marker/status fields specified in SHARED-001; do not alter unrelated schemas, publication or queue behaviour.
- Background's `src/domain/pending-recovery-candidate.ts` and `src/services/pending-recovery-candidate/candidate-index.store.ts` are **reference-only** for Redis key ownership. Background association, recovery admission and SQL writes belong to BACKGROUND-001/002.

## Cart correlation marker — S002 producer responsibilities

- [ ] Use S001's **one** versioned marker contract, not a second token alias or shopper-preference store. Implement `prepareCartMarker` and the associated current-cart lookup in `app/services/shopify-consent/` with Node CSPRNG `randomBytes(32)`, the exact `m1_` marker format and the three temporary Redis record families; duplicate preparation returns the persisted winner atomically. Do not mint a new marker from a checkbox click or webhook. Keep existing explicit-decision fields and revision ordering on the same cart record.
- [ ] Use the existing React Router explicit route registry `app/routes.ts` to expose an independent Shopify App Proxy resource route under `/shopify/consent/*` (handler under `app/routes/shopify/consent/`, not the embedded `/app` UI route). Configure `[app_proxy]` in `shopify.app.moda-interact.toml` with `url = "/shopify/consent"`, `prefix = "apps"`, `subpath = "moda-consent"` and Shopify's required `write_app_proxy` authorization; check actual app/proxy availability, merchant authorization and configurable `path_prefix` rather than presuming the example `/apps/moda-consent` path is already live. If an existing proxy is found in the implementation checkout, reuse its root; Shopify supports only one app-proxy route. Stop for architect review if this path cannot be authenticated and deployed without altering unrelated Shopify functionality.
- [ ] Freeze three authenticated operations beneath that single proxy: POST `cart/prepare` (verified shop, current cart token; returns marker, record version and owner revision), GET `cart/status` (verified shop/current cart, and signed returning customer where present; returns latest active selection over permitted SQL status), POST `cart/choice` (explicit action ID, GRANT/REVOKE, disclosure text/version/locale and verified current cart+issued marker). Do not accept a caller-supplied shop ID, customer ID or previously unknown marker as authority. All app-proxy requests must verify Shopify signature and fresh timestamp through Shopify's authenticated server route, with this fixed request policy: require Shopify server signature verification, a non-stale Shopify request timestamp under the existing SDK rules, JSON Content-Type for POST, exact authenticated shop-scoped origin on browser POST (or fail closed if missing), unique `actionId` bound to cart/marker, atomic expected-revision compare-and-set and same-ID/same-payload idempotent replay only. Deny mismatched origins, cross-shop marker use, missing/malformed proofs and changed-payload action-ID reuse. Do not add a new cookie/JWT/session auth service.
- [ ] Signed App Proxy verifies the shop only. `prepare` accepts a temporary cart locator and creates no customer permission; `choice` requires the existing reciprocal Redis marker/cart reference plus an atomic expected-revision/action-ID write and acknowledges only a **temporary** selection. There is no separate guest session-proof discovery task. B002, **only after recoverability**, requires guest checkout `cart_token` digest equality or verified signed-logged-in customer-ID equality, as frozen in S001 item 11. A malformed/unknown marker, conflicting action revision or cross-shop request fails closed; missing checkout binding fails closed at B002, not by writing early SQL. No client-side cart/status assertion is trusted as consent proof.
- [ ] In `app/services/webhooks/checkout-normalization.ts`, after authenticated ingestion through existing `app/services/webhooks/shopify-webhook-ingress.service.ts`, extract **only** `moda_cart_correlation_v1` from `payload.note_attributes` on checkout-create/update and set the optional Shared fields `cartCorrelationMarker` and `cartCorrelationMarkerStatus` per SHARED-001, using the authenticated shop ID already resolved inside `ingestShopifyWebhook` (never from client input). Preserve all current checkout metadata and existing queue names, job IDs and ordering. `PRESENT` requires exactly one validated 46-character `m1_` marker; `ABSENT` is verified absence; `INVALID` captures malformed value; `AMBIGUOUS` captures duplicate/conflicting attribute names. The single temporary PII-free marker **may be carried only in the existing checkout event**, never in logs; compute classification after authenticated ingress, then merge the optional fields into normalized V2 create/V3 update payloads before `.strict()` validation. Do not silently discard an invalid/duplicated observed marker as absent, and do not log raw marker/webhook body.
- [ ] `prepare` records the exact S001 cart+reverse marker keys atomically with bounded TTL; returns an existing same-owner marker on retry; rejects collisions, partial versions and conflicting owners. A successful `choice` validates that marker, shop and canonical cart digest correspond to the current verified cart and records the explicit decision atomically; it does not mutate PostgreSQL. Preserve original provider error messages/details in server-side redacted logs without leaking keys to shoppers.

## Required behaviour

### 1. Initialise checkbox from the correct source

- [ ] For a verified returning Shopify customer opening a **new cart**, query existing PostgreSQL records scoped by shop and Shopify customer ID. Read their existing active/current consent decision and STOP/no-contact state using the existing schema. When a verified current grant is present and the customer/phone association is unambiguous, report checked; otherwise do not claim a verified grant.
- [ ] When the *current* cart/checkout already has a later accepted temporary selection, display that latest Redis selection over the prior database state **for this current cart/checkout only**. A read must not itself create a grant, revocation or database write.
- [ ] For a guest without verified returning customer identity, initialise from the verified current cart/checkout's temporary selection, if any; otherwise unchecked. A different guest cart cannot inherit prior permission by phone, email or basket similarity.
- [ ] No Redis customer-preference key or long-lived Redis consent mirror is permitted. PostgreSQL remains the source for **previously materialised customer consent**; Redis is only the active cart/checkout choice and correlation surface.

### 2. Record explicit cart/checkout actions in Redis only

- [ ] Verify the Shopify signed App Proxy **shop** at `prepare`, `status` and `choice`; reject client-selected shop/customer identity. Treat the browser Ajax cart token as an untrusted **cart locator** only. An accepted cart choice is a temporary Redis action tied to `{shopId, cartDigest, marker, actionId, revision}`, never proof of a guest identity or permission to send. If the signed proxy supplies a verified `logged_in_customer_id`, capture it at accepted action time to allow B002's authenticated-customer matching rule; never accept a client-supplied Shopify customer ID. Plus verifies its signed extension checkout context. **Do not add a new guest session/JWT/cookie scheme.**
- [ ] Record a deliberate check as `GRANT` and a deliberate uncheck as `REVOKE` against the current cart or checkout. Preserve the exact displayed disclosure text, Shopify-owned version, locale, action identity and accepted time in that temporary record.
- [ ] A new cart event, checkbox render, server read, checkout-created webhook, refresh or absence of a choice is neutral: it must not manufacture a GRANT or REVOKE.
- [ ] On each accepted checkbox action, **do not update `Customer`, `CustomerPhone`, consent revisions, STOP/no-contact fields, or SQL evidence**. This rule applies equally to an authenticated returning customer's withdrawal and regrant. S002 must not schedule recoveries or reserve credits.
- [ ] Use the versioned Redis-only namespace and exact payload/identity encoding frozen in SHOPIFY-001. Record the latest accepted explicit choice with idempotent action IDs and bounded revision ordering; identical retries are no-ops, conflicting action replays fail, and an older request may not overwrite a newer accepted choice. This must not require an additional distributed-lock framework.
- [ ] A successful checkbox action is acknowledged only after the Redis write succeeds. If Redis is unavailable, do not claim acceptance and never block the merchant's cart/checkout flow. Redact tokens, phone numbers, credentials and proofs in browser responses/logs while preserving safe original provider failure diagnostics server-side.

### 3. Deferred recovery materialisation — Background ownership

- [ ] S002 exposes the SHOPIFY-001-approved read contract for Background to obtain the latest cart/checkout choice and validated identity/correlation evidence. **S002 does not itself decide recoverability, fetch abandoned checkout phone numbers, materialise SQL consent or send messages.**
- [ ] BACKGROUND-001 associates cart consent with checkout using the authenticated event shop, checkout token and verified `cartCorrelationMarker` from the existing checkout event schema; it does not change BullMQ job IDs, queue names or candidate indexes. BACKGROUND-002, and **only when the checkout becomes recoverable**, resolves customer/recipient and applies the applicable `GRANT` or `REVOKE` to existing PostgreSQL consent state under the existing database constraints.
- [ ] If a recoverable checkout has no new temporary choice, Background may use the current previously materialised verified database permission for the correct shop/customer under its approved admission policy. An unchecked default is not a new withdrawal.
- [ ] For a returning customer whose existing SQL permission is `GRANTED`, an explicit `REVOKE` on a new checkout is **temporary until that checkout becomes recoverable**. If the checkout completes or otherwise never becomes eligible, do not persist that choice to PostgreSQL; discard it during normal cleanup. On a later new cart the checkbox again reflects the current database decision. This is the deliberately selected recovery-lifecycle policy; do not add an immediate SQL withdrawal/regrant path.
- [ ] Once an eligible checkout's choice has been successfully materialised, or the cart/checkout is terminal/ineligible, let the Background-owned recovery lifecycle remove the associated temporary Redis records. Do not delete a pending choice while materialisation/retry is unfinished or because a candidate index was removed prematurely.

### 4. Redis ownership and cleanup

- [ ] Store **only** temporary cart/checkout choice and correlation records in the dedicated versioned Shopify consent prefix. No permanent customer-preference index or standalone long-lived Redis consent history is in S002's scope.
- [ ] Define TTL and cleanup hooks according to the existing cart/checkout recovery lifecycle, while retaining state throughout configured maturity and bounded Shopify visibility retries. Never inherit an index TTL blindly; expiry must not permit outreach using an assumed GRANT.
- [ ] Do not write, delete, rename, change value, or extend TTL of `pending-recovery:index:*`, `pending-recovery:lock:*`, `pending-recovery:order-completed:*` or any BullMQ-owned key. No `KEYS` scan, database-wide `FLUSH*`, unrelated queue payload modification or global Redis policy change; the two optional Shared checkout marker/status fields remain explicitly allowed.
- [ ] Shopify uninstall and permitted privacy erasure must remove only keys proven to belong to the correct shop/identity; avoid broad tenant-unsafe scans. Existing PostgreSQL deletion/privacy behaviour is not modified by this task.

## Mandatory zero-effect selection boundary

- [ ] The only writes at `prepare`, `status`, `choice`, cart/checkout app block, and Plus selection events are the approved temporary scoped Redis keys; **zero** `Customer`, `CustomerPhone`, consent revision/sequence, no-contact or STOP writes and **zero** new outreach gating/suppression writes. Deliberate REVOKE on Cart B while Cart A has already sent an initial message does not change A's SQL permission or queued proactive follow-up until B independently becomes recoverable.
- [ ] If Cart B is paid/completed/otherwise ineligible, B's acknowledged Redis REVOKE is removed by Background terminal cleanup and A's existing SQL GRANTED permission stays unchanged. If B becomes recoverable, B002—not S002—persists REVOKED. Do not add user-click SQL callbacks, Redis pending-revoke suppression reads to final-send, STOP side effects, alternative opt-out widgets or customer-level Redis history.
- [ ] **Frozen guest contract:** Permit an explicitly acknowledged, temporary guest `choice` under signed-shop context and the existing reciprocal cart/marker/revision checks; the action creates **no** effective consent. B002 can materialise it only if the authenticated checkout has **both** matching marker and exact canonical `cart_token` digest, a verified eligible recipient and all existing safety guards. A checkout cart-token mismatch with no verified same-customer identity is a typed fail-closed outcome; no extra guest authentication technology or alternate matching path is permitted. Never infer valid consent from a marker or address phone alone.

## Tests and acceptance

- [ ] Authenticated returning Shopify customer opens a **new** cart: status reads PostgreSQL, not a persistent Redis customer key; GRANTED yields checked, UNKNOWN/REVOKED/unverified does not imply permission.
- [ ] An acknowledged cart or Plus checkbox change is stored in Redis and **produces zero PostgreSQL consent writes**, including a returning customer unchecking an already-checked box.
- [ ] For the *same* cart/checkout, Redis's latest accepted explicit choice overrides the older database snapshot for display; new unrelated carts do not inherit another temporary selection.
- [ ] A checkout that **never becomes recoverable** leaves `CustomerPhone` unchanged after temporary-key cleanup; a recoverable checkout delegates SQL materialisation to BACKGROUND-002.
- [ ] Guest scope, forged shop/customer/cart identity, cross-shop access, replay, two tabs, stale writes, changed-action-payload conflict and unverified checkout token are denied as prescribed by S001.
- [ ] Redis outage or eviction never becomes a grant and never blocks checkout. No background candidate index, job ID, job delay, lock, order tombstone or BullMQ key changes from an S002 operation.
- [ ] Tests distinguish a verified SQL consent read from the old Shopify-native provider API. No Shopify native consent API is invoked. Report exact test command, affected files and original provider errors with sensitive-data redaction.

## Reconciled downstream contract

SHOPIFY-001 now defines temporary Redis choice/correlation storage only. BACKGROUND-001 owns checkout association/cleanup, while BACKGROUND-002 applies any verified explicit decision **only at eligible recovery** to the existing PostgreSQL `CustomerPhone` under its normal revisions, purpose, source and STOP constraints. In this Shopify initiative the existing `SHOPIFY_NATIVE` enum value identifies **Moda-verified Shopify checkbox consent**, not a native Shopify marketing-consent API observation. S002 does not write SQL on customer interaction or query that retired provider. If the accepted S001/B002 read/write contract cannot be implemented without weakening these invariants, stop for architect review.

**Stop:** if the SHOPIFY-001 identity/Redis contract is unapproved, the SQL source/consent constraints cannot be honoured without a schema change, a returning customer cannot be unambiguously resolved, or S002 would require changes to Background/BullMQ-owned keys. Report the precise blocker, do not invent a fallback.
