---
id: ARCH-025-COMMERCE-008
architecture_id: ARCH-025
title: Extract persisted External HTTP Tool editor
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-025-COMMERCE-007
enables:
  - ARCH-025-COMMERCE-009
created: 2026-10-02
updated: 2026-10-03
---

# Extract persisted External HTTP Tool editor

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Supplementary observations: `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`

Coordinator: `moda_architect`

## Objective

Extract the persisted External HTTP DRAFT workflow into a focused wrapper while preserving request/response validation, live-Test, Result Template, Review and publication semantics.

## Context

External HTTP is the largest execution-kind branch. It owns authorised connection availability, request/response authoring actions, local raw response-processing/result-schema buffers, live Test, authoritative Review validation, save convergence and publication presentation.

## Scope

Authorised implementation surface:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/persisted-external-http-tool-editor.tsx
tests/persisted-external-http-tool-editor.test.tsx
```

## Out of Scope

Common controller changes, ExternalHttpEditor/response implementation redesign, provider protocol changes, publication-rule cleanup or observed-issue fixes.

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

### R1 — consume-only controller

Consume the accepted COMMERCE-006 controller without expanding it.

### R2 — External provider/authoring boundary

Preserve `ExternalHttpEditor`, preview request, request validation, response observation, response validation and live-Test action ownership exactly. Preserve authorised-port unavailable presentation and connectionRevisionId pinning. Do not add/remove provider calls.

### R3 — External revisions/Test/Result Template

Preserve Request/Response/Result Template revision advancement and STALE transitions, local raw response-processing/result-schema retention, Result Template metadata and validation, and current live-Test requirement before save. Preserve the current no-port asymmetry recorded as observation O9: when the authorised External port is unavailable, editing the fallback raw Input Schema marks dirty and invalidates External validation but does **not** explicitly advance the common Request revision. Do not normalise that path during extraction.

### R4 — Review validation/save convergence

Preserve Review action-key generation/in-flight fencing. On save, preserve `candidateWasValidated` capture and retain `externalValidated` only when the returned saved definition is canonically identical to the submitted candidate. Preserve the existing post-save asymmetries documented in the observations file; do not normalize them.

### R5 — publication

Preserve current SUPER_ADMIN gate, dirty/definition/authoritative-validation/reason checks and server-authoritative `LIVE_TEST_REQUIRED` behaviour exactly. Do not add a new client Test publication gate in this structural task.

### R6 — shell-owned RevisionHistory and source-shape branch

Keep `RevisionHistory` rendered by `ToolEditor` until COMMERCE-010; do not duplicate it or import it back from the shell into the wrapper. Keep exactly one source-shape branch matching the accepted persisted External DRAFT uniqueness assertion (`selected?.status === "DRAFT"` plus `definition.execution.kind === "EXTERNAL_HTTP"`) in the bounded ToolEditor module set after extraction.

## Work Items

- [ ] Extract External persisted DRAFT wrapper and server-action wiring.
- [ ] Keep RevisionHistory and the single persisted-External dispatch condition shell-owned until COMMERCE-010.
- [ ] Keep existing specialised External editor/result/review components canonical.
- [ ] Add focused wrapper tests for save/validation convergence if needed.
- [ ] Prove controller, Policy wrapper and accepted External source harness remain unchanged.

## Interfaces / Contracts

Repository-internal persisted External HTTP DRAFT wrapper consuming the common controller and existing External authoring ports/actions.

## Dependencies

- `ARCH-025-COMMERCE-007`

## Enables

- `ARCH-025-COMMERCE-009`

## Acceptance Criteria

- [ ] External Request/Response/Test/Result Template/Review behaviour is unchanged.
- [ ] One provider/action call pattern and stale-validation suppression are unchanged.
- [ ] Returned-candidate equality controls validation retention exactly as today.
- [ ] Existing server-authoritative publication rejection behaviour is preserved.
- [ ] Prior accepted modules/tests remain unchanged.

## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/shopify-admin-tools-ui.test.tsx':'d856cac3626605670e08a21826cfcc1a8e6595dcffc764e20d9ef59c2ff78446','tests/tool-authoring-screen.test.tsx':'2245e54996589f7289639bb28c6b364f1726ec291debec390e208a5c304b6c20','tests/new-tool-authoring-state.test.ts':'267352261520b38eaa9845f93dc09eb8860e75a4010d9da26827c6617bcdcf63'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `npx vitest run tests/persisted-external-http-tool-editor.test.tsx tests/external-tools-ui.test.tsx` passes.
- [ ] `git diff -- src/studio/tools/authoring/use-persisted-tool-authoring-controller.ts src/studio/tools/authoring/persisted-policy-operation-tool-editor.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx tests/new-tool-authoring-state.test.ts` is empty.
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
