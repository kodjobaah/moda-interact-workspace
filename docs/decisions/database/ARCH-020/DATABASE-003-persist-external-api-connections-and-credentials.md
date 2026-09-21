---
id: ARCH-020-DATABASE-003
architecture_id: ARCH-020
title: Persist external API connections and encrypted credentials
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 145
executor: copilot
claimed_at: 2026-09-21T15:08:21Z
attempt: 1
depends_on:
  - ARCH-020-DATABASE-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-020
  - ARCH-020-COMMERCE-028
created: 2026-09-21
updated: 2026-09-21
---

# Persist external API connections and encrypted credentials

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own Prisma schema, SQL migrations, generated-client guidance and ERD only. Implement exactly the four models, enums, partial indexes and immutable triggers in C21 section3. Do not implement encryption, HTTP, Studio or application seed data.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own Prisma schema, SQL migrations, generated-client guidance and ERD only. Implement exactly the four models, enums, partial indexes and immutable triggers in C21 section3. Do not implement encryption, HTTP, Studio or application seed data.

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

- [ ] Map every section3 field to Prisma/SQL, retaining existing tables and grants. Add Shop/PlatformAdmin backrelations and RESTRICT relations.
- [ ] Provide migrations for credential scope uniqueness (including NULL platform rows), version/bounds checks and immutable revisions/audit. Encryption bytes are stored opaquely; no plaintext field.
- [ ] Document migration/client-generation consumption for Commerce nested database submodule and rollback limitations; do not copy schema into consumers.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-DATABASE-001

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-020
- ARCH-020-COMMERCE-028

## Acceptance Criteria

- [ ] X02: fresh and existing disposable database migrations succeed without changing existing tool/grant rows.
- [ ] Duplicate platform/shop credential rows, invalid byte lengths, stale immutable updates/deletes and foreign keys fail with expected constraints; transaction rollback leaves zero partial rows.

## Validation

Provide `test:arch020-external-connections:database` in the owning repository and document its exact scope.
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

Expected mirrored branch: task/ARCH-020-DATABASE-003. Attempt0; no implementation worktree or
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
