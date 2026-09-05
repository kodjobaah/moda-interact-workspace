---
id: ARCH-003-ADMIN-009
architecture_id: ARCH-003
title: Repair KPI card JSX compile regression
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: superseded
priority: 16
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-003-ADMIN-008
enables: []
created: 2026-09-04
updated: 2026-09-04
---

# Repair KPI card JSX compile regression

## Superseded — correction completed in ADMIN-008 Attempt 2

Do not execute this task.

After a checkpoint restore, `ARCH-003-ADMIN-008` was confirmed to still be in
`review`, so the KPI-card parser regression remained within that task's original
containment scope. The correction was completed and validated in ADMIN-008
Attempt 2.

This task is retained only as coordination history and has no remaining work or
enables.

## Architecture

Architecture ID:

`ARCH-003`

Architecture document:

`docs/architecture/ARCH-003-admin-operational-ui.md`

Coordinator:

`moda_architect`

## Objective

Repair the current `KpiCard` JSX/template expression so the Admin application
parses and builds again, while preserving the accepted ADMIN-008 behavior:

- healthy numeric KPI values keep the large KPI treatment;
- non-numeric unavailable status text stays compact and contained inside the
  card.

## Context

After `ARCH-003-ADMIN-008` was architect-accepted, current-workspace runtime
evidence showed a compile-time parse failure in:

```text
moda-interact-admin/src/components/admin/kpi-card.tsx
```

The observed error is:

```text
Error: Expected '</', got '}'
Parsing ecmascript source code failed
```

The screenshot shows the `className` expression around the status/numeric style
branch has malformed JSX/template-literal closing syntax.

This is a current-working-tree regression. It blocks the Admin application from
rendering and therefore blocks further ARCH-003 UI work.

The previously reviewed archive contained a syntactically valid `KpiCard`, so
the repository state must be treated as the source of truth for this correction.
Do not assume the old reviewed archive matches the current working tree.

## Scope

- inspect the current `KpiCard` implementation;
- repair only the malformed JSX/template-literal/className expression;
- preserve the existing `status` behavior used for `Unavailable`;
- preserve the existing healthy numeric KPI styling;
- preserve card containment/min-width behavior introduced by ADMIN-008;
- add or adjust focused regression coverage only if required to ensure the
  component remains syntactically executable/renderable;
- run the complete validation contract before returning to review.

## Out of Scope

- Redis/BullMQ connection changes;
- queue readiness logic;
- queue overview data-model changes;
- Observability page/table work;
- failed-job work;
- redesign of the KPI card;
- unrelated formatting or refactoring;
- database, gateway, background, Shopify, messaging or shared-package changes.

## Requirements

1. `kpi-card.tsx` must parse as valid TSX.

2. Preserve the behavior split:

   ```text
   status=true
     -> compact wrapping status text suitable for "Unavailable"

   status=false
     -> existing large numeric KPI styling
   ```

3. Do not solve the compile error by removing the `status` capability or
   reverting the containment fix.

4. Do not change Redis settings or queue-reader logic.

5. The Tenant Directory route must render without the Next.js parser error shown
   in the reported evidence.

6. The final current working tree must pass TypeScript and the production build.
   A Completion Report claiming a passing build is not sufficient without the
   current tree actually parsing.

## Work Items

- [ ] Re-read the current `kpi-card.tsx` before editing.
- [ ] Repair the malformed JSX/template-literal closing syntax.
- [ ] Preserve compact unavailable-state styling and large numeric styling.
- [ ] Run focused KPI/queue-overview tests.
- [ ] Run the full Admin test suite.
- [ ] Run TypeScript validation.
- [ ] Run lint.
- [ ] Run the production build.
- [ ] Run `git diff --check`.
- [ ] Return the task to `review` and STOP.

## Interfaces / Contracts

Consumes the `KpiCard` component behavior established by:

- `ARCH-003-ADMIN-001`
- `ARCH-003-ADMIN-008`

No runtime or cross-service contract changes are authorised.

## Dependencies

- `ARCH-003-ADMIN-008`

## Enables

- `ARCH-003-ADMIN-003`

## Acceptance Criteria

- [ ] `kpi-card.tsx` parses successfully.
- [ ] The Admin Tenant Directory no longer shows the Next.js
      `Expected '</', got '}'` parser error.
- [ ] `Unavailable` remains contained within the KPI card.
- [ ] Healthy numeric KPI values retain their existing visual emphasis.
- [ ] No Redis/BullMQ behavior is changed.
- [ ] Focused tests pass.
- [ ] Full Admin tests pass.
- [ ] Typecheck passes.
- [ ] Lint passes.
- [ ] Production build passes.
- [ ] `git diff --check` passes.

## Validation

- [ ] focused KPI / queue-overview tests
- [ ] full Admin tests
- [ ] repository typecheck
- [ ] repository lint
- [ ] production build
- [ ] `git diff --check`

## Implementation Notes

Keep the correction minimal.

A valid shape is conceptually:

```tsx
<h3
  className={
    status
      ? '...compact status classes...'
      : `...numeric classes ${accent ? '...' : '...'}`
  }
>
  {value}
</h3>
```

This example communicates the required syntax/branch shape only. Preserve the
current repository's accepted class names unless a tiny syntactic correction is
required.

## Completion Report

### Status

Not started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.
