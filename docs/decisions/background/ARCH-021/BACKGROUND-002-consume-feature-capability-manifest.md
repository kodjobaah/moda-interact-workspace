---
id: ARCH-021-BACKGROUND-002
architecture_id: ARCH-021
title: Consume the simplified Feature capability manifest
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 95
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-DATABASE-003
  - ARCH-021-SHARED-002
  - ARCH-021-COMMERCE-089
enables:
  - ARCH-021-COMMERCE-092
created: 2026-09-29
updated: 2026-09-29
---

# Consume the simplified Feature capability manifest

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Move Background CommerceAgent hosting onto the published direct Feature/Capability/Tool manifest, removing per-Capability prompt fetches and assumptions about a mandatory base Capability.

## Context

Background currently parses the ARCH-020 manifest, fetches one MCP prompt for every Capability via `capability.promptName`, and relies on Shared grant rules that require `conversation_core`.

The new Shared contract embeds the immutable release Feature behaviour snapshots once per Feature and gives each Capability one exact Tool descriptor. Background should consume that contract directly; it must not reconstruct old revision/binding concepts locally.

## Scope

Primary files include:

```text
package.json / lockfile                         # consume SHARED-002 version
database/                                       # consume DATABASE-003 gitlink as required
src/commerce/mcp-client.ts
src/commerce/host.ts
src/commerce/grants.ts
focused commerce host/grant/integration tests
```

## Out of Scope

- Commerce producer/release implementation.
- Billing/subscription entitlement calculation.
- Studio authoring UI.
- Platform/shop Agent Configuration runtime cutover not already required by this manifest change.
- Shared contract redesign.

## Requirements

### R1 — consume the exact published Shared contract

Update `@modainteract/moda-interact-shared` to the version published by SHARED-002. Do not duplicate the manifest schema or old compatibility types locally.

### R2 — remove per-Capability prompt MCP calls

Delete the loop that fetches `client.prompt(capability.promptName)` for each manifest Capability.

Pass the manifest's Feature behaviour instructions through the new Shared runner contract exactly once per Feature.

Do not invent synthetic prompt names for Feature behaviour.

### R3 — allow zero selected Capabilities

A valid Commerce turn may have an empty selected Capability list and zero granted Tools. Background must not fail solely because `conversation_core` or another BASE capability is absent.

Existing host/runner safety instructions still apply.

### R4 — preserve exact Tool authorization

Tool list/execute checks must still require exact granted Tool identity/revision/name/descriptor provenance. The one-Tool-per-Capability simplification must not weaken current authorization.

A reused Tool granted by multiple Capabilities remains one executable Tool with multiple Capability keys.

### R5 — persist/reconcile the new grant shape only

Grant persistence and replay must accept the new Shared schema, including empty `selectedCapabilityKeys`, without reintroducing Capability type/configuration fields.

Consume the accepted DATABASE-003 grant/release schema through the Background database submodule as required.

### R6 — removed concepts stay removed

Background runtime code/tests must not depend on:

```text
selectionBinding
BASE / RECOVERY_POLICY
conversation_core requirement
Capability promptName
Capability revision identity
Capability maxSearchResults/maxRecommendations
```

## Work Items

- [x] Update Shared package dependency to the SHARED-002 version.
- [x] Consume DATABASE-003 Prisma schema/gitlink as required.
- [x] Update MCP manifest parsing to the new schema.
- [x] Remove per-Capability prompt retrieval.
- [x] Pass Feature behaviour through the new runner input/manifest contract once per Feature.
- [x] Support zero selected Capabilities/Tools.
- [x] Preserve exact Tool grant/descriptor authorization checks.
- [x] Update grant persistence/reconciliation for the new contract.
- [x] Replace legacy host/grant fixtures and assertions.
- [x] Add reused-Tool, multiple-capabilities-one-Feature and zero-capability regressions.

## Interfaces / Contracts

Consumes:

```text
@modainteract/moda-interact-shared version from ARCH-021-SHARED-002
Commerce manifests produced by ARCH-021-COMMERCE-089
DATABASE-003 Prisma schema where required
```

## Dependencies

- ARCH-021-DATABASE-003
- ARCH-021-SHARED-002
- ARCH-021-COMMERCE-089

