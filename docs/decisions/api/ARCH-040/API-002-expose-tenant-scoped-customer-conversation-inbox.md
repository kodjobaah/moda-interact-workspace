---
id: ARCH-040-API-002
architecture_id: ARCH-040
title: Expose WooCommerce customer conversation inbox and message reads
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
  - ARCH-040-DATABASE-001
enables:
  - ARCH-040-WOOCOMMERCE-001
  - ARCH-040-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---

# ARCH-040-API-002 — Expose WooCommerce customer conversation inbox and message reads

## Architecture

Initiative: `ARCH-040`. Architecture document: `docs/architecture/ARCH-040-merchant-customer-conversations-human-handover.md`. Coordinator: `moda_architect`. **Portable definition only; defined but not materialised, no branch/commit/worktree.**

## Objective

Provide **WooCommerce-only** authenticated, bounded inbox, conversation detail and paginated transcript reads using existing `Conversation`/`ConversationMessage` data without introducing a second conversation.

## Context

The 2026-10-14 hosted API already has `WooInstallationAuthenticator` (`x-moda-installation-id` + server-side Bearer installation credential) and recovery read routes at `/v1/merchant/recoveries/{id}` with `/messages` and `/related`. Those recovery-detail reads validate `WooCommerceInstallation`, shop state, and nullable `Conversation.shopId` against `CheckoutRecovery.shopId` in a transaction. Extend these patterns, not Shopify authentication. `ARCH-035-API-013` remains responsible for its own recovery-detail capability; reuse its already implemented methods where appropriate.

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

### HTTP endpoints — exact v1 shape

- `GET /v1/merchant/conversations?limit=20&cursor=<opaque>` — a bounded, most-recent-first page for the authenticated Woo installation's shop. Default `limit=20`, maximum 50. Unknown query keys, repeated or malformed parameters fail with `400 invalid_request`.
- `GET /v1/merchant/conversations/{conversationId}` — one scoped conversation with current mode/revision and basic recovery context.
- `GET /v1/merchant/conversations/{conversationId}/messages?limit=20&cursor=<opaque>` — stable oldest-to-newest display page (or consistently documented newest-first pagination with UI reversal). Default 20/max 50, strict cursor validation. `conversationId` is a validated opaque path identifier, not a shop selector.
- All endpoints require the **existing** `WooInstallationAuthenticator.authenticate(request)` before reading data. Never accept a caller-supplied `shopId`, tenant header or staff identity as authority. Only allow `GET`; never accept a request body. Preserve existing no-store/nosniff response headers.

### Output contract (local to API; not Shared)

- List response: `{ schemaVersion: 1, items: ConversationInboxItem[], nextCursor: string|null }`. Each item includes `conversationId`, `checkoutRecoveryId` (nullable), `controlMode`, `controlRevision`, `lastMessageAt`, `lastInboundAt`, bounded customer display context, latest message preview (`senderType`, `direction`, bounded text/placeholder) and relevant recovery status. ISO-8601 timestamps, nullable where unknown; never return provider secrets or full raw payloads.
- Detail response: `{ schemaVersion: 1, conversationId, checkoutRecoveryId, controlMode, controlRevision, lastMessageAt, lastInboundAt, recoveryStatus, followUp: { sequence2Used, initiatedBy } }`, plus only the minimum customer/recovery display fields needed by Woo. Indicate service-window eligibility as **advisory** (`windowExpiresAt`/`windowOpen` derived from most recent verified customer inbound) rather than treating a read response as send authorisation.
- Message page: `{ schemaVersion:1, items:[{ id, createdAt, direction, senderType, content:{type,text,transcriptionStatus}, delivery:{status,sentAt,deliveredAt,readAt}|null }], nextCursor, previousCursor }`. Preserve `CUSTOMER`, `AGENT`, `AUTOMATION`, `HUMAN`; unknown audio/media are safe placeholders. Reuse ARCH-035 message representation instead of duplicating recovery-message behaviour when compatible.

### Query, scope, stability

