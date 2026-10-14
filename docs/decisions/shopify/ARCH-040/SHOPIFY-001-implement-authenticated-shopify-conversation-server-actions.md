---
id: ARCH-040-SHOPIFY-001
architecture_id: ARCH-040
title: Implement authenticated Shopify conversation server actions
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
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
  - ARCH-040-DATABASE-002
  - ARCH-040-DATABASE-003
enables:
  - ARCH-040-SHOPIFY-002
  - ARCH-040-SHOPIFY-003
  - ARCH-040-SYSTEM-TEST-002
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-SHOPIFY-001 — Implement authenticated Shopify conversation server actions

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Implement the **Shopify-owned authenticated server-side conversation data/actions boundary** directly on canonical Prisma tables, without calling `moda-interact-api`.

## Context

The existing Shopify app has `authenticate.admin(request)` and Prisma access. The hosted merchant API handles WooCommerce installations only. The Shopify app must implement its own server read/mutation boundary with precisely the same durable mode, command and follow-up invariants used by the Woo API.

## Scope

- Add small authenticated Shopify loaders/server actions (or equivalent Shopify app framework handlers) for inbox/message history, takeover/resume and durable send command acceptance/status.
- Reuse existing app Shopify session→Shop resolving and Prisma connection.
- Keep business logic segmented into testable shop-scoped read, control and send services; no monolithic route handling.

## Out of Scope

- No Shopify-to-hosted-API assertion, signing key, Gateway secret or HTTP proxy client.
- No change to the WooCommerce hosted API or WordPress PHP.
- No provider send, queue worker, billing settlement or follow-up scheduler; Background remains authoritative for dispatch.
- No staff-specific identity/account/assignment/permission model; app session and shop ownership suffice.
- No new Conversation or duplicate transcript/credit ledger; no `_index.md` changes.

## Requirements

- Require `authenticate.admin(request)` or the existing equivalent for **every** read/action; derive trusted Shop ID from the authenticated session/shop record, never a browser-supplied shopId. Fail closed on inactive/disconnected shop and cross-tenant IDs. Recovery threads authorize via `CheckoutRecovery.shopId` even when `Conversation.shopId` is null; standalone via `Conversation.shopId`.
- Expose a bounded, ordered inbox and transcript using Prisma models; return `controlMode`, `controlRevision`, senderType, last inbound, current delivery state and advisory service-window eligibility. Keep list/thread page size capped (same 20 default/50 max as Woo) and cursors scope-bound; reuse existing recovery-detail read shaping where practical.
- In a single Prisma transaction perform `Conversation.controlMode/controlRevision` CAS plus one `ConversationControlEvent`, with idempotent current-revision same-mode no-op and explicit stale conflict. Human Take Over is always available to authenticated merchant; switching modes does not itself dispatch or bill.
- For sending, require current HUMAN control revision, text-only in an open last-CUSTOMER-inbound service window, or the single approved recovery sequence-2 template when closed. In one DB transaction persist an immutable, shop-idempotent `MerchantConversationSendCommand` and, for template, atomically claim the existing unique sequence-2 attempt; no new conversation or independent credit.
- Return accepted command identity/status rather than claiming WhatsApp delivery; preserve safe duplicate replay vs conflicting payload, and expose command-status read. Background will recheck eligibility/mode and complete send/credit.
- Preserve existing Shopify route conventions, CSRF/session protections, validation, bounded PII and shared structured logging. Use no new staff grant mechanism, browser DB access or server signing credentials.

## Work Items

- [ ] Implement reusable shop-scoped read service for inbox, detail, messages and command status with pagination.
- [ ] Implement session-authenticated control action with database CAS/transition audit.
- [ ] Implement session-authenticated human send action with immutable command idempotency, window/template rules and shared follow-up claim.
- [ ] Expose only browser-safe typed data/errors to SHOPIFY-002/003; no hosted-API client.
- [ ] Add action/loader authorization, PostgreSQL race, replay, cross-shop and 24-hour boundary tests.

## Interfaces / Contracts

`moda-interact` owns its Shopify UI-facing loaders/actions and request validation; `moda-interact-database` owns canonical persisted data. Use the `DATABASE-001/002/003` fields and transaction contracts and match Woo API observable behaviour (especially CAS, idempotency, window eligibility and sequence-2 claim). **Shopify must not call the Woo-only hosted API.** Background consumes durable commands regardless of origin.

## Dependencies

- ARCH-040-DATABASE-001
- ARCH-040-DATABASE-002
- ARCH-040-DATABASE-003

## Enables

- ARCH-040-SHOPIFY-002
- ARCH-040-SHOPIFY-003
- ARCH-040-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Valid Shopify admin session for shop A sees or changes only shop A conversations, including recovery with null `Conversation.shopId`.
- [ ] Human takeover/resume updates the original conversation and immutable audit event with monotonically increasing revision.
- [ ] Identical send retry creates one command; mismatched request key conflicts; post-window follow-up competes for the same sequence-2 attempt as AI.
- [ ] All human/AI/customer/recovery messages remain on the same conversation and no billing/provider send occurs within UI requests.
- [ ] No Shopify assertion/header secret, hosted API call, or new Shopify staff permission is required.

## Validation

- [ ] Shopify authenticated loader/action and cross-tenant tests, no-op/race tests.
- [ ] Disposable PostgreSQL fixtures for mode CAS, command idempotency, follow-up claim and cursor paging.
- [ ] Applicable repository lint/typecheck/build, `git diff --check`, canonical isolated task-worktree evidence.

## Stop Condition

After only this task’s Work Items, Acceptance Criteria and Validation are complete, record implementation evidence, set status to review and return control to moda_architect. Do not begin dependent tasks.

## Implementation Notes

Use the existing Shopify app auth session and direct Prisma server access. Keep React UI separate from data access and server action wiring. Cross-repository integration with Background is verified under the terminal system tests. The architecture has no Shopify-to-hosted-API or Gateway work.

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
