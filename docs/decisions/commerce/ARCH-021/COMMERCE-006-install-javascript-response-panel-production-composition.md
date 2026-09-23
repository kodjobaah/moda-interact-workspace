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
status: ready
priority: 50
executor: null
claimed_at: null
attempt: 2
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

- [x] Provide the production `CodeResponsePort` adapter over accepted code-validation/preview services.
- [x] Expand/adjust the typed code-panel composition boundary only as needed to supply the accepted `CodeResponsePanel` with its required draft/run context.
- [x] Install the panel in the production U06 external Tool editor JavaScript mode.
- [x] Bind source changes back to the current Tool draft response-processing definition without duplicate durable state.
- [x] Preserve server-only sandbox execution and existing cancellation/idempotency semantics.
- [x] Add a production-composition regression proving JavaScript mode renders the real panel and server adapter, not the unavailable placeholder.
- [x] Preserve existing independent code-editor tests and add one Tool-authoring integration path covering visual -> JavaScript -> edit/validate/sample -> visual switching with dirty-state protection.

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

- [x] Production JavaScript response mode renders the accepted code-response panel rather than the unavailable placeholder.
- [x] Code validation/sample execution uses the accepted server-side sandbox/preview services and never browser execution.
- [x] Editing code updates the current Tool draft definition and stale validation/results are invalidated correctly.
- [x] Synthetic sample run/read/cancel continues to obey current idempotency/cancellation/unknown semantics.
- [x] No provider network request or credential decryption is introduced by this Phase 1 panel wiring.
- [x] Existing visual response authoring remains functional and switching modes retains the accepted dirty/discard guard.

## Validation

- [x] existing code-editor focused suite
- [x] existing external Tool authoring focused suite
- [x] focused production code-panel composition test
- [x] relevant preview service/route tests for the adapter seam
- [x] targeted lint/typecheck for changed files
- [x] `git diff --check`

Do not require a live provider call.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin Phase 2 work.

## Implementation Notes

If the current `ExternalCodePanelSlotProps` is too narrow to compose `CodeResponsePanel`, correct that local typed boundary. Do not work around it by adding hidden mutable singleton state or duplicating the code-response engine.

Phase 4 will replace the human-facing synthetic tool-test data source; keep that future swap possible by preserving an injected port boundary.

## Completion Report

### Status

Ready for Review (Attempt 2 corrections complete)

### Files Changed

- [components/production-studio-page.tsx](../../../../../moda-interact-commerce/components/production-studio-page.tsx)
- [components/studio-workspace.tsx](../../../../../moda-interact-commerce/components/studio-workspace.tsx)
- [src/studio/code-response/code-response-panel.tsx](../../../../../moda-interact-commerce/src/studio/code-response/code-response-panel.tsx)
- [src/studio/code-response/contracts.ts](../../../../../moda-interact-commerce/src/studio/code-response/contracts.ts)
- [src/studio/code-response/index.ts](../../../../../moda-interact-commerce/src/studio/code-response/index.ts)
- [src/studio/code-response/production-panel.tsx](../../../../../moda-interact-commerce/src/studio/code-response/production-panel.tsx)
- [src/studio/code-response/production-port.ts](../../../../../moda-interact-commerce/src/studio/code-response/production-port.ts)
- [app/api/studio/code-response/validate/route.ts](../../../../../moda-interact-commerce/app/api/studio/code-response/validate/route.ts)
- [app/api/studio/preview/tool-tests/[runId]/cancel/route.ts](../../../../../moda-interact-commerce/app/api/studio/preview/tool-tests/[runId]/cancel/route.ts)
- [tests/external-tools-ui.test.tsx](../../../../../moda-interact-commerce/tests/external-tools-ui.test.tsx)

Attempt 2 correction files:

- [components/studio-workspace.tsx](../../../../../moda-interact-commerce/components/studio-workspace.tsx)
- [src/studio/external-http/editor.tsx](../../../../../moda-interact-commerce/src/studio/external-http/editor.tsx)
- [src/studio/external-http/ports.ts](../../../../../moda-interact-commerce/src/studio/external-http/ports.ts)
- [src/studio/code-response/contracts.ts](../../../../../moda-interact-commerce/src/studio/code-response/contracts.ts)
- [src/studio/code-response/code-response-panel.tsx](../../../../../moda-interact-commerce/src/studio/code-response/code-response-panel.tsx)
- [src/studio/code-response/production-panel.tsx](../../../../../moda-interact-commerce/src/studio/code-response/production-panel.tsx)
- [tests/external-tools-ui.test.tsx](../../../../../moda-interact-commerce/tests/external-tools-ui.test.tsx)

