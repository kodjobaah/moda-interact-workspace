# ARCH-024 database tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_database`.

Repository: `moda-interact-database`.

Coordinator: `moda_architect`.

ARCH-024 deliberately consolidates all durable model/availability/OpenRouter credential schema work into one coherent database task.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [DATABASE-001](DATABASE-001-persist-model-catalogue-availability-openrouter-credentials.md) | Persist Model Availability, scoped Catalogue Entries, dynamic provider/model identity, OpenRouter configuration JSON, encrypted per-environment credential and audit constraints | Ready | - |

## Execution frontier

```text
ARCH-024-DATABASE-001 -> Ready
```

The task is a pre-production/breaking migration and may reset incompatible development-only model catalogue state rather than preserving legacy `OPENAI/GROQ` development rows. It must preserve unrelated durable platform state.
