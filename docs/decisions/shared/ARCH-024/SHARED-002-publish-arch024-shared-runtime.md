---
id: ARCH-024-SHARED-002
architecture_id: ARCH-024
title: Publish ARCH-024 Shared model and Commerce turn runtime
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 21
executor: copilot
In Progress — npm accepted publication; registry verification pending
attempt: 1
depends_on:
  - ARCH-024-SHARED-001
- `moda-interact-shared/package.json` — version `1.0.1` to `1.1.0`
- `moda-interact-shared/package-lock.json` — root version metadata `1.0.1` to `1.1.0`
  - ARCH-024-ADMIN-001
  - ARCH-024-ADMIN-004
  - ARCH-024-COMMERCE-002
- Confirmed SHARED-001 is `Complete / Accepted — Attempt 2`; accepted source commit `c4627f1` is an ancestor of prepared source head `eaf62bc`. The working tree was clean before release mutation and the implementation-source tree has no diff from the accepted baseline.
- Recorded synchronized starting version `1.0.1`; computed and applied exactly one minor increment to `1.1.0` using `npm version minor --no-git-tag-version` (no tag created).
- Installed the exact lockfile dependencies with `npm ci` because the prepared worktree initially lacked `tsup`.
- `npm pack --dry-run` succeeded after the normal `prepack` build. JSON inventory assertions passed for model/model-node JS and declarations, runner JS/declarations, and existing Commerce/logging JS and declarations.
- Ran the specified `npm publish --access public --registry=https://registry.npmjs.org/`. npm accepted `@modainteract/moda-interact-shared@1.1.0` and returned success. Publish output shasum: `923e5b71942bd17e2d2537820f884c9edc3cdeaf`.
- Committed and pushed only release metadata as Shared commit `3480905` on `origin/task/ARCH-024-SHARED-002`.
- No implementation source, consumer code, or downstream task was changed.
created: 2026-10-01
updated: 2026-10-01
---
- Prerequisite accepted source/status: passed; SHARED-001 report is `Complete / Accepted — Attempt 2`, source commit `c4627f1` is included in `eaf62bc`.
- Starting version `1.0.1`; target version `1.1.0`; both package and lockfile root metadata match after versioning.
- Release diff before commit contained only `package.json` and `package-lock.json`; `git diff --check` passed.
- `npm pack --dry-run` passed; the required public entrypoint artifact list is present.
- `npm publish --access public --registry=https://registry.npmjs.org/` returned success and npm reported `+ @modainteract/moda-interact-shared@1.1.0`.
- Registry verification is currently blocked by npm propagation: `npm view @modainteract/moda-interact-shared@1.1.0 version dist.tarball dist.shasum dist.integrity --json` returned E404 on two attempts; `npm view @modainteract/moda-interact-shared dist-tags --json` still reports `latest: 1.0.1`.
- Clean external consumer installation of exact `@modainteract/moda-interact-shared@1.1.0` returned `ETARGET` because the registry does not yet expose the version. The disposable directory was removed automatically. Required import verification is therefore pending.
- `dist.integrity` and registry `dist.tarball` have not yet been obtainable; the publish CLI's integrity display was truncated and is not recorded as registry evidence.
# Publish ARCH-024 Shared model and Commerce turn runtime

## Architecture
Registry visibility has not caught up with npm's successful publish response. No second publish attempt will be made for this immutable version.
Architecture ID:

`ARCH-024`
The successful npm publish response means npm accepted the immutable `1.1.0` version; the subsequent E404/ETARGET responses are temporary registry propagation, consistent with npm's publish output warning that processing may take a few minutes.
Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`
Await exact-version npm registry metadata and a successful exact-version clean-consumer install/import. Do not retry publication; resume with registry verification only.
Coordinator:

`moda_architect`
None. Task remains `in_progress`; do not hand off for review until registry metadata and clean-consumer verification pass.

### Prepared Execution Evidence

- Launcher prepared and claimed Attempt 1 for `copilot`; dependency gate passed because `ARCH-024-SHARED-001` is complete. Claim commit `50c4d1fff1a127c97afe2968faea74c806835ea7` was committed and pushed.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-SHARED-002`, `task/ARCH-024-SHARED-002`; prepared head `fef30bcd29cfbcd01ee9aea512196f688633c30f`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-SHARED-002`, `task/ARCH-024-SHARED-002`; prepared head `eaf62bc2e4f7f2e7833c325345108282da04a2e5`.
- Parent and implementation task refs did not require fast-forward; `origin/main` was already incorporated. Recursive submodule sync/update passed; the submodule entry list is empty.
- Release metadata commit `3480905` is pushed to `origin/task/ARCH-024-SHARED-002`. No main merge or consumer changes were made.
## Objective

Publish the architect-accepted ARCH-024-SHARED-001 combined implementation as the next backward-compatible minor release of `@modainteract/moda-interact-shared`, verify the exact public package identity and entrypoints, then stop before any consumer integration.
Publication was accepted by npm, but registry metadata and exact-version consumer imports remain unavailable at the time of this report. Keep the task in progress and resume verification; never republish `1.1.0`.
## Context

ARCH-024-SHARED-001 contains the accepted model contracts/OpenRouter client, modular LangGraph-backed `runCommerceTurn`, guardrails and canonical structured runner logging. Admin, Commerce and Background must consume one canonical published Shared version; they must not copy these contracts locally or depend on unpublished task-branch source.

This is a publication gate only. Implementation correctness is established by SHARED-001 and its Architect Review.

At the time this task was authored, `moda-interact-shared/package.json` is `1.0.1`. Adding new backward-compatible public entrypoints/capabilities is a **minor** SemVer change under the repository README. If no intervening Shared release occurs, the target is therefore `1.1.0`.

If the package version has legitimately advanced before this publication task is claimed, compute the next minor from the synchronized current package version rather than forcing `1.1.0`; record both the starting and published versions in the Completion Report.

## Scope

- Verify ARCH-024-SHARED-001 is `complete` with an Accepted Architect Review.
- Confirm the prepared Shared task branch contains exactly the architect-accepted implementation.
- Determine the synchronized starting package version.
- Apply exactly one SemVer **minor** version increment.
- Update release metadata required by the package manager (`package.json` and lockfile only unless the repository's normal version command deterministically changes another release-metadata file).
- Inspect the publish artifact.
- Publish the package to the public npm registry.
- Verify the exact published package version and integrity metadata.
- Verify the model, model/node, runner and logging public entrypoints from a clean external consumer directory using the exact published version.
- Record the published version for later ARCH-024 consumer tasks.

## Out of Scope

- Any implementation-source change.
- Contract/schema changes.
- LangChain/OpenRouter dependency changes except release metadata already accepted in SHARED-001.
- Unit/integration test reruns.
- Typecheck reruns.
- Production-build reruns solely to revalidate SHARED-001. The package's normal `prepack` build is allowed because it is part of publication mechanics.
- Database changes.
- Admin, Commerce, Background or Gateway dependency updates.
- Consumer integration.
- OpenRouter credentials or live OpenRouter calls.

## Requirements

### R1 — Publication cannot start before accepted implementation

Before any version or publication mutation, verify all of the following:

```text
ARCH-024-SHARED-001 status: complete
ARCH-024-SHARED-001 Architect Review: Accepted
Shared task branch contains the accepted source
working tree contains no unrelated changes
```

If any condition is false, stop without modifying release metadata.

### R2 — Release increment is exactly one minor version

Read the synchronized starting version from:

```text
moda-interact-shared/package.json
```

Compute:

```text
nextVersion = semver.inc(startingVersion, "minor")
```

The release must use exactly `nextVersion`.

Examples:

```text
1.0.1 -> 1.1.0
1.1.3 -> 1.2.0
2.4.0 -> 2.5.0
```

Do not choose a patch release because ARCH-024 adds new public package capabilities. Do not choose a major release because SHARED-001 is defined to be backward-compatible with existing public entrypoints.

Use the repository/package-manager mechanism that updates package and lockfile consistently, for example:

```bash
npm version minor --no-git-tag-version
```

Do not create a Git tag in this task.

### R3 — Release diff is metadata only

After versioning and before publication, the implementation-source tree must remain identical to the accepted SHARED-001 source.

Normally the only changed release files are:

```text
package.json
package-lock.json
```

If any `src/**`, `scripts/**`, build-config or documentation file changes after the accepted SHARED-001 implementation baseline, stop and return the publication problem to `moda_architect`.

### R4 — Inspect the exact publish artifact before publishing

Run:

```bash
npm pack --dry-run
```

The artifact must contain JavaScript and declarations for the model runtime and modular Commerce runner:

```text
dist/commerce/model/index.js
dist/commerce/model/index.d.ts
dist/commerce/model/node.js
dist/commerce/model/node.d.ts
dist/commerce/runner/index.js
dist/commerce/runner/index.d.ts
```

and existing published Commerce/logging entrypoints must remain present.

Do not publish if either model entrypoint or the Commerce runner entrypoint is absent.

### R5 — Publish once to the intended public registry

Use exactly:

```bash
npm publish --access public --registry=https://registry.npmjs.org/
```

The package's normal `prepack` script may build as part of this command. Do not separately rerun SHARED-001 validation merely because `prepack` builds the package.

If publication fails before npm accepts the package, correct only an environment/release-mechanics problem that does not require implementation-source changes and retry the same intended version where npm permits it.

If npm has accepted the version, never attempt to overwrite/re-publish the same immutable version. Stop and return any subsequent issue to `moda_architect`.

### R6 — Verify exact registry identity

After publication, query the public npm registry for the exact version and record at least:

```text
package name
published version
dist.tarball
dist.shasum
dist.integrity
dist-tags/latest
```

The exact version must be visible as:

```text
@modainteract/moda-interact-shared@<nextVersion>
```

Do not treat the local package.json version alone as publication evidence.

### R7 — Verify the exact published package from a clean consumer directory

Create a disposable directory outside `moda-interact-shared` and outside any repository `node_modules` resolution path. Initialize a minimal npm package and install exactly:

```text
@modainteract/moda-interact-shared@<nextVersion>
```

Then run a Node ESM process that imports:

```text
@modainteract/moda-interact-shared/commerce/model
@modainteract/moda-interact-shared/commerce/model/node
@modainteract/moda-interact-shared/commerce/runner
@modainteract/moda-interact-shared/logging
```

The check must prove at minimum:

```text
CommerceModelCatalogueEntrySchema is present
CommerceModelConfigurationSchema is present
createOpenRouterModelId is present
OpenRouterModelClient is present
runCommerceTurn is present
runnerVersion is present
createLogger is present
```

Do not invoke OpenRouter and do not require an OpenRouter credential for this import test.

Remove the disposable consumer directory after evidence is recorded.

### R8 — Record the publication identity for consumers

The Completion Report must state the exact version that later ARCH-024 Admin/Commerce/Background tasks must install.

Consumer tasks must use that exact published version rather than:

```text
workspace source
file: dependency
link: dependency
floating latest
unpublished task branch
```

## Work Items

- [ ] Verify SHARED-001 is Complete/Accepted and source is clean.
- [ ] Read and record the synchronized starting package version.
- [ ] Compute/apply exactly one minor SemVer increment.
- [ ] Confirm the release diff contains release metadata only.
- [ ] Run `npm pack --dry-run` and verify the ARCH-024 model and runner public entrypoints/declarations.
- [ ] Publish once to the public npm registry.
- [ ] Verify exact registry version, tarball, shasum, integrity and `latest` tag.
- [ ] Install the exact published version in a clean disposable consumer and import model, model/node, runner and logging entrypoints.
- [ ] Record the exact published version for downstream tasks.
- [ ] Clean the disposable consumer directory and set the task to review.

## Interfaces / Contracts

Publishes:

```text
@modainteract/moda-interact-shared
```

including the accepted ARCH-024 public paths:

```text
@modainteract/moda-interact-shared/commerce/model
@modainteract/moda-interact-shared/commerce/model/node
@modainteract/moda-interact-shared/commerce/runner
@modainteract/moda-interact-shared/logging
```

No new contract is defined by this publication task.

## Dependencies

- `ARCH-024-SHARED-001`

## Enables

The direct ARCH-024 frontier tasks listed in YAML `enables` depend on this SHARED-002 publication gate and must install the exact version recorded here. Later consumers such as `ARCH-024-COMMERCE-007` may also declare SHARED-002 as a hard dependency, but are not listed as directly enabled when additional prerequisite tasks still gate their execution.

## Acceptance Criteria

- [ ] SHARED-001 was Complete and Accepted before any release mutation.
- [ ] The package version advanced by exactly one minor SemVer increment from the synchronized starting version.
- [ ] Only authorised release metadata changed after the accepted SHARED-001 implementation baseline.
- [ ] `npm pack --dry-run` contains model, model/node and runner JavaScript/declarations and retains the existing logging entrypoint.
- [ ] Publication to the public npm registry succeeded.
- [ ] The exact published version is visible in registry metadata.
- [ ] `dist.tarball`, `dist.shasum` and `dist.integrity` are recorded.
- [ ] A clean external consumer installed the exact published version and successfully imported model, model/node, runner and logging entrypoints.
- [ ] No implementation source, Admin, Commerce or Background consumer code was changed by this publication task.
- [ ] The exact version required by later ARCH-024 consumers is recorded in the Completion Report.

## Validation

Publication validation only:

```bash
# prerequisite/source evidence
# use repository/Git commands appropriate to the prepared task branch

npm pack --dry-run

npm publish --access public --registry=https://registry.npmjs.org/

npm view "@modainteract/moda-interact-shared@<nextVersion>" \
  version dist.tarball dist.shasum dist.integrity dist-tags --json

git diff --check
```

Also perform the R7 clean-consumer exact-version import test.

Do **not** rerun SHARED-001 unit tests, typecheck or explicit production build as publication validation.

Required publication evidence:

- [ ] SHARED-001 prerequisite acceptance confirmed
- [ ] starting version recorded
- [ ] exact minor target version recorded
- [ ] publish artifact inspected
- [ ] publication command succeeded
- [ ] exact registry metadata recorded
- [ ] clean external exact-version imports passed
- [ ] release diff contains no unauthorised implementation source changes
- [ ] `git diff --check` passes

## Stop Condition

After the package is published and all R6/R7 evidence is recorded, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP.

Do not update Admin, Commerce, Background, Gateway or any other consumer dependency.

## Implementation Notes

This task is intentionally release-only. If publication reveals that accepted SHARED-001 source must change, do not fix it here. Stop and return the implementation issue to `moda_architect` so the owning implementation task (SHARED-001) can be reopened/corrected under the normal review protocol.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not Run

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
