---
id: ARCH-034
title: WhatsApp webhook ingress route maintainability refactor
status: in_progress
coordinator: moda_architect
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-034: WhatsApp webhook ingress route maintainability refactor

## Status

In Progress. MESSAGING-001 (normalizers), MESSAGING-002 (Meta verification-token/HMAC) and MESSAGING-003 (deterministic BullMQ identity/publication) are architect-accepted through the developer-managed patch workflow, with non-launcher execution deviations recorded in their task reports. MESSAGING-003 reduced the route from 243 to 185 lines and introduced independently testable 24-line identity and 47-line publication modules. The developer reports all requested unit/typecheck/build checks passing and supplied live disposable Docker Redis telemetry evidence (2/2 PASS, no skips). MESSAGING-004 is now architect-accepted Complete following the developer-confirmed green validation. MESSAGING-005 is Ready; system testing remains Pending.

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
7. **After** the behaviour-preserving extraction, harden the authenticated webhook acceptance boundary: invalid structure or invalid inbound messages must be rejected before *any* queue publication for that HTTP request.

## Non-goals

- **For extraction tasks MESSAGING-001 through -004:** changing what Meta webhook events are accepted, ignored, rejected or acknowledged.
- **For extraction tasks MESSAGING-001 through -004:** redesigning malformed top-level webhook payload handling or fixing **existing partial enqueue before a later 400**. These are intentionally deferred to MESSAGING-005, after the pure extraction is accepted.
- **For MESSAGING-005:** changing valid provider-status/inbound contract interpretation, legitimate accepted event behaviour, or existing queue delivery/failure guarantees beyond pre-publication rejection of invalid authenticated payloads.
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

The known possibility of **some jobs being enqueued before a later invalid inbound event returns 400** remains deliberately unchanged in MESSAGING-001 through -004; it is addressed by the separately sequenced **MESSAGING-005** task once the extraction is accepted.

### Post-refactor hardening policy — MESSAGING-005

The hardening task introduces an intentional **authenticated-request validation** change, not a billing or queue contract change:

1. Verify HMAC on the exact raw body, then parse JSON as before. Invalid JSON remains `400` / `invalid_json`.
2. Validate the parsed Meta envelope shape before publication: root must be a non-array object with an `entry` array (empty allowed); each entry and change must be non-array objects; absent/null `changes` and `messages`/`statuses` collections remain empty where legacy code treated them that way; present non-null collections must be arrays; a `messages` field change requires a non-array object `value`.
3. Ignore non-`messages` changes as before. Continue to ignore invalid **individual** provider statuses as before. Any invalid inbound message or malformed relevant envelope returns `400` / `invalid_payload` without publishing *any* job from that HTTP request. An absent/malformed `entry` now receives a deliberate `400` instead of an accidental `200`/`500`.
4. Implement a **pure whole-webhook preflight** that stages valid normalized events in existing entry/change, messages-before-statuses order. Only after the entire request has passed preflight may publication begin; publish sequentially through the unchanged BullMQ producer.
5. A queue or Redis failure **after publication begins** can still leave earlier jobs accepted and cause a `500`/retry. Do not claim cross-job atomicity; preserve deterministic job IDs, consumer idempotency and existing retry/backoff behaviour. No PostgreSQL outbox, new durable receipt, or distributed transaction is introduced in this bounded task.
6. Preflight must be linear-time with no new database/provider round trips; stage only bounded Shared-normalized event objects, not copies of raw bodies/error payloads. Preserve existing telemetry reason vocabulary and signed-request security.

This explicit behaviour change is scoped to malformed authenticated requests. Valid signed traffic, v1/v3 message/status contracts, GET verification, queue identities and publication ordering are unchanged.

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

MESSAGING-001 through -004 are a **compatibility-preserving refactor**; MESSAGING-005 is an **explicit post-refactor hardening change** for malformed authenticated requests, with the accepted/rejected response matrix above as its approval boundary. Neither tranche requires a database migration, Shared publication, queue drain, contract-version bump, new environment variable or coordinated Background rollout. The provider-status v3 release remains in effect. Validate each extraction before beginning the next; validate the completed hardening with real signed HTTP + queue-boundary evidence before the terminal system-test task. Do not silently extend the hardening into queue atomicity or unrelated event interpretation.

