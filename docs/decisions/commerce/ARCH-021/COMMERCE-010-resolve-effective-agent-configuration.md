---
id: ARCH-021-COMMERCE-010
architecture_id: ARCH-021
title: Resolve effective platform/shop CommerceAgent configuration
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 60
executor: copilot
claimed_at: 2026-09-23T20:00:39Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-003
  - ARCH-021-COMMERCE-007
  - ARCH-021-COMMERCE-009
enables:
  - ARCH-021-COMMERCE-012
created: 2026-09-23
updated: 2026-09-23
---

# Resolve effective platform/shop CommerceAgent configuration

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Provide one deterministic server-side resolver that returns the effective model and effective configurable prompt for a selected shop using independent shop-override -> platform-default fallback.

## Context

Model and prompt ownership are independent. Phase 2 UI needs to show both the effective value and its source before later preview/runtime phases freeze the same identities. The resolver must not yet create grants/manifests or execute providers.

## Scope

- Resolve the trusted current `CommerceEnvironment` server-side.
- Validate/resolve the requested Commerce shop id using the accepted shop execution context.
- Resolve model: explicit shop override when present, otherwise platform default.
- Resolve prompt: explicit shop override when present, otherwise platform active prompt.
- Return source (`SHOP` or `PLATFORM`) independently for model and prompt.
- Return stable ids and safe presentation fields needed by Studio (catalogue entry/provider/model display; prompt lineage/revision/hash/content as appropriate for authorized Studio authoring). `CommerceAgentPrompt` has no separate prompt-name identity in Phase 2; do not invent one in the resolver DTO.
- Return explicit configuration-unavailable results when mandatory platform state is absent or the selected platform model/prompt state is invalid/disabled.
- If an explicit shop model override exists but references a disabled/unavailable entry, fail closed and do not fall back.
- If an explicit prompt pointer is invalid/missing/non-published/scope-invalid, fail closed.
- Add tests for all four inheritance combinations and failure states.

## Out of Scope

- Freezing configuration into a preview or conversation grant.
- Manifest changes.
- Background changes.
- Provider execution.
- Feature/capability prompt removal.

## Requirements

- Model and prompt fallback must be calculated independently.
- Absence of an override is the only condition that triggers fallback.
- A broken explicit override must remain visible as a configuration error, not masquerade as inheritance.
- The resolver must be side-effect free.
- Browser/client input must not select an arbitrary environment.
- The resolver's model selection, prompt selection and referenced immutable records must be observed through one coherent database read snapshot; do not compose independently committed reads that can return a model/prompt combination that never existed together.
- A normal multi-statement PostgreSQL `READ COMMITTED` transaction is not sufficient for this invariant. Use either one database statement/query that obtains the complete effective configuration or a transaction with snapshot semantics (`REPEATABLE READ` or stronger) for all participating reads.
- The resolver must not mutate defaults while resolving.

### Deterministic persistence and file boundary

The resolver must compose the exact Phase 2 rows below in one coherent database snapshot:

```text
model:
  CommerceShopModelSelection
    ?? CommercePlatformModelSelection
  -> CommerceModelCatalogueEntry

prompt:
  CommerceShopPromptPointer
    ?? CommercePlatformPromptPointer
  -> CommerceAgentPromptRevision
  -> CommerceAgentPrompt
```

Primary implementation locations for this task are:

```text
src/commerce/agent-configuration/effective-configuration.ts
src/studio/agent-configuration/effective-contracts.ts
src/studio/agent-configuration/effective-server-actions.ts
tests/agent-configuration-effective.test.ts
```

Absence of the shop selection/pointer is the only inheritance signal. Do not infer inheritance from disabled rows, invalid FKs, missing revisions or provider availability. Do not create a new persistence table for the computed effective configuration.

## Work Items

- [ ] Define Commerce-local effective agent-configuration DTO/result types.
- [ ] Implement server-side model resolution.
- [ ] Implement server-side prompt resolution.
- [ ] Ensure model/prompt selection and referenced immutable records are resolved through one coherent database snapshot.
- [ ] Integrate selected-shop validation.
- [ ] Add source/provenance fields required by Studio.
- [ ] Add explicit unavailable/error mapping.
- [ ] Add focused resolver tests for inheritance matrix and broken override cases.

## Interfaces / Contracts

Consumes:

- model configuration semantics/read contracts from ARCH-021-COMMERCE-007;
- prompt lifecycle/configuration semantics/read contracts from ARCH-021-COMMERCE-009;
- selected-shop server validation from ARCH-021-COMMERCE-003;
- the accepted ARCH-021 Prisma rows when direct snapshot-aware composition is required to satisfy the one-snapshot invariant.

Do not satisfy this interface by calling separately committed model-service and prompt-service reads and combining their results afterward.

Produces the Commerce-local effective configuration read model used by Phase 2 Studio UI. The future grant/manifest Shared contract is intentionally not created here.

## Dependencies

- ARCH-021-COMMERCE-003
- ARCH-021-COMMERCE-007
- ARCH-021-COMMERCE-009

## Enables

- ARCH-021-COMMERCE-012

## Acceptance Criteria

