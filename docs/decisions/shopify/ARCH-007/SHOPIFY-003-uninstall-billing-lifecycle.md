---
id: ARCH-007-SHOPIFY-003
architecture_id: ARCH-007
title: Make Shopify uninstall stop new billing admission while preserving pre-uninstall drain state
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 80
executor: null
claimed_at: null
attempt: 2
depends_on: 
  - ARCH-007-SHOPIFY-001
enables: 
  - ARCH-007-SYSTEM-TEST-003
created: 2026-09-07
updated: 2026-09-08
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-SHOPIFY-003: Make Shopify uninstall stop new billing admission while preserving pre-uninstall drain state

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Extend APP_UNINSTALLED handling so durable shop/subscription lifecycle state is sufficient for Background to stop new usage and drain valid pre-uninstall App Events.

## Context

Current uninstall behavior primarily deletes Shopify session state. ARCH-007 requires durable shop uninstall time/status and billing projection state while retaining historical UsageEvents for post-uninstall reporting/reconciliation.

## Scope

Existing app-uninstalled webhook route/service and focused tests only, plus typed Prisma use from accepted database revision.

## Out of Scope

- Publishing App Events (BACKGROUND-007/008).
- Deleting/anonymizing billing history.
- Admin operations.

## Requirements

- Process uninstall idempotently by durable Shopify shop identity.
- Set Shop.status=UNINSTALLED and uninstalledAt to the authoritative webhook processing/event time according to existing webhook conventions; preserve existing value on duplicate delivery rather than moving the boundary later.
- Mark local subscription projection so runtime no longer admits new plan entitlements; preserve current/pending handles and historical billing periods needed for reconciliation.
- Do not delete UsageEvent/BillingPeriod/ShopEntitlementCounter/adjustment/audit history required for billing correctness.
- Do not synchronously call Shopify App Events inside webhook handling.
- Keep webhook acknowledgement bounded; post-uninstall drain is Background responsibility.

## Work Items

- [ ] Inspect current APP_UNINSTALLED handler/session deletion behavior.
- [ ] Implement durable lifecycle update with Prisma transaction as needed.
- [ ] Preserve billing history.
- [ ] Add duplicate webhook and historical-usage preservation tests.

## Interfaces / Contracts

Durable handoff to Background:

```text
Shop.status=UNINSTALLED
Shop.uninstalledAt=<stable timestamp>
pending UsageEvent.occurredAt <= uninstalledAt remain publishable candidates
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-SYSTEM-TEST-003

## Acceptance Criteria

- [ ] Duplicate uninstall delivery does not move the uninstall cutoff later.
- [ ] New runtime subscription entitlement is disabled after uninstall.
- [ ] Historical/pending usage is retained.
- [ ] No App Events network call occurs in webhook request.
- [ ] Tests and repository validation pass.

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
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-SHOPIFY-003` branch and the mirrored parent-workspace `task/ARCH-007-SHOPIFY-003` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status
Ready for Review (Attempt 2)

### Files Changed

- `moda-interact/app/routes/webhooks.app.uninstalled.jsx`
- `moda-interact/app/services/shop/shop.service.ts`
- `moda-interact/tests/unit/services/shop.service.test.ts`
- `moda-interact/package.json` (verified accepted Shared range `^0.7.4`)
- `moda-interact/package-lock.json` (verified accepted root range and installed `0.7.4`)

### Work Completed

- Restored and verified the accepted SHOPIFY-002 Shared dependency baseline: `^0.7.4` in the manifest and lockfile root, resolving to `0.7.4`; npm reconciliation produced no unrelated dependency churn.
- Routed `APP_UNINSTALLED` through `ShopService.markUninstalled`.
- Used Shopify `triggeredAt` when valid, with bounded processing-time fallback.
- Added a transactional, conditional uninstall cutoff write so duplicate delivery does not move `Shop.uninstalledAt` later.
- Set the durable shop status to `UNINSTALLED` and the local subscription projection to fail-closed `NO_CONTRACT` without clearing plan handles or billing history fields.
- Retained session deletion and made no App Events call or history deletion.
- Added focused coverage for the lifecycle update and duplicate cutoff condition.

### Validation Results

