---
id: ARCH-047-MESSAGING-001
architecture_id: ARCH-047
title: Authenticate and publish Meta template-status webhooks to BullMQ
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-25
updated: 2026-10-25
---

# Authenticate and publish Meta template-status webhooks to BullMQ

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

**Authoritative consumer contract:** `docs/decisions/background/ARCH-047/BACKGROUND-003-manage-meta-template-submission-and-status.md`, **Attempt 2, Requirement R3**. The normalized payload, SHA-256 identity and BullMQ options in this task reproduce that frozen consumer contract. They are **not** a second independently designed protocol. If the live BG003 contract differs, stop and return the difference to the architect; do not invent a compatible-looking local event.

This is a **portable task definition**: the source snapshot permits determining scope and readiness, but no task branch, task worktree, commit or push has been created by its authorship. `status: ready` means the task has no formal prerequisite; execution must still be materialised/claimed through the canonical task launcher.

## Objective

Extend the existing signed Meta WhatsApp webhook ingress to durably enqueue one strictly normalised `meta-template-status-update` job per `message_template_status_update` change, without altering current inbound-message and delivery-status processing.

## Context

The current `moda-interact-messaging` code already authenticates the raw `POST /webhook/whatsapp` body in `app/routes/whatsapp.tsx`, stages existing inbound and delivery-status observations in `app/lib/whatsapp/webhook-preflight.ts`, dispatches in `app/lib/whatsapp/webhook-dispatch.server.ts` and publishes using `app/lib/whatsapp/whatsapp-job-publisher.server.ts` to the `whatsapp-events` BullMQ queue. Preflight currently ignores all change fields other than `messages`.

`ARCH-047-BACKGROUND-003` already owns a Meta template management service and, in Attempt 2, owns the strict `whatsapp-events` consumer for **this exact job**. Messaging must not read/write PostgreSQL, interpret template approval, query Meta, create template registrations or activate merchant assignments.

Meta template-status webhooks are **WABA-level** events; unlike ordinary `messages` callbacks, they may arrive only at the Meta app's **default webhook callback URL**. Verify the actual app-level callback/subscription and route at handoff. A WABA/phone-specific `messages` callback override is not proof that template events will reach this service.

## Scope

Only `moda-interact-messaging/` source/tests and this assigned task file. Required source ownership:

```text
app/lib/whatsapp/template-status-normalizer.ts          NEW: pure Meta-change to bounded v1 field mapping
app/lib/whatsapp/template-status-job-identity.server.ts NEW: canonical JSON/SHA-256 identity helper
app/lib/whatsapp/webhook-preflight.ts                   EXTEND: stage template changes with existing events
app/lib/whatsapp/webhook-dispatch.server.ts             EXTEND: dispatch new staged kind in sequence
app/lib/whatsapp/whatsapp-job-publisher.server.ts       EXTEND: one narrow template-status publisher
app/lib/queues/whatsapp.queue.ts                        REUSE: existing whatsapp-events producer
app/routes/whatsapp.tsx                                 REUSE: raw-body HMAC and HTTP behaviour
```

The task may choose a smaller equivalent split only if it preserves focused, separately testable normalisation, identity and publishing responsibilities. Do not create a new catch-all route/dispatcher or any new source file over 300 physical lines. Add focused `tests/whatsapp-template-status-*.test.mjs` alongside the existing webhook, publisher and route tests. Do not change existing job payloads or their identity helpers.

## Out of Scope

- No new REST/webhook endpoint, Meta app registration automation, provider GET/POST operations, database model/migration or PostgreSQL connection in Messaging.
- No `MetaTemplateRegistration` lookup; do not filter out unknown/external templates at ingress. Background handles author provenance and current provider state.
- No BG003 consumer, its polling scheduler, provider reconciliation, drift detection, WhatsApp sending, customer admission or automatic merchant publication. Those belong to Background.
- No generic Shared AST/event package, template AST parsing, translation, image processing or R2 interaction.
- No changes to the existing inbound v1, outbound provider-status v3 or conversation-turn queue contracts.
- `message_template_components_update`, `message_template_quality_update` and `template_category_update` are outside this **status-only v1** producer; continue ignoring unrelated fields, reporting later feature gaps to the architect if necessary.

## Requirements

### R1 — Preserve authenticated ingress and HTTP contract

Use the **existing** `POST /webhook/whatsapp` React Router action and `verifyMetaSignature(request, rawBody)`. Check the `X-Hub-Signature-256` HMAC-SHA256 against the unmodified UTF-8 request body **before** JSON parsing, preflight or queue publication. Keep the existing GET verification challenge and route configuration unchanged.

