---
id: ARCH-054
title: Merchant-configurable delayed AI replies with immediate human handover
status: in_progress
coordinator: moda_architect
created: 2026-10-31
updated: 2026-11-01
---

# ARCH-054: Merchant-configurable delayed AI replies with immediate human handover

## Status and rollout

Implementation is underway. This is a new initiative and does not reopen ARCH-040 or ARCH-052. The attached 2026-10-31 16:28 snapshot is the inspected baseline. Task definitions are materialised in their canonical parent worktrees. Database, shared-contract, API-002 and Shopify-001/002 work is architect-accepted; remaining implementation and terminal system-test tasks are still pending or ready according to their dependencies.

The feature is pre-production; a coordinated breaking database and contract rollout is permissible. Preserve currently valid human-message commands and Meta message histories. Queue items created under the previous processor must be drained/reconciled at rollout; never treat an old queued job as entitlement to send.

## Problem

`ShopSettings` has `recoveryDelayMinutes` for *initial recovery outreach*, not for replies. `BackgroundRuntimeConfig.conversationQuietWindowMs` (default 3000) and `conversationMaxSettleWindowMs` (default 10000) combine customer fragments, but do not offer merchant-specific AI waiting. `ConversationTurnProcessor` schedules BullMQ jobs keyed by conversation ID/inbound version and uses `Conversation.pendingTurnStartedAt`, `inboundVersion`, `lastProcessedVersion`, and processing leases. The recovery-only AI/HUMAN fence reads `Conversation.controlRevision` via `AiTurnOwnershipService`; Shopify and hosted WooCommerce have separate control transitions. HUMAN commands already use a durable, direct dispatch workflow. There is no merchant-configurable AI response delay or durable per-turn eligibility deadline.

## Agreed behaviour and non-goals

1. A merchant sets **any whole number of minutes 0–30 inclusive**; default **0**. Reject strings, fractions, negatives, >30, NaN, unknown keys, unauthorised writes and revision conflicts at each public boundary.
2. Delay applies only to **CommerceAgent-generated customer replies** on active recovery conversations while `controlMode=AI`. It applies to every new pending AI turn, not merely the first reply after outreach. The delay is **additional to** the existing quiet/maximum-settle calculation. Zero retains the old settle-first behaviour.
3. The anchor is the **first processable customer message of a pending AI turn**, not the initial outreach send, nor the last message received. For text, use the transaction's first committed customer-message receipt time; for audio, use the first successful transcription-completion time. Subsequent customer messages join the same pending turn and **must not move the AI deadline**, even if an inbound version changes.
4. Record the merchant's delay and `controlRevision` **once** when that pending turn is opened; changes to merchant settings affect only *future* turns. A HUMAN→AI cycle never resurrects work scheduled under an earlier control revision.
5. Human-written replies are **never delayed by this setting**. Existing `HUMAN_TEXT` and permitted human follow-up commands continue through existing moderation, entitlement, tenant ownership, 24-hour window, idempotency and dispatch gates. The feature does not guarantee instant provider delivery; it only adds **zero discretionary waiting** to HUMAN messages.
6. Do not delay STOP/unsubscribe handling, safety/abuse controls, provider receipts, initial recovery outreach, configured no-response follow-up, or deterministic routing guidance. The configurable delay gates an **AGENT model reply**, not unrelated AUTOMATION/Meta operations.
7. Exact contextual routing continues to use the quoted outbound Meta ID, recovery-scoped shop ownership and the customer's normalised shop-scoped phone. A person contacting two shops through one Meta sender must have independently scheduled conversations and cannot leak data between merchants.
8. No new worker class per conversation, blocking `sleep`, open SQL transaction while waiting, new database/queue infrastructure, per-customer timer row, merchant staff account or standalone-order inbox. Do not reuse `recoveryDelayMinutes` or repurpose Background Admin quiet-window controls.
9. At each final outbound admission, existing moderation, active recovery, current inbound version, control revision, human takeover, consent/STOP and Meta service-window fences remain authoritative. A provider request already dispatched cannot be recalled.
10. Preserve originating Prisma/Meta/SDK error details through `@modainteract/moda-interact-shared/logging`, with redaction and no swallowed exceptions; internal reason codes supplement but do not replace provider messages.

