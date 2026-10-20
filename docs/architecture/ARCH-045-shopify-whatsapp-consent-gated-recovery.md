---
id: ARCH-045
title: Shopify WhatsApp consent-gated recovery, merchant notice and later-consent resumption
status: proposed
coordinator: moda_architect
created: 2026-10-20
updated: 2026-10-20
---

# ARCH-045 — Shopify WhatsApp consent-gated recovery

## Status

**Proposed, portable task definitions only.** The architect has access to the supplied 2026-10-20 snapshot, **not** the developer's Git common-dir, task branches, remotes or canonical worktrees. No task is materially claimed, implemented, reviewed, accepted or Complete. The developer must materialise each canonical task through the approved launcher. This architecture is intentionally limited to **business-initiated Shopify WhatsApp checkout recovery**, merchant notification and resumption when verified consent is given later.

## Problem

The Shopify checkout recovery path currently resolves recipients and applies recipient reachability suppression, but does **not** check Shopify's WhatsApp marketing consent before business-initiated recovery outreach. No consent-specific `RecoveryAdmissionBlockReason` exists. Therefore absent/revoked consent does not create a durable waiting state, merchant notification or later-consent wake-up. Treating a lack of consent as a permanent cancellation would also lose potentially valid recoveries after customers opt in.

**Important distinction:** Shopify Customer Privacy API tracking choices (`setTrackingConsent`, `currentVisitorConsent`, `visitorConsentCollected`) govern storefront tracking purposes, not WhatsApp marketing opt-in. A visitor allowing analytics or marketing cookies **never** authorises a WhatsApp recovery message. Shopify's Admin GraphQL `Customer.defaultPhoneNumber.whatsAppMarketingConsent` is the proposed read-only authority for channel-specific consent. The event trigger is `customers_whats_app_marketing_consent/update` (available in Shopify API 2026-07). The app must not write or fabricate marketing consent.

## Goals

1. Before **every business-initiated recovery WhatsApp template** (initial, scheduled no-response follow-up, merchant post-window recovery follow-up), check Shopify's **current** WhatsApp marketing consent for the **same Shopify customer and the exact current canonical recipient**. Permit only `SUBSCRIBED`; fail closed for other values, missing identity and verification errors.
2. Initial recovery without verified consent remains `DETECTED`, with `admissionBlockReason=WHATSAPP_CONSENT_MISSING`, a bounded 72-hour consent-wait deadline, **no outreach attempt/billing reservation/provider send**, and one idempotent merchant **Support inbox** system message per recovery generation.
3. On Shopify WhatsApp consent-update webhook, asynchronously and idempotently locate eligible blocked recoveries by `(shopId, shopifyCustomerId)`, re-read current Shopify consent, revalidate checkout/eligibility under existing coordination, and resume the **same** recovery generation if still valid. The webhook is a **wakeup**, not consent proof.
4. If the 72-hour deadline passes, expire the blocked recovery without sending. A later opt-in must never revive a terminal or stale recovery. Cleanup must progress even if the opt-in event never arrives.
5. Preserve existing credit/capacity, recipient reachability, original outreach attempt identity, refund/compensation, one sequence-two follow-up, human-control and provider-send protections. No charge for a suppressed/blocked attempt.
6. Prevent cross-shop/customer/recipient confusion, duplicates and races; produce bounded structured diagnostic events without PII.
7. Provide a simple merchant-facing explanation of the native Shopify WhatsApp opt-in path in existing Recovery Settings and Support inbox (not another cookie banner).

## Non-Goals

- Collecting tracking-cookie consent through `setTrackingConsent`, `visitorConsent`, app blocks, theme embeds, custom pixels or a separate CMP; **none** of those is a replacement for WhatsApp opt-in. Such storefront features require their own justified design if Moda introduces tracking or custom consent collection later.
- Sending any WhatsApp message to a customer asking for permission when permission is absent.
- Creating merchant-initiated campaigns or a generic consent management platform.
- Writing consent using `customerWhatsAppMarketingConsentUpdate`; **only Shopify/merchant-approved sources** collect it.
- Replacing provider opt-out/reachability suppression, human inbound replies within the customer-service window, existing credit accounting, or privacy data-export/redaction architecture.
- Full WooCommerce consent implementation: this initiative covers Shopify only and must not infer Woo equivalence.
- New frontend notifications channel, new standalone microservice, new datastore, full CMS or consent-event history warehouse.

