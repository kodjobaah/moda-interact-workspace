---
id: ARCH-025-COMMERCE-002
architecture_id: ARCH-025
title: Extract immutable Release Composer
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
claimed_at: 2026-10-02T23:33:24Z
attempt: 1
depends_on:
  - ARCH-025-COMMERCE-001
enables:
  - ARCH-025-COMMERCE-003
created: 2026-10-02
updated: 2026-10-02
---

# Extract immutable Release Composer

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract immutable Release composition and response-contract validation into a dedicated module without changing validation freshness, role gating, creation or navigation semantics.

## Context

`ReleaseComposer` is the largest domain-specific view in StudioWorkspace and owns a complete local state/validation lifecycle distinct from global workspace orchestration. COMMERCE-001 already establishes the global command/navigation contract it consumes.

## Scope

Authorised implementation surface:

```text
components/studio-workspace.tsx
components/studio-workspace/release-composer.tsx
tests/release-composer.test.tsx
```

## Out of Scope

Workspace-controller changes, Release Detail extraction, Shop views, generic page-router extraction, server-action or contract changes.

## Requirements

### Common ARCH-025 StudioWorkspace invariants

- This is a **move-only structural refactor**. Do not change Studio product behaviour, server-action signatures/authorization, persistence semantics, Tool authoring, Agent Configuration, Discovery, Test Conversations/Preview or Shop execution contracts.
- Preserve `StudioWorkspace` and the `StudioPage` type at `components/studio-workspace.tsx`. Existing production callers/browser-evidence fixtures do not migrate.
- Preserve route identity as `page:detailId:revisionId:authoringSessionId`, while the page/detail load effect continues to trigger only from `page`, `detailId` and `revisionId`; changing only `authoringSessionId` must not add a Studio data load.
- Preserve one-time `initialResult`/`initialDetail` hydration suppression through the hydrated route identity and monotonic `loadToken` stale-result rejection.
- Preserve current page-load/provider cardinality/order: Tool list/detail, Explore schema, Release list/detail and Shop list/detail calls must not be added, removed, merged or reordered as incidental cleanup. Agent Configuration still performs no Studio list/detail server action and sets the bounded local loaded state.
- Preserve write single-flight through the current pending ref/token semantics. A second write is not admitted while one is pending; an `unknown` outcome stores the original operation ID, label, run callback, admitted content revision and optional success callback for reconciliation.
- Preserve the current operation-ID format (`c` + base36 `Date.now()` + 18 hex-like UUID characters with hyphens removed) everywhere it is used, including Release edit-as-new handoff.
- Preserve content-revision dirty fencing: `setDirty(true)` increments the content revision; a successful command clears dirty only when the submitted revision still equals the current revision.
- Preserve Studio composer navigation blocking: dirty Agent Configuration state, unconfirmed Agent Configuration operations and unknown workspace operations continue to participate in the existing blocker/lock semantics.
- Preserve specialised early-return boundaries: `AgentConfigurationScreen` and `ToolAuthoringScreen` remain outside the generic `<main>` page/detail router and retain their current props/data handoff.
- Preserve `StudioComposerContext`, `DirtyNavigationGuard`, `StudioState`, `ToolAuthoringScreen`, `AgentConfigurationScreen`, `AdminExplorer` and `src/studio/server-actions.ts` as canonical existing owners. Do not create a new router, plugin framework, command bus, state store or DI framework.
- Preserve exact current strings/routes/role gates and current source quirks during extraction. Do not opportunistically redesign Shop search/Preview/Test links, dirty clearing, validation messages or confirmation behaviour.
- These tests are frozen byte-for-byte throughout COMMERCE-001..005: `tests/studio-workspace.test.tsx` (`400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7`, 13 tests), `tests/agent-configuration-screen-state.test.tsx` (`72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a`, 3 tests), `tests/external-tools-ui.test.tsx` (`97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3`, 90 tests).
- `tests/legacy-capability-surface.test.ts` and `tests/arch024-preview-cleanup.test.ts` may be changed only by COMMERCE-001 and only to make their source loader follow the bounded StudioWorkspace module set without deleting/weakening existing assertions. COMMERCE-002..005 must not modify the accepted COMMERCE-001 versions.
- No ARCH-025 Commerce task may modify the adjacent canonical owner files listed in the parent regression baseline except for import-only changes explicitly authorised by that task.
- Keep tests honest: no skipped/only/todo tests, weakened expectations or new behavioural expectations merely to accommodate extraction.

