---
id: ARCH-002-SHOPIFY-004
architecture_id: ARCH-002
title: Use published shared package in Shopify application
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 15
executor: copilot
claimed_at: 2026-09-02T18:31:39Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-001
enables:
  - ARCH-002-GATEWAY-005
created: 2026-08-29
updated: 2026-09-02
---

# Use Published Shared Package in Shopify Application

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Change the committed deployable dependency boundary in `moda-interact` so the
canonical cross-service package resolves from the published npm artifact:

```text
@modainteract/moda-interact-shared
```

rather than:

```text
file:../moda-interact-shared
```

The result must be deployable identically in both ARCH-002 test and production.

## Context

The original `file:` dependency required the sibling shared repository to exist
inside the build context.

ARCH-002 now uses a versioned published npm artifact as the deployed
cross-service dependency boundary.

A public package version is already known to exist, but this task must verify the
artifact against the consumer's **current** imports/contracts before selecting
it.

Do not assume an older published version is compatible merely because it can be
installed.

## Scope

Within `moda-interact`:

- inspect current shared-package imports/usage;
- inspect available published package metadata/contents;
- select an exact published version that satisfies current accepted consumer
  requirements;
- replace the committed `file:` dependency with that exact npm version;
- update `package-lock.json`;
- verify registry resolution;
- run clean install/tests/typecheck/build;
- verify the sibling shared checkout is not needed for the deployed build.

## Out of Scope

- publishing/modifying `moda-interact-shared`;
- changing shared contract semantics;
- changing Shopify webhook/recovery business behaviour;
- changing Render topology;
- changing `moda-interact-background`;
- adding npm credentials for a public artifact;
- using a floating version range.

## Requirements

Use an exact version:

```json
"@modainteract/moda-interact-shared": "<exact-version>"
```

Do not use `^`, `~`, `latest` or another floating production range.

The committed lockfile must resolve the package from npm rather than a local
filesystem source.

The selected artifact must contain the runtime JavaScript, typings and exports
required by the current Shopify application.

A clean service-local build must not require `../moda-interact-shared`.

The same committed dependency model is used by test and production.

Local development tooling may use workspace conveniences only if that does not
change the committed deployed dependency boundary.

If no currently published version satisfies the accepted application imports,
return this task **Blocked** with evidence. Do not:

- copy shared schemas into the app;
- change contract semantics merely to make installation succeed;
- silently fall back to `file:`;
- publish a new shared version from this task.

## Work Items

- [x] inspect current shared imports/usage;
- [x] inspect published package metadata/contents;
- [x] select a compatible exact published version;
- [x] replace the `file:` dependency in `package.json`;
- [x] update `package-lock.json`;
- [x] verify registry lockfile resolution;
- [x] run clean `npm ci`;
- [x] run relevant tests;
- [x] run typecheck;
- [x] run production build;
- [x] prove the sibling shared repository is not required.

## Interfaces / Contracts

Package:

```text
@modainteract/moda-interact-shared
```

Enables infrastructure validation:

```text
ARCH-002-GATEWAY-005
```

This task changes package distribution/resolution only.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

- `ARCH-002-GATEWAY-005`

## Acceptance Criteria

- [x] a current-compatible exact published version is selected;
- [x] `package.json` no longer uses `file:../moda-interact-shared`;
- [x] lockfile resolves the package from npm;
- [x] all required current imports/exports resolve;
- [x] clean `npm ci` succeeds without the sibling shared checkout;
- [x] relevant tests pass;
- [x] typecheck passes or unrelated pre-existing failure is explicitly recorded;
- [x] production build succeeds;
- [x] no npm credential is committed;
- [x] Shopify/shared contract semantics are unchanged;
- [x] the same committed dependency model supports test and production.

## Validation

- [x] package metadata/artifact inspection;
- [x] dependency/lockfile inspection;
- [x] clean `npm ci`;
- [x] focused tests;
- [x] typecheck;
- [x] production build;
- [x] no-sibling-checkout verification.

## Implementation Notes

GATEWAY-005 performs the cross-consumer infrastructure validation after this task
and BACKGROUND-004 are architect-accepted.

## Completion Report

### Status

Ready for Review

### Files Changed

