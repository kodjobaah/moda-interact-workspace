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
status: pending
priority: 86
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-ADMIN-005
- ARCH-010-DATABASE-013
enables:
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-12
updated: '2026-09-12'
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
