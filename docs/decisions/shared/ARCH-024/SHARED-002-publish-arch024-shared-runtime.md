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
status: complete
priority: 21
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-024-SHARED-001
enables:
  - ARCH-024-ADMIN-001
  - ARCH-024-ADMIN-004
  - ARCH-024-COMMERCE-002
  - ARCH-024-BACKGROUND-001
created: 2026-10-01
updated: 2026-10-01
---

# Publish ARCH-024 Shared model and Commerce turn runtime

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Publish the architect-accepted ARCH-024-SHARED-001 combined implementation as the next backward-compatible minor release of `@modainteract/moda-interact-shared`, verify the exact public package identity and entrypoints, then stop before any consumer integration.

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

- [x] Verify SHARED-001 is Complete/Accepted and source is clean.
- [x] Read and record the synchronized starting package version.
- [x] Compute/apply exactly one minor SemVer increment.
- [x] Confirm the release diff contains release metadata only.
- [x] Run `npm pack --dry-run` and verify the ARCH-024 model and runner public entrypoints/declarations.
- [x] Publish once to the public npm registry.
- [x] Verify exact registry version, tarball, shasum, integrity and `latest` tag.
- [x] Install the exact published version in a clean disposable consumer and import model, model/node, runner and logging entrypoints.
- [x] Record the exact published version for downstream tasks.
- [x] Clean the disposable consumer directory and set the task to review.

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

- [x] SHARED-001 was Complete and Accepted before any release mutation.
- [x] The package version advanced by exactly one minor SemVer increment from the synchronized starting version.
- [x] Only authorised release metadata changed after the accepted SHARED-001 implementation baseline.
- [x] `npm pack --dry-run` contains model, model/node and runner JavaScript/declarations and retains the existing logging entrypoint.
- [x] Publication to the public npm registry succeeded.
- [x] The exact published version is visible in registry metadata.
- [x] `dist.tarball`, `dist.shasum` and `dist.integrity` are recorded.
- [x] A clean external consumer installed the exact published version and successfully imported model, model/node, runner and logging entrypoints.
- [x] No implementation source, Admin, Commerce or Background consumer code was changed by this publication task.
- [x] The exact version required by later ARCH-024 consumers is recorded in the Completion Report.

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

- [x] SHARED-001 prerequisite acceptance confirmed
- [x] starting version recorded
- [x] exact minor target version recorded
- [x] publish artifact inspected
- [x] publication command succeeded
- [x] exact registry metadata recorded
- [x] clean external exact-version imports passed
- [x] release diff contains no unauthorised implementation source changes
- [x] `git diff --check` passes

## Stop Condition

After the package is published and all R6/R7 evidence is recorded, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP.

Do not update Admin, Commerce, Background, Gateway or any other consumer dependency.

## Implementation Notes

This task is intentionally release-only. If publication reveals that accepted SHARED-001 source must change, do not fix it here. Stop and return the implementation issue to `moda_architect` so the owning implementation task (SHARED-001) can be reopened/corrected under the normal review protocol.

## Completion Report

### Status

Published; ready for Architect Review

### Files Changed

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`

### Work Completed

- Verified SHARED-001 was Complete / Accepted at Attempt 2 and the prepared Shared source contained accepted commit `c4627f1` without source or working-tree drift.
- Advanced the synchronized package version from `1.0.1` to exactly `1.1.0` with `npm version minor --no-git-tag-version`; no Git tag was created.
- Inspected the dry-run archive; model, model/node, runner, Commerce, and logging JavaScript/declaration outputs were present.
- Published once to `https://registry.npmjs.org/`; npm accepted `@modainteract/moda-interact-shared@1.1.0`.
- Verified exact public registry metadata and installed the exact published version in a clean external consumer. All required imports passed without an OpenRouter request or credential.
- Downstream ARCH-024 consumers must install exactly `@modainteract/moda-interact-shared@1.1.0`.

### Validation Results

