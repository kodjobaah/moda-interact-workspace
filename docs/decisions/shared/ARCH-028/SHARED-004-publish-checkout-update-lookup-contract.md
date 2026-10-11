---
id: ARCH-028-SHARED-004
architecture_id: ARCH-028
title: Publish compatible Shopify checkout-update lookup-context contract
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: blocked
priority: 29
executor: copilot
claimed_at: 2026-10-11T13:32:19Z
attempt: 1
depends_on:
  - ARCH-028-SHARED-003
enables:
  - ARCH-028-BACKGROUND-012
  - ARCH-028-SHOPIFY-001
created: 2026-10-08
updated: 2026-10-11
---

# Publish compatible Shopify checkout-update lookup-context contract

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Publish one exact registry version containing the accepted SHARED-003 Shopify checkout-update v2/v3 parser and contract, without modifying runtime implementation or consumer repositories.

## Context

SHARED-003 must be Complete and architect-accepted before this publication task executes. SHARED-002 already published the separate WhatsApp provider-status contract. This task follows that release rather than racing it, then makes the separately reviewed Shopify contract available to Background and Shopify consumer/producer tasks.

## Scope

- Verify SHARED-003 is Complete and architect-accepted, recording its implementation commit.
- Establish checked-in package version and actual public npm registry baseline, stopping if they disagree.
- Select exactly one approved compatible patch version, change only release metadata (normally `package.json` and lockfile) and publish using the repository's normal process.
- Verify exact package version, registry integrity, tarball and clean-install runtime imports of the accepted Shopify subpath contract.
- Record registry/published-version evidence for BACKGROUND-012 and SHOPIFY-001.

## Out of Scope

- Modifying Shared `src` or tests; fixing implementation defects in the publication branch.
- Rerunning unit tests, lint, typecheck or builds already accepted in SHARED-003.
- Changing WhatsApp schema, rolling back SHARED-002, changing consumer/producer repositories.
- Performing Background or Shopify implementation work.

## Requirements

- [x] SHARED-003 must have status Complete and Architect Review Accepted.
- [ ] Checked-in and registry version baseline must agree before patch bump.
- [ ] Release is one compatible patch and contains accepted SHARED-003 Shopify exports.
- [x] No implementation source is modified, and no implementation validation is rerun.
- [ ] Exact published version and clean-install imports are proven.

## Work Items

- [x] Record accepted SHARED-003 implementation SHA and package baseline.
- [ ] Apply allowed release metadata patch bump and publish once.
- [ ] Validate npm registry version/integrity and the clean-install Shopify exports.
- [ ] Record publication evidence in Completion Report.

## Interfaces / Contracts

Publishes `@modainteract/moda-interact-shared/shopify` containing accepted SHARED-003 v2/v3 checkout-update contracts. BACKGROUND-012 consumes first; SHOPIFY-001 emits new v3 events only after Background acceptance. The separate SHARED-002 WhatsApp contract remains intact.

## Dependencies

- `ARCH-028-SHARED-003`

## Enables

- `ARCH-028-BACKGROUND-012`
- `ARCH-028-SHOPIFY-001`

## Acceptance Criteria

- [ ] Accepted prerequisite implementation is verified.
- [ ] A single exact patch release is available from target npm registry.
- [ ] Clean install resolves the version and runtime exports; package integrity is recorded.
- [ ] No unauthorized source change or code-validation run occurs in publication task.

## Validation

Release mechanics only: version baseline, patch metadata, npm publish, registry/integrity/tarball lookup, clean installation/import of the exact published artifact and `git diff --check`. Do not rerun SHARED-003 tests, typecheck or build.

## Stop Condition

Complete the publication report, set status `review`, return to `moda_architect`, and STOP. Never continue into consumer integration.

## Implementation Notes

If publication reveals an implementation defect or version-baseline disagreement, stop and return to architect for same-task correction; do not modify implementation source here. Credentials are supplied securely outside source control.

## Completion Report

### Status

