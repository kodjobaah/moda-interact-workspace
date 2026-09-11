---
id: ARCH-007-SYSTEM-TEST-002
architecture_id: ARCH-007
title: Validate paid Shopify App Events, retries, overage and pending downgrade
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 220
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-007-SHOPIFY-002
  - ARCH-007-BACKGROUND-008
  - ARCH-007-ADMIN-004
  - ARCH-007-GATEWAY-001
enables: []
created: 2026-09-07
updated: 2026-09-07
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-SYSTEM-TEST-002: Validate paid Shopify App Events, retries, overage and pending downgrade

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Prove the integrated paid recurring+usage lifecycle including all-conversation reporting, permanent idempotency, included/overage continuation, reconciliation and deferred downgrade semantics.

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
- Test paid mapped plan current FlatRatePrice + TieredPrice meter is projected regardless of item order.
- Test each successful paid recovery creates one local +1 and one Shopify App Event with configured meter/idempotency identity; duplicate job/event retry does not double meter.
- Test paid recovery continues after included units are exceeded and Shopify usage quantity increases rather than Moda hard-stopping.
- Test provider timeout/crash-after-accept replay uses same key and local state eventually REPORTED.
- Test SUPER_ADMIN negative correction produces linked -1 and Shopify net usage adjusts without original mutation.
- Test Shopify pending paid->Free update remains paid until cycle boundary, then reconciler activates Free and preserved lifetime Free usage applies.
- Test Admin displays current usage/report state and no reconciliation mismatch after convergence.

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

- [ ] Test paid mapped plan current FlatRatePrice + TieredPrice meter is projected regardless of item order.
- [ ] Test each successful paid recovery creates one local +1 and one Shopify App Event with configured meter/idempotency identity; duplicate job/event retry does not double meter.
- [ ] Test paid recovery continues after included units are exceeded and Shopify usage quantity increases rather than Moda hard-stopping.
- [ ] Test provider timeout/crash-after-accept replay uses same key and local state eventually REPORTED.
- [ ] Test SUPER_ADMIN negative correction produces linked -1 and Shopify net usage adjusts without original mutation.
- [ ] Test Shopify pending paid->Free update remains paid until cycle boundary, then reconciler activates Free and preserved lifetime Free usage applies.
- [ ] Test Admin displays current usage/report state and no reconciliation mismatch after convergence.

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
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-SYSTEM-TEST-002` branch and the mirrored parent-workspace `task/ARCH-007-SYSTEM-TEST-002` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


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
