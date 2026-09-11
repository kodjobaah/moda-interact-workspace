---
id: ARCH-007-SHOPIFY-001
architecture_id: ARCH-007
title: Implement Shopify App Pricing subscription verification and typed local projection
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 60
executor: null
attempt: 3
depends_on: 
  - ARCH-007-SHARED-002
  - ARCH-007-DATABASE-003
enables: 
  - ARCH-007-SHOPIFY-002
  - ARCH-007-SHOPIFY-003
  - ARCH-007-BACKGROUND-003
  - ARCH-007-BACKGROUND-008
  - ARCH-007-ADMIN-003
created: 2026-09-07
updated: 2026-09-07T22:41:53+01:00
claimed_at: null
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-SHOPIFY-001: Implement Shopify App Pricing subscription verification and typed local projection

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Replace the simple first-item billing lookup with a deterministic Shopify 2026-07 Active Subscription projection that supports flat-rate plan items, tiered usage items, pending updates and unknown-plan fail-closed semantics.

## Context

Current `ShopifyBillingProvider` picks the first non-null subscription item handle and only returns ACTIVE/TRIALING. With paid usage meters, `items` contains both plan and meter handles. This task is the canonical merchant-request verification path and local Subscription projection writer.

## Scope

Billing provider/types/service and focused routes/tests needed to query Shopify Partner API and persist the accepted DATABASE-003 projection. Adopt the accepted database submodule and exact Shared release.

## Out of Scope

- Merchant billing page/CTA rendering (SHOPIFY-002).
- Uninstall lifecycle (SHOPIFY-003).
- Background scheduled reconciliation.
- Creating Shopify plans/prices/meters.

## Requirements

- Use Partner API 2026-07 endpoint and ActiveSubscription fields exactly listed in ARCH-007 External Shopify Contract Baseline.
- On Partner HTTP/GraphQL failure, throw/surface a billing synchronization error. Never interpret provider failure as `activeSubscription=null`.
- If activeSubscription is null, persist/represent `NO_CONTRACT` and allow the caller to redirect to Shopify hosted pricing; do not create internal Free automatically.
- Identify current plan only from active `FlatRatePrice` item handle(s). Require exactly one handle that maps to an active Moda BillingPlan appropriate to the contract. Do not use array order.
- For mapped `PAID_METERED`, verify configured `shopifyUsageEventHandle` appears as a `TieredPrice` item. Persist a sync error/fail closed if paid mapping lacks the expected usage item.
- For mapped Free plan, require no paid usage reporting semantics and map exact Free plan handle.
- Persist current billing period/cycle, trial, cancel flag, provider subscription ID, `lastSyncedAt`, and provider usage snapshot information only where schema supports it without becoming a second commercial source of truth.
- Read `pendingUpdate`; map its FlatRatePrice plan handle separately and persist observed/mapped pending plan and effective boundary (current cycle end). Do not change current plan entitlement early.
- Unknown/inactive current handle => `UNMAPPED`, preserve observed handle, null planId, no guessed entitlement.
- Successful sync clears stale sync-error fields. Write changes idempotently using Prisma; no raw SQL.

## Work Items

- [x] Adopt accepted database/Shared revisions and regenerate Prisma.
- [x] Extend Shopify provider response types/query with price/usage/pendingUpdate.
- [x] Implement deterministic item classification/mapping.
- [x] Persist typed Subscription/BillingPeriod projection transactionally as appropriate.
- [x] Add focused tests for null contract, Partner failure, flat+tiered item order permutations, unknown handle, missing expected meter, pending downgrade and trial/current-cycle cases.

## Interfaces / Contracts

Shopify source contract is frozen in the parent architecture. Local output is the accepted typed `Subscription` projection.

Hosted pricing route pattern remains Shopify-owned; do not invent a Moda checkout.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-SHOPIFY-002
- ARCH-007-SHOPIFY-003
- ARCH-007-BACKGROUND-003
- ARCH-007-BACKGROUND-008
- ARCH-007-ADMIN-003

