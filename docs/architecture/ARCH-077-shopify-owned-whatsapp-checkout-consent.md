---
id: ARCH-077
title: Shopify-owned WhatsApp consent via signed checkout attribute and deferred PostgreSQL materialisation
status: proposed
coordinator: moda_architect
created: 2026-11-17
updated: 2026-11-18
---

# ARCH-077 — Shopify-owned WhatsApp checkout consent

> **Architect acceptance — 17 November 2026, SHOPIFY-002 Attempt 3.** The Redis-cart-choice design is superseded by the stateless signed checkout-attribute receipt contract. SHOPIFY-002 producer code was inspected and accepted using Shared credential AEAD and the existing keyring; S001 and SHARED-001 remain complete. This acceptance does **not** certify live cart/Plus attribute transport, Background verification, materialisation or WhatsApp dispatch. Those remain separate downstream tasks and system tests.

## Binding specification

The complete, executable v1 decision is [Shopify checkout-attribute receipt v1](ARCH-077/checkout-attribute-consent-v1.md). It prescribes exact wire format, signed verification, source files, Shopify plan placements, failure semantics, Background materialisation/idempotency, rollout and test gates. If an agent sees a conflicting Redis-based instruction in older task notes or completion reports, **the linked v1 specification prevails**. Do not invent an alternative. Agents must stop on a concrete unsupported SDK/source contract, not make architectural decisions.

## Purpose and boundaries

The original Shopify production regression was that abandoned checkout had a verified Shopify customer and billing/shipping phones but `customer.phone` and `customer.defaultPhoneNumber` were null. Shopify-native WhatsApp marketing consent is **not** required: Moda owns the checkbox and uses its own Meta sender.

- Exactly one customer-facing location by plan: **non-Plus cart App Block** or **Plus checkout UI extension**, never both. English copy stays **`Send me WhatsApp shopping updates, reminders and offers.`** Shopify 20-locale equivalents preserve meaning; no Woo translation import or Shopify Messaging dependency.
- One signed Shopify checkout attribute `moda_wa_consent_v1` holds a checkout-scoped temporary explicit `GRANT`/`REVOKE`. Standard cart uses Ajax Cart API to write the attribute and Shopify carries it into checkout; Plus writes via Shopify Checkout UI Extension. **No Redis consent choice, marker association or temporary-consent TTL.** Existing Background Redis/BullMQ *checkout processing* is unchanged.
- Background reads the unique attribute through the **existing** authoritative Shopify `AbandonedCheckout.customAttributes` lookup, validates signature and independent shop/checkout/customer/recipient binding, then **only if checkout is independently recoverable** persists GRANT/REVOKE to existing PostgreSQL `CustomerPhone` under `SHOPIFY_NATIVE`, `WHATSAPP_CHECKOUT_RECOVERY`, STOP and revision constraints. Ineligible or paid checkout never changes SQL; missing/invalid attribute never manufactures consent.
- Current PostgreSQL permission determines future **proactive** sends, retries and unsent follow-ups. A later materialised Cart B REVOKE blocks unsent Cart A proactive messages, but not valid customer-initiated AI/human replies within WhatsApp 24-hour service conditions; STOP remains immediate and independent. No click-time SQL change or Redis suppression.
- No new SQL migration, table, enum, separate API app, queue, scheduler, Redis preference store or mandatory Shared package change. The completed SHARED-001 marker fields stay optional/unused until separately retired; no rollback of completed Shared work in this task branch.
- **Limit of stateless design:** an old legitimately signed receipt can be restored within the **same** checkout. Shared authenticated encryption prevents modification but not this replay; do not falsely assert otherwise. Cross-shop/checkout copying is denied by binding checks. The user's requested minimalist approach explicitly keeps no new action-history store; any decision to require strict same-checkout replay prevention must return to the architect.

## Actual proof and source status

