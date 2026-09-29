---
id: ARCH-021-COMMERCE-094
architecture_id: ARCH-021
title: Resolve Commerce production build TypeScript diagnostics
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 9
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-093
enables:
  - ARCH-021-COMMERCE-086
created: 2026-09-29
updated: 2026-09-29
---

# Resolve Commerce production build TypeScript diagnostics

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Resolve the bounded set of TypeScript diagnostics preventing the Commerce production build from completing, then prove the normal production build passes. Do not broaden this into unrelated cleanup or change runtime behavior beyond what is necessary to make the reported code type-safe.

## Context

ARCH-021-COMMERCE-093 corrects three over-deep imports in:

```text
app/api/studio/code-response/validate/route.ts
```

After those imports resolve, the normal `npm run build` advances to Next.js type validation and fails with 23 TypeScript diagnostics across 12 files. The diagnostic files observed on 2026-09-29 are:

```text
scripts/validate-shopify-admin-local.ts
src/studio/discovery/admin-query-builder.ts
src/studio/tools/authoring/result-template-tab.tsx
tests/admin-query-execution.test.ts
tests/agent-configuration-effective.test.ts
tests/agent-configuration-prompts-postgres.test.ts
tests/c20-integration-fixture.test.ts
tests/local-external-mcp-diagnostic.test.ts
tests/result-template-tab.test.tsx
tests/selected-shop-context.test.ts
tests/shopify-admin-live-test.test.ts
tests/tool-result-contract.test.ts
```

The current diagnostic output is recorded in the preceding C093 Attempt 1 Completion Report. These defects are outside C093's route-import scope. This task is the production-build prerequisite for C086's clean build and static-manual HTTP smoke.

## Scope

Implementation repository:

```text
moda-interact-commerce/
```

Allowed implementation files are limited to the 12 diagnostic-bearing files listed above, plus focused tests only if a reported source diagnostic requires a test adjustment. Do not modify C086 packaging, manual source, or guide-link files except where an existing diagnostic in the listed Result Template files requires a strictly minimal type correction.

## Out of Scope

- Changing the three route imports fixed by C093.
- C086 manual packaging, manual content, build lifecycle integration, or guide-link behavior, except minimal type corrections required to resolve diagnostics in the listed files.
- Unrelated TypeScript cleanup outside the enumerated diagnostic sites.
- Broad changes to TypeScript compiler options, lint rules, or strictness.
- Adding `@ts-ignore`, `@ts-nocheck`, unsafe casts, blanket suppressions, or disabling type checking to make the build pass.
- Runtime behavior changes not required to make the reported code type-safe.
- Database schema, generated Prisma model, dependency, or lockfile changes.

## Requirements

### R1 — resolve the observed diagnostic set

Use the current branch's actual compiler output as authoritative because diagnostics may shift after C093 is accepted. Resolve only the diagnostics in the 12 listed files that prevent the required build from passing. Do not assume the original count remains exactly 23 after code changes.

### R2 — preserve runtime behavior

Make type-correct implementation changes that preserve existing runtime contracts. Prefer correct narrowing, annotations, and compatible test fixtures over weakening types or suppressing diagnostics.

### R3 — normal production build passes

Run the repository-declared command from a clean generated state as appropriate:

```text
npm run build
```

Acceptance requires exit code zero. Record the full command outcome. If an unrelated build failure outside this task's bounded diagnostic set appears, do not fix it here; report the exact blocker to `moda_architect`.

### R4 — unblock C086 without doing C086

Do not start C086 Attempt 2. `moda_architect` must accept C093 and C094 and explicitly return C086 to Ready before its next authorized claim. C086 then owns its own clean-build and production-start HTTP smoke.

## Work Items

- [x] Run TypeScript diagnostics and reconcile the current errors with the 12-file baseline recorded by C093.
- [x] Correct the locally resolvable type errors in the enumerated files, preserving runtime behavior.
- [x] Add or adjust focused tests only when needed to substantiate changed behavior or type-safe fixtures.
- [x] Run targeted ESLint for changed files.
- [ ] Run `npx tsc --noEmit --pretty false` and verify there are no remaining project diagnostics.
- [x] Run `git diff --check`.
- [ ] Run the normal `npm run build` and require success.
- [x] Complete the report with changed files, validations, and any remaining out-of-scope blocker.

## Dependencies

- ARCH-021-COMMERCE-093

## Enables

- ARCH-021-COMMERCE-086

## Acceptance Criteria

- [ ] The listed TypeScript diagnostics are resolved without suppressing type checking or adding blanket ignores.
- [ ] Runtime behavior remains unchanged except for necessary type-safe corrections.
- [ ] Changes remain limited to the listed files and directly required focused tests.
- [x] Targeted lint passes for changed files.
- [ ] `npx tsc --noEmit --pretty false` passes with no diagnostics.
- [x] `git diff --check` passes.
- [ ] Normal `npm run build` succeeds.
- [x] No C086 Attempt 2 or production-start smoke is performed by this task.

## Validation

