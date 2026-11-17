---
id: ARCH-077
title: Shopify-owned WhatsApp checkout consent with temporary Redis choices and deferred PostgreSQL materialisation
status: proposed
coordinator: moda_architect
created: 2026-11-17
updated: 2026-11-17
---

# ARCH-077 — Shopify-owned WhatsApp checkout consent

> **ARCHITECT-RECONCILED TASK DEFINITIONS — not implementation acceptance.** All nine tasks remain `pending`. S001 first verifies/finalises the exact integration contract and returns evidence for architect acceptance; dependent agents must not invent missing Shopify identity or Redis contracts. No application code or runtime data is changed by this document.

## Purpose and ownership

In a real Shopify abandoned-checkout test, the checkout had a Shopify customer ID and billing/shipping phones but `customer.phone` and `customer.defaultPhoneNumber` were null. Background found the checkout and returned `deferred-no-recipient`. ARCH-077 replaces the Shopify-native WhatsApp marketing-consent dependency with **Moda's own Shopify checkbox**, without changing WooCommerce or requiring Shopify Messaging.

- `moda-interact` owns Shopify's consent capture, authenticated status reads, two Shopify extension presentations and temporary Redis writes; `moda-interact-background` owns cart-to-checkout association, recoverability, recipient selection, PostgreSQL materialisation and outreach admission.
- `moda-interact-api` is WooCommerce-facing and `moda-interact-woocommerce` stays unchanged. No new standalone Shopify API application.
- **No database migration, schema/enum/table change.** Existing `commerce.Customer`, `commerce.CustomerPhone`, revisions and STOP protection are reused. The existing enum value **`SHOPIFY_NATIVE` is the approved database identifier for Moda's Shopify checkbox consent** in this initiative; it does **not** require a Shopify-native WhatsApp marketing API observation. Obsolete provider reads, projection/sync writers and webhook processing must be retired in B002/S006. Do not use the WooCommerce-installation-bound `commerce.WhatsAppConsentEvidence` table for Shopify.
- The customer-facing checkbox wording is **exactly** `Send me WhatsApp shopping updates, reminders and offers.` Reuse its meaning in Shopify-owned translations; do not import WooCommerce implementation or alter the wording. Permission covers checkout-recovery shopping updates, reminders and offers from the identified merchant, not unrelated campaigns or other merchants.
- Existing merchant-defined inactivity delay, Shopify abandoned-checkout verification retries, order/payment cancellation, STOP, billing/credit compensation, moderation, two-proactive-outreach limit, human/AI communication controls and ARCH-076 sender routing remain in force.

## Consent policy — customer scope, checkout correlation

- Consent is **merchant-scoped customer permission**, valid for future eligible abandoned checkouts once recorded in PostgreSQL, not merely permission for the first basket. Cart/checkout tokens provide a verified path from the explicit selection to the recovery being processed; they are not lasting customer identities.
- The **latest accepted deliberate action** wins for the same verified customer/merchant when applied through the approved recovery lifecycle: an explicit later GRANT reauthorises after an earlier REVOKE, and a later REVOKE supersedes an earlier GRANT. Delayed older checkout jobs/actions cannot overwrite newer accepted decisions. A render, unchecked default, database status read, cart event or checkout event never creates a decision.
- **At checkbox interaction:** record only a temporary GRANT/REVOKE choice in a separate Shopify consent Redis namespace. No `Customer`, `CustomerPhone`, consent revision, STOP or SQL evidence change occurs, **including when a returning customer unchecks an already checked box**.
- **At eligible abandonment:** Background retrieves the authoritative Shopify abandoned checkout; resolves the verified customer and recipient; obtains the latest verified temporary choice (if any); and applies that choice to existing PostgreSQL consent state **only when the checkout becomes recoverable**. If there is no explicit choice, it may reuse already verified PostgreSQL consent for that shop/customer/recipient. STOP overrides any grant.
- **At normal completion or definitive ineligibility:** no PostgreSQL consent update occurs. Temporary Redis consent is cleaned up through the existing recovery lifecycle. A returning customer's next new cart reads the still-current PostgreSQL permission again. This is the approved deferred-grant/deferred-withdrawal business rule; no click-time SQL withdrawal exception is part of ARCH-077.
- PostgreSQL is authoritative **after materialisation** for initial proactive outreach, re-entries, retries, follow-ups and the existing final SQL dispatch fence. Redis is not a permanent customer-preference database and is not queried on every later send. Do not introduce a Redis/PostgreSQL distributed final-dispatch lock.

## Presentation and returning customer

