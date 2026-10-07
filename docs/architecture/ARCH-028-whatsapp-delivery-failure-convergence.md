---
id: ARCH-028
title: WhatsApp delivery-failure convergence and merchant credit protection
status: agreed
coordinator: moda_architect
created: 2026-10-03
updated: 2026-10-07
---

# ARCH-028: WhatsApp delivery-failure convergence and merchant credit protection

## Status

Agreed.

ARCH-028 is now fully decomposed. The architecture separates provider message lifecycle, recovery-attempt response lifecycle, recovery usage compensation and recipient reachability. A Meta delivery-status failure is associated with its Shop/recovery through durable provider-message and outreach-attempt relations; Shop ownership is never inferred from a customer phone number.

The implementation frontier begins with independent `ARCH-028-DATABASE-001` and `ARCH-028-SHARED-001`. The v3 Shared contract is published before consumer-first Background adoption and later Messaging production. Terminal-recipient policy then converges recovery state, performs idempotent compensation from the provider-status job, removes undelivered outbound-message hard-limit usage, updates finite Shop-scoped recipient suppression, and emits a merchant SYSTEM message only after financial correction succeeds.

ARCH-028 is a pre-production initiative. Backwards compatibility with legacy database rows is not required; DATABASE tasks may use strict new invariants and fresh-database migration validation. Queue-version compatibility remains required for the v2 -> v3 provider-status rollout because producer/consumer deployment is intentionally staged.

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
- Treat missing phone/recipient as a zero-billing, zero-provider-call condition that may become eligible later.
- Split generic recovery compensation from committed purchased-credit compensation so the generic path is not gated by ARCH-027 refund completion.
- Emit a deduplicated merchant SYSTEM message only after release/compensation has durably succeeded.
- Preserve duplicate/out-of-order provider-status safety.

## Non-Goals

- Pre-send WhatsApp-account discovery/existence probing.
- A permanent `Customer.hasWhatsApp` or global phone blacklist.
- Inferring Shop ownership solely from a phone number.
- Redesigning general Shopify/WooCommerce billing or plan economics.
- Introducing a second billing-refund model or provider monetary refund path.
- Retrying every provider error identically.
- Generalizing Meta provider-code policy beyond the explicitly accepted terminal-recipient code without later architecture review.
- Changing unrelated inbound-conversation behaviour except where positive reachability evidence can be cleared after Shop/conversation resolution.
- Introducing a new recovery status solely for late delivery failure; `CheckoutRecovery.MESSAGE_SENT` may remain historical evidence that the provider accepted an outbound recovery. Message/attempt/compensation state is the delivery authority.

## Current Architecture

`moda-interact-background` resolves the recovery recipient before billing admission, creates a `RecoveryOutreachAttempt`, reserves recovery capacity, admits an outbound automated message, calls Meta, then commits recovery usage after a confirmed provider message ID. Follow-up processing later moves the initial attempt from `WAITING_FOR_RESPONSE` to `NO_RESPONSE` before creating the follow-up attempt.

`moda-interact-messaging` receives Meta status webhooks and publishes the Shared normalized status event. `moda-interact-background/src/services/whatsapp-provider-status.service.ts` currently uses a numeric rank:

```text
PENDING=0, FAILED=1, SENT=2, DELIVERED=3, READ=4
```

which means a late `SENT` can incorrectly advance a terminal `FAILED` message back to `SENT`.

Outbound admission creates one `OUTBOUND_AUTOMATED_MESSAGE` UsageEvent before the provider call. Synchronous definitive provider failure currently deletes that usage through `failPrepared`, but an asynchronous terminal failure does not. ARCH-028 makes those semantics consistent.

`RecoveryOutreachAttempt.outboundMessageId` already provides the exact recovery-attempt association for an outbound message. `CheckoutRecovery.shopId` provides tenant identity. A phone number is therefore not needed to determine which Shop/recovery a Meta delivery failure belongs to.

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

Missing customer phone is an expected zero-billing result, not an exception that permanently fails the customer:

```text
no usable recipient
    -> no recovery billing admission
    -> no outbound message admission
    -> no Meta call
    -> mark recovery temporarily blocked: NO_WHATSAPP_RECIPIENT
```

Later customer/recovery reconciliation with a usable number may clear the block and try normal admission. There is no aggressive polling solely for a missing number.

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

DATABASE-001 owns strict pre-production persistence for message failure evidence, reachability, suppression policy and recovery admission-block reasons. DATABASE-002 owns generic committed-reservation compensation lineage/disposition. DATABASE-003 separately adds required `RecoveryOutreachAttempt.recipient` so Background adopts that breaking create-contract only when BACKGROUND-005 is ready to populate it.

