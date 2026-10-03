# ARCH-026 Background tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_background`.

Repository: `moda-interact-background`.

Coordinator: `moda_architect`.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-adopt-shared-onboarding-milestone.md) | Make shared `Shop.onboardingCompleted` authoritative across the extracted reconciliation/discount owners while mirroring completion to the retained legacy field | Ready | DATABASE-001, ARCH-025-BACKGROUND-007 |
| [BACKGROUND-002](BACKGROUND-002-adopt-shared-international-context.md) | Read merchant language/time-zone/country from shared Shop state in Conversation, template selection and RecoverySnapshotBuilder | Pending | DATABASE-002, SHOPIFY-002, BACKGROUND-001, ARCH-025-BACKGROUND-015 |

## Execution frontier

BACKGROUND-001 is Ready because DATABASE-001 and the ARCH-025 reconciliation-refactor prerequisite BACKGROUND-007 are architect-accepted Complete. BACKGROUND-002 remains Pending until DATABASE-002, SHOPIFY-002 and BACKGROUND-001 are architect-accepted Complete; its ARCH-025 CheckoutRecovery prerequisite BACKGROUND-015 is already Complete.
