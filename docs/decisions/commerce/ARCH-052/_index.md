# ARCH-052 Commerce Tasks

Architecture: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`
Owner: `moda_commerce`
Coordinator: `moda_architect`

Individual task YAML frontmatter is authoritative; this index reflects the current task state. Superseded tasks must never be executed.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-052-COMMERCE-001](COMMERCE-001-verify-shopify-discount-against-current-checkout.md) | Prove Shopify discount eligibility for a recovery checkout | Ready | — |
| [ARCH-052-COMMERCE-002](COMMERCE-002-read-authoritative-shopify-checkout-product-image.md) | Read first checkout-product image from Shopify product facts | Superseded | — |
| [ARCH-052-COMMERCE-003](COMMERCE-003-serve-authenticated-private-shopify-recovery-reads.md) | Serve authenticated private Shopify checkout and alternative-product discount proof | Pending | `ARCH-052-COMMERCE-001`, `ARCH-052-COMMERCE-008`, `ARCH-052-SHARED-003` |
| [ARCH-052-COMMERCE-004](COMMERCE-004-author-published-discount-mcp-tools.md) | Author version-2 discount MCP tool definitions in Commerce Studio | Superseded | — |
| [ARCH-052-COMMERCE-005](COMMERCE-005-publish-approved-mcp-discount-capabilities.md) | Publish approved version-2 discount MCP capabilities in TEST | Superseded | — |
| [ARCH-052-COMMERCE-006](COMMERCE-006-bootstrap-product-search-and-get-product-tools.md) | Bootstrap version-controlled product search and exact-product MCP tool definitions | Complete | `ARCH-052-SHARED-010` |
| [ARCH-052-COMMERCE-007](COMMERCE-007-publish-code-defined-product-tool-release.md) | Publish reviewed code-defined product tools to the TEST Commerce release | Ready | `ARCH-052-COMMERCE-006`, `ARCH-052-MCP-003` |
| [ARCH-052-COMMERCE-008](COMMERCE-008-verify-shopify-alternative-product-promotion.md) | Verify Shopify discounts for a specific recommended product without checkout mutation | Pending | `ARCH-052-COMMERCE-001`, `ARCH-052-SHARED-003` |
