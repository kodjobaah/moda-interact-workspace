---
id: ARCH-028
title: WhatsApp delivery-failure convergence and merchant credit protection
status: agreed
coordinator: moda_architect
created: 2026-10-03
updated: 2026-10-03
---

# ARCH-028: WhatsApp delivery-failure convergence and merchant credit protection

## Status

Agreed.

ARCH-028 is being materialised iteratively. `ARCH-028-DATABASE-001`, `ARCH-028-SHARED-001`, publication-only `ARCH-028-SHARED-002`, consumer-first `ARCH-028-BACKGROUND-001`, gated v3 producer `ARCH-028-MESSAGING-001`, terminal recipient-delivery convergence `ARCH-028-BACKGROUND-002`, and compensation-provenance `ARCH-028-DATABASE-002` are now defined. Later Background compensation/reachability/merchant-notification tasks will be added one at a time after their precise contracts have been reviewed against the then-current codebase.

## Problem

Moda currently distinguishes WhatsApp provider message states at the `ConversationMessage` level, but a provider-accepted outbound recovery can later receive an asynchronous `FAILED` status after the recovery credit has already been committed and a no-response follow-up has been scheduled.

The current provider-status path can therefore leave durable state inconsistent:

```text
ConversationMessage = FAILED
RecoveryOutreachAttempt = WAITING_FOR_RESPONSE
CheckoutRecovery = MESSAGE_SENT
recovery capacity = committed
follow-up = still actionable
merchant = not informed
```

The current normalized provider-status contract also drops Meta failure codes. Background therefore cannot reliably distinguish a terminal recipient-delivery failure from a transient or ambiguous provider failure.

A customer may have supplied a syntactically valid telephone number that is not currently reachable on WhatsApp. Moda must not repeatedly send proactive recovery messages to a recipient that the provider has classified as terminally undeliverable, and a definitively undelivered recovery must not ultimately consume the merchant's recovery allowance.

## Goals

- Distinguish provider acceptance, provider delivery and customer response as separate lifecycle facts.
- Preserve bounded provider failure evidence for outbound WhatsApp messages.
- Maintain tenant-scoped durable WhatsApp recipient reachability evidence and **temporary** suppression without asserting that a customer permanently "has no WhatsApp account" from one failure.
- Converge asynchronous terminal recipient failures across message, outreach-attempt and follow-up state.
- Ensure a definitively undelivered recovery does not ultimately consume merchant recovery capacity.
- Reuse the existing negative `UsageEvent` correction mechanism where sufficient rather than inventing a second billing-refund model.
- Produce a deduplicated merchant-visible SYSTEM support message only after release/compensation has durably succeeded.
- Prevent a no-response follow-up from being sent after the initial outbound message is authoritatively known to be undelivered.
- Preserve duplicate/out-of-order provider-status safety and make all convergence idempotent.

## Non-Goals

- Pre-send WhatsApp-account discovery or existence probing.
- Claiming categorically that a recipient "does not have WhatsApp" when provider evidence is ambiguous.
- Changing Meta/WhatsApp pricing policy.
- Redesigning general merchant billing, Shopify billing, WooCommerce billing or plan economics.
- Introducing a new merchant-notification subsystem; ARCH-028 reuses `MerchantSupportThread` / `MerchantSupportMessage`.
- Retrying or compensating every provider failure identically.
- Changing unrelated inbound WhatsApp conversation behaviour.
- Changing the CheckoutRecovery status enum unless a later source review demonstrates that existing states cannot express the required converged behaviour safely.

## Current Architecture

Outbound proactive recovery sends are admitted and sent from `moda-interact-background`. Once the Meta send API returns a provider message identifier, the current recovery finalisation path can commit the recovery reservation, move the outreach attempt to `WAITING_FOR_RESPONSE`, move the recovery to `MESSAGE_SENT` and schedule a follow-up.

`moda-interact-messaging` receives Meta webhook statuses and normalizes `sent`, `delivered`, `read` and `failed` into the versioned Shared `NormalizedWhatsAppStatus` contract. The current normalized status does not retain provider failure codes.

`moda-interact-background/src/services/whatsapp-provider-status.service.ts` applies the normalized status to `whatsapp.ConversationMessage`. A later `FAILED` status can therefore move the message to `FAILED`, but it does not currently reconcile the associated recovery attempt, follow-up, recovery capacity or merchant notification.

