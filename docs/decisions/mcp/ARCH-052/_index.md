# ARCH-052 Mcp Tasks

Architecture: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`
Owner: `moda_mcp`
Coordinator: `moda_architect`

Task materialisation and current status are recorded in each task YAML frontmatter; several MCP tasks are portable definitions while MCP-003 and MCP-005 have materialised task branches. Superseded tasks must never be executed.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-052-MCP-001](MCP-001-authorize-initial-recovery-outreach-tool-context.md) | Authorize shop- and purpose-scoped discount and published product tools | Complete | `ARCH-052-SHARED-003` |
| [ARCH-052-MCP-002](MCP-002-execute-published-discount-options-and-proof.md) | Execute built-in discount discovery and checkout proof in MCP | Pending | `ARCH-052-SHARED-012`, `ARCH-052-BACKGROUND-013`, `ARCH-052-BACKGROUND-014`, `ARCH-052-MCP-001`, `ARCH-052-SHARED-010`, `ARCH-052-BACKGROUND-011`, `ARCH-052-SHARED-014` |
| [ARCH-052-MCP-003](MCP-003-direct-provider-product-search-and-exact-read.md) | Execute Shopify and WooCommerce product search directly inside MCP | Complete | `ARCH-052-SHARED-010`, `ARCH-052-COMMERCE-006`, `ARCH-052-MCP-005` |
| [ARCH-052-MCP-004](MCP-004-verify-alternative-product-discount-promotions.md) | Verify alternate product promotions using existing MCP provider proof | Pending | `ARCH-052-MCP-001`, `ARCH-052-MCP-002`, `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-008`, `ARCH-052-WOOCOMMERCE-001` |
| [ARCH-052-MCP-005](MCP-005-implement-direct-woocommerce-rest-product-reader.md) | Implement secure direct WooCommerce product REST reader | Complete | — |
| [ARCH-052-MCP-006](MCP-006-preserve-original-woo-provider-errors.md) | Preserve original WooCommerce REST and transport errors in MCP logs | Complete | `ARCH-052-MCP-005` |
