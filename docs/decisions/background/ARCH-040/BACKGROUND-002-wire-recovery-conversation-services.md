---
id: ARCH-040-BACKGROUND-002
architecture_id: ARCH-040
title: Wire recovery conversation services into live Background paths
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-040-DATABASE-001
  - ARCH-040-BACKGROUND-001
enables:
  - ARCH-040-SHOPIFY-001
  - ARCH-040-WOOCOMMERCE-001
  - ARCH-040-SYSTEM-TEST-001
  - ARCH-040-SYSTEM-TEST-002
  - ARCH-040-SYSTEM-TEST-003
created: 2026-10-14
updated: 2026-10-18
---

# ARCH-040-BACKGROUND-002 — Wire recovery conversation services into live Background paths

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. On 2026-10-17, dependency-frontier reconciliation confirmed `ARCH-040-DATABASE-001` and `ARCH-040-BACKGROUND-001` complete and promoted this task to ready at Attempt 0. Its canonical parent task branch/worktree were created from `origin/main` solely to record that readiness transition.

### Developer Ownership Amendment

On 2026-10-17, `/moda_developer_create ARCH-040-BACKGROUND-002` was invoked to take over this ready task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_background`, repository ownership, scope, dependencies and acceptance criteria are unchanged. Attempt 1 is claimed by `developer`. The canonical implementation worktree was created from current `origin/main`; the shared implementation source checkout was not switched or modified.

### Developer Attempt 2 Claim

On 2026-10-18, `/moda_developer_create ARCH-040-BACKGROUND-002` claimed Attempt 2 after Attempt 1 was returned Changes Requested. Both explicit dependencies were re-resolved as complete. The canonical parent and implementation worktrees were reused and synchronized; no implementation changes were present at claim time. Attempt 2 is scoped to the corrective integration and runtime tests listed below, plus any narrowly required implementation changes they expose.

## Objective

Integrate the accepted BACKGROUND-001 service operations into **all actual runtime entrypoints** for recovery-linked AI turns, queued HUMAN commands, follow-up jobs and final WhatsApp provider admission; verify end-to-end worker behaviour, concurrency and receipts without reimplementing the policies.

## Context

A passing service unit test does not mean a running worker invokes the new control, restriction, screening and credit gates. This task owns application composition, job plumbing, worker registration and exact call-site coverage for both Shopify- and Woo-produced durable commands. It must not wait for the Woo hosted API or Shopify UI implementation.

## Scope

- Wire accepted BACKGROUND-001 methods into existing Background runner/scheduler/provider call paths. Add the smallest required durable command relay/worker entrypoint, startup/queue wiring and retry/reconciliation integration.
- Keep customer WhatsApp inbound persistence, agent turn scheduling, existing Meta transport, provider status reconciliation, recovery billing and existing recovery follow-up scheduling intact except for necessary checks at approved integration points.
- Add integration and race tests that execute **real call sites** against disposable PostgreSQL/Redis and a mock provider. Avoid a new chat service/process solely for human replies.

## Out of Scope

- No reimplementation of BACKGROUND-001 policy or another command status machine.
- No new Prisma schema, Shopify route/controller, WooCommerce HTTP route/WordPress plugin, merchant UI, new Shared contracts or admin dashboard.
- No global worker serialization, second follow-up scheduler, second WhatsApp sender, second recovery credit system or automatic suspension on heuristics.

## Requirements

### Required integration call-site matrix

| Existing execution boundary | Invocation and safety requirement |
|---|---|
| `src/workers/whatsapp.worker.ts` / `src/services/conversation-turn-processor.service.ts` | Preserve inbound/customer recording; invoke the AI mode/revision gate before agent processing, after awaited model/tool work and on final outbound admission. HUMAN/stale results suppress only the unsent automated reply, not customer ingress. |
| `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts` | Invoke the authoritative final send-admission/fencing operation for recovery AI and HUMAN sends before irreversible Meta submission. Respect existing AGENT/AUTOMATION caps and recipient checks; do not cast HUMAN into the old automated sender contract. |
| Durable `MerchantConversationSendCommand` relay/consumer | Claim/lease accepted commands by stable command ID, invoke HUMAN owner/window/restriction/screening policy, use existing WhatsApp text/template delivery, persist provider-accurate `ConversationMessage` / command statuses; provide bounded retry, restart recovery and duplicate suppression. Both Shopify and Woo insert into this same command source. |
| `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts` and existing recovery follow-up worker | Invoke shared recovery follow-up claim and credit admission; scheduled no-response follow-up retains customer-replied suppression and checks HUMAN mode. Merchant-approved sequence-2 template uses the same attempt/credit, not another job/scheduler. |
| `src/services/whatsapp-provider-status.service.ts` and existing recovery billing reconciliation | Reuse provider receipts / status transitions for HUMAN and follow-up, finalise or compensate existing recovery credits once, preserve unknown-provider outcomes and never fabricate SENT on accepted command alone. |
| Runtime startup/shutdown + job queue configuration | Ensure command relay actually runs, has bounded concurrency/backpressure, restart-safe state and no dangling registration; if polling, document cadence and retry semantics. No new deployment unless demonstrated necessary. |

### Race-safe admission is required

- Prove merchant Take Over committed before AI provider submission prevents the unsent AI response, including a stale model reply completing after Resume AI.
- Prove shop suspension committed before HUMAN final admission prevents even a previously accepted/leased command; restore does not automatically replay terminally denied commands. Provider request already submitted first is not falsely described as recalled.
- No long DB transaction surrounding provider HTTP; use BACKGROUND-001's documented reservation/fence and test the exact precedence/limits at real call sites.
- At most one sequence-2 send/credit, same `Conversation.id` for initial/AI/HUMAN/follow-up, no repeated sends or rate counter amplification on queue replay.
- When free-text window closes while queued, do not dispatch text or silently substitute templates. Reject appropriately; no extra recovery credit.

## Concrete implementation blueprint — production wiring only

**Baseline reviewed:** `moda-interact-background` source in `moda-interact-workspace(20261017-115551).zip`. All `src/...` existing paths below were found in that snapshot. BG001's `src/services/recovery-conversation/` files are **proposed new dependencies** and must have been implemented/accepted before this task begins. Do not duplicate their policy functions here.

### 1. Exact existing files to modify

| Actual file | Where to connect BG001 methods | Required effect |
|---|---|---|
| `src/services/conversation-turn-processor.service.ts` | Extend injected `ConversationTurnProcessorDependencies` with ownership/fencing port. Capture control revision at start/claim, validate after loading recovery context, before an `AUTOMATION` clarification/terminal send, after `runCommerceAgentAfterAdmission` returns, and before `admission.sendPreparedText`. Preserve `hasChanged` inbound-version detection as a **separate** condition. | AI and automation do not send if HUMAN owns the conversation or if the original control revision is stale. A suppressed turn completes/releases safely; never drop the inbound customer message or accidentally schedule an AI response during HUMAN mode. |
| `src/workers/whatsapp.worker.ts` | Inject the accepted BG001 ownership port when constructing `ConversationTurnProcessor`; preserve inbound `message-received` and `message-status` job handlers, audio handling and `process-conversation-turn` registration. | Real workers use the same revision policy; no duplicated inference logic. Audit its direct voice-fallback `outboundWhatsAppAdmissionService.sendText` path for recovery-only ownership fencing. |
| `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts` | Invoke BG001's **atomic final send fence** for all recovery-linked AGENT/AUTOMATION prepared text and template sends, and for HUMAN sends through an approved narrow adapter. Keep existing `revalidateBeforeProvider`, `sendWhatsAppText`/`sendWhatsAppTemplate`, `markSent`, and failure/unknown behaviour. | This is the final provider-boundary choke point. Do not merely add another early check in `ConversationTurnProcessor`. `OutboundAdmissionInput.senderType` remains AGENT/AUTOMATION; **do not cast HUMAN into it or record OUTBOUND_AUTOMATED_MESSAGE usage for human messages**. |
| `src/services/outbound-whatsapp-admission.service.ts` | Expose any narrow forwarding method the existing delivery facade needs to pass the immutable control revision/send identity; retain automatic admission API semantics. | One transport and provider-receipt path, but separate human versus automated quota admission. |
| `src/services/checkout-recovery/recovery-outreach-follow-up-processor.service.ts` | Immediately before its existing `markNoResponseIfWaiting`/`getOrCreateFollowUp`, consult BG001 AI ownership and sequence-2 claim policy. Recheck at final template send. Preserve checkout/recovery lock, recipient suppression, template selector, `RecoveryBillingService`, and `RecoveryOutreachFinalizationService`. | Scheduled follow-up remains no-response-only and cannot send during HUMAN control. A human template uses the same unique sequence-2 row and recovery credit source rather than a second scheduled job. |
| `src/workers/recovery-outreach-follow-up.worker.ts`, `src/services/checkout-recovery.service.ts` | Keep existing `processRecoveryOutreachFollowUp` job delegate; pass the new policy dependencies into the existing processor if constructor injection requires it. | No new follow-up queue, job identity or scheduling cycle. |
| `src/services/whatsapp-provider-status.service.ts` | On an existing HUMAN outbound message status event, reconcile its linked send command and outreach attempt/credit through BG001's reconciliation method without changing the canonical status ordering. Reuse `canApplyProviderStatus`. | DELIVERED/READ/FAILED receipts update the **same message**, never a shadow delivery row; duplicate and out-of-order provider events are harmless. |
| `src/entrypoints/messaging.ts` | Start the new durable human command dispatcher alongside `createWhatsappWorker()`, and register its cancellation/drain in the existing worker shutdown/resource list. | A production messaging deployment consumes commands accepted by either Shopify or WooCommerce. |
| `src/index.ts` | Register the same human dispatcher in the combined local development worker entrypoint and include its orderly cleanup. | Local development exercises the real path; no orphan service running only in tests. |

`src/entrypoints/recovery.ts` remains the owner of the existing recovery worker and its queue; change it **only if** a demonstrated dependency-injection/startup requirement exists. Do not add a new Render service or route simply to host the command consumer. Review any direct calls to `whatsAppService.sendWhatsAppText` (e.g. routing guidance) and document whether they are recovery-linked; do not globally apply recovery ownership to unrelated provider traffic.

### Sender attribution and inbound-time wiring — actual existing methods

- `src/services/conversation.service.ts` currently implements `toAgentMessage` as `direction === INBOUND ? user : assistant`, which would incorrectly present HUMAN messages as if CommerceAgent said them. Update the history query/projection to carry `senderType`, and represent merchant-authored outbound content as separately labelled, **untrusted** context. Keep AI/automation and customer attribution correct; do not add merchant content to privileged model instructions. Ensure the real history used after a Take Over → Resume AI cycle includes recent HUMAN messages and surrounding customer messages in chronological order, within existing token bounds. If other history readers share this projection, preserve their non-recovery behaviour.
- `ConversationService.receiveMessage()` currently updates `lastInboundAt: occurredAt`. Replace this overwrite with a database-safe monotonic max of valid verified customer inbound `occurredAt` and existing `lastInboundAt`; apply compatible behaviour to `lastMessageAt` and verified inbound audio events, including duplicate/out-of-order webhook delivery across processes. Do not infer the window from text/audio transcription completion or outbound provider receipts. Preserve inbound `inboundVersion` and idempotent message persistence.
- `src/services/conversation-turn-processor.service.ts` must use the new sender-aware history and a *captured* original revision on the awaited AI turn. An obsolete model completion remains rejected after HUMAN→AI, even when mode has returned to AI. No messages are lost from the canonical transcript.


### 2. New dispatcher — single durable source, no new queue required

Add a small module such as `src/services/recovery-conversation/merchant-send-dispatcher.ts` (or `src/workers/merchant-conversation-send.worker.ts` if a worker abstraction is preferred) that **polls the accepted PostgreSQL command table**. This is preferable to requiring Shopify and WooCommerce to publish to Redis after database commit. Do not introduce a second BullMQ queue/outbox publisher unless a measured need or an existing approved primitive justifies it.

- A bounded poll discovers `ACCEPTED` and due retryable commands by indexed `nextAttemptAt`/lease expiry; defaults proposed for first version: **batch <= 25 per poll, at most 4 concurrent processing calls, 3-second poll interval**, all configurable/test-injectable. Values are provisional operating defaults, *not measured capacity*.
- Claim each row using BG001's PostgreSQL lease/CAS operations (e.g. `FOR UPDATE SKIP LOCKED` in a short transaction); no global per-shop lock or long transaction around network I/O. Stop/drain on shutdown; startup recovers expired leases and pending commands.
- Re-load command by durable `commandId` and expected lease token. Use frozen payload/recipient, owner revision, current restriction, send window, recipient suppression, template eligibility and rate policy. Route allowed work to the existing WhatsApp delivery adapter with BG001's final fence, then reconcile message/command/attempt/credit state.
- A failed or disconnected poll does not mark a command SENT; transient errors use bounded backoff with stable command identity. A provider-unknown result is reconciled, never blindly resent. The dispatcher itself does **not** rewrite policy rules or choose different template text.
- Add structured log events for `human_command.claimed`, `.suppressed`, `.submitted`, `.unknown`, `.reconciled` using shared logger and IDs/reason codes only. Do not log message bodies, names, phone numbers, secrets or administrative notes. Reuse approved framework instrumentation; no custom duplicate HTTP/queue metrics.

### Platform-neutral scheduling matrix — do not add platform-specific queues

| Trigger | Existing/new mechanism | Owning component | Exact contract |
|---|---|---|---|
| Inbound verified WhatsApp event | Existing BullMQ messaging/turn consumer | Existing WhatsApp ingress and Background worker | Persist/dedupe inbound; check AI ownership before generation and final provider admission |
| Automatic no-response recovery follow-up | Existing delayed `recovery-outreach-follow-up` BullMQ job | Existing recovery worker | Suppress if engaged, HUMAN-owned, terminal or sequence-2 already claimed; share BG001 claim/fence |
| Merchant reply or eligible post-window follow-up from **either** platform | **One** bounded PostgreSQL dispatcher polling `MerchantConversationSendCommand` | Existing messaging worker registered in `entrypoints/messaging.ts` and local `index.ts` | Read indexed due records; lease with row lock/CAS; BG001 policy; final durable permit; one existing Meta transport |
| UI reads provider/command status | Existing platform-specific HTTP/browser refresh | Shopify screen / Woo screen through hosted API | Read-only bounded refresh, not BullMQ scheduling or delivery |

Do **not** implement `SHOPIFY` versus `WOOCOMMERCE` branches in the dispatcher, Background services, queue names, billing, provider reconciliation, or admission. Shared identifiers are `shopId`, `conversationId`, `recoveryId`, `commandId` and original attempt IDs; a shop's provider credentials may be loaded through existing canonical shop adapters, never through Woo WordPress or Shopify browser calls in the worker.

Use the configurable v1 defaults already specified below (3-second polling, batches <=25, <=4 concurrent), not hardcoded capacity promises. Poll only indexed due `ACCEPTED` / safe retryable work; recover expired *pre-admission* leases, but a `DISPATCH_ADMITTED`/`UNKNOWN` operation is reconciliation-only. Multi-replica scheduling must use PostgreSQL locks/leases and stable command IDs. A timeout or poll exception must not create new command IDs or new follow-up jobs. Stop/drain the single relay with the existing messaging-worker lifecycle. No new Render service, queue or Redis publisher is needed for merchant sends.


### 3. Explicit execution order, with concrete call sequences

**AI inbound turn (existing queue):**

```text
WhatsApp inbound verified/persisted (unchanged)
  -> process-conversation-turn job, capture controlRevision = R
  -> checkAutomatedTurn(conversationId, R, "start")
  -> reserve existing automated outbound if eligible
  -> model / tool await
  -> checkAutomatedTurn(conversationId, R, "after-await")
  -> existing hasChanged(inboundVersion)
  -> final provider admission under BG001 fence using R
  -> existing WhatsApp transport and message receipt flow