The current database already has useful billing primitives:

- `UsageReservation` records admission and the committed recovery `UsageEvent`;
- `UsageEvent.correctionOfUsageEventId` supports durable correction lineage;
- Shop, billing-period, purchased and promotional counters retain reserved/committed/current quantities;
- `MerchantSupportMessage.sourceKey` already provides deduplicated system-message identity.

ARCH-028 must reuse those capabilities before adding new billing persistence.

## Proposed Architecture

The provider-status lifecycle becomes:

```text
Meta status webhook
    -> Messaging validates/normalizes bounded failure evidence
    -> versioned Shared provider-status event
    -> Background resolves ConversationMessage
    -> Background classifies failure evidence

terminal recipient-delivery failure
    -> ConversationMessage FAILED + durable failure evidence
    -> RecoveryOutreachAttempt FAILED
    -> no-response follow-up becomes non-actionable
    -> release RESERVED usage OR compensate already COMMITTED usage
    -> restore the exact capacity source
    -> record recipient failure evidence + finite suppressUntil
    -> deduplicated merchant SYSTEM message

later suppression expiry
    -> proactive sending becomes eligible again (subject to normal admission)

later inbound/successful delivery evidence
    -> record positive reachability evidence
    -> clear active suppression immediately
```

Provider failure classification must remain explicit. Temporary/configuration/ambiguous failures must not be silently converted into terminal recipient failures.

### Iterative task-definition rule

DATABASE-001 and SHARED-001 are now materialised as independent implementation tasks. Their definition order does **not** create an artificial execution dependency: the durable database foundation and the versioned Shared runtime contract can be implemented/reviewed independently. Later Shared publication, Messaging, Background and system-validation tasks will be defined only after re-inspecting the then-current producer/consumer code and accepted implementation state.

## Request / Event Flow

### Synchronous terminal rejection before recovery commit

```text
Background send
    -> provider rejects definitively
    -> message FAILED with bounded failure evidence
    -> RESERVED recovery reservation released
    -> attempt FAILED
    -> record recipient failure evidence + finite suppression
    -> merchant SYSTEM message after durable release
```

### Asynchronous terminal rejection after provider acceptance

```text
Background send accepted -> provider message id
    -> recovery usage committed
    -> attempt WAITING_FOR_RESPONSE
    -> follow-up scheduled

Meta later reports FAILED
    -> Messaging publishes bounded failure evidence
    -> Background atomically/idempotently converges recovery lifecycle
    -> negative UsageEvent correction when required
    -> exact capacity source restored
    -> follow-up suppressed
    -> record recipient failure evidence + finite suppression
    -> merchant SYSTEM message after compensation succeeds
```

### Reachability recovery

Recipient suppression is deliberately temporary.

A terminal recipient failure records failure evidence and a finite `suppressUntil`. When that time expires, the old failure must no longer by itself block another proactive send. A person who is unreachable today may become reachable tomorrow.

A later successful delivery or inbound WhatsApp message provides positive evidence sooner and must clear active suppression immediately. Historical failure evidence may remain for audit/diagnostics; it is not a permanent blacklist.

## Repository Responsibilities

### `moda-interact-database` / `moda_database`

Owns durable message-level failure evidence, tenant-scoped recipient reachability persistence and the minimal compensation provenance required by later Background accounting. DATABASE-001 remains the failure/reachability foundation; DATABASE-002 adds only committed-reservation correction linkage plus purchased-credit/refund provenance proven necessary by source review.

### `moda-interact-shared` / `moda_shared`

Owns the versioned normalized WhatsApp provider-status contract. `ARCH-028-SHARED-001` defines a v3 status contract carrying optional bounded provider-failure evidence while retaining v2 parsing for rolling deployment. Producer and consumer must import the same published schema after `ARCH-028-SHARED-002` publishes the architect-accepted Shared implementation.

### `moda-interact-messaging` / `moda_messaging`

`ARCH-028-MESSAGING-001` owns adoption of the exact SHARED-002 release, v3 provider-status production, and bounded extraction of Meta failure codes from verified status webhooks. Messaging does not decide provider-code policy, billing, recovery, reachability or merchant-notification outcomes.

### `moda-interact-background` / `moda_background`

Owns consumer-first adoption of the published dual-version provider-status contract and bounded message failure-evidence persistence in `ARCH-028-BACKGROUND-001`. `ARCH-028-BACKGROUND-002` owns the first policy step: classify the bounded `131026` evidence as a recipient-undeliverable bucket, converge a linked waiting recovery outreach attempt to `FAILED`, and ensure its no-response follow-up is non-actionable. Later Background tasks will own capacity release/compensation, recipient reachability updates and merchant SYSTEM notification. Background must reuse the existing billing reservation/correction owners rather than create a competing accounting mechanism.

### Shopify / WooCommerce / Admin / Gateway

No implementation task is currently required. Merchant notification reuses the existing support surface. Gateway topology is unchanged.

## Data Model

### DATABASE-001 durable failure/reachability foundation

Add bounded provider-failure evidence to `whatsapp.ConversationMessage`:

```text
providerFailureCode?   bounded provider code
failedAt?              provider failure occurrence time
```

Add tenant-scoped reachability evidence:

```text
whatsapp.WhatsAppRecipientReachability
    id
    shopId -> commerce.Shop
    recipient
    lastProviderFailureCode?
    lastFailureAt?
    suppressUntil?
    lastSuccessfulAt?
    version
    createdAt
    updatedAt

UNIQUE(shopId, recipient)
```

There is deliberately no durable `REACHABLE | UNDELIVERABLE` status enum.

The row stores historical evidence plus an optional temporary suppression window. Active suppression is derived from `suppressUntil > now`. After that timestamp expires, the old failure does not remain authoritative evidence that the person still cannot receive WhatsApp.

Absence of a row means reachability is unknown. ARCH-028 does not persist a permanent `customer.hasWhatsApp` boolean.

### DATABASE-002 compensation provenance

The existing `UsageEvent.correctionOfUsageEventId` remains the canonical correction lineage and is not replaced. A deeper review of the purchased-credit commit/refund lifecycle found one missing durable fact: a final reserved purchased credit may commit while its lot is `WITHDRAWN`, transition the lot to `COMPLETED`, and cancel live refund requests as `NO_CREDITS_REMAINING`. Current rows do not preserve enough direct provenance to reconstruct that exact prior state later without guessing.

DATABASE-002 therefore adds only:

```text
UsageReservation.compensationUsageEventId?
UsageReservation.compensationReason?
UsageReservation.compensatedAt?
UsageReservation.purchasedCreditPurchaseStatusAtCommit?
UsageReservationRefundCancellation(usageReservationId, refundId, previousStatus)
```

The original reservation remains `COMMITTED`; the linked negative UsageEvent is the auditable correction. No compensation is performed by the database task.

### Merchant notification

The existing support schema is reused:

```text
MerchantSupportThread
MerchantSupportMessage(kind = SYSTEM, sourceKey UNIQUE)
```

No new notification table is planned.

## Contracts

The cross-repository runtime contract is the normalized WhatsApp provider-status event owned by `moda-interact-shared` and imported from `@modainteract/moda-interact-shared/billing` by Messaging and Background.

### ARCH-028 provider-status contract versioning

`ARCH-028-SHARED-001` defines the following rolling-deployment contract:

```text
v2 (legacy)
    schemaVersion = 2
    existing identity/status/occurredAt/pricing fields only

v3 (current)
    schemaVersion = 3
    same existing fields
    + optional failure.providerCode
```

`failure.providerCode` is a trimmed, non-empty provider code string bounded to 64 characters so it maps safely to the DATABASE-001 persistence boundary. It is **not** free-form provider text, a webhook body, error details or a Moda classification.

For v3:

- `failure` is permitted only when `status = FAILED`;
- a `FAILED` event may omit `failure` when bounded provider evidence is unavailable;
- non-FAILED events must reject `failure`;
- all existing identity/timestamp/pricing strictness remains unchanged.

The Shared parser accepts both v2 and v3. Existing v2 queue records therefore remain consumable by an upgraded Background consumer. Messaging will move to v3 only after the Background consumer has adopted the published dual-version parser.

The safe rolling-deployment order is:

```text
SHARED-001 implementation accepted
    -> SHARED publication-only gate
    -> Background consumer installs published version and accepts v2 + v3
    -> Messaging producer installs published version and begins emitting v3
```

An old Background consumer must never be exposed to v3 events because its current strict v2 schema rejects unknown schema versions/fields. No queue drain is required when the consumer-first order is followed because the upgraded consumer continues accepting v2 backlog.

