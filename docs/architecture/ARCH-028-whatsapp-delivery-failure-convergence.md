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

ARCH-028 is being materialised iteratively. `ARCH-028-DATABASE-001` and `ARCH-028-SHARED-001` are now defined. Messaging, Background, Shared publication and terminal system-validation tasks will be added one at a time after their precise contracts have been reviewed against the then-current codebase.

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

Owns durable message-level failure evidence and tenant-scoped recipient reachability persistence. DATABASE-001 is additive and does not alter billing accounting semantics.

### `moda-interact-shared` / `moda_shared`

Owns the versioned normalized WhatsApp provider-status contract. `ARCH-028-SHARED-001` defines a v3 status contract carrying optional bounded provider-failure evidence while retaining v2 parsing for rolling deployment. Producer and consumer must import the same published schema after the later publication-only gate.

### `moda-interact-messaging` / `moda_messaging`

Will own extraction/normalization of bounded Meta failure evidence from webhook statuses. Messaging does not decide billing, recovery or merchant-notification outcomes.

### `moda-interact-background` / `moda_background`

Will own provider-failure classification, recovery/outreach/follow-up convergence, capacity release/compensation, recipient reachability updates and merchant SYSTEM notification. Background must reuse the existing billing reservation/correction owners rather than create a competing accounting mechanism.

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

### Compensation

The existing schema already contains `UsageEvent.correctionOfUsageEventId`. Later Background task design must first prove whether that relation plus existing counters and deterministic idempotency keys are sufficient for recovery compensation. A second ARCH-028 database task must not be created merely to duplicate existing correction semantics.

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
- If recovery usage is already `COMMITTED`, later Background design must preserve the original commit and create auditable correction evidence rather than rewriting history as if the commit never occurred.
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

Later runtime tasks must tolerate rows/messages created before ARCH-028 fields are populated.

No queue drain is required for DATABASE-001. For the later v3 runtime rollout, deploy the dual-version Background consumer before the v3 Messaging producer; the upgraded consumer continues accepting v2 backlog.

## Decisions / Tasks

Task definitions are materialised iteratively.

| Task | Owner | Status | Depends On |
|------|-------|--------|------------|
| ARCH-028-DATABASE-001 | moda_database | Ready | - |
| ARCH-028-SHARED-001 | moda_shared | Ready | - |

DATABASE-001 and SHARED-001 are intentionally independent: one establishes durable persistence, while the other establishes the cross-service runtime envelope. Do not serialize them merely because their definitions were authored sequentially.

Planned but not yet materialised work includes the Shared publication-only gate, Messaging v3 normalization, Background dual-version consumption/classification/convergence/compensation/reachability/merchant notification, and terminal system validation. Exact task IDs and dependencies will be added only after each boundary is inspected.

## Open Questions

- Exact provider-code classification table and which Meta failures qualify as terminal recipient failures.
- Exact finite suppression duration and whether it varies by provider failure classification.
- Whether existing `UsageEvent.correctionOfUsageEventId` and current counter models are fully sufficient for compensation without another migration.
- Whether `CheckoutRecovery.MESSAGE_SENT` may remain as historical "provider accepted" state after an outreach attempt is later marked FAILED, or whether a later architecture refinement needs a new recovery status.

## Change History

- 2026-10-03: ARCH-028 agreed. Defined DATABASE-001 as the first iterative task. The architecture explicitly separates durable failure/reachability evidence from later billing compensation and reuses existing merchant support/correction primitives where possible.
- 2026-10-03: Clarified that recipient unreachability is temporary evidence, not durable identity. Removed the proposed persistent reachability status enum; active suppression is finite (`suppressUntil`) and expires automatically unless newer evidence changes it sooner.
- 2026-10-03: Defined SHARED-001. Provider-status v3 adds only optional bounded `failure.providerCode` evidence on FAILED events; the canonical parser accepts both v2 and v3 so Background can be upgraded before Messaging begins producing v3.
