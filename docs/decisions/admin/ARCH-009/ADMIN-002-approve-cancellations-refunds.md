---
id: ARCH-009-ADMIN-002
architecture_id: ARCH-009
title: Approve cancellation/refund operations and confirm manual Shopify refund settlement
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-009-ADMIN-001
  - ARCH-009-BACKGROUND-001
  - ARCH-009-BACKGROUND-002
enables:
  - ARCH-009-ADMIN-003
created: 2026-09-09
updated: 2026-11-05
---

# ARCH-009-ADMIN-002

## Authorization

Only active SUPER_ADMIN mutates.

## Cancellation approval

Display current/snapshot billing identity.

Expose exactly four enum modes, not booleans:

```text
END_OF_CYCLE
IMMEDIATE_NO_PRORATION
IMMEDIATE_PRORATED
IMMEDIATE_SKIP_FINAL_USAGE
```

Approval REQUESTED -> APPROVED:

```text
mode
approvedByPlatformAdminId
approvedAt
reason 1..1000
version+1
audit SUBSCRIPTION_CANCELLATION
```

Reject REQUESTED:

```text
REJECTED
reason
audit
BILLING_CANCELLATION_REJECTED once
```

Do not reject after providerAcceptedAt as if no provider action occurred.

## Refund approval

Display purchase/snapshots/counter including refunding and Shared available.

Require:

```text
purchase ACTIVE
available >= creditsSnapshot
```

Modes exactly:

```text
CURRENT_CYCLE_APP_EVENT_CORRECTION
PARTNER_DASHBOARD_REFUND
```

Correction mode enabled only when server proves:

```text
original REPORTED
original billingPeriodId == current billingPeriodId
current meter == snapshot
current plan == snapshot
```

Approval REQUESTED -> APPROVED with settlementMode, actor, reason, audit.

## Provider confirmation

For PROVIDER_ACTION_REQUIRED.

PARTNER_DASHBOARD_REFUND instruction:

```text
Issue refund in Shopify Partner Dashboard.
Use Shopify charge/invoice monetary source.
Do not enter Moda amount.
Return and record provider reference.
```

Form:

```text
refundId
providerReference
confirmation checkbox
```

Reference 1..512.

CURRENT_CYCLE correction cannot confirm until correction UsageEvent REPORTED.

Transition:

```text
PROVIDER_CONFIRMED
providerReference
providerConfirmedByPlatformAdminId
providerConfirmedAt
audit
```

Admin never calls Shopify network.

## Tests

- ADMIN denied;
- SUPER_ADMIN allowed;
- enum modes only;
- duplicate approval idempotent;
- refund insufficient denied;
- refunding subtracts availability;
- correction mode server eligibility;
- dashboard no Moda amount;
- bounded provider ref;
- correction not confirm before REPORTED;
- no provider call;
- audit;
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

## Architect frontier reconciliation — 2026-11-05

ARCH-009-ADMIN-002 is Pending because ARCH-009-ADMIN-001 is not Complete. At refreshed origin/main 4b300e7ec, ADMIN-001 is Ready; its published task branch records Review, not accepted completion. Neither state satisfies this dependency. No implementation review or acceptance is implied. Preserve Attempt 0, executor null and claimed_at null. ADMIN-003 remains Pending because ADMIN-002 and ARCH-007-ADMIN-004 are not Complete. No task was claimed and no implementation worktree was created.

## Architect supersession — 2026-11-05

Explicitly authorized by the developer. Superseded; do not claim or implement this legacy definition. Preserve all earlier attempt, implementation and review history; supersession does not accept the old implementation.

Binding replacements: [ARCH-010 lifecycle ownership](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md) removes the local cancellation state machine and assigns subscription cancellation to Shopify. [ARCH-015 Admin refund replacement](../ARCH-015/ADMIN-001-manual-refund-fallback.md) owns the current refund workflow and guarded provider settlement. Remaining Woo-specific support stays in ARCH-027-ADMIN-001.
