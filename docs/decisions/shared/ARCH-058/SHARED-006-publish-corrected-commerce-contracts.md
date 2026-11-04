---
id: ARCH-058-SHARED-006
architecture_id: ARCH-058
title: Publish the corrected ARCH-058 Shared contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 38
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-058-SHARED-003
  - ARCH-058-SHARED-004
  - ARCH-058-SHARED-005
enables:
  - ARCH-058-MCP-002
  - ARCH-058-COMMERCE-001
  - ARCH-058-BACKGROUND-001
  - ARCH-058-SYSTEM-TEST-001
created: 2026-11-04
updated: 2026-11-04
---

# ARCH-058-SHARED-006: Publish the corrected ARCH-058 Shared contracts

## Architecture

Architecture ID: `ARCH-058`.

Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`.

Publication policy: `moda-interact-shared/README.md` semantic-versioning and package-inspection rules.

Coordinator: `moda_architect`.

This publication replaces the unexecuted revision-9 SHARED-004 4.0.1 proposal. The accepted 4.0.0 receipt remains immutable historical evidence.

## Objective

Publish the exact architect-accepted combined SHARED-003/004/005 source as the next breaking Shared package, approved target `@modainteract/moda-interact-shared@5.0.0`, and verify that the registry artifact exposes the corrected no-hash built-in contract at `definitionVersion: "2.0.0"`, omits the obsolete conversation-tool-context export, preserves runner `1.1.0`, and enforces the canonical Commerce UTC datetime syntax.

## Context

The corrected package removes public fields/exports and intentionally narrows one pre-production wire validator. Shared's repository release policy classifies this as a major public API/package compatibility change. Therefore 4.0.1 is not an acceptable publication target for this correction.

`5.0.0` is the architect-approved target **only if it is unoccupied when this publication task runs**. If registry metadata shows that 5.0.0 already exists, stop and return to `moda_architect`; do not choose 5.0.1, 6.0.0 or overwrite an existing version automatically.

## Scope

Publication/release mechanics only:

- verify SHARED-003/004/005 are Complete and architect-accepted;
- verify the release worktree contains the accepted combined source and no unreviewed implementation changes;
- apply package/lock release metadata for 5.0.0 through the existing npm release process;
- inspect the exact local tarball;
- publish that inspected tarball using existing registry/authentication configuration;
- retrieve exact 5.0.0 and verify registry bytes/metadata and the corrected public surface;
- record an immutable publication receipt.

## Out of Scope

No schema implementation, test fixes, dependency pinning, Database work, MCP/Commerce/Background upgrades, Studio publication, deployment or system-test execution. Do not rerun implementation unit/integration/lint/typecheck suites already accepted in SHARED-003/004/005.

## Requirements

1. Check actual registry versions immediately before changing metadata. `5.0.0` must be unoccupied.
2. Change only release metadata required by the existing process, normally package/lock package version scalars from 4.0.0 to 5.0.0.
3. Build only as required by the package's prepack lifecycle. Do not alter implementation source in this publication task.
4. The inspected and registry artifacts must expose:
   - `CommerceBuiltInToolDescriptorSchema` and `CommerceBuiltInToolGrantSchema` without `contractHash` and requiring exactly `definitionVersion: "2.0.0"`;
   - `commerceDiscountBuiltInDescriptors` with exactly the two name/version identities;
   - no `commerceBuiltInToolContractPayload` export;
   - no `CommerceConversationToolContextSchema` or `CommerceConversationToolContext` export;
   - preserved `CommerceConversationGrantSchema`, `CommerceAssertionSchema` and `CommerceOutreachToolContextSchema`;
   - `runnerVersion === "1.1.0"`;
   - corrected discount timestamp behavior from SHARED-005, verified through `CommerceOfferSchema` and `CommerceDiscountConditionFactsSchema`; the general `DateSchema` remains the accepted pre-existing export unchanged.
5. Do not pin or modify Zod because of this publication.
6. Record exact source/release commits, registry version, tarball URL, integrity/shasum/size and verification result. Do not invent values before publication.

## Work Items

- [x] Verify all three implementation prerequisites are Complete and accepted.
- [x] Verify 5.0.0 is unoccupied immediately before release.
- [x] Apply only approved release metadata and inspect the local artifact.
- [x] Publish the exact inspected artifact.
- [x] Retrieve exact 5.0.0 and verify bytes/metadata/public API.
- [x] Record the immutable receipt and stop.

## Interfaces / Contracts

Package:

```text
@modainteract/moda-interact-shared@5.0.0
```

The package contains the combined breaking corrections from SHARED-003, SHARED-004 and SHARED-005. Both discount built-in definition versions are `2.0.0` because SHARED-005 changes their accepted output timestamp semantics; npm package version `5.0.0` and built-in definition version `2.0.0` remain separate concepts.

## Dependencies

- `ARCH-058-SHARED-003`
- `ARCH-058-SHARED-004`
- `ARCH-058-SHARED-005`

## Enables

- `ARCH-058-MCP-002`
- `ARCH-058-COMMERCE-001`
- `ARCH-058-BACKGROUND-001`
- `ARCH-058-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] All implementation prerequisites were Complete and accepted before publication.
- [x] Exact version 5.0.0 was unoccupied immediately before publication and is retrievable afterwards.
- [x] Registry archive bytes/integrity match the inspected local artifact according to the established release verification approach.
- [x] Corrected no-hash built-in identities are present, strict, and require exactly `definitionVersion: "2.0.0"`; legacy `1.0.0` is rejected by the corrected schemas.
- [x] Removed hash helper and conversation-tool-context exports are absent.
- [x] Preserved conversation/grant/outreach exports and runner 1.1.0 remain present.
- [x] Corrected discount timestamp fixtures pass through `CommerceOfferSchema` and `CommerceDiscountConditionFactsSchema`, and the general `DateSchema` export has not changed from the accepted SHARED-002 source.
- [x] No consumer repository or Database source was changed.

