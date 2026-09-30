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
| [ADMIN-001](ADMIN-001-author-merchant-knowledge-plan-entitlement.md) | Merchant Knowledge Feature/default plan inclusion and plan-specific C2 configuration | Ready | DATABASE-001, SHARED-002 |
| [ADMIN-002](ADMIN-002-manage-store-categories-default-templates.md) | Store Category, canonical-English default templates and Shopify taxonomy mappings | Complete — Accepted Attempt 2 | DATABASE-001 |
| [ADMIN-003](ADMIN-003-author-platform-shop-instructions.md) | Platform/Shop prompt draft, publish, activation and pending-category promotion | Ready — Changes Requested Attempt 1 | DATABASE-001, ADMIN-002 |

### ADMIN-003 Attempt 1 review

ADMIN-003 is `Ready` for Attempt 2 after architect review found two database-bound correctness issues and one required validation/evidence gap:

- each `CommerceAuditEvent` row must use a distinct non-null `operationId` under the accepted unique index;
- Admin Platform/Shop prompt input is bounded to the accepted database limit of 32,000 characters;
- the pending-category publish/rollback path must pass the required real PostgreSQL integration proof, and the Completion Report must contain exact launcher/worktree synchronization evidence.

No dependent task is promoted by this review.

## Removed obsolete decomposition

The previous ARCH-023 Admin tasks for database-backed Store Category/template translations are obsolete. The current architecture uses source-controlled Shopify localization catalogues and contains no Admin translation queue/lifecycle for categories/templates.

## Execution frontier

DATABASE-001 and ADMIN-002 are Complete/accepted. ADMIN-002 Attempt 2 implemented the
Store Category/template/taxonomy catalogue against the corrected immutable-slug contract.
Therefore:

```text
ADMIN-003 -> Ready
```

ADMIN-003 must use the normal task preparation/claim path; this review does not start it
implicitly.

After DATABASE-001 and SHARED-002 are Complete/accepted:

```text
ADMIN-001 -> Ready
DATABASE-001 and SHARED-002 are Complete/accepted. The current independent Admin frontier is:

```text
ADMIN-001 -> Ready   # exact Shared revision: @modainteract/moda-interact-shared@1.0.1
ADMIN-002 -> Ready
```

After ADMIN-002 is Complete/accepted:

```text
ADMIN-003 -> Ready
```
