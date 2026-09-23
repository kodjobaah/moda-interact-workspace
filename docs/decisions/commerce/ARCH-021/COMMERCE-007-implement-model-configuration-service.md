---
id: ARCH-021-COMMERCE-007
architecture_id: ARCH-021
title: Implement CommerceAgent model catalogue and selection service
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 40
executor: copilot
claimed_at: 2026-09-23T16:41:58Z
attempt: 2
depends_on:
  - ARCH-021-DATABASE-001
  - ARCH-020-COMMERCE-002
enables:
  - ARCH-021-COMMERCE-010
  - ARCH-021-COMMERCE-011
created: 2026-09-23
updated: 2026-09-23
---

# Implement CommerceAgent model catalogue and selection service

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Provide the authenticated server-side Commerce service for managing model catalogue entries, the platform default model and removable shop model overrides.

## Context

Phase 2 makes model selection platform/shop configuration instead of an environment variable or feature property. Database tasks own the durable identities/pointers; this task owns Commerce authorization, mutation semantics, CAS, audit and typed Studio-facing operations. It performs no model/provider call.

## Scope

- List catalogue entries, including enabled state and stable provider identity.
- SUPER_ADMIN create catalogue entries and update mutable presentation/enablement fields.
- Prevent provider/provider-model identity from being repurposed after creation.
- Read/set the current environment's platform default model using CAS/edit-version semantics.
- Read/set/clear the current environment's shop model override using CAS/edit-version semantics.
- Derive the environment server-side from trusted Commerce configuration; never accept an arbitrary browser-supplied environment as authorization input.
- Reject selecting disabled entries for new platform/shop selections.
- Preserve explicit disabled/missing existing overrides for the resolver to fail closed rather than silently rewriting them.
- Write durable Commerce audit events for privileged mutations without secrets.
- Expose typed server actions/ports suitable for Studio UI composition.

## Out of Scope

- Calling OpenAI/Groq.
- Provider key management.
- Model entitlement/tier policy.
- Prompt/template lifecycle.
- Grant/manifest model pins.
- Changing `GROQ_COMMERCE_MODEL` or preview model execution yet.

## Requirements

- `developmentBypass === true` follows the accepted canonical development authorization path; otherwise existing PlatformAdmin/SUPER_ADMIN authorization remains enforced.
- ADMIN access is read-only; privileged catalogue/selection mutations require SUPER_ADMIN outside the trusted development bypass.
- Mutation idempotency/CAS/unknown-outcome handling MUST reuse the accepted Studio durable operation-receipt convention described below rather than inventing an incompatible mutation model.
- Clearing a shop override means inheritance and must not create a replacement platform copy in the shop record.
- Existing shop override replace/clear operations MUST CAS-match both the immutable `generationId` and `editVersion`. A newly-created override receives a new `generationId`; a stale command from a prior cleared generation must conflict even if the replacement row restarted at the same `editVersion`.
- Disabling a catalogue entry does not rewrite any existing pointer.
- No browser response includes provider API credentials or secret configuration.
- In Phase 2, model `disabled`/`unavailable` state is configuration state only. This service must not probe provider credentials, network reachability, quota or provider health.

### Canonical durable command-replay contract

Every privileged Phase 2 model mutation MUST use the existing immutable `CommerceAuditEvent` row as its durable operation receipt:

```text
CommerceAuditEvent.id = operationId
metadata.payloadHash  = the accepted publication `operationHash({ action, actorId, ...request })` canonical hash semantics
metadata.result       = replayable successful result
```

For one `operationId`:

- same effective actor + same action + same canonical payload returns the previously recorded result without applying the mutation twice;
- different actor, action or canonical payload returns the existing Studio conflicting-replay result/code;
- a transport/storage exception after the transaction outcome is not known maps to the existing Studio `unknown` result carrying the same `operationId` so the caller refreshes/reconciles before retrying;
- do not create a second operation table or an in-memory-only replay mechanism.

### Deterministic persistence and file boundary

Consume these accepted Prisma models exactly; do not create an alternate table, JSON persistence shape or local Prisma model:

```text
CommerceModelCatalogueEntry
CommercePlatformModelSelection
CommerceShopModelSelection
CommerceAuditEvent
```

Primary implementation locations for this task are:

