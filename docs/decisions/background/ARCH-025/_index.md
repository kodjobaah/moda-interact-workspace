# ARCH-025 Background tasks

Architecture: [`ARCH-025`](../../../architecture/ARCH-025-shopify-billing-service-maintainability.md).

Assigned agent: `moda_background`.

Repository: `moda-interact-background`.

Coordinator: `moda_architect`.

This directory contains two independent Background maintainability chains under ARCH-025:

- BACKGROUND-001..007: billing-subscription reconciliation coordinator;
- BACKGROUND-008..015: CheckoutRecoveryService lifecycle façade.

Neither Background chain depends on the Shopify tranche or on the other Background chain. They may therefore advance independently. BACKGROUND-001 is architect-accepted Complete at Attempt 3, BACKGROUND-002 and BACKGROUND-003 are architect-accepted Complete at Attempt 2, and BACKGROUND-004 through BACKGROUND-007 are architect-accepted Complete at Attempt 1; the billing-reconciliation chain is complete. BACKGROUND-008 through BACKGROUND-013 are architect-accepted Complete at Attempt 1; BACKGROUND-014 is independently Ready. Each chain is sequential internally because it progressively extracts from one high-churn compatibility façade/coordinator.

```text
BACKGROUND-001 -> BACKGROUND-002 -> BACKGROUND-003 -> BACKGROUND-004
      -> BACKGROUND-005 -> BACKGROUND-006 -> BACKGROUND-007

BACKGROUND-008 -> BACKGROUND-009 -> BACKGROUND-010 -> BACKGROUND-011
      -> BACKGROUND-012 -> BACKGROUND-013 -> BACKGROUND-014 -> BACKGROUND-015
```

Frozen Background regression asset:

```text
moda-interact-background/tests/unit/services/billing-subscription-reconciliation.service.test.ts
146 tests
SHA-256: 0b53c44561a166e26c358d0b4b05a4a30da2f6dbb192e0b5d922064f90919239
```

Every BACKGROUND-001..007 task must leave that file byte-for-byte unchanged and all 146 tests must pass. `tests/unit/runtime/entrypoint-isolation.test.ts` must also pass to protect the seven-position billing-worker construction contract.

Frozen CheckoutRecovery regression assets for BACKGROUND-008..015:

```text
tests/unit/services/matured-candidate.materialization.test.ts
  SHA-256: 28d629008a63e3fc554dd15bd268c52a73287169832f40f63f5d02c0c3bcafcb
tests/unit/services/checkout-refresh.test.ts
  SHA-256: 3330367841b6a35e5cdb15c6f8619b529b74336834da8c307d66c16e3202a36f
tests/unit/services/order-recovery-correlation.test.ts
  SHA-256: 7b3d3020f822ee1bc514de7aee9f15245f3d86cd6dacd6fee6b1f892a6516dbf
tests/unit/services/checkout-recovery.capacity-resume.test.ts
  SHA-256: 8c11db2f98681899742579db2766527ec5f26b5dfdf15a264551eecea9a115e1
```

Every BACKGROUND-008..015 task must leave all four files byte-for-byte unchanged and pass them. Focused tests are added in separate files. `tests/unit/runtime/entrypoint-isolation.test.ts` remains required so recovery-worker topology is not changed accidentally.

Individual task YAML is authoritative.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-extract-reconciliation-classification.md) | Pure durable state/job classification | Complete | - |
| [BACKGROUND-002](BACKGROUND-002-extract-reconciliation-queue.md) | Deterministic queue publication and reconstruction | Complete | BACKGROUND-001 |
| [BACKGROUND-003](BACKGROUND-003-extract-initial-activation-reconciliation.md) | Initial Free/Paid activation and shared exact primitives | Complete | BACKGROUND-002 |
| [BACKGROUND-004](BACKGROUND-004-extract-reinstall-reconciliation.md) | UNINSTALLED reinstall lifecycle | Complete | BACKGROUND-003 |
| [BACKGROUND-005](BACKGROUND-005-extract-billing-cycle-reconciliation.md) | Cycle discovery, pre-close and same-plan rollover | Complete | BACKGROUND-004 |
| [BACKGROUND-006](BACKGROUND-006-extract-established-plan-change-reconciliation.md) | Established plan-change convergence | Complete | BACKGROUND-005 |
| [BACKGROUND-007](BACKGROUND-007-reduce-subscription-reconciliation-coordinator.md) | Final bounded context/coordinator | Complete | BACKGROUND-006 |
| [BACKGROUND-008](BACKGROUND-008-extract-recovery-initiation.md) | Initial outreach + confirmed-send finalisation | Complete | - |
| [BACKGROUND-009](BACKGROUND-009-extract-recovery-outreach-follow-up-processor.md) | No-response follow-up execution | Complete | BACKGROUND-008 |
| [BACKGROUND-010](BACKGROUND-010-extract-recovery-snapshot-mapping.md) | Canonical Shopify -> recovery snapshot mapping | Complete | BACKGROUND-009 |
| [BACKGROUND-011](BACKGROUND-011-extract-matured-candidate-materialization.md) | Matured candidate -> durable recovery | Complete | BACKGROUND-010 |
| [BACKGROUND-012](BACKGROUND-012-extract-checkout-event-orchestration.md) | Checkout/create/update/cart orchestration | Complete | BACKGROUND-011 |
| [BACKGROUND-013](BACKGROUND-013-extract-order-recovery-correlation.md) | Order completion correlation | Complete | BACKGROUND-012 |
| [BACKGROUND-014](BACKGROUND-014-extract-capacity-blocked-recovery-resume.md) | Durable capacity-blocked resume | Ready | BACKGROUND-013 |
| [BACKGROUND-015](BACKGROUND-015-extract-recovery-agent-context.md) | Agent-context reads + final façade | Pending | BACKGROUND-014 |

## Execution frontier

The billing-reconciliation chain is complete through `ARCH-025-BACKGROUND-007`. `ARCH-025-BACKGROUND-014` is independently Ready because BACKGROUND-013 is architect-accepted Complete at Attempt 1. BACKGROUND-015 remains Pending until BACKGROUND-014 is architect-accepted Complete. Full-suite no-regression evidence for this repository is governed by `ARCH025-BACKGROUND-TEST-001` in `docs/development-baseline.md`; unrelated Commerce deadline and observability preload/runtime failures observed during B013 are not added to that durable baseline because they cannot execute B013 code.
