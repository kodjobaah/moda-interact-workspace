---
id: ARCH-010-ADMIN-005
architecture_id: ARCH-010
title: Manage promotion catalogue, close campaigns and reopen by expiry only
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 85
attempt: 1
depends_on:
- ARCH-010-ADMIN-004
enables:
- ARCH-010-ADMIN-006
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: '2026-09-13'
---

# ARCH-010-ADMIN-005: Manage promotion catalogue, close campaigns and reopen by expiry only

## Objective

Give SUPER_ADMIN a durable catalogue of **all promotions ever created**, with clear running/expired/closed state, append-only lifecycle history, manual close and safe reopen of the **same campaign ID** by changing only its expiry (and status when necessary).

## Required catalogue

Show at minimum:

```text
campaign name
scope
target summary
credit quantity
startsAt
expiresAt
derived running/expired state
persisted status
createdAt/creator
last lifecycle change
```

Support bounded filtering for running, expired/closed, scope and target where current Admin patterns permit it. Do not delete historical campaigns.

## Close

SUPER_ADMIN may close a DRAFT/ACTIVE campaign using the DATABASE-010 state machine. Closing must append `PromotionCampaignEvent(CLOSED)` and make the campaign immediately unavailable for new merchant selection/new promotional reservations.

Closing does not delete existing merchant grant/history and does not claw back committed usage.

## Reopen / extend expiry

Reopen must preserve:

```text
same campaign id
same scope
same target
the same credit quantity
all existing merchant grant/history rows
```

The only campaign commercial field that may change during reopen is `expiresAt`, and the new value must be in the future and after `startsAt`.

For an expired ACTIVE campaign, reopen means advancing `expiresAt` and appending `REOPENED`/`EXPIRY_CHANGED` audit evidence according to the canonical event convention.

For a CLOSED campaign, reopen also restores `status=ACTIVE` and appends the lifecycle evidence.

Reopen MUST NOT:

- clone the campaign;
- grant credits;
- reset any merchant's campaign quantity;
- clear committed usage;
- change target/quantity;
- auto-select the campaign for merchants.

## Concurrency/idempotency

Use optimistic/version/transaction patterns already supported by DATABASE-010. Two conflicting close/reopen actions must not silently overwrite each other.

## Required tests

At minimum prove:

1. catalogue retains DRAFT/ACTIVE/CLOSED/expired campaigns;
2. derived running state uses status + time window;
3. only SUPER_ADMIN can close/reopen;
4. close is audited and immediately prevents running state;
5. reopen keeps same ID;
6. reopen accepts only future expiry;
7. reopen cannot change quantity/scope/target;
8. reopen creates no merchant grant/selection;
9. existing merchant campaign usage remains untouched;
10. concurrent stale mutation fails safely;
11. no delete action removes campaign history.

## Non-goals

Do not implement merchant catalogue/selection, Background consumption, campaign usage analytics, automated scheduling messages or Shopify billing actions.

## Stop conditions

Stop if ADMIN-004/DATABASE-010 state names differ materially; reconcile with `moda_architect` rather than inventing parallel lifecycle values.

## Completion Report

### Status
Review.

### Files Changed
- `src/app/(protected)/promotions/page.tsx`
- `src/app/actions/promotions.ts`
- `src/components/admin/promotion-campaign-form.tsx`
- `src/lib/admin/promotion-validation.ts`
- `src/lib/admin/promotions.ts`
- `tests/security/admin-promotions.test.mjs`
- `tests/unit/promotion-validation.test.ts`

### Work Completed
- Added a durable SUPER_ADMIN promotion catalogue projection retaining DRAFT, ACTIVE, CLOSED, and expired campaigns, with bounded state/scope/target filters, persisted status, derived state, scope/target summary, quantity, dates, creator, creation time, and latest lifecycle event.
- Added transactional close and reopen mutations using `PromotionCampaign.version` compare-and-set predicates. Close supports DRAFT/ACTIVE, writes CLOSED audit evidence, and immediately removes the campaign from the running state. Reopen preserves the same campaign ID and commercial terms, changes only expiry (and restores ACTIVE for CLOSED campaigns), and writes REOPENED plus EXPIRY_CHANGED evidence.
- Enforced future expiry and `expiresAt > startsAt` on reopen; lifecycle forms expose no quantity, scope, target, or start-time editing.
- Preserved existing grants, selections, usage, and committed history by keeping lifecycle mutations isolated from those models; no delete action was introduced.
- Added focused validation and static security coverage for role gating, catalogue retention/derived state, lifecycle audit/CAS behavior, commercial-term immutability, preservation boundaries, and absence of deletion.

### Validation Results
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `node --experimental-strip-types --test tests/unit/promotion-validation.test.ts`: passed, 5 tests.
- `node --test tests/security/admin-promotions.test.mjs`: passed, 12 tests.
- `npm test`: passed.
- `npm run lint`: passed with two pre-existing warnings in `src/components/admin/queue-monitor.tsx`.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed; existing BullMQ optional-dependency/critical-dependency warnings remain.
- `git diff --check`: passed.

### Git / VCS
Physical worktree isolation:
	canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
	parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-005`
	parent branch: `task/ARCH-010-ADMIN-005`
	implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-005`
	implementation branch: `task/ARCH-010-ADMIN-005`
	shared workspace checkout switched/mutated for task work: no
	shared implementation checkout switched/mutated for task work: no
	another task worktree reused: no

database submodule initialized: yes
database gitlink expected: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`
database submodule HEAD: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`
database gitlink staged/changed: no

Parent claim commit: `d1b58fc`, pushed to `origin/task/ARCH-010-ADMIN-005` in `moda-interact-workspace`.
Implementation commit: `a8c13cf`, pushed to `origin/task/ARCH-010-ADMIN-005` in `moda-interact-admin`.
Parent report commit: pending publication.
The implementation worktree was clean after publication; main branches were not modified.

### Architect Review
Pending.
