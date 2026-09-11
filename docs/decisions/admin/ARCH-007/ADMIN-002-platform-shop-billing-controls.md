---
id: ARCH-007-ADMIN-002
architecture_id: ARCH-007
title: Build platform safety, shop overrides and Free allowance adjustment administration
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 70
executor: null
claimed_at: null
attempt: 2
depends_on: 
  - ARCH-007-ADMIN-001
enables: 
  - ARCH-007-ADMIN-003
  - ARCH-007-SYSTEM-TEST-001
created: 2026-09-07
updated: 2026-09-08T19:20:00+01:00
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

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
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-ADMIN-002` branch and the mirrored parent-workspace `task/ARCH-007-ADMIN-002` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for Architect Review (Attempt 2)

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
- Corrected first soft-only and pause-only shop overrides so they remain ADMIN-authorized while hard-control mutations remain SUPER_ADMIN-only.
- Added strict UTC calendar round-trip validation so impossible expiry dates are rejected without changing valid end-of-day semantics.

### Validation Results

- Focused ADMIN-002 security tests: 6 passed, 0 failed, including all six Architect Review authorization cases and all required expiry-date cases.
- Full admin test suite: 115 passed, 0 failed.
- `npx tsc --noEmit`: passed.
- `npm run prisma:generate`: passed.
- `npm run prisma:validate`: passed.
- `npm run lint`: passed with two pre-existing queue-monitor hook warnings.
- `npm run build`: passed with existing BullMQ optional Valkey/dynamic dependency warnings.
- `git diff --check`: passed.
- `npm run format:check` was not rerun; the task-required focused tests, typecheck, Prisma validation, lint, build and diff check all passed.

### Deviations

- No database schema changes were required; the accepted database submodule already exposed the required Prisma delegates.

### Assumptions

- Runtime consumers continue to ignore expired overrides; Admin displays expiry/history and allows audited replacement or clearing.

### Unresolved Issues

- None identified in the implemented scope.

### Architectural Concerns

None

### Attempt 2 Correction Mapping

- Correction 1 implemented in `src/lib/admin/billing-control-validation.ts` and `src/app/actions/billing-controls.ts`; behavioral matrix covered in `tests/security/admin-billing-controls.test.mjs`.
- Correction 2 implemented in `src/lib/admin/billing-control-validation.ts`; deterministic calendar and leap-day cases covered in `tests/security/admin-billing-controls.test.mjs`.

## Architect Review

### Review Status

Accepted

### Review Notes

#### Attempt 2 — Accepted

Attempt 2 is architect-accepted Complete.

Both Attempt 1 corrections are implemented correctly.

1. Shop override authorization now distinguishes the absence of an existing override from the presence of an existing hard control. `ADMIN` may create first soft-only and pause-only overrides, while setting, removing or replacing `outboundHardLimit` or `recoverySafetyCeiling` remains `SUPER_ADMIN`-only. The existing platform absolute ceiling and effective soft `<` hard validation remain in force.

2. Expiry parsing now performs strict UTC calendar round-trip validation. Impossible dates such as `2026-02-29`, `2026-02-31` and `2026-04-31` are rejected, while valid dates including leap day `2028-02-29` retain end-of-day `23:59:59.999Z` semantics.

Focused behavioral coverage directly proves the required authorization and expiry matrices. The focused ADMIN-002 suite was independently verified at 6/6 passing.

Previously reviewed ADMIN-002 behavior remains intact, including SUPER_ADMIN-only platform policy mutation, platform absolute-ceiling enforcement, effective soft `<` hard validation, append-only signed Free allowance adjustments, transactional `BillingAuditEvent` writes, expired override history visibility and ICU localization.

No further implementation changes are required for ARCH-007-ADMIN-002. No Attempt 3 is required.

#### Attempt 1 — Changes Requested

The overall ADMIN-002 implementation is architecturally aligned, but exactly two defects must be corrected before acceptance. This is a narrow Attempt 2. Do not redesign billing controls, change database schema, broaden authorization policy, or modify another ARCH-007 task.

##### Correction 1 — First safe shop override must remain ADMIN-authorized

Target function: `src/app/actions/billing-controls.ts` -> `mutateShopBillingOverrideAction()`.

Current defect:

```ts
const hardControlChanged =
  values.outboundHardLimit !== null ||
  values.recoverySafetyCeiling !== null ||
  existing?.outboundHardLimit !== null ||
  existing?.recoverySafetyCeiling !== null;