### Work Completed

- Composed the production `CodeResponsePanel` in the real Tool detail JavaScript path, preserving the existing visual-to-JavaScript discard guard and selected-shop/connection context.
- Added the production `CodeResponsePort` adapter over the accepted server validation and synthetic external preview services, including status reads and cancellation.
- Preserved server-only QuickJS execution, draft save-before-run/content-hash protection, idempotent run identifiers, cancellation and unknown-outcome reconciliation.
- Preserved the external editor disabled boundary and added a production composition regression proving the accepted panel replaces the unavailable placeholder.
- Acceptance mapping: production panel composition is covered by `tests/external-tools-ui.test.tsx`; server sandbox and processor behavior by the existing code-editor/processor/runtime suites; preview idempotency/cancellation/unknown semantics by external-preview, preview-service/routes, and external-wiring suites; no provider request or credential decryption was added.

Attempt 2 corrections:

- Preserved the authoritative `editVersion` returned by each successful draft update and used the live value for JavaScript saves, full Tool saves and publication in [components/studio-workspace.tsx](../../../../../moda-interact-commerce/components/studio-workspace.tsx).
- Extended the typed JavaScript slot and response panel callback so only a saved, validated, completed current synthetic sample marks the existing U06 publication gate current; source, sample, contract and failed/unknown/cancelled run changes revoke it in [src/studio/external-http/ports.ts](../../../../../moda-interact-commerce/src/studio/external-http/ports.ts), [src/studio/external-http/editor.tsx](../../../../../moda-interact-commerce/src/studio/external-http/editor.tsx), [src/studio/code-response/code-response-panel.tsx](../../../../../moda-interact-commerce/src/studio/code-response/code-response-panel.tsx), and [src/studio/code-response/production-panel.tsx](../../../../../moda-interact-commerce/src/studio/code-response/production-panel.tsx).
- Added focused U06 regression coverage for the `[2, 3, 4]` draft CAS sequence and the canonical JavaScript publication handoff in [tests/external-tools-ui.test.tsx](../../../../../moda-interact-commerce/tests/external-tools-ui.test.tsx).

### Validation Results

- `npm exec vitest run tests/external-tools-ui.test.tsx`: passed, 11 tests.
- `npm exec vitest run tests/code-editor.test.tsx tests/code-response-processor.test.ts tests/response-processing.test.ts tests/external-http-executor.test.ts tests/external-preview.test.ts tests/preview-routes.test.ts tests/preview-service.test.ts tests/external-wiring.test.ts tests/external-tools-ui.test.tsx`: passed, 9 files, 103 tests.
- `npm exec vitest run tests/code-editor.test.tsx tests/code-response-processor.test.ts tests/code-runtime-proof.test.ts`: 29 passed, 1 pre-existing baseline failure in `tests/code-runtime-proof.test.ts` (`EXECUTION_ERROR` received where the existing expectation requires `RESOURCE_LIMIT`).
- `npm exec vitest run tests/external-preview.test.ts tests/preview-routes.test.ts tests/preview-service.test.ts`: passed, 49 tests.
- `npm exec vitest run tests/external-wiring.test.ts`: passed, 4 tests.
- `npm exec vitest run tests/response-processing.test.ts tests/external-http-executor.test.ts tests/preview-integration.test.ts tests/preview-client.test.ts`: passed, 27 tests.
- Targeted ESLint over changed files: passed with 0 errors and 2 existing `react-hooks/exhaustive-deps` warnings in `src/studio/code-response/code-response-panel.tsx`.
- `npm run typecheck`: repository baseline failures remain, `234 errors in 14 files`, in existing Prisma/publication-storage, studio-service and test fixture typing; no diagnostics were reported for changed production-panel, adapter, slot, workspace or regression files.
- `git diff --check`: passed.
- No live third-party/provider calls were made.

### Deviations

- The existing QuickJS runtime-proof baseline failure was not changed because it is outside this production composition task and the current change does not alter the runtime engine or limits.

### Assumptions

- The accepted preview service remains the source of truth for synthetic run lifecycle and reconciliation; the production adapter intentionally does not add provider networking.

### Unresolved Issues

- Repository-wide typecheck remains blocked by the documented pre-existing baseline diagnostics noted above.

### Architectural Concerns

