---
id: ARCH-007-BACKGROUND-001
architecture_id: ARCH-007
title: Implement typed effective entitlement and billing safety policy resolution
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 60
executor: null
attempt: 2
depends_on: 
  - ARCH-007-SHARED-002
  - ARCH-007-DATABASE-003
enables:
  - ARCH-007-BACKGROUND-002
created: 2026-09-07
updated: 2026-09-07T22:32:00+01:00
claimed_at: null
---

# ARCH-007-BACKGROUND-001: Implement typed effective entitlement and billing safety policy resolution

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Replace JSON/calendar-month entitlement lookup with a typed Prisma service that resolves current mapped plan features, Free allowance and effective message/safety policy from platform, plan, shop override and adjustments.

## Context

The current EntitlementService reads JSON and aggregates monthly usage. ARCH-007 needs a single deterministic local policy answer that all recovery/message services can use without Shopify hot-path calls.

## Scope

Background billing/entitlement domain service(s), typed errors and focused tests. Adopt accepted DB/Shared versions. Do not integrate recovery sends yet.

## Out of Scope

- Reservation mutation (BACKGROUND-002).
- Recovery usage integration (BACKGROUND-003).
- Outbound send integration (BACKGROUND-004).
- Shopify network calls.

## Requirements

- Resolve only subscriptions with mapped active BillingPlan and eligible local status ACTIVE/TRIALING. NO_CONTRACT/UNMAPPED/SYNC_ERROR fail closed with typed reason.
- Feature checks use BillingPlanFeature typed rows, not JSON.
- For Free, calculate effective lifetime allowance = plan base + sum signed BillingAllowanceAdjustment; expose committed/reserved/remaining from ShopEntitlementCounter without mutating it.
- For paid, do not treat Shopify included usage as a hard entitlement limit. Return paid metered semantics/event handle and current BillingPeriod projection.
- Effective outbound hard limit = minimum(platform absolute hard limit, validated shop override hard when active else plan default hard). Soft limit is likewise bounded below hard; invalid data fails closed/configuration error rather than silently unlimited.
- Ignore expired shop override values. Respect global and shop pause flags.
- Return one typed EffectiveBillingPolicy object suitable for recovery/message admission with planId/kind, features, Free allowance data, event handle, soft/hard/terminal-reserved semantics, pause reasons and policy versions useful for audit/debug.
- No `startOfCurrentMonth`/calendar fallback in ARCH-007 paid path.
- Use Prisma delegates only; remove/retire old JSON EntitlementService behavior that conflicts with this service.

## Work Items

- [x] Adopt DB/Shared artifacts and regenerate Prisma.
- [x] Implement EffectiveBillingPolicy resolver and typed errors/reasons.
- [x] Add focused tests for Free/paid/no-contract/unmapped, adjustment, expired override, platform cap domination, pauses and invalid limits.
- [x] Remove obsolete JSON/calendar fallback path from ARCH-007 callers/service.

## Interfaces / Contracts

Pure/read-side contract (no capacity mutation):

```text
resolve(shopId, now) -> EffectiveBillingPolicy | typed fail-closed error
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-BACKGROUND-002

## Acceptance Criteria

- [x] No active mapped plan never becomes implicit Free.
- [x] Paid included quantity is not a local hard stop.
- [x] Platform hard ceiling always bounds shop override.
- [x] Expired override is ignored.
- [x] Free remaining calculation includes signed adjustments and committed/reserved counters.
- [x] No raw SQL/calendar fallback/Shopify network call exists in resolver.
- [x] Focused tests and validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes

Exact Shared dependency: `@modainteract/moda-interact-shared@0.7.3`. Adopt the accepted database revision and regenerate Prisma before implementing typed policy resolution.


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-BACKGROUND-001` branch and the mirrored parent-workspace `task/ARCH-007-BACKGROUND-001` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for Review

### Files Changed

- `database` submodule gitlink, adopted at accepted database revision `7ed2253`.
- `package.json` and `package-lock.json`, Shared dependency `0.7.3`.
- `src/services/effective-billing-policy.service.ts`.
- `src/services/entitlement.service.ts`.
- `src/services/usage.service.ts`.
- `tests/unit/services/effective-billing-policy.service.test.ts`.
- `tests/unit/runtime/observability-startup.test.ts`.

### Work Completed

