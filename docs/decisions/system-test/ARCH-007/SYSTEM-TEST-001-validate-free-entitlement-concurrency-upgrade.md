---
id: ARCH-007-SYSTEM-TEST-001
architecture_id: ARCH-007
title: Validate Free lifetime entitlement, concurrency and merchant upgrade flow
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 210
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-007-SHOPIFY-002
  - ARCH-007-BACKGROUND-003
  - ARCH-007-ADMIN-002
enables: []
created: 2026-09-07
updated: 2026-09-07
---

# ARCH-007-SYSTEM-TEST-001: Validate Free lifetime entitlement, concurrency and merchant upgrade flow

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Prove the integrated Free plan lifecycle from Shopify selection through exactly five lifetime conversations, concurrent final-credit admission, exhaustion messaging/CTA and upgrade to a mapped paid plan.

## Context

This is a terminal architecture-validation task. It MUST NOT be used as a dependency for any implementation/publication/infrastructure task. The developer may leave it Ready while manually validating the completed feature and invokes it only when explicitly desired.

## Scope

System-test repository fixtures/orchestration/evidence for the listed integrated scenarios only.

## Out of Scope

- Implementing/correcting product code.
- Running before all listed dependencies are architect-accepted Complete.
- Becoming a gate for non-system-test work.

## Requirements

- Use architecture-approved test environment and real service boundaries where feasible.
- Create deterministic fixtures and cleanup.
- Capture evidence without secrets/customer data.
- Test a shop selecting mapped Free in Shopify and receiving 5 lifetime allowance.
- Test 4 committed then two concurrent new-recovery attempts: exactly one fifth starts and the other is denied; no double usage.
- Test sixth new recovery is blocked while existing fifth conversation can continue subject to message cap.
- Test exactly one exhaustion SYSTEM message and merchant Upgrade CTA.
- Test SUPER_ADMIN Free allowance +2 adjustment allows two more starts without changing prior committed usage.
- Test upgrade through Shopify to mapped paid plan and preservation of Free lifetime committed count for future downgrade/reinstall semantics.

## Work Items

- [ ] Create/extend system-test fixtures for scenarios.
- [ ] Run only after developer explicitly invokes the Ready task.
- [ ] Record reproducible evidence/results.
- [ ] Return to review and STOP.

## Interfaces / Contracts

Validate the integrated architecture described in the Acceptance Criteria; no new production contract is owned by system-test.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

None

## Acceptance Criteria

- [ ] Test a shop selecting mapped Free in Shopify and receiving 5 lifetime allowance.
- [ ] Test 4 committed then two concurrent new-recovery attempts: exactly one fifth starts and the other is denied; no double usage.
- [ ] Test sixth new recovery is blocked while existing fifth conversation can continue subject to message cap.
- [ ] Test exactly one exhaustion SYSTEM message and merchant Upgrade CTA.
- [ ] Test SUPER_ADMIN Free allowance +2 adjustment allows two more starts without changing prior committed usage.
- [ ] Test upgrade through Shopify to mapped paid plan and preservation of Free lifetime committed count for future downgrade/reinstall semantics.

## Validation

Run the architecture-level system tests explicitly defined by this task against the approved test environment. Do not implement application fixes inside system-test; return failures to moda_architect with evidence.

## Implementation Notes

Manual-gated terminal task. Becoming Ready does not mean auto-run.
Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Do not run `git commit` or `git push`.


## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

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

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
