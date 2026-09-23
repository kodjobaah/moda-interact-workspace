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
claimed_at: 2026-09-23T16:59:02Z
attempt: 3
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
- `tests/agent-configuration-model-postgres.test.ts`

### Work Completed

- Added the authenticated Commerce model catalogue CRUD and enablement service.
- Added environment-scoped platform selection and generation/edit-version protected shop override set/clear operations.
- Added durable `CommerceAuditEvent` replay, conflicting-replay, and unknown-outcome handling without provider calls or credential exposure.
- Added typed Studio server actions and focused authorization, bypass, identity, disabled-pointer, replay, and generation-aware CAS tests.
- Corrected all catalogue, platform, and shop writes to claim expected CAS tokens atomically; create/delete races now return `CAS_CONFLICT`.
- Reconciled concurrent `CommerceAuditEvent.id` receipt races by replaying the winning result or returning conflicting replay.
- Added explicit PostgreSQL concurrency coverage for platform first-write CAS, shop first-write CAS, and identical operation replay.

### Validation Results

- `npx vitest run tests/agent-configuration-model.test.ts` passed: 6 tests.
- `COMMERCE_TEST_DATABASE_URL=... npx vitest run tests/agent-configuration-model-postgres.test.ts` passed: 3 tests.
- Targeted ESLint passed for all five task files.
- Task-owned TypeScript diagnostics passed for `src/commerce/agent-configuration`, `src/studio/agent-configuration`, and both focused tests.
- `git diff --check` passed.
- ARCH-021 migration validator applied the accepted schema before the service rehearsal; its unrelated prompt-lineage fixture stopped at an existing fixture assertion after the migration and initial model/schema checks passed. The service-level rehearsal then passed against the isolated migrated database.
- Repository-wide `tsc --noEmit` remains baseline-red in unrelated existing preview/integration paths; no task-owned diagnostics were reported.
- Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-007`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-007`; attempt-2 claim commit `81290db6800f2e0cd617447a6eb121d9269f73f2`; implementation commits `d3252e05710c5eac1be730b058544ad44beda921`, `b79fc72`; database submodule `98fdf715e54fe6df92ac6951facd104e410068f2`.

### Deviations

Architect-requested atomic CAS and concurrent receipt reconciliation are implemented and covered by the PostgreSQL rehearsal above.

### Assumptions

- The accepted Prisma schema and generated client are supplied by the database submodule at the pinned task revision.

### Unresolved Issues

The migration validator's existing prompt-lineage fixture assertion is unrelated to this Commerce service and does not block the service-level PostgreSQL concurrency suite.

### Architectural Concerns

None after the requested rework.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 2 implementation `b79fc72` with parent report `8ae46735` corrects the two concurrency defects from Attempt 1. The catalogue/platform/shop existing-row mutations now claim CAS tokens atomically at the database write boundary; first-write races use create semantics; shop clear uses conditional deletion; and concurrent `CommerceAuditEvent.id = operationId` races reconcile the winning durable receipt. The submitted disposable-PostgreSQL concurrency suite passes 3/3 and directly covers platform first-write CAS, shop first-write CAS and identical concurrent operation replay.

One narrow generation/CAS edge remains before the service can be accepted:

1. **An absent selection row must accept only creation tokens.** When the current platform selection is absent, `setPlatformModel()` must create only when `expectedEditVersion === null`; a stale non-null expected version must return `CAS_CONFLICT` rather than being reinterpreted as a new create. When the current shop override is absent, `setShopModel()` must create only when both `expectedGenerationId === null` and `expectedEditVersion === null`; any stale non-null token from a previously cleared generation must return `CAS_CONFLICT` rather than creating a new generation.

   This preserves the Phase 2 ABA invariant:

   ```text
   generation G1 exists
       -> clear G1
       -> row absent
       -> stale caller still carries G1/editVersion
       -> CAS_CONFLICT
       -> only a caller that actually observed absence may create G2
   ```

   The same principle applies to the platform pointer without a generation token: a stale update token must not become an implicit create merely because another actor removed the current selection first.

The accepted Attempt 2 atomic-write and durable-replay implementation must otherwise remain unchanged. This is a service-concurrency correctness boundary for concurrent/stale clients; it does not require duplicate UI functionality or special multi-tab UI logic.

### Reviewed Files

- `src/commerce/agent-configuration/model-service.ts`
- `src/studio/agent-configuration/model-contracts.ts`
- `src/studio/agent-configuration/model-server-actions.ts`
- `tests/agent-configuration-model.test.ts`
- `tests/agent-configuration-model-postgres.test.ts`
- `src/commerce/connections/command-kernel.ts` (accepted durable replay/CAS reference)
- `database/prisma/schema.prisma` and ARCH-021 generation/CAS guards relevant to model selections

### Validation Reviewed

- Submitted focused unit suite: 6/6 passed.
- Submitted disposable-PostgreSQL concurrency suite: 3/3 passed.
- Submitted targeted ESLint, task-owned TypeScript diagnostics and `git diff --check`: passed.
- Repository-wide TypeScript baseline failures remain unrelated to this task.

Attempt 3 needs only focused proof that an absent platform row rejects a non-null expected edit version and an absent shop row rejects stale non-null generation/edit-version tokens. Exhaustive service or PostgreSQL retesting is not required; preserve the already-passing concurrency suite.

### Architecture Conformance

Partial. Atomic existing-row CAS, first-write race handling, durable concurrent replay, authorization, environment scoping, audit storage and the no-provider-call boundary now conform. The remaining absent-row creation branch must reject stale non-null CAS tokens so the generation-aware ABA contract is complete.

### Follow-up

Return the same task through `/moda-task ARCH-021-COMMERCE-007`. Preserve `attempt: 2`; the next claim becomes Attempt 3. COMMERCE-010 and COMMERCE-011 remain gated until COMMERCE-007 is architect-accepted Complete. COMMERCE-008 remains independent and its separately reviewed state must be preserved during branch reconciliation.
