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
| BACKGROUND-002 | Converge recipient-undeliverable WhatsApp delivery failures | Pending | BACKGROUND-001, MESSAGING-001 |
| BACKGROUND-003 | Capture purchased recovery compensation provenance at commit | Pending | DATABASE-002 |

## Current frontier

`ARCH-028-BACKGROUND-001` is defined but remains Pending until both the durable DATABASE-001 schema and the exact published SHARED-002 package are Complete and architect-accepted.

This task is deliberately consumer-first. `ARCH-028-MESSAGING-001` is defined as its downstream producer gate; Messaging must not begin emitting provider-status v3 until BACKGROUND-001 is Complete and deployed/adopted. `ARCH-028-BACKGROUND-002` is defined after that producer gate and remains Pending until both BACKGROUND-001 and MESSAGING-001 are Complete. Independently, `ARCH-028-BACKGROUND-003` becomes eligible only after DATABASE-002 and records purchased-credit commit/refund provenance needed by the later compensation task.

## Boundary

BACKGROUND-001 owns only Background consumer adoption and message-level failure evidence persistence. BACKGROUND-002 owns the first bounded failure-policy/convergence step for `131026`: linked `WAITING_FOR_RESPONSE` recovery attempts become `FAILED` and their no-response follow-ups become non-actionable. BACKGROUND-003 owns only additive purchased-credit commit/refund provenance capture. None of these tasks yet updates recipient reachability, compensates usage, restores merchant capacity or notifies merchants.
