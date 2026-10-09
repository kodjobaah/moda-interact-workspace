---
id: ARCH-028
title: WhatsApp delivery-failure convergence and merchant credit protection
status: agreed
coordinator: moda_architect
created: 2026-10-03
updated: 2026-10-09
---

# ARCH-028: WhatsApp delivery-failure convergence and merchant credit protection

## Status

Agreed.

ARCH-028 has a revised pre-production task decomposition. The architecture separates provider message lifecycle, recovery-attempt response lifecycle, recovery usage compensation, recipient reachability and independent checkout-update re-entry. A Meta delivery-status failure is associated with its Shop/recovery through durable provider-message and outreach-attempt relations; Shop ownership is never inferred from a customer phone number.

The implementation frontier includes architect-accepted `ARCH-028-DATABASE-001`, `ARCH-028-DATABASE-003`, and `ARCH-028-BACKGROUND-007` alongside the accepted `ARCH-028-SHARED-001` contract, completed `ARCH-028-SHARED-002` publication of `@modainteract/moda-interact-shared@1.3.1`, and Ready `ARCH-028-SHARED-003` and `ARCH-028-BACKGROUND-005` tasks. DATABASE-001 consolidates the former DATABASE-002 additive compensation provenance; accepted DATABASE-003 is the strict attempt-recipient gate and may be adopted only together with the compatible BACKGROUND-005 attempt writers. Missing-recipient safety no longer waits for billing compensation. The v3 Shared contract is published before consumer-first Background adoption and later Messaging production. Terminal-recipient policy then converges recovery state, performs idempotent compensation from the provider-status job, removes undelivered outbound-message hard-limit usage, updates finite Shop-scoped recipient suppression, and emits a merchant SYSTEM message only after financial correction succeeds.

ARCH-028 is a pre-production initiative. Backwards compatibility with legacy database rows is not required; DATABASE tasks may use strict new invariants and fresh-database migration validation. Queue-version compatibility remains required for staged v2 -> v3 provider-status and Shopify checkout-update rollouts because old strict queue consumers and queued events can coexist with new producers.

## Problem

Moda can accept an outbound WhatsApp recovery at the Meta API and commit recovery capacity before Meta later reports that the message could not be delivered to the recipient. The current provider-status path can therefore leave durable state inconsistent:

```text
ConversationMessage = FAILED
RecoveryOutreachAttempt = WAITING_FOR_RESPONSE or NO_RESPONSE
CheckoutRecovery = MESSAGE_SENT
recovery capacity = committed
outbound hard-limit usage = consumed
follow-up = potentially actionable
merchant = not informed
```

The current normalized provider-status contract also drops Meta failure codes, so Background cannot distinguish the bounded terminal-recipient condition ARCH-028 needs from other provider failures.

A syntactically valid telephone number may also be temporarily unreachable on WhatsApp. Moda must avoid repeatedly attempting new recoveries for the same Shop/recipient during a finite suppression window, without asserting that a person permanently lacks WhatsApp. The same phone number may occur under multiple Shops and those tenant identities must remain completely independent.

## Goals

- Distinguish provider acceptance, provider delivery and customer response as separate lifecycle facts.
- Preserve bounded provider failure evidence for outbound WhatsApp messages.
- Resolve an asynchronous delivery failure through durable `providerMessageId -> ConversationMessage -> RecoveryOutreachAttempt -> CheckoutRecovery -> Shop` state rather than through phone-number ownership lookup.
- Persist the exact canonical recipient used by each recovery outreach attempt.
- Maintain Shop-scoped `(shopId, recipient)` reachability evidence with finite suppression.
- Make suppression a pre-admission recovery gate so a known-suppressed recipient consumes neither recovery capacity nor a provider send.
- Default terminal-recipient suppression to seven days and allow SUPER_ADMIN configuration through the existing Platform Billing Policy UI.
- Converge terminal recipient failures without making compensation depend on the mutable `RecoveryOutreachAttempt.status` response lifecycle.
- Ensure a definitively undelivered recovery does not ultimately consume recovery capacity.
- Ensure a terminally undelivered automated WhatsApp message does not consume the outbound automated-message hard limit.
- Invoke compensation idempotently from the provider-status job after durable status convergence and make job retries replay compensation safely.
- Apply the same terminal-recipient policy to synchronous Meta rejection and asynchronous FAILED status evidence.
- Treat missing phone/recipient as a pre-materialisation condition: do not create `CheckoutRecovery`, bill, or call Meta until a usable Shop-scoped current `CustomerPhone` exists. Pass the exact validated phone to the initial send.
- Split generic recovery compensation from committed purchased-credit compensation so the generic path is not gated by ARCH-027 refund completion.
- Emit a deduplicated merchant SYSTEM message only after release/compensation has durably succeeded.
- Preserve duplicate/out-of-order provider-status safety.
- Allow token-identified checkout updates to re-enter pending recovery after no-recipient deferral, without treating `abandonedCheckoutUrl` as an identity key.

## Non-Goals

- Pre-send WhatsApp-account discovery/existence probing.
- A permanent `Customer.hasWhatsApp` or global phone blacklist.
- Inferring Shop ownership solely from a phone number.
- Redesigning general Shopify/WooCommerce billing or plan economics.
- Introducing a second billing-refund model or provider monetary refund path.
- Retrying every provider error identically.
- Generalizing Meta provider-code policy beyond the explicitly accepted terminal-recipient code without later architecture review.
- Changing unrelated inbound-conversation behaviour except where positive reachability evidence can be cleared after Shop/conversation resolution.
- Replacing the existing bounded Shopify abandoned-checkout lookup or claiming the GraphQL query can search directly by checkout token without verification.
- Introducing a new recovery status solely for late delivery failure; `CheckoutRecovery.MESSAGE_SENT` may remain historical evidence that the provider accepted an outbound recovery. Message/attempt/compensation state is the delivery authority.

## Current Architecture

`moda-interact-background` currently creates the recovery during initiation before all missing-recipient cases have been ruled out; this can leave a recovery record before a missing phone aborts the send path. It creates a `RecoveryOutreachAttempt`, reserves recovery capacity, admits an outbound automated message, calls Meta, then commits recovery usage after a confirmed provider message ID. Follow-up processing later moves the initial attempt from `WAITING_FOR_RESPONSE` to `NO_RESPONSE` before creating the follow-up attempt.

`moda-interact-messaging` receives Meta status webhooks and publishes the Shared normalized status event. `moda-interact-background/src/services/whatsapp-provider-status.service.ts` currently uses a numeric rank:

```text
PENDING=0, FAILED=1, SENT=2, DELIVERED=3, READ=4
```

which means a late `SENT` can incorrectly advance a terminal `FAILED` message back to `SENT`.

Outbound admission creates one `OUTBOUND_AUTOMATED_MESSAGE` UsageEvent before the provider call. Synchronous definitive provider failure currently deletes that usage through `failPrepared`, but an asynchronous terminal failure does not. ARCH-028 makes those semantics consistent.

`RecoveryOutreachAttempt.outboundMessageId` already provides the exact recovery-attempt association for an outbound message. `CheckoutRecovery.shopId` provides tenant identity. A phone number is therefore not needed to determine which Shop/recovery a Meta delivery failure belongs to. For checkout events, `(shopId, checkoutToken)` is the canonical business/candidate identity; the current Shopify abandoned-checkout GraphQL lookup separately uses a bounded created-at window and URL match for retrieval.

## Proposed Architecture

### 1. Provider-status lifecycle and explicit status lattice

The provider-status consumer uses explicit transitions rather than a numeric total rank:

```text
PENDING -> SENT | DELIVERED | READ | FAILED
SENT    -> DELIVERED | READ | FAILED
FAILED  -> DELIVERED | READ
DELIVERED -> READ
READ    -> terminal success
```

A late `SENT` never resurrects `FAILED`. `DELIVERED` or `READ` is stronger positive delivery evidence and may advance an earlier `FAILED`. Historical `providerFailureCode`/`failedAt` may remain for audit when later positive evidence wins.

### 2. Terminal-recipient association and compensation authority

For provider code `131026`:

```text
providerMessageId
    -> ConversationMessage
    -> RecoveryOutreachAttempt (when linked)
    -> CheckoutRecovery
    -> Shop
    -> UsageReservation sourceKey/outreach-attempt identity
```

Compensation eligibility is determined from the durable failed message plus exact recovery/reservation lineage. It does **not** require `RecoveryOutreachAttempt.status = FAILED`; the attempt may already be `NO_RESPONSE` when delayed provider evidence arrives.

BACKGROUND-002 may still move an eligible `WAITING_FOR_RESPONSE` attempt to `FAILED` and suppress due follow-up work, but a non-waiting attempt cannot prevent financial correction.

### 3. Provider-status job post-transaction convergence

The queue-facing provider-status job performs:

```text
apply/reconcile provider status transaction
    -> classify terminal recipient evidence
    -> idempotent compensation/release call
    -> correct outbound automated-message hard-limit usage
    -> update Shop-scoped reachability suppression
    -> emit deduplicated merchant SYSTEM notification
```

The compensation call is executed on every relevant provider-status replay, including when the message was already durably `FAILED`. If compensation/reachability/notification fails after message convergence, the job fails and retries; prior stages are idempotent.

### 4. Recovery recipient and reachability

