---
id: ARCH-016-BACKGROUND-004
architecture_id: ARCH-016
title: Apply effective recovery policy to pending-candidate inactivity scheduling
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 45
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-004-BACKGROUND-002
- ARCH-016-BACKGROUND-003
enables:
- ARCH-016-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# ARCH-016-BACKGROUND-004

## Objective

Make the pending-recovery inactivity clock consume the canonical **effective recovery policy** instead of reading `ShopSettings.recoveryDelayMinutes` directly.

This task closes one integration discrepancy in the accepted ARCH-016 policy architecture:

```text
active unexpired ShopRecoveryPolicyOverride exists
    -> effective recoveryDelayMinutes = override.recoveryDelayMinutes
otherwise
    -> effective recoveryDelayMinutes = ShopSettings.recoveryDelayMinutes
```

The existing `RecoveryPolicyService` is already the canonical resolver for that precedence. Reuse it. Do not implement a second override resolver.

## Confirmed current defect

In the 2026-09-20 current workspace snapshot, initial candidate scheduling in:

```text
src/services/pending-recovery-candidate.service.ts
```

still contains:

```ts
const delayMinutes =
  shop.settings?.recoveryDelayMinutes ?? DEFAULT_RECOVERY_DELAY_MINUTES;
```

and activity rescheduling still calls this helper:

```ts
private async getRecoveryDelayMinutes(shopId: string) {
  const shop = await prisma.shop.findUnique({
    where: { id: shopId },
    select: { settings: { select: { recoveryDelayMinutes: true } } },
  });
  return shop?.settings?.recoveryDelayMinutes ?? DEFAULT_RECOVERY_DELAY_MINUTES;
}
```

Those reads bypass:

```text
src/services/recovery-policy.service.ts
RecoveryPolicyService.resolve(shopId, now?)
```

which already applies the complete Admin-override-vs-merchant precedence contract.

Concrete incorrect state today:

```text
ShopSettings.recoveryDelayMinutes = 30
active ShopRecoveryPolicyOverride.recoveryDelayMinutes = 120

merchant/admin UI effective value = 120
initial PendingRecoveryCandidate delay = 30       <- wrong
later activity reschedule delay = 30              <- wrong
```

After this task both scheduling decisions MUST use `120` while that override is active.

## Scope and ownership

### Authorized production file

Modify only:

```text
src/services/pending-recovery-candidate.service.ts
```

### Authorized focused test file

Modify only:

```text
tests/unit/services/pending-recovery-candidate.service.test.ts
```

The normal parent Completion Report may be updated by the task workflow.

Do NOT modify:

```text
src/services/recovery-policy.service.ts
src/services/shop-execution-eligibility.service.ts
Prisma schema or migrations
Shared contracts
Shopify merchant application
Admin application
Gateway/Render configuration
BullMQ queue names or worker topology
```

If the correction cannot be completed within the two implementation/test files above, STOP and return the concrete dependency to `moda_architect` rather than expanding scope.

## Canonical effective-policy dependency

Use the existing singleton exactly from:

```ts
import { recoveryPolicyService } from "./recovery-policy.service.js";
```

Do not duplicate the override query.

Do not query `shopRecoveryPolicyOverride` directly from `PendingRecoveryCandidateService`.

Do not add another helper that independently decides whether an override is expired.

Do not cache the recovery delay across separate scheduling decisions.

`RecoveryPolicyService.resolve(shopId)` remains authoritative for:

```text
active/unexpired override precedence
merchant fallback
platform default fallback when no merchant row exists
```

## Required production change 1 — initial candidate scheduling

In:

```text
PendingRecoveryCandidateService.scheduleFromCheckoutCreated(...)
```

preserve all existing shop-status, subscription and execution-eligibility gates exactly as they are.

After:

```ts
if (!execution.allowed) {
  ...
}
```

replace the direct `ShopSettings` delay read:

```ts
const delayMinutes =
  shop.settings?.recoveryDelayMinutes ?? DEFAULT_RECOVERY_DELAY_MINUTES;
```

with exactly this effective-policy resolution:

```ts
const policy = await recoveryPolicyService.resolve(shop.id);
const delayMinutes = policy.recoveryDelayMinutes;
```

Do not move policy resolution before the existing execution-eligibility gates. An unavailable/frozen/ineligible shop must continue to return before queue/index work and before a recovery-policy lookup is needed.

Keep all existing scheduling math unchanged:

