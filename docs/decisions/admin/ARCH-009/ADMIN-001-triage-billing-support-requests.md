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
status: ready
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-009-DATABASE-001
  - ARCH-009-SHARED-001
  - ARCH-009-SHOPIFY-001
  - ARCH-008-ADMIN-001
enables:
  - ARCH-009-ADMIN-002
created: 2026-09-09
updated: 2026-09-10
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
