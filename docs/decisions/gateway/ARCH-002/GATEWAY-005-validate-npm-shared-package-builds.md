---
id: ARCH-002-GATEWAY-005
architecture_id: ARCH-002
title: Validate npm-based shared package production builds
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: pending
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-GATEWAY-001
  - ARCH-002-SHOPIFY-004
  - ARCH-002-BACKGROUND-004
enables:
  - ARCH-002-GATEWAY-003
created: 2026-08-29
updated: 2026-08-29
---

# Validate npm-based shared package production builds

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Validate that `moda-interact` and `moda-interact-background` can perform clean,
independent production builds using the published npm package:

```text
@modainteract/moda-interact-shared
```

rather than relying on the sibling workspace dependency:

```text
file:../moda-interact-shared
```

Production deployment must not require the Render build context to include the
`moda-interact-shared` repository solely to satisfy this package dependency.

## Context

`@modainteract/moda-interact-shared` is already published as a public npm
package.

ARCH-002 therefore uses the npm registry as the production distribution
boundary for the shared cross-service package.

The intended production dependency model is:

```text
moda-interact-shared
        |
        | publish versioned package
        v
     npm registry
        |
        +-------------------------------+
        |                               |
        v                               v
moda-interact                  moda-interact-background
npm ci                         npm ci
        |                               |
        +-------------------------------+
                        |
                 exact shared version
```

The application repositories own their own dependency declarations.

`moda_gateway` does not modify application `package.json` or lockfiles merely to
make infrastructure deployable.

Those consumer changes are owned by:

```text
ARCH-002-SHOPIFY-004
ARCH-002-BACKGROUND-004
```

There is no speculative ARCH-002 shared-package task in the dependency graph.

If either consumer task proves that the currently published package cannot
satisfy the accepted runtime contract, that consumer task must return Blocked
with evidence. `moda_architect` may then create a bounded `moda_shared` task.

Do not invent such a shared task in advance.

Local development may continue to use workspace-oriented workflows where
useful, but committed production dependency resolution must use the exact
versioned npm artifact selected by the accepted consumer tasks.

## Scope

This task may modify infrastructure-owned files required to validate and
document the production build model, including:

- `moda-interact-gateway` deployment/build documentation;
- infrastructure validation scripts owned by `moda_gateway`.

This task may inspect:

- `moda-interact/package.json`;
- `moda-interact/package-lock.json`;
- `moda-interact/Dockerfile`;
- `moda-interact-background/package.json`;
- `moda-interact-background/package-lock.json`;
- `moda-interact-background/Dockerfile`;
- published `@modainteract/moda-interact-shared` package metadata/artifact;
- `moda-interact-shared/package.json` where useful for artifact verification.

Validate clean, service-local production builds after the owning application
agents have replaced the `file:` dependency.

GATEWAY-005 does **not** own the Render Blueprint files. GATEWAY-003 consumes the
validated build assumptions and creates:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

## Out of Scope

- modifying `moda-interact/package.json` or its lockfile;
- modifying `moda-interact-background/package.json` or its lockfile;
- publishing a new shared npm package version;
- creating a speculative `ARCH-002-SHARED-*` task;
- changing shared runtime contracts;
- application business logic;
- queue/event schema changes;
- using a workspace-root Docker context solely to reach
  `../moda-interact-shared`;
- modifying Render Blueprint topology.

## Requirements

Production consumers must resolve `@modainteract/moda-interact-shared` from the
npm registry.

Each consumer must use an architect-approved **exact** package version.

GATEWAY-005 must inspect the exact versions committed by the architect-accepted
`ARCH-002-SHOPIFY-004` and `ARCH-002-BACKGROUND-004` tasks.

The two consumers must resolve to a compatible accepted package artifact.

If the completed consumer tasks use different versions and that difference
prevents one coherent deployment contract, return GATEWAY-005 Blocked to
`moda_architect` rather than silently selecting a version.

Do not assume a particular package version merely because it is currently
published.

Consumer lockfiles must resolve the package to a registry artifact and must not
resolve it to:

```text
file:../moda-interact-shared
```

or another local filesystem path.

The published package must contain the compiled JavaScript, typings and exports
required by the accepted application/background contracts.

A clean production build of each consumer must succeed using only that service's
normal source repository/build context plus registry dependencies.

