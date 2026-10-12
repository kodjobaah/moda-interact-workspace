---
id: ARCH-034-MESSAGING-005
architecture_id: ARCH-034
title: Validate signed WhatsApp webhook batches before publication
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 60
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-034-MESSAGING-004"]
enables: ["ARCH-034-SYSTEM-TEST-001"]
created: 2026-10-11
updated: 2026-10-12
---

# Validate signed WhatsApp webhook batches before publication

## Architecture

Architecture ID: `ARCH-034`.

Architecture document: `docs/architecture/ARCH-034-whatsapp-webhook-ingress-maintainability.md`.

Coordinator: `moda_architect`.

## Objective

Ensure an authenticated WhatsApp webhook containing a malformed envelope or any invalid inbound message is rejected with a controlled `400` **before** the request publishes a queue job, while preserving valid v1/v3 event behaviour and the existing publication/retry contract.

## Context

In the inspected pre-refactor `app/routes/whatsapp.tsx`, `JSON.parse(rawBody)` is followed by unchecked traversal of `payload.entry`, `entry.changes`, `change.value.messages` and `change.value.statuses`. A syntactically valid JSON object with a wrong shape can throw into the processing-error path and become `500` instead of a controlled `400`.

Publication currently happens during traversal: a valid inbound message or provider status may be queued before a **later invalid inbound message** returns `400` for the same request. Meta may retry that rejected webhook. Job IDs already provide deterministic deduplication, but earlier side effects should not precede deliberate rejection of a malformed authenticated batch.

`ARCH-034-MESSAGING-001` through `-004` deliberately extract the route without changing these behaviours. This task is the subsequent, explicitly approved **hardening stage**, not part of the behaviour-preserving refactor. Run it only on the accepted post-MESSAGING-004 implementation.

## Scope

- In `moda-interact-messaging`, use the extracted dispatcher and pure inbound/status normalizers to add a focused, **side-effect-free whole-webhook preflight**; do not re-create a >300-line route or dispatcher.
- Validate the authenticated parsed envelope's structural shape and normalize every relevant inbound message and valid provider status before the first publisher call.
- Stage only canonical Shared-normalized events in the legacy entry/change order, with inbound messages before statuses per `messages` change. Publish those events sequentially through the existing publisher only when the full preflight succeeds.
- Return controlled `400` with existing `invalid_payload` ingress telemetry for malformed signed envelopes and invalid inbound messages anywhere in the request. Invalid JSON remains `400` with `invalid_json`; missing/bad HMAC remains `401` before parsing and staging.
- Add focused unit, route/dispatcher and queue-publication regression tests for the malformed/retry cases below. Use injected bounded publisher stubs or disposable Redis; avoid production infrastructure and test-only global queue replacements.

## Out of Scope

- Database changes, a transactional outbox, queue transactions, or a claim that multiple BullMQ `add()` calls are atomic.
- Changing valid v1 inbound or v3 provider-status schemas, failure evidence, deterministic IDs, queue/job names, retry/backoff, or Background idempotent processing.
- Treating an invalid **individual provider status** as a malformed webhook; preserve current ignore-and-continue policy for such statuses.
- Rejecting previously ignored non-`messages` changes, unrelated Meta fields, or well-formed empty arrays; do not create a new business-content filter at ingress.
- New Shopify/Commerce/Meta API calls, tenant lookups, cross-service contracts, dependencies, secrets, generic observability mechanisms, or substantial unrelated refactoring.
- Resolving queue-outage partial publication beyond the current idempotent retry contract.

## Requirements

### R1 — Authentication and explicit response matrix

Preserve HTTP method checks, GET challenge verification, signature verification against the **exact raw POST body** and all currently supported successful payloads. Use the existing route response and bounded telemetry mechanisms:

| Input | Required outcome | Queue publication |
|---|---|---|
| Non-POST action method | Existing `405` | None |
| Missing/invalid HMAC | Existing `401` | None |
| Invalid JSON syntax with valid HMAC | Existing `400` / `invalid_json` | None |
| Authenticated JSON with invalid relevant envelope shape | `400` / `invalid_payload` (never incidental `500`) | None |
| Signed batch with one or more invalid inbound messages, including one *after* valid events | `400` / `invalid_payload` | **None from the entire request** |
| Valid signed batch, including empty arrays and non-`messages` changes | Existing `200 EVENT_RECEIVED` | Same validated events in original order |
| Structurally valid individual invalid provider status | Continue to ignore it, without rejecting otherwise-valid events | None for that status |
| Publisher/Redis failure after preflight succeeds | Preserve exception/`500` and retry semantics | May be partial; no atomicity claim |

