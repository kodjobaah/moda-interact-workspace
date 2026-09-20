# ARCH-019 shopify tasks

Architecture: [ARCH-019](../../../architecture/ARCH-019-merchant-recovery-experience.md).

Coordinator: moda_architect. Individual task YAML and canonical task worktrees are authoritative.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-019-SHOPIFY-001](SHOPIFY-001-bounded-recovery-cohort-readers.md) | Implement bounded recovery cohort metrics and list readers | Ready | ARCH-019-DATABASE-001 |
| [ARCH-019-SHOPIFY-002](SHOPIFY-002-bounded-recovery-detail-readers.md) | Implement tenant-scoped recovery detail and transcript readers | Ready | ARCH-019-DATABASE-001 |
| [ARCH-019-SHOPIFY-003](SHOPIFY-003-recovery-list-page.md) | Build the recovery browsing page and guarded route | Pending | ARCH-019-SHOPIFY-001 |
| [ARCH-019-SHOPIFY-004](SHOPIFY-004-recovery-conversation-detail-page.md) | Build the read-only recovery conversation page | Pending | ARCH-019-SHOPIFY-002, ARCH-019-SHOPIFY-003 |
| [ARCH-019-SHOPIFY-005](SHOPIFY-005-recovery-performance-overview.md) | Replace the usage-first home page with the recovery overview | Pending | ARCH-019-SHOPIFY-001, ARCH-019-SHOPIFY-003, ARCH-019-SHOPIFY-004 |
| [ARCH-019-SHOPIFY-006](SHOPIFY-006-merchant-navigation-and-billing-history.md) | Align merchant navigation and bounded billing-history access | Pending | ARCH-019-SHOPIFY-005 |

No implementation has started. System tests are terminal and developer-invoked.

SHOPIFY-002: Changes Requested on Attempt 1; Ready for correction of PostgreSQL harness timestamp semantics and required plan evidence. See canonical task review. SHOPIFY-004 remains gated.
