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
status: review
priority: 60
executor: copilot
claimed_at: 2026-09-10T02:27:42Z
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
  commit: `PENDING` (Attempt 3 review handoff commit)
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

Changes Requested

### Review Notes

Attempt 2 establishes the intended tenant Billing progressive-disclosure structure and is correctly scoped to the Admin repository, but it is not yet acceptable.

There are four implementation/validation corrections plus one task-report correction.

#### 1. Overview omits the pending-plan effective date

The task requires Overview to show:

```text
pending plan name/effective date when present
```

The implementation shows `subscription.pendingPlan?.name`, but does not render `subscription.pendingEffectiveAt` in Overview.

Required correction:

- keep the pending plan name;
- when `pendingEffectiveAt` is present, render it in Overview using the existing `billing.pendingEffectiveAt` translation and `adminI18n.formatDateTime`;
- when absent, use the existing intentional empty/not-recorded presentation;
- add focused regression coverage.

Also preserve the requirement that attention states are visible near the top. `SYNC_ERROR` is already warned. Ensure other genuine projection-attention states represented by the existing model (at minimum `UNMAPPED`) are not silently presented as ordinary healthy state.

#### 2. Usage -> Advanced limits drops required override metadata

The task requires Advanced limits to expose, when present and safe:

```text
plan/default outbound hard limit
platform absolute hard cap
override hard limit
override reason/effective/expiry metadata
```

The current implementation shows:

- plan/default hard limit;
- platform hard cap;
- override state;
- override reason only while the override is ACTIVE.

It does not show `billing.override.outboundHardLimit`, and an expired historical override loses its reason and `expiresAt` detail even though the task explicitly says expired historical overrides belong in Usage -> Advanced limits/details.

Required correction:

- render override hard limit when an override record exists;
- render override reason when an override record exists, including EXPIRED;
- render `expiresAt` when present;
- retain `overrideState` so Active/Expired remains explicit;
- do not reintroduce a large standalone override panel;
- do not add or change mutation controls;
- add focused regressions for both ACTIVE and EXPIRED override presentation.

There is no requirement to invent an effective timestamp if the current read model does not contain one.

#### 3. Shopify discrepancy-present branch does not show business quantities

The task requires:

```text
when discrepancy data exists, display business-level local/provider quantities first
```

The current `billing.discrepancy` branch renders only the generic `billing.discrepancyDetected` text.

Required correction:

- when `billing.discrepancy` is non-null, render the existing business-level `modaQuantity` and `shopifyQuantity` (and meter handle only if useful and already safe);
- keep the exact short unavailable message when `billing.discrepancy === null`:
  `Shopify usage comparison is not available for this tenant.`
- do not add a live Partner/Shopify request;
- do not expose raw provider payload/error details here;
- add focused regression coverage for null and non-null discrepancy cases.

#### 4. Required production build validation did not complete

The task's validation contract includes:

```text
npm run build
```

Attempt 2 reports that Next.js production compilation started but the process exited `130` before completion. Exit 130 is an interrupted build, not a successful validation result.

Required correction:

- rerun `npm run build` from the canonical ADMIN-003 implementation worktree;
- it must complete successfully before the task returns to review;
- if it fails with a source/build error, fix the in-scope cause and rerun;
- if the environment interrupts it again, report the exact reproducible environment blocker rather than marking validation successful.

The archive does not contain `node_modules`, so the architect could not independently rerun the build in the review container.

#### 5. Completion Report / task document is stale and internally contradictory

The parent handoff commit changes frontmatter to `status: review` and adds implementation/validation statements near the top of the task file, but the canonical `## Completion Report` section still says:

```text
Status: In Progress
implementation blocked
required shared drawer absent
implementation commit: none
```

Those statements are obsolete after ADMIN-002 was merged and `aa11e5a` was implemented.

The handoff also overwrote canonical task-specification sections (`# title`, canonical Architecture/Objectives/preflight prose) with completion data rather than putting that data solely in the Completion Report.

Required correction:

