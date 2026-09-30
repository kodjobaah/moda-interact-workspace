---
id: ARCH-023-SHARED-002
architecture_id: ARCH-023
title: Publish accepted ARCH-023 Shared package
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 21
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-023-SHARED-001
enables:
  - ARCH-023-ADMIN-001
  - ARCH-023-BACKGROUND-001
  - ARCH-023-COMMERCE-001
  - ARCH-023-COMMERCE-003
  - ARCH-023-SHOPIFY-001
  - ARCH-023-SHOPIFY-002
  - ARCH-023-SHOPIFY-004
created: 2026-09-29
updated: 2026-09-30
---

# Publish accepted ARCH-023 Shared package

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator:

`moda_architect`

## Objective

Publish exactly one compatible `@modainteract/moda-interact-shared` patch release containing the architect-accepted `ARCH-023-SHARED-001` implementation, verify the exact registry revision and clean consumer imports, record the published version/integrity, and stop without modifying consumer repositories.

## Context

`ARCH-023-SHARED-001` owns all implementation and implementation validation.

This task is a release gate only.

ARCH-023 consumers must depend on an exact published Shared revision rather than source-worktree state or duplicated local contracts.

## Scope

Only release-specific work is authorized:

```text
verify SHARED-001 is Complete and architect-accepted
verify current checked-in package version against npm registry
compute the next compatible patch version
update package.json/package-lock release version metadata only
publish the package
verify exact published version + integrity
clean-install the published version
verify ARCH-023 public subpaths/exports
record publication evidence
```

## Out of Scope

- Any implementation-source change.
- Fixing SHARED-001 code.
- Adding/changing tests.
- Refactoring.
- Rerunning implementation tests, lint or typecheck merely to revalidate accepted source.
- Database changes.
- Consumer package updates.
- Admin/Shopify/Background/Commerce implementation.
- Creating downstream task definitions.
- Publishing a minor or major version.
- Publishing more than once to work around an implementation defect.

## Requirements

### R1. Verify prerequisite acceptance before release

Before modifying release metadata, verify:

```text
ARCH-023-SHARED-001.status = complete
ARCH-023-SHARED-001 Architect Review = Accepted
```

Record the accepted implementation commit SHA in this task's Completion Report.

If SHARED-001 is not Complete and accepted, STOP without publishing.

### R2. Establish the release baseline deterministically

Read:

```text
moda-interact-shared/package.json version
```

Query the intended npm registry:

```bash
npm view @modainteract/moda-interact-shared version --registry=https://registry.npmjs.org
```

The checked-in package version MUST equal the currently published registry version before this task performs its bump.

If they differ:

```text
STOP
report version/release baseline conflict to moda_architect
do not guess which version wins
do not publish
```

### R3. Bump exactly one patch version

Using semantic versioning:

```text
X.Y.Z -> X.Y.(Z+1)
```

Update only release/version metadata required by the repository's normal npm publication process.

Expected normal changed files:

```text
package.json
package-lock.json
```

Do not change implementation source.

Do not choose a minor or major version.

### R4. Publication command

Publish using the existing public-package convention:

```bash
npm publish --access public
```

The package's existing `prepack` build is allowed because it is part of the publication mechanism.

Do not manually run implementation tests/lint/typecheck/build as a second validation pass.

If `npm publish` reveals an implementation defect requiring source changes:

```text
STOP
do not patch source in this task
return the defect to moda_architect
```

### R5. Verify exact registry revision

After successful publication, verify the exact new version:

```bash
npm view @modainteract/moda-interact-shared@<NEW_VERSION> \
  version dist.integrity dist.tarball \
  --json \
  --registry=https://registry.npmjs.org
```

Record:

```text
version
dist.integrity
dist.tarball
```

in the Completion Report.

The registry version must exactly equal the version written to `package.json`.

### R6. Verify package contents

Use:

```bash
npm pack --dry-run
```

or the publication output/tarball metadata to verify the published package contains built JavaScript and declarations for:

```text
dist/internationalization.js
dist/internationalization.d.ts

dist/merchant-knowledge.js
dist/merchant-knowledge.d.ts

dist/merchant-knowledge/node.js
dist/merchant-knowledge/node.d.ts

dist/commerce/runner/index.js
dist/commerce/runner/index.d.ts
```

Do not accept publication if one of those ARCH-023 entrypoints is absent.

### R7. Clean-install the exact published revision

Create a temporary empty consumer directory outside the repository worktree.

Install exactly:

```text
@modainteract/moda-interact-shared@<NEW_VERSION>
```

from the intended npm registry.

The clean consumer must not resolve the local repository package through workspace linking.

### R8. Verify exact public imports from the clean install

From the clean consumer, import exactly:

```text
@modainteract/moda-interact-shared/internationalization
@modainteract/moda-interact-shared/merchant-knowledge
@modainteract/moda-interact-shared/merchant-knowledge/node
@modainteract/moda-interact-shared/commerce/runner
```

Assert at least:

```text
MODA_SUPPORTED_LANGUAGE_TAGS exists
resolveModaConfigurationLocale("zh-HK") === "zh-Hant"

MerchantKnowledgeFeatureConfigurationSchema exists
MerchantKnowledgeProcessSourceRevisionJobSchema exists

createMerchantKnowledgeProcessJobId({
  shopId: "shop-1",
  sourceRevisionId: "revision-1",
  generation: 1
})
matches ^merchant-knowledge-process-[0-9a-f]{64}$

RUNTIME_DATA_AUTHORITY_INSTRUCTION exists
PLATFORM_INSTRUCTIONS[0] === RUNTIME_DATA_AUTHORITY_INSTRUCTION
```

This is publication mechanics verification, not a rerun of the implementation test suite.

### R9. No consumer changes

Do not modify:

```text
moda-interact
moda-interact-admin
moda-interact-background
moda-interact-commerce
moda-interact-database
moda-interact-gateway
moda-interact-system-test
```

Consumer adoption belongs to later ARCH-023 tasks.

### R10. Record the publication result for downstream task authoring

The Completion Report must contain a clearly copyable block:

```text
Published Shared revision:
@modainteract/moda-interact-shared@<NEW_VERSION>

Integrity:
<dist.integrity>

Accepted SHARED-001 implementation:
<commit SHA>
```

Later consumer tasks will be defined to adopt that exact published revision.

Do not update those future tasks from this publication task.

## Work Items

- [x] Verify SHARED-001 is Complete and architect-accepted.
- [x] Record the accepted SHARED-001 implementation SHA.
- [x] Verify checked-in package version equals current npm registry version.
- [x] Calculate exactly the next patch version.
- [x] Update release/version metadata only.
- [x] Publish with the normal npm public-package command.
- [x] Verify exact version, integrity and tarball from npm.
- [x] Verify the package contains all required ARCH-023 built entrypoints/declarations.
- [x] Clean-install the exact published revision in a temporary consumer.
- [x] Verify all four required public imports and representative exports.
- [x] Confirm no implementation or consumer source changed.
- [x] Record publication attempt and verification evidence.
- [x] Return only this publication task for architect review.

## Interfaces / Contracts

This task publishes the implementation accepted under:

```text
ARCH-023-SHARED-001
```

The published package is:

```text
@modainteract/moda-interact-shared@<NEW_VERSION>
```

Required ARCH-023 public subpaths:

```text
@modainteract/moda-interact-shared/internationalization
@modainteract/moda-interact-shared/merchant-knowledge
@modainteract/moda-interact-shared/merchant-knowledge/node
@modainteract/moda-interact-shared/commerce/runner
```

No new source contract is defined by this publication task.

## Dependencies

- `ARCH-023-SHARED-001`

The prerequisite must be Complete and architect-accepted.

## Enables

The exact published Shared revision is now fixed as:

```text
@modainteract/moda-interact-shared@1.0.1
```

Direct consumer tasks materialised under ARCH-023 are:

- `ARCH-023-ADMIN-001`
- `ARCH-023-BACKGROUND-001`
- `ARCH-023-COMMERCE-001`
- `ARCH-023-COMMERCE-003`
- `ARCH-023-SHOPIFY-001`
- `ARCH-023-SHOPIFY-002`
- `ARCH-023-SHOPIFY-004`

Only tasks whose complete dependency sets are satisfied become Ready when this publication task is accepted.

## Acceptance Criteria

- [x] SHARED-001 was Complete and architect-accepted before publication.
- [x] Checked-in version matched the npm registry baseline before the bump.
- [x] Exactly one patch version was applied.
- [x] `npm publish --access public` succeeded.
- [x] Exact new version is visible from the intended npm registry.
- [x] Registry `dist.integrity` and tarball evidence are recorded.
- [x] Published package contains all required ARCH-023 JS and declaration entrypoints.
- [x] Clean temporary install of the exact version succeeds.
- [x] All required public imports work from the clean consumer.
- [x] Representative ARCH-023 exports have the expected runtime behavior.
- [x] Only release/version metadata changed in the repository during this task.
- [x] No consumer repository was modified.
- [x] Published version and accepted implementation SHA are recorded for downstream consumers.

## Validation

Publication validation only:

- [x] prerequisite acceptance verified
- [x] package/registry baseline version check passed
- [x] publication command succeeded
- [x] exact registry revision verified
- [x] package-content verification passed
- [x] clean-install/import verification passed
- [x] `git diff --check` — passed.
- [x] changed-file inspection proves no implementation-source changes.

