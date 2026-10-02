---
id: ARCH-021-COMMERCE-065
architecture_id: ARCH-021
title: Split Shopify Admin Request and Response authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 75
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-062
  - ARCH-021-COMMERCE-064
enables:
  - ARCH-021-COMMERCE-068
created: 2026-09-27
updated: 2026-09-27
---

# Split Shopify Admin Request and Response authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make Shopify Admin Tool authoring follow the same conceptual Request/Response separation as External HTTP: Request owns the Admin GraphQL invocation, while Response owns `resultPath` and the compiler-derived read-only `resultSchema` supplied by COMMERCE-062.

## Context

The current Shopify Admin editor places GraphQL, operation name, variable mappings, `resultPath` and raw editable `resultSchema` together in Request, while Response is a placeholder saying that the schema is authored in Request.

That duplicates schema knowledge already available from the pinned Admin query and prevents the result contract from becoming a clean source for Result Template fields.

COMMERCE-064 has already established the Admin Explore round trip. This task changes only the Request/Response authoring responsibility; general traversal/gating remains deferred.

## Scope

Expected implementation areas include:

```text
src/studio/tools/shopify-admin-editor.tsx
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx              # persisted DRAFT parity where this authoring surface exists
src/studio/tools/authoring/                    # focused Shopify Response component if useful
src/studio/tools/*server-actions*.ts           # consume COMMERCE-062 derivation action
app/styles.css

tests/shopify-admin-tools-ui.test.tsx
tests/tool-authoring-screen.test.tsx
```

## Out of Scope

- Explore Shopify schema/query-builder implementation; COMMERCE-064 owns it.
- Result Template tab; COMMERCE-066/068 own it.
- General tab gating/Next/Back coordination.
- Provider execution or live Test UI.
- Manual editing of Admin `resultSchema`.
- External HTTP Response behavior.
- Database schema changes.

## Requirements

### R1 — Request owns only invocation authoring

The Shopify Request tab contains the Admin invocation concerns:

```text
GraphQL document
operation name
variable mappings
Explore Shopify entry point
Admin query validation status/diagnostics
```

Remove editable `resultPath` and editable raw `resultSchema` from Request.

Manual GraphQL remains fully editable.

### R2 — Response owns result selection

The Shopify Response tab contains:

```text
resultPath
non-mutating derive/validate result contract action/status
derived result shape/fields
read-only derived resultSchema disclosure where useful
```

Do not duplicate Request controls here.

### R3 — resultSchema is compiler-produced

When the current Admin document/resultPath is derivable, update the canonical local Tool candidate's `execution.resultSchema` with the exact schema returned by COMMERCE-062.

The author does not type/edit the schema directly.

Temporarily invalid `resultPath` input remains visible locally with Response-local diagnostics; it must not silently revert.

### R4 — schema derivation becomes stale when Request changes

Any change to Admin query identity that can alter the selected result must invalidate the currently displayed derivation success, including:

```text
document
operationName
apiVersion/schemaHash where authoring can change them
resultPath
```

Variable mapping changes do not change the output shape but remain governed by Request validation.

Do not implement tab gating; only mark the Response derivation stale.

### R5 — show the actual derived fields

Present the derived result structure in an understandable read-only form sufficient for an author to see what `data.values` will contain.

Do not require users to understand raw JSON Schema to determine available fields.

A technical read-only schema disclosure may remain available as secondary detail.

### R6 — local-only lifecycle remains intact

For new Tools, Request/Response authoring stays in the existing local/session draft until final Create.

For persisted DRAFTs, deriving the result contract does not save the DRAFT automatically.

### R7 — do not change general navigation semantics

Request and Response remain freely navigable. No tab becomes locked because query/result validation has not been run.

## Work Items

- [x] Remove Result path/schema controls from Shopify Request UI.
- [x] Add Shopify Response authoring component/surface.
- [x] Wire Response derivation to COMMERCE-062.
- [x] Promote only valid derived schemas into canonical local Tool state.
- [x] Retain invalid resultPath text and show actionable Response-local diagnostics.
- [x] Invalidate stale derivation when query/resultPath changes.
- [x] Show derived values structure/read-only schema.
- [x] Cover new Tool and persisted DRAFT authoring parity where applicable.