**A — Standard-plan cart page:** A merchant-enabled Shopify Theme App Extension App Block, added/saved through Shopify's theme editor, reads the current Ajax cart token and submits only deliberate changes to the authenticated Moda Shopify backend. An authenticated `checkouts/create` event provides `shopId + cartToken + checkoutToken` for B001's association. Support consent before/after the relevant webhooks without guessing identity from email, phone, matching products or timestamps. The Shopify settings UI provides a verified cart-template activation deep link/status; installed or previewed is not automatically published/active.

**E — Shopify Plus checkout:** A distinct Checkout UI Extension at the supported `purchase.checkout.contact.render-after` target uses Shopify's signed extension context and verified checkout token to write directly to checkout-scoped temporary Redis consent. When both extensions are enabled, display the latest authenticated, accepted explicit choice for the current checkout/cart before falling back to previously verified PostgreSQL permission; display alone never records a new grant.

**Returning authenticated customer, new cart:** Identify the customer by verified Shopify customer identity within the merchant scope, not by the new cart token. Read their already materialised current `CustomerPhone` consent and no-contact status **from PostgreSQL through S002**. A verified GRANTED decision displays checked; REVOKED/UNKNOWN/ambiguous/unavailable evidence cannot be claimed granted. An explicit change is temporarily recorded on the current cart/checkout and only materialised if it becomes recoverable. Guests with a new unrelated cart do not inherit previous permission from a matching phone or email.

**Shopper failure behaviour:** If Moda's status/write endpoint or Redis is unavailable, both extensions fail **silently**: no error banners, toasts, prompts or blocking payment/navigation. Hide only Moda's control when its initial status cannot be verified; never visually claim an unacknowledged action succeeded. The server preserves original useful underlying errors with required secret/PII redaction.

## Recipient and verified recovery

At eligible abandoned-checkout maturity, B002 reads the existing authoritative Shopify lookup and considers contact candidates in this priority: **customer phone → billing phone → shipping phone**. An invalid or absent higher-priority number may fall back to the next valid, attributable number. Different values across these fields are not automatically ambiguous; a known third-party shipping contact must not be treated as the consenting customer merely because the number appears on the address. Use the published Shared canonical phone contract, the correct shop/customer identity, and preserve any pre-existing STOP/no-contact history on formatting/phone changes. No additional cart-page phone field is required.

`customer.phone = null` with matching billing/shipping phone is the observed regression case. Neither finding a number nor discovering an abandoned checkout manufactures consent. The old Shopify `defaultPhoneNumber.whatsAppMarketingConsent` API is not consulted.

## Redis ownership, ordering and cleanup

- S001 must freeze **exact, versioned and independently namespaced** temporary cart choice, checkout choice and verified cart-to-checkout association records, keyed with scoped encoded/token-digest identities, including replay handling, accepted-action ordering, expiry and cross-repository test vectors. **Do not create permanent Redis customer-preference or consent-history mirrors.** Store only bounded evidence required to process the active cart/checkout.
- Consent writes are acknowledged only after atomic Redis success. Duplicate actions are idempotent, conflicting replays fail and older accepted actions must not be replayed over later choices. B001 does not grant permission on a webhook.
- Temporary consent survives normal candidate activity, merchant-configured maturity, bounded abandoned-checkout visibility retries and any necessary recoverability/materialisation retry. Cleanup occurs only after a successful B002 materialisation or after the cart/checkout has definitively completed or become ineligible. An active cart with no checkout has separately bounded retention. No premature cleanup on theme navigation, job-index deletion or frontend unload.
- Consent keys are **not** the existing `pending-recovery:index:checkout:*`, `pending-recovery:index:cart:*`, `pending-recovery:index:shop:*`, `pending-recovery:lock:*`, `pending-recovery:order-completed:*` or BullMQ job/payload keys. Those owners retain their exact values, TTLs, rescheduling and deletion semantics. No `KEYS` scans, `FLUSH*`, global Redis policy changes or new consent queue/scheduler without separate approval.
- Redis outage, lost evidence or indeterminate association must never manufacture permission. Existing PostgreSQL consent may be used only when the absence of a pending choice is **verified** under the approved S001/B002 read contract; a failed Redis read must not be treated as an empty choice.

## Persistent consent and final dispatch

