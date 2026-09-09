---
id: ARCH-008-ADMIN-003
architecture_id: ARCH-008
title: Simplify Tenant Directory billing inspection
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-008-ADMIN-002
enables:
  - ARCH-008-SYSTEM-TEST-001
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-008-ADMIN-003: Simplify Tenant Directory billing inspection

## Architecture

Canonical: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

## Objective

Replace the Tenant Directory Billing tab's single stacked diagnostic surface with four tenant-scoped URL-backed sub-tabs so support operators see plan/health first and open usage/provider/activity detail only when needed.

## Current inspected baseline

The supplied snapshot currently renders all of the following together in `src/components/admin/tenant-billing.tsx`:

- subscription and billing period;
- entitlement usage and limits;
- billing policy override;
- Shopify reconciliation;
- a wide App Event ledger.

`src/app/(protected)/page.tsx` selects the top-level tenant tab and fetches tenant billing, while `src/components/admin/tenant-detail-panel.tsx` owns `Administration | Recovery Logs | Billing` navigation.

That top-level navigation stays unchanged.

## Required preflight

1. Work in launcher-resolved ADMIN-003 task worktree after synchronisation.
2. Confirm ADMIN-002 is Complete and reusable Admin billing drawer/tab primitives exist.
3. Confirm Tenant Billing current equivalent of:
   - `src/app/(protected)/page.tsx`
   - `src/components/admin/tenant-detail-panel.tsx`
   - `src/components/admin/tenant-billing.tsx`
   - `src/lib/admin/billing.ts`
4. Confirm tenant detail reads can pass the selected `shopId` into ADMIN-001 detail helpers so another shop's event/purchase cannot be opened by changing only the detail id.
5. If ADMIN-002 did not produce a reusable drawer shell/detail component as accepted, STOP and return dependency mismatch rather than creating a competing drawer mechanism.

## Required URL contract

Keep existing top-level tenant `tab=billing` mechanism.

Inside Billing use:

```text
billingView=overview|usage|shopify|activity
```

Rules:

- missing/invalid `billingView` -> `overview`;
- switching tenant top-level tab preserves existing tenant selection but clears billing-only drawer/page params;
- switching billing sub-tab clears detail params irrelevant to destination;
- browser back/forward/deep links work;
- use `<Link>` + existing `withParamUpdates` helper/pattern, not client-only tab state.

Activity detail params should reuse ADMIN-002 canonical names where possible:

```text
purchaseId=<id>
eventId=<id>
billingPage=<n>
packPage=<n>
```

## Required sub-tabs

Exactly:

```text
Overview | Usage | Shopify | Activity
```

Do not add separate tabs for policy overrides or raw diagnostics.

## Data-loading / tenant-scope rule

Continue to use protected server-side reads. Do not fetch billing data directly from browser code.

Where practical, avoid loading large activity datasets when not on Activity. It is acceptable to keep one existing bounded tenant billing summary query if splitting it would create duplicate complex entitlement calculations, but the App Event ledger and pack-activity pages must not be loaded on every tenant billing subview merely to remain hidden.

Any selected `purchaseId` / `eventId` detail must be read with the current tenant `shopId` at the database query boundary.

## Sub-view requirements

### A. Overview — default

Purpose: answer the new operator's first questions.

Render a compact summary containing:

- current effective plan;
- subscription status;
- concise billing-health state;
- current billing-period start/end;
- remaining entitlement (or clear unavailable state);
- pending plan name/effective date when present;
- last synced timestamp or sync warning;
- billing policy status as one concise line.

Billing-policy rule:

```text
no active override -> show one line: Default policy
active override    -> show visible warning: Billing policy override active
expired historical override -> do not show a large default card; expose in Usage -> Advanced limits/details only
```

Do **not** render the App Event ledger or provider diagnostic fields on Overview.

If subscription status is a sync error or other attention state, surface a concise warning near the top; do not force the operator to infer it by scanning raw fields.

### B. Usage

Group existing entitlement values semantically.

Primary usage block:

- Base allowance
- Allowance adjustments
- Committed
- Reserved
- Remaining
- Reported/submitted paid recovery usage using current semantic label where applicable
- Automated messages this period
- Effective outbound hard cap

Place low-frequency limit internals behind an accessible `<details>`/equivalent disclosure labelled **Advanced limits**:

- plan/default outbound hard limit;
- platform absolute hard cap;
- override hard limit;
- override reason/effective/expiry metadata when present and safe.

Do not add/edit policy controls here. Tenant control mutations remain under the existing Administration surface.

### C. Shopify

Purpose: provider projection/reconciliation only.

Show concise fields from existing `TenantBilling` provider data:

- observed Shopify plan;
- pending Shopify plan;
- pending effective date;
- last provider sync;
- last sync error/status;
- current reconciliation/discrepancy summary when available.

