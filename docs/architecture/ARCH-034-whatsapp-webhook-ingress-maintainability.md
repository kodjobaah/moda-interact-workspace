---
id: ARCH-034
title: WhatsApp webhook ingress route maintainability refactor
status: agreed
coordinator: moda_architect
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-034: WhatsApp webhook ingress route maintainability refactor

## Status

Agreed for task definition. **Portable definitions only; no branch/worktree materialisation or implementation has occurred in this architecture handoff.**

## Problem

After `ARCH-028-MESSAGING-001` was accepted and merged, `moda-interact-messaging/app/routes/whatsapp.tsx` remains a **467-physical-line** React Router module with roughly 18 functions. Inspected on 2026-10-11 on Messaging `main` (file Git blob `b8000b2c5722ebabf4b877dcffce1c74e50dbaff`). It combines:

- GET verification and POST HTTP response/telemetry orchestration;
- raw-body HMAC signature verification and environment-secret retrieval;
- trusted-identity extraction, inbound text/audio/reply normalization;
- Meta provider-status v3, bounded failure-code and pricing normalization;
- BullMQ producer calls, retry options, deterministic inbound/status job identity;
- iteration and short-circuit decisions over a webhook's entries and changes.

These concerns have different test and failure boundaries. Pure parsing currently requires importing a route module with server/queue imports, and queue/authentication changes risk unrelated normalization regressions.

The current Messaging repo declares `npm test`, `npm run typecheck`, and `npm run build`; its tests include `tests/whatsapp-provider-status.test.mjs`, `tests/whatsapp-inbound-normalization.test.mjs`, `tests/whatsapp-ingress-telemetry.test.mjs`, and Redis-conditional `tests/whatsapp-queue-telemetry.test.mjs`. The route-normalization helper exports are consumed inside this repository's own tests, not by another observed application module.

## Goals

1. Make the existing WhatsApp route a small HTTP/authenticated-ingress composition boundary (target at most 150 physical lines).
2. Place pure inbound and provider-status normalization in cohesive, independently testable modules.
3. Separate Meta verification, deterministic job identities, BullMQ publication, and authenticated webhook iteration.
4. Preserve every existing externally observable behaviour and published queue contract, including ARCH-028 v3 failure-evidence semantics.
5. Keep new production modules focused (target no more than 200 physical lines; hard maximum 300). Avoid a replacement catch-all dispatcher.
6. Retain and strengthen focused, route-level and independent system-test evidence without weakening existing assertions.

## Non-goals

- Changing what Meta webhook events are accepted, ignored, rejected or acknowledged.
- Redesigning malformed top-level webhook payload handling or fixing **existing partial enqueue before a later 400**. Both require separately agreed behaviour/security/error semantics and separate follow-up tasks.
- Changing HTTP route URLs, HMAC algorithm, Shopify/Meta secrets, provider identities, or logging of sensitive payloads.
- Changing BullMQ queue/job names, attempts/backoff, idempotency keys, payloads, retry/deduplication semantics or database state.
- Changing v3 failure-code bounds, first-valid-evidence selection, identity/timestamp/pricing normalization, or inbound text/audio/context semantics.
- New database migrations, Shared schema/package publication, Background provider policy, Commerce/Shopify implementation, new infrastructure or new observability frameworks.
- Broad file-formatting, unrelated cleanup, dependency upgrades or restructuring unrelated Messaging routes.

## Inspected current architecture

`app/routes.ts` maps `webhook/whatsapp` to `app/routes/whatsapp.tsx`. The exported `loader` handles Meta GET challenge; `action` accepts signed POST body, parses JSON, iterates `entry[].changes[]` of field `messages`, publishes inbound events and status jobs, and observes its outcome with `recordWhatsAppIngressTelemetry`.

Canonical incoming contracts:

- `@modainteract/moda-interact-shared/whatsapp`: `safeParseNormalizedWhatsAppInboundMessage` (v1).
- `@modainteract/moda-interact-shared/billing`: `safeParseNormalizedWhatsAppStatus`, `WHATSAPP_PROVIDER_STATUS_SCHEMA_VERSION` (currently v3).
- Messaging currently pins `@modainteract/moda-interact-shared@1.3.1` exactly. Preserve the published dependency rather than copying Shared validators.

Transport: existing `whatsapp-events` BullMQ producer via `app/lib/queues/whatsapp.queue.ts`, job names `message-received` and `message-status`. An inbound job ID is SHA-256 of provider message ID with `wa-` prefix. Status IDs use `ws-` plus a bounded deterministic hash of provider account, phone number, message ID and status, with normalized failure code included for evidence-bearing FAILED v3 only. Producer attempts=3 and exponential backoff delay=1000ms. The existing queue adapter already owns Redis connectivity and shared BullMQ observability.

## Proposed architecture

```text
app/routes/whatsapp.tsx                       # exported GET loader + POST action, responses/telemetry
    |
    +-- app/lib/whatsapp/webhook-auth.server.ts   # verify GET token and POST raw-body HMAC
    +-- app/lib/whatsapp/webhook-dispatch.server.ts # authenticated JSON event traversal/order
    |      +-- inbound-message-normalizer.ts      # Shared inbound v1 validation
    |      +-- provider-status-normalizer.ts       # Shared provider-status v3 validation
    |      +-- whatsapp-job-publisher.server.ts    # existing queue producer
    |             +-- job-identity.server.ts       # existing deterministic identities
    +-- app/lib/whatsapp/normalization-utils.ts  # narrow pure shared parsing primitives

app/lib/queues/whatsapp.queue.ts            # unchanged canonical queue/telemetry adapter
app/lib/observability/whatsapp-ingress-telemetry.ts # unchanged semantic telemetry
```

