---
id: ARCH-017-ADMIN-002
architecture_id: ARCH-017
title: Add operator-requested provider subscription reconciliation control
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-017-BACKGROUND-003
enables: []
created: 2026-09-19
updated: 2026-09-19
---

# ARCH-017-ADMIN-002

## Objective

Add a safe SUPER_ADMIN control to request an immediate provider reconciliation for one merchant subscription without allowing Admin to choose or force the resulting subscription state.

The action MUST do only this durable scheduling mutation:

```text
Subscription.nextReconcileAt = request timestamp
```

plus an audit record.

It MUST NOT change plan mapping, Subscription status, BillingPeriod state, pending-plan state, Shopify/provider identifiers, or sync-error fields.

`ARCH-017-BACKGROUND-003` is a hard dependency because that task makes a due `nextReconcileAt` request take priority on the next global billing-reconciliation cycle.

The existing UNMAPPED repair workflow remains separate and authoritative for mapping repair. This task does not replace it.

## Supported states

The new generic Admin control is supported for exactly:

```text
ACTIVE
TRIALING
SYNC_ERROR
FROZEN
NO_CONTRACT
```

Do NOT expose this generic action for `UNMAPPED`.

For `UNMAPPED`, Admin must continue using the existing `/billing?view=unmapped` repair workflow because an unknown/missing plan mapping may need catalogue/operational repair before a provider reread can succeed.

Typical uses of the new action include:

```text
ACTIVE + PARTNER_API_ERROR
TRIALING + transient provider failure
SYNC_ERROR after operator investigation/configuration correction
FROZEN when an operator wants an immediate Shopify re-check
NO_CONTRACT when an operator wants to verify whether Shopify now reports a contract
```

## Read before editing

Read these exact files:

```text
src/app/actions/billing-unmapped-subscriptions.ts
src/components/admin/tenant-billing.tsx
src/components/admin/tenant-detail-panel.tsx
src/app/(protected)/page.tsx
src/lib/admin/billing.ts
src/lib/admin/types.ts
src/lib/auth/platform-admin.ts
src/lib/auth/development-platform-admin.ts
src/lib/prisma.ts
tests/security/admin-tenant-billing-progressive-disclosure.test.mjs
tests/security/admin-billing-visibility.test.mjs
database/prisma/schema.prisma
docs/decisions/background/ARCH-017/BACKGROUND-003-prioritize-manual-subscription-reconciliation.md
```

Search existing Admin tests/actions for SUPER_ADMIN mutation/recheck conventions and follow them exactly.

## Authorized implementation surface

Preferred files:

```text
src/app/actions/billing-subscription-reconciliation.ts                 # new
src/components/admin/subscription-reconciliation-control.tsx          # new
src/components/admin/tenant-billing.tsx
src/components/admin/tenant-detail-panel.tsx
src/app/(protected)/page.tsx
src/lib/admin/billing.ts
src/lib/admin/types.ts
tests/security/admin-tenant-billing-progressive-disclosure.test.mjs
focused new unit/security tests for the server action
```

Use existing i18n only if the surrounding component convention requires it. Do not broaden this task into unrelated Billing UI cleanup.

No database schema/submodule edit is authorized.

## Part A — expose reconciliation scheduling state in tenant billing

### 1. Extend `TenantBilling.subscription`

In `src/lib/admin/types.ts`, add:

```ts
nextReconcileAt: Date | null;
lastSyncErrorAt: Date | null;
```

next to the existing `lastSyncedAt` / `lastSyncErrorCode` fields.

### 2. Select those fields in `getTenantBilling()`

In `src/lib/admin/billing.ts`, extend the existing Subscription select with exactly:

```ts
nextReconcileAt: true,
lastSyncErrorAt: true,
```

Do not add a second query for these fields.

## Part B — server action

### 3. Create `src/app/actions/billing-subscription-reconciliation.ts`

Use the same mutation-security shape as the existing billing Admin actions.

Required imports are conceptually:

```ts
"use server";

import {
  BillingAuditAction,
  SubscriptionProjectionStatus,
} from "@prisma/client";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { ensureDevelopmentPlatformAdmin } from "@/lib/auth/development-platform-admin";
import { requirePlatformAdminMutation } from "@/lib/auth/platform-admin";
import { prisma } from "@/lib/prisma";
```

Use the repository's existing formatting/import conventions.

Define this exact state allow-list locally in this action file:

```ts
const REQUESTABLE_SUBSCRIPTION_STATUSES = new Set<SubscriptionProjectionStatus>([
  SubscriptionProjectionStatus.ACTIVE,
  SubscriptionProjectionStatus.TRIALING,
  SubscriptionProjectionStatus.SYNC_ERROR,
  SubscriptionProjectionStatus.FROZEN,
  SubscriptionProjectionStatus.NO_CONTRACT,
]);
```

