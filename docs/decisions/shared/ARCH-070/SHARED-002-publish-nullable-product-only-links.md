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
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-12T13:04:16Z
attempt: 1
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

Release only the immutable accepted5.13.3 artifact. Record exact version, hashes, npm publication receipt and canonical registry availability. No source/test changes or rebuild.

## Out of Scope

Background/MCP implementation, basket mutation URL relaxation, fabricated URLs, credentials, unrelated refactors and live customer sends.

## Requirements

Publish only the exact accepted5.13.3 tarball to the canonical public npm registry after Shared001 architect acceptance and developer implementation merge. No implementation changes or repeated test/build validation. Sole publisher; do not republish on CDN lag.

## Work Items

- [ ] Verify approved accepted artifact and version.
- [ ] Publish exact artifact once and verify registry evidence.
- [ ] Record receipt/integrity and return review without consumer integration.

## Interfaces / Contracts

Release the unchanged accepted public Shared presentation contract; Background pins this exact published version after acceptance.

## Dependencies

ARCH-070-SHARED-001; architect acceptance and developer merge must precede publication.

## Enables

ARCH-070-BACKGROUND-001 after actual public artifact availability and architect acceptance.

## Acceptance Criteria

- [ ] Exact accepted artifact published once to canonical npm registry; metadata and downloadable bytes match its approved hashes.
- [ ] No implementation source or test changes, rebuild or repeated implementation validation.
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
