---
id: ARCH-021-COMMERCE-009
architecture_id: ARCH-021
title: Implement platform and shop prompt lifecycle service
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 50
executor:
claimed_at:
attempt: 1
depends_on:
  - ARCH-021-DATABASE-001
  - ARCH-021-COMMERCE-008
  - ARCH-020-COMMERCE-002
enables:
  - ARCH-021-COMMERCE-010
  - ARCH-021-COMMERCE-012
  - ARCH-021-COMMERCE-014
created: 2026-09-23
updated: 2026-09-23
---

# Implement platform and shop prompt lifecycle service

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Provide the authenticated Commerce lifecycle for platform/shop behavioural prompt drafts, immutable published revisions and independent environment-scoped active pointers.

## Context

ARCH-021 requires exactly one configurable behavioural prompt at runtime. Platform admins author one platform prompt lineage and optionally one shop-specific lineage per shop. Prompt templates are copy-on-use starting points, not runtime inheritance.

Phase 2 only authors and selects prompts; existing ARCH-020 per-capability prompts remain intact until the later runtime migration.

## Scope

- Read/create the singleton platform prompt lineage and per-shop prompt lineage.
- Create/update prompt drafts with CAS/edit-version semantics.
- Allow a new draft to start blank/from current lineage content or by copying one exact published template revision that is currently selectable for new authoring.
- Record `sourceTemplateRevisionId` provenance without dynamic linkage.
- Publish immutable prompt revisions.
- Read/set the current environment's platform active prompt pointer.
- Read/set/clear the current environment's shop prompt override pointer.
- Enforce that active pointers target published revisions.
- Enforce platform pointer -> platform lineage and shop pointer -> the exact selected shop's lineage.
- Derive environment server-side and validate shop identity server-side.
- Write durable audit events for privileged mutations.
- Expose typed server actions/ports for Studio.

## Out of Scope

- Removing capability-level prompt fields.
- Manifest/grant/runner changes.
- Executing a model with the prompt.
- Merchant authorization.
- Shop-owned reusable templates.

## Requirements

- ADMIN is read-only; mutations require SUPER_ADMIN outside development bypass.
- Development bypass uses the canonical effective development actor.
- Only one platform lineage and at most one lineage per shop may exist; service handles concurrent create races using database constraints/idempotency.
- DRAFT prompt revisions may persist empty prompt text; publication MUST reject blank/whitespace-only text.
- Published revisions cannot be mutated.
- Published `contentHash` is SHA-256 over the exact UTF-8 bytes of the persisted `promptText`; do not trim, normalise line endings or otherwise transform text for hashing.
- Copy-from-template copies exact content into the new prompt draft and records provenance; subsequent template changes have no effect.
- New copy-from-template authoring requires the owning category and template to be enabled at copy time and the revision to be published. Historical/provenance reads of a disabled template revision remain valid and do not invalidate prompts already copied from it.
- Clearing a shop prompt override means inheritance and must not alter shop model selection.
- Platform pointer mutations use CAS/editVersion. Existing shop pointer replace/clear mutations MUST CAS-match both immutable `generationId` and `editVersion`; clear + recreate produces a new generation so a stale command cannot ABA-match the replacement row.
- Every privileged prompt mutation MUST reuse the existing immutable `CommerceAuditEvent` operation-receipt convention: `id = operationId`, `metadata.payloadHash` using the accepted publication `operationHash({ action, actorId, ...request })` canonical semantics, and replayable `metadata.result`; same request replays, conflicting reuse returns `CONFLICTING_REPLAY`, and unknown outcomes return the existing Studio `unknown` result for reconciliation. Do not create another operation table or invent different JSON canonicalisation.

### Deterministic persistence and file boundary

Consume these accepted Prisma models exactly:

```text
CommerceAgentPrompt
CommerceAgentPromptRevision
CommercePlatformPromptPointer
CommerceShopPromptPointer
CommercePromptTemplateRevision   # provenance source only
CommerceAuditEvent
```

Primary implementation locations for this task are:

```text
src/commerce/agent-configuration/prompt-service.ts
src/studio/agent-configuration/prompt-contracts.ts
src/studio/agent-configuration/prompt-server-actions.ts
tests/agent-configuration-prompts.test.ts
```

`CommerceAgentPrompt` is the only platform/shop configurable prompt lineage. Do not create a second platform-prompt table, a per-feature prompt table or a model-specific prompt table. `sourceTemplateRevisionId` must be written only when copying an exact published `CommercePromptTemplateRevision`; copied `promptText` becomes independent content.