This is an action-policy allow-list, not a global feature/status registry.

### 4. Action input

Export:

```ts
export async function requestSubscriptionReconciliationAction(
  formData: FormData,
): Promise<void>
```

Require these fields:

```text
shopId
subscriptionId
reason
returnTo
```

Validation rules:

```text
shopId: non-empty string
subscriptionId: non-empty string
reason: trimmed, required, max 1000 chars
returnTo: internal path only; default "/"
```

Never accept a subscription status, plan id, billing-period id or requested resulting state from the browser.

### 5. Authorization

At action start:

```ts
const principal = await requirePlatformAdminMutation();
if (principal.role !== "SUPER_ADMIN") {
  throw new Error("SUPER_ADMIN access is required to request subscription reconciliation.");
}
```

Inside the transaction:

1. call `ensureDevelopmentPlatformAdmin(transaction, principal)` following existing development behavior;
2. re-read `PlatformAdmin` by principal id;
3. require `active=true` and `role=SUPER_ADMIN` again before mutation.

Do not trust only the pre-transaction principal object.

### 6. Preflight read

Before entering the transaction, read the subscription by `subscriptionId` with:

```text
id
shopId
status
nextReconcileAt
lastSyncedAt
lastSyncErrorCode
lastSyncErrorAt
shop.id
shop.status
shop.shopifyShopId
```

Require:

```text
subscription exists
subscription.shopId === submitted shopId
Shop.status === ACTIVE
Shop.shopifyShopId != null
subscription.status is in REQUESTABLE_SUBSCRIPTION_STATUSES
```

If status is `UNMAPPED`, return the explicit error:

```text
UNMAPPED subscriptions must be repaired from the billing mapping queue before requesting generic reconciliation.
```

For any other unsupported state, fail closed.

Do not contact Shopify from Admin.

### 7. Transaction and compare-and-set

Set:

```ts
const requestedAt = new Date();
```

Inside one Prisma transaction:

1. perform the durable SUPER_ADMIN recheck;
2. re-read the Subscription by id;
3. require it still belongs to `shopId`;
4. require its current status is still in the allowed set;
5. require the Shop is still ACTIVE and still has `shopifyShopId`;
6. update ONLY `nextReconcileAt`.

Use an optimistic `updateMany` so a concurrently changed Subscription is not silently overwritten.

The update should be equivalent to:

```ts
const updated = await transaction.subscription.updateMany({
  where: {
    id: current.id,
    shopId: current.shopId,
    status: current.status,
    nextReconcileAt: current.nextReconcileAt,
  },
  data: {
    nextReconcileAt: requestedAt,
  },
});

if (updated.count !== 1) {
  throw new Error(
    "The subscription changed while reconciliation was being requested. Reload and try again.",
  );
}
```

If Prisma requires explicit null handling for the nullable timestamp, construct the `where` object so it still compares the exact currently observed value. Do not remove the concurrency check.

### 8. Forbidden writes

The action MUST NOT write any of these fields:

```text
status
planId
observedShopifyPlanHandle
billingPeriodId
currentPeriodStart
currentPeriodEnd
trialEndsAt
cancelAtPeriodEnd
providerSubscriptionId
pendingShopifyPlanHandle
pendingPlanId
pendingEffectiveAt
lastSyncedAt
lastSyncErrorCode
lastSyncErrorAt
```

The live provider reconciliation owns those values.

### 9. Audit event

Use the existing enum value:

```ts
BillingAuditAction.BILLING_EVENT_RETRY
```

Do NOT add a database enum value in this task.

Create one `BillingAuditEvent` in the same transaction:

```text
action = BILLING_EVENT_RETRY
shopId = current.shopId
platformAdminId = principal.id
reason = operator supplied reason
relatedEntityType = "Subscription"
relatedEntityId = current.id
```

`beforeValue` must include at minimum:

```text
status
nextReconcileAt
lastSyncedAt
lastSyncErrorCode
lastSyncErrorAt
```

`afterValue` must include the same fields with:

```text
nextReconcileAt = requestedAt
```

and MUST NOT pretend a provider reconciliation has completed.

### 10. Post-commit behavior

After a successful transaction:

```ts
revalidatePath("/");
redirect(<safe returnTo with reconciliationRequested=1>);
```

Use existing query helper conventions if available. Do not redirect to the UNMAPPED queue.

## Part C — Admin UI

### 11. Pass SUPER_ADMIN capability to tenant billing UI

