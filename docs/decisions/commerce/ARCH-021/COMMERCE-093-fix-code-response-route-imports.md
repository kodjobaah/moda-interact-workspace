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
status: in_progress
priority: 10
executor: copilot
claimed_at: 2026-09-29T11:28:16Z
attempt: 1
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

- [x] Correct the three over-deep imports in the code-response validation route.
- [x] Add/execute a bounded import-resolution or route-compilation regression.
- [x] Verify route behavior contract remains unchanged.
- [x] Run targeted ESLint for changed files.
- [x] Run changed-file TypeScript diagnostics.
- [x] Run `git diff --check`.
- [ ] Run the normal repository `npm run build` successfully (attempted; blocked by unrelated project type errors).
- [x] Record build evidence and any unrelated blocker in the Completion Report.

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

- [x] All three route imports resolve to existing files inside the Commerce repository.
- [x] No route request/authorization/validation/service/error behavior changes.
- [x] No C086 manual-packaging/link source is modified.
- [x] Focused route/import validation passes.
- [x] Changed-file lint/TypeScript diagnostics are clean.
- [x] `git diff --check` passes.
- [ ] Normal `npm run build` succeeds.

## Validation

- [x] focused route/import-resolution regression or equivalent bounded route-compilation check
- [x] targeted ESLint for changed files
- [x] changed-file TypeScript diagnostics
- [x] `git diff --check`
- [ ] `npm run build` (blocked by unrelated project type errors; see Completion Report)

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP.

Do not begin C086 Attempt 2. `moda_architect` must first accept C093 and explicitly return C086 to Ready.

## Implementation Notes

Prefer the minimum three-line import-depth correction.

Do not use this task as an opportunity to convert the repository to path aliases or reorganize preview routes.

The production build is required because this defect was discovered specifically at the Next compilation stage and a source-only check is insufficient proof that the blocker is removed.

## Completion Report

### Status

Route imports are corrected, but this task remains `in_progress` and blocked
from review: the required production build fails at TypeScript validation with
23 diagnostics in 12 unrelated files. No diagnostic names the corrected route.
Per R4 and the task scope, those files were not modified; returning the blocker
to `moda_architect`.

### Files Changed

`app/api/studio/code-response/validate/route.ts` (only the three import paths).

### Work Completed

Changed the three over-deep imports from six parent traversals to five. No route
behavior, request schema, authorization, service call, response header, runtime
or dynamic setting changed. No C086 source or test file was touched.

### Validation Results

- Focused TypeScript module-resolution check passed. The corrected specifiers
  resolve to `lib/preview/http.ts`, `lib/preview/runtime.ts`, and
  `src/commerce/preview/types.ts`, all inside the Commerce repository.
- Targeted ESLint for the changed route passed.
- `git diff --check` passed; the diff contains only the three import-path edits.
- `npx tsc --noEmit --pretty false` reports 23 project-wide diagnostics across
  12 files. No diagnostic references
  `app/api/studio/code-response/validate/route.ts`.
- Required `npm run build` failed at `Failed to type check.` after the route
  import-resolution errors were removed. Diagnostics are in:
  `scripts/validate-shopify-admin-local.ts`,
  `src/studio/discovery/admin-query-builder.ts`,
  `src/studio/tools/authoring/result-template-tab.tsx`,
  `tests/admin-query-execution.test.ts`,
  `tests/agent-configuration-effective.test.ts`,
  `tests/agent-configuration-prompts-postgres.test.ts`,
  `tests/c20-integration-fixture.test.ts`,
  `tests/local-external-mcp-diagnostic.test.ts`,
  `tests/result-template-tab.test.tsx`,
  `tests/selected-shop-context.test.ts`,
  `tests/shopify-admin-live-test.test.ts`, and
  `tests/tool-result-contract.test.ts`.
  These files are outside C093's permitted implementation scope. R4 is not
  met and no production-start test was attempted.

### Deviations

The production build acceptance criterion remains blocked by TypeScript errors
outside the scoped route. The route correction and local module-resolution
check pass.

### Assumptions

None.

### Unresolved Issues

`npm run build` cannot pass until the reported TypeScript diagnostics are
resolved or otherwise dispositioned by `moda_architect`. C093 prohibits fixing
those unrelated defects; architect direction is required before this task can
meet R4 and enable C086.

### Architectural Concerns

The build now advances past the targeted route-import failure but is blocked by
unrelated repository type errors. Keep C093 scoped to the three route imports;
do not absorb those additional fixes here.

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
