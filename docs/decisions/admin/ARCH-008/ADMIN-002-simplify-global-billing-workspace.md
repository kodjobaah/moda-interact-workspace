---
id: ARCH-008-ADMIN-002
architecture_id: ARCH-008
title: Simplify the global Admin Billing workspace
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 50
executor: copilot
claimed_at: 2026-09-10T00:00:00Z
attempt: 1
depends_on:
  - ARCH-008-ADMIN-001
enables:
  - ARCH-008-ADMIN-003
created: 2026-09-09
updated: 2026-09-10
---

# ARCH-008-ADMIN-002: Simplify the global Admin Billing workspace

## Architecture

Canonical: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

## Objective

Replace the current single long global Billing page with five URL-backed views and right-side detail/edit drawers so a new platform operator sees billing business state first and operational detail only on demand.

## Current inspected baseline

The supplied snapshot has:

- `src/app/(protected)/billing/page.tsx` loading `getBillingPlans`, `getPlatformBillingPolicy`, `getBillingOverview`, and `getBillingLedger` together;
- `src/components/admin/billing-plan-catalog.tsx` rendering Register plan plus every existing plan as a full expanded `PlanForm`;
- `src/components/admin/billing-overview.tsx` rendering global cards plus the wide App Event ledger;
- `src/components/admin/billing-controls.tsx` with existing `PlatformBillingControls`;
- `src/lib/admin/query.ts` with `withParamUpdates` query helpers;
- `src/components/admin/recovery-drawer.tsx` / related code as the canonical URL-backed right-side drawer interaction pattern.

The task must simplify presentation without changing billing economics/mutations.

## Required preflight

1. Work only in the launcher-resolved ADMIN-002 task worktree.
2. Confirm ADMIN-001 is Complete and its i18n/read helpers are present.
3. Inspect current implementations of the baseline files above.
4. If the global billing route was materially redesigned after the supplied snapshot, map the requirements below onto the current equivalent components. Do not create a duplicate `/billing` route.
5. Confirm all existing plan mutation functions and controls remain protected server actions; do not move them to browser-only logic.

## Required URL contract

Use the existing `/billing` route and query parameter:

```text
view=overview|plans|packs|events|controls
```

Rules:

- missing/invalid `view` -> `overview`;
- tab links are server-rendered `<Link>` navigation, not client-only hidden tabs;
- preserve only query parameters relevant to the selected view;
- selecting a different top-level tab clears drawer-selection params and unrelated page/filter params;
- browser back/forward and copied URL must reproduce the selected view.

Expected view-specific query params:

```text
plans:   planId=<id> OR drawer=register-plan
packs:   packPage=<n>, packStatus=<status>, purchaseId=<id>
events:  eventPage=<n>, state=<state>, shopId=<id>, from=<date>, to=<date>, eventId=<id>
controls: no new required params
```

Exact names may be adjusted to avoid collision with existing route params, but keep one canonical name per concept and test deep-link behavior.

## Required component structure

Prefer the following decomposition unless current code has an equivalent reusable component already:

```text
BillingPage
├── BillingTabs
├── BillingOverviewView
├── BillingPlansView
├── BillingRecoveryPacksView
├── BillingAppEventsView
├── BillingControlsView
├── AdminDetailDrawer              (shared shell)
├── BillingPlanDrawer
├── BillingEventDrawer
└── RecoveryCreditPurchaseDrawer
```

`AdminDetailDrawer` must follow the existing `RecoveryDrawer` interaction style:

- full-screen/link overlay closes drawer;
- right-side `<aside>`;
- close `<Link>` removes selection param while preserving active tab/filter/page state;
- server-rendered; do not add a new drawer package.

Drawer/detail components created here must be reusable by ADMIN-003 where the same safe detail is shown.

## Data-loading rule — mandatory

Do **not** continue to `Promise.all` every plans/policy/overview/ledger dataset on every `/billing` request.

Load by selected view:

```text
overview -> getBillingOverview only (plus minimal common tab metadata if already available without extra query)
plans    -> getBillingPlans (+ selected plan detail only if drawer open)
packs    -> getRecoveryCreditPurchases (+ selected purchase detail only if drawer open)
events   -> getBillingLedger (+ selected ledger item only if drawer open)
controls -> getPlatformBillingPolicy only
```

If an existing function internally returns a small amount of unavoidable common data, reuse it. Do not introduce duplicate database round-trips merely to satisfy the pseudocode mechanically.

## View requirements

### A. Overview — default

Purpose: answer “what is billing state across the platform?” quickly.

Must:

- render **no full App Event ledger**;
- render **no plan forms**;
- render **no PlatformBillingControls form**;
- show at most six primary cards/summary items before any secondary text.

Use existing `BillingOverview` data. Preferred primary items:

1. Free tenants
2. Paid tenants
3. Unmapped tenants
4. Subscription sync errors
5. paid recovery usage submitted this period / existing paid-usage aggregate
6. App Events needing attention

If the exact existing overview shape uses slightly different names, map to the closest existing business signal; do not add a new billing calculation solely for the card count.

Do not render one primary card for every internal report-state enum. Internal state breakdown can be secondary compact text if still useful.

### B. Plans

Purpose: browse/select a plan, then intentionally open edit detail.

Replace the current “all forms expanded” layout with compact cards or a compact table. Each plan row/card must show only primary fields:

- display name;
- plan kind/tier;
- active/inactive;
- Shopify plan handle;
- primary usage meter handle;
- included recovery allowance;
- pack enabled + pack credits summary where present.

