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
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 4
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

Ready for Review (Attempt 4 corrections complete)

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

Attempt 3 correction:

- Updated [components/studio-workspace.tsx](../../../../../moda-interact-commerce/components/studio-workspace.tsx) so JavaScript draft saves parse and schema-validate the complete visible U06 candidate, including the current `inputSchemaText` and `responseTemplateText`, and persist that candidate in the same `updateToolDraft` operation. A successful complete save updates both sibling buffers from the authoritative returned definition before clearing dirty state; invalid sibling JSON/schema leaves the dirty/navigation/publication guard active and performs no write.
- Added the focused U06 regression in [tests/external-tools-ui.test.tsx](../../../../../moda-interact-commerce/tests/external-tools-ui.test.tsx), proving invalid sibling JSON cannot be saved through the JavaScript panel and the existing Manage-connections discard guard remains active.
- Implementation commit: `5991dde`, pushed to `origin/task/ARCH-021-COMMERCE-006`.

### Validation Results

- `npm exec vitest run tests/external-tools-ui.test.tsx`: passed, 11 tests.
- `npm exec vitest run tests/code-editor.test.tsx tests/code-response-processor.test.ts tests/response-processing.test.ts tests/external-http-executor.test.ts tests/external-preview.test.ts tests/preview-routes.test.ts tests/preview-service.test.ts tests/external-wiring.test.ts tests/external-tools-ui.test.tsx`: passed, 9 files, 103 tests.
- `npm exec vitest run tests/code-editor.test.tsx tests/code-response-processor.test.ts tests/code-runtime-proof.test.ts`: 29 passed, 1 pre-existing baseline failure in `tests/code-runtime-proof.test.ts` (`EXECUTION_ERROR` received where the existing expectation requires `RESOURCE_LIMIT`).
- `npm exec vitest run tests/external-tools-ui.test.tsx`: passed, 12 tests, including the Attempt 3 invalid-sibling dirty-state regression.
- `npm exec vitest run tests/code-editor.test.tsx tests/code-response-processor.test.ts tests/response-processing.test.ts tests/external-http-executor.test.ts tests/external-preview.test.ts tests/preview-routes.test.ts tests/preview-service.test.ts tests/external-wiring.test.ts tests/external-tools-ui.test.tsx`: passed, 9 files, 104 tests.
- `npm exec vitest run tests/response-processing.test.ts tests/external-http-executor.test.ts tests/preview-integration.test.ts tests/preview-client.test.ts tests/external-preview.test.ts tests/preview-routes.test.ts tests/preview-service.test.ts`: passed, 7 files, 76 tests.
- Targeted `npx eslint components/studio-workspace.tsx tests/external-tools-ui.test.tsx`: passed with 0 errors and no warnings.
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

### Attempt 4 Correction Report

#### Correction Mapping

- Preserved the accepted Attempt 2 edit-version/CAS/publication fixes and Attempt 3 complete top-level Input JSON Schema / Response template persistence unchanged in [components/studio-workspace.tsx](../../../../../moda-interact-commerce/components/studio-workspace.tsx).
- Added an editor-owned preflight for the visible Advanced response processing and Response shape / resultSchema buffers. Invalid JSON now reports invalid execution state, prevents JavaScript draft persistence, and leaves the shared U06 dirty/navigation/publication guard active in [src/studio/external-http/editor.tsx](../../../../../moda-interact-commerce/src/studio/external-http/editor.tsx), [src/studio/external-http/ports.ts](../../../../../moda-interact-commerce/src/studio/external-http/ports.ts), and [src/studio/code-response/production-panel.tsx](../../../../../moda-interact-commerce/src/studio/code-response/production-panel.tsx).
- Prevented the parent full-draft save from clearing dirty state while a visible execution buffer is invalid, preserving exact persisted-definition publication semantics in [components/studio-workspace.tsx](../../../../../moda-interact-commerce/components/studio-workspace.tsx).
- Added focused regression coverage for JavaScript edit -> invalid Response shape JSON -> JavaScript Save draft, proving no draft write and retained discard protection in [tests/external-tools-ui.test.tsx](../../../../../moda-interact-commerce/tests/external-tools-ui.test.tsx).
- Preserved server-side QuickJS/external-preview execution, cancellation/reconciliation, ADMIN/SUPER_ADMIN boundaries, and no-provider-network/credential behavior.

#### Attempt 4 Validation Results

