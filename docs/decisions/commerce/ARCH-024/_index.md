# ARCH-024 Commerce tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_commerce`.

Repository: `moda-interact-commerce`.

Coordinator: `moda_architect`.

The Commerce sequence intentionally removes the obsolete human Preview composition first and builds the replacement flow on the cleaned surface.

```text
COMMERCE-001  cleanup old human Preview UI
       |
       v
COMMERCE-002  effective available + one active model
       |
       v
COMMERCE-003  Studio model selection-only
       |
       v
COMMERCE-004  Feature -> all Capabilities composition
       |
       v
COMMERCE-005  new Test Conversations UI
       |
       v
COMMERCE-006  real selected-Shop Tool execution
       |
       v
COMMERCE-007  OpenRouter model execution
```

Additional dependencies from Database/Shared/Admin/ARCH-023 are shown below.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [COMMERCE-001](COMMERCE-001-remove-redundant-human-preview-functionality.md) | Remove obsolete human-facing Tool/Release/Fixture Preview composition while retaining referenced internal runtime seams | Ready | - |
| [COMMERCE-002](COMMERCE-002-resolve-effective-available-active-model.md) | Resolve effective Shop model availability and exactly one active model with fail-closed explicit overrides | Pending | DATABASE-001, SHARED-004, COMMERCE-001 |
| [COMMERCE-003](COMMERCE-003-make-commerce-studio-model-selection-only.md) | Retire Catalogue administration from Studio and retain only Platform/Shop active-model selection | Pending | COMMERCE-002, ADMIN-002 |
| [COMMERCE-004](COMMERCE-004-compose-test-conversations-from-selected-features.md) | Resolve selected Feature IDs to every direct Capability, Feature Behaviour and exact published Tool revisions | Pending | COMMERCE-003 |
| [COMMERCE-005](COMMERCE-005-build-feature-composed-test-conversations-ui.md) | Build selected-Shop Feature-composed Test Conversations UI and create Conversation Configuration Snapshots | Pending | COMMERCE-004, ARCH-023-COMMERCE-003 |
| [COMMERCE-006](COMMERCE-006-execute-test-conversation-tools-against-selected-shop.md) | Execute exact snapshot Tool revisions through production execution against the real selected Shop | Pending | COMMERCE-005 |
| [COMMERCE-007](COMMERCE-007-execute-test-conversation-models-through-openrouter.md) | Execute the snapshot active model through Shared OpenRouter runtime using the current environment credential per invocation | Pending | COMMERCE-006, SHARED-004, ADMIN-003 |

## Execution frontier

```text
ARCH-024-COMMERCE-001 -> Ready
```

COMMERCE-001 is independent of the new database/shared/admin model stack and may execute in parallel with DATABASE-001.

COMMERCE-005 intentionally depends on frozen `ARCH-023-COMMERCE-003` for additive trusted Platform + optional Shop Instructions. ARCH-024 does not redefine that contract.

Shared `runCommerceTurn` is now internally LangGraph-backed after SHARED-004. Commerce remains a consumer only: no direct LangGraph or MCP-client dependency is introduced. COMMERCE-007 passes its existing `StructuredLogger` into the runner.
