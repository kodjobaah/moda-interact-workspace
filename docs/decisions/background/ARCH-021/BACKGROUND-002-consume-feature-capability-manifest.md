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
status: in_progress
priority: 95
executor: copilot
claimed_at: 2026-09-29T17:59:46Z
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

- [ ] Update Shared package dependency to the SHARED-002 version.
- [ ] Consume DATABASE-003 Prisma schema/gitlink as required.
- [ ] Update MCP manifest parsing to the new schema.
- [ ] Remove per-Capability prompt retrieval.
- [ ] Pass Feature behaviour through the new runner input/manifest contract once per Feature.
- [ ] Support zero selected Capabilities/Tools.
- [ ] Preserve exact Tool grant/descriptor authorization checks.
- [ ] Update grant persistence/reconciliation for the new contract.
- [ ] Replace legacy host/grant fixtures and assertions.
- [ ] Add reused-Tool, multiple-capabilities-one-Feature and zero-capability regressions.

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

- [ ] Background performs zero per-Capability prompt-name fetches.
- [ ] Feature behaviour is applied once per Feature through the Shared runner contract.
- [ ] A valid zero-Capability/zero-Tool manifest can proceed without a BASE-capability error.
- [ ] Tool execution remains restricted to exact currently granted Tool descriptors/revisions.
- [ ] Reused Tools preserve all Capability-key provenance without duplicate executable entries.
- [ ] Grant persistence/replay conforms to the new Shared schema.
- [ ] No Background runtime dependency on the removed Capability concepts remains.

## Validation

- [ ] focused Commerce host tests
- [ ] focused grant tests
- [ ] affected integration tests
- [ ] `npm run build`
- [ ] repository-supported lint/typecheck evidence where declared
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not modify Commerce Studio or Shared.

## Implementation Notes

Do not use this task to implement the later platform/shop Agent Configuration runtime cutover unless an accepted dependency has already changed the Shared runner contract to require it.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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
