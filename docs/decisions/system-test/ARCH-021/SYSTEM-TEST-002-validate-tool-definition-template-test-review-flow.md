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
status: ready
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-079
  - ARCH-021-COMMERCE-081
  - ARCH-021-COMMERCE-083
  - ARCH-021-COMMERCE-095
  - ARCH-021-COMMERCE-102
  - ARCH-021-COMMERCE-103
enables: []
created: 2026-09-28
updated: 2026-09-29
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

Validate the integrated Commerce Studio new-Tool authoring flow for External HTTP and Shopify Admin from Tool library launcher -> Tool Definition -> Request -> Response -> Result Template -> Test rendered agent output -> Review -> Save/Cancel, plus persisted-DRAFT six-step traversal parity across External HTTP, Shopify Admin and Policy Operation Tools, including zero-write Test/Cancel/navigation boundaries.

## Context

This is terminal architecture validation for the 2026-09-28 Tool-creation-flow refinement. It runs only after the Commerce implementation tasks are architect-accepted Complete. It must not implement missing Commerce behaviour.

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

For persisted DRAFT authoring of External HTTP, Shopify Admin and Policy Operation Tools, prove all six tabs remain directly clickable and the sequential footer follows exactly:

```text
Tool Definition -> Request -> Response -> Result Template -> Test -> Review
```

with `Previous` absent only on Tool Definition and `Next` absent only on Review. Prove Previous/Next navigate one step without validation, provider execution or Tool lifecycle mutation, including when the current candidate is invalid/stale.

### R3 — External complete Test

With deterministic External fixture response, prove Request/Response produces canonical values, Result Template is rendered server-side, and Test displays the exact populated `Result shown to agent` before diagnostics. Change the template and prove the old Test result becomes stale.

### R4 — Shopify Admin complete Test and explicit execution target

With deterministic Admin fixture/session, prove the Test surface visibly identifies the selected shop domain and offline-session availability before execution. Prove:

```text
no selected shop                     -> Run Test disabled, zero live-Test dispatch
selected shop + offline unavailable  -> Run Test disabled, zero live-Test dispatch
selected shop + offline available    -> normal Test prerequisites may enable Run Test
```

For the executable target, prove selected-shop execution maps arguments, validates compiler-derived result contract, renders the Result Template and displays the exact populated `Result shown to agent`. Prove no access token/shop credential appears in rendered UI/diagnostics. Prove a stale/invalid URL shop cannot remain an execution target when the shell has no selected shop.

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

### R7 — consequential Tool-authoring actions are single-flight

Exercise representative integrated consequential actions with rapid repeated activation and prove one admitted operation per current action/candidate. At minimum cover one lifecycle mutation and Shopify Admin Run Test. The Commerce implementation tests own exhaustive per-button same-tick coverage; this system test proves the integrated boundary does not duplicate durable mutation/provider execution.

For an unknown lifecycle mutation outcome, prove reconciliation checks the original operation and does not replay the mutation.

## Work Items

- [ ] Add Tool-library/Tool Definition zero-write scenario.
- [ ] Add exact six-step ownership scenario for External HTTP.
- [ ] Add exact six-step ownership scenario for Shopify Admin.
- [ ] Add External rendered-template Test scenario.
- [ ] Add Shopify rendered-template Test scenario with explicit selected-shop/offline-session gating and credential-leak assertions.
- [ ] Add invalid/stale selected-shop route scenario proving no hidden Shopify execution target remains.
- [ ] Add rapid repeated-activation scenario proving one Shopify Test dispatch.
- [ ] Add new Tool Save/Cancel persistence scenario, including rapid repeated Save admission.
- [ ] Add persisted DRAFT CAS Save/Cancel scenario.
- [ ] Add persisted DRAFT Previous/Next parity scenario for External HTTP, Shopify Admin and Policy Operation, including invalid/stale zero-side-effect traversal.
- [ ] Add provider-switch destructive-reset confirmation scenario.

## Interfaces / Contracts

Consumes only architect-accepted outputs of COMMERCE-079, COMMERCE-081, COMMERCE-083, COMMERCE-095, COMMERCE-102 and COMMERCE-103 and their transitive prerequisites.

## Dependencies

- ARCH-021-COMMERCE-079
- ARCH-021-COMMERCE-081
- ARCH-021-COMMERCE-083
- ARCH-021-COMMERCE-095
- ARCH-021-COMMERCE-102
- ARCH-021-COMMERCE-103

## Enables

None.

## Acceptance Criteria

- [ ] Exact six-step UI is proven for both new-Tool provider kinds.
- [ ] Persisted External HTTP, Shopify Admin and Policy Operation DRAFTs expose the same six-step order with direct-click tabs plus exact Previous/Next one-step traversal.
- [ ] Persisted Previous/Next remains usable for invalid/stale candidates and causes zero validation, provider execution and Tool lifecycle mutation.
- [ ] No Agent Contract authoring tab exists.
- [ ] Agent Contract shown in Review is derived/read-only.
- [ ] External Test displays exact server-rendered agent text and stales on template changes.
- [ ] Shopify Test identifies the selected shop domain and offline-session availability before execution.
- [ ] No-shop/offline-unavailable Shopify targets keep Run Test disabled and dispatch zero live-Test calls.
- [ ] Invalid/stale route shop context cannot survive as a hidden Tool-authoring execution target.
- [ ] Shopify Test displays exact server-rendered agent text and leaks no credential material.
- [ ] Rapid repeated Shopify Test activation dispatches one current-candidate live Test.
- [ ] New authoring/Test/Cancel creates no durable Tool state.
- [ ] New Save creates exactly one Tool + revision-1 DRAFT, including under rapid repeated activation.
- [ ] Persisted Cancel writes nothing; persisted Save uses CAS and one mutation.
- [ ] Unknown mutation reconciliation checks the original operation without replaying the mutation.
- [ ] Provider switch does not clear state before confirmation and does reset after confirmation.

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