```text
lastActivityAt
activityDueAtMs(...)
BullMQ delay
pendingCandidateIndexTtlMs(...)
checkout/cart/shop indexes
legacy/new deterministic job identity
existing-candidate monotonic refresh behavior
```

The only semantic change is the source of `delayMinutes`.

## Required production change 2 — checkout/cart activity rescheduling

Keep the existing `refreshResolvedCandidateActivity(...)` ordering exactly:

```text
reject mismatched cart token
reject stale activity
resolve BullMQ job
handle empty-cart cancellation
require delayed state
resolve recovery delay
update candidate activity
change BullMQ delay
update indexes
```

Do not resolve policy for stale, cancelled or non-reschedulable candidates.

Replace the current direct-database implementation of:

```ts
private async getRecoveryDelayMinutes(shopId: string)
```

with exactly:

```ts
private async getRecoveryDelayMinutes(shopId: string) {
  const policy = await recoveryPolicyService.resolve(shopId);
  return policy.recoveryDelayMinutes;
}
```

No direct Prisma lookup is allowed in this helper.

## Required import cleanup

After the two changes above, `PendingRecoveryCandidateService` must not require `DEFAULT_RECOVERY_DELAY_MINUTES` for runtime scheduling.

If it becomes unused, remove:

```ts
DEFAULT_RECOVERY_DELAY_MINUTES,
```

from the import list in `pending-recovery-candidate.service.ts`.

Do not remove the default constant from the domain module itself. Other code/tests may legitimately use it.

The existing `prisma` import must remain if the service still uses Prisma elsewhere in the file. Do not remove it merely because `getRecoveryDelayMinutes()` no longer uses Prisma.

## Policy timing semantics — explicit

This task does **not** introduce live bulk rescheduling when a merchant or Admin changes policy.

Required semantics are:

```text
new pending candidate
  -> resolve effective policy at scheduling time
  -> schedule from lastActivityAt + effective recoveryDelayMinutes

later qualifying checkout/cart activity on an existing delayed candidate
  -> resolve effective policy again at rescheduling time
  -> reschedule from new lastActivityAt + then-current effective recoveryDelayMinutes

Admin override is created/changed/cleared/expires with no new checkout/cart activity
  -> do NOT scan/rewrite all existing BullMQ delayed jobs
  -> existing delayed candidate keeps its current due time
  -> next qualifying activity refresh uses the then-current effective policy
```

This matches the existing merchant-setting behaviour and avoids inventing a new policy-change reconciliation mechanism.

If implementation appears to require immediate bulk rescheduling of existing pending candidates when policy changes, STOP and return to `moda_architect`. That is outside this task.

## Failure semantics

Do not catch a `RecoveryPolicyService.resolve()` database/runtime failure and silently fall back to `ShopSettings` or the default constant.

The canonical resolver is the policy authority. A resolver failure must propagate through the existing scheduling failure path rather than silently applying a different policy.

Do not add retry loops, new BullMQ jobs or another queue for policy resolution.

## Focused test setup — exact mocking contract

In:

```text
tests/unit/services/pending-recovery-candidate.service.test.ts
```

add a hoisted mock for the canonical policy service before importing the service under test:

```ts
const recoveryPolicyMocks = vi.hoisted(() => ({
  resolve: vi.fn(),
}));

vi.mock("../../../src/services/recovery-policy.service.js", () => ({
  recoveryPolicyService: {
    resolve: recoveryPolicyMocks.resolve,
  },
}));
```

In `beforeEach`, reset it and establish this default merchant policy:

```ts
recoveryPolicyMocks.resolve.mockReset();
recoveryPolicyMocks.resolve.mockResolvedValue({
  recoveryDelayMinutes: 45,
  recoveryOfferMode: "NONE",
  fixedShopifyDiscountId: null,
  followUpEnabled: false,
  followUpDelayMinutes: null,
  source: "MERCHANT",
  offerSnapshot: null,
});
```

Keep the existing Prisma shop mock for shop/execution eligibility. The test must deliberately be able to prove that the policy delay can differ from `shop.settings.recoveryDelayMinutes`.

Do not replace `RecoveryPolicyService` with hand-written override-selection logic inside the test.

## Required focused tests

### Case 1 — merchant effective policy remains the normal scheduling source

Update/rename the existing test currently named approximately:

```text
schedules a delayed candidate using recovery delay from shop settings
```

to express effective policy, for example:

```text
schedules a delayed candidate using the effective recovery-policy delay
```

With the default mock returning `45`, retain the existing assertions that:

```text
result.delayMinutes = 45
BullMQ delay = 45 * 60 * 1000
shop-index due score uses 45 minutes
```

and additionally assert:

```ts
expect(recoveryPolicyMocks.resolve).toHaveBeenCalledWith("shop_1");
```

### Case 2 — active Admin override wins over merchant setting for initial scheduling

Add a focused test with:

```text
ShopExecution shop.settings.recoveryDelayMinutes = 45
RecoveryPolicyService.resolve("shop_1").recoveryDelayMinutes = 120
RecoveryPolicyService source = ADMIN_OVERRIDE
```

Call `scheduleFromCheckoutCreated(...)`.

Required assertions:

```text
outcome = enqueued
result.delayMinutes = 120
BullMQ add delay = 120 * 60 * 1000
shop-index due score = lastActivityAt + 120 minutes
```

The test MUST keep the mocked merchant `ShopSettings` delay at `45` so it proves the pending-candidate service is no longer sourcing the delay from that row.

### Case 3 — activity rescheduling re-resolves the current effective policy

Create a candidate using the default 45-minute policy.

Then change only the policy mock before the activity refresh:

```ts
recoveryPolicyMocks.resolve.mockResolvedValue({
  recoveryDelayMinutes: 120,
  recoveryOfferMode: "NONE",
  fixedShopifyDiscountId: null,
  followUpEnabled: false,
  followUpDelayMinutes: null,
  source: "ADMIN_OVERRIDE",
  offerSnapshot: null,
});
```

Call `refreshCandidateActivity(...)` with a newer activity timestamp.

Assert the refreshed shop-index score is:

```text
new activityAt + 120 minutes
```

not `+45 minutes`.

Also assert the policy resolver was called for the refresh.

Do not require an exhaustive matrix of every policy field. This task concerns the recovery delay only.

### Existing tests

Preserve all existing tests for:

```text
shop execution eligibility
FROZEN suppression
candidate identity
legacy job compatibility
monotonic activity
cart-token changes
stale activity
empty-cart cancellation
BullMQ state boundaries
Redis indexes and TTLs
order-completed tombstone
international context
```

If any existing mock sequencing assumed the removed direct Prisma delay lookup, update only that obsolete expectation. Do not weaken unrelated assertions.

## Source invariants

After implementation, this command must return **no matches**:

```bash
rg -n \
  'shop\.settings\?\.recoveryDelayMinutes|settings:\s*\{\s*select:\s*\{\s*recoveryDelayMinutes' \
  src/services/pending-recovery-candidate.service.ts
```

This command must show the canonical resolver being used for both initial scheduling and refresh resolution:

```bash
rg -n 'recoveryPolicyService\.resolve' \
  src/services/pending-recovery-candidate.service.ts
```

Expected implementation shape: one call in `scheduleFromCheckoutCreated(...)` and one call in `getRecoveryDelayMinutes(...)`.

Do not satisfy the invariant by renaming a direct ShopSettings query. The runtime delay must actually come from `RecoveryPolicyService.resolve()`.

## Non-goals / forbidden changes

Do NOT:

```text
change RecoveryPolicyService precedence
change Admin override persistence
change merchant Recovery Settings UI
change recovery-offer selection
change follow-up scheduling
change recovery-credit admission
change recovery generation/expiry
change checkout/cart correlation rules
change candidate queue/job names
change Redis index formats
change candidate idempotency keys
add a policy-change scheduler
bulk reschedule existing candidates
add a new worker or Render service
change database schema/migrations
change Shared contracts
```

## Validation — exact commands

From `moda-interact-background`, inspect `package.json` first and then run these declared commands exactly:

```bash
npm run prisma:generate
npm run prisma:validate

npx vitest run \
  tests/unit/services/pending-recovery-candidate.service.test.ts

npm run build
npm test

git diff --check
```

Then run the source invariants:

```bash
if rg -n \
  'shop\.settings\?\.recoveryDelayMinutes|settings:\s*\{\s*select:\s*\{\s*recoveryDelayMinutes' \
  src/services/pending-recovery-candidate.service.ts; then
  echo "FAIL: pending-recovery scheduling still reads recoveryDelayMinutes directly from ShopSettings" >&2
  exit 1
else
  echo "PASS: no direct ShopSettings recovery-delay scheduling read remains"
fi

rg -n 'recoveryPolicyService\.resolve' \
  src/services/pending-recovery-candidate.service.ts
```

Do not invent a lint command; this repository currently declares no lint script.