### R1 — Release Composer ownership

Move the entire current `ReleaseComposer` workflow into `components/studio-workspace/release-composer.tsx`. Release-specific state remains local to that component: open/closed state, exact members/positions, capability options, instructions, raw schema text, publication reason, validation state/pending/generation/hash refs. Do not move it into the global workspace controller.

### R2 — initial seed/default semantics

Preserve seed precedence exactly: `composer.release` before the currently ACTIVE release before the existing default response contract/instructions/reason. Preserve `open = Boolean(seed)`. Continue loading `listReleaseCapabilities()` once on mount and ignore non-OK results as today.

### R3 — candidate parsing/freshness

Preserve `CommerceResponseContractSchema.safeParse(...)`, raw invalid JSON retention, `JSON.stringify({ members, responseContract })` canonical input hash, generation token, duplicate-validation guard and current-input-hash fence. Member/instructions/schema changes mark dirty and stale validation; publication-reason changes mark dirty but do **not** stale validation. An old asynchronous validation result must never validate newer content.

### R4 — role/create/cancel semantics

Preserve the current asymmetric role behaviour exactly. The top-level **Create release** opener is shown only to `SUPER_ADMIN`, while `ADMIN` receives the explanatory copy. However, when the composer is already open from `composer.release` seed state (for example via Edit as new release), the inner **Create immutable release** button is currently gated only by `pending || locked || !validated` and is not independently hidden/disabled by role; server authorization remains authoritative. Do not add a new client role gate during extraction. Preserve the exact create payload, success navigation to `/releases/<id>?tab=response-contract`, and `DirtyNavigationGuard` Cancel behaviour. Do not restore any obsolete Preview/Test handoff.


## Work Items

- [ ] Move Release Composer into the dedicated module.
- [ ] Keep all Release-specific state/validation local to that module.
- [ ] Add focused Release Composer tests for seed/default/freshness/single-flight/create/cancel behaviour.
- [ ] Keep the accepted COMMERCE-001 controller and source-inspection tests unchanged.


## Interfaces / Contracts

Consumes the accepted COMMERCE-001 common workspace props/command contract. Release candidate state remains module-local.

## Dependencies

- `ARCH-025-COMMERCE-001`

## Enables

- `ARCH-025-COMMERCE-003`

## Acceptance Criteria

- [ ] Releases page renders the same records/composer UI through the extracted module.
- [ ] Validation freshness/single-flight/hash semantics are unchanged.
- [ ] Publication reason still does not stale validation.
- [ ] No Preview handoff or new server action is introduced.
- [ ] SUPER_ADMIN-only opener / seeded-composer ADMIN submission asymmetry is unchanged; no new client create-role gate is introduced.
- [ ] Frozen 13/3/90-test assets and accepted COMMERCE-001 source-inspection tests are unchanged and pass.


## Validation

- [ ] `node -e "const fs=require('node:fs'),c=require('node:crypto');const e={'tests/studio-workspace.test.tsx':'400ce6b68cb5a9fdeecf9233bc2b3f58a42742c974da2c5b6ffd2b5a16ae44a7','tests/agent-configuration-screen-state.test.tsx':'72c71a09eaf5bdc2d79c686cf5ec43d5abfd49cfe421cadedbbe665140582b0a','tests/external-tools-ui.test.tsx':'97ffbc70e29d4ff60a48e5aabd0ff3faec6dea7984ed0f239fcb4a8fc868f4d3'};for(const [p,x] of Object.entries(e)){const h=c.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!==x){console.error(p,h);process.exitCode=1}else console.log(p,h)}"` prints all expected frozen hashes.
- [ ] `npx vitest run tests/release-composer.test.tsx tests/studio-workspace.test.tsx tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` passes.
- [ ] `git diff -- tests/legacy-capability-surface.test.ts tests/arch024-preview-cleanup.test.ts` is empty.

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
