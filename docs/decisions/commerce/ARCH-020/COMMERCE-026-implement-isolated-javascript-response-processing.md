---
id: ARCH-020-COMMERCE-026
architecture_id: ARCH-020
title: Implement isolated JavaScript response processing
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
  - ARCH-020-SHARED-002
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
  - ARCH-020-GATEWAY-003
created: 2026-09-21
updated: 2026-09-21
---

# Implement isolated JavaScript response processing

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/code-response/**, pinned QuickJS sync WASM/worker packaging and security/resource tests. Implement C21 section2.2 with data-only ports. No UI, credentials, HTTP, production factories or host-evaluated source.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/code-response/**, pinned QuickJS sync WASM/worker packaging and security/resource tests. Implement C21 section2.2 with data-only ports. No UI, credentials, HTTP, production factories or host-evaluated source.

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

- [ ] Implement createCodeResponseProcessor with fresh worker/WASM/runtime per invocation, pinned runtimeVersion and documented exact artifact hashes.
- [ ] Enforce actual finite WASM memory, QuickJS heap/stack, guest interrupt, supervisor deadline and process concurrency caps. Validate recursive output under limits without invoking guest objects on host.
- [ ] Implement source compilation and bounded line/column diagnostics; remove ambient clock/randomness and expose no module loader/host callbacks. No promise/async transform results.
- [ ] Provide syntax, infinite-loop, regex/native-long-operation, allocation, malformed return, proxy/getter/serialization, abort/startup failure and concurrent data-isolation evidence. Sandbox failure must not poison next run.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-SHARED-002

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024
- ARCH-020-GATEWAY-003

## Acceptance Criteria

- [ ] X11: actual packaged WASM/worker tests prove time/memory ceilings and denial of network/process/filesystem/environment/credentials, not mock-only assertions.
- [ ] JSON/text/HTML/XML/CSV text samples can be transformed using documented standard JS; same source/input yields same output; invalid/cyclic/nonfinite/oversized outputs fail.
- [ ] All handles/worker slots released on every terminal path; fifth concurrent invocation throttles; supported runtime/version compiled and documented.

## Validation

Provide `test:arch020-code-sandbox` in the owning repository and document its exact scope.
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

Expected mirrored branch: task/ARCH-020-COMMERCE-026. Attempt0; no implementation worktree or
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