- 17 November 2026: non-Plus cart test marker survived into authenticated `CHECKOUTS_CREATE`/`CHECKOUTS_UPDATE` and authoritative `AbandonedCheckout.customAttributes`. The marker SHA-256 prefix was `ef5dbf7582291225` across both; the checkout GraphQL result was `gid://shopify/AbandonedCheckout/67330154594377`. This proves **transport**, not signed receipt issuance or live Plus support.
- SHOPIFY-002 Attempt 3 was accepted after inspection of the supplied worktree (`96ad35f` implementation; `8ae1840` parent report, both SHAs agent-reported). The producer now uses published Shared AES-256-GCM credential APIs, existing keyring configuration, and corrected signed App Proxy/source checks. The prior Redis and HMAC implementations are superseded. Agent reports 46 focused tests, 168 webhook unit tests, 9 Redis webhook regression tests, lint and build passed; the five unchanged webhook-root type errors persist. Live Plus and authoritative **signed-receipt** GraphQL readback are still outstanding in their owning downstream tasks.
- Deployment remains gated on real Plus extension verification, Shopify signed App Proxy/checkout authentication, matching event token, Background idempotency and actual published app/Shared versions. A document patch alone changes none of those.

## Task ownership and ordering

| Task | Status/role under this reconciliation |
| --- | --- |
| SHOPIFY-001 | `complete`, accepted historical cart-to-checkout marker experiment; not re-run |
| SHARED-001 | `complete`, backward-compatible optional marker fields remain unused |
| **SHOPIFY-002** | `complete`, Attempt 3 architect-accepted stateless signed receipt producer and returning-customer SQL status (not live transport certification) |
| SHOPIFY-003 | `complete`: Attempt 3 architect-accepted non-Plus cart App Block, verified-receipt display, theme editor, cart-change guard and configurable App Proxy root (not live activated/certified) |
| SHOPIFY-004 | `ready`: Plus checkout UI Extension writes/reads back the **same attribute**, never cart+checkout controls together |
| SHOPIFY-005 | `pending`: merchant activation/placement and 20 locales, returning SQL consent display |
| BACKGROUND-001 | `complete`: Attempt 1 architect-accepted authoritative checkout-attribute read on existing bounded lookup; no Redis consent correlation or cleanup |
| BACKGROUND-002 | `ready`: verify receipt, recoverability and existing PostgreSQL consent materialisation/final-send |
| SHOPIFY-006 | `pending`: retire old Shopify native consent publisher/sync; no compatibility layer |
| SYSTEM-TEST-001 | `pending`: real browser/Shopify, disposable PostgreSQL/Redis worker isolation and final outbound certification |

**Dependency rule:** S002 is `complete` after architect acceptance of Attempt 3, enabling S003, S004 and B001 independently. B001 is now architect-accepted `complete` (Attempt 1), so B002 is `ready`. S005 retains its S003/S004 dependencies; S006 and terminal system test retain their prerequisites. Do not start tasks before their own launcher claims; do not treat S002 acceptance as live Plus/Background integration evidence. Filenames mentioning Redis are legacy task paths, **not** permission to restore Redis consent storage.

## Execution/validation protocol

- Work in the existing S002 task branch/submodule; preserve original task reports and SHAs. Code rework must be separately committed and tested. Parent workspace documentation changes only become `main` changes after the intended worktree merge.
- Report exact changed paths, source commit SHAs, Shared version pins, scripts and environment, `git diff --check`, unit/integration results, real Shopify plan/browser observations and actual error messages with sensitive redaction. No unsupported claims of executed tests.
- Never modify `docs/decisions/**/_index.md`, old migrations or unrelated Woo/API. Do not merge or deploy a stale Redis-based SHOPIFY-002 implementation under the revised contract.


## Architect rework disposition — 17 November 2026

The SHOPIFY-002 Attempt 1 runtime submission is **Changes Requested**, not accepted. Architect has returned this same task to `ready` and cleared its prior claim to enable the standard task launcher to claim Attempt 2. The accepted signed-checkout-attribute v1 specification is the mandatory implementation contract. S001 and SHARED-001 remain `complete`; none of S003/S004/S005/B001 is unblocked by this rework transition. After the agent implements and validates the correction it must set SHOPIFY-002 back to `review` for a fresh architect inspection.

