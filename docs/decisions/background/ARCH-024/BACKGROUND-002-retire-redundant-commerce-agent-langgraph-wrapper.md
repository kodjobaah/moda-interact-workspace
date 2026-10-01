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
status: review
priority: 56
executor:
claimed_at:
attempt: 2
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

- [x] Prove the one-node pipeline is unreferenced by production code.
- [x] Delete the wrapper and focused wrapper test.
- [x] Prove no remaining Background source/test imports LangGraph.
- [x] Remove the direct LangGraph package dependency and update lockfile normally.
- [x] Verify `CommerceMcpClient` and official MCP SDK dependencies are unchanged.
- [x] Run focused/full Background validation required below.

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

- [x] The redundant one-node Background graph and its unit test are deleted.
- [x] Background production code has no direct `@langchain/langgraph` import.
- [x] Background package metadata no longer directly depends on `@langchain/langgraph`.
- [x] Production WhatsApp -> CommerceAgent call path is unchanged.
- [x] `CommerceMcpClient` still uses the official MCP SDK and retains the hardened transport invariants.
- [x] No `@langchain/mcp-adapters` dependency is introduced.
- [x] Existing Commerce host/MCP/conversation-turn tests remain passing.

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

Ready for Architect Review

### Files Changed

- `src/agents/commerce.agent.pipeline.ts`: deleted unused one-node LangGraph wrapper.
- `tests/unit/agent/commerce.agent.pipeline.test.ts`: deleted its isolated wrapper test.
- `package.json`, `package-lock.json`: removed the direct `@langchain/langgraph` dependency using npm.
- `docs/decisions/background/ARCH-024/BACKGROUND-002-retire-redundant-commerce-agent-langgraph-wrapper.md`: Attempt 2 lifecycle and A1-R1/A1-R2 evidence update; the Architect Review section is unchanged.

### Work Completed

- Static R1 search before deletion found references only in the wrapper and its focused test. The production WhatsApp worker calls `runCommerceAgent` through `ConversationTurnProcessor`/admission and does not route through the wrapper.
- Deleted the wrapper and test; post-deletion `rg` returned no matches for `@langchain/langgraph`, `createCommerceAgentPipeline` or `commerce.agent.pipeline` in `src`, `tests` or `package.json`.
- Removed the direct LangGraph dependency; `npm ls --depth=0` reports it absent from root dependencies. It remains installed transitively through the published Shared package.
- Preserved `@modelcontextprotocol/sdk@1.30.0` and the official `CommerceMcpClient` / `StreamableHTTPClientTransport` / `Client.callTool` implementation unchanged. No `@langchain/mcp-adapters` dependency was added.
- Attempt 1 implementation commit `ed12296fe11669f48eda50066163aef50aa7fa8d` remains the only implementation commit; Attempt 2 required evidence reconciliation only, so no implementation source/test files changed.

Architect Review rework dispositions:

- **A1-R1 — implemented.** This task Completion Report now records the canonical workspace, dedicated parent/implementation worktrees and branches, start synchronization, recursive submodule result and database gitlink, Shared version, Attempt 1 implementation SHA, prior parent report/claim commit identities, and final clean/remote synchronization evidence. The only file changed for this item is this task document.
- **A1-R2 — implemented.** Ran plain `npm test` at the exact pre-task commit `0b629d4365d857eb21127f55a701d63635a201c5` and the submitted `ed12296fe11669f48eda50066163aef50aa7fa8d` tree under Node `v24.21.0`, npm `11.19.0`, Vitest `4.1.11`, database gitlink `cfeeb12456b4e05067a96857a8c47837d7e33bbd`, the same `localhost:5432` integration-test environment, and lockfile-installed dependencies. Both runs produced the same 8 failed tests and the same missing-fixture suite; the submitted tree has exactly one fewer passing test because the wrapper's isolated test was intentionally deleted. No new or worsened failure was found, so no implementation changes were required. The focused observability slice passed on both trees (5 files / 27 tests each), confirming the four Attempt 1 observability timeouts were transient. The only file changed for this item is this task document.

