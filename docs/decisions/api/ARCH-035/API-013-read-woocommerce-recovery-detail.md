---
id: ARCH-035-API-013
architecture_id: ARCH-035
title: Expose shop-authorised recovery detail and paginated history reads for Woo UI
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-009
enables: []
created: 2026-10-12
updated: 2026-10-16
---

# ARCH-035-API-013 — Recovery Detail reads for WooCommerce UI

## Architecture

`ARCH-035`; parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
Coordinator: `moda_architect`. Portable definition only; no parent/implementation task branch or developer worktree has been materialised here.

## Objective

Expose the existing Shop-owned Recovery Detail, conversation messages and related recoveries through three strictly authenticated, read-only merchant endpoints, with independent cursor pagination.

## Context

The developer visually approved the modular Woo Recoveries list and requested the same Shopify detail experience. The Stage 1 Woo detail shell displays intentional unavailable states until the read API exists. API-009 provides only a paginated list. This task is the newly authorised **bounded read-only data dependency** of that UI, not authorisation to implement checkout ingestion, recovery creation or background jobs. The current Stage 1 Woo detail shell's JavaScript/CSS lint findings are separate Woo task corrections.

## Scope

- `moda-interact-api/src/merchant/recoveries/detail/`: request/response contracts, cursor codec, query services, route and focused tests.
- `src/index.ts` and `src/woocommerce/installation/routes.ts`: register the detail route behind the existing Woo installation credential authenticator.
- `openapi/merchant-recovery-detail-v1.yaml`: document the three versioned read endpoints.
- Reuse the existing generated Prisma data model, shop/installation identity and shared structured logger.

## Out of Scope

- WooCommerce WordPress REST proxy, React state/controllers, browser-side data integration, UI styling and translations (Stage 3).
- All writes, checkout/order ingestion, background jobs, coupons/offers, commerce tools, Redis or new telemetry mechanisms.
- Database schema changes, migrations, Shared package publication, Gateway work and Shopify source modifications.
- `docs/decisions/**/_index.md` changes during this review session.

## Requirements

- `GET /v1/merchant/recoveries/:recoveryId` returns `schemaVersion:1`, `timeZone`, `id`, status, exact decimal value/currency/incomplete, permitted customer name/email, `hasConversation`, and detected/messageSent/engaged/completed/expired milestones.
- `GET /v1/merchant/recoveries/:recoveryId/messages?cursor=…` returns at most 50 chronologically ordered messages with direction, sender, safe text/transcription state and delivery receipts. `window=latest` loads the most recent 50. `window=first` or no window starts from the oldest. Return `previousCursor` and `nextCursor` independently of related recoveries.
- `GET /v1/merchant/recoveries/:recoveryId/related?cursor=…` returns at most five newest-first related recoveries, with independent forward/backward cursors. Related means exact durable Customer ID within the authenticated shop—not email, name, phone or guessed identity.
- Cursor scope binds `shopId`, `recoveryId` and section. Validate canonical base64url encoding, length, fields and ISO timestamp. It is not an authorisation token.
- Authenticate installation bearer plus `x-moda-installation-id` on each read. Recheck active same-site Woo Shop/installation and recovery ownership inside a repeatable-read transaction; reject conflicting foreign customer/conversation association. Missing and foreign recoveries both return 404 without PII.
- All reads are bounded; no full conversation/history exports. Do not send checkout tokens, phone, full customer profile, raw provider media identifiers, provider credentials or messages from another recovery.
- Reject invalid route/query/cursor with 400, missing/invalid installation with 401, missing/foreign recovery with 404, integrity mismatch with 409, and unexpected failure with 500. Do not leak internal errors or secrets. Private no-store response headers.
- Keep each code module focused and testable. Reuse existing Prisma indexes; do not create redundant query or activity tables.

## Work Items

- [ ] Implement independent bounded detail, message and related-reader services.
- [ ] Add canonical resource-bound cursor parsing and negative tests.
- [ ] Add privileged routes and integrate with existing Woo installation router.
- [ ] Document exact request/response/error contracts in OpenAPI.
- [ ] Cover tenant isolation, old/revoked installation state, missing resources, safe projection, latest window, 50/5-page navigation and timestamp ties.
- [ ] Record validation evidence and stop at Architect review.

## Interfaces / Contracts

- Owner/producer: `moda_api`; consumer: future Woo WordPress PHP REST proxy, never browser-to-hosted API.
- Source of truth: existing `CheckoutRecovery`, `Customer`, `Conversation`, `ConversationMessage`, `Shop` and `WooCommerceInstallation` models.
- Parent contract: API-009 authenticates/authorises the same Woo shop and provides navigation IDs; it does not expose detail records.
- Version: numeric `schemaVersion:1`; cursor encoding and independent page size limits documented in `openapi/merchant-recovery-detail-v1.yaml`.

