---
id: ARCH-043-SHOPIFY-001
architecture_id: ARCH-043
title: Consume shared Merchant Knowledge upload policy in Shopify
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
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

# Consume shared Merchant Knowledge upload policy in Shopify

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Proposed schema/key contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact` / `moda_app`.
- Portable definition only: **defined but not materialised**; task worktrees, claims and Git commits must be established by normal task launcher.

## Objective

Move non-secret Shopify-side Merchant Knowledge policy reads to PostgreSQL; do not modify Shopify OAuth bootstrapping, which belongs to SHOPIFY-002.

## Context

Shopify presently has separate R2 settings; tenant and browser boundaries must remain unchanged.

## Scope

- Load the validated environment-specific `merchantKnowledge.upload` policy server-side.
- Apply its safe upload limits/format bounds where Shopify owns upload flows.
- Keep Shopify R2 keys external; preserve existing tenant checks and distinct server-side endpoint validation.

## Out of Scope

- No Shopify client OAuth bootstrap, session secret migration or credentials.

## Requirements

- No per-customer request config DB loop or tenant leakage.
- If Shopify cannot safely consume the same R2 location for an operation, keep approved local wiring and record the boundary instead of weakening restrictions.

## Work Items

- [ ] Load the validated environment-specific `merchantKnowledge.upload` policy server-side.
- [ ] Apply its safe upload limits/format bounds where Shopify owns upload flows.
- [ ] Keep Shopify R2 keys external; preserve existing tenant checks and distinct server-side endpoint validation.
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

- [ ] No per-customer request config DB loop or tenant leakage.
- [ ] If Shopify cannot safely consume the same R2 location for an operation, keep approved local wiring and record the boundary instead of weakening restrictions.
- [ ] The bounded task implementation passes the specified validation without regressions to existing domain configuration.

## Validation

- [ ] Shopify file-limit and security checks
- [ ] Empty and environment-mismatched config tests
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