Attempt 2 launcher evidence:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-BACKGROUND-002`, branch `task/ARCH-024-BACKGROUND-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-BACKGROUND-002`, branch `task/ARCH-024-BACKGROUND-002`.
- Shared/default workspace checkout switched or mutated: no. Shared/default implementation checkout switched or mutated: no. Another task worktree reused: no.
- Parent start sync: remote task fast-forward `not-needed`; `origin/main` incorporated `yes`.
- Implementation start sync: remote task fast-forward `not-needed`; `origin/main` incorporated `already-current`.
- Recursive submodule sync and update/init: both passed. Database gitlink: `cfeeb12456b4e05067a96857a8c47837d7e33bbd`.
- Published Shared package: `@modainteract/moda-interact-shared@1.1.0`.
- Attempt 1 parent report commit: `deb53a18beca5f0763d2dc4c7ad4835553620fc4`. Attempt 2 parent pre-claim head: `033eeed04b9e7bb8ca619b03a095950c30d88c18`; durable launcher claim commit: `9051412935dcf3a45ed4360b1c4a97171aef381d` (pushed).
- Implementation final verification: worktree clean; local `HEAD` and `origin/task/ARCH-024-BACKGROUND-002` both equal `ed12296fe11669f48eda50066163aef50aa7fa8d`.

### Validation Results

- Exact pre-task baseline `0b629d4365d857eb21127f55a701d63635a201c5` and submitted `ed12296fe11669f48eda50066163aef50aa7fa8d` both ran plain `npm test` with Node `v24.21.0`, npm `11.19.0`, Vitest `4.1.11`, database gitlink `cfeeb12456b4e05067a96857a8c47837d7e33bbd`, and integration tests targeting unavailable `localhost:5432`.
- Baseline result: 4 failed files, 96 passed files, 15 skipped files (115 total); 8 failed tests, 1,393 passed tests, 38 skipped tests (1,439 total).
- Submitted result: 4 failed files, 95 passed files, 15 skipped files (114 total); 8 failed tests, 1,392 passed tests, 38 skipped tests (1,438 total). The one-file/one-test reduction is exactly the deleted wrapper test; the failure set is unchanged.
- Identical failures in both runs:
  - `tests/unit/commerce/evidence.test.ts`: suite collection fails with `ENOENT` for the missing `/moda-interact-workspace-task-ARCH-020-BACKGROUND-002/docs/architecture/ARCH-020-evidence-contract-fixtures.json` fixture.
  - `tests/integration/translation-enum-bindings.integration.test.ts`: `persists submission failure statuses through the real enum column`, `persists terminal poll Batch and translation statuses through real enum columns`, `persists failed provider results through the real translation enum column`, and `persists SUBMISSION_UNKNOWN correlation adoption through the real Batch enum column`; each cannot connect to `localhost:5432`.
  - `tests/unit/services/billing-reconciliation.service.test.ts`: `persists rotating provider-cycle lag and enqueues the existing +60 second job`, `repairs a missing Paid cycle schedule during rotating provider-cycle lag`, and `repairs a missing pack-enabled Free cycle schedule during rotating provider-cycle lag`.
  - `tests/unit/services/matured-candidate.materialization.test.ts`: `creates a recovery from current Shopify data when the lookup is found and recoverable`.
- Focused observability rerun on baseline and submitted trees: both passed 5 files / 27 tests; the four Attempt 1 observability timeouts were transient.
- Focused host/conversation/worker/CommerceAgent slice: passed 4 files / 93 tests.
- Post-deletion `rg -n '@langchain/langgraph|createCommerceAgentPipeline|commerce\.agent\.pipeline' src tests package.json`: PASS; no matches.
- MCP boundary scan: PASS; official SDK, `CommerceMcpClient`, `StreamableHTTPClientTransport` and `callTool` remain; `@langchain/mcp-adapters` is absent. `src/commerce/host.ts` and `src/commerce/mcp-client.ts` are unchanged from the pre-task baseline.
- `npm run build`: PASS; generated Prisma Client v6.19.3 and completed `tsc`.
- `npm run typecheck`: unavailable; this script is not declared in `package.json`. The declared build runs TypeScript compilation and passed.
- `git diff --check`: PASS. Implementation tree contains only the previously published task delta; no Attempt 2 implementation changes were made.

### Deviations

- Full `npm test` is non-green but baseline-equivalent for the exact same failure set above; the prior four observability timeouts did not recur. The task-focused 4-file/93-test slice passes. Standalone `typecheck` is not a declared script; `npm run build` is the declared Prisma-generation plus TypeScript gate.

### Assumptions

None.

### Unresolved Issues

The identical baseline full-suite failures listed in Validation Results remain for Architect triage; the ARCH-020 fixture and PostgreSQL service were unavailable in this environment. No unrelated source or test failures were modified.

### Architectural Concerns

None identified. The implementation removes only the redundant Background wrapper/dependency and leaves the approved Shared runner and official MCP transport boundaries intact.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 implementation is architecturally conformant in the inspected task-owned source. Against the accepted BACKGROUND-001 implementation baseline, the only repository changes are deletion of `src/agents/commerce.agent.pipeline.ts`, deletion of `tests/unit/agent/commerce.agent.pipeline.test.ts`, and removal of the direct `@langchain/langgraph` dependency from `package.json` / the root dependency map in `package-lock.json`. The deleted wrapper is exactly the documented one-node `START -> commerceAgent -> END` graph and the pre-task baseline references it only from its own focused test. Post-task source/test/package scans contain no direct Background LangGraph reference. LangGraph remains transitively supplied by published Shared `1.1.0`, which is expected.

The retained production boundary is unchanged: `src/commerce/host.ts` and `src/commerce/mcp-client.ts` are byte-identical to the accepted BACKGROUND-001 baseline; `@modelcontextprotocol/sdk@1.30.0`, `CommerceMcpClient`, `StreamableHTTPClientTransport` and `Client.callTool(...)` remain in place; no `@langchain/mcp-adapters` dependency is introduced. No source redesign is requested by this review.

Acceptance is withheld for durable execution/validation evidence only.

**A1-R1 — Record the prepared-launch/worktree evidence in the Completion Report.** Add the launcher-resolved canonical workspace root, dedicated parent task worktree, dedicated `moda-interact-background` implementation worktree, exact `task/ARCH-024-BACKGROUND-002` branches, start-of-attempt synchronization evidence, recursive implementation-submodule materialisation evidence, accepted database gitlink identity, exact Shared `1.1.0` consumption, implementation commit `ed12296fe11669f48eda50066163aef50aa7fa8d`, parent report commit identities, remote-head equality and final clean-worktree evidence. The prepared launcher packet is valid evidence, but the Completion Report must preserve it durably.

**A1-R2 — Prove the non-clean full suite is non-regressing against the synchronized BACKGROUND-002 pre-task baseline.** The accepted BACKGROUND-001 final run recorded eight persistent baseline-equivalent failing tests plus the missing external ARCH-020 evidence fixture, with observability tests passing on its final rerun. This submission reports twelve failing tests and specifically adds four observability timeouts. Because this task changes installed dependency metadata, do not classify those extra failures as unrelated without comparison evidence. Run the same `npm test` command against the synchronized pre-task implementation baseline and the submitted implementation under equivalent Node/npm/Vitest/database-gitlink/environment conditions; record exact failing files/test names/outcomes for both. Re-run the focused observability file when needed to determine whether the four timeouts are transient. If the submitted state is baseline-equivalent or better and task-owned focused validation remains green, no source churn is required. If any current failure is new or worsened, correct only that regression in this same task and rerun the required validation.

No new task is required. This is evidence/reconciliation work unless A1-R2 proves an implementation regression.

### Reviewed Files

- `src/agents/commerce.agent.pipeline.ts` from the accepted BACKGROUND-001 baseline (deleted by this task)
- `tests/unit/agent/commerce.agent.pipeline.test.ts` from the accepted BACKGROUND-001 baseline (deleted by this task)
- `package.json`
- `package-lock.json`
- `src/commerce/host.ts`
- `src/commerce/mcp-client.ts`
- `docs/decisions/background/ARCH-024/BACKGROUND-002-retire-redundant-commerce-agent-langgraph-wrapper.md`
- `docs/decisions/background/ARCH-024/_index.md`
- `docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