## Current implementation evidence

| Boundary | Inspected source | Existing capability |
|---|---|---|
| Durable state | `moda-interact-database/prisma/schema.prisma` | `ShopSettings`, `Conversation` version/claim/control fields |
| Text inbound | `moda-interact-background/src/services/conversation.service.ts` | Atomic message write/inbound-version update; pending-turn start |
| Audio inbound | `moda-interact-background/src/services/inbound-whatsapp-audio.service.ts` | Version increments at transcription completion |
| Worker | `moda-interact-background/src/services/conversation-turn-processor.service.ts` | `settleDelay`, versioned job IDs, BullMQ `moveToDelayed`, claim/release |
| Ownership | `moda-interact-background/src/services/recovery-conversation/ai-turn-ownership.service.ts` | Recovery, shop, controlMode/revision checks |
| Shopify control | `moda-interact/app/services/recoveries/recovery-human-commands.server.ts` | Atomic `controlRevision` increment |
| Woo control | `moda-interact-api/src/merchant/conversations/control/service.ts` | Authenticated control transition within transaction |
| Shopify settings | `app/routes/app/recovery-settings/*`, `app/routes/app/settings-save/route.ts` | Authenticated settings loader and save |
| Woo settings | `moda-interact-api/src/merchant/recovery-policy/*`, `moda-interact-woocommerce/includes/Rest/RecoveryPolicyController.php` | Hosted API + protected WordPress REST pattern |
| Human send | `moda-interact-api/src/merchant/conversations/messages/*` and Shopify human commands | Independent immediate durable HUMAN path |

## Exact durable model

`moda-interact-database/prisma/schema.prisma`:

```prisma
model ShopSettings {
  // add beside existing recovery settings; existing fields unchanged
  aiResponseDelayMinutes Int @default(0)
}

model Conversation {
  // nullable together; set once for a pending AI turn
  pendingAiNotBeforeAt      DateTime? @db.Timestamptz(3)
  pendingAiControlRevision  Int?
  pendingAiDelayMinutes     Int?

  @@index([pendingAiNotBeforeAt, id])
}
```

These are **fragments** to insert into the existing models; do not replace the models. Migration `20261031170000_arch054_merchant_ai_response_delay` adds the columns, DB CHECK for integer delay 0–30, nullable-triple consistency, nonnegative revision, and 0–30 pending delay. `pendingAiNotBeforeAt` must not be earlier than `pendingTurnStartedAt`. A complete/cleared turn has all pending-AI fields null. Existing standalone/HUMAN conversations may have no pending-AI fields. PostgreSQL is the authoritative clock/deadline and recovery of missing queue publications.

## Scheduling and concurrency contract

First processable inbound customer text / completed audio for an AI-controlled recovery conversation:

```text
inside the existing short inbound DB transaction:
  verify exact recovery -> shop binding
  lock/compare-and-set the conversation pending-turn opening
  read ShopSettings.aiResponseDelayMinutes (missing valid settings row => default 0)
  if AI and no pending turn:
    pendingTurnStartedAt = now
    pendingAiNotBeforeAt = now + delay * 60_000 ms
    pendingAiDelayMinutes = delay
    pendingAiControlRevision = CURRENT controlRevision
  persist inbound message/version and clocks atomically
commit; enqueue process-conversation-turn by the existing version-specific job ID
```

The pending timestamp and deadline are **not** recomputed on later messages, retries, duplicate webhooks, polling, tool calls, setting changes, or repair. For non-recovery conversations preserve the pre-ARCH-054 behaviour rather than fabricating shop ownership. When `controlMode=HUMAN`, persist customer messages but do not create or schedule AI work; mark the processed watermark accordingly to avoid replay after Resume AI. Existing audio transcription completion remains the processable-audio event (a `PENDING` audio blob alone is not a model prompt).

For valid AI pending turns, compute the due time:

```ts
const settleAtMs = Math.min(
  lastInboundAt.getTime() + quietWindowMs,
  pendingTurnStartedAt.getTime() + maxSettleWindowMs,
);
const eligibleAtMs = Math.max(settleAtMs, pendingAiNotBeforeAt.getTime());
const delayMs = Math.max(0, eligibleAtMs - nowMs);
```

