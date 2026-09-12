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
status: pending
priority: 85
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-ADMIN-004
enables:
- ARCH-010-ADMIN-006
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: '2026-09-12'
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
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
