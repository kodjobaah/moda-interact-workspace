---
id: ARCH-058-SHARED-004
architecture_id: ARCH-058
title: Publish the accepted contract-runtime correction as Shared 4.0.1
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 36
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-058-SHARED-003
enables:
  - ARCH-058-MCP-002
  - ARCH-058-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-058-SHARED-004: Publish the accepted contract-runtime correction as Shared 4.0.1

## Architecture

`docs/architecture/ARCH-058-commerce-agent-product-discovery.md`, `docs/architecture/ARCH-058/contracts.md`, `docs/architecture/ARCH-058/implementation-handoff.md` and ARCH-058-SHARED-003. Coordinator: `moda_architect`.

**Definition state:** defined but not materialised, pending SHARED-003 acceptance. No package is published by this definition. After the prerequisite is Complete and the task becomes Ready, use `/moda-task ARCH-058-SHARED-004` through the normal launcher.

## Objective

Publish the exact architect-accepted SHARED-003 implementation as immutable `@modainteract/moda-interact-shared@4.0.1`, verify the actual registry artifact with the accepted packed-consumer harness, and issue the receipt required for coordinated consumer adoption. Preserve the accepted built-in definition versions/hashes and runner 1.1.0. This is a release-only task.

## Context and selected version

The 4.0.0 artifact is intact; its open Zod range allowed a different installed schema runtime to change generated payloads and datetime validation. SHARED-003 restores the accepted behavior by declaring exact Zod 4.4.3 and proving the supported aligned consumer graph. The Shared README release policy classifies a backward-compatible correction to an existing capability as a **patch** release. The approved target is **4.0.1**.

The architect's reconciliation observed exact registry 4.0.1 as absent. That observation does not reserve the version. Recheck that exact target immediately before publication. If it is already occupied or the prepared accepted source is not the specified 4.0.0 baseline plus SHARED-003, stop with the observed evidence. Do not select another version, overwrite a release, unpublish 4.0.0 or reinterpret an occupied version as this task's successful publication.

## Scope and exact edit map

| Path in `moda-interact-shared` | Authorized release change |
| --- | --- |
| `package.json` | Change package `version` from `4.0.0` to `4.0.1` only. |
| `package-lock.json` | Change the top-level package version and `packages[""].version` from `4.0.0` to `4.0.1` only. |

All SHARED-003 implementation, dependency records, scripts, public exports, schemas, built-in literals and runner code remain byte-identical to the accepted source. The task report records publication evidence and receipt. Do not modify the old SHARED-002 receipt or completed histories, another task's lifecycle, consumer manifests/lockfiles, parent gitlinks or decision indexes.

## Requirements

### 1. Accepted source and isolated release preparation

The canonical SHARED-003 task must be Complete with an explicit architect acceptance and exact accepted implementation commit. Record that full commit and the clean isolated release worktree/base. Verify the release source contains that accepted commit or separately recorded accepted equivalence, and that its relevant source/package tree matches the accepted result. An unreviewed local branch, an unfinished implementation, or a successful test without architect acceptance is insufficient.

The prepared source must declare package version 4.0.0, exact `dependencies.zod: "4.4.3"`, and the accepted `validate:commerce-consumer-artifact` script. The built-in descriptors remain definition **1.0.0** with options hash `a0a4a88c7920a25a31657a03761b6556419189aeab251261a58e2dfb83a3bdcb` and details hash `776f6bc6ac1800c75744c2ffa7357f07a32be2b61309b1d71abf0493a2de316f`. Runner remains **1.1.0**.

Use the launcher's worktree and existing Node/registry/authentication configuration. Do not expose credentials. Before Node/npm commands:

```bash
command -v node >/dev/null 2>&1 || source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

### 2. Exact target check, metadata bump and inspected artifact

Query the existing intended registry for `@modainteract/moda-interact-shared@4.0.1` with npm's structured output. Only the explicit package/version-not-found response establishes vacancy. Authentication, DNS, transport, rate-limit or other registry failures are blockers, not evidence that the version is free. The existing registry remains `https://registry.npmjs.org/` as recorded by SHARED-002; an actual configuration mismatch needs reconciliation rather than a silent registry change.

Reuse the launcher's matching dependency-install evidence for the accepted lockfile. If that exact installation is absent, run `npm ci --ignore-scripts --no-audit --no-fund` in the isolated release worktree before packaging and verify it preserves the lockfile. Do not refresh dependency resolution.

Apply `npm version 4.0.1 --no-git-tag-version`. Compare parsed JSON to the accepted source and require exactly the three version-scalar changes in the edit map. Commit the release metadata through the normal task workflow so its exact SHA can be recorded before publication. Do not create a Git tag or broaden the release source.