Each `RecoveryOutreachAttempt` stores the exact canonical digits-only recipient selected for that attempt before recovery billing admission/provider send.

Reachability is stored independently as:

```text
WhatsAppRecipientReachability(shopId, recipient)
```

The same number in two Shops has independent state. Provider delivery status never performs phone-to-Shop resolution.

Before recovery billing admission:

```text
resolve current recipient
    -> canonicalize
    -> check (shopId, recipient) reachability
    -> active suppression?
         yes: zero billing, zero provider call, block candidate until suppression expiry
         no:  persist attempt recipient and continue normal admission
```

A later different customer phone is a different recipient key and is independently eligible.

### 5. Suppression policy

`PlatformBillingPolicy.whatsappRecipientSuppressionDays` is a positive integer with default `7`. The existing SUPER_ADMIN Platform Billing Policy UI owns configuration and audit/version semantics.

Terminal `131026` evidence sets:

```text
suppressUntil = failureTime + configured days
```

Expired suppression no longer blocks proactive sending. `DELIVERED`, `READ`, or a successfully routed inbound message for the same Shop/recipient clears active suppression earlier. A contextless inbound message that cannot establish one Shop must not clear multiple Shop rows.

### 6. Synchronous terminal rejection

`WhatsAppServiceError` retains a bounded optional `providerCode`. A synchronous Meta rejection carrying `131026` follows the same policy as asynchronous terminal delivery failure:

- durable message failure evidence;
- recovery reservation release/compensation as applicable;
- outbound hard-limit correction;
- Shop-scoped suppression;
- merchant notification after correction.

Raw provider error text/body is not persisted.

### 7. Missing recipient

Missing customer phone is a pre-materialisation outcome, not a blocked `CheckoutRecovery`. The fresh abandoned-checkout snapshot is first resolved to the Shop-scoped Customer; any supplied phone is written through the existing `CustomerPhone` history service, and the current `CustomerPhone` is then the authoritative recovery recipient source. `Customer.phone` is not authoritative for ARCH-028 recipient resolution.

```text
PendingRecoveryCandidate
    -> fresh abandoned-checkout lookup
    -> resolve/update Shop-scoped Customer + CustomerPhone
    -> no active usable CustomerPhone
         -> no CheckoutRecovery
         -> no RecoveryOutreachAttempt
         -> no recovery billing admission
         -> no outbound message admission
         -> no Meta call
```

The matured BullMQ candidate may complete and be removed normally. `ARCH-028-BACKGROUND-007` implements only the early no-recipient decision and exact initial-send recipient handoff; it does not wait for reachability compensation or invent an update event.

A separate checkout-update re-entry path handles a later `CHECKOUTS_UPDATE` when no pending candidate and no `CheckoutRecovery` exists:

```text
verified Shopify checkout.updated (v3; v2 retained during rollout)
    -> (shopId, checkoutToken) identity / deterministic queue key
    -> existing candidate/recovery? refresh existing behaviour
    -> neither exists? idempotently schedule a fresh candidate by token
    -> optional bounded Shopify lookup context supplied when available
    -> at maturity: fresh abandoned-checkout lookup
    -> current CustomerPhone prerequisite -> normal materialisation if eligible
```

`abandonedCheckoutUrl` and `checkoutCreatedAt` are **lookup hints**, never alternative identity or queue keys. The current `AbandonedCheckoutLookupService` still needs them to find the exact abandoned checkout from a bounded `created_at` query; the GraphQL `AbandonedCheckout` response does not expose a checkout-token field. A token-only event is valid for correlation and can be enqueued, but if the hints remain unavailable at maturity, processing must finish with an explicit non-billable lookup-unavailable outcome, not invent URL/time values or create a recovery. The Shopify producer must preserve context when actually supplied by the verified webhook. There is no aggressive polling solely for a missing number and no durable `NO_WHATSAPP_RECIPIENT` recovery block state.

### 8. Generic versus purchased compensation

Generic compensation owns:

- release of any still-`RESERVED` source;
- committed lifetime-Free correction;
- committed paid-included correction;
- committed promotional correction.

A committed purchased-credit source is deferred to `ARCH-028-BACKGROUND-009`, which depends on final `ARCH-027-BACKGROUND-005` purchase/refund semantics. This prevents ARCH-027 refund work from blocking generic ARCH-028 compensation.

### 9. Merchant notification ordering

Merchant notification is last:

```text
terminal failure
    -> durable status convergence
    -> durable release/compensation
    -> outbound hard-limit correction
    -> reachability suppression
    -> merchant SYSTEM message
```

A message must never claim that recovery capacity was restored before correction succeeded. Notification is deduplicated by deterministic `MerchantSupportMessage.sourceKey` and must describe the actual compensation disposition rather than claiming spendable credit when the result is historical-only/held.

