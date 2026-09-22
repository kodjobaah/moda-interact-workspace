---
id: ARCH-020-COMMERCE-030
architecture_id: ARCH-020
title: Implement external tool publication validation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor: copilot
claimed_at: 2026-09-22T01:39:41Z
attempt: 1
depends_on:
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-003
  - ARCH-020-COMMERCE-021
  - ARCH-020-COMMERCE-025
  - ARCH-020-COMMERCE-026
enables:
  - ARCH-020-COMMERCE-031
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-22
---

# Implement external tool publication validation

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/external-publication/** only. Implement complete external definition validation, exact-hash sample receipts and publication admission ports. No UI, preview lifecycle/routes, final factories or provider HTTP.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/external-publication/** only. Implement complete external definition validation, exact-hash sample receipts and publication admission ports. No UI, preview lifecycle/routes, final factories or provider HTTP.

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

- [ ] Export section9 createExternalPublicationValidation with validateForPublication/validateSampleAndRecord/readReceipt and injected connection metadata, compiler/processor and receipt store ports.
- [ ] Derive output wrapper/template schema; validate visual projection or code syntax/runtime and sample output before issuing receipt. No additional network call or guessed output schema.
- [ ] Implement Redis receipt store/TTL/key hash and active tester checks; changed definition/sample outcomes never reuse stale success. Keep sample data/source out of receipt.
- [ ] Provide real-validator sample->receipt->publication positive test plus stale/expired/unavailable and semantically invalid template tests.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-003
- ARCH-020-COMMERCE-021
- ARCH-020-COMMERCE-025
- ARCH-020-COMMERCE-026

## Enables

- ARCH-020-COMMERCE-031
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024

## Acceptance Criteria

- [ ] PV01: saved external tool with valid sample receives exact definition/runtime receipt and passes full publication admission; both visual and code modes covered.
- [ ] PV02: missing/expired/changed-hash/inactive-author receipt or Redis outage blocks; invalid schema/template/projection/syntax performs zero publication writes.
- [ ] PV03: altered real response later fails same schema validation; published receipt is never treated as permission to skip runtime validation.

## Validation

Provide `test:arch020-external-publication` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

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

Review; implementation committed and pushed for moda_architect review.

### Files Changed

- `moda-interact-commerce/src/commerce/external-publication/contracts.ts`
- `moda-interact-commerce/src/commerce/external-publication/index.ts`
- `moda-interact-commerce/src/commerce/external-publication/receipt-store.ts`
- `moda-interact-commerce/tests/external-publication.test.ts`
- `moda-interact-commerce/package.json`

### Work Completed

- Added typed `createExternalPublicationValidation` ports for saved-definition identity, connection metadata, compiler, visual/code processors, staff authorization, clock and digest injection.
- Implemented strict definition/sample bounds, visual and JavaScript sample processing, result-schema validation, semantic template validation, and no-network sample admission.
- Implemented Redis receipt storage with environment/revision/definition/runtime key binding, 24-hour TTL, bounded receipt fields, inactive-staff rejection and fail-closed unavailable handling.
- Added visual and code positive paths plus missing, unavailable, inactive, changed-hash, invalid-template and receipt-store regression scenarios.

### Validation Results

| Criterion | Test / command | Observable result |
|---|---|---|
| PV01 visual | `tests/external-publication.test.ts` / `records a real visual sample receipt and admits the matching definition`; `npm run test:arch020-external-publication` | Passed; receipt contains revision, runtime and tester binding and matching admission returns `ok: true`. |
| PV01 code | `tests/external-publication.test.ts` / `records a code-mode sample receipt through the injected processor`; same command | Passed; injected code processor path records `quickjs-sync.v1` receipt. |
| PV02 rejection | `tests/external-publication.test.ts` / `blocks missing, unavailable, inactive, and changed-hash receipts`; same command | Passed; missing/stale/inactive block and receipt outage returns `VALIDATOR_UNAVAILABLE`. |
| PV02 invalid definition | `tests/external-publication.test.ts` / `rejects a semantically invalid template before writing a receipt`; same command | Passed; no receipt write occurs. |
| Receipt bounds | `tests/external-publication.test.ts` / `stores only bounded receipt data under the environment and hash key with a TTL`; same command | Passed; environment/hash key, `86400` TTL and receipt-only payload verified. |
| Focused lint | `npx eslint src/commerce/external-publication/*.ts tests/external-publication.test.ts` | Passed with no warnings/errors. |
| Task-local diagnostics | VS Code diagnostics for all changed implementation/test files | No errors. |
| Repository typecheck | `npm run typecheck` | Still fails on unrelated existing Prisma/integration diagnostics; no `external-publication` diagnostics remain. |

Developer-owned PostgreSQL/container checks were not run; this task owns Redis receipt/admission ports and has no migration scope.

### Deviations

No scope deviation. The accepted Shared `validateDefinitionForPublication` helper is used for strict definition/template admission; provider HTTP, preview lifecycle, UI and final factories remain out of scope.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript are executed by the injected accepted processors. The saved-definition and connection ports are supplied by their owning lifecycle/credential implementations.

### Unresolved Issues

The full repository typecheck remains blocked by baseline Prisma generated-client and integration typing errors outside COMMERCE-030. Real Redis/PostgreSQL deployment checks remain developer-owned follow-up evidence.

### Architectural Concerns

Receipt creation is intentionally limited to successful sample processing and schema/template validation. Publication admission never treats a receipt as a substitute for fresh definition, compiler, schema or connection checks.

### Git / VCS

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-030`; physical isolation confirmed by launcher. Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-030`.

Preparation packet: dependency gate passed for SHARED-002, COMMERCE-003, COMMERCE-021, COMMERCE-025 and COMMERCE-026; recursive database submodule sync/update passed at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.

Implementation commit: `59f0c34` (`feat(commerce): validate external publication samples`), pushed to `origin task/ARCH-020-COMMERCE-030`.

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
