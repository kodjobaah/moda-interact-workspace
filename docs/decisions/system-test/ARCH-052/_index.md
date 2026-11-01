# ARCH-052 System Test Tasks

Architecture: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`
Owner: `moda_system_test`
Coordinator: `moda_architect`

These are portable task definitions, **defined but not materialised**; the individual task YAML frontmatter is authoritative. Superseded tasks must never be executed. SYSTEM-TEST-001 and SYSTEM-TEST-002 include `ARCH-052-BACKGROUND-012` for Meta IMAGE sample upload/approval.

| Task | Bounded outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-052-SYSTEM-TEST-001](SYSTEM-TEST-001-certify-shopify-initial-outreach-modes.md) | Certify Shopify initial outreach personalization and all offer modes | Pending | `ARCH-052-BACKGROUND-008`, `ARCH-052-SHOPIFY-001`, `ARCH-052-BACKGROUND-009`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002`, `ARCH-052-SHARED-003`, `ARCH-052-MCP-001`, `ARCH-052-MCP-002`, `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-006`, `ARCH-052-COMMERCE-007`, `ARCH-052-BACKGROUND-010`, `ARCH-052-GATEWAY-001`, `ARCH-052-SHARED-010`, `ARCH-052-BACKGROUND-007`, `ARCH-052-BACKGROUND-012`, `ARCH-052-BACKGROUND-011` |
| [ARCH-052-SYSTEM-TEST-002](SYSTEM-TEST-002-certify-woocommerce-initial-outreach-modes.md) | Certify Woo initial outreach, MCP product facts and stored checkout CTA | Pending | `ARCH-052-BACKGROUND-008`, `ARCH-052-GATEWAY-001`, `ARCH-052-ADMIN-001`, `ARCH-052-ADMIN-002`, `ARCH-052-SHARED-003`, `ARCH-052-MCP-001`, `ARCH-052-MCP-002`, `ARCH-052-MCP-003`, `ARCH-052-COMMERCE-006`, `ARCH-052-COMMERCE-007`, `ARCH-052-BACKGROUND-010`, `ARCH-052-SHARED-010`, `ARCH-052-BACKGROUND-007`, `ARCH-052-BACKGROUND-012` |
| [ARCH-052-SYSTEM-TEST-003](SYSTEM-TEST-003-certify-shared-sender-contextual-replies.md) | Certify exact quoted-message text and voice routing across merchants | Ready | `ARCH-052-BACKGROUND-015`, `ARCH-052-BACKGROUND-008`, `ARCH-052-ADMIN-003`, `ARCH-012-MESSAGING-001`, `ARCH-040-BACKGROUND-002`, `ARCH-045-BACKGROUND-005` |
| [ARCH-052-SYSTEM-TEST-004](SYSTEM-TEST-004-certify-mandatory-initial-checkout-items.md) | Certify mandatory initial checkout-items binding | Pending | `ARCH-052-ADMIN-004`, `ARCH-052-BACKGROUND-017`, `ARCH-052-BACKGROUND-008`, `ARCH-052-BACKGROUND-007`, `ARCH-052-BACKGROUND-005` |
