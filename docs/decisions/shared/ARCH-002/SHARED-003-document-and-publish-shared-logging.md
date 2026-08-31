---
id: ARCH-002-SHARED-003
architecture_id: ARCH-002
title: Document and publish shared logging package release
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 26
executor: codex
claimed_at: 2026-08-30T17:18:53Z
attempt: 1
depends_on:
  - ARCH-002-SHARED-002
enables:
  - ARCH-002-SHOPIFY-003
created: 2026-08-30
updated: 2026-08-30
---

# Document and Publish Shared Logging Package Release

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Logging design:

`docs/architecture/ARCH-002-shared-logging-amendment.md`

Release amendment:

`docs/architecture/ARCH-002-shared-logging-release-amendment.md`

Coordinator:

`moda_architect`

## Objective

Prepare, document, publish and independently verify the first public
`@modainteract/moda-interact-shared` release containing:

```text
@modainteract/moda-interact-shared/logging
```

This is deliberately separate from `ARCH-002-SHARED-002`.

`SHARED-002` owns logger implementation.

`SHARED-003` owns the public npm release boundary:

```text
README
package version
package-lock version
pack validation
npm publication
registry verification
clean external-consumer smoke test
```

Shopify remains blocked until this release is architect-accepted.

## Dependency

This task may begin only after:

```text
ARCH-002-SHARED-002 = Complete
```

Do not publish an implementation merely because it has been returned for review.

## Public README

The complete target public README is supplied at:

```text
docs/decisions/shared/ARCH-002/SHARED-003-reference/README.md
```

Use it to update:

```text
moda-interact-shared/README.md
```

Before committing it, reconcile only factual symbol/export details against the
accepted SHARED-002 implementation.

Do not silently redesign the documented logging API.

The public README must document:

- package purpose and ownership boundary;
- Shopify shared contracts;
- structured logging;
- `createLogger`;
- log levels;
- optional `child()` semantics;
- service/environment identity;
- sensitive-data rules;
- Error handling;
- logging/OpenTelemetry separation;
- public package subpaths;
- development commands;
- semantic-version/release policy.

## Version

The currently known package version before this logging release is:

```text
0.1.0
```

The new `./logging` export is a backwards-compatible additive public capability.

Therefore, if the package is still `0.1.0` when this task executes, the
architect-approved release target is:

```text
0.2.0
```

Update both:

```text
package.json
package-lock.json
```

If the current version is no longer `0.1.0`, stop and report the observed
version to `moda_architect`. Do not overwrite a newer version or guess the next
release.

## Pre-Publish Validation

Before publication confirm:

```text
SHARED-002 status = complete
package name = @modainteract/moda-interact-shared
package version = architect-approved target
./logging export exists
dist/logging/index.js exists after build
dist/logging/index.d.ts exists after build
README documents ./logging
no unrelated release changes are being included
```

Run the repository's declared validation commands:

```bash
npm test
npm run typecheck
npm run build
npm pack --dry-run
```

Inspect the pack output and verify the intended runtime JavaScript and type
declarations for all public subpaths are present.

## Registry Preflight

Confirm npm authentication without exposing credentials:

```bash
npm whoami
```

Never print tokens or copy `.npmrc` secrets into the Completion Report.

Confirm the target version is not already published.

For the expected first logging release:

```bash
npm view @modainteract/moda-interact-shared@0.2.0 version
```

If that exact version already exists, stop. Do not attempt to overwrite or
republish it.

## Publish

After every precondition passes:

```bash
npm publish --access public
```

Do not use `--force`.

Do not change the package name.

Do not create a prerelease tag unless `moda_architect` explicitly changes the
release decision.

The intended dist-tag is the normal:

```text
latest
```

## Independent Registry Verification

A successful publish command is not sufficient by itself.

Verify:

```bash
npm view @modainteract/moda-interact-shared version
npm view @modainteract/moda-interact-shared@<version> version
```

