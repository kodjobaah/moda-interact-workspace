---
id: ARCH-021-COMMERCE-006
architecture_id: ARCH-021
title: Install the JavaScript response panel in production Tool authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 50
executor: copilot
claimed_at: 2026-09-23T12:13:25Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-005
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-027
  - ARCH-020-COMMERCE-031
enables: []
created: 2026-09-23
updated: 2026-09-23
---

# Install the JavaScript response panel in production Tool authoring

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Install the already-accepted bounded JavaScript response editor/validator into the production external Tool authoring flow, using real Studio/server composition rather than leaving the `renderCodePanel` slot unbound.

## Context

ARCH-020-COMMERCE-026 provides the bounded QuickJS response processor, ARCH-020-COMMERCE-027 provides `CodeResponsePanel`, and ARCH-020-COMMERCE-031 provides the external synthetic preview backend. `ExternalHttpEditor` exposes a typed `renderCodePanel` slot, but `ProductionStudioPage` currently does not install it.

Phase 1 must make JavaScript authoring actually available in production Studio. The panel's **sample execution remains synthetic in Phase 1**; Phase 4 later replaces the administrator-facing tool test with a real read-only provider call. This task must not introduce provider networking.

## Scope

- Install `CodeResponsePanel` (or the accepted equivalent) in the production `ExternalHttpEditor` JavaScript mode.
- Add/complete the production `CodeResponsePort` adapter needed for server-side code validation plus current synthetic sample run/read/cancel.
- Ensure source edits update the Tool draft's `responseProcessing` definition and preserve saved-vs-unsaved identity.
- Preserve current QuickJS sandbox/runtime limits and prohibit browser execution/eval.
- Preserve preview run idempotency/cancellation/unknown reconciliation.
- Keep the selected shop context/real connection revision visible to the surrounding Tool authoring flow without using either to make a provider request yet.

## Out of Scope

- Live external HTTP calls.
- Live Shopify calls.
- Request-side JavaScript authoring (Phase 3).
- Replacing synthetic samples with provider responses (Phase 4).
- Changing QuickJS sandbox limits or runtime engine.
- Prompt/model configuration.
- Publication contract redesign.

## Requirements

- Production Tool authoring must no longer render “JavaScript code editor is unavailable” merely because the slot was not composed.
- JavaScript code is validated/executed only by the accepted server-side bounded runtime; never by browser `eval`, Function, DOM, fetch/imports or active HTML.
- The production adapter must use accepted code-response/external-preview services rather than reimplementing the compiler/runtime.
- Save-before-run, content-hash stale protection, cancellation and unknown-run reconciliation remain intact.
- The source stored in `CommerceToolDefinition.execution.responseProcessing` remains the single draft definition source; the panel must not maintain an independent durable copy.
- Synthetic sample execution is explicitly temporary Phase 1 behaviour and must remain clearly separated from future live provider execution.

## Work Items

- [ ] Provide the production `CodeResponsePort` adapter over accepted code-validation/preview services.
- [ ] Expand/adjust the typed code-panel composition boundary only as needed to supply the accepted `CodeResponsePanel` with its required draft/run context.
- [ ] Install the panel in the production U06 external Tool editor JavaScript mode.
- [ ] Bind source changes back to the current Tool draft response-processing definition without duplicate durable state.
- [ ] Preserve server-only sandbox execution and existing cancellation/idempotency semantics.
- [ ] Add a production-composition regression proving JavaScript mode renders the real panel and server adapter, not the unavailable placeholder.
- [ ] Preserve existing independent code-editor tests and add one Tool-authoring integration path covering visual -> JavaScript -> edit/validate/sample -> visual switching with dirty-state protection.

## Interfaces / Contracts

Consumes:

- `CodeResponsePanel` / `CodeResponsePort` from ARCH-020-COMMERCE-027
- bounded code processor from ARCH-020-COMMERCE-026
- external preview service from ARCH-020-COMMERCE-031
- real external Tool authoring composition from ARCH-021-COMMERCE-005

Produces:

- production-composed JavaScript response authoring inside U06.

No Shared/Database contract change is introduced.

## Dependencies

- ARCH-021-COMMERCE-005
- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-027
- ARCH-020-COMMERCE-031

## Enables

None. Completion of this task closes the Phase 1 implementation set.

## Acceptance Criteria

- [ ] Production JavaScript response mode renders the accepted code-response panel rather than the unavailable placeholder.
- [ ] Code validation/sample execution uses the accepted server-side sandbox/preview services and never browser execution.
- [ ] Editing code updates the current Tool draft definition and stale validation/results are invalidated correctly.
- [ ] Synthetic sample run/read/cancel continues to obey current idempotency/cancellation/unknown semantics.
- [ ] No provider network request or credential decryption is introduced by this Phase 1 panel wiring.
- [ ] Existing visual response authoring remains functional and switching modes retains the accepted dirty/discard guard.

## Validation

- [ ] existing code-editor focused suite
- [ ] existing external Tool authoring focused suite
- [ ] focused production code-panel composition test
- [ ] relevant preview service/route tests for the adapter seam
- [ ] targeted lint/typecheck for changed files
- [ ] `git diff --check`

Do not require a live provider call.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin Phase 2 work.

## Implementation Notes

If the current `ExternalCodePanelSlotProps` is too narrow to compose `CodeResponsePanel`, correct that local typed boundary. Do not work around it by adding hidden mutable singleton state or duplicating the code-response engine.

Phase 4 will replace the human-facing synthetic tool-test data source; keep that future swap possible by preserving an injected port boundary.

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
