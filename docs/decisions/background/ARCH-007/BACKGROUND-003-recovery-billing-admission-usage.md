---
id: ARCH-007-BACKGROUND-003
architecture_id: ARCH-007
title: Integrate Free/paid recovery admission, usage commitment and merchant billing notifications
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 80
executor: null
claimed_at: null
attempt: 2
depends_on: 
  - ARCH-007-BACKGROUND-002
  - ARCH-007-SHOPIFY-001
enables: 
  - ARCH-007-BACKGROUND-004
  - ARCH-007-BACKGROUND-007
  - ARCH-007-SYSTEM-TEST-001
created: 2026-09-07
updated: 2026-09-08
---

# ARCH-007-BACKGROUND-003: Integrate Free/paid recovery admission, usage commitment and merchant billing notifications

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Apply ARCH-007 billing admission to the actual recovery initiation path so Free exhaustion blocks only a new conversation, paid conversations create reportable +1 usage, and merchant billing SYSTEM messages are idempotent.

## Context

Current recovery flow creates/sends recovery messages without the new reservation/paid ledger lifecycle. This task wires the accepted policy/reservation services into the exact point where a recovery becomes a WhatsApp conversation.

## Scope

Recovery candidate/materialization/initial-send path, billing usage service integration, MerchantSupportMessage SYSTEM creation through existing service semantics, and focused tests. Do not yet refactor all follow-up WhatsApp sends (BACKGROUND-004).

## Out of Scope

- Shopify App Events network publication.
- Meta status webhook consumer.
- Admin UI.
- Changing recovery eligibility unrelated to billing.

## Requirements

- Before initiating a new recovery conversation, resolve effective billing policy and global/shop new-recovery pause.
- Free: obtain deterministic reservation before provider send. If exhausted, do not create/send a new recovery; create exactly one `BILLING_FREE_ALLOWANCE_EXHAUSTED` SYSTEM message for the relevant exhaustion lifecycle using deterministic sourceKey. Optionally create the one-remaining warning when transition reaches architecture-approved warning threshold; it must also be idempotent.
- The fifth successful Free conversation remains active; billing exhaustion must not terminate its later replies.
- Paid: do not reserve included Shopify units; allow recovery subject to safety/pause. On successful initial provider initiation create exactly one RECOVERY_CONVERSATION +1 UsageEvent with report state PENDING, snapshotted plan usage event handle and permanent Shopify idempotency key.
- Free successful initiation commits reservation and creates NOT_APPLICABLE/NOT_REPORTABLE usage; definitive provider failure releases it.
- If initial provider outcome is ambiguous after crossing provider boundary, do not blindly resend or release. Persist/retain AMBIGUOUS state and let existing message/provider reconciliation or BACKGROUND-008 resolve.
- Create `BILLING_PLAN_UPGRADED`, downgrade-scheduled/subscription-ended messages only when this runtime is the architecture-owned state transition source; otherwise leave those to App/reconciler. Never create duplicate messages on repeated jobs.
- Merchant system-message insertion must use Prisma/service code, not the current raw-SQL billing notification shortcut.
- Paid usage `occurredAt` is the actual successful initiation time, not publisher retry time.

## Work Items

- [x] Locate exact recovery initiation/provider send transaction path.
- [x] Integrate policy + Free reservation before send.
- [x] Integrate Free commit/release/ambiguous handling.
- [x] Create paid +1 reportable UsageEvent exactly once after successful initiation.
- [x] Implement idempotent exhaustion/warning SYSTEM messages through existing support thread/message service or Prisma service.
- [x] Add focused duplicate, Free 4/5->5/5->blocked-next, paid-over-included-still-allowed, provider-failure and ambiguous tests.

## Interfaces / Contracts

Commercial semantics:

```text
FREE: new start denied after effective lifetime allowance; existing conversation continues
PAID_METERED: every successful new recovery +1 PENDING App Event; no included-unit hard stop
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-BACKGROUND-004
- ARCH-007-BACKGROUND-007
- ARCH-007-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Conversation row creation alone does not consume Free/paid recovery usage.
- [x] Free final credit cannot be overspent through integrated path.
- [x] Free exhausted next start is blocked and notification deduplicated.
- [x] Paid +1 exists once even on duplicate recovery job.
- [x] Paid usage continues beyond Shopify included quantity.
- [x] No App Events HTTP call occurs in recovery transaction.
- [x] No new raw SQL billing notification path is added.
- [x] Focused tests/validation pass.

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

Ready for Review

### Files Changed

- `moda-interact-background/src/services/recovery-billing.service.ts`
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/tests/unit/services/recovery-billing.service.test.ts`
- `moda-interact-background/tests/unit/services/matured-candidate.materialization.test.ts`
- `moda-interact-background/tests/unit/services/checkout-refresh.test.ts`

