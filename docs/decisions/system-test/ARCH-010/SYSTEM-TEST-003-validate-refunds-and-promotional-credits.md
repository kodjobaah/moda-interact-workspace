---
id: ARCH-010-SYSTEM-TEST-003
architecture_id: ARCH-010
title: Validate purchased-credit partial refunds and promotional-credit operations
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: manual
status: pending
priority: 102
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-BACKGROUND-014
  - ARCH-010-ADMIN-003
  - ARCH-010-ADMIN-005
  - ARCH-010-SHOPIFY-017
  - ARCH-010-SHOPIFY-020
enables:
  - ARCH-010-SYSTEM-TEST-004
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-SYSTEM-TEST-003: Validate purchased-credit partial refunds and promotional-credit operations

## Terminal/manual gate

Do **not** auto-start. The developer explicitly invokes this terminal/manual validation after the relevant implementation is integrated and manually smoke-checked.

No implementation task depends on this task.

## Objective

Validate the two shop-lifetime non-plan capacity workflows that require strong accounting provenance:

1. purchased top-up credit lots with partial human-settled refunds;
2. Moda-funded promotional credit grants/campaigns.

## Required scenarios

### A. Purchased-credit FIFO lot consumption

Create at least three provider-confirmed top-up lots with distinguishable activation times and quantities.

Prove:

- purchased recovery reserves the oldest refundable/spendable lot first;
- exhausted/refunding/refunded lot capacity is skipped;
- reservation/commit/release updates lot and aggregate accounting exactly once;
- concurrent recovery cannot overspend the final available purchased credit;
- provider reconciliation does not re-activate or re-grant manually refunded quantities.

### B. Partial refund triage

From an explicit merchant support message:

- Admin sees only same-shop provider-confirmed purchase lots;
- lifetime Free and promotional balances are never refund candidates;
- refundable quantity is derived exactly from grant/committed/reserved/refunding/refunded state;
- positive whole-credit quantity within the current refundable amount creates one idempotent request;
- request creation does not hold capacity;
- canonical merchant acknowledgement is emitted once.

### C. SUPER_ADMIN hold and settlement

Prove approval revalidates the exact requested quantity against current refundable state.

If the merchant spent some credits after request creation and the full requested quantity is no longer refundable, approval must fail rather than silently reduce the quantity.

On valid approval:

- exact quantity moves into refund hold atomically;
- new recovery cannot spend the held quantity;
- provider settlement mode is explicitly recorded as `REFUND` or `CREDIT` from human Shopify Partner Dashboard evidence;
- local finalization occurs only after provider evidence is recorded;
- replay does not decrement local granted capacity twice;
- multiple later partial refunds against the same purchase are possible while refundable balance remains;
- new ARCH-010 refunds do not convert the purchase provider-confirmation state to `REFUNDED`.

Where live Shopify money movement would be inappropriate for the test environment, use a developer-approved non-production charge/invoice or stop at the manual provider-evidence gate; never fabricate a successful provider refund.

### D. Single-shop promotional grant

Validate SUPER_ADMIN grant with:

```text
quantity > 0
grantType
reason
optional campaignReference
unique requestKey
```

Prove:

- exact shop aggregate promotional counter increases;
- provenance and billing audit records are written;
- duplicate requestKey with same payload is idempotent;
- duplicate requestKey with changed payload fails closed;
- no Shopify/App Event is emitted;
- grant does not alter lifetime Free or purchased counters;
- grant may exist for a currently non-executable shop but cannot bypass `NO_CONTRACT`, `FROZEN` or inactive-shop execution gates.

### E. Bounded targeted campaign

Run a multi-shop campaign that includes successful and intentionally invalid/failing targets.

Prove:

- per-shop idempotency keys are deterministic;
- successful shops retain their grant when another target fails;
- retry does not double-grant successful shops and can retry failed shops;
- campaign attribution is visible to internal Admin/audit only;
- merchant surfaces show aggregate promotional balance but not internal campaign provenance.

### F. Final priority/refund interaction

Create a merchant with all capacity sources and verify:

```text
Paid included -> promotional -> purchased -> lifetime Free
```

Then prove promotional consumption preserves purchased refundable balance until promotional capacity is exhausted.

Promotional credits are never included in purchased refund quantity or provider refund instructions.

## Required evidence

Return separate accounting tables for each purchased lot and promotional grant, plus the final aggregate counters and audit entries.

For any provider refund/credit action record only safe provider evidence; never include credentials.

## Validation

Any harness changes must pass repository-declared tests/type/lint and `git diff --check`.

## Non-goals

Do not test subscription-fee refunds; Shopify owns those. Do not implement automatic negative App Event refund settlement. Do not add promotional expiry/revocation.

## Stop conditions

STOP if historical purchased balances cannot be mapped to deterministic lots, Shopify provider settlement cannot be performed safely in the chosen non-production environment, or Admin authorization cannot be exercised without production credentials/data.

Implementation defects return to the owning task rather than being patched from system-test.

## Completion Report

### Status
Not started.

### Scenarios Executed
Populate during execution.

### Evidence
Populate during execution.

### Validation Results
Populate during execution.

### Git / VCS
Populate if harness code changes.

### Architect Review
Manual terminal gate; pending developer/architect acceptance.