```

When `existing` is `null`, optional chaining returns `undefined`, and `undefined !== null` is `true`. Therefore an ordinary `ADMIN` is incorrectly forced through `requireSuperAdmin()` even when creating the first soft-only or pause-only shop override.

Required authorization behavior after the fix:

| Principal | Mutation | Required result |
| --- | --- | --- |
| `ADMIN` | first override with only `outboundSoftLimit` | ALLOW |
| `ADMIN` | first override with only `pauseNewRecoveries` and/or `pauseAutomatedWhatsapp` | ALLOW |
| `ADMIN` | set non-null `outboundHardLimit` | REJECT |
| `ADMIN` | set non-null `recoverySafetyCeiling` | REJECT |
| `ADMIN` | remove or replace an existing non-null hard control | REJECT |
| `SUPER_ADMIN` | set/remove/replace hard controls | ALLOW, subject to existing bounds validation |

Implementation constraint: compute whether an existing hard control is present only when an existing override actually exists. An acceptable shape is:

```ts
const existingHasHardControl =
  existing !== null &&
  (existing.outboundHardLimit !== null ||
    existing.recoverySafetyCeiling !== null);

const hardControlChanged =
  values.outboundHardLimit !== null ||
  values.recoverySafetyCeiling !== null ||
  existingHasHardControl;
```

Equivalent code is acceptable if and only if it produces the matrix above. Preserve the existing platform absolute ceiling and effective soft `<` hard validation exactly.

Required regression coverage: add behavioral tests that invoke the relevant server-side mutation/authorization path or an extracted pure authorization helper. Do not satisfy this requirement only with source-text/regex assertions. Prove at minimum all six rows in the matrix above.

##### Correction 2 — Reject impossible calendar expiry dates

Target function: `src/lib/admin/billing-control-validation.ts` -> `optionalDate()`.

Current defect: the function validates only `YYYY-MM-DD` shape and then relies on `new Date(...)`. JavaScript normalizes impossible dates instead of rejecting them; for example `2026-02-31` becomes a March date.

Required behavior:

| Input | Required result |
| --- | --- |
| empty / omitted | `null` |
| `2026-02-28` | ACCEPT |
| `2026-02-29` | REJECT |
| `2028-02-29` | ACCEPT |
| `2026-02-31` | REJECT |
| `2026-04-31` | REJECT |
| malformed non-`YYYY-MM-DD` input | REJECT |

Implementation constraint: after parsing year/month/day, construct the UTC date and round-trip `getUTCFullYear()`, `getUTCMonth()`, and `getUTCDate()` against the submitted components. Do not use locale-dependent parsing. Continue returning the valid expiry at `23:59:59.999Z` as the current implementation does.

Required regression coverage: add deterministic tests for every row in the table above.

##### Attempt 2 scope and stop condition

Only change what is necessary for these two corrections and their focused regressions. Preserve all already-reviewed ADMIN-002 behavior, including:

- SUPER_ADMIN-only platform policy mutation;
- platform absolute outbound ceiling enforcement;
- effective soft `<` hard server validation;
- append-only signed Free allowance adjustments;
- no mutation of committed/reserved usage to grant support credit;
- transactional `BillingAuditEvent` writes;
- expired override visibility/history semantics;
- ICU localization already added by Attempt 1.

Do not create a new task, do not implement ADMIN-003, do not change Prisma schema, and do not add raw SQL. After the focused corrections and repository validation pass, update this same task Completion Report for Attempt 2, set only this task back to `review`, and STOP for architect review.

### Reviewed Files

- `src/app/actions/billing-controls.ts`
- `src/lib/admin/billing-control-validation.ts`
- `src/lib/admin/billing-controls.ts`
- `src/lib/admin/data.ts`
- `src/components/admin/billing-controls.tsx`
- `src/components/admin/tenant-administration.tsx`
- `tests/security/admin-billing-controls.test.mjs`
- supporting ADMIN-002 ICU/type/page changes listed in the Completion Report

### Validation Reviewed

Attempt 1 reported focused security tests `4/4`, full suite `113/113`, TypeScript, Prisma validation/generation, build and `git diff --check` passing. Those results are acknowledged, but the focused suite does not currently exercise the two failing behavioral cases above, so they are insufficient for acceptance.

### Architecture Conformance

Changes required. Core ADMIN-002 architecture is retained; only the two defects above block acceptance.

### Follow-up

Reclaim the same task as Attempt 2. Implement only Correction 1 and Correction 2 plus the deterministic behavioral regressions described above, return the task to `review`, and stop.
