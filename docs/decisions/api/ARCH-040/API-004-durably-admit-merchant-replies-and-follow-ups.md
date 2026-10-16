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
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-040-API-003
  - ARCH-040-DATABASE-002
  - ARCH-040-DATABASE-003
enables:
  - ARCH-040-WOOCOMMERCE-001
created: 2026-10-14
updated: 2026-10-15
---

# ARCH-040-API-004 — Admit WooCommerce human replies and recovery follow-ups

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Provide one WooCommerce-installation-authenticated HTTP command for **durably accepting** a human reply or the recovery’s one allowed post-window follow-up; Background owns actual WhatsApp sending and credit finalisation.

## Context

`DATABASE-003` persists `MerchantConversationSendCommand` (unique `[shopId,idempotencyKey]`, payload hash, expected revision and relay state); `DATABASE-002` adds immutable initiation claim fields on the existing unique sequence-2 `RecoveryOutreachAttempt`. `BACKGROUND-002/003` will dispatch/reconcile through the canonical provider/recovery billing mechanisms. Woo is the only caller of these hosted endpoints.

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
- Existing `WooInstallationAuthenticator` and **current** installation/shop validity are required. Look up conversation ownership through recovery or standalone shop link, including nullable `Conversation.shopId`; no browser-supplied tenant ID or staff identifiers. `HUMAN` mode and matching `controlRevision` are required; client must take over using API-003 first. Do not silently change mode inside send.
- Ordinary text requires a currently open 24-hour service window derived from the latest verified CUSTOMER inbound timestamp; its expiry is `lastInboundAt + 24h`, checked with server clock. A closed window rejects text (`409 service_window_closed`) rather than making an automatic template. Re-evaluate again at Background dispatch because accepted work may wait in queue.
- A closed-window recovery follow-up requires approved template, actionable associated recovery and available single `sequence=2` claim; **one per CheckoutRecovery**, shared with CommerceAgent/automation. The initial recovery `sequence=1` is a different attempt. Do not issue arbitrary proactive templates for standalone conversations. Reuse existing approved recovery template selection and recipient rules; do not allow caller-chosen arbitrary Meta template names.
- For follow-up acceptance, in the **same DB transaction** as accepting the command, upsert/find existing unclaimed sequence-2 attempt and atomically claim it (`initiatedBy=HUMAN`, `initiationKey`, `claimedAt`, `trigger=POST_WINDOW_FOLLOW_UP` as appropriate) without overwriting an already claimed HUMAN/AGENT/AUTOMATION attempt. Point the command to that exact attempt. Never create sequence 3, new Conversation or independent human credit ledger.
- Follow-up claim is a logical reservation, **not a charge**; Background owns provider outcome, retry, credit admission and compensation using the existing `recovery-outreach:<attempt.id>` source identity. Do not invoke provider, Redis or billing network work inside the admission transaction.
- Accept command `202` with `{schemaVersion:1,commandId,conversationId,state:"ACCEPTED",controlRevision,kind}`. An identical `(shopId,idempotencyKey)` replay returns same command identity/current persisted state (`200`) and never claims/sends/bills again; same key with changed canonical payload returns `409 idempotency_conflict`.
- `GET /v1/merchant/conversations/{conversationId}/send-commands/{commandId}` returns `{schemaVersion:1,commandId,conversationId,kind,state,createdAt,updatedAt,messageId|null,failureCode|null}` for polling, scoped to the same installation/shop/conversation. Distinguish ACCEPTED/CLAIMED/UNKNOWN/SENT/terminal failures rather than telling UI a send has succeeded at acceptance.
- Other HTTP failures: `401 unauthorized`, `404 not_found` (foreign conversation/command), `400 invalid_request`, `409 stale_control_revision`, `409 not_human_controlled`, `409 follow_up_unavailable`, `409 template_not_allowed`, `409 service_window_closed`, `409 recipient_unavailable`, `500 internal_error`. Return stable machine codes and safe error envelopes. Repeat no failed request with a different command unless instructed by user.
- Any pending accepted command whose mode/revision changed must be blocked at Background dispatch; dispatch order/race correctness is the shared database+Background protocol, not one optimistic request read.

## Work Items

- [ ] Implement strict Woo-authenticated human send POST and command-status GET with API-local request and response validation.
- [ ] Resolve tenant/conversation/recovery/recipient and current HUMAN revision inside the durable admission transaction; enforce service window and template catalogue eligibility.
- [ ] Persist idempotent `MerchantConversationSendCommand`, server canonical payload hash and recipient snapshot; same key replays same command only.
- [ ] Atomically claim/link existing unique recovery `sequence=2` attempt for approved follow-up across HUMAN/AGENT/AUTOMATION; no new credit counter.
- [ ] Return 202 accepted vs 200 replay and bounded current status, with explicit stale/window/template/follow-up errors.
- [ ] Add HTTP/OpenAPI, negative security, PostgreSQL idempotency/race/recovery-window tests; ensure no provider or Redis call in the API transaction.

## Interfaces / Contracts

Routes: `POST /v1/merchant/conversations/{conversationId}/messages` and `GET /v1/merchant/conversations/{conversationId}/send-commands/{commandId}`. Existing Woo installation credentials are the sole hosted API auth mechanism. Persisted identities/states come from `DATABASE-001/002/003`; API owns HTTP validation/status/error envelopes, while `BACKGROUND-002` leases/reconciles command and `BACKGROUND-003` settles follow-up provider/credit outcomes. Shopify writes the **same** durable Prisma command/attempt under its authenticated app server; it does not call this API.

## Dependencies

- ARCH-040-API-003
- ARCH-040-DATABASE-003
- ARCH-040-DATABASE-002

## Enables

- ARCH-040-WOOCOMMERCE-001

## Acceptance Criteria

- [ ] Successful submission commits exactly one command before replying 202; same-key replay returns original identity, never an additional command/send/credit.
- [ ] A changed payload for an existing key conflicts without mutating the accepted command or existing follow-up claim.
- [ ] Closed-window text, disallowed template, stale mode/revision, blocked recipient, disabled shop/installation and foreign tenant all fail without accepting a send.
- [ ] Concurrent human vs automated follow-up claims result in at most one sequence-2 winner and one logical credit identity, with the original Conversation id unchanged.
- [ ] Server does not perform a provider send, bill a credit or publish Redis from within the HTTP DB transaction; terminal command status is correctly retrievable on later reads.
- [ ] API tests prove a human message uses senderType=HUMAN when Background processes it, rather than inventing separate message persistence.

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
