---
id: ARCH-007-SHOPIFY-002
architecture_id: ARCH-007
title: Build merchant billing plan state, hosted-plan actions and billing SYSTEM-message CTAs
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 70
executor: null
claimed_at: null
attempt: 3
depends_on: 
  - ARCH-007-SHOPIFY-001
enables: 
  - ARCH-007-SYSTEM-TEST-001
  - ARCH-007-SYSTEM-TEST-002
created: 2026-09-07
updated: 2026-09-08
---

# ARCH-007-SHOPIFY-002: Build merchant billing plan state, hosted-plan actions and billing SYSTEM-message CTAs

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Update merchant-facing billing/onboarding/support UI so Free/paid current and pending plan state is clear, plan changes use Shopify hosted pricing, and billing SYSTEM messages render safe UI-owned actions.

## Context

The existing merchant app redirects merchants without subscription to Billing and already has a MerchantSupportMessage channel. ARCH-007 needs explicit no-contract plan selection, current/pending plan display and upgrade actions without embedding URLs in translated SYSTEM message bodies.

## Scope

Merchant billing/onboarding routes/components, merchant-support read DTO if needed, i18n keys and focused tests. Use SHOPIFY-001 service; do not duplicate Partner queries in components.

## Out of Scope

- Admin plan registration.
- Background generation of billing system messages.
- Shopify plan configuration.
- Usage publisher.

## Requirements

- No-contract merchant is sent to Shopify hosted plan-selection page; external navigation must use the correct top-level target pattern already approved by Shopify/app framework.
- Display mapped current plan name/state and current billing cycle where applicable. For Free, display lifetime allowance/remaining usage from Moda data; for paid, display Moda usage and provider commercial information available from local projection without inventing charges.
- Display pending plan change and effective date separately. Current entitlement remains current plan.
- Merchant-support read result must expose `systemCode`/`systemVersion` required for deterministic billing CTA rendering while preserving translation behavior.
- UI mapping: FREE warning -> View plans; FREE exhausted -> Upgrade plan; upgraded/downgrade scheduled/subscription ended/safety limit -> architecture-appropriate Billing/View plan action. Route destinations are application constants owned by UI, not translated body text.
- Unknown system code has no privileged/actionable fallback.
- Add translation keys for action labels/plan-state copy using existing i18n conventions.

## Work Items

- [x] Update billing/onboarding presentation and hosted pricing action.
- [x] Expose safe system-code metadata to merchant UI if not already available.
- [x] Add deterministic CTA mapping.
- [x] Add focused loader/action/component/i18n tests including pending downgrade and unmapped/no-contract cases.

## Interfaces / Contracts

Merchant-facing route target:

```text
/app/billing
  -> Shopify hosted pricing selection for choose/change plan
```

SYSTEM message body remains translatable semantic text; CTA destination is derived from canonical code.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-SYSTEM-TEST-001
- ARCH-007-SYSTEM-TEST-002

## Acceptance Criteria

- [x] Free merchant can see allowance state and reach Shopify plan selection.
- [x] Paid merchant sees current plan and scheduled pending change without premature entitlement display.
- [x] Exhaustion system message renders Upgrade action exactly once per message without URL-in-body coupling.
- [x] Unknown/unmapped billing state fails safely with support/configuration guidance rather than paid feature access.
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

Ready for Review (Attempt 3)

### Files Changed

- `app/routes/app.billing.tsx`
- `app/routes/app.merchant-support.jsx`
- `app/services/billing/billing.service.ts`
- `app/services/merchant-support/merchant-support.service.ts`
- `app/services/merchant-support/system-message-actions.ts`
- `app/i18n/locales/*.json`
- `tests/unit/billing-ui.test.ts`
- `tests/unit/billing-i18n.test.ts`
- `tests/unit/merchant-support-route.test.ts`
- `tests/unit/merchant-support-service.test.ts`
- `package.json`
- `package-lock.json`

### Work Completed

- Added merchant billing state loading for current Free/paid plans, allowance/usage, billing cycle, pending plan changes, and fail-closed unmapped/no-contract handling.
- Added Shopify-hosted plan-selection navigation using the app billing route constants.
- Added safe SYSTEM message metadata propagation and canonical billing CTA mapping without URL parsing from translated bodies.
- Added billing translation keys across all locale catalogues and focused regression coverage.
- Reconciled `@modainteract/moda-interact-shared` manifest, lockfile and installed dependency at architect-required version `0.7.4`.
- Added the complete hosted-pricing redirect regression: `/app/billing` no-contract redirect to `/app/billing/select`, followed by Shopify pricing navigation with `target: "_top"`.
- Added pending paid-to-Free downgrade coverage proving current paid entitlement remains current while the pending change is separate.
- Added unmapped projection fail-closed presentation coverage and all-locale ARCH-007 billing-key coverage.
- Narrowed the merchant-support system CTA lookup once so unknown codes remain non-actionable and nullable action access is safe.
- Updated subscription-ended SYSTEM-message persistence to use `BILLING_SYSTEM_MESSAGE_CODES.SUBSCRIPTION_ENDED` from Shared 0.7.4, producing the canonical `BILLING_SUBSCRIPTION_ENDED` value.
- Added an executable regression that captures the actual persisted system code, verifies its `/app/billing` CTA mapping, and rejects the legacy `SUBSCRIPTION_ENDED` literal.

### Validation Results