## Current Architecture — verified from supplied snapshot

- `moda-interact/shopify.app.moda-interact.toml`: `api_version="2026-07"`, `read_customers`, checkout/cart/order subscriptions, but **no** WhatsApp marketing consent-update subscription. **Caveat:** the snapshot also contains `moda-interact/shopify.app.toml` with substantially different template scopes/configuration. The owning task MUST verify which CLI app config is actually deployed; do not assume both files are authoritative.
- `moda-interact/app/routes/webhooks/root/route.jsx` authenticates Shopify webhooks before `shopify-webhook-ingress.service.ts` publishes supported events to BullMQ using Shared contracts. An unknown authenticated topic is currently ignored.
- `moda-interact-background/src/services/checkout-recovery/recovery-materialization.service.ts`: mature checkout resolves abandoned-checkout state and recipient; missing phone currently defers before materialising recovery and is **not** the same as missing consent.
- `recovery-initiation.service.ts`: materialises DETECTED recovery, checks recipient suppression, creates sequence-one outreach attempt, admits billing, then dispatches provider message. There is no WhatsApp-consent reader.
- `recovery-outreach-follow-up-processor.service.ts` sends scheduled sequence-two follow-up; `recovery-conversation/human-command-evaluation.service.ts` and `human-command-dispatcher.service.ts` govern merchant post-window template follow-up. A consent gate must cover each applicable proactive path; ordinary replies in an active customer-initiated 24-hour service window are not covered by this marketing gate.
- `moda-interact-database/prisma/schema.prisma`: `CheckoutRecovery` already has `status`, `detectedAt`, `admissionBlockedAt`, `admissionBlockReason`, `customerId`, generation uniqueness and indexes. Enum currently contains `RECOVERY_CAPACITY_EXHAUSTED` and `WHATSAPP_RECIPIENT_SUPPRESSED`. `Customer` has unique `(shopId, shopifyCustomerId)`. `MerchantSupportMessage.sourceKey` is unique, and Support inbox UI already reads system messages.
- `recovery-capacity-resume.service.ts` / worker: existing targeted wakeups, checkout lock/recheck, and repair tick. Existing general repair is **capacity-only**; do not repurpose a capacity-reason scan as a consent-resume scan.
- Shared package has Shopify versioned contracts and queue constants, but no WhatsApp-consent-change event contract.

## Proposed Architecture

### Source of consent truth and applicability

- Use the Shopify **Admin GraphQL API 2026-07** (or a newer stable version verified by the Shopify owner) with the already required `read_customers` scope. Query `customer(id: ShopifyCustomerGID) { id defaultPhoneNumber { phoneNumber whatsAppMarketingConsent { state updatedAt } } }` through the existing offline session/token service; verify current schema/field availability in the targeted API release during implementation.
- Resolve a **verified Shopify customer ID** for the shop, then normalise `defaultPhoneNumber.phoneNumber` using the same canonical recipient normalisation as the recovery. `SUBSCRIBED` is necessary **and** the number must equal the recovery's current outbound recipient. Nonmatching phone, absent customer/default phone, missing Shopify ID, `PENDING`, `UNSUBSCRIBED`, `NEVER_SUBSCRIBED`, `REDACTED`, unknown state, insufficient scope or non-successful read all prevent proactive sending.
- The typed Background consent reader returns `allowed`, `not-authorised`, or `verification-unavailable` (no secret/phone in logs). Only Background interprets the provider response; no duplicate Shopify consent state is needed as a durable authority. Consent freshness must be rechecked near the **irreversible provider-send boundary**. If a credit reservation was acquired between an earlier check and a later denial, use existing pre-provider release/correction behaviour. No guarantee is claimed for withdrawal that happens **after** provider dispatch has begun.
- A guest's phone number by itself is **not** proof of Shopify identity or consent. Shopify's consent-update webhook must not locate/recover by phone alone. If no verifiable `(shopId, shopifyCustomerId)` link exists, preserve the blocked state and wait for a legitimate identity-bearing checkout update/within-window re-evaluation; otherwise expire.

