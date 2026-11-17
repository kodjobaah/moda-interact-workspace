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
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-SHOPIFY-001]
enables: []
created: 2026-11-17
updated: 2026-11-17
---

# Capture temporary Shopify checkout consent and read existing customer permission

## Architecture / status

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Pending architecture review. Do not implement until SHOPIFY-001's Redis and identity contract has been reconciled with this task and accepted.**

## Objective and scope

The Shopify application captures explicit checkbox selections temporarily against the *current cart/checkout* in Redis. It reads an existing, verified customer's permission from the **existing PostgreSQL `commerce.Customer` and `commerce.CustomerPhone` records** to initialise the checkbox on a new cart. **It does not persist a checkbox GRANT or REVOKE to PostgreSQL when the customer clicks.** When the checkout is independently determined to be recoverable, Background consumes the latest relevant temporary choice and applies it to existing customer consent records during its normal recovery processing.

The checked/unchecked wording must remain exactly the existing WooCommerce wording: **“Send me WhatsApp shopping updates, reminders and offers.”** No additional consent language, second phone input, Shopify native WhatsApp marketing consent, Shopify Messaging, WooCommerce code or WooCommerce-facing API is part of this task.

## Owning touchpoints

- New Shopify-only `app/services/shopify-consent/` module and authenticated request handlers selected in accepted SHOPIFY-001 (do not invent routes before contract approval).
- Existing Shopify authentication and Prisma access; resolve a returning customer using the authenticated shop + verified Shopify customer ID, never a browser-asserted customer ID.
- `app/services/webhooks/shopify-webhook-queue.server.ts` is **reference-only** for Redis configuration. Do not change its connection, BullMQ settings, event schemas, queue payloads or publisher behaviour.
- Background's `src/domain/pending-recovery-candidate.ts` and `src/services/pending-recovery-candidate/candidate-index.store.ts` are **reference-only** for Redis key ownership. Background association, recovery admission and SQL writes belong to BACKGROUND-001/002.

## Required behaviour

### 1. Initialise checkbox from the correct source

- [ ] For a verified returning Shopify customer opening a **new cart**, query existing PostgreSQL records scoped by shop and Shopify customer ID. Read their existing active/current consent decision and STOP/no-contact state using the existing schema. When a verified current grant is present and the customer/phone association is unambiguous, report checked; otherwise do not claim a verified grant.
- [ ] When the *current* cart/checkout already has a later accepted temporary selection, display that latest Redis selection over the prior database state **for this current cart/checkout only**. A read must not itself create a grant, revocation or database write.
- [ ] For a guest without verified returning customer identity, initialise from the verified current cart/checkout's temporary selection, if any; otherwise unchecked. A different guest cart cannot inherit prior permission by phone, email or basket similarity.
- [ ] No Redis customer-preference key or long-lived Redis consent mirror is permitted. PostgreSQL remains the source for **previously materialised customer consent**; Redis is only the active cart/checkout choice and correlation surface.

### 2. Record explicit cart/checkout actions in Redis only

- [ ] Authenticate each Shopify shop and bind the shopper action to the current verified cart/session or Plus checkout identity using the accepted SHOPIFY-001 contract. An App Proxy signature does not by itself establish guest ownership of an arbitrary cart token; a Plus action must validate its signed extension context.
- [ ] Record a deliberate check as `GRANT` and a deliberate uncheck as `REVOKE` against the current cart or checkout. Preserve the exact displayed disclosure text, Shopify-owned version, locale, action identity and accepted time in that temporary record.
- [ ] A new cart event, checkbox render, server read, checkout-created webhook, refresh or absence of a choice is neutral: it must not manufacture a GRANT or REVOKE.
- [ ] On each accepted checkbox action, **do not update `Customer`, `CustomerPhone`, consent revisions, STOP/no-contact fields, or SQL evidence**. This rule applies equally to an authenticated returning customer's withdrawal and regrant. S002 must not schedule recoveries or reserve credits.
- [ ] Use the versioned Redis-only namespace and exact payload/identity encoding frozen in SHOPIFY-001. Record the latest accepted explicit choice with idempotent action IDs and bounded revision ordering; identical retries are no-ops, conflicting action replays fail, and an older request may not overwrite a newer accepted choice. This must not require an additional distributed-lock framework.
- [ ] A successful checkbox action is acknowledged only after the Redis write succeeds. If Redis is unavailable, do not claim acceptance and never block the merchant's cart/checkout flow. Redact tokens, phone numbers, credentials and proofs in browser responses/logs while preserving safe original provider failure diagnostics server-side.

### 3. Deferred recovery materialisation — Background ownership

