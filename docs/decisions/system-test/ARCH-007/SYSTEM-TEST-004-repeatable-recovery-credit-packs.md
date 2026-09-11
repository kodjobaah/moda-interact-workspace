---
id: ARCH-007-SYSTEM-TEST-004
architecture_id: ARCH-007
title: Validate repeatable recovery-credit packs across Free and paid plans
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: pending
priority: 120
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-007-SHOPIFY-004
  - ARCH-007-BACKGROUND-009
  - ARCH-007-BACKGROUND-008
  - ARCH-007-ADMIN-005
enables: []
created: 2026-09-08
updated: 2026-09-08
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-SYSTEM-TEST-004

Terminal/manual-gated integrated validation only.

Validate:
- Free allowance exhausted -> pack request -> Shopify pack UsageEvent reported -> credits activate -> recovery allowed.
- consume whole pack -> another pack can be bought and activates again.
- paid included allowance exhausted -> purchased credits are consumed before overage.
- paid pack exhaustion -> overage resumes.
- buying another paid pack -> subsequent recoveries consume the new purchased balance.
- top-up-covered recovery is not double-reported on normal recovery meter.
- failed/needs-attention pack billing grants zero credits.
- repeated purchase request ID does not double charge/grant.
- higher-tier price differences remain Shopify configuration; the test verifies correct plan-specific top-up meter is selected, not a Moda-stored price.

Do not run until all dependencies are architect-accepted Complete and the developer chooses to invoke system testing.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-SYSTEM-TEST-004` branch and the mirrored parent-workspace `task/ARCH-007-SYSTEM-TEST-004` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status
Pending

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
None.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status
Pending

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending

### Follow-up
None.

