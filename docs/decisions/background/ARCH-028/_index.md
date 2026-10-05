# ARCH-028 Background Tasks

Architecture: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Assigned Agent: `moda_background`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| BACKGROUND-001 | Adopt provider-status v3 and persist bounded failure evidence | Pending | DATABASE-001, SHARED-002 |
| BACKGROUND-002 | Converge recipient-undeliverable WhatsApp delivery failures | Pending | BACKGROUND-001, MESSAGING-001 |
| BACKGROUND-003 | Capture purchased recovery compensation provenance at commit | Superseded | - |
| BACKGROUND-004 | Compensate terminally undelivered recovery usage | Pending | BACKGROUND-002, DATABASE-002, ARCH-027-BACKGROUND-001, ARCH-027-BACKGROUND-005 |

## Current frontier

BACKGROUND-001 remains the consumer-first v3 adoption gate. BACKGROUND-002 owns terminal async recovery-attempt/follow-up convergence. DATABASE-002 independently supplies generic compensation lineage. BACKGROUND-004 can begin only after both terminal convergence and the accepted ARCH-027 provider/refund accounting frontier exist.

BACKGROUND-003 is superseded because compensation no longer reconstructs pre-commit refund cancellation history.

## Planned follow-ons

Reachability/suppression, synchronous provider rejection, missing-phone/no-recipient handling, merchant SYSTEM notification and terminal system validation remain to be materialised.
