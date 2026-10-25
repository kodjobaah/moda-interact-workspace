---
id: ARCH-047-BACKGROUND-003
architecture_id: ARCH-047
title: Implement Meta template submission and reconciliation module
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-047-DATABASE-001
enables: []
created: 2026-10-24
updated: 2026-10-25
---

# Implement Meta template submission and reconciliation module

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This task was originally defined from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It was materialised and claimed for developer execution in canonical task worktrees after verifying DB001 completion and synchronising with the workspace mainline. Attempt 1 implemented and pushed the bounded Meta submission/reconciliation module, but did not wire a production queue consumer or a due-registration caller. The architect's 25 October Attempt 1 review now fixes the **exact** `whatsapp-events` job contract, caller, and correction tests below; this is the same task returned to `ready` for developer Attempt 2 with `executor`/`claimed_at` cleared. Preserve the Attempt 1 Completion Report as historical evidence. Messaging's producer remains separately owned: BG003 may implement/test its consumer against the frozen contract fixture without waiting for live producer deployment. No new ARCH-047 Shared AST package is assumed.

## Objective

Submit Admin-compiled Meta template payloads, consume queued authenticated Meta status observations and reconcile provider identities/drift without adopting external templates.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Retain and complete the already-implemented `src/services/meta-template-management/` module (submission orchestrator, server-only Meta Graph API adapter, reconciliation reader, provider observation handler, Prisma repository and module-local ports). Amend rather than replace its existing Attempt 1 source and tests.
- Wire a **separate** `meta-template-status-update` handler into the existing `whatsapp-events` consumer in `src/workers/whatsapp.worker.ts`. Implement its bounded, strictly validated decoder; it invokes the existing module port, never the inbound-message parser.
- Wire the existing `processDueRegistrations(limit)` port to the production messaging-worker entrypoint (`src/entrypoints/messaging.ts`) using a bounded timer and the DB CAS/claim already owned by the module. No new public route, queue, deployment or database table.
- Consume frozen `WhatsAppTemplateMetaRegistration` rows and append `WhatsAppTemplateMetaEvent` receipts. Background maintains current `providerStatus`, provider ID and drift observations, **not** authoring ASTs, translation content, shop assignments or publication permissions.
- Reuse existing sender/WABA credential resolution, Meta API error/retry conventions, BullMQ worker orchestration and structured logging.

## Out of Scope

- No `POST /{TEMPLATE_ID}` editing, template import/adoption, Admin AST parsing or compiling, customer messaging, merchant publication or Meta webhook signature verification.
- No PostgreSQL connection added to Messaging; no changes to DB001 schema; no generic new Shared AST/event package solely for this module. A previously unsupported new cross-repository queue format must be referred to the architect rather than duplicated independently.

## Requirements

**R1 — Exact create-only provider operation.** Admin-006 writes immutable, confirmed `WhatsAppTemplateMetaRegistration` rows with `submissionState = READY_TO_SUBMIT`; a registration is a *request for Background execution*, not proof that Meta accepted it. On claim, use its stored fields to send exactly:

```http
POST /{wabaId}/message_templates
Authorization: Bearer <server-only configured Meta credential>
Content-Type: application/json
```

```json
{
  "name": "<registration.providerTemplateName>",
  "language": "<registration.providerLanguageCode>",
  "category": "<registration.category>",
  "components": "<registration.componentsSnapshot: JSON array, unchanged>"
}
```

`parameterBindingsSnapshot`, `submittedContentHash`, local definition/locale IDs and shop data are **never** provider request fields. Use the centrally configured `messaging.sender` WABA/token and require the stored WABA to match. Parse a successful create response's provider `id` as a **string**, record `SUBMITTED` and the provider template ID, but do not treat request success or a returned status as administrator publication. Store bounded provider outcome evidence. Reuse current module code; never use Meta's edit-existing-template endpoint or adopt an unrelated preexisting `(WABA,name,language)` match. For an image-header registration, pass only the frozen Admin-authorised sample/media handle; do not fetch merchant-original images or recompile the AST.

