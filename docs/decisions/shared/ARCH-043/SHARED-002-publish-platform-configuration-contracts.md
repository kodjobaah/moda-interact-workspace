---
id: ARCH-043-SHARED-002
architecture_id: ARCH-043
title: Publish accepted platform configuration contracts
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-043-SHARED-001
- ARCH-043-SHARED-003
enables:
- ARCH-043-ADMIN-001
- ARCH-043-ADMIN-002
- ARCH-043-API-001
- ARCH-043-API-002
- ARCH-043-API-003
- ARCH-043-BACKGROUND-001
- ARCH-043-BACKGROUND-002
- ARCH-043-COMMERCE-001
- ARCH-043-COMMERCE-002
- ARCH-043-MCP-001
- ARCH-043-MESSAGING-001
- ARCH-043-SHOPIFY-001
- ARCH-043-SHOPIFY-002
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Publish accepted platform configuration contracts

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Proposed schema/key contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-shared` / `moda_shared`.
- Portable definition only: **defined but not materialised**; task worktrees, claims and Git commits must be established by normal task launcher.

## Objective

Publish the accepted non-secret configuration schema **and** server-only sealed-secret envelope runtime in one approved Shared release.

## Context

The architect role requires an independently reviewable publication gate before consumers depend on the package.

## Scope

- Require accepted SHARED-001 and SHARED-003 implementations.
- Publish one version with the strict browser-safe policy entrypoint and Node-only secret entrypoint; verify the exact exported version at the registry.
- Record the version and release evidence; do not rerun accepted tests or implement consumers.

## Out of Scope

- No new runtime source behaviour or implementation tests, typecheck, lint or build repeated from accepted SHARED-001.

## Requirements

- Secrets/Node cryptography must never be exported through a browser-safe Shared entrypoint.
- Publication is a release-only task. No code changes beyond approved version metadata.

## Work Items

- [ ] Verify prerequisite SHARED-001 and SHARED-003 implementations are Complete and architect-accepted.
- [ ] Publish browser-safe policy schemas plus Node-only sealed secret export as one package version.
- [ ] Verify exact published version and export separation; no implementation-code changes.

## Interfaces / Contracts

- `PlatformConfiguration` and `PlatformConfigurationAudit` are owned by `ARCH-043-DATABASE-001`; schema supports typed non-secret objects and sealed envelopes; environment-scoped and redacted in audit.
- Closed JSON shapes and validators are owned by `ARCH-043-SHARED-001` and published in `ARCH-043-SHARED-002` through `@modainteract/moda-interact-shared`.
- Existing billing, tenant, provider credential and bootstrap contracts retain their established owners.

## Dependencies

- `ARCH-043-SHARED-001`
- `ARCH-043-SHARED-003`

## Enables

- `ARCH-043-ADMIN-001`
- `ARCH-043-ADMIN-002`
- `ARCH-043-API-001`
- `ARCH-043-API-002`
- `ARCH-043-API-003`
- `ARCH-043-BACKGROUND-001`
- `ARCH-043-BACKGROUND-002`
- `ARCH-043-COMMERCE-001`
- `ARCH-043-COMMERCE-002`
- `ARCH-043-MCP-001`
- `ARCH-043-MESSAGING-001`
- `ARCH-043-SHOPIFY-001`
- `ARCH-043-SHOPIFY-002`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Prerequisites accepted before publish, approved version visible from registry.
- [ ] No browser entrypoint exports secret codecs or Node cryptography; no code changes outside release metadata.

## Validation

- [ ] Verify SHARED-001 and SHARED-003 are Complete/accepted, approved package version and immutable code.
- [ ] Verify published browser-safe policy and Node-only sealed codec paths are available without leakage.
- [ ] No rerun of accepted implementation test suites.

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
