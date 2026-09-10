---
id: ARCH-008-ADMIN-001
architecture_id: ARCH-008
title: Establish asynchronous billing presentation and safe Admin read primitives
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor:
claimed_at:
attempt: 1
depends_on:
  - ARCH-008-BACKGROUND-002
  - ARCH-007-ADMIN-003
enables:
  - ARCH-008-ADMIN-002
created: 2026-09-09
updated: 2026-09-10
---

# ARCH-008-ADMIN-001: Establish asynchronous billing presentation and safe Admin read primitives

## Architecture

Canonical: `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`

## Objective

Give later ARCH-008 Admin UI tasks one accurate, authorization-safe billing presentation/read layer: `REPORTED` is labelled **Submitted to Shopify**, pack statuses are explicit, and bounded pack/event detail queries expose only safe diagnostics.

## Why this task does not redesign the page

This task prepares shared semantics/data. It must not perform the global or tenant layout redesign. Those are ADMIN-002 and ADMIN-003.

## Required preflight

1. Work only in the launcher-resolved ADMIN-001 implementation worktree after normal synchronisation.
2. Confirm ARCH-008-BACKGROUND-002 is Complete and the integrated schema/runtime semantics are present.
3. Confirm current Admin billing visibility implementation exists, including equivalents of:
   - `src/lib/admin/billing.ts`
   - `src/lib/admin/types.ts`
   - `src/lib/admin/billing-presentation.mjs`
   - `src/i18n/locales/en.json`
   - `src/i18n/required-keys.ts`
4. Confirm the current package still provides the expected test/lint/build/typecheck capabilities.
5. If Background introduced an architecture-approved field/state different from this task's expected durable contract, STOP and report the exact mismatch to `moda_architect`; do not paper over it in UI.

## Primary files

Expected targets:

- `moda-interact-admin/src/lib/admin/billing.ts`
- `moda-interact-admin/src/lib/admin/types.ts`
- `moda-interact-admin/src/lib/admin/billing-presentation.mjs`
- `moda-interact-admin/src/i18n/locales/en.json`
- `moda-interact-admin/src/i18n/required-keys.ts`
- focused tests under `moda-interact-admin/tests/security/`

Do not make major edits to `src/app/(protected)/billing/page.tsx` or `src/components/admin/tenant-billing.tsx` in this task.

## Required implementation

### A. Exact user-facing semantic labels

Retain raw durable enum values internally. Change presentation so:

```text
REPORTED -> Submitted to Shopify
```

Do not label it `Reported`, `Confirmed`, `Charged`, `Billed`, `Paid`, `Settled` or equivalent.

Where the durable field is `reportedAt`, UI label must be:

```text
Submitted at
```

The code key may remain backwards-compatible if renaming a key would create unnecessary churn; displayed text is normative.

Add bounded explanatory copy:

```text
Shopify has received the App Event. Billing validation is asynchronous.
```

And operational guidance:

```text
If provider usage does not reconcile, inspect App Billing Event logs in the Shopify Dev Dashboard.
```

Do not imply Moda can retrieve the exact asynchronous validation error through an API if it cannot.

### B. Recovery-credit purchase status presentation

Define/reuse one presentation mapping for durable purchase status:

```text
PENDING_BILLING  -> Awaiting Shopify confirmation
ACTIVE           -> Active
NEEDS_ATTENTION  -> Needs attention
CANCELLED        -> Cancelled
```

Do not derive ACTIVE from UsageEvent.REPORTED in Admin.

### C. Add bounded protected recovery-pack read models

In `src/lib/admin/billing.ts` (or accepted equivalent), add protected read helpers with existing `requirePlatformAdminRead()` authorization:

```text
getRecoveryCreditPurchases({ page, pageSize, shopId?, status? })
getRecoveryCreditPurchaseDetail(id, shopId?)
getBillingLedgerItem(id, shopId?)
```

Exact function names may vary only if the existing module naming convention requires it; document actual names.

#### List constraints

- default page size: 20;
- hard maximum page size: 50;
- stable newest-first ordering: `createdAt DESC`, then `id DESC`;
- optional `shopId` must be applied at database query level, not filtered in browser code;
- optional status filter must be allowlisted against durable enum values;
- return total/page metadata consistent with existing Admin pagination patterns.

