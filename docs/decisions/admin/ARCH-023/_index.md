# ARCH-023 Admin tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_admin`.

Repository: `moda-interact-admin`.

Coordinator: `moda_architect`.

The Admin decomposition follows independent product/lifecycle boundaries:

```text
            DATABASE-001 + SHARED-002
                    |
                    v
                ADMIN-001
      Merchant Knowledge plan entitlement

DATABASE-001
     |
     v
 ADMIN-002
 Store Categories / templates / taxonomy
     |
     v
 ADMIN-003
 Platform + Shop Instructions lifecycle
```

ADMIN-001 and ADMIN-002 are independent once their prerequisites are complete and may execute in parallel.

Individual task YAML is authoritative.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [ADMIN-001](ADMIN-001-author-merchant-knowledge-plan-entitlement.md) | Merchant Knowledge Feature/default plan inclusion and plan-specific C2 configuration | Complete — Accepted Attempt 2 | DATABASE-001, SHARED-002 |
| [ADMIN-004](ADMIN-004-make-merchant-knowledge-merchant-opt-in.md) | Reconcile Merchant Knowledge Feature to `MERCHANT_OPT_IN` without seeding per-shop preferences | Ready | ADMIN-001 |
| [ADMIN-002](ADMIN-002-manage-store-categories-default-templates.md) | Store Category, canonical-English default templates and Shopify taxonomy mappings | Complete — Accepted Attempt 2 | DATABASE-001 |
| [ADMIN-003](ADMIN-003-author-platform-shop-instructions.md) | Platform/Shop prompt draft, publish, activation and pending-category promotion | Ready | DATABASE-001, ADMIN-002 |

## Removed obsolete decomposition

The previous ARCH-023 Admin tasks for database-backed Store Category/template translations are obsolete. The current architecture uses source-controlled Shopify localization catalogues and contains no Admin translation queue/lifecycle for categories/templates.

## Execution frontier

The authoritative Admin task state after ADMIN-001 Attempt 2 acceptance is:

```text
ADMIN-001 -> Complete — Accepted Attempt 2
ADMIN-002 -> Complete — Accepted Attempt 2
ADMIN-003 -> Ready
```

ADMIN-001 and ADMIN-002 remain independent completed product/lifecycle boundaries. ADMIN-004 is independently Ready from the accepted ADMIN-001 baseline and owns only the merchant-opt-in reconciliation; it does not alter Store Category/prompt work.
ADMIN-003 was already Ready because its declared prerequisites are DATABASE-001 and
ADMIN-002; ADMIN-001 acceptance does not change that status and does not start it
implicitly.

ADMIN-001 also satisfies one prerequisite of downstream `ARCH-023-COMMERCE-002`, but that
Commerce task remains Pending until its other prerequisite, `ARCH-023-COMMERCE-001`, is
Complete.

## Merchant opt-in reconciliation

`ADMIN-004` is a bounded follow-up to accepted ADMIN-001. It does not rewrite ADMIN-001 history; it transitions the fixed `merchant_knowledge` Feature from the previously accepted `ALWAYS_ENABLED` state to the final `MERCHANT_OPT_IN` state.