None

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 2 correctly resolves both functional defects from the Attempt 1 correction contract and must preserve those fixes.

1. The production U06 Tool editor now retains the authoritative `editVersion` returned by each successful `updateToolDraft(...)` and uses the live value for subsequent JavaScript saves, the enclosing full Tool save and `Publish validated revision`. The focused U06 regression proves the expected `2 -> 3 -> 4` compare-and-swap sequence.

2. The JavaScript panel now hands completed current synthetic-sample state through the existing typed composition boundary to the canonical outer `externalValidated` publication gate. Source/sample/definition invalidation clears that gate, ADMIN still cannot publish, and SUPER_ADMIN publication uses the latest retained edit version. The accepted server-only QuickJS/external-preview, cancellation/reconciliation and no-provider-network boundaries remain intact.

One production-functional saved-vs-unsaved defect remains in the new JavaScript draft-save composition.

`saveCodeDraft(...)` persists the current `definition` object and then unconditionally calls `setDirty(false)`. However, U06 keeps `Input JSON Schema` and `Response template` in independent text buffers (`inputSchemaText` and `responseTemplateText`) until the enclosing Tool `Save draft` parses and applies them. Therefore a user can:

```text
edit Input JSON Schema or Response template
-> edit JavaScript
-> use the JavaScript panel Save draft
-> JavaScript save persists a definition that still contains the previous sibling value
-> shared U06 dirty state becomes false
```

The screen can then display a sibling edit that is not present in the persisted Tool revision while navigation protection is cleared. After a new JavaScript validation/sample cycle, the outer publication gate can also become eligible against the persisted revision even though the screen still displays an unsaved sibling value. That violates the task requirement to preserve saved-vs-unsaved Tool-draft identity and can publish a revision different from the definition visibly being reviewed.

The Attempt 2 implementation commit is `14c4c3e`; the submitted parent report commit is `f031e16`.

### Reviewed Files

- `components/studio-workspace.tsx`
- `src/studio/external-http/editor.tsx`
- `src/studio/external-http/ports.ts`
- `src/studio/code-response/contracts.ts`
- `src/studio/code-response/code-response-panel.tsx`
- `src/studio/code-response/production-panel.tsx`
- `tests/external-tools-ui.test.tsx`
- `docs/decisions/commerce/ARCH-021/COMMERCE-006-install-javascript-response-panel-production-composition.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

The submitted functionality-focused evidence is sufficient for the Attempt 2 CAS/publication corrections: 103/103 focused tests passed; targeted ESLint reported no errors; `git diff --check` passed; and the repository-wide typecheck remains blocked by the documented pre-existing baseline diagnostics.

No exhaustive test expansion is requested. The next correction needs only focused proof that JavaScript save cannot clear or bypass unsaved sibling Tool-definition state.

### Architecture Conformance

Partial.

The production JavaScript panel composition, authoritative edit-version continuity, canonical JavaScript validation/publication handoff, server-only execution boundary, cancellation/reconciliation behavior and Phase 1 no-provider-network constraint conform.

The JavaScript save path does not yet preserve the complete U06 saved-vs-unsaved identity because it may mark the whole Tool clean while sibling schema/template buffers remain unpersisted. Phase 1 therefore cannot close on Attempt 2.

### Follow-up

Attempt 3 correction contract:

1. Keep the accepted Attempt 2 edit-version and publication-gate fixes unchanged.
2. Correct JavaScript draft-save semantics so a successful code-panel save cannot clear the shared U06 dirty/navigation/publication guard while any sibling Tool-definition state displayed by U06 remains unpersisted.
3. The implementation may either persist the complete current valid U06 candidate atomically with the JavaScript source or retain the appropriate dirty state for sibling unsaved buffers. Do not create a second durable Tool definition or separate publication mechanism.
4. Invalid sibling JSON must not be silently discarded or treated as saved merely because JavaScript source can be saved.
5. Publication must continue to represent the exact persisted definition visibly under review. An unsaved sibling schema/template value must therefore either be persisted as part of the same valid draft save or continue to block publication/navigation as dirty.
6. Add one focused U06 regression proving this behavior. Exhaustive editor testing is not required.
7. Preserve all accepted server-side QuickJS/external-preview, cancellation/reconciliation, ADMIN/SUPER_ADMIN and no-provider-network/credential boundaries.

Return this same task through the normal launcher. Preserve `attempt: 2`; the next authorized claim increments it to Attempt 3.