**R2 — Durable claiming, unknown outcomes and retries.** `processDueRegistrations(25)` is the module-owned entrypoint for registrations due to be created or reconciled. Run it from the deployed `moda-messaging-worker` process at **60-second intervals**, with a bounded initial jitter (0–10 seconds), no overlapping cycle in one process, and a shutdown cleanup. Use the existing `WhatsAppTemplateMetaRegistration` `submissionState`/`nextRetryAt` and conditional-UPDATE (CAS) fields to arbitrate claims across replicas; no new queue/table/lease enum is authorised just to schedule this small control-plane workload. An empty scan must be cheap. On exceptions, use the shared structured logger and propagate/report the failure; the next cycle remains scheduled. Include a production-startup integration test proving that registrations do not stay at `READY_TO_SUBMIT` indefinitely.

Persist create intent before any POST and a **POST-intent receipt** immediately before network dispatch. No network call inside a Prisma transaction. After a timeout, crash, 429/5xx or lost response, keep an **uncertain state** and perform Meta GET by the exact WABA/name/language (and provider ID when known) before any subsequent create attempt. A provider name collision *before* Moda's durable POST intent is not proof of Moda authorship and must be blocked, not adopted. A confirmed provider creation must never be POSTed twice, even after job/worker replay. Reconciliation must handle provider pagination or return explicit `UNCONFIRMED` on an incomplete listing; it must never interpret an incomplete response as absence. Distinguish definitive validation failures from transient/unknown outcomes, apply bounded backoff, and keep registered state and event evidence transactional via the existing Prisma repository. Do not turn reconciliation or later Meta approval into a shop activation.

**R3 — Frozen Messaging → BullMQ → Background status contract (v1).** This task adopts the following precise architecture-owned boundary so the Background consumer can be implemented and tested independently of the separately owned Messaging producer. Do not ask an implementer to invent another payload. The producing task `ARCH-047-MESSAGING-001` must use this same payload and a shared compatibility fixture when it is defined/materialised; do not independently fork its semantics or create a general Shared AST package.

- **Queue:** existing `whatsapp-events`; **job name:** `meta-template-status-update` (exact, case-sensitive). Do **not** reuse `message-status`, `message-received` or `process-conversation-turn`.
- **Input:** Meta's authenticated `whatsapp_business_account.entry[].changes[]` with `field = message_template_status_update`. Messaging validates the signature and converts **each matching change** into exactly one bounded queue job. The `entry.id` is `wabaId`; the `value` fields map `message_template_id → providerTemplateId`, `message_template_name → providerTemplateName`, `message_template_language → providerLanguageCode`, `event → providerStatus` and `reason → reasonCode`. Never infer WABA from a phone-number ID. Messaging must not write PostgreSQL. Other Meta event types follow their preexisting ingress paths.
- **Payload:** the following JSON shape, with no AST, full webhook, customer content, token or authorisation header. `schemaVersion` is the number `1`; `providerTemplateId` is a decimal **string** or `null` when not supplied; `reasonCode` is a bounded string or `null`; `receivedAt` is the time Messaging authenticated/received the observation, **not** an asserted Meta event time.

```json
{
  "schemaVersion": 1,
  "eventIdentity": "meta-template-status:v1:<64 lowercase hex SHA-256>",
  "wabaId": "123456789",
  "providerTemplateId": "987654321",
  "providerTemplateName": "checkout_recovery_initial_v2",
  "providerLanguageCode": "en_GB",
  "providerStatus": "APPROVED",
  "reasonCode": "NONE",
  "receivedAt": "2026-10-25T19:00:00.000Z"
}
```

- **Identity and retries:** when Meta supplies no stable event ID, calculate `eventIdentity` as `meta-template-status:v1:` plus SHA-256 of deterministic canonical JSON over **only** `(wabaId, providerTemplateId, providerTemplateName, providerLanguageCode, providerStatus, reasonCode)` after normalisation. Exclude `receivedAt` and the BullMQ attempt count. Identical observations then deduplicate on replay; because Meta may omit a unique event occurrence ID, this key represents an *observation identity*, not proof that separate identical real-world transitions never occurred. A linked duplicate still triggers a fresh current-state reconciliation, so effective provider state stays correct. For `jobId`, use `meta-template-status-v1-<same SHA-256>` (no colon); database `eventIdentity` remains the durable dedupe key.
- **Canonicalisation test vector:** build the event-identity input as an object whose keys are sorted lexicographically, serialize as compact UTF-8 JSON without whitespace and hash with SHA-256. Preserve Meta's exact validated name/language/status strings; convert a safe provider numeric ID to its base-10 string; use `null` (not a blank string) when optional ID/reason is absent. Never hash `receivedAt`. For the example payload above, the exact canonical bytes are:

```json
{"providerLanguageCode":"en_GB","providerStatus":"APPROVED","providerTemplateId":"987654321","providerTemplateName":"checkout_recovery_initial_v2","reasonCode":"NONE","wabaId":"123456789"}
```

The resulting lowercase hex SHA-256 is `022da3c966c7197c8e225393be7963e771f032b148739e6f9156ee446c565ef4`. The queue `eventIdentity` and colon-free `jobId` must embed this digest; add a deterministic producer/consumer compatibility test. If a provider ID arrives as an unsafe JavaScript number that cannot be represented exactly, reject that delivery for reconciliation rather than persisting a rounded identity.
- **Bounds and decoding:** reject any job with the wrong name, unknown `schemaVersion`, missing WABA/name/language/status, malformed ID, invalid ISO-8601 `receivedAt`, non-string required value, overlong metadata or an unexpected payload field. Limit the encoded job to **4 KiB**; WABA/ID decimal strings ≤32 chars, name ≤255 chars, language ≤16 chars, status ≤32 chars, reason ≤128 chars. Unknown-but-well-formed provider status labels must be recorded and treated as unavailable (`UNKNOWN`), not guessed as `APPROVED`. In the worker, convert `receivedAt` to the module port's existing `occurredAt` only at the adapter boundary; do not use it to order status transitions.
- **Publication and error policy:** Messaging acknowledges the provider only **after** durable BullMQ acceptance; enqueue failure is retryable. The producer requests **5 attempts with exponential backoff starting at 5 seconds**. Background verifies the v1 envelope before invoking `metaTemplateManagementService.processTemplateStatusObservation(...)`. Malformed/unknown jobs fail visibly through the existing worker failure path (no silent successful acknowledgement), with bounded logs and no sensitive payload echo. Successful processing writes event evidence and reconciles the linked registration by Meta GET. The worker must continue to support the three existing WhatsApp job names unchanged.
- **Delivery order:** Meta webhook values alone do not update an active shop assignment. Background loads the *current* provider state using Meta GET for the known registration; stale/duplicate `APPROVED` notifications cannot undo a later `PAUSED`/`DISABLED` or clear an Admin-disabled variant. If the provider is unavailable, keep current eligibility conservative and retry/reconcile later.

The above wire contract is the architect-approved **BG003 consumer fixture**. Messaging's separate implementation must reproduce it exactly. A dedicated Shared runtime package may be proposed only if actual producer/consumer validation demonstrates this boundary cannot be maintained safely without one; do not block this task merely to create a speculative AST/translation Shared package.

**R4 — Reconciliation and drift.** The v1 handler matches only registrations that originate from Moda definitions. Persist provider event history with optional nullable registrationId for unknown external notifications; **never create a definition, locale, registration or assignment from those notifications**. Handle duplicates, out-of-order/stale statuses and missed webhooks through current Meta reads for the known identity. Store `lastObservedContentHash`, `lastObservedCategory`, `lastReconciledAt`, `driftDetectedAt` using the canonical frozen submission comparison; a status webhook is not proof that content still matches.

**R5 — Runtime safety.** Provider `APPROVED`, `PAUSED`, `DISABLED`, `REJECTED` and drift observations update provider state only; neither activate a shop variant nor clear STOP/consent suppression. A later APPROVED event cannot silently enable an assignment previously disabled by Admin. Provide explicit failure/unknown status outputs for consuming Background selector. Reconciliation may use Meta GET, ordinary WhatsApp sends may **not**.

**R5a — Admin-authored image-header sample.** If the frozen `componentsSnapshot` describes a true Meta `IMAGE` header (not a body text token containing `shopBrand.logoUrl`), verify it has the required Meta-compatible **submission sample/media handle** and supported component structure supplied through the authorised Admin/media preparation path. This module may use its server-only Meta adapter for the required provider sample-media submission operation, but must not fetch original ShopBrand URLs, resize images, upload to R2, invent sample handles, change the template category, or silently mutate an immutable compiled snapshot. Return a typed submission-blocked result when a valid sample/handle is unavailable. The merchant's READY runtime R2 image is a separate value resolved at send time by BG001, not the one sample permanently sent to every shop.