The response contract stays:

| Condition | HTTP outcome | Publication |
|---|---|---|
| Wrong method | Existing `405` | None |
| Missing/invalid Meta signature | Existing `401` | None |
| Signed syntactically invalid JSON | Existing `400` | None |
| Signed invalid envelope, invalid inbound message or **invalid matching template-status change** | Existing `400` / `invalid_payload` | **No jobs from that HTTP batch** |
| Valid signed batch, including mixed template, inbound and delivery-status changes | Existing `200 EVENT_RECEIVED` **after all queue `add` calls succeed** | One job per staged event in source order |
| Queue/Redis publication throws or is not durably accepted | Failure/retry path, **not `200`** | Existing already-accepted jobs may remain; no false atomicity claim |

Preflight **all relevant changes before the first queue operation**. Preserve messages-first/statuses-second within each existing `messages` change and preserve the traversal order of `entry[]` and `changes[]`. Do not change the existing policy that malformed **individual ordinary delivery statuses** are skipped; template-status changes instead require complete validated identity to prevent silently losing an approval notification.

### R2 — Exact Meta source recognition and mapping

In signed payloads, recognise **only** changes where `field === "message_template_status_update"` within `object: "whatsapp_business_account"`, `entry[]`, `changes[]`. Stage **one** template-status event per such change. For template events the surrounding `entry.id` is the authoritative **WABA ID**; never substitute `value.metadata.phone_number_id` or another phone-number identifier. Leave unrelated changes alone.

The source-to-v1 mapping is exact:

| Meta path | Outbound property | Required handling |
|---|---|---|
| `entry.id` | `wabaId` | Required decimal string, 1–32 chars |
| `change.value.message_template_id` | `providerTemplateId` | Decimal string 1–32 chars, or `null` if absent |
| `change.value.message_template_name` | `providerTemplateName` | Required nonempty string, max 255 chars |
| `change.value.message_template_language` | `providerLanguageCode` | Required nonempty string, max 16 chars; keep Meta form, e.g. `en_GB` |
| `change.value.event` | `providerStatus` | Required nonempty string, max 32 chars; preserve provider spelling/case |
| `change.value.reason` | `reasonCode` | String max 128 chars or `null` when absent/null |
| Local authenticated-receipt time | `receivedAt` | Canonical UTC ISO-8601 string ending `Z`; not provider occurrence time |

For any numeric provider ID, accept only a **safe nonnegative integer** that can be losslessly converted to a base-10 decimal string; reject an unsafe JavaScript number rather than hash a rounded ID. Reject blank/whitespace-padded strings, arrays, objects, booleans, invalid formats or out-of-range lengths. Preserve validated Meta name, language, status and reason values **exactly**; do not translate, uppercase, truncate, replace, or silently change their spelling. When an ID/reason is absent, emit explicit JSON `null`, not `""` or an omitted key.

Known statuses include `APPROVED`, `REJECTED`, `PENDING`, `PAUSED` and `DISABLED`; **do not implement an exhaustive status allowlist**. A new but bounded, well-formed Meta status string must be forwarded unchanged for BG003 to record as unknown/unavailable and reconcile. Never coerce an unrecognised status to `APPROVED`.

### R3 — Exact `whatsapp-events` queue/job payload v1

Publish to the **existing queue** `whatsapp-events`, using the **case-sensitive job name** `meta-template-status-update`. Never use `message-received`, `message-status` or `process-conversation-turn` for template-status observations.

The job `data` must be an object containing **exactly these nine properties**, with types/keys as shown; no raw provider webhook or extra internal fields:

```json
{
  "schemaVersion": 1,
  "eventIdentity": "meta-template-status:v1:022da3c966c7197c8e225393be7963e771f032b148739e6f9156ee446c565ef4",
  "wabaId": "123456789",
  "providerTemplateId": "987654321",
  "providerTemplateName": "checkout_recovery_initial_v2",
  "providerLanguageCode": "en_GB",
  "providerStatus": "APPROVED",
  "reasonCode": "NONE",
  "receivedAt": "2026-10-25T19:00:00.000Z"
}
```

`schemaVersion` is the JSON number `1`, not the string `"1"`. `providerTemplateId` is a **string or null**, never a JSON number. `eventIdentity` must match R4. The encoded `JSON.stringify(job.data)` must be **at most 4096 UTF-8 bytes**; reject oversize changes during preflight rather than enqueuing a payload the Background decoder will reject. The producer must not forward webhook `object`/`entry`/`changes`, category, arbitrary provider metadata, message contents, credentials, headers or unneeded customer data.

