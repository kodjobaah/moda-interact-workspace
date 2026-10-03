# ARCH-028 Shared Tasks

Architecture:

`docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Assigned Agent:

`moda_shared`

Coordinator:

`moda_architect`

## Execution Order

```text
ARCH-028-SHARED-001
Define dual-version WhatsApp provider-status contract (v2 + v3)
        |
        v
future ARCH-028-SHARED-002 publication-only gate
        |
        +--> Background consumer adoption before v3 producer deployment
        |
        +--> Messaging producer adoption after consumer compatibility
```

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [SHARED-001](SHARED-001-define-whatsapp-provider-failure-status-contract.md) | Define the v3 bounded WhatsApp failure-evidence contract while retaining v2 parsing for rolling deployment | Ready | - |

## Current frontier

`ARCH-028-SHARED-001` is Ready and independent of DATABASE-001.

The later Shared publication task is intentionally not materialised yet. Consumer/producer adoption must use the published architect-accepted package, never unpublished Shared task-branch source.

## Boundary

SHARED-001 owns only the runtime-safe provider-status envelope in `@modainteract/moda-interact-shared/billing`. It does not parse Meta webhook payloads, classify provider codes, persist reachability, compensate recovery usage, suppress recipients, or notify merchants.

The contract must preserve rolling-deployment compatibility by accepting both legacy v2 and current v3 events. Messaging must not begin producing v3 until Background has adopted the published dual-version parser.
