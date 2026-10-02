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
| [ADMIN-004](ADMIN-004-make-merchant-knowledge-merchant-opt-in.md) | Reconcile Merchant Knowledge Feature to `MERCHANT_OPT_IN` without seeding per-shop preferences | Complete — Accepted Attempt 1 | ADMIN-001 |
| [ADMIN-002](ADMIN-002-manage-store-categories-default-templates.md) | Store Category, canonical-English default templates and Shopify taxonomy mappings | Complete — Accepted Attempt 2 | DATABASE-001 |
| [ADMIN-003](ADMIN-003-author-platform-shop-instructions.md) | Platform/Shop prompt draft, publish, activation and pending-category promotion | Complete — Accepted Attempt 3 | DATABASE-001, ADMIN-002 |

### ADMIN-003 Attempt 1 review

ADMIN-003 is `Ready` for Attempt 2 after architect review found two database-bound correctness issues and one required validation/evidence gap:

- each `CommerceAuditEvent` row must use a distinct non-null `operationId` under the accepted unique index;
- Admin Platform/Shop prompt input is bounded to the accepted database limit of 32,000 characters;
- the pending-category publish/rollback path must pass the required real PostgreSQL integration proof, and the Completion Report must contain exact launcher/worktree synchronization evidence.

No dependent task is promoted by this review.

### ADMIN-003 Attempt 2 review

Attempt 2 closes the prior audit-operation-ID, 32,000-character bound, real-PostgreSQL
promotion proof and worktree-evidence corrections. A remaining snapshot-provenance defect
keeps ADMIN-003 `Ready` for Attempt 3: the Admin read/publish paths must not compare a
pending revision's `sourceTemplateId` to the category's current `defaultTemplateId`.
The pending DRAFT remains the authoritative selection-time snapshot even if the category
default changes later. Attempt 3 is limited to that correction, its focused regressions
and the corresponding disposable-PostgreSQL proof.

No dependent task is promoted by this review.

### ADMIN-003 Attempt 3 review

Attempt 3 is Accepted. The Admin read/publish paths now treat `sourceTemplateId` and
`sourceTemplateEditVersion` as selection-time snapshot provenance: changing a Store Category's
current default template from A to B no longer invalidates, rewrites or reseeds the exact pending
DRAFT. Focused regressions and the disposable-PostgreSQL proof cover the A-to-B case plus stale
configuration/profile rollback.

ADMIN-003 is Complete. Its completion satisfies the final dependency of
`ARCH-023-COMMERCE-003`, which is promoted to Ready without being started.

## Removed obsolete decomposition

The previous ARCH-023 Admin tasks for database-backed Store Category/template translations are obsolete. The current architecture uses source-controlled Shopify localization catalogues and contains no Admin translation queue/lifecycle for categories/templates.

## Execution frontier

The authoritative Admin task state after ADMIN-004 Attempt 1 acceptance is:

```text
ADMIN-001 -> Complete — Accepted Attempt 2
ADMIN-002 -> Complete — Accepted Attempt 2
ADMIN-003 -> Complete — Accepted Attempt 3
ADMIN-004 -> Complete — Accepted Attempt 1
```

ADMIN-003 completion promotes `ARCH-023-COMMERCE-003` to Ready because its other declared
prerequisites, DATABASE-001 and SHARED-002, are already Complete. No Commerce implementation is
started implicitly by this review.

## Merchant opt-in reconciliation

`ADMIN-004` is a bounded follow-up to accepted ADMIN-001. It does not rewrite ADMIN-001 history; it transitions the fixed `merchant_knowledge` Feature from the previously accepted `ALWAYS_ENABLED` state to the final `MERCHANT_OPT_IN` state.

### ADMIN-004 Attempt 1 review

Attempt 1 is Accepted. The fixed `merchant_knowledge` Feature is reconciled from the exact previously accepted `ALWAYS_ENABLED` state to `MERCHANT_OPT_IN` through the existing authenticated Merchant Pricing Plan transaction, with one normal audit event and no per-shop preference seeding. Already-target state is idempotent and conflicting states fail closed.

ADMIN-004 completion promotes `ARCH-023-SHOPIFY-004` and `ARCH-023-BACKGROUND-006` to Ready. `ARCH-023-COMMERCE-004` remains Pending until COMMERCE-002 is Complete.
