---
id: ARCH-077-SHOPIFY-002
architecture_id: ARCH-077
title: Issue Shopify signed checkout-attribute consent receipts and read returning consent
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
attempt: 1
depends_on: [ARCH-077-SHOPIFY-001, ARCH-077-SHARED-001]
enables: [ARCH-077-BACKGROUND-001, ARCH-077-SHOPIFY-003, ARCH-077-SHOPIFY-004, ARCH-077-SHOPIFY-005]
created: 2026-11-17
updated: 2026-11-17
---

# Shopify consent receipt service — architect-directed rework of S002

**Architect review outcome: Changes Requested; task returned to `ready` for Attempt 2.** The submitted implementation commit (`c0c2cca` per agent report) still creates `m1_` markers and GRANT/REVOKE in temporary Redis. **Do not merge that implementation as the final ARCH-077 consent path.** The accepted [checkout-attribute receipt v1 contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md) supersedes all Redis choices, marker preparation, marker forwarding and TTL work from the earlier task definition. S001 and SHARED-001 stay historically complete. No reimplementation or promotion of the submitted tests is implied by this document patch.

## Objective and file-by-file implementation instructions

Implement **one server-owned, stateless receipt issuer** and returning-customer SQL status reader in `moda-interact`. The Shopify checkbox will write the returned receipt into the single Shopify attribute `moda_wa_consent_v1` under S003/S004. S002 does not itself touch the customer's cart, write PostgreSQL consent, create a recovery, or enqueue a consent job.

1. **Replace** `app/services/shopify-consent/shopify-consent.server.ts` Redis-heavy implementations `prepareCartMarker`, `recordCartChoice`, `readCartConsentStatus`, marker index, revisions, cart key/TTL and Redis errors with `app/services/shopify-consent/consent-receipt.server.ts`, implementing `issueConsentReceipt`, `verifyConsentReceipt`, and a focused `readReturningShopperConsentStatus`. Preserve only applicable provider-error logging and the exact English disclosure constant. Preserve the already-approved `ShopifyConsentServiceError` style as a typed server error where useful; do not keep unused Redis code or a compatibility path.
2. **Delete** `app/services/shopify-consent/marker.ts` if it becomes unused. Do not write `m1_`, `moda_cart_correlation_v1`, `shopify:consent:*` Redis keys or alter BullMQ indexes. The permanent Shopify webhook processing remains unaffected.
3. **Refactor** `app/routes/shopify/consent/route.ts`: remove old `cart/prepare`, `cart/choice` and marker status; implement signed App Proxy `GET cart/status` (verified shop+optional Shopify customer, SQL read only) and `POST cart/receipt` (explicit action choice; issue kind `c` receipt). Keep independent React Router registration `route('shopify/consent/*', ...)`. Existing `[app_proxy]` can remain once verified live; avoid duplicate Shopify proxy routes. Verify Shopify signed `timestamp` within ±300 seconds, the rule that browser Origin, if present, must be well-formed HTTPS but **must not** be compared to the `.myshopify.com` shop identity (Shopify SDK signature and bounded timestamp are the authentication boundary), approved `path_prefix`, max request body, JSON and a valid base Ajax cart token; do not treat a signed shop as proof of an anonymous shopper or trust body customer IDs.
4. **Add** a separate authenticated Plus Checkout UI Extension issuer route in `app/routes.ts` and a narrowly focused new route under `app/routes/shopify/consent/checkout-receipt/route.ts` (distinct from App Proxy and embedded UI). Authenticate `Authorization: Bearer <Shopify checkout session token>` with the installed SDK checkout authentication, require verified shop/audience/session claims, supplied current checkout token, explicit action and locale, then issue kind `x` receipt. If installed SDK/target cannot provide verified shop/checkout context, stop and report a concrete SDK blocker; do not invent new claims or bypass authentication. S004 owns writing this receipt through `applyAttributeChange` and proving capability/readback.
5. **Revert only S002-specific marker projection** in `app/services/webhooks/checkout-normalization.ts` and related S002 ingestion changes: authenticated `CHECKOUTS_CREATE`/`CHECKOUTS_UPDATE` remain unchanged, but no new `cartCorrelationMarker` producer data is needed. Do not remove the accepted optional SHARED-001 fields from the Shared package; they remain optional/unused. Preserve all existing queue names/IDs and original checkout metadata.
6. **Key configuration:** require only `SHOPIFY_CONSENT_RECEIPT_KEY_V1` (32 random bytes unpadded base64url) to sign and verify receipts in Shopify and Background. No marker HMAC secret, Redis consent storage, new secret per merchant, distributed lock, expiry scheduler, migration or additional service. The receipt has **no independent TTL**; it remains a Shopify checkout attribute until Shopify's normal checkout lifecycle.
7. **Existing PostgreSQL status:** read only an unambiguous current shop+verified Shopify customer `CustomerPhone` decision/STOP/recipient association; checked only for verified current GRANTED. A guest starts unchecked unless the current cart already contains a **verified** receipt. An initial render or status read never mints a new selection. A returning customer's explicit REVOKE is only a receipt in Shopify until the checkout is recoverable.
8. **Wire contract:** implement exact dot-separated v1 payload, field regexes, SHA-256 token binding, HMAC-SHA256 base64url signature and `timingSafeEqual` verification as defined in the linked spec. Include deterministic known key/payload/MAC vectors in tests, valid/invalid MAC tests, wrong shop, copied checkout token, malformed/duplicate attribute, wrong kind, unsafe future clock, locale and server-log redaction. Document same-checkout valid-receipt replay as an accepted **limitation**, not a passed replay-security property.
9. **No shopper-facing errors:** on SDK, signing, status or network failure, return typed non-sensitive failure; the S003/S004 control hides/restores unacknowledged selection and checkout always remains functional. Server preserves original useful SDK/Shopify/Prisma error details with redaction; never print raw tokens/receipts/customer data.

