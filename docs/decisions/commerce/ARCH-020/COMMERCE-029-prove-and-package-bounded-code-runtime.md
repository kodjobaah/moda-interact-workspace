---
id: ARCH-020-COMMERCE-029
architecture_id: ARCH-020
title: Prove and package bounded code runtime
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 150
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-001
enables:
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-012
  - ARCH-020-GATEWAY-003
created: 2026-09-21
updated: 2026-09-21
---

# Prove and package bounded code runtime

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/code-response/runtime/**, runtime artifact/build manifest and minimal direct runtime tests. Deliver a reusable bounded QuickJS worker kernel, not a paper evaluation or throwaway prototype. No Shared schemas, business validation, UI or production factory wiring.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/code-response/runtime/**, runtime artifact/build manifest and minimal direct runtime tests. Deliver a reusable bounded QuickJS worker kernel, not a paper evaluation or throwaway prototype. No Shared schemas, business validation, UI or production factory wiring.

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

- [ ] Build/pin the synchronous QuickJS WASM variant with enforceable finite memory maximum and worker entry; record dependency/artifact hashes and supported runtime profile quickjs-sync.v1.
- [ ] Implement the section9 SandboxKernel compile/run entry points and bounded JSON-text result. Prove C21 memory/time/abort/concurrency constraints with real execution.
- [ ] Run positive text transform, infinite-loop, built-in long operation, allocation/serialization attack, forbidden capability and post-failure recovery scenarios before architecture acceptance.
- [ ] Publish docs/code-runtime-proof.md with actual limits/results and artifact loading in the repository production build; if a required limit is not enforceable report that concrete gap and do not mark Complete or weaken it.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-COMMERCE-001

## Enables

- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-012
- ARCH-020-GATEWAY-003

## Acceptance Criteria

- [ ] SB01: actual pinned worker/WASM executes synthetic transform and produces exact output; production build can load bundled artifact without network download.
- [ ] SB02: heap/stack/WASM maximum and supervisor termination are demonstrated, including infinite loop and memory pressure; process remains usable afterward.
- [ ] SB03: no guest network/filesystem/environment/module loader; distinct concurrent inputs remain isolated; fifth run throttles; slots/handles reclaimed on every terminal path.

## Validation

Provide `test:arch020-code-runtime-proof` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

Use focused checks while implementing, then existing typecheck/build/lint where defined. Record unrun developer-owned PostgreSQL/container checks accurately; executable scenarios must still exist. No repeated unrelated full suites or screenshot quotas. No live credentials/WhatsApp delivery.

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

Expected mirrored branch: task/ARCH-020-COMMERCE-029. Attempt0; no implementation worktree or
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
