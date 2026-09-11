---
id: ARCH-009-ADMIN-001
architecture_id: ARCH-009
title: Triage merchant billing support requests into deterministic lifecycle actions
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 60
executor: copilot
claimed_at: 2026-09-11T01:43:49Z
attempt: 1
depends_on:
  - ARCH-009-DATABASE-001
  - ARCH-009-SHARED-001
  - ARCH-009-SHOPIFY-001
  - ARCH-008-ADMIN-001
enables:
  - ARCH-009-ADMIN-002
created: 2026-09-09
updated: 2026-09-11T01:52:00Z
---

# ARCH-009-ADMIN-001

## Objective

Human Admin classifies exact merchant message as:

```text
PLAN_CHANGE
SUBSCRIPTION_CANCELLATION
RECOVERY_CREDIT_REFUND
```

No NLP auto-classification.

## Authorization

ADMIN/SUPER_ADMIN triage.

SUPER_ADMIN approval later.

## Support billing context

Server-side:

```text
current/pending plan
current period
Free remaining
purchased granted/committed/reserved/refunding/available
current cancellation request
recent pack purchases
recent refund requests
```

No provider network.

## PLAN_CHANGE

Button:

```text
Send Change plan action
```

Message code:

```text
BILLING_PLAN_CHANGE_ACTION_REQUIRED
```

CTA /app/billing.

No target plan selected.

No Subscription mutation.

## SUBSCRIPTION_CANCELLATION

Reload current subscription and require ACTIVE/TRIALING, provider ID and plan
handle.

Create/reuse:

```text
subscription-cancel:<shopId>:<providerSubscriptionId>
source MERCHANT_SUPPORT
sourceMessageId
providerSubscriptionIdSnapshot
planHandleSnapshot
currentPeriodEndSnapshot
mode END_OF_CYCLE
status REQUESTED
```

No approval.

## RECOVERY_CREDIT_REFUND

Human selects same-shop ACTIVE purchase.

Create/reuse:

```text
recovery-credit-refund:<purchaseId>
source MERCHANT_SUPPORT
sourceMessageId
originalUsageEventIdSnapshot
billingPeriodIdSnapshot
planHandleSnapshot
eventHandleSnapshot
creditsSnapshot
status REQUESTED
```

No settlement mode/hold.

## Pagination

Purchases:

```text
pageSize default 20 max 50
createdAt DESC,id DESC
shopId in DB query
```

## i18n

All Admin-visible copy through existing ICU catalogues.

## Tests

- Admin triage authorized;
- no message text auto-classification;
- plan change no Subscription mutation;
- exact message code;
- cancellation snapshots current identity;
- replay;
- cross-shop rejection;
- refund same-shop ACTIVE only;
- refund replay;
- no hold;
- max 50;
- i18n.

## Validation

```bash
npm test
npx tsc --noEmit
npm run lint
npm run build
npm run prisma:validate
git diff --check
```

## Stop

Return review and STOP.

## Completion Report

### Status
Ready for Review
### Files Changed
- `src/lib/admin/billing-lifecycle.ts`
- `src/app/actions/billing-lifecycle.ts`
- `src/app/(protected)/merchant-support/page.tsx`
- `src/components/admin/merchant-support-inbox.tsx`
- `src/i18n/locales/en.json`
- `src/i18n/required-keys.ts`
- `tests/security/admin-billing-lifecycle.test.mjs`
### Work Completed
- Added ADMIN/SUPER_ADMIN-protected deterministic billing triage actions for PLAN_CHANGE, SUBSCRIPTION_CANCELLATION, and RECOVERY_CREDIT_REFUND.
- Added bounded server-side billing context with current and pending plan identity, free remaining, purchased-credit granted/committed/reserved/refunding/available values, recent purchases, cancellation state, and refund state.
- Added exact shared system code/version for plan-change actions, `/app/billing` workflow ownership, END_OF_CYCLE cancellation snapshots, same-shop ACTIVE purchase refund snapshots, replay-safe request keys, and durable audit snapshots.
- Kept provider calls, subscription mutation, settlement mode, and refund holds out of the admin request path.
- Added ICU catalogue keys and focused security/i18n regression coverage.
### Validation Results
- Focused `node --test tests/security/admin-billing-lifecycle.test.mjs`: passed, 2 tests.
- `git diff --check`: passed.
- `npm run lint`: passed with two pre-existing `queue-monitor.tsx` exhaustive-deps warnings.
- `npm test`: blocked by the existing ungenerated Prisma client (`@prisma/client did not initialize yet`) in this isolated checkout.
- `npx tsc --noEmit`: blocked by the same ungenerated Prisma client/types.
- `npm run prisma:validate`: blocked because this admin checkout has no `database/prisma/schema.prisma`.
- `npm run build`: blocked by the same missing Prisma schema during `prisma:generate`.
### Deviations
- The admin repository does not contain its Prisma schema or generated client in this checkout; the implementation follows the accepted ARCH-009 database contract and uses the existing parameterized raw-SQL admin boundary.
### Assumptions
- ARCH-009 shared release `0.9.0` is available to the synchronized deployment/install environment.
### Unresolved Issues
- Full typecheck, Prisma validation, build, and existing integration security scripts require the admin repository’s generated Prisma client/schema materialization.
### Architectural Concerns
- None beyond the repository-owned schema materialization prerequisite.

### Git / VCS

Task branch: `task/ARCH-009-ADMIN-001`

Implementation repository commit: `1a80ffb`
Implementation remote branch: `origin/task/ARCH-009-ADMIN-001`
Implementation pushed: yes

Parent workspace report branch: `task/ARCH-009-ADMIN-001`

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
