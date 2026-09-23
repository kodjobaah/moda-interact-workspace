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
attempt: 3
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

Ready for Review (Attempt 3 corrections complete)

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

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 3 correctly resolves the specific top-level sibling-buffer defect from the Attempt 2 correction contract and preserves the accepted Attempt 2 CAS/publication fixes.

The JavaScript draft-save path now parses and schema-validates the current `inputSchemaText` and `responseTemplateText`, persists those values together with the current JavaScript source in the same `updateToolDraft(...)`, refreshes the authoritative returned definition/buffers/edit version, and only then clears the shared U06 dirty state. Invalid top-level sibling JSON performs no write and retains the navigation guard. The focused U06 regression proves that path, and the submitted functionality-focused suites are sufficient.

One remaining production-functional saved-vs-unsaved defect exists in the same U06 JavaScript save boundary.

`ExternalHttpEditor` also owns independently buffered JSON editors that are visibly part of the U06 Tool definition:

- `Advanced response processing JSON` (`advanced`)
- `Response shape / resultSchema JSON` (`schemaText`)

When either editor contains invalid JSON, its local buffer is retained and the shared U06 dirty state is set, but the invalid value is intentionally not copied into `definition`. A user can therefore:

```text
edit JavaScript source
-> enter invalid Advanced response processing JSON or Response shape JSON
-> JavaScript panel Save draft
-> saveCodeDraft(...) persists the previous valid execution value
-> setDirty(false)
```

The invalid editor text remains visibly displayed even though the persisted Tool revision contains the previous value. A subsequent validate/sample cycle can make `externalValidated` current again and enable SUPER_ADMIN publication against the persisted revision while U06 still visibly shows an unpersisted invalid execution value.

This is the same saved-vs-unsaved/publication-integrity invariant as the Attempt 2 correction, not an exhaustive-test concern.

The Attempt 3 implementation commit is `5991dde`; the submitted parent report commit is `2b37c7b`.

### Reviewed Files

- `components/studio-workspace.tsx`
- `src/studio/external-http/editor.tsx`
- `src/studio/code-response/code-response-panel.tsx`
- `src/studio/code-response/production-panel.tsx`
- `tests/external-tools-ui.test.tsx`
- `docs/decisions/commerce/ARCH-021/COMMERCE-006-install-javascript-response-panel-production-composition.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

The submitted functionality-focused validation is sufficient: the U06 suite reports 12 passing tests; the focused composition/preview set reports 104 passing tests; the response/preview integration subset reports 76 passing tests; targeted ESLint and `git diff --check` passed. The documented QuickJS runtime-proof failure and repository-wide typecheck baseline remain unrelated and are not blockers.

No exhaustive test expansion is requested. The next correction needs only focused proof for the remaining editor-buffer publication-integrity path.

### Architecture Conformance

Partial.

The production JavaScript response-panel composition, authoritative edit-version continuity, JavaScript validation/publication handoff, complete top-level U06 schema/template persistence, server-only QuickJS/external-preview execution, cancellation/reconciliation and Phase 1 no-provider-network/credential boundaries conform.

Phase 1 cannot close while a JavaScript save can clear the shared U06 dirty/navigation/publication guard although another visible Tool-definition JSON editor still contains an unpersisted invalid value.

### Follow-up

Attempt 4 correction contract:

1. Preserve the accepted Attempt 2 CAS/publication fixes and the Attempt 3 complete top-level `Input JSON Schema` / `Response template` persistence unchanged.
2. Before any JavaScript-panel save may clear the shared U06 dirty state, account for the visible `ExternalHttpEditor` definition buffers as well. In particular, invalid `Advanced response processing JSON` or invalid `Response shape / resultSchema JSON` must remain dirty and must not be silently bypassed by saving JavaScript.
3. Publication must continue to represent the exact persisted Tool definition visibly under review. If a visible execution-definition buffer is invalid/unpersisted, navigation/publication protection must remain active until that state is corrected, discarded through an accepted guard, or successfully persisted.
4. Use the smallest coherent correction. Do not create a second durable Tool definition, a second publication path, provider networking, credential access, or a new response-processing engine.
5. Add only focused functional regression proof for this path. For example: edit JavaScript -> make Response shape JSON invalid -> JavaScript Save draft -> no false-clean state/no publication eligibility; equivalent coverage for the shared preflight mechanism is sufficient. Exhaustive editor testing is not required.
6. Preserve all accepted server-side QuickJS/external-preview, cancellation/reconciliation, ADMIN/SUPER_ADMIN and no-provider-network/credential boundaries.

Return this same task through the normal launcher. Preserve `attempt: 3`; the next authorized claim increments it to Attempt 4.
