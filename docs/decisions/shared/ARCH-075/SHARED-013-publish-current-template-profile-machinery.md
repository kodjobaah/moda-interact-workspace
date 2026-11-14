---
id: ARCH-075-SHARED-013
architecture_id: ARCH-075
title: Publish accepted current template-profile machinery as a major release
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-14T02:44:01Z
attempt: 1
depends_on:
  - ARCH-075-SHARED-012
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Publish accepted current template-profile machinery as a major release

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Prepare and separately authorize publication of the exact already-accepted current-only template-profile package.

## Context

Shared012 removes previously public fixed composite APIs; this is breaking and requires a major release. Root guidance is6.0.0 subject to registry availability. Published5.13.11 must never be overwritten/unpublished. User has NOT approved this new public release yet.

## Scope

Release metadata/version only, exact accepted-dist archive packaging without rebuilding, artifact identity/manifest comparison, gated approved publication and independent registry download verification.

## Out of Scope

Implementation changes, new runtime behavior, tests/lint/type/build reruns, consumer code, main/gitlink merge or live activation.

## Requirements

- Prerequisite Shared012 must be Complete/Accepted and actually integrated before normal claim. Accepted source59068290eb69506fd7a5d248c5ed359cfb98163d; accepted test archive SHA256029bdf8c2016ffe926d54e3c79ab759d51ad51df234297712a9f1af43a2a0929,965707B/161files. Verify actual final merged source/accepted dist before metadata work; do not regenerate implementation.
- Inspect registry version availability, prepare major6.0.0 if unused; if taken return version conflict to architect. Only root package version metadata may change. npm pack/publish use --ignore-scripts so accepted dist is not rebuilt.
- Compare every packed file with exact accepted artifact; same members and byte-identical nonmetadata files, package JSON only approved version change. Produce immutable exact archive size/SHA256/SHA512/npm shasum/integrity/manifest and source draft before approval prompt. No private actual QA assets.
- PUBLICATION HOLD: source/archive preparation is authorized, but public npm/latest publication requires ROOT-RELAYED EXPLICIT USER approval of exact version/archive/hash. Root first obtains concrete tested Admin009 and BG014 same-artifact source checkpoints. Do not infer consent from earlier5.13.11 approval or current implementation authorization. Keep In Progress checkpoint while held, no final Complete claim.
- Root may integrate reviewed metadata separately before publication. Publish exact approved archive to registry.npmjs.org/public/latest only after explicit authorization; independently download actual registry tarball and verify version/latest/full bytes/integrity. No repack/rebuild between approval/publication.
- No implementation tests/lint/type/build repeated. If code fix needed stop and return architect; do not fix within publication task.

## Work Items

- [x] Verify acceptance/integration and select unused major version.
- [x] Prepare metadata-only source/exact archive and approval identity checkpoint.
- [ ] Wait for explicit exact-archive public approval.
- [ ] Publish approved archive and verify independent registry receipt; push report.

## Interfaces / Contracts

Accepted Shared012 existing commerce/presentation and Node exports; consumers separately adopt published exact package after registry receipt.

## Dependencies

ARCH-075-SHARED-012 actual accepted source/parent integration.

## Enables

Admin009/BG014 final normal registry locks/npmci/CI; no automatic consumer/main/deploy action.

## Acceptance Criteria

- [x] No implementation source changed; metadata-only major release exact accepted bytes.
- [ ] Explicit exact-archive approval precedes public publication.
- [ ] Actual registry version/latest/download identity matches approved archive.
- [ ] Mirrored isolation/source/report publication evidence complete; no live operations.

## Validation

- [x] Prerequisite acceptance/integration/source metadata diff verified.
- [x] Exact package version/member/byte/hash/private scan and prepared approval identity verified.
- [ ] Publication command succeeds and independent registry tarball/version/latest/integrity match.

## Stop Condition

Return approval checkpoint while held; after approved publication verification set review, push report and STOP. No tests/build or consumer work.

## Implementation Notes

Normal launcher dedicated sibling worktrees. You are not alone; preserve others. Root owns Git main merges and all publication consent/live rollout. This task may prepare exact metadata/archive now once Ready; public release remains held.

## Completion Report

### Status

Prepared — awaiting exact-archive public approval. Task remains In Progress; publication and registry receipt are pending. This is an approval checkpoint, not a completion claim.

### Files Changed

- Implementation `package.json`, `package-lock.json`: root release version5.13.11→6.0.0 only (three metadata entries); no dependency/runtime/source changes.
- Metadata commit `dcfbfef99935709dc485fad003dbfa7164a6203b`, draft source PR https://github.com/kodjobaah/moda-interact-shared/pull/90.
- Task-owned `SHARED-013-release-manifest.json`: immutable candidate identity, byte-comparison result and full161-member SHA256/size manifest.

