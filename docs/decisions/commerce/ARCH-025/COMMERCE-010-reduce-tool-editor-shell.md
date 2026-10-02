---
id: ARCH-025-COMMERCE-010
architecture_id: ARCH-025
title: Reduce ToolEditor to final thin persisted-authoring dispatch
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-COMMERCE-009
enables: []
created: 2026-10-02
updated: 2026-10-02
---

# Reduce ToolEditor to final thin persisted-authoring dispatch

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Supplementary observations: `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`

Coordinator: `moda_architect`

## Objective

Extract generic revision/read-only/fallback views and reduce `tool-editor.tsx` to the public compatibility shell that selects a revision and dispatches to accepted persisted execution-kind wrappers.

## Context

After COMMERCE-006..009, shared state and all three supported persisted execution-kind workflows have stable owners. The remaining code is revision selection/history, no-revision/create-draft, published read-only/edit-as-new, defensive generic DRAFT editing and final dispatch.

## Scope

Authorised implementation surface:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/revision-history.tsx
src/studio/tools/authoring/definition-read-only.tsx
src/studio/tools/authoring/persisted-generic-tool-editor.tsx
tests/tool-editor-dispatch.test.tsx
```

## Out of Scope

Controller/wrapper redesign, new execution kinds, plugin registration framework, publication-rule cleanup, observed-issue fixes or server-action changes.

## Requirements

### Common ARCH-025 ToolEditor invariants

- This is a **move-only structural refactor**. Do not change Tool authoring product behaviour, server-action signatures/authorization, publication semantics, provider protocols, Test checkpoint rules, CAS/editVersion semantics, Result Template semantics or execution-kind contracts.
- Preserve `ToolEditor` at `src/studio/tools/tool-editor.tsx` with the same public props/caller boundary. Existing `ToolAuthoringScreen` and Studio callers do not migrate.
- Preserve persisted DRAFT execution-kind dispatch for `POLICY_OPERATION`, `EXTERNAL_HTTP` and `SHOPIFY_ADMIN_GRAPHQL`, plus the existing published/no-revision/defensive-generic paths.
- Preserve the six persisted authoring tabs and default persisted tab `request` unless an existing authoring session contains one of the accepted persisted sections.
- Preserve `new-tool-authoring-state.ts` as the canonical Test/revision/result-template freshness engine. Do not invent another revision/checkpoint model in the controller or wrappers.
- Preserve Test freshness/STALE transitions, candidate/revision identity, transient Test argument/shop semantics and the exact requirement that saved/published evidence belongs to the current candidate.
- Preserve Review-validation generation fencing including A→B→A protection and duplicate in-flight suppression. Do not reduce it to canonical-value equality alone.
- Preserve current execution-kind-specific validation/action ownership. The shared controller owns common candidate/revision/reset/save convergence state; External/Admin/Policy wrappers own their existing provider/execution-kind validation calls and presentation.
- Preserve current save/cancel/publish asymmetries documented in `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`. They are follow-up observations, not authority to normalize behaviour in ARCH-025.
- Preserve immutable Policy Operation MCP name and operation/operationVersion binding, External connection-revision pinning, and Shopify Admin schema/result-contract identity rules.
- Preserve `SUPER_ADMIN` publication gating and current publication-reason behaviour per execution kind.
- Preserve `StudioComposerContext` authoring-session handoffs and the exact existing Explore Shopify return payload. Do not redesign Studio navigation or authoring-session ownership.
- Reuse existing specialised owners: `policy-operation-editor.tsx`, `external-http/editor.tsx`, `shopify-admin-editor.tsx`, `shopify-admin-response-editor.tsx`, `authoring/result-template-tab.tsx`, `authoring/review-tab.tsx`, `authoring/shopify-admin-test-tab.tsx`, `authoring/tool-authoring-tabs.tsx`, `authoring/tool-authoring-step-navigation.tsx` and `new-tool-authoring-state.ts`.
- Do not create a generic execution-kind plugin/registration framework, new state store, command bus or DI framework solely for this extraction.
- These tests are frozen byte-for-byte throughout COMMERCE-006..010: `tests/shopify-admin-tools-ui.test.tsx` (`d856cac3626605670e08a21826cfcc1a8e6595dcffc764e20d9ef59c2ff78446`), `tests/tool-authoring-screen.test.tsx` (`2245e54996589f7289639bb28c6b364f1726ec291debec390e208a5c304b6c20`) and `tests/new-tool-authoring-state.test.ts` (`267352261520b38eaa9845f93dc09eb8860e75a4010d9da26827c6617bcdcf63`).
- `tests/external-tools-ui.test.tsx` starts at SHA-256 `97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3`. COMMERCE-006 may change only its bounded source-loading mechanism for the existing “one persisted External DRAFT implementation” assertion; all other assertions/behaviour remain unchanged. COMMERCE-007..010 must not modify the accepted COMMERCE-006 version.
- No task may weaken, skip, delete or rewrite assertions merely to accommodate extraction.

### R1 — final dispatch

Reduce `tool-editor.tsx` to controller composition and small discriminated dispatch using the **accepted COMMERCE-006 selected/base/default-definition state** rather than reimplementing revision selection or default/base restoration in the shell: no selected revision; published revision; Policy DRAFT; External DRAFT; Shopify Admin DRAFT; defensive generic DRAFT fallback. Keep exactly one persisted External DRAFT branch so the accepted source-shape assertion remains meaningful.

### R2 — revision/read-only behaviour

Move `RevisionHistory` and `DefinitionReadOnly` without changing links/text. `ToolEditor` remains the owner that renders RevisionHistory around selected Policy/External/Admin/generic DRAFT wrappers; accepted wrappers from COMMERCE-007..009 are not modified merely to inject history. Preserve the no-selection `Revision history` heading/list and create-draft flow using the controller's exact current default definition. Preserve Edit-as-new from published revision, including existing `createToolDraft` inputs/navigation. Published Policy continues using `PublishedPolicyOperationReadOnly`; other published definitions use generic read-only.

### R3 — generic fallback

Move the existing defensive generic DRAFT editor as-is, including its parse-error retention, save/publish actions and role gating. Preserve its current use of the selected revision's `editVersion`/direct save-publish behaviour rather than retrofitting execution-kind saved-convergence or persisted Test/Review machinery. Do not invent support for another execution kind.

### R4 — no duplicate orchestration

Final ToolEditor must consume the accepted COMMERCE-006 controller and COMMERCE-007..009 wrappers rather than reimplementing their state/workflows.

## Work Items

- [ ] Extract revision history/read-only/generic fallback presentation.
- [ ] Reduce `tool-editor.tsx` to the final compatibility dispatch shell.
- [ ] Add focused dispatch tests.
- [ ] Prove all accepted controller/wrapper/source-harness files remain unchanged.

## Interfaces / Contracts

Final repository-internal dispatch/presentation contract. Public compatibility remains the existing `ToolEditor` props/export.

## Dependencies

- `ARCH-025-COMMERCE-009`

## Enables

None

## Acceptance Criteria

- [ ] `ToolEditor` public props/import path remain unchanged.
- [ ] Revision/no-selection/published/generic fallback behaviour is unchanged.
- [ ] Supported persisted DRAFT workflows dispatch to exactly one accepted wrapper each.
- [ ] No generic execution-kind plugin framework is introduced.
- [ ] All frozen and accepted suites pass without weakened expectations.

## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/shopify-admin-tools-ui.test.tsx':'d856cac3626605670e08a21826cfcc1a8e6595dcffc764e20d9ef59c2ff78446','tests/tool-authoring-screen.test.tsx':'2245e54996589f7289639bb28c6b364f1726ec291debec390e208a5c304b6c20','tests/new-tool-authoring-state.test.ts':'267352261520b38eaa9845f93dc09eb8860e75a4010d9da26827c6617bcdcf63'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `npx vitest run tests/tool-editor-dispatch.test.tsx tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts` passes.
- [ ] `git diff -- src/studio/tools/authoring/use-persisted-tool-authoring-controller.ts src/studio/tools/authoring/persisted-policy-operation-tool-editor.tsx src/studio/tools/authoring/persisted-external-http-tool-editor.tsx src/studio/tools/authoring/persisted-shopify-admin-tool-editor.tsx tests/external-tools-ui.test.tsx` is empty.
- [ ] `npx vitest run tests/external-tools-ui.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts` passes.
- [ ] `npm test` passes without task-introduced regression.
- [ ] `npm run typecheck` passes.
- [ ] targeted `npm run lint -- <changed Commerce source/test files>` (or repository-equivalent targeted ESLint invocation using the declared lint script) passes.
- [ ] `npm run build` succeeds.
- [ ] `git diff --check` passes.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and **STOP**. Do not begin the enabled or adjacent ARCH-025 Commerce task.

## Implementation Notes

None

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

Pending.

### Follow-up

None
