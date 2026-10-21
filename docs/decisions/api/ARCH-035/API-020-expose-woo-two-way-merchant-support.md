---
id: ARCH-035-API-020
architecture_id: ARCH-035
title: Expose Woo two-way merchant Support API
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 31
executor: developer
claimed_at: 2026-10-21T21:54:18Z
attempt: 1
depends_on: []
enables:
  - ARCH-035-WOOCOMMERCE-016
created: 2026-10-21
updated: 2026-10-21
---

# ARCH-035-API-020: Expose Woo two-way merchant Support API

## Architecture

Architecture ID: `ARCH-035`. Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`. Coordinator: `moda_architect`.

**Lifecycle:** Portable definition from the developer-supplied 2026-10-21 workspace ZIP, now materialised in the canonical parent task worktree. No implementation claim existed before this developer preparation.

## Objective

Expose the existing Shopify-equivalent merchant Support thread/history, compose, and read-state commands to authenticated WooCommerce installations through the hosted API.

## Context

The existing `ARCH-035-API-001` was superseded without implementation during the former UI-only phase. `ARCH-035-WOOCOMMERCE-001` has since delivered the Support UI but its real client still has `read:false`, `send:false`, `markRead:false`. Shopify reference: `moda-interact/app/services/merchant-support/merchant-support.service.ts` and `app/routes/app/merchant-support/route.jsx`. ARCH-046 consent notices use the same existing Support SYSTEM messages; a separate read-only notice endpoint would duplicate this thread.

## Scope

- Add bounded installation-authenticated Support read, send and mark-read routes and register in the current modular API composition.
- Reuse existing support.MerchantSupportThread and support.MerchantSupportMessage, their translation pipeline and Shared merchant-communications validators.
- Ship strict API DTO validation/OpenAPI contract and focused service/route/database tests; keep read and write code in independently testable modules.

## Out of Scope

- No new Support schema/migration, separate notice feed/inbox, customer WhatsApp send, admin queue redesign or Woo/PHP code.
- No merchant Shopify sessions or Shopify-only refund, purchase cancellation or privileged admin actions.

## Requirements

- Provide `GET /v1/merchant/support/messages?page=1&pageSize=25`, `POST /v1/merchant/support/messages` with `{body,actionId}` and `POST /v1/merchant/support/messages/{messageId}/read` with empty body; own exact response DTOs and publish them in OpenAPI. A schemaVersion field is required.
- Read returns page/pageSize/total/totalPages/unread/items, ordered exactly as Shopify merchant Support; include `MERCHANT`, available `ADMINISTRATIVE` and available `SYSTEM`, translated/original display and safe `systemCode`/`systemVersion`. Bounded pageSize 10/25/50; reject invalid/unexpected inputs.
- Authenticate only via existing active Woo installation credentials and derive Shop server-side. Never accept browser-supplied `shopId`, `shopifyUserId`, platform-admin identifier or tenant owner. Preserve Shopify-like ability to read Support in supported restricted lifecycle states; do not relax a revoked/uninstalled installation.
- Validate 500 Unicode graphemes using the published `AuthoredSupportBodySchema` and `countUnicodeGraphemes` contract. Save MERCHANT message with null `shopifyUserId`; preserve default-language/translation rules and `needsAdminResponse`/merchant-version semantics.
- Use per-shop actionId idempotency with unique `sourceKey` (`woo-support:<shopId>:<actionId>` or a deterministically bounded equivalent); same action + body returns the same result, same action + changed body returns conflict. Concurrent duplicates must not produce multiple Support messages or translations.
- Mark-read is monotonic and restricted to the authenticated Shop-owned ADMINISTRATIVE or SYSTEM message; another shop/unknown message must never leak existence. Read is not a send and must not consume usage credits.
- Translation pending-state persistence precedes best-effort queue dispatch; dispatch outage must not discard a committed merchant message. Use Shared structured logging without credentials, message bodies or sensitive PII; protect provider and database failures.
- Compatibility: existing Shopify Support flows, internal admin reply handling, and ARCH-046 SYSTEM notices must remain functional.

## Work Items

- [ ] [ ] Discover and reuse current installation authentication/route/error infrastructure; confirm model and Shared package versions.
- [ ] [ ] Implement read projection, translate/original, paging and unread counts with tenant-scoped SQL.
- [ ] [ ] Implement transactional idempotent merchant compose and translation dispatch.
- [ ] [ ] Implement tenant-scoped monotonic mark-read.
- [ ] [ ] Register routes, strict runtime validation, OpenAPI and focused negative/concurrency/database tests.

## Interfaces / Contracts

- Owner of HTTP DTOs: `moda-interact-api`. Consumers: WooCommerce privileged WordPress REST proxy in `ARCH-035-WOOCOMMERCE-016`; no browser direct hosted credentials.
- Reuse published `@modainteract/moda-interact-shared/merchant-communications` (`AuthoredSupportBodySchema`, translation queue contracts, language/length rules) and existing Prisma Support schema.
- All three hosted routes run only under Woo installation authentication, never Shopify session authentication.

## Dependencies

None

## Enables

- `ARCH-035-WOOCOMMERCE-016`

## Acceptance Criteria

- [ ] Shop A cannot list, send as, or mark-read for Shop B, including stale/rotated/revoked installations.
- [ ] History includes read-only consent/system notices alongside human Admin replies and MERCHANT messages, with Shopify-compatible displayed body and safe metadata.
- [ ] Repeated, concurrent and conflicting action IDs are deterministic and do not create duplicate messages/translations.
- [ ] 500 graphemes accepted and 501 rejected; Unicode/translations and processing/failed admin messages handled correctly.
- [ ] No new tables, support pipelines, billing charges or Shopify regressions.
- [ ] OpenAPI matches validated runtime DTO; errors safely distinguish invalid request, forbidden/unavailable and conflict.

## Validation

- [ ] Run focused route/service tests, disposable Postgres integration including concurrent duplicate actions, tenant isolation, queue-unavailable and Shopify regression tests.
- [ ] Run actual API repo typecheck/lint/build and `git diff --check`, reporting environment blockers precisely.

## Stop Condition

After all required Work Items, Acceptance Criteria and task-specific Validation are satisfied, update the task Completion Report and `status: review`, return to `moda_architect` and STOP. Do not perform dependent tasks, create new task implementation worktrees, merge or push main, or change `docs/decisions/**/_index.md`.

## Implementation Notes

Reuse business rules from Shopify as the behaviour reference, but do not import the Shopify app runtime into the hosted API. Avoid copying reusable published validators. Do not reinterpret the earlier superseded `API-001` as completed or reactivate its history. Keep implementation bounded to the hosted API service.

Start with `scripts/start-agent-task.py --prepare` through the normal `/moda-task` path. The prepared packet proves canonical parent/implementation worktree identity, synchronization and submodule state; record that packet in the Completion Report. Re-read the latest task and architect review before claiming. Use actual repository scripts. The architect in this externally supplied ZIP session has not created any Git branches or worktrees.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-21T21:54:18Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Inspect current canonical developer workspace when materialising; this source ZIP may lag task branches.

### Unresolved Issues

None identified at definition time.

### Architectural Concerns

None identified at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

Definition approved for handoff; no implementation has been accepted.

## Developer Takeover and Materialisation Amendment — 2026-10-21

The developer explicitly invoked `/moda_developer_create ARCH-035-API-020` for this ready agent-owned portable task. The definition was materialised on the canonical parent task branch from the supplied task content. Execution ownership is transferred to the developer and completion requires an explicit developer decision after architect review. The logical repository owner remains `moda_api`; task scope, dependencies, acceptance criteria and validation requirements are unchanged.