- B002 performs any required `Customer`/`CustomerPhone` mutation **only at recoverable checkout maturity**, using the existing `SHOPIFY_NATIVE`, `WHATSAPP_CHECKOUT_RECOVERY`, verified timestamps, monotonic decision sequence/consent revisions and STOP/no-contact columns. A newer accepted checkout decision cannot be undone by an older delayed worker. Newer explicit GRANT can follow REVOKE without clearing STOP.
- Following materialisation, the existing `RecoveryStoredConsentService`, `recovery-runtime-eligibility.service.ts`, `checkFinalStoredRecoveryConsent`, multipart and outbound admission paths read current PostgreSQL consent and enforce the short final SQL fence. No Redis read inside that transaction; do not disable the final gate. Customer-initiated replies and WooCommerce's separately owned admission policy remain unchanged.
- The obsolete Shopify native-consent GraphQL provider, webhooks, job publisher, sync processor and projection behavior are removed through B002/S006. **Preproduction:** no legacy-job adapter or data compatibility is required; any environment cleanup must be scoped and must not flush the shared checkout/cart/order queues or unrelated customer/STOP data.
- Existing Shopify consent table limitations remain explicit: `CustomerPhone` is current durable permission, whereas the Woo-bound `WhatsAppConsentEvidence` cannot serve as Shopify disclosure-event history. ARCH-077 forbids new tables; do not claim a complete immutable Shopify SQL evidence history that does not exist. S001/B002 must specify what bounded Redis evidence is available at materialisation and report any audit/proof blocker rather than bypass the approved storage boundaries.

## Execution graph and task register

| Task | Repository | Depends on | Implementation responsibility |
| --- | --- | --- | --- |
| [SHOPIFY-001](../decisions/shopify/ARCH-077/SHOPIFY-001-freeze-shopify-identity-and-redis-contract.md) | `moda-interact` | none | Prove Shopify identities and freeze Redis/read/write contracts; architect acceptance gate |
| [SHOPIFY-002](../decisions/shopify/ARCH-077/SHOPIFY-002-capture-checkout-consent-in-redis.md) | `moda-interact` | S001 | Shopify-authenticated temporary Redis choice service; returning-customer SQL read |
| [SHOPIFY-003](../decisions/shopify/ARCH-077/SHOPIFY-003-render-cart-page-consent.md) | `moda-interact` | S002 | Merchant-enabled cart App Block, activation link, silent shopper failure |
| [SHOPIFY-004](../decisions/shopify/ARCH-077/SHOPIFY-004-render-plus-checkout-consent.md) | `moda-interact` | S001/S002 | Plus checkout extension, direct checkout choice, silent shopper failure |
| [SHOPIFY-005](../decisions/shopify/ARCH-077/SHOPIFY-005-returning-customers-withdrawal-and-locales.md) | `moda-interact` | S002/S003/S004 | Returning-customer presentation verification, merchant activation/settings and 20 locales |
| [BACKGROUND-001](../decisions/background/ARCH-077/BACKGROUND-001-associate-cart-consent-with-checkout.md) | `moda-interact-background` | S001/S002 | Cart-to-checkout association and temporary Redis cleanup without touching worker indexes |
| [BACKGROUND-002](../decisions/background/ARCH-077/BACKGROUND-002-gate-recovery-and-final-dispatch-by-consent.md) | `moda-interact-background` | B001 | Recoverable-checkout recipient and SQL consent materialisation; preserve final SQL fence; retire native sync |
| [SHOPIFY-006](../decisions/shopify/ARCH-077/SHOPIFY-006-retire-native-whatsapp-consent-integration.md) | `moda-interact` | B002/S005 | Remove Shopify native consent webhook ingress/publisher; no preproduction compatibility |
| [SYSTEM-TEST-001](../decisions/system-test/ARCH-077/SYSTEM-TEST-001-certify-shopify-consent-and-redis-isolation.md) | `moda-interact-system-test` | S003/S004/S005/B001/B002/S006 | Real Shopify browser and disposable Redis/PostgreSQL end-to-end certification **after S006** |

**Suggested execution:** S001 → S002 → (S003, S004, B001 in parallel when their contracts are frozen) → (S005 and B002 after their prerequisites) → S006 → SYSTEM-TEST-001. The `depends_on` metadata in each task is the authoritative executable ordering. All tasks remain `pending` until claimed; architectural review alone does not make them `in_progress` or `completed`.

## Review/implementation protocol

- Task definitions are architect-owned. Do not edit `docs/decisions/**/_index.md`, change task statuses, or start implementation just because this document is patched. S001 contract evidence must receive architect acceptance before its dependants begin.
- Agents must inspect actual code, pinned Shared schemas, configured Shopify app, Redis namespace ownership and applicable Shopify plan before changing source. Provide deterministic file touchpoints, tests and stop conditions; do not make unreviewed architectural decisions.
- All changes must be validated with exact worktree paths, Git SHAs, staging commands, `git apply --check --whitespace=error-all`, unit/integration tests and disposable PostgreSQL/Redis/browser evidence as applicable. Distinguish static findings from executed validations. Preserve original provider/SDK failure details in redacted server-side logs; do not add diagnostic-only Redis/SQL queries.
- No Shopify-native WhatsApp marketing consent, Shopify Messaging dependency, WooCommerce/API change, new PostgreSQL schema or migration, new Redis queue, background scheduler or global infrastructure rewrite is authorised.