#### Safe recovery-pack list/detail projection

Return only fields required by Admin operations, including where available:

- purchase `id`;
- `shopId` and safe shop name/domain summary through existing relation;
- plan display name if available;
- `shopifyPlanHandleSnapshot`;
- `shopifyEventHandleSnapshot`;
- `creditsGranted`;
- purchase `status`;
- `activatedAt`;
- `createdAt` / `updatedAt`;
- linked UsageEvent safe diagnostics:
  - id;
  - metric;
  - quantity;
  - occurredAt;
  - shopifyReportState;
  - reportAttemptCount;
  - lastReportAttemptAt;
  - reportedAt;
  - providerErrorCode;
  - bounded providerResponseSummary;
  - shopifyEventHandle.

Do **not** return access tokens, provider credentials, authorization headers or raw secret-bearing request payloads.

#### Billing ledger detail

`getBillingLedgerItem(id, shopId?)` must reuse the same safe field set already exposed by the bounded billing ledger. It must not make a provider network call.

### D. Add all ARCH-008 Admin strings now

ADMIN-002 and ADMIN-003 are deliberately serial but should not each invent semantic wording. Add the following keys to `en.json` and required-key coverage using the repository's existing i18n convention. If the exact key namespace convention differs, use equivalent names while preserving these exact English meanings:

```text
billing.tab.overview                  Overview
billing.tab.plans                     Plans
billing.tab.recoveryPacks             Recovery packs
billing.tab.appEvents                 App Events
billing.tab.controls                  Controls

billing.tenantTab.overview            Overview
billing.tenantTab.usage               Usage
billing.tenantTab.shopify             Shopify
billing.tenantTab.activity            Activity

billing.state.REPORTED                Submitted to Shopify
billing.submittedAt                   Submitted at
billing.asyncReceiptHelp              Shopify has received the App Event. Billing validation is asynchronous.
billing.devDashboardHelp              If provider usage does not reconcile, inspect App Billing Event logs in the Shopify Dev Dashboard.

billing.packStatus.PENDING_BILLING    Awaiting Shopify confirmation
billing.packStatus.ACTIVE             Active
billing.packStatus.NEEDS_ATTENTION    Needs attention
billing.packStatus.CANCELLED          Cancelled

billing.closeDetails                  Close details
billing.planDetails                   Plan details
billing.eventDetails                  App Event details
billing.recoveryPackDetails           Recovery pack details
billing.registerPlanAction            Register plan
billing.editPlanAction                Edit plan
billing.viewDetails                   View details
billing.creditsGranted                Credits
billing.activatedAt                   Activated at
billing.purchaseId                    Purchase ID
billing.usageEventId                  Usage event ID
billing.planSnapshot                  Plan handle snapshot
billing.packMeterSnapshot             Pack meter snapshot
billing.noRecoveryPacks               No recovery-credit purchases match the current filters.
billing.billingHealth                 Billing status
billing.advancedLimits                Advanced limits
billing.defaultPolicy                 Default policy
billing.overrideActiveWarning         Billing policy override active
billing.overrideExpiredNotice         An expired billing policy override is recorded.
billing.activity                      Billing activity
billing.reconciliationUnavailableShort Shopify usage comparison is not available for this tenant.
```

Do not remove existing keys used elsewhere.

### E. Tests

Update/add focused tests to prove:

- `REPORTED` renders exactly `Submitted to Shopify`;
- `reportedAt` presentation uses `Submitted at` semantics;
- all four purchase states map to exact copy above;
- required i18n keys are present;
- pack list/detail and ledger-detail reads require platform-admin authorization;
- `shopId` detail scoping cannot return another tenant's row;
- pagination is bounded to maximum 50;
- safe projections do not include secrets/provider credentials.

## Out of Scope / MUST NOT

- No major billing-page/tab/drawer layout yet.
- No Shopify provider calls from Admin.
- No billing mutation/business-logic changes.
- No Prisma schema migration.
- No entitlement calculation changes.
- No new client-side state framework.
- No exposure of secrets/raw provider payloads.