- SHARED-001 prerequisite: `Complete / Accepted — Attempt 2`; accepted commit `c4627f1` is an ancestor of prepared Shared source head `eaf62bc`.
- Starting version `1.0.1`; target/published version `1.1.0` (exactly one minor increment).
- Source identity check passed: no diff between accepted SHARED-001 source and prepared source for source, scripts, build configuration, docs, or package metadata before version mutation.
- Release diff contained only `package.json` and `package-lock.json`; `git diff --check` passed.
- `npm pack --dry-run` passed after normal `prepack`. JSON inventory assertions passed for model/model-node JS and declarations, runner JS/declarations, Commerce JS/declarations, and logging JS/declarations.
- `npm publish --access public --registry=https://registry.npmjs.org/` succeeded. npm accepted version `1.1.0`.
- Exact public registry metadata:

  ```json
  {
    "name": "@modainteract/moda-interact-shared",
    "version": "1.1.0",
    "dist.tarball": "https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-1.1.0.tgz",
    "dist.shasum": "923e5b71942bd17e2d2537820f884c9edc3cdeaf",
    "dist.integrity": "sha512-XZMhMbEn8oy9xZfqrAWmbjcbYdOxScUsCE1myCqiywuUgcDPnhGDs1jj2bORyqhFYvOwhFzI4K5vmkSlxqOwiA==",
    "dist-tags.latest": "1.1.0"
  }
  ```

- Clean consumer directory installed exactly `@modainteract/moda-interact-shared@1.1.0` from npmjs. Imports passed for `commerce/model`, `commerce/model/node`, `commerce/runner`, and `logging`; `CommerceModelCatalogueEntrySchema`, `CommerceModelConfigurationSchema`, `createOpenRouterModelId`, `OpenRouterModelClient`, `runCommerceTurn`, `runnerVersion`, and `createLogger` were present. No model invocation or credential was used. The disposable directory was removed.
- No implementation source or consumer repository was changed. No unit tests or typecheck were rerun, consistent with publication-only validation scope.

### Deviations

The prepared worktree initially lacked `tsup`; `npm ci` installed exactly the committed lockfile dependencies before the required dry-run artifact build. No tracked dependency or source file changed.

### Assumptions

The exact npmjs registry metadata and successful clean-consumer import verify public availability; `1.1.0` is the canonical version for downstream ARCH-024 consumers.

### Unresolved Issues

None.

### Architectural Concerns

None.

### Prepared Execution Evidence

- Launcher prepared and claimed Attempt 1 for `copilot`; dependency gate passed for `ARCH-024-SHARED-001`. Claim commit `50c4d1fff1a127c97afe2968faea74c806835ea7` was committed and pushed.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-024-SHARED-002`, `task/ARCH-024-SHARED-002`; prepared head `fef30bcd29cfbcd01ee9aea512196f688633c30f`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-024-SHARED-002`, `task/ARCH-024-SHARED-002`; prepared head `eaf62bc2e4f7f2e7833c325345108282da04a2e5`.
- Both task refs did not require fast-forward and `origin/main` was already incorporated. Recursive submodule sync/update passed; the recursive submodule entry list is empty.
- Release metadata commit `3480905` is pushed to `origin/task/ARCH-024-SHARED-002`. Parent report commit/push completes review submission. No main merge, tag, consumer integration, or downstream task was started.

## Architect Review

### Review Status

Accepted — Attempt 1

### Review Notes

ARCH-024-SHARED-002 conforms to the publication-only release-gate contract.

- `ARCH-024-SHARED-001` was Complete / Architect-Accepted at Attempt 2 before publication; the accepted implementation identity recorded by this task is `c4627f1`.
- The release metadata advances exactly one backward-compatible minor version, `1.0.1 -> 1.1.0`.
- Independent architect comparison against the accepted SHARED-001 snapshot found no Shared source, script or build-configuration drift. `package.json` changes only the package version, and `package-lock.json` changes only the root/package version metadata.
- Publication evidence records one successful `npm publish --access public --registry=https://registry.npmjs.org/` for `@modainteract/moda-interact-shared@1.1.0`, followed by exact registry metadata and a clean external exact-version consumer import of `commerce/model`, `commerce/model/node`, `commerce/runner` and `logging`.
- Release metadata commit `3480905` is recorded as pushed on `origin/task/ARCH-024-SHARED-002`; no Git tag, consumer integration or downstream implementation was started by the publication task.
- The submitted task document contained stale intermediate publication-progress text duplicated outside the standard task sections and inside YAML frontmatter. Architect reconciliation removes that coordination drift only; all substantive publication evidence remains preserved in the Completion Report and no repository rework or republish is required.

