---
id: ARCH-010-BACKGROUND-008
architecture_id: ARCH-010
title: Make paid recovery initiation safe across the billing-cycle boundary
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 46
executor: copilot
claimed_at: '2026-09-13T12:47:07Z'
attempt: 2
depends_on:
- ARCH-010-BACKGROUND-002
- ARCH-010-SHARED-008
- ARCH-010-BACKGROUND-019
enables:
- ARCH-010-BACKGROUND-007
created: 2026-09-11
updated: '2026-09-13'
---

# ARCH-010-BACKGROUND-008: Make paid recovery initiation safe across the billing-cycle boundary

## Objective

Prevent a normal paid Shopify-metered recovery from being admitted in one BillingPeriod and actually initiated after that period is closing/expired. Add a five-minute paid-period drain guard, pre-provider revalidation, period-specific included-reservation identity, and a bounded WhatsApp send timeout shorter than the drain window.

This task does not close/open BillingPeriods; BACKGROUND-007 owns rollover.

## Inspect before editing

```text
src/services/effective-billing-policy.service.ts
src/services/recovery-billing.service.ts
src/services/checkout-recovery.service.ts
src/services/paid-included-recovery-reservation.service.ts   # name may differ after BACKGROUND-002
src/services/purchased-recovery-reservation.service.ts
src/services/outbound-whatsapp-admission.service.ts
src/services/whatsapp.service.ts
src/providers/shopify-app-events.provider.ts
src/services/shopify-usage-event-publisher.service.ts
tests/unit/services/effective-billing-policy.service.test.ts
tests/unit/services/recovery-billing.service.test.ts
tests/unit/services/outbound-whatsapp-admission.service.test.ts
tests/unit/services/whatsapp.service.test.ts
package.json
```

Read the implemented BACKGROUND-002 result first. Do not create a second paid included reservation implementation.

## Required Shared constant

Import from the accepted published Shared billing package:

```text
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
```

The canonical value is 300000 ms (5 minutes). Do not redeclare a different app-local constant.

## Derived paid period phases

For a mapped ACTIVE paid subscription with exact current BillingPeriod:

```text
ACTIVE:
  now < periodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS

DRAINING:
  periodEnd - window <= now < periodEnd

EXPIRED_RECONCILING:
  now >= periodEnd while Subscription still points at that period
```

Do not persist a new SubscriptionProjectionStatus for these phases.

Expose enough typed policy information for RecoveryBillingService to distinguish ACTIVE vs DRAINING. Once the period is expired, subscription-dependent business admission must fail closed with a specific local reason equivalent to:

```text
BILLING_PERIOD_RECONCILIATION_REQUIRED
```

Do not map an expired period to NO_CONTRACT or SYNC_ERROR.

## Paid admission behaviour

### ACTIVE

Keep the final ARCH-010 ordering after BACKGROUND-019:

```text
selected promotional -> period included -> purchased lifetime -> shop-lifetime Free -> recovery blocked
```

### DRAINING

Do not start a new recovery that would create the normal paid recovery-meter App Event in the closing period.

Required routing:

```text
try selected usable promotional campaign
  -> available: allow promotional-funded recovery
  -> unavailable: try purchased lifetime credit
       -> available: allow purchased-credit recovery
       -> unavailable: try shop-lifetime Free credit
            -> available: allow lifetime-Free-funded recovery
            -> unavailable: block with billing-period-closing reason
```

Do not consume included capacity and do not create any overage path during DRAINING. A usable selected promotion is checked first; promotional-, purchased- and lifetime-Free-funded recoveries create no normal paid recovery App Event and may continue in canonical fallback order.

### EXPIRED_RECONCILING

Block all new recovery initiation until the subscription/billing-period reconciliation worker verifies the successor state. If a purchased-credit reservation was created before the expiry but no provider action has started, release it.

## Period-specific included reservation source identity

Amend the BACKGROUND-002 period-included sourceKey so it contains the BillingPeriod identity.

Conceptual form:

```text
paid-included:<billingPeriodId>:<canonical recovery identity>
```

Use the repository's existing deterministic/bounded key conventions; do not leak customer data.

This is required so a recovery whose old-period admission is safely released can later be re-admitted under a different BillingPeriod without colliding with the globally unique `UsageReservation.sourceKey`.

Purchased lifetime source identity remains period-independent.

## Revalidate immediately before provider business action

The current checkout recovery flow admits billing before conversation creation and calls Meta later. That creates a race with `periodEnd`.

Add one explicit billing revalidation hook immediately before `outboundWhatsAppAdmissionService.sendTemplate(...)` (or the exact provider-initiation boundary after integrated refactoring).

