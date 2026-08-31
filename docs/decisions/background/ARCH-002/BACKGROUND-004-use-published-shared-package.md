---
id: ARCH-002-BACKGROUND-004
architecture_id: ARCH-002
title: Use published shared package in background service
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 15
executor: codex
claimed_at: 2026-08-31 17:04:35+00:00
attempt: 1
depends_on:
- ARCH-002-GATEWAY-001
- ARCH-002-SHARED-010
enables:
- ARCH-002-GATEWAY-005
- ARCH-002-BACKGROUND-005
created: 2026-08-29
updated: '2026-08-31'
---

# Use Published Shared Package in Background Service

## Current Architect Instruction — Exact Shared Release

`ARCH-002-SHARED-010` is architect-accepted Complete.

Use the exact published release:

```text
@modainteract/moda-interact-shared@0.4.0
```

Do not select a different version and do not use a floating semver range.

The task still owns dependency/lockfile migration and clean-consumer validation;
it does not publish or modify the shared package.

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Change the committed deployable dependency boundary in
`moda-interact-background` so the canonical cross-service package resolves from
the published npm artifact:

```text
@modainteract/moda-interact-shared
```

rather than:

```text
file:../moda-interact-shared
```

The result must support all three ARCH-002 worker entrypoints in both test and
production.

## Context

The original `file:` dependency required the sibling shared repository to exist
inside the build context.

ARCH-002 now uses a versioned published npm artifact as the deployed
cross-service dependency boundary.

A public version is known to exist, but this task must verify the artifact
against the **current** background imports, queue/event contracts and runtime
exports before selecting it.

## Scope

Within `moda-interact-background`:

- inspect current shared-package imports/usage;
- inspect available published package metadata/contents;
- select an exact compatible published version;
- replace the committed `file:` dependency with that exact npm version;
- update `package-lock.json`;
- verify registry resolution;
- verify all three worker entrypoints/build targets compile against the artifact;
- run clean install/tests/typecheck/build;
- verify the sibling shared checkout is not required for deployed builds.

## Out of Scope

- publishing/modifying `moda-interact-shared`;
- changing shared queue/event contracts;
- changing recovery/order/messaging business semantics;
- changing worker topology;
- changing Render infrastructure;
- changing `moda-interact`;
- adding npm credentials for a public artifact;
- using a floating version range.

## Requirements

Use an exact version:

```json
"@modainteract/moda-interact-shared": "<exact-version>"
```

The lockfile must resolve the artifact from npm rather than a local path.

The selected package must expose all schemas, queue/job constants, types and
helpers consumed by the current background implementation.

The same committed dependency model must work for:

```text
moda-shopify-event-worker
moda-recovery-worker
moda-messaging-worker
```

and for both deployed environments.

If no currently published artifact satisfies the accepted consumer code, return
this task **Blocked** with evidence. Do not:

- copy/recreate shared contracts locally;
- change contract semantics merely to install a package;
- silently fall back to `file:`;
- publish a new package version from this task.

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
- [x] verify all three worker entrypoints compile/start as applicable;
- [x] prove the sibling shared repository is not required.

## Interfaces / Contracts

Package:

```text
@modainteract/moda-interact-shared
```

Enables:

```text
ARCH-002-GATEWAY-005
```

This task changes package distribution/resolution only.

## Dependencies

- `ARCH-002-GATEWAY-001`
- `ARCH-002-SHARED-010`

## Enables

- `ARCH-002-GATEWAY-005`
- `ARCH-002-BACKGROUND-005`

## Acceptance Criteria

- [x] a current-compatible exact published version is selected;
- [x] `package.json` no longer uses `file:../moda-interact-shared`;
- [x] lockfile resolves the package from npm;
- [x] all required current background exports resolve;
- [x] all three worker deployment units compile against the package;
- [x] clean `npm ci` succeeds without the sibling shared checkout;
- [x] relevant tests pass;
- [x] typecheck passes or unrelated pre-existing failure is explicitly recorded;
- [x] production build succeeds;
- [x] no npm credential is committed;
- [x] background/shared contract semantics are unchanged;
- [x] the same committed dependency model supports test and production.

## Validation

- [x] package metadata/artifact inspection;
- [x] dependency/lockfile inspection;
- [x] clean `npm ci`;
- [x] focused tests;
- [x] typecheck;
- [x] production build;
- [x] worker-entrypoint compile/start verification where practical;
- [x] no-sibling-checkout verification.

## Implementation Notes

GATEWAY-005 performs the cross-consumer infrastructure validation after this task
and SHOPIFY-004 are architect-accepted.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `docs/decisions/background/ARCH-002/BACKGROUND-004-use-published-shared-package.md`

### Work Completed

- Inspected all current background imports of the shared package. Runtime code
	consumes `@modainteract/moda-interact-shared/shopify` and
	`@modainteract/moda-interact-shared/shopify/node`.
