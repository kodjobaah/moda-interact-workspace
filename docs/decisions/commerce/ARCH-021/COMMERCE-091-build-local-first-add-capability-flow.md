---
id: ARCH-021-COMMERCE-091
architecture_id: ARCH-021
title: Build the local-first Add Capability flow
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 94
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-088
  - ARCH-021-COMMERCE-090
enables:
  - ARCH-021-COMMERCE-092
created: 2026-09-29
updated: 2026-09-29
---

# Build the local-first Add Capability flow

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Provide a simple `Capability -> Tool -> Review` Feature-scoped authoring flow that keeps all new-Capability state local until the final Create action atomically assigns one existing Tool.

## Context

A Capability is not a miniature publication workflow. Its behaviour comes from an already-authored Tool and the Feature-level Behaviour prompt shared with sibling Capabilities.

The current flow persists a shell before a Tool is assigned, then requires a second Capability draft/editor. The accepted Tool creation work has already established the desired local-first principle: incomplete authoring belongs to the browser; durable identity is created only at the final save boundary.

This Capability flow is deliberately smaller than Tool creation because Tool Request/Response/Test/Result Template authoring already happened elsewhere.

## Scope

Primary implementation should live under the dedicated Feature domain introduced by COMMERCE-090, for example:

```text
src/studio/features/add-capability/*
src/studio/features/* contracts/state as required
app/features/[id]/* route integration
focused Add Capability UI tests
```

Use the existing Tool read service/library data and COMMERCE-088 `createFeatureCapability` mutation.

## Out of Scope

- Tool creation/editing/testing.
- Feature behaviour editing beyond the COMMERCE-090 surface.
- Release creation/runtime.
- Capability revision/history/publish UI.
- Billing/subscription/plan selection.
- Adding multiple Tools to one Capability.
- Final legacy route/API deletion (COMMERCE-092).

## Requirements

### R1 — exactly three authoring phases

Expose the sequence:

```text
Capability
Tool
Review
```

`Previous` / `Next` controls may guide traversal. Once a phase has sufficient local state to be enabled, direct clicking of that enabled phase must remain allowed; do not impose unnecessary forced sequential navigation.

### R2 — Capability phase owns only identity/display metadata

Collect:

```text
Capability key
Display name
Description
```

The parent Feature is already fixed by route/context and is shown read-only.

Do not collect a prompt, Capability type, binding type, configuration limits or Tool revisions.

### R3 — Tool phase selects one existing usable Tool

Display the existing Tool library in a user-readable selector. Each selectable Tool must currently be enabled and have at least one PUBLISHED revision, matching COMMERCE-088 final server validation.

The user selects a Tool identity only. Do not expose or ask them to choose a Tool revision.

### R4 — all pre-Create state is local/non-durable

Opening the flow, editing Capability fields, changing tabs/phases, selecting/changing the Tool, navigating Back or cancelling must perform zero Capability mutation Server Actions.

The browser may use component state/session state as appropriate for this bounded flow, but must not create orphaned durable Capability records.

### R5 — Review is derived and read-only

Review shows at least:

```text
Feature
the Feature Behaviour prompt relationship (summary, not an editable duplicate)
Capability key/display name/description
selected Tool
```

The Review phase does not own additional editable fields.

### R6 — final Create performs exactly one mutation

`Create capability` calls `createFeatureCapability` once with the complete candidate.

On success, navigate back to the Feature configuration surface and show the newly created Capability/Tool association.

On validation/replay/conflict failure, keep the local candidate available for correction/retry. Do not create a second row silently.

### R7 — no old Capability workflow terminology

The new flow contains no UI/action for:

```text
Create draft
Edit as new draft
Publish Capability
Capability revision
selectionBinding
BASE
RECOVERY_POLICY
maxSearchResults
maxRecommendations
Tool bindings
```

## Work Items

- [ ] Add local authoring state for Capability metadata + one Tool identity.
- [ ] Build Capability phase.
- [ ] Build Tool selection phase from existing usable Tools.
- [ ] Build derived read-only Review phase.
- [ ] Add Previous/Next and enabled-phase direct navigation semantics.
- [ ] Add Cancel/Back with zero persistence.
- [ ] Wire final Create to exactly one COMMERCE-088 mutation.
- [ ] Refresh/navigate to the parent Feature after success.
- [ ] Preserve the local candidate across recoverable final-create failures.
- [ ] Add mutation-spy regressions proving no create call before final Create.
- [ ] Add final Create success/replay/conflict/error regressions.

## Interfaces / Contracts

Consumes:

```text
COMMERCE-088 createFeatureCapability
COMMERCE-088 Feature context
existing Tool read contract
```

No new cross-repository contract.

## Dependencies

- ARCH-021-COMMERCE-088
- ARCH-021-COMMERCE-090

## Enables

- ARCH-021-COMMERCE-092

## Acceptance Criteria

- [ ] The visible sequence is exactly Capability -> Tool -> Review.
- [ ] The author never selects a Capability type/binding, Tool revision, search limit or recommendation limit.
- [ ] Only enabled Tools with at least one PUBLISHED revision are selectable.
- [ ] No durable Capability exists before the final Create mutation succeeds.
- [ ] Cancel/Back before Create causes zero Capability mutation calls.
- [ ] Review is derived and read-only.
- [ ] Final Create performs one `createFeatureCapability` call with the full candidate.
- [ ] Success returns to the Feature and shows the new Capability with its assigned Tool.
- [ ] Recoverable failures preserve the local candidate without duplicate rows.
- [ ] Enabled phases remain directly clickable; the UI does not unnecessarily lock previously enabled navigation.

## Validation

- [ ] focused Add Capability component/flow tests
- [ ] explicit zero-mutation-before-final-Create regression
- [ ] final-create replay/conflict/error regression coverage
- [ ] targeted ESLint
- [ ] changed-file TypeScript diagnostics / repository typecheck evidence per baseline policy
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not begin legacy deletion.

## Implementation Notes

Prefer a small dedicated state machine/model over reusing Tool authoring state structures that carry irrelevant Request/Response/Test concepts.

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