## Precise acceptance and tests

- Replace old `tests/integration/shopify-consent.redis.integration.test.ts` with receipt-focused deterministic tests, and update `tests/unit/routes/shopify-consent-route.test.ts`; do not delete independent `tests/integration/shopify-webhook-publication.redis.integration.test.ts` or queue regression coverage.
- Test signed custom-storefront-domain POST and each supported signed App Proxy prefix (do not hardcode `myshopify.com` as origin), fresh/stale/future signed timestamps, invalid/replayed signature, Shop A versus B, signed customer versus guest, changed cart token and Plus session token rejection; use the installed SDK or label mocks explicitly.
- Unit-test a real `cart/update.js` receipt readback fixture, checkout note attribute fixture and authoritative GraphQL `customAttributes` fixture. Tests must distinguish the previously verified marker experiment from **new** real receipt behavior, and must not claim Plus live functionality without a Plus checkout test.
- Verify no `redis` import or consent TTL in reworked issuer; no SQL consent writes from any S002 action; optional Shared marker fields unused; no queue naming changes; existing Shopify webhook integration tests pass.
- Execute actual `npm run build`, targeted lint/typecheck and source-controlled tests; report the five known pre-existing webhook-root implicit-any type errors separately if still present. Provide exact changed files, SHA, package pins and meaningful redacted original provider errors.

**STOP conditions:** the verified Shopify checkout token cannot be bound to Plus receipt issuance, signed App Proxy origin/shop cannot be verified, the receipt attribute cannot round-trip intact, a newly added route weakens authentication, or the agent would need a new DB/Redis consent state to complete the task. Return the specific blocker; do not silently reintroduce the abandoned Redis design. The architect has returned this task to `ready` for an unclaimed correction attempt. After implementation and validation, the implementing agent must set it to `review` and stop for architect acceptance.


## Architect Review

### Review Status

