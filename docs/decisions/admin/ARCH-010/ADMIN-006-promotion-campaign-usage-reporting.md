---
id: ARCH-010-ADMIN-006
architecture_id: ARCH-010
title: Report campaign merchant selection and promotional-credit usage
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 86
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-010-ADMIN-005
- ARCH-010-DATABASE-013
enables:
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-12
updated: 2026-09-13
---

# ARCH-010-ADMIN-006: Report campaign merchant selection and promotional-credit usage

## Objective

Add internal campaign-detail reporting so Moda can answer which merchants selected/used a promotion and how much of each one-time campaign allocation remains, without using aggregate shop counters as historical truth.


## Required campaign detail

For one campaign show bounded/paginated merchant rows containing at minimum:

```text
shop identity/display label
firstSelectedAt
lastSelectedAt
selectionCount
quantity granted
reserved
committed
remaining allocation
firstUsedAt
lastUsedAt
exhaustedAt/status
currently selected? (derived from MerchantPromotionSelection)
```

Provide summary counts such as:

```text
merchants selected
merchants actually used (firstUsedAt != null)
merchants exhausted
total campaign credits committed
```

Use `PromotionalCreditGrant(campaignId, shopId)` as campaign merchant history and accounting authority. DATABASE-013 has no aggregate promotional entitlement counter; reporting must be derived from exact campaign grant lots.

## Privacy/security

- SUPER_ADMIN only;
- bounded pagination/filtering;
- no shopper PII beyond existing safe tenant identity surfaces;
- no ability to mutate merchant grant quantities from this reporting task.

## Required tests

Prove selected-vs-used distinction, remaining calculation, reopened campaign preserving same merchant grant, exhausted reporting, currently-selected derivation, pagination/security and absence of mutation actions.

## Non-goals

Do not add campaign creation/reopen, merchant selection, direct credit adjustment, export pipeline or marketing automation.

## Stop conditions

Stop if DATABASE-011 does not expose deterministic per-campaign/shop grant history fields required by this report.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-admin/src/lib/admin/promotion-report-model.ts`
- `moda-interact-admin/src/lib/admin/promotion-report.ts`
- `moda-interact-admin/src/app/(protected)/promotions/page.tsx`
- `moda-interact-admin/src/app/(protected)/promotions/[campaignId]/page.tsx`
- `moda-interact-admin/tests/unit/promotion-report.test.ts`
- `moda-interact-admin/tests/security/admin-promotions.test.mjs`

### Work Completed
- Added a SUPER_ADMIN-only, server-side campaign usage report derived from exact `PromotionalCreditGrant(campaignId, shopId)` lots.
- Added bounded 25-row pagination and bounded merchant search across safe shop ID/domain fields, with selected/used/exhausted filters.
- Added campaign-wide selected, used, exhausted and committed-credit summaries.
- Added merchant rows with selection/use timestamps, selection count, granted/reserved/committed/remaining quantities, exhaustion and current-selection derivation from `MerchantPromotionSelection`.
- Added a read-only detail route and linked it from the existing campaign catalogue. No grant, selection, campaign, entitlement or audit mutation is exposed.
- Added a pure report-model seam so executable unit tests cover selected-vs-used distinction, independent first/last use timestamps, remaining calculation, reopened/reselected grant preservation, exhaustion/current selection fields, page/search normalization, pagination/filter bounds, SUPER_ADMIN gating and mutation absence.
- Completed the Attempt-2 presentation correction: the merchant table visibly renders first/last selection and use timestamps, selection count, all allocation quantities, exhausted status and current-selection state; Previous/Next links preserve normalized status and non-empty search filters.

### Validation Results
- `node --experimental-strip-types --test tests/unit/promotion-report.test.ts tests/security/admin-promotions.test.mjs`: passed, 20/20.
- `npm test`: passed, 171/171 (declared observability/security suite).
- `npm run lint`: passed with two pre-existing warnings in `src/components/admin/queue-monitor.tsx` (missing `refresh` hook dependencies); no errors attributable to ADMIN-006.
- `npm run build`: passed; Prisma client generated and TypeScript/Next production build completed, including `/promotions/[campaignId]`.
- `git diff --check`: passed.
- Build emitted existing BullMQ warnings for dynamic dependency resolution and optional `@valkey/valkey-glide`; no build failure.

### Git / VCS
- Attempt-2 launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-006`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-006`; both synchronized on `task/ARCH-010-ADMIN-006`; recursive database submodule status `ready` at `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`.
- Attempt-2 implementation commit and push: `b0332e5` pushed to `origin/task/ARCH-010-ADMIN-006`.
- Attempt-2 claim evidence: executor `copilot`, dependency gate passed, claim committed and pushed before implementation; parent report publication is the commit containing this update.
- Launcher packet evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-006` on `task/ARCH-010-ADMIN-006`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-006` on the same branch name.
- Prepared execution reported physical isolation/synchronization ready, dependency gate passed, parent head `a72e144342dd0335cf5ccaac822c2fe9e2dab51f`, implementation head `7f484c3883400fa36ac472222e48389c9390fbd8`, and initialized database submodule at `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`.
- Implementation commit and push: `4fca6c8` pushed to `origin/task/ARCH-010-ADMIN-006`.
- Parent report commit and push: recorded by the parent publication commit after this report update.

### Architect Review
No Architect Review section was present in the complete claimed task file; there were no Changes Requested items. Ready for architect review after implementation publication.

## Architect Review — Attempt 1

### Review Status

Changes Requested

### Implementation reviewed

```text
implementation repository: moda-interact-admin
implementation commit: 4fca6c8da67ad6c715a4d22d1f3f78f8c03a186d
parent Completion Report commit: 1b0d00184cc0d5bbd02eeeb909c6aa57ca53d436
attempt reviewed: 1
```

The implementation is within the original ADMIN-006 scope and the server-side
read model is directionally correct. Keep this same task. Do not create a
replacement task and do not start `ARCH-010-SYSTEM-TEST-003`.

The following Attempt-1 work is accepted in substance and MUST be preserved:

```text
- SUPER_ADMIN-only page/data access;
- PromotionalCreditGrant(campaignId, shopId) remains campaign history and
  accounting authority;