### R4 — Deterministic cross-service event identity and BullMQ job ID

Meta does not supply a stable occurrence ID for this event. Build the identity preimage using **only** the six normalised values below in this exact **lexicographic key order**:

```json
{"providerLanguageCode":"en_GB","providerStatus":"APPROVED","providerTemplateId":"987654321","providerTemplateName":"checkout_recovery_initial_v2","reasonCode":"NONE","wabaId":"123456789"}
```

Algorithm: construct an object with the six lexicographically sorted keys, serialise as **compact UTF-8 JSON** (no spaces/newlines, conventional JSON string escaping), SHA-256 the exact bytes and encode as lowercase 64-character hexadecimal. Use JSON `null` for missing optional values. **Do not** include `receivedAt`, queue attempt, transport timestamp, webhook entry index or any other field. Preserve the validated provider strings unchanged.

For the frozen example, the SHA-256 digest **must** equal:

```text
022da3c966c7197c8e225393be7963e771f032b148739e6f9156ee446c565ef4
```

Set:

```text
eventIdentity = meta-template-status:v1:022da3c966c7197c8e225393be7963e771f032b148739e6f9156ee446c565ef4
jobId         = meta-template-status-v1-022da3c966c7197c8e225393be7963e771f032b148739e6f9156ee446c565ef4
```

The colon-free BullMQ `jobId` and colon-containing durable `eventIdentity` are **different strings**. Repeat deliveries carrying identical six-field observations produce the same digest even when `receivedAt` differs. This is an **observation-level dedupe key**, not proof that identical status transitions cannot recur in reality. Background owns final provider reconciliation; Messaging must not treat deduplication as authority to activate or reject a shop assignment.

### R5 — Queue publication, retries and error propagation

Add `enqueueMetaTemplateStatus(event, queue?)` beside the two existing narrow publisher functions, using `getWhatsAppQueue()` and an injected queue writer test seam. The exact BullMQ producer options are:

```ts
{
  jobId: `meta-template-status-v1-${digest}`,
  attempts: 5,
  backoff: { type: "exponential", delay: 5000 }
}
```

Do not alter the existing options for `message-received` or `message-status`. In the dispatcher publish only staged, preflight-validated events, in their established traversal order. **Await each queue `add`** and return `200` only when every add resolves as accepted. An enqueue failure must propagate to the existing route failure/ingress-telemetry path so Meta can retry; no catch-and-ack, silent skip or in-process fallback buffer. Already-accepted earlier jobs may remain when a later publication fails; deterministic IDs and Background idempotency handle redelivery.

The deterministic `jobId` may suppress a repeat while a prior job is still retained by BullMQ. Do not assert that every identical Meta delivery creates a fresh job or forces a new Meta GET; this transport limitation must be covered by BG003's provider reconciliation and later system validation. This producer task does not change the architect-approved job-ID contract.

### R6 — Module boundaries, security and monitoring

- Messaging authenticates, validates, normalises and enqueues only. It does **not** read `WhatsAppTemplateMetaRegistration` or `WhatsAppTemplateMetaEvent`, query Meta, infer shop identity, approve a template or write PostgreSQL.
- Keep `template-status-normalizer.ts` independently testable; keep the SHA/queue identity helper and queue adapter separate from route logic. Preserve the current webhook-preflight and dispatcher composition; no duplicate generic logger or queue client.
- Reuse the existing request telemetry and BullMQ telemetry; if adding generic runtime logs, use `@modainteract/moda-interact-shared/logging`. Log bounded event type/status, event identity and reason codes only as allowed by the shared redaction convention; never log raw webhook bodies, message text, bearer tokens, signed headers, full customer payloads or R2 media URLs.
- Provider auth may be missing/invalid, Redis may be unavailable and Meta may redeliver: handle these through the existing fail-closed/HTTP retry paths; no unexpected business-state side effect is allowed at ingress.
- Keep template-status functionality limited to the existing URL and service, and verify the real **Meta app-level default webhook callback** points to this publicly routed endpoint and subscribes to `message_template_status_update`. If deployment settings are outside the implementation agent's access, record the exact setting/verification needed; request a bounded Gateway change only for a demonstrated routing deficiency. Do not claim configuration verified without evidence.

### R7 — No accidental Meta-import or outbound admission changes