### Absent consent / merchant notice

- Only initial outreach with a real canonical recipient and persisted `DETECTED` recovery enters `WHATSAPP_CONSENT_MISSING`. Do **not** classify no-phone candidates as missing consent (ARCH-028 no-recipient path remains independent).
- Compute `consentWaitDeadline = recovery.detectedAt + 72 hours` (fixed v1 policy, not a new setting). Do not reset deadline upon checkout updates, duplicate webhook deliveries, rechecks or reblocking. At or after the deadline, do not send; set existing `EXPIRED` terminal status and status-history reason.
- Blocking happens **before creating sequence-one attempt and before billable reservation**. Use the existing `MerchantSupportThread` / `MerchantSupportMessage` mechanism with `kind=SYSTEM`, `state=AVAILABLE`, one deterministic `sourceKey=arch045:consent-missing:<recoveryId>` per recovery generation, merchant-readable copy and no recipient PII. Notice says consent is not verified, no message/credit was used, and an opt-in in Shopify may permit resumption **before expiry**. Notification failure must be observable/retryable without opening billing/provider admission; state and notification must eventually agree.

### Later consent / safe resumption

1. Shopify publishes `customers_whats_app_marketing_consent/update` on a customer preference change. Shopify ingress authenticates, validates minimal identifiers and durably accepts a small **versioned Shared** event; acknowledge only after queue acceptance. Never enqueue full webhook/phone/consent evidence unnecessarily.
2. Background consumes the event from an isolated consent-event job name/queue registered in the existing worker deployment (no new Render service). Resolve shop/customer identity; select only `DETECTED` consent-blocked recoveries linked to the exact Shopify customer and within 72 hours. Use indexed, bounded pagination and per-checkout coordination; no global scan for every consent webhook.
3. For each candidate, use existing targeted recovery-resume machinery, not a new generic recovery execution path. Fresh Shopify consent, exact current recipient, shop entitlement, checkout still abandoned, no completed order, elapsed recovery delay, suppression, ownership, deadline, generation and attempt idempotency must all be honoured. A later `UNSUBSCRIBED`/stale webhook cannot itself authorise sending; re-read live consent.
4. On successful revalidation clear **only** the consent block on the still-`DETECTED` row and enter existing sequence-one admission, once. If consent remains invalid, retain the block with no new merchant notice. If API unavailable, fail closed with bounded retry; never interpret 404/403/timeout as subscribed. Already terminal/recovered rows are ignored.
5. Prevent orphaned blocks: add deterministic expiry wake-up at the original deadline and **bounded repair of past-deadline consent-blocked rows** to the existing recovery repair cycle. An enqueue error must not silently strand a DETECTED recovery; startup/periodic repair can expire it. No polling of all unexpired opt-in waits.

### Follow-ups and manual actions

- Reuse the **same** injected Background consent policy for scheduled sequence-two outreach and for any merchant-initiated **post-window recovery template**. These must check consent before attempting billing and again as near to actual provider dispatch as practical. Do not mark a non-sent follow-up `SENT`, consume the sequence-two credit or burn its slot merely due to an absent-consent check.
- Keep the human-owned ordinary `HUMAN_TEXT` reply path, when a verified customer-initiated service window is open, separate from proactive marketing-template outreach. Preserve existing WhatsApp platform and moderation checks for both paths.
- Do not add a merchant-side bypass button or allow manual post-window recovery to ignore the consent gate.

## Request / Event Flow

```text
matured Shopify checkout -> real abandoned checkout / recipient
  -> Shopify Admin WhatsApp consent for matching customer and phone
     | SUBSCRIBED + eligible --> existing attempt / credit / provider admission
     | absent/pending/revoked/unknown --> DETECTED + WHATSAPP_CONSENT_MISSING
                                     -> deduped merchant Support notice
                                     -> expiry deadline (72h)

Shopify consent-update webhook (authenticated)
  -> versioned Shared event -> BullMQ (durable acceptance)
  -> Background bounded customer-linked blocked-recovery lookup
  -> targeted existing resume + fresh checkout/Shopify consent check
  -> still valid? yes: same generation / normal admission once
                  no: remain blocked or expire; never bill/send

expiry wakeup + periodic expired-row repair -> EXPIRED if still blocked
```

