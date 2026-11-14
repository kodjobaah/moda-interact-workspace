---
id: ARCH-075-ADMIN-010
architecture_id: ARCH-075
title: Expose common composite media bindings and dimensions
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-14T11:47:43Z
attempt: 1
depends_on:
  - ARCH-075-ADMIN-009
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Expose common composite media bindings and dimensions

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Expose truthful common-template media bindings with discoverable saved logo/product dimensions and matching schematic preview.

## Context

ADMIN009 is Complete and already provides compositeProfile geometry. Existing logoWidth/Height and productWidth/Height controls are hidden under a profile checkbox. response.productImage is an AI-only optional BEFORE_BODY binding; SHARED composite runtime independently uses the verified selected product. Do not expose a selectable SHARED field the worker ignores.

## Scope

Admin template editor controls, binding explanation and preview; focused UI/persistence regression tests.

## Out of Scope

Shared releases, Background semantics, new variables/URLs/media sources, provider registration, live edits, activation, database/schema changes, independent configuration policy.

## Requirements

Show fixed trusted shop-logo and optional verified selected-product bindings for SHARED common composites; identify image absence/no-product behavior honestly. Reuse existing compositeProfile numeric dimensions and validation, grouped clearly as Logo size and Product image size. Make required profile discoverable rather than hidden behind an unchecked optional-looking control. Preserve existing AI productImage binding behavior. Do not save SHARED productImage or imply arbitrary binding choices. Preview uses same saved/unsaved geometry, product/no-product variants and caption position; label schematic accurately. Preserve canonical source/profile hashing, explicit clone/review workflow, locale equality, bounds, and historical audit display. No infrastructure or telemetry changes.

## Work Items

- [x] Inspect current editor/binding/preview seams.
- [x] Expose fixed SHARED media bindings and grouped dimensions.
- [x] Update matching preview and focused regressions.
- [x] Record exact isolation/source/check evidence.

## Interfaces / Contracts

Published Shared6.0.0 compositeProfile and existing AI ConversationProductImageBinding remain unchanged. SHARED presentation uses existing runtime-selected verified product, not an invented response variable.

## Dependencies

ARCH-075-ADMIN-009 Complete and integrated.

## Enables

None

## Acceptance Criteria

- [x] SHARED editor visibly explains actual logo/verified-product binding without unsupported selectable fields.
- [x] Logo/product width and height are explicit, discoverable and persist through existing clone/save/read.
- [x] Preview reflects edited dimensions and no-product case; AI binding behavior unchanged.
- [x] Invalid dimensions/profile and immutable existing revisions remain protected.

## Validation

- [x] Focused editor/preview/profile persistence tests and relevant authoring tests.
- [x] Types, scoped lint, production build and exact remote check.
- [x] Inspect package scripts; no unaffected PG/full-suite repeats unless relevant failure requires them.
- [x] Diff/privacy and browser-safe dependency graph checks appropriate to changed imports.

## Stop Condition

After work/checks publish source and mirrored report, set review and STOP. Root owns all merges/live operations.

## Implementation Notes

Normal moda-task launcher must create dedicated sibling worktrees; task authoring created only parent worktree. You are not alone; preserve others. Prefer existing controls and preview over new editor/framework. Return any genuine unsupported runtime binding requirement before implementing contract changes.

## Completion Report

### Status

Ready for Review — exact source and all required checks passed; no merge or live operations performed.

### Files Changed

- `template-composite-profile-editor.tsx`: fixed trusted binding labels, required-profile discovery, grouped logo/product size and existing canvas/placement controls.
- `template-composite-profile-preview.tsx`: visible slot dimensions, precise selected-product sample toggle and header-only explanation, contain/scaling limitation.
- `arch075-template-composite-profile-components.test.tsx`: actual interaction, persistence/hash/clone and preview regressions.

### Work Completed

Source `7782f4c16a6b2c31a15341585a565cb578029cb6` pushed on `task/ARCH-075-ADMIN-010`, Admin PR [99](https://github.com/kodjobaah/moda-interact-admin/pull/99). Current SHARED geometry is immediately visible; historical clones explicitly add their required profile. Fixed `LOGO` and `response.productImage` / `BEFORE_BODY` sources are displayed as explanations, never selectable fields. No SHARED productImage is saved. The no-selected-product header-only case is distinguished from unverified selected-product media, which falls back to complete text. Existing AI-only binding and server bounds are unchanged.

### Validation Results

- Focused six-suite authoring/media/profile regression run: **53 passed, 0 failed, 0 skipped**. Actual component handlers edit all four logo/product dimensions while preserving all authored text; immutable serialization/read, source/prepared hashes and CloneAsNew retain exact geometry. Preview state toggles product/no-product canvas and retains caption. Existing AI and authoring service regressions pass.
- `npx tsc --noEmit` and scoped ESLint for all three changed files: passed.
- Declared scripts inspected; no unaffected PostgreSQL/full-suite repeats for this UI-only change, with existing persistence APIs exercised through immutable record compile/read/clone.
- `npm run build`: passed (terminal exit 0); existing optional BullMQ Valkey-resolution warnings unchanged. Production browser graph scanned across 71 JS files: no Node renderer, font loader or frozen-verifier markers. Diff/privacy checks passed; package and lock unchanged.
- Exact source `7782f4c16a6b2c31a15341585a565cb578029cb6`: Vercel SUCCESS at 2026-11-14T11:56:05Z, Preview Comments SUCCESS at 11:56:06Z.
- Root independently exercised the actual local editor/preview: logo 140×120 and product 1000×500 reflected immediately; invalid logo width 500 produced the bounds alert; no-product sample removed the product slot and selected the 1125×300 header-only canvas. Local fictional fixture uses actual components, no production route/database/customer data; local server stopped after review.

### Deviations

None

### Assumptions

Root owns main integration and all live operations. No runtime, Shared release, database, package/lock, registration or activation change. Existing slot dimensions use contain without cropping; WhatsApp scales the final image and no native-header sizing guarantee is made.

### Unresolved Issues

None

### Architectural Concerns

None. Physical isolation: prepared canonical root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`, parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-ADMIN-010`, implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-ADMIN-010`, both `task/ARCH-075-ADMIN-010`. Launcher verified existing remote/main synchronization, dependency Complete, recursive Database at `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`; implementation base `f84a32cb8c2f24d076c7eeda9c80e2f472b4459e`. Attempt1 claim `3e5eee2012a217f334cc0dc272940a489b7b1d34` pushed. No primary/other task source changes.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

Root integration after acceptance
