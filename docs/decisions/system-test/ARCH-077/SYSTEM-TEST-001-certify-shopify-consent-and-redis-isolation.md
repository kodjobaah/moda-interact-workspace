---
id: ARCH-077-SYSTEM-TEST-001
architecture_id: ARCH-077
title: Certify signed Shopify checkout-attribute consent and worker isolation
task_kind: verification
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  [
    ARCH-077-SHOPIFY-003,
    ARCH-077-SHOPIFY-004,
    ARCH-077-SHOPIFY-005,
    ARCH-077-BACKGROUND-001,
    ARCH-077-BACKGROUND-002,
    ARCH-077-SHOPIFY-006,
  ]
enables: []
created: 2026-11-17
updated: 2026-11-17
---

# Certify ARCH-077 Shopify checkout-attribute consent and worker isolation

**Pending last, after S002-S006 and B001/B002.** This replaces former Redis consent-retention certification with [one Shopify attribute receipt contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md). Preserve existing BullMQ/Redis **checkout processing**, but do not demand a new Redis consent store or marker cleanup.

## A. Shopify transport, exact plan placement and signed receipt

- Real **non-Plus** Shopify test: S003 cart App Block active in published cart template, exact 20-locale copy, explicit GRANT and later REVOKE overwrite the one `moda_wa_consent_v1` attribute, observed in authenticated checkout create/update then in GraphQL `AbandonedCheckout.customAttributes` from the **already-used** authoritative fetch. Compare bounded redacted Shared AEAD verification outcomes, never print raw checkout tokens/receipts.
- Real **Plus** store test: only S004 checkout UI Extension at `purchase.checkout.contact.render-after`, with a verified signed checkout JWT/token, `instructions.attributes.canUpdateAttributes`, `applyAttributeChange` success/readback and same GraphQL attribute. Cart App Block must not run on Plus. Accelerated/unsupported checkout fails silently without a fabricated consent choice.
- Existing 17 November SHA prefix `ef5dbf7582291225` proves historical non-Plus _probe_ propagation only; never claim it proves signed receipts or Plus implementation. Live proof needed for final acceptance.
- One attribute only; no `moda_cart_correlation_v1`, `moda_s001_probe`, GRANT/REVOKE Redis keys or additional event payload. SHARED-001 optional marker fields remain unused/compatible and existing queue schemas accept old events.

## B. Signature, identity and minimal-stateless limitation

- Canonical plaintext/AAD bytes and Shared AEAD encrypted-receipt round-trip, wrong/missing/rotated keys, incorrect/duplicate envelope fields, tag/ciphertext tampering, wrong shop/AAD, mismatched event checkout/cart token, different guest/customer, invalid source kind/locale, oversized payload, missing customer attribution, future timestamp, Redis outage and missing Shopify attribute. No forged plain `GRANT` authorises outreach.
- Demonstrate that a receipt copied to another shop or checkout **fails**; demonstrate and explicitly document that a previously valid receipt restored to the **same** checkout can be accepted by this stateless model (accepted tradeoff). Do **not** misreport this as replay prevention or silently introduce Redis customer preference to make the test pass.
- Guest accepted only with trusted event token correlation and attributable recipient; an earlier observed cart-token mismatch fails closed. Signed customer ID mismatch denies. Unverified/missing checkout or SDK context must never be replaced by phone/email/item matching.

## C. Deferred consent, two checkouts, STOP and outreach

- A GRANT click -> only signed Shopify attribute, no PostgreSQL write; A recoverable -> SQL GRANTED then legitimate first outreach. B REVOKE click -> SQL still GRANTED and A proactive follow-up still evaluated under current SQL; B paid -> no SQL change; B recoverable -> SQL REVOKED before denying B outreach, A's unsent proactive follow-up denied, earlier delivered A outreach preserved. Future C with no choice uses stored SQL decision; future recoverable C GRANT may reauthorise unless STOP. STOP follows independent immediate suppression at any stage.
- Existing customer replies to Cart A after B's REVOKE can receive AI/human service responses if allowed by real inbound, WhatsApp 24h window, moderation and STOP; unsolicited retry/follow-up is **not** converted into a service reply just because a window is open.
- Crash/retry and competing workers: verify real existing checkout/recovery identity, normal BullMQ retries and durable SQL guards. Require duplicate suppression **only when current durable state proves the same checkout decision was already applied**; otherwise record actual behaviour and the architect-accepted rare delayed A-after-B overwrite limitation. Do **not** assert absolute cross-checkout monotonicity or exactly-once consent application, create a schema fix, or trigger `MATERIALISATION_IDEMPOTENCY_BLOCKER` solely because this limitation exists. Still fail for actual transaction integrity, recoverability, STOP, recipient, final-send, billing/credit or sender-routing regressions. Preserve one conversation per recovery, credit reserve/commit/release, two proactive messages per recovery and sender assignment.

## D. Worker/database isolation and regression

- Assert no new Redis consent/marker/TTL storage, queue or lifecycle cleanup; existing `pending-recovery:index:*`, locks, completion tombstones, BullMQ queue metadata and job IDs/delays are identical before/after consent feature. Confirm no additional Shopify API request for attributes: inspect the existing abandoned-checkout query's response.
- Test Shopify native marketing-consent read and webhook removal; WooCommerce consent/regressions remain unchanged; original server errors logged with sensitive-data redaction; no new schema or migrations.
- Run focused + full test suites in correct repo worktrees and real disposable PostgreSQL/Redis, report actual commit SHAs, Shared pins, exact plan/theme/extension configuration and real vs mock verification. Container cleanup required. Do not mark runtime accepted from documentation-only checks.
