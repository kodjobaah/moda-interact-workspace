---
id: ARCH-010-DATABASE-003
architecture_id: ARCH-010
title: Persist authenticated reinstall reconciliation state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 48
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-001
enables:
  - ARCH-010-BACKGROUND-006
  - ARCH-010-SHOPIFY-006
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-DATABASE-003: Persist authenticated reinstall reconciliation state

## Objective

Add the smallest durable marker required to distinguish:

```text
shop is still genuinely uninstalled
```

from:

```text
Shopify has authenticated a reinstall, but Moda deliberately keeps execution disabled until Partner subscription reconciliation succeeds
```

Do not add a new ShopStatus or subscription status.

## Inspect before editing

Repository: `moda-interact-database/`.

Inspect at minimum:

```text
prisma/schema.prisma
prisma/migrations/**
scripts/validate-billing-lifecycle-schema.mjs
package.json
docs/generated/prisma-erd.puml
```

Read the integrated ARCH-010 DATABASE-001 migration first. `Subscription.nextReconcileAt` is the durable wake-up time and must not be duplicated on Shop.

## Required schema change

Add exactly one nullable field to `commerce.Shop`:

```prisma
reinstallPendingAt DateTime?
```

Add a reconstruction-friendly index equivalent to:

```prisma
@@index([status, reinstallPendingAt])
```

Preserve existing:

```text
status
installedAt
uninstalledAt
```

semantics and data.

## Durable semantics

```text
reinstallPendingAt = NULL
  -> no authenticated reinstall is awaiting subscription reconciliation

Shop.status = UNINSTALLED
AND reinstallPendingAt != NULL
  -> authenticated reinstall has occurred, but all normal shop/customer execution remains disabled until reconciliation completes
```

The field is not Shopify subscription truth and is not an entitlement counter.

`Subscription.nextReconcileAt` remains the scheduling timestamp for the canonical BullMQ reconciliation job.

## Migration requirements

- nullable column, no backfill;
- existing Shops remain valid with NULL;
- no ShopStatus enum change;
- no rewrite of `installedAt` or `uninstalledAt`;
- no Subscription/BillingPeriod/counter/purchase/refund rewrite;
- add the composite/index using the repository's actual PostgreSQL naming conventions.

## Required validation

After inspecting `package.json`, run the repository-declared Prisma format/validate/generate/schema validation commands and `git diff --check`.

Add/update schema validation proving at least:

1. `Shop.reinstallPendingAt` exists and is nullable;
2. existing rows need no backfill;
3. `(status, reinstallPendingAt)` is indexed;
4. ShopStatus still contains exactly the existing lifecycle values unless another accepted task has changed it;
5. `Subscription.nextReconcileAt` remains present and unchanged;
6. migration does not mutate entitlement/purchase/refund data.

Regenerate the repository-owned ERD if that is part of normal schema validation.

## Non-goals

Do not implement:

- auth/reinstall routes;
- Partner API calls;
- BullMQ;
- billing-period rollover;
- shop identity redesign;
- Admin UI;
- subscription history.

## Stop conditions

STOP and return to `moda_architect` if:

- a newer integrated Shop lifecycle model already has an equivalent reinstall/reconciliation marker;
- DATABASE-001 is not integrated and `nextReconcileAt` has materially changed;
- the migration requires a ShopStatus expansion merely to add this marker;
- another repository would need modification from this task.

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
