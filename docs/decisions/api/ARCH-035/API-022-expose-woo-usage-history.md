---
id: ARCH-035-API-022
architecture_id: ARCH-035
title: Expose authoritative WooCommerce usage history and entitlement periods
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-035-WOOCOMMERCE-018
created: 2026-10-22
updated: 2026-10-22
---
# ARCH-035-API-022: Expose authoritative WooCommerce usage history and entitlement periods

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Historical `ARCH-035-API-007` remains Superseded; this contract matches the **completed** Usage History UI instead of its incompatible original query shape.
- Reference: `moda-interact/app/services/usage/history.server.ts`, `app/components/dashboard/UsageEvents.tsx`.

## Objective

Expose real, merchant-safe WooCommerce usage events and current/past Moda entitlement periods from existing billing records, with correct Free-plan behaviour and reliable paging.

## Context

`ARCH-035-WOOCOMMERCE-006` is Complete as UI-only. `src/usage-history/usage-history-client.js` explicitly sets `available:false`. Its controller expects `usageEvents`, `usagePagination` and `periodPage` with period cursors; the old superseded API-007 contract does not match that UI.

## Scope

- Implement authenticated GET route, request/response validation, service, OpenAPI, route registration, focused unit/integration tests and shared structured logging in `moda-interact-api`.
- Read existing `UsageEvent`, `BillingPeriod`, `Subscription`, `CheckoutRecovery` (for safe optional source link) and applicable purchased/promotional credit context. No new schema or usage-recording writes.
- Reuse established Shopify history cursor/paging semantics where provider-neutral, without Shopify authentication or Shopify-only reporting fields.

## Out of Scope

- Payment/purchase history, Woo subscription charging, new usage consumption or refunds, changes to UsageEvent writers, Shopify Billing UI, new migrations, WordPress proxy/UI implementation, `_index.md` files.

## Requirements

1. Hosted `GET /v1/merchant/usage-history?view=current|past&periodId=<opaque>&kind=ALL|RECOVERY_CONVERSATION&page=1&pageSize=10&periodCursor=<opaque>` is installation-authenticated, tenant-derived and read-only; no `shopId` parameter. Supported page sizes **10, 25, 50, 100**; page 1–1000; period cursor ≤1024 URL-safe chars; period ID ≤128 bounded chars. Reject unknown/duplicate filter parameters, malformed dates/IDs, foreign periods and cursors with stable `400`/`409` responses rather than silently falling back.
2. Return `{schemaVersion:1,state:'ready'|'unavailable',usageView:'current'|'past',periodPage,usageEvents,usagePagination}` with ISO dates and authoritative numeric totals. `periodPage:{items:[{id,periodStart,periodEnd}],previousCursor:null|string,nextCursor:null|string}` (max 25 periods). `usagePagination:{page,pageSize,total,totalQuantity,billId:null|string,periodStart:null|string,periodEnd:null|string}`. `usageEvents:[{id,metric,quantity,occurredAt,sourceRecovery:null|{recoveryId,customerName}}]`. The optional `customerName` must be supplied **only** when the linked recovery and customer are confirmed to belong to the authenticated Shop; otherwise `sourceRecovery:null`.
3. `current` for a paid Shop selects the currently applicable Moda entitlement `BillingPeriod`/30-day entitlement window; `past` selects closed Shop-owned periods. Woo payment-provider billing month is not the Moda entitlement interval. Period list/cursor identity and sort use `(periodStart DESC,id DESC)`; usage rows use `(occurredAt DESC,id DESC)`. Cursors are scoped to Shop and view, and tampered/cross-Shop tokens are rejected. Correct offsets/caps prevent unbounded data retrieval.
4. **Free lifetime:** if no real BillingPeriod exists, `current` reads genuine Shop-owned unperiodised Free-plan recovery usage events without manufacturing a BillingPeriod ID; `past` is empty unless real historical periods exist. A paid Shop without a qualifying current period yields explicit empty/unavailable state rather than reading all history. No `0` invented for unavailable data.
5. Usage rows read only matching `shopId` and provider `WOOCOMMERCE` or explicitly valid provider-neutral history. Do not include another provider's Shop or Shopify-report-only data. Real correction/compensation records retain their semantics/sign; totalQuantity must reflect the selected event set. Never invent charges or omit compensating entries merely to make totals positive.
6. No raw provider billing IDs, idempotency keys, sensitive source payload, PSP event handles, Meta/Shopify secret data or cross-Shop customer details in response or logs. Use bounded selects, no-store response, runtime DTO validation, API-owned OpenAPI and shared logging.

## Work Items

- [ ] Confirm `UsageEvent`/`BillingPeriod` schema, legitimate provider-neutral rows and Free lifecycle behaviour in current code.
- [ ] Implement tenant-scoped period selection, pagination and current/Free rules.
- [ ] Implement usage event read and same-Shop recovery linking, with safe correction handling.
- [ ] Add strict request/response schema, API route registration, OpenAPI and error mapping.
- [ ] Test negative, period, provider, Free, billing-cadence, paging and correction paths.

## Interfaces / Contracts

- Contract owner: `moda-interact-api`; consumer is `ARCH-035-WOOCOMMERCE-018` via the approved WordPress PHP client/proxy.
- Existing database: `billing.UsageEvent`, `billing.BillingPeriod` and `commerce.CheckoutRecovery`. No Shared queue/writer contract changes.
- Controller/view model must match `src/usage-history/{usage-history-controller,usage-history-toolbar,usage-history-results}.js`.

## Dependencies

None. Existing Woo installation and Billing schema foundations are recorded Complete; verify repository pins when claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-018`.

## Acceptance Criteria

- [ ] Real Free-lifetime, paid current/past, cancellation/history, empty, correction/compensation and period pagination cases return correct event sets and totals.
- [ ] Shop crossover, tampered cursor, foreign period, malformed filters, incorrect platform and disabled/revoked installation produce safe nonleaking errors.
- [ ] Correct same-Shop recovery links, stable chronological ordering, 10/25/50/100 paging and 25-period cursor semantics.
- [ ] Shopify usage routes and financial purchase history are unchanged; OpenAPI, shared logging and no-store handling verified.

## Validation

- [ ] Focused unit/route and disposable DB tests including period-boundary/Free/correction/tenant/provider cases.
- [ ] Repository-declared typecheck/lint/build and existing usage regressions where applicable.
- [ ] `git diff --check`, launcher-resolved worktree/commit evidence and Completion Report.

## Stop Condition

Set `status: review` with real tests and stop; API-022 does not implement the Woo plugin consumer.

## Implementation Notes

Prefer small route, period-cursor, query and projection modules. Distinguish `occurredAt` from database insertion time; never mislabel a Woo billing cycle as a 30-day entitlement period. If genuine Free usage storage contradicts the historical task description, report exact evidence before altering domain accounting.

## Completion Report

### Status

Not Started — portable definition, not claimed or materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

No Git worktree, branch, implementation commit, provider credentials, deployment or acceptance is created by this task definition.

### Unresolved Issues

None recorded at definition time; report concrete schema/contract gaps to the architect rather than broadening scope.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending.

### Review Notes

Not reviewed. This is a new task definition, not an accepted implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed from implementation and test evidence.

### Follow-up

Architect acceptance required before enabling dependants.