## Request / Event Flow

### Asynchronous terminal failure

```text
Meta FAILED / 131026
    -> Messaging v3 status
    -> Background explicit status lattice
    -> identify exact message/attempt/recovery/shop
    -> attempt convergence where safe
    -> idempotent compensation/release
    -> remove exact OUTBOUND_AUTOMATED_MESSAGE hard-limit usage
    -> suppress (shopId, attempt.recipient) for policy duration
    -> deduplicated merchant SYSTEM message
```

### Synchronous terminal rejection

```text
Background provider call
    -> Meta HTTP rejects / providerCode 131026
    -> message FAILED + bounded evidence
    -> exact reservation release/compensation
    -> remove outbound hard-limit usage
    -> suppress (shopId, attempt.recipient)
    -> merchant SYSTEM message
```

### Pre-admission suppression

```text
recovery candidate
    -> resolve/canonicalize recipient
    -> active reachability suppression?
       yes -> no billing/no provider call; block until suppressUntil
       no  -> persist attempt recipient; continue admission
```

### Positive evidence

```text
DELIVERED/READ provider status
or successfully Shop-routed inbound WhatsApp message
    -> identify Shop + canonical recipient
    -> record lastSuccessfulAt
    -> clear active suppressUntil
```

## Repository Responsibilities

### `moda-interact-database` / `moda_database`

DATABASE-001 owns one strict pre-production migration for message failure evidence, reachability, suppression policy, admission-block reasons **and committed-reservation compensation lineage/disposition** (former DATABASE-002 is superseded). It is based on the accepted `ARCH-027-DATABASE-001` canonical Woo billing migration, rather than a stale Background nested database revision. DATABASE-003 separately adds required `RecoveryOutreachAttempt.recipient` so Background adopts that breaking create-contract only when BACKGROUND-005 is ready to populate it.

### `moda-interact-shared` / `moda_shared`

SHARED-001/002 own the WhatsApp provider-status v2/v3 contract and its publication gate. SHARED-003/004 later own the separate strictly versioned Shopify `checkout.updated` event and its publication; the existing strict v2 event remains unchanged. Consumer-first deployment applies to both.

### `moda-interact-messaging` / `moda_messaging`

MESSAGING-001 emits v3 from verified Meta status webhooks and bounded provider codes. It does not decide billing/recovery/reachability policy.

### `moda-interact-background` / `moda_background`

BACKGROUND-001/002 own provider-status adoption and terminal classification. BACKGROUND-004 owns generic compensation, replay and hard-limit correction. BACKGROUND-007 independently guards missing recipients before recovery materialisation and passes the validated recipient to initial sends. BACKGROUND-005 then adopts strict per-attempt recipient snapshots (initial and follow-up). BACKGROUND-010 owns zero-billing suppression reads/admission/expiry resume; BACKGROUND-011 owns post-correction reachability writes and positive-evidence clearing. BACKGROUND-012 consumes compatible checkout updates and re-enters token-identified candidates. BACKGROUND-006 owns synchronous rejection parity, BACKGROUND-008 owns merchant notification and BACKGROUND-009 owns committed purchased-credit compensation after ARCH-027 refund support. BACKGROUND-003 remains superseded.

### `moda-interact-admin` / `moda_admin`

ADMIN-001 exposes the platform suppression duration through the existing SUPER_ADMIN Platform Billing Policy controls, using existing policy audit/version semantics.

### `moda-interact-system-test` / `moda_system_test`

SYSTEM-TEST-001 validates the integrated async/sync failure, compensation, hard-limit, reachability, tenant-isolation, missing-recipient and notification behaviour only after every implementation dependency is Complete.

### `moda-interact` / `moda_app`

SHOPIFY-001 emits the separately versioned checkout.updated payload, preserving `checkoutToken` identity and optional lookup context only after the new Background consumer is accepted. The Shopify ingress hot path remains receive/validate/durably enqueue/acknowledge.

### Gateway / WooCommerce

No ARCH-028 Gateway or WooCommerce implementation task is required. No new deployment topology is introduced.

## Data Model

### DATABASE-001

Logical additions:

```prisma
model ConversationMessage {
  providerFailureCode String? @db.VarChar(64)
  failedAt            DateTime?
}

enum RecoveryAdmissionBlockReason {
  RECOVERY_CAPACITY_EXHAUSTED
  WHATSAPP_RECIPIENT_SUPPRESSED
}

model WhatsAppRecipientReachability {
  id String @id @default(cuid())
  shopId String
  recipient String @db.VarChar(64)
  lastProviderFailureCode String? @db.VarChar(64)
  lastFailureAt DateTime?
  suppressUntil DateTime?
  lastSuccessfulAt DateTime?
  version Int @default(0)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  @@unique([shopId, recipient])
  @@index([shopId, suppressUntil])
  @@schema("whatsapp")
}

model PlatformBillingPolicy {
  whatsappRecipientSuppressionDays Int @default(7)
}
```