## Repository Responsibilities

| Repository / owner | Work |
|---|---|
| `moda-interact-database` / `moda_database` | Extend admission-block enum, migration validation. Existing indexed relationships retained. |
| `moda-interact-shared` / `moda_shared` | Canonical v1 consent-update queue contract and publication gate. |
| `moda-interact` / `moda_app` | Confirm actual app-config selection, webhook subscription and authenticated ingress; merchant Recovery Settings guidance. |
| `moda-interact-background` / `moda_background` | Read-only Shopify consent adapter, initial block/merchant notice, event-driven re-entry, deadline expiry/repair, proactive follow-up gate. |
| `moda-interact-system-test` / `moda_system_test` | Black-box merchant/customer workflow and billing/expiry evidence once implementation dependencies are Complete. |

No Gateway deployment-topology changes are currently justified: the work uses existing authenticated Shopify HTTPS ingress, Redis/BullMQ, recovery worker deployment, PostgreSQL and Support inbox. If a new externally exposed route/worker service is actually required, return that gap to `moda_architect` for a bounded `moda_gateway` task; do not add one speculatively.

## Data Model

- Add enum `RecoveryAdmissionBlockReason.WHATSAPP_CONSENT_MISSING` through one Database-owned Prisma migration. **Do not** introduce a parallel consent table, stored consent Boolean, new recovery status or phone-linked consent lookup.
- Use existing `CheckoutRecovery.detectedAt` as immutable deadline anchor; `admissionBlockedAt` is diagnostic only, **not** the expiry clock. Preserve generation uniqueness `(shopId, checkoutToken, generation)`, `Customer (shopId,shopifyCustomerId)` uniqueness and `CheckoutRecovery (shopId,customerId,detectedAt,id)`/`(shopId,admissionBlockReason,status,detectedAt)` access paths. Database owner must confirm actual query plans and add a focused index only if measured necessity is demonstrated.
- Merchant support idempotency uses existing unique `MerchantSupportMessage.sourceKey` and shop-unique thread. `systemCode` is domain-owned; new general-purpose Shared enum is **not** required solely for one service-owned merchant notice unless another consumer needs a stable code.
- Recovery terminalisation creates a normal `CheckoutRecoveryStatusHistory` reason and does not create a new recovery generation. Keep personal data out of status/history metadata.

## Contracts

- `ShopifyWhatsAppConsentChangedJobV1` (proposed): Shared-owned Zod runtime schema and typed export in `@modainteract/moda-interact-shared/shopify` with `{schemaVersion:1, shopId, shopifyCustomerId, deliveryId, triggeredAt}` (all bounded strings; `triggeredAt` UTC ISO or null when absent). `shopifyCustomerId` is normalised as a numeric Shopify customer identifier encoded as a string; the worker constructs/validates a Shopify Customer GID at its boundary. No raw phone, email, consent `state`, full customer payload, credentials or cookies cross the queue.
- Shared owns dedicated queue/job constants and deterministic job identity `(shopId, deliveryId)`; publishing/consuming services import from the *published* Shared package. Duplicate delivery may enqueue twice after Redis cleanup; Background must remain idempotent. The worker **never** authorises based on the event's claimed marketing value.
- Producer: `moda-interact`; consumer: `moda-interact-background`; runtime validation: Shared schema, version 1. Publication of Shared contract is independently gated (`SHARED-002`) before consumer adoption.
- Background-local injectable `WhatsAppRecoveryConsentReader.check({shopId,shopifyCustomerId,recipient}) -> allowed | not-authorised | verification-unavailable` owns Shopify read and canonicalisation, and is not automatically a cross-service Shared runtime contract.
- Merchant message deduplication identity: `arch045:consent-missing:<recoveryId>`; no second general-purpose messaging queue/contract is needed.