- campaign-wide selected/used/exhausted/committed summary queries;
- 25-row server-side result bound;
- merchant search bounded to 255 characters and restricted to safe shop ID/domain
  surfaces;
- quantity/reserved/committed/remaining projection from the exact grant lot;
- current-selection derivation from MerchantPromotionSelection;
- campaign catalogue -> read-only usage-report navigation;
- no grant, campaign, selection, entitlement-counter or audit mutation path.
```

Attempt 2 is a bounded correction of the report presentation and its permanent
evidence. Do not redesign promotion lifecycle/accounting and do not modify the
Prisma schema or another repository.

### Changes Requested

#### 1. Show the complete minimum merchant-history fields required by ADMIN-006

File:

```text
moda-interact-admin/src/app/(protected)/promotions/[campaignId]/page.tsx
```

The task requires both first and last selection/use timestamps. The current
projection fetches/maps `lastSelectedAt` and `lastUsedAt`, but the UI never
renders them.

Change the merchant table so every row visibly presents:

```text
firstSelectedAt
lastSelectedAt
selectionCount
firstUsedAt
lastUsedAt
exhaustedAt / derived status
currentlySelected
quantityGranted
reserved
committed
remainingAllocation
```

For nullable timestamps render a deterministic placeholder such as `-`.
Do not remove the existing first-selection or first-use timestamps.

#### 2. Make pagination operable from the report UI

File:

```text
moda-interact-admin/src/app/(protected)/promotions/[campaignId]/page.tsx
```

`getPromotionReport()` already reads `page` and bounds each database page to 25
rows, but the UI exposes no way to move between pages. A user must not need to
manually edit the URL.

Add explicit Previous/Next report navigation with these exact rules:

```text
Previous is available only when report.page > 1.
Next is available only when report.page < report.totalPages.
The destination page is report.page - 1 / report.page + 1 respectively.
Preserve the normalized status filter.
Preserve the current merchant-search value when non-empty.
Do not introduce a client-side fetch/state pagination layer.
Do not change PROMOTION_REPORT_PAGE_SIZE from 25.
```

Use normal Next `Link` navigation/query parameters. Keep this page a server
component.

#### 3. Replace source-text-only accounting tests with behavioural report tests

Current file:

```text
moda-interact-admin/tests/unit/promotion-report.test.ts
```

The two current tests only read `promotion-report.ts` as text and prove that
particular tokens/formulas are present. They do not execute the reporting
projection and therefore do not satisfy the task's required evidence for
selected-vs-used distinction, reopened/reselected grant preservation,
exhaustion/current-selection projection or remaining-allocation behaviour.

Create a small pure reporting projection seam so these rules can be executed by
Node unit tests without importing Next auth or the live Prisma singleton.
Preferred deterministic shape:

```text
moda-interact-admin/src/lib/admin/promotion-report-model.ts
```

Move only pure report-domain behaviour into that file, for example:

```text
PROMOTION_REPORT_PAGE_SIZE = 25
page normalization
search trim/255-character normalization
PromotionalCreditGrant -> PromotionMerchantRow projection
```

`promotion-report.ts` MUST call/reuse the pure helpers; do not duplicate the
formula in production and tests. Keep Prisma queries, authorization and I/O in
`promotion-report.ts`.

`tests/unit/promotion-report.test.ts` must import and execute the pure helpers.
At minimum add behavioural assertions proving all of the following:

1. selected-but-unused grant:
   - `firstSelectedAt` is preserved;
   - `firstUsedAt`/`lastUsedAt` remain null;
   - it is distinguishable from a used grant;
2. used grant:
   - first and last use timestamps are preserved independently from selection
     timestamps;
3. remaining allocation is exactly:
   `quantity - reservedQuantity - committedQuantity`, bounded at zero;
4. reopened/reselected same campaign grant:
   - one input grant with `selectionCount > 1` remains one projected allocation;
   - original `quantity` is not replenished or multiplied;
   - first/last selection history is preserved;
5. exhausted grant preserves `exhaustedAt`;
6. `currentlySelected` is true only when the grant has the current
   `MerchantPromotionSelection` relation and false when it does not;
7. page normalization rejects zero, negative, fractional and non-finite values
   to page 1 while preserving valid positive integer pages;
8. merchant search is trimmed and truncated to at most 255 characters.

Do not satisfy these items with `fs.readFileSync(...)/assert.match(...)` alone.
The accounting/history assertions above must execute real TypeScript functions.

#### 4. Extend permanent UI/security evidence for the corrected presentation

Files:

```text
moda-interact-admin/tests/security/admin-promotions.test.mjs
and/or another focused ADMIN-006 presentation test
```

Keep the existing SUPER_ADMIN/read-only assertions and add evidence that the
report UI contains:

```text
lastSelectedAt presentation
lastUsedAt presentation
Previous pagination
Next pagination
filter-preserving pagination construction
```

The read-only source assertion must continue to prove that ADMIN-006 introduces
no create/update/upsert/delete mutation path.

### Scope boundaries

Attempt 2 MUST NOT:

```text
- change database schema/migrations;
- change PromotionalCreditGrant or MerchantPromotionSelection persistence
  semantics;
