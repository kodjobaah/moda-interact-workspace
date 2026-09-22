---
id: ARCH-020-COMMERCE-031
architecture_id: ARCH-020
title: Implement external response preview backend
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 150
executor: copilot
claimed_at: 2026-09-22T11:57:58Z
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-019
  - ARCH-020-COMMERCE-009
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-025
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-030
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-22
---

# Implement external response preview backend

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/external-preview/** and narrowly specified preview request/store/lifecycle extensions. Implement raw fixture freezing, syntax/sample services and quotas. No UI or production HTTP/credential resolver.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/external-preview/** and narrowly specified preview request/store/lifecycle extensions. Implement raw fixture freezing, syntax/sample services and quotas. No UI or production HTTP/credential resolver.

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

- [ ] Extend accepted ToolTestBodySchema/ConversationBodySchema/stored preview state with C21 optional external fixtures, preserving old request behavior; freeze exact saved revision/definition/runtime before executing.
- [ ] Implement section9 createExternalPreviewService with validateCode/runSample plus read/cancel delegation to existing lifecycle; use030 sample-validation receipt writer, never a duplicate receipt engine.
- [ ] Enforce authenticated Origin/role, exact tool ownership, Redis distributed admin limits, existing run identity/replay/cancel and bounded preview envelope. Preserve only synthetic samples under existing TTL.
- [ ] Inject025/026 directly with fixture data; assert zero live HTTP/credential/decryption dependencies. Provide actual Redis cross-instance replay/quota/cancel fixtures.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-COMMERCE-019
- ARCH-020-COMMERCE-009
- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-025
- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-030

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024

## Acceptance Criteria

- [ ] PR01: save->sample->processed result->receipt succeeds for text code and visual JSON with actual processors and accepted preview lifecycle.
- [ ] PR02: repeat same run returns original result; changed payload conflicts; cancel/unknown/expiry and two-instance quotas use same identity; changed draft does not alter frozen preview.
- [ ] PR03: old preview request unchanged; invalid foreign fixture ID, unsupported media/oversize, raw HTML and invalid output fail safely; provider/decrypt call counts remain zero.

## Validation

Provide `test:arch020-external-preview` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

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

Expected mirrored branch: task/ARCH-020-COMMERCE-031. Attempt0; no implementation worktree or
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
