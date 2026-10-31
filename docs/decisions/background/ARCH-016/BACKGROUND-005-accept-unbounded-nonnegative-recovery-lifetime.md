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
status: ready
priority: 30
executor: null
claimed_at: null
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

- [x] Replace the one lifetime `[1, 90]` bounded-map entry with a dedicated non-negative integer check, leaving unrelated runtime bounds unchanged.
- [x] Add refresh and startup tests for 0, 1, 21, 90, 91, 180, 365 and `2147483647`.
- [x] Add negative, fractional, non-finite and malformed-value tests that fail closed; retain all existing tests of runtime immutability and versioning.
- [x] Safely calculate the expiry cutoff (including large-value no-age-expiry handling) without invalid Prisma `Date` arguments.
- [x] Add expiry tests at 0, 21, 180, 365 and `2147483647` and at the exact cutoff; verify other lifecycle and race protections remain unchanged.
- [x] Record validation, changed paths and test results in the Completion Report.

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

- [x] Runtime accepts 0 and values above 90 (including the PostgreSQL INTEGER maximum) without substituting defaults.
- [x] Runtime rejects negatives, decimals, `NaN`, infinity and non-integer types; existing unrelated bounds still work.
- [x] At 0, expiry uses `cutoff=now`; active recoveries at/before that point expire. This may suppress all recovery outreach when 0 is configured and must be treated as deliberate admin policy.
- [x] No invalid `Date`, overflowing date serialization or unexpected database query occurs for very large allowed values; no recovery ages out when its threshold is beyond the representable timestamp range.
- [x] Expiry still records status history, cancels unsent attempts and handles concurrent activity correctly.
- [x] No new business maximum, new setting or unrelated service refactor.

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

Attempt 1 was returned with Changes Requested. The task remains at attempt 1; the launcher owns the next attempt increment.

### Files Changed

- `moda-interact-background/src/runtime/background-runtime-config.ts`
- `moda-interact-background/src/services/checkout-recovery-expiry.service.ts`
- `moda-interact-background/tests/unit/runtime/background-runtime-config.test.ts`
- `moda-interact-background/tests/unit/services/checkout-recovery-expiry.service.test.ts`

### Work Completed

- Removed `checkoutRecoveryLifetimeDays` from the generic numeric bounds and added a dedicated non-negative safe-integer validator used by startup and refresh. Other numeric bounds are unchanged.
- Added startup and refresh coverage for 0, 1, 21, 90, 91, 180, 365 and 2147483647, plus startup rejection of negative, fractional, NaN, infinity, string, null and object values. Invalid refresh retains the last known-good snapshot and logs the validation failure.
- Replaced floating-point millisecond subtraction with exact BigInt cutoff arithmetic. The worker now checks PostgreSQL's minimum timestamp and JavaScript Date's maximum before constructing a Date; an unrepresentable cutoff returns 0 without querying Prisma.
- Preserved the existing `lte` cutoff filter in both candidate selection and transactional `updateMany`, bounded pagination, status history, unsent-attempt cancellation and race recheck behavior. Added boundary tests for 0, 21, 180, 365, the exact inclusive cutoff, the maximum persisted Int and a PostgreSQL-out-of-range cutoff that JavaScript Date can represent.
- Corrected short-page test fixtures so unused second-page mock results do not leak into later tests.

### Validation Results

- `npm exec -- vitest run tests/unit/runtime/background-runtime-config.test.ts tests/unit/services/checkout-recovery-expiry.service.test.ts`: 2 files passed, 32 tests passed.
- `npm run test:unit -- tests/unit/runtime/background-runtime-config.test.ts tests/unit/services/checkout-recovery-expiry.service.test.ts`: the package script expands to `vitest run tests/unit` plus the supplied paths, so the filter does not narrow the run. The full unit suite reported 315 files, 3,348 tests, 3,322 passed and 26 failed across unrelated suites; both task-owned files passed in the same run. The explicit Vitest invocation above is the supported focused validation.
- `npm run lint`: passed.
- `npm run build`: passed; Prisma Client generation and TypeScript compilation completed.
- `git diff --check`: passed.
- VS Code diagnostics: no errors in the four changed files.
- Launcher prepared Attempt 1 at `2026-10-31T12:14:32Z`; dependencies `ARCH-016-DATABASE-002` and `ARCH-016-BACKGROUND-002` passed, recursive Database submodule was ready at `af77c594ecbfc78c26d01c0021a090830884bbff`, and the parent claim was pushed as `d90a4254d3009877aceb134a9cadf0b72171a42c`.
- Implementation commit `aca1d2c` (`fix(BACKGROUND-005): accept unbounded recovery lifetimes`) was pushed to `origin/task/ARCH-016-BACKGROUND-005`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-016-BACKGROUND-005`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-016-BACKGROUND-005`.
- Both task worktrees use branch `task/ARCH-016-BACKGROUND-005`. No implementation merge or Architect acceptance was performed.

