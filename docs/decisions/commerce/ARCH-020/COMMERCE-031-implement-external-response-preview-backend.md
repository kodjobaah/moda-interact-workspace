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
status: review
priority: 150
executor: null
claimed_at: null
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

Implementation complete for the bounded first slice; submitted for Architect Review with acceptance gaps recorded below.

### Files Changed

- `moda-interact-commerce/src/commerce/external-preview/contracts.ts`
- `moda-interact-commerce/src/commerce/external-preview/service.ts`
- `moda-interact-commerce/src/commerce/external-preview/index.ts`
- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/tests/external-preview.test.ts`
- `moda-interact-commerce/package.json`

### Work Completed

Added bounded optional external response fixtures to conversation/tool-test schemas and stored state, including ownership checking and frozen fixture retention. Added `createExternalPreviewService` with canonical code hash validation, accepted COMMERCE-026 code and COMMERCE-025 visual processor injection, COMMERCE-030 sample-validation/receipt delegation, distributed Redis admin slot, and existing preview replay/conflict result persistence. Added external tool-test completion without live tool execution.

### Validation Results

PR01 partial: `tests/external-preview.test.ts` covers visual JSON processing, receipt-validator delegation, and canonical code validation; `npm run test:arch020-external-preview` passed 3 tests. Adjacent `npm run test:arch020-external-publication` passed 11 tests, `npm run test:arch020-code-processor` passed 6 tests, and focused legacy preview routes/store passed 10 tests. Changed-file ESLint passed. Repository typecheck remains blocked by pre-existing Prisma generation and integration diagnostics; no changed external-preview errors remain.

PR02 partial: external preview replay/conflict is covered in `tests/external-preview.test.ts`; Redis cross-instance quota/cancel/expiry coverage is not yet implemented.

PR03 partial: legacy request compatibility and zero live executor usage are covered by the implementation shape and focused positive test; the required foreign-fixture, unsupported-media, oversize, raw HTML, invalid-output, and explicit zero HTTP/credential/decryption call regressions are not yet covered.

### Deviations

The accepted COMMERCE-030 validator currently returns only a success envelope, so the external preview service independently reprocesses the frozen sample with the accepted 025/026 processors to persist the bounded preview result. The production runtime factory remains owned by the existing preview composition and was not broadened into live external adapters.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox.

### Unresolved Issues

The current slice does not yet provide the complete C21 PR02 Redis race matrix or all PR03 rejection cases. The `runSample` contract requires the saved definition from the caller so COMMERCE-030 can recheck current definition identity; no new definition loader was invented.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Expected mirrored branch: `task/ARCH-020-COMMERCE-031`, attempt 1. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-031`; parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-031`. Dependencies were installed from the committed lockfile for validation. Commit and push evidence is recorded after submission.

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