Required contract conceptually:

```ts
revalidateBeforeProvider({ admission, recoveryId })
  -> admitted with same/replacement admission
  -> BLOCK NEW RECOVERY ADMISSION
```

Here the blocked result is the capacity/billing-boundary outcome for the not-yet-started recovery; it is not a global merchant execution state.

Algorithm:

1. Free lifetime admission: preserve existing semantics, but current Shop availability still applies.
2. Purchased admission:
   - if current subscription/business execution is still valid, keep it;
   - if current paid period is expired and successor truth is not installed, release before provider and block.
3. Paid included:
   - re-resolve current billing policy;
   - if same period remains ACTIVE, continue;
   - if period changed, DRAINING or EXPIRED, release any old included reservation before provider;
   - call normal `admit()` once to reclassify against current state;
   - accept the replacement only if it is currently valid;
   - never loop repeatedly.
4. If re-admission returns blocked, do not call WhatsApp/Commerce provider work.

The revalidation must occur after any potentially slow local preparation but before the irreversible external provider action.

## WhatsApp send timeout

The current `WhatsAppService` uses bare `fetch()` with no bounded timeout. That permits a provider call started before the drain window to remain in-flight across the cycle boundary.

Add a bounded timeout to Meta message/template requests.

Canonical requirement for this task:

```text
WHATSAPP_SEND_TIMEOUT_MS = 30_000
```

The timeout is Background-local; do not add another Shared package constant.

Use the workspace-supported standard abort mechanism (for example `AbortSignal.timeout`) rather than adding an unrelated timeout package.

A timeout is an **ambiguous** provider outcome, not a definitive rejection. Preserve existing ambiguity semantics; do not release/charge as if Meta definitely rejected the request.

The 30-second timeout must remain strictly less than the five-minute drain window.

## RecoveryBillingService blocked reasons

Extend typed local blocked reasons so tests/callers can distinguish at minimum:

```text
billing-period-closing
billing-period-reconciliation
```

These are local workflow outcomes. Do not expose raw internal error strings to customers.

Checkout recovery should treat them as terminal no-send/no-new-work for that attempt, using existing recovery scheduling/retry semantics rather than throwing an unbounded worker error.

## No synchronous Shopify App Events call in the recovery hot path

Do not solve the boundary by reporting the Shopify billing App Event synchronously before WhatsApp. Preserve asynchronous usage publication.

The drain window plus pre-provider revalidation plus bounded provider call duration are the boundary-safety mechanism.

## Required tests

At minimum prove:

1. ACTIVE paid period still permits included reservation;
2. DRAINING paid period does not reserve included capacity;
3. DRAINING with purchased credit admits purchased recovery;
4. DRAINING without promotional capacity falls through to purchased credit, then lifetime Free when available, and blocks only when all fallback sources are unavailable;
5. EXPIRED period blocks normal recovery initiation;
6. included reservation source key differs across BillingPeriods for the same recovery;
7. duplicate admission inside the same BillingPeriod remains idempotent;
8. pre-provider revalidation with unchanged ACTIVE period preserves admission;
9. pre-provider revalidation after rollover releases old included reservation and may re-admit under new period;
10. pre-provider revalidation entering DRAINING releases old included reservation and falls back to promotional, then purchased FIFO, then lifetime Free; it blocks only when all fallback sources are unavailable;
11. pre-provider revalidation entering EXPIRED releases pre-provider reservation and performs no WhatsApp call;
12. purchased reservation is released if the period expires before provider action and no valid successor entitlement exists;
13. WhatsApp template send passes a 30-second abort timeout;
14. WhatsApp text send passes the same timeout;
15. timeout is treated as ambiguous, not definitive provider rejection;
16. no normal paid recovery UsageEvent is created when boundary revalidation blocks;
17. Free and purchased baseline tests remain passing;
18. no Shopify App Events network call is moved into the recovery hot path.

## Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test:unit
npm run build
git diff --check
```

Run relevant existing integration tests through `npm run test:integration` when their declared infrastructure is available.

## Non-goals

Do not implement:

- BillingPeriod close/open;
- BullMQ boundary scheduling;
- usage-event drain/flush;
- merchant UI;
- top-up purchase UI/server guard;
- upgrade/downgrade/cancellation;
- a Messaging-ingress tenant lookup redesign;
- Admin changes.

## Stop conditions

STOP and return to `moda_architect` if:

- BACKGROUND-002 did not create an explicit period-included reservation that can be released before provider work;
- the recovery flow has no safe pre-provider hook after integrated changes;
- Meta provider calls cannot be bounded below the drain window without changing a cross-repository contract;
- adding period-specific source identity would break an accepted externally-visible idempotency contract.

## Completion Report

### Status
In Progress.

### Files Changed
- `moda-interact-background/src/services/checkout-recovery.service.ts`
- `moda-interact-background/src/services/effective-billing-policy.service.ts`
- `moda-interact-background/src/services/paid-included-recovery-reservation.service.ts`
- `moda-interact-background/src/services/recovery-billing.service.ts`
- `moda-interact-background/src/services/whatsapp.service.ts`
- `moda-interact-background/tests/unit/services/recovery-billing.service.test.ts`
- `moda-interact-background/tests/unit/services/whatsapp.service.test.ts`

### Work Completed
- Added typed ACTIVE, DRAINING, and EXPIRED_RECONCILING paid-period phases using the published Shared drain-window constant.
- Prevented included paid reservation and normal paid usage admission during DRAINING; preserved promotional, purchased, and lifetime-Free fallback order.
- Added typed billing-period-closing and billing-period-reconciliation blocked outcomes.
- Added one-shot pre-provider billing revalidation with release and re-admission across rollover, drain, and expiry; expired pre-provider reservations can be released.
- Added a 30-second AbortSignal timeout to WhatsApp text and template requests while preserving ambiguous provider-failure handling.
- Preserved asynchronous Shopify usage publication; no synchronous App Event call was added to the recovery hot path.

### Validation Results
- `npx vitest run tests/unit/services/whatsapp.service.test.ts`: passed, 8 tests.
- `git diff --check`: passed.
- `npm run prisma:validate`: blocked by the clean checkout's existing `database/prisma/schema.prisma` script path; the tracked schema is `prisma/schema.prisma`.
- `npm run prisma:generate`: blocked by the same existing schema-path mismatch; focused billing suites therefore stop before test execution because Prisma Client is not generated.
- `npm run test:unit`: baseline blocked by the same ungenerated Prisma Client; also reports pre-existing unrelated failures in recovery-routing and observability startup tests.
- `npm run build` and `npx tsc --noEmit`: blocked by the same generated-Prisma baseline diagnostics.

### Git / VCS
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-008`
- Parent branch: `task/ARCH-010-BACKGROUND-008`; claim commit `c0dd717`; pushed to `origin/task/ARCH-010-BACKGROUND-008`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-008`
- Implementation branch: `task/ARCH-010-BACKGROUND-008`; implementation commit `c2d326e`; pushed to `origin/task/ARCH-010-BACKGROUND-008`.
- Both worktrees were created from and synchronized with current `origin/main` before claim; both were clean before implementation, and the implementation worktree is clean after publication.
- `submodule gitlink staged: no`; main branches were not modified.

### Architect Review
Changes Requested

#### Attempt 1 — Changes Requested

Attempt 1 is **not accepted**. Keep this same task and return it to `ready` for Attempt 2. Do not create a replacement task and do not start `ARCH-010-BACKGROUND-007`.

The implemented period-phase calculation, DRAINING exclusion of paid included capacity, period-scoped paid-included source identity, release support for an old period reservation, one-shot rollover re-admission shape, and 30-second WhatsApp timeout are retained. The corrections below are intentionally narrow.

##### Correction 1 — a newly-active recovery pause must win at pre-provider revalidation

File: `moda-interact-background/src/services/recovery-billing.service.ts`.

`revalidateBeforeProvider()` currently resolves the current policy but then preserves `free`, `lifetime-free`, and `purchased` admissions unconditionally and preserves same-period `paid` admission whenever the period is still ACTIVE. Therefore a global/shop `newRecoveriesPaused` change that occurs after initial admission but before WhatsApp can be bypassed.

After the existing `EXPIRED_RECONCILING` branch and **before** any admission-preservation branch, add an exact current-policy pause guard equivalent to:

```ts
if (current.newRecoveriesPaused) {
  await this.releaseBeforeProvider(input.admission);
  return { kind: "blocked", reason: "paused" };
}
```

Required ordering:

```text
1. resolve current policy
2. if current Paid period is EXPIRED_RECONCILING:
     release original reservation
     return billing-period-reconciliation
3. if current.newRecoveriesPaused:
     release original reservation
     return paused
