---
id: ARCH-021-COMMERCE-093
architecture_id: ARCH-021
title: Fix code-response validation route imports
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-021-COMMERCE-086
  - ARCH-021-COMMERCE-094
created: 2026-09-29
updated: 2026-09-29
---

# Fix code-response validation route imports

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Correct the three over-deep repository-local imports in the Studio code-response validation route and prove the corrected imports resolve within Commerce, without changing preview-validation behavior or absorbing C086 manual-packaging work.

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

C086 is blocked on this task because its R11/R12 production-start HTTP smoke cannot run until the Commerce production build succeeds. Architect review has assigned the unrelated TypeScript diagnostics discovered after correcting these imports to the separate task ARCH-021-COMMERCE-094. C093 owns only the route import correction and bounded import-resolution evidence.

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

### R4 — production build ownership

Production build validation and unrelated TypeScript diagnostics are owned by ARCH-021-COMMERCE-094. C093 must record its observed build result as evidence that the corrected route imports are no longer the blocker, but C093 acceptance does not require the repository build to pass.
- [ ] Record the production-build result and confirm the corrected route imports are no longer unresolved; do not fix unrelated TypeScript diagnostics in C093.

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
- [x] Run the normal repository `npm run build` and record that the route import failure is gone; unrelated TypeScript diagnostics are transferred to C094.
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
- [x] The build no longer fails to resolve these three route imports; remaining production type-check/build gate is owned by C094.

## Validation

- [x] focused route/import-resolution regression or equivalent bounded route-compilation check
- [x] targeted ESLint for changed files
- [x] changed-file TypeScript diagnostics
- [x] `git diff --check`
- [x] `npm run build` confirms the route imports resolve; unrelated TypeScript errors are transferred to C094 (see Completion Report).

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP.
After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. For Attempt 2, make no source changes: confirm the Attempt 1 route fix and import-resolution evidence, record the build's unrelated C094-owned TypeScript blocker, and submit for review.

Do not begin C086 Attempt 2. `moda_architect` must first accept C093 and explicitly return C086 to Ready.

## Implementation Notes

Prefer the minimum three-line import-depth correction.

Do not use this task as an opportunity to convert the repository to path aliases or reorganize preview routes.

The production build is used only as integration evidence that the route-import blocker is gone. Repository-wide production-build success is owned by C094 after the build advanced to unrelated TypeScript diagnostics.

## Completion Report

### Status

Attempt 1 corrected the three imports and proved they resolve within Commerce.
The production build now fails only on unrelated TypeScript diagnostics, which
the Architect assigned to ARCH-021-COMMERCE-094. The Architect returned C093
to `ready` for Attempt 2, report-only: preserve the Attempt 1 implementation,
confirm route resolution and the build blocker, then submit for review without
source changes.

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

ARCH-021-COMMERCE-094 owns the 23 unrelated TypeScript diagnostics across the
12 files listed above and the production build gate. C093 must be accepted
before C094's dependency gate passes. C086 remains blocked until both C093 and
C094 are complete and its production build/start/manual HTTP smoke is rerun.

### Architectural Concerns

The build now advances past the targeted route-import failure but is blocked by
unrelated repository type errors. Keep C093 scoped to the three route imports;
do not absorb those additional fixes here. The Architect explicitly directed
the report-only C093 Attempt 2 and separate C094 work.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is accepted.

C093's bounded objective is satisfied:

- the three code-response validation route imports now use the correct repository-local depth;
- all three specifiers resolve to existing Commerce-local modules;
- the route diff changes only those three import paths;
- POST/authentication/input-schema/service/signal/cache/error/runtime/dynamic behavior is unchanged;
- targeted module resolution, ESLint, changed-file TypeScript diagnostics and `git diff --check` pass; and
- the normal Commerce build advances past the original route-import failure.

The subsequent build failure is a separate repository-wide TypeScript gate: 23 diagnostics across 12 files outside C093's permitted source scope. C093 correctly did not modify those files.

Architecturally, the production-build-success criterion is therefore transferred to COMMERCE-094. C093 requires only proof that its import-resolution blocker is removed and that the build proceeds beyond that blocker. The stale duplicate "build must succeed" Work Item/Acceptance/Validation entries have been removed by this acceptance reconciliation.

No report-only Attempt 2 is required. The Attempt 1 Completion Report already contains the exact source diff, route-resolution evidence, build progression evidence, changed-file diagnostics and unrelated blocker list. Reclaiming the same task solely to restate that evidence would add no implementation or validation information.

The user reports that COMMERCE-094 has been materialised on its own task branch at parent commit `58f65e5b`, depends on C093, and owns the listed TypeScript diagnostics plus the production-build gate. That C094 task file is not physically present in this submitted C093 snapshot, so this acceptance does not fabricate or overwrite a second C094 definition.

### Reviewed Files

- `app/api/studio/code-response/validate/route.ts`
- `lib/preview/http.ts`
- `lib/preview/runtime.ts`
- `src/commerce/preview/types.ts`
- `docs/decisions/commerce/ARCH-021/COMMERCE-093-fix-code-response-route-imports.md`
- `docs/decisions/commerce/ARCH-021/COMMERCE-086-add-result-template-guide-link.md`
- C093 Completion Report — Attempt 1

### Validation Reviewed

Submitted evidence:

- focused TypeScript module resolution: passed;
- corrected targets resolve inside `moda-interact-commerce`;
- targeted ESLint: passed;
- `git diff --check`: passed;
- no changed-file TypeScript diagnostic for the route;
- normal `npm run build` proceeds beyond route import resolution and then fails at TypeScript checking with 23 diagnostics across 12 out-of-scope files.

Direct snapshot inspection independently confirms the corrected five-level import paths resolve to:

```text
lib/preview/http.ts
lib/preview/runtime.ts
src/commerce/preview/types.ts
```

inside the Commerce repository.

### Architecture Conformance

Conforms.

C093 makes only the narrow import-resolution correction and leaves the newly exposed repository-wide TypeScript/build gate to C094.

### Follow-up

C093 is Complete / Accepted — Attempt 1.

C094 is now dependency-eligible and should be promoted from Pending to Ready on its own canonical task branch.

C086 remains Blocked and now depends on both C093 and C094. After C094 is architect-accepted Complete, return C086 through the authorised Changes Requested path to Ready with `attempt: 1` preserved; the next claim becomes C086 Attempt 2 for the clean build + production-start manual HTTP smoke.
