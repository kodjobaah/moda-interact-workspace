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
status: in_progress
priority: 86
executor: copilot
claimed_at: 2026-09-13T21:04:14Z
attempt: 1
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
- Added focused unit/security coverage for selected-vs-used distinction, remaining calculation, exhaustion/current selection fields, pagination/filter bounds, SUPER_ADMIN gating and mutation absence.

### Validation Results
- `node --experimental-strip-types --test tests/unit/promotion-report.test.ts tests/security/admin-promotions.test.mjs`: passed, 15/15.
- `npm test`: passed (declared observability/security suite).
- `npm run lint`: passed with two pre-existing warnings in `src/components/admin/queue-monitor.tsx` (missing `refresh` hook dependencies); no errors.
- `npm run build`: passed; Prisma client generated and TypeScript/Next production build completed, including `/promotions/[campaignId]`.
- `git diff --check`: passed.
- Build emitted existing BullMQ warnings for dynamic dependency resolution and optional `@valkey/valkey-glide`; no build failure.

### Git / VCS
- Launcher packet evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-006` on `task/ARCH-010-ADMIN-006`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-006` on the same branch name.
- Prepared execution reported physical isolation/synchronization ready, dependency gate passed, parent head `a72e144342dd0335cf5ccaac822c2fe9e2dab51f`, implementation head `7f484c3883400fa36ac472222e48389c9390fbd8`, and initialized database submodule at `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`.
- Implementation commit and push: `4fca6c8` pushed to `origin/task/ARCH-010-ADMIN-006`.
- Parent report commit and push: recorded by the parent publication commit after this report update.

### Architect Review
No Architect Review section was present in the complete claimed task file; there were no Changes Requested items. Ready for architect review after implementation publication.