## Dependencies

- `ARCH-035-API-009`: must be architect-accepted and developer-completed before this task becomes formally Ready. The supplied proposed patch is based on its Attempt 2 source.

## Enables

- The future WooCommerce Stage 3 recovery-detail data integration task; no dependent execution before API acceptance and developer completion.

## Acceptance Criteria

- [ ] Summary fields and milestones match the existing Shopify Recovery Detail information architecture without requiring Shopify auth/route imports.
- [ ] Message page length ≤50, related page length ≤5; previous/next/latest navigation never omits or repeats tied-timestamp rows.
- [ ] Both paginated sections maintain independently scoped cursors.
- [ ] Invalid, revoked, Shopify/foreign Shop and malformed input fail closed with safe HTTP responses.
- [ ] Missing and foreign Recovery IDs produce the same 404 response with no cross-tenant data disclosure.
- [ ] Sensitive tokens/media/phones are excluded and no full transcripts are exported.
- [ ] Query and response validators, code, and OpenAPI are consistent.
- [ ] No database, background, Shopify, Woo plugin or `_index.md` changes.

## Validation

- [ ] `npm run typecheck`.
- [ ] `npm run lint`.
- [ ] Focused detail read, pagination and route tests.
- [ ] `npm run test` and `npm run build`.
- [ ] Real/disposable PostgreSQL smoke with an owned Recovery and separately paginated messages/related records, including foreign-shop negative test.
- [ ] `git diff --check` and task-worktree isolation/synchronisation evidence where materialised.

## Stop Condition

After validation, record the Completion Report and return for Architect review. Do not implement the WooCommerce proxy/React Stage 3, or any other domain work. Completion-mode developer requires explicit developer completion after review.

## Implementation Notes

Reuse established Woo installation authentication, tenant isolation, Prisma schema, error policy, request/response bounds and shared structured logging. Keep summary, cursor and paginated-query logic separately testable. No new index or migration is authorised; inspect and reuse the existing `(conversationId, createdAt, id)` and `(shopId, customerId, detectedAt, id)` indexes.

## Completion Report

### Status

Not Started — proposed portable patch awaiting developer application and validation.

### Files Changed

Not yet recorded in developer worktree.

### Work Completed

Pending developer validation.

### Validation Results

Pending developer runtime; isolated architect-side checks are not completion evidence.

### Deviations

None.

### Assumptions

API-009 Attempt 2 and the approved existing recovery schema are in the developer checkout.

### Unresolved Issues

Real PostgreSQL fixture evidence and canonical task-worktree launch evidence pending.

### Architectural Concerns

None beyond preserving cursor compatibility after publication.

## Architect Review

### Review Status

Accepted — retrospective code-based review, 16 October 2026.

### Review Notes

Authenticated summary, messages and related read endpoints, separate page/cursor logic, safe projection, OpenAPI and focused tests are present.

This is a **retrospective, source-code-based architectural reconciliation** against the developer-provided 2026-10-16 10:58:55 workspace ZIP. The source snapshot is not the historical paired task worktrees or Git branches; an original launcher packet, accepted task commit, Completion Report validation and LocalWP run cannot be reconstructed from it. Retain `attempt: 0` and the original developer/agent Completion Report; no historical execution claim or test pass is manufactured.

### Reviewed Files

- `moda-interact-api/src/merchant/recoveries/detail/{routes.ts,read.service.ts,pages.ts}`
- `moda-interact-api/src/merchant/recoveries/detail/{routes.test.ts,pages.test.ts,openapi-contract.test.ts}`
- `moda-interact-api/openapi/merchant-recovery-detail-v1.yaml`

### Validation Reviewed

Test files for route, tenant, pagination, query/contract and (where applicable) PostgreSQL paths inspected but **not executed**: this snapshot has no Node dependencies or database services. OpenAPI path is present. No live/disposable PostgreSQL, lint/typecheck/build or launcher/worktree evidence was available.

### Architecture Conformance

The inspected implementation provides the task's bounded capability and uses the approved architecture/repository boundary. The source-based reconciliation is not a claim of unobserved runtime validation, task worktree isolation or release certification.

### Follow-up

`completion_mode: developer` is authoritative. **Do not change this task to `complete` from architect acceptance alone.** Await explicit developer completion (`/moda_developer_update ARCH-035-API-013 complete`) after the developer reviews the evidence and any missing required validation. For API-013, complete API-009 first to satisfy its recorded dependency.
