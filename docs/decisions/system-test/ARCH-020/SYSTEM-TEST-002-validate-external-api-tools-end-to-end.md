---
id: ARCH-020-SYSTEM-TEST-002
architecture_id: ARCH-020
title: Validate external API tools end to end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 198
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-024
  - ARCH-020-GATEWAY-003
  - ARCH-020-BACKGROUND-002
enables:
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-21
updated: 2026-09-21
---

# Validate external API tools end to end

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Manual invocation only. Own system-test fixtures and cross-service tests for this extension; no provider/application implementation. Use actual Background and Commerce with controlled provider/model and isolated stores.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Manual invocation only. Own system-test fixtures and cross-service tests for this extension; no provider/application implementation. Use actual Background and Commerce with controlled provider/model and isolated stores.

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

- [ ] Execute X09 with published external tool and unchanged Background discovery/tool-call/final-response flow; record exact Shared/Commerce/Background/database revisions.
- [ ] Cover platform and per-shop connections, two simultaneous shops, disabled/missing/rotated credentials, old conversation pins and denial after revocation.
- [ ] Exercise visual projection and JSON/plain-text/HTML/XML/CSV code samples, including schema errors, loop/allocation attacks and abort; discarded upstream fields never reach model input. Preview asserts zero provider calls/decrypts and processing is same pure engine.
- [ ] Prove original Shopify tools and language/referral behavior coexist; avoid real customer data/WhatsApp delivery and distinguish unrun hosted checks.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-COMMERCE-024
- ARCH-020-GATEWAY-003
- ARCH-020-BACKGROUND-002

## Enables
- ARCH-020-SYSTEM-TEST-001


## Acceptance Criteria

- [ ] X09 and XN01–03 pass on assembled services; Background has no external-service credentials or hard-coded operation handler.
- [ ] No user-supplied identity changes credential selection, new releases cannot add tools to existing grants, unknown external facts refer rather than fabricate.
- [ ] Evidence uses real HTTP execution boundary/isolated PostgreSQL and existing Redis where needed; build/fixtures alone do not claim end-to-end acceptance.

## Validation

Provide `test:arch020-external-e2e` in the owning repository and document its exact scope.
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

Expected mirrored branch: task/ARCH-020-SYSTEM-TEST-002. Attempt0; no implementation worktree or
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