Required actions:

```text
Register plan -> opens right-side register drawer containing existing PlanForm/create behavior
Edit          -> opens right-side plan drawer containing existing PlanForm/update behavior
Activate/deactivate -> preserve existing action and safety rules; may remain row action or move into edit drawer
```

Do not render full editable forms for every plan at once.

Preserve all existing mutation invariants, including immutable identifiers/required reason/audit behavior where already implemented.

If a helper is needed to read one plan by id, add it in the existing Admin billing-plan data module using the same authorization pattern. Do not fetch plan detail from browser code.

### C. Recovery packs

Purpose: see merchant pack lifecycle independently from App Event transport detail.

Use ADMIN-001 bounded read helper.

Default page size: 20; hard max remains server-side.

Compact list columns:

- Shop
- Status (using exact ARCH-008 labels)
- Credits
- Created
- Activated
- Details action

Optional status filter uses durable allowlisted statuses only.

Click/view details opens reusable `RecoveryCreditPurchaseDrawer` showing safe detail:

- Purchase ID
- Shop
- status
- credits snapshot
- created/activated timestamps
- plan handle snapshot
- pack/event handle snapshot
- linked UsageEvent id/metric/quantity
- linked event state using `Submitted to Shopify` terminology
- Submitted at
- attempt count / last attempt
- provider error code / bounded provider response summary
- async receipt explanation + Dev Dashboard guidance when appropriate

Do not add a provider “confirm now” button in this task.

### D. App Events

Purpose: inspect operational usage-event activity without exposing every diagnostic column by default.

Preserve existing ledger filters and pagination behavior. Table primary columns must be limited to:

- Shop
- Metric
- Quantity
- State
- Occurred at
- Details action

`REPORTED` displays `Submitted to Shopify`.

Move these low-level fields out of the primary table into `BillingEventDrawer`:

- report attempt count
- last report attempt
- Submitted at (`reportedAt`)
- provider error code
- provider response summary
- Shopify event handle
- durable event id / other safe identifiers already available

Drawer must reuse ADMIN-001 `getBillingLedgerItem` and never perform a provider network call.

### E. Controls

Render the existing `PlatformBillingControls` only. Do not redesign policy semantics or mutations.

If the component contains a “back to catalogue” link that becomes misleading after tabs, update navigation so it returns to `?view=overview` or the appropriate tab without changing the action logic.

## Styling / UX constraints

- Reuse existing Admin typography/card/border/spacing conventions; do not introduce a design-system dependency.
- Current active tab must be visually distinguishable and accessible (`aria-current` where appropriate).
- Drawers need accessible heading and close label.
- Do not hide important validation errors inside a closed drawer after a failed mutation; preserve existing server-action error presentation or reopen the relevant drawer through URL state if the current pattern supports it.
- On normal desktop width, the page should no longer require scrolling through all plan forms merely to reach controls or events.

## MUST NOT

- No billing business-logic changes.
- No database migration.
- No Shopify/provider API calls from Admin UI.
- No new client-state/router/drawer library.
- No duplicate `/billing` route.
- No removal of existing authorization/audit requirements.
- No raw secret-bearing provider payloads.
- No opportunistic redesign of Tenant Directory Billing; that is ADMIN-003.

## Required tests

Add focused `tests/security/admin-billing-progressive-disclosure.test.mjs` (or repository-consistent equivalent) proving at minimum by source/runtime-safe test approach already used in this repo:

1. allowed global views are exactly Overview/Plans/Recovery packs/App Events/Controls;
2. missing/invalid view defaults to Overview;
3. Overview does not render plan forms, ledger table or policy control form;
4. Plans no longer renders every plan as an always-expanded editable form;
5. pack/event detail read paths remain admin-protected;
6. App Events primary table does not expose provider-response diagnostic columns;
7. drawer close/detail links preserve selected tab and relevant filters;
8. all new visible strings use translation keys, not hard-coded English in components;
9. existing plan mutation security tests still pass.

If current test style uses static/source contract tests rather than DOM rendering, follow the established approach; do not add a heavy UI test framework solely for this task.

## Acceptance Criteria

- [ ] `/billing` defaults to Overview.
- [ ] Five required URL-backed tabs work and are deep-linkable.
- [ ] Data is loaded only for selected view plus selected detail.
- [ ] Overview shows business summary without ledger/forms/controls overload.
- [ ] Plans are compact and register/edit happens in drawers.
- [ ] Recovery packs have their own compact lifecycle view + drawer.
- [ ] App Events has a compact primary table + diagnostic drawer.
- [ ] Controls contains existing policy controls only.
- [ ] `REPORTED` is `Submitted to Shopify` everywhere in this surface.
- [ ] Existing billing mutations/authorization/audit semantics are unchanged.
- [ ] Shared drawer shell/detail components are reusable by ADMIN-003.

## Validation — run from `moda-interact-admin`

Focused first:

```bash
node --test \
  tests/security/admin-billing-progressive-disclosure.test.mjs \
  tests/security/admin-billing-visibility.test.mjs \
  tests/security/admin-billing-plan.test.mjs \
  tests/security/admin-billing-controls.test.mjs \
  tests/security/admin-internationalization.test.mjs
```

Then:

```bash
npm test
npx tsc --noEmit
npm run lint
npm run build
npm run prisma:validate
git diff --check
```

## Stop / return rule

After successful validation, complete Completion Report, set task `review`, return to `moda_architect`, and STOP. Do not begin ADMIN-003.

## Completion Report

### Status

In Progress

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