4. only then apply preserved/reclassified admission logic
```

This guard applies to **every** original admission kind: `paid`, `purchased`, `free`, `lifetime-free`, and `promotional`.

Do not call `admit()` after returning `paused`. Do not keep the original reservation held after returning `paused`. Do not introduce a new blocked-reason string. Do not change `automatedWhatsappPaused`; outbound WhatsApp admission already owns that separate execution gate.

##### Correction 2 — the checkout pre-provider hook must be mandatory, not optional

File: `moda-interact-background/src/services/checkout-recovery.service.ts`.

Replace the optional/fallback form:

```ts
const revalidated = this.billingService.revalidateBeforeProvider
  ? await this.billingService.revalidateBeforeProvider(...)
  : billing;
```

with one unconditional call to `this.billingService.revalidateBeforeProvider(...)`. `CheckoutRecoveryService` is constructed with a `RecoveryBillingService`; the safety hook is part of that concrete contract and must not silently disappear.

Required behaviour:

- if revalidation returns `blocked`, return before `outboundWhatsAppAdmissionService.sendTemplate(...)`;
- do not call `commitSuccessfulInitiation()` for that blocked attempt;
- do not add a fallback that sends with the stale original admission;
- do not move Shopify App Event publication into this hot path.

##### Correction 3 — add the missing boundary regression coverage

Use the existing test files where possible. New tests may be added only when needed to prove the checkout send boundary.

Required files to update/add:

```text
moda-interact-background/tests/unit/services/recovery-billing.service.test.ts
moda-interact-background/tests/unit/services/paid-included-recovery-reservation.service.test.ts
moda-interact-background/tests/unit/services/effective-billing-policy.service.test.ts
moda-interact-background/tests/unit/services/whatsapp.service.test.ts
moda-interact-background/tests/unit/services/checkout-recovery.service.billing-boundary.test.ts   # add only if no existing focused checkout harness fits
```

The Attempt 2 focused coverage must prove all of the following literally:

1. an initial `paid` admission for the same still-ACTIVE BillingPeriod is released and returns `{ kind: "blocked", reason: "paused" }` when current `newRecoveriesPaused` becomes true;
2. an initial `purchased` admission is released and blocked as `paused` under the same race;
3. an initial `lifetime-free`/Free admission is released and blocked as `paused` under the same race;
4. a promotional admission is also released and blocked if the current pause is active;
5. DRAINING initial admission checks selected promotion first, then purchased FIFO, then lifetime Free, and returns `billing-period-closing` only when all three are unavailable;
6. pre-provider transition from an old `paid` admission into DRAINING releases the old included reservation and re-admits in the exact order `promotional -> purchased -> lifetime Free`;
7. the DRAINING revalidation path returns `billing-period-closing` only after all three non-App-Event sources are unavailable;
8. pre-provider transition into `EXPIRED_RECONCILING` releases an old paid-included reservation and returns `billing-period-reconciliation`;
9. pre-provider transition into `EXPIRED_RECONCILING` releases an already-created purchased reservation and returns `billing-period-reconciliation`;
10. `PaidIncludedRecoveryReservationService.release()` succeeds for a still-RESERVED paid-included reservation even after its owning BillingPeriod is expired/closed, while `commit()` still fails for that stale period;
11. period-scoped source identity remains different across two BillingPeriods for the same recovery and duplicate reserve inside one period remains idempotent;
12. checkout-level blocked revalidation performs **no** `sendTemplate` call and **no** `commitSuccessfulInitiation` call;
13. a timeout/abort-style provider error is classified as `ambiguous`: the relevant reservation service receives `markAmbiguous`, not `release`;
14. both text and template WhatsApp sends pass an AbortSignal created for `WHATSAPP_SEND_TIMEOUT_MS`, and `WHATSAPP_SEND_TIMEOUT_MS === 30_000`;
15. no test or production change introduces a synchronous Shopify App Events provider call in `handleCheckoutCreated`.

Do not delete existing BACKGROUND-002/BACKGROUND-019 regression cases to make the new tests pass.

##### Correction 4 — validate from the declared database submodule; do not rewrite the Prisma scripts

The Attempt 1 report describes a schema-path mismatch, but this repository declares:

```text
[submodule "database"]
  path = database
```

and `package.json` intentionally runs Prisma against:

```text
database/prisma/schema.prisma
```

The review archive contains an empty `database/` directory, which is consistent with an uninitialised submodule checkout. Treat this as task-worktree materialisation, not as a reason to change `package.json`.

From the canonical BACKGROUND-008 implementation worktree, before validation, run exactly:

```bash
git submodule sync -- database
git submodule update --init --recursive database

test -f database/prisma/schema.prisma