Then install the exact published package in a clean temporary directory outside
the shared repository.

Conceptually:

```bash
tmpdir="$(mktemp -d)"
cd "$tmpdir"
npm init -y
npm install @modainteract/moda-interact-shared@<exact-version>
```

Smoke-test the public logging export:

```js
import {
  createLogger
} from "@modainteract/moda-interact-shared/logging";

const records = [];

const logger = createLogger({
  serviceName: "release-smoke-test",
  environment: "test",
  sink: (record) => records.push(record),
});

logger.info("release.smoke", {
  value: 1,
});

if (records.length !== 1) {
  throw new Error("shared logging smoke test failed");
}
```

Also import at least one **existing Shopify export actually used by current
consumers** so the release proves the existing public package surface still
works.

Use the accepted source to choose the symbol; do not invent an export name.

## Public README Verification

Verify the packed/published artifact contains the updated public README.

The README must not contain:

```text
private workspace paths
tokens
credentials
temporary architect instructions
task-review notes
```

## Git / Tag Boundary

This task authorizes npm publication.

If the repository already defines a Git tag/release convention, follow it.

If it does not, do not invent one as part of this task. Report the package
version and source commit state to `moda_architect`.

## Work Items

- [x] confirm SHARED-002 is Complete;
- [x] inspect the current package version;
- [x] inspect the accepted logging export;
- [x] apply/reconcile the supplied public README;
- [x] verify no internal/private content leaked into README;
- [x] bump `0.1.0` to `0.2.0` only if `0.1.0` remains current;
- [x] update package-lock consistently;
- [x] run `npm test`;
- [x] run `npm run typecheck`;
- [x] run `npm run build`;
- [x] run `npm pack --dry-run`;
- [x] inspect packed files and exports;
- [x] run `npm whoami`;
- [x] confirm the target version is not already published;
- [x] publish with `npm publish --access public`;
- [x] verify the registry version;
- [x] clean-install the exact published version externally;
- [x] smoke-test `./logging`;
- [x] smoke-test an existing Shopify export;
- [x] verify updated README in the package;
- [x] record exact published version;
- [x] return task with `status: review`.

## Out of Scope

- changing the accepted logger API;
- adding another logger implementation;
- changing Shopify/background/messaging/admin source;
- adding OpenTelemetry to the shared logger;
- changing event contracts merely for this release;
- publishing unrelated changes;
- setting up release CI/CD;
- creating npm credentials;
- exposing npm credentials;
- changing Render infrastructure.

## Interfaces / Contracts

Package:

```text
@modainteract/moda-interact-shared
```

New required subpath:

```text
@modainteract/moda-interact-shared/logging
```

Expected first logging release, subject to version preflight:

```text
0.2.0
```

Consumer:

```text
ARCH-002-SHOPIFY-003
```

## Dependencies

- `ARCH-002-SHARED-002`

## Enables

- `ARCH-002-SHOPIFY-003`

## Acceptance Criteria

- [x] SHARED-002 was Complete before publication;
- [x] public README accurately documents contracts and structured logging;
- [x] README explains `child()` as optional pre-filled context, not a process or
      queue abstraction;
- [x] package/package-lock versions use the approved next minor release;
- [x] tests pass;
- [x] typecheck passes;
- [x] build passes;
- [x] pack dry-run includes required public artifacts;
- [x] npm authentication succeeds without exposing credentials;
- [x] target version did not already exist before publication;
- [x] npm publication succeeds;
- [x] registry reports the exact published version;
- [x] clean external exact-version installation succeeds;
- [x] `./logging` imports from the registry-installed artifact;
- [x] logger smoke test succeeds;
- [x] existing Shopify public export smoke test succeeds;
- [x] updated README is present in the package;
- [x] no secrets/private workspace information are published;
- [x] exact published version is recorded in Completion Report.

## Completion Report

### Status

Ready for Review

### Starting Package Version