- [ ] Inspect actual TypeScript diagnostics after C093 is accepted.
- [ ] Targeted ESLint for changed files.
- [ ] `npx tsc --noEmit --pretty false`.
- [ ] `git diff --check`.
- [ ] `npm run build`.

## Stop Condition

After all Work Items, Acceptance Criteria, and Validation items pass, set this task to `review`, complete the Completion Report, and stop. Do not begin C086 Attempt 2.

## Completion Report

### Status

Blocked; not submitted for Architect Review because the required project typecheck and production build remain blocked by ARCH-021 legacy Prisma consumers outside C094's implementation-file boundary.

### Files Changed

Implementation files:

- `scripts/validate-shopify-admin-local.ts`
- `src/studio/discovery/admin-query-builder.ts`
- `src/studio/tools/authoring/result-template-tab.tsx`
- `tests/admin-query-execution.test.ts`
- `tests/agent-configuration-effective.test.ts`
- `tests/agent-configuration-prompts-postgres.test.ts`
- `tests/local-external-mcp-diagnostic.test.ts`
- `tests/result-template-tab.test.tsx`
- `tests/selected-shop-context.test.ts`
- `tests/shopify-admin-live-test.test.ts`
- `tests/tool-result-contract.test.ts`

### Work Completed

Corrected type narrowing in GraphQL AST construction and result-schema rendering; aligned fixture types with the Commerce result/template contracts; corrected nullable result assertions and prompt-result test narrowing; updated selected-shop tests to use the current server-action-backed API. No runtime contract was intentionally changed.

The current compiler baseline exposed an architecture-level blocker: the Prisma Client generated from the launcher-pinned `database` submodule commit `e9fb60221f1532205650154dfff2aadb6270b14c` does not expose `CommerceCapabilityRevision`, the release-capability `revision` relation / `capabilityRevisionId`, or capability `selectionBinding`. The affected production consumers are outside C094's allowed implementation files and belong to the ARCH-021 legacy-removal work in COMMERCE-092. No database schema, submodule pointer, compiler configuration, or out-of-scope source was changed.

Prepared execution evidence:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-094`, branch `task/ARCH-021-COMMERCE-094`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-094`, branch `task/ARCH-021-COMMERCE-094`
- Shared workspace and implementation checkouts were not switched or edited; no other task worktree was reused.
- The prepared launcher synchronized both task branches and initialized recursive submodules; the `database` submodule remained at `e9fb60221f1532205650154dfff2aadb6270b14c`.

### Validation Results

Passed:

- `npx eslint scripts/validate-shopify-admin-local.ts src/studio/discovery/admin-query-builder.ts src/studio/tools/authoring/result-template-tab.tsx tests/admin-query-execution.test.ts tests/agent-configuration-effective.test.ts tests/agent-configuration-prompts-postgres.test.ts tests/local-external-mcp-diagnostic.test.ts tests/result-template-tab.test.tsx tests/selected-shop-context.test.ts tests/shopify-admin-live-test.test.ts tests/tool-result-contract.test.ts`
- Focused Vitest suites: 48 tests passed across `tests/admin-query-execution.test.ts`, `tests/agent-configuration-effective.test.ts`, `tests/result-template-tab.test.tsx`, `tests/selected-shop-context.test.ts`, `tests/tool-result-contract.test.ts`, and `tests/shopify-admin-live-test.test.ts`.
- `git diff --check`
- `npm run prisma:generate` completed using the task-pinned database submodule.

Blocked:

- `npx tsc --noEmit --pretty false`: 122 errors in five files, all involving the missing ARCH-021-removed Prisma models/relations or cascading implicit types: `src/commerce/integration/backend.ts` (72), `src/commerce/integration/backend/c20-test-fixture.ts` (12), `src/commerce/integration/backend/publication-storage.ts` (18), `tests/c20-integration-fixture.test.ts` (16), and `tests/local-external-mcp-diagnostic.test.ts` (4).
- `npm run build`: failed at Next.js TypeScript validation with the same 122 errors; build did not complete.

### Deviations

Required project-wide typecheck and normal production build could not pass without editing out-of-scope legacy consumers or changing the database schema, both prohibited by this task. The task remains `blocked`, not `review`.

### Assumptions

The removed Prisma model/fields are intentionally absent under ARCH-021; C094 must not restore them or add compatibility suppressions. C094 should be resumed after the COMMERCE-092 legacy-consumer/fixture cleanup is accepted, or after the Architect explicitly re-scopes its dependency and remaining work.

### Unresolved Issues

`moda_architect` must coordinate COMMERCE-092 before C094 can satisfy the global typecheck/build criteria. The architecture agent recommended making C092 an explicit C094 prerequisite or otherwise re-scoping C094 around C092 completion. DATABASE-003 task metadata also reportedly has a completion/review/index-state inconsistency that should be reconciled before relying on it as accepted.

### Architectural Concerns

The production build's Prisma type errors show that the staged ARCH-021 legacy-removal work is not yet reconciled with this task's original C093-era diagnostic baseline. C086 Attempt 2 and its production-start HTTP smoke were not started.

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

Pending

### Follow-up

None
