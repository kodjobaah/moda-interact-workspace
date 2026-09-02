---
id: ARCH-002-SHOPIFY-005
architecture_id: ARCH-002
title: Eliminate existing Shopify application TypeScript baseline debt
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: ready
priority: 16
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-SHOPIFY-002
enables: []
created: 2026-08-30
updated: 2026-08-30
---

# Eliminate Existing Shopify Application TypeScript Baseline Debt

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Remove the known repository-wide TypeScript baseline debt from `moda-interact`
so the application's existing typecheck command:

```bash
npm run typecheck
```

completes successfully with zero TypeScript errors.

The current command is:

```text
react-router typegen && tsc --noEmit
```

The task is complete only when that existing repository validation command
returns exit code `0`.

## Context

During ARCH-002 Shopify work, repository-wide typecheck repeatedly reported a
known pre-existing baseline of:

```text
48 errors in 8 files
```

That baseline was deliberately not allowed to block bounded tasks such as
`ARCH-002-SHOPIFY-001` and `ARCH-002-SHOPIFY-002`, because those tasks did not
introduce the errors.

The baseline is now being addressed directly by this dedicated cleanup task.

Current observed compiler categories are:

| TypeScript error | Count | Current symptom |
|---|---:|---|
| `TS7006` | 27 | function/callback parameter implicitly has `any` |
| `TS2307` | 9 | `@/...` module imports cannot be resolved |
| `TS7031` | 7 | destructured route parameters implicitly have `any` |
| `TS7017` | 3 | `global.prismaGlobal` is not typed on `globalThis` |
| `TS2339` | 2 | Shopify `s-app-nav` is not known to JSX intrinsic elements |
| **Total** | **48** | **8 files** |

Current observed files:

```text
app/db.server.js                              3
app/routes/_index/route.jsx                  1
app/routes/app._index.jsx                   23
app/routes/app.jsx                           4
app/routes/app.usage.jsx                    12
app/routes/auth.$.jsx                        2
app/routes/auth.login/error.server.jsx       1
app/routes/auth.login/route.jsx              2
                                            --
                                            48
```

Treat this output as the starting evidence, not as a prescribed implementation
solution.

## Architectural Intent

This is a type-safety/configuration cleanup task.

It must preserve the application's accepted runtime behaviour and deployment
contracts.

Fix root causes where practical rather than suppressing compiler diagnostics.

Examples of root causes that must be investigated include:

- whether the `@/...` path alias is missing or inconsistent between runtime
  tooling and TypeScript;
- whether unresolved imports are causing downstream loss of inferred types;
- how Prisma's development global singleton should be typed;
- how React Router loader/action/header arguments should be typed under the
  repository's existing JSX/JS-checking approach;
- how Shopify custom elements such as `s-app-nav` should receive their intended
  JSX typings;
- which remaining implicit-`any` callbacks require explicit types after upstream
  resolution is repaired.

These are investigation targets, not instructions to force a particular fix.

## Scope

Within `moda-interact`:

- inspect the current TypeScript/JavaScript checking configuration;
- inspect React Router type-generation configuration and current route typing
  conventions;
- inspect path-alias configuration across TypeScript and runtime/build tooling;
- inspect existing Shopify web-component type support;
- inspect the Prisma client singleton typing;
- fix the current 48 errors at their appropriate root causes;
- add focused type declarations/configuration only where genuinely required;
- preserve runtime behaviour;
- run the existing repository-wide typecheck until it returns zero;
- run relevant tests and production build after the cleanup.

The task may modify existing affected source/configuration files where needed.

## Out of Scope

- redesigning Shopify application behaviour;
- changing checkout/recovery business logic;
- changing ARCH-002 Render topology;
- changing database schema;
- changing shared-package contract semantics;
- changing unrelated repositories;
- broad conversion of the application to TypeScript unless a small conversion is
  demonstrably the safest fix for a specific affected file;
- unrelated lint/style cleanup;
- package upgrades unrelated to resolving the actual typecheck failures.

## Prohibited Shortcuts

Do not make typecheck green by weakening the validation contract.

Specifically, do not:

- remove or bypass `npm run typecheck`;
- remove `react-router typegen`;
- remove `tsc --noEmit`;
- disable `checkJs` merely to hide existing JS/JSX errors;
- weaken `strict`/`noImplicitAny` or equivalent settings merely to hide errors;
- add `// @ts-nocheck`;
- add blanket `// @ts-ignore`;
- add broad/global `any` declarations solely to suppress diagnostics;
- declare `s-app-nav` as an untyped catch-all element if an existing Shopify
  typing mechanism can be correctly wired;
- replace unresolved imports with duplicated local code;
- change runtime behaviour merely to satisfy the compiler.

A narrow `any` is permitted only when it accurately models an unavoidable
external boundary and is justified in the Completion Report. It must not be used
as the default cleanup strategy.

## Suggested Investigation Order

The implementing agent should work from upstream causes toward downstream
symptoms.

### 1. Module/path resolution

Investigate the nine `TS2307` errors involving imports such as:

```text
@/components/...
@/services/...
```

Determine whether the source files exist and whether the project's alias is
configured consistently for TypeScript and the application's build/runtime.

Do not assume the alias is the cause until configuration and source paths are
inspected.

