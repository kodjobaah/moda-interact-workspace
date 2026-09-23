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
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-007
  - ARCH-021-COMMERCE-009
enables:
  - ARCH-021-COMMERCE-011
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
- Return stable ids and safe presentation fields needed by Studio (catalogue entry/provider/model display; prompt lineage/revision/name/hash/content as appropriate for authorized Studio authoring).
- Return explicit configuration-unavailable results when mandatory platform state is absent.
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
- The resolver's result must be deterministic for one transactionally observed database state; do not mutate defaults while resolving.

## Work Items

- [ ] Define Commerce-local effective agent-configuration DTO/result types.
- [ ] Implement server-side model resolution.
- [ ] Implement server-side prompt resolution.
- [ ] Integrate selected-shop validation.
- [ ] Add source/provenance fields required by Studio.
- [ ] Add explicit unavailable/error mapping.
- [ ] Add focused resolver tests for inheritance matrix and broken override cases.

## Interfaces / Contracts

Consumes:

- model configuration service from ARCH-021-COMMERCE-007;
- prompt lifecycle/configuration service from ARCH-021-COMMERCE-009;
- selected-shop server validation from ARCH-021-COMMERCE-003.

Produces the Commerce-local effective configuration read model used by Phase 2 Studio UI. The future grant/manifest Shared contract is intentionally not created here.

## Dependencies

- ARCH-021-COMMERCE-007
- ARCH-021-COMMERCE-009

## Enables

- ARCH-021-COMMERCE-011
- ARCH-021-COMMERCE-012

## Acceptance Criteria

- [ ] No shop overrides -> platform model + platform prompt.
- [ ] Shop model only -> shop model + platform prompt.
- [ ] Shop prompt only -> platform model + shop prompt.
- [ ] Both overrides -> shop model + shop prompt.
- [ ] Missing platform model or prompt yields explicit unavailable state.
- [ ] Disabled/broken explicit shop model override fails closed without model fallback.
- [ ] Invalid explicit shop prompt pointer fails closed without prompt fallback.
- [ ] No provider call, grant write or manifest mutation occurs.

## Validation

- [ ] focused effective-configuration resolver tests
- [ ] selected-shop validation regression tests
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

## Implementation Notes

Keep these DTOs Commerce-local until the later runtime phase defines the exact cross-service frozen grant/manifest contract. Do not prematurely publish a Shared schema solely for the Phase 2 UI.

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

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
