# ARCH-021 Shared Tasks

Architecture:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Assigned Agent:

`moda_shared`

Coordinator:

`moda_architect`

## Phase 5 — simplified Feature Capability contract

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [SHARED-001](SHARED-001-simplify-feature-capability-contracts.md) | Remove Capability binding/config/revision semantics and define direct Feature/Capability/Tool manifest + runner contract | Ready | ARCH-020-SHARED-001 |
| [SHARED-002](SHARED-002-publish-simplified-feature-capability-contracts.md) | Publish the accepted simplified Shared Commerce contract | Pending | SHARED-001 |

SHARED-001 is independently executable. SHARED-002 is a publication-only gate and must not rerun implementation validation or modify consumer repositories.