**R6 — Reliability and owned production wiring.** Keep `MetaTemplateManagementService` modular: current provider adapter/repository/status processor remain owned by `src/services/meta-template-management/`, the queue decoder/dispatch belongs in `src/workers/whatsapp.worker.ts`, and the due-registration timer belongs in `src/entrypoints/messaging.ts` or a small imported module controlled by that entrypoint. Use shared structured logging, existing BullMQ instrumentation and bounded outcomes, without a second logger, new queue, new database table or a catch-all 300+ line service. The timer is control-plane work; WhatsApp customer-message processing and final-send admission must not be delayed by Meta API calls. Provider/outbound admission tests must demonstrate no regression.

## Work Items

- [ ] Preserve the Attempt 1 `src/services/meta-template-management/` implementation; address any exact R1/R2 contract mismatches without unrelated refactoring (notably production due-registration scheduling and incomplete provider pagination).
- [ ] Add a **strict** v1 `meta-template-status-update` decoder and thin dispatch in the existing `whatsapp-events` worker, mapping `receivedAt → occurredAt` at its local port; do not alter inbound-message parsing.
- [ ] Add bounded `processDueRegistrations(25)` production polling from the messaging-worker entrypoint (60-second cadence, jitter, no process-local overlap, clean shutdown, DB CAS-safe across replicas).
- [ ] Record the exact queue JSON fixture and its deterministic event/job-identity generation in module tests so the future Messaging producer can reuse the same test vector; keep the contract in this task as the source for `ARCH-047-MESSAGING-001`.
- [x] Consume frozen `WhatsAppTemplateMetaRegistration` rows and append `WhatsAppTemplateMetaEvent` receipts. Background maintains current `providerStatus`, provider ID and drift observations, **not** authoring ASTs, translation content, shop assignments or publication permissions.
- [ ] Reuse existing sender/WABA credential resolution, Meta API error/retry conventions, BullMQ worker orchestration and structured logging; check that the present adapter maps POST/GET fields and template IDs exactly as in R1, and does not mistake incomplete paginated reads for absence.
- [x] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

## Interfaces / Contracts

**Consumes DB001** `WhatsAppTemplateMetaRegistration`, `WhatsAppTemplateMetaEvent` and immutable compiled JSON fields. **Produces/consumes** Meta's WABA template-management API via server-only client; authenticated input from the agreed Messaging producer via `whatsapp-events`. Only this module interprets provider status and writes Meta registration current-state projections.

**Ports:** `submitPreparedRegistration(registrationId)`, `processDueRegistrations(limit = 25)`, `processTemplateStatusObservation(observation)`, `reconcileRegistration(registrationId)`. The first three already exist in the Attempt 1 service; wire them rather than replace them. `processTemplateStatusObservation` receives the local `AuthenticatedTemplateObservation` after **strict parsing of the R3 BullMQ v1 payload**, not raw Meta webhooks, a duplicate authoring AST or the existing inbound-message schema. The production status event job name is exactly `meta-template-status-update`. Confirm Meta Graph POST/GET request and response mappings from R1 and R2. No Shared package publication is required solely for AST transport; the producer/consumer fixture contract is explicitly specified in R3.

## Dependencies

- `ARCH-047-DATABASE-001`


**Ready for developer Attempt 2.** The earlier cross-repository **wire-format uncertainty** that blocked Attempt 1 is resolved by the architect-approved R3 contract in this task. `ARCH-047-DATABASE-001` is its only formal prerequisite and was recorded `complete` when Attempt 1 was claimed; recheck its live canonical status before reclaiming. The Messaging **producer implementation** remains in a separately owned task and is **not** to be implemented here. Consumer tests may run against the frozen fixture without a deployed producer; the integrated webhook path is certified later by system tests.

## Enables

None in this nine-task Background set.

## Acceptance Criteria