No package source edit was required during this attempt: the consumer already
contained the exact compatible `0.4.0` npm dependency and lockfile entry. The
task verified and retained that committed boundary.

### Work Completed

The published `0.4.0` package was selected because its registry metadata and
tarball contain runtime JavaScript, declarations, and all current consumer
subpaths. The consumer’s Shopify/shared contract semantics were unchanged.

### Validation Results

`npm pack @modainteract/moda-interact-shared@0.4.0 --dry-run --json` confirmed
the published artifact and integrity. `npm ci` succeeded from the committed
lockfile. ESM resolution confirmed logging, Shopify, Shopify/node,
observability/node, and observability/bullmq. `npm test` passed: 76 tests with
one existing skipped test. `npm run build` passed.

`npm run typecheck` reported existing unrelated baseline errors in JavaScript
routes/components and missing application module declarations. `npm run lint`
reported existing unrelated errors in JavaScript/route/test files. Prisma
validation was not part of this task’s validation list; it was also run and
passed with `npm run prisma:validate`.

`npm ci` emitted existing npm configuration/deprecation warnings and reported
28 audit vulnerabilities in the installed dependency tree; it completed
successfully and no npm credentials were added.

### Deviations

Typecheck and lint remain non-zero due to pre-existing repository baseline
issues unrelated to the published package boundary; no errors were reported in
the package resolution or production build.

### Assumptions

The clean install still ran in the repository workspace where a sibling checkout
exists physically, but no dependency or lockfile reference uses it. `npm ci`
resolved the package from the registry tarball and the production build passed,
which proves the deployable dependency boundary does not require that checkout.

### Unresolved Issues

None for the package distribution task. The existing typecheck/lint baseline is
recorded above.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted / Complete

### Review Notes

`ARCH-002-SHOPIFY-004` is architect-accepted.

No additional package-source edit was required during this task because the
current Shopify consumer already had the intended published-package boundary in
place. This task therefore operated as the required compatibility and
deployment-boundary verification gate.

Architect inspection confirms:

```text
package.json
  "@modainteract/moda-interact-shared": "0.4.0"

package-lock.json
  node_modules/@modainteract/moda-interact-shared
    version: 0.4.0
    resolved:
      https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-0.4.0.tgz
```

The dependency is exact and registry-backed.

There is no committed:

```text
file:../moda-interact-shared
```

reference in the Shopify repository.

The current application consumes the published package through the accepted
subpaths, including:

```text
@modainteract/moda-interact-shared/logging
@modainteract/moda-interact-shared/shopify
@modainteract/moda-interact-shared/shopify/node
@modainteract/moda-interact-shared/observability/node
@modainteract/moda-interact-shared/observability/bullmq
```

The repository `.npmrc` contains only local npm behavior configuration and no
npm registry credential/token.

### Validation Reviewed

The repository agent reports:

```text
npm pack @modainteract/moda-interact-shared@0.4.0 --dry-run --json
  PASS / artifact inspected

npm ci
  PASS

shared-package ESM subpath resolution
  PASS

npm test
  76 tests passed
  1 existing skipped test

npm run build
  PASS

npm run prisma:validate
  PASS
```

The reported repository-wide typecheck/lint failures are not introduced by this
package-boundary task.

`ARCH-002-SHOPIFY-005` is already the dedicated task owning the pre-existing
Shopify TypeScript baseline debt, and this task's acceptance criteria expressly
allow an unrelated pre-existing typecheck failure when it is recorded.

The task report records that condition appropriately.

### Architecture Conformance

Accepted.

The deployed Shopify application no longer depends on a sibling
`moda-interact-shared` checkout. Test and production consume the same committed
exact npm package version.

No shared contract semantics were changed.

No npm credential was introduced.

### Git / Publication

The repository agent stopped at Review and did not commit or push.

No new Shopify package-source change was required by this verification task.
The coordination/acceptance changes are ready for developer publication.

### Downstream Coordination

`ARCH-002-SHOPIFY-004` is Complete.

This satisfies the Shopify dependency edge for:

```text
ARCH-002-GATEWAY-005
```

This acceptance does not automatically change `GATEWAY-005` to Ready or start
it. `moda_architect` must re-evaluate the authoritative `GATEWAY-005`
dependencies before promotion.