Database fields are persistence contracts, not a replacement for this Shared runtime event schema.

## Consistency and Transactions

- Duplicate provider-status events must not duplicate capacity restoration, correction UsageEvents, reachability transitions or merchant notifications.
- A merchant notification claiming the recovery was not charged must be persisted only after release/compensation has durably succeeded.
- If a reservation is still `RESERVED`, release is preferred; do not manufacture a correction UsageEvent for usage that was never committed.
- If recovery usage is already `COMMITTED`, preserve the original commit and create auditable correction evidence rather than rewriting history as if the commit never occurred. DATABASE-002 makes the one-to-one correction link and purchased/refund provenance durable; later Background code owns the actual transaction.
- Recipient reachability is tenant scoped by `(shopId, recipient)`.
- Provider failure evidence must be bounded; raw webhook payloads are not durable failure state.

## Ordering

Provider status events may be duplicated, delayed and delivered out of order.

Suppression expires by time as well as by positive evidence. Once `suppressUntil` has passed, the old failure must no longer block a new proactive attempt solely because of that historical failure.

A later positive delivery/read or inbound-message signal clears suppression earlier. ARCH-028 must not treat one terminal-looking failure as a permanent global blacklist.

The same outreach attempt/message identity is the narrow ordering/correlation key for recovery convergence; the whole shop must not be globally serialized.

## Failure Handling

- Invalid provider-status payloads remain rejected by runtime validation.
- Unknown provider message IDs remain bounded operational failures and must not create reachability state for an unowned recipient.
- Temporary/configuration/ambiguous provider failures must not be represented as definite recipient unreachability.
- Compensation failure must leave the merchant notification unsent and the work retryable/idempotent.
- Translation failure for the merchant SYSTEM message must not roll back already-completed recovery compensation.
- Observability/backend failures must not become recovery correctness dependencies.

## Scalability

ARCH-028 work occurs only for outbound WhatsApp messages/status events, not raw Shopify webhook volume. Recipient reachability is a narrow `(shopId, recipient)` lookup/upsert and should use a unique index rather than scans.

Provider-status convergence must remain horizontally safe under duplicate and concurrent webhook delivery. No global serialization is introduced.

## Security

- Never persist raw Meta webhook payloads, access tokens, authorization headers or arbitrary provider error text as reachability evidence.
- Provider failure codes must be bounded.
- Reachability is shop scoped to preserve tenant isolation.
- Merchant support notifications must never leak cross-tenant customer data.
- Do not expose operational provider failure payloads directly to merchants; merchant text must use bounded platform-owned wording.

## Observability

Later Background/Messaging tasks should preserve existing structured logging and add only bounded semantic outcomes required to distinguish terminal-recipient, temporary-provider, configuration and ambiguous failures.

Useful identifiers are `shopId`, internal message ID, provider message ID, outreach-attempt ID and bounded provider code. Do not log complete customer/message payloads.

No new telemetry transport or Gateway task is required.

## Rollout / Migration

Rollout classification: additive pre-production/compatible migration.

DATABASE-001 adds nullable message fields and a new reachability table. Existing messages are not backfilled with invented provider-failure evidence; existing absence of reachability data means UNKNOWN.

DATABASE-002 is also additive: existing reservations/refunds retain null/empty compensation provenance. It must not require current pre-compensation Background code to populate the new provenance immediately on migration deployment.

Later runtime tasks must tolerate rows/messages/reservations created before ARCH-028 fields are populated.

No queue drain is required for DATABASE-001. For the later v3 runtime rollout, `ARCH-028-BACKGROUND-001` adopts the exact SHARED-002 package and DATABASE-001 fields before the v3 Messaging producer is allowed to deploy; the upgraded consumer continues accepting v2 backlog.

## Decisions / Tasks

Task definitions are materialised iteratively.

| Task | Owner | Status | Depends On |
|------|-------|--------|------------|
| ARCH-028-DATABASE-001 | moda_database | Ready | - |
| ARCH-028-DATABASE-002 | moda_database | Pending | ARCH-028-DATABASE-001 |
| ARCH-028-SHARED-001 | moda_shared | Ready | - |
| ARCH-028-SHARED-002 | moda_shared | Pending | ARCH-028-SHARED-001 |
| ARCH-028-BACKGROUND-001 | moda_background | Pending | ARCH-028-DATABASE-001, ARCH-028-SHARED-002 |
| ARCH-028-MESSAGING-001 | moda_messaging | Pending | ARCH-028-SHARED-002, ARCH-028-BACKGROUND-001 |
| ARCH-028-BACKGROUND-002 | moda_background | Pending | ARCH-028-BACKGROUND-001, ARCH-028-MESSAGING-001 |

