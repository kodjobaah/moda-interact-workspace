---
id: ARCH-021-COMMERCE-093
architecture_id: ARCH-021
title: Fix code-response validation route imports and restore Commerce production build
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-021-COMMERCE-086
created: 2026-09-29
updated: 2026-09-29
---

# Fix code-response validation route imports and restore Commerce production build

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Correct the three over-deep repository-local imports in the Studio code-response validation route and prove the normal Commerce production build succeeds, without changing preview-validation behavior or absorbing C086 manual-packaging work.

## Context

C086's clean production build reaches Next compilation after successfully completing:

```text
manual packaging/smoke
code-runtime packaging/smoke
Prisma generation
```

and then fails in this untouched route:

```text
app/api/studio/code-response/validate/route.ts
```

The route currently imports:

```ts
../../../../../../lib/preview/http
../../../../../../lib/preview/runtime
../../../../../../src/commerce/preview/types
```

From:

```text
app/api/studio/code-response/validate/
```

six parent traversals resolve one directory above the Commerce repository. The repository-local `lib/` and `src/` roots are five parent traversals away.

The referenced modules already exist. This task is therefore a narrow import-resolution/build correction.

C086 is blocked on this task because its R11/R12 production-start HTTP smoke cannot run until the Commerce production build succeeds.

## Scope

Primary implementation file:

```text
app/api/studio/code-response/validate/route.ts
```

Allowed focused regression area:

```text
tests/                         # only a small route/import regression if useful
```

Expected repo-local targets remain:

```text
lib/preview/http
lib/preview/runtime
src/commerce/preview/types
```

## Out of Scope

- C086 manual source, packaging scripts, guide link or manual tests.
- Preview-service behavior changes.
- Authentication/authorization changes.
- Request/response schema changes.
- QuickJS/code-runtime semantics.
- Redis preview-state changes.
- Database schema/migrations.
- Prisma model changes.
- Result Template behavior.
- Refactoring unrelated route imports.
- Introducing path aliases or a broad import-style migration.
- Fixing any new unrelated build defect discovered after this one; return such a blocker to `moda_architect`.

## Requirements

### R1 — correct only the three broken imports

Make the minimum route-source correction so the route resolves the existing repository-local modules.

The mechanically expected relative imports from:

```text
app/api/studio/code-response/validate/route.ts
```

are equivalent to:

```ts
../../../../../lib/preview/http
../../../../../lib/preview/runtime
../../../../../src/commerce/preview/types
```

A mechanically equivalent repo-local import is acceptable only if it does not introduce new configuration or broader refactoring.

### R2 — route behavior is unchanged

Preserve exactly the existing behavior:

```text
POST only
previewPrincipal authorization
parseJson
strict input schema:
  source <= 16 KiB
  runtimeVersion <= 128 chars
  contentHash = 64 lowercase hex chars
getExternalPreviewService()
UNAVAILABLE when service is absent
service.validateCode(...)
request.signal propagation
Cache-Control: no-store
previewErrorResponse(error)
runtime = nodejs
dynamic = force-dynamic
```

Do not alter request/response semantics merely to make the build pass.

### R3 — prove repository-local resolution

Add a focused regression or bounded validation proving all three corrected import targets resolve inside the Commerce repository and the route module can be compiled/resolved by the repository toolchain.

Do not use a brittle test that merely duplicates the exact relative string without checking actual resolution.

### R4 — normal Commerce production build succeeds

From the prepared C093 Commerce worktree, run the repository-declared normal production build:

```text
npm run build
```

Record the complete outcome.

Acceptance requires the build to pass.

If the corrected imports compile but the build fails on a different pre-existing/unrelated defect:

```text
do not fix the new defect in C093
record the exact blocker
return C093 blocked to moda_architect
```

### R5 — no C086 source changes

Do not modify:

```text
manuals/result-template-guide.html
scripts/package-manuals.mjs
scripts/manuals-packaged-smoke.mjs
Result Template guide-link UI
C086 manual packaging tests
```

C086 will rerun its own production manual/start smoke after C093 is accepted Complete.

## Work Items

- [ ] Correct the three over-deep imports in the code-response validation route.
- [ ] Add/execute a bounded import-resolution or route-compilation regression.
- [ ] Verify route behavior contract remains unchanged.
- [ ] Run targeted ESLint for changed files.
- [ ] Run changed-file TypeScript diagnostics.
- [ ] Run `git diff --check`.
- [ ] Run the normal repository `npm run build`.
- [ ] Record build evidence and any unrelated blocker in the Completion Report.

## Interfaces / Contracts

Consumes existing Commerce-local modules:

```text
lib/preview/http
lib/preview/runtime
src/commerce/preview/types
```

Changes no runtime contract.

Enables C086 to resume its production build/start/manual HTTP smoke.

## Dependencies

None.

## Enables

- ARCH-021-COMMERCE-086

## Acceptance Criteria

- [ ] All three route imports resolve to existing files inside the Commerce repository.
- [ ] No route request/authorization/validation/service/error behavior changes.
- [ ] No C086 manual-packaging/link source is modified.
- [ ] Focused route/import validation passes.
- [ ] Changed-file lint/TypeScript diagnostics are clean.
- [ ] `git diff --check` passes.
- [ ] Normal `npm run build` succeeds.

## Validation

- [ ] focused route/import-resolution regression or equivalent bounded route-compilation check
- [ ] targeted ESLint for changed files
- [ ] changed-file TypeScript diagnostics
- [ ] `git diff --check`
- [ ] `npm run build`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP.

Do not begin C086 Attempt 2. `moda_architect` must first accept C093 and explicitly return C086 to Ready.

## Implementation Notes

Prefer the minimum three-line import-depth correction.

Do not use this task as an opportunity to convert the repository to path aliases or reorganize preview routes.

The production build is required because this defect was discovered specifically at the Next compilation stage and a source-only check is insufficient proof that the blocker is removed.

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

Pending

### Follow-up

None
