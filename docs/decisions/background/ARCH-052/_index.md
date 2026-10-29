# ARCH-052 Background Tasks

Architecture: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`
Owner: `moda_background`
Coordinator: `moda_architect`

These are portable task definitions, **defined but not materialised**; the individual task YAML frontmatter is authoritative. Superseded tasks must never be executed.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-052-BACKGROUND-001](BACKGROUND-001-snapshot-authorised-discount-policy-at-attempt.md) | Freeze effective selected-discount policy at initial attempt creation | Superseded | — |
| [ARCH-052-BACKGROUND-002](BACKGROUND-002-discover-bounded-offer-candidates.md) | Discover all relevant catalogue candidates with bounded pagination | Superseded | — |
| [ARCH-052-BACKGROUND-003](BACKGROUND-003-connect-shopify-woo-live-eligibility-providers.md) | Wire independent Shopify and Woo checkout-specific eligibility adapters | Superseded | — |
| [ARCH-052-BACKGROUND-004](BACKGROUND-004-wire-bounded-ai-offer-selector.md) | Connect approved AI recommendation to verified offer shortlist | Superseded | — |
| [ARCH-052-BACKGROUND-005](BACKGROUND-005-bind-basket-summary-and-merchant-context.md) | Bind deterministic basket summary and merchant category for initial outreach | Pending | `ARCH-052-SHARED-003` |
| [ARCH-052-BACKGROUND-006](BACKGROUND-006-resolve-fresh-woo-resume-checkout-links.md) | Resolve fresh authenticated Woo restore links at initial send preparation | Superseded | — |
| [ARCH-052-BACKGROUND-007](BACKGROUND-007-resolve-verified-product-image-at-runtime.md) | Resolve optional checkout or promoted-product image via MCP at runtime | Pending | `ARCH-052-SHARED-003`, `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-007`, `ARCH-049-BACKGROUND-001`, `ARCH-049-BACKGROUND-004` |
| [ARCH-052-BACKGROUND-008](BACKGROUND-008-integrate-three-modes-into-initial-whatsapp-send.md) | Bind approved outreach variants and existing checkoutUrl via current send pipeline | Pending | `ARCH-052-BACKGROUND-010`, `ARCH-052-BACKGROUND-005`, `ARCH-052-BACKGROUND-007`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002`, `ARCH-052-GATEWAY-001` |
| [ARCH-052-BACKGROUND-009](BACKGROUND-009-preserve-shopify-merchant-selection-during-sync.md) | Make Shopify catalogue and lifecycle writers preserve merchant selection | Ready | — |
| [ARCH-052-BACKGROUND-010](BACKGROUND-010-implement-langgraph-initial-outreach-offer-agent.md) | Implement the LangGraph InitialOutreachOfferAgent with existing MCP tools | Pending | `ARCH-052-MCP-002`, `ARCH-052-MCP-004`, `ARCH-052-COMMERCE-007`, `ARCH-052-SHARED-003` |