Existing architecture-level Messaging system tests should be reused. Independent end-to-end customer scenarios are BLACK_BOX only when validated at the supported external/Meta emulator boundary; queue/status ingress checks without an externally observable outcome remain INTEGRATION evidence and must **not** be claimed as completion of the existing planned `MESSAGING-STATUS-001` BLACK_BOX requirement.

## Decisions / Tasks

| Task | Owner | Status | Depends On |
|---|---|---|---|
| `ARCH-034-MESSAGING-001` — Extract pure WhatsApp normalizers | `moda_messaging` | Complete — Accepted Attempt 1 | `ARCH-028-MESSAGING-001` (Complete) |
| `ARCH-034-MESSAGING-002` — Isolate Meta webhook authentication | `moda_messaging` | Complete — Accepted Attempt 1 | `ARCH-034-MESSAGING-001` (Complete) |
| `ARCH-034-MESSAGING-003` — Extract BullMQ publication and job identity | `moda_messaging` | Complete — Accepted manual patch iteration 2 | `ARCH-034-MESSAGING-002` (Complete) |
| `ARCH-034-MESSAGING-004` — Extract webhook dispatch and slim the route | `moda_messaging` | Complete — Accepted Attempt 1 | `ARCH-034-MESSAGING-003` (Complete) |
| `ARCH-034-MESSAGING-005` — Reject invalid signed webhooks before publication | `moda_messaging` | Ready | `ARCH-034-MESSAGING-004` |
| `ARCH-034-SYSTEM-TEST-001` — Verify ingress refactor and rejection hardening | `moda_system_test` | Pending | `ARCH-034-MESSAGING-005` |

System test is **terminal**: no implementation task depends upon it. The developer may validate the finished Messaging implementation manually before invoking the Ready system-test task.

## Open questions

No unresolved question blocks the behaviour-preserving extraction. The requested bounded malformed-payload/pre-publication hardening has now been agreed as `ARCH-034-MESSAGING-005` with its response, preflight and queue-failure boundaries above. Any later request for true cross-job atomic publication would require separate architecture and durable-acceptance design.

## Change history

- 2026-10-11: Established ARCH-034 as a separate Messaging maintainability initiative after ARCH-028 producer acceptance and integration; authored portable task definitions without `_index.md` changes.
- 2026-10-11: Added sequential `ARCH-034-MESSAGING-005` for explicit malformed-envelope and no-partial-publication-on-rejection hardening **after** MESSAGING-004. System-test dependency and scope now include the hardening acceptance matrix. No `_index.md` changes or task worktree/branch operations are claimed.
- 2026-10-11: Reviewed the manually applied MESSAGING-001 normalization extraction: route 467 -> 288 lines, three new pure modules (63/111/10), full unit suite 42 pass / 0 fail / 1 Redis-conditional skip, TypeScript and client/SSR builds PASS. Recorded developer manual-main-checkout policy deviation without fabricating worktree/commit evidence; marked MESSAGING-001 Complete and MESSAGING-002 Ready.
- 2026-10-11: Reviewed MESSAGING-002: extracted Meta verification token and raw-body HMAC to a 48-line `.server.ts` module; route 288 -> 243 lines; ten targeted tests added. Developer reported all required validation passing without attached logs. Recorded retrospective manual-checkout policy deviation; accepted Attempt 1 and promoted MESSAGING-003 to Ready.
- 2026-10-11: Accepted MESSAGING-003 after two developer-applied patch deliveries: pure deterministic job-ID helper (24 lines), BullMQ publisher (47), route 243 -> 185 lines, six publisher tests and a 69-line disposable-Redis runner. Developer confirmed all requested unit/typecheck/build checks passed and supplied live Redis integration output 2/2 PASS with no skip. Manual-main execution deviation recorded; promoted MESSAGING-004 to Ready without touching domain indexes.

- 2026-10-11: Accepted manually applied MESSAGING-004 after the developer confirmed all local tests, typecheck and build green. Extracted a focused 60-line dispatcher and reduced the route to 138 lines while explicitly preserving known malformed-envelope/partial-publication behaviour; recorded manual-checkout execution deviation. Promoted MESSAGING-005 to Ready, leaving the terminal system test Pending. No `_index.md` changes.
