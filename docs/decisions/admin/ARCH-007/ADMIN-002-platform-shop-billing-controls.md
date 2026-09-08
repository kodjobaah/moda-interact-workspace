---
id: ARCH-007-ADMIN-002
architecture_id: ARCH-007
title: Build platform safety, shop overrides and Free allowance adjustment administration
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: ready
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-007-ADMIN-001
enables: 
  - ARCH-007-ADMIN-003
  - ARCH-007-SYSTEM-TEST-001
created: 2026-09-07
updated: 2026-09-08
---
# ARCH-007-ADMIN-002: Build platform safety, shop overrides and Free allowance adjustment administration

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Provide safe Admin controls for application-wide WhatsApp/recovery circuit breakers, per-shop bounded overrides and append-only Free support credits.

## Context

ARCH-007 intentionally keeps autonomous message safety under Moda control. Support must be able to change limits without deploy, but a tenant override must never bypass the platform absolute ceiling or falsify historical usage.

## Scope

Admin platform billing policy screen plus tenant billing-controls panel/actions/audit/tests.

## Out of Scope

- Billing event retry/correction.
- Changing Shopify plan price/tier.
- Directly editing counters/UsageEvent history.

## Requirements

- Platform policy view/edit is SUPER_ADMIN-only for mutation and exposes global pause-new-recoveries, global pause-automated-WhatsApp, finite absolute outbound hard cap and bounded warning threshold.
- Shop controls allow nullable soft/hard outbound cap override, pause-new-recoveries, pause-automated-WhatsApp, optional recovery safety ceiling, required reason and optional expiry.
- Server validation rejects shop hard override > platform absolute hard cap and rejects soft >= effective hard. Do not rely only on form constraints.
- Expired override is displayed as expired/history but runtime will ignore it; Admin may clear/replace through audited action.
- Free allowance adjustment action appends signed adjustment row with required reason; UI shows base allowance, total adjustments, committed, reserved and effective remaining. Never update committed counter or delete usage to grant credit.
- Every mutation writes BillingAuditEvent with actor/reason/before/after and shop when applicable.
- Use existing PlatformAdmin ADMIN/SUPER_ADMIN authorization; hard platform/correction-level controls require SUPER_ADMIN.

## Work Items

- [ ] Build platform policy page/actions.
- [ ] Add shop controls section to tenant detail or dedicated Billing tab.
- [ ] Implement adjustment ledger action/display.
- [ ] Implement server-side bounds/expiry validation and audit transactions.
- [ ] Add security/validation/audit tests.

## Interfaces / Contracts

Runtime consumers are BACKGROUND-001/002/004. Admin writes configuration only; it does not directly stop workers or mutate Redis.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-ADMIN-003
- ARCH-007-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Platform hard ceiling cannot be bypassed by tenant override.
- [ ] Support credit changes effective allowance without changing committed usage.
- [ ] All controls are durable/audited and survive process restart.
- [ ] Expired override semantics are visible and safe.
- [ ] Unauthorized mutation is rejected.
- [ ] Tests/validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


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