## Validation

Publication validation only, following repository policy. Record the actual commands; normally:

```bash
npm view @modainteract/moda-interact-shared versions --json
npm version 5.0.0 --no-git-tag-version
npm pack --json --pack-destination <temporary-local-directory>
npm publish <exact-inspected-tarball> --access public
npm view @modainteract/moda-interact-shared@5.0.0 dist --json
npm pack @modainteract/moda-interact-shared@5.0.0 --prefer-online --ignore-scripts --json --pack-destination <temporary-registry-directory>
git diff --check
```

Use a temporary runtime/declaration consumer against the retrieved artifact to inspect the corrected public API and the SHARED-005 discount timestamp fixtures, including the unchanged general `DateSchema` baseline. This is artifact verification, not a rerun of the implementation suites.

## Stop Condition

Set status to `review`, provide the immutable publication receipt and worktree/commit/push evidence, return to `moda_architect` and STOP. Do not update MCP, Commerce or Background from this task.

## Implementation Notes

Do not publish from a source tree that contains only a subset of SHARED-003/004/005. Publication must use the accepted combined source after those tasks have been integrated through the normal workflow.

## Completion Report

### Status

Ready for Review — Attempt 1, 2026-11-04. Published and retrieved exact `@modainteract/moda-interact-shared@5.0.0` from the existing public npm registry. The registry archive is byte-identical to the inspected local archive, and both local and retrieved runtime/declaration consumers passed. Release metadata is committed/pushed as `1927375a74496488aa83049c39edeee9d278497a`. No architect acceptance, main merge or consumer adoption is asserted.

### Files Changed

Implementation: `package.json` and `package-lock.json` only. Exactly three version scalars changed from4.0.0 to5.0.0: package version, lock root version and lock root-package version. Structured JSON comparison proved every other metadata/dependency/export field unchanged; no implementation or test source changed. Parent changes are limited to this task report/state. The existing4.0.0 receipt and all architect-owned review/reconciliation history remain untouched.

### Work Completed

