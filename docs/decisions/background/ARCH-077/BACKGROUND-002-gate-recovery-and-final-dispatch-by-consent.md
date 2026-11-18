---
id: ARCH-077-BACKGROUND-002
architecture_id: ARCH-077
title: Gate Shopify recovery and outbound sends using signed checkout consent
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-BACKGROUND-001]
enables: [ARCH-077-SHOPIFY-006, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-17
---

# Gate Shopify recovery and final proactive sends using signed checkout consent

**Ready after architect-accepted B001 (17 November 2026).** Follow the [ARCH-077 signed receipt v1 contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md). This **replaces** Redis consent read/materialisation while preserving existing PostgreSQL `CustomerPhone` and final-SQL permission guards.

## Ownership and exact sequence

1. Keep existing authoritative Shopify abandoned-checkout lookup, merchant-configured maturity/visibility retries, payment/completion/cancellation guards and checkout identity before any consent decision. Determine `RECOVERABLE` independently of prior stored GRANT/REVOKE or whether an outreach record can be created.
2. Extract **one** `moda_wa_consent_v1` from `AbandonedCheckout.customAttributes {key value}` already read under B001. No additional provider call. Verify the exact v1 Shared AES-256-GCM authenticated receipt (`v1.` canonical envelope), rejecting incorrect version/shop/plan kind/binding/customer/locale, wrong AAD/tag/unknown key, malformed or duplicate attributes. Use the existing `MODA_ENCRYPTION_KEYS_JSON` Shared credential keyring and exact AAD/decoder/claims defined in `docs/architecture/ARCH-077/checkout-attribute-consent-v1.md`, **not** `SHOPIFY_CONSENT_RECEIPT_KEY_V1` or a duplicate HMAC/AES implementation, and the original authenticated checkout candidate token: `kind c` requires original authenticated checkout event `cart_token` matching signed base-cart SHA-256; `kind x` requires trusted checkout token matching signed checkout SHA-256. The GraphQL `AbandonedCheckout` object does **not** expose `cartToken`; don't invent it. If event tokens missing/ambiguous, fail closed; no Redis marker fallback.
3. Resolve the correct shop, verified Shopify customer and attributable recipient: valid customer phone, else billing, else shipping; a shipping recipient known unrelated is ineligible, and differing phone fields are not inherently ambiguous. Signed `customerId` must exactly match verified customer where present. Signed guest `-` still requires trusted token match and attributable recipient; never infer identity solely from phone/email or cart items. Preserve existing STOP/no-contact and canonical phone revision checks.
4. Only when checkout is **recoverable** and a verified explicit receipt exists, materialise `G`/`R` via existing `Customer`/`CustomerPhone` SQL transaction using `SHOPIFY_NATIVE`, `WHATSAPP_CHECKOUT_RECOVERY`, verified time and revision/decision sequence. A recoverable REVOKE must persist **before** B outreach is denied even if no `CheckoutRecovery` is created. A nonrecoverable/paid/completed checkout does not write consent; its signed receipt is ignored at materialisation time. Missing attribute means no *new* decision; reuse previously verified PostgreSQL GRANTED only under existing customer/recipient/STOP checks.
5. **Cart A / Cart B:** A first recoverable GRANT persists GRANTED and may send initial outreach; B later recoverable REVOKE persists REVOKED and blocks B outreach and A's future unsolicited follow-up. B paid normally => no SQL change; A's already delivered initial message and customer-initiated AI/human service replies remain valid if allowed under 24-hour WhatsApp/moderation/STOP. A subsequent independent recoverable GRANT can reauthorise new proactive sends absent STOP.
6. One-time materialisation and ordering must be enforced with **existing durable checkout/recovery identity** and SQL transaction guards; a duplicate/late A worker after materialised B cannot regrant. If current schema lacks sufficient durable per-checkout evidence, return `MATERIALISATION_IDEMPOTENCY_BLOCKER` and stop (do not decide a new table/enum/sequence workaround). Do not sort solely by client acceptedAt; signed timestamps are audit evidence, not durable commit identity.
7. For all future proactive outbound initial/retry/follow-up/multipart, retain the short current PostgreSQL final-send guard and STOP. Never check Redis consent or the old Shopify `defaultPhoneNumber.whatsAppMarketingConsent`; do not accidentally apply proactive rules to legitimate customer-initiated service replies or alter billing/ARCH-076 sender assignment.

## Typed outcomes

- `NOT_RECOVERABLE_TERMINAL`: no new SQL/outreach; `NO_EXPLICIT_CHOICE`: no new decision, current SQL only; `INVALID_OR_AMBIGUOUS_RECEIPT`: no new decision or proactive outreach relying on this evidence; `DEFER_CHECKOUT_BINDING`: no consent write/outreach if missing trusted event identity; `DEFER_IDENTITY_OR_RECIPIENT`: no SQL/outreach; `MATERIALISED_GRANTED`: one durable SQL write and normal admission; `MATERIALISED_REVOKED`: one durable SQL write, no new proactive outreach; `ALREADY_MATERIALISED`: SQL unchanged; `BLOCKED_STOP`: preserve STOP; `MATERIALISATION_FAILURE`: no false success/partial materialisation. Reuse existing return shape, don't build a second state machine.

## Required integration tests and release blockers

- Disposable PostgreSQL with real current `CustomerPhone` constraints, unit tests for Shared-authenticated receipt verifier, key-ID rotation with old key retained, token/AAD binding, guest/new customer, tampering/copy/wrong tag, missing/duplicate attr, provider errors and identical/no-choice.
- Recoverable A GRANT -> one initial outreach; B pre-recoverability REVOKE -> SQL unchanged; B paid -> SQL unchanged; B recoverable -> SQL REVOKED even when B has no outreach; A unsent proactive follow-up denied; legitimate inbound A reply/AI-human response remains eligible under service window; independent STOP remains immediate.
- Inject crash after SQL commit and before job acknowledgement; replay A after B and B duplicate, verify no newer stored permission regresses; include two overlapping recoveries and test preflight/final-send fences. If cannot prove idempotency using current schema, block acceptance instead of weakening enforcement.
- Preserve order completion, existing BullMQ retry/idempotency and provider error logs, billing credit compensation, 2 proactive cap, Woo regression and ARCH-076 sender route. Do not modify migrations, Woo/API, `_index.md` or create Redis consent infrastructure.
