# ARCH-040 System Test Tasks

Architecture: [ARCH-040-merchant-customer-conversations-human-handover](../../../architecture/ARCH-040-merchant-customer-conversations-human-handover.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.
Ready means implementation prerequisites are complete; system certification still requires explicit manual launch and a recorded passing result.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-040-SYSTEM-TEST-001](SYSTEM-TEST-001-certify-one-conversation-and-shared-follow-up-credit.md) | Certify one conversation and shared follow-up credit | ready | `ARCH-040-DATABASE-001`, `ARCH-040-BACKGROUND-002`, `ARCH-040-ADMIN-001`, `ARCH-040-DATABASE-005`, `ARCH-040-BACKGROUND-006`, `ARCH-040-BACKGROUND-007`, `ARCH-040-BACKGROUND-008`, `ARCH-040-BACKGROUND-009` |
| [ARCH-040-SYSTEM-TEST-002](SYSTEM-TEST-002-certify-shopify-customer-inbox-end-to-end.md) | Certify Shopify recovery-detail conversation and basket end-to-end | ready | `ARCH-040-SHOPIFY-001`, `ARCH-040-BACKGROUND-002`, `ARCH-040-BACKGROUND-006`, `ARCH-040-BACKGROUND-007`, `ARCH-040-BACKGROUND-008`, `ARCH-040-BACKGROUND-009`, `ARCH-040-SHOPIFY-004`, `ARCH-040-SHOPIFY-005` |
| [ARCH-040-SYSTEM-TEST-003](SYSTEM-TEST-003-certify-woo-customer-inbox-end-to-end.md) | Certify Woo recovery-detail conversation and basket end-to-end | ready | `ARCH-040-WOOCOMMERCE-001`, `ARCH-040-API-005`, `ARCH-040-BACKGROUND-002`, `ARCH-040-BACKGROUND-006`, `ARCH-040-BACKGROUND-007`, `ARCH-040-BACKGROUND-008`, `ARCH-040-BACKGROUND-009` |