### R2 — Envelope shape without over-rejection

Treat parsed JSON as `unknown`, not trusted `any`. At minimum:

- Root must be a non-null, non-array object with an `entry` **array**; an empty array remains valid, while absent/non-array `entry` is `invalid_payload`.
- Each `entry` and each `change` must be a non-null, non-array object. `changes` omitted or null retains current empty/no-op behaviour; a present non-null `changes` value must be an array.
- Ignore changes whose `field` is not `messages`, as today. For a `messages` change, `value` must be a non-null, non-array object.
- `value.messages` and `value.statuses` may be omitted/null (existing empty/no-op behaviour); when present and non-null they must be arrays.
- Validly structured but invalid inbound message elements fail preflight. Invalid provider-status elements continue to normalize to null and are skipped; they do not invalidate the whole request.
- Extra Meta fields not consumed by the accepted contracts must not become new rejection reasons.

### R3 — Preflight before **any** side effect

- Fully traverse/validate and normalize *all* events in the signed request before invoking the publisher even once; no Redis, queue, database or external request during preflight.
- Preflight returns either a discriminated invalid-payload result or an ordered list of the existing canonical inbound v1 / provider-status v3 events.
- Preserve the exact old event order within and across entries, `changes`, inbound messages and statuses, and preserve invalid individual status skip behaviour.
- On preflight failure, discard staged normalized events and return controlled `400` with **zero** queue jobs, including when an earlier valid status preceded a later invalid inbound message.
- Only after successful preflight, publish sequentially through the existing publisher; no parallel enqueue or additional derived identities. Preflight stays linear in event count and stores normalized bounded event data rather than raw webhook/error copies.

### R4 — Queue failure, retry and observability boundaries

- Publisher failure after successful preflight may still leave earlier jobs enqueued. Preserve propagation and the existing `processing_error` telemetry, `500` response semantics and Meta retries; deterministic job IDs/consumer idempotency remain the recovery mechanism.
- Do not add a PostgreSQL outbox, global mutex, additional Redis operations, or a second queue to approximate atomicity.
- Preserve existing semantic ingress telemetry reason vocabulary and the approved shared instrumentation. Never log raw webhook bodies, Meta error details, secrets, customer messages or unnecessary customer metadata.

### R5 — Maintainability and testability

- Build on the accepted modular `-001` through `-004` decomposition; keep the route <=150 physical lines when practical and all new/expanded production modules <=300 physical lines (target <=200).
- Use focused pure preflight and small publishing/orchestration seams; do not rebuild a monolithic dispatcher or create competing Meta/Shared schemas.
- If the accepted -004 implementation requires a materially different design or this behaviour would conflict with another active task, stop and return the issue to `moda_architect` before code changes.

## Work Items

- [x] Verify MESSAGING-004 is architect-accepted `complete` and inspect its actual extracted dispatcher and publisher APIs before implementation.
- [x] Add narrow envelope shape validation and whole-batch event preflight, preserving accepted no-op/skip cases.
- [x] Ensure no publication occurs before all relevant inbound messages are valid; preserve existing sequential queue publication afterwards.
- [x] Add focused invalid JSON/envelope/mixed-late-invalid and valid mixed-v3 regression tests with exact status, telemetry and zero-publication assertions.
- [x] Test queue failure after preflight as a **non-atomic** publication boundary and assert unchanged idempotent retry/job identity.
- [x] Run the declared repository validation and record changed file sizes, security/telemetry findings and Completion Report.

## Interfaces / Contracts

Producer: `moda-interact-messaging`, using the accepted `ARCH-034-MESSAGING-004` dispatcher, `-001` normalizers and `-003` publisher.

Contracts: published `@modainteract/moda-interact-shared/whatsapp` inbound v1 and `/billing` provider-status v3. No new Shared export or schema version.

Transport: existing `whatsapp-events` BullMQ queue, `message-received` and `message-status` job names, unchanged deterministic IDs and retries. Background remains the owner of durable processing/idempotency.

Route: existing GET/POST `/webhook/whatsapp` and `recordWhatsAppIngressTelemetry`, preserving existing reason vocabulary.

## Dependencies

- `ARCH-034-MESSAGING-004`

## Enables

- `ARCH-034-SYSTEM-TEST-001` — terminal validation after the hardening implementation is architect-accepted Complete.