- Confirmed latest prerequisite acceptance records: SHARED-003 Attempt2 at59ea61f34197d64180e46680ac6d552b5e989a36, SHARED-004 Attempt1 at2efd9cd529256a0203a5e370640a9bb134080225 and SHARED-005 Attempt1 at070975e6ea1a38fd5f01e8c7a001b15e1bd67d4c. Launcher verified all Complete. All three commits are ancestors of the release baseline; baseline d3d7cb6813fdd381ebd7b0ad98b6ec10cce4d8a1 has a full tree identical to accepted SHARED-005. Worktree was clean before metadata changes and before publishing.
- Checked actual registry versions before release metadata and again immediately before publication.5.0.0 was absent, with latest4.0.0. Applied only the approved major release metadata through `npm version5.0.0 --no-git-tag-version` (actual spaced command below).
- Installed the committed build graph, packed with the existing prepack lifecycle, and performed the README-required dry-run inventory inspection. Every public package export target is present. Archive extraction rejected absolute/parent-traversal and nonregular/nondirectory members. No environment/authentication files are in the inspected package.
- Verified exact local archive through its own package self-reference, not a Shared source import. Runtime checks establish the two strict no-hash built-ins at2.0.0, legacy1.0.0 rejection, removed helper/context absence, preserved grant/assertion/outreach schemas and runner1.1.0. A strict temporary TypeScript consumer verifies public declarations and expected errors for legacy/hash-bearing grants and removed runtime/type exports.
- Published that exact inspected archive once using the existing registry/authentication configuration and public access. npm accepted the upload with a processing notice. The first two immediate exact-version reads returned E404; the third retrieval succeeded. No second publish was attempted. Downloaded exact5.0.0 with prefer-online/ignore-scripts and compared complete archive bytes, independent SHA512/SHA1/SHA256, file count and unpacked size.
- Repeated artifact runtime/declaration checks against the downloaded registry archive. Both consumers pass, their runtime reports agree exactly, and the general DateSchema remains the accepted baseline. latest now points to5.0.0. No implementation suites were rerun or represented as newly passing publication checks.

### Immutable Publication Receipt

The following is the actual receipt generated only after successful registry verification; timestamps, metadata, URL, sizes and hashes are observed values. The same receipt is retained locally at `/tmp/moda-shared-5.0.0-42wvvrfq/receipt.json`.

```json
{
  "schemaVersion": "1",
  "taskId": "ARCH-058-SHARED-006",
  "package": "@modainteract/moda-interact-shared",
  "version": "5.0.0",
  "acceptedSourceCommits": {
    "SHARED-003": "59ea61f34197d64180e46680ac6d552b5e989a36",
    "SHARED-004": "2efd9cd529256a0203a5e370640a9bb134080225",
    "SHARED-005": "070975e6ea1a38fd5f01e8c7a001b15e1bd67d4c"
  },
  "combinedSourceCommit": "d3d7cb6813fdd381ebd7b0ad98b6ec10cce4d8a1",
  "releaseCommit": "1927375a74496488aa83049c39edeee9d278497a",
  "registryPublishedAt": "2026-11-04T21:42:21.462Z",
  "verifiedAt": "2026-11-04T21:45:56.629609+00:00",
  "tarballUrl": "https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-5.0.0.tgz",
  "archive": {
    "filename": "modainteract-moda-interact-shared-5.0.0.tgz",
    "bytes": 287137,
    "sha256": "37e9d1dd28844d8015aae8bdaf85d010028e97b00f61073ef0f183be18a5a06b",
    "shasum": "77e2415d48af273c2053573480cafe529c3a789e",
    "integrity": "sha512-6IcxLh8QcNNRCN5/n2he7IdbzbWLao4ZNazD/wdijkZ5W2ztHHdEN+LAxILgVrbXuLNw82j7/xtSKuEcjPwSjQ==",
    "byteIdenticalToLocal": true,
    "publicExportTargetsPresent": true
  },
  "unpackedBytes": 1302170,
  "fileCount": 131,
  "distTagsBefore": {
    "latest": "4.0.0"
  },
  "distTagsAfter": {
    "latest": "5.0.0"
  },
  "prepublishCheck": {
    "checkedAt": "2026-11-04T21:41:00.485008+00:00",
    "versionUnoccupied": "5.0.0",
    "localArchiveUnchanged": true
  },
  "verification": {
    "localRuntime": "PASS",
    "localDeclarations": "PASS",
    "registryRuntime": "PASS",
    "registryDeclarations": "PASS",
    "byteEquality": "PASS",
    "publicExportTargets": "PASS",
    "builtInDefinitionVersions": "2.0.0",
    "runnerVersion": "1.1.0",
    "strictNoHash": true,
    "removedExportsAbsent": true,
    "preservedExportsPresent": true,
    "generalDateSchemaMatchesAcceptedSource": "0b5567c3e01748de1d5d8c7d3be0d84a55dfb139",
    "generalPrimitivesSha256": "c0ef1212147df0bed4f993814a925eea38eed19f4c4d84956fc3e6964d5072eb",
    "timestampFixtures": 19,
    "validTimestampFixtures": 7,
    "invalidTimestampFixtures": 12
  },
  "publicationAttempts": 1,
  "metadataRetrievalAttempts": 3,
  "registryPropagation": "Upload accepted with processing notice; first two metadata reads returned E404; third read and exact archive retrieval succeeded. No republication."
}
```

