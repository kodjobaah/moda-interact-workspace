# ARCH-053 — api tasks

Architecture: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`

Assigned agent: `moda_api`. Coordinator: `moda_architect`.

Task YAML is authoritative; this index reflects the reconciled dependency frontier.

| Task | Purpose | Status | Depends On |
|---|---|---|---|
| [ARCH-053-API-001](API-001-accept-woo-cart-restoration-checkout-events.md) | Extend canonical Woo activity v1 with restoration and verified phone | Complete | ARCH-053-SHARED-002 |
| [ARCH-053-API-002](API-002-resolve-generation-bound-woo-checkout-link.md) | Resolve Woo recovery link with installation and generation authorization | Complete | ARCH-053-SHARED-002, ARCH-053-DATABASE-001 |
| [ARCH-053-API-003](API-003-resolve-confirmed-initial-outreach-offer.md) | Resolve confirmed initial outreach offer in Woo restore response v1 | Pending | ARCH-053-API-002, ARCH-053-SHARED-002, ARCH-053-BACKGROUND-004 |

ARCH-052 is separately owned dynamic-discount discovery; no checkout restoration tasks are to be implemented under ARCH-052.