Use real persisted values; do not substitute current settings after the turn started. The existing deterministic job ID (`conversation-turn__${conversationId}__${observedVersion}`) and BullMQ `moveToDelayed`/`DelayedError` remain authoritative for scheduling, **not** for send eligibility. When an old observed inbound version wakes, exit stale; the newest version's job inherits the same persisted deadline. The inexpensive claim/initial routing/moderation phase checks current mode, revision, pending version and processing lease. The **AGENT-only execution gate after routing classification** checks due time before reserve/model invocation; deterministic guidance is not delayed. A processing lease does not justify using a new control revision after takeover or resume. Redis is disposable; PostgreSQL must allow reconstruction of delayed jobs.

A Shopify or Woo `AI→HUMAN` transition commits **one atomic DB change**: increment control revision, set HUMAN, clear all pending-AI metadata and pending-turn start, advance `lastProcessedVersion` to the current inbound version, and clear any stale processing lease (without causing an already-dispatched provider request to be recalled). `HUMAN→AI` also clears obsolete pending state; only subsequent customer messages open new AI turns under the new control revision. Provider-send checks continue to re-evaluate the original revision and inbound version. If human takeover commits before final dispatch admission, the AI send is suppressed; if the provider request is already in flight, it cannot be recalled.

Because some old queued jobs may still arrive, **every** read, claim and outbound send checks the durable state; cancellation/removal of queued jobs is an optional performance optimisation, never a correctness gate. Use bounded, batched, keyset-paged pending-turn repair on the existing messaging worker process to re-enqueue missing/overdue jobs; no process sleeps and no unbounded scan. No HOT-path lookup of the setting for duplicate messages or non-actionable webhook events.

## Shared API contract (v1 only)

Shared published entrypoint: `@modainteract/moda-interact-shared/ai-response-delay` (new `src/ai-response-delay.ts`, package exports AND `tsup.config.ts` entry). The owner defines strict Zod schemas and inferred types. `AiResponseDelayMinutesSchema` is `z.number().int().min(0).max(30)`; `AiResponseDelayRevisionSchema` accepts `UNCONFIGURED` or an ISO millisecond UTC timestamp. `MerchantAiResponseDelayReadV1Schema` is exactly `{schemaVersion:1, revision, aiResponseDelayMinutes}`; `MerchantAiResponseDelayWriteV1Schema` is exactly `{schemaVersion:1, expectedRevision, aiResponseDelayMinutes}`. Both are strict; there is no `v2`, no independent business policy in Zod, and no mutable conversation turn field in the merchant-facing wire contract.

```json
{ "schemaVersion": 1, "expectedRevision": "UNCONFIGURED", "aiResponseDelayMinutes": 7 }
```

```json
{ "schemaVersion": 1, "revision": "2026-10-31T16:28:55.123Z", "aiResponseDelayMinutes": 7 }
```

Woo hosted API route: `GET/PUT /v1/merchant/ai-response-delay` with the existing authenticated Woo installation principal; WordPress proxy: `GET/PUT /wp-json/moda-interact/v1/merchant/ai-response-delay`. Shopify uses its existing authenticated `/app/recovery-settings` UI and `settings-save` action with a distinct `ai-response-delay` intent; it does not call the Woo hosted API. The stored configuration is one `ShopSettings` row per shop, not a new per-platform setting. `revision` is the current settings `updatedAt` or `UNCONFIGURED` where a valid Woo shop has no settings row; writes take the existing Shop row lock, use optimistic revision checking, advance `updatedAt` monotonically, and reject invalid requests without mutating other settings.

## Repository ownership and dependency order

- Database: schema and migration of shop policy + pending AI deadline.
- Shared: wire schemas/types and **separate** publication/release gate before cross-repository consumers.
- Background: deterministic pending capture for text/audio; delay/turn claim/final admission; bounded repair and observability. Continue using the existing `whatsapp-events` queue and messaging deployment.
- API: separate authenticated Woo policy boundary and existing Woo control-transition invalidation.
- Shopify: settings UI/action and existing Shopify control-transition invalidation.
- WooCommerce: authenticated PHP proxy, JS settings controller/UI and tests, with no direct DB/Redis access.
- System test: terminal integrated and concurrency/repair tests, after all required implementations and publication. No repository implementation task depends on system tests.
- Gateway/Admin: no new service or Admin runtime setting. Existing quiet-window Admin control remains separate; no new gateway task unless observed deployments demonstrate a concrete missing capability.

