# ARCH-024 Shared Tasks

Architecture:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Assigned Agent:

`moda_shared`

Coordinator:

`moda_architect`

## Execution Order

```text
ARCH-024-DATABASE-001
        |
        v
ARCH-024-SHARED-001
Complete Shared implementation:
model contracts + OpenRouterModelClient + modular LangGraph runner +
runner guardrails + canonical structured logging
        |
        v
ARCH-024-SHARED-002
Publication-only gate
```

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [SHARED-001](SHARED-001-implement-model-contracts-openrouter-runtime.md) | Implement the complete unpublished Shared ARCH-024 Commerce runtime: model contracts/OpenRouter client, modular LangGraph runner, deterministic guardrails and canonical structured logging | Ready | DATABASE-001 |
| [SHARED-002](SHARED-002-publish-arch024-shared-runtime.md) | Publish the exact architect-accepted SHARED-001 implementation as one backward-compatible Shared package release | Pending | SHARED-001 |

## Current frontier

```text
ARCH-024-DATABASE-001 -> Complete
ARCH-024-SHARED-001   -> Ready
ARCH-024-SHARED-002   -> Pending
```

## Boundary

SHARED-001 is the only ARCH-024 Shared implementation task. It is intentionally deterministic and contains the exact model/Price-Plan contracts, Shared-owned OpenRouter credential AAD contract, module decomposition, four-node low-level `StateGraph`, trust/authorization/evidence rules, and `commerce.turn.*` logging contract. It MUST stop at `review` and MUST NOT publish.

SHARED-002 is publication-only. It MUST NOT change implementation source or rerun implementation validation solely to re-prove SHARED-001.

All Admin, Commerce and Background consumers use the exact version published by SHARED-002. No consumer may depend on unpublished Shared task-branch source.
