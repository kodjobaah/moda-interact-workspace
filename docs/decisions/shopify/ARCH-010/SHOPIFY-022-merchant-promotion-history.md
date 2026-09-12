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
status: pending
priority: 86
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-SHOPIFY-021
  - ARCH-010-DATABASE-011
enables:
  - ARCH-010-SYSTEM-TEST-003
created: 2026-09-12
updated: 2026-09-12
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

Legacy campaign-less DATABASE-009 direct grants may be shown only as a generic historical Moda promotional credit entry if product UX needs to preserve existing data; do not fabricate a campaign identity for them.

## Required tests

Prove tenant isolation, selected-vs-used distinction, exhausted/expired/reopened display, remaining calculation, legacy-row safe fallback, pagination and absence of internal provenance leakage.

## Non-goals

Do not allow selecting campaigns from history, mutate campaign/grant quantities, reopen campaigns, refund promotional credits or add export/marketing analytics.

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
