---
id: ARCH-020-COMMERCE-024
architecture_id: ARCH-020
title: Integrate external tools connections and Studio
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 170
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-020
  - ARCH-020-COMMERCE-021
  - ARCH-020-COMMERCE-022
  - ARCH-020-COMMERCE-023
  - ARCH-020-COMMERCE-025
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-018
  - ARCH-020-COMMERCE-019
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-027
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-002
created: 2026-09-21
updated: 2026-09-21
---

# Integrate external tools connections and Studio

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/integration/external/** and minimal accepted factory/Server Action/U13 wiring. Assemble accepted components; no replacement business implementations or re-opening base tasks.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/integration/external/** and minimal accepted factory/Server Action/U13 wiring. Assemble accepted components; no replacement business implementations or re-opening base tasks.

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

- [ ] Install027 panels into023 slots; add exact-hash sample receipts and section2.3 validation. Guard publication against stale/expired receipts. Use existing preview lifecycle for saved-revision tests with new optional externalResponseFixture, leaving old requests compatible.

- [ ] Wire real Prisma/keyring connection service, visual processor, sandboxed code engine, raw-response decoder and HTTP executor into accepted backend/publication/Studio/preview boundaries; map section4 service methods to authenticated Server Actions.
- [ ] Implement merchant inspection exclusion for missing credential/disabled connection and same authorization before every call; existing conversation grants never gain new tools/revisions.
- [ ] Freeze exact external connection revision/processing definition in preview while using fixture resolver/transport with no keys or live network, even in Model mode.
- [ ] Prove XN01–04 with real application services, isolated DB and controlled HTTP fixture; expose deterministic integration seed. Explicitly mark EXTERNAL_HTTP uncached for012.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-COMMERCE-020
- ARCH-020-COMMERCE-021
- ARCH-020-COMMERCE-022
- ARCH-020-COMMERCE-023
- ARCH-020-COMMERCE-025
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-018
- ARCH-020-COMMERCE-019
- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-027

## Enables
- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-002


## Acceptance Criteria

- [ ] X07: author JSON or TEXT -> visual/code processing -> schema/test -> publish -> behaviour binding -> release activation -> merchant selection -> MCP call returns only processed external facts.
- [ ] Two merchants with PER_SHOP credentials cannot cross accounts; absent credential excluded; PLATFORM shared access is deliberate; rotation/disable and old revision pinning match C21.
- [ ] Preview and UI cannot read secrets or make live external requests; original Shopify/policy routes still work; current Background descriptors/envelopes remain unchanged.

## Validation

Provide `test:arch020-external-integration` in the owning repository and document its exact scope.
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

Expected mirrored branch: task/ARCH-020-COMMERCE-024. Attempt0; no implementation worktree or
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
