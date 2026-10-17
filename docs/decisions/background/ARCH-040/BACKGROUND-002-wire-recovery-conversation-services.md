---
id: ARCH-040-BACKGROUND-002
architecture_id: ARCH-040
title: Wire recovery conversation services into live Background paths
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
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
updated: 2026-10-17
---

# ARCH-040-BACKGROUND-002 — Wire recovery conversation services into live Background paths

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. Portable definition; no worktree, branch, commit or implementation is claimed.

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

### 2. New dispatcher — single durable source, no new queue required

Add a small module such as `src/services/recovery-conversation/merchant-send-dispatcher.ts` (or `src/workers/merchant-conversation-send.worker.ts` if a worker abstraction is preferred) that **polls the accepted PostgreSQL command table**. This is preferable to requiring Shopify and WooCommerce to publish to Redis after database commit. Do not introduce a second BullMQ queue/outbox publisher unless a measured need or an existing approved primitive justifies it.

- A bounded poll discovers `ACCEPTED` and due retryable commands by indexed `nextAttemptAt`/lease expiry; defaults proposed for first version: **batch <= 25 per poll, at most 4 concurrent processing calls, 3-second poll interval**, all configurable/test-injectable. Values are provisional operating defaults, *not measured capacity*.
- Claim each row using BG001's PostgreSQL lease/CAS operations (e.g. `FOR UPDATE SKIP LOCKED` in a short transaction); no global per-shop lock or long transaction around network I/O. Stop/drain on shutdown; startup recovers expired leases and pending commands.
- Re-load command by durable `commandId` and expected lease token. Use frozen payload/recipient, owner revision, current restriction, send window, recipient suppression, template eligibility and rate policy. Route allowed work to the existing WhatsApp delivery adapter with BG001's final fence, then reconcile message/command/attempt/credit state.
- A failed or disconnected poll does not mark a command SENT; transient errors use bounded backoff with stable command identity. A provider-unknown result is reconciled, never blindly resent. The dispatcher itself does **not** rewrite policy rules or choose different template text.
- Add structured log events for `human_command.claimed`, `.suppressed`, `.submitted`, `.unknown`, `.reconciled` using shared logger and IDs/reason codes only. Do not log message bodies, names, phone numbers, secrets or administrative notes. Reuse approved framework instrumentation; no custom duplicate HTTP/queue metrics.

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

## Work Items

- [ ] Wire AI owner/revision checks into turn start, awaited-agent continuation and final provider-send path, including queued retry suppression.
- [ ] Register and run a durable HUMAN command consumer using BACKGROUND-001 service APIs, existing transport, idempotency/receipts and bounded worker lifecycle.
- [ ] Wire scheduled and merchant-initiated sequence-2 follow-up to the same existing processor/credit identity; preserve scheduled no-response suppression.
- [ ] Integrate final suspension, abuse screening and provider-fence checks at the irreversible send handoff, not only at claim/dequeue time.
- [ ] Wire provider status/failure/unknown and recovery credit reconciliation; add cross-service runtime tests for races and both command producers.

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

## Acceptance Criteria

- [ ] Every existing-file row and all three execution sequences in the detailed integration blueprint have real exercised call sites, asserted outcomes and startup/shutdown registration; no orphan BG001 service methods.
- [ ] Running Background workers deliver both producer types' HUMAN messages through the existing WhatsApp path, preserving one transcript, delivery receipts and billing identity.
- [ ] Takeover/suspension precedence and queue retries are demonstrated at actual send admission; unrelated AI and inbound traffic remain unaffected.
- [ ] Scheduled no-response and merchant post-window follow-up are unified without a second attempt, credit or scheduler.
- [ ] Neither Shopify nor WooCommerce implementation is a dependency of this task, and no additional runtime deployable is introduced without an approved architecture change.

## Validation

- [ ] Focused integration tests for all listed worker/service/provider/receipt entrypoints
- [ ] Disposable PostgreSQL/Redis worker restart, duplicate, lease, suspense and race matrix
- [ ] Provider mocked ordering and delivery-status/unknown compensation tests
- [ ] End-to-end recovery follow-up credit/idempotency test using actual background call sites
- [ ] Typecheck, changed-file lint, applicable build/test scripts and `git diff --check`

## Stop Condition

After implementing only the listed scope and completing validation, record worktree, tests, and files in Completion Report, set task to `review`, return to `moda_architect` and **STOP**. Do not execute another task automatically.

## Implementation Notes

Use the canonical launcher-resolved dedicated parent/implementation task worktrees and matching `task/<TASK_ID>` branches. Check the repository scripts before selecting validation commands. Use the published `@modainteract/moda-interact-shared/logging` API; log stable identifiers and reason codes only, never message bodies, credentials, personal details or admin notes. Avoid editing `docs/decisions/**/_index.md` until this architectural session is explicitly closed. This architecture targets fresh development-schema validation; do not add historical migration/backfill work.

## Completion Report

### Status
Not Started

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
Use the accepted consolidated DATABASE-001 schema; don't implement new schema in Background.

### Unresolved Issues
None recorded.

### Architectural Concerns
Return cross-repository schema/contract or provider-send-ordering gaps to `moda_architect`.

## Architect Review

### Review Status
Pending.

### Review Notes
Not reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending.

### Follow-up
None.
