---
id: ARCH-075-SHARED-015
architecture_id: ARCH-075
title: Publish accepted common layout structural reader
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
claimed_at: 2026-11-14T14:16:56Z
attempt: 1
depends_on:
  - ARCH-075-SHARED-014
enables: []
created: 2026-11-14
updated: 2026-11-14
---

# Publish accepted common layout structural reader

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Publish accepted common layout structural reader.

## Context

User requests compact one-bubble AI product lists and website in clickable caption footer instead of image header. Published6 reader currently hardcodes website/header and checkout placement business policy; correct ownership once, saved template remains source of truth. No live source/activation changes by agents.

## Scope

Release-only accepted source as proposed6.0.1; confirm semver before metadata. Produce immutable exact archive and public diff, no implementation changes. Public npm publication requires ROOT relay of explicit user approval for that exact archive; existing6.0.0 approval does not apply. Do not publish before concrete Admin/BG candidate validation. Verify registry downloaded bytes/SRI/latest and report.

## Out of Scope

Unrelated refactors, arbitrary user-programmable layouts, new database/infrastructure, main merges/live operations. Preserve all others work.

## Requirements

Release-only accepted source as proposed6.0.1; confirm semver before metadata. Produce immutable exact archive and public diff, no implementation changes. Public npm publication requires ROOT relay of explicit user approval for that exact archive; existing6.0.0 approval does not apply. Do not publish before concrete Admin/BG candidate validation. Verify registry downloaded bytes/SRI/latest and report.

## Work Items

- [x] Prepare release-only metadata and exact accepted-byte archive.
- [x] Reuse accepted014 behavior validation without rerunning implementation checks.
- [x] Record exact source/archive approval checkpoint.
- [ ] Obtain new root-relayed exact-archive approval, publish and verify actual registry receipt.

## Interfaces / Contracts

Shared owns technical structure/hash/render safety; applications own trusted bindings/placement/operational authority. Existing Shared6 published source immutable. Publication prerequisite ARCH-075-SHARED-014.

## Dependencies

ARCH-075-SHARED-014

## Enables

None; dependent promotions architect-owned.

## Acceptance Criteria

- [ ] Defined capability and owning-policy boundaries satisfied.
- [x] Accepted implementation bytes and integrity retained; no runtime behavior changes in release task.
- [ ] Required checks and exact immutable reports complete; no live/merge actions.

## Validation

Publication mechanics only; no repeat tests/lint/build/typecheck. Verify accepted prerequisite, metadata-only diff, exact archive, actual approved publish and registry identity.

## Stop Condition

After required work/checks publish matching source and parent report, set review and STOP. Do not continue dependent work.

## Implementation Notes

Normal moda-task canonical sibling isolation/claim required. You are not alone; do not revert others. Pending consumer tasks may perform preparatory source work only after explicit architect Ready amendment; final acceptance requires accepted published dependency. No unpublished sibling imports or fabricated registry lock.

## Publication authorization gate

Source014 accepted/integrated Sharedmain20aa60f0e9feb4c14ca909b7d7a68771e2b37bcf; parentmain d6d2f0078e05bddad7feb4f37157e6533e532255. Prepare exact6.0.1 metadata/archive from accepted bits without repeating implementation tests/build. Compare nonmetadata archive members against accepted6618d7 candidate. Send archive version/hash/size/SRI and source metadata checkpoint; do NOT publish until root explicitly relays new user approval for that exact archive after concrete consumer tests. Existing6approval is insufficient. Remain In Progress at held release gate.

## Completion Report

### Status

Prepared — awaiting new exact-archive publication approval. Task remains In Progress; publication and independent registry receipt are pending. No completion claim.

### Files Changed

- `package.json`, `package-lock.json`: only three root version entries6.0.0→6.0.1; no implementation/dependency changes.
- Metadata source `016f660d0a51469233b29552be3acfef637899e7`, draft PR https://github.com/kodjobaah/moda-interact-shared/pull/92.
- Task-owned `SHARED-015-release-manifest.json`: exact approval identity, comparison outcome and complete161-member SHA256/size manifest.

### Work Completed

