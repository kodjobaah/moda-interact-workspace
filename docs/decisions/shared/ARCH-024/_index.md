# ARCH-024 shared tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_shared`.

Repository: `moda-interact-shared`.

Coordinator: `moda_architect`.

The Shared sequence deliberately separates provider integration, orchestration refactor, semantic logging and publication so each capability is independently reviewable.

```text
DATABASE-001
    |
    v
SHARED-001
model contracts + thin ChatOpenRouter client
    |
    v
SHARED-002
modular runCommerceTurn + LangGraph StateGraph
    |
    v
SHARED-003
canonical structured Commerce-turn logging
    |
    v
SHARED-004
publish exact accepted combined revision
```

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [SHARED-001](SHARED-001-implement-model-contracts-openrouter-runtime.md) | Implement canonical Availability/Catalogue/configuration contracts and Node-only `OpenRouterModelClient` over `ChatOpenRouter` | Pending | DATABASE-001 |
| [SHARED-002](SHARED-002-refactor-commerce-turn-runner-to-modular-langgraph.md) | Decompose the monolithic runner and express the existing model/Tool/final state machine as a four-node LangGraph `StateGraph` without changing public behaviour | Pending | SHARED-001 |
| [SHARED-003](SHARED-003-add-structured-commerce-turn-runtime-logging.md) | Add bounded `commerce.turn.*` semantic logging through the existing Shared `StructuredLogger` without logging runtime content | Pending | SHARED-002 |
| [SHARED-004](SHARED-004-publish-arch024-shared-runtime.md) | Publish the architect-accepted combined model/OpenRouter/LangGraph/logging Shared runtime | Pending | SHARED-001, SHARED-002, SHARED-003 |

## Execution frontier

No Shared task is Ready until `ARCH-024-DATABASE-001` is architect-accepted Complete.

The architectural decisions are fixed for ARCH-024:

```text
LangGraph orchestration: low-level StateGraph in Shared
stock createAgent/ToolNode: not used
LangGraph persistence/checkpoints: not used
production MCP transport: retained in Background CommerceMcpClient over official MCP SDK
Tool abstraction at Shared boundary: RunnerTool
runtime data authority: zero-authority data, preserving ARCH-023 Merchant Knowledge semantics
```