In `src/app/(protected)/page.tsx`, retain the result of:

```ts
const principal = await requirePlatformAdminPage();
```

instead of discarding it.

Pass:

```text
canRequestSubscriptionReconciliation = principal.role === "SUPER_ADMIN"
```

through the existing tenant-detail component boundary to `TenantBillingView`.

Do not perform role inference in the client/browser.

### 12. Add `SubscriptionReconciliationControl`

Create a small server component (no client JavaScript is required) at:

```text
src/components/admin/subscription-reconciliation-control.tsx
```

Props:

```ts
type Props = {
  shopId: string;
  subscription: TenantBilling["subscription"];
  canRequest: boolean;
  returnTo: string;
};
```

Render a bordered Admin section showing at minimum:

```text
Current subscription status
Last synced at
Last sync error code
Last sync error at
Next reconciliation at
```

For `UNMAPPED`:

- do not render the generic mutation form;
- render explanatory text that mapping repair must be used;
- render an internal link to `/billing?view=unmapped&subscriptionId=<id>`.

For the allowed statuses:

- if `canRequest=false`, render read-only state only;
- if `canRequest=true`, render a form targeting `requestSubscriptionReconciliationAction`;
- require a textarea/input named `reason`;
- include hidden `shopId`, `subscriptionId`, `returnTo`;
- button copy: `Request provider reconciliation`.

The UI must explicitly state that this action:

```text
requests a fresh Shopify/provider read;
does not force ACTIVE, cancel, unfreeze or remap the subscription.
```

### 13. Place the control on Tenant Billing > Overview

In `TenantBillingView`, place `SubscriptionReconciliationControl` in the overview stack after the existing billing summary and before or after `TenantBillingControls`.

Do not create a second global billing tab for this task.

### 14. Success notice

When the tenant detail route contains:

```text
reconciliationRequested=1
```

show a bounded success notice such as:

```text
Provider reconciliation requested. Background billing will re-read Shopify on the next reconciliation cycle.
```

Do not say reconciliation succeeded; only the request succeeded.

## Required tests

Add focused tests following the repository's current security/server-action test style.

Prove:

1. non-SUPER_ADMIN cannot request reconciliation;
2. ACTIVE is accepted;
3. TRIALING is accepted;
4. SYNC_ERROR is accepted;
5. FROZEN is accepted;
6. NO_CONTRACT is accepted;
7. UNMAPPED is rejected and directed to the existing mapping workflow;
8. Shop must be ACTIVE;
9. Shop must have `shopifyShopId`;
10. submitted `shopId` must match the Subscription's actual shop;
11. reason is required and capped at 1000 chars;
12. action updates only `nextReconcileAt` on Subscription;
13. existing `status`, `planId`, `billingPeriodId`, pending-plan state and sync-error fields are not cleared/changed by the Admin action;
14. concurrent Subscription change causes the compare-and-set to fail closed;
15. a `BillingAuditEvent` with `BILLING_EVENT_RETRY` is written with Subscription identity and reason;
16. tenant billing loader exposes `nextReconcileAt` and `lastSyncErrorAt`;
17. generic reconciliation form is hidden for UNMAPPED;
18. a SUPER_ADMIN sees the request form for an allowed state;
19. a non-SUPER_ADMIN sees reconciliation state but not a mutation control;
20. success UI says `requested`, never `completed` or `succeeded`.

## Acceptance Criteria

- [ ] The control is available from Tenant Billing Overview for eligible non-UNMAPPED states.
- [ ] Only SUPER_ADMIN can schedule it.
- [ ] UNMAPPED retains the existing dedicated repair workflow.
- [ ] Admin does not call Shopify directly.
- [ ] Admin changes only `Subscription.nextReconcileAt` plus audit state.
- [ ] No Subscription/BillingPeriod result is forced by Admin.
- [ ] The audit trail records who requested the reconciliation and why.
- [ ] UI shows current sync/retry information and accurately describes the action as a request.
- [ ] Required focused/security tests pass.
- [ ] Required repository validation passes.

## Validation

After inspecting `package.json`, run only repository-declared commands. At minimum:

- [ ] focused tests for the new server action
- [ ] affected Admin billing/security tests
- [ ] TypeScript/typecheck command declared by the repository, if present
- [ ] lint command declared by the repository, if present
- [ ] production build command declared by the repository, if required by current convention
- [ ] `git diff --check`

Do not modify the database schema to add a new audit enum solely for this feature.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. finish the Completion Report;
2. set task status to `review`;
3. return control to `moda_architect`;
4. STOP.

Do not implement additional billing repair workflows or system tests in this task.