### Validation Reviewed

- Independently compared the submitted `moda-interact-background` tree with the accepted BACKGROUND-001 implementation snapshot: task delta is limited to the two required deletions plus direct dependency metadata removal.
- Confirmed the pre-task baseline references `createCommerceAgentPipeline` / `commerce.agent.pipeline` only from the deleted wrapper and its dedicated test.
- Confirmed the submitted `src`, `tests` and `package.json` contain no `@langchain/langgraph`, `createCommerceAgentPipeline`, `commerce.agent.pipeline` or `@langchain/mcp-adapters` reference.
- Confirmed `package-lock.json` removes only the root direct LangGraph dependency while published Shared `1.1.0` continues to depend transitively on `@langchain/langgraph@1.4.15`.
- Confirmed `src/commerce/host.ts` and `src/commerce/mcp-client.ts` are byte-identical to the accepted BACKGROUND-001 baseline.
- Reviewed submitted focused-test evidence: 4 files / 93 tests passed.
- Reviewed submitted `npm run build` and `git diff --check` PASS results.
- Repository-wide `npm test` is not yet accepted as non-regressing because A1-R2 baseline-parity evidence is missing.

### Architecture Conformance

Implementation design: conformant.

Task lifecycle/evidence: not yet conformant because the Completion Report does not durably preserve the prepared launcher/worktree/synchronization/submodule evidence and the twelve-test repository-suite failure set has not been compared deterministically with this task's synchronized pre-task baseline.

### Follow-up

Reclaim `ARCH-024-BACKGROUND-002` for Attempt 2. Treat A1-R1 as report/evidence reconciliation and A1-R2 as evidence-only unless the comparison demonstrates a new or worsened regression. Do not begin any follow-on work.