**Changes Requested — 17 November 2026.** Architect-approved attribute-based reconciliation is complete as a *document decision*, not as a verified runtime implementation. The submitted Attempt 1 Shopify implementation is not accepted under the new contract. The task is returned from `review` to `ready` for the same `moda_app` agent to claim Attempt 2 through the normal launcher. Do not manually mark this task `in_progress` or increment `attempt` before the launcher claims it.

### Review Notes and precise correction contract

The accepted `docs/architecture/ARCH-077/checkout-attribute-consent-v1.md` replaces the Redis cart/checkout choice, marker preparation and TTL architecture. The existing code still implements those obsolete mechanisms. Rework the **same** SHOPIFY-002 implementation rather than launching a separate feature or merging the obsolete code. The numbered instructions and tests above are mandatory, not suggestions. In particular:

1. Replace Redis choice/marker issuer with the stateless signed `moda_wa_consent_v1` receipt issuer and verifier, using the *exact* approved versioned wire contract. No additional Redis consent retention or cleanup task.
2. Change the authenticated cart App Proxy endpoints to `GET cart/status` and `POST cart/receipt` with the approved shop, request-freshness, input and storefront-domain handling. No client-supplied merchant identity or guest identity is authoritative.
3. Introduce the separate authenticated Plus checkout receipt-issuance boundary specified above. Do not implement S004's checkout checkbox/attribute writer inside S002.
4. Remove obsolete `m1_` marker preparation, Redis GRANT/REVOKE keys, TTL/revision scripts and S002 webhook-marker projection. Do not alter the accepted optional Shared schema fields, existing checkout-event queues or unrelated BullMQ processing.
5. Preserve returning-customer PostgreSQL **read-only** status, with no GRANT/REVOKE materialisation until Background independently verifies recoverability; preserve STOP and existing reactive-message semantics.
6. Replace Redis-specific task tests with receipt/signature, signed App Proxy, isolation, token binding, webhook regression and failure-path tests listed above. Preserve unrelated passing tests. Report real SDK/Plus test constraints; no fabricated provider evidence.

### Reviewed Files / Evidence

- Submitted SHOPIFY-002 implementation worktree and earlier completion report: implementation commit `c0c2cca` (reported); parent report `c4f2e158` (reported)
- `app/services/shopify-consent/shopify-consent.server.ts` and `app/routes/shopify/consent/route.ts` from prior architect inspection, containing the superseded Redis path
- Accepted non-Plus cart attribute propagation evidence and authoritative `AbandonedCheckout.customAttributes` query
- Reconciled ARCH-077 parent and `docs/architecture/ARCH-077/checkout-attribute-consent-v1.md`

### Validation Reviewed

The prior agent reported 173 webhook tests, 9 Redis webhook integrations, 4 consent Redis tests and a successful production build. Those runs demonstrate the **previous Redis implementation**, not the new receipt contract; they cannot be carried forward as acceptance for Attempt 2. This document/status correction has no runtime changes. No receipt runtime tests were executed by this architect amendment.

### Architecture Conformance

**Not yet conformant:** current submitted runtime uses Redis consent choice/marker lifecycle, now superseded. The new single Shopify attribute receipt contract is approved at the document level. Preserve unchanged merchant plan placement (cart for non-Plus, checkout for Plus), delayed consent materialisation, proactive vs reactive conversation rules and no new database/queue.

### Rework Handoff and Stop

`assigned_agent: moda_app`, repository `moda-interact`, task `ARCH-077-SHOPIFY-002`, `attempt: 1` preserved until the launcher claims Attempt 2. `executor` and `claimed_at` are cleared. Dependencies S001 and SHARED-001 remain `complete`. S003, S004, S005 and B001 remain gated until SHOPIFY-002 passes architect acceptance and reaches `complete`. The implementation agent must read this entire latest Architect Review before changing code; after correction and validation it must set the task to `review`, submit the updated Completion Report and stop. Do not modify task indexes, advance dependent tasks, merge branches or mark S002 `complete` during this rework.