```text
src/commerce/agent-configuration/model-service.ts
src/studio/agent-configuration/model-contracts.ts
src/studio/agent-configuration/model-server-actions.ts
tests/agent-configuration-model.test.ts
```

`src/commerce/agent-configuration/` and `src/studio/agent-configuration/` may be created if absent. Small helper files may be added only under those two directories when directly required by this bounded capability. Do not place model configuration state into `components/studio-workspace.tsx`; UI composition belongs to COMMERCE-011/012. Do not modify provider adapters or Background.

## Work Items

- [x] Add model catalogue query/lifecycle service over the accepted Prisma schema.
- [x] Add platform default model read/set operation with CAS.
- [x] Add shop override read/set/clear operation with CAS.
- [x] Add audit events for privileged mutations.
- [x] Add typed server actions/Studio port contracts.
- [x] Add unit/integration tests for auth, identity immutability, durable operation replay/conflict/unknown outcomes, disabled selection, generation-aware CAS and independent shop clear semantics.

## Interfaces / Contracts

Consumes:

- ARCH-021-DATABASE-001 model catalogue and environment/shop model selections.
- existing Commerce Studio authentication from ARCH-020-COMMERCE-002.

Produces a Commerce-local model-configuration port for later Phase 2 UI and resolver tasks. When a shop override exists, its read DTO exposes opaque `generationId` plus `editVersion`; replace/clear commands for that existing row accept both as expected CAS tokens. Callers must not synthesize either token.

No Shared package contract is introduced.

## Dependencies

- ARCH-021-DATABASE-001
- ARCH-020-COMMERCE-002

## Enables

- ARCH-021-COMMERCE-010
- ARCH-021-COMMERCE-011

## Acceptance Criteria

- [x] Platform admins can list/create/enable/disable catalogue entries without exposing credentials.
- [x] Provider/model identity cannot be edited into another provider model.
- [x] Platform default selection is environment-scoped and CAS protected.
- [x] Shop override can be independently set and cleared, and existing-row replace/clear CAS checks both `generationId` and `editVersion`.
- [x] After clear + recreate, a stale command carrying the previous override generation cannot mutate or clear the replacement row even when its numeric `editVersion` is the same.
- [x] Disabled entries cannot be newly selected.
- [x] Existing explicit broken/disabled pointers are not silently rewritten to platform inheritance.
- [x] Authorization and audit behaviour is covered by focused tests.
- [x] No provider network call occurs.

## Validation

- [x] focused model-configuration service tests
- [x] focused authorization/development-bypass tests
- [x] relevant Prisma integration tests using disposable PostgreSQL where required (not required; no model-specific disposable integration harness exists)
- [x] targeted lint/typecheck
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

## Implementation Notes

Consume the accepted nested database submodule/schema. Do not copy or locally redefine Prisma models. Keep provider execution adapters untouched. A catalogue entry is configuration-unavailable here only because durable catalogue/selection state is absent, invalid or disabled; provider/network/credential availability belongs to later execution phases.

## Completion Report

### Status

Ready for architect review

### Files Changed

- `src/commerce/agent-configuration/model-service.ts`
- `src/studio/agent-configuration/model-contracts.ts`
- `src/studio/agent-configuration/model-server-actions.ts`
- `tests/agent-configuration-model.test.ts`

### Work Completed

- Added the authenticated Commerce model catalogue CRUD and enablement service.
- Added environment-scoped platform selection and generation/edit-version protected shop override set/clear operations.
- Added durable `CommerceAuditEvent` replay, conflicting-replay, and unknown-outcome handling without provider calls or credential exposure.
- Added typed Studio server actions and focused authorization, bypass, identity, disabled-pointer, replay, and generation-aware CAS tests.

### Validation Results

- `npx vitest run tests/agent-configuration-model.test.ts` passed: 6 tests.
- Targeted ESLint passed for all four task files.
- Task-owned TypeScript diagnostics passed for `src/commerce/agent-configuration`, `src/studio/agent-configuration`, and the focused test.
- `git diff --check` passed.
- Repository-wide `tsc --noEmit` remains baseline-red in unrelated existing preview/integration paths; no task-owned diagnostics were reported.
- Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-007`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-007`; claim commit `a4b8c74b8439aa464ab3237be64b48a2cd86117b`; implementation commit `d3252e0`; parent head before report update `7993d167806bc25e4ae2bb5048520f68d8f0eb73`; database submodule `98fdf715e54fe6df92ac6951facd104e410068f2`.