Produce one actual tarball with the existing `prepack` build. Inspect its package metadata and every declared public export target for included JavaScript/declaration/fixture files, as applicable. Require exact package name/version/Zod pin, the accepted file inventory except for the reviewed repair files/metadata, and no task evidence, test fixture installations, credentials or temporary files. Record archive bytes, SHA-256, SHA-512 integrity and SHA-1 shasum. Run the accepted artifact harness against this exact local tarball before publication; both its supported aligned graph and isolated foreign-runtime graph must pass.

### 3. Publish and retrieve the exact inspected bytes

Recheck exact target vacancy immediately before publishing. Publish **the inspected tarball path** with the established public registry workflow; do not invoke a source-directory publish that repacks a different artifact. Use the existing public access/latest-tag behavior from SHARED-002. The task authorizes only this selected version after its gates succeed.

Retrieve exact registry `@modainteract/moda-interact-shared@4.0.1` into a separate task-owned directory with `npm pack ... --prefer-online`. Obtain its exact registry `dist` metadata. Compare retrieved archive bytes and computed hashes with the inspected/published local archive, and compare SHA-512 integrity/SHA-1 shasum with the registry metadata. A successful publish command alone is insufficient. Transient propagation may be retried with explicit bounded attempts and reported evidence; do not report a retrievable verified release until retrieval succeeds.

Invoke the unchanged SHARED-003 harness against the downloaded registry tarball with `--expected-version 4.0.1`. Its fixture installations must consume those downloaded bytes, with no source dependency symlinks or reused build dependency graph. Require both original built-in hashes, Shared's exact 4.4.3 runtime identity in both fixtures, the aligned strict composition checks, timestamp controls and runner 1.1.0. Do not rerun the entire source implementation suite for this metadata-only release.

If publication succeeds but verification fails, record the actual immutable published version and exact failure, retain evidence and stop for architect reconciliation. Do not retry publication, rewrite the occupied version or claim this gate passed.

### 4. Immutable receipt and downstream handoff

Record a JSON receipt in this task's Completion Report with these required fields populated from actual evidence:

- `schemaVersion: "1"`, package name, `version: "4.0.1"`, registry and registry `publishedAt`.
- Full `acceptedSourceCommit` from SHARED-003, `releaseBaseCommit` and `releaseMetadataCommit`.
- Exact tarball URL, registry `integrity` and `shasum`, computed `sha256`, byte size and unpacked file count/size from the actual artifact metadata.
- `localRegistryBytesIdentical: true`, actual observed dist-tag after publication, and `verifiedAt`.
- `sharedZodVersion: "4.4.3"`, `supportedComposingConsumerZodVersion: "4.4.3"`, runner `1.1.0`, both built-in names/definition versions/original hashes.
- Results for `aligned` direct Zod 4.4.3 and `foreign-runtime` direct Zod 4.6.5, each resolving Shared's own Zod to 4.4.3. Distinguish the passing aligned type/runtime composition from the foreign fixture's runtime-only assurance.
- Actual local/downloaded harness commands and their exit statuses; all public export-target inclusion check and owned temporary cleanup result.

Do not populate unknown receipt values with anticipated hashes/commits or mark verification true before execution. Preserve SHARED-002's 4.0.0 receipt as historical evidence. The architect's acceptance/reconciliation promotes the new receipt to the current consumer baseline; publication alone does not edit consumer pins or accept MCP-002.

MCP-002 resumes its existing **in_progress Attempt 1** under its existing claim only after this task is accepted and Complete. It installs exact Shared 4.0.1 and direct Zod 4.4.3 under its amended task, retaining its accepted Database pin, WIP and required validation. COMMERCE-001 and BACKGROUND-001 perform the same exact Shared/Zod alignment in their own tasks. Direct consumer parsing behavior can change with this alignment; all three applications retain their existing focused parsing regression and typecheck requirements, and this publication does not certify those application checks. MCP-003 inherits the accepted MCP-002 graph. SYSTEM-TEST-001 verifies the accepted application artifacts and receipt without adding a new SystemTest Shared dependency. No consumer is upgraded in this publication task.

## Work Items

- [ ] Verify Complete/accepted SHARED-003 source and clean release preparation.
- [ ] Verify exact 4.0.1 target vacancy and apply only the three approved version scalars.
- [ ] Build, inspect and verify the exact local tarball with the accepted artifact harness.
- [ ] Publish that inspected tarball after a final exact-target vacancy check.
- [ ] Retrieve exact 4.0.1, compare bytes and registry hashes, and verify it with the same artifact harness.
- [ ] Record the immutable receipt and actual commit/worktree/push evidence, then submit for architect review.