After fixing module resolution, rerun typecheck before manually typing callback
parameters because restored imported types may eliminate downstream implicit-any
errors.

### 2. Prisma development global

Resolve the three `TS7017` errors around:

```text
global.prismaGlobal
```

using a type-safe project-appropriate declaration/implementation.

Preserve the existing development singleton behaviour.

### 3. React Router route contracts

Resolve the `TS7031` route argument errors and route `headersArgs` errors using
the repository's supported React Router typing approach.

Prefer framework-provided/generated types or precise JSDoc/type declarations
over generic object/`any` annotations.

### 4. Shopify JSX custom elements

Resolve the two `TS2339` errors for:

```text
s-app-nav
```

by correctly wiring the intended Shopify web-component JSX typings where
available.

Do not suppress JSX checking globally.

### 5. Remaining callback inference

After upstream typing/module-resolution fixes, inspect the remaining `TS7006`
errors individually.

Use inferred domain/service/Prisma types wherever possible.

Add explicit narrow types only where inference cannot correctly supply them.

## Work Items

- [ ] capture the starting `npm run typecheck` result;
- [ ] confirm the starting baseline is the documented 48-error condition or
      explain any drift before implementation;
- [ ] inspect TypeScript/JS checking configuration;
- [ ] inspect React Router generated typing conventions;
- [ ] resolve `@/...` import/type resolution correctly;
- [ ] resolve Prisma global singleton typing;
- [ ] resolve route loader/action/header argument typing;
- [ ] resolve Shopify `s-app-nav` JSX typing;
- [ ] resolve remaining implicit-any callback parameters;
- [ ] rerun repository-wide `npm run typecheck`;
- [ ] run relevant/full test suite;
- [ ] run production build;
- [ ] inspect the final diff for type-suppression shortcuts;
- [ ] report final baseline as zero.

## Interfaces / Contracts

The existing validation contract remains:

```bash
npm run typecheck
```

which executes:

```text
react-router typegen && tsc --noEmit
```

Do not replace that contract with a narrower command for task acceptance.

Runtime Shopify/HTTP/database contracts must remain unchanged.

## Dependencies

- `ARCH-002-SHOPIFY-002`

This dependency ensures the accepted deployment/startup contract remains the
stable base while this cleanup is performed.

## Enables

None.

This task improves the repository validation baseline but is not intended to
silently add a new blocking dependency to existing ARCH-002 tasks.

## Acceptance Criteria

- [ ] `npm run typecheck` exits `0`;
- [ ] TypeScript reports zero repository-wide errors;
- [ ] the original 48-error baseline is eliminated;
- [ ] all nine current `TS2307` module-resolution errors are resolved correctly;
- [ ] Prisma global singleton typing is type-safe;
- [ ] React Router route arguments use appropriate framework/project types;
- [ ] Shopify custom-element typing is correctly wired;
- [ ] remaining callback parameters have useful inferred or explicit types;
- [ ] no `@ts-nocheck` is introduced;
- [ ] no blanket `@ts-ignore` suppression is introduced;
- [ ] TypeScript/JavaScript checking is not weakened to hide the baseline;
- [ ] runtime business behaviour is unchanged;
- [ ] relevant/full tests pass;
- [ ] production build succeeds;
- [ ] no unrelated repository is modified.

## Validation

Required:

```bash
npm run typecheck
```

Expected final result:

```text
exit code: 0
TypeScript errors: 0
```

Also run:

- relevant focused tests for changed behaviour/configuration;
- the repository's full test suite where practical;
- production build;
- any existing lint command required by the repository/task workflow.

The Completion Report must include:

- starting error count;
- final error count;
- root-cause groups actually found;
- files/configuration changed;
- whether any errors disappeared as a consequence of upstream fixes rather than
  direct annotations;
- tests/build results;
- confirmation that no prohibited compiler-suppression shortcut was used.

## Development Baseline Follow-up

The workspace development baseline currently records this condition as:

```text
TYPECHECK-001
Disposition: KNOWN BASELINE DEBT
```

Do not mark that baseline entry `RESOLVED` yourself unless the task workflow
explicitly assigns that global documentation ownership to `moda_app`.

Instead, once this task reaches `status: review`, report:

```text
TYPECHECK-001 candidate for RESOLVED
npm run typecheck: 0 errors
```

`moda_architect` will update the durable baseline as part of architect
acceptance.

After architect acceptance, the intended future baseline becomes:

```text
moda-interact npm run typecheck
    -> must remain at 0 errors
```

Future Shopify tasks may not rely on the former 48-error exemption after this
task is accepted.

## Implementation Notes

The supplied baseline output shows the errors are concentrated rather than
repository-wide in origin.

Do not assume all 27 implicit-any errors require 27 manual annotations.

In particular, unresolved service/component imports may be preventing useful
type propagation. Re-run typecheck after each root-cause group is corrected.

Keep the solution as small as possible while restoring a genuinely clean
repository typecheck.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Starting Baseline

```text
48 TypeScript errors in 8 files
```

### Final Baseline

Not run.

### Root Causes Found

Pending implementation.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None recorded yet.

### Architectural Concerns

None recorded yet.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Baseline Follow-up

On acceptance, update `TYPECHECK-001` from `KNOWN BASELINE DEBT` to `RESOLVED`
only after architect verification of a clean repository-wide typecheck.

### Follow-up

Pending.