- Added a Prisma-first `EffectiveBillingPolicyResolver` with typed fail-closed reasons for no contract, unmapped/inactive plans, sync errors, unavailable shops and invalid configuration.
- Resolved typed plan features, Free signed allowance adjustments and committed/reserved counter state without mutation.
- Resolved paid meter handles and Shopify billing-period projections without applying included usage as a local hard stop.
- Applied active shop overrides, platform hard ceilings, bounded soft limits, pause flags and audit-friendly policy version metadata; expired overrides are ignored.
- Retired the JSON entitlement and calendar-month fallback path while preserving existing entitlement/usage service entry points over typed data.
- Attempt 2 exposes independent `newRecoveriesPaused` and `automatedWhatsappPaused` controls with bounded `BillingPauseReason` values and preserves every active global/shop source.
- Attempt 2 validates terminal reserved slots against the effective hard limit and types paid billing-period status with generated `BillingPeriodStatus`.
- Attempt 2 adds public-resolver regression coverage for all requested subscription, override, pause, terminal-slot and paid-period cases.

### Validation Results

- `./node_modules/.bin/vitest run tests/unit/services/effective-billing-policy.service.test.ts` — passed, 16 tests.
- `npm run prisma:validate` — passed.
- `npm run prisma:generate` — passed.
- `npx tsc --noEmit` — passed.
- `npm run build` — passed.
- `git diff --check` — passed.
- `npm test` — 243 passed, 5 skipped, 3 pre-existing failures in recovery-routing/pending-recovery-candidate tests; no failures in the changed billing policy tests.
- `git status --short` — expected prior Attempt 1 changes plus the resolver source/test files; no unrelated new files.

### Deviations

The background repository's existing full suite remains red in the same three unrelated recovery-routing/pending-recovery tests. They were not modified because they are outside BACKGROUND-001 scope.

### Assumptions

The existing entitlement and usage service method signatures remain available for current callers, with legacy metric names mapped to typed ARCH-007 metrics.

### Unresolved Issues

None.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted

### Review Notes

BACKGROUND-001 Attempt 2 is architect-accepted Complete.

Direct review confirms that the Attempt-1 corrections are now implemented in
the public resolver contract:

- `newRecoveriesPaused` and `automatedWhatsappPaused` are independent typed
  machine-readable dimensions;
- `BillingPauseReason` is a bounded literal union;
- all simultaneously active platform/shop pause sources are retained;
- `terminalMessageReservedSlots` fails closed unless it is a safe integer with
  `1 <= slots < effective outboundHardLimit`;
- paid BillingPeriod projection preserves Prisma `BillingPeriodStatus`;
- Free allowance remains read-only and is calculated as base + signed
  adjustments - committed - reserved;
- paid metered plans do not treat included Shopify quantity as a local hard
  entitlement stop;
- inactive/unmapped/sync-error/missing-meter/invalid-policy states fail closed;
- active shop hard overrides cannot exceed the platform absolute hard ceiling;
- expired overrides are ignored;
- paid billing with no local BillingPeriod remains `billingPeriod: null` with no
  calendar-month fallback;
- no new billing raw SQL or Shopify network call exists in the resolver.

The resolver is therefore stable for BACKGROUND-002's concurrency-safe
reservation service and for later recovery/outbound admission work.

### Reviewed Files

- `moda-interact-background/src/services/effective-billing-policy.service.ts`
- `moda-interact-background/src/services/entitlement.service.ts`
- `moda-interact-background/src/services/usage.service.ts`
- `moda-interact-background/tests/unit/services/effective-billing-policy.service.test.ts`
- `moda-interact-background/package.json`
- `moda-interact-background/package-lock.json`
- `moda-interact-background/database/prisma/schema.prisma`
- task Completion Report

### Validation Reviewed

Attempt 2 reports:

- Prisma validate/generate: passed;
- TypeScript `--noEmit`: passed;
- build: passed;
- focused resolver suite: 16 cases passed;
- `git diff --check`: passed;
- full suite: 243 passed, 5 skipped, with the same 3 unrelated pre-existing
  recovery-routing/pending-candidate failures.

The unchanged unrelated failure set is not a BACKGROUND-001 acceptance blocker.

### Architecture Conformance

Conformant.

One metadata correction is included in this acceptance record:
`ADMIN-002` is removed from BACKGROUND-001's `enables` list because individual
task YAML dependencies are authoritative and ADMIN-002 depends on ADMIN-001,
not BACKGROUND-001.

### Follow-up

ARCH-007-BACKGROUND-002 may now begin.

BACKGROUND-003 remains Pending until both BACKGROUND-002 and SHOPIFY-001 are
architect-accepted Complete. Do not start BACKGROUND-003 early.
