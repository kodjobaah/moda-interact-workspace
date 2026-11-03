# ARCH-046 Woocommerce Tasks

Architecture: [ARCH-046-woocommerce-whatsapp-consent-gated-recovery](../../../architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-046-WOOCOMMERCE-001](WOOCOMMERCE-001-render-optional-woo-whatsapp-recovery-opt-in.md) | Register Moda Woo consent checkbox and Recovery Settings guidance | complete | — |
| [ARCH-046-WOOCOMMERCE-002](WOOCOMMERCE-002-capture-pre-submit-woo-consent-and-publish-to-moda.md) | Capture affirmative pre-submit Woo consent and publish durable evidence | complete | `ARCH-035-WOOCOMMERCE-007`, `ARCH-046-API-001`, `ARCH-046-WOOCOMMERCE-001` |
| [ARCH-046-WOOCOMMERCE-003](WOOCOMMERCE-003-allow-later-consent-on-returning-woo-checkout.md) | Complete returning Woo consent, v2 publishing and verified checkout status | in_progress | `ARCH-046-WOOCOMMERCE-002` |
| [ARCH-046-WOOCOMMERCE-004](WOOCOMMERCE-004-show-readonly-woo-merchant-support-notices.md) | Display authenticated consent-related merchant Support system notices | superseded | `ARCH-046-API-002` |
| [ARCH-046-WOOCOMMERCE-005](WOOCOMMERCE-005-explain-woo-consent-in-recovery-settings.md) | Configure Woo consent source and explain recovery eligibility in Recovery Settings | superseded | — |
| [ARCH-046-WOOCOMMERCE-006](WOOCOMMERCE-006-connect-wp-customer-privacy-hooks.md) | Connect WordPress personal data export and erase to Moda hosted consent | superseded | — |
| [ARCH-046-WOOCOMMERCE-007](WOOCOMMERCE-007-merchant-recorded-whatsapp-opt-outs.md) | Manage merchant Woo customer recovery selection | complete | `ARCH-046-API-005`, `ARCH-035-WOOCOMMERCE-016` |
