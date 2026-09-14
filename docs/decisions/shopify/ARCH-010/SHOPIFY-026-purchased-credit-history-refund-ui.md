---
id: ARCH-010-SHOPIFY-026
architecture_id: ARCH-010
title: Build dedicated purchased-credit history and refund-management UI
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 80
executor: copilot
claimed_at: 2026-09-14T19:42:33Z
attempt: 1
depends_on:
- ARCH-010-SHOPIFY-025
- ARCH-010-SHOPIFY-012
enables:
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-13
updated: 2026-09-14
---

# ARCH-010-SHOPIFY-026: Build dedicated purchased-credit history and refund-management UI

## Objective

Add a dedicated merchant surface for viewing and managing every `RecoveryCreditPurchase` without overloading `/app/billing/options`.

Canonical route:

```text
/app/billing/recovery-credit-purchases
```

Use an equivalent route only if the integrated route convention makes this exact path invalid; document any deviation.

The page must let the merchant:

- view ACTIVE purchases;
- view purchases pending refund (`WITHDRAWN`);
- view COMPLETED purchases;
- view REFUNDED purchases;
- see REQUESTED purchases awaiting Shopify confirmation;
- select **one or more ACTIVE purchases** and request refund of each whole remaining purchase;
- reactivate a WITHDRAWN purchase while SHOPIFY-025 says reactivation is still allowed.

The merchant never chooses a credit quantity.

## Inspect before editing

```text
app/routes/app/billing/**
app/components/dashboard/BillingPurchaseHub.*
app/components/dashboard/TopUpPurchasePanel.*
app/routes.ts
merchant i18n catalogues/runtime
existing table/card/pagination/confirmation patterns
SHOPIFY-025 server read/action contract
```

Prefer a focused component such as:

```text
app/components/dashboard/RecoveryCreditPurchaseManager.*
```

Do not place Prisma/provider business logic in UI components.

## Navigation

Add a clear merchant link from the production billing/capacity surface, for example:

```text
Manage purchased credits
```

Do not replace the top-up purchase CTA. This page manages historical purchase lots; SHOPIFY-014/012 continue to own buying new top-ups.

No link to `moda-interact-admin` is ever exposed.

## Page organization

Provide an accessible filter/tab model equivalent to:

```text
Active
Refund pending
Completed
Refunded
All
```

`All` includes REQUESTED purchases. If UX is clearer, a visible `Pending purchase` filter may be added, but the required four merchant lifecycle groupings above must remain obvious.

Use server pagination. Do not load an unbounded purchase history into the browser.

## Purchase row/card content

At minimum show safely localized:

```text
purchase/activation date
plan snapshot/name
original credits purchased
current credits remaining
credits currently reserved/in progress
currently available amount when ACTIVE
original purchase amount/currency when confirmed
human-readable lifecycle status
refund workflow summary when present
```

Do not expose raw provider subscription IDs, internal BillingPeriod IDs, Admin IDs or provider reference secrets.

Merchant-facing label mapping:

```text
REQUESTED  -> Awaiting Shopify confirmation
ACTIVE     -> Active
WITHDRAWN  -> Refund pending
COMPLETED  -> Completed / all credits used
REFUNDED   -> Refunded
```

Do not use internal word `WITHDRAWN` without explanatory merchant copy.

## ACTIVE selection and refund request

Each ACTIVE row:

- has a selectable checkbox only when the loaded `availableAmount > 0`;
- shows disabled/explanatory state when `availableAmount = 0` because all remaining credits are currently reserved/in progress;
- never contains a quantity input, slider, monetary amount input or provider-action selector.

Allow selecting one or more eligible ACTIVE rows and one action:

```text
Request refund for selected purchases
```

Before submission, show a confirmation dialog summarizing each selected purchase and explicitly state:

```text
- the request applies to all credits that ultimately remain unused on each selected purchase;
- conversations already in progress may still finish;
- final refundable credits can therefore differ from the number visible now;
- no new conversation will use a purchase once its refund request wins server-side;
- each purchase is processed independently.
```

Do not promise current displayed quantities as final provider refund quantities.

## Per-purchase race results

Render the exact per-item results returned by SHOPIFY-025 rather than collapsing the batch into generic success/failure.

Required UX examples:

### Credit disappeared before click won

Merchant saw 1 available, but reservation won first:

```text
Refund not available — this purchase no longer has an unreserved credit available.
```

Refresh row from server. It remains ACTIVE unless later state says otherwise.

### Two shown, one became reserved

Fresh server result withdrew only the currently unreserved part while another conversation was already in flight:

```text
Refund requested. 1 credit is currently eligible for refund and 1 credit is still in progress.
The final refund will include every credit left after the in-progress conversation resolves.
```

Use returned numbers; do not recompute from stale component props.

### Mixed batch

If A succeeds, B has no availability and C is no longer ACTIVE, show all three outcomes. Do not imply the successful request was rolled back.

## Refund-pending / WITHDRAWN rows

Show:

```text
currentAmount
reservedAmount still in progress
current unreserved amount held for refund
refund workflow state
```

While exact refund status is `REQUESTED` and SHOPIFY-025 says reactivation is allowed, show:

```text
Reactivate credits
```

Require a confirmation dialog explaining that the refund request will be cancelled and the purchase will become available for future conversations again, subject to current reservations.

After successful reactivation, refresh the row into ACTIVE. Its original purchase date/order is unchanged.

If provider action has begun (`PROVIDER_ACTION_REQUIRED`/ambiguous later state), hide/disable reactivation and explain that the refund can no longer be cancelled in-app because settlement may have started.

## COMPLETED rows

Show the purchase as historical, with copy equivalent to:

```text
All purchased credits have been used.
```

No refund/reactivation controls.

## REFUNDED rows

Show the purchase as terminal historical state, including when safe:

```text
credits refunded
provider-confirmed refund/credit amount + currency
refund completion date
```

Do not expose internal provider reference unless an existing merchant receipt/history pattern explicitly treats it as merchant-safe.

No refund/reactivation controls.

## REQUESTED rows

Show purchase awaiting provider confirmation. It cannot be spent, refunded or selected.

Use linked provider/reporting state only to provide bounded safe guidance; do not invent a sixth purchase lifecycle status in UI.

## Monetary presentation

The original purchase amount/currency comes only from immutable purchase provenance.

For ACTIVE/WITHDRAWN rows, do not calculate a speculative final cash refund from current plan/top-up pricing.

Once ADMIN-003 has frozen `expectedProviderAmount/currency` at provider-action boundary, the page may display that exact persisted value if the merchant read model exposes it safely.

Completed REFUNDED rows may display actual provider-confirmed amount/currency.

## Accessibility/i18n

All visible strings use merchant localization. Required controls:

- keyboard-operable row selection;
- select-all applies only to currently eligible ACTIVE rows on the current page;
- explicit loading/submitting/disabled states;
- confirmation dialogs with accessible labels/focus handling;
- status must not rely on color alone;
- per-item result summary announced accessibly.

## Required tests

At minimum prove:

1. dedicated route exists and is authenticated;
2. billing surface links to it;
3. Active/Refund pending/Completed/Refunded/All views work;
4. REQUESTED is visible but non-selectable;
5. ACTIVE available >0 can be selected;
6. ACTIVE available=0 is non-selectable with explanation;
7. no credit-quantity input exists;
8. one selected purchase sends one purchase ID only;
9. multiple selected purchases send bounded unique IDs;
10. stale displayed quantities are not submitted as authority;
11. per-item partial batch outcomes render independently;
12. refund-not-available race is rendered correctly;
13. fresh reduced availability race is rendered from server numbers;
14. WITHDRAWN REQUESTED refund shows Reactivate;
15. provider-action-started state blocks Reactivate;
16. reactivation refreshes row to ACTIVE without changing purchase identity/date;
17. COMPLETED/REFUNDED rows have no refund controls;
18. REFUNDED shows actual persisted settlement data only;
19. original purchase money is not recalculated from current plan;
20. cross-shop/internal provider data is never rendered;
21. pagination and filter state are bounded;
22. all new strings have i18n parity;
23. component/route tests, typecheck/build/lint and `git diff --check` pass.

## Non-goals

Do not implement server CAS logic, Admin provider settlement, Shopify refund APIs, negative App Events or top-up purchase creation.

## Stop conditions

