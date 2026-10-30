# ARCH-052 Mcp Tasks

Architecture: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`
Owner: `moda_mcp`
Coordinator: `moda_architect`

These are portable task definitions, **defined but not materialised**; the individual task YAML frontmatter is authoritative. Superseded tasks must never be executed.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-052-MCP-001](MCP-001-authorize-initial-recovery-outreach-tool-context.md) | Authorize shop- and purpose-scoped discount and published product tools | Ready | `ARCH-052-SHARED-003` |
| [ARCH-052-MCP-002](MCP-002-execute-published-discount-options-and-proof.md) | Execute built-in discount discovery and checkout proof in MCP | Pending | `ARCH-052-MCP-001`, `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-003`, `ARCH-052-WOOCOMMERCE-001`, `ARCH-052-GATEWAY-001`, `ARCH-052-SHARED-003` |
| [ARCH-052-MCP-003](MCP-003-direct-provider-product-search-and-exact-read.md) | Execute Shopify and WooCommerce product search directly inside MCP | Pending | `ARCH-052-SHARED-003`, `ARCH-052-COMMERCE-006` |
| [ARCH-052-MCP-004](MCP-004-verify-alternative-product-discount-promotions.md) | Verify alternate product promotions using existing MCP provider proof | Pending | `ARCH-052-MCP-001`, `ARCH-052-MCP-002`, `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-008`, `ARCH-052-WOOCOMMERCE-001` |