If the current read model has no persisted Shopify usage snapshot (`discrepancy == null` in the inspected baseline), render only the short exact message:

```text
Shopify usage comparison is not available for this tenant.
```

Do not render a large empty reconciliation card and do not invent a live Partner request from Admin to fill it.

When discrepancy data exists after accepted ARCH-008 background reconciliation, display business-level local/provider quantities first. Raw provider response/error details remain in the corresponding Activity drawer.

### D. Activity

Purpose: operational history on demand.

Show two compact sections:

#### Recovery packs

Use ADMIN-001 tenant-scoped pack list, default page size 10.

Columns:

- Created
- Status
- Credits
- Activated
- Details

Empty state is one concise sentence, not a large card.

Details opens the reusable `RecoveryCreditPurchaseDrawer` from ADMIN-002, with tenant-scoped read.

#### App Events

Preserve tenant event pagination, default page size 10.

Primary columns only:

- Occurred at
- Metric
- Quantity
- State
- Details

Do not keep provider error code/response/attempt/handle as wide primary columns. Move them into the reusable `BillingEventDrawer` from ADMIN-002.

`REPORTED` displays **Submitted to Shopify** and `reportedAt` displays **Submitted at**.

If both subsections paginate independently, use `packPage` and `billingPage` so changing one does not reset the other unnecessarily.

## Required component direction

Prefer:

```text
TenantBilling
├── TenantBillingTabs
├── TenantBillingOverviewView
├── TenantBillingUsageView
├── TenantBillingShopifyView
└── TenantBillingActivityView
      ├── Recovery packs compact list -> shared RecoveryCreditPurchaseDrawer
      └── App Events compact list     -> shared BillingEventDrawer
```

Reuse the shared drawer shell/detail components accepted in ADMIN-002. Do not fork copies merely to change tenant layout; pass tenant-scoping props/return query as needed.

## Accessibility / progressive disclosure

- Active sub-tab has accessible current-state indication.
- `<details>` advanced limits has clear summary text.
- Drawers have heading, close label and keyboard-reachable close link.
- Status warnings use text as well as colour.
- “Unavailable” is displayed intentionally instead of an empty value when source data does not exist.

## MUST NOT

- Do not change the top-level Tenant Directory `Administration | Recovery Logs | Billing` information architecture.
- Do not change entitlement calculations.
- Do not add tenant billing mutations here.
- Do not call Shopify/Partner APIs from the browser/Admin request solely for reconciliation display.
- Do not add another drawer implementation if ADMIN-002's accepted primitive exists.
- Do not render another shop's detail by id without tenant-scoped query.
- Do not add schema/migrations.
- Do not expose secrets/raw provider payloads.

## Required tests

Add focused `tests/security/admin-tenant-billing-progressive-disclosure.test.mjs` (or repository-consistent equivalent) proving:

1. required sub-tabs are exactly Overview/Usage/Shopify/Activity;
2. missing/invalid billingView defaults Overview;
3. Overview does not render App Event ledger/provider diagnostics;
4. no-override state does not render the previous full empty override card and shows `Default policy` concisely;
5. advanced limits are behind disclosure;
6. Shopify unavailable reconciliation uses the short i18n message and makes no new provider client call;
7. Activity uses compact event columns and pack list;
8. event/purchase detail query is tenant-scoped and cannot open another tenant's record;
9. shared ADMIN-002 drawers are reused rather than copied;
10. existing tenant billing security/visibility tests continue to pass.

## Acceptance Criteria

- [ ] Tenant top-level navigation remains unchanged.
- [ ] Billing defaults to Overview and has four deep-linkable sub-tabs.
- [ ] Overview contains only concise business/health information.
- [ ] Usage groups entitlement counters and hides advanced limit internals behind disclosure.
- [ ] Empty billing override no longer consumes a full panel.
- [ ] Shopify provider state/reconciliation is isolated to Shopify subview.
- [ ] Activity contains compact pack + App Event history with drawers.
- [ ] Low-level App Event diagnostics are no longer primary table columns.
- [ ] All detail reads are server-side and tenant-scoped.
- [ ] ADMIN-002 drawer primitives are reused.
- [ ] No billing calculation/mutation/provider architecture changes.

## Validation — run from `moda-interact-admin`

Focused first:

```bash
node --test \
  tests/security/admin-tenant-billing-progressive-disclosure.test.mjs \
  tests/security/admin-billing-progressive-disclosure.test.mjs \
  tests/security/admin-billing-visibility.test.mjs \
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

After successful validation, complete Completion Report, set task `review`, return to `moda_architect`, and STOP. Do not execute SYSTEM-TEST-001 automatically.

## Completion Report

### Status

Not Started

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
