---
id: ARCH-077-BACKGROUND-002
architecture_id: ARCH-077
title: Materialise Moda Shopify checkbox consent at recovery and enforce stored permission
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-BACKGROUND-001]
enables: []
created: 2026-11-17
updated: 2026-11-17
---

# Materialise Moda Shopify checkbox consent at recovery and enforce stored permission

## Architecture / status

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Draft amendment, pending architect acceptance.** Interpret this task together with the accepted SHOPIFY-001, SHOPIFY-002 and BACKGROUND-001 consent contracts. Earlier draft language making Redis the permanent consent authority or requiring Redis checks at every send is superseded by this task. The parent architecture and remaining drafts require final reconciliation before implementation.

## Objective and fixed ownership

Only **when an authoritative Shopify abandoned checkout becomes recoverable**, apply the latest explicit Moda checkbox selection for that checkout to the existing PostgreSQL customer/phone consent state. If there is no explicit selection, use the existing verified customer consent already in PostgreSQL. Admit recovery only with effective GRANTED permission, an eligible recipient and normal STOP/other safeguards. Later proactive sends use **existing PostgreSQL preflight and final SQL fences**, not temporary Redis consent. Do not add a new worker, queue, persistent Redis customer-preference index, database migration or native Shopify WhatsApp marketing-consent dependency.

- Shopify (`moda-interact`) owns the checkbox and the temporary Redis choice writer; BACKGROUND-001 owns verified cart-to-checkout correlation and temporary Redis lifecycle. This task reads their frozen contract and owns **recovery-time consent materialisation and outbound admission**.
- `commerce.CustomerPhone` remains the persistent current-permission authority for returning customers and subsequent recoveries. In this Shopify workflow, the existing database enum `SHOPIFY_NATIVE` is **the approved identifier for evidence established by Moda's own Shopify checkbox**. It does **not** instruct any consumer to query Shopify Messaging or `defaultPhoneNumber.whatsAppMarketingConsent`.
- `WHATSAPP_CHECKOUT_RECOVERY` purpose, decision revision/sequence, verified timestamps, matching recipient, merchant-scoped no-contact/STOP and final-send safeguards remain mandatory. `WOO_MODA_CHECKBOX` and WooCommerce API/Background paths are unchanged.
- A checkbox selection **never** writes to PostgreSQL during an ordinary cart/checkout interaction. Neither GRANT nor REVOKE is persisted when a customer completes a checkout without recoverable abandonment. This agreed deferred lifecycle applies also to returning customers.
- Do not represent a mere checkbox display, a cart/checkout webhook, a phone number in a Shopify address or a missing Redis record as a fresh opt-in or opt-out.

## Verified existing touchpoints (inspect current source before editing)

- `src/services/abandoned-checkout-lookup.service.ts`, `src/domain/abandoned-checkout.ts`, `src/services/checkout-recovery/recovery-mappers.ts`: Shopify abandoned-checkout contact projection.
- `src/services/checkout-recovery/recovery-materialization.service.ts`, `recovery-recipient-resolver.service.ts`, `recovery-shopify-customer.service.ts`, `recovery-initiation.service.ts`, `recovery-consent-admission.service.ts`: maturity, identity/phone resolution, first admission and re-entry.
- `src/services/shopify-whatsapp-consent.service.ts` and `src/services/shopify-whatsapp-consent/recipient.ts`, `projection-writer.ts`: replace the old provider-read semantics on the actual Shopify recovery path while preserving source/STOP/revision invariants. S006 later removes obsolete native provider and sync entrypoints.
- `src/services/recovery-conversation/recovery-stored-consent.service.ts`, `recovery-runtime-eligibility.service.ts`, `src/services/recovery-multipart/fence.ts`: existing stored-consent preflight, final SQL fence and multipart checks.
- `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`, `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts`: existing initial, retry, follow-up and delivery paths.
- `src/services/whatsapp-contact-opt-out/stop-writer.ts`, `src/services/pending-recovery-candidate/checkout-order-guard.service.ts`: preserve STOP, order-completion guard and checkout locking.

## Recovery-time sequence — no separate consent scheduling

