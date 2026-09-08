---
id: ARCH-007-ADMIN-002
architecture_id: ARCH-007
title: Build platform safety, shop overrides and Free allowance adjustment administration
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: review
priority: 70
executor: copilot
claimed_at: 2026-09-08T16:59:11Z
attempt: 1
depends_on: 
  - ARCH-007-ADMIN-001
enables: 
  - ARCH-007-ADMIN-003
  - ARCH-007-SYSTEM-TEST-001
created: 2026-09-07
updated: 2026-09-08T18:05:00Z
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

- [x] Build platform policy page/actions.
- [x] Add shop controls section to tenant detail or dedicated Billing tab.
- [x] Implement adjustment ledger action/display.
- [x] Implement server-side bounds/expiry validation and audit transactions.
- [x] Add security/validation/audit tests.
- [x] Any components created make sure icu internationalization is supported using the same approach as the current components.

## Interfaces / Contracts

Runtime consumers are BACKGROUND-001/002/004. Admin writes configuration only; it does not directly stop workers or mutate Redis.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-ADMIN-003
- ARCH-007-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Platform hard ceiling cannot be bypassed by tenant override.
- [x] Support credit changes effective allowance without changing committed usage.
- [x] All controls are durable/audited and survive process restart.
- [x] Expired override semantics are visible and safe.
- [x] Unauthorized mutation is rejected.
- [x] Tests/validation pass.

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

Ready for Architect Review (Attempt 1)

### Files Changed

- `src/app/(protected)/billing/page.tsx`
- `src/app/(protected)/billing/controls/page.tsx`
- `src/app/actions/billing-controls.ts`
- `src/components/admin/billing-controls.tsx`
- `src/components/admin/tenant-administration.tsx`
- `src/i18n/locales/en.json`
- `src/i18n/required-keys.ts`
- `src/lib/admin/billing-control-validation.ts`
- `src/lib/admin/billing-controls.ts`
- `src/lib/admin/data.ts`
- `src/lib/admin/types.ts`
- `tests/security/admin-billing-controls.test.mjs`

### Work Completed

- Added SUPER_ADMIN platform policy controls with bounded hard cap and warning threshold validation.
- Added audited per-shop nullable overrides, expiry/history display, platform ceiling enforcement, and effective soft/hard validation.
- Added append-only signed Free allowance adjustments and effective allowance display without mutating entitlement counters.
- Added transactional `BillingAuditEvent` writes for every mutation and canonical ICU catalogue keys for the new UI.

### Validation Results

- Focused ADMIN-002 security tests: 4 passed.
- Full admin test suite: 113 passed, 0 failed.
- `npx tsc --noEmit`: passed.
- `npm run prisma:generate`: passed.
- `npm run prisma:validate`: passed.
- `npm run lint`: passed with two pre-existing queue-monitor hook warnings.
- `npm run build`: passed with existing BullMQ optional Valkey/dynamic dependency warnings.
- `git diff --check`: passed.
- Repository-wide `npm run format:check` remains a baseline failure across existing files; changed ADMIN-002 files were formatted directly.

### Deviations

- No database schema changes were required; the accepted database submodule already exposed the required Prisma delegates.

### Assumptions

- Runtime consumers continue to ignore expired overrides; Admin displays expiry/history and allows audited replacement or clearing.

### Unresolved Issues

- None identified in the implemented scope.

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
