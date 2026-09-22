---
id: ARCH-020-COMMERCE-025
architecture_id: ARCH-020
title: Implement bounded response filtering and projection
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor:
claimed_at:
attempt: 2
depends_on:
  - ARCH-020-SHARED-002
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
  - ARCH-020-COMMERCE-030
  - ARCH-020-COMMERCE-031
created: 2026-09-21
updated: 2026-09-22
---

# Implement bounded response filtering and projection

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/external-response/** and focused pure tests only. Implement C21 section2.1 createResponseProcessor; no network, application factories, persistence, UI or arbitrary scripts.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/external-response/** and focused pure tests only. Implement C21 section2.1 createResponseProcessor; no network, application factories, persistence, UI or arbitrary scripts.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [x] Implement deterministic OBJECT/LIST projection, AND filtering, stable sort, bounded limit and own-property paths exactly as section2.1.
- [x] Use supplied signal/clock/deadline, enforce row/field/value limits and return typed failures without copying raw data into output.
- [x] Expose reusable pure port for production executor and preview; document input/result fixtures used by021/023/024. Do not mutate caller objects or keep shared request state.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-SHARED-002

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024
- ARCH-020-COMMERCE-030
- ARCH-020-COMMERCE-031

## Acceptance Criteria

- [x] X10: golden samples prove output field removal/rename, type-strict comparisons, null/missing behavior, Unicode order and stable ties.
- [x] 1001 rows fail rather than truncate, abort/deadline checked, unsafe paths rejected; two concurrent invocations cannot contaminate results.
- [x] No networking, secrets or eval dependency; old response rendering unchanged because processor is a separate stage.

## Validation

Provide `test:arch020-response-processing` in the owning repository and document its exact scope.
Run focused changed-boundary tests, then existing repository typecheck/build
and lint where defined. Inspect package scripts first; do not invent a claim that
an absent script passed. Use C21 controlled transports and isolated stores.
Follow current developer-owned live/container validation policy; clearly separate
actual agent results from required unrun developer checks. No arbitrary screenshot
quota or repeated full-suite runs without new changes/failures.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-commerce/src/commerce/external-response/index.ts`
- `moda-interact-commerce/tests/response-processing.test.ts`
- `moda-interact-commerce/package.json`
- `moda-interact-commerce/package-lock.json`

### Work Completed

- Implemented server-only `createResponseProcessor({now})` for C21 visual OBJECT/LIST processing.
- Added own-property-safe scalar projection, strict filters, code-point sorting with stable ties, null/missing handling, bounded rows/fields/filters/limits, and typed deadline/cancellation failures.
- Corrected DESC sorting so valid values are ordered by direction while null/missing values remain last in either direction, preserving stable order among null/missing rows.
- Added `import 'server-only';` as the module boundary and added the exact DESC null/missing regression.
- Added focused tests for projection, strict filters, null/missing behavior, Unicode ordering, stable ties, unsafe paths, scalar validation, row bounds, cancellation and deadlines.
- Aligned the Commerce dependency with the accepted `@modainteract/moda-interact-shared@0.14.2` contract.

### Validation Results

Agent-executed validation:

- `npm run test:arch020-response-processing`: passed, 6/6 tests, including the exact DESC null/missing regression.
- `npm run lint`: failed on the pre-existing `react-hooks/set-state-in-effect` error in `src/studio/connections/connections-ui.tsx`; six warnings were also reported, with no diagnostics in changed files.
- `npm run typecheck`: failed with 183 repository baseline errors across unrelated auth, Prisma, integration, execution and code-processor files; no diagnostics were reported for `src/commerce/external-response` or `tests/response-processing.test.ts`.
- `npm run build`: production bundle compilation passed, then the repository TypeScript phase failed on the same unrelated baseline diagnostics; the overlapping retry exited on the generated Next build lock and is not treated as a code result.
- `git diff --check`: passed.

Implementation repository commits: `44f9138` (`feat(ARCH-020-COMMERCE-025): add bounded response processor`) and `8b281cf` (`fix(ARCH-020-COMMERCE-025): correct response sort null ordering`), pushed to `origin/task/ARCH-020-COMMERCE-025`.

### Deviations

The canonical implementation worktree was absent and was recreated at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-025`; its recorded `database` submodule was initialized at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`. No unrelated source or parent gitlink was changed.

### Assumptions

C21 read-only visual processing only; the separate JavaScript processor remains out of scope. Missing and non-scalar filter fields do not match, including `NE`; `EQ`/`NE` use identical scalar types as specified by C21.

### Unresolved Issues

Repository-wide typecheck, lint and build TypeScript validation remain blocked by established unrelated repository errors. Focused behavior tests and diff validation pass; changed files have no reported diagnostics.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-025`
  parent branch: `task/ARCH-020-COMMERCE-025`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-025`
  implementation branch: `task/ARCH-020-COMMERCE-025`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  `git submodule sync --recursive`: passed
  `git submodule update --init --recursive`: passed
  recorded submodule commits: `database@7f920e8f2ad523e78e566f4dbdfbb1f68118b082`

Expected mirrored branch: `task/ARCH-020-COMMERCE-025`. Implementation commits `44f9138` and `8b281cf` are pushed. Parent task metadata is being returned on the same mirrored branch for architect review; no merge, self-acceptance, or main update performed.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

Reviewed the exact submitted snapshot reporting implementation `44f9138` and
parent report `4bd1e71`. The bounded OBJECT/LIST processor is materially aligned
with C21, including own-property paths, strict filtering, code-point ordering,
row bounds, projection and typed cancellation/deadline failures. Two task-owned
contract defects remain and must be corrected in this same task.

**A1-R1 — DESC sorting must keep missing/null values last.** The current comparator
first assigns missing/null a positive ordering value and then multiplies that value
by the DESC direction (`-1`). That moves missing/null rows to the front for DESC,
contradicting C21 section 2.1: “missing/null last in either direction”. Correct the
comparator so direction is applied only when both compared values are non-null
valid sort values. Missing/null ordering is direction-independent and always after
non-null values. When both values are missing/null, preserve original row order.

Add this exact focused regression to `tests/response-processing.test.ts`:

```ts
const source = [
  {id: 'a', sortKey: 'a'},
  {id: 'null-1', sortKey: null},
  {id: 'missing'},
  {id: 'b', sortKey: 'b'},
  {id: 'null-2', sortKey: null},
];
const processing = list({
  fields: {id: {path: 'id'}},
  sort: {path: 'sortKey', direction: 'DESC'},
});
expect(run(source, processing)).toEqual({
  ok: true,
  values: {items: [
    {id: 'b'},
    {id: 'a'},
    {id: 'null-1'},
    {id: 'missing'},
    {id: 'null-2'},
  ]},
});
```

The existing ASC behavior must remain unchanged. Do not implement nulls-first or a
configurable null-order option.

**A1-R2 — enforce the server-only module boundary.** C21 section 2.1 explicitly
requires server-only `createResponseProcessor`. Add `import 'server-only';` as the
first import in `src/commerce/external-response/index.ts`, matching the existing
Commerce server-side runtime convention. Do not add a client wrapper or duplicate
processor implementation.

**A1-R3 — complete the task-defined validation after A1-R1/R2.** Run exactly the
repository scripts that already exist; do not invent replacement commands:

```bash
npm run test:arch020-response-processing
npm run lint
npm run typecheck
npm run build
git diff --check
```

If repository-wide `typecheck` or `build` still fails only on an established
unrelated baseline, record the exact diagnostics/baseline reference and confirm
there are no diagnostics in the task-owned files. Do not fix unrelated baseline
code inside COMMERCE-025. A missing/failed build must not be silently reported as
passed.

The submitted snapshot also still contains `executor: copilot` and a non-null
`claimed_at` despite the handoff saying claims were cleared. This architect overlay
clears those fields while returning the task to Ready; no separate implementation
change is required for that coordination mismatch.

### Reviewed Files

- `moda-interact-commerce/src/commerce/external-response/index.ts`
- `moda-interact-commerce/tests/response-processing.test.ts`
- `moda-interact-commerce/package.json`
- `moda-interact-commerce/package-lock.json`
- `docs/architecture/ARCH-020-external-api-tools.md` (C21 section 2.1)
- this task Completion Report

### Validation Reviewed

Submitted evidence:

- `npm run test:arch020-response-processing`: 5/5 passed.
- `npm run lint`: passed with two reported pre-existing warnings.
- `npm run typecheck`: failed on reported unrelated existing repository errors;
  task-owned files reported clean.
- `git diff --check`: passed.
- Production `npm run build` evidence was not supplied.

Independent source reproduction of A1-R1 confirms the current DESC comparator
orders null/missing rows before non-null rows.

### Architecture Conformance

Partially conformant. The implementation respects the task ownership boundary and
does not add networking, persistence, UI or arbitrary script execution. Acceptance
is blocked only by the direction-dependent null/missing sort defect, missing
server-only marker and completion of the task-defined validation. No Shared schema
or C21 architecture change is requested.

### Follow-up

Return the same task through `/moda-task ARCH-020-COMMERCE-025`. Preserve
`attempt: 1`; the next valid claim increments it once to Attempt 2. Implement only
A1-R1/A1-R2, add the exact regression, run A1-R3 validation, update the Completion
Report, set status to Review, clear claim metadata and STOP. Do not start
COMMERCE-012, COMMERCE-024, COMMERCE-030 or COMMERCE-031.
