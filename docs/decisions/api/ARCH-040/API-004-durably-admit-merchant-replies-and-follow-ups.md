---
id: ARCH-040-API-004
architecture_id: ARCH-040
title: Admit WooCommerce human replies and recovery follow-ups
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-API-003
  - ARCH-040-DATABASE-001
  - ARCH-040-DATABASE-005
enables:
  - ARCH-040-WOOCOMMERCE-001
created: 2026-10-14
updated: 2026-10-19
---

# ARCH-040-API-004 — Admit WooCommerce human replies and recovery follow-ups

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Provide one WooCommerce-installation-authenticated HTTP command for **durably accepting** a human reply or the recovery’s one allowed post-window follow-up; Background owns actual WhatsApp sending and credit finalisation.

## Context

`DATABASE-001` supplies both `MerchantConversationSendCommand` (unique `[shopId,idempotencyKey]`, payload hash, expected revision and relay state) and immutable initiation claim fields on the existing unique sequence-2 `RecoveryOutreachAttempt`. `BACKGROUND-002/003` will dispatch/reconcile through the canonical provider/recovery billing mechanisms. Woo is the only caller of these hosted endpoints.

## Scope

- Implement only the WooCommerce-hosted API boundary described here, using the existing authenticated installation and generated Prisma models.
- Follow the existing API HTTP route, validation, logging, error and OpenAPI patterns, and add focused tests.
- Keep API controller/validation, tenant-scoped service, persistence and API contract tests modular. Do not introduce a catch-all file.

## Out of Scope

- Shopify authentication, Shopify app routes or direct Shopify merchant calls to this hosted API.
- New Moda merchant accounts, per-staff permissions/assignments or staff attribution identifiers.
- A second conversation, another message table, a second follow-up allowance or a new recovery credit ledger.
- Provider WhatsApp delivery, background worker business logic, webhook processing or queue workers.
- WordPress admin/UI implementation, which belongs to `moda_woocommerce`.
- Recreating Shared conversation DTOs; Prisma is canonical for persisted data, while HTTP DTOs are local to API.
- No `docs/decisions/**/_index.md` changes before explicit user confirmation.

## Requirements

### Moderation status and queued-command contract

The HTTP request stores the frozen HUMAN command; it does **not** call OpenAI or Meta. The accepted reply remains queued for BG006 review. Status GET must distinguish `moderation_pending`, `moderation_blocked`, `moderation_review_required`, `moderation_retryable_error` and ordinary WhatsApp delivery outcomes using DATABASE-005. On a blocked command return stable `HUMAN_CONTENT_MODERATION_BLOCKED` without treating it as provider failure or consuming a recovery credit. Idempotent repeat returns the same command and moderation decision, not a new command/assessment. The client cannot submit `moderationApproved`, provider/model scores or authority fields.

- No separate follow-up/credit ledger or human-only WhatsApp provider sender. This endpoint creates the canonical merchant command and (when eligible) claims existing sequence-2 outreach; provider delivery/receipts and billing remain Background-owned. A previously engaged customer does not cause a **scheduled** follow-up; an eligible deliberate merchant template after a closed service window remains subject to the single sequence-2 limit.

### Exact HTTP endpoints

`POST /v1/merchant/conversations/{conversationId}/messages`

Open-window human text body:
```json
{ "kind":"HUMAN_TEXT", "expectedControlRevision":5, "idempotencyKey":"merchant-send-key", "textBody":"Hello, I can help" }
```

Closed-window recovery follow-up body:
```json
{ "kind":"RECOVERY_FOLLOW_UP_TEMPLATE", "expectedControlRevision":5, "idempotencyKey":"merchant-send-key", "templateName":"approved_recovery_follow_up", "templateLanguage":"en_GB", "templateParameters":{} }
```