## Acceptance Criteria

- [x] Changing item order cannot change plan identification.
- [x] Partner API failure never redirects a known merchant as though no contract exists.
- [x] Unknown plan is persisted UNMAPPED/fail closed.
- [x] Paid plan requires its mapped tiered usage item.
- [x] Pending update is visible without replacing current entitlement.
- [x] No calendar-month period fallback is introduced.
- [x] Focused tests plus repository validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes

Exact Shared dependency: `@modainteract/moda-interact-shared@0.7.3`. Install/adopt that exact published version; do not use a floating range or local substitute.


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-SHOPIFY-001` branch and the mirrored parent-workspace `task/ARCH-007-SHOPIFY-001` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact/app/services/billing/billing.types.ts`
- `moda-interact/app/services/billing/providers/shopify-billing.provider.ts`
- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/tests/unit/services/billing.service.test.ts`
- `moda-interact/tests/unit/services/shopify-billing.provider.test.ts`
- `moda-interact/app/routes/app.billing.callback.tsx`
- `moda-interact/app/routes/app._index.jsx`
- `moda-interact/app/routes/app.usage.jsx`
- `moda-interact/app/components/dashboard/UsageOverview.jsx`
- `moda-interact/app/components/dashboard/UsageEvents.jsx`
- `moda-interact/tests/unit/routes/billing-callback.test.ts`
- `moda-interact/tests/unit/billing-period-compatibility.test.ts`

### Work Completed

- Adopted exact `@modainteract/moda-interact-shared@0.7.3` in manifest, lockfile, and installed dependency.
- Expanded the Shopify Partner API 2026-07 query and typed response for flat-rate prices, tiered prices, usage, current cycle, and pending updates.
- Identified the current plan only from exactly one active flat-rate item, independent of item order.
- Preserved provider failures as thrown errors and represented null contracts as `NO_CONTRACT` without creating a Free plan.
- Added fail-closed `UNMAPPED` and paid-meter `SYNC_ERROR` projections while preserving the observed plan handle.
- Added pending-plan mapping and transactional `BillingPeriod` upsert/linking without changing current entitlement early.
- Added deterministic `lastSyncErrorCode`/`lastSyncErrorAt` handling and stale-error clearing.
- Added focused provider and service coverage for null contracts, Partner failures, item ordering, ambiguous plans, pending downgrade observation, unknown plans, and missing usage meters.
- Attempt 3 changed the four reviewed merchant historical-period consumers from removed `PAID` status checks to accepted `CLOSED` semantics while retaining `OPEN` current-period semantics.
- Attempt 3 gates callback success on a verified mapped current or pending plan projection; `NO_CONTRACT`, `UNMAPPED`, `SYNC_ERROR`, mismatches and incomplete mappings redirect inactive.
- Added valid paid-meter projection coverage asserting mapped plan, `TRIALING`, exact billing-period link, observed handle and stale-error clearing.
- Added callback route regression coverage and a bounded four-consumer `CLOSED` compatibility source-contract test.

### Validation Results

- `./node_modules/.bin/vitest run tests/unit/billing-period-compatibility.test.ts tests/unit/routes/billing-callback.test.ts tests/unit/services/billing.service.test.ts tests/unit/services/shopify-billing.provider.test.ts` — passed, 29 tests.
- Focused ESLint for all changed source/tests — passed; TypeScript parser compatibility warning only.
- `npm run prisma:validate` — passed.
- `npm run typecheck` — repository baseline remains failing on the same unrelated JSX/type/module diagnostics; the task-local callback enum diagnostic was corrected and no callback error remains.
- `npm run build` — passed with existing package/build warnings.
- `npm test` — 165 passed, 1 skipped.
- `npm ls @modainteract/moda-interact-shared --depth=0` — confirmed `0.7.3`.
- `git diff --check` — passed.
- `npm ls @modainteract/moda-interact-shared --depth=0` — confirmed `0.7.3`.

### Deviations

- Full repository typecheck remains blocked by unrelated pre-existing JavaScript route/module diagnostics; focused tests, lint, Prisma validation, build and projection checks pass.

### Assumptions

- Provider usage snapshots remain provider observations because the accepted Subscription projection has no usage-snapshot column; usage events remain owned by downstream billing workers.

### Unresolved Issues

- None within SHOPIFY-001 scope.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted

### Review Notes

SHOPIFY-001 Attempt 3 is architect-accepted Complete.

The three-attempt review sequence is closed.

Attempt 1 established the Shopify Partner API subscription-classification
direction but implemented against the stale pre-ARCH-007 database contract.

Attempt 2 adopted the architect-accepted DATABASE-003 schema and implemented
the canonical typed current/pending subscription projection, including exact
Shopify BillingPeriod persistence, but retained legacy `PAID` BillingPeriod
consumers and permissive billing-callback success handling.

Attempt 3 closes those remaining defects.

Direct architect review confirms:

- all four reviewed merchant historical BillingPeriod consumers now use
  `CLOSED` rather than the removed `PAID` status;
- current billing periods continue to use `OPEN`;
- billing callback success requires projection status `ACTIVE` or `TRIALING`;
- a current-plan callback succeeds only when
  `observedShopifyPlanHandle === requestedPlanHandle` and `planId` is non-null;
- a pending-plan callback succeeds only when
  `pendingShopifyPlanHandle === requestedPlanHandle`, `pendingPlanId` is
  non-null, and `pendingEffectiveAt` is non-null;
- `NO_CONTRACT`, `UNMAPPED`, `SYNC_ERROR`, mismatched handles and unmapped
  current/pending plans cannot produce `billing=success`;
- the URL `plan_handle` remains an untrusted hint that must be verified against
  the Partner-derived durable projection;
- the valid `PAID_METERED` regression proves mapped plan persistence, exact
  BillingPeriod linkage, observed Shopify handle preservation and stale
  sync-error clearing;
- callback regressions cover verified current plan, verified pending plan,
  fail-closed projection states, mismatches, null mappings, untrusted requested
  handles and missing `plan_handle`;
- the BillingPeriod compatibility regression checks all four known merchant
  consumers and prohibits the removed `PAID` runtime criterion.

The previously accepted Attempt-2 projection remains intact:

- exact architect-accepted DATABASE-003 schema;
- exact `@modainteract/moda-interact-shared@0.7.3`;
- typed BillingPlan/Subscription/BillingPeriod fields and enums;
- current FlatRate and Tiered meter classification independent of item order;
- exact Shopify current billing-cycle persistence;
- no calendar-month fallback;
- pending plan state stored separately from current entitlement;
- unknown/inactive plan mapping fails closed;
- missing paid usage meter becomes `SYNC_ERROR`;
- null Shopify contract becomes `NO_CONTRACT`;
- successful provider observations clear stale synchronization errors.

### Validation Reviewed

Attempt 3 reported:

- focused suite: 29 passed;
- full suite: 165 passed, 1 skipped;
- Prisma validation: passed;
- focused ESLint: passed;
- build: passed;
- exact Shared `0.7.3` dependency verification: passed;
- `git diff --check`: passed;
- repository typecheck retained the same unrelated existing JSX/module baseline
  diagnostics.

The unchanged typecheck baseline is not a SHOPIFY-001 acceptance blocker.

### Architecture Conformance

Conformant.

Shopify now acts as the verified commercial-subscription projection boundary.
Shopify Partner state is authoritative for observed current and pending
commercial state; Moda persists that state using the typed DATABASE-003 model
and fails closed when provider state cannot be safely mapped.

### Follow-up

ARCH-007-SHOPIFY-002 may now begin.

SHOPIFY-003 remains Pending until SHOPIFY-002 is architect-accepted Complete.

BACKGROUND-003 remains Pending until BACKGROUND-002 is also architect-accepted
Complete.

Do not start later dependent tasks early.