### Deviations

- The repository's `test:unit` script hardcodes the entire `tests/unit` directory and appends positional paths, preventing focused filtering via the task-prescribed npm script. Ran the same installed Vitest runner directly with explicit target paths. The broad unit run remains non-green due to 26 failures outside this task's changed files.
- The implementation branch inherited `origin/main` as its initial upstream, so the default GitKraken push correctly refused the mismatch. The commit was explicitly pushed to `origin/task/ARCH-016-BACKGROUND-005` and that task branch is now its upstream.

### Assumptions

The PostgreSQL timestamp lower bound is checked in Unix milliseconds; JavaScript Date's upper bound is stricter than PostgreSQL's upper timestamp limit and is used as the upper guard.

### Unresolved Issues

The full repository unit suite has 26 failures in unrelated test suites; the focused task suites, lint and build pass. No unrelated failures were changed.

### Architectural Concerns

None. No new business maximum or persistent/configuration field was introduced.

## Architect Review

### Review Status

Attempt 1 — Changes Requested

### Review Notes

The implementation correctly removes the 90-day runtime cap, validates
non-negative safe integers, uses BigInt cutoff arithmetic, and preserves the
existing inclusive query and transactional lifecycle safeguards. One
acceptance blocker remains in the PostgreSQL lower-timestamp guard:

1. `src/services/checkout-recovery-expiry.service.ts` sets
   `MIN_POSTGRES_TIMESTAMP_MS` to `-212_760_172_800_000`. PostgreSQL source
   defines `MIN_TIMESTAMP` as `-211813488000000000` microseconds relative to
   the 2000 epoch. Converting that to Unix milliseconds requires adding the
   2000-to-1970 epoch offset, yielding `-210_866_803_200_000`. The current
   guard is earlier than PostgreSQL's actual minimum and can therefore accept
   cutoffs that PostgreSQL cannot store. Correct the bound/conversion and add
   boundary tests proving an in-range cutoff queries normally while a cutoff
   just below the PostgreSQL minimum returns `0` without calling Prisma.

References: [PostgreSQL timestamp range](https://www.postgresql.org/docs/current/datatype-datetime.html)
and [PostgreSQL timestamp source](https://doxygen.postgresql.org/datatype_2timestamp_8h_source.html).

### Reviewed Files

- `src/runtime/background-runtime-config.ts`
- `src/services/checkout-recovery-expiry.service.ts`
- `tests/unit/runtime/background-runtime-config.test.ts`
- `tests/unit/services/checkout-recovery-expiry.service.test.ts`
- This task definition and Completion Report

### Validation Reviewed

The Completion Report records the two task-owned unit files passing (32 tests),
lint, build and `git diff --check`. The broader unit suite reported 26 failures
outside the changed files. No tests were rerun for this review; the focused
test evidence does not cover the PostgreSQL lower-bound edge that remains an
acceptance blocker.

### Architecture Conformance

The runtime validation and BigInt calculation follow the architecture, but the
incorrect PostgreSQL lower bound means the promised no-invalid-timestamp
behavior is not yet met for every representable configuration value.

### Follow-up

Correct the lower timestamp bound and add tests immediately on both sides of
the PostgreSQL minimum. Resubmit the same task after the focused tests, lint,
build and diff check pass. Attempt remains 1; do not increment it in this
review. `ARCH-016-ADMIN-003` and `ARCH-016-SYSTEM-TEST-001` remain Pending.