## Interfaces / Contracts

`@modainteract/moda-interact-shared@4.0.1` through all existing public subpaths, with Shared and composing consumer Zod both exactly 4.4.3. Built-in definition versions/hashes, public wire schemas and runner 1.1.0 are unchanged. The explicit foreign-runtime fixture does not authorize consumers to compose public Shared schemas with Zod 4.6.5.

## Dependencies

- `ARCH-058-SHARED-003`: exact architect-accepted implementation and passing packed-consumer validation.

## Enables

- `ARCH-058-MCP-002`: unblock the existing attempt's package/Zod adoption and original hash gate without restarting or resetting that task.
- `ARCH-058-SYSTEM-TEST-001`: exact corrected immutable package receipt after all other declared prerequisites complete.

## Acceptance Criteria

- [ ] The release source is exactly the accepted SHARED-003 result plus the three authorized metadata version changes.
- [ ] Approved exact 4.0.1 was vacant before publication and is retrievable from the intended registry afterward.
- [ ] The retrieved tarball is byte-identical to the inspected published artifact and matches registry integrity/shasum.
- [ ] Public export targets and the actual downloaded artifact's aligned/foreign-runtime harness checks pass with the original hashes and accepted timestamp behavior.
- [ ] The complete truthful receipt and actual source/release metadata commits are recorded.
- [ ] No consumer, Database, tool publication, environment, runtime contract, historical receipt or decision index changed.

## Validation

Use the existing release workflow and record actual commands. The following is the fixed command sequence after accepted-source preparation; read and handle the exact-target query result as specified above. A package-not-found response is expected only for the two vacancy checks.

```bash
npm view @modainteract/moda-interact-shared@4.0.1 version --json
npm version 4.0.1 --no-git-tag-version
shared_release_artifact_dir="$(mktemp -d "${TMPDIR:-/tmp}/moda-shared-contract-release.XXXXXX")"
npm pack --json --pack-destination "$shared_release_artifact_dir"
npm run validate:commerce-consumer-artifact -- --tarball "$shared_release_artifact_dir/modainteract-moda-interact-shared-4.0.1.tgz" --expected-version 4.0.1
git diff --check
npm view @modainteract/moda-interact-shared@4.0.1 version --json
npm publish "$shared_release_artifact_dir/modainteract-moda-interact-shared-4.0.1.tgz" --access public
shared_registry_artifact_dir="$(mktemp -d "${TMPDIR:-/tmp}/moda-shared-contract-registry.XXXXXX")"
npm pack @modainteract/moda-interact-shared@4.0.1 --prefer-online --json --pack-destination "$shared_registry_artifact_dir"
npm view @modainteract/moda-interact-shared@4.0.1 dist --json
npm run validate:commerce-consumer-artifact -- --tarball "$shared_registry_artifact_dir/modainteract-moda-interact-shared-4.0.1.tgz" --expected-version 4.0.1
```

The source/metadata/byte/integrity checks above are required between the corresponding commands. Do not paste the sequence as an unchecked pipeline or treat every nonzero `npm view` as vacancy. Record required packaging/build work once, the two local/registry artifact verification results, and cleanup. No Docker, database, provider/model traffic, implementation-suite rerun or consumer installation belongs to this gate.

## Out of Scope

No schema/test/harness implementation, alternative package or built-in version, hash regeneration, republishing 4.0.0, consumer upgrades, task resets, Database change, taxonomy migration/import, Commerce feature/tool publication, deployment, Admin change, customer send, index edit or main-branch merge.

## Stop Condition

Stop with exact evidence for an unaccepted/mismatching source, occupied target, registry/authentication problem, metadata scope violation, artifact mismatch, failed harness or unsupported consumer graph. Do not repair implementation during publication. After successful publication and verification, complete the report, set status to `review`, and return to the architect. Architect acceptance is required before the corrected release is a satisfied downstream dependency.

## Completion Report

### Status

Not started. Defined but not materialised; SHARED-003 acceptance and publication are pending.

### Files Changed

None.

### Work Completed

None.

### Immutable Publication Receipt

Not issued. Record only actual publication and retrieval evidence using the fields above.

### Validation Results

Not run by this publication task.

### Deviations

None.

### Unresolved Issues

SHARED-003 must be accepted and Complete before this task can start. Target vacancy must be rechecked at execution.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation acceptance, publication or downstream task promotion is granted by this portable definition.
