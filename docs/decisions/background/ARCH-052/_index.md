# ARCH-052 Background Tasks

Architecture: [ARCH-052-checkout-personalised-initial-whatsapp-outreach](../../../architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-052-BACKGROUND-001](BACKGROUND-001-snapshot-authorised-discount-policy-at-attempt.md) | Freeze effective selected-discount policy at initial attempt creation | superseded | — |
| [ARCH-052-BACKGROUND-002](BACKGROUND-002-discover-bounded-offer-candidates.md) | Discover all relevant catalogue candidates with bounded pagination | superseded | — |
| [ARCH-052-BACKGROUND-003](BACKGROUND-003-connect-shopify-woo-live-eligibility-providers.md) | Wire independent Shopify and Woo checkout-specific eligibility adapters | superseded | — |
| [ARCH-052-BACKGROUND-004](BACKGROUND-004-wire-bounded-ai-offer-selector.md) | Connect approved AI recommendation to verified offer shortlist | superseded | — |
| [ARCH-052-BACKGROUND-005](BACKGROUND-005-bind-basket-summary-and-merchant-context.md) | Bind deterministic basket summary and merchant category for initial outreach | complete | `ARCH-052-SHARED-003` |
| [ARCH-052-BACKGROUND-006](BACKGROUND-006-resolve-fresh-woo-resume-checkout-links.md) | Resolve fresh authenticated Woo restore links at initial send preparation | superseded | — |
| [ARCH-052-BACKGROUND-007](BACKGROUND-007-resolve-verified-product-image-at-runtime.md) | Resolve optional checkout or promoted-product image via MCP at runtime | complete | `ARCH-052-BACKGROUND-008`, `ARCH-052-ADMIN-002`, `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-007`, `ARCH-049-BACKGROUND-001`, `ARCH-049-BACKGROUND-004` |
| [ARCH-052-BACKGROUND-008](BACKGROUND-008-integrate-three-modes-into-initial-whatsapp-send.md) | Send approved checkout or alternative-product promotion via existing initial outreach | complete | `ARCH-052-SHARED-012`, `ARCH-052-ADMIN-003`, `ARCH-052-BACKGROUND-010`, `ARCH-052-BACKGROUND-005`, `ARCH-052-ADMIN-001`, `ARCH-052-BACKGROUND-015`, `ARCH-052-BACKGROUND-016` |
| [ARCH-052-BACKGROUND-009](BACKGROUND-009-preserve-shopify-merchant-selection-during-sync.md) | Make Shopify catalogue and lifecycle writers preserve merchant selection | complete | — |
| [ARCH-052-BACKGROUND-010](BACKGROUND-010-implement-langgraph-initial-outreach-offer-agent.md) | Implement the LangGraph InitialOutreachOfferAgent with existing MCP tools | complete | `ARCH-052-SHARED-012`, `ARCH-052-MCP-002`, `ARCH-052-COMMERCE-007`, `ARCH-052-SHARED-010`, `ARCH-052-SHARED-014`, `ARCH-052-BACKGROUND-016` |
| [ARCH-052-BACKGROUND-011](BACKGROUND-011-enrich-shopify-discount-catalogue-condition-facts.md) | Enrich Shopify discount catalogue with source-backed targeting facts | complete | `ARCH-052-BACKGROUND-009`, `ARCH-052-SHARED-010` |
| [ARCH-052-BACKGROUND-012](BACKGROUND-012-upload-trusted-meta-image-template-sample.md) | Upload a controlled IMAGE sample for Meta template submission | complete | `ARCH-052-ADMIN-002`, `ARCH-047-BACKGROUND-003` |
| [ARCH-052-BACKGROUND-013](BACKGROUND-013-capture-complete-shopify-combination-identities.md) | Capture Shopify discount classes and own combination tags | complete | `ARCH-052-BACKGROUND-011` |
| [ARCH-052-BACKGROUND-014](BACKGROUND-014-preserve-woo-coupon-restriction-presence-facts.md) | Preserve WooCommerce coupon restriction presence without personal data | complete | — |
| [ARCH-052-BACKGROUND-015](BACKGROUND-015-route-contextual-recovery-text-voice-and-guidance.md) | Enforce shared-sender contextual recovery replies and accurate text/voice guidance | complete | `ARCH-012-MESSAGING-001`, `ARCH-040-BACKGROUND-002`, `ARCH-045-BACKGROUND-005` |
| [ARCH-052-BACKGROUND-016](BACKGROUND-016-reconcile-current-product-prices-before-outreach.md) | Reconcile observed checkout prices with current exact-product catalogue facts | complete | `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-007`, `ARCH-052-BACKGROUND-005` |
| [ARCH-052-BACKGROUND-017](BACKGROUND-017-enforce-initial-checkout-items-at-send.md) | Enforce mandatory checkout-summary BODY binding in every initial Meta send | complete | `ARCH-052-ADMIN-004`, `ARCH-052-BACKGROUND-008`, `ARCH-052-BACKGROUND-007`, `ARCH-052-BACKGROUND-005` |
| [ARCH-052-BACKGROUND-018](BACKGROUND-018-guarantee-initial-no-offer-text-after-enrichment-failure.md) | Guarantee approved no-offer TEXT outreach after optional enrichment failures | complete | `ARCH-052-BACKGROUND-008`, `ARCH-052-ADMIN-004`, `ARCH-052-BACKGROUND-005` |
