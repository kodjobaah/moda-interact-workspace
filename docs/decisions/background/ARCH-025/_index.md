# ARCH-025 Background tasks

Architecture: [`ARCH-025`](../../../architecture/ARCH-025-shopify-billing-service-maintainability.md).

Assigned agent: `moda_background`.

Repository: `moda-interact-background`.

Coordinator: `moda_architect`.

This directory is the Background billing-subscription reconciliation tranche of ARCH-025. It is independent of the Shopify tranche: `ARCH-025-BACKGROUND-001` does **not** depend on the remaining Shopify tasks and may execute while Shopify work continues. Background tasks themselves are sequential because they progressively extract from the same coordinator.

```text
BACKGROUND-001 -> BACKGROUND-002 -> BACKGROUND-003 -> BACKGROUND-004
      -> BACKGROUND-005 -> BACKGROUND-006 -> BACKGROUND-007
```

Frozen Background regression asset:

```text
moda-interact-background/tests/unit/services/billing-subscription-reconciliation.service.test.ts
98 tests
SHA-256: 0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239
```

Every task must leave that file byte-for-byte unchanged and all 98 tests must pass. `tests/unit/runtime/entrypoint-isolation.test.ts` must also pass to protect the seven-position billing-worker construction contract.

Individual task YAML is authoritative.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-extract-reconciliation-classification.md) | Pure durable state/job classification | Ready | - |
| [BACKGROUND-002](BACKGROUND-002-extract-reconciliation-queue.md) | Deterministic queue publication and reconstruction | Pending | BACKGROUND-001 |
| [BACKGROUND-003](BACKGROUND-003-extract-initial-activation-reconciliation.md) | Initial Free/Paid activation and shared exact primitives | Pending | BACKGROUND-002 |
| [BACKGROUND-004](BACKGROUND-004-extract-reinstall-reconciliation.md) | UNINSTALLED reinstall lifecycle | Pending | BACKGROUND-003 |
| [BACKGROUND-005](BACKGROUND-005-extract-billing-cycle-reconciliation.md) | Cycle discovery, pre-close and same-plan rollover | Pending | BACKGROUND-004 |
| [BACKGROUND-006](BACKGROUND-006-extract-established-plan-change-reconciliation.md) | Established plan-change convergence | Pending | BACKGROUND-005 |
| [BACKGROUND-007](BACKGROUND-007-reduce-subscription-reconciliation-coordinator.md) | Final bounded context/coordinator | Pending | BACKGROUND-006 |

## Execution frontier

`ARCH-025-BACKGROUND-001` is Ready. BACKGROUND-002 through BACKGROUND-007 remain Pending until the immediately preceding Background task is architect-accepted Complete.
