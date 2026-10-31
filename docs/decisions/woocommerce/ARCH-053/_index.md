# ARCH-053 — woocommerce tasks

Architecture: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`

Assigned agent: `moda_woocommerce`. Coordinator: `moda_architect`.

**Portable definitions only; no task branch/worktree materialisation is asserted.** Individual task YAML is authoritative; do not treat this index as execution claim.

| Task | Purpose | Status | Depends On |
|---|---|---|---|
| [ARCH-053-WOOCOMMERCE-001](WOOCOMMERCE-001-capture-original-cart-coupons-and-options.md) | Capture original Woo cart coupons and restorable line data | Ready | ARCH-053-API-001, ARCH-053-BACKGROUND-001 |
| [ARCH-053-WOOCOMMERCE-002](WOOCOMMERCE-002-restore-cart-from-customer-confirmed-link.md) | Restore products after customer-confirmed Woo checkout link | Pending | ARCH-053-WOOCOMMERCE-001, ARCH-053-API-002 |
| [ARCH-053-WOOCOMMERCE-003](WOOCOMMERCE-003-capture-manual-return-to-unchanged-woo-checkout.md) | Detect human return to an unchanged existing Woo checkout | Pending | ARCH-053-WOOCOMMERCE-001 |
| [ARCH-053-WOOCOMMERCE-004](WOOCOMMERCE-004-capture-coupon-only-checkout-activity.md) | Publish coupon additions and removals as Woo checkout activity | Pending | ARCH-053-WOOCOMMERCE-001 |
| [ARCH-053-WOOCOMMERCE-005](WOOCOMMERCE-005-reapply-original-coupons-at-restore.md) | Reapply original basket coupons through native WooCommerce validation | Pending | ARCH-053-WOOCOMMERCE-002, ARCH-053-WOOCOMMERCE-004 |
| [ARCH-053-WOOCOMMERCE-006](WOOCOMMERCE-006-surface-rejected-coupon-notices.md) | Display rejected original coupons and updated checkout totals | Pending | ARCH-053-WOOCOMMERCE-005 |

ARCH-052 is exclusively dynamic-discount discovery. ARCH-053 only restores previously applied original Woo coupons and core basket data; no dynamic incentive work is authorized.
