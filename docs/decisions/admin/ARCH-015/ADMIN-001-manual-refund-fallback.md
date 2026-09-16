---
id: ARCH-015-ADMIN-001
architecture_id: ARCH-015
title: Preserve manual recovery-credit REFUND/CREDIT fallback without double settlement
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-015-BACKGROUND-003
enables:
- ARCH-015-SYSTEM-TEST-001
created: 2026-09-15
updated: 2026-09-16
---

# ARCH-015-ADMIN-001

## Objective

Align the existing Admin recovery-credit refund settlement UI/service with ARCH-015 so Admin performs provider REFUND/CREDIT only for refunds explicitly routed to `PROVIDER_ACTION_REQUIRED`, while preventing duplicate monetary action after an automated App Event correction was submitted.

## Authorized implementation surface

```text
src/lib/admin/recovery-credit-refund-settlement.ts
src/lib/admin/recovery-credit-refunds.ts
src/components/admin/recovery-credit-refunds.tsx
src/app/actions/recovery-credit-refunds.ts
src/lib/admin/types.ts
tests/security/admin-recovery-credit-refund*.test.mjs
# directly affected unit tests
```

No Shopify App Event submission from Admin.

## Manual-action eligibility

Normal manual provider action is available only when:

```text
refund.status == PROVIDER_ACTION_REQUIRED
purchase.status == WITHDRAWN
purchase.reservedAmount == 0
frozen finalCreditQuantity/expectedProviderAmount/currency exist
```

Before allowing action, inspect the explicit ARCH-015-DATABASE-002 relation:

```text
refund.automaticCorrectionUsageEventId
refund.automaticCorrectionUsageEvent
```

Normal manual provider action requires `automaticCorrectionUsageEventId == null`.

If the link is non-null, do not issue a new manual monetary action regardless of whether the linked UsageEvent is PENDING, IN_FLIGHT, RETRYABLE, REPORTED or NEEDS_ATTENTION. Surface bounded "automatic provider correction already exists; reconcile first" state.

The `sourceType/sourceId` pair on UsageEvent remains useful consistency evidence, but Admin MUST NOT use a loose source query as the authority for whether an automatic correction exists; the typed refund FK is authoritative.

## Evidence

Admin must record:

```text
providerActionKind = REFUND | CREDIT
providerReference
providerAmount
providerCurrency
explicit confirmation
```

Do not offer a generic "mark complete" button.

System verifies exact amount/currency against frozen expected values.

Match => complete using existing entitlement/audit/system-message semantics.

Mismatch => NEEDS_ATTENTION.

## Existing lock action

If the old workflow has a `lockRecoveryCreditRefund` step from REQUESTED, normal ARCH-015 flow should no longer require an administrator to promote a newly REQUESTED refund manually; Background decides automatic vs manual.

Retain backward-compatible lock behavior only if current supported operations require it, and it MUST refuse when `automaticCorrectionUsageEventId` is non-null.

Do not let Admin change historical purchase provenance or recalculate from current plan prices.

## UI evidence

Display:

- purchase original plan handle;
- purchase event handle;
- purchase billing period/provider context snapshot;
- original provider purchase amount/currency;
- frozen final refundable credits;
- frozen expected provider amount/currency;
- automatic correction presence/state, if any;
- reason Background routed manual action;
- recorded provider action/reference/evidence.

## Tests

- PROVIDER_ACTION_REQUIRED permits exact evidence submission;
- REQUESTED automatic-in-progress refund cannot be manually settled;
- non-null automaticCorrectionUsageEventId blocks manual provider action;
- exact evidence completes;
- mismatch becomes NEEDS_ATTENTION;
- no generic mark-complete path;
- SUPER_ADMIN authorization/audit preserved;
- entitlement decremented exactly once;
- no App Events submission introduced.

## Stop conditions

STOP if existing Admin task must become provider monetary authority, if ARCH-015-DATABASE-002 relation fields are unavailable, or if double-settlement prevention cannot be achieved through the explicit refund->automatic-correction UsageEvent relation.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
