# ARCH-023 shopify tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md).

Assigned agent: `moda_app`. Repository: `moda-interact`. Coordinator: `moda_architect`.

These are portable task definitions from the 2026-09-27 review patch; individual task YAML is authoritative. No task branch/worktree is materialised by this patch.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [SHOPIFY-001](SHOPIFY-001-gate-managed-pricing-store-category.md) | Gate Managed Pricing with Store Category | Pending | DATABASE-002, SHARED-004 |
| [SHOPIFY-002](SHOPIFY-002-support-post-onboarding-store-category-changes.md) | Support later Store Category changes | Pending | SHOPIFY-001, DATABASE-002, SHARED-004 |
| [SHOPIFY-003](SHOPIFY-003-persist-queue-merchant-knowledge.md) | Persist/queue Merchant Knowledge | Pending | DATABASE-001, DATABASE-003, SHARED-004 |
| [SHOPIFY-004](SHOPIFY-004-build-merchant-knowledge-settings-ui.md) | Build Merchant Knowledge settings UI | Pending | SHOPIFY-003 |

## Execution frontier

Ready: None.
