---
id: ARCH-020-SHARED-002
architecture_id: ARCH-020
title: Publish external HTTP and response-processing contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 145
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-023
  - ARCH-020-COMMERCE-021
  - ARCH-020-COMMERCE-025
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-022
  - ARCH-020-COMMERCE-020
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-027
  - ARCH-020-COMMERCE-028
  - ARCH-020-COMMERCE-030
  - ARCH-020-COMMERCE-031
  - ARCH-020-COMMERCE-032
created: 2026-09-21
updated: 2026-09-21
---

# Publish external HTTP and response-processing contracts

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own /commerce exported contracts, discriminated execution validation, argument mapping/hash/compiler contracts, DTOs and package documentation/publication. No provider transport, encryption or response-processing implementation.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own /commerce exported contracts, discriminated execution validation, argument mapping/hash/compiler contracts, DTOs and package documentation/publication. No provider transport, encryption or response-processing implementation.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [ ] Implement C21 sections2/2.1/4 strict shapes and export the named schemas/types, including connection DTOs, JSON/TEXT decoding, visual/JAVASCRIPT processing union, TransformResponse and both processor input/result types. Preserve existing exports.
- [ ] Extend every execution-kind branch explicitly; reject unauthorized inputs/methods/path/query mappings. Retain definition size bound and add processing config to canonical tool hash through execution.
- [ ] Allow publication compiler output-schema derivation for external wrapper/projection; keep MCP/grant/final-response wire shapes unchanged. Add unchanged old-definition/descriptor/runner fixtures.
- [ ] Update README including complete inventory; publish one new exact package version following normal Shared release workflow and record registry/install verification. Do not mark Complete on local build alone.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-SHARED-001

## Enables

- ARCH-020-COMMERCE-023
- ARCH-020-COMMERCE-021
- ARCH-020-COMMERCE-025
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-022
- ARCH-020-COMMERCE-020
- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-027
- ARCH-020-COMMERCE-028
- ARCH-020-COMMERCE-030
- ARCH-020-COMMERCE-031
- ARCH-020-COMMERCE-032

## Acceptance Criteria

- [ ] X01: C21 worked examples parse, unsupported method/body/authority/type/path/oversize fails, old two execution variants still parse unchanged.
- [ ] Projection bounds/filter unions/connection DTOs are strict; malformed processing affects hash; external descriptor contains no origin/auth/execution fields.
- [ ] Package exports and fresh install/typecheck demonstrate new named APIs; published version and integrity evidence recorded.

## Validation

Provide `test:arch020-external-contracts` in the owning repository and document its exact scope.
Run focused changed-boundary tests, then existing repository typecheck/build
and lint where defined. Inspect package scripts first; do not invent a claim that
an absent script passed. Use C21 controlled transports and isolated stores.
Follow current developer-owned live/container validation policy; clearly separate
actual agent results from required unrun developer checks. No arbitrary screenshot
quota or repeated full-suite runs without new changes/failures.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Not Started.

### Files Changed

None; task definition only.

### Work Completed

None.

### Validation Results

No implementation validation performed.

### Deviations

Definition authored on main under the user's existing instruction.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox.

### Unresolved Issues

No implementation reported. Explicit dependencies gate execution.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Expected mirrored branch: task/ARCH-020-SHARED-002. Attempt0; no implementation worktree or
commit claimed. At submission record physical isolation, dependency versions,
recursive database submodule evidence where applicable, commits and pushes.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation acceptance.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.