## Consistency and Transactions

- Shopify ingress durable acceptance point: **successful BullMQ acceptance** of validated event; ack promptly. No Shopify API read or recovery lookup in ingress.
- Initial block is a conditional update for `DETECTED` with no conflicting block reason; atomic/deduplicated merchant thread/message write uses existing PostgreSQL transaction. Failures must leave no path to a provider send; idempotent repair/retry brings missing notifications to convergence.
- Expiry/wakeup intent is idempotent and repairable. No Redis or Shopify network operation inside a PostgreSQL transaction. Use existing checkout lock, persisted statuses, unique attempt sequence, source keys and outbound idempotency. Credit reservation made before a late negative consent result must be released with existing pre-provider compensation semantics.
- Only a current verified subscribed state can lead to provider admission. A race where Shopify withdrawal follows the final successful check and occurs after an irreversible provider handoff cannot retroactively cancel a dispatched message; document and test the practical boundary rather than claiming impossible cross-provider atomicity.

## Ordering

- Shopify webhook delivery can be duplicated, delayed and out of order. Events are **hints to re-read live consent**, not ordered state updates.
- Preserve narrow `(shopId,checkoutToken)` locking and per-attempt idempotency. Do not serialise all shops or all consent updates. `EXPIRED`, `COMPLETED` and `CANCELLED` are terminal; a late event cannot change them back to `DETECTED`.
- The first valid send uses the existing sequence-one attempt. Schedule/human follow-up still share at most sequence two.

## Failure Handling

- Shopify 403/404, absent/offline token, GraphQL errors, timeout, customer identity ambiguity and mismatched default number: fail closed; distinguish `not-authorised` from retryable `verification-unavailable` for metrics/diagnostics.
- Queue enqueue fails before acceptance: return retryable webhook error instead of Shopify 2xx; duplicate delivery must not duplicate effects. Poison validation must have bounded failure evidence without leaking payloads.
- Merchant notice insertion/translation/display errors cannot trigger recovery or billing. Retry safely using deterministic `sourceKey`; no silently missing notices after recovery is blocked.
- Consent notification before resumption, revocation after block, customer order between event and resume, notification delayed, crash after scheduling, renewal after deadline and missing webhook must all be deterministic.

## Scalability

- Shopify reference ingress is ~20,000 *all webhook* events/minute, **not** 20,000 consent changes/minute. This design adds no Shopify GraphQL read for irrelevant incoming webhooks. The expensive consent read occurs only on actionable recovery admission, relevant proactive follow-ups and bounded blocked-recovery resume checks.
- Consent-update event processing first resolves the `(shopId,shopifyCustomerId)` link, then uses bounded indexed recovery results. Apply fixed per-job work limit, continuation and ordinary rate limits, avoiding per-shop global locks or Redis polling of every blocked recovery. Expiry repair queries only past-deadline blocks.

## Security

- Verify Shopify webhook HMAC/session first; reject or quarantine unknown/inactive shop. Constrain event IDs, customer ID format and Shopify GID construction. Use only Shopify-installed shop offline token; never cross tenant boundaries.
- Keep exact recipient matching; no consent inference from email/SMS consent, marketing cookies, tracking consent, another shop or another customer's phone number. `read_customers` is sufficient for read-only consent; **do not request `write_customers`**.
- Merchant inbox text, logs and traces must not expose full phone, provider token, customer payload or consent evidence. Use the shared structured logger and existing telemetry where available.

## Observability

- Emit bounded semantic outcomes such as `recovery.consent.checked`, `recovery.consent.blocked`, `recovery.consent.merchant_notice`, `recovery.consent.wakeup`, `recovery.consent.resumed`, `recovery.consent.expired`. Include `shopId`, `recoveryId`, `outcome`, `reasonCode`, `deliveryId` or correlation key; **no phone/email/full webhook**.
- Reuse `@modainteract/moda-interact-shared/logging` and existing BullMQ/HTTP OpenTelemetry; no redundant generic metrics. Provider outage and absent consent must be distinguishable operationally; logger failure must never change business outcome. No new Grafana/Gateway task unless current instrumentation proves insufficient.

