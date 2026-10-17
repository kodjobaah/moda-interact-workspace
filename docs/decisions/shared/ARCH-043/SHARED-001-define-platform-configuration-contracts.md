---
id: ARCH-043-SHARED-001
architecture_id: ARCH-043
title: Define allowlisted platform configuration schemas
task_kind: implementation
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
depends_on: []
enables:
- ARCH-043-SHARED-002
created: '2026-10-17'
updated: '2026-10-17'
---

# Define allowlisted platform configuration schemas

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Proposed schema/key contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-shared` / `moda_shared`.
- Portable definition only: **defined but not materialised**; task worktrees, claims and Git commits must be established by normal task launcher.

## Objective

Define strict, versioned validators for the six approved **non-secret** policy JSON shapes and safe public key metadata; sealed-secret envelope codecs belong to `ARCH-043-SHARED-003`.

## Context

A generic JSON column does not mean arbitrary data. Every reader/writer must import one canonical validated shape.

## Scope

- Provide key allowlist and exact closed schemas for `woo.couponSync`, `merchantKnowledge.upload`, `speech.transcription`, `support.translation`, `commerce.preview` and `admin.grafana`.
- Define browser-safe key metadata and non-secret field descriptions; protect server-only values from browser output as required.
- Export parsers, default policies where proven safe, and shape compatibility vectors from documented existing bounds.

## Out of Scope

- No sealed secret cryptography (owned by SHARED-003), source consumer refactor, migration or package publication within this task.

## Requirements

- Reject unknown keys, unexpected fields, secret-shaped strings in prohibited fields and out-of-range integers.
- Preserve meaning and units from existing readers; no direct dependency on Prisma, app secrets or database sessions.
- R2 endpoint and bucket validation must not weaken existing service-specific SSRF/allowlist controls.

## Work Items

- [ ] Provide key allowlist and exact closed schemas for `woo.couponSync`, `merchantKnowledge.upload`, `speech.transcription`, `support.translation`, `commerce.preview` and `admin.grafana`.
- [ ] Define browser-safe key metadata and non-secret field descriptions; protect server-only values from browser output as required.
- [ ] Export parsers, default policies where proven safe, and shape compatibility vectors from documented existing bounds.
- [ ] Record actual files changed, validation results, worktree isolation and Completion Report; stop at Review.

## Interfaces / Contracts

- `PlatformConfiguration` and `PlatformConfigurationAudit` are owned by `ARCH-043-DATABASE-001`; schema supports typed non-secret objects and sealed envelopes; environment-scoped and redacted in audit.
- Closed JSON shapes and validators are owned by `ARCH-043-SHARED-001` and published in `ARCH-043-SHARED-002` through `@modainteract/moda-interact-shared`.
- Existing billing, tenant, provider credential and bootstrap contracts retain their established owners.

## Dependencies

None

## Enables

- `ARCH-043-SHARED-002`

## Acceptance Criteria

- [ ] Reject unknown keys, unexpected fields, secret-shaped strings in prohibited fields and out-of-range integers.
- [ ] Preserve meaning and units from existing readers; no direct dependency on Prisma, app secrets or database sessions.
- [ ] R2 endpoint and bucket validation must not weaken existing service-specific SSRF/allowlist controls.
- [ ] The bounded task implementation passes the specified validation without regressions to existing domain configuration.

## Validation

- [ ] Unit tests of six keys and strict rejection
- [ ] Package typecheck, lint, build and export tests

## Stop Condition

Complete the defined scope and required validation, update the task and Completion Report to Review, return to `moda_architect`, and STOP. No execution of enabled tasks and no `_index.md` edits.

## Implementation Notes

- Preserve the current service boundaries; any new cross-service contract goes into the published Shared package, not a parallel local validator.
- Changes to shared generic logging, if needed, must use `@modainteract/moda-interact-shared/logging`.
- Use launcher-resolved dedicated task worktrees and start-of-attempt synchronisation evidence.

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

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation, validation evidence and architect decision.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not yet assessed.

### Follow-up

None