- `idempotencyKey` required, opaque, length bounded by DB schema; stable for retry/double click, not generated afresh for every network retry. Strictly enforce exclusive text/template shape, server-side template allowlist and parameter bounds, a nonempty bounded human text and a request size limit. Use an API-local versioned canonical JSON representation and compute `payloadSha256` on server (not from client).
- Existing `WooInstallationAuthenticator` and **current** installation/shop validity are required. Require `Conversation.checkoutRecoveryId IS NOT NULL` and resolve ownership **only through** `CheckoutRecovery.shopId`; reject standalone/product-support conversations even with a nonnull `Conversation.shopId`. No browser-supplied tenant ID or staff identifiers. `HUMAN` mode and matching `controlRevision` are required; client must take over using API-003 first. Do not silently change mode inside send.
- Ordinary text requires a currently open 24-hour service window derived from the latest verified CUSTOMER inbound timestamp; its expiry is `lastInboundAt + 24h`, checked with server clock. A closed window rejects text (`409 service_window_closed`) rather than making an automatic template. Re-evaluate again at Background dispatch because accepted work may wait in queue.
- A closed-window recovery follow-up requires approved template, actionable associated recovery and available single `sequence=2` claim; **one per CheckoutRecovery**, shared with CommerceAgent/automation. The initial recovery `sequence=1` is a different attempt. Do not issue arbitrary proactive templates or HUMAN_TEXT for standalone conversations in ARCH-040. Reuse existing approved recovery template selection and recipient rules; do not allow caller-chosen arbitrary Meta template names.
- For follow-up acceptance, in the **same DB transaction** as accepting the command, upsert/find existing unclaimed sequence-2 attempt and atomically claim it (`initiatedBy=HUMAN`, `initiationKey`, `claimedAt`, `trigger=POST_WINDOW_FOLLOW_UP` as appropriate) without overwriting an already claimed HUMAN/AGENT/AUTOMATION attempt. Point the command to that exact attempt. Never create sequence 3, new Conversation or independent human credit ledger.
- Follow-up claim is a logical reservation, **not a charge**; Background owns provider outcome, retry, credit admission and compensation using the existing `recovery-outreach:<attempt.id>` source identity. Do not invoke provider, Redis or billing network work inside the admission transaction.
- Accept command `202` with `{schemaVersion:1,commandId,conversationId,state:"ACCEPTED",controlRevision,kind}`. An identical `(shopId,idempotencyKey)` replay returns same command identity/current persisted state (`200`) and never claims/sends/bills again; same key with changed canonical payload returns `409 idempotency_conflict`.
- `GET /v1/merchant/conversations/{conversationId}/send-commands/{commandId}` returns `{schemaVersion:1,commandId,conversationId,kind,state,createdAt,updatedAt,messageId|null,failureCode|null}` for polling, scoped to the same installation/shop/conversation. Distinguish ACCEPTED/CLAIMED/UNKNOWN/SENT/terminal failures rather than telling UI a send has succeeded at acceptance.
- Other HTTP failures: `401 unauthorized`, `404 not_found` (foreign conversation/command), `400 invalid_request`, `409 stale_control_revision`, `409 not_human_controlled`, `409 follow_up_unavailable`, `409 template_not_allowed`, `409 service_window_closed`, `409 recipient_unavailable`, `500 internal_error`. Return stable machine codes and safe error envelopes. Repeat no failed request with a different command unless instructed by user.
- Any pending accepted command whose mode/revision changed must be blocked at Background dispatch; dispatch order/race correctness is the shared database+Background protocol, not one optimistic request read.

### Platform suspension on message admission

- Resolve the DATABASE-001 restriction for the authenticated Woo shop and reject SUSPENDED merchant HUMAN sends with `403 human_messaging_suspended`; no command or sequence-2 follow-up claim should be created.
- Perform the restriction check under the command admission transaction with an appropriate ordering fence against Admin suspension. Always rely on BACKGROUND-001 restriction policy as wired by BACKGROUND-002 for a second, mandatory check at final provider admission. Never send because the UI said the shop was ACTIVE.
- The command-status GET may report `human_messaging_suspended`, `human_rate_limited`, `human_repeated_spam`, `human_content_invalid` or `human_screening_unavailable` when these are persisted worker outcomes. Never leak internal administrator notes.


### Platform-neutral persistence and dispatch contract

Woo API is an authenticated **producer**, not a dispatcher. Inside its existing Woo-installation/shop-scoped PostgreSQL transaction it commits the very same `MerchantConversationSendCommand` shape/idempotency identity that Shopify's server action writes. It must **not** publish BullMQ, invoke Meta, call a Background HTTP endpoint, or distinguish scheduling by commerce platform. The shared BG002 messaging-worker **PostgreSQL poller** is the sole consumer of HUMAN sends. Existing inbound WhatsApp and delayed automatic recovery follow-ups keep their established BullMQ jobs; do not schedule a new BullMQ job for a merchant's immediate post-window follow-up.

For an existing unclaimed sequence-2 PENDING row, atomically claim that row and bind approved template/recipient snapshot, selected trigger and initiation fields in the **same** transaction as the command. Do not overwrite a claimed row or a provider-unknown operation; retry uses the original command and credit idempotency identity. Acceptance returns `ACCEPTED`, not provider delivery. Server-side eligibility must explicitly resolve the existing send entitlement independently of `RECOVERY_HISTORY` read access, and reject terminal recoveries under the shared policy. Use the maximum verified inbound timestamp for the 24-hour window. Final dispatch revalidates these conditions under the BG001 fence.


## Work Items

