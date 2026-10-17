---
id: ARCH-043-COMMERCE-001
architecture_id: ARCH-043
title: Read Commerce preview budgets from database
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
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
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Read Commerce preview budgets from database

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Proposed schema/key contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-commerce` / `moda_commerce`.
- Portable definition only: **defined but not materialised**; task worktrees, claims and Git commits must be established by normal task launcher.

## Objective

Move **only** Commerce preview budgets to validated database configuration without changing Studio authentication or Commerce credential keyring loading.

## Context

Commerce preview limits are currently environment-backed; the realtime CommerceAgent production path is distinct.

## Scope

- Add fresh environment-scoped read of `commerce.preview` with service-owned validation and no new Shared implementation.
- Wire deadline and output-token budgets into Studio preview admission while preserving code hard ceilings, timeout bounds and slot expiration.
- Document safe no-row defaults and fresh per-preview-operation behaviour without caching.

## Out of Scope

- No Commerce/Google AUTH_SECRET or Commerce keyring cutover; owned by COMMERCE-002.

## Requirements

- Never allow deadline beyond slot reservation safety margin.
- Invalid update must not weaken hard caps or cross environments.

## Work Items

- [ ] Add fresh environment-scoped read of `commerce.preview` with service-owned validation and no new Shared implementation.
- [ ] Wire deadline and output-token budgets into Studio preview admission while preserving code hard ceilings, timeout bounds and slot expiration.
- [ ] Document safe no-row defaults and fresh per-preview-operation behaviour without caching.
- [ ] Record actual files changed, validation results, worktree isolation and Completion Report; stop at Review.

## Interfaces / Contracts

- `PlatformConfiguration` and `PlatformConfigurationAudit` are owned by `ARCH-043-DATABASE-001`; schema supports typed non-secret objects and sealed envelopes; environment-scoped and redacted in audit.
- Closed policy shapes are specified in `docs/architecture/ARCH-043-configuration-schema-review.md`. Admin validates before writes; each service independently validates the configuration it consumes. No ARCH-043 Shared publication is required.
- Existing billing, tenant, provider credential and bootstrap contracts retain their established owners.

## Dependencies

- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Never allow deadline beyond slot reservation safety margin.
- [ ] Invalid update must not weaken hard caps or cross environments.
- [ ] The bounded task implementation passes the specified validation without regressions to existing domain configuration.

## Validation

- [ ] Existing preview tests including deadline boundary
- [ ] Fresh-read, invalid configuration and safe-default/fail-closed tests
- [ ] Typecheck/lint/build

## Stop Condition

Complete the defined scope and required validation, update the task and Completion Report to Review, return to `moda_architect`, and STOP. No execution of enabled tasks and no `_index.md` edits.

## Implementation Notes

- Preserve service ownership boundaries and existing published ARCH-039 credential functions. Use the ARCH-043 documented policy shapes and AAD byte convention; do not invent a new crypto codec or require new Shared publication.
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
