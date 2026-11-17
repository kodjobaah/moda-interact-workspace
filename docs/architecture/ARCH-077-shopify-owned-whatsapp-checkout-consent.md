---
id: ARCH-077
title: Shopify-owned WhatsApp consent via signed checkout attribute and deferred PostgreSQL materialisation
status: proposed
coordinator: moda_architect
created: 2026-11-17
updated: 2026-11-17
---

# ARCH-077 — Shopify-owned WhatsApp checkout consent

> **Architect reconciliation — 17 November 2026, Shopify-002 task worktree.** This document supersedes the earlier Redis-cart-consent/marker association design **for new implementation**. The proof of Shopify attribute transport is complete, but the current `moda-interact` S002 runtime source has not yet been converted. **Do not merge this task branch as completed runtime** until its implementation is reconciled and retested. S001 and SHARED-001 remain accepted historical results, not requirements to repeat the marker experiment.

## Binding specification

The complete, executable v1 decision is [Shopify checkout-attribute receipt v1](ARCH-077/checkout-attribute-consent-v1.md). It prescribes exact wire format, signed verification, source files, Shopify plan placements, failure semantics, Background materialisation/idempotency, rollout and test gates. If an agent sees a conflicting Redis-based instruction in older task notes or completion reports, **the linked v1 specification prevails**. Do not invent an alternative. Agents must stop on a concrete unsupported SDK/source contract, not make architectural decisions.

## Purpose and boundaries

The original Shopify production regression was that abandoned checkout had a verified Shopify customer and billing/shipping phones but `customer.phone` and `customer.defaultPhoneNumber` were null. Shopify-native WhatsApp marketing consent is **not** required: Moda owns the checkbox and uses its own Meta sender.

- Exactly one customer-facing location by plan: **non-Plus cart App Block** or **Plus checkout UI extension**, never both. English copy stays **`Send me WhatsApp shopping updates, reminders and offers.`** Shopify 20-locale equivalents preserve meaning; no Woo translation import or Shopify Messaging dependency.
- One signed Shopify checkout attribute `moda_wa_consent_v1` holds a checkout-scoped temporary explicit `GRANT`/`REVOKE`. Standard cart uses Ajax Cart API to write the attribute and Shopify carries it into checkout; Plus writes via Shopify Checkout UI Extension. **No Redis consent choice, marker association or temporary-consent TTL.** Existing Background Redis/BullMQ *checkout processing* is unchanged.
- Background reads the unique attribute through the **existing** authoritative Shopify `AbandonedCheckout.customAttributes` lookup, validates signature and independent shop/checkout/customer/recipient binding, then **only if checkout is independently recoverable** persists GRANT/REVOKE to existing PostgreSQL `CustomerPhone` under `SHOPIFY_NATIVE`, `WHATSAPP_CHECKOUT_RECOVERY`, STOP and revision constraints. Ineligible or paid checkout never changes SQL; missing/invalid attribute never manufactures consent.
- Current PostgreSQL permission determines future **proactive** sends, retries and unsent follow-ups. A later materialised Cart B REVOKE blocks unsent Cart A proactive messages, but not valid customer-initiated AI/human replies within WhatsApp 24-hour service conditions; STOP remains immediate and independent. No click-time SQL change or Redis suppression.
- No new SQL migration, table, enum, separate API app, queue, scheduler, Redis preference store or mandatory Shared package change. The completed SHARED-001 marker fields stay optional/unused until separately retired; no rollback of completed Shared work in this task branch.
- **Limit of stateless design:** an old legitimately signed receipt can be restored within the **same** checkout. HMAC prevents modification but not this replay; do not falsely assert otherwise. Cross-shop/checkout copying is denied by binding checks. The user's requested minimalist approach explicitly keeps no new action-history store; any decision to require strict same-checkout replay prevention must return to the architect.

## Actual proof and source status

