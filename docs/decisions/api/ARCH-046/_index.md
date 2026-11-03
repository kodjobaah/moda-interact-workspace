# ARCH-046 Api Tasks

Architecture: [ARCH-046-woocommerce-whatsapp-consent-gated-recovery](../../../architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-046-API-001](API-001-accept-authenticated-woo-consent-changes.md) | Accept verified Woo customer-phone consent changes | complete | `ARCH-045-DATABASE-002`, `ARCH-045-SHARED-002` |
| [ARCH-046-API-002](API-002-expose-woo-merchant-consent-support-notices.md) | Expose Woo merchant Support system notices read-only | superseded | — |
| [ARCH-046-API-003](API-003-manage-woocommerce-consent-collection-source.md) | Manage consent source on existing WooCommerceInstallation | superseded | — |
| [ARCH-046-API-004](API-004-handle-woo-customer-privacy-requests.md) | Handle authenticated WooCommerce consent privacy export and erasure | superseded | — |
| [ARCH-046-API-005](API-005-record-woo-merchant-contact-opt-outs.md) | Manage merchant recovery suppression for Woo customers | complete | `ARCH-045-DATABASE-002` |
| [ARCH-046-API-006](API-006-read-proof-backed-woo-whatsapp-consent-status.md) | Read current Woo WhatsApp consent using acknowledged shopper-bound grant evidence | ready | `ARCH-046-API-007`, `ARCH-045-DATABASE-002`, `ARCH-045-SHARED-002` |
| [ARCH-046-API-007](API-007-make-woo-consent-write-api-thin.md) | Make the Woo WhatsApp consent write API a thin, bounded persistence boundary | complete | `ARCH-046-API-001`, `ARCH-045-DATABASE-002`, `ARCH-045-SHARED-002` |
