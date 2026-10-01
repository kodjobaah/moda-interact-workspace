# ARCH-024 shared tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_shared`.

Repository: `moda-interact-shared`.

Coordinator: `moda_architect`.

The Shared decomposition is intentionally exactly two tasks: implementation, then publication.

```text
DATABASE-001
    |
    v
SHARED-001
contracts + thin LangChain/OpenRouter runtime
    |
    v
SHARED-002
publish exact accepted revision
```

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [SHARED-001](SHARED-001-implement-model-contracts-openrouter-runtime.md) | Implement canonical Availability/Catalogue/configuration contracts and Node-only `OpenRouterModelClient` over `ChatOpenRouter` | Pending | DATABASE-001 |
| [SHARED-002](SHARED-002-publish-model-contracts-openrouter-runtime.md) | Publish the architect-accepted Shared model/OpenRouter runtime package revision | Pending | SHARED-001 |

## Execution frontier

No Shared task is Ready until `ARCH-024-DATABASE-001` is architect-accepted Complete.

LangGraph is explicitly out of scope; Shared remains a thin model-runtime integration behind the existing Commerce runner contract.
