---
id: ARCH-020-COMMERCE-020
architecture_id: ARCH-020
title: Implement external connection management service
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 150
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-DATABASE-003
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-002
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
  - ARCH-020-GATEWAY-003
created: 2026-09-21
updated: 2026-09-21
---

# Implement external connection management service

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/connections/** and its service tests. Implement persistence/auth/encryption/replay behind section4 ports. No UI, network calls, shared factories or existing backend composition edits.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/connections/** and its service tests. Implement persistence/auth/encryption/replay behind section4 ports. No UI, network calls, shared factories or existing backend composition edits.

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

- [ ] Consume accepted database submodule revision and published Shared version. Implement every section4 method with exact DTOs/errors, principal checks, Origin at browser adapter boundary and locked CAS.
- [ ] Implement immutable revision creation, per-shop/platform credential resolution, AES-256-GCM/AAD and validated key injection exactly as C21. Expose no secret-bearing DTO.
- [ ] Use audit replay identity/digest and same-transaction business effect; authorization before replay, unique-race winner reconciliation, no action on stale/changed replay.
- [ ] Expose injected server-only resolveConnection port for021; document creation/rotation/missing-key behavior and exact factory exports in docs/external-connections-service.md.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-DATABASE-003
- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-002

## Enables
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024
- ARCH-020-GATEWAY-003


## Acceptance Criteria

- [ ] X03: ADMIN/revoked account denied for writes; duplicate concurrent operation creates one effect/audit; altered replay conflicts; stale CAS leaves rows unchanged.
- [ ] Exact-shop credentials used; no fallback; ciphertext/AAD tampering, wrong key, missing key and disabled connection fail closed without exposing secrets.
- [ ] Two independent database clients prove unique insert and update races; revision creation never copies credentials or changes prior revisions.

## Validation

Provide `test:arch020-external-connections` in the owning repository and document its exact scope.
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

Expected mirrored branch: task/ARCH-020-COMMERCE-020. Attempt0; no implementation worktree or
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
