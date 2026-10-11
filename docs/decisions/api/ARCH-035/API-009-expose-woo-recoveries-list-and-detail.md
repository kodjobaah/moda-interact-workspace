---
id: ARCH-035-API-009
architecture_id: ARCH-035
title: Expose shop-authorised paginated recoveries read API for Woo UI
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-API-009: Expose shop-authorised paginated recoveries read API for Woo UI

## Architecture

- Architecture ID: `ARCH-035`.
- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`.
- Task re-scoped from a superseded checkout-dependent list/detail API to an explicitly approved **read-only list** supporting the inspected Woo Recoveries UI shell.
- Portable task definition: no developer worktree or Git branch has been created or claimed by the architect.

## Objective

Provide the WooCommerce merchant Recoveries screen with an authenticated, paginated and filtered list of **existing** `CheckoutRecovery` data, using no new persistence or recovery processing.

## Context

The developer approved a three-stage implementation: (1) modular responsive React shell, (2) read-only hosted API for real data with pagination, (3) WordPress REST proxy and React data integration. Stage 1 is manually visually validated. This task implements **Stage 2 only**. The old task's dependency on BACKGROUND-002 no longer applies: no ingestion or recovery materialisation belongs to this task. Real data must already exist for the authenticated Woo Shop; it is never copied from a Shopify Shop.

## Scope

- `moda-interact-api/src/merchant/recoveries/`: request/query parsing, tenant-safe read service, response contract, runtime validation and route.
- `moda-interact-api/src/index.ts` and `src/woocommerce/installation/routes.ts`: register under existing Woo installation authentication/routing.
- `moda-interact-api/openapi/merchant-recoveries-v1.yaml`: versioned GET contract.
- Focused tests for pagination, query filtering, date boundaries/DST, tenant isolation, redaction, empty/missing states and error responses.

## Out of Scope

- WooCommerce plugin PHP/JS UI client or REST proxy: separate Stage 3 task.
- Recovery detail, transcript/history, related recoveries and server-side actions: separate task(s).
- Checkout/order activity producers, recovery materialisation, background/queue or delivery logic.
- New database models/migrations, Shopify changes, Shared publication and Gateway changes.
- Any `docs/decisions/**/_index.md` changes before final reconciliation.

## Requirements

- `GET /v1/merchant/recoveries` authenticated with server-only Woo installation bearer and `X-Moda-Installation-Id`; no `shopId` query or URL parameter.
- Query: `from`, `to` (`YYYY-MM-DD`, inclusive store-local dates); `q` (customer name/email, max 100 characters); `status` (`all`, `ongoing`, or an existing CheckoutRecovery status); `page` (1..9999); `pageSize` (10, 20, 25, 50; default 25).
- Default date window: last 30 shop-local calendar days. Date span max 366 days, no future dates. Prefer persisted IANA shop timezone; fallback UTC when unset/invalid.
- Read `Shop`, active Woo installation, exact filtered count and requested page in **one repeatable-read snapshot**; order by `(detectedAt DESC, id DESC)`, paginate with database `skip/take`, clamp out-of-range page to last page.
- Response: `schemaVersion: 1`, applied dates/search/status/timezone, `page`, `pageSize`, `total`, `totalPages`, `hasPrevious`, `hasNext` and `items`. Each item includes only internal recovery ID, status, detected/last-activity times, exact decimal amount string, currency, tenant-safe customer displayName/email. Do not expose checkout URLs/tokens, provider IDs, phone, secrets or full customer profiles.
- Fail closed on invalid/revoked/foreign installation, Shopify Shop platform, inconsistent Shop binding or foreign Customer references. No transaction writes. Return 400 invalid filter, 401 unauthenticated, 409 integrity conflict, 500 internal failure, with no private error details.
- The server-to-plugin PHP REST integration is **not** part of this task; lack of UI data until Stage 3 is expected.

## Work Items

- [ ] Implement the bounded read-only route, parser, query service and response validator.
- [ ] Add the API route to existing Woo installation route composition.
- [ ] Document authentication, pagination and response schema in OpenAPI 3.1.
- [ ] Cover pagination, default/filtered reads, timezone/DST, disconnected shop, foreign data and secret redaction.
- [ ] Record actual validation in the Completion Report and return to Architect review.

## Interfaces / Contracts

- Producer/owner: `moda_api` in `moda-interact-api`.
- Source of truth: existing Prisma `CheckoutRecovery`, `Customer`, `Shop`, `WooCommerceInstallation`, generated from existing database submodule. No Shared package release.
- Consumers: future privileged WooCommerce WordPress REST proxy, then modular React Recoveries adapter. Browser must not call this hosted API directly.
- Contract: `openapi/merchant-recoveries-v1.yaml`, `GET /v1/merchant/recoveries`, `schemaVersion: 1`.
- Pagination must be request-scoped and consistent for count and rows; concurrent writes between separate page requests may shift offset pages. Cursor paging may be proposed later only through a separate explicit contract decision.

## Dependencies

None. The endpoint is read-only over existing recovery data and the accepted ARCH-026 Woo installation identity. No ARCH-035 Background task is a dependency.

## Enables

Stage 3: architect-defined WooCommerce REST proxy + React list integration task, after API-009 is accepted and developer-completed.

## Acceptance Criteria

- [ ] Page 1 and later pages have correct `total`, `totalPages`, Previous/Next flags, size limits and deterministic ordering.
- [ ] Filter and count use identical tenant-scoped query predicates, with one repeatable-read snapshot.
- [ ] Date range uses store-local inclusive dates, including DST transitions, and rejects invalid/oversized ranges.
- [ ] All requests require a currently active Woo installation; Shopify/foreign data cannot be read.
- [ ] Payload never includes checkout tokens/URLs, phone, provider credentials or cross-tenant customer data.
- [ ] Route and OpenAPI definitions agree; error codes are safe.
- [ ] No schema, migration, Woo plugin, Background or Shopify implementation changed.

## Validation

- [ ] `npm run typecheck`.
- [ ] `npm run lint`.
- [ ] Focused `node --test` / `tsx --test` recoveries suites.
- [ ] `npm run test` and `npm run build` where environment permits.
- [ ] Tenant-scoped live/disposable Postgres smoke test with developer-provided data and credentials (no credentials in reports).
- [ ] `git diff --check` and clean task-worktree/sync evidence, when materialised in the developer workspace.

## Stop Condition

Stop after delivering the API and evidence for Architect review. Do not implement Stage 3, the recovery detail API, or follow-on tasks automatically. With `completion_mode: developer`, final completion requires the developer's explicit decision after review.

## Implementation Notes

Reuse the existing Woo installation authenticator and native route composer. Do not introduce custom authentication, a new merchant identity, a second database or Shopify route imports. Keep query, service, routes, contracts and tests separated. Prefer a documented bounded page offset over an unbounded export.

## Completion Report

### Status

Not Started. The developer may apply a portable proposed implementation patch; that does not by itself claim, complete or accept the canonical task.

### Files Changed

None recorded in developer worktree.

### Work Completed

Pending developer application and validation.

### Validation Results

Pending developer validation.

### Deviations

None.

### Assumptions

Developer has existing CheckoutRecovery data in the authenticated Woo Shop.

### Unresolved Issues

Real database/LocalWP smoke and implementation worktree evidence are outstanding.

### Architectural Concerns

Future offset pagination may need cursor migration for extreme page depth or concurrent write stability; do not change this v1 contract without approval.

## Architect Review

### Review Status

Pending developer validation and implementation review.

### Review Notes

This task was explicitly re-scoped following the developer's UI-shell approval and request for a paginated read endpoint. A proposed code patch is not a durable acceptance decision.

### Reviewed Files

None from a developer implementation branch.

### Validation Reviewed

Not yet received from developer runtime.

### Architecture Conformance

Pending.

### Follow-up

Stage 3 UI data integration is defined only after the API contract is accepted. `_index.md` remains untouched.
