# ARCH-046 System Test Tasks

Architecture: [ARCH-046-woocommerce-whatsapp-consent-gated-recovery](../../../architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.
Ready means implementation prerequisites are complete; system certification still requires explicit manual launch and a recorded passing result.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-046-SYSTEM-TEST-001](SYSTEM-TEST-001-certify-woo-precheckout-opt-in-capture.md) | Certify Woo pre-submission WhatsApp consent capture on LocalWP | pending | `ARCH-045-DATABASE-002`, `ARCH-046-API-001`, `ARCH-046-API-006`, `ARCH-046-WOOCOMMERCE-001`, `ARCH-046-WOOCOMMERCE-002`, `ARCH-046-WOOCOMMERCE-003`, `ARCH-045-SHARED-002`, `ARCH-045-BACKGROUND-005`, `ARCH-046-API-005`, `ARCH-046-WOOCOMMERCE-007` |
| [ARCH-046-SYSTEM-TEST-002](SYSTEM-TEST-002-certify-woo-consent-block-notice-and-resume.md) | Certify Woo consent-gated first recovery creation and later opt-in | blocked | `ARCH-045-DATABASE-002`, `ARCH-046-API-001`, `ARCH-046-API-006`, `ARCH-035-API-020`, `ARCH-046-WOOCOMMERCE-002`, `ARCH-046-WOOCOMMERCE-003`, `ARCH-035-WOOCOMMERCE-016`, `ARCH-046-BACKGROUND-001`, `ARCH-046-BACKGROUND-002`, `ARCH-046-BACKGROUND-004`, `ARCH-045-SHARED-002`, `ARCH-045-BACKGROUND-005`, `ARCH-046-API-005`, `ARCH-046-WOOCOMMERCE-007`, `ARCH-048-BACKGROUND-003`, `ARCH-048-BACKGROUND-004`, `ARCH-048-BACKGROUND-005`, `ARCH-048-WOOCOMMERCE-002`, `ARCH-048-WOOCOMMERCE-003` |