### Work Completed

- Added policy-gated Free/paid recovery admission before conversation/message creation.
- Added deterministic Free reservation commit/release/ambiguous handling around the initial provider boundary.
- Added paid `RECOVERY_CONVERSATION` usage upsert with `PENDING` Shopify reporting, mapped meter handle, billing-period snapshot and permanent idempotency keys.
- Added Prisma-only, source-key-idempotent Free allowance exhaustion SYSTEM messages.
- Prevented duplicate Free reservation replays from sending another provider message and released pre-provider setup failures.
- Classified provider failures at the billing boundary: definitive configuration/provider rejection fails the pending message, while invalid or unknown provider outcomes remain pending and preserve retryability.
- Fixed exhaustion notification identity to the subscription and effective allowance lifecycle, preventing duplicate SYSTEM messages across distinct recovery source keys.
- Added integrated regression coverage for definitive and ambiguous provider outcomes, the fifth Free credit and subsequent block, paid overage usage, duplicate execution, and replay idempotency.

### Validation Results

- Focused recovery billing and materialization suites: 29 tests passed.
- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- `npm run prisma:validate`: passed.
- `npm test`: 264 passed, 6 skipped; 3 unrelated pre-existing failures remain in recovery-routing and pending-recovery-candidate tests.
- `git diff --check`: passed.
- Editor diagnostics for touched source/tests: no errors.

### Deviations

The full repository suite retains the three unrelated baseline failures listed above; no unrelated production code was changed for this task.

### Assumptions

The existing recovery checkout lock remains the serialization boundary for duplicate materialization jobs; deterministic reservation and usage identities provide the billing idempotency boundary.

### Unresolved Issues

The three unrelated baseline test failures remain for architect review; they are outside this task's changed production path. The paid usage publication remains asynchronous by design, with the committed usage event left pending for the publisher task.

### Architectural Concerns

None within BACKGROUND-003 scope.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is architect-accepted.

The correction pass satisfies the complete Attempt 1 rework contract:

1. Provider failure disposition is now explicit and shared between billing and the recovery caller. `configuration-missing` and `provider-rejected` are definitive; `invalid-provider-response` and unclassified post-boundary errors fail safe as ambiguous. Definitive failures release Free capacity and may mark the outbound message `FAILED`; ambiguous outcomes retain Free `AMBIGUOUS` state where applicable and leave the outbound message non-terminal instead of falsely declaring failure.

2. Free allowance exhaustion notification identity is no longer recovery-attempt-specific. The SYSTEM-message event identity is `free-allowance:<subscriptionId>:<effectiveAllowance>` and is passed through the canonical Shared `createMerchantBillingSystemSourceKey(...)` helper. Focused tests model two distinct denied recoveries within one exhaustion lifecycle producing one durable SYSTEM-message identity and a changed lifecycle producing a distinct key.

3. The focused regression matrix now covers the fifth Free recovery being admitted/committed, the following distinct recovery being blocked before provider send, preservation of the successful fifth recovery, duplicate materialization suppression, paid replay/idempotency identity, paid operation without Free reservation/included-unit hard stop, definitive provider rejection, and ambiguous Free/paid provider outcomes.

The implementation continues to reuse the architect-accepted `FreeRecoveryReservationService`; no raw SQL or synchronous Shopify App Events publication was introduced.

### Reviewed Files

- `moda-interact-background/src/services/recovery-billing.service.ts`
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/tests/unit/services/recovery-billing.service.test.ts`
- `moda-interact-background/tests/unit/services/matured-candidate.materialization.test.ts`
- `moda-interact-background/tests/unit/services/checkout-refresh.test.ts`
- `docs/decisions/background/ARCH-007/BACKGROUND-003-recovery-billing-admission-usage.md`

### Validation Reviewed

Completion Report records:

- focused tests: 29 passed;
- build: passed;
- Prisma validation: passed;
- `git diff --check`: passed;
- full suite: 264 passed, 6 skipped, with 3 documented unrelated baseline failures.

No task-scope regression was identified during architect inspection.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-BACKGROUND-004` is now Ready because its sole dependency, `ARCH-007-BACKGROUND-003`, is Complete.

`ARCH-007-BACKGROUND-007` remains Pending because `ARCH-007-BACKGROUND-006` is not yet Complete.

System-test work remains terminal/manual-gated and is not made Ready merely by this acceptance.
