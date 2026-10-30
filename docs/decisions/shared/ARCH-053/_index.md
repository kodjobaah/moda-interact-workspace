# ARCH-053 — shared tasks

Architecture: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`

Assigned agent: `moda_shared`. Coordinator: `moda_architect`.

SHARED-001 is architect-accepted Complete with published implementation and parent task branches. SHARED-002 is Ready for package publication. Individual task YAML is authoritative.

| Task | Purpose | Status | Depends On |
|---|---|---|---|
| [ARCH-053-SHARED-001](SHARED-001-define-woocommerce-cart-restore-contracts.md) | Define canonical Woo restoration wire schemas | Complete | — |
| [ARCH-053-SHARED-002](SHARED-002-publish-woocommerce-restore-contracts.md) | Publish accepted Woo restoration contracts | Ready | ARCH-053-SHARED-001 |

ARCH-052 is separately owned dynamic-discount discovery; no checkout restoration tasks are to be implemented under ARCH-052.
