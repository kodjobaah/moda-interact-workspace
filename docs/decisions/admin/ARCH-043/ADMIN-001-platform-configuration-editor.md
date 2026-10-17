---
id: ARCH-043-ADMIN-001
architecture_id: ARCH-043
title: Manage allowlisted platform settings and history
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-043-DATABASE-001
- ARCH-043-SHARED-002
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Manage allowlisted platform settings and history

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Proposed schema/key contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-admin` / `moda_admin`.
- Portable definition only: **defined but not materialised**; task worktrees, claims and Git commits must be established by normal task launcher.

## Objective

Provide a typed, version-controlled Moda Admin editor for **non-secret** policy keys only; secured secret administration belongs to `ARCH-043-ADMIN-002`.

## Context

The database stores only non-secret configurable values; admins need safe controlled edit/review.

## Scope

- Add platform configuration navigation and grouped editor for six approved keys, with field descriptions, units, validation and safe defaults.
- Add server-side privileged read/write handlers scoped to trusted environment, with strict Shared schemas, monotonic optimistic CAS and transactional audit records.
- Display current version, change history, editor actor and reason, with inline conflicts and disable duplicate saves.
- Consume `admin.grafana` for operational navigation links, without modifying OTLP/Loki exporter configuration.

## Out of Scope

- No plaintext or sealed-secret browser listing, secret rotation, auth-bootstrap wiring, credentials, or `_index.md` edits.

## Requirements

- Verify privilege server-side; hide sensitive values and never accept secret material.
- Request older than most recent clear must fail stale CAS.
- Never offer production values to the development environment.
- Authoritative audit must cover create/edit/clear in same transaction, with no duplicate submissions.

## Work Items

- [ ] Add platform configuration navigation and grouped editor for six approved keys, with field descriptions, units, validation and safe defaults.
- [ ] Add server-side privileged read/write handlers scoped to trusted environment, with strict Shared schemas, monotonic optimistic CAS and transactional audit records.
- [ ] Display current version, change history, editor actor and reason, with inline conflicts and disable duplicate saves.
- [ ] Consume `admin.grafana` for operational navigation links, without modifying OTLP/Loki exporter configuration.
- [ ] Record actual files changed, validation results, worktree isolation and Completion Report; stop at Review.

## Interfaces / Contracts

- `PlatformConfiguration` and `PlatformConfigurationAudit` are owned by `ARCH-043-DATABASE-001`; schema supports typed non-secret objects and sealed envelopes; environment-scoped and redacted in audit.
- Closed JSON shapes and validators are owned by `ARCH-043-SHARED-001` and published in `ARCH-043-SHARED-002` through `@modainteract/moda-interact-shared`.
- Existing billing, tenant, provider credential and bootstrap contracts retain their established owners.

## Dependencies

- `ARCH-043-DATABASE-001`
- `ARCH-043-SHARED-002`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Verify privilege server-side; hide sensitive values and never accept secret material.
- [ ] Request older than most recent clear must fail stale CAS.
- [ ] Never offer production values to the development environment.
- [ ] Authoritative audit must cover create/edit/clear in same transaction, with no duplicate submissions.
- [ ] The bounded task implementation passes the specified validation without regressions to existing domain configuration.

## Validation

- [ ] Admin handler authorisation, reject key/field/secret tests
- [ ] Concurrency create-clear-replay test
- [ ] UI component validation, history and conflict tests
- [ ] Typecheck/lint/build

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