- For recovery conversations authorize through `CheckoutRecovery.shopId`, **even when `Conversation.shopId` is null**; where both shop IDs exist and disagree, fail closed. For standalone conversations, use `Conversation.shopId`. Reject unowned/inconsistent conversation–customer–recovery links.
- Verify current Woo installation ID/shop/platform/site URL/credential version and active/non-revoked state consistent with the existing recovery-detail service. `404 not_found` for another shop's conversation and non-existent IDs (no enumeration leak); `401 unauthorized` for bad installation credentials; `409` bounded integrity error for inconsistent owned data.
- Cursor is opaque and bound to effective `shopId`, endpoint and sort position; tampered, cross-shop, cross-endpoint or stale/invalid cursors fail closed. Use a deterministic tie-breaker (`lastMessageAt/createdAt` plus `id` for inbox; `createdAt,id` for messages), no OFFSET scans, no unbounded joins; include empty-page behaviour.
- Preserve explicit upper bounds on response size and PII; do not expose telephone numbers, WhatsApp raw credentials or full transcript in list summaries. Query efficiently using canonical database indexes and the recovery join rather than `Conversation.shopId` alone.
- Keep `Conversation.id` unchanged for initial outreach and sequence-2 follow-up. List one row per conversation, never one per message/attempt or per author.

## Work Items

- [ ] Add Woo-authenticated three GET routes under `/v1/merchant/conversations` and register them through the existing server/router wiring.
- [ ] Add strict URL/limit/cursor validation and API-local v1 DTO validation, with no client-controlled shop identity.
- [ ] Implement transactional tenant-scoped recovery/standalone reads with the nullable conversation shopId handling and disconnected/rotated-installation checks.
- [ ] Implement bounded inbox keyset paging, thread paging, preview sanitisation and actor labels; reuse the ARCH-035 recovery message transformer.
- [ ] Add HTTP contract/OpenAPI coverage, auth/tenant failure cases, pagination stability and PostgreSQL fixtures.

## Interfaces / Contracts

Owned routes: `GET /v1/merchant/conversations`, `/v1/merchant/conversations/{conversationId}`, `/v1/merchant/conversations/{conversationId}/messages`. Request/response/error schemas belong locally in `moda-interact-api`; canonical persisted fields are from `moda-interact-database`/Prisma. The caller is **WooCommerce PHP server only** (through WordPress REST proxy); no Shopify API client or Shopify assertion. Reuse `WooInstallationPrincipal` and the recovery detail read pattern in `src/merchant/recoveries/detail/`. Reads are not send permission grants.

## Dependencies

- ARCH-040-DATABASE-001

## Enables

- ARCH-040-WOOCOMMERCE-001
- ARCH-040-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] A connected Woo shop sees one inbox item and one conversation ID for a recovery, even with initial, follow-up, CUSTOMER, AGENT and HUMAN messages.
- [ ] Foreign-shop IDs return a non-enumerating 404; invalid/revoked/rotated credentials fail 401; inconsistent stored owner associations fail closed.
- [ ] List, detail and messages return the documented v1 shape, bounded data, stable cursor pages including equal timestamps, and no overlap/skip for unchanged data.
- [ ] Nullable `Conversation.shopId` on a recovery does not suppress valid messages or accidentally leak another tenant.
- [ ] Bad query parameters, repeated cursor keys, tampered/cross-shop cursors and bad IDs are rejected; existing recovery-detail routes remain unchanged.

## Validation

- [ ] API route and OpenAPI contract tests for all three endpoints, bad methods/bodies/queries, no-store headers, and malformed/inactive credentials.
- [ ] Disposable PostgreSQL tests for recovery (nullable and non-null shopId), standalone, foreign shop, broken integrity, zero messages and mixed-author histories.
- [ ] Keyset pagination tests for equal timestamps, boundaries, invalid cursor and no cross-tenant leakage; check query boundedness/index plan as practical.
- [ ] `git diff --check`, repository's applicable typecheck/build/lint, and isolated worktree/Completion Report evidence.

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
