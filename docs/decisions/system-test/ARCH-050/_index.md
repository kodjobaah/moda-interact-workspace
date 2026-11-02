# ARCH-050 System Test Tasks

Architecture: [ARCH-050-merchant-recovery-initial-outreach-support-notifications](../../../architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.
Ready means implementation prerequisites are complete; system certification still requires explicit manual launch and a recorded passing result.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-050-SYSTEM-TEST-001](SYSTEM-TEST-001-verify-shopify-initial-recovery-support-notices.md) | Verify Shopify opt-in initial outreach Support notification end to end | ready | `ARCH-050-BACKGROUND-002`, `ARCH-050-SHOPIFY-001`, `ARCH-050-SHOPIFY-002` |
| [ARCH-050-SYSTEM-TEST-002](SYSTEM-TEST-002-verify-woo-initial-recovery-support-notices.md) | Verify WooCommerce test-mode initial outreach Support notification end to end | ready | `ARCH-050-BACKGROUND-003`, `ARCH-050-API-001`, `ARCH-050-API-002`, `ARCH-050-WOOCOMMERCE-001`, `ARCH-050-WOOCOMMERCE-002`, `ARCH-048-WOOCOMMERCE-002`, `ARCH-048-WOOCOMMERCE-003` |
