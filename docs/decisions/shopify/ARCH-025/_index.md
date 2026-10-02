# ARCH-025 Shopify tasks

Architecture: [`ARCH-025`](../../../architecture/ARCH-025-shopify-billing-service-maintainability.md).

Assigned agent: `moda_app`.

Repository: `moda-interact`.

Coordinator: `moda_architect`.

This directory is the Shopify `BillingService` tranche of ARCH-025. Background billing-subscription reconciliation is now a separate sibling tranche under `docs/decisions/background/ARCH-025/` and does **not** gate this Shopify sequence. CheckoutRecovery, Admin and Commerce maintainability work remain outside ARCH-025.

The tasks execute sequentially because they share the `billing.service.ts` compatibility façade and later tasks consume collaborators extracted by earlier tasks.

```text
SHOPIFY-001 -> SHOPIFY-002 -> SHOPIFY-003 -> SHOPIFY-004 -> SHOPIFY-005
     -> SHOPIFY-006 -> SHOPIFY-007 -> SHOPIFY-008 -> SHOPIFY-009
     -> SHOPIFY-010 -> SHOPIFY-011
```

The frozen regression asset is `moda-interact/tests/unit/services/billing.service.test.ts`: 213 tests, SHA-256 `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`. Durable baseline `ARCH025-TEST-001` records the 18 frozen-suite failures and six additional full-suite failures proven identical on the exact pre-task and SHOPIFY-001 implementation commits. Every task must leave the frozen file byte-for-byte unchanged and introduce no failing identifier outside that baseline.

Source/task reconciliation additionally fixes two shared internal mechanics: SHOPIFY-006 establishes `subscription-locks.ts` and `billing-retry-policy.ts` for later hosted/sync reuse; SHOPIFY-010 remains a participant in the caller-owned sync transaction rather than becoming a transaction owner. SHOPIFY-002 retains the thin runtime-private `resolveOrMaterializeBillingPlan(...)` delegate required by the frozen regression suite.

Individual task YAML is authoritative.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [SHOPIFY-001](SHOPIFY-001-extract-billing-period-projection.md) | Extract current BillingPeriod projection/cycle invariants | Complete | - |
| [SHOPIFY-002](SHOPIFY-002-extract-billing-plan-resolution.md) | Extract operational BillingPlan resolution and catalogue reads | Complete | SHOPIFY-001 |
| [SHOPIFY-003](SHOPIFY-003-extract-subscription-read-service.md) | Extract local/provider Subscription read model | Complete | SHOPIFY-002 |
| [SHOPIFY-004](SHOPIFY-004-extract-recovery-capacity-read-service.md) | Extract merchant recovery-capacity read model | Complete | SHOPIFY-003 |
| [SHOPIFY-005](SHOPIFY-005-extract-merchant-billing-read-service.md) | Extract merchant billing-page read model | Complete | SHOPIFY-004 |
| [SHOPIFY-006](SHOPIFY-006-extract-subscription-activation-service.md) | Extract initial Free/Paid activation intent workflow | Complete | SHOPIFY-005 |
| [SHOPIFY-007](SHOPIFY-007-extract-hosted-plan-change-service.md) | Extract hosted plan-change callback fencing | Complete | SHOPIFY-006 |
| [SHOPIFY-008](SHOPIFY-008-extract-recovery-credit-purchase-request-service.md) | Extract recovery-credit purchase initiation | Complete | SHOPIFY-007 |
| [SHOPIFY-009](SHOPIFY-009-extract-subscription-ended-notification-service.md) | Extract subscription-ended support notification | Complete | SHOPIFY-008 |
| [SHOPIFY-010](SHOPIFY-010-extract-initial-paid-activation-finalisation.md) | Extract initial Paid activation durable finalisation from sync | Complete | SHOPIFY-009 |
| [SHOPIFY-011](SHOPIFY-011-extract-subscription-sync-service.md) | Extract remaining provider-to-local synchronization coordinator | Complete | SHOPIFY-010 |

## Execution frontier

`ARCH-025-SHOPIFY-001` is Complete and architect-accepted at Attempt 2. `ARCH-025-SHOPIFY-002` is Complete and architect-accepted at Attempt 1. `ARCH-025-SHOPIFY-003` is Complete and architect-accepted at Attempt 2. `ARCH-025-SHOPIFY-004` through `ARCH-025-SHOPIFY-008` are Complete and architect-accepted at Attempt 1. `ARCH-025-SHOPIFY-009` is Complete and architect-accepted at Attempt 2. `ARCH-025-SHOPIFY-010` is Complete and architect-accepted at Attempt 1. `ARCH-025-SHOPIFY-011` is Complete and architect-accepted at Attempt 2. The **Shopify tranche is complete**; the independent Background tranche remains the ARCH-025 execution frontier.