- add campaign creation/close/reopen behaviour;
- add merchant grant/selection mutation;
- add credit adjustment or export actions;
- modify another repository;
- change the 25-row page size;
- weaken SUPER_ADMIN gating;
- turn this report into client-side state/fetch architecture;
- fix unrelated lint/build warnings.
```

Production changes outside the detail-page presentation and the small pure
report-model extraction are not authorized unless a new behavioural test proves
that the existing report query is incorrect. If that happens, STOP and return
the exact defect to `moda_architect` instead of broadening scope.

### Required validation for Attempt 2

Run from the dedicated ADMIN-006 implementation worktree after launcher
preparation:

```bash
node --experimental-strip-types --test tests/unit/promotion-report.test.ts tests/security/admin-promotions.test.mjs
npm test
npm run build
npm run lint
git diff --check
```

Expected result:

```text
- focused ADMIN-006 tests pass, including behavioural projection tests;
- repository test suite passes;
- production build passes;
- lint has no new errors/warnings attributable to ADMIN-006; the two documented
  pre-existing queue-monitor hook warnings may remain if unchanged;
- git diff --check passes;
- database submodule/gitlink remains unchanged.
```

The Completion Report must name the new behavioural test cases explicitly and
record launcher-resolved parent/implementation worktree isolation,
start-of-attempt synchronization, recursive database-submodule evidence and the
implementation/report commits.

### Attempt / reclaim contract

Return this SAME task to the normal `/moda-task` execution path:

```text
status: ready
executor: null
claimed_at: null
attempt: 1
```

Preserve `attempt: 1` in this architect overlay. The next authorized claim MUST
increment it to **Attempt 2 exactly once**.

### Stop Condition

After the exact corrections and required validation above are complete, update
the Completion Report, set this same task to `review`, clear the active claim,
push both mirrored `task/ARCH-010-ADMIN-006` branches, return control to
`moda_architect`, and STOP.

Do not start `ARCH-010-SYSTEM-TEST-003` or any adjacent Admin task.

## Architect Review — Attempt 2

### Review Status

Accepted.

### Implementation reviewed

```text
implementation repository: moda-interact-admin
implementation commit: b0332e51f95eaa6072bc482db84dcc01489ecf1d
parent Completion Report commit: bbe6647975b0dccf8d4f50ce424e045786d1a41b
attempt reviewed: 2
```

Attempt 2 satisfies the bounded Changes Requested contract from Attempt 1.
The implementation remains within ADMIN-006 scope and preserves the already
accepted campaign accounting/security design.

The architect verified that the report now visibly presents the complete minimum
merchant-history projection required by this task:

```text
firstSelectedAt
lastSelectedAt
selectionCount
quantityGranted
reserved
committed
remainingAllocation
firstUsedAt
lastUsedAt
exhaustedAt / status
currentlySelected
```

Nullable first/last selection/use timestamps use the deterministic `-` placeholder.
The status presentation distinguishes exhausted, currently selected and no-longer-current
grants without adding a mutation path.

Pagination is now operable from the server-rendered report. `Previous` is emitted
only when `report.page > 1`; `Next` is emitted only when
`report.page < report.totalPages`; both use normal Next `Link` navigation and
preserve the normalized status filter plus a non-empty merchant search. The report
remains server-side and `PROMOTION_REPORT_PAGE_SIZE` remains exactly 25.

The new pure production seam:

```text
src/lib/admin/promotion-report-model.ts
```

is imported by `promotion-report.ts` and owns the page/search normalization and
grant-to-row projection. The unit tests execute those production helpers directly;
they no longer rely on source-text matching for the accounting/history semantics.

The permanent behavioural tests prove:

```text
- selected-but-unused is distinct from used;
- first/last selection history is preserved;
- first/last use history is preserved independently;
- remaining = max(0, quantity - reserved - committed);
- reselection with selectionCount > 1 preserves one original grant allocation;
- exhaustion timestamp is preserved;
- currentlySelected is derived only from the current selection relation;
- invalid/fractional/non-finite pages normalize to page 1;
- positive integer pages are preserved;
- merchant search is trimmed and truncated to 255 characters.
```

Security/presentation evidence continues to prove SUPER_ADMIN gating, bounded
server-side pagination, safe shop ID/domain search, read-only report behaviour,
last-selection/last-use presentation, Previous/Next navigation and preservation of
status/search query state. No Prisma create/update/upsert/delete path was introduced
by ADMIN-006.

### Validation Reviewed

The architect independently reran against the uploaded Attempt-2 snapshot:

```text
node --experimental-strip-types --test \
  tests/unit/promotion-report.test.ts \
  tests/security/admin-promotions.test.mjs