`0.1.0` (verified in `package.json` and `package-lock.json` before modification).

### Published Package Version

`0.2.0` — published to npm as `@modainteract/moda-interact-shared@0.2.0` on the `latest`
dist-tag with `--access public`.

Tarball:

```text
https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-0.2.0.tgz
shasum: 3963a516c8840be98f995aaa8ff85c317ebba765
```

### Files Changed

- `moda-interact-shared/README.md` — replaced with the architect-supplied
  public README (`SHARED-003-reference/README.md`), applied verbatim after
  reconciling factual symbol/export details against the accepted SHARED-002
  implementation (no API redesign).
- `moda-interact-shared/package.json` — `version` `0.1.0` -> `0.2.0`.
- `moda-interact-shared/package-lock.json` — root `version` and root
  `packages[""]` `version` `0.1.0` -> `0.2.0` (consistent).

No unrelated release changes were included. The `src/logging/` directory and
`tsup.config.ts` were already part of the architect-accepted SHARED-002
implementation.
- `.codex/agents/moda_shared.toml` — corrected the stale published package name in the agent description to `@modainteract/moda-interact-shared`.
- `.claude/agents/moda_shared.agent.md` — generated description kept aligned with the canonical package-name correction.


### Work Completed

- Confirmed `ARCH-002-SHARED-002` status is `complete` before publication.
- Inspected the current package version (`0.1.0`) and the accepted logging
  export (`createLogger`, `StructuredLogger`, `LogFields`, levels, `child()`,
  redaction, sink abstraction).
- Applied/reconciled the supplied public README and scanned it for private
  workspace paths, tokens, credentials and review notes (clean).
- Bumped `package.json` and `package-lock.json` to `0.2.0`.
- Ran `npm test`, `npm run typecheck`, `npm run build`, `npm pack --dry-run`;
  inspected the packed files and exports.
- Ran `npm whoami` (identity only; no credentials printed).
- Confirmed the target `0.2.0` was not already published (only `0.1.0`
  existed).
- Published with `npm publish --access public` (no `--force`, no prerelease
  tag, normal `latest` dist-tag).
- Verified the registry version and dist-tag.
- Clean-installed the exact published `0.2.0` in a temporary directory outside
  the shared repository.
- Smoke-tested `./logging` and existing Shopify exports actually used by
  current consumers (`SHOPIFY_WEBHOOK_QUEUE_CONTRACTS` from `/shopify`,
  `createPendingRecoveryCandidateJobId` from `/shopify/node`).
- Verified the updated public README is present in the installed package.
- Recorded the exact published version.

### Validation Results

- `npm test`: 13/13 pass, 0 fail, 0 skipped.
- `npm run typecheck`: exit 0 (`tsc --noEmit`).
- `npm run build`: ESM + DTS success; `dist/logging/index.js` and
  `dist/logging/index.d.ts` present.
- `npm pack --dry-run`: tarball `modainteract-moda-interact-shared-0.2.0.tgz`,
  16 files, 18.7 kB. Contains `README.md` (9.8 kB), `dist/logging/index.js`,
  `dist/logging/index.d.ts`, `dist/logging/index.js.map`, plus existing
  root `/shopify` `/shopify/node` JS and type declarations, and `package.json`
  (`version: 0.2.0`).

### Registry Verification

- `npm whoami` -> `kwadwoafriyie` (authentication succeeded; no secrets
  printed, no `.npmrc` contents copied).
- Pre-publish: `npm view @modainteract/moda-interact-shared versions` ->
  `["0.1.0"]`; `npm view @modainteract/moda-interact-shared@0.2.0 version`
  -> 404 (target did not exist).
- Post-publish: `npm view @modainteract/moda-interact-shared version` ->
  `0.2.0`; `npm view @modainteract/moda-interact-shared@0.2.0 version` ->
  `0.2.0`; `dist-tags.latest` -> `0.2.0`.

### External Consumer Smoke Test