Canonical reachability recipient representation is digits only, non-empty and bounded to 64 characters. Application code performs canonicalization before reachability persistence.

### DATABASE-003

Add strict per-attempt destination snapshot:

```prisma
model RecoveryOutreachAttempt {
  recipient String @db.VarChar(64)
}
```

This task is separate from DATABASE-001 because the required field changes the Background creation contract. BACKGROUND-005 adopts DATABASE-003 while updating every initial/follow-up attempt creation path to supply the canonical recipient. No nullable/backfill compatibility is introduced.

### Committed compensation provenance (DATABASE-001; DATABASE-002 superseded)

Committed compensation remains linked to the original `UsageReservation`/positive UsageEvent through exactly one negative correction and a durable disposition:

```text
RESTORED_SPENDABLE
HELD_FOR_REFUND
HISTORICAL_ONLY
```

A still-RESERVED reservation is released and does not manufacture a compensation UsageEvent. DATABASE-001 also adds the all-or-nothing `UsageReservation.compensationUsageEventId`, `compensationReason`, `compensationDisposition`, `compensatedAt` fields, reason/disposition enums and same-Shop exact-negative correction integrity.

## Contracts

The WhatsApp cross-repository runtime contract remains the normalized provider-status event owned by `@modainteract/moda-interact-shared/billing`.

```text
v2: existing provider status fields
v3: existing fields + optional failure.providerCode (FAILED only)
```

The safe order is:

```text
SHARED-001 accepted
  -> SHARED-002 published
  -> BACKGROUND-001 installs dual-version consumer
  -> MESSAGING-001 begins v3 production
```

Provider-code classification is Background policy, not Shared schema policy.

The **separate Shopify checkout-update contract** is owned by `@modainteract/moda-interact-shared/shopify`:

```text
Existing v2 checkout.updated: strict `{ checkoutToken }` (unchanged)
New v3 checkout.updated:  strict `{ checkoutToken, cartToken?,
                                checkoutCreatedAt?, abandonedCheckoutUrl? }`
Canonical parser:        accepts existing v2 recovery events OR v3 checkout.updated
Business identity:       tenant.shopId + payload.checkoutToken
Lookup context:          optional nullable, bounded, never an identity substitute
```

The Shared implementation and publication gates are SHARED-003 and SHARED-004. Background-012 installs the accepted exact Shared version and dual-version parser **before** Shopify-001 starts producing v3. Existing Shopify event variants keep their v2 contract; an old strict v2 parser must never be fed an unversioned v3 payload. Legacy queued v2 events with no lookup hints remain safely consumable.

## Consistency and Transactions

- Status application remains Serializable/CAS protected.
- `FAILED` + terminal provider evidence may be durable before compensation; provider-status job retry must replay compensation even when status convergence is already a no-op.
- Compensation does not require attempt status `FAILED`.
- A reservation still RESERVED is released; committed generic sources receive exact negative correction; committed purchased source is delegated to BACKGROUND-009. Every negative correction copies the original committed recovery UsageEvent's exact Shop/provider (`SHOPIFY` or `WOOCOMMERCE`), never Prisma's provider default; corrections are non-reportable to Shopify, including when correcting a previously reportable Shopify usage event.
- The exact `OUTBOUND_AUTOMATED_MESSAGE` UsageEvent for a terminally undelivered message is removed/corrected idempotently so the hard limit is not consumed.
- Reachability write occurs only after successful release/compensation for the terminal failure being processed.
- Merchant notification occurs only after financial correction and reachability update succeed.
- Duplicate provider-status events cannot duplicate compensation, suppression, hard-limit correction or merchant messages.

## Ordering

Provider statuses may be duplicate, delayed or out of order. Explicit status transitions are authoritative; there is no total numeric rank that lets `SENT` supersede `FAILED`.

`RecoveryOutreachAttempt.status` represents outreach/response lifecycle and may already be `NO_RESPONSE`; it is not provider-delivery authority. `ConversationMessage` status/failure evidence is the provider-delivery authority.

Ordering/serialization remains narrow to the message/attempt/recovery; the Shop is not globally serialized. For checkout-update re-entry, the refactored candidate activity service may return `not-reschedulable` while a candidate is active, followed by worker index cleanup and BullMQ `removeOnComplete`. BACKGROUND-012 must test and prevent loss of a qualifying newer update across that boundary while preserving checkout-scoped order/recovery idempotency.

## Failure Handling

