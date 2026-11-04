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
status: pending
priority: 38
executor: null
claimed_at: null
attempt: 0
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

- [ ] Verify all three implementation prerequisites are Complete and accepted.
- [ ] Verify 5.0.0 is unoccupied immediately before release.
- [ ] Apply only approved release metadata and inspect the local artifact.
- [ ] Publish the exact inspected artifact.
- [ ] Retrieve exact 5.0.0 and verify bytes/metadata/public API.
- [ ] Record the immutable receipt and stop.

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

- [ ] All implementation prerequisites were Complete and accepted before publication.
- [ ] Exact version 5.0.0 was unoccupied immediately before publication and is retrievable afterwards.
- [ ] Registry archive bytes/integrity match the inspected local artifact according to the established release verification approach.
- [ ] Corrected no-hash built-in identities are present, strict, and require exactly `definitionVersion: "2.0.0"`; legacy `1.0.0` is rejected by the corrected schemas.
- [ ] Removed hash helper and conversation-tool-context exports are absent.
- [ ] Preserved conversation/grant/outreach exports and runner 1.1.0 remain present.
- [ ] Corrected discount timestamp fixtures pass through `CommerceOfferSchema` and `CommerceDiscountConditionFactsSchema`, and the general `DateSchema` export has not changed from the accepted SHARED-002 source.
- [ ] No consumer repository or Database source was changed.

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

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

5.0.0 is the approved target only while unoccupied; availability must be rechecked by the publication owner.

### Unresolved Issues

Actual registry receipt does not exist yet.

### Architectural Concerns

None.

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
