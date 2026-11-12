---
id: ARCH-069-BACKGROUND-001
architecture_id: ARCH-069
title: Adopt chronological model serialization
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-069-SHARED-002
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Adopt chronological model serialization

## Architecture

ARCH-069 — `docs/architecture/ARCH-069-chronological-commerce-model-inputs.md`; coordinator moda_architect.

## Objective

Consume the published chronological Shared model adapter in Background without changing delivery or turn lifecycle contracts.

## Context

Production's snowboard turn returned an internal-looking indicator. The model serializer independently places current context before prior history. This task addresses only its bounded owning outcome; the exact indicator cause requires evidence and must not be asserted merely from a passing structural test.

## Scope

Repository: `moda-interact-background`.

- Pin the approved published Shared 5.13.2 package and matching lockfile integrity.
- Add or adjust a focused consumer regression proving older history precedes the current snowboard question at the actual model boundary.
- Preserve admission, STOP/consent, tenant ownership, existing message/usage idempotency and delivery behavior.
- Support coordinator-owned read-only/no-send reproduction and record how production verification will be performed; do not send or replay production messages as an implementation test.

## Out of Scope

Moderation/STOP changes, sentinel blocklists, provider/model switching, schema or queue changes, credential edits, production message replay, unrelated dependency changes and another repository's implementation.

## Requirements

- Pin the approved published Shared 5.13.2 package and matching lockfile integrity.
- Add or adjust a focused consumer regression proving older history precedes the current snowboard question at the actual model boundary.
- Preserve admission, STOP/consent, tenant ownership, existing message/usage idempotency and delivery behavior.
- Support coordinator-owned read-only/no-send reproduction and record how production verification will be performed; do not send or replay production messages as an implementation test.

## Work Items

- [ ] Pin the approved published Shared 5.13.2 package and matching lockfile integrity.
- [ ] Add or adjust a focused consumer regression proving older history precedes the current snowboard question at the actual model boundary.
- [ ] Preserve admission, STOP/consent, tenant ownership, existing message/usage idempotency and delivery behavior.
- [ ] Support coordinator-owned read-only/no-send reproduction and record how production verification will be performed; do not send or replay production messages as an implementation test.

## Interfaces / Contracts

Existing Shared ModelRequest/ModelStep and `@modainteract/moda-interact-shared/commerce/model/node`; no wire schema changes. Background remains host/lifecycle owner. Shared implementation owner: ARCH-069-SHARED-001.

## Dependencies

- ARCH-069-SHARED-002

## Enables

None

## Acceptance Criteria

- [ ] Pin the approved published Shared 5.13.2 package and matching lockfile integrity.
- [ ] Add or adjust a focused consumer regression proving older history precedes the current snowboard question at the actual model boundary.
- [ ] Preserve admission, STOP/consent, tenant ownership, existing message/usage idempotency and delivery behavior.
- [ ] Support coordinator-owned read-only/no-send reproduction and record how production verification will be performed; do not send or replay production messages as an implementation test.

## Validation

- [ ] Inspect package scripts and run the relevant model/host/turn integration unit checks.
- [ ] Run Background typecheck, changed-file lint and required full CI suite.
- [ ] Use disposable PostgreSQL/Redis only if the scoped regression requires persistence; never inherited live DATABASE_URL/REDIS_URL.
- [ ] Confirm dependency resolves from the published registry artifact and no sibling source imports are introduced.

## Stop Condition

After the scoped work, acceptance criteria and required validation pass, complete this task's report, set review, publish both mirrored task branches, return to moda_architect and STOP. Do not begin dependent work, merge main or send a production message.

## Implementation Notes

Use launcher-resolved physical parent and implementation task worktrees for the entire attempt. Preserve unrelated changes. All no-send/live diagnostic artifacts must be protected and excluded from Git; no credentials or private customer prompt payloads in reports. Publication task validation is release mechanics only.

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

Existing request schemas and pinned-release contracts remain unchanged.

### Unresolved Issues

Exact indicator causality and production answer verification remain coordinator-owned evidence gates.

### Architectural Concerns

None beyond the bounded ordering defect.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