1. Allow the existing merchant-defined delay, checkout/order guard, bounded Shopify verification and candidate handling to run unchanged. Only after the checkout is **confirmed abandoned and eligible for recovery** may this task materialise a new consent selection.
2. Resolve the verified `shopId + checkoutToken` and associated `cartToken` through BACKGROUND-001's separate consent namespace. Read the latest accepted **explicit** cart/checkout selection and its originating action timestamp/revision. Missing selection is distinct from an explicit unchecked REVOKE. If the Redis read/association is unavailable or indeterminate, do not infer permission; use the existing eligible retry/defer policy rather than treating an unverified result as a successful materialisation.
3. Resolve the Shopify customer from its authenticated, shop-scoped Shopify identity where present. Never merge two customers using only a matching phone or email. An unverified guest identity/ownership association cannot be silently fabricated; stop for architect review if the approved S001 guest binding cannot establish the intended customer/recipient.
4. Obtain available checkout phones from the existing authoritative Shopify abandoned-checkout lookup, including `customer.phone`, `billingAddress.phone` and `shippingAddress.phone` (in that **priority**). Select the first valid, attributable candidate, normalising with the published Shared recipient identity contract. Differing numbers are not automatically an error; an absent/invalid candidate falls through to the next source. A number known to be a third-party shipping contact is not automatically authorised. Do not attach an unrelated recipient by phone-only lookup.
5. Update/resolve the correct existing `Customer` and active `CustomerPhone` using the selected recipient; on a changed phone, preserve existing STOP/suppression history and never reformat into a new row merely to clear a STOP. A verified same-customer ongoing grant may apply to a subsequent eligible checkout/recipient, subject to the approved phone-ownership and STOP checks; do not assume a phone alone proves ownership.
6. If the checkout has an explicit Redis **GRANT** or **REVOKE**, apply it to the persistent customer consent state using the existing `SHOPIFY_NATIVE` enum, `WHATSAPP_CHECKOUT_RECOVERY` purpose and normal revision, decision-sequence and timestamp guards. The accepted original checkbox decision timestamp orders competing actions; worker processing order must not allow an older GRANT to overwrite a later REVOKE. A later deliberate GRANT may supersede an earlier REVOKE. Keep STOP authoritative regardless of either decision.
7. If the checkout has **no explicit selection**, read the current verified PostgreSQL customer/recipient decision. GRANTED can authorise a future recoverable checkout without a new checkbox action; UNKNOWN/REVOKED/no-contact cannot. A status read itself never creates a new decision.
8. Complete the persistent write successfully **before** treating consent as materialised or proceeding with the normal first-recovery admission. First-send reentry uses the **current stored** permission and cannot call Shopify's native WhatsApp marketing-consent provider. No `CheckoutRecovery` is created solely because consent was absent.
9. Return an explicit materialisation result to BACKGROUND-001. On successful application, B001 may remove the temporary Redis selection at the approved lifecycle point. A failed, conflicted or retryable SQL write must not be acknowledged as applied or cause premature cleanup. Completed/cancelled/ineligible checkouts clean up temporary selections through B001 without a PostgreSQL consent decision write.
10. The normal existing billing, message allowance, initial/follow-up scheduling, WhatsApp sender allocation, product/price checks and order-completion guards remain in charge. Consent capture must not itself send messages or reserve credits.

## Re-entry, provider dispatch and STOP

