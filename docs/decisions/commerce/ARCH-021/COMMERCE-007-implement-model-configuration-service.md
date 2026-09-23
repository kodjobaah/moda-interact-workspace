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
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
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
- Mutation idempotency/CAS/unknown-outcome handling should follow existing Studio command patterns rather than inventing an incompatible mutation model.
- Clearing a shop override means inheritance and must not create a replacement platform copy in the shop record.
- Disabling a catalogue entry does not rewrite any existing pointer.
- No browser response includes provider API credentials or secret configuration.
- In Phase 2, model `disabled`/`unavailable` state is configuration state only. This service must not probe provider credentials, network reachability, quota or provider health.

## Work Items

- [ ] Add model catalogue query/lifecycle service over the accepted Prisma schema.
- [ ] Add platform default model read/set operation with CAS.
- [ ] Add shop override read/set/clear operation with CAS.
- [ ] Add audit events for privileged mutations.
- [ ] Add typed server actions/Studio port contracts.
- [ ] Add unit/integration tests for auth, identity immutability, disabled selection, CAS replay/conflict and independent shop clear semantics.

## Interfaces / Contracts

Consumes:

- ARCH-021-DATABASE-001 model catalogue and environment/shop model selections.
- existing Commerce Studio authentication from ARCH-020-COMMERCE-002.

Produces a Commerce-local model-configuration port for later Phase 2 UI and resolver tasks.

No Shared package contract is introduced.

## Dependencies

- ARCH-021-DATABASE-001
- ARCH-020-COMMERCE-002

## Enables

- ARCH-021-COMMERCE-010
- ARCH-021-COMMERCE-011

## Acceptance Criteria

- [ ] Platform admins can list/create/enable/disable catalogue entries without exposing credentials.
- [ ] Provider/model identity cannot be edited into another provider model.
- [ ] Platform default selection is environment-scoped and CAS protected.
- [ ] Shop override can be independently set and cleared.
- [ ] Disabled entries cannot be newly selected.
- [ ] Existing explicit broken/disabled pointers are not silently rewritten to platform inheritance.
- [ ] Authorization and audit behaviour is covered by focused tests.
- [ ] No provider network call occurs.

## Validation

- [ ] focused model-configuration service tests
- [ ] focused authorization/development-bypass tests
- [ ] relevant Prisma integration tests using disposable PostgreSQL where required
- [ ] targeted lint/typecheck
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP.

## Implementation Notes

Consume the accepted nested database submodule/schema. Do not copy or locally redefine Prisma models. Keep provider execution adapters untouched. A catalogue entry is configuration-unavailable here only because durable catalogue/selection state is absent, invalid or disabled; provider/network/credential availability belongs to later execution phases.

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