## Acceptance Criteria

- [x] Valid JSON with invalid envelope shapes is rejected deterministically as `400`, not an incidental `500`, without queue publication.
- [x] Late invalid inbound message in a signed mixed batch causes `400 invalid_payload` with **zero** enqueued jobs from that request.
- [x] Valid signed event batches preserve byte-compatible normalized queue payloads, deterministic job IDs and original publish ordering.
- [x] Invalid individual provider statuses remain ignored without rejecting otherwise-valid batches; extra Meta fields and non-`messages` changes are accepted/ignored as before.
- [x] Existing GET, HMAC verification, invalid JSON, 405, 401 and valid 200 response/telemetry behaviour remains intact.
- [x] Queue failure after publication starts retains retry/500 semantics and is **not** misrepresented as an atomic queue transaction.
- [x] No sensitive provider/customer payloads introduced into logs/traces or tests; no new database/Shared/Gateway implementation.
- [x] No new production file exceeds 300 physical lines and no all-purpose route/dispatcher regression.

## Validation

Inspect the current Messaging `package.json` and use its actual scripts, not inferred commands. In the reviewed baseline these were available:

- [x] Focused webhook route/dispatcher/preflight tests (test filenames from MESSAGING-004 and new focused tests).
- [x] `node --import tsx --test tests/whatsapp-inbound-normalization.test.mjs tests/whatsapp-provider-status.test.mjs`
- [x] `node --import tsx --test tests/whatsapp-ingress-telemetry.test.mjs`
- [x] Publisher/queue tests for zero-publication-on-rejection and partial-publisher-failure retry (synthetic queue stub or disposable Redis only).
- [x] `npm test`
- [x] `npm run typecheck`
- [x] `npm run build`
- [x] `git diff --check`
- [x] Record source line counts and confirm no new production module exceeds 300 physical lines.

## Stop Condition

After the specified Work Items, Acceptance Criteria and Validation pass, update only this task's execution state/Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not begin the dependent system test. Use the launcher-created mirrored task branch/worktrees, not a shared/default checkout.

## Implementation Notes

Do not attempt to make multi-job BullMQ publication transactional. The key guarantee in this task is **zero publication when the request is rejected by preflight**. A `500` after a publisher error may still follow partial acceptance; retries remain idempotent via existing IDs. Use a single preflight pass over the authenticated object; do not run an additional deep serializer or broaden Meta schema interpretation beyond the bounded shape contract.

## Completion Report

### Status

Ready for Review — retrospective developer-applied Attempt 1, architect-accepted on 2026-10-12.

### Files Changed

Production (3):

- `app/lib/whatsapp/webhook-preflight.ts` (new; 58 lines)
- `app/lib/whatsapp/webhook-dispatch.server.ts` (updated; 34 lines)
- `app/routes/whatsapp.tsx` (updated; 138 lines)

Focused tests (4):

- `tests/whatsapp-webhook-preflight.test.mjs` (new)
- `tests/whatsapp-webhook-preflight-telemetry.test.mjs` (new)
- `tests/whatsapp-webhook-dispatch.test.mjs` (updated)
- `tests/whatsapp-webhook-route.test.mjs` (updated)

No schema, Shared package, Gateway, queue adapter or deployment configuration was changed.

### Work Completed

- Added side-effect-free `preflightWhatsAppWebhook(payload: unknown)`, enforcing the bounded Meta envelope shape after raw-body HMAC verification and before any BullMQ publication. An invalid relevant envelope or inbound v1 event anywhere in a batch yields `invalid_payload` / HTTP 400 with **zero jobs from that request**.
- Preserved original entry/change ordering, messages-before-statuses ordering, Shared inbound v1/provider-status v3 normalization, the existing ignore-invalid-individual-status rule, and ignored unrelated Meta fields and non-`messages` changes.
- Updated the dispatcher to stage canonical normalized events and publish them sequentially only after preflight succeeds; the route now treats parsed JSON as `unknown`.
- Kept publisher failure separate from preflight rejection: a queue error can still follow earlier successful publication and causes an exception/processing-error path (500 and retry); no false multi-job atomicity guarantee.
- Added signed route, pure preflight, dispatcher, and ingress telemetry regressions for malformed/late-invalid batches, valid v3 failure evidence, ordering, and publisher failure after publication starts. No newly logged raw webhook payload, credentials, Meta failure details or customer message bodies were identified in the bounded source diff.

### Validation Results