## Security, failure, testing and observability

Use shop ownership from `CheckoutRecovery.shopId` on recovery conversations. Do not authorise from nullable `Conversation.shopId`, phone number, last merchant contacted, or merchant-controlled URL. The Hosted API rechecks Woo installation credentials/site bindings, and Shopify uses the existing authenticated shop session. Response settings are read with no-store headers. Cache/retry or a missing settings row cannot silently select a different shop's delay.

Log structured, redacted correlation (`shopId`, `conversationId`, original control revision, due timestamp, version, outcome, time waited, queue lag) through Shared logger; preserve originating SDK/Prisma errors and exception causes. Do not log message bodies, phone numbers, credentials or unredacted provider payloads. Existing framework/BullMQ metrics should be reused; a custom domain event is justified only for distinct delayed-turn scheduling/eligibility/repaired/suppressed outcomes.

Tests must cover 0,1,7,30; reject -1,31,0.5,string/null; text and audio; follow-up customer fragments; early and late jobs; timeout/retries; config changes during pending turn; H→AI→H cycles and rapid control toggles; duplicate provider webhook and job; different merchants sharing the same WhatsApp sender and customer phone; immediate HUMAN dispatch; API tampering; Redis downtime/repair; 10,000 delayed turns with 0 occupied waiting workers; exact provider admission race. No exact-once assumption.

## Rollout / rollback

Database migration → Shared implementation acceptance → Shared publication → API + Shopify/Woo settings and control-fence changes, and Background capture/processor/repair → developer manual validation → terminal system tests. Until the Background consumer and both control-fence writers are deployed, do not enable nonzero delay in test/production merchant settings. Explicitly reconcile old pending turns and queued jobs at deployment; no implicit rollout to existing messages. Reverting after nonzero pending turn creation requires draining or safely invalidating them, not merely downgrading the merchant setting. Default 0 retains the pre-feature behaviour.

## Decisions / task graph

| Task | Owner | Current status | Depends on |
|---|---|---|---|
| ARCH-054-DATABASE-001 | moda_database | Complete | — |
| ARCH-054-SHARED-001 | moda_shared | Complete | — |
| ARCH-054-SHARED-002 | moda_shared | Complete | SHARED-001 |
| ARCH-054-BACKGROUND-001 | moda_background | Ready | DATABASE-001 |
| ARCH-054-BACKGROUND-002 | moda_background | Pending | BACKGROUND-001, API-002, SHOPIFY-002 |
| ARCH-054-BACKGROUND-003 | moda_background | Pending | BACKGROUND-002 |
| ARCH-054-API-001 | moda_api | Ready | DATABASE-001, SHARED-002 |
| ARCH-054-API-002 | moda_api | Complete | DATABASE-001 |
| ARCH-054-SHOPIFY-001 | moda_app | Complete | DATABASE-001, SHARED-002 |
| ARCH-054-SHOPIFY-002 | moda_app | Complete | DATABASE-001 |
| ARCH-054-WOOCOMMERCE-001 | moda_woocommerce | Pending | API-001 |
| ARCH-054-SYSTEM-TEST-001 | moda_system_test | Pending | all implementation/release tasks |
| ARCH-054-SYSTEM-TEST-002 | moda_system_test | Pending | SYSTEM-TEST-001, BACKGROUND-003 |

## Open questions

None blocking task definition. Whether to add optional merchant notifications for new customer messages is a separate notification feature and is not part of the response-delay correctness contract.

## Change history

- 2026-10-31: Initial ARCH-054 definition, split from ARCH-040/ARCH-052; integer 0–30 merchant delay, zero additional delay for human replies, persisted deadline and takeover fencing.
- 2026-11-01: Accepted ARCH-054-SHOPIFY-002 at Attempt 2 after the disposable PostgreSQL transaction suite passed all three required cases. BACKGROUND-002 remains Pending because BACKGROUND-001 is Ready, not Complete; no downstream task became newly eligible.
