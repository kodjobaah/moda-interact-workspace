---
id: ARCH-077-SHARED-001
architecture_id: ARCH-077
title: Transport Shopify checkout cart-correlation marker in existing strict V2/V3 events
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 45
executor: copilot
claimed_at: 2026-11-17T13:15:00Z
attempt: 1
depends_on: [ARCH-077-SHOPIFY-001]
enables: [ARCH-077-SHOPIFY-002, ARCH-077-BACKGROUND-001]
created: 2026-11-17
updated: 2026-11-17
---

# Transport Shopify checkout cart-correlation marker in existing strict V2/V3 events

## Authorisation

**Ready for implementation now.** S001 marker propagation has been verified and the v1 transport field contract has been frozen. Implement exactly the two optional fields below; no repeat browser diagnostic or unapproved auth scheme is required. Do not claim real Shopify/Redis integration from schema unit tests.

## Scope and verified source boundary

The 13 November workspace snapshot has `moda-interact/app/services/webhooks/checkout-normalization.ts` forwarding only checkout identity, optional cart token, checkout-created time and abandoned URL. The existing strict Shared schemas discard/reject extra fields and do not expose `note_attributes`. Therefore BACKGROUND-001 **cannot consume** the marker directly from today's queued checkout events. This task adds **only** a minimal, backward-compatible optional marker transport to the existing Shopify event contracts; it neither creates a new event/queue nor changes consent authority.

## Exact repository changes

- [ ] Edit `src/shopify/v2/checkout-created.schema.ts` `CheckoutCreatedPayloadV2Schema` and `src/shopify/v3/checkout-updated.schema.ts` `CheckoutUpdatedPayloadV3Schema`. Add precisely `cartCorrelationMarker: z.string().regex(/^m1_[A-Za-z0-9_-]{43}$/).optional()` and `cartCorrelationMarkerStatus: z.enum(["PRESENT", "ABSENT", "INVALID", "AMBIGUOUS"]).optional()` to their strict payload objects. They are **optional** for old jobs. Do not add new event/queue types, HMAC secrets, encryption, digest transport, metadata envelopes or database columns.
- [ ] In S002's Shopify producer code, enforce the pair: `PRESENT` requires exactly one validated 46-character `cartCorrelationMarker`; `ABSENT`, `INVALID`, `AMBIGUOUS` omit marker. When fields are both absent on a legacy event B001 treats it as `NOT_OBSERVED`, not verified `ABSENT`. Pair validation belongs to the producer/consumer, not business rules hidden in Zod.
- [ ] In `src/shopify/v2/recovery-event.test.ts`, `src/shopify/recovery-event.schema.test.ts` and current V3 contract tests, verify exact round-trip of the marker, all other status variants, invalid pair rejection before publication, legacy omission and unchanged strict top-level event behaviour.
- [ ] Preserve `SHOPIFY_COMMERCE_EVENT_SCHEMA_VERSION_V2/V3`, existing checkout event names, queue names, job IDs, event ordering keys, all cart/order event contracts, and WooCommerce contracts. Publish/pin a coherent compatible Shared version in Shopify and Background **before** production of new optional fields.

## Exact producer → existing queue → consumer path

- [ ] In the existing authenticated webhook ingress (`moda-interact/app/services/webhooks/shopify-webhook-ingress.service.ts` and checkout-create/update event assembly), use the trusted existing shop resolution, not an untrusted webhook body field. Read only `moda_cart_correlation_v1` from authenticated Shopify checkout `note_attributes` (array `{name,value}` or object form). Exactly one canonical 46-character `m1_` value gives `PRESENT` plus that marker; absent gives `ABSENT`; malformed gives `INVALID`; duplicates or contradictions give `AMBIGUOUS`. Discard the remaining attribute array. Never place any contact information or consent decision in checkout events.
- [ ] Populate only the two optional fields on existing checkout-created V2 and checkout-updated V3 event payloads after normalisation, before strict parse/enqueue. Do not modify `checkout-normalization.ts` token handling, worker queues, route auth, payment/order cancellation, or idempotency. The random marker is already shopper-writable cart data and **not an authentication secret**; it may be present transiently in the existing bounded queue and Redis. Never log it.
- [ ] B001 consumes these two fields from the mapped existing event, revalidates the marker's format, scopes all lookups to the authenticated event shop, and resolves `shopify:consent:v1:marker:<shopId>:<marker>` plus the reciprocal temporary cart record. Marker possession alone never authenticates a shopper or grants consent. Missing fields from an old event are `NOT_OBSERVED`; `INVALID`/`AMBIGUOUS` fail closed rather than becoming `ABSENT`.
- [ ] If a strict parser rejects or drops these optional fields under the pinned Shared version, **stop** for a coordinated Shared pin, not a second Redis side-channel.

## Validation / stop

Run Shared schema round-trip/type checks and test fixtures for existing V2 create, V3 update, old queued events and new optional marker states. Confirm the Shopify and Background dependency lockfiles resolve the **same** new Shared export and no cross-service strict schema rejects a valid event. Return exact commands, SHA, package version and green/red evidence. Stop for architect review if adding fields requires a breaking schema version, touches unrelated app/queue behavior, or invalid/ambiguous states cannot be transported without discarding checkout events. No edits to any `docs/decisions/**/_index.md`.