### Validation Results

Publication/artifact verification only:

| Actual command/check | Result |
|---|---|
| Prerequisite acceptance records, accepted commit ancestry, baseline-to-accepted full-tree comparison | Passed; accepted combined implementation present |
| `npm view @modainteract/moda-interact-shared versions --json` |5.0.0 absent before metadata change |
| `npm ci --no-audit --no-fund` | Passed; committed dependency graph retained |
| `npm version 5.0.0 --no-git-tag-version` | Passed; exactly three version scalars changed |
| `npm pack --json --pack-destination /tmp/moda-shared-5.0.0-42wvvrfq/local` | Passed; sole build via existing prepack lifecycle |
| `npm pack --dry-run --ignore-scripts --json` | Passed; README inventory inspection on completed build, without another build |
| Local archive inventory, runtime verifier and strict declaration consumer | Passed; all public export targets present |
| `npm view @modainteract/moda-interact-shared versions --prefer-online --json` | Fresh prepublish guard:5.0.0 absent; exact inspected archive hash unchanged |
| `npm publish /tmp/moda-shared-5.0.0-42wvvrfq/local/modainteract-moda-interact-shared-5.0.0.tgz --access public` | Accepted once; subsequently verified retrievable |
| `npm view @modainteract/moda-interact-shared@5.0.0 version dist --prefer-online --json` | Third read succeeded after two processing-related E404 responses |
| `npm pack @modainteract/moda-interact-shared@5.0.0 --prefer-online --ignore-scripts --json --pack-destination /tmp/moda-shared-5.0.0-42wvvrfq/registry` | Passed; actual registry archive retrieved |
| Full local/registry byte comparison, registry integrity/shasum/size checks | Passed;287137 compressed bytes,1302170 unpacked bytes,131 files |
| Retrieved archive runtime verifier and strict declaration consumer | Passed; same outcomes as local archive |
| `npm view @modainteract/moda-interact-shared time --prefer-online --json` and dist-tags query | Actual publication timestamp and latest5.0.0 recorded in receipt |
| `git diff --check` and metadata-only working-tree checks | Passed |

Both temporary declaration consumers use the installed compiler with `--noEmit --module NodeNext --moduleResolution NodeNext --target ES2022 --strict --skipLibCheck --types node` on the artifact's verify.ts. Dependency-resolution links expose only the installed third-party build dependencies; the inspected/downloaded package resolves its own public exports. Node24.19.0/npm11.17.0 came from the workspace bootstrap; Zod4.4.3 remains the existing locked build/runtime-fixture dependency, and package Zod range remains unchanged. No application Zod pin/override was introduced.

