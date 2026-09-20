# ARCH-019 shopify tasks

Architecture: [ARCH-019](../../../architecture/ARCH-019-merchant-recovery-experience.md).

Coordinator: moda_architect. Individual task YAML and canonical task worktrees are authoritative.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-019-SHOPIFY-001](SHOPIFY-001-bounded-recovery-cohort-readers.md) | Implement bounded recovery cohort metrics and list readers | Complete | ARCH-019-DATABASE-001 |
| [ARCH-019-SHOPIFY-002](SHOPIFY-002-bounded-recovery-detail-readers.md) | Implement tenant-scoped recovery detail and transcript readers | In Progress | ARCH-019-DATABASE-001 |
| [ARCH-019-SHOPIFY-003](SHOPIFY-003-recovery-list-page.md) | Build the recovery browsing page and guarded route | Ready | ARCH-019-SHOPIFY-001 |
| [ARCH-019-SHOPIFY-004](SHOPIFY-004-recovery-conversation-detail-page.md) | Build the read-only recovery conversation page | Pending | ARCH-019-SHOPIFY-002, ARCH-019-SHOPIFY-003 |
| [ARCH-019-SHOPIFY-005](SHOPIFY-005-recovery-performance-overview.md) | Replace the usage-first home page with the recovery overview | Pending | ARCH-019-SHOPIFY-001, ARCH-019-SHOPIFY-003, ARCH-019-SHOPIFY-004 |
| [ARCH-019-SHOPIFY-006](SHOPIFY-006-merchant-navigation-and-billing-history.md) | Align merchant navigation and bounded billing-history access | Pending | ARCH-019-SHOPIFY-005 |

Current frontier: DATABASE-001 and SHOPIFY-001 accepted/Complete. SHOPIFY-002 In Progress at Attempt 2; SHOPIFY-003 Ready at Attempt 0. SHOPIFY-004/005/006 and SYSTEM-TEST-001 remain Pending. Accepted dependency metadata is reconciled into the newly Ready task worktree. The developer authorized publication of these review updates on the matching parent task branches on 2026-09-20. Readiness does not launch execution or authorize prerequisite integration.