- restore the task specification sections to their canonical task-definition content; do not use Architecture/Objectives/current-baseline sections as a substitute Completion Report;
- update the actual `## Completion Report` with Attempt 3 status, files changed, work completed, canonical worktree/synchronization evidence, implementation commit(s), validation results, deviations, unresolved issues and architecture concerns;
- explicitly record that the earlier dependency-base blocker was resolved because ADMIN-002 was merged before Attempt 2/3 implementation;
- do not alter or delete this Architect Review;
- return the same task to `status: review` after successful validation.

### Positive Findings To Preserve

The following parts conform and should not be regressed:

- top-level `Administration | Recovery Logs | Billing` navigation remains unchanged;
- Billing uses exactly `billingView=overview|usage|shopify|activity`;
- missing/invalid Billing view defaults to Overview;
- billing-only page/detail params are cleared on tenant/top-level navigation transitions;
- App Event and recovery-pack activity datasets are loaded only for Activity;
- selected event/purchase reads pass the current tenant `shopId` at the database query boundary;
- recovery-pack and App Event pagination use independent `packPage` and `billingPage`, page size 10;
- Activity primary columns are compact;
- accepted ADMIN-002 `RecoveryCreditPurchaseDrawer` and `BillingEventDrawer` primitives are reused rather than forked;
- drawers can return to the tenant route;
- `REPORTED` remains `Submitted to Shopify`;
- Overview does not render raw App Event/provider diagnostics;
- Usage uses an accessible `<details>` disclosure for advanced limits;
- no tenant billing mutation, entitlement calculation, schema migration, or provider-network architecture change was introduced;
- SYSTEM-TEST-001 was correctly not executed.

### Reviewed Files

- `src/app/(protected)/page.tsx`
- `src/components/admin/billing-drawers.tsx`
- `src/components/admin/tenant-billing.tsx`
- `src/components/admin/tenant-detail-panel.tsx`
- `src/components/admin/tenant-table.tsx`
- `src/i18n/locales/en.json`
- `src/i18n/required-keys.ts`
- `src/lib/admin/billing.ts`
- `src/lib/admin/types.ts`
- `tests/security/admin-billing-visibility.test.mjs`
- `tests/security/admin-tenant-billing-progressive-disclosure.test.mjs`
- this task's published parent handoff/report
- published implementation commit `aa11e5a`
- published parent commit `4ced8ec`

### Validation Reviewed

Agent-reported:

- focused tests: 31 passed;
- full Admin tests: 140 passed, 3 skipped;
- TypeScript: passed;
- lint: passed with two pre-existing `queue-monitor.tsx` warnings;
- Prisma validation: passed;
- `git diff --check`: passed;
- build: NOT complete — process exited 130 during Next.js production build.

Published branch verification:

- `task/ARCH-008-ADMIN-003` implementation tip is `aa11e5a06cf89736a85fe5f243c947ebc13598ea`;
- implementation branch is one commit ahead of Admin `main`, zero behind;
- implementation commit is based directly on `2d254c723a6b401b51a2c991e8c9f70a5abf13a8`;
- changed Admin files are limited to the ten declared ADMIN-003 source/test files;
- parent task branch tip is `4ced8ec7f9d7528913a7abb81d882eb9b066ce01`.

### Architecture Conformance

Changes required.

### Follow-up

Attempt 3 must remain on the SAME task and SAME mirrored `task/ARCH-008-ADMIN-003` branches.

Attempt 3 checklist:

1. add pending-plan effective date and proper attention-state warning behavior to Overview;
2. complete Advanced limits override hard-limit/reason/expiry presentation, including expired overrides;
3. render local/provider quantities when discrepancy data exists while retaining the exact unavailable message when it does not;
4. add focused regressions for all above corrections;
5. restore/update the canonical task specification + Completion Report structure;
6. rerun focused tests, full Admin tests, TypeScript, lint, Prisma validation, `git diff --check`, and a production build that completes successfully;
7. return the same task to `review` and STOP.

Do not start or execute `ARCH-008-SYSTEM-TEST-001`. It remains terminal/manual-gated.