Developer-supplied local results following application of the MESSAGING-005 patch:

- `npm test`: **80 tests; 79 passed, 0 failed, 1 skipped** (the separately gated Redis test).
- `npm run typecheck` (`react-router typegen && tsc`): **PASS**, no errors.
- `npm run build`: **PASS**, both Vite client and SSR/server builds; Node-core/ioredis browser-externalization advisories were non-fatal.
- `bash scripts/run-whatsapp-queue-redis-test.sh`: **2 passed, 0 failed, 0 skipped** against disposable Docker Redis, including queue payload preservation and inbound trace continuation.

Earlier isolated focused checks of the delivered M005 source reported **21/21 passing** with substitute Shared validators; these are not represented as an independent full-dependency runtime result. The complete installed-dependency suite above supplies the primary runtime evidence. Normalizer, telemetry, dispatcher, route, publisher and zero-publication-on-rejection cases are covered by the reported suite. The architect additionally reconstructed the accepted M004 baseline and verified `git apply --check --whitespace=error-all`, patch application and `git diff --check` for the M005 diff; the developer's own Git working tree and separate focused invocations were not independently inspected. Confirmed source sizes: route 138, dispatcher 34, preflight 58 physical lines.

### Deviations

The developer used the agreed manual, architect-supplied incremental patch workflow on their Messaging checkout instead of launcher-owned mirrored task worktrees and branches. This is documented execution-workflow non-conformance; no task-branch, launcher, claim, commit or push evidence is claimed. This report records one implementation attempt (`attempt: 1`) rather than counting earlier refactor tasks as attempts of MESSAGING-005.

### Assumptions

The developer's posted `npm test`, `npm run typecheck`, build and disposable-Redis results were produced after applying the M005 patch on top of the accepted M004 implementation. Existing Shared v1/v3 contracts and BullMQ ID/retry implementation remain unchanged.

### Unresolved Issues

None blocking this bounded task. A Redis/publisher failure after publication begins can still leave partial job acceptance; this is explicitly within the accepted retry/idempotency model and is not an unresolved preflight defect. Terminal cross-service system validation is assigned to `ARCH-034-SYSTEM-TEST-001`.

### Architectural Concerns

None blocking. Preflight is pure and linear in request event count and stages only canonical normalized event data. No schema change, transactional queue guarantee, added provider lookup or new shared contract was introduced.

## Architect Review

### Review Status

Accepted — Attempt 1 (2026-10-12).

### Review Notes

The implementation meets the agreed post-refactor hardening boundary. Authentication and JSON parsing still precede structural preflight; malformed signed envelopes and any late-invalid inbound event are rejected before the first queue publication. Valid signed traffic retains the canonical v1/v3 payloads, ordering and status-ignore policy. The sequential publisher and its non-atomic failure semantics are unchanged. Manual-checkout execution deviation is recorded rather than represented as launcher compliance.

### Reviewed Files

`app/lib/whatsapp/webhook-preflight.ts`, `app/lib/whatsapp/webhook-dispatch.server.ts`, `app/routes/whatsapp.tsx`, `tests/whatsapp-webhook-preflight.test.mjs`, `tests/whatsapp-webhook-preflight-telemetry.test.mjs`, `tests/whatsapp-webhook-dispatch.test.mjs`, and `tests/whatsapp-webhook-route.test.mjs`, together with the previously accepted normalizer, authentication and publisher contracts.

### Validation Reviewed

Developer-supplied test summary 79/80 passed (one expected conditional skip), successful TypeScript typecheck, client/SSR build and live disposable-Redis telemetry 2/2 PASS. Source structure and bounded code paths reviewed; earlier isolated M005 behavioural tests reported 21/21 PASS with substitute validators. The architect verified patch application and diff whitespace checks on a reconstructed baseline, but did not independently execute the full installed-dependency test suite or access the user's live Git worktree.

### Architecture Conformance

Conforms to ARCH-034-MESSAGING-005's explicit behaviour-change contract and preserves Messaging ownership, HMAC/security boundary, canonical Shared event contracts, deterministic queue IDs and existing retry/telemetry semantics. Does not introduce multi-job atomicity, new infrastructure or Background policy.

### Follow-up

`ARCH-034-SYSTEM-TEST-001` is now eligible for Ready after this task's acceptance; the developer may manually validate before invoking the terminal system-test task. ARCH-034 remains In Progress pending independent system validation. No `docs/decisions/**/_index.md` files are changed.
