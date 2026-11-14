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
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
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

- [ ] Verify acceptance/integration and select unused major version.
- [ ] Prepare metadata-only source/exact archive and approval identity checkpoint.
- [ ] Wait for explicit exact-archive public approval.
- [ ] Publish approved archive and verify independent registry receipt; push report.

## Interfaces / Contracts

Accepted Shared012 existing commerce/presentation and Node exports; consumers separately adopt published exact package after registry receipt.

## Dependencies

ARCH-075-SHARED-012 actual accepted source/parent integration.

## Enables

Admin009/BG014 final normal registry locks/npmci/CI; no automatic consumer/main/deploy action.

## Acceptance Criteria

- [ ] No implementation source changed; metadata-only major release exact accepted bytes.
- [ ] Explicit exact-archive approval precedes public publication.
- [ ] Actual registry version/latest/download identity matches approved archive.
- [ ] Mirrored isolation/source/report publication evidence complete; no live operations.

## Validation

- [ ] Prerequisite acceptance/integration/source metadata diff verified.
- [ ] Exact package version/member/byte/hash/private scan and approved identity verified.
- [ ] Publication command succeeds and independent registry tarball/version/latest/integrity match.

## Stop Condition

Return approval checkpoint while held; after approved publication verification set review, push report and STOP. No tests/build or consumer work.

## Implementation Notes

Normal launcher dedicated sibling worktrees. You are not alone; preserve others. Root owns Git main merges and all publication consent/live rollout. This task may prepare exact metadata/archive now once Ready; public release remains held.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Root relays exact publication approval only after concrete consumer checkpoints.

### Unresolved Issues

Dependency integrated: sourcef06cf317781bf584b62f2c286d06118f21e40123, parentb4ae79170ef3427d1744ef1151ef40e013ebbb78. New exact public approval pending.

### Architectural Concerns

Breaking export removal requires major version; no compatibility restoration just to avoid major.

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