- [ ] S002 exposes the SHOPIFY-001-approved read contract for Background to obtain the latest cart/checkout choice and validated identity/correlation evidence. **S002 does not itself decide recoverability, fetch abandoned checkout phone numbers, materialise SQL consent or send messages.**
- [ ] BACKGROUND-001 associates cart consent with checkout using verified `shopId`, `cartToken`, `checkoutToken` without modifying BullMQ jobs or candidate indexes. BACKGROUND-002, and **only when the checkout becomes recoverable**, resolves customer/recipient and applies the applicable `GRANT` or `REVOKE` to existing PostgreSQL consent state under the existing database constraints.
- [ ] If a recoverable checkout has no new temporary choice, Background may use the current previously materialised verified database permission for the correct shop/customer under its approved admission policy. An unchecked default is not a new withdrawal.
- [ ] For a returning customer whose existing SQL permission is `GRANTED`, an explicit `REVOKE` on a new checkout is **temporary until that checkout becomes recoverable**. If the checkout completes or otherwise never becomes eligible, do not persist that choice to PostgreSQL; discard it during normal cleanup. On a later new cart the checkbox again reflects the current database decision. This is the deliberately selected recovery-lifecycle policy; do not add an immediate SQL withdrawal/regrant path.
- [ ] Once an eligible checkout's choice has been successfully materialised, or the cart/checkout is terminal/ineligible, let the Background-owned recovery lifecycle remove the associated temporary Redis records. Do not delete a pending choice while materialisation/retry is unfinished or because a candidate index was removed prematurely.

### 4. Redis ownership and cleanup

- [ ] Store **only** temporary cart/checkout choice and correlation records in the dedicated versioned Shopify consent prefix. No permanent customer-preference index or standalone long-lived Redis consent history is in S002's scope.
- [ ] Define TTL and cleanup hooks according to the existing cart/checkout recovery lifecycle, while retaining state throughout configured maturity and bounded Shopify visibility retries. Never inherit an index TTL blindly; expiry must not permit outreach using an assumed GRANT.
- [ ] Do not write, delete, rename, change value, or extend TTL of `pending-recovery:index:*`, `pending-recovery:lock:*`, `pending-recovery:order-completed:*` or any BullMQ-owned key. No `KEYS` scan, database-wide `FLUSH*`, queue payload modification or global Redis policy change.
- [ ] Shopify uninstall and permitted privacy erasure must remove only keys proven to belong to the correct shop/identity; avoid broad tenant-unsafe scans. Existing PostgreSQL deletion/privacy behaviour is not modified by this task.

## Tests and acceptance

- [ ] Authenticated returning Shopify customer opens a **new** cart: status reads PostgreSQL, not a persistent Redis customer key; GRANTED yields checked, UNKNOWN/REVOKED/unverified does not imply permission.
- [ ] An acknowledged cart or Plus checkbox change is stored in Redis and **produces zero PostgreSQL consent writes**, including a returning customer unchecking an already-checked box.
- [ ] For the *same* cart/checkout, Redis's latest accepted explicit choice overrides the older database snapshot for display; new unrelated carts do not inherit another temporary selection.
- [ ] A checkout that **never becomes recoverable** leaves `CustomerPhone` unchanged after temporary-key cleanup; a recoverable checkout delegates SQL materialisation to BACKGROUND-002.
- [ ] Guest scope, forged shop/customer/cart identity, cross-shop access, replay, two tabs, stale writes, changed-action-payload conflict and unverified checkout token are denied as prescribed by S001.
- [ ] Redis outage or eviction never becomes a grant and never blocks checkout. No background candidate index, job ID, job delay, lock, order tombstone or BullMQ key changes from an S002 operation.
- [ ] Tests distinguish a verified SQL consent read from the old Shopify-native provider API. No Shopify native consent API is invoked. Report exact test command, affected files and original provider errors with sensitive-data redaction.

## Architectural reconciliation required before implementation

The **previous S001 amendment** still describes a Redis-resident customer preference/history and a current customer-level withdrawal effect. **The approved S002 direction supersedes those Redis persistence and immediate-withdrawal assumptions:** returning preference comes from PostgreSQL, checkbox actions remain cart/checkout-scoped Redis state, and SQL GRANT/REVOKE happens only when the checkout becomes recoverable. Do not modify S001 or other tasks in this one-file patch; return the conflict for a targeted S001/Background reconciliation before implementation. The existing `CustomerPhone` source enum/SQL guards and `SHOPIFY_NATIVE` final-send check also require a separately reviewed, schema-neutral Background resolution; S002 must not bypass them or mislabel a Moda checkbox event as a native Shopify observation.

**Stop:** if the SHOPIFY-001 identity/Redis contract is unapproved, the SQL source/consent constraints cannot be honoured without a schema change, a returning customer cannot be unambiguously resolved, or S002 would require changes to Background/BullMQ-owned keys. Report the precise blocker, do not invent a fallback.
