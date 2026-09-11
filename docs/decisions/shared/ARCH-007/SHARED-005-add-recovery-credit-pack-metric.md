---
id: ARCH-007-SHARED-005
architecture_id: ARCH-007
title: Add canonical recovery-credit pack billing metric
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
status: complete
priority: 37
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-007-DATABASE-005
enables:
  - ARCH-007-SHARED-006
created: 2026-09-08
updated: 2026-09-08
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-SHARED-005: Add canonical recovery-credit pack billing metric

## Exact change

In the canonical Shared billing contract, add exactly:

```text
RECOVERY_CREDIT_PACK_PURCHASE
```

to `BILLING_USAGE_METRICS`.

Do not rename existing values.

The Database `UsageMetric` enum and Shared `BILLING_USAGE_METRICS` must match exactly for the new value.

Do NOT add:
- `INBOUND_AUTOMATED_MESSAGE`;
- `INBOUND_CUSTOMER_MESSAGE`;
- `COMMERCE_AGENT_TURN`;
- top-up monetary prices;
- another idempotency helper when `createShopifyUsageIdempotencyKey(shopId, usageEventId)` already satisfies the billing-event identity requirement.

## Required files

Inspect and update only the Shared billing contract/tests/export metadata required by the current package layout, principally:

```text
src/billing.ts
src/billing.test.ts
package.json only if normal implementation metadata requires it
```

Add tests proving parsing accepts the new metric and all existing metric values remain unchanged.

Do not publish in this task.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-SHARED-005` branch and the mirrored parent-workspace `task/ARCH-007-SHARED-005` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status
Ready for Review (Attempt 1)

### Files Changed
- `moda-interact-shared/src/billing.ts`
- `moda-interact-shared/src/billing.test.ts`

### Work Completed
- Added `RECOVERY_CREDIT_PACK_PURCHASE` to the canonical `BILLING_USAGE_METRICS` tuple and derived schema.
- Added executable assertions that the new metric parses and all existing metric values remain unchanged.

### Validation Results
- `npm test`: passed, 104 tests passed and 1 skipped.
- `npm run typecheck`: passed.
- `npm run build`: passed, including billing ESM and declaration output.
- `git diff --check`: passed.

### Deviations
None.

### Assumptions
- The existing Database `UsageMetric` contract is the authoritative matching dependency, and no package version or publication change is required for this source-level contract update.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is architect-accepted Complete.

The implementation matches the exact SHARED-005 contract:

- `RECOVERY_CREDIT_PACK_PURCHASE` is added to canonical `BILLING_USAGE_METRICS`;
- existing metric values remain unchanged and in their existing order;
- `BillingUsageMetricSchema` continues to derive from the canonical tuple;
- focused regression coverage proves the complete canonical metric list and direct parsing of `RECOVERY_CREDIT_PACK_PURCHASE`;
- no inbound-message/agent-turn billing metric was added;
- no new idempotency helper was introduced;
- package/source publication metadata was not changed;
- package version remains `0.7.4`;
- no publication was performed.

Cross-contract inspection confirms the accepted DATABASE-005 `UsageMetric` enum now matches the Shared tuple exactly:

```text
RECOVERY_CONVERSATION
OUTBOUND_AUTOMATED_MESSAGE
DELIVERED_WHATSAPP_MESSAGE
RECOVERY_CREDIT_PACK_PURCHASE
```

### Reviewed Files

- `moda-interact-shared/src/billing.ts`
- `moda-interact-shared/src/billing.test.ts`
- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- accepted DATABASE-005 `UsageMetric` enum
- `docs/decisions/shared/ARCH-007/SHARED-005-add-recovery-credit-pack-metric.md`

### Validation Reviewed

Repository-agent Completion Report records:

- `npm test`: 104 passed, 1 skipped;
- `npm run typecheck`: passed;
- `npm run build`: passed;
- `git diff --check`: passed.

Architect inspection additionally verified:

- `package.json` and `package-lock.json` remain at `0.7.4`;
- the billing entrypoint/export already exists and requires no export-surface change;
- no forbidden inbound/agent billing metrics are present;
- the Database and Shared canonical metric lists align exactly.

The extracted selective archive does not include installed `node_modules`, so the architect did not rerun the Node suite from the review copy.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-SHARED-006` is now Ready.

SHARED-006 is publication-only and must publish the architect-accepted SHARED-005 source contract as exactly:

```text
@modainteract/moda-interact-shared@0.8.0
```

Until SHARED-006 is completed, architect-accepted, and publication is verified, all consumer repositories must continue to treat `0.7.4` as the current published Shared release.

Do not start `ARCH-007-ADMIN-005`, `ARCH-007-SHOPIFY-004`, or `ARCH-007-BACKGROUND-009` yet; they remain gated on SHARED-006 and their other dependencies.