- [ ] Inspect/re-run tests proving `POST /{WABA}/message_templates` sends only name, language, category and the exact saved `componentsSnapshot`; does not send internal binding/hash data or call Meta edit-existing-template APIs. Retain old evidence where already sufficient; add focused tests only for a demonstrated gap.
- [x] Image-header submissions use a valid authorised sample/media handle; a missing, invalid or external-original-URL sample is blocked before provider creation. Text-only templates continue unchanged. Submission never performs ShopBrand ingestion/R2 preprocessing.
- [ ] Provider tests exercise duplicate create intent, uncertain timeout, 429/5xx, definitive rejection, WABA mismatch and an incomplete/paginated Meta template lookup. Never double POST after a known or uncertain provider create; no unauthorized external adoption.
- [ ] Strict queue tests prove exact `meta-template-status-update` name and v1 payload, deterministic hash identity/job ID, multiple changes fan-out in the producer fixture, rejection of wrong name/version/unknown fields/oversized payload, and that existing `message-received`, `message-status`, `process-conversation-turn` jobs remain unaffected. Duplicate/reordered APPROVED/PAUSED/DISABLED, unsupported status, unmatched external identity and drift result in the expected bounded database evidence and provider reconciliation; provider GET failures do not falsely activate a template.
- [x] PostgreSQL integration exercises unique event identities, registration status transitions and append-only event evidence; no automatic shop activation.
- [ ] A test of the actual messaging-worker startup proves due `READY_TO_SUBMIT` registrations are scheduled and processed (or safely retried) without a manual service method call. Multi-replica claim CAS and clean timer shutdown are exercised. Existing inbound/message-status queue and final-send admission regressions pass; focused unit/build/typecheck and `git diff --check` are recorded. Live Meta webhook receipt remains with Messaging/System Test.
- [x] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [x] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

## Validation

