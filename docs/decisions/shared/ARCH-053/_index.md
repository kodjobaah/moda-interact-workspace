# ARCH-053 — shared tasks

Architecture: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`

Assigned agent: `moda_shared`. Coordinator: `moda_architect`.

**Portable definitions only; no task branch/worktree materialisation is asserted.** Individual task YAML is authoritative; do not treat this index as execution claim.

| Task | Purpose | Status | Depends On |
|---|---|---|---|
| [ARCH-053-SHARED-001](SHARED-001-define-woocommerce-cart-restore-contracts.md) | Define canonical Woo restoration wire schemas | Ready | — |
| [ARCH-053-SHARED-002](SHARED-002-publish-woocommerce-restore-contracts.md) | Publish accepted Woo restoration contracts | Pending | ARCH-053-SHARED-001 |

ARCH-052 is separately owned dynamic-discount discovery; no checkout restoration tasks are to be implemented under ARCH-052.
