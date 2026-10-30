# ARCH-053 — background tasks

Architecture: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`

Assigned agent: `moda_background`. Coordinator: `moda_architect`.

**Portable definitions only; no task branch/worktree materialisation is asserted.** Individual task YAML is authoritative; do not treat this index as execution claim.

| Task | Purpose | Status | Depends On |
|---|---|---|---|
| [ARCH-053-BACKGROUND-001](BACKGROUND-001-carry-restoration-evidence-through-candidates.md) | Carry validated restoration evidence through Woo candidates | Pending | ARCH-053-SHARED-002 |
| [ARCH-053-BACKGROUND-002](BACKGROUND-002-persist-restore-evidence-at-recovery-admission.md) | Persist immutable restore snapshot at Woo recovery admission | Pending | ARCH-053-BACKGROUND-001, ARCH-053-DATABASE-001 |
| [ARCH-053-BACKGROUND-003](BACKGROUND-003-issue-idempotent-woo-generation-checkout-links.md) | Issue immutable, safe generation-specific Woo resume URLs | Pending | ARCH-053-BACKGROUND-002, ARCH-048-BACKGROUND-011 |

ARCH-052 is separately owned dynamic-discount discovery; no checkout restoration tasks are to be implemented under ARCH-052.
