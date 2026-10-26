---
id: ARCH-047-MESSAGING-001
architecture_id: ARCH-047
title: Authenticate and publish Meta template-status webhooks to BullMQ
task_kind: implementation
domain: messaging
repository: moda-interact-messaging
assigned_agent: moda_messaging
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-SHARED-002
enables: []
created: 2026-10-25
updated: 2026-10-26
---

# Authenticate and publish Meta template-status webhooks to BullMQ

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

**Authoritative cross-repository contract:** published `@modainteract/moda-interact-shared/whatsapp-template-events` **v2** from `ARCH-047-SHARED-001/002`. BG003 consumes the same schema. The earlier document-only v1 hash-based event ID is superseded before production. No Admin AST contract is moved into Shared.

This is a materialized task definition. `ARCH-047-SHARED-002` completed on 2026-10-26 and published the accepted `2.5.1` subpath; the dependency gate is satisfied. Execution must still be claimed through the canonical task launcher.

## Objective

Extend the existing signed Meta WhatsApp webhook ingress to durably enqueue one strictly normalised `meta-template-status-update` job per `message_template_status_update` change, without altering current inbound-message and delivery-status processing.

## Context

The current `moda-interact-messaging` code already authenticates the raw `POST /webhook/whatsapp` body in `app/routes/whatsapp.tsx`, stages existing inbound and delivery-status observations in `app/lib/whatsapp/webhook-preflight.ts`, dispatches in `app/lib/whatsapp/webhook-dispatch.server.ts` and publishes using `app/lib/whatsapp/whatsapp-job-publisher.server.ts` to the `whatsapp-events` BullMQ queue. Preflight currently ignores all change fields other than `messages`.

`ARCH-047-BACKGROUND-003` owns the Meta management consumer for **this exact published Shared v2 job**. Messaging must not read/write PostgreSQL, interpret template approval, query Meta, create template registrations or activate merchant assignments.

Meta template-status webhooks are **WABA-level** events; unlike ordinary `messages` callbacks, they may arrive only at the Meta app's **default webhook callback URL**. Verify the actual app-level callback/subscription and route at handoff. A WABA/phone-specific `messages` callback override is not proof that template events will reach this service.

## Scope

Only `moda-interact-messaging/` source/tests and this assigned task file. Required source ownership:

```text
app/lib/whatsapp/template-status-normalizer.ts          NEW: pure Meta-change to bounded v2 field mapping
app/lib/whatsapp/template-status-observation-id.server.ts NEW: generate a fresh UUID v4 per authenticated change; format using Shared v2 helper
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
- No generic Shared AST package, template AST parsing, translation, image processing or R2 interaction.
- No changes to the existing inbound v1, outbound provider-status v3 or conversation-turn queue contracts.
- `message_template_components_update`, `message_template_quality_update` and `template_category_update` are outside this **status-only v2** producer; continue ignoring unrelated fields, reporting later feature gaps to the architect if necessary.

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

The source-to-v2 mapping is exact:

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

### R3 — Exact `whatsapp-events` queue/job payload v2

Use the **published Shared** `MetaTemplateStatusObservationV2Schema` and `META_TEMPLATE_STATUS_{QUEUE,JOB,SCHEMA_VERSION}`. Queue remains `whatsapp-events`, job name `meta-template-status-update` and retry options `attempts: 5`, exponential 5000ms. Payload has **exactly nine** fields:

```json
{
  "schemaVersion": 2,
  "eventIdentity": "meta-template-status:v2:550e8400-e29b-41d4-a716-446655440000",
  "wabaId": "123456789",
  "providerTemplateId": "987654321",
  "providerTemplateName": "checkout_recovery_initial_v2",
  "providerLanguageCode": "en_GB",
  "providerStatus": "APPROVED",
  "reasonCode": "NONE",
  "receivedAt": "2026-10-25T19:00:00.000Z"
}
```

Reject missing/unknown fields, malformed identities, invalid timestamps, wrong schema version, malformed IDs, unsafe numeric source IDs and UTF-8 job data >4096 bytes **during whole-batch preflight**. Preserve Meta spelling and unknown bounded status values. `receivedAt` is Messaging's receipt time, not Meta event ordering. Do not include raw webhook/customer payloads, headers, Meta credentials or AST. The producer/consumer must run the **same published Shared fixture** and v2 validator; neither may redefine the event locally.

### R4 — Occurrence identity rather than content-based dedupe

When processing each authenticated `message_template_status_update` change, allocate a fresh `crypto.randomUUID()` **for that change** after successful signed whole-batch preflight, and call Shared's pure UUID identity and job-ID formatters. For the fixed UUID `550e8400-e29b-41d4-a716-446655440000`, the resulting identifiers are:

```text
eventIdentity = meta-template-status:v2:550e8400-e29b-41d4-a716-446655440000
jobId         = meta-template-status-v2-550e8400-e29b-41d4-a716-446655440000
```

A second independently received identical APPROVED (including APPROVED → PAUSED → APPROVED) must get a **new UUID**, so BullMQ's retained first job cannot coalesce it. A retry of the *same enqueued job* keeps the same ID. A Meta redelivery can lead to duplicate business information under a new UUID; BG003 reconciles current provider state and deduplicates effects. Do **not** hash just WABA/name/language/status/reason for job identity, rely on `removeOnComplete`, or assume provider `receivedAt` orders transitions. A content fingerprint may be logged as bounded diagnostics but is distinct from occurrence identity.

### R5 — Existing publisher and acknowledgement boundary

Publish one job per staged matching change into the existing queue using `getWhatsAppQueue()` and injected queue writer as in current module boundaries. Producer options remain `{jobId: formatMetaTemplateStatusJobId(observationId), attempts: 5, backoff: {type: "exponential", delay: 5000}}`. Stage/preflight **all** relevant changes before adding the first job; then await each queued add in source order. Return provider `200` only after durable acceptance of all jobs; an enqueue exception follows the existing retry/non-200 path. A mid-publish failure can leave earlier accepted jobs; the next Meta retry creates new occurrence IDs, and BG003 reconciles idempotently. Preserve existing inbound `message-received`, `message-status` and conversation-turn job payloads/options without modification.

BullMQ completed-job retention and lazy removal may remain at their current settings. Event occurrence IDs—not removal policy—guarantee distinct later observations can enqueue. The **independent BG003 due-registration reconciliation** remains a separate backstop when notifications fail or are lost; the producer does not poll Meta or write PostgreSQL.

### R6 — Module boundaries, security and monitoring

- Messaging authenticates, validates, normalises and enqueues only. It does **not** read `WhatsAppTemplateMetaRegistration` or `WhatsAppTemplateMetaEvent`, query Meta, infer shop identity, approve a template or write PostgreSQL.
- Keep `template-status-normalizer.ts` independently testable; keep the Shared UUID occurrence formatter and queue adapter separate from route logic. Preserve the current webhook-preflight and dispatcher composition; no duplicate generic logger or queue client.
- Reuse the existing request telemetry and BullMQ telemetry; if adding generic runtime logs, use `@modainteract/moda-interact-shared/logging`. Log bounded event type/status, event identity and reason codes only as allowed by the shared redaction convention; never log raw webhook bodies, message text, bearer tokens, signed headers, full customer payloads or R2 media URLs.
- Provider auth may be missing/invalid, Redis may be unavailable and Meta may redeliver: handle these through the existing fail-closed/HTTP retry paths; no unexpected business-state side effect is allowed at ingress.
- Keep template-status functionality limited to the existing URL and service, and verify the real **Meta app-level default webhook callback** points to this publicly routed endpoint and subscribes to `message_template_status_update`. If deployment settings are outside the implementation agent's access, record the exact setting/verification needed; request a bounded Gateway change only for a demonstrated routing deficiency. Do not claim configuration verified without evidence.

### R7 — No accidental Meta-import or outbound admission changes

An authenticated template-status webhook for an unknown/external template is still published as an **observation**; BG003 decides whether it is linked to a Moda-created registration. Messaging must never create, import, adopt, activate or delete a template from such a notification. No customer send, commerce mutation, consent/STOP decision, billing charge, Chat/AI action or merchant assignment is performed in this task.

## Work Items

- [ ] Inspect the current signed route, preflight/dispatcher, queue writer and existing `whatsapp-events` tests; preserve its request/response behaviour.
- [ ] Implement the standalone Meta template-status field normaliser (R2) with strict bounded data and canonical `receivedAt`.
- [ ] Use the published Shared v2 formatter with fresh `crypto.randomUUID()` per authenticated observation; verify its UUID test fixture (R4).
- [ ] Extend preflight and dispatch to stage and publish signed template-status changes, preserving whole-batch validation and existing ordering (R1, R5).
- [ ] Add the narrow queue publisher with the exact job name, `jobId`, attempts and backoff, using the existing queue/telemetry adapter.
- [ ] Add focused unit, signed-route, dispatch/producer, mixed-batch and disposable Redis tests described below.
- [ ] Verify/document app-level Meta webhook callback/subscription configuration and any unresolved operational routing requirement without implementing unrelated Gateway work.
- [ ] Record complete validation, changed files, task worktree isolation, start synchronisation, commit/push evidence and remaining issues in Completion Report.

## Interfaces / Contracts

**Producer:** `moda-interact-messaging` `POST /webhook/whatsapp` → existing BullMQ `whatsapp-events` job `meta-template-status-update`, `schemaVersion: 2`, exact Shared contract from R2–R5.

**Consumer:** `moda-interact-background` `src/workers/whatsapp.worker.ts` strict Shared v2 decoder → BG003 `processTemplateStatusObservation(...)` → existing PostgreSQL provider-registration/event tables. BG003 maps the producer's `receivedAt` to its local `occurredAt` adapter field; `receivedAt` is not provider ordering evidence.

**Authoritative wire test fixture:** the published `ARCH-047-SHARED-001` v2 nine-field fixture, strict Zod schema, UUID and expected job ID. Both repositories must import/test the same published contract. Do not derive semantics from Prisma JSONB columns.

**Source fields:** Meta `entry[].id` is WABA, `changes[].field === message_template_status_update` and `changes[].value` fields are defined in R2; no customer phone ID or sender-WABA inference.

**No other runtime contracts introduced.** Existing inbound v1 and provider-status v3 remain unchanged. The only new Shared dependency is the narrow published status-event v2 contract; no Shared AST/translation contract.

## Dependencies

`ARCH-047-SHARED-002` — the canonical v2 schema/identity package must be published and accepted before Messaging claims this task. No ARCH-047 database access or live BG003 consumer is required to implement and test against Shared fixtures. Complete integration is deferred to the terminal ARCH-047 System Test after both owners are accepted.

## Enables

The eventual cross-service ARCH-047 system test can verify the real Meta webhook → Messaging → BullMQ → BG003 → PostgreSQL path after all required implementations are Complete. This task does **not** permit the Messaging agent to start BG003 or the system test, and it is not a formal implementation prerequisite of BG003 Attempt 2.

## Acceptance Criteria

- [ ] Valid signed Meta `message_template_status_update` produces **exactly one** `meta-template-status-update` add per matching change; multiple entries/changes retain source order, and mixed valid inbound/status/template batches preserve current event ordering.
- [ ] The exact Shared R3 payload has **nine** keys and no extra raw webhook/PII, with `schemaVersion = 2`, WABA from `entry.id`, decimal-string/null template ID and ISO `receivedAt`.
- [ ] Shared UUID fixture yields the exact R4 event/job identities; two identical Meta observations with different UUIDs are independently enqueued while a retained completed job exists; safe numeric ID conversion and unsafe-number rejection are demonstrated.
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

**Important transport limitation:** The published v2 occurrence-ID contract replaces the unsafe v1 six-field hash. Each independently authenticated status change must enqueue even when identical provider values previously occurred and BullMQ retains completed jobs. Surface any evidence that the consumer has no recovery path rather than silently changing the agreed v2 format.

## Completion Report

### Status

Ready — developer takeover recorded on 2026-10-26. Attempt 1 is not yet claimed; the canonical launcher will prepare/synchronize the implementation worktree, verify dependencies, and durably claim it.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run. Implementation verification is outstanding.

### Deviations

None.

### Assumptions

The inspected Messaging snapshot uses the existing signed route, preflight, publisher and `whatsapp-events` queue. Re-inspect at claim. `ARCH-047-SHARED-002` must publish the canonical v2 event contract first; no Shared AST package is required.

### Unresolved Issues

The Meta app's **default** webhook callback URL and live `message_template_status_update` subscription cannot be proven from source alone. Confirm with deployment-owner evidence before asserting production readiness.

### Architectural Concerns

Ensure replay/retention tests use distinct UUID v2 occurrence IDs for genuine later transitions. Consumer and final-admission tests must prove UNKNOWN provider projection after a disabling observation survives Meta GET outage; final integrated certification is separate.

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

Not assessed; review the producer against published Shared event v2 and existing Messaging ingress/queue constraints.

### Follow-up

After acceptance, coordinate integration with BG003 and the terminal ARCH-047 System Test; do not change upstream tasks or indexes from the Messaging implementation.

## Execution Ownership Amendment

- Date: 2026-10-26.
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-MESSAGING-001` to take over this Ready agent-owned task. Execution and completion modes are now `developer`; attempt remains 0 until the canonical launcher claims it.
- Preserved: `assigned_agent: moda_messaging`, coordinator, repository, dependency, task scope, acceptance criteria and validation requirements.
- Dependency check: `ARCH-047-SHARED-002` is `complete` in its canonical parent task record and published package contract is documented above.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-MESSAGING-001`, branch `task/ARCH-047-MESSAGING-001`, synchronized from remote and current `origin/main` before this amendment.
- Implementation worktree: to be prepared by the canonical launcher at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-MESSAGING-001`.
- No implementation changes are made by this ownership amendment. No branch is merged into `main`.
