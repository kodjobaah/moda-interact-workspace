---
id: ARCH-024-BACKGROUND-002
architecture_id: ARCH-024
title: Retire redundant Background CommerceAgent LangGraph wrapper
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 56
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-024-BACKGROUND-001
enables: []
created: 2026-10-01
updated: 2026-10-01
---

# Retire redundant Background CommerceAgent LangGraph wrapper

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Remove the unused one-node Background `commerce.agent.pipeline` LangGraph wrapper and Background's direct LangGraph dependency after the published Shared `runCommerceTurn` owns the actual Commerce turn graph, without changing the production WhatsApp/conversation processing path or the hardened MCP client.

## Context

The current Background file:

```text
src/agents/commerce.agent.pipeline.ts
```

builds only:

```text
START -> commerceAgent -> END
```

where `commerceAgent` delegates to `runCommerceAgent`. Production WhatsApp processing already invokes `runCommerceAgent` through the conversation-turn/admission path rather than this wrapper. After the combined SHARED-001 implementation is published through SHARED-002, retaining a second one-node graph in Background is misleading and leaves an unnecessary direct `@langchain/langgraph` dependency.

This task is cleanup only. It must not redesign production orchestration.

## Scope

Delete when still present and unreferenced:

```text
src/agents/commerce.agent.pipeline.ts
tests/unit/agent/commerce.agent.pipeline.test.ts
```

Remove the direct `@langchain/langgraph` dependency from:

```text
package.json
package-lock.json
```

only after static inspection proves no remaining Background source/test needs it.

Update Background-owned CommerceAgent documentation only if it explicitly describes the deleted wrapper.

## Out of Scope

- `runCommerceAgent` behaviour.
- `ConversationTurnProcessor`.
- WhatsApp worker/admission/ordering/lease behaviour.
- `executeCommerceHost`.
- `RunnerTool` semantics.
- `CommerceMcpClient`.
- Official `@modelcontextprotocol/sdk` usage.
- MCP manifest/list/call/resource behaviour.
- `COMMERCE_MCP_URL`.
- `X-Moda-Commerce-Context`.
- Tool authorization, grants, evidence or final response handling.
- Shared graph changes.
- New worker queues or services.

## Requirements

### R1 — prove the wrapper is not a production entry path

Before deletion, statically confirm the only source/test references to `createCommerceAgentPipeline`/`commerce.agent.pipeline` are the wrapper and its focused unit test. If a new production reference exists when the task is claimed, stop and return that architectural conflict to `moda_architect`.

### R2 — delete the redundant wrapper/test

Delete exactly:

```text
src/agents/commerce.agent.pipeline.ts
tests/unit/agent/commerce.agent.pipeline.test.ts
```

Do not replace them with another Background-local graph.

### R3 — remove direct LangGraph dependency only when unused

After deletion:

```bash
rg -n '@langchain/langgraph|createCommerceAgentPipeline|commerce\.agent\.pipeline' src tests
```

must return no matches.

Then remove `@langchain/langgraph` from Background `package.json` and update `package-lock.json` through the normal package-manager operation. Do not manually hand-edit transitive lockfile rows.

### R4 — retain the current official MCP SDK boundary

The following remains architecture-approved and MUST NOT be replaced:

```text
src/commerce/mcp-client.ts
CommerceMcpClient
@modelcontextprotocol/sdk Client
StreamableHTTPClientTransport
Client.callTool(...)
```

Preserve the current Moda-specific transport envelope:

```text
exact /api/mcp endpoint
POST only
request body bound
X-Moda-Commerce-Context
redirect:error
bounded timeout
401/403 -> DENIED
no mcp-session-id
JSON content-type profile
response body bound
CommerceToolResultSchema
isError/status consistency
```

Do not add `@langchain/mcp-adapters`.

### R5 — production call path remains unchanged

The production flow remains:

```text
WhatsApp worker
  -> ConversationTurnProcessor/admission
  -> runCommerceAgent
  -> executeCommerceHost
  -> published Shared runCommerceTurn
  -> RunnerTool.execute
  -> CommerceMcpClient.call
  -> official MCP SDK
```

No queue/lease/history/ordering/stale-turn behaviour changes are authorised.

## Work Items

- [ ] Prove the one-node pipeline is unreferenced by production code.
- [ ] Delete the wrapper and focused wrapper test.
- [ ] Prove no remaining Background source/test imports LangGraph.
- [ ] Remove the direct LangGraph package dependency and update lockfile normally.
- [ ] Verify `CommerceMcpClient` and official MCP SDK dependencies are unchanged.
- [ ] Run focused/full Background validation required below.

## Interfaces / Contracts

Consumes published Shared:

```text
@modainteract/moda-interact-shared/commerce/runner
```

Retains production MCP implementation:

```text
@modelcontextprotocol/sdk
CommerceMcpClient
```

No new cross-service contract.

## Dependencies

- ARCH-024-BACKGROUND-001

SHARED-002 is already consumed by BACKGROUND-001 and is therefore not repeated as a direct dependency. This cleanup task only removes the now-redundant local wrapper/dependency after the production host has moved to the published Shared runner.

## Enables

None directly. Gateway depends on BACKGROUND-001 because deployment/keyring cutover does not require deletion of the unused local graph wrapper.

## Acceptance Criteria

- [ ] The redundant one-node Background graph and its unit test are deleted.
- [ ] Background production code has no direct `@langchain/langgraph` import.
- [ ] Background package metadata no longer directly depends on `@langchain/langgraph`.
- [ ] Production WhatsApp -> CommerceAgent call path is unchanged.
- [ ] `CommerceMcpClient` still uses the official MCP SDK and retains the hardened transport invariants.
- [ ] No `@langchain/mcp-adapters` dependency is introduced.
- [ ] Existing Commerce host/MCP/conversation-turn tests remain passing.

## Validation

Inspect the repository's declared scripts first, then run its required typecheck/test/build checks for this bounded dependency cleanup. At minimum record:

```bash
rg -n '@langchain/langgraph|createCommerceAgentPipeline|commerce\.agent\.pipeline' src tests package.json
rg -n '@modelcontextprotocol/sdk|CommerceMcpClient|StreamableHTTPClientTransport|callTool' src/commerce package.json
npm run typecheck
npm test
npm run build
git diff --check
```

If `npm run build` or another named command is not declared in the synchronized Background `package.json`, do not invent it; record the actual declared validation command per repository policy.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin Gateway work.

## Implementation Notes

This task removes only a redundant wrapper. Shared now owns the real Commerce turn graph. Background continues to own production conversation lifecycle and the hardened private MCP transport.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