### `moda-interact-shared` / `moda_shared`

SHARED-001/002 own the dual-version v2/v3 provider-status runtime contract and publication gate. v3 carries optional bounded `failure.providerCode`; Background continues accepting v2 during consumer-first rollout.

### `moda-interact-messaging` / `moda_messaging`

MESSAGING-001 emits v3 from verified Meta status webhooks and bounded provider codes. It does not decide billing/recovery/reachability policy.

### `moda-interact-background` / `moda_background`

BACKGROUND-001 owns v3 consumer adoption, message failure evidence and explicit status transitions. BACKGROUND-002 owns terminal `131026` classification plus recovery/follow-up convergence without making attempt status a compensation gate. BACKGROUND-004 owns generic compensation, replay invocation and outbound hard-limit correction. BACKGROUND-005 owns reachability/suppression/pre-admission gating/positive clearing. BACKGROUND-007 owns missing-recipient zero-billing handling. BACKGROUND-006 owns synchronous Meta rejection parity. BACKGROUND-008 owns post-compensation merchant notification. BACKGROUND-009 adds committed purchased-credit compensation after ARCH-027's provider refund semantics are available. BACKGROUND-003 remains superseded.

### `moda-interact-admin` / `moda_admin`

ADMIN-001 exposes the platform suppression duration through the existing SUPER_ADMIN Platform Billing Policy controls, using existing policy audit/version semantics.

### `moda-interact-system-test` / `moda_system_test`

SYSTEM-TEST-001 validates the integrated async/sync failure, compensation, hard-limit, reachability, tenant-isolation, missing-recipient and notification behaviour only after every implementation dependency is Complete.

### Gateway / Shopify / WooCommerce

No ARCH-028 Gateway, Shopify or WooCommerce implementation task is required. No new deployment topology is introduced.

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
  NO_WHATSAPP_RECIPIENT
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

### DATABASE-002

Committed compensation remains linked to the original `UsageReservation`/positive UsageEvent through exactly one negative correction and a durable disposition:

```text
RESTORED_SPENDABLE
HELD_FOR_REFUND
HISTORICAL_ONLY
```

A still-RESERVED reservation is released and does not manufacture a compensation UsageEvent.

## Contracts

The cross-repository runtime contract remains the normalized WhatsApp provider-status event owned by `@modainteract/moda-interact-shared/billing`.

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

## Consistency and Transactions

- Status application remains Serializable/CAS protected.
- `FAILED` + terminal provider evidence may be durable before compensation; provider-status job retry must replay compensation even when status convergence is already a no-op.
- Compensation does not require attempt status `FAILED`.
- A reservation still RESERVED is released; committed generic sources receive exact negative correction; committed purchased source is delegated to BACKGROUND-009.
- The exact `OUTBOUND_AUTOMATED_MESSAGE` UsageEvent for a terminally undelivered message is removed/corrected idempotently so the hard limit is not consumed.
- Reachability write occurs only after successful release/compensation for the terminal failure being processed.
- Merchant notification occurs only after financial correction and reachability update succeed.
- Duplicate provider-status events cannot duplicate compensation, suppression, hard-limit correction or merchant messages.

## Ordering

Provider statuses may be duplicate, delayed or out of order. Explicit status transitions are authoritative; there is no total numeric rank that lets `SENT` supersede `FAILED`.

`RecoveryOutreachAttempt.status` represents outreach/response lifecycle and may already be `NO_RESPONSE`; it is not provider-delivery authority. `ConversationMessage` status/failure evidence is the provider-delivery authority.

Ordering/serialization remains narrow to the message/attempt/recovery; the Shop is not globally serialized.

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

ARCH-028 runs on outbound WhatsApp/recovery workload, not raw Shopify event volume. Pre-admission reachability is one indexed `(shopId, recipient)` lookup. Provider-status convergence remains horizontally safe under duplicate/concurrent delivery.

No new queue infrastructure/service deployment is required. Existing Background worker/queue mechanisms may be extended for bounded suppression-expiry resume work where required.

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

There is no production ARCH-028 state to preserve. DATABASE-001/002/003 may enforce strict new invariants without legacy row backfill or upgrade compatibility. Fresh-database migration/rehearsal is the required correctness target. Development databases may be reset as needed.

The v2/v3 provider-status queue still requires consumer-first deployment because retained/rolling queue events may exist during development/integration:

