# ARCH-050 Background Tasks

Architecture: [ARCH-050-merchant-recovery-initial-outreach-support-notifications](../../../architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md).

Reconciled on 2026-11-02. Individual task frontmatter and review reports are authoritative. Superseded tasks must not be executed.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [ARCH-050-BACKGROUND-001](BACKGROUND-001-finalize-initial-attempt-and-write-deduplicated-support-notice.md) | Atomically sample preference and create a deduplicated first-outreach Support notice | complete | `ARCH-050-DATABASE-001` |
| [ARCH-050-BACKGROUND-002](BACKGROUND-002-attach-shopify-initial-send-notice-finalization.md) | Wire Shopify automated initial-outreach confirmation to the common Support notice | complete | `ARCH-050-BACKGROUND-001` |
| [ARCH-050-BACKGROUND-003](BACKGROUND-003-attach-woo-initial-send-notice-finalization.md) | Wire WooCommerce confirmed initial outreach to the common Support notice | complete | `ARCH-050-BACKGROUND-001`, `ARCH-048-BACKGROUND-005` |
