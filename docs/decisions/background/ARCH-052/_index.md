# ARCH-052 Background Tasks

Architecture: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`
Owner: `moda_background`
Coordinator: `moda_architect`

The individual task YAML is authoritative. BACKGROUND-009 is Complete; the other listed tasks remain governed by their own status and materialisation state. Superseded tasks must never be executed.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-052-BACKGROUND-001](BACKGROUND-001-snapshot-authorised-discount-policy-at-attempt.md) | Freeze effective selected-discount policy at initial attempt creation | Superseded | — |
| [ARCH-052-BACKGROUND-002](BACKGROUND-002-discover-bounded-offer-candidates.md) | Discover all relevant catalogue candidates with bounded pagination | Superseded | — |
| [ARCH-052-BACKGROUND-003](BACKGROUND-003-connect-shopify-woo-live-eligibility-providers.md) | Wire independent Shopify and Woo checkout-specific eligibility adapters | Superseded | — |
| [ARCH-052-BACKGROUND-004](BACKGROUND-004-wire-bounded-ai-offer-selector.md) | Connect approved AI recommendation to verified offer shortlist | Superseded | — |
| [ARCH-052-BACKGROUND-005](BACKGROUND-005-bind-basket-summary-and-merchant-context.md) | Bind deterministic basket summary and merchant category for initial outreach | Ready | `ARCH-052-SHARED-003` |
| [ARCH-052-BACKGROUND-006](BACKGROUND-006-resolve-fresh-woo-resume-checkout-links.md) | Resolve fresh authenticated Woo restore links at initial send preparation | Superseded | — |
| [ARCH-052-BACKGROUND-007](BACKGROUND-007-resolve-verified-product-image-at-runtime.md) | Resolve optional checkout or promoted-product image via MCP at runtime | Pending | `ARCH-052-BACKGROUND-008`, `ARCH-052-ADMIN-002`, `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-007`, `ARCH-049-BACKGROUND-001`, `ARCH-049-BACKGROUND-004` |
| [ARCH-052-BACKGROUND-008](BACKGROUND-008-integrate-three-modes-into-initial-whatsapp-send.md) | Bind approved outreach variants and existing checkoutUrl via current send pipeline | Complete | `ARCH-052-SHARED-012`, `ARCH-052-ADMIN-003`, `ARCH-052-BACKGROUND-010`, `ARCH-052-BACKGROUND-005`, `ARCH-052-ADMIN-001`, `ARCH-052-BACKGROUND-015`, `ARCH-052-BACKGROUND-016` |
| [ARCH-052-BACKGROUND-009](BACKGROUND-009-preserve-shopify-merchant-selection-during-sync.md) | Make Shopify catalogue and lifecycle writers preserve merchant selection | Complete | — |
| [ARCH-052-BACKGROUND-010](BACKGROUND-010-implement-langgraph-initial-outreach-offer-agent.md) | Implement the LangGraph InitialOutreachOfferAgent with existing MCP tools | Complete | `ARCH-052-SHARED-012`, `ARCH-052-MCP-002`, `ARCH-052-COMMERCE-007`, `ARCH-052-SHARED-010`, `ARCH-052-SHARED-014`, `ARCH-052-BACKGROUND-016` |
| [ARCH-052-BACKGROUND-011](BACKGROUND-011-enrich-shopify-discount-catalogue-condition-facts.md) | Enrich source-backed Shopify discount condition facts | Complete | `ARCH-052-BACKGROUND-009`, `ARCH-052-SHARED-010` |
| [ARCH-052-BACKGROUND-012](BACKGROUND-012-upload-trusted-meta-image-template-sample.md) | Upload fixed Moda sample to Meta and attach a returned handle only in the provider IMAGE create request | Ready | `ARCH-052-ADMIN-002`, `ARCH-047-BACKGROUND-003` |
| [ARCH-052-BACKGROUND-013](BACKGROUND-013-capture-complete-shopify-combination-identities.md) | Capture Shopify discount classes and own combination tags | Complete | `ARCH-052-BACKGROUND-011` |

BACKGROUND-009's repository-wide validation reconciliation is complete; its task record remains authoritative for the review evidence.

BACKGROUND-011 is Complete after the accepted Attempt 6 error-diagnostics correction. BACKGROUND-013 is Complete after the accepted Attempt 1 implementation; MCP-002 remains Pending until its other upstream dependencies are complete.