- `npm test -- --run tests/unit/services/shop.service.test.ts`: passed, 5 tests.
- `npm test`: passed, 176 tests; 1 skipped.
- `npm run prisma:validate`: passed.
- `npm run build`: passed.
- `git diff --check`: passed.
- `npm ls @modainteract/moda-interact-shared --depth=0`: passed, `@modainteract/moda-interact-shared@0.7.4`.
- Lockfile inspection: passed, root range `^0.7.4` and installed package version `0.7.4`.
- `npm run typecheck`: reports the existing repository-wide JSX/type errors, including the prior uninstall service's implicit-`any` transaction diagnostic; no dependency-related errors were introduced.
- `npm run lint`: reports 10 existing repository-wide lint errors outside the dependency metadata and current correction scope.

### Deviations

- Repository-wide typecheck and lint remain non-green because of existing diagnostics; the typecheck diagnostic in `shop.service.ts` belongs to the retained Attempt 1 uninstall implementation and was not changed in this correction attempt.
- The accepted dependency metadata was already present in `HEAD`; npm reconciliation confirmed it without producing a package metadata diff.

### Assumptions

- `SubscriptionProjectionStatus.NO_CONTRACT` is the existing fail-closed projection status because billing admission accepts only `ACTIVE` and `TRIALING`.
- Invalid or absent Shopify `triggeredAt` falls back to webhook processing time.

### Unresolved Issues

- None within this task scope.

### Architectural Concerns

- None. Background remains responsible for draining eligible pre-uninstall usage events.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is architect-accepted Complete.

Attempt 2 performed exactly the narrow dependency-baseline reconciliation requested after Attempt 1:

```text
package.json
  @modainteract/moda-interact-shared = ^0.7.4

package-lock.json
  root dependency                    = ^0.7.4
  installed package version          = 0.7.4
```

Architect comparison of Attempt 1 and Attempt 2 confirms that the only repository implementation changes in Attempt 2 are `package.json` and `package-lock.json`, and those changes contain only the expected Shared 0.7.3 -> 0.7.4 restoration. No unrelated package/dependency churn was introduced.

The accepted Attempt 1 uninstall behavior remains intact:

- `APP_UNINSTALLED` routes through `ShopService.markUninstalled`;
- the durable shop is resolved by normalized Shopify domain;
- lifecycle mutation is transactional;
- `Shop.status` becomes `UNINSTALLED`;
- the first valid uninstall cutoff is preserved and duplicate delivery cannot move `uninstalledAt` later;
- subscription admission becomes fail-closed through `NO_CONTRACT`;
- current/pending plan handles, provider subscription identity, billing periods, UsageEvents, counters, allowance adjustments, audit/history state are retained;
- the webhook performs no synchronous Shopify App Events reporting;
- Shopify sessions are removed idempotently with `deleteMany`;
- valid Shopify `triggeredAt` is used with bounded processing-time fallback.

### Pre-feature-branch workflow note

This task was implemented and corrected before the workspace-wide task-feature-branch rule was introduced.

The absence of a feature-branch commit/push is therefore **not** a review defect for this task. Future task attempts follow `docs/agent-vcs-ownership-policy.md`.

### Reviewed Files

- `moda-interact/app/routes/webhooks.app.uninstalled.jsx`
- `moda-interact/app/services/shop/shop.service.ts`
- `moda-interact/tests/unit/services/shop.service.test.ts`
- `moda-interact/package.json`
- `moda-interact/package-lock.json`
- `docs/decisions/shopify/ARCH-007/SHOPIFY-003-uninstall-billing-lifecycle.md`

### Validation Reviewed

Repository-agent Completion Report records:

```text
npm ls @modainteract/moda-interact-shared --depth=0
  -> @modainteract/moda-interact-shared@0.7.4

focused ShopService tests
  -> 5 passed

full tests
  -> 176 passed, 1 skipped

Prisma validation
  -> passed

build
  -> passed

git diff --check
  -> passed
```

Repository-wide lint/typecheck retain documented pre-existing diagnostics. Attempt 2 introduced no dependency-related diagnostic.

Architect static comparison verified the package/lock correction is limited to the accepted Shared 0.7.4 baseline.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-SHOPIFY-003` is Complete.

`ARCH-007-SYSTEM-TEST-003` remains Pending/manual-gated because its other implementation/infrastructure dependencies are not yet Complete. Do not invoke it automatically.

No downstream implementation task becomes Ready solely from this acceptance.