## Rollout / Migration

- The 2026-10-20 ZIP is a **snapshot**, not proof of deployed production state. Implementation owner must verify whether affected shops/queues exist in production before choosing a breaking rollout; do not assume it from local worktree layout. Default safe order: Database migration -> Shared accepted implementation -> Shared publication -> Background reader/block/notice/resume/follow-up consumers -> Shopify webhook producer/config -> merchant UI guidance -> manual test -> terminal system test.
- Run migrations against disposable fresh PostgreSQL first. If live recoveries, old queues or rolling deployments exist, use backward-compatible consumer-first deployment and verify prior queue jobs; do not drain production queues merely for this initiative.
- Preserve existing recoveries and credit histories; no backfill of consent evidence inferred from phone numbers. Consent blocking applies when new admission/re-admission is evaluated under the new implementation.

## Decisions / Tasks

These statuses are **portable definition eligibility**, not claims that tasks have been materialised into canonical Git worktrees.

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-045-DATABASE-001 | moda_database | ready | — |
| ARCH-045-SHARED-001 | moda_shared | ready | — |
| ARCH-045-SHARED-002 | moda_shared | pending | SHARED-001 |
| ARCH-045-SHOPIFY-001 | moda_app | pending | SHARED-002 |
| ARCH-045-BACKGROUND-001 | moda_background | ready | — |
| ARCH-045-BACKGROUND-002 | moda_background | pending | DATABASE-001, BACKGROUND-001 |
| ARCH-045-BACKGROUND-003 | moda_background | pending | DATABASE-001, SHARED-002, SHOPIFY-001, BACKGROUND-002 |
| ARCH-045-BACKGROUND-004 | moda_background | pending | BACKGROUND-001, BACKGROUND-002 |
| ARCH-045-SHOPIFY-002 | moda_app | pending | BACKGROUND-002 |
| ARCH-045-SYSTEM-TEST-001 | moda_system_test | pending | DATABASE-001, SHARED-002, SHOPIFY-001/002, BACKGROUND-001/002/003/004 |

No **non-system-test** task depends on SYSTEM-TEST-001. When all implementation and publication tasks are architect-accepted Complete, the developer may manually verify the implementation before invoking SYSTEM-TEST-001.

## Open Questions / Explicit defaults

- **Provisional product policy for the requested task creation:** 72-hour consent wait measured from `detectedAt`. This is a concrete implementable v1 default, **not** an externally mandated Shopify value. Amend this architecture/task contract before implementing if the merchant wants another duration. This default does **not** change the existing recipient-suppression duration.
- An automatic wakeup requires an unambiguous Shopify customer ID linked to the existing recovery. Guest/phone-only recoveries remain blocked until a verified identity appears through an approved existing checkout event or until expiry. Do not add speculative phone-based matching.
- Shopify provider API/permissions must be checked in the target live app during implementation; snapshot config ambiguity is recorded above.

## External provider references (verified 2026-10-20)

These references are **external Shopify documentation**, not claims that the supplied snapshot already implements the feature:

- Shopify Admin GraphQL 2026-07 [`CustomerPhoneNumber`](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/CustomerPhoneNumber) — `phoneNumber` and `whatsAppMarketingConsent` read access (`read_customers`).
- Shopify [WhatsApp marketing consent launch](https://shopify.dev/changelog/posts/whatsapp-marketing-consent-now-available) — available starting Admin API 2026-07.
- Shopify [2026-07 webhook reference](https://shopify.dev/docs/api/webhooks/2026-07) — `customers_whats_app_marketing_consent/update`, sample payload and customer ID.
- Shopify [app-specific webhook subscription configuration](https://shopify.dev/docs/apps/build/webhooks/subscribe) — recommend config-managed topic and active config verification.

## Change History

- 2026-10-20: Initial portable task definitions for absence-of-consent merchant notification and later-consent automatic recovery. Narrowed consent to WhatsApp channel-specific opt-in; explicitly separated storefront tracking/CMP concerns and fixed an initial 72-hour deadline for deterministic tasks.