- Normal prepared launcher claimed attempt1/codex at2026-11-14T14:16:56Z, durable claim `493e3ad54a279c7cabda3bb59ff6990ab2369e39`. Explicit Shared014 dependency Complete; source merge `20aa60f0e9feb4c14ca909b7d7a68771e2b37bcf` has the exact same source tree as accepted `a870977566babb35aac7b38e59efd194b64770b3`; integrated parent `d6d2f0078e05bddad7feb4f37157e6533e532255` is recorded by the task.
- Verified exact accepted test archive SHA256 `6618d7c97e99c1e75ab67240ba940a5a5eade2a37a5661de000f25c5ade3a97a`,161 files, and package metadata equal to accepted merged source before editing metadata.
- Patch6.0.1 appropriate: no exports/types/wire/mechanical contract removals; accepted014 corrects common reader application-policy ownership while preserving hash/frame integrity. Registry6.0.1 returned404 (unused); at preparation latest remains6.0.0 with prior approved integrity `sha512-8agnwKYGRaHpNjL5DxqKN2dqqag/OZwSHjtEAtYC9VEeZ8NdvXa86/u0clWs5/p55PwUB3PT5/yd6AEw+7tvvw==`.
- Ran `npm pack --ignore-scripts` from extracted accepted package after changing only package version; no rebuild/prepack/install or implementation tests/lint/type reruns. All161 members have identical names;160 nonmetadata files are byte-identical to accepted6618. Only package/package.json changes, solely version6.0.0→6.0.1, and matches committed source package metadata exactly. Root lock version entries only changed in source.

### Validation Results

Prepared target: `@modainteract/moda-interact-shared@6.0.1`, public access, registry `https://registry.npmjs.org`, dist-tag `latest` — publication NOT yet authorized.

- Exact immutable/read-only archive `/tmp/ARCH-075-SHARED-015/modainteract-moda-interact-shared-6.0.1.tgz`:965127 bytes, unpacked3327095 bytes,161 members.
- SHA256 `fd7b4a70d2a54da175556739074acdb5ee4487dc9c7e9c68a656717de3137aa2`.
- SHA512 hex `abf9d9654a432300a7682bf22536b6d345d1cebf4d46d0653230d5eb82acefbe35f41c3f78659c7edf577a8ba765fcd8f8696871f8d4e4b6f2c6c912d451fdd9`.
- npm SHA1/shasum `b0fd8cc7801bb49ba1d74aae30151b8e189895b6`.
- npm SRI `sha512-q/nZZUpDIwCnaCvyJTa200XRzr9NRtBlMjDV64Ks77419Bw/eGWcft9XeounZfzY+GlocfjU5LbyxskS1FH92Q==`.
- Release manifest SHA256 `ceacc531762b325809cdcba811815a436958c7062817a58655ef170ee99ffa96`; complete member manifest/receipt is adjacent `SHARED-015-release-manifest.json`. Local accepted/release manifests, npm pack JSON, registry-before snapshot, exact metadata diff and approval receipt are under `/tmp/ARCH-075-SHARED-015/`.
- Metadata-only source diff,161-member/160-byte comparison, semantic package version-only comparison, npm hash/SRI consistency and no private actual QA inputs/assets/backups: PASS. `git diff --check`: PASS.
- No implementation tests/build/lint/type repeated; accepted014 tests/installed/browser proof remains the validation baseline. No consumer work or fabricated registry lock.
- Canonical isolation: primary `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `moda-interact-workspace-task-ARCH-075-SHARED-015` reused, implementation `moda-interact-workspace.worktrees/ARCH-075-SHARED-015` created; mirrored branches `task/ARCH-075-SHARED-015`. Parent initial `c63366b0fffe9c9c7a3ba809e745277307eca794`; implementation initial `20aa60f0e9feb4c14ca909b7d7a68771e2b37bcf`. Both remote task fast-forward not-needed/origin-main already-current. Recursive implementation sync/update passed, ready/no entries. No shared checkout, other task, main or gitlink writes.

### Deviations

None. Inherited implementation-regression boilerplate is fulfilled by accepted014 behavior validation; this publication task explicitly forbids repeating those checks. Publication gate supersedes the generic review stop until approved publication/registry receipt completes.

### Assumptions

Root obtains concrete consumer proofs and relays NEW explicit user approval for this exact6.0.1 archive/hash/public/latest target. Existing6.0.0 approval does not authorize6.0.1. Root owns metadata/source/parent main integration and all live operations.

### Unresolved Issues

PUBLICATION HOLD: no new exact-archive user approval has been relayed. No npm publish command has run; actual registry version/latest/download receipt remains deliberately pending. Task stays In Progress at this prepared checkpoint.

### Architectural Concerns

Published6.0.0 remains immutable. Do not rebuild/repack/replace this archive after approval. Explicit root-relayed approval is required before publishing these exact bytes with scripts disabled; independently download and verify actual registry bytes/SRI/version/latest afterward. Consumer business policy and deployment readiness remain separately owned.

## Architect Review

### Review Status

Pending

### Review Notes

Prepublication checkpoint reviewed: exact016f660d0a51469233b29552be3acfef637899e7 changes only package/lock version metadata6.0.1. Independently hashed immutable965127-byte archive fd7b4a70d2a54da175556739074acdb5ee4487dc9c7e9c68a656717de3137aa2;160nonmetadata identity proof reviewed. Metadata source is acceptable for root integration independently; task remains In Progress/Pending final review, NOT publication Accepted/Complete. New explicit public approval still required.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

Root may merge exact metadata; publish only after actual explicit approval and verify registry receipt. No implementation revalidation needed.
