# ARCH-053 — system-test tasks

Architecture: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`

Assigned agent: `moda_system_test`. Coordinator: `moda_architect`.

**Portable definitions only; no task branch/worktree materialisation is asserted.** Individual task YAML is authoritative; do not treat this index as execution claim.

| Task | Purpose | Status | Depends On |
|---|---|---|---|
| [ARCH-053-SYSTEM-TEST-001](SYSTEM-TEST-001-certify-woo-checkout-links-coupons-and-generations.md) | Certify core Woo checkout link and recovery-generation lifecycle | Pending | ARCH-053-BACKGROUND-003, ARCH-053-BACKGROUND-005, ARCH-053-API-004, ARCH-016-ADMIN-003, ARCH-053-WOOCOMMERCE-002, ARCH-053-WOOCOMMERCE-003, ARCH-048-BACKGROUND-011, ARCH-046-WOOCOMMERCE-003 |
| [ARCH-053-SYSTEM-TEST-002](SYSTEM-TEST-002-certify-original-coupon-restoration.md) | Certify original applied-coupon capture persistence and restoration | Pending | ARCH-053-WOOCOMMERCE-004, ARCH-053-WOOCOMMERCE-006, ARCH-053-BACKGROUND-003, ARCH-053-WOOCOMMERCE-003, ARCH-048-BACKGROUND-011, ARCH-046-WOOCOMMERCE-003 |

ARCH-052 is exclusively dynamic-discount discovery. ARCH-053 only restores previously applied original Woo coupons and core basket data; no dynamic incentive work is authorized.
