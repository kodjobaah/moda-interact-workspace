---
id: ARCH-047-SHARED-002
architecture_id: ARCH-047
title: Publish canonical Meta template status queue contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-047-SHARED-001
enables:
  - ARCH-047-MESSAGING-001
  - ARCH-047-BACKGROUND-003
created: 2026-10-25
updated: 2026-10-26
---

# Publish canonical Meta template status queue contract

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

## Objective

Publish the architect-accepted, already tested `@modainteract/moda-interact-shared/whatsapp-template-events` v2 contract for use by Messaging and Background.

## Context

ARCH-047-SHARED-001 owns implementation/tests. Consumer repositories must depend on a published package rather than unpublished sibling source code or separate local event schemas.

## Scope

Release-specific package/version metadata and registry publication only, after architect acceptance of SHARED-001.

## Out of Scope

No source implementation changes, dependency redesign, tests/lint/typecheck re-runs, Admin AST/translation work, consumer integration, queue operations or database changes.

## Requirements

- R1. Verify `ARCH-047-SHARED-001` status `complete` and accepted Architect Review before publication.
- R2. Select and apply the architecture-approved new package version, update only release metadata/lockfile if required and run the repository-declared publication command.
- R3. Verify that the exact version, including `./whatsapp-template-events` subpath, is available from the intended registry. Record version, publication command, registry verification and source commit; do not claim publication from local build files alone.
- R4. No source/behaviour changes beyond release-specific metadata; if a code defect is discovered, return to the architect for a correction task rather than fixing it during publication.

## Work Items

- [ ] Verify prerequisite acceptance and choose an architecture-approved, semver-conforming release version. SHARED-001 acceptance is verified; `2.5.1` was published but is not accepted as the correct version.
- [x] Publish the selected package version using `npm publish`; registry metadata confirms `2.5.1` was published.
- [x] Verify the published subpath and fixture from the actual registry tarball and record evidence. Completion remains blocked on resolving the version issue.

## Interfaces / Contracts

Published package `@modainteract/moda-interact-shared/whatsapp-template-events` — exact v2 schema, identity and job format from SHARED-001. Publishing does not create another contract.

## Dependencies

- `ARCH-047-SHARED-001` — architect-accepted and Complete. SHARED-001 Attempt 1 is complete and its Architect Review was accepted on 2026-10-25 (parent task commit `7ba6066f`).

## Enables

- `ARCH-047-MESSAGING-001` and `ARCH-047-BACKGROUND-003` may consume published version once their other task dependencies are satisfied.

## Acceptance Criteria

- [x] Source implementation accepted before publication.
- [ ] Architecture-approved package version available from registry and exact new export present. The artifact is present in `2.5.1`, but the version conflicts with the repository's semver guidance and lacks architecture approval.
- [x] Release evidence recorded and no implementation behaviour altered.

## Validation

- [x] Publication command and success evidence: `npm publish` invocation in the local npm debug log; registry publication timestamp and tarball metadata independently confirm success.
- [x] Exact version available at registry and published tarball/export check.
- [x] `git diff --check` on allowed metadata-only changes.

## Stop Condition

Record the released version and Completion Report, set task to `review`, then STOP. Do not start consumer implementation or rerun prior implementation tests.

## Implementation Notes

Use the repository's existing publication workflow and mirrored isolated task branches. No `_index.md` changes.

## Completion Report

### Status

Changes Requested — Attempt 1, developer-claimed on 2026-10-25T21:54:15Z. The prerequisite Architect Review was accepted before release, and package `2.5.1` was published and independently verified. The review fails because this new public subpath is an additive package capability, while the repository's versioning guidance requires a minor increment for additive capabilities; `2.5.1` is a patch increment from `2.5.0`. Do not treat `2.5.1` as the approved consumer version. The task is returned to `ready` at Attempt 1; no Attempt 2 is claimed.

### Files Changed

- `package.json` — version changed from `2.5.0` to `2.5.1`; the existing `./whatsapp-template-events` export and fixture export are included in the published manifest.
- `package-lock.json` — root package version changed from `2.5.0` to `2.5.1`.

The release-only implementation commit is `580de0a06dfc129f046cc311089a9bf9c18509c6`, tagged `v2.5.1`, and is pushed to `origin/task/ARCH-047-SHARED-002`; no source implementation changes were made. The npm publish invocation followed this commit. The commit and tag do not establish that `2.5.1` is the architecture-approved semver choice.

### Work Completed