Performed in a `mktemp -d` directory outside the shared repository:

- `npm init -y` + `npm install @modainteract/moda-interact-shared@0.2.0`
  succeeded (0 vulnerabilities); installed version confirmed `0.2.0`.
- `./logging`: the task-specified smoke snippet passed (`records.length === 1`
  with `createLogger`/custom `sink`). Additionally verified envelope identity
  (`service.namespace`, `service.name`, `deployment.environment.name`), log
  levels, optional `child()` pre-filled context, sensitive-data redaction
  (Bearer token, query token, nested `accessToken`/`secretKey`), `Error`
  serialization without stack traces, and sink-failure isolation.
- `/shopify`: `SHOPIFY_WEBHOOK_QUEUE_CONTRACTS` importable and an object.
- `/shopify/node`: `createPendingRecoveryCandidateJobId` importable,
  deterministic, non-empty string.
- Installed package contains `README.md` (9,760 bytes) documenting `./logging`
  with no private workspace paths, tokens, credentials, or review notes.

### Deviations

One non-functional coordination edit was made outside the narrow release-file
list:

```text
.codex/agents/moda_shared.toml
.claude/agents/moda_shared.agent.md
```

The package-name description was corrected from the stale
`@kodjobaah/moda-interact-shared` value to the authoritative
`@modainteract/moda-interact-shared` name.

No behavioral agent policy changed. The architect accepts this correction and
records it explicitly.

### Assumptions

- The package was still `0.1.0` when executed, so the architect-approved
  `0.2.0` target was applied (verified before modifying metadata).
- The supplied public README was applied verbatim after factual reconciliation
  and was not silently redesigned.
- The `moda_shared` agent-definition description references an older
  `@kodjobaah/moda-interact-shared` name, but the authoritative contract
  (`package.json`, ARCH-002 

## Architect Review

### Review Status

Accepted

### Review Notes

The public npm release is accepted.

Actual returned source/package metadata was inspected.

The accepted release is:

```text
@modainteract/moda-interact-shared@0.2.0
```

The public README is byte-identical to the architect-supplied SHARED-003
reference README.

`package.json` and `package-lock.json` consistently identify version `0.2.0`.

The accepted SHARED-002 logger implementation remains unchanged.

The implementing agent records successful tests, typecheck, build, pack,
publication, registry verification, clean exact-version installation and public
subpath smoke testing.

The architect review environment could not independently re-query npm because
the direct registry command timed out. No contradictory evidence was found.

### Reviewed Files

- `moda-interact-shared/README.md`
- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- `moda-interact-shared/src/logging/types.ts`
- `moda-interact-shared/src/logging/redaction.ts`
- `moda-interact-shared/src/logging/logger.ts`
- `moda-interact-shared/src/logging/index.ts`
- `moda-interact-shared/src/logging/logger.test.ts`
- `moda-interact-shared/tsup.config.ts`
- `.codex/agents/moda_shared.toml`
- `.claude/agents/moda_shared.agent.md`

### Validation Reviewed

Agent-recorded:

```text
npm test: 13/13 pass
npm run typecheck: pass
npm run build: pass
npm pack --dry-run: pass
npm publish --access public: pass
registry latest: 0.2.0
clean external install: pass
./logging smoke test: pass
/shopify smoke test: pass
/shopify/node smoke test: pass
```

Source-level architect verification:

```text
package.json version: 0.2.0
package-lock top/root version: 0.2.0
README == SHARED-003 reference README
logger source == accepted SHARED-002 reference source
```

### Architecture Conformance

Accepted.

The versioned npm artifact is now the approved production shared-library
boundary for the logging capability.

### Follow-up

`ARCH-002-SHOPIFY-003` is Ready.

It must consume:

```text
@modainteract/moda-interact-shared@0.2.0
```

and replace its local generic structured logger with:

```text
@modainteract/moda-interact-shared/logging
```

while retaining Shopify-specific OpenTelemetry locally.