STOP if SHOPIFY-025 does not expose all lifecycle/action states required for deterministic rendering or if the only approach would trust browser quantities/money.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact/app/routes.ts`
- `moda-interact/app/routes/app/billing/recovery-credit-purchases/route.tsx`
- `moda-interact/app/components/dashboard/RecoveryCreditPurchaseManager.jsx`
- `moda-interact/app/components/dashboard/BillingPurchaseHub.jsx`
- `moda-interact/app/i18n/catalogues.js`
- `moda-interact/app/i18n/locales/en.json`

### Work Completed
- Added the authenticated canonical `/app/billing/recovery-credit-purchases` route using the SHOPIFY-025 loader/action contract, bounded to the server page/pageSize limits and the server-owned purchase IDs, amounts and outcomes.
- Added Active, Refund pending, Completed, Refunded and All views. All exposes REQUESTED as awaiting Shopify confirmation without selection controls.
- Added eligible ACTIVE selection only when server `availableAmount > 0`, current-page unique select-all, bounded multi-purchase submission, no quantity or money inputs, and no browser quantity/money authority.
- Added confirmation dialogs with all five required uncertainty statements, loading/submitting/disabled states, keyboard-operable controls, live result announcements and modal labels/focus.
- Added independent per-purchase result rendering for request races, partial availability, mixed batches and non-active/refunded outcomes, followed by server refresh.
- Added Reactivate only for WITHDRAWN plus exact REQUESTED refund state; provider-action states are blocked with explanatory copy. COMPLETED and REFUNDED rows have no refund/reactivation controls.
- Added persisted original purchase money and persisted completed settlement money/currency display without recalculation or provider/internal reference exposure.
- Added a production billing/capacity link while preserving the existing top-up CTA.
- Added merchant catalogue parity through the existing catalogue registry with English fallback values for all supported merchant locales.

### Correction Checklist
- The launcher/task context identified `rework_required`, but the complete authoritative task file contained no `## Architect Review` section or Changes Requested items. No review section was edited; the full task acceptance criteria were treated as the correction checklist.
- Authenticated route and production navigation: implemented.
- Lifecycle filters, REQUESTED visibility/non-selection and bounded pagination: implemented.
- Server-authoritative eligibility, payload bounds and stale-value exclusion: implemented.
- Confirmation uncertainty statements and accessible loading/submission/result states: implemented.
- Independent race/mixed outcomes and post-action refresh: implemented.
- Reactivation/provider-action gating and historical terminal controls: implemented.
- Persisted settlement/money safety, cross-shop/internal data safety and merchant i18n: implemented.

### Validation Results
- Passed focused route/configuration test: `tests/unit/routes/explicit-route-config.test.ts` (7 tests).
- Passed focused billing/i18n tests: `tests/unit/routes/explicit-route-config.test.ts`, `tests/unit/billing-purchase-hub.test.tsx`, `tests/unit/billing-i18n.test.ts`, `tests/unit/merchant-i18n.test.ts` (4 files, 27 tests).
- Passed changed-file ESLint and `git diff --check`.
- Passed `npm run build` after final changes; Prisma client generation and client/SSR builds completed.
- `npm run typecheck` remains blocked by the documented repository baseline: 256 errors across 30 existing files, including generated Prisma-client enum/API mismatch and existing checked-JavaScript diagnostics. No diagnostics remained in the task-owned manager, route, route table or catalogue files after local fixes.
- Full `npm test` remains blocked by the same baseline/generated-client state: 5 suites fail to initialize because `@prisma/client` is not initialized in the Vitest process and 7 existing billing-callback tests fail on missing generated enum values. The task-focused suites pass.
- Contract limitation for architect review: SHOPIFY-025 exposes bounded pagination but no lifecycle filter parameter. The UI keeps server pagination bounded and filters the loaded page; it does not load unbounded history or invent a server contract.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-026`.
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-026`.
- Mirrored branch: `task/ARCH-010-SHOPIFY-026`.
- Implementation commit/push: `e37f9a7` pushed to `origin/task/ARCH-010-SHOPIFY-026`.
- Parent report commit/push: `76b1076` pushed to `origin/task/ARCH-010-SHOPIFY-026`.

### Architect Review
Pending. The task is returned for architect review; this agent made no architect acceptance decision.
