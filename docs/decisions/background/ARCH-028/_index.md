# ARCH-028 Background Tasks

Architecture:

`docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Assigned Agent:

`moda_background`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| BACKGROUND-001 | Adopt provider-status v3 and persist bounded failure evidence | Pending | DATABASE-001, SHARED-002 |

## Current frontier

`ARCH-028-BACKGROUND-001` is defined but remains Pending until both the durable DATABASE-001 schema and the exact published SHARED-002 package are Complete and architect-accepted.

This task is deliberately consumer-first. `ARCH-028-MESSAGING-001` is defined as its downstream producer gate; Messaging must not begin emitting provider-status v3 until BACKGROUND-001 is Complete and deployed/adopted.

## Boundary

BACKGROUND-001 owns only Background consumer adoption and message-level failure evidence persistence. It does not classify provider codes, update recipient reachability, reconcile RecoveryOutreachAttempt/CheckoutRecovery/follow-up state, compensate usage, restore merchant capacity or notify merchants.