## Acceptance Criteria

- [ ] All Admin surfaces can consume one truthful `REPORTED` label: `Submitted to Shopify`.
- [ ] `reportedAt` is presented as `Submitted at`.
- [ ] Pack statuses have exact bounded user-facing labels.
- [ ] Protected bounded pack list/detail + ledger detail helpers exist.
- [ ] Tenant detail helper enforces `shopId` at query boundary.
- [ ] No provider network call is added to Admin.
- [ ] ARCH-008 tab/drawer copy is present in required i18n coverage.
- [ ] No global/tenant layout redesign is performed prematurely.

## Validation — run from `moda-interact-admin`

Run focused billing/security/i18n tests first:

```bash
node --test \
  tests/security/admin-billing-visibility.test.mjs \
  tests/security/admin-billing-plan.test.mjs \
  tests/security/admin-billing-controls.test.mjs \
  tests/security/admin-internationalization.test.mjs \
  <any-new-focused-billing-read-test.mjs>
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

If current scripts differ, use current declared equivalents and record why.

## Stop / return rule

After successful validation, complete Completion Report, set task `review`, return to `moda_architect`, and STOP. Do not begin ADMIN-002.

## Completion Report

### Status

Review — attempt 1 implementation complete and returned to `moda_architect`.

### Files Changed

- `src/lib/admin/billing.ts`
- `src/lib/admin/types.ts`
- `src/lib/admin/billing-presentation.mjs`
- `src/i18n/required-keys.ts`
- `src/i18n/locales/en.json`
- `tests/security/admin-billing-visibility.test.mjs`

### Work Completed

- Added the exact asynchronous report-state and recovery-pack status presentation mappings.
- Added protected, bounded recovery-pack list/detail and ledger-detail read helpers with database-level tenant scoping, durable status allowlisting, stable newest-first ordering, safe projections, and bounded provider summaries.
- Added the ARCH-008 Admin ICU keys and changed the existing reported-at label to `Submitted at` without changing the `reportedAt` data contract.
- Preserved the existing Admin layout and made no provider network calls.
- Implementation commits: `79a2397`, `e6361c9` on `task/ARCH-008-ADMIN-001`.

### Validation Results

- Focused ADMIN-001 tests: 33 passed, 0 failed.
- Full Admin tests: 126 passed, 3 skipped, 0 failed.
- `npx tsc --noEmit`: passed.
- `npm run lint`: passed with two pre-existing `queue-monitor.tsx` hook warnings.
- `npm run build`: passed with existing BullMQ dependency/critical-dependency warnings.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.

### Deviations

- The tracked database submodule was initialized locally because the Admin worktree did not have `database/prisma/schema.prisma`; no schema changes or parent gitlink changes were made.

### Assumptions

- `reportedAt` remains the durable field name; Admin presentation now localizes its label as `Submitted at`.

### Unresolved Issues

- None for ADMIN-001.

### Architectural Concerns

None

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is directionally correct and the protected read primitives are implemented within the intended Admin boundary, but the task is not yet acceptable.

The task specification makes the ARCH-008 English catalogue wording normative. The implementation added the required keys, but twelve task-owned values do not match the canonical copy:

```text
billing.tab.appEvents
  expected: App Events
  actual:   App events

billing.asyncReceiptHelp
  expected: Shopify has received the App Event. Billing validation is asynchronous.
  actual:   This is an asynchronous receipt. Shopify confirmation may arrive later.

billing.devDashboardHelp
  expected: If provider usage does not reconcile, inspect App Billing Event logs in the Shopify Dev Dashboard.
  actual:   Use the Shopify Partner Dashboard for provider-side billing details.

billing.eventDetails
  expected: App Event details
  actual:   Event details

billing.creditsGranted
  expected: Credits
  actual:   Credits granted

billing.planSnapshot
  expected: Plan handle snapshot
  actual:   Plan snapshot

billing.noRecoveryPacks
  expected: No recovery-credit purchases match the current filters.
  actual:   No recovery packs found

billing.billingHealth
  expected: Billing status
  actual:   Billing health

