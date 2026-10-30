# ARCH-053 — api tasks

Architecture: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`

Assigned agent: `moda_api`. Coordinator: `moda_architect`.

**Portable definitions only; no task branch/worktree materialisation is asserted.** Individual task YAML is authoritative; do not treat this index as execution claim.

| Task | Purpose | Status | Depends On |
|---|---|---|---|
| [ARCH-053-API-001](API-001-accept-woo-cart-restoration-checkout-events.md) | Accept Woo checkout v3 with coupon/restoration data | Pending | ARCH-053-SHARED-002 |
| [ARCH-053-API-002](API-002-resolve-generation-bound-woo-checkout-link.md) | Resolve Woo recovery link with installation and generation authorization | Pending | ARCH-053-SHARED-002, ARCH-053-DATABASE-001 |

ARCH-052 is separately owned dynamic-discount discovery; no checkout restoration tasks are to be implemented under ARCH-052.