Blocked before publication: the checked-in package/lockfile baseline is `1.3.5`, while the current public npm registry version is `1.4.0`. The task requires stopping when these baselines disagree. No release metadata was changed and nothing was published.

### Files Changed

Parent task report only: `docs/decisions/shared/ARCH-028/SHARED-004-publish-checkout-update-lookup-contract.md`. The implementation worktree is unchanged.

### Work Completed

Verified prerequisite `ARCH-028-SHARED-003` is `complete` with Architect Review `Accepted — Attempt 1 (2026-10-11)`. Accepted implementation SHA: `fbd05b232e708e551dd275e6f09bbce7d5200edd`.

Checked-in `package.json` and `package-lock.json` both declare `@modainteract/moda-interact-shared` version `1.3.5`. Read-only npm registry queries returned current version `1.4.0` with integrity `sha512-sZgPFsXHNZXhCvz+CU3GvF1cG7+FGE8zEBadHF8vrQbblnnfHeYdREASPObkEiNqPnZrXV/wfu0bOF/FviLSyw==` and tarball `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-1.4.0.tgz`. Exact registry lookup for `1.3.5` also succeeds with integrity `sha512-HhqY27SXT0fwJM2XEfTmmqQS2nnFw3CnLxoKO2JgJdilZQ4Oy3pZaJtvInv71Hvsgcl3/4nmPDLfnOJlTcdTBg==` and tarball `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-1.3.5.tgz`.

Because the checked-in and current registry baselines disagree, stopped before selecting a patch version, editing `package.json`/lockfile, publishing, or running clean-install checks. No Shared source/tests/build/typecheck or consumer repository was changed or validated in this publication task.

### Validation Results

- `npm view @modainteract/moda-interact-shared version dist.integrity dist.tarball --json`: current public registry record is `1.4.0` with the integrity/tarball above.
- `npm view @modainteract/moda-interact-shared@1.3.5 version dist.integrity dist.tarball --json`: exact checked-in release exists with the integrity/tarball above.
- Checked `package.json` and `package-lock.json`: both `1.3.5`.
- Verified SHARED-003 task report says `status: complete`; its Architect Review says `Accepted — Attempt 1` and identifies implementation SHA `fbd05b232e708e551dd275e6f09bbce7d5200edd`.
- `git diff --check`: passed; no implementation worktree changes were present.
- No npm publish, clean install, tarball extraction, or runtime import was attempted because the required version-baseline gate failed.

### Deviations

Publication and clean-install verification were not performed. The explicit task instruction requires stopping and returning to Architect when the checked-in and registry version baselines disagree.

### Assumptions

None.

### Unresolved Issues

Architect must resolve the checked-in `1.3.5` versus registry-current `1.4.0` discrepancy and direct the next same-task action. Publishing from the stale checked-in baseline could duplicate or mis-version already published package contents, so no version bump was guessed.

### Architectural Concerns

No source or registry mutation was made. The release cannot safely continue until Architect reconciles the package baseline and confirms whether `1.4.0` is the accepted SHARED-003 release or another publication state.

### Attempt 1 Worktree and Launcher Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; not derived from a previous task worktree.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-SHARED-004`, branch `task/ARCH-028-SHARED-004`; created for this task.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-SHARED-004`, branch `task/ARCH-028-SHARED-004`; created for this task.
- Parent sync: remote task fast-forward `not-needed`; `origin/main` incorporation `already-current`; prepared head `d45807eda72fd5a3e57a629787035549adcc8613`.
- Implementation sync: remote task fast-forward `not-needed`; `origin/main` incorporation `already-current`; prepared head `e3416bdedbab7b241481e099d2f7d780f876cef8`.
- Recursive implementation submodule sync and update both passed; status `ready`; no submodule entries were present.
- Durable Attempt 1 claim commit `54e044ff0e24c4f409b1b373df2203867c36e985` was committed and pushed. No shared/default checkout, foreign task worktree, or implementation source was modified.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