billing.overrideActiveWarning
  expected: Billing policy override active
  actual:   An active billing override is applied.

billing.overrideExpiredNotice
  expected: An expired billing policy override is recorded.
  actual:   This billing override has expired.

billing.activity
  expected: Billing activity
  actual:   Activity

billing.reconciliationUnavailableShort
  expected: Shopify usage comparison is not available for this tenant.
  actual:   Reconciliation unavailable
```

The `billing.devDashboardHelp` mismatch is materially incorrect, not merely stylistic: the task explicitly directs operators to App Billing Event logs in the Shopify Dev Dashboard and explicitly warns against implying unavailable provider detail.

The current tests do not detect these catalogue errors. `admin-internationalization.test.mjs` validates key presence/ICU validity, while `admin-billing-visibility.test.mjs` constructs its own in-memory labels for report/purchase-state tests. Therefore the test suite can pass while the shipped catalogue violates the task contract.

The read-helper implementation itself is architecture-conformant on inspection: authorization is server-side, tenant scoping is placed in the Prisma query, default/max page sizes are 20/50, ordering is `createdAt DESC, id DESC`, the recovery-pack provider summary is bounded, and no provider network call or layout redesign was introduced.

### Reviewed Files

- `moda-interact-admin/src/lib/admin/billing.ts`
- `moda-interact-admin/src/lib/admin/types.ts`
- `moda-interact-admin/src/lib/admin/billing-presentation.mjs`
- `moda-interact-admin/src/i18n/locales/en.json`
- `moda-interact-admin/src/i18n/required-keys.ts`
- `moda-interact-admin/tests/security/admin-billing-visibility.test.mjs`
- `moda-interact-admin/tests/security/admin-internationalization.test.mjs`
- `docs/architecture/ARCH-008-shopify-app-pricing-conformance.md`
- this task's Completion Report
- published implementation commits `79a2397`, `e6361c9`
- published parent report commit `97de144`

### Validation Reviewed

- Agent-reported focused ADMIN-001 tests: 33 passed.
- Agent-reported full Admin tests: 126 passed, 3 skipped.
- Agent-reported TypeScript, build, Prisma validation and `git diff --check`: passed.
- Agent-reported lint: passed with two pre-existing `queue-monitor.tsx` warnings.
- Published implementation branch is two commits ahead of Admin `main`, zero behind, and limited to the six task-authorised source/test files.
- The above passing tests are insufficient to validate the normative catalogue values because they do not assert those shipped values directly.

### Architecture Conformance

Changes required.

The protected read-model architecture and asynchronous billing state model conform. The user-facing catalogue does not yet conform to the canonical ARCH-008 wording, and the task-required regression proof is incomplete.

### Follow-up

Attempt 2 must remain on the SAME task and SAME mirrored `task/ARCH-008-ADMIN-001` branches.

Required corrections:

1. Correct the twelve catalogue values listed above to the canonical task wording. Do not substitute alternate wording or a different Shopify dashboard/location.
2. Add focused regression assertions against the actual `src/i18n/locales/en.json` catalogue for the ARCH-008 normative values. At minimum cover `REPORTED`, `Submitted at`, both explanatory/help strings, all four pack statuses, and every value corrected in item 1.
3. Strengthen the read-helper security/contract regression so it specifically proves the two detail helpers apply `id + shopId` at the Prisma query boundary, rather than relying on the current broad `/shopId,/` source match. Also explicitly cover the `providerResponseSummary` bound and the 20-default/50-maximum pagination contract.
4. Record the mandatory launcher-resolved physical parent/implementation worktree evidence and start-of-attempt synchronisation evidence in the Completion Report. If Attempt 1 did use the canonical isolated worktrees, record that evidence accurately; do not invent it. If it did not, restore/use the canonical task worktrees, rerun required validation there, and record the workflow non-conformance and corrected validation. No source churn is required solely for this evidence item.
5. Rerun the task's focused tests, full Admin test suite, TypeScript, lint, build, Prisma validation and `git diff --check`; record the results and return the task to `review`.

Do not start `ARCH-008-ADMIN-002` until this task is architect-accepted Complete.
