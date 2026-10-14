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
status: in_progress
priority: 22
executor: developer
claimed_at: 2026-10-14T00:15:57Z
attempt: 1
depends_on:
  - ARCH-038-DATABASE-001
  - ARCH-038-ADMIN-001
enables:
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-14
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

- Add a separate **CommerceAgent Policy** section to the internal Tenant Directory merchant detail/admin view, reusing the schema-driven Admin editor from ADMIN-001 with independent **Override / Inherit** controls.
- Expose Shop overrides and a read-only **Platform / current Price Plan / Merchant / Effective** per-field comparison, with accurate source labels. Show the current subscribed plan and link to its existing editor when verified.
- Add authorised CAS mutations, required audit reason, clear-to-inherit, disabled repeat submission, inline validation, conflict/reload recovery and a scoped paginated **Policy History** using CommerceAuditEvent.
- Include unknown/no-current-plan and mismatched-plan provenance without inventing a plan selection or implying an effective plan override.

## Out of Scope

- No Shopify/WooCommerce/merchant-facing settings page or write endpoint.
- Do not modify existing ShopBillingPolicyOverride or Preview policy.

## Requirements

- Target Shop comes from trusted internal merchant ID, not a spoofable request scope.
- Clearing either Shop `budget` key deletes that explicit key, then falls back to Price Plan and Platform without copying inherited values; reject JSON null, empty override and unsupported versions/keys. Use the ADMIN-001 allowlisted field descriptors.
- Reject cross-shop operations and expired/invalid Admin access.

## Work Items

- [ ] Build internal merchant budget settings read and mutation flow using shared Admin policy editor; display independent controls and current verified plan link (when available).
- [ ] Render effective-policy comparison with per-field Platform/Plan/Merchant/Effective source labels; provide explicit unknown/current-plan-unresolved state.
- [ ] Present scoped, paginated audit history with before/after changes, reason and actor.
- [ ] Add authorisation/tenant/CAS/audit, duplicate-submit/conflict-reload, missing-plan, history isolation and independent-field fallback regressions.

## Interfaces / Contracts

Consumes DATABASE-001 `CommerceModelPolicy` (`context=LIVE`, `scope=SHOP`, sparse JSONB `budget`), ADMIN-001 reusable Admin editor/field descriptors, and existing BillingPlan/MerchantPricingPlan resolution for display. No Background-owned runtime code.

## Dependencies

- `ARCH-038-DATABASE-001`
- `ARCH-038-ADMIN-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Only platform admins can change Shop overrides.
- [ ] Per-field inheritance and source display match the agreed hierarchy.
- [ ] Preview policies and other Shop records remain untouched.
- [ ] UI displays verified plan (with link), per-field inheritance, effective value and source even when plan resolution is unavailable.
- [ ] Policy History is scoped to the trusted Shop/environment/context and shows actor, time, reason and changed fields; stale submissions offer recovery.

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

In Progress — Attempt 1 claimed by developer at 2026-10-14T00:15:57Z. Attempt 0 review history is preserved below.

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