- [ ] No shop overrides -> platform model + platform prompt.
- [ ] Shop model only -> shop model + platform prompt.
- [ ] Shop prompt only -> platform model + shop prompt.
- [ ] Both overrides -> shop model + shop prompt.
- [ ] Missing platform model or prompt yields explicit unavailable state.
- [ ] A disabled/broken platform default model yields explicit unavailable state; there is no fallback beyond the platform default.
- [ ] An invalid/non-published/scope-invalid platform active prompt yields explicit unavailable state; there is no fallback beyond the platform prompt.
- [ ] Disabled/broken explicit shop model override fails closed without model fallback.
- [ ] Invalid explicit shop prompt pointer fails closed without prompt fallback.
- [ ] No provider call, grant write or manifest mutation occurs.

## Validation

- [ ] focused effective-configuration resolver tests
- [ ] coherent-snapshot regression covering configuration mutation during effective resolution
- [ ] selected-shop validation regression tests
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

## Implementation Notes

Keep these DTOs Commerce-local until the later runtime phase defines the exact cross-service frozen grant/manifest contract. Do not prematurely publish a Shared schema solely for the Phase 2 UI. Satisfy the coherent-snapshot requirement with either one complete database statement/query or a `REPEATABLE READ`/stronger transaction spanning all required reads; merely wrapping multiple queries in the repository's ordinary `ReadCommitted` transaction pattern does not satisfy this task.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 source review confirms the resolver uses one `REPEATABLE READ` interactive transaction, reads platform/shop model and prompt state inside that snapshot, calculates model and prompt inheritance independently, and validates explicit broken shop overrides fail closed. The authenticated server action also derives the environment server-side and resolves the requested shop through the accepted Studio shop execution context.

One functional fail-closed defect remains. ARCH-021 defines the platform model default and platform active prompt as mandatory environment state. The current resolver validates only the row selected by `shopOverride ?? platformDefault`, so a valid shop override can mask missing/disabled/invalid mandatory platform state. For example, a shop model override succeeds when the platform model selection is absent, and a shop prompt override succeeds when the platform prompt pointer is absent. That violates the parent architecture and this task's explicit acceptance criteria that missing/broken platform model or prompt state yields configuration unavailable.

Attempt 2 must first validate the platform model selection and platform prompt pointer independently as valid mandatory environment baselines, then apply shop overrides independently. A shop override may replace the effective value only after the corresponding platform baseline is known valid. Preserve the existing rule that a broken explicit shop override fails closed rather than falling back.

The submitted focused test only asserts that `RepeatableRead` was requested; it does not satisfy the task's required coherent-snapshot regression covering a concurrent configuration mutation. Attempt 2 must add focused proof, preferably against disposable PostgreSQL with two connections, that model/prompt values returned by one resolver call come from one repeatable-read snapshot and cannot form a combination that never coexisted. Also add the task-required selected-shop server-action regression proving an invalid/unavailable shop is returned without resolving effective configuration. These are bounded validation additions, not a request for broader/exhaustive testing.

The supplied parent snapshot was still `in_progress` with an unfinalized Completion Report. Because the functional correction is required, the same task is returned to `ready`; the next authorized claim becomes Attempt 2 and must complete the normal Completion Report/review handoff.

### Reviewed Files

- `src/commerce/agent-configuration/effective-configuration.ts`
- `src/studio/agent-configuration/effective-contracts.ts`
- `src/studio/agent-configuration/effective-server-actions.ts`
- `tests/agent-configuration-effective.test.ts`
- `docs/decisions/commerce/ARCH-021/COMMERCE-010-resolve-effective-agent-configuration.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

- Submitted focused resolver result: 7 tests passed.
- Submitted touched-file ESLint: passed.
- Submitted `git diff --check`: passed.
- Repository-wide TypeScript baseline remains unrelated/non-blocking.
- Source inspection confirms the current unit test checks the requested transaction isolation but does not yet exercise the required concurrent-mutation snapshot behavior.

### Architecture Conformance

Changes Requested. The one-snapshot mechanism and independent override selection are structurally aligned, but mandatory platform baseline validation is incomplete and the explicit coherent-snapshot/selected-shop validation evidence required by the task is not yet present.

### Follow-up

Attempt 2 correction contract:

1. Resolve and validate the platform model selection as mandatory state even when a shop model override exists. Missing selection, missing catalogue row, or disabled catalogue entry must return `UNAVAILABLE`.
2. Resolve and validate the platform prompt pointer as mandatory state even when a shop prompt override exists. Missing pointer, non-published revision, or invalid platform scope must return `UNAVAILABLE`.
3. After both platform baselines are valid, choose shop model and shop prompt overrides independently; a present but broken shop override must continue to fail closed with no fallback.
4. Add focused regression cases where a valid shop model override cannot mask missing/disabled platform model state and a valid shop prompt override cannot mask missing/invalid platform prompt state.
5. Add the required coherent-snapshot regression with a configuration mutation during resolution, using real snapshot semantics rather than merely asserting the `RepeatableRead` option.
6. Add the required selected-shop server-action regression proving an invalid/unavailable requested shop is rejected before effective configuration resolution.
7. Preserve the side-effect-free/no-provider-call/no-grant/no-manifest boundary and stop at architect review.
