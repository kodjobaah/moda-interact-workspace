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
| [SHARED-001](SHARED-001-simplify-feature-capability-contracts.md) | Remove Capability binding/config/revision semantics and define direct Feature/Capability/Tool manifest + runner contract | Complete | ARCH-020-SHARED-001 |
| [SHARED-002](SHARED-002-publish-simplified-feature-capability-contracts.md) | Publish the accepted simplified Shared Commerce contract | Complete | SHARED-001 |

SHARED-001 and SHARED-002 are architect-accepted Complete. The simplified Feature/Capability/Tool contract is published as `@modainteract/moda-interact-shared@1.0.0`. Commerce and Background consumer migrations remain separate and must consume that published version.