An authenticated template-status webhook for an unknown/external template is still published as an **observation**; BG003 decides whether it is linked to a Moda-created registration. Messaging must never create, import, adopt, activate or delete a template from such a notification. No customer send, commerce mutation, consent/STOP decision, billing charge, Chat/AI action or merchant assignment is performed in this task.

## Work Items

- [ ] Inspect the current signed route, preflight/dispatcher, queue writer and existing `whatsapp-events` tests; preserve its request/response behaviour.
- [ ] Implement the standalone Meta template-status field normaliser (R2) with strict bounded data and canonical `receivedAt`.
- [ ] Implement the exact event/job identity helper and verify the frozen SHA-256 vector (R4).
- [ ] Extend preflight and dispatch to stage and publish signed template-status changes, preserving whole-batch validation and existing ordering (R1, R5).
- [ ] Add the narrow queue publisher with the exact job name, `jobId`, attempts and backoff, using the existing queue/telemetry adapter.
- [ ] Add focused unit, signed-route, dispatch/producer, mixed-batch and disposable Redis tests described below.
- [ ] Verify/document app-level Meta webhook callback/subscription configuration and any unresolved operational routing requirement without implementing unrelated Gateway work.
- [ ] Record complete validation, changed files, task worktree isolation, start synchronisation, commit/push evidence and remaining issues in Completion Report.

## Interfaces / Contracts

**Producer:** `moda-interact-messaging` `POST /webhook/whatsapp` → existing BullMQ `whatsapp-events` job `meta-template-status-update`, `schemaVersion: 1`, precise R2–R5 format.

**Consumer:** `moda-interact-background` `src/workers/whatsapp.worker.ts` strict v1 decoder → BG003 `processTemplateStatusObservation(...)` → existing PostgreSQL provider-registration/event tables. BG003 maps the producer's `receivedAt` to its local `occurredAt` adapter field; `receivedAt` is not provider ordering evidence.

**Authoritative wire test fixture:** R3 and R4 of `ARCH-047-BACKGROUND-003`, including the exact example bytes, digest, eventIdentity and jobId. Both repositories must independently execute the **same canonical fixture**; do not publish a second incompatible schema or infer it from Prisma JSONB column types.

**Source fields:** Meta `entry[].id` is WABA, `changes[].field === message_template_status_update` and `changes[].value` fields are defined in R2; no customer phone ID or sender-WABA inference.

**No other runtime contracts introduced.** Existing inbound v1 and provider-status v3 contracts remain unchanged; there is no ARCH-047 Shared package-release prerequisite for the AST or event.

## Dependencies

None. This is a Messaging ingress/queue producer that does **not** require ARCH-047 database access or an already deployed BG003 consumer to be implemented and tested with producer fixtures. BG003 may be independently implemented against the same frozen R3 contract. Complete integration is deferred to the terminal ARCH-047 System Test after both owners are accepted.

## Enables

The eventual cross-service ARCH-047 system test can verify the real Meta webhook → Messaging → BullMQ → BG003 → PostgreSQL path after all required implementations are Complete. This task does **not** permit the Messaging agent to start BG003 or the system test, and it is not a formal implementation prerequisite of BG003 Attempt 2.

## Acceptance Criteria

- [ ] Valid signed Meta `message_template_status_update` produces **exactly one** `meta-template-status-update` add per matching change; multiple entries/changes retain source order, and mixed valid inbound/status/template batches preserve current event ordering.
- [ ] The exact R3 payload has **nine** keys and no extra raw webhook/PII, with `schemaVersion = 1`, WABA from `entry.id`, decimal-string/null template ID and ISO `receivedAt`.
- [ ] Hash/vector fixture yields the exact R4 digest, `eventIdentity` and `jobId`; replay with a different `receivedAt` yields the same identity; safe numeric ID conversion and unsafe-number rejection are demonstrated.
- [ ] The queue name, exact job name and producer retry options match R5, and existing message-received/message-status jobs retain their names, IDs, payloads and retry settings.
- [ ] Missing fields, wrong ID types, unsafe numeric IDs, oversized fields, malformed template observation or outbound payload over 4096 bytes reject the signed batch **before any publication**; malformed *ordinary provider statuses* retain their existing skip semantics.
- [ ] Unknown bounded provider status labels are forwarded unmodified, never interpreted as approved; unrelated fields are ignored, including category/quality/components updates.
- [ ] Invalid signature, malformed JSON, missing-secret and wrong-method behaviour are unchanged; a queue failure does not result in a `200` acknowledgement. No partial jobs are published after preflight rejection (though a sequential mid-publish failure may leave earlier accepted jobs).
- [ ] Tests show no database access, Meta API call, external-template adoption, customer send or changes to consent/STOP, billing, worker-side status interpretation or checkout state.
- [ ] Callback/subscription requirement is verified where access exists or recorded accurately for deployment review; any missing route/config is returned to the architect, not silently invented by the producer.
- [ ] New code is modular and focused, existing Messaging tests/typecheck/build pass and `git diff --check` is clean.

