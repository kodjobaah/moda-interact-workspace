# ARCH-024 Commerce tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_commerce`.

Repository: `moda-interact-commerce`.

Coordinator: `moda_architect`.

The Commerce graph is intentionally **not** one serial chain. Human Preview cleanup and database-backed model resolution can progress independently; the authored Test Conversation snapshot joins the model-resolution, Feature-composition and ARCH-023 Instruction prerequisites only when all three are actually required.

```text
COMMERCE-001 cleanup old human Preview UI
       |
       v
COMMERCE-004 Feature -> all Capabilities composition
       |
       +--------------------------+
                                  |
DATABASE-001 + SHARED-002         |
       |                          |
       v                          |
COMMERCE-002 effective available + SHOP -> PRICING_PLAN -> PLATFORM model
       |\                         |
       | \                        |
       |  \-> COMMERCE-003 Studio model selection-only
       |          ^
       |          |
       |      ADMIN-002 ownership replacement
       |
       +--------------------------+
                                  |
ARCH-023-COMMERCE-003 ------------+
                                  v
                           COMMERCE-005
                         Test Conversations UI +
                       complete authored snapshot
                                  |
                                  v
                           COMMERCE-006
                       real selected-Shop Tools
                                  |
                                  v
                           COMMERCE-007
                         OpenRouter model execution
```

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [COMMERCE-001](COMMERCE-001-remove-redundant-human-preview-functionality.md) | Remove obsolete human-facing Tool/Release/Fixture Preview composition while retaining referenced internal runtime seams | Complete | - |
| [COMMERCE-002](COMMERCE-002-resolve-effective-available-active-model.md) | Resolve effective Shop availability and exactly one model with fail-closed `SHOP -> current PRICING_PLAN -> PLATFORM` precedence | Complete | DATABASE-001, SHARED-002 |
| [COMMERCE-003](COMMERCE-003-make-commerce-studio-model-selection-only.md) | Retire Catalogue administration from Studio; retain explicit Platform/Shop selection and surface inherited `PRICING_PLAN` vs `PLATFORM` provenance | Pending | COMMERCE-002, ADMIN-002 |
| [COMMERCE-004](COMMERCE-004-compose-test-conversations-from-selected-features.md) | Resolve selected Feature IDs to every direct Capability, Feature Behaviour and exact published Tool revisions | Complete | COMMERCE-001 |
| [COMMERCE-005](COMMERCE-005-build-feature-composed-test-conversations-ui.md) | Build selected-Shop Feature-composed Test Conversations UI and create the complete authored Conversation Configuration Snapshot | Ready | COMMERCE-002, COMMERCE-004, ARCH-023-COMMERCE-003 |
| [COMMERCE-006](COMMERCE-006-execute-test-conversation-tools-against-selected-shop.md) | Execute exact snapshot Tool revisions through production execution against the real selected Shop | Pending | COMMERCE-005 |
| [COMMERCE-007](COMMERCE-007-execute-test-conversation-models-through-openrouter.md) | Execute the snapshot active model through Shared OpenRouter runtime using the current environment credential per invocation | Pending | COMMERCE-006, SHARED-002 |

## Execution frontier

```text
ARCH-024-COMMERCE-005 -> Ready
```

COMMERCE-002 is Complete / Accepted at Attempt 2 and consumes the accepted Database contract plus exactly `@modainteract/moda-interact-shared@1.1.0`. COMMERCE-004 is already Complete / Accepted at Attempt 1.

COMMERCE-005 is now Ready because COMMERCE-002, COMMERCE-004 and frozen `ARCH-023-COMMERCE-003` are all Complete. Studio model-selection UI does not gate Feature composition.

COMMERCE-003 retains one deliberate cross-application dependency on ADMIN-002 because it removes Commerce-owned Catalogue administration only after the Admin-owned replacement control plane exists. That is an ownership-migration dependency, not a source-code dependency.

COMMERCE-005 intentionally joins C002 effective model resolution, C004 Feature composition and frozen `ARCH-023-COMMERCE-003` Platform + optional Shop Instructions to create the complete authored snapshot.

COMMERCE-007 reads the durable credential row directly and consumes the Shared-owned AAD contract; it does not wait for the Admin credential-management UI.

Shared `runCommerceTurn` is internally LangGraph-backed after SHARED-002. Commerce remains a consumer only: no direct LangGraph or MCP-client dependency is introduced. COMMERCE-007 passes its existing `StructuredLogger` into the runner.