```text
DATABASE-001 -> DATABASE-002 -> BACKGROUND-004
DATABASE-001 -> DATABASE-003 -> BACKGROUND-005
DATABASE-001 -> ADMIN-001
SHARED-001 -> SHARED-002 -> BACKGROUND-001 -> MESSAGING-001 -> BACKGROUND-002 -> BACKGROUND-004
BACKGROUND-004 + DATABASE-003 -> BACKGROUND-005
BACKGROUND-005 -> BACKGROUND-006 -> BACKGROUND-008
BACKGROUND-005 -> BACKGROUND-007
BACKGROUND-004 + BACKGROUND-008 + ARCH-027-BACKGROUND-005 -> BACKGROUND-009
ADMIN-001 + BACKGROUND-007 + BACKGROUND-009 -> SYSTEM-TEST-001
```

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-028-DATABASE-001 | moda_database | Ready | - |
| ARCH-028-DATABASE-002 | moda_database | Pending | DATABASE-001 |
| ARCH-028-DATABASE-003 | moda_database | Pending | DATABASE-001 |
| ARCH-028-SHARED-001 | moda_shared | Ready | - |
| ARCH-028-SHARED-002 | moda_shared | Pending | SHARED-001 |
| ARCH-028-ADMIN-001 | moda_admin | Pending | DATABASE-001 |
| ARCH-028-BACKGROUND-001 | moda_background | Pending | DATABASE-001, SHARED-002 |
| ARCH-028-MESSAGING-001 | moda_messaging | Pending | SHARED-002, BACKGROUND-001 |
| ARCH-028-BACKGROUND-002 | moda_background | Pending | BACKGROUND-001, MESSAGING-001 |
| ARCH-028-BACKGROUND-003 | moda_background | Superseded | - |
| ARCH-028-BACKGROUND-004 | moda_background | Pending | BACKGROUND-002, DATABASE-002, ARCH-027-BACKGROUND-001 |
| ARCH-028-BACKGROUND-005 | moda_background | Pending | BACKGROUND-004, DATABASE-003 |
| ARCH-028-BACKGROUND-006 | moda_background | Pending | BACKGROUND-005 |
| ARCH-028-BACKGROUND-007 | moda_background | Pending | BACKGROUND-005 |
| ARCH-028-BACKGROUND-008 | moda_background | Pending | BACKGROUND-006 |
| ARCH-028-BACKGROUND-009 | moda_background | Pending | BACKGROUND-004, BACKGROUND-008, ARCH-027-BACKGROUND-005 |
| ARCH-028-SYSTEM-TEST-001 | moda_system_test | Pending | ADMIN-001, BACKGROUND-007, BACKGROUND-009 |

`DATABASE-001` and `SHARED-001` are independent Ready tasks. ADMIN-001 may execute after DATABASE-001 without gating provider-status contract work.

The Background chain is intentionally sequential where the tasks modify the same recovery/provider-status path or consume the prior bounded capability. Purchased committed compensation is isolated in BACKGROUND-009 so ARCH-027 refund work cannot block generic compensation, suppression, synchronous parity, no-recipient handling or merchant-notification foundations.

## Open Questions

None blocking implementation.

Provider codes beyond exact `131026` remain outside ARCH-028 terminal-recipient policy until separately reviewed.

## Change History

- 2026-10-03: ARCH-028 agreed. Defined DATABASE-001 as the first iterative task and separated durable failure/reachability evidence from later billing compensation.
- 2026-10-03: Recipient unreachability defined as temporary evidence rather than permanent identity; v3 Shared failure evidence and consumer-first publication/adoption sequence defined.
- 2026-10-04: Initial purchased compensation provenance task defined.
- 2026-10-05: Reconciled with ARCH-027 provider-owned refund flow; BACKGROUND-003 superseded, DATABASE-002 reduced to generic compensation lineage, and BACKGROUND-004 became compensation owner.
- 2026-10-07: Deep architectural reconciliation completed. Shop/recovery association is resolved from provider message/recovery lineage rather than phone lookup; each outreach attempt snapshots its canonical recipient; explicit message-status lattice prevents FAILED -> SENT resurrection; compensation no longer depends on attempt status; provider-status jobs replay idempotent compensation; terminally undelivered outbound hard-limit usage is removed; Shop-scoped pre-admission suppression is configurable in Admin with a seven-day default; synchronous `131026` follows async policy; missing phone is zero-billing and retryable on later evidence; committed purchased compensation is split to BACKGROUND-009; merchant SYSTEM notification is last and deduplicated; DATABASE rollout is explicitly pre-production/breaking.
