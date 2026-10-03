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

BACKGROUND-001 Attempt 2 is Ready / Changes Requested for an evidence-only Completion
Report correction. Its implementation `3918ee03...` is accepted in substance; no
Background source change is requested.

DATABASE-002, SHOPIFY-002 and the ARCH-025 CheckoutRecovery prerequisite BACKGROUND-015
are architect-accepted Complete, so BACKGROUND-002 now waits only for BACKGROUND-001.
ADMIN-001 likewise remains Pending on BACKGROUND-001 after accepted SHOPIFY-001.

## BACKGROUND-001 Attempt 2 architect review — 2026-10-03

**Changes Requested / Ready, Attempt 2 retained; claim clear.** The shared onboarding
migration implementation is accepted in substance. Shared Shop authority, dual-write
compatibility, canonical `commerce.Shop` locking, completion lock ordering and discount
eligibility are conformant. Full-suite residuals are existing
`ARCH025-BACKGROUND-TEST-001` identities, not task regressions.

Attempt 3 is evidence/report-only: record the complete launcher worktree/synchronization/
recursive-submodule packet and correct the database-gitlink description. BACKGROUND-002
and ADMIN-001 remain gated.