DATABASE-001 and SHARED-001 are intentionally independent: one establishes durable persistence, while the other establishes the cross-service runtime envelope. Do not serialize them merely because their definitions were authored sequentially.

BACKGROUND-001 is the consumer-first rollout gate. It adopts the exact published Shared package and accepted message failure-evidence fields, accepts both v2/v3, and persists bounded FAILED evidence without yet introducing provider-code policy.

MESSAGING-001 is deliberately gated on both SHARED-002 and BACKGROUND-001. It upgrades the producer to v3 only after the dual-version consumer is ready, preserves exact non-failure status job identity, and gives a v3 FAILED event carrying new failure evidence a distinct deterministic job identity so it cannot be suppressed by a retained legacy v2 FAILED BullMQ job.

Planned but not yet materialised work includes the Background compensation implementation, recipient reachability updates, merchant notification and terminal system validation. DATABASE-002 now provides the compensation provenance prerequisite; exact Background task IDs/dependencies will be added only after that implementation boundary is inspected.

### Terminal recipient-delivery classification boundary

`ARCH-028-BACKGROUND-002` deliberately starts with one narrow provider-code policy:

```text
providerFailureCode == "131026"
    -> RECIPIENT_UNDELIVERABLE

all other / absent provider codes
    -> UNCLASSIFIED by this task
```

`RECIPIENT_UNDELIVERABLE` means only that Meta supplied its recipient-undeliverable bucket for this message. It must not be rendered or persisted as a permanent assertion that the person has no WhatsApp account. This task changes the linked recovery outreach attempt from `WAITING_FOR_RESPONSE` to `FAILED` using guarded/idempotent persistence and makes any already-scheduled no-response follow-up non-actionable. It does not yet release/compensate usage, write recipient suppression, or notify the merchant.

## Open Questions

- Exact provider-code classification table and which Meta failures qualify as terminal recipient failures.
- Exact finite suppression duration and whether it varies by provider failure classification.
- Whether `CheckoutRecovery.MESSAGE_SENT` may remain as historical "provider accepted" state after an outreach attempt is later marked FAILED, or whether a later architecture refinement needs a new recovery status.

## Change History

- 2026-10-03: ARCH-028 agreed. Defined DATABASE-001 as the first iterative task. The architecture explicitly separates durable failure/reachability evidence from later billing compensation and reuses existing merchant support/correction primitives where possible.
- 2026-10-03: Clarified that recipient unreachability is temporary evidence, not durable identity. Removed the proposed persistent reachability status enum; active suppression is finite (`suppressUntil`) and expires automatically unless newer evidence changes it sooner.
- 2026-10-03: Defined SHARED-001. Provider-status v3 adds only optional bounded `failure.providerCode` evidence on FAILED events; the canonical parser accepts both v2 and v3 so Background can be upgraded before Messaging begins producing v3.
- 2026-10-03: Defined SHARED-002 as the publication-only gate. It publishes exactly one compatible patch release after SHARED-001 acceptance and verifies the exact registry revision plus clean-install billing exports before any consumer adoption.
- 2026-10-03: Defined BACKGROUND-001 as the consumer-first v3 adoption gate. It depends on DATABASE-001 and the published SHARED-002 revision, accepts both v2/v3 provider statuses and persists only bounded message failure evidence; Messaging v3 production remains blocked until this consumer is accepted.
- 2026-10-03: Defined MESSAGING-001 as the gated v3 producer. It depends on SHARED-002 plus accepted BACKGROUND-001 consumer compatibility, emits only bounded provider codes from verified Meta FAILED statuses, and refines FAILED job identity only when new failure evidence is present so legacy v2 retention cannot suppress evidence enrichment.
- 2026-10-03: After reviewing committed recovery accounting, defined DATABASE-002. Existing UsageEvent correction lineage is retained, but the task adds one-to-one compensation linkage and explicit purchased-credit/refund cancellation provenance so later compensation never guesses pre-commit purchase/refund state.
