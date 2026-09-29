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
status: pending
priority: 21
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-SHARED-001
enables: []
created: 2026-09-29
updated: 2026-09-29
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

- [ ] Verify SHARED-001 is Complete and architect-accepted.
- [ ] Record the accepted SHARED-001 implementation SHA.
- [ ] Verify checked-in package version equals current npm registry version.
- [ ] Calculate exactly the next patch version.
- [ ] Update release/version metadata only.
- [ ] Publish with the normal npm public-package command.
- [ ] Verify exact version, integrity and tarball from npm.
- [ ] Verify the package contains all required ARCH-023 built entrypoints/declarations.
- [ ] Clean-install the exact published revision in a temporary consumer.
- [ ] Verify all four required public imports and representative exports.
- [ ] Confirm no implementation or consumer source changed.
- [ ] Record publication evidence.
- [ ] Return only this publication task for architect review.

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

None are materialised yet.

After this task is accepted Complete, `moda_architect` will attach the exact published revision to the later ARCH-023 Admin, Shopify, Background and Commerce consumer tasks as those tasks are defined.

## Acceptance Criteria

- [ ] SHARED-001 was Complete and architect-accepted before publication.
- [ ] Checked-in version matched the npm registry baseline before the bump.
- [ ] Exactly one patch version was applied.
- [ ] `npm publish --access public` succeeded.
- [ ] Exact new version is visible from the intended npm registry.
- [ ] Registry `dist.integrity` and tarball evidence are recorded.
- [ ] Published package contains all required ARCH-023 JS and declaration entrypoints.
- [ ] Clean temporary install of the exact version succeeds.
- [ ] All required public imports work from the clean consumer.
- [ ] Representative ARCH-023 exports have the expected runtime behavior.
- [ ] Only release/version metadata changed in the repository during this task.
- [ ] No consumer repository was modified.
- [ ] Published version and accepted implementation SHA are recorded for downstream consumers.

## Validation

Publication validation only:

- [ ] prerequisite acceptance verified
- [ ] package/registry baseline version check passed
- [ ] publication command succeeded
- [ ] exact registry revision verified
- [ ] package-content verification passed
- [ ] clean-install/import verification passed
- [ ] `git diff --check`
- [ ] changed-file inspection proves no implementation-source changes

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

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

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

Pending.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