- Verified registry metadata for architect-approved exact release `0.4.0`,
	including both required JavaScript/declaration export targets.
- Replaced `file:../moda-interact-shared` with exact version `0.4.0` and updated
	the lockfile to the npm registry tarball and published integrity.
- Preserved all shared contract imports, queue/job constants, worker entrypoints
	and business behavior unchanged.

### Validation Results

- `npm view @modainteract/moda-interact-shared@0.4.0 version dist.tarball dist.integrity exports --json`:
	confirmed version `0.4.0`, the public npm tarball, accepted integrity
	`sha512-eBSb...Ypl+7og==`, and required `./shopify` and `./shopify/node`
	exports.
- Lockfile inspection confirmed exact root dependency `0.4.0`, registry tarball
	resolution, matching integrity, and no `file:`, sibling `resolved`, or `link`
	marker. Credential scan found no committed npm authentication material.
- `npm ci`: passed from the registry-backed lockfile. npm reported three high
	severity audit findings and five allow-scripts advisories; no install failure.
- Direct ESM imports of `./shopify` and `./shopify/node`: passed.
- `npm test -- --run tests/unit/events/shopify-contract-adapter.test.ts tests/unit/services/pending-recovery-candidate.service.test.ts`:
	passed, 2 files and 12 tests.
- `npm test`: 10 files passed, 2 failed, 1 skipped; 64 tests passed, 2 failed,
	2 skipped. Failures were the existing `customerPhone.findMany` Prisma mock
	omission in `recovery-routing.service.test.ts` and an external Groq response
	whose tool-call arguments were not valid JSON in
	`commerce.agent.integration.test.ts`; neither concerns shared contracts.
- `./node_modules/.bin/tsc --noEmit`: passed.
- `npm run build`: passed, including Prisma Client generation and production
	TypeScript compilation of all three worker entrypoints.
- A temporary standalone copy with no sibling shared repository passed clean
	`npm ci`, direct shared-subpath imports, typecheck, production build, and all
	three compiled worker start-command resolution checks.
- `scripts/workspace-doctor.sh --quick`: 7 checks passed; one unrelated existing
	Shopify `shamefully-hoist` warning remained.
- VS Code diagnostics for package and lockfile were clean.

### Deviations

None.

### Assumptions

- The architect-approved `0.4.0` registry integrity recorded by SHARED-010 and
	returned by npm is the canonical package artifact for this consumer.

### Unresolved Issues

- The unrelated recovery-routing mock defect leaves one unit test failing.
- The live Groq integration returned malformed tool-call JSON during this run;
	focused shared-contract tests remain green.
- npm reports three high-severity audit findings and five install-script
	approval advisories; dependency migration, typecheck and build still succeed.

### Architectural Concerns

None. This task changed package distribution/resolution only; shared contracts,
queue semantics, worker topology and business behavior are unchanged.

## Architect Review

### Review Status

Accepted

### Review Notes

Accepted by `moda_architect` on 2026-08-31.

The implementation is exactly scoped to the published-package migration:

- `moda-interact-background/package.json` now pins
  `@modainteract/moda-interact-shared` to exact version `0.4.0`;
- `package-lock.json` resolves the package from the npm registry tarball rather
  than `file:../moda-interact-shared`;
- the lockfile records the architect-approved `0.4.0` integrity;
- all existing background shared imports remain unchanged;
- no shared contract, queue/job semantic, worker topology or business logic was
  modified;
- comparison with the architect-accepted BACKGROUND-002 workspace confirms zero
  background implementation-source changes.

### Reviewed Files

Reviewed:

- `moda-interact-background/package.json`;
- `moda-interact-background/package-lock.json`;
- current background shared-package import usage;
- Completion Report and validation evidence.

### Validation Reviewed

Accepted evidence:

- npm registry metadata inspection for exact `0.4.0`;
- registry-backed lockfile resolution and integrity verification;
- clean `npm ci`;
- direct ESM import checks for `./shopify` and `./shopify/node`;
- focused shared-contract tests: 12/12 passed;
- TypeScript typecheck passed;
- production build passed;
- all three worker entrypoints compiled/resolved;
- standalone no-sibling-checkout verification passed.

The repository-wide suite still contains the previously known unrelated
recovery-routing Prisma mock failure. One live Groq integration also returned
malformed external tool-call JSON during this run. Neither failure concerns the
package-distribution boundary changed by this task.

### Architecture Conformance

Conforms.

This task changed only dependency distribution/resolution. It did not begin
BACKGROUND-005 shared observability runtime integration.

### Follow-up

`ARCH-002-BACKGROUND-004` is Complete.

All dependencies of `ARCH-002-BACKGROUND-005` are now Complete, so
BACKGROUND-005 may become Ready.