- `npm exec vitest run tests/external-tools-ui.test.tsx`: passed, 13 tests.
- `npm exec vitest run tests/code-editor.test.tsx tests/code-response-processor.test.ts tests/response-processing.test.ts tests/external-http-executor.test.ts tests/external-preview.test.ts tests/preview-routes.test.ts tests/preview-service.test.ts tests/external-wiring.test.ts tests/external-tools-ui.test.tsx`: passed, 9 files, 105 tests.
- Targeted ESLint over all five changed files: passed with no reported errors or warnings.
- `git diff --check`: passed.
- `npm run typecheck`: remains blocked by the existing repository baseline, reporting 234 errors in 14 files, including pre-existing diagnostics in the touched workspace/test files; no new production-panel, external-editor, external-port, or regression behavior failure was observed in focused validation.
- No live provider calls, provider credentials, or network-backed execution were used.

#### Attempt 4 Publication

- Implementation commit: `3982471`, pushed to `origin/task/ARCH-021-COMMERCE-006`.
- Parent report commit: pending after this metadata/report update.
- Final task metadata: `status: review`, `executor: null`, `claimed_at: null`, `attempt: 4`.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 4 resolves the final saved-vs-unsaved/publication-integrity defect identified in Attempt 3 without reopening the accepted CAS, publication, QuickJS or preview mechanics.

`ExternalHttpEditor` now owns a `canSaveDraft()` preflight for the JavaScript composition slot. Before a JavaScript-panel save can reach the durable `updateToolDraft(...)` path, the preflight parses and schema-validates both visible execution-definition buffers that can otherwise remain local while invalid: `Advanced response processing JSON` (`advanced`) and `Response shape / resultSchema JSON` (`schemaText`). `ProductionCodeResponsePanel` enforces that preflight immediately before invoking the existing `onSaveDraft` callback. If either visible buffer is invalid, no Tool draft write occurs and the shared U06 dirty/navigation guard remains active.

`StudioWorkspace` also tracks the editor's execution-definition validity for the enclosing full-draft save. This preserves the same exact-definition publication invariant outside the JavaScript-panel save path: a visibly invalid execution buffer cannot be silently bypassed by the parent save operation.

The focused regression demonstrates the required JavaScript edit -> invalid Response-shape JSON -> JavaScript Save path: no `updateToolDraft` command is issued and Manage Connections remains behind the unsaved-changes guard. The same preflight parses the Advanced response-processing buffer, so separate exhaustive duplication is not required for this functionality-focused acceptance.

The accepted Attempt 2/3 behavior remains intact: authoritative `editVersion` continuity, complete top-level Input JSON Schema / Response template persistence, current JavaScript validation/sample publication handoff, server-only QuickJS execution, preview cancellation/reconciliation, ADMIN/SUPER_ADMIN boundaries, and the Phase 1 no-provider-network/no-credential-access rule.

Implementation handoff: `39824714febb6198645a5f4e151f8acc33bb8c70`. Submitted parent report handoff: `ad00499156b587bf10513033e719b5a4f5030113`.

### Reviewed Files

- `components/studio-workspace.tsx`
- `src/studio/external-http/editor.tsx`
- `src/studio/external-http/ports.ts`
- `src/studio/code-response/production-panel.tsx`
- `src/studio/code-response/code-response-panel.tsx`
- `tests/external-tools-ui.test.tsx`
- `docs/decisions/commerce/ARCH-021/COMMERCE-006-install-javascript-response-panel-production-composition.md`
- `docs/decisions/commerce/ARCH-021/_index.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

- Submitted U06 focused suite: 13 passed.
- Submitted focused response/preview suite: 105 passed.
- Submitted targeted ESLint: passed.
- Submitted `git diff --check`: passed.
- Submitted repository typecheck remains non-zero on the documented baseline (`234 errors in 14 files`); the functionality-focused review found no task-owned regression requiring another attempt.
- Static comparison with Attempt 3 confirms the correction is narrowly scoped to the visible execution-definition validity/preflight boundary plus its focused regression.
- The supplied review archive contains no `node_modules`, so the architect did not rerun the submitted Node/Vitest commands in the review container.

### Architecture Conformance

Conformant.

COMMERCE-006 now satisfies the production JavaScript response-panel composition contract and the saved-vs-unsaved identity requirements discovered during review. Publication eligibility corresponds to the exact persisted Tool definition under review, invalid visible definition buffers retain navigation/publication protection, and no parallel durable state or publication mechanism was introduced.

With COMMERCE-001 through COMMERCE-006 architect-accepted Complete, the ARCH-021 Phase 1 exit criteria are satisfied. The parent architecture remains `Agreed`, not `Implemented`, because Phases 2-9 are intentionally not yet materialised or completed.

### Follow-up

No implementation correction is required for COMMERCE-006. The task is Complete and the Phase 1 implementation set is closed.

Phase 2 remains intentionally unmaterialised. No Phase 2 task is implicitly Ready or launched by this acceptance; the next architecture step is to define the bounded Phase 2 task set when the developer chooses to proceed.