## Interfaces / Contracts

Consumes COMMERCE-062's non-mutating Admin result-contract derivation.

Produces no new runtime/durable contract beyond the already-canonical persisted `execution.resultSchema`.

## Dependencies

- `ARCH-021-COMMERCE-062`
- `ARCH-021-COMMERCE-064`

## Enables

- `ARCH-021-COMMERCE-068`

## Acceptance Criteria

- [x] Shopify Request contains document, operation and mappings but no editable result schema.
- [x] Shopify Response owns resultPath.
- [x] A valid resultPath derives and installs the canonical local `resultSchema`.
- [x] Invalid resultPath text remains visible and actionable.
- [x] Query changes invalidate prior derived-result success.
- [x] Authors can inspect the resulting `data.values` shape without editing JSON Schema.
- [x] New Tool derivation causes no durable write.
- [x] Persisted-DRAFT derivation does not save automatically.
- [x] Manual GraphQL remains supported.
- [x] Tab navigation remains ungated.

## Validation

- [x] Shopify Admin Request UI tests
- [x] Shopify Admin Response UI tests
- [x] stale-derivation regression tests
- [x] new/persisted authoring lifecycle tests
- [x] targeted lint
- [x] changed-file TypeScript diagnostics
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-068 or COMMERCE-069.

## Implementation Notes

Keep output-schema derivation on the canonical COMMERCE-062 boundary. React must not reconstruct GraphQL response types independently.

## Completion Report

### Status

Ready for Architect Review (Attempt 1)

### Files Changed

