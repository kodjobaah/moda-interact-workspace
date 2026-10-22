---
id: ARCH-035-API-022
architecture_id: ARCH-035
title: Expose authoritative WooCommerce usage history and entitlement periods
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 35
executor: developer
claimed_at: 2026-10-22T09:40:33Z
attempt: 1
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

- [x] Confirm `UsageEvent`/`BillingPeriod` schema, legitimate provider-neutral rows and Free lifecycle behaviour in current code.
- [x] Implement tenant-scoped period selection, pagination and current/Free rules.
- [x] Implement usage event read and same-Shop recovery linking, with safe correction handling.
- [x] Add strict request/response schema, API route registration, OpenAPI and error mapping.
- [x] Test negative, period, provider, Free, billing-cadence, paging and correction paths.

## Interfaces / Contracts

- Contract owner: `moda-interact-api`; consumer is `ARCH-035-WOOCOMMERCE-018` via the approved WordPress PHP client/proxy.
- Existing database: `billing.UsageEvent`, `billing.BillingPeriod` and `commerce.CheckoutRecovery`. No Shared queue/writer contract changes.
- Controller/view model must match `src/usage-history/{usage-history-controller,usage-history-toolbar,usage-history-results}.js`.

## Dependencies

None. Existing Woo installation and Billing schema foundations are recorded Complete; verify repository pins when claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-018`.

## Acceptance Criteria

- [ ] Real Free-lifetime, paid current/past, cancellation/history, empty, correction/compensation and period pagination cases return correct event sets and totals. (Focused tests cover Free, paid, historical periods, empty/unavailable, signed corrections and paging; an explicit cancelled-subscription history scenario is not evidenced.)
- [x] Shop crossover, tampered cursor, foreign period, malformed filters, incorrect platform and disabled/revoked installation produce safe nonleaking errors.
- [x] Correct same-Shop recovery links, stable chronological ordering, 10/25/50/100 paging and 25-period cursor semantics.
- [ ] Shopify usage routes and financial purchase history are unchanged; OpenAPI, shared logging and no-store handling verified. (The implementation patches are scoped away from those legacy routes, but no existing-route regression suite was run in the supplied transcript.)

## Validation

- [x] Focused unit/route and disposable DB tests including period-boundary/Free/correction/tenant/provider cases.
- [ ] Repository-declared typecheck/lint/build and existing usage regressions where applicable. (`typecheck`, `lint`, `build` passed; existing usage regressions not evidenced.)
- [ ] `git diff --check`, launcher-resolved worktree/commit evidence and Completion Report. (`git diff --check` passed, dedicated worktree paths/branch and local implementation HEAD evidenced; launcher preparation/synchronisation and remote push evidence remain outstanding.)

## Stop Condition

Set `status: review` with real tests and stop; API-022 does not implement the Woo plugin consumer.

## Implementation Notes

Prefer small route, period-cursor, query and projection modules. Distinguish `occurredAt` from database insertion time; never mislabel a Woo billing cycle as a 30-day entitlement period. If genuine Free usage storage contradicts the historical task description, report exact evidence before altering domain accounting.

## Completion Report

### Status

In Progress — developer-owned canonical Attempt 1 (`claimed_at: 2026-10-22T09:40:33Z`). Implementation changes and focused validation are recorded below for pre-review reconciliation. **Do not change task status to `review` until the unchecked acceptance/validation items and required publication/worktree evidence are resolved.** The `attempt1` and `attempt2` implementation patch filenames are patch revisions within this one claimed task attempt.

### Files Changed

Implementation changes in `moda-interact-api` (Attempt 1 patch plus incremental Attempt 2 correction):

- `openapi/merchant-usage-history-v1.yaml`
- `package.json`
- `scripts/test-arch035-usage-history-postgres.mjs`
- `src/composition/merchant.ts`
- `src/merchant/usage-history/contract.ts`
- `src/merchant/usage-history/cursor.ts`
- `src/merchant/usage-history/history.service.ts`
- `src/merchant/usage-history/periods.ts`
- `src/merchant/usage-history/routes.ts`
- `src/merchant/usage-history/schema.ts`
- `src/merchant/usage-history/sources.ts`
- `tests/integration/merchant/usage-history/usage-history.postgres.test.ts`
- `tests/unit/composition/real-route-registration.test.ts`
- `tests/unit/merchant/usage-history/contract.test.ts`
- `tests/unit/merchant/usage-history/cursor.test.ts`
- `tests/unit/merchant/usage-history/history.service.test.ts`
- `tests/unit/merchant/usage-history/openapi.test.ts`
- `tests/unit/merchant/usage-history/periods.test.ts`
- `tests/unit/merchant/usage-history/routes.test.ts`

Parent workspace update: **only this task definition / Completion Report**. No migrations, WooCommerce UI/proxy code, Shopify usage route, purchase-history implementation or domain `_index.md` file is changed by these patches.

### Work Completed

- Added read-only, installation-authenticated `GET /v1/merchant/usage-history` with strict filter/query parsing, response validation, no-store handling, privacy-safe errors, OpenAPI, route registration and shared structured logging.
- Added Shop-scoped Free lifetime reads for genuine unperiodised usage, paid current/past Moda entitlement-period selection, signed and scoped keyset cursors (25 historical periods per page), and stable event paging (10/25/50/100).
- Added WooCommerce-only usage filtering, purchased/promotional credits, signed correction inclusion and authoritative quantity totals, and same-Shop-only recovery/customer details.
- Added focused unit, contract, route, cursor, OpenAPI and disposable PostgreSQL tests.
- Applied the incremental patch revision to resolve overlapping historical test fixtures, nullable/response TypeScript issues and test ESLint errors. Git commits/review attempts do not map 1:1 to patch revision numbers.

### Validation Results

Evidence: supplied developer terminal transcript `typescript(20261022-100057)`, 22 October 2026, after both implementation patch revisions.

- `git diff --check`: passed (no diagnostics).
- `npm run test:arch035-usage-history:unit`: **passed, 14/14**.
- `npm run test:arch035-usage-history:postgres`: **passed, 1/1**, against disposable PostgreSQL; **58 migrations** applied to fixture database.
- `npm run typecheck`: **passed**, including Prisma Client generation.
- `npm run lint`: **passed**, with `eslint . --max-warnings=0`.
- `npm run build`: **passed**, including Prisma Client generation and TypeScript production build.
- Prior transcript `typescript(20261022-094854)` had one failing integration assertion, two type errors, eight ESLint errors and blocked build; the later run passed all the repeated checks.
- Not evidenced: `npm test` or an existing Shopify/usage-route regression suite; remote branch publication/ancestry; explicit cancelled-subscription history test.

### Branch and Worktree Evidence

- **Implementation worktree** from developer `pwd`: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-022`.
- **Implementation branch** from developer command: `task/ARCH-035-API-022`; **local HEAD:** `98f0c9ee0fb32d77ed75f3e9285057f5dbd8b45b`.
- **Implementation working tree:** clean (`git status --short` emitted no entries). The provided `git worktree list` includes this dedicated implementation worktree and separately lists the main checkout and other task worktrees.
- **Implementation recursive submodule snapshot:** `database` at `807af3393f992c8a19bc9ef278d7e7e05f41799d` (`heads/main`) in the supplied `git submodule status --recursive` output; this alone does not prove launcher-time synchronisation.
- **Parent task worktree** from developer `pwd`: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-022`; branch from developer output: `task/ARCH-035-API-022`.
- **Canonical developer claim** in the uploaded parent task file: `execution_mode: developer`, `completion_mode: developer`, `status: in_progress`, `executor: developer`, `attempt: 1`, `claimed_at: 2026-10-22T09:40:33Z`. The previous task-update patch was rejected due to pre-claim context, and is superseded by this rebased report patch.
- **Not yet evidenced:** launcher-resolved prepared packet with both worktree IDs and start-of-attempt fetch/fast-forward/merge evidence; parent task HEAD and both remote task-branch push confirmations; remote ancestry for the implementation HEAD.

### Deviations

- No implementation scope expansion identified in the delivered changes.
- Documentation-only patch rebased onto the developer-claimed parent task file; no modification to `Developer Takeover Amendment` or `Architect Review`.
- Full worktree preparation and VCS publication conformance cannot yet be established from the supplied output.

### Assumptions

- The uploaded `moda-interact-workspace-ARCH-035-API-022.zip` represents the developer's current parent task file and API source snapshot. It does not itself attest remote Git state.
- All implementation work is one developer-owned canonical **Attempt 1**. `attempt2` is an incremental delivery patch, not a separate `/moda_developer_create` claim.

### Unresolved Issues

- Complete or explicitly reconcile the cancelled-subscription/history acceptance scenario and existing usage-route regressions before marking the remaining acceptance/validation items satisfied.
- Provide launcher preparation/start-of-attempt synchronisation evidence or document exact workflow non-conformance; verify both parent and implementation task branch publication. Record parent task report commit after publication.
- Submit through `/moda_developer_update ARCH-035-API-022` for developer-mode reconciliation/review; with `completion_mode: developer`, final completion requires a later explicit developer decision after a durable Accepted review.

### Architectural Concerns

No new schema migration, shared queue contract, cross-repository implementation or altered repository ownership was introduced by the supplied API changes. Final architecture conformance remains subject to authorised review.

## Developer Takeover Amendment — 2026-10-22

The developer explicitly invoked `/moda_developer_create ARCH-035-API-022` for this agent-owned task. The task is transferred to developer execution with developer-controlled completion while preserving the assigned agent `moda_api`, repository ownership, task scope, dependencies, acceptance criteria and validation requirements. The canonical launcher will record the Attempt 1 claim after this amendment is published.

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