#### Timestamp and general-DateSchema verification

Local and registry artifact checks use otherwise-valid full CommerceOfferSchema and CommerceDiscountConditionFactsSchema fixtures at all four named fields, plus composed options/details outputs. All19 timestamp cases match:7 accepted and12 rejected. This includes every mandatory SHARED-005 example: seconds-only and fractions1/2/3/10 digits pass; minute-only, numeric offset, Feb30 and leap-second60 fail. Additional checks cover valid2000/2024 leap days, invalid1900/2100 leap days, April31, lowercase z, empty fractions and surrounding whitespace/newline. Original fractional bytes and nullability survive; equal/reversed non-null offer boundaries fail, increasing ones pass.

General primitives are byte-identical to accepted SHARED-002 source0b5567c3e01748de1d5d8c7d3be0d84a55dfb139 (SHA256 in receipt). The exported DateSchema JSON schema and parse outcomes match its accepted `z.iso.datetime({offset:false})` baseline under the same resolved Zod, proving that publication did not replace it with the discount-specific validator.

#### Runtime/declaration public surface

Both artifacts expose exactly commerce_get_discount_options@2.0.0 and commerce_get_discount_details@2.0.0. Strict descriptor/grant validators reject1.0.0, contractHash and unknown extra fields. Canonical names/descriptions/inputs remain the accepted source. The payload hash helper and obsolete conversation-tool-context runtime/type exports are absent; CommerceConversationGrantSchema, CommerceAssertionSchema and CommerceOutreachToolContextSchema remain present, and runnerVersion is1.1.0. Declaration expected-error assertions passed for removed exports and legacy/hash-bearing grants.

### Physical Worktree / Commit / Push Evidence

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-SHARED-006
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-SHARED-006
both branches: task/ARCH-058-SHARED-006
parent prepared head: dc5da17151c43cb4117e5a14df82373a0d932e08
implementation prepared head: d3d7cb6813fdd381ebd7b0ad98b6ec10cce4d8a1
claim commit, pushed: e0d61f8e02412b8367f32d938ce345682c61058e
claim executor/time: codex / 2026-11-04T21:31:14Z; Attempt1
release metadata commit, pushed: 1927375a74496488aa83049c39edeee9d278497a
parent remote task fast-forward: not-needed
parent origin/main incorporation: already-current
implementation remote task fast-forward: not-needed
implementation origin/main incorporation: already-current
recursive submodule sync/update/init/verification: passed by launcher; no submodule entries
shared/default checkouts switched/mutated for task implementation: no
another task worktree reused: no
```

The final parent report is committed/pushed on the matching task branch as this report submission. No main branch, Git release tag, parent implementation gitlink, consumer task/state or Database source was changed.

### Deviations

No implementation or release-scope deviation. npm processing required two failed exact-version metadata reads before successful retrieval; this transient propagation is recorded rather than treated as immediate publication verification. A metadata-only release commit was pushed before packing, binding the inspected artifact to its exact release source.

### Assumptions

No remaining conditional version assumption:5.0.0 was proven unoccupied at the publication boundary and retrieved afterwards. Prior accepted implementation validation remains authoritative and was not rerun by this publication task.

### Unresolved Issues

None blocking this publication gate. The known optional Commerce projection compatibility issue accepted as separate coordination in SHARED-005 was not rerun or represented as passing integrated-consumer validation here. Consumer adoption, persisted development-grant migration, environment tool publication and system-test validation remain with their designated tasks.

### Architectural Concerns

No new concerns. The published version is exactly5.0.0, with built-in contract versions exactly2.0.0; these remain separate identities. Registry publication is verified, while architect review of this task remains pending.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Architect Dependency Reconciliation (2026-11-04)

SHARED-005 Attempt 1 is architect-accepted and Complete at `070975e`. All explicit prerequisites are Complete. Promoted to Ready with executor/claim empty and Attempt 0 preserved; no execution is started. The known optional Commerce projection issue recorded in SHARED-005 remains a consumer-validation coordination item, not a passing integration claim.