- [ ] Implement strict Woo-authenticated human send POST and command-status GET with API-local request and response validation.
- [ ] Resolve tenant/conversation/recovery/recipient and current HUMAN revision inside the durable admission transaction; enforce service window and template catalogue eligibility.
- [ ] Persist idempotent `MerchantConversationSendCommand`, server canonical payload hash and recipient snapshot; same key replays same command only.
- [ ] Atomically claim/link existing unique recovery `sequence=2` attempt for approved follow-up across HUMAN/AGENT/AUTOMATION; no new credit counter.
- [ ] Return 202 accepted vs 200 replay and bounded current status, with explicit stale/window/template/follow-up errors.
- [ ] Add HTTP/OpenAPI, negative security, PostgreSQL idempotency/race/recovery-window tests; ensure no provider or Redis call in the API transaction.

- [ ] Reject HUMAN command acceptance under persisted suspension in a shop-scoped transaction; propagate safe restriction and screening outcomes.

## Interfaces / Contracts

Routes: `POST /v1/merchant/conversations/{conversationId}/messages` and `GET /v1/merchant/conversations/{conversationId}/send-commands/{commandId}`. Existing Woo installation credentials are the sole hosted API auth mechanism. Persisted identities/states come from `DATABASE-001`; API owns HTTP validation/status/error envelopes, while `BACKGROUND-002` leases/reconciles command and `BACKGROUND-002` invokes the BACKGROUND-001 policy to settle follow-up provider/credit outcomes. Shopify writes the **same** durable Prisma command/attempt under its authenticated app server; it does not call this API.

## Dependencies

- ARCH-040-API-003
- ARCH-040-DATABASE-001


- ARCH-040-DATABASE-005
## Enables

- ARCH-040-WOOCOMMERCE-001

## Acceptance Criteria

- [ ] Woo human-send commands expose the persistent moderation lifecycle without synchronous moderation in API requests, without client-provided approvals and without extra Meta sends or credits.

- [ ] Successful submission commits exactly one command before replying 202; same-key replay returns original identity, never an additional command/send/credit.
- [ ] A changed payload for an existing key conflicts without mutating the accepted command or existing follow-up claim.
- [ ] Closed-window text, disallowed template, stale mode/revision, blocked recipient, disabled shop/installation and foreign tenant all fail without accepting a send.
- [ ] Concurrent human vs automated follow-up claims result in at most one sequence-2 winner and one logical credit identity, with the original Conversation id unchanged.
- [ ] Server does not perform a provider send, bill a credit or publish Redis from within the HTTP DB transaction; terminal command status is correctly retrievable on later reads.
- [ ] API tests prove a human message uses senderType=HUMAN when Background processes it, rather than inventing separate message persistence.

- [ ] Suspended HUMAN requests admit no command or follow-up claim; AI/automation policy remains unchanged.

## Validation

- [ ] HTTP/OpenAPI contract matrix: valid text/follow-up, malformed/unknown fields, duplicate idempotency, time window and response/error shapes.
- [ ] Disposable PostgreSQL transactions: concurrent HUMAN/AGENT/AUTOMATION sequence-2 claim, replay and changed-payload conflict, lease receipt link integrity, missing/foreign conversation.
- [ ] Clock-boundary tests at window expiry, invalid customer-inbound evidence, stale revision and changed mode.
- [ ] Auth tests for revoked/rotated Woo credential and no staff-specific authorization; ensure no provider/network/Redis side effects during API acceptance.
- [ ] `git diff --check`, applicable repository typecheck/build/lint, and Completion Report/worktree evidence.

## Stop Condition

After only this task’s Work Items, Acceptance Criteria and Validation are complete, record implementation evidence, set status to review and return control to moda_architect. Do not begin dependent tasks.

## Implementation Notes

- Follow the canonical `scripts/start-agent-task.py --prepare` preparation packet and the parent/implementation worktree policy. Only claim the task in the real development workspace, not this portable definition.
- Do not assume a particular validation command: inspect `moda-interact-api/package.json` and the task's requirements. Use disposable PostgreSQL integration fixtures from this repository.
- Use `@modainteract/moda-interact-shared/logging` for structured logging; log bounded identifiers/outcomes rather than customer content, bearer tokens, WordPress credentials or private recipient numbers.
- Fresh development schema only. No historical-data migration/backfill/old-contract adapters are required for ARCH-040. Keep existing WooCommerce credential rotation/disconnection and API response header security protections.

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
The architecture is proposed; implementation starts only after agreed/materialised task definition.

### Unresolved Issues
None recorded at definition time.

### Architectural Concerns
Return newly discovered contract or ownership gaps to moda_architect.

## Architect Review

### Review Status
Pending

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