- 17 November 2026: non-Plus cart test marker survived into authenticated `CHECKOUTS_CREATE`/`CHECKOUTS_UPDATE` and authoritative `AbandonedCheckout.customAttributes`. The marker SHA-256 prefix was `ef5dbf7582291225` across both; the checkout GraphQL result was `gid://shopify/AbandonedCheckout/67330154594377`. This proves **transport**, not signed receipt issuance or live Plus support.
- In the uploaded **ARCH-077-SHOPIFY-002** task-worktree snapshot, `app/services/shopify-consent/shopify-consent.server.ts` still contains Redis prepare/choice logic and `app/routes/shopify/consent/route.ts` still implements temporary marker endpoints. Both must be rewritten by S002 before its existing review is accepted. S002's previous Redis-focused tests cannot stand as evidence for the new receipt architecture.
- Deployment remains gated on real Plus extension verification, Shopify signed App Proxy/checkout authentication, matching event token, Background idempotency and actual published app/Shared versions. A document patch alone changes none of those.

## Task ownership and ordering

| Task | Status/role under this reconciliation |
| --- | --- |
| SHOPIFY-001 | `complete`, accepted historical cart-to-checkout marker experiment; not re-run |
| SHARED-001 | `complete`, backward-compatible optional marker fields remain unused |
| **SHOPIFY-002** | `ready` / **Changes Requested; unclaimed Attempt 2 rework**: stateless receipt issuance, verification contract and returning shopper SQL read |
| SHOPIFY-003 | `pending`: non-Plus cart App Block writes the **single signed attribute** |
| SHOPIFY-004 | `pending`: Plus checkout UI Extension writes the **same attribute**, never cart+checkout controls together |
| SHOPIFY-005 | `pending`: merchant activation/placement and 20 locales, returning SQL consent display |
| BACKGROUND-001 | `pending`: thin authoritative checkout candidate / attribute-read integration, **no Redis consent correlation or cleanup** |
| BACKGROUND-002 | `pending`: verify receipt, recoverability and existing PostgreSQL consent materialisation/final-send |
| SHOPIFY-006 | `pending`: retire old Shopify native consent publisher/sync; no compatibility layer |
| SYSTEM-TEST-001 | `pending`: real browser/Shopify, disposable PostgreSQL/Redis worker isolation and final outbound certification |

**Dependency rule:** S002 is `ready` only for its own correction attempt; its dependencies remain accepted. S002 corrections must be reviewed/accepted before S003, S004 and B001 implementation proceeds. B002 follows accepted B001; S006 and final system-test follow existing prerequisites. This architect transition from `review` to `ready` clears S002 claim metadata while preserving `attempt: 1`; only the launcher may claim Attempt 2. Downstream tasks remain gated and agents must not promote them. Task paths are stable for the existing launcher; filenames mentioning Redis are legacy paths, **not** permission to restore Redis consent storage.

## Execution/validation protocol

- Work in the existing S002 task branch/submodule; preserve original task reports and SHAs. Code rework must be separately committed and tested. Parent workspace documentation changes only become `main` changes after the intended worktree merge.
- Report exact changed paths, source commit SHAs, Shared version pins, scripts and environment, `git diff --check`, unit/integration results, real Shopify plan/browser observations and actual error messages with sensitive redaction. No unsupported claims of executed tests.
- Never modify `docs/decisions/**/_index.md`, old migrations or unrelated Woo/API. Do not merge or deploy a stale Redis-based SHOPIFY-002 implementation under the revised contract.


## Architect rework disposition — 17 November 2026

The SHOPIFY-002 Attempt 1 runtime submission is **Changes Requested**, not accepted. Architect has returned this same task to `ready` and cleared its prior claim to enable the standard task launcher to claim Attempt 2. The accepted signed-checkout-attribute v1 specification is the mandatory implementation contract. S001 and SHARED-001 remain `complete`; none of S003/S004/S005/B001 is unblocked by this rework transition. After the agent implements and validates the correction it must set SHOPIFY-002 back to `review` for a fresh architect inspection.
