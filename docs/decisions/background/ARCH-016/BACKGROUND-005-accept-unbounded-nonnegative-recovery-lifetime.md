---
id: ARCH-016-BACKGROUND-005
architecture_id: ARCH-016
title: Accept all non-negative integer recovery lifetimes in Background and expire safely
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-10-31T12:14:32Z
attempt: 1
depends_on:
  - ARCH-016-DATABASE-002
  - ARCH-016-BACKGROUND-002
enables:
  - ARCH-016-ADMIN-003
  - ARCH-016-SYSTEM-TEST-001
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-016-BACKGROUND-005 — Non-negative unbounded recovery lifetime runtime

## Architecture

- Architecture: `ARCH-016` — `docs/architecture/ARCH-016-merchant-recovery-policy-shopify-discounts-followups-expiry.md`.
- Coordinator: `moda_architect`; implementation owner: `moda_background`.

## Objective

Make the Background runtime accept every **non-negative whole-day** value supported by the persisted `Int` field, without enforcing the previous 90-day maximum, while maintaining safe and deterministic expiration at zero and at extremely large integer values.

## Context

`src/runtime/background-runtime-config.ts` currently declares `checkoutRecoveryLifetimeDays: [1, 90]` in `NUMERIC_BOUNDS`. `src/services/checkout-recovery-expiry.service.ts` subtracts `days * 24 * 60 * 60 * 1000` and constructs a JavaScript `Date`. This arithmetic can produce an invalid `Date` for a large but valid PostgreSQL `INTEGER` (e.g. `2147483647` days), so merely deleting the upper bound would introduce a runtime failure. The existing expiry worker owns this calculation.

## Scope

Authorized changes inside `moda-interact-background`:

```text
src/runtime/background-runtime-config.ts
tests/unit/runtime/background-runtime-config.test.ts
src/services/checkout-recovery-expiry.service.ts
tests/unit/services/checkout-recovery-expiry.service.test.ts
```

A small internal helper placed alongside expiry logic and its focused tests is permitted if needed; do not create a new cross-repository package or configuration field.

## Out of Scope

- No Database, Admin, WooCommerce, API, Shopify, Shared, Gateway, consumer template or outbound-send implementation in this task.
- No changes to other `NUMERIC_BOUNDS`, retry limits, outreach credit rules, recovery generation status rules or customer consent/STOP handling.
- Do not introduce a new hardcoded maximum (90, 365 or otherwise), clamp the **stored configuration value**, or silently replace invalid settings with 21.
- Checkout URL eligibility unification across API and template bindings remains in the separate ARCH-053 work; this task only changes lifetime acceptance and the existing expiry scan.

## Requirements

1. Remove `checkoutRecoveryLifetimeDays` from the bounded `NUMERIC_BOUNDS` map.
2. Add a dedicated validation in `validateConfig(row)`:

   ```typescript
   const days = value.checkoutRecoveryLifetimeDays;
   if (!Number.isSafeInteger(days) || (days as number) < 0) {
     throw new Error("Invalid background runtime configuration: invalid checkoutRecoveryLifetimeDays.");
   }
   ```

   It must be reached for both `start()` and configuration refresh (`getFresh()`); keep every other field's existing bounded validation intact.
3. Treat `0` as a valid administrator-controlled value: the expiry cutoff is **now**; an active recovery with `lastExternalActivityAt <= now` expires in the next sweep, subject to the existing transaction/recheck safeguards. Never shift the cutoff to yesterday or substitute 1 day.
4. Preserve the exact `<` / `<=` eligibility equivalence used by existing recovery-expiry semantics at the cutoff.
5. Calculate the expiry cutoff safely for all non-negative persisted `Int` values. When subtracting the chosen lifetime would yield an unrepresentable timestamp for Prisma/PostgreSQL, treat the inactivity-expiry scan as finding **no age-expired recoveries**, return `0` and avoid passing an invalid/out-of-range `Date` to Prisma. Do not cap the config or reinterpret it as 90 days. Use a focused, tested representability check rather than catching and hiding a Prisma error.
6. For representable cutoffs, preserve the existing bounded pagination, active statuses, conditional `updateMany`, status history and unsent-attempt cancellation. A newer checkout activity racing the expiry transaction still wins safely.
7. Continue using `@modainteract/moda-interact-shared/logging` for any newly required runtime diagnostics; preserve original error details when logging unexpected failures, redact sensitive information, and propagate failures to the owning boundary. Do not introduce a competing logger or silently swallow errors.