## Validation

Use the current repository's `package.json` scripts, not assumed commands from Background or Admin. In the inspected 25 October snapshot the required checks are:

- [ ] Focused pure/queue tests: `node --import tsx --test tests/whatsapp-template-status-*.test.mjs tests/whatsapp-webhook-preflight.test.mjs tests/whatsapp-webhook-dispatch.test.mjs tests/whatsapp-job-publisher.test.mjs`.
- [ ] Signed route regression: `node --import tsx --test tests/whatsapp-webhook-route.test.mjs tests/whatsapp-webhook-auth.test.mjs`.
- [ ] Redis-backed queue integration using the repo-owned disposable Redis harness: `bash scripts/run-whatsapp-queue-redis-test.sh tests/whatsapp-template-status-queue.test.mjs` (create this focused file, or record equivalent explicit disposable Redis evidence; do **not** connect tests to shared/prod Redis). This test must skip cleanly without `TEST_REDIS_URL` so `npm test` does not require Docker/Redis.
- [ ] `npm test`.
- [ ] `npm run typecheck`.
- [ ] `npm run build`.
- [ ] `git diff --check` and report focused new module sizes; no new >300-line catch-all.
- [ ] Record the Meta app default callback/subscription check outcome. If credentials/dashboard access are not available in the implementation environment, record an honest configuration blocker or manual verification requirement; do not claim a live provider test.

Do not check validation boxes based on another task's Completion Report. Any non-executable required check must remain unchecked with a specific explanation.

## Stop Condition

When work items and acceptance criteria are satisfied and validation evidence is recorded, change the task to `review`, complete the task's Completion Report and return to `moda_architect`. **STOP.** Do not start BG003, another ARCH-047 task, a system test or unrelated code cleanup.

## Implementation Notes

Use the standard `scripts/start-agent-task.py --prepare` task launcher and its returned physical parent/implementation worktrees, branch isolation, start-of-attempt sync and recursive submodule evidence. Do not apply this portable task definition in a shared/default implementation checkout and claim it was materialised. Use mirrored `task/ARCH-047-MESSAGING-001` branches when running an authorised implementation.

ARCH-047 is pre-production, but raw webhook authentication, queue durable acceptance and existing message-status v3 compatibility remain security/correctness boundaries. Keep error logs bounded, do not substitute empty/invalid fields, and don't introduce implicit fallbacks for absent WABA identity. If existing installed Shared telemetry requires a missing export, report that specific dependency gap; do not create a competing generic logger.

**Important transport limitation:** The identical six-field job ID intentionally deduplicates webhook retransmissions. With completed-job retention it can also suppress an identical later transition; that limitation belongs to BG003's verified provider-state reconciliation and terminal system testing, not a Messaging-only reinterpretation of the R3 identity. Surface any evidence that the consumer has no recovery path rather than silently changing the agreed v1 format.

## Completion Report

### Status

Not Started — defined but not materialised in the developer's Git environment.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run. Implementation verification is outstanding.

### Deviations

None.

### Assumptions

The reviewed 25 October 2026 Messaging snapshot still uses the route, extracted preflight/publisher modules and existing `whatsapp-events` queue described above. Re-inspect the real task implementation worktree at claim time. BG003 Attempt 2 R3 is the fixed consumer format; there is no approved Shared AST/event package prerequisite.

### Unresolved Issues

The Meta app's **default** webhook callback URL and live `message_template_status_update` subscription cannot be proven from source alone. Confirm with deployment-owner evidence before asserting production readiness.

### Architectural Concerns

Repeated identical provider transitions may be coalesced by the deterministic BullMQ job ID while a job is retained. Consumer reconciliation must preserve conservative provider eligibility; final integrated certification is separate.

## Architect Review

### Review Status

Pending — implementation not reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed; review the implemented producer against BG003 R3 and the existing Messaging ingress/queue constraints.

### Follow-up

After acceptance, coordinate integration with BG003 and the terminal ARCH-047 System Test; do not change upstream tasks or indexes from the Messaging implementation.
