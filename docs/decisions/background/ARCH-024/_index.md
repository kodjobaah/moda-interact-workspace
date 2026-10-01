# ARCH-024 Background tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_background`.

Repository: `moda-interact-background`.

Coordinator: `moda_architect`.

ARCH-024 uses two bounded Background tasks: production model/runtime migration first, then deletion of the redundant Background one-node LangGraph wrapper after Shared owns the real Commerce-turn graph.

```text
DATABASE-001 + SHARED-002
        |
        v
BACKGROUND-001
production SHOP -> PRICING_PLAN -> PLATFORM model + OpenRouter + runner logger wiring
        |
        +----------------------+
        |                      |
        v                      v
BACKGROUND-002            GATEWAY-001
remove redundant          deployment/keyring cutover
local graph wrapper
```

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-use-effective-openrouter-model-production-commerce-turns.md) | Replace conversational Groq model path with parent-architecture `SHOP -> current PRICING_PLAN -> PLATFORM` resolution + current OpenRouter credential + published Shared model/LangGraph runner; inject canonical logger; retain hardened MCP client | Pending | DATABASE-001, SHARED-002 |
| [BACKGROUND-002](BACKGROUND-002-retire-redundant-commerce-agent-langgraph-wrapper.md) | Delete the unused one-node Background LangGraph wrapper and direct dependency while preserving the official MCP SDK client | Pending | BACKGROUND-001 |

## Execution frontier

Ready: none.

Background does not wait for Commerce or Admin application implementation. It consumes the accepted Database schema plus published Shared runtime/contracts, implements the parent architecture's model-precedence policy locally, and uses the Shared-owned OpenRouter credential AAD contract.

Production conversation ordering, admission, leases, history and stale-turn semantics remain Background-owned. The hardened `CommerceMcpClient` over official `@modelcontextprotocol/sdk` is retained; `@langchain/mcp-adapters` is not adopted.
