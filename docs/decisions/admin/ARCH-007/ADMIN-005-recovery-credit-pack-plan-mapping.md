---
id: ARCH-007-ADMIN-005
architecture_id: ARCH-007
title: Add recovery-credit pack fields to billing plan catalog
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: ready
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-007-ADMIN-001
  - ARCH-007-DATABASE-005
  - ARCH-007-SHARED-006
enables:
  - ARCH-007-SHOPIFY-004
created: 2026-09-08
updated: 2026-09-08
---
# ARCH-007-ADMIN-005: Add recovery-credit pack fields to billing plan catalog

## Exact product rule

SUPER_ADMIN configures Moda's mapping to Shopify App Pricing. Admin does not set Shopify monetary prices.

Add these fields to the existing BillingPlan catalog create/edit presentation:

```text
recoveryCreditPackEnabled
recoveryCreditsPerPack
shopifyRecoveryCreditPackEventHandle
includedRecoveryConversationAllowance
```

## Server-side validation

When `recoveryCreditPackEnabled=false`:
- pack size and pack event handle must be null/empty.

When `recoveryCreditPackEnabled=true`:
- `recoveryCreditsPerPack` must be a positive integer;
- `shopifyRecoveryCreditPackEventHandle` must be trimmed, non-empty;
- it must differ from `shopifyUsageEventHandle`.

FREE:
- existing `freeLifetimeConversationAllowance` remains required;
- existing normal `shopifyUsageEventHandle` remains null;
- top-up meter is allowed.

PAID_METERED:
- existing normal `shopifyUsageEventHandle` remains required;
- `includedRecoveryConversationAllowance` must be a non-negative integer when top-ups are enabled.

Do not add a money/price input.

## Required copy

The form/help text must state:

```text
"Pack price is configured in Shopify App Pricing. Moda stores only the pack size and Shopify meter mapping."
```

and:

```text
"Configure a cheaper recovery-credit-pack meter rate on higher paid plans in Shopify if that is the intended commercial policy."
```

## Audit

Every change uses existing `PLAN_CATALOG_CHANGED` audit semantics with bounded before/after data. Include the four new fields.

## Tests

Prove all validation combinations above, SUPER_ADMIN mutation protection, audit writing, and that no price field exists in the action schema/UI.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-ADMIN-005` branch and the mirrored parent-workspace `task/ARCH-007-ADMIN-005` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
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

