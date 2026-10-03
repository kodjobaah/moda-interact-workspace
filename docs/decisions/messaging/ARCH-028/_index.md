# ARCH-028 Messaging Tasks

Architecture:

`docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Assigned Agent:

`moda_messaging`

Coordinator:

`moda_architect`

| Task | Description | Status | Dependencies |
|------|-------------|--------|--------------|
| MESSAGING-001 | Emit provider-status v3 with bounded WhatsApp failure evidence | Pending | SHARED-002, BACKGROUND-001 |

## Current frontier

`ARCH-028-MESSAGING-001` is defined but remains Pending until the dual-version Shared package is published and `ARCH-028-BACKGROUND-001` is Complete. This is the producer side of the consumer-first rollout.

## Boundary

MESSAGING-001 owns only Messaging adoption of the exact published Shared package, extraction of bounded provider failure codes from already-verified Meta status webhooks, v3 normalized status production, and deterministic queue identity required to deliver newly enriched FAILED evidence.

It does not classify provider codes, resolve Shops, write database state, suppress recipients, reconcile recoveries/follow-ups, compensate usage, restore capacity or notify merchants.
