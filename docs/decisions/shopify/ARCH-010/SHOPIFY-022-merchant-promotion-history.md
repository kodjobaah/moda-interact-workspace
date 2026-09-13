---
id: ARCH-010-SHOPIFY-022
architecture_id: ARCH-010
title: Show merchant promotion selection and usage history
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 86
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-010-SHOPIFY-021
- ARCH-010-DATABASE-013
enables:
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-12
updated: 2026-09-13
---

# ARCH-010-SHOPIFY-022: Show merchant promotion selection and usage history

## Objective

Expose a tenant-safe merchant history of promotions this Shop selected/used while preserving campaign and internal Admin privacy boundaries.

## Required history

Read campaign-linked `PromotionalCreditGrant` rows for the authenticated Shop and present bounded/paginated entries containing merchant-safe information equivalent to:

```text
campaign name
original promotional quantity
committed/used quantity
remaining allocation
first/last selected time
first/last used time when present
campaign current expiry
status such as selected / used / exhausted / expired / closed / no-longer-eligible
```

The history must distinguish:

```text
selected but never used
actually used (firstUsedAt != null)
exhausted
partially used then expired/closed
reopened with remaining allocation
```

Do not infer merchant campaign history from the aggregate promotional counter.

## Privacy

Never expose Admin identity, internal audit event payloads, internal target IDs, request keys or support/internal grant classifications.

DATABASE-013 contains only campaign-linked merchant promotional grants. Do not implement a campaign-less/direct-grant fallback, fabricate a campaign identity, or query removed compatibility provenance.

## Required tests

Prove tenant isolation, selected-vs-used distinction, exhausted/expired/reopened display, remaining calculation, pagination, campaign-link integrity and absence of internal provenance leakage.

## Non-goals

Do not allow selecting campaigns from history, mutate campaign/grant quantities, reopen campaigns, refund promotional credits or add export/marketing analytics.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact/app/services/promotions/promotion.service.ts`
- `moda-interact/app/routes/app/promotions/route.tsx`
- `moda-interact/tests/unit/services/promotion.service.test.ts`
- `moda-interact/tests/unit/routes/promotion-route.test.ts`

### Work Completed
- Added a tenant-scoped `getPromotionHistory` query over exact `PromotionalCreditGrant` rows, bounded to 25 entries per page and ordered by selection history.
- Added merchant-safe campaign history projection for granted, committed, remaining, selection/use timestamps, current expiry, current-selection state and lifecycle status.
- Distinguishes selected, used, exhausted, expired, closed, no-longer-eligible and reopened history without reading aggregate promotional counters or internal provenance.
- Added history presentation and Previous/Next pagination to the existing promotions route; history exposes no mutation controls or internal admin metadata.

### Validation Results
- Focused promotion service/route tests: passed, 33/33.
- Full test suite: passed, 316 tests; 34 files passed and 2 skipped.
- Production build: passed; Prisma client generated and React Router client/SSR bundles built.
- `git diff --check`: passed.
- `npm run typecheck`: repository baseline failure; no diagnostics in the changed promotion service or route. Existing errors remain across unrelated JSX, billing, webhook and Redis files.
- `npm run lint`: repository baseline failure with 11 unrelated errors in onboarding, billing, merchant support, privacy and webhook files; no errors in changed promotion files. TypeScript 5.9 unsupported-version warning also remains baseline.

### Git / VCS
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-SHOPIFY-022` on `task/ARCH-010-SHOPIFY-022`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-SHOPIFY-022` on `task/ARCH-010-SHOPIFY-022`.
- Launcher preparation: dependency gate passed; parent and implementation worktrees created and synchronized; recursive database submodule ready at `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`; Attempt 1 claim committed and pushed by launcher as `e16ba673b0236aaba9ab1772d5334a9cdf0dfae4`.
- Implementation commit `0d66cc1` pushed to `origin/task/ARCH-010-SHOPIFY-022`.

### Architect Review
Pending architect review after publication.