### Work Completed

- Normal deterministic launcher claimed attempt1, executor codex, at2026-11-14T02:44:01Z; durable pushed claim `21327d20fa353f0bc32bb8876c9c38a71cee4df9`.
- Accepted Shared012 source `59068290eb69506fd7a5d248c5ed359cfb98163d` and actual merged `f06cf317781bf584b62f2c286d06118f21e40123` have identical source trees. Launcher proved dependency Complete and integrated parent `b4ae79170ef3427d1744ef1151ef40e013ebbb78` is recorded by the task. Exact accepted candidate SHA256 `029bdf8c2016ffe926d54e3c79ab759d51ad51df234297712a9f1af43a2a0929` reverified before extraction; its package metadata matches merged source.
- Registry6.0.0 lookup returned404 (unused); latest remains5.13.11 with prior approved integrity `sha512-rKkT3jdiPMVllTP270KUKQon+kcH5FcxpEojrRmPjhhVVm2bIqYsLtWewhlMa8jLXjToSHwsTwmVhoOxAwKBEA==`. Prior public5.13.11 is unchanged.
- `npm pack --ignore-scripts --pack-destination /tmp/ARCH-075-SHARED-013 --json` ran from extracted accepted package after changing only package version. No build/install/prepack implementation code was executed; accepted dist, maps, declarations, font/license/cmap and fixtures are reused exactly.
- Both archives have exactly the same161 members.160 nonmetadata files are byte-identical. Only `package/package.json` differs, solely `version`; its bytes match committed metadata package JSON. Source diff is only package root/lock version entries. No implementation tests/lint/type/build repeated.

### Validation Results

Prepared public approval target: `@modainteract/moda-interact-shared@6.0.0`, registry `https://registry.npmjs.org`, access `public`, dist-tag `latest`.

- Exact archive: `/tmp/ARCH-075-SHARED-013/modainteract-moda-interact-shared-6.0.0.tgz` (read-only after preparation),965706 bytes,161 files; unpacked size3330453 bytes.
- SHA256: `49802947a11110f9cbd211b9a10849b019c4ce10d8519416977add0564fecfc8`.
- SHA512 hex: `f1a827c0a60645a1e93632f90f1a8a37676aa9a83f399c121e3b4402d602f5511e67c35dbd76bcebfbb47255ace7fa79e4fc140773d3e7fc9de80130fbbb6fbf`.
- npm SHA1/shasum: `d4ee0ab635e55a1f34c82e27c1afb9d2791ec6be`.
- npm integrity: `sha512-8agnwKYGRaHpNjL5DxqKN2dqqag/OZwSHjtEAtYC9VEeZ8NdvXa86/u0clWs5/p55PwUB3PT5/yd6AEw+7tvvw==`.
- Release member manifest SHA256: `8995df2d9465b1271f044099f800af7a29ea0afc35dcc66364ac228043339730`; durable full manifest/receipt is `SHARED-013-release-manifest.json` beside this task. Local accepted/release manifests, comparison receipt, npm pack result and registry-before snapshot remain under `/tmp/ARCH-075-SHARED-013/`.
- Exact member/byte/semantic metadata comparison and package JSON/source metadata equality: PASS. Private asset scan: no actual logo/product/header files, private QA images or backups. `git diff --check`: PASS.
- Release semantics intentionally use a major version for removed public fixed composite APIs. Existing accepted implementation validation belongs to Shared012 and is not rerun in this release-only task.
- Prepared launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `moda-interact-workspace-task-ARCH-075-SHARED-013` reused, implementation `moda-interact-workspace.worktrees/ARCH-075-SHARED-013` created, both on mirrored `task/ARCH-075-SHARED-013`. Remote task fast-forward not-needed and origin/main already-current in both repositories. Recursive sync/update passed, submodule statusready/no entries. No shared checkout/main/gitlink/other task changes.

### Deviations

None. Metadata version6.0.0 is a deliberate major release for accepted breaking export removal; the accepted unpublished5.13.11-named test artifact is only the byte baseline, never republished under5.13.11.

### Assumptions

Root obtains concrete Admin009 and BG014 same-artifact checkpoints and relays NEW explicit user approval of this exact6.0.0 archive/hash/public registry/latest target. Root may independently integrate metadata before publication; this agent does not merge main.

### Unresolved Issues

PUBLICATION HOLD: explicit exact-archive user approval has not been relayed. No npm publish command was run. Registry publication/version/latest/download verification is deliberately pending, and task remains In Progress.

### Architectural Concerns

Do not rebuild/repack/change this archive after approval. Public5.13.11 remains immutable. After explicit root authorization, publish exactly this archive with scripts disabled, then independently verify actual registry tarball bytes/version/latest/integrity before submitting final review.

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

No architecture/live completion claim.