- Invalid provider-status payloads remain rejected by Shared runtime validation.
- Unknown provider message IDs never create recovery/reachability state.
- Non-`131026` provider failures remain unclassified by ARCH-028 terminal-recipient policy.
- Compensation failure fails the provider-status job and is retried idempotently.
- Purchased committed compensation may return a bounded deferred result until BACKGROUND-009 is available; no suppression/notification claims correction before it succeeds.
- Reachability write/merchant notification failure after compensation may retry safely.
- Positive delivery after completed compensation does not claw compensation back; it may clear suppression.
- Observability failures remain isolated from business correctness.

## Scalability

ARCH-028 delivery convergence runs on outbound WhatsApp/recovery workload, not raw Shopify event volume. The new checkout-update re-entry branch runs on Shopify checkout update events and must preserve the minimal ingress path; only no-candidate/no-recovery cases enqueue another pending candidate. Pre-admission reachability is one indexed `(shopId, recipient)` lookup. Provider-status convergence remains horizontally safe under duplicate/concurrent delivery.

No new queue infrastructure/service deployment is required. Existing Background worker/queue mechanisms may be extended for bounded suppression-expiry resume and token-keyed candidate work where required.

## Security

- Phone numbers are not global customer identifiers.
- Reachability is always Shop scoped.
- Provider delivery status resolves Shop through durable message/conversation/recovery ownership, never through phone lookup.
- Do not persist raw Meta error payloads or provider text.
- Merchant SYSTEM wording is platform-owned and tenant scoped.

## Observability

Use the existing Shared structured logger. New semantic logs may include bounded IDs/outcomes such as message ID, attempt ID, recovery ID, provider code, compensation disposition and suppression outcome. Do not log full phone numbers, message content or raw provider payloads.

No new telemetry transport/Gateway task is required.

## Rollout / Migration

Classification: **PRE-PRODUCTION / BREAKING ROLLOUT** for database/application state, with **compatible staged rollout** for the queue contract.

There is no production ARCH-028 state to preserve. Accepted `ARCH-027-DATABASE-001` precedes ARCH-028-DATABASE-001 in the canonical database migration chain; Background consumers must adopt the integrated database revision before relying on the new Woo fields. DATABASE-001 (including superseded DATABASE-002 provenance scope) and DATABASE-003 may enforce strict new invariants without legacy row backfill or upgrade compatibility. Fresh-database migration/rehearsal is the required correctness target. DATABASE-003 mandatory attempt-recipient revision must not be deployed ahead of BACKGROUND-005's compatible attempt writers. Development databases may be reset as needed.

The v2/v3 provider-status queue and checkout-update queue both require consumer-first deployment because retained/rolling events may exist during development/integration:

