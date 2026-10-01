# ARCH-024 Background tasks

Architecture: [`ARCH-024`](../../../architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md).

Assigned agent: `moda_background`.

Repository: `moda-interact-background`.

Coordinator: `moda_architect`.

ARCH-024 requires one Background task because the production change is one coherent runtime migration: resolve the same effective active model and invoke it through the published Shared OpenRouter runtime while preserving existing conversation orchestration.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-use-effective-openrouter-model-production-commerce-turns.md) | Replace the conversational Groq model path with effective ARCH-024 model resolution + current OpenRouter credential + Shared model runtime | Pending | DATABASE-001, SHARED-002, COMMERCE-002, ADMIN-003 |

## Execution frontier

Ready: none.

The existing Background LangGraph/workflow, ordering, history/admission behaviour and Groq speech-transcription use remain outside this task.
