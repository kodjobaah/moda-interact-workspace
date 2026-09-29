---
id: ARCH-021-SYSTEM-TEST-002
architecture_id: ARCH-021
title: Validate Tool Definition through rendered-Test and Review flow
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-079
  - ARCH-021-COMMERCE-081
  - ARCH-021-COMMERCE-083
  - ARCH-021-COMMERCE-088
enables: []
created: 2026-09-28
updated: 2026-09-28
---

# Validate Tool Definition through rendered-Test and Review flow

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Validate the integrated Commerce Studio Tool authoring flow for both External HTTP and Shopify Admin: Tool library launcher -> Tool Definition -> Request -> Response -> Result Template -> Test rendered agent output -> Review -> Save/Cancel, including persisted-DRAFT parity and zero-write Test/Cancel boundaries.

## Context

This is terminal architecture validation for the Tool-creation-flow refinement, including the 2026-09-29 progressive new-Tool navigation addition. It runs only after the Commerce implementation tasks are architect-accepted Complete. It must not implement missing Commerce behaviour.

## Scope

Add/update system-test scenarios and fixtures needed to exercise the integrated UI/server boundaries using deterministic provider fixtures/adapters.

## Out of Scope

- Fixing Commerce defects in the system-test repository.
- Real production Shopify or arbitrary Internet provider calls.
- Publication-proof redesign.
- Database/schema changes.

## Requirements

### R1 — Tool library launch and zero-write local authoring

Prove `/tools` contains `Create Tool` and no inline Tool Definition form. Start a new Tool, edit Tool Definition/Request/Response/Result Template and prove no Tool/ToolRevision exists until Review -> Save.

### R2 — exact flow and ownership for both providers

Prove the visible steps are exactly:

```text
Tool Definition
Request
Response
Result Template
Test
Review
```

Prove no Agent Contract tab exists; input schema is edited under Request; template is edited under Result Template; Review shows Agent Contract read-only and Result Template separately.

### R3 — External complete Test

With deterministic External fixture response, prove Request/Response produces canonical values, Result Template is rendered server-side, and Test displays the exact populated `Result shown to agent` before diagnostics. Change the template and prove the old Test result becomes stale.

### R4 — Shopify Admin complete Test

With deterministic Admin fixture/session, prove selected-shop execution maps arguments, validates compiler-derived result contract, renders the Result Template and displays the exact populated `Result shown to agent`. Prove no access token/shop credential appears in rendered UI/diagnostics.

### R5 — Save/Cancel boundaries

For a new Tool:

```text
Cancel -> zero Tool/ToolRevision created
Save   -> exactly one Tool + revision-1 DRAFT through atomic creation
```

For a persisted DRAFT:

```text
Cancel unsaved changes -> restores saved revision, zero mutation
Save draft             -> one CAS update
```

### R6 — provider switch reset

Author provider-specific state, request a provider-kind change, prove no state is cleared before explicit confirmation, then confirm and prove Request/Response/Result Template/Test state is reset to the new provider defaults.

### R7 — progressive traversal for both provider kinds

For **new Tool creation** with both External HTTP and Shopify Admin, prove all six canonical tabs are visible from session start, only Tool Definition is initially enabled, and `Next` unlocks exactly one subsequent step when the current step's accepted readiness predicate is satisfied. Prove `Previous` navigates to the immediately preceding enabled step without validation or mutation.

After a tab has once been unlocked, edit an upstream section so its validation/Test state becomes stale or invalid and prove the already-unlocked tab remains directly clickable and reachable by Previous/Next. Prove Save/Create remains disabled according to the existing validation/Test persistence gate.

Prove a cancelled provider-kind change preserves the unlock frontier and a confirmed destructive provider-kind change resets the active step/frontier to Tool Definition. Persisted-DRAFT navigation must remain unchanged.

## Work Items

- [ ] Add Tool-library/Tool Definition zero-write scenario.
- [ ] Add exact six-step ownership scenario for External HTTP.
- [ ] Add exact six-step ownership scenario for Shopify Admin.
- [ ] Add External rendered-template Test scenario.
- [ ] Add Shopify rendered-template Test scenario with credential-leak assertions.
- [ ] Add new Tool Save/Cancel persistence scenario.
- [ ] Add persisted DRAFT CAS Save/Cancel scenario.
- [ ] Add provider-switch destructive-reset confirmation scenario.
- [ ] Add progressive External new-Tool Previous/Next/unlock-frontier scenario.
- [ ] Add progressive Shopify Admin new-Tool Previous/Next/unlock-frontier scenario.
- [ ] Add regression proving enabled tabs remain accessible after upstream state becomes stale/invalid.
- [ ] Add regression proving persisted-DRAFT tab navigation remains unchanged.

## Interfaces / Contracts

Consumes only architect-accepted outputs of COMMERCE-079, COMMERCE-081, COMMERCE-083 and COMMERCE-088 and their transitive prerequisites.

## Dependencies

- ARCH-021-COMMERCE-079
- ARCH-021-COMMERCE-081
- ARCH-021-COMMERCE-083
- ARCH-021-COMMERCE-088

## Enables

None.

## Acceptance Criteria

- [ ] Exact six-step UI is proven for both provider kinds.
- [ ] No Agent Contract authoring tab exists.
- [ ] Agent Contract shown in Review is derived/read-only.
- [ ] External Test displays exact server-rendered agent text and stales on template changes.
- [ ] Shopify Test displays exact server-rendered agent text and leaks no credential material.
- [ ] New authoring/Test/Cancel creates no durable Tool state.
- [ ] New Save creates exactly one Tool + revision-1 DRAFT.
- [ ] Persisted Cancel writes nothing; persisted Save uses CAS and one mutation.
- [ ] Provider switch does not clear state before confirmation and does reset after confirmation.
- [ ] External and Shopify new-Tool authoring both expose progressive Previous/Next traversal with the same canonical six-step order.
- [ ] All six new-Tool tabs are visible from session start; only the current unlock frontier is clickable.
- [ ] `Next` unlocks only the immediate next step and does not run validation itself.
- [ ] Once enabled, a tab remains directly accessible after upstream edits make current state stale/invalid.
- [ ] Existing Save/Create readiness still blocks persistence when current validation/Test state is not ready.
- [ ] Confirmed provider replacement resets progressive navigation to Tool Definition; cancelled replacement does not.
- [ ] Persisted-DRAFT tab navigation is unchanged by COMMERCE-088.

## Validation

- [ ] focused ARCH-021 system-test scenario suite for this flow
- [ ] deterministic fixture/provider validation only; no live Internet dependency
- [ ] targeted lint/typecheck required by `moda-interact-system-test/package.json` and repository instructions
- [ ] `git diff --check`

## Stop Condition

After all scenarios pass, set the task to `review`, complete the Completion Report and STOP. Route any discovered defect to the owning Commerce task; do not patch Commerce from system-test.

## Implementation Notes

System testing is terminal validation. It must not become a dependency of any Commerce implementation task.

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
