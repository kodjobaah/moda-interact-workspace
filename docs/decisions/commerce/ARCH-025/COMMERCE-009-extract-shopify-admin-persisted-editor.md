---
id: ARCH-025-COMMERCE-009
architecture_id: ARCH-025
title: Extract persisted Shopify Admin Tool editor
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: copilot
claimed_at: 2026-10-03T19:39:36Z
attempt: 1
depends_on:
  - ARCH-025-COMMERCE-008
enables:
  - ARCH-025-COMMERCE-010
created: 2026-10-02
updated: 2026-10-03
---

# Extract persisted Shopify Admin Tool editor

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Supplementary observations: `docs/architecture/ARCH-025-tool-editor-refactor-observations.md`

Coordinator: `moda_architect`

## Objective

Extract the persisted Shopify Admin GraphQL DRAFT workflow into a focused wrapper that preserves compiler/result-contract freshness, Explore handoff, Test, save and publish behaviour.

## Context

The Admin branch has distinct variable mapping and derived result-contract semantics. It must move without conflating mapping freshness with query/result identity or changing the existing server-authoritative publication gate.

## Scope

Authorised implementation surface:

```text
src/studio/tools/tool-editor.tsx
src/studio/tools/authoring/persisted-shopify-admin-tool-editor.tsx
tests/persisted-shopify-admin-tool-editor.test.tsx
```

## Out of Scope

Common controller changes, Shopify Admin compiler/editor redesign, Explore workflow redesign, server-action changes, publication-rule cleanup or observed-issue fixes.

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

### R2 — Admin request/result freshness

Preserve the current distinction: document, operationName, apiVersion, schemaHash or resultPath changes stale `adminResultContractFresh`; variable/literal mapping-only changes do **not** stale the already-derived result contract. Preserve `adminMappingValid` independently.

### R3 — Explore Shopify handoff

Preserve the exact existing `onOpenAdminExplore` existing-draft authoring-session payload: tool/revision identity, current candidate, Result Template metadata and raw editor buffers (`section`, input/response/result-schema/result-path/literal text). No persistence occurs merely by opening Explore.

### R4 — Test/save/publish convergence

Preserve current Test requirement before save, result-contract/mapping gates, CAS editVersion, returned saved definition/editVersion restoration, dirty clearing, `adminValidated` reset, editor remount and authoring-session consumption. Preserve current publish action/reason/client gates and server-authoritative `LIVE_TEST_REQUIRED` behaviour; do not introduce a new client Test publication gate in this structural task.

### R5 — Result Template/Review

Preserve output-schema fallback, Result Template metadata/validation and Review candidate/presentation exactly.

### R6 — RevisionHistory remains shell-owned until COMMERCE-010

Keep `RevisionHistory` rendered by `ToolEditor`; do not duplicate it in the Admin wrapper or import it back from the shell. COMMERCE-010 owns the eventual `revision-history.tsx` extraction.

## Work Items

- [ ] Extract Shopify Admin persisted DRAFT wrapper.
- [ ] Keep RevisionHistory shell-owned until COMMERCE-010.
- [ ] Keep `ShopifyAdminEditor`, `ShopifyAdminResponseEditor` and `ShopifyAdminTestTab` canonical.
- [ ] Add focused wrapper tests where useful.
- [ ] Prove controller, Policy/External wrappers and frozen suites remain unchanged.

## Interfaces / Contracts

Repository-internal persisted Shopify Admin DRAFT wrapper consuming the common controller and existing Admin editor/compiler/server actions.

## Dependencies

- `ARCH-025-COMMERCE-008`

## Enables

- `ARCH-025-COMMERCE-010`

## Acceptance Criteria

- [ ] Admin mapping/result-contract freshness semantics are unchanged.
- [ ] Explore authoring-session round trip is unchanged.
- [ ] Save uses returned editVersion and existing convergence semantics.
- [ ] Existing client/server publication behaviour is unchanged.
- [ ] Prior accepted modules/tests remain unchanged.

## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/shopify-admin-tools-ui.test.tsx':'d856cac3626605670e08a21826cfcc1a8e6595dcffc764e20d9ef59c2ff78446','tests/tool-authoring-screen.test.tsx':'2245e54996589f7289639bb28c6b364f1726ec291debec390e208a5c304b6c20','tests/new-tool-authoring-state.test.ts':'267352261520b38eaa9845f93dc09eb8860e75a4010d9da26827c6617bcdcf63'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `npx vitest run tests/persisted-shopify-admin-tool-editor.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/tool-authoring-screen.test.tsx` passes.
- [ ] `git diff -- src/studio/tools/authoring/use-persisted-tool-authoring-controller.ts src/studio/tools/authoring/persisted-policy-operation-tool-editor.tsx src/studio/tools/authoring/persisted-external-http-tool-editor.tsx tests/external-tools-ui.test.tsx` is empty.
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
