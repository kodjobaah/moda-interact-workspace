---
id: ARCH-007-ADMIN-005
architecture_id: ARCH-007
title: Add recovery-credit pack fields to billing plan catalog
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: review
priority: 65
executor: copilot
claimed_at: 2026-09-08T21:50:19Z
attempt: 1
depends_on:
  - ARCH-007-ADMIN-001
  - ARCH-007-DATABASE-005
  - ARCH-007-SHARED-006
enables:
  - ARCH-007-SHOPIFY-004
created: 2026-09-08
updated: 2026-09-08
---
# ARCH-007-ADMIN-005: Add recovery-credit pack fields to billing plan catalog

## Exact product rule

SUPER_ADMIN configures Moda's mapping to Shopify App Pricing. Admin does not set Shopify monetary prices.

Add these fields to the existing BillingPlan catalog create/edit presentation:

```text
recoveryCreditPackEnabled
recoveryCreditsPerPack
shopifyRecoveryCreditPackEventHandle
includedRecoveryConversationAllowance
```

## Server-side validation

When `recoveryCreditPackEnabled=false`:
- pack size and pack event handle must be null/empty.

When `recoveryCreditPackEnabled=true`:
- `recoveryCreditsPerPack` must be a positive integer;
- `shopifyRecoveryCreditPackEventHandle` must be trimmed, non-empty;
- it must differ from `shopifyUsageEventHandle`.

FREE:
- existing `freeLifetimeConversationAllowance` remains required;
- existing normal `shopifyUsageEventHandle` remains null;
- top-up meter is allowed.

PAID_METERED:
- existing normal `shopifyUsageEventHandle` remains required;
- `includedRecoveryConversationAllowance` must be a non-negative integer when top-ups are enabled.

Do not add a money/price input.

## Required copy

The form/help text must state:

```text
"Pack price is configured in Shopify App Pricing. Moda stores only the pack size and Shopify meter mapping."
```

and:

```text
"Configure a cheaper recovery-credit-pack meter rate on higher paid plans in Shopify if that is the intended commercial policy."
```

INTERNATIONALISATION: these quoted English strings define the required
source-language meaning only. They MUST be implemented as keys in the existing
ARCH-005 Admin ICU/i18n catalogue path, not embedded as English literals in the
component. Reuse the current Admin locale resolver/runtime and
`src/i18n/locales/*`; update `src/i18n/required-keys.ts` when that is the
repository convention. Add each new key to every Admin locale catalogue currently
declared by the repository. Do not create a second i18n mechanism.

## Audit

Every change uses existing `PLAN_CATALOG_CHANGED` audit semantics with bounded before/after data. Include the four new fields.

## Tests

Prove all validation combinations above, SUPER_ADMIN mutation protection, audit writing, and that no price field exists in the action schema/UI.

Also prove the new recovery-credit-pack Admin copy resolves through the existing
Admin ICU catalogue path and that required-key/catalogue validation remains
complete. A source-regex assertion alone is not sufficient if the repository has
a behavioral i18n test helper available.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-ADMIN-005` branch and the mirrored parent-workspace `task/ARCH-007-ADMIN-005` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status
Implementation complete; returned to review (Attempt 1)

### Files Changed
In `moda-interact-admin`:

- `src/app/actions/billing-plan.ts`
- `src/components/admin/billing-plan-catalog.tsx`
- `src/i18n/locales/en.json`
- `src/i18n/required-keys.ts`
- `src/lib/admin/billing-plan-audit.ts`
- `src/lib/admin/billing-plan-validation.ts`
- `tests/security/admin-billing-plan.test.mjs`

### Work Completed
- Added validation and persistence mapping for `recoveryCreditPackEnabled`, `recoveryCreditsPerPack`, `shopifyRecoveryCreditPackEventHandle`, and `includedRecoveryConversationAllowance`.
- Enforced disabled-pack clearing, positive pack size, non-empty distinct Shopify meter handle, and non-negative paid-plan included allowance rules.
- Added the recovery-credit pack controls and required ICU help copy to the BillingPlan catalog without adding a monetary price input.
- Extended `PLAN_CATALOG_CHANGED` audit before/after snapshots to include all four fields, including toggle mutations.
- Added focused validation, security, audit, no-price-field, and ICU catalogue coverage.
- Implementation commit: `e1e4017` (`feat(admin): map recovery credit pack billing fields`).
- Implementation branch pushed: `task/ARCH-007-ADMIN-005`.

### Validation Results
- `npm test -- --test-name-pattern='billing plan|recovery-credit pack|recovery-credit'`: passed, 117/117.
- `npm test`: passed, 117/117.
- `npm run prisma:validate`: passed.
- `npx tsc --noEmit`: passed using the accepted DATABASE-005 schema revision for generated Prisma client validation.
- `npm run lint`: passed with two pre-existing `queue-monitor.tsx` exhaustive-deps warnings and no errors.
- Targeted Prettier check: passed for all seven changed files.
- `npm run build`: passed against the accepted DATABASE-005 schema revision; existing Next.js workspace-root, BullMQ dynamic dependency, and missing optional `@valkey/valkey-glide` warnings remained.
- `git diff --check`: passed.
- Nested `database` submodule gitlink staged: no.

### Deviations
- The Admin checkout's nested `database` submodule remains pinned at `7ed22538d1a6f04bc3b7c48924add6add0f74801`, before DATABASE-005. Prisma client generation and production build validation temporarily used the accepted DATABASE-005 revision `b5a184ca53459bdd6c58e7f01bdcceb1aa652918`; the submodule checkout was restored and no gitlink update was staged.

### Assumptions
- The accepted DATABASE-005 schema revision is available to the Admin validation environment and will be present through the dependency integration path before runtime deployment.

### Unresolved Issues
- The Admin repository's nested database pointer still requires the normal dependency integration/update outside this task before a clean checkout can regenerate the new Prisma client without the accepted DATABASE-005 schema revision.

### Architectural Concerns
- None introduced by this implementation. Admin continues to store Shopify meter mappings and allowance configuration, while Shopify App Pricing remains the source of monetary pack pricing.

## Architect Review

### Review Status
Pending

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Pending

### Follow-up
None.