Canonical ARCH-024 Shared release identity:

```text
Published Shared revision:
@modainteract/moda-interact-shared@1.1.0

Registry SHA-1:
923e5b71942bd17e2d2537820f884c9edc3cdeaf

Registry integrity:
sha512-XZMhMbEn8oy9xZfqrAWmbjcbYdOxScUsCE1myCqiywuUgcDPnhGDs1jj2bORyqhFYvOwhFzI4K5vmkSlxqOwiA==

Accepted SHARED-001 implementation:
c4627f1

Release metadata commit:
3480905
```

### Reviewed Files

- `docs/decisions/shared/ARCH-024/SHARED-002-publish-arch024-shared-runtime.md`
- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- accepted ARCH-024-SHARED-001 Shared snapshot
- ARCH-024 Shared/Admin/Commerce/Background domain indexes and direct consumer task definitions
- `docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

### Validation Reviewed

Publication review intentionally did not rerun SHARED-001 implementation tests, lint, typecheck or an explicit production build.

Reviewed publication evidence:

- prerequisite SHARED-001: Complete / Accepted Attempt 2;
- synchronized starting version: `1.0.1`;
- exact published version: `1.1.0`;
- registry SHA-1: `923e5b71942bd17e2d2537820f884c9edc3cdeaf`;
- registry integrity: `sha512-XZMhMbEn8oy9xZfqrAWmbjcbYdOxScUsCE1myCqiywuUgcDPnhGDs1jj2bORyqhFYvOwhFzI4K5vmkSlxqOwiA==`;
- registry tarball: `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-1.1.0.tgz`;
- `npm pack --dry-run`: recorded PASS with required model/model-node/runner/logging JavaScript and declaration entrypoints;
- clean external exact-version consumer: recorded PASS for all required public imports with no OpenRouter invocation or credential;
- implementation-source comparison against the accepted SHARED-001 snapshot: PASS, no changes beyond authorised release version metadata;
- current ARCH-024 consumer package manifests in the submitted workspace do not yet depend on `1.1.0`, confirming consumer integration remained out of scope;
- `git diff --check`: recorded PASS.

Direct npm registry retrieval was unavailable from this architect review environment. Consistent with the cross-environment review policy, the exact registry identity is accepted from the durable publication and clean-consumer evidence recorded in the Completion Report; no contradictory evidence was found.

### Architecture Conformance

Conforms. The architect-accepted ARCH-024 Shared model/OpenRouter/LangGraph runtime is now consumable through the canonical exact package revision `@modainteract/moda-interact-shared@1.1.0`. Publication and consumer integration remain separate ownership boundaries as required.

### Follow-up

Mark `ARCH-024-SHARED-002` Complete and require downstream ARCH-024 consumers to install exactly `@modainteract/moda-interact-shared@1.1.0`.

The dependency graph now makes exactly these tasks Ready:

```text
ARCH-024-ADMIN-001
ARCH-024-ADMIN-004
ARCH-024-COMMERCE-002
ARCH-024-BACKGROUND-001
```

No task is automatically claimed or started by this acceptance. `ARCH-024-ADMIN-002`, `ARCH-024-ADMIN-003`, `ARCH-024-COMMERCE-003`, `ARCH-024-COMMERCE-005`, `ARCH-024-COMMERCE-006`, `ARCH-024-COMMERCE-007`, `ARCH-024-BACKGROUND-002` and `ARCH-024-GATEWAY-001` remain Pending behind their additional declared dependencies.