## Enables

- ARCH-021-COMMERCE-092

## Acceptance Criteria

- [x] Background performs zero per-Capability prompt-name fetches.
- [x] Feature behaviour is applied once per Feature through the Shared runner contract.
- [x] A valid zero-Capability/zero-Tool manifest can proceed without a BASE-capability error.
- [x] Tool execution remains restricted to exact currently granted Tool descriptors/revisions.
- [x] Reused Tools preserve all Capability-key provenance without duplicate executable entries.
- [x] Grant persistence/replay conforms to the new Shared schema.
- [x] No Background runtime dependency on the removed Capability concepts remains.

## Validation

- [x] focused Commerce host tests
- [x] focused grant tests (covered through host grant persistence/replay and exact Tool authorization cases)
- [x] affected integration tests
- [x] `npm run build`
- [x] repository-supported lint/typecheck evidence where declared
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not modify Commerce Studio or Shared.

## Implementation Notes

Do not use this task to implement the later platform/shop Agent Configuration runtime cutover unless an accepted dependency has already changed the Shared runner contract to require it.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

Implementation: `package.json`, `package-lock.json`, `src/commerce/host.ts`, `src/commerce/mcp-client.ts`, and `tests/integration/commerce/host.test.ts`. Parent task record updated for review; the database submodule pointer was not changed.

### Work Completed

Pinned `@modainteract/moda-interact-shared` to 1.0.0 and consumed its direct Feature/Capability/Tool manifest. Removed the MCP prompt method and per-Capability prompt fetch loop; the Shared runner now receives the manifest's `featureBehaviours` and applies each once. Updated host parsing and MCP fixture handling for singular `toolDescriptor`, strengthened list and execution authorization to exact Tool identity/revision/name/version and grant provenance, and covered empty selected keys/tools, sibling Capabilities sharing one Feature, reused Tool deduplication, and absence of `prompts/get`.

Physical worktree isolation:
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-BACKGROUND-002`, `task/ARCH-021-BACKGROUND-002`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-BACKGROUND-002`, `task/ARCH-021-BACKGROUND-002`.
- Shared workspace and implementation checkouts were not switched or mutated for task implementation; no other task worktree was reused.
- Start-of-attempt synchronization: parent remote task branch fast-forward `not-needed`; parent `origin/main` incorporation `already-current`; implementation remote task branch fast-forward `not-needed`; implementation `origin/main` incorporation `already-current`.
- Recursive submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; `database` recorded at `e9fb60221f1532205650154dfff2aadb6270b14c`.
- Launcher claim: attempt 1, executor `copilot`, claim commit `fc4d1fd0efff7ca0a1f9cd3fd62747f2e9a579bd`, pushed successfully.

### Validation Results

On `task/ARCH-021-BACKGROUND-002`:
- Focused host suite: 41/41 passed.
- Affected Commerce integration and pipeline suites (`host.test.ts`, `commerce.agent.integration.test.ts`, `commerce.agent.pipeline.test.ts`): 43/43 passed.
- `npm run build`: passed, including Prisma Client generation and TypeScript compilation.
- `npm run prisma:validate`: passed against the pinned DATABASE-003 schema.
- Exact installed/locked Shared version: `@modainteract/moda-interact-shared@1.0.0`.
- Removed-concept audit across `src/` and `tests/` (`selectionBinding`, `RECOVERY_POLICY`, `conversation_core`, `promptName`, Capability revision identities/limits, and `toolDescriptors`): no matches.
- No lint script is declared in this repository's `package.json`; TypeScript validation is provided by the passing build.
- `git diff --check`: passed.

### Deviations

No database submodule update was needed: the prepared checkout already contained the DATABASE-003 schema at the accepted recorded commit. The repository does not declare a lint script, so none was invented or run.

### Assumptions

Shared 1.0.0's runner is authoritative for applying `manifest.featureBehaviours`; Background passes the manifest directly and does not reconstruct prompt messages or identities.

### Unresolved Issues

None within this task's scope.

### Architectural Concerns

None identified. No Commerce Studio or Shared implementation was changed; platform/shop Agent Configuration runtime work remains out of scope.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