- `src/studio/tools/authoring-session.ts`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/shopify-admin-editor.tsx`
- `src/studio/tools/shopify-admin-response-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/admin-explorer.test.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`

### Work Completed

- Implementation commit: `806c93f20f420e9b35d661ba9f18cc689a81fc95` on `task/ARCH-021-COMMERCE-065` (pushed).
- Split Shopify Admin authoring so Request contains invocation fields and Response owns local `resultPath` editing and derivation.
- Used COMMERCE-062's derivation action as the sole source of result schema; successful derivation promotes its schema into local candidate state without an automatic write.
- Added stale-result identity handling for API/schema identity, document, operation name, and result path; mapping-only edits preserve freshness.
- Preserved invalid path text in authoring sessions and exposed compiler issue codes, paths, and messages in Response.
- Rendered a readable `data.values` shape and a read-only schema disclosure.
- Applied the same derivation freshness and save/publish protections to persisted DRAFT authoring, including a submit-handler guard.
- Kept Request/Response navigation ungated and retained manual GraphQL editing.

### Validation Results

- Passed targeted ESLint for all changed source and test files.
- Passed focused Vitest suites: 4 files, 47 tests (`shopify-admin-tools-ui`, `tool-authoring-screen`, `tool-authoring-session`, `admin-explorer`).
- Pylance diagnostics: no errors in the 8 changed files.
- Passed `git diff --check`.
- `npm run typecheck` remains unsuccessful: 28 diagnostics across 17 other package files; none reference the C065 changed files. Diagnostics include missing `lib/preview/http` modules and unrelated compiler, schema typing, and test errors.

### Deviations

No scope deviations. The package-wide typecheck limitation is recorded above; focused tests, lint, and changed-file diagnostics pass.

### Assumptions

The existing persisted `execution.resultSchema` remains the canonical storage contract; session `resultSchemaText` remains only for existing generic Explore/session compatibility and is not editable or used to derive Admin schemas.

### Unresolved Issues

The repository-wide TypeScript check is blocked by 28 diagnostics in files outside this task's changed-file set; Architect Review should decide whether that baseline warrants follow-up.

### Architectural Concerns

None identified within C065 scope.

### Attempt 2 Completion Report

#### Worktree and Synchronization Evidence

- Launcher-resolved canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Dedicated parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-065`, branch `task/ARCH-021-COMMERCE-065`.
- Dedicated implementation task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-065`, branch `task/ARCH-021-COMMERCE-065`.
- Attempt 2 used these launcher-resolved task worktrees only; no shared/default checkout or another task's worktree was used.
- Start-of-attempt synchronization for both repositories: task-branch fast-forward was `not-needed`; `origin/main` was `already-current` in each task branch. Both worktrees were clean before implementation edits.
- Implementation submodules were synchronized and recursively initialized before claim. Recursive status was clean at the recorded database submodule commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

#### Changes and VCS Publication

- Attempt 2 implementation commit: `cb07cb7837c8bb2072f9363fc98b61ecd493eda6` on `task/ARCH-021-COMMERCE-065`; pushed to `origin`.
- Synchronous layout-commit invalidation now advances the derivation generation and marks freshness false when the Request identity changes, preventing an obsolete asynchronous completion from promoting its schema.
- Added deferred stale-completion regressions for both New Tool creation and persisted-DRAFT Save/Publish, asserting that obsolete schema is not promoted and persistence remains blocked.
- Parent report-content commit: `524c5de4f5c4e5c013ae1b9b044ed9bcda19be1c` on the parent `task/ARCH-021-COMMERCE-065` branch; pushed to `origin`.
- No parent database submodule gitlink was staged or changed for C065 task reporting.

#### Attempt 2 Validation

- Focused Vitest: 4 files, 49 tests passed (`shopify-admin-tools-ui`, `tool-authoring-screen`, `tool-authoring-session`, `admin-explorer`).
- Targeted ESLint passed for all 8 changed source/test files.
- Changed-file TypeScript/editor diagnostics: no errors in all 8 changed files.
- `git diff --check` passed.
- The package-wide typecheck limitation recorded for Attempt 1 remains unrelated to changed files: 28 diagnostics across 17 other package files. It was not treated as a C065 blocker, consistent with the Architect Review.

### Attempt 2 Status

Ready for Architect Review. The Attempt 2 implementation and deferred regressions are published on the task branch; task metadata is set to `review`, with `executor` and `claimed_at` cleared. No follow-on task was started.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 satisfies the Attempt 1 correction contract and is accepted.

The stale asynchronous derivation window is closed at the Response authoring boundary. `shopify-admin-response-editor.tsx` now invalidates the active derivation generation and marks freshness false in a layout-commit effect whenever the Admin result identity changes (`apiVersion`, `schemaHash`, `document`, `operationName` or `resultPath`). An in-flight completion must still match both the submitted generation and the latest committed identity before it may promote a derived schema or mark the result contract fresh.

The deferred regressions exercise both lifecycle consumers. New Tool authoring starts derivation A, changes the Admin Request identity before A resolves, then proves A cannot install its obsolete schema or re-enable Create. Persisted-DRAFT authoring proves the same stale completion cannot install the obsolete schema, re-enable Save Draft or Publish, or invoke either persistence action.

The Attempt 2 Completion Report also supplies the required launcher-resolved workspace root, dedicated parent/implementation worktree paths and branches, start-of-attempt synchronization evidence, recursive submodule state, implementation/report commit and push evidence, and explicit confirmation that the parent database gitlink was not staged for task reporting.

### Reviewed Files

- `src/studio/tools/shopify-admin-response-editor.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/shopify-admin-tools-ui.test.tsx`
- `docs/decisions/commerce/ARCH-021/COMMERCE-065-split-shopify-request-response-authoring.md`

### Validation Reviewed

- Submitted Attempt 2 focused Vitest packet: 49/49 tests across four suites passed.
- Submitted targeted ESLint: passed for the eight changed source/test files.
- Submitted changed-file TypeScript/editor diagnostics: no errors in the eight changed files.
- Submitted `git diff --check`: passed.
- The package-wide typecheck remains red on 28 diagnostics across 17 unrelated files and is not treated as a C065 regression.
- Source/test inspection confirms the deferred stale-completion tests cover both New Tool Create and persisted-DRAFT Save/Publish gates.

### Architecture Conformance

Conformant. Shopify Admin Request remains the invocation-authoring surface; Response owns `resultPath` and the COMMERCE-062 compiler-derived read-only result contract. Invalid path text remains local/actionable, derivation does not persist automatically, navigation stays ungated, and obsolete asynchronous results cannot become authoritative for a newer Request identity.

### Follow-up

COMMERCE-065 is Complete. COMMERCE-066 and COMMERCE-067 are already Complete, so all dependencies of COMMERCE-068 are now satisfied and COMMERCE-068 is promoted to Ready. COMMERCE-069 remains independently Ready.