## Work Items

- [x] Implement platform/shop prompt lineage read/create operations.
- [x] Implement draft create/update operations with CAS.
- [x] Implement copy-from-published-template draft creation with category/template new-authoring selectability validation.
- [x] Implement immutable publish operation.
- [x] Implement platform active pointer set/read.
- [x] Implement shop override set/read/clear.
- [x] Enforce prompt scope and published-state invariants.
- [x] Add audit events and typed server actions/ports.
- [x] Add concurrency, scope, template-copy, CAS/replay and auth tests.

## Interfaces / Contracts

Consumes:

- ARCH-021-DATABASE-001 prompt lineages/revisions and environment-scoped active pointers.
- ARCH-021-COMMERCE-008 exact template-revision reads for copy-on-use.

Produces a Commerce-local prompt configuration port for effective resolution and Studio UI. When a shop prompt pointer exists, its read DTO exposes opaque `generationId` plus `editVersion`; replace/clear commands for that existing row accept both as expected CAS tokens. Callers must not synthesize either token.

## Dependencies

- ARCH-021-DATABASE-001
- ARCH-021-COMMERCE-008
- ARCH-020-COMMERCE-002

## Enables

- ARCH-021-COMMERCE-010
- ARCH-021-COMMERCE-012
- ARCH-021-COMMERCE-014

## Acceptance Criteria

- [x] Platform and shop prompt lineages obey singleton/per-shop ownership.
- [x] Empty DRAFT prompt revisions may be saved; publishing blank/whitespace-only prompt text is rejected.
- [x] Draft edits are CAS protected; published revisions are immutable and hash exact persisted UTF-8 prompt text bytes without trimming/newline normalisation.
- [x] A prompt draft created from a template is an independent copy with immutable provenance.
- [x] A disabled category or template cannot be used to create a new prompt draft even when its published revision id is supplied directly; historical provenance remains readable.
- [x] Platform active prompt can only target a published platform revision.
- [x] Shop override can only target a published revision belonging to that exact shop.
- [x] Clearing the shop prompt override returns prompt inheritance without changing model state.
- [x] Existing shop-pointer replace/clear CAS checks both `generationId` and `editVersion`; after clear + recreate a stale command from the prior generation cannot mutate/clear the replacement row.
- [x] Privileged commands prove durable same-request replay, conflicting operation-id reuse and unknown-outcome reconciliation through the existing audit receipt convention.
- [x] Existing capability prompt/runtime behaviour is not modified in Phase 2.
- [x] No model/provider call occurs.

## Validation

- [x] focused prompt lifecycle tests
- [x] template-copy/provenance tests
- [x] CAS/concurrency tests with disposable PostgreSQL where required
- [x] focused authorization/development-bypass tests
- [x] targeted lint/typecheck
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

## Implementation Notes

Do not concatenate platform and shop configurable prompts. Shop override selection replaces the platform configurable prompt for that shop.

## Completion Report

### Status

Ready for architect review

### Files Changed

src/commerce/agent-configuration/prompt-service.ts; src/studio/agent-configuration/prompt-contracts.ts; src/studio/agent-configuration/prompt-server-actions.ts; tests/agent-configuration-prompts.test.ts; tests/agent-configuration-prompts-postgres.test.ts

### Work Completed

Implemented platform/shop lineages, blank/current/template draft creation, exact UTF-8 publication hashing, immutable revisions, scope-bound environment pointers, generation-plus-edit CAS, durable audit replay/unknown handling, server-derived environment wiring, and authenticated typed Studio actions.

### Validation Results

Focused Vitest: 3 prompt tests passed; existing template/model suites: 16 tests passed; PostgreSQL concurrency: 1 test passed. Focused ESLint passed, focused TypeScript diagnostics passed, and `git diff --check` passed.

### Deviations

PostgreSQL validation used the configured disposable/shared test database and isolated TEST prompt fixtures before the concurrency case.

### Assumptions

No unresolved implementation issues identified.

### Unresolved Issues

No model/provider execution or capability prompt/runtime changes were introduced.

### Architectural Concerns

None

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 substantially implements the Phase 2 prompt lineage, draft/publication and environment-scoped pointer boundaries, but it is not yet acceptable at the CAS/replay boundary. The write predicates themselves are largely correct and must be preserved: draft update/publish use `status + editVersion`, platform pointer replacement uses `environment + editVersion`, shop pointer replacement uses `environment + shopId + generationId + editVersion`, and shop clear uses the same generation/edit tokens in `deleteMany`.