- Focused Vitest: billing/service and merchant-support regression suite passed 29 tests; the complete focused billing set previously passed 52 tests.
- Full Vitest: 27 files passed, 1 skipped; 174 tests passed, 1 skipped.
- `npm run prisma:validate`: passed.
- `npm run build`: passed.
- `git diff --check`: passed.
- `npm ls @modainteract/moda-interact-shared --depth=0`: resolved `0.7.4`.
- Focused ESLint: changed billing producer/test and CTA consumer surfaces passed.
- `npm run lint`: baseline remains at 11 errors in unrelated/pre-existing files (`PlanSelector.jsx`, `app._index.jsx`, `app.billing.select.jsx`, `app.merchant-support.jsx`, `privacy.tsx`, and webhook tests).
- `npm run typecheck`: passed with the repository's existing unsupported-TypeScript-version warning.

### Deviations

- Regenerated the Prisma client required by the accepted ARCH-007 schema so the billing enums and typed transaction client are available.
- Refreshed the app lockfile/install state to consume Shared package `0.7.4`, which provides the canonical billing entrypoint.

### Assumptions

- Shopify hosted pricing navigation continues to use the existing top-level redirect pattern at `/app/billing/select`.

### Unresolved Issues

- Repository-wide lint remains non-zero due to documented pre-existing diagnostics; focused behavioral tests, focused lint, typecheck, build and dependency resolution pass.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 is architect-accepted Complete.

The final Attempt 2 correction is implemented correctly:

- `billing.service.ts` imports `BILLING_SYSTEM_MESSAGE_CODES` from the accepted Shared 0.7.4 billing entrypoint;
- subscription-ended SYSTEM-message persistence uses `BILLING_SYSTEM_MESSAGE_CODES.SUBSCRIPTION_ENDED`;
- the persisted canonical value is therefore `BILLING_SUBSCRIPTION_ENDED`;
- `systemVersion = "1"` and the existing deterministic source-key/translation/idempotency behavior remain unchanged;
- the executable billing-service regression captures the actual value supplied to persistence and feeds it into `getMerchantSystemMessageAction(...)`;
- the canonical persisted value resolves to:
  - `href: "/app/billing"`;
  - `labelKey: "billing.viewPlans"`;
- legacy `SUBSCRIPTION_ENDED` remains non-actionable.

The accepted Attempt 2 behavior remains intact:

1. `package.json` and `package-lock.json` resolve `@modainteract/moda-interact-shared@0.7.4`, with the lockfile installing exact 0.7.4.
2. A no-contract merchant follows `/app/billing -> /app/billing/select -> Shopify hosted pricing`.
3. Hosted Shopify pricing navigation uses top-level `target: "_top"`.
4. Current paid entitlement remains current while a pending Free downgrade is displayed separately.
5. `UNMAPPED` billing projection fails closed rather than granting paid presentation/entitlement.
6. Free allowance/remaining state is Moda-derived.
7. `systemCode` / `systemVersion` are exposed for merchant-support rendering.
8. Known billing SYSTEM codes map to UI-owned routes/labels rather than URLs embedded in translated message bodies.
9. Unknown system codes have no actionable fallback.
10. Every ARCH-007 `billing.*` key exists in all 20 locale catalogues.

The fact that some non-English billing catalogue values are still English is not a SHOPIFY-002 defect. Complete natural-language authenticated merchant UI translation is owned by `ARCH-005-SHOPIFY-004`, which is now unblocked by this acceptance.

### Reviewed Files

- `moda-interact/app/routes/app.billing.tsx`
- `moda-interact/app/routes/app.billing.select.jsx`
- `moda-interact/app/routes/app.merchant-support.jsx`
- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/app/services/merchant-support/merchant-support.service.ts`
- `moda-interact/app/services/merchant-support/system-message-actions.ts`
- `moda-interact/tests/unit/services/billing.service.test.ts`
- `moda-interact/tests/unit/billing-ui.test.ts`
- `moda-interact/tests/unit/billing-i18n.test.ts`
- `moda-interact/tests/unit/merchant-support-route.test.ts`
- `moda-interact/tests/unit/merchant-support-service.test.ts`
- `moda-interact/package.json`
- `moda-interact/package-lock.json`

### Validation Reviewed

Repository-agent Completion Report records:

- focused tests: 29/29 passed;
- full Vitest: 174 passed, 1 skipped;
- Prisma validation: passed;
- build: passed;
- typecheck: passed with the repository's existing unsupported-TypeScript-version warning;
- focused lint on changed surfaces: passed;
- Shared dependency verification: resolved 0.7.4;
- `git diff --check`: passed;
- repository-wide lint retains 11 documented pre-existing/baseline errors.

Architect inspection additionally verified:

- the producer uses the Shared constant directly;
- the regression captures the actual persisted SYSTEM code;
- the captured code maps to the expected billing CTA;
- the legacy literal remains rejected;
- the lockfile records exact installed Shared 0.7.4;
- hosted pricing, pending-downgrade, `UNMAPPED`, and all-locale billing-key regressions remain present.

The extracted selective review archive does not include installed `node_modules`, so the architect did not rerun the Node suite from the review copy.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-SHOPIFY-002` is Complete.

Cross-architecture consequence:

`ARCH-005-SHOPIFY-004` is now Ready because all of its explicit dependencies are architect-accepted Complete:

```text
ARCH-005-SHOPIFY-002 Complete
ARCH-006-SHOPIFY-003 Complete
ARCH-007-SHOPIFY-002 Complete
```

`ARCH-007-SHOPIFY-004` remains Pending because `ARCH-007-SHARED-006` and `ARCH-007-ADMIN-005` are not yet Complete. DATABASE-005 and SHOPIFY-002 are now Complete.

ARCH-007 system-test tasks remain Pending/manual-gated. Do not start them automatically.