## Work Items

- [ ] Replace the one lifetime `[1, 90]` bounded-map entry with a dedicated non-negative integer check, leaving unrelated runtime bounds unchanged.
- [ ] Add refresh and startup tests for 0, 1, 21, 90, 91, 180, 365 and `2147483647`.
- [ ] Add negative, fractional, non-finite and malformed-value tests that fail closed; retain all existing tests of runtime immutability and versioning.
- [ ] Safely calculate the expiry cutoff (including large-value no-age-expiry handling) without invalid Prisma `Date` arguments.
- [ ] Add expiry tests at 0, 21, 180, 365 and `2147483647` and at the exact cutoff; verify other lifecycle and race protections remain unchanged.
- [ ] Record validation, changed paths and test results in the Completion Report.

## Interfaces / Contracts

Existing unchanged persistence field:

```typescript
// Prisma-backed, still stored as PostgreSQL INTEGER, default = 21
checkoutRecoveryLifetimeDays: number; // integer >= 0; no business maximum
```

No new queue event, Published Shared schema, `expiresAt` column or derived durable field. The expiry worker reads the current `BackgroundRuntimeConfigSnapshot` and applies the selected lifetime on each scan.

## Dependencies

- `ARCH-016-DATABASE-002` — the persisted range constraint must be removed first.
- `ARCH-016-BACKGROUND-002` — existing expiry implementation (Complete).

## Enables

- `ARCH-016-ADMIN-003` — Admin must not allow large values before Background can read them.
- Existing terminal `ARCH-016-SYSTEM-TEST-001`, once other required dependencies are accepted.

## Acceptance Criteria

- [ ] Runtime accepts 0 and values above 90 (including the PostgreSQL INTEGER maximum) without substituting defaults.
- [ ] Runtime rejects negatives, decimals, `NaN`, infinity and non-integer types; existing unrelated bounds still work.
- [ ] At 0, expiry uses `cutoff=now`; active recoveries at/before that point expire. This may suppress all recovery outreach when 0 is configured and must be treated as deliberate admin policy.
- [ ] No invalid `Date`, overflowing date serialization or unexpected database query occurs for very large allowed values; no recovery ages out when its threshold is beyond the representable timestamp range.
- [ ] Expiry still records status history, cancels unsent attempts and handles concurrent activity correctly.
- [ ] No new business maximum, new setting or unrelated service refactor.

## Validation

Inspect actual repository scripts first; required commands from the current snapshot:

```bash
npm run test:unit -- tests/unit/runtime/background-runtime-config.test.ts tests/unit/services/checkout-recovery-expiry.service.test.ts
npm run lint
npm run build
git diff --check
```

Record the real commands and results; use the existing test runner rather than inventing an alternative. If the repository runner requires a different positional filter, record its supported syntax.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are satisfied, finish the Completion Report, move to `review`, return to `moda_architect` and **STOP**. Do not begin ADMIN-003.

## Implementation Notes

There is no newly imposed maximum. The native SQL `INTEGER` storage limit is not a business rule. When the config is zero, the existing strict expiry condition intentionally expires every active recovery whose activity is not in the future. Extremely large values must not overflow `Date` construction; implement safe arithmetic with explicit checks. Do not use a generic catch-and-continue fallback on database failures.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

Not Started

### Validation Results

Not Run

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

Pending implementation evidence.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not assessed.

### Follow-up

None