EXPECTED_DATABASE_GITLINK="$(git rev-parse HEAD:database)"
ACTUAL_DATABASE_HEAD="$(git -C database rev-parse HEAD)"
test "$EXPECTED_DATABASE_GITLINK" = "$ACTUAL_DATABASE_HEAD"
```

Do **not**:

- edit `package.json` to point Prisma at `prisma/schema.prisma`;
- stage or advance the `database` gitlink;
- switch the database submodule to another task branch;
- copy a schema manually into `database/`;
- use another task's database worktree.

If the recorded gitlink initializes successfully but does not contain `database/prisma/schema.prisma`, STOP and return the exact gitlink SHA and directory listing to `moda_architect`.

##### Correction 5 — required Attempt 2 validation

After the submodule is correctly initialized, run from the canonical implementation worktree:

```bash
npm run prisma:validate
npm run prisma:generate

npx vitest run \
  tests/unit/services/effective-billing-policy.service.test.ts \
  tests/unit/services/paid-included-recovery-reservation.service.test.ts \
  tests/unit/services/recovery-billing.service.test.ts \
  tests/unit/services/whatsapp.service.test.ts \
  tests/unit/services/checkout-recovery.service.billing-boundary.test.ts

npm run test:unit
npm run build
git diff --check
```

If the checkout-boundary regression is added to an existing test file instead of the named new file, replace only that one path in the focused Vitest command with the actual file used.

Focused boundary tests, Prisma validate/generate, build, and `git diff --check` must pass. If the repository-wide unit suite still has unrelated pre-existing failures after Prisma generation, record the exact failing test names and evidence; do not modify unrelated tests or production code.

Run `npm run test:integration` only when its declared PostgreSQL/Redis infrastructure is available. Record whether it ran or was unavailable.

##### Correction 6 — Completion Report must use the mandatory isolation evidence shape

Attempt 1's general statement that both worktrees were synchronized is not the complete evidence required by `docs/agent-worktree-isolation-policy.md`.

For Attempt 2, record the actual observed values in this exact structure:

```text
Physical worktree isolation:
  canonical workspace root: <actual launcher-resolved workspace root>
  parent worktree: <actual canonical parent BACKGROUND-008 worktree>
  parent branch: task/ARCH-010-BACKGROUND-008
  implementation worktree: <actual canonical Background BACKGROUND-008 worktree>
  implementation branch: task/ARCH-010-BACKGROUND-008
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Also record:

```text
database submodule initialized: yes
database gitlink expected: <full SHA>
database submodule HEAD: <full SHA>
database gitlink staged/changed: no
```

Record only values actually observed during Attempt 2. Do not reconstruct missing Attempt 1 evidence.

##### Attempt 2 allowed implementation scope

Production changes are limited to:

```text
moda-interact-background/src/services/recovery-billing.service.ts
moda-interact-background/src/services/checkout-recovery.service.ts
```

Test-only changes may touch the five focused test locations listed above. The task file may be updated for execution metadata and Completion Report evidence.

Do not change unless a required focused test proves the existing implementation is wrong:

```text
src/services/effective-billing-policy.service.ts
src/services/paid-included-recovery-reservation.service.ts
src/services/whatsapp.service.ts
```

In particular, do not redesign the phase calculation, period-scoped source key, promotion ordering, or 30-second timeout.

Do not modify Shared, Database, Shopify, Admin, Messaging, Gateway, or System-Test repositories. Do not modify another ARCH-010 task.

##### Attempt 2 stop conditions

STOP and return this same task to `moda_architect` with exact evidence if:

1. the canonical BACKGROUND-008 worktree is not on `task/ARCH-010-BACKGROUND-008`;
2. the `database` submodule cannot be initialized at the recorded gitlink without changing the gitlink;
3. the pause race cannot be fixed without changing a cross-repository contract;
4. mandatory revalidation cannot be called before `sendTemplate` without moving an irreversible provider action earlier;
5. a required focused boundary test fails after the scoped correction and fixing it would require changing an accepted dependency task;
6. satisfying this review would require synchronous Shopify App Event publication in the recovery hot path.

After the scoped correction and validation, set this same task to `status: review`, update the Completion Report with the new implementation commit and parent-report commit, push both task branches, and STOP for `moda_architect`. Do not execute `ARCH-010-BACKGROUND-007`.


## Final promotional fallback during drain/revalidation

After BACKGROUND-019, DRAINING/pre-provider fallback order is:

```text
promotional -> purchased FIFO -> lifetime Free
```

Paid included is unavailable for new reservation while DRAINING. A usable selected promotion is non-App-Event capacity and may continue under an otherwise executable subscription, exactly like purchased/lifetime Free capacity. Revalidation must never skip promotional and jump directly to purchased.
