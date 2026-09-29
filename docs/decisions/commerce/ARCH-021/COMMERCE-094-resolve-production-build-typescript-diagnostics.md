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
attempt: 0
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

- [ ] Run TypeScript diagnostics and reconcile the current errors with the 12-file baseline recorded by C093.
- [ ] Correct only the relevant type errors in the enumerated files, preserving runtime behavior.
- [ ] Add or adjust focused tests only when needed to substantiate changed behavior or type-safe fixtures.
- [ ] Run targeted ESLint for changed files.
- [ ] Run `npx tsc --noEmit --pretty false` and verify there are no remaining project diagnostics.
- [ ] Run `git diff --check`.
- [ ] Run the normal `npm run build` and require success.
- [ ] Complete the report with changed files, validations, and any remaining out-of-scope blocker.

## Dependencies

- ARCH-021-COMMERCE-093

## Enables

- ARCH-021-COMMERCE-086

## Acceptance Criteria

- [ ] The listed TypeScript diagnostics are resolved without suppressing type checking or adding blanket ignores.
- [ ] Runtime behavior remains unchanged except for necessary type-safe corrections.
- [ ] Changes remain limited to the listed files and directly required focused tests.
- [ ] Targeted lint passes for changed files.
- [ ] `npx tsc --noEmit --pretty false` passes with no diagnostics.
- [ ] `git diff --check` passes.
- [ ] Normal `npm run build` succeeds.
- [ ] No C086 Attempt 2 or production-start smoke is performed by this task.

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