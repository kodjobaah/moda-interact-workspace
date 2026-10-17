---
id: ARCH-043-SYSTEM-TEST-001
architecture_id: ARCH-043
title: Certify runtime policy configuration across services
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-043-DATABASE-001
- ARCH-043-SHARED-002
- ARCH-043-ADMIN-001
- ARCH-043-ADMIN-002
- ARCH-043-BACKGROUND-001
- ARCH-043-BACKGROUND-002
- ARCH-043-API-001
- ARCH-043-API-002
- ARCH-043-API-003
- ARCH-043-COMMERCE-001
- ARCH-043-COMMERCE-002
- ARCH-043-SHOPIFY-001
- ARCH-043-SHOPIFY-002
- ARCH-043-MCP-001
- ARCH-043-MESSAGING-001
- ARCH-043-GATEWAY-001
enables: []
created: '2026-10-17'
updated: '2026-10-17'
---

# Certify runtime policy configuration across services

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Proposed schema/key contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-system-test` / `moda_system_test`.
- Portable definition only: **defined but not materialised**; task worktrees, claims and Git commits must be established by normal task launcher.

## Objective

Independently certify non-secret policy refresh **and** sealed-secret bootstrap, encryption, validation, private distribution and rotation across the required runtime boundaries.

## Context

The system test is terminal and begins after architect acceptance of every implementation/publication prerequisite; the developer may first validate manually.

## Scope

- Run documented non-secret policy scenarios from the six allowlisted policy keys.
- Verify Admin/Commerce/Shopify protected cold starts with encrypted DB secrets and unavailable DB/KMS fail-closed behaviour.
- Verify Commerce keyring decrypts previously stored ciphertext without changing AAD/format; expired/unknown root keys are rejected.
- Verify Meta webhook challenge/HMAC verification uses the scoped secret snapshot, rejects bad/missing signatures and does not query PostgreSQL on each webhook.
- Verify authenticated private API isolation, replay resistance, environment and secret-purpose isolation; redacted audit, no secret leaks in logs/browser.
- Validate rotation, rollback and Gateway environment cleanup sequencing.

## Out of Scope

- No new implementation code outside test harness; no new deployment secrets, no direct merchant WordPress DB access.

## Requirements

- No non-system-test task may depend on this test.
- Test should exercise actual supported endpoints/workflows, not only mocks.
- Do not claim architecture Implemented before passing evidence and architect acceptance.

## Work Items

- [ ] Test trusted admin write/audit/CAS with create-clear-stale replay, failed attempts and cross-environment access.
- [ ] Verify configured values take effect in Background, API, Commerce and Shopify without application-policy redeploy, or document required worker restart.
- [ ] Test Postgres outage, invalid/missing values, cache refresh, rollback and secret-free persistence/logs.
- [ ] Verify removed environment declarations no longer influence configured runtime.
- [ ] Record actual files changed, validation results, worktree isolation and Completion Report; stop at Review.

## Interfaces / Contracts

- `PlatformConfiguration` and `PlatformConfigurationAudit` are owned by `ARCH-043-DATABASE-001`; schema supports typed non-secret objects and sealed envelopes; environment-scoped and redacted in audit.
- Closed JSON shapes and validators are owned by `ARCH-043-SHARED-001` and published in `ARCH-043-SHARED-002` through `@modainteract/moda-interact-shared`.
- Existing billing, tenant, provider credential and bootstrap contracts retain their established owners.

## Dependencies

- `ARCH-043-DATABASE-001`
- `ARCH-043-SHARED-002`
- `ARCH-043-ADMIN-001`
- `ARCH-043-ADMIN-002`
- `ARCH-043-BACKGROUND-001`
- `ARCH-043-BACKGROUND-002`
- `ARCH-043-API-001`
- `ARCH-043-API-002`
- `ARCH-043-API-003`
- `ARCH-043-COMMERCE-001`
- `ARCH-043-COMMERCE-002`
- `ARCH-043-SHOPIFY-001`
- `ARCH-043-SHOPIFY-002`
- `ARCH-043-MCP-001`
- `ARCH-043-MESSAGING-001`
- `ARCH-043-GATEWAY-001`

## Enables

None

## Acceptance Criteria

- [ ] No non-system-test task may depend on this test.
- [ ] Test should exercise actual supported endpoints/workflows, not only mocks.
- [ ] Do not claim architecture Implemented before passing evidence and architect acceptance.
- [ ] The bounded task implementation passes the specified validation without regressions to existing domain configuration.

## Validation

- [ ] Disposable/Postgres integrated execution
- [ ] Real service and environment isolation scenarios
- [ ] Failure-recovery and no-secret assertions

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
