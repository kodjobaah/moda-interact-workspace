# ARCH-026 Background tasks

Architecture: [`ARCH-026`](../../../architecture/ARCH-026-woocommerce-application-foundation.md).

Assigned agent: `moda_background`.

Repository: `moda-interact-background`.

Coordinator: `moda_architect`.

| Task | Outcome | Status | Dependencies |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-adopt-shared-onboarding-milestone.md) | Make shared `Shop.onboardingCompleted` authoritative across the extracted reconciliation/discount owners while mirroring completion to the retained legacy field | Complete (Accepted, Attempt 3) | DATABASE-001, ARCH-025-BACKGROUND-007 |
| [BACKGROUND-002](BACKGROUND-002-adopt-shared-international-context.md) | Read merchant language/time-zone/country from shared Shop state in Conversation, template selection and RecoverySnapshotBuilder | Ready | DATABASE-002, SHOPIFY-002, BACKGROUND-001, ARCH-025-BACKGROUND-015 |

## Execution frontier

BACKGROUND-001 is Complete / Accepted at Attempt 3. Its implementation remains
`3918ee03...`; Attempt 3 was report-only and closed the launcher/submodule/baseline
evidence correction.

DATABASE-002, SHOPIFY-002, BACKGROUND-001 and the ARCH-025 CheckoutRecovery prerequisite
BACKGROUND-015 are architect-accepted Complete, so BACKGROUND-002 is Ready.

ADMIN-001 is independently Ready because SHOPIFY-001 and BACKGROUND-001 are both
architect-accepted Complete.

## BACKGROUND-001 Attempt 2 architect review — 2026-10-03

**Changes Requested / Ready, Attempt 2 retained; claim clear.** The shared onboarding
migration implementation is accepted in substance. Shared Shop authority, dual-write
compatibility, canonical `commerce.Shop` locking, completion lock ordering and discount
eligibility are conformant. Full-suite residuals are existing
`ARCH025-BACKGROUND-TEST-001` identities, not task regressions.

Attempt 3 is evidence/report-only: record the complete launcher worktree/synchronization/
recursive-submodule packet and correct the database-gitlink description. BACKGROUND-002
and ADMIN-001 remain gated.

## BACKGROUND-001 Attempt 3 architect acceptance — 2026-10-03

**Accepted / Complete, Attempt 3.** Attempt 3 changed only Completion Report evidence.
The report now records the full launcher/worktree/synchronization/recursive-submodule
packet, accurately identifies `database@16dba1a7...` as the accepted DATABASE-002
descendant already present before BACKGROUND-001, and maps the residual repository-wide
failures to `ARCH025-BACKGROUND-TEST-001`.

Implementation remains `3918ee03df507631387a7a73dbe157ece47eb3a1`; focused
onboarding/reconciliation/discount coverage remains 240/240 with coordinator 146/146.
BACKGROUND-002 and ADMIN-001 are promoted Ready.
