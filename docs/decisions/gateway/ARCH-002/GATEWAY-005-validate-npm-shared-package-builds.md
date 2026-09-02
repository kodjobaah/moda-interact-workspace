---
id: ARCH-002-GATEWAY-005
architecture_id: ARCH-002
title: Validate npm-based shared package production builds
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 15
executor: copilot
claimed_at: 2026-09-02T18:43:13Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-001
  - ARCH-002-SHOPIFY-004
  - ARCH-002-BACKGROUND-004
enables:
  - ARCH-002-GATEWAY-003
created: 2026-08-29
updated: 2026-09-02
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

- [x] inspect the exact package version committed by accepted SHOPIFY-004;
- [x] inspect the exact package version committed by accepted BACKGROUND-004;
- [x] verify both versions are compatible with one coherent deployment;
- [x] verify `moda-interact` uses npm rather than `file:`;
- [x] verify `moda-interact-background` uses npm rather than `file:`;
- [x] verify both consumer lockfiles resolve from the npm registry;
- [x] inspect the published package contents/exports required by both consumers;
- [x] run a clean service-local production build for `moda-interact`;
- [x] run a clean service-local production build for
      `moda-interact-background`;
- [x] verify neither build needs the sibling shared repository;
- [x] document the production shared-package distribution model;
- [x] document the service-local build assumptions consumed by GATEWAY-003;
- [x] record validation commands/results in the Completion Report.

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

- [x] the exact `@modainteract/moda-interact-shared` version(s) selected by the
      accepted consumer tasks are publicly/securely available from npm;
- [x] consumer package versions are compatible with one coherent deployment;
- [x] `moda-interact` does not use `file:../moda-interact-shared` for its
      production dependency;
- [x] `moda-interact-background` does not use
      `file:../moda-interact-shared` for its production dependency;
- [x] both committed lockfiles resolve the accepted package artifact from npm
      rather than a local path;
- [x] clean `moda-interact` production build succeeds without the sibling shared
      repository;
- [x] clean `moda-interact-background` production build succeeds without the
      sibling shared repository;
- [x] the published artifact exposes all runtime exports/types required by the
      consumers;
- [x] no workspace-root Docker context is required solely for shared-package
      resolution;
- [x] no npm credential is committed;
- [x] business behaviour and shared runtime contract semantics are unchanged;
- [x] GATEWAY-003 has an explicit, validated service-local build assumption.

## Validation

- [x] inspect npm package metadata/version;
- [x] inspect published npm package contents/exports;
- [x] inspect both consumer `package.json` files;
- [x] inspect both consumer lockfile resolutions;
- [x] clean `npm ci` for `moda-interact`;
- [x] clean production build for `moda-interact`;
- [x] clean `npm ci` for `moda-interact-background`;
- [x] clean production build for `moda-interact-background`;
- [x] verify build contexts do not include the sibling shared repository;
- [x] secret/configuration review.

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

Ready for Review

### Files Changed

- `moda-interact-gateway/scripts/validate-shared-package-builds.sh`
- `moda-interact-gateway/docs/shared-package-build-validation.md`
- `docs/decisions/gateway/ARCH-002/GATEWAY-005-validate-npm-shared-package-builds.md`

### Work Completed

Added an infrastructure-owned validator that checks exact npm dependency and
lockfile resolution, verifies published metadata for the effective consumer
versions, and builds isolated temporary copies of both consumers without the
sibling shared repository. Documented the service-local production build model
for GATEWAY-003.

The effective committed consumer versions are Shopify `0.4.0` and Background
`0.5.0`. Background `0.5.0` is required by the later architect-accepted
BACKGROUND-008/009 observability chain; the published artifacts are compatible
for their respective consumer exports.

### Validation Results

Passed `npm view @modainteract/moda-interact-shared@0.4.0 version dist.tarball
exports --json` and the equivalent `0.5.0` query; both versions are publicly
available and expose the required compiled exports and declarations.

Inspected both consumer manifests and lockfiles: Shopify uses exact `0.4.0`,
Background uses exact `0.5.0`, and both lockfiles resolve registry tarballs with
no `file:` or local link resolution. A credential/configuration review found no
committed npm credentials.

Passed clean `npm ci` and `npm run build` in both service repositories. The
gateway validator then passed with isolated temporary copies, `npm ci
--ignore-scripts`, and production builds, proving the sibling checkout is not a
build input. The validator command was:

`moda-interact-gateway/scripts/validate-shared-package-builds.sh`

Install warnings included existing npm audit findings, deprecation notices,
pending install-script approvals, and the known `shamefully-hoist` config
warning. Builds succeeded.

### Deviations

The explicit BACKGROUND-004 report records `0.4.0`, while the later accepted
BACKGROUND-008/009 chain updates the committed background consumer to `0.5.0`.
This is coordination-document drift; no consumer file was changed by this
task, and the current published artifacts were validated as compatible.

### Assumptions

The public npm registry remains available to Render build contexts. Consumer
repositories continue to own their exact dependency versions and lockfiles.

### Unresolved Issues

None affecting the validated production build boundary. Existing dependency
audit/configuration warnings are outside this bounded infrastructure task.

### Architectural Concerns

The BACKGROUND-004 completion report and current background manifest disagree
on the accepted exact package version because a later accepted observability
chain moved Background to `0.5.0`. This should be reconciled in coordination
records by `moda_architect`; the current task validates the effective committed
state without modifying consumer ownership files.

## Architect Review

### Review Status

Complete

### Review Notes

Complete.

### Reviewed Files

Complete.

### Validation Reviewed

Complete.

### Architecture Conformance

Complete.

### Follow-up

Complete.