```text
ARCH-027-DATABASE-001 (accepted canonical migration)
    -> DATABASE-001 (includes former DATABASE-002 provenance)
    -> BACKGROUND-004 (also needs BACKGROUND-002 + ARCH-027-BACKGROUND-001)
    -> BACKGROUND-011 (also needs BACKGROUND-010)
DATABASE-001 -> DATABASE-003 -> BACKGROUND-005
DATABASE-001 -> ADMIN-001
SHARED-001 -> SHARED-002 -> BACKGROUND-001 -> MESSAGING-001 -> BACKGROUND-002
SHARED-002 -> SHARED-003 -> SHARED-004 -> BACKGROUND-012 -> SHOPIFY-001
BACKGROUND-007 (architect-accepted Complete) -> BACKGROUND-005 and BACKGROUND-012 (each retains its other prerequisite)
BACKGROUND-005 -> BACKGROUND-010 -> BACKGROUND-011 -> BACKGROUND-006 -> BACKGROUND-008
BACKGROUND-004 + BACKGROUND-008 + ARCH-027-BACKGROUND-005 -> BACKGROUND-009
ADMIN-001 + BACKGROUND-007 + BACKGROUND-009 + SHOPIFY-001 -> SYSTEM-TEST-001
```

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-028-DATABASE-001 | moda_database | Complete | ARCH-027-DATABASE-001 (Complete) |
| ARCH-028-DATABASE-002 | moda_database | Superseded | - (scope consolidated into DATABASE-001) |
| ARCH-028-DATABASE-003 | moda_database | Complete | ARCH-028-DATABASE-001 |
| ARCH-028-SHARED-001 | moda_shared | Complete | - |
| ARCH-028-SHARED-002 | moda_shared | Complete | ARCH-028-SHARED-001 |
| ARCH-028-SHARED-003 | moda_shared | Ready | ARCH-028-SHARED-002 |
| ARCH-028-SHARED-004 | moda_shared | Pending | ARCH-028-SHARED-003 |
| ARCH-028-ADMIN-001 | moda_admin | Ready | ARCH-028-DATABASE-001 |
| ARCH-028-BACKGROUND-001 | moda_background | Pending | ARCH-028-DATABASE-001, ARCH-028-SHARED-002 |
| ARCH-028-MESSAGING-001 | moda_messaging | Pending | ARCH-028-SHARED-002, ARCH-028-BACKGROUND-001 |
| ARCH-028-BACKGROUND-002 | moda_background | Pending | ARCH-028-BACKGROUND-001, ARCH-028-MESSAGING-001 |
| ARCH-028-BACKGROUND-003 | moda_background | Superseded | - |
| ARCH-028-BACKGROUND-004 | moda_background | Pending | ARCH-028-BACKGROUND-002, ARCH-028-DATABASE-001, ARCH-027-BACKGROUND-001 |
| ARCH-028-BACKGROUND-007 | moda_background | Complete | - |
| ARCH-028-BACKGROUND-005 | moda_background | Ready | ARCH-028-DATABASE-003, ARCH-028-BACKGROUND-007 |
| ARCH-028-BACKGROUND-010 | moda_background | Pending | ARCH-028-DATABASE-001, ARCH-028-BACKGROUND-005 |
| ARCH-028-BACKGROUND-011 | moda_background | Pending | ARCH-028-BACKGROUND-004, ARCH-028-BACKGROUND-010 |
| ARCH-028-BACKGROUND-006 | moda_background | Pending | ARCH-028-BACKGROUND-011 |
| ARCH-028-BACKGROUND-008 | moda_background | Pending | ARCH-028-BACKGROUND-006 |
| ARCH-028-BACKGROUND-009 | moda_background | Pending | ARCH-028-BACKGROUND-004, ARCH-028-BACKGROUND-008, ARCH-027-BACKGROUND-005 |
| ARCH-028-BACKGROUND-012 | moda_background | Pending | ARCH-028-BACKGROUND-007, ARCH-028-SHARED-004 |
| ARCH-028-SHOPIFY-001 | moda_app | Pending | ARCH-028-SHARED-004, ARCH-028-BACKGROUND-012 |
| ARCH-028-SYSTEM-TEST-001 | moda_system_test | Pending | ARCH-028-ADMIN-001, ARCH-028-BACKGROUND-007, ARCH-028-BACKGROUND-009, ARCH-028-SHOPIFY-001 |

DATABASE-001, DATABASE-003 and BACKGROUND-007 are architect-accepted Complete; DATABASE-001 has a satisfied cross-architecture dependency on accepted ARCH-027-DATABASE-001. BACKGROUND-005 is Ready because both of its prerequisites have completed; it must adopt DATABASE-003 and its required recipient field together with every compatible Background attempt writer, not deploy the migration ahead of the writers. SHARED-001 and its publication gate SHARED-002 are architect-accepted Complete; the exact published status-contract package is `@modainteract/moda-interact-shared@1.3.1`, promoting SHARED-003 to Ready. BACKGROUND-001 remains Pending until DATABASE-001 is Complete; MESSAGING-001 remains Pending until BACKGROUND-001 is Complete. DATABASE-001 combines two additive persistence contracts and does **not** collapse the later mandatory-recipient schema gate. SHARED-002/004 are separate publication gates after accepted implementation tasks; SHOPIFY-001 must follow consumer-first BACKGROUND-012 acceptance.

Suppression reads (BACKGROUND-010) can be validated independently using seeded reachability rows; suppression writes/positive clearing (BACKGROUND-011) depend on successful compensation. Purchased committed compensation remains isolated in BACKGROUND-009 so ARCH-027 refund work does not block generic correction or missing-recipient protection. No implementation task depends on SYSTEM-TEST-001.

## Open Questions

Provider codes beyond exact `131026` remain outside ARCH-028 terminal-recipient policy until separately reviewed.

**Lookup-context coverage remains an integration-verification condition:** checkoutToken and Shop are sufficient for Moda candidate identity, but the current Shopify abandoned-checkout GraphQL retrieval requires URL and creation-time hints. Some checkout.updated payloads may lack these fields. SHARED-003/004 and SHOPIFY-001 carry them when present; BACKGROUND-012 must safely defer materialisation when missing rather than inventing them. System tests must demonstrate a usable context-bearing re-entry and safe token-only behaviour. A token-only *provider retrieval* guarantee is not asserted without a supported API.

## Change History