20 tests
20 passed
0 failed
```

The Completion Report additionally records:

```text
npm test: 171/171 passed
npm run build: passed
npm run lint: passed with only the two documented pre-existing queue-monitor warnings
git diff --check: passed
database submodule: unchanged at 5443afdd8f0c816dc16e1f3e93f9906c5ca31d94
```

The reported launcher evidence records the canonical isolated parent and
implementation worktrees, synchronized mirrored `task/ARCH-010-ADMIN-006`
branches and recursively materialized database submodule. No shared/default or
other-task worktree execution is reported.

### Architecture Conformance

Conformant.

`PromotionalCreditGrant(campaignId, shopId)` remains the campaign merchant-history
and accounting authority. `MerchantPromotionSelection` is used only to derive
current selection. Campaign-wide summary counts remain read-only. The task does
not alter campaign lifecycle, grant persistence, selection persistence, the Prisma
schema, another repository or the promotion-consumption architecture.

### Architect Decision

**Accepted — Attempt 2.**

Because `completion_mode: automatic`, the task is now:

```text
status: complete
attempt: 2
executor: null
claimed_at: null
```

### Dependency reconciliation

`ARCH-010-SYSTEM-TEST-003` remains `pending / manual-gated`. ADMIN-006 is now a
satisfied dependency, but SYSTEM-TEST-003 still has multiple incomplete
implementation dependencies. Do not claim or start it solely because ADMIN-006 is
Complete.

