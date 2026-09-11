---
id: ARCH-010-SHARED-005
architecture_id: ARCH-010
title: Add merchant top-up refund billing message contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 22
executor: copilot
claimed_at: 2026-09-11T16:08:10Z
attempt: 1
depends_on: []
enables:
  - ARCH-010-SHARED-006
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-SHARED-005: Add merchant top-up refund billing message contracts

## Objective

Add the canonical merchant billing system-message codes required by ARCH-010 partial purchased-top-up refunds.

## Required codes

Extend the existing billing system-message contract with exactly:

```text
BILLING_REFUND_REQUEST_RECEIVED
BILLING_REFUND_COMPLETED
BILLING_REFUND_REJECTED
```

Use the existing `BILLING_SYSTEM_MESSAGE_CODES`, `BillingSystemMessageCodeSchema` and `createMerchantBillingSystemSourceKey` conventions.

Do not introduce a second message-code registry.

## Idempotency identity

Refund messages use the durable `RecoveryCreditRefund.id` as `eventIdentity`.

Examples:

```text
billing-system:<shopId>:BILLING_REFUND_REQUEST_RECEIVED:<refundId>:1
billing-system:<shopId>:BILLING_REFUND_COMPLETED:<refundId>:1
billing-system:<shopId>:BILLING_REFUND_REJECTED:<refundId>:1
```

Do not put purchase amount, merchant PII or support-message text into source keys.

## Compatibility

The frozen ARCH-009 Shared branch may already contain equivalent codes. At task preflight:

- if exact names/values already exist in the integrated source, do not duplicate them; add/retain the ARCH-010 acceptance tests and report reuse;
- if values differ, STOP and return the conflict to `moda_architect`.

Do not import frozen ARCH-009 task metadata as a dependency.

## Required tests

Prove:

1. all three exact values are included in `BillingSystemMessageCodeSchema`;
2. deterministic refund source keys are stable;
3. long shop/refund IDs remain bounded through existing helper semantics;
4. unrelated billing/WhatsApp contracts are unchanged.

Run repository unit/type/build validation declared by `package.json` and `git diff --check`.

## Non-goals

Do not publish the package, edit consumer repositories, add refund quantities/status enums or create queue contracts.

## Stop conditions

STOP if equivalent refund message codes already exist with different values/semantics or if adding the codes would require changing a consumer repository. Report the exact conflict to `moda_architect`.

## Completion Report

### Status
In Progress.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