Do NOT rerun:

```text
npm test
npm run typecheck
lint
implementation integration tests
```

merely to revalidate SHARED-001.

The `prepack` build invoked by publication is part of release mechanics and is permitted.

## Stop Condition

After publication validation is complete:

1. finish the Completion Report;
2. set the task to `review`;
3. return control to `moda_architect`;
4. STOP.

Do not begin any Admin, Shopify, Background, Commerce, Gateway or system-test task.

## Implementation Notes

This task is intentionally small.

If publication uncovers a code/contract problem, do not repair it here. Return the problem to `moda_architect` so SHARED-001 can be reopened or a bounded correction can be defined if genuinely necessary.

Do not infer a release version from this task definition. The exact version is determined from the checked-in/registry baseline at execution time and must be exactly one patch increment.

## Completion Report

### Status

Ready for Architect Review (`review`).

### Files Changed

Implementation task worktree: only `package.json` and `package-lock.json`, with the package version changed from `1.0.0` to `1.0.1`. No implementation source or consumer repository changed. This Completion Report is the only parent-worktree change beyond the launcher claim.

### Work Completed

Verified `ARCH-023-SHARED-001` is Complete and Architect Review says “Accepted — Attempt 2”; accepted implementation commit: `c96b7eb8eaaae14133ab174de80e130c8551f366`. Checked-in version `1.0.0` matched npm's current version `1.0.0`; selected exactly patch `1.0.1`. Updated and committed only release version metadata (`9172f8f8b3c0b84c50c7dfd4bd704ad813d3ff35`). The first publish invocation stopped before upload because this fresh worktree lacked `tsup`; after `npm ci`, one successful `npm publish --access public` invocation completed its prepack ESM/declaration build and published `@modainteract/moda-interact-shared@1.0.1`. No second publish was attempted.

### Validation Results

Pre-bump registry baseline passed (`npm view ... version` returned `1.0.0`). Registry lookup confirmed `1.0.1` was absent before publication. After a short registry processing delay, exact `npm view @modainteract/moda-interact-shared@1.0.1 version dist.integrity dist.tarball --json --registry=https://registry.npmjs.org` returned:

```text
version: 1.0.1
dist.integrity: sha512-xwVRw1rZWZIlfvrnml+psA5roRz+qMoTl7Znob1myNA1PTXIuHYX4lQHCof8Ef2F1QElrvi09jKstOc6QHdcKg==
dist.tarball: https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-1.0.1.tgz
```

The successful publish output reported shasum `c381787626b576d17be14252fb76daf298d94cb6` and 81 files. `npm pack --dry-run` confirmed all required JS and declaration paths: `dist/internationalization.js`/`.d.ts`, `dist/merchant-knowledge.js`/`.d.ts`, `dist/merchant-knowledge/node.js`/`.d.ts`, and `dist/commerce/runner/index.js`/`.d.ts`.

Installed the exact `@modainteract/moda-interact-shared@1.0.1` into an empty temporary consumer outside the repository (`/tmp/moda-shared-1.0.1-consumer.pjve2C`). All four required subpaths imported successfully. Assertions passed for `MODA_SUPPORTED_LANGUAGE_TAGS`, `resolveModaConfigurationLocale("zh-HK") === "zh-Hant"`, Merchant Knowledge schema exports, the exact job-ID prefix/64-lowercase-hex format, and `PLATFORM_INSTRUCTIONS[0] === RUNTIME_DATA_AUTHORITY_INSTRUCTION`. `git diff --check` passed.

### Deviations

The first publish attempt failed in `prepack` before upload because dependencies were absent (`sh: tsup: command not found`). `npm ci` restored the lockfile-pinned dependencies without tracked dependency changes; it reported one low-severity audit advisory and install-script approval warnings. npm initially returned 404 while processing the successful publish, then exposed the exact version and tarball; the clean consumer install and imports passed. No source changes or duplicate publish were made.

### Assumptions

The accepted SHARED-001 implementation was already merged to `origin/main` before SHARED-002 preparation; the publication branch contains it as an ancestor. Registry processing delay was transient and did not require another publish.

### Unresolved Issues

None. npm emitted dependency install-script approval warnings for the temporary consumer install; all required imports and runtime assertions passed.

### Architectural Concerns

None. Release scope remains limited to version metadata; no consumer repository was changed.