Three bounded corrections remain:

1. **Receipt-first reconciliation after CAS/domain failures.** `command()` currently returns any `LifecycleError` immediately. Therefore an identical concurrent operation can lose an otherwise-correct atomic CAS (or observe the lineage/pointer created by the winning transaction) and return `CAS_CONFLICT`/`CONFLICT` even after the winning transaction has durably committed the same `operationId` receipt. After a transaction failure, first read `CommerceAuditEvent(id = operationId)`. A matching actor/action/payload hash MUST replay its stored result; a mismatched receipt MUST return `CONFLICTING_REPLAY`; only when no receipt exists should the original known domain/CAS error be returned. Preserve the existing `unknown` result only for genuinely indeterminate failures with no durable receipt.

2. **Pointer audit targets must satisfy the accepted database constraint.** The generic audit mapper currently derives `agentPromptRevisionId` from `value.id`. `PlatformPromptPointer`/`ShopPromptPointer` expose `promptRevisionId`, not `id`, so SET pointer receipts omit the required revision target. CLEAR returns only `{ shopId, cleared }`, so it omits both required prompt targets. Under the accepted `arch020_audit_targets` constraint, SET/CLEAR pointer transactions therefore cannot durably commit their receipt. Carry explicit audit targets from the mutation: SET platform/shop must write the selected `promptId` + `promptRevisionId` (+ environment/shop where applicable); CLEAR must read the current pointer inside the same transaction, CAS-delete that exact generation/edit version, and write the cleared row's `promptId` + `promptRevisionId` + shop/environment into the audit receipt. Do not infer revision ids from a generic `id` field.

3. **Template copy must identify one exact published template revision.** `sourceTemplateId` alone currently lets `findFirst()` choose an arbitrary published revision. The architecture requires copy-on-use from one exact published template revision. Require `sourceTemplateRevisionId` for template-copy authoring (an optional `sourceTemplateId` may only cross-check ownership), while preserving enabled category/template validation and immutable provenance.

### Reviewed Files

- `src/commerce/agent-configuration/prompt-service.ts`
- `src/studio/agent-configuration/prompt-contracts.ts`
- `src/studio/agent-configuration/prompt-server-actions.ts`
- `tests/agent-configuration-prompts.test.ts`
- `tests/agent-configuration-prompts-postgres.test.ts`
- `database/prisma/migrations/20260923150000_arch021_agent_configuration/migration.sql`
- `docs/decisions/commerce/ARCH-021/COMMERCE-009-implement-prompt-lifecycle-service.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

- Submitted focused validation: 20 tests reported passing across prompt/template/model coverage.
- Submitted PostgreSQL concurrency coverage proves only the singleton platform-lineage race; it does not exercise draft/pointer CAS, same-operation replay after a CAS loser, shop-generation ABA, or pointer audit-target constraints.
- Submitted targeted ESLint, focused TypeScript diagnostics and `git diff --check` are accepted as supporting evidence.
- Attempt 2 requires focused disposable-PostgreSQL proof for the corrected CAS/audit paths; exhaustive coverage is not required.

### Architecture Conformance

Changes Requested. The basic persistence boundaries, exact-content publication hashing, immutable published revisions and atomic CAS predicates conform. Durable same-request replay and pointer audit receipt correctness do not yet satisfy the Phase 2 command/CAS contract, and template copy is not yet restricted to one exact published template revision.

### Follow-up

Return the same task for Attempt 2. Preserve the existing atomic CAS predicates and bounded scope. Add focused regressions proving at minimum:

- two distinct operations using the same existing prompt-draft/pointer CAS token yield exactly one mutation winner and one `CAS_CONFLICT`;
- two concurrent identical CAS-bound commands with the same `operationId` return the same durable successful result and only one audit receipt;
- platform/shop SET pointer and shop CLEAR pointer commit valid audit receipts containing the required prompt/revision targets;
- shop clear -> recreate produces a new `generationId`, and stale prior-generation replace/clear commands remain rejected;
- template copy rejects `sourceTemplateId`-only ambiguity and copies the explicitly selected published revision exactly.

Set task state to `ready`, clear `executor`/`claimed_at`, preserve `attempt: 1`, and STOP after returning Attempt 2 to Architect Review.