- **Do not use Redis as a consent authority after successful materialisation.** Subsequent initial-send retries, follow-ups and proactive provider sends read current `CustomerPhone` permission using the existing preflight and short PostgreSQL final-send transaction.
- Preserve `checkFinalStoredRecoveryConsent` and its exact shop/customer/active phone, canonical recipient, `SHOPIFY_NATIVE`, purpose, decision, verified timestamps, consent/no-contact revisions and STOP checks. No Redis network operations are added inside that SQL transaction, and no replacement distributed Redis/SQL dispatch lock is required.
- Update the Shopify consent admission and materialisation callers so `SHOPIFY_NATIVE` rows are written from Moda-verified Shopify checkbox decisions **without querying** `defaultPhoneNumber.whatsAppMarketingConsent`. Do not simply remove or bypass a final stored-consent fence.
- A current PostgreSQL REVOKED/UNKNOWN decision, a newer materialised withdrawal or any local STOP prevents future proactive sends. Customer-originated replies, merchant human handover and WhatsApp 24-hour policies must not accidentally inherit a new proactive-only requirement.
- Existing order-completion fences, suppression, credit reservation/release and ARCH-076 sender assignment/idempotency remain unchanged. A send already accepted by the provider is not recallable. Never claim a transient unmaterialised Redis selection has changed the persistent state of earlier recoveries.
- Shopify-native provider-sync jobs already queued before S006 must not re-grant, rewrite or invalidate Moda's new checkbox decisions. Coordinate that retirement with S006, without changing the database schema or reinterpreting Woo evidence.

## Redis and database boundaries

- Read only versioned ARCH-077 consent keys frozen in S001/B001. **Never** alter `pending-recovery:index:checkout:*`, `pending-recovery:index:cart:*`, `pending-recovery:index:shop:*`, `pending-recovery:lock:*`, `pending-recovery:order-completed:*`, BullMQ job payloads, job IDs, queue delays or TTLs for consent storage.
- Do not introduce permanent Redis customer consent/history, new database tables, enums, fields, migrations, new recovery queues, secondary Shopify consent API service or WooCommerce application/API changes.
- Keep database access limited to existing recipient/customer, consent and admission operations; avoid duplicate shop/customer queries, diagnostic-only SELECTs and long transactions containing Shopify API/Redis network calls.
- Log the original safe Redis/Shopify/Prisma error message and relevant provider details at the server boundary with secret/PII redaction; return fixed, non-sensitive failure codes. A Redis failure or missing evidence is not a valid consent decision.

## Required tests and acceptance

- New authenticated Shopify customer with an explicit GRANT: abandoned checkout verified, recipient resolved, stored consent GRANTED, normal recovery admitted.
- Existing customer GRANTED and **no new checkbox action**: future abandoned checkout uses stored permission without minting another GRANT. Existing REVOKED/UNKNOWN denies.
- Existing customer GRANTED, explicit REVOKE on a new cart, checkout **becomes recoverable**: newer REVOKE is materialised before admission and blocks outreach. The same new cart **completes normally**: no SQL update, no recovery, temporary consent cleaned by B001, per approved lifecycle.
- Newer explicit GRANT after earlier REVOKE is accepted; older delayed GRANT processed after a newer REVOKE is rejected as stale. Parallel eligible checkouts for one customer remain correctly ordered across retries.
- `customer.phone = null`, billing and shipping phones present: billing used; valid customer phone takes precedence over different billing phone; invalid customer phone falls back to billing; no false ambiguity simply because numbers differ. Known unrelated shipping recipient is denied.
- Changed recipient, Shopify customer identity/phone mismatch, unverified guest association, missing Redis state, Redis outage, duplicate action, conflicted association, failed SQL write, aborted eligibility and premature cleanup all fail closed appropriately.
- Existing STOP across consent/recipient changes; no-contact revision and final SQL fence preserve suppression. Existing initial/reentry/retry/follow-up/multipart paths use PostgreSQL after materialisation; no native Shopify marketing-consent API read.
- Order completion, merchant-configured maturity, bounded Shopify retries, credit compensation, ARCH-076 sender allocation and WooCommerce regression stay unchanged.
- Execute disposable PostgreSQL + Redis integration tests with real concurrent accepted decisions and rejected stale replay, plus Shopify/Meta mocked boundary tests; verify exact task worktree/commit/submodule pin and container cleanup. Do not present mocked tests as real provider evidence.

**Stop conditions:** Abort implementation and report an architect blocker if the S001 guest/session binding cannot identify the intended recipient, if a newly accepted consent decision cannot be persisted under the existing `SHOPIFY_NATIVE` constraints without database changes, if an old/native provider sync job can overwrite checkbox materialisation, if old grants supersede newer withdrawals, or if any proactive final-send path can bypass the current stored-consent/STOP fence. Do not weaken the existing SQL constraints or WooCommerce policy to make tests pass.