- Verified in the canonical SHARED-001 parent task branch that Architect Review was accepted at commit `7ba6066f412295bc7be2995f1779f7d933349890` (`2026-10-25T21:48:18Z`), before the release commit `580de0a...` (`2026-10-25T21:55:44Z`). The earlier Pending text was a stale copy in this task branch, not the canonical SHARED-001 record.
- Confirmed the release commit changes only `package.json` and `package-lock.json`, and `git diff --check origin/main...HEAD` passes.
- Confirmed the local npm debug log records the command `npm publish` from the canonical implementation worktree. Npm registry metadata records version `2.5.1` published at `2026-10-25T21:57:05.768Z`.
- Verified `npm view @modainteract/moda-interact-shared@2.5.1` returns the exact registry version, tarball URL and integrity metadata.
- Downloaded and inspected the actual published tarball. It contains `package/dist/whatsapp-template-events.js`, `package/dist/whatsapp-template-events.d.ts`, and `package/fixtures/meta-template-status-v2.json`; the packed `package.json` declares the expected import/types export and fixture subpath.
- Made no consumer integration or follow-on task changes as part of this publication handoff.

### Validation Results

- **PASS** — local npm debug log records `npm publish`; registry metadata records publication at `2026-10-25T21:57:05.768Z`. Registry state and the retrieved tarball corroborate successful publication.
- **PASS** — npm reports tarball SHA-1 `00cf2087907c606daae87b9b4b4c7cd905d6d757` and SHA-512 integrity `sha512-4Vs2lYY5f9r1B/lCd9nz0g41MGx3OykJ2q1uLVKWdjhbkW3d2sqMbAdZ4iutNo3aJo5wSa5nlCyLpKfP+tFEcQ==`.
- **PASS** — actual published tarball contains the runtime JS, declaration file and fixture; its package manifest exposes the exact `./whatsapp-template-events` import/types targets and fixture subpath.
- **PASS** — release source commit `580de0a06dfc129f046cc311089a9bf9c18509c6` changes only `package.json` and `package-lock.json`; the task branch and `v2.5.1` tag are pushed; `git diff --check origin/main...HEAD` passes.
- Implementation tests, lint, typecheck and builds were deliberately **not repeated** during this publication task, as required by its release-only scope.

### Deviations

- Version `2.5.1` was published before the version choice was reconciled with the package's documented semver policy. The package README says an additive public API capability should receive a minor increment; the new subpath was released as a patch increment. A published npm version cannot be overwritten, so a corrective release requires architect approval and a higher version.

### Assumptions

- npmjs.org is the intended publication registry, consistent with the successful `npm publish` invocation and verified registry artifact.
- Commit `580de0a...` is the release source commit because it contains the release-only version metadata and precedes the registry publication; the package has no independent npm provenance attestation recorded here.

### Unresolved Issues

- Obtain an explicit architect decision on the semver-conforming corrective release version. The repository README's additive-capability guidance points to a minor increment; do not assume or publish a replacement version without that decision.
- In the next attempt, publish the approved higher version without changing source behavior, capture the command result, verify its actual registry tarball and export, and record the release commit. Treat `2.5.1` as superseded for consumer adoption.

### Architectural Concerns

Do not promote `ARCH-047-MESSAGING-001` or `ARCH-047-BACKGROUND-003` from `2.5.1`. The prerequisite acceptance and artifact export are verified, but the version choice conflicts with documented semver guidance; consumer adoption remains blocked until an architect-approved corrective release is published and this task is accepted.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.

## Execution Ownership Amendment

- Date: 2026-10-25
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-SHARED-002` for this ready agent-owned publication task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_shared`, coordinator, repository, dependency set, publication-only scope, acceptance criteria and validation requirements.
- Dependency verification: SHARED-001 is Complete with Architect Review Accepted (parent task record commit `7ba6066f`; current frontier reconciliation `9c616a4a`).
- Claim: This amendment does not increment or claim an attempt. The canonical launcher will claim Attempt 1 after worktree synchronization and dependency verification.

## Developer Self-Review - Changes Requested

### Review Decision

Attempt 1 review did not pass on 2026-10-26. The implementation is limited to package version metadata and the `2.5.1` artifact is published, but the release version is not accepted: the new public subpath is an additive capability and the package README says additive capabilities should use a minor version increment. `2.5.1` is only a patch increment from `2.5.0`.

### Required Corrections

- Obtain and record the architect's semver decision and approved corrective version before publishing again. The approved version must be higher than immutable npm version `2.5.1`; follow the repository's additive-capability minor-version guidance unless the architect records a justified exception.
- Publish the approved corrective version using the repository package workflow, with release-only metadata changes. Capture the command result and verify the exact version's published tarball contains the runtime module, type declarations and fixture export.
- Record the corrective release commit and registry evidence. Keep consumers blocked from adopting `2.5.1`; identify the architect-approved version as the consumer target.

### State Transition

Set `status: ready`, `executor: null`, `claimed_at: null`, and keep `attempt: 1`. No Attempt 2 is claimed by this review.
