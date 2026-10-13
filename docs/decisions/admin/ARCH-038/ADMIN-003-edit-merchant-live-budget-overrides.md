---
id: ARCH-038-ADMIN-003
architecture_id: ARCH-038
title: Manage Merchant LIVE CommerceAgent overrides
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 22
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-038-DATABASE-001
  - ARCH-038-ADMIN-001
enables:
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-13
---
# Manage Merchant LIVE CommerceAgent overrides

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_admin`
- Repository: `moda-interact-admin`

## Objective

Allow authorised Moda administrators to set or clear per-Shop LIVE budget overrides from Tenant Directory merchant details.

## Context

Merchant override is the highest-priority LIVE setting but must never be editable by merchants themselves.

## Scope

- Add CommerceAgent execution settings to the internal Tenant Directory merchant detail/admin view.
- Expose each Shop override, inherited Plan/Platform value and effective per-field source.
- Add authorised CAS mutations, required audit reason, clear-to-inherit, disabled repeat submission and conflict recovery.
- Include unknown/no-current-plan and mismatched-plan provenance without inventing a plan selection.

## Out of Scope

- No Shopify/WooCommerce/merchant-facing settings page or write endpoint.
- Do not modify existing ShopBillingPolicyOverride or Preview policy.

## Requirements

- Target Shop comes from trusted internal merchant ID, not a spoofable request scope.
- Clearing Merchant deadline and/or tokens falls back to Price Plan, then Platform.
- Reject cross-shop operations and expired/invalid Admin access.

## Work Items

- [ ] Build internal merchant budget settings read and mutation flow.
- [ ] Render effective-policy preview with source labels.
- [ ] Add authorisation/tenant/CAS/audit and fallback regressions.

## Interfaces / Contracts

Consumes DATABASE-001 LIVE Shop override and existing BillingPlan/MerchantPricingPlan resolution for display. No Background-owned runtime code.

## Dependencies

- `ARCH-038-DATABASE-001`
- `ARCH-038-ADMIN-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Only platform admins can change Shop overrides.
- [ ] Per-field inheritance and source display match the agreed hierarchy.
- [ ] Preview policies and other Shop records remain untouched.

## Validation

- [ ] Focused Tenant Directory component/server-action tests
- [ ] Relevant typecheck/lint/build scripts
- [ ] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-ADMIN-003` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

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

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation

### Follow-up

None
