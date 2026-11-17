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
status: complete
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

**Architect acceptance — 17 November 2026 (Shared contract scope only).** SHARED-001 is `complete`: implementation commit `3245489f8cf4b6e03b90bca3eedae54497ee093e` was inspected from the supplied worktree and its two optional marker fields conform to this contract. The completion report below distinguishes agent-reported tests from architect-inspected source. Shared package `6.2.0` is **prepared, not verified published**. Shopify and Background must both pin a compatible published build before marker-producing/consuming deployment. Do not mistake this schema acceptance for runtime webhook, Redis, consent or release acceptance.

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

## Completion report — architect accepted 17 November 2026

### Decision and inspected evidence

**ACCEPT SHARED-001** within its defined Shared schema/contract scope. The supplied `moda-interact-workspace-ARCH-077-SHARED-001.zip` contains the task worktree and Shared package source. Reported implementation commit: `3245489f8cf4b6e03b90bca3eedae54497ee093e` on `task/ARCH-077-SHARED-001`, based on `8bb6ca5ec0ce28540e99c92084885fae8ebb1af9`. This ZIP does not contain Git history, so the commit's association with those exact bytes was not independently verified against the remote Git object; source was reviewed directly from the archive.

Reviewed source and contract tests:

- `moda-interact-shared/src/shopify/v2/checkout-created.schema.ts`: exactly two optional properties added to strict `CheckoutCreatedPayloadV2Schema` — `cartCorrelationMarker` (`^m1_[A-Za-z0-9_-]{43}$`) and `cartCorrelationMarkerStatus` (`PRESENT | ABSENT | INVALID | AMBIGUOUS`).
- `moda-interact-shared/src/shopify/v3/checkout-updated.schema.ts`: same two properties on strict `CheckoutUpdatedPayloadV3Schema`.
- `src/shopify/v2/recovery-event.test.ts` and `src/shopify/recovery-event.schema.test.ts`: tests cover marker round-trip, all status values, invalid marker/status rejection, legacy omission and strict extra-field rejection. V2 checkout-updated is intentionally unchanged.
- `moda-interact-shared/package.json` and `package-lock.json`: package and root lockfile version fields consistently read `6.2.0`; this is release metadata, not independent proof of npm publication.

No new queue, event type, HMAC key, envelope, SQL schema, consent decision or unrelated provider contract was observed in the inspected files. The strict schema deliberately permits optional fields independently: the S002 producer and B001 consumer **must** enforce `PRESENT` iff exactly one valid marker, and all other explicit statuses with no marker. Omitted fields mean legacy `NOT_OBSERVED`, not verified `ABSENT`. Do not move those business rules into Zod without new architect approval.

### Test evidence and limitations

Agent completion report (not independently rerun in this review environment): `npm run typecheck` passed; focused tests passed 35/35; full `npm test` reported 849 tests (846 pass, 3 pre-existing skipped); `npm run build` passed. The ZIP has source and tests but no `node_modules` or complete raw test logs. Tests do not establish successful Shopify provider delivery, Redis correlation, final outbound eligibility or publishing the package.

### Required integration handoff / release gates

1. Publish and verify `@modainteract/moda-interact-shared@6.2.0` from the inspected commit, or a documented equivalent build with exactly these exports. Do not assume `package.json` version equals publication.
2. In `ARCH-077-SHOPIFY-002`, pin the actual published Shared version in `moda-interact` package and lockfile, classify authenticated checkout `note_attributes`, construct the pair **before** strict event parsing/enqueue, and verify full producer serialization. Never log the raw marker.
3. In `ARCH-077-BACKGROUND-001`, pin the **same compatible Shared build** in `moda-interact-background` and verify dequeue/parse, missing-legacy fields, invalid/ambiguous status, shop-scoped Redis resolution and old queue-event compatibility. If the pinned consumer strips/rejects these fields, stop rather than add a second queue or side channel.
4. Preserve the agreed deferred GRANT/REVOKE materialisation: marker propagation alone is never consent. STOP, existing `CheckoutRecovery` admission, credit and outbound fences remain under their owning tasks.
5. No changes to any `docs/decisions/**/_index.md`, repository Git links or task branches are made by this acceptance patch.

### Task orchestration

This acceptance changes SHARED-001 to canonical `complete`, normalises the already architect-accepted S001 dependency to `complete`, and makes SHOPIFY-002 `ready` in the parent task register. Downstream tasks must still pass their own named dependency and runtime acceptance gates. Reported task branch correction commit `923f67bb7eaf9ea789d0314f732f725da3917206` and launcher claim `e6883d5d73f890a410161fa5a6c8fa75bed5fb83` are provenance from the agent report; this patch does not merge those branches or move the Shared submodule pin.
