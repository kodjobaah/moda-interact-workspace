---
id: ARCH-007-ADMIN-003
architecture_id: ARCH-007
title: Build billing overview, tenant detail and Shopify reconciliation visibility
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: review
priority: 120
executor: copilot
claimed_at: 2026-09-08T19:30:49Z
attempt: 1
depends_on: 
  - ARCH-007-ADMIN-002
  - ARCH-007-BACKGROUND-007
  - ARCH-007-SHOPIFY-001
enables: 
  - ARCH-007-ADMIN-004
created: 2026-09-07
updated: 2026-09-08T21:15:00Z
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
- INTERNATIONALISATION — every new or changed Admin user-visible string in this task MUST use the existing ARCH-005 Admin ICU/i18n path. Reuse the current Admin locale resolver/runtime and `src/i18n/locales/*`; update `src/i18n/required-keys.ts` when that is the repository convention. Do not hard-code English labels, headings, filters, empty states, reconciliation/status copy or help text in TSX/server UI responses. Add each new key to every Admin locale catalogue currently declared by the repository and use the existing locale-aware formatting helpers for dates/numbers. Do not create a second i18n mechanism.

## Work Items

- [x] Add Billing overview navigation/page.
- [x] Add paginated report-state/event listing.
- [x] Extend tenant detail with Billing section.
- [x] Implement bounded queries and filters for plan/state/date/shop.
- [x] Add security/pagination/empty-state/reconciliation tests.
- [x] Add focused i18n coverage proving every new Admin-visible key resolves through the existing Admin ICU catalogue path and required-key validation remains complete.

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
- [ ] All new Admin-visible copy uses the existing ARCH-005 ICU/i18n catalogues; no task-introduced user-visible English literal bypasses that path.
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

Ready for Architect Review (Attempt 1)

### Files Changed

- `moda-interact-admin/src/lib/admin/billing.ts`
- `moda-interact-admin/src/lib/admin/types.ts`
- `moda-interact-admin/src/app/(protected)/billing/page.tsx`
- `moda-interact-admin/src/app/(protected)/page.tsx`
- `moda-interact-admin/src/components/admin/billing-overview.tsx`
- `moda-interact-admin/src/components/admin/tenant-billing.tsx`
- `moda-interact-admin/src/components/admin/tenant-detail-panel.tsx`
- `moda-interact-admin/src/components/admin/tenant-table.tsx`
- `moda-interact-admin/src/i18n/locales/en.json`
- `moda-interact-admin/src/i18n/required-keys.ts`
- `moda-interact-admin/tests/security/admin-billing-visibility.test.mjs`

### Work Completed

- Added authenticated, bounded billing overview reads for mapped Free/paid distribution, unmapped/sync-error subscriptions, Free exhaustion, reported paid recovery usage, and App Event report-state counts.
- Added filtered, date-ranged, shop-scoped, state-scoped, paginated App Event ledger visibility with safe provider status fields and no bearer-token/customer-payload display.
- Added a tenant Billing tab showing observed/current/pending plan state, exact billing cycle, Free base/adjustment/committed/reserved/remaining values, current-cycle paid meter usage, active policy override values, ledger rows, and an explicit unavailable reconciliation state.
- Added required-key catalogue entries and focused security/contract tests.
- Admin implementation commit: `66c5730`; pushed to `origin/task/ARCH-007-ADMIN-003`.

### Validation Results

- `npm run build`: passed; existing BullMQ dynamic dependency warnings remain.
- `npm test -- --runInBand`: passed, 111 tests.
- Focused `node --test tests/security/admin-billing-visibility.test.mjs`: passed, 2 tests.
- `npm run lint`: passed with 2 pre-existing queue-monitor hook warnings and no errors.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- `npm run format:check`: repository-wide check reports 78 pre-existing files; all task-changed files were formatted with the repository Prettier binary.

### Deviations

- The accepted Admin Prisma schema has no durable Shopify usage snapshot or discrepancy table. Reconciliation is therefore rendered as explicitly unavailable (`discrepancy: null`) rather than fabricated or obtained with raw SQL.
- Overview Free exhaustion uses the bounded indexed counter threshold of 5; tenant detail computes the exact base plus signed adjustments versus committed and reserved quantities. A schema-supported aggregate for per-plan allowance plus adjustments would be needed for exact cross-tenant overview counts without loading all shops.

### Assumptions

- `BillingPlan.freeLifetimeConversationAllowance` is the configured Free allowance and the current accepted Free policy threshold is 5.
- Paid current-cycle usage is represented by reported `UsageEvent` rows matching the subscription billing period and mapped Shopify usage-event handle.

### Unresolved Issues

- Shopify-vs-Moda numeric discrepancy remains unavailable until Background or Database provides a durable provider usage snapshot/comparison contract.

### Architectural Concerns

- The discrepancy requirement is a cross-repository contract gap, not an Admin presentation gap. `ADMIN-004` should not add a local duplicate or raw provider query; it should consume the accepted shared/database snapshot contract when available.

## Architect Review

### Review Status

Pending

### Review Notes

Implementation is complete and awaits `moda_architect` review. No architect acceptance decision has been made by this agent.

### Reviewed Files

Pending architect review.

### Validation Reviewed

Pending architect review.

### Architecture Conformance

Pending

### Follow-up

None