### Execution Provenance

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent task worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-SHARED-002
parent branch: task/ARCH-023-SHARED-002
implementation repository: moda-interact-shared
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-SHARED-002
implementation branch: task/ARCH-023-SHARED-002
parent remote task-branch fast-forward: not-needed
parent origin/main: already-current
implementation remote task-branch fast-forward: not-needed
implementation origin/main: already-current
recursive submodule sync/update: passed; ready, no entries
launcher claim commit: 5a58239abe6eaf93d73cecf059fedb2a03d15d20 (pushed)
```

The launcher reported clean synchronization gates, dependency `ARCH-023-SHARED-001` complete, and created both canonical task worktrees. Implementation task commit `9172f8f8b3c0b84c50c7dfd4bd704ad813d3ff35` is pushed to `origin/task/ARCH-023-SHARED-002`. Package version `1.0.1` and the accepted SHARED-001 implementation SHA are recorded above for downstream task authoring.

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

ARCH-023-SHARED-002 conforms to the publication-only release-gate contract.

- `ARCH-023-SHARED-001` was Complete / Architect-Accepted at Attempt 2 before publication; the accepted implementation identity recorded by this task is `c96b7eb8eaaae14133ab174de80e130c8551f366`.
- The release metadata advances exactly one patch version, `1.0.0 -> 1.0.1`.
- Independent review comparison against the accepted SHARED-001 snapshot found no Shared source drift. `package.json` changes only the package version, and `package-lock.json` changes only the root/package version fields.
- The first `npm publish --access public` invocation stopped inside `prepack` before upload because the fresh worktree did not yet contain `tsup`. After lockfile-pinned `npm ci`, one successful publish completed; no second package upload/republish was used to mask an implementation defect.
- The Completion Report records the exact npm registry version, integrity, tarball, package-content proof and a clean temporary-consumer install of the published revision.
- No consumer repository was modified during the publication task.

Canonical ARCH-023 Shared release identity:

```text
Published Shared revision:
@modainteract/moda-interact-shared@1.0.1

Integrity:
sha512-xwVRw1rZWZIlfvrnml+psA5roRz+qMoTl7Znob1myNA1PTXIuHYX4lQHCof8Ef2F1QElrvi09jKstOc6QHdcKg==

Accepted SHARED-001 implementation:
c96b7eb8eaaae14133ab174de80e130c8551f366

Release metadata commit:
9172f8f8b3c0b84c50c7dfd4bd704ad813d3ff35
```

### Reviewed Files

- `docs/decisions/shared/ARCH-023/SHARED-002-publish-arch023-shared-package.md`
- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- accepted SHARED-001 Shared source snapshot
- ARCH-023 Shared/Admin/Background/Commerce/Shopify dependency indexes and direct consumer task definitions

### Validation Reviewed

Publication review intentionally did not rerun SHARED-001 implementation tests, lint, typecheck or build.

Reviewed publication evidence:

- prerequisite SHARED-001: Complete / Accepted Attempt 2;
- pre-bump checked-in/registry baseline: `1.0.0`;
- release version: `1.0.1`;
- registry integrity: `sha512-xwVRw1rZWZIlfvrnml+psA5roRz+qMoTl7Znob1myNA1PTXIuHYX4lQHCof8Ef2F1QElrvi09jKstOc6QHdcKg==`;
- registry tarball: `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-1.0.1.tgz`;
- successful publication output recorded 81 package files and SHA-1 `c381787626b576d17be14252fb76daf298d94cb6`;
- package-content verification recorded all required ARCH-023 JavaScript/declaration entrypoints;
- clean external consumer installed exactly `@modainteract/moda-interact-shared@1.0.1` and passed all four required public-subpath imports plus the required runtime assertions;
- `git diff --check`: PASS;
- implementation-source comparison: PASS, no source changes beyond authorized release metadata.

Direct npm registry retrieval was unavailable from this architect review environment. Consistent with the cross-environment review policy, the exact registry identity is therefore accepted from the durable publication and clean-install evidence recorded in the Completion Report; no contradictory evidence was found.

### Architecture Conformance

Conforms. The architect-accepted ARCH-023 Shared contract/runtime trust implementation is now consumable through the canonical exact package revision `@modainteract/moda-interact-shared@1.0.1`. Publication and consumer integration remain separate boundaries as required.

### Follow-up

Mark `ARCH-023-SHARED-002` Complete and pin ARCH-023 consumers to exactly `@modainteract/moda-interact-shared@1.0.1`.

The dependency graph now makes these tasks Ready:

```text
ARCH-023-ADMIN-001
ARCH-023-BACKGROUND-001
ARCH-023-COMMERCE-001
ARCH-023-SHOPIFY-001
ARCH-023-SHOPIFY-002
```

`ARCH-023-ADMIN-002` was already Ready and remains Ready. `ARCH-023-COMMERCE-003` and `ARCH-023-SHOPIFY-004` are pinned to the same Shared revision but remain Pending until their other declared dependencies are Complete.
