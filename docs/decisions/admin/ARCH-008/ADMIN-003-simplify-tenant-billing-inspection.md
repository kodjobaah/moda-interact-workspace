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
status: complete
priority: 60
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-008-ADMIN-002
enables:
  - ARCH-008-SYSTEM-TEST-001
created: 2026-09-09
updated: 2026-09-10
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

- [x] Tenant top-level navigation remains unchanged.
- [x] Billing defaults to Overview and has four deep-linkable sub-tabs.
- [x] Overview contains only concise business/health information.
- [x] Usage groups entitlement counters and hides advanced limit internals behind disclosure.
- [x] Empty billing override no longer consumes a full panel.
- [x] Shopify provider state/reconciliation is isolated to Shopify subview.
- [x] Activity contains compact pack + App Event history with drawers.
- [x] Low-level App Event diagnostics are no longer primary table columns.
- [x] All detail reads are server-side and tenant-scoped.
- [x] ADMIN-002 drawer primitives are reused.
- [x] No billing calculation/mutation/provider architecture changes.

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

Ready for Review

### Files Changed

- `src/app/(protected)/page.tsx`
- `src/components/admin/billing-drawers.tsx`
- `src/components/admin/tenant-billing.tsx`
- `src/components/admin/tenant-detail-panel.tsx`
- `src/components/admin/tenant-table.tsx`
- `src/i18n/locales/en.json`
- `src/i18n/required-keys.ts`
- `src/lib/admin/billing.ts`
- `tests/security/admin-billing-visibility.test.mjs`
- `tests/security/admin-tenant-billing-progressive-disclosure.test.mjs`

### Work Completed

- Restored the canonical task-definition sections after the prior handoff had overwritten them with completion notes.
- Completed Attempt 3 corrections for pending plan timing and `UNMAPPED` attention-state visibility in Overview.
- Exposed override hard limit, reason, state, and expiry metadata in Usage -> Advanced limits for active and expired records.
- Rendered business-level Moda and Shopify quantities when discrepancy data exists while retaining the exact unavailable message when it does not.
- Added focused regressions for all requested correction behavior and catalogue keys.
- Confirmed the earlier ADMIN-002 dependency-base blocker was resolved before implementation; shared drawer primitives are present on the synchronized mainline.

### Validation Results

- Focused correction suite: 24 passed, 0 failed.
- Full `npm test`: 145 passed, 0 failed, 0 skipped after the production build generated `.next/BUILD_ID`.
- `npx tsc --noEmit`: passed.
- `npm run lint`: passed with 2 pre-existing `queue-monitor.tsx` hook warnings.
- `npm run build`: passed; existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings remain.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.

### Git / VCS

Task branch: `task/ARCH-008-ADMIN-003`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-008-ADMIN-003`
  parent branch: `task/ARCH-008-ADMIN-003`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-008-ADMIN-003`
  implementation branch: `task/ARCH-008-ADMIN-003`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-admin`
  commit: `87664de`
  remote branch: `origin/task/ARCH-008-ADMIN-003`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/admin/ARCH-008/ADMIN-003-simplify-tenant-billing-inspection.md`
  commit: `80e0890`
  remote branch: `origin/task/ARCH-008-ADMIN-003`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Deviations

The prior Attempt 2 handoff had replaced canonical task-definition sections and left an obsolete blocked Completion Report; Attempt 3 restores both structures. No source, schema, or provider architecture deviation was introduced.

### Assumptions

The tracked `database` submodule is initialized in the implementation worktree for Prisma generation and validation; no schema or submodule pointer changes are part of this task.

### Unresolved Issues

None.

### Architectural Concerns

None introduced.


## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 closes the complete Attempt 2 Changes Requested contract and conforms to ARCH-008.

Verified corrections:

1. Overview now renders the pending plan effective date through `subscription.pendingEffectiveAt` and surfaces both `SYNC_ERROR` and `UNMAPPED` as concise attention warnings near the top.
2. Usage -> Advanced limits now preserves override hard limit, reason, state and expiry metadata whenever an override record exists, including EXPIRED historical overrides, without reintroducing a large standalone override panel.
3. Shopify now renders business-level Moda and Shopify quantities when persisted discrepancy data exists, while retaining the exact short unavailable message when the discrepancy projection is null.
4. The canonical task-definition sections and actual `## Completion Report` are restored. The Completion Report records the resolved ADMIN-002 dependency-base condition, dedicated mirrored task worktrees, synchronization evidence, implementation commit, validation results, deviations, and no unresolved issues.
5. The required production build is now reported as completed successfully.

The small duplicated restored preflight items 4/5 were documentation-only and are deduplicated by this architect acceptance overlay; no implementation rework is required.

The previously conformant ADMIN-003 structure remains intact:

- top-level `Administration | Recovery Logs | Billing` navigation is unchanged;
- Billing uses exactly `billingView=overview|usage|shopify|activity`;
- missing/invalid Billing view defaults to Overview;
- billing-only URL/detail state is cleared when changing tenant or top-level navigation;
- the existing bounded tenant billing summary may load for Billing views, while App Event and recovery-pack activity pages are loaded only for Activity;
- Activity uses independent `packPage` and `billingPage` pagination with page size 10;
- selected purchase/event detail reads pass the selected tenant `shopId` at the Prisma query boundary;
- accepted ADMIN-002 recovery-pack and App Event drawer primitives are reused and return correctly to the tenant route;
- primary Activity tables remain compact and low-level diagnostics remain in drawers;
- `REPORTED` remains `Submitted to Shopify`;
- Overview does not expose raw provider/App Event diagnostics;
- Usage keeps advanced limits behind accessible `<details>`;
- no billing mutation, entitlement calculation, schema migration, provider network call, or competing drawer architecture was introduced;
- `ARCH-008-SYSTEM-TEST-001` was not executed during implementation.

### Validation Reviewed

Agent-reported Attempt 3 validation:

- focused correction suite: 24 passed;
- full Admin tests: 145 passed;
- TypeScript: passed;
- lint: passed with two pre-existing `queue-monitor.tsx` warnings;
- Prisma validation: passed;
- `git diff --check`: passed;
- production build: passed, with the existing BullMQ dynamic-dependency / optional `@valkey/valkey-glide` warnings.

The supplied review archive does not contain `node_modules`, so validation commands were not independently rerun in the architect container. The changed source/tests and published Git state were inspected directly.

Published verification:

- implementation task branch tip: `87664de57711f202f6658d87ffafc82a157fd206`;
- Attempt 3 commit directly follows Attempt 2 `aa11e5a06cf89736a85fe5f243c947ebc13598ea`;
- cumulative Admin task branch is two commits ahead of Admin `main`, zero behind;
- cumulative changes remain limited to the ten declared ADMIN-003 source/test files;
- parent review handoff commit: `80e0890c91715279236825960fc89e9dedd8804c`;
- final parent report correction / branch tip: `4ee567a0d936ddec53436e81566e97c336a01c3a`.

### Architecture Conformance

Accepted.

The ARCH-008 implementation dependency set is now complete and architect-accepted.

### Follow-up

`ARCH-008-SYSTEM-TEST-001` is now Ready because every dependency in its authoritative YAML is Complete.

This is a terminal/manual-gated system-test task. Do NOT execute it automatically. The developer may manually exercise the integrated implementation first and must explicitly invoke `ARCH-008-SYSTEM-TEST-001` before `moda_system_test` runs.

ARCH-008 architecture status remains non-final until the required terminal system test is Complete (unless system testing is explicitly documented as not applicable).
