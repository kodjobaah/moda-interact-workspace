---
id: ARCH-007-ADMIN-003
architecture_id: ARCH-007
title: Build billing overview, tenant detail and Shopify reconciliation visibility
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: ready
priority: 120
executor: null
claimed_at: null
attempt: 0
depends_on: 
  - ARCH-007-ADMIN-002
  - ARCH-007-BACKGROUND-007
  - ARCH-007-SHOPIFY-001
enables: 
  - ARCH-007-ADMIN-004
created: 2026-09-07
updated: 2026-09-08T19:20:00+01:00
---

# ARCH-007-ADMIN-003: Build billing overview, tenant detail and Shopify reconciliation visibility

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Add bounded operational billing views for plan distribution, merchant usage, App Event delivery and per-shop Shopify-vs-Moda reconciliation without turning Admin into the telemetry transport owner.

## Context

With paid usage billing, support needs to see why a merchant was billed/blocked and whether Moda reporting matches Shopify. Existing tenant view only shows limited plan/subscription state.

## Scope

Admin billing overview, paginated UsageEvent/report-state views and tenant Billing tab/read services/tests. Read-only operations in this task.

## Out of Scope

- Retrying events or creating corrections (ADMIN-004).
- Changing policy/plan mappings (ADMIN-001/002).
- Building custom telemetry duplicates.

## Requirements

- Overview uses bounded/paginated/index-supported database queries; never load all shops/events to aggregate in application memory.
- Show counts/distribution for mapped Free/paid/unmapped/sync-error shops, Free exhaustion, paid recovery usage, pending/retryable/needs-attention/reported events, and safety-cap outcomes where persisted.
- Tenant Billing detail shows current mapped/observed plan, pending plan/effective date, exact Shopify cycle, Free lifetime base/adjustments/committed/reserved/remaining, paid current-cycle Moda usage, provider reported usage/cost snapshot when available, message counts/cap and active/expired overrides.
- Show App Event ledger rows with occurredAt, quantity, report state/attempts/last error/reportedAt and safe provider response summary. Do not show bearer tokens/customer payload.
- Show reconciliation discrepancy between Moda net REPORTED recovery usage for current meter/cycle and Shopify TieredPrice usage quantity when BACKGROUND-008 records/provides it.
- Every named shop route remains tenant-parameter-safe and Admin-authenticated; cross-shop lookup cannot be influenced by merchant-controlled identifiers without authorization.
- Use Grafana/OTel only for generic operational telemetry already present; billing ledger/reconciliation is domain data and can be queried from DB.

## Work Items

- [ ] Add Billing overview navigation/page.
- [ ] Add paginated report-state/event listing.
- [ ] Extend tenant detail with Billing section.
- [ ] Implement bounded queries and filters for plan/state/date/shop.
- [ ] Add security/pagination/empty-state/reconciliation tests.

## Interfaces / Contracts

Read-only domain sources:

```text
BillingPlan/Subscription/BillingPeriod
ShopEntitlementCounter/adjustments/overrides
UsageEvent report ledger
reconciliation state produced by Background
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-ADMIN-004

## Acceptance Criteria

- [ ] Admin can identify unmapped plan and failed billing event without database shell access.
- [ ] Tenant view explains Free remaining and paid current-cycle usage.
- [ ] Reconciliation discrepancy is visible and bounded.
- [ ] Pages are paginated/index-aligned and secure.
- [ ] No secret/PII leakage.
- [ ] Tests/build/validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-ADMIN-003` branch and the mirrored parent-workspace `task/ARCH-007-ADMIN-003` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
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
