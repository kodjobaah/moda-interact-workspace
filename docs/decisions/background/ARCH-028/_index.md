# ARCH-028 Background Tasks

Architecture: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Assigned Agent: `moda_background`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| BACKGROUND-001 | Adopt v3 failure evidence and explicit provider-message status lattice | Pending | DATABASE-001, SHARED-002 |
| BACKGROUND-002 | Classify 131026 and converge recovery/follow-up without attempt-status compensation gate | Pending | BACKGROUND-001, MESSAGING-001 |
| BACKGROUND-003 | Historical purchased compensation provenance capture | Superseded | - |
| BACKGROUND-004 | Generic release/compensation + outbound hard-limit correction + provider-job replay | Pending | BACKGROUND-002, DATABASE-002, ARCH-027-BACKGROUND-001 |
| BACKGROUND-005 | Shop-scoped reachability, pre-admission suppression and positive clearing | Pending | BACKGROUND-004, DATABASE-003 |
| BACKGROUND-006 | Synchronous terminal Meta rejection parity | Pending | BACKGROUND-005 |
| BACKGROUND-007 | Missing-recipient zero-billing path | Pending | BACKGROUND-005 |
| BACKGROUND-008 | Merchant SYSTEM notification after correction/suppression | Pending | BACKGROUND-006 |
| BACKGROUND-009 | Committed purchased-credit compensation | Pending | BACKGROUND-004, BACKGROUND-008, ARCH-027-BACKGROUND-005 |

## Current frontier

BACKGROUND-001 waits on accepted DATABASE-001 and published SHARED-002. Producer MESSAGING-001 remains consumer-first gated on BACKGROUND-001. BACKGROUND-002 then establishes terminal-recipient recovery convergence before compensation work begins.

The generic path through BACKGROUND-008 does not depend on ARCH-027-BACKGROUND-005. Only BACKGROUND-009 waits for final purchased/refund semantics.

## Boundary

Background owns recovery/provider-status policy and accounting orchestration. Shop identity for provider delivery failure comes from durable message/recovery ownership, never a phone lookup. Reachability phone state is only `(shopId, attempt.recipient)` policy evidence.
