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
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-034-MESSAGING-004"]
enables: ["ARCH-034-SYSTEM-TEST-001"]
created: 2026-10-11
updated: 2026-10-11
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

- [ ] Verify MESSAGING-004 is architect-accepted `complete` and inspect its actual extracted dispatcher and publisher APIs before implementation.
- [ ] Add narrow envelope shape validation and whole-batch event preflight, preserving accepted no-op/skip cases.
- [ ] Ensure no publication occurs before all relevant inbound messages are valid; preserve existing sequential queue publication afterwards.
- [ ] Add focused invalid JSON/envelope/mixed-late-invalid and valid mixed-v3 regression tests with exact status, telemetry and zero-publication assertions.
- [ ] Test queue failure after preflight as a **non-atomic** publication boundary and assert unchanged idempotent retry/job identity.
- [ ] Run the declared repository validation and record changed file sizes, security/telemetry findings and Completion Report.

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

- [ ] Valid JSON with invalid envelope shapes is rejected deterministically as `400`, not an incidental `500`, without queue publication.
- [ ] Late invalid inbound message in a signed mixed batch causes `400 invalid_payload` with **zero** enqueued jobs from that request.
- [ ] Valid signed event batches preserve byte-compatible normalized queue payloads, deterministic job IDs and original publish ordering.
- [ ] Invalid individual provider statuses remain ignored without rejecting otherwise-valid batches; extra Meta fields and non-`messages` changes are accepted/ignored as before.
- [ ] Existing GET, HMAC verification, invalid JSON, 405, 401 and valid 200 response/telemetry behaviour remains intact.
- [ ] Queue failure after publication starts retains retry/500 semantics and is **not** misrepresented as an atomic queue transaction.
- [ ] No sensitive provider/customer payloads introduced into logs/traces or tests; no new database/Shared/Gateway implementation.
- [ ] No new production file exceeds 300 physical lines and no all-purpose route/dispatcher regression.

## Validation

Inspect the current Messaging `package.json` and use its actual scripts, not inferred commands. In the reviewed baseline these were available:

- [ ] Focused webhook route/dispatcher/preflight tests (test filenames from MESSAGING-004 and new focused tests).
- [ ] `node --import tsx --test tests/whatsapp-inbound-normalization.test.mjs tests/whatsapp-provider-status.test.mjs`
- [ ] `node --import tsx --test tests/whatsapp-ingress-telemetry.test.mjs`
- [ ] Publisher/queue tests for zero-publication-on-rejection and partial-publisher-failure retry (synthetic queue stub or disposable Redis only).
- [ ] `npm test`
- [ ] `npm run typecheck`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] Record source line counts and confirm no new production module exceeds 300 physical lines.

## Stop Condition

After the specified Work Items, Acceptance Criteria and Validation pass, update only this task's execution state/Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not begin the dependent system test. Use the launcher-created mirrored task branch/worktrees, not a shared/default checkout.

## Implementation Notes

Do not attempt to make multi-job BullMQ publication transactional. The key guarantee in this task is **zero publication when the request is rejected by preflight**. A `500` after a publisher error may still follow partial acceptance; retries remain idempotent via existing IDs. Use a single preflight pass over the authenticated object; do not run an additional deep serializer or broaden Meta schema interpretation beyond the bounded shape contract.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