- 2026-10-09: Architect accepted `ARCH-028-DATABASE-003` Attempt 1. Required `RecoveryOutreachAttempt.recipient VARCHAR(64)` with a PostgreSQL digits-only/non-empty constraint has no default, backfill or nullable accommodation; fresh migration tests include boundary and rejection cases. Both ARCH-028 database validators passed independently; full disposable PostgreSQL rehearsal and Prisma/ERD checks are documented in the Completion Report. BACKGROUND-005 is now Ready, with a required coordinated adoption/deployment boundary for the strict database revision. No `_index.md` reconciliation was performed.
- 2026-10-09: Architect accepted `ARCH-028-BACKGROUND-007` Attempt 2 (recipient prerequisite and disposable PostgreSQL test-routing correction). `npm test` with stale `TEST_DATABASE_URL` passed; four real translation-enum tests passed through disposable PostgreSQL. Unrelated integration/voice/observability failures remain explicitly documented without being classified as resolved. BACKGROUND-005 and BACKGROUND-012 remain Pending behind DATABASE-003 and SHARED-004 respectively; no `_index.md` reconciliation is performed.
- 2026-10-03: ARCH-028 agreed. Defined DATABASE-001 as the first iterative task and separated durable failure/reachability evidence from later billing compensation.
- 2026-10-03: Recipient unreachability defined as temporary evidence rather than permanent identity; v3 Shared failure evidence and consumer-first publication/adoption sequence defined.
- 2026-10-04: Initial purchased compensation provenance task defined.
- 2026-10-05: Reconciled with ARCH-027 provider-owned refund flow; BACKGROUND-003 superseded, DATABASE-002 reduced to generic compensation lineage, and BACKGROUND-004 became compensation owner.
- 2026-10-07: Deep architectural reconciliation completed. Shop/recovery association is resolved from provider message/recovery lineage rather than phone lookup; each outreach attempt snapshots its canonical recipient; explicit message-status lattice prevents FAILED -> SENT resurrection; compensation no longer depends on attempt status; provider-status jobs replay idempotent compensation; terminally undelivered outbound hard-limit usage is removed; Shop-scoped pre-admission suppression is configurable in Admin with a seven-day default; synchronous `131026` follows async policy; missing phone is zero-billing; committed purchased compensation is split to BACKGROUND-009; merchant SYSTEM notification is last and deduplicated; DATABASE rollout is explicitly pre-production/breaking.
- 2026-10-08: Missing-recipient handling was moved before `CheckoutRecovery` materialisation. A matured candidate with no active usable Shop-scoped `CustomerPhone` creates no recovery/attempt/billing/provider work. A later `CHECKOUTS_UPDATE` may schedule a fresh candidate when no recovery exists. `NO_WHATSAPP_RECIPIENT` was removed from durable recovery admission-block state, and `Customer.phone` is not an authoritative recovery-recipient source.
- 2026-10-08: Revised task decomposition: consolidated additive DATABASE-002 into DATABASE-001 (DATABASE-002 superseded), retained DATABASE-003 required-recipient gate; made BACKGROUND-007 independently Ready for early no-recipient safety; narrowed BACKGROUND-005 to immutable attempt-recipient snapshots; separated suppression admission (BACKGROUND-010) from corrected-failure/positive reachability writes (BACKGROUND-011); isolated checkout-update re-entry (BACKGROUND-012) behind compatible separate Shared checkout-update contract/publication (SHARED-003/004) and consumer-first Shopify producer (SHOPIFY-001). Canonical checkout identity is `(shopId, checkoutToken)`; optional URL/time fields are current Shopify lookup hints, never identity.

- 2026-10-08: Pre-task rebaseline after Background candidate/reservation refactoring: ARCH-028-DATABASE-001 now formally depends on accepted ARCH-027-DATABASE-001 as its migration baseline; BACKGROUND-004/009 preserve exact original Shop/provider on non-reportable negative UsageEvents; BACKGROUND-005 tests current `CustomerPhone` even when legacy `Customer.phone` is missing/stale; BACKGROUND-012 must prove checkout-update re-entry survives active-candidate completion/index cleanup without duplicate recovery or polling. No new task IDs or index changes.
- 2026-10-08: Architect accepted `ARCH-028-SHARED-001` Attempt 1. The exact v2 status schema remains strict, while the dual-version canonical Shared parser accepts bounded v3 `FAILED.failure.providerCode` evidence without coercion or policy classification. `ARCH-028-SHARED-002` is now Ready as a publication-only gate; Background, Messaging and downstream system tests remain dependent on the approved consumer-first sequence.

- 2026-10-08: Architect accepted `ARCH-028-SHARED-002` Attempt 3: published `@modainteract/moda-interact-shared@1.3.1` (release metadata only), with exact registry integrity/tarball and clean installed v2/v3 billing parser evidence. `SHARED-003` is Ready; Background and Messaging remain dependency-gated pending Database and consumer-first adoption. Developer owns integration of the accepted Shared publication task branch and parent gitlink before subsequent implementation.