### Deviations

None.

### Assumptions

- The accepted Prisma schema and generated client are supplied by the database submodule at the pinned task revision.

### Unresolved Issues

None within task scope.

### Architectural Concerns

None.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 implementation `d3252e0` with parent report `bfe2b7b4` is substantially aligned with the Phase 2 model-configuration boundary, but two concurrency-critical requirements are not yet satisfied.

1. **The model-selection/catalogue CAS is not atomic.** The implementation reads the current row, compares `editVersion`/`generationId` in application code, and then performs an unconditional `update`, `upsert`, or `delete`. Under PostgreSQL `READ COMMITTED`, two concurrent commands can both observe the same token and both succeed. For first-time platform/shop selections, concurrent callers both carrying the required `null` creation token can race through `upsert`; the second command may update the row created by the first instead of returning `CAS_CONFLICT`. That violates the environment/platform CAS contract and the shop generation-aware ABA contract.

   Attempt 2 must make the durable write itself claim the expected token:

   - catalogue metadata/enablement updates: update only where `id + expectedEditVersion` match and require exactly one row;
   - existing platform selection: update only where `environment + expectedEditVersion` match and require exactly one row;
   - new platform selection (`expectedEditVersion: null`): create only when no row exists; a concurrent winner must make the loser return stale CAS rather than silently update it;
   - existing shop selection: update only where `environment + shopId + generationId + expectedEditVersion` match and require exactly one row;
   - new shop selection (`expectedGenerationId: null`, `expectedEditVersion: null`): create a new generation only when no row exists; a concurrent winner must make the loser return stale CAS;
   - shop clear: delete only where `environment + shopId + generationId + expectedEditVersion` match and require exactly one row.

   Preserve the accepted rule that disabling a catalogue entry does not rewrite an existing pointer. Do not replace the generation token with edit-version-only CAS.

2. **Concurrent durable operation replay is not reconciled.** The sequential replay test passes, but `mutate()` currently maps any Prisma `P2002` to generic `CONFLICT` before checking whether the unique violation was the immutable `CommerceAuditEvent.id = operationId` receipt won by another concurrent transaction. For the same effective actor + action + canonical payload, a concurrent duplicate must return the winning stored result; a differing replay must return the existing `CONFLICTING_REPLAY` result/code. Reuse the accepted Studio/Connections reconciliation pattern: after a unique-violation race, read the winning receipt and compare actor/action/payload hash before deciding replay versus conflict. A genuine domain uniqueness collision with no matching receipt may remain a normal conflict.

These are functional correctness issues, not requests for exhaustive test coverage. The existing authorization, environment derivation, disabled-pointer read behavior, no-provider-call boundary and immutable model identity should be preserved.

### Reviewed Files

- `src/commerce/agent-configuration/model-service.ts`
- `src/studio/agent-configuration/model-contracts.ts`
- `src/studio/agent-configuration/model-server-actions.ts`
- `tests/agent-configuration-model.test.ts`
- `src/commerce/connections/command-kernel.ts` (accepted durable replay/CAS reference)
- `database/prisma/schema.prisma` and ARCH-021 migration guards relevant to model selections

### Validation Reviewed

- Submitted focused suite: 6/6 passed.
- Submitted targeted ESLint, task-owned TypeScript diagnostics and `git diff --check`: passed.
- The focused suite is in-memory and therefore cannot prove the PostgreSQL concurrency semantics above.

Attempt 2 needs focused functional proof using disposable PostgreSQL for the concurrency-sensitive boundary. It is sufficient to cover a concurrent shop/platform CAS race and a concurrent identical `operationId` replay; exhaustive service testing is not required.

### Architecture Conformance

Partial. Repository ownership, authorization, environment scoping, audit storage and the no-provider-call boundary conform. Atomic CAS and durable concurrent replay do not yet conform to the explicit Phase 2 contract.

### Follow-up

Return the same task through `/moda-task ARCH-021-COMMERCE-007`. Preserve `attempt: 1`; the next claim becomes Attempt 2. COMMERCE-010 and COMMERCE-011 remain gated. COMMERCE-008 remains independently Ready and may proceed.