These are proposed responsibilities, not a mandate for monolithic implementation files or a second generic framework. The assigned agent may use a tighter module split if each responsibility remains explicit and tests stay focused.

The route is **not** a public TypeScript API. Its only required React Router exports are `loader` and `action`; current test-only helper imports may move to their new owning modules when assertions are preserved. Do not alter `app/routes.ts` or the URL.

## Request, event, ordering and durable-state boundaries

1. For POST, preserve method check and raw-body retrieval; verify `x-hub-signature-256` using the exact body before parsing or publishing anything.
2. Preserve JSON parse failure response, traversal order (each entry; each `messages` change; messages before statuses), invalid inbound rejection, and invalid provider-status ignore behaviour.
3. Normalize only via the published Shared runtime schemas; do not reconstruct local service contracts.
4. Publish through existing BullMQ queue with the same job data, job ID, attempts/backoff, and errors/retry propagation. Do not move business relevance filtering into the HTTP request.
5. Return the same acknowledgement/verification responses and existing telemetry observations; failures after publication and duplicate Meta delivery must retain current semantics.
6. PostgreSQL durable processing, delayed jobs and customer/conversation ordering remain with Background. No transaction or schema changes occur here.

The known possibility of **some jobs being enqueued before a later invalid inbound event returns 400** is deliberately documented, not newly declared correct. A future error/acceptance redesign must specify all-or-nothing vs partial acceptance and retry safety before changing it.

## Interfaces / contracts / security

- Contract producer: `moda-interact-messaging`; existing consumers: Background.
- Contract owner: `moda-interact-shared`; consume published `/whatsapp` and `/billing` exports only.
- Runtime validation: current Shared safe-parse methods; strict, bounded v3 failure evidence only on FAILED.
- HMAC: SHA-256 of **raw** body against server-side `META_APP_SECRET`, constant-time comparison; preserve absent-secret fail-closed behaviour.
- GET verification uses `WHATSAPP_VERIFY_TOKEN` and the existing `hub.*` query parameters.
- No tenant/shop lookup, raw body, full Meta error text, secrets, customer content, access tokens or authorization headers in newly emitted logs/metrics/traces.
- Existing shared structured logging/OTel infrastructure remains canonical; do not add a competing logger or duplicate generic request metrics.

## Failure, scalability and observability

Keep the ingress minimal: verify, normalize, enqueue, acknowledge; no synchronous external billing, LLM, Meta API or database requests. Do not change queue fan-out for duplicate and unrelated entries. Preserve request/queue failure isolation and bounded error responses. Existing `recordWhatsAppIngressTelemetry` is the only route semantic telemetry emitter; shared BullMQ adapter is left intact. No new Gateway, Database, Shared or deployment implementation is justified.

## Rollout and validation

Classify this as a **compatibility-preserving refactor**. It does not require a database migration, new package publication, queue drain, contract-version bump, new environment variable, or coordinated Background rollout. The provider status v3 release remains in effect. Validate each extraction before beginning the next, and verify the final built HTTP endpoint and BullMQ outputs against known behaviour. If work reveals that an observable behaviour must change, stop and refer it to `moda_architect` rather than hiding the change in a refactor.

Existing architecture-level Messaging system tests should be reused. Independent end-to-end customer scenarios are BLACK_BOX only when validated at the supported external/Meta emulator boundary; queue/status ingress checks without an externally observable outcome remain INTEGRATION evidence and must **not** be claimed as completion of the existing planned `MESSAGING-STATUS-001` BLACK_BOX requirement.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| `ARCH-034-MESSAGING-001` — Extract pure WhatsApp normalizers | `moda_messaging` | Ready (defined, not materialised) | `ARCH-028-MESSAGING-001` (Complete) |
| `ARCH-034-MESSAGING-002` — Isolate Meta webhook authentication | `moda_messaging` | Pending | `ARCH-034-MESSAGING-001` |
| `ARCH-034-MESSAGING-003` — Extract BullMQ publication and job identity | `moda_messaging` | Pending | `ARCH-034-MESSAGING-002` |
| `ARCH-034-MESSAGING-004` — Extract webhook dispatch and slim the route | `moda_messaging` | Pending | `ARCH-034-MESSAGING-003` |
| `ARCH-034-SYSTEM-TEST-001` — Verify signed WhatsApp ingress parity | `moda_system_test` | Pending | `ARCH-034-MESSAGING-004` |

System test is **terminal**: no implementation task depends upon it. The developer may validate the finished Messaging implementation manually before invoking the Ready system-test task.

## Open questions

No unresolved question blocks the behaviour-preserving extraction. Future malformed-payload handling and all-or-nothing vs partial enqueue policy should be designed as a separate initiative or bounded correction after agreement; they are not part of these tasks.

## Change history

- 2026-10-11: Established ARCH-034 as a separate Messaging maintainability initiative after ARCH-028 producer acceptance and integration; authored portable task definitions without `_index.md` changes.
