---
id: ARCH-035-WOOCOMMERCE-018
architecture_id: ARCH-035
title: Connect WooCommerce Usage History screen to authoritative usage API
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-022
  - ARCH-035-WOOCOMMERCE-006
enables:
  - ARCH-035-SYSTEM-TEST-007
created: 2026-10-22
updated: 2026-10-22
---
# ARCH-035-WOOCOMMERCE-018: Connect WooCommerce Usage History screen to authoritative usage API

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- API contract: `ARCH-035-API-022`; UI predecessor `ARCH-035-WOOCOMMERCE-006` remains accepted Complete.

## Objective

Replace the Usage History UI's hard-coded unavailable transport with the approved authenticated Woo API and show real current/past events and billing-period selections.

## Context

`src/usage-history/usage-history-client.js` currently returns `{available:false}`. The UI/controller/toolbar/results already exist and must be reused; Billing purchase history is a separate feature and must not be altered.

## Scope

- Add WordPress `GET /wp-json/moda-interact/v1/merchant/usage-history` privileged proxy and allowlisted ModaApiClient route to hosted `GET /v1/merchant/usage-history`.
- Replace only `src/usage-history/usage-history-client.js` transport and minimal controller/hook glue needed for API-022, retaining existing state and presentation behavior.
- Extend focused WP REST/client tests, controller tests, translations if necessary, build/ZIP evidence.

## Out of Scope

- New usage events, billing periods, fee calculations, purchases/refunds, PHP direct database access, hosted API/database code, cross-Shop analytics, new dashboard design, `_index.md` changes.

## Requirements

1. WordPress `manage_woocommerce` and `X-WP-Nonce` gate all reads. Resolve Woo installation credentials server-side; enforce canonical site identity and post-fetch credential rotation/disconnect fence. The browser must not receive hosted API credentials or specify `shopId`.
2. Forward only the documented `view`, `periodId`, `kind`, `page`, `pageSize`, `periodCursor` filters within API-022 bounds. Preserve `_locale=user` handling only when appropriate for WordPress; never forward arbitrary paths, headers or provider IDs.
3. Parse API-022 `schemaVersion:1` response and map to existing `usageEvents`, `usagePagination` and `periodPage` view model. Valid real empty results show **No recorded usage**, while unavailable/401/403/invalid period/cursor/5xx have distinct states, without synthetic records or zero totals.
4. Honor existing Current/Past tabs, period next/previous cursor, 10/25/50/100 rows per page, event kind filter, page reset rules, server-driven total/totalQuantity and same-Shop recovery links. Use existing WordPress locale-aware formatting and no content escaping errors.
5. On refresh/disconnect/unmount/identity change, abort or discard stale responses. Invalid period/cursor uses existing clear-selection affordance; 401 prompts reconnect, 403 disables access; no infinite retry/loop or duplicate HTTP requests from one control event.
6. Keep `Billing > Purchase History` and all existing WordPress navigation unchanged except for minimal Usage History integration changes. 20 locales must still compile.

## Work Items

- [ ] Check API-022 accepted OpenAPI and current Woo `ModaApiClient`/REST patterns.
- [ ] Add bounded privileged GET proxy, security/response handling and live client.
- [ ] Wire existing Usage History controller/hook and verify all filter/page/period transitions.
- [ ] Add tests for 401/403/409/5xx/disconnect, invalid cursors, no usage, Free lifetime and paid periods.
- [ ] Run repository validation and document LocalWP manual live checks.

## Interfaces / Contracts

- WP: `GET moda-interact/v1/merchant/usage-history`.
- Hosted: `GET /v1/merchant/usage-history` (owner API-022).
- No new shared queue schema; UI uses API-022 response validated server-side and in Woo client.

## Dependencies

- `ARCH-035-API-022` (architect-accepted Complete).
- `ARCH-035-WOOCOMMERCE-006` (existing completed UI).

## Enables

- `ARCH-035-SYSTEM-TEST-007`.

## Acceptance Criteria

- [ ] Real Woo usage populates Current/Past UI, filters, period cursors, recovery links, totals and pagination without fabricated data.
- [ ] Free lifetime and paid entitlement windows present correctly; purchased credit history remains separate.
- [ ] Disconnect/rotation, nonce/capability denial, tampered query/cursor and hosted failure cannot leak other-Shop usage or show stale results.
- [ ] Accessibility, 20 native WP Admin languages and production plugin build remain valid.

## Validation

- [ ] Relevant `npm run test:js`, `npm run test:i18n`, `npm run i18n:verify:20`, `npm run test:php`, `npm run build`, `npm run plugin-zip` (actual declared scripts), focused PHP validation and JS controller tests.
- [ ] User/developer LocalWP real authenticated workflow with owned current/past events; no invented production success evidence.
- [ ] `git diff --check`, canonical worktree evidence and Completion Report.

## Stop Condition

Set `status: review` and return to `moda_architect`, then STOP. Do not implement the system test under this task.

## Implementation Notes

Reuse existing `UsageHistoryController` and view, and keep PHP proxy/request validation, JS transport and view-model mapping separately testable. No new generic logging implementation.

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