Known unrelated baseline failures may be recorded using the durable development-baseline mechanism, but any failure in either authorized changed file is blocking.

## Acceptance criteria

All must be true:

- [ ] Initial pending-recovery scheduling obtains `recoveryDelayMinutes` from `RecoveryPolicyService.resolve(shopId)`.
- [ ] Checkout/cart activity rescheduling obtains `recoveryDelayMinutes` from the same canonical resolver.
- [ ] An active Admin override delay wins over a different merchant `ShopSettings` delay.
- [ ] After override removal/expiry, the canonical resolver's merchant value is used on the next schedule/reschedule decision.
- [ ] No direct `ShopSettings.recoveryDelayMinutes` scheduling read remains in `PendingRecoveryCandidateService`.
- [ ] Shop/subscription eligibility gates remain before initial policy resolution.
- [ ] Stale/cancelled/non-reschedulable activity paths do not perform unnecessary policy resolution.
- [ ] Existing delayed candidates are not bulk rewritten merely because policy changes.
- [ ] Existing queue identity, Redis indexes, monotonic activity and BullMQ state semantics are unchanged.
- [ ] Focused tests prove both initial scheduling and later activity rescheduling use effective policy.
- [ ] Prisma generation/validation, focused tests, build and `git diff --check` pass except documented unrelated baseline conditions.

## Completion Report requirements

Return the task to `review` with:

```text
status: review
executor: null
claimed_at: null
```

Record:

```text
Attempt number
implementation commit
parent Completion Report commit
launcher-prepared parent/implementation worktree evidence
start-of-attempt synchronization evidence
recursive submodule/database revision evidence
focused test result
Prisma generate result
Prisma validate result
build result
full test result
git diff --check result
source-invariant results
```

The report must explicitly state:

```text
1. Initial pending-candidate scheduling now resolves the effective recovery policy.
2. Activity rescheduling re-resolves the effective recovery policy.
3. Active Admin override recoveryDelayMinutes therefore governs both paths.
4. No bulk policy-change rescheduling mechanism was introduced.
5. No direct ShopSettings recovery-delay scheduling read remains in PendingRecoveryCandidateService.
```

## Stop conditions

STOP and return to `moda_architect` without speculative changes if:

```text
RecoveryPolicyService cannot be reused without changing its public contract;
fix requires database/schema/shared changes;
fix requires modifying Shopify/Admin applications;
fix requires a new queue/worker/scheduler;
correctness appears to require immediate bulk rescheduling when an override changes;
existing candidate identity/index semantics would need redesign.
```

Do not solve any stop condition by expanding task scope.

## Completion Report

Status: Ready for Review

- Attempt: 1
- Implementation commit: `2c6fbab` (`fix: use effective recovery delay for pending candidates`)
- Parent Completion Report commit: `4a3edd63` (`docs: return background recovery delay task for review`)
- Launcher preparation: authoritative prepared execution completed with `prepared_execution=true`, `status=in_progress`, `dependency_gate=passed`, `attempt=1`, `executor=copilot`; dedicated implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-016-BACKGROUND-004` and parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-016-BACKGROUND-004` were used.
- Start-of-attempt synchronization: supplied by the prepared launcher packet; not repeated.
- Recursive submodule/database revision evidence: supplied by the prepared launcher packet; no database schema or migration changes were made.
- Focused test: `npx vitest run tests/unit/services/pending-recovery-candidate.service.test.ts` passed, 39/39 tests.
- Prisma generate: `npm run prisma:generate` passed.
- Prisma validate: `npm run prisma:validate` passed.
- Build: `npm run build` passed.
- Full test: `npm test` ran 83 files; 70 passed, 12 skipped, and 3 unrelated billing-reconciliation tests failed in `tests/unit/services/billing-reconciliation.service.test.ts`. No failure was in either authorized changed file.
- `git diff --check`: passed.
- Source invariants: no direct `ShopSettings.recoveryDelayMinutes` scheduling read remains; `recoveryPolicyService.resolve` is used at lines 121 and 619 of the implementation file.

1. Initial pending-candidate scheduling now resolves the effective recovery policy.
2. Activity rescheduling re-resolves the effective recovery policy.
3. Active Admin override `recoveryDelayMinutes` therefore governs both paths.
4. No bulk policy-change rescheduling mechanism was introduced.
5. No direct ShopSettings recovery-delay scheduling read remains in `PendingRecoveryCandidateService`.

No blockers for the scoped implementation. The unrelated full-suite billing-reconciliation failures remain documented above for architect review.