```

**Merchant HUMAN text/template (both producers):**

```text
Shopify server action OR WooCommerce authenticated hosted API
  -> commit same MerchantConversationSendCommand in PostgreSQL
  -> messaging dispatcher polls and leases command ID
  -> BG001 validates shop/recovery, HUMAN revision and frozen recipient
  -> BG001 validates customer window or unique sequence-2 template claim
  -> BG001 validates restriction, rate/abuse, recipient/plan rules
  -> BG001 durable final send admission/fence
  -> existing WhatsApp provider transport (one submission)
  -> canonical ConversationMessage(senderType=HUMAN) + command outcome
  -> existing Meta provider status / follow-up credit reconciliation
```

**Existing automated follow-up:**

```text
recovery-outreach-follow-up BullMQ job (unchanged)
  -> existing checkout/recovery lock, due/no-response checks
  -> reject if HUMAN-controlled / stale control revision
  -> unique sequence-2 claim via BG001 (same attempt/credit)
  -> existing template + RecoveryBillingService admission
  -> BG001 final fence and original WhatsApp template send
  -> existing attempt finalization and provider receipts
```

### 4. Tests must prove the *real* injection points, not mocks alone

Add focused tests alongside the repo's existing `tests/unit/services/conversation-turn-processor/`, `tests/unit/services/outbound-whatsapp-admission/`, `tests/unit/services/checkout-recovery/recovery-outreach-follow-up-processor.service.test.ts`, `tests/unit/services/whatsapp-provider-status.service.test.ts`, and worker tests. For actual database/worker proof, use the existing disposable PostgreSQL/Redis test integration conventions (see `tests/integration/conversation-turn-scheduling.integration.test.ts`).

**Required integration matrix:**

1. Real WhatsApp worker receives customer inbound in HUMAN mode: CUSTOMER transcript persists; no CommerceAgent reply or automated clarification goes out.
2. AI was running at revision R; merchant takes over and later resumes AI at R+2; the old AI response never sends. Independently test takeover immediately before final provider admission and immediately after irrevocable admission.
3. Shopify-origin and Woo-origin **indistinguishable** command rows each result in exactly one HUMAN transcript message; no HTTP/API/Shopify code is imported by Background.
4. Two dispatcher replicas compete for one accepted command: only one valid provider submission. Crash after lease/after provider request tests UNKNOWN and restart recovery, with no blind resend.
5. Human command was accepted before suspension, but shop restriction commits before final send admission: blocked without Meta send or credit. Later restore does not release a terminal rejection.
6. Human text queued while window open, processed after 24-hour window closed: denied (not silently changed to template). Human-approved template allowed only when sequence-2 claim remains available.
7. Scheduled no-response follow-up and manual HUMAN follow-up race: one sequence-2 attempt and one credit identity; existing engaged/terminal recovery suppression remains intact.
8. Rate-limit/spam denial and Redis outage: no provider calls and no duplicated quota-counter charge on retry. Other AI messages are unaffected by *human-only* suspension.
9. Duplicate/out-of-order SENT/DELIVERED/READ/FAILED provider receipts update canonical message/command, without phantom SENT or double credit. A definitive provider failure is handled differently from provider uncertainty.
10. Production `src/entrypoints/messaging.ts` and local `src/index.ts` actually start/stop the command dispatcher; test startup registration and clean shutdown, not only direct service calls.

**Stop point:** BG002 finishes only when these entrypoints, provider boundary, follow-up route and reconciliation are proven to invoke BG001. It does not add new database models, duplicate policy services, UI routes or Shopify/Woo tasks; acceptance requires end-to-end tests with mocked Meta and disposable dependencies where available.

### Integration acceptance traces that must be executable

1. Both authenticated merchant producers commit the **same command shape**; the single DB dispatcher never accesses an origin-platform field. Test equivalent commands via seeded producer-neutral PostgreSQL fixtures (neither Shopify nor Woo implementation is a BG002 prerequisite).
2. Inbound customer messages continue through existing BullMQ; verified out-of-order and audio inbound keep monotonic `lastInboundAt`, and an old message cannot prematurely close the active window.
3. CommerceAgent resumed after HUMAN intervention receives properly attributed merchant-authored history, not forged `assistant` messages; an obsolete AI turn never sends after a mode revision cycle.
4. Automated follow-up remains on its original delayed BullMQ queue and uses the same sequence-2 claim as a HUMAN template. A previously scheduled *unclaimed* row can be won exactly once by HUMAN; a claimed/UNKNOWN/sent row cannot be stolen.
5. All recovery-linked AI/AUTOMATION and HUMAN provider sends reach one final durable admission boundary. `CLAIMED` does not send, a committed suspension/takeover before permit denies, a permit-first provider request may complete later, and a crash/unknown result cannot cause a blind duplicate Meta submission.
6. Two messaging worker replicas poll concurrently: one command claim/permit, bounded concurrency and correct restart/shutdown. Redis polling is **not** used for merchant command discovery; Redis/BullMQ continues for existing inbound/follow-up jobs.


## Work Items

- [x] Wire AI owner/revision checks into turn start, awaited-agent continuation and final provider-send path, including queued retry suppression.
- [x] Register and run a durable HUMAN command consumer using BACKGROUND-001 service APIs, existing transport, command idempotency and bounded worker lifecycle; reconcile linked provider receipts.
- [x] Wire scheduled and merchant-initiated sequence-2 follow-up to the same existing processor/credit identity; preserve scheduled no-response suppression and prove the race at the shared claim and dispatch path.
- [x] Integrate final suspension, abuse screening and provider-fence checks at the irreversible send handoff, not only at claim/dequeue time.
- [x] Wire HUMAN provider-status receipt reconciliation to the linked command and recovery attempt while preserving canonical status ordering. Credit admission/finalisation remains on the existing dispatcher path and duplicate receipts do not create another credit identity.

### Attempt 2 Corrective Work Items

- [x] Reconcile verified HUMAN provider-status receipts with the linked send command and recovery attempt while preserving canonical status ordering. Duplicate/out-of-order receipts are covered by the PostgreSQL integration case; legal `DISPATCH_ADMITTED` and `UNKNOWN` command convergence is covered by unit tests.
- [x] Exercise normalized WhatsApp worker job ingress and the HUMAN turn-processor gate: customer messages persist and enqueue, HUMAN suppresses automated generation, and the existing AI integration path remains covered.
- [x] Exercise two equivalent producer-neutral command rows through the same dispatcher; each produces exactly one HUMAN transcript message and provider submission, with no platform-specific Background branch or import.
- [x] Test a HUMAN text command whose customer window expires before dispatch; it is denied without template substitution. The race integration covers an eligible sequence-2 template and rejects a retry after the unique slot is claimed.
- [x] Race scheduled no-response and merchant sequence-2 claims at the shared policy boundary, then dispatch only the winning merchant command; assert one attempt and one credit admission/confirmation identity.
- [x] Test the shared dispatcher lifecycle helper used by both `src/entrypoints/messaging.ts` and `src/index.ts`; verify start and orderly async close registration.

## Interfaces / Contracts

- BACKGROUND-001 is the authoritative service/policy implementation; this task consumes its exports rather than duplicating decisions.
- Consolidated DATABASE-001 defines durable entities/commands. No new Shared publication. Jobs may carry only stable command IDs, with commands loaded and authorised via PostgreSQL.
- Actual source paths above are inspected from the October 17 snapshot; retain repository-local modularisation and adapt to accepted code as needed, documenting deviations in Completion Report.

## Dependencies

- ARCH-040-DATABASE-001
- ARCH-040-BACKGROUND-001

## Enables

- ARCH-040-SHOPIFY-001
- ARCH-040-WOOCOMMERCE-001
- ARCH-040-SYSTEM-TEST-001
- ARCH-040-SYSTEM-TEST-002
- ARCH-040-SYSTEM-TEST-003

- [x] Production call sites and worker entrypoints implement the platform-neutral scheduling matrix with **one** PostgreSQL human-command dispatcher; neither merchant platform publishes a post-commit BullMQ job.
- [x] Tests exercise sender-aware agent history, monotonic verified inbound timestamps, the single original sequence-2 row and final durable send-admission behavior. The exact split between unit and disposable runtime evidence is recorded under Deviations and was accepted in the architect review.

## Acceptance Criteria

- [x] Existing-file execution paths and all three sequences in the integration blueprint have exercised call sites and asserted outcomes; dispatcher lifecycle registration is shared by production and local entrypoints.
- [x] Producer-neutral command fixtures each deliver one HUMAN transcript message through the existing WhatsApp path, with linked receipts and shared billing identity; platform producer implementations remain independent.
- [x] Takeover/suspension precedence and queue retries are demonstrated at actual send admission; unrelated AI and inbound behavior remain covered.
- [x] Scheduled no-response and merchant post-window follow-up share one sequence-two attempt and credit identity, without a second scheduler.
- [x] Neither Shopify nor WooCommerce implementation is a dependency of this task, and no additional runtime deployable is introduced.

## Validation

- [x] Focused integration and unit tests for BG002 call sites: wiring suite 6 files / 88 tests; provider-status unit suite 1 file / 29 tests; PostgreSQL/Redis runtime suite 1 file / 15 tests.
- [x] Disposable PostgreSQL/Redis runtime cases cover competing leases, suspension-before-permit, UNKNOWN restart, rate denial, credit repair, producer-neutral parity, expired-window denial, scheduled/merchant sequence-two race, and linked receipt ordering.
- [x] Provider status ordering and command convergence cover duplicate/out-of-order SENT/DELIVERED/READ/FAILED events, plus `DISPATCH_ADMITTED`/`UNKNOWN` reconciliation; build and lint pass.
- [x] End-to-end recovery follow-up credit/idempotency tests use actual Background call sites, including scheduled/manual sequence-two competition, definitive failure compensation, and confirmed-send credit repair.
- [x] Typecheck, changed-file lint, applicable build/test scripts and `git diff --check` for the implemented slice. Build, lint, focused suites, and implementation diff hygiene passed; accepted test-boundary deviations are listed in the Completion Report.

## Stop Condition

After implementing only the listed scope and completing validation, record worktree, tests, and files in Completion Report, set task to `review`, return to `moda_architect` and **STOP**. Do not execute another task automatically.

## Implementation Notes

Use the canonical launcher-resolved dedicated parent/implementation task worktrees and matching `task/<TASK_ID>` branches. Check the repository scripts before selecting validation commands. Use the published `@modainteract/moda-interact-shared/logging` API; log stable identifiers and reason codes only, never message bodies, credentials, personal details or admin notes. Avoid editing `docs/decisions/**/_index.md` until this architectural session is explicitly closed. This architecture targets fresh development-schema validation; do not add historical migration/backfill work.

## Completion Report

### Status
Complete — Attempt 2 was accepted in architect review, and the developer explicitly completed the task on 2026-10-18. Attempt remains 2; no merge to `main` was performed.

### Files Changed
Baseline implementation commit `837686b983acc93263afdbd8b1fe4bf82186ac07` changes 26 files in the Background task worktree. Attempt 2 correction commit `ea526a6` adds HUMAN provider-status command convergence, sequence-two failure receipt reconciliation, normalized worker-job coverage, a shared dispatcher lifecycle helper used by both entrypoints, and the focused test scenarios. Both commits are published on `origin/task/ARCH-040-BACKGROUND-002`.

### Work Completed
Attempt 1 implementation remains published as `837686b983acc93263afdbd8b1fe4bf82186ac07`: central AI revision gates, final outbound fencing, PostgreSQL-leased HUMAN command dispatcher, bounded polling/processing, restart-safe UNKNOWN handling, scheduled/merchant sequence-2 policy sharing, follow-up credit repair, and production/local dispatcher registration. Attempt 2 adds linked HUMAN receipt reconciliation, normalized worker job parsing/persistence coverage paired with the turn-processor HUMAN suppression test, producer-neutral parity, expired-window/no-fallback, sequence-two claim/send/credit competition and retry denial, and shared lifecycle start/close coverage.

### Validation Results
Final rerun on 2026-10-18 against implementation commit `ea526a6`:
- `npm run test:arch040-background-wiring`: passed, 6 files / 88 tests.
- `node_modules/.bin/vitest run tests/unit/services/whatsapp-provider-status.service.test.ts`: passed, 1 file / 29 tests.
- `npm run test:arch040-background-runtime:postgres`: passed, 1 file / 15 tests against disposable PostgreSQL/Redis and the Background-local WhatsApp emulator.
- `npm run build`: passed (Prisma client generation and TypeScript compilation).
- `npm run lint`: passed.
- `git diff --check`: passed before commit.
- Implementation HEAD and `origin/task/ARCH-040-BACKGROUND-002` both resolve to `ea526a6`.

The architect accepted the documented evidence boundaries: producer parity is proven with equivalent origin-neutral database command fixtures rather than platform-owned producers; inbound persistence and HUMAN suppression are tested at their production worker/turn-processor boundaries rather than in one end-to-end BullMQ process; and both entrypoints use the lifecycle helper whose start/close contract is directly unit-tested. The separate ARCH-040 system-test tasks retain end-to-end platform certification responsibility.

### Deviations
Architect Review Accepted the bounded evidence approach: Shopify and WooCommerce producer implementations are out of scope; runtime parity seeds two equivalent origin-neutral command rows and proves identical dispatcher behavior without importing either platform's code. Worker ingress and downstream HUMAN suppression are proven at their production function boundaries in focused unit suites rather than one end-to-end BullMQ integration process. The shared dispatcher lifecycle helper's start/close contract is tested directly and is registered by both entrypoints; platform end-to-end certification remains with the dependent system-test tasks.

### Assumptions
Use the accepted consolidated DATABASE-001 schema; don't implement new schema in Background.

### Unresolved Issues
None within BG002's accepted scope. Platform end-to-end certification remains assigned to the dependent ARCH-040 system-test tasks.

### Architectural Concerns
Return cross-repository schema/contract or provider-send-ordering gaps to `moda_architect`.

### Physical Worktree Isolation and Synchronization
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-040-BACKGROUND-002`, `task/ARCH-040-BACKGROUND-002`
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-040-BACKGROUND-002`, `task/ARCH-040-BACKGROUND-002`
- Shared workspace checkout switched/mutated during task preparation: briefly switched to `task/ARCH-040-BACKGROUND-002` while materializing readiness, then restored to `main`; no user files were staged or committed there, and all pre-existing local changes were preserved
- Shared implementation source checkout switched/mutated for task work: no; its pre-existing database submodule modification was preserved
- Another task worktree reused: no
- Parent remote task branch was synchronized at `d2b49e511aa3bd7be9a33614bcce9a087f781a4c`; current `origin/main` at `28ad855fed3e86789b86a2bb1319ea3bd5c416cf` was merged into the parent task branch as `c489572c4220ab0d94e33176746c5c7cc45835c7` before the Attempt 2 claim.
- Implementation task branch and `origin/task/ARCH-040-BACKGROUND-002` both resolve to `ea526a6`; implementation worktree is clean and no merge to `main` was performed.
- Parent task completion record is committed and pushed on `task/ARCH-040-BACKGROUND-002`; parent worktree is clean after publication.
- Recursive implementation submodules remain at the recorded task gitlinks; no implementation files or submodule pointers changed during Attempt 2 preparation.
- Recursive implementation submodules: initialized and verified against recorded gitlinks; `database` is at `d00492ad1c10e78ab50d415acefc12bf872c17af`

## Architect Review

### Review Status
Accepted — acceptance was explicitly supplied by the developer for this completion action on 2026-10-18.

### Review Notes
Attempt 2 is accepted with the bounded evidence deviations recorded in the Completion Report: producer-neutral fixtures stand in for platform producer execution; inbound worker persistence and HUMAN turn suppression are covered at their respective production boundaries; the two runtime entrypoints share a directly tested lifecycle helper. Platform end-to-end certification remains assigned to the dependent system-test tasks.

### Reviewed Files
- `src/services/whatsapp-provider-status.service.ts`
- `src/entrypoints/messaging.ts`
- `src/index.ts`
- `tests/integration/recovery-human-dispatch.integration.test.ts`
- `tests/unit/services/whatsapp-provider-status.service.test.ts`
- `tests/unit/workers/whatsapp.worker.test.ts`

### Validation Reviewed
- `npm run test:arch040-background-wiring`: 6 files / 88 tests passed.
- `node_modules/.bin/vitest run tests/unit/services/whatsapp-provider-status.service.test.ts`: 1 file / 29 tests passed.
- `npm run test:arch040-background-runtime:postgres`: 1 file / 15 tests passed.
- `npm run build`, `npm run lint`, and `git diff --check`: passed.

### Architecture Conformance
Accepted for the task scope. No new deployable, platform-specific dispatcher logic, duplicate scheduler, schema, or UI route was added.

### Follow-up
Platform-specific end-to-end producer and inbox certification remains with ARCH-040-SHOPIFY-001, ARCH-040-WOOCOMMERCE-001, and ARCH-040-SYSTEM-TEST-001/002/003 after their other dependencies are satisfied.

## Developer Self-Review - Changes Requested

### Review Result
Attempt 1 does not pass the task's stated acceptance criteria. This is a developer self-review, not an architect acceptance or completion decision. Keep `attempt: 1`; transition to `status: ready`, `executor: null`, and `claimed_at: null` so the next developer claim creates Attempt 2.

### Required Corrections
- Wire verified HUMAN outbound provider status events to the linked `MerchantConversationSendCommand` and recovery attempt/credit reconciliation, preserving `canApplyProviderStatus` ordering and idempotency. Add tests for duplicate and out-of-order SENT/DELIVERED/READ/FAILED receipts.
- Add real call-site tests proving verified customer inbound persists during HUMAN ownership without an automated reply, while unrelated AI and inbound behavior remains intact.
- Prove both producer paths create the same platform-neutral command behavior and each results in one canonical HUMAN transcript message and provider submission.
- Test a HUMAN text command whose 24-hour customer window expires before dispatch; it must be denied without template substitution. Cover the eligible/blocked template boundary.
- Race scheduled no-response follow-up against merchant sequence-2 follow-up and prove exactly one attempt and credit identity wins.
- Test dispatcher startup and orderly shutdown from both `src/entrypoints/messaging.ts` and `src/index.ts`.

### Reviewed Evidence
Implementation diff and source paths were reviewed in the canonical Background task worktree. Focused wiring tests, the 11-case PostgreSQL/Redis integration suite, build, lint and diff hygiene passed. The missing criteria above are concrete coverage and integration gaps, not validation-command failures.

### Physical Worktree Review
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-040-BACKGROUND-002`, branch `task/ARCH-040-BACKGROUND-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-040-BACKGROUND-002`, branch `task/ARCH-040-BACKGROUND-002`.
- Implementation changes are committed and published; validation left the implementation worktree clean.
- No merge to `main` was performed.