The build must not depend on an unpublished sibling checkout of
`moda-interact-shared`.

No npm authentication token is required for a public package. Do not introduce
an npm secret merely because the package is namespaced.

If the accepted package is later made private, npm authentication must be
handled as a separate secret/configuration decision; credentials must never be
committed.

## Work Items

- [ ] inspect the exact package version committed by accepted SHOPIFY-004;
- [ ] inspect the exact package version committed by accepted BACKGROUND-004;
- [ ] verify both versions are compatible with one coherent deployment;
- [ ] verify `moda-interact` uses npm rather than `file:`;
- [ ] verify `moda-interact-background` uses npm rather than `file:`;
- [ ] verify both consumer lockfiles resolve from the npm registry;
- [ ] inspect the published package contents/exports required by both consumers;
- [ ] run a clean service-local production build for `moda-interact`;
- [ ] run a clean service-local production build for
      `moda-interact-background`;
- [ ] verify neither build needs the sibling shared repository;
- [ ] document the production shared-package distribution model;
- [ ] document the service-local build assumptions consumed by GATEWAY-003;
- [ ] record validation commands/results in the Completion Report.

## Interfaces / Contracts

Package:

```text
@modainteract/moda-interact-shared
```

Consumer dependency owners:

```text
ARCH-002-SHOPIFY-004
ARCH-002-BACKGROUND-004
```

Infrastructure validation owner:

```text
ARCH-002-GATEWAY-005
```

Blueprint consumer:

```text
ARCH-002-GATEWAY-003
```

This task does not redefine any shared runtime contract.

It proves that the exact published artifact selected by the accepted consumers
can be consumed by the production deployment model.

## Dependencies

- `ARCH-002-GATEWAY-001`
- `ARCH-002-SHOPIFY-004`
- `ARCH-002-BACKGROUND-004`

## Enables

- `ARCH-002-GATEWAY-003`

## Acceptance Criteria

- [ ] the exact `@modainteract/moda-interact-shared` version(s) selected by the
      accepted consumer tasks are publicly/securely available from npm;
- [ ] consumer package versions are compatible with one coherent deployment;
- [ ] `moda-interact` does not use `file:../moda-interact-shared` for its
      production dependency;
- [ ] `moda-interact-background` does not use
      `file:../moda-interact-shared` for its production dependency;
- [ ] both committed lockfiles resolve the accepted package artifact from npm
      rather than a local path;
- [ ] clean `moda-interact` production build succeeds without the sibling shared
      repository;
- [ ] clean `moda-interact-background` production build succeeds without the
      sibling shared repository;
- [ ] the published artifact exposes all runtime exports/types required by the
      consumers;
- [ ] no workspace-root Docker context is required solely for shared-package
      resolution;
- [ ] no npm credential is committed;
- [ ] business behaviour and shared runtime contract semantics are unchanged;
- [ ] GATEWAY-003 has an explicit, validated service-local build assumption.

## Validation

- [ ] inspect npm package metadata/version;
- [ ] inspect published npm package contents/exports;
- [ ] inspect both consumer `package.json` files;
- [ ] inspect both consumer lockfile resolutions;
- [ ] clean `npm ci` for `moda-interact`;
- [ ] clean production build for `moda-interact`;
- [ ] clean `npm ci` for `moda-interact-background`;
- [ ] clean production build for `moda-interact-background`;
- [ ] verify build contexts do not include the sibling shared repository;
- [ ] secret/configuration review.

## Implementation Notes

The preferred production boundary is:

```text
source repository
    ->
npm ci
    ->
published @modainteract/moda-interact-shared exact version
    ->
production build
```

not:

```text
workspace root
    ->
sibling moda-interact-shared checkout
    ->
file:../moda-interact-shared
```

This intentionally removes a cross-repository build-context dependency.

Do not replace an explicit version with a floating dependency merely for
convenience.

If the npm artifact selected by the accepted consumer tasks cannot satisfy the
current consumer code, return the task Blocked with evidence. Do not silently
fall back to the workspace `file:` dependency.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

`@modainteract/moda-interact-shared` remains available through the
architecture-approved npm registry.

### Unresolved Issues

The exact npm package version is determined by the accepted SHOPIFY-004 and
BACKGROUND-004 consumer implementations.

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

### Follow-up

Pending.