- [ ] Run focused BG003 unit tests and disposable PostgreSQL integration; test the **actual** BullMQ worker's status-job dispatch using a fixture and its existing unknown-job rejection. Record exact commands/results; preserve currently passing Attempt 1 suites.
- [x] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [ ] Run the existing `whatsapp.worker`, `whatsapp-provider-status`, outbound/final-send admission and lifecycle regression suites affected by the new branch, plus `git diff --check`; record actual commands, pass/fail results, task-isolated restart/synchronisation and mirrored parent/implementation branch evidence.
- [x] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Meta template status webhooks are WABA events and must reach the configured Meta app callback. **The exact producer/consumer contract is frozen in R3**; the separate `ARCH-047-MESSAGING-001` task owns Meta signature verification, app subscription, per-change normalisation and successful BullMQ publication. BG003 owns only the queue consumer/decoder, provider reconciliation and database projection. BG003 may complete its bounded implementation with producer-format fixtures; it must not claim end-to-end webhook certification, which belongs to system testing. Do not create another general WhatsApp event transport.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-003`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.

**Architectural resolution:** This amendment closes the previously unagreed wire format through one architecture-owned R3 contract and fixture. Do not invent an alternate Messaging format. If actual producer work discovers an incompatible installed Shared/queue transport interface that cannot carry the bounded v1 job, report that concrete compatibility gap to `moda_architect` rather than adding an undocumented adapter.

## Completion Report

### Status

Blocked — developer Attempt 1, initially claimed `2026-10-25T19:11:32Z`. The bounded Meta submission/reconciliation module has been implemented and committed, but the full BG003 task cannot yet satisfy the queued-status-job and final-send regression criteria. Returning the cross-repository boundary to `moda_architect` for a scoped decision; not claiming Accepted/Complete.

### Files Changed

Implementation repository (`moda-interact-background/`, commit `568eed8`):

- `src/services/meta-template-management/contracts.ts`
- `src/services/meta-template-management/index.ts`
- `src/services/meta-template-management/meta-graph.adapter.ts`
- `src/services/meta-template-management/repository.ts`
- `src/services/meta-template-management/service.ts`
- `tests/unit/services/meta-template-management/meta-management.test.ts`
- `tests/integration/arch047-meta-template-management.integration.test.ts`

No parent architecture file, `_index.md`, existing WhatsApp worker, Messaging repository, or database schema was changed by this implementation commit.

### Work Completed

- Implemented module-local create-only Meta submission, frozen compiled-component transport, private server-side WABA credential use, image-header sample validation and provider-name collision blocking.
- Persisted a claim and POST intent before provider I/O; handled unknown create outcomes without blindly reposting; exposed reconciliation and bounded due-processing ports.
- Added Prisma-backed append-only Meta event evidence, event identity deduplication, provider projection and drift detection; no automatic merchant/shop activation or external-template adoption.
- Added injectable authenticated status-observation processing with repeat/reorder handling. This is **not** the production `whatsapp-events` queue decoder/handler.
- Used `@modainteract/moda-interact-shared/logging` and preserved/propagated unexpected errors; logging and compensation-error behavior are covered in focused unit tests.
- Implemented 16 new unit tests and one disposable-PostgreSQL integration scenario with multiple database assertions.
- Developer terminal evidence records a successful implementation commit and push: `568eed8` (`feat(arch-047-background-003)`) to `origin/task/ARCH-047-BACKGROUND-003`. The recording does **not** establish a later parent task-branch push or architect acceptance.

### Validation Results

Evidence: uploaded terminal recording `typescript(20261025-192158)` and the matching code snapshot `moda-interact-workspace-ARCH-047-BACKGROUND-003.zip`.

| Check | Command / evidence | Outcome |
|---|---|---|
| Dependencies | `npm ci`; `npm run prisma:generate` | Completed; npm reported 20 audit advisories (8 moderate, 12 high), not investigated in this task |
| Build/typecheck | `npm run build` (`prisma:generate` followed by `tsc`) | Passed; no TypeScript errors reported |
| Focused lint | `npx eslint src/services/meta-template-management tests/unit/services/meta-template-management` | No ESLint diagnostics reported in captured run |
| Unit + existing status/worker regression | `npx vitest run tests/unit/services/meta-template-management/meta-management.test.ts tests/unit/workers/whatsapp.worker.test.ts tests/unit/services/whatsapp-provider-status.service.test.ts` | **69/69 passed in 3 test files** (16 new, 53 existing) |
| Disposable PostgreSQL integration | `npm run test:integration -- tests/integration/arch047-meta-template-management.integration.test.ts` | **1/1 passed**, real Prisma persistence, concurrent claims, duplicate observation, reconciliation, stale CAS and no variant activation |
| Local diff check | `git diff --check` appears in terminal during patch application | No whitespace diagnostic shown; final post-commit diff check is not independently recorded |
| Branch publication | `git commit` and `git push -u origin task/ARCH-047-BACKGROUND-003` | Background implementation commit `568eed8` pushed |
| Final outbound-admission regression | Not present in captured commands | **Not run/verified** |
| Template-status BullMQ producer/consumer integration | No agreed ARCH-047 Messaging producer/job contract in supplied snapshot | **Not implemented/tested** |
| Real Meta webhook end-to-end | Separate Messaging/system-test boundary | **Not run** |

The existing database integration test is a **single combined scenario**, not a comprehensive matrix of independent database tests. It runs against the disposable test database (`TEST_DATABASE_URL`, `MODA_DISPOSABLE_INTEGRATION=1`); it does not exercise a BullMQ template-status job because that producer/consumer contract is absent.

### Deviations

- Did not wire a `message_template_status_update` job into `whatsapp-events`, or implement wrong-job-name/version rejection: the agreed Messaging producer and canonical cross-repository queue format are absent from this snapshot. A guessed local envelope would violate the task's explicit queue-contract stop condition.
- Implemented module-owned due-processing entrypoint only; no production scheduling caller or independent new queue was added.
- Did not run the existing final-send admission regression suite, so that acceptance condition is left unchecked.
- An initial patch-application command failed because the downloaded patch was not yet at the named local path; a subsequent application and the committed implementation are visible in the recording. The failed command is not counted as successful validation.

### Assumptions

- `ARCH-047-DATABASE-001` was `complete` at claim time per the canonical task record. The tested Prisma schema provides the expected registration/event tables.
- Admin owns preparation of immutable compiled components and authorised image sample handles; Background neither recompiles the AST nor ingests original merchant images.
- Messaging owns verification and publication of future Meta template-status events. Background accepts only validated/authenticated observation data at its current module-level port.

### Unresolved Issues

1. `ARCH-047-MESSAGING-001` is **planned but not defined** in the uploaded architecture. Agree and materialise its authenticated template-status BullMQ payload/job contract; then assign the correct owner to wire the existing Background `whatsapp-events` dispatcher and cover wrong name/version rejection.
2. Architect to decide whether this BG003 task should remain blocked pending that integration or be explicitly **narrowed** to the now-validated module, with a separate dependent queue-integration task. Do not silently treat the present module as a wired consumer.
3. Run and record the applicable outbound-admission/final-send regression suite before full BG003 acceptance. No passing result is claimed from the current terminal log.
4. Inspect task-isolated start-of-attempt synchronisation evidence and both published mirrored task branches during review. The task preparation metadata documents worktree paths and initial synchronisation; the terminal recording independently confirms the implementation worktree and background push only.

### Architectural Concerns

The missing Messaging queue contract is a cross-repository interface gap. No new private schema or unapproved Shared package should be created inside Background. Do not infer readiness for production Meta webhook processing, background polling or customer sends from the module-only tests. There is no evidence of changing the consent, STOP or final outbound-admission safeguards.

## Architect Review

### Review Status

Changes Requested — Attempt 1 contract/call-site correction; task returned to `ready` for developer Attempt 2. This is **not** acceptance of the implementation.

### Review Notes

The supplied task worktree contains developer Attempt 1 implementation commit `568eed8` and its Completion Report, with a module-local Meta adapter, repository, service, contracts and focused tests. Attempt 1 deliberately stopped short of the production `whatsapp-events` queue decoder/handler because the Messaging producer wire format was unspecified; it also records no production due-registration startup caller and no verified outbound-admission regression. This amendment fixes the producer/consumer v1 envelope and gives an exact in-repository correction scope while preserving earlier completed module behaviour. Developer reclaims the **same** task as Attempt 2; do not start a new BG003 task or overwrite the historical Completion Report.

### Reviewed Files

- `docs/decisions/background/ARCH-047/BACKGROUND-003-manage-meta-template-submission-and-status.md` (current task and Attempt 1 evidence)
- `src/services/meta-template-management/{contracts,service,repository,meta-graph.adapter,index}.ts` (supplied Background snapshot)
- `src/workers/whatsapp.worker.ts` and `src/entrypoints/messaging.ts` (existing queue consumer and production startup)
- `docs/decisions/admin/ARCH-047/ADMIN-006-submit-and-monitor-meta-template-approvals.md` (completed DB-intent producer)
- `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md` (authoritative boundaries)

### Validation Reviewed

Attempt 1 Completion Report records 69/69 passing focused unit/status-worker tests, one disposable PostgreSQL integration test and a passing build/lint, but these commands were **not rerun** during this task-definition amendment. Neither BullMQ template-status dispatch nor the final-send regression was run in Attempt 1; both remain mandatory for Attempt 2.

### Architecture Conformance

The module-local create-only, no-AST, no-external-adoption approach matches ARCH-047. The **execution integration is incomplete**: no exact queue v1 decoder/worker handler, no durable-request production polling caller and no final-admission regression evidence. The R3 contract has been narrowed to an architecture-owned, bounded existing-BullMQ job without introducing a new Shared authoring package or modifying Messaging's ownership.

### Follow-up

**Attempt 2 correction contract (required source and tests):**

1. Add the R3 v1 strict decoder and `meta-template-status-update` `switch` branch plus telemetry job-name registration in `src/workers/whatsapp.worker.ts`, delegating only to the existing BG003 observation service. Tests must reject wrong job name/schema version and preserve all prior WhatsApp jobs.
2. Connect `processDueRegistrations(25)` to `src/entrypoints/messaging.ts` or a dedicated imported startup helper on a bounded, nonoverlapping 60-second cadence with safe shutdown and multi-process DB CAS protection; include production-startup tests.
3. Compare the existing Meta adapter/Prisma service to R1–R2 and correct **only** demonstrated request, state, retry, pagination or snapshot-hash mismatches; do not churn already-conformant module code merely to force a new commit.
4. Rerun focused unit, DB integration, WhatsApp-worker and final outbound-admission regression tests; record any baseline conditions, new source changes, explicit result counts, and the canonical developer worktree/branch synchronisation evidence.
5. Preserve Meta-authored-only provenance, shop non-activation, STOP/consent and no checkout mutation. Do not implement the separate Messaging producer or claim the system test. On completion set task `review`, update the developer Completion Report with Attempt 2 evidence and return for architect/developer review through the configured completion mode.

## Execution Ownership Amendment

- Date: 2026-10-25.
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, dependency, task scope, acceptance criteria and validation requirements.
- Dependency check: `ARCH-047-DATABASE-001` is `complete` in its canonical task record.
- Claim: Attempt 1 is claimed by `developer` at `2026-10-25T19:11:32Z` after canonical worktree preparation and synchronization.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-BACKGROUND-003`, branch `task/ARCH-047-BACKGROUND-003`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-BACKGROUND-003`, branch `task/ARCH-047-BACKGROUND-003`, created from current Background `origin/main` because no BACKGROUND-003 task branch existed locally or remotely.
- The parent task branch was merged with current workspace `origin/main`; it is intentionally ahead of its previously published task-branch tip and will be published with this claim. No implementation changes were made during preparation. No branch was merged into `main`.
