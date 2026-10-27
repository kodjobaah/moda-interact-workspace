# ARCH-050 Background Tasks

Architecture: [`ARCH-050`](../../../architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md).

Assigned Agent: `moda_background`.

Repository: `moda-interact-background`.

Coordinator: `moda_architect`.

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| [BACKGROUND-001](BACKGROUND-001-finalize-initial-attempt-and-write-deduplicated-support-notice.md) | Atomically sample preference and create a deduplicated first-outreach Support notice | Ready | ARCH-050-DATABASE-001 |
| [BACKGROUND-002](BACKGROUND-002-attach-shopify-initial-send-notice-finalization.md) | Wire Shopify initial-outreach confirmation to the common Support notice | Pending | ARCH-050-BACKGROUND-001 |
| [BACKGROUND-003](BACKGROUND-003-attach-woo-initial-send-notice-finalization.md) | Wire WooCommerce initial-outreach confirmation to the common Support notice | Pending | ARCH-050-BACKGROUND-001; ARCH-048-BACKGROUND-005 |

Individual task YAML is authoritative. The former test-suite stabilisation task was promoted to ARCH-051; it is not part of this notification initiative.
