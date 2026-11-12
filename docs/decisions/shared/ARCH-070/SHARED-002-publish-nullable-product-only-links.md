---
id: ARCH-070-SHARED-002
architecture_id: ARCH-070
title: Publish accepted nullable product-only link artifact
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
  - ARCH-070-SHARED-001
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Publish accepted nullable product-only link artifact

## Architecture

ARCH-070; docs/architecture/ARCH-070-verified-recommendation-terminal-turn-recovery.md; coordinator moda_architect.

## Objective

Publish accepted nullable product-only link artifact without relaxing existing production security or lifecycle guarantees.

## Context

MCP valid catalogue products can have onlineStoreUrl null, but existing Shared recommendation schema/render requires a link. Background must consume a canonical safe contract rather than weaken verification.

## Scope

Shared recommendation presentation schema/render and directly related tests/types; approved5.13.3 package metadata. Publication task scope is only accepted-artifact release mechanics.

## Out of Scope

Background/MCP implementation, basket mutation URL relaxation, fabricated URLs, credentials, unrelated refactors and live customer sends.

## Requirements

Publish only the exact accepted5.13.3 tarball to the canonical public npm registry after Shared001 architect acceptance and developer implementation merge. No implementation changes or repeated test/build validation. Sole publisher; do not republish on CDN lag.

## Work Items

- [ ] Verify approved accepted artifact and version.
- [ ] Publish exact artifact once and verify registry evidence.
- [ ] Record receipt/integrity and return review without consumer integration.

## Interfaces / Contracts

Consume published Shared contracts and existing MCP product evidence / durable conversation lifecycle. No new wire or schema contract is authorized. Cross-repository gaps return to architect.

## Dependencies

ARCH-070-SHARED-001; architect acceptance and developer merge must precede publication.

## Enables

Developer integration and production verification after architect acceptance of both tasks.

## Acceptance Criteria

- [ ] Requirements demonstrated with deterministic positive and negative regression tests.
- [ ] Existing tenant, domain, message identity and lifecycle guarantees preserved.
- [ ] No duplicate delivery, live test send, secret logging or unrelated changes.
- [ ] Completion Report records canonical launcher packet, physical isolation, synchronization and recursive submodule evidence.

## Validation

- [ ] Verify prerequisite Accepted/Complete, exact artifact hashes/version, publication receipt and canonical registry version/integrity and distributable artifact. No implementation tests/lint/typecheck/build reruns.
- [ ] Exact changed-file scope and secret hygiene review.

## Stop Condition

Complete owned work and required validation, set review, return report and STOP. Do not merge, deploy or begin another task.

## Implementation Notes

You are not alone in the codebase. Preserve others' changes. Use the prepared dedicated mirrored worktrees and task branch. Verify actual package scripts before running checks. Existing structured semantic logs suffice; do not introduce competing logging or repeated provider work as a diagnostic mechanism.

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

Existing runtime evidence needs corroboration in source and fixtures.

### Unresolved Issues

None known beyond investigation.

### Architectural Concerns

Return contract or schema gaps before implementing outside scope.

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
