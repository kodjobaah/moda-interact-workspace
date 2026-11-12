---
id: ARCH-070-SHARED-006
architecture_id: ARCH-070
title: Publish accepted typed referral reason contract
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
claimed_at: 2026-11-12T15:21:27Z
attempt: 1
depends_on:
  - ARCH-070-SHARED-005
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Publish accepted typed referral reason contract

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Publish accepted typed referral reason contract within existing strict final-envelope and bounded execution guarantees.

## Context

Fresh production version7 entered selection repair but failed final schema at referralReason invalid_value. Exact raw invalid value is unknown and must not be assumed. User explicitly authorized correcting referralReason, testing, commit/push/merge and fresh production recommendation/footer verification. All previous eight accepted tasks remain valid; architecture stays In Progress.

## Scope

Only exact immutable accepted5.13.5 artifact canonical public npm publication and actual downloadable-byte verification.

## Out of Scope

Unknown-value normalization, schema weakening, missing-field dropping, extra repair/queue loops, automatic selections, provider/model switching, credentials, unrelated refactors, production replay and unsolicited Meta sends.

## Requirements

After accepted prerequisite and developer merge, sole-publish exact accepted5.13.5 tarball once to existing canonical public npm package/destination. No source changes, rebuild or implementation validation reruns. Exact canonical metadata/download hashes required; no republish on propagation lag. If approval review questions public egress, establish existing public source repository, artifact whitelist/publishConfig and same destination; do not use an alternate execution channel.

## Work Items

- [ ] Establish owned source/release behavior and preserve relevant regression evidence.
- [ ] Complete only the bounded owned correction or exact artifact release.
- [ ] Record required validation, exact hashes/heads and return review.

## Interfaces / Contracts

Shared owns canonical finalResponse provider schema, validator and bounded runner. Background consumes published @modainteract/moda-interact-shared package and retains tenant/host/evidence/delivery policy. No new wire/schema version or mandatory-referral change authorized.

## Dependencies

ARCH-070-SHARED-005. Publication additionally requires developer implementation merge; consumer starts only after actual public artifact integrity acceptance.

## Enables

Next ARCH-070 publication/consumer gate, then root/developer fresh production verification.

## Acceptance Criteria

- [ ] Requirements and required validation pass without weakening strict validation or bounded execution.
- [ ] No private prompts/prose, raw invalid values, customer data or secrets in diagnostics/probes.
- [ ] No unrelated files or implementation-owner boundary violation.
- [ ] Launcher mirrored physical isolation, synchronization and recursive submodule evidence recorded.

## Validation

- [ ] Prerequisite accepted/version/merge, exact artifact hashes, successful sole canonical npm receipt and matching metadata plus actual public downloaded bytes; unchanged source. No tests/lint/types/build repetitions.
- [ ] Diff scope/hygiene and secret validation.

## Stop Condition

When owned work and required validation are complete, set review, report and STOP. No follow-on task, merge/deploy or publication outside explicit task scope.

## Implementation Notes

You are not alone; preserve others' changes. Use canonical prepared packet paths and matching mirrored branch. Read actual package scripts; do not rerun accepted implementation validation in publication. Existing shared structured logger only if diagnostics needed. Exact historical invalid referral value remains unconfirmed.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

Historical exact raw invalid referralReason is unavailable.

### Unresolved Issues

None beyond owned correction/release.

### Architectural Concerns

Return cross-owner gaps before modifying outside scope.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