## Developer Self-Review - Passed

### Review Result
Attempt 2 addresses the concrete corrections from the Attempt 1 self-review. Required focused integration, unit, build, lint, and diff-hygiene checks pass. The architect accepted the review and the developer explicitly completed the task; attempt remains 2.

### Reviewed Evidence
- Implementation commit `ea526a6` is pushed to `origin/task/ARCH-040-BACKGROUND-002`.
- The runtime suite verifies HUMAN text expiry without template fallback, origin-neutral command parity, scheduled/manual sequence-two competition through one winning provider submission and credit identity, and linked duplicate/out-of-order provider receipt behavior.
- Unit suites verify normalized inbound job persistence/enqueue, HUMAN turn suppression, legal in-flight command receipt convergence, and dispatcher start/close lifecycle.
- `npm run test:arch040-background-wiring`: 6 files / 88 tests passed.
- `node_modules/.bin/vitest run tests/unit/services/whatsapp-provider-status.service.test.ts`: 1 file / 29 tests passed.
- `npm run test:arch040-background-runtime:postgres`: 1 file / 15 tests passed.
- `npm run build`, `npm run lint`, and `git diff --check` passed.

### Completion Decision
The developer explicitly completed `ARCH-040-BACKGROUND-002` on 2026-10-18 after Architect Review Accepted. Set `status: complete`, `executor: null`, `claimed_at: null`, and preserve `attempt: 2`. No merge to `main` was performed or is required.

### Dependency Frontier
Rechecked downstream tasks that explicitly depend on BG002. Shopify-001, WooCommerce-001, Background-006, and System-Test-001/002/003 remain `pending` because each has other incomplete prerequisites; the system-test tasks also retain their manual execution gate. No downstream status transition was warranted by this completion.