## Historical architect disposition — SHOPIFY-002 Attempt 2 (17 November 2026)

The uploaded Attempt 2 implementation is **Changes Requested**, not yet accepted. It introduced a separate `SHOPIFY_CONSENT_RECEIPT_KEY_V1` and local HMAC receipt logic, inconsistent with the already-approved Shared credential keyring and AEAD (`MODA_ENCRYPTION_KEYS_JSON`, `MODA_ENCRYPTION_ACTIVE_KEY_ID`). The immutable, unreleased v1 wire contract is now reconciled in `ARCH-077/checkout-attribute-consent-v1.md` to reuse Shared's existing `CredentialEnvelope`, encrypt/decrypt and key-ID rotation. No additional key/rotation system, Redis consent state, DB schema, job or mandatory Shared publication is authorised. S002 returns to `ready`, clear claim, `attempt: 2` preserved for launcher Attempt 3. S003/S004/B001 still wait for S002 `complete`; B002 consumes the exact updated receipt format. Existing release/Plus/GraphQL verification gates remain unchanged.

## Latest architect disposition — SHOPIFY-002 Attempt 3 (17 November 2026)

Architect accepted the inspected stateless Shopify receipt producer using Shared keyring/AEAD, canonical v1 envelope/AAD and corrected signed App Proxy route. Task `ARCH-077-SHOPIFY-002` is `complete`. S003, S004 and B001 are `ready`; S005/B002 remain gated. Live cart/Plus receipt propagation, consumer parity and recoverable-only SQL materialisation are expressly *not* certified by this producer acceptance; see the SHOPIFY-002 Architect Review for evidence and follow-up ownership.


## ARCH-077-SHOPIFY-003 Attempt 1 review — 18 November 2026

The non-Plus Theme App Block implementation is submitted but **Changes Requested**: its current-cart display assumes every existing receipt is unchecked, rather than verifying the already-saved GRANT/REVOKE. S003 now owns one narrow authenticated `POST cart/verify` integration using existing S002 AEAD verification, with no new state/storage or cryptography. The task returns to `ready` with `attempt: 1`, cleared claim, and dependent SHOPIFY-005 remains gated. Published-theme activation is still S005-owned; live cart/checkout GraphQL transport remains terminal system-test evidence.


## ARCH-077-SHOPIFY-003 Attempt 2 architect review — 18 November 2026

Attempt 2 correctly implements server-verified saved receipt display (`GRANT` checked, `REVOKE` unchecked, no automatic write), authenticated read-only `cart/verify` and theme-editor section reinitialisation. **Changes Requested** remains necessary for one bounded inconsistency: the cart App Block hard-codes `/apps/moda-consent`, although Shopify permits merchant-customised App Proxy prefix/subpath and S002 validates those signed configurations. S003 now owns one validated `app_proxy_root` App Block text setting (default `/apps/moda-consent`) from which its three existing endpoint URLs are derived; S005 later explains merchant configuration. Task returns to `ready`, prior claim cleared, attempt 2 preserved for launcher Attempt 3. No new credential, server endpoint, Redis/SQL state, queue or cryptography. S004 and B001 retain their independent statuses; S005 remains `pending` until S003 **and** S004 are complete. Live Shopify publication/GraphQL and Background verification remain downstream certification.


## Latest architect disposition — SHOPIFY-003 Attempt 3 (18 November 2026)

Architect accepted the inspected non-Plus cart App Block after the remaining proxy-root correction. One configurable `app_proxy_root` supplies the three authenticated receipt/status/verify paths, with bounded same-origin validation; existing receipt state, explicit-only writes and theme-section handling remain correct. Task `ARCH-077-SHOPIFY-003` is now `complete` (Attempt 3). Agent-reported 57 focused tests and Shopify app/Theme Check/build passed; unchanged webhook-route TS7006 baseline errors remain. This is source/test acceptance, **not** live published-theme, signed-App-Proxy or GraphQL readback certification. SHOPIFY-005 stays `pending` until SHOPIFY-004 also becomes `complete`, and must document matching merchant App Proxy path settings. The architect review does not merge source or parent worktrees.
