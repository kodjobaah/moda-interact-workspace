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
status: in_progress
priority: 75
executor: copilot
claimed_at: 2026-09-27T17:58:58Z
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

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 establishes the intended Request/Response ownership split: Shopify Admin Request owns invocation authoring, Response owns `resultPath` plus the compiler-derived read-only result contract, invalid path text is retained, and both New Tool and persisted-DRAFT flows use the COMMERCE-062 derivation boundary without an automatic durable write.

Two corrections are required before C065 can be accepted:

1. `shopify-admin-response-editor.tsx` can promote an obsolete in-flight derivation after the Request identity has changed. The completion guard compares against refs whose identity/generation invalidation is updated from a passive `useEffect`. A render for a changed `document`, `operationName`, API/schema identity, or `resultPath` can therefore occur before that effect updates the refs; if the older derivation resolves in that window, it can still call `onDerived(...)` and `onFreshChange(true)`. This violates R4 because an earlier query/result-path result may become fresh for the newer candidate.
2. The Completion Report does not contain the mandatory task-worktree/start-of-attempt VCS evidence required by the workspace execution protocol. Passing tests and a pushed task branch do not substitute for evidence that Attempt 1 ran from the launcher-resolved dedicated parent and implementation worktrees synchronized from their canonical bases.

The repository-wide TypeScript failure reported by the implementation is not itself a C065 rejection reason: the submitted evidence records 28 diagnostics in 17 files outside the C065 changed-file set and no changed-file diagnostics.

### Reviewed Files

- `src/studio/tools/shopify-admin-response-editor.tsx`
- `src/studio/tools/shopify-admin-editor.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `src/studio/tools/authoring-session.ts`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`
- `tests/admin-explorer.test.tsx`
- `docs/decisions/commerce/ARCH-021/COMMERCE-065-split-shopify-request-response-authoring.md`

### Validation Reviewed

- Submitted focused Vitest result: 47 tests across 4 files passed.
- Submitted targeted ESLint result: passed for the changed source/test files.
- Submitted changed-file diagnostics: no errors in the 8 changed files.
- Submitted `git diff --check`: passed.
- Submitted package-wide `npm run typecheck`: 28 diagnostics in 17 other package files; none reported in C065 changed files.
- Source/test inspection found the unresolved asynchronous stale-derivation completion window described above, which is not covered by the submitted stale-derivation regressions.

### Architecture Conformance

The Request/Response separation, COMMERCE-062 derivation ownership, local-only derivation lifecycle, invalid-path retention and ungated navigation conform to the task architecture in principle. Attempt 1 is not acceptable yet because the asynchronous completion race can violate R4's freshness boundary and the Completion Report lacks the required physical-isolation/start-of-attempt evidence.

### Follow-up

Attempt 2 must satisfy all of the following and then return this same task to Architect Review:

- [ ] Make the latest Admin derivation identity synchronously observable to an in-flight completion handler; do not rely on a passive effect to invalidate an obsolete request after a Request-identity-changing render.
- [ ] Add a deferred/asynchronous regression that starts derivation A, changes `document`, `operationName`, API/schema identity or `resultPath` before A resolves, then resolves A and proves the obsolete schema is not promoted and derivation freshness remains false.
- [ ] Prove the stale completion cannot re-enable New Tool Create or persisted-DRAFT Save/Publish. This may be demonstrated through focused consumer regressions or through shared-component coverage plus explicit consumer gate coverage, but both authoring lifecycles must remain protected.
- [ ] Update the Completion Report with launcher-resolved canonical workspace root, dedicated parent and implementation worktree paths/branches, confirmation that no shared/default or another task worktree was used, and start-of-attempt synchronization evidence for both parent and implementation repositories.
- [ ] Record implementation and parent branch/commit/push evidence, including confirmation that the parent submodule gitlink was not staged as part of C065 task reporting.
- [ ] Rerun the C065-required focused validation from the canonical C065 implementation worktree after the source correction and record the results. Do not require unrelated repository-wide baseline diagnostics to be fixed unless they newly affect C065 changed files.
- [ ] Set the task back to `review` with the Attempt 2 Completion Report complete, then STOP. Do not start COMMERCE-068 or COMMERCE-069.

No new task is required for these corrections; they remain within the original C065 scope. The next authorized claim increments `attempt` from 1 to 2.
