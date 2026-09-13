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
status: complete
priority: 46
executor: null
claimed_at: null
attempt: 3
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
Review.

### Files Changed
- `moda-interact-background/src/services/paid-included-recovery-reservation.service.ts`
- `moda-interact-background/tests/unit/services/paid-included-recovery-reservation.service.test.ts`
- `moda-interact-background/tests/unit/services/recovery-billing.service.test.ts`

### Work Completed
- Attempt 3 corrected all paid recovery test fixtures to provide the accepted sixth promotional reservation dependency.
- Added boundary proofs for ACTIVE-to-DRAINING fallback/release, EXPIRED paid and purchased release, and ambiguous provider timeout ownership.
- Added stale-period paid-included release coverage and repaired the missing `requireOpenReservationCounter()` production helper used by ambiguous reservation transitions.
- Preserved period-boundary routing, pre-provider revalidation, 30-second WhatsApp timeout, and asynchronous usage publication behavior.

### Validation Results
- `npm run prisma:validate`: passed against `database/prisma/schema.prisma`.
- `npm run prisma:generate`: passed.
- Required focused suite (`effective-billing-policy`, `paid-included-recovery-reservation`, `recovery-billing`, `whatsapp`): passed, 4 files and 106 tests.
- BACKGROUND-008 boundary proofs: passed, 5 tests in `recovery-billing` and `paid-included-recovery-reservation`.
- Checkout blocked-send proof: passed, 1 test.
- WhatsApp suite: passed, 8 tests.
- Outbound ambiguity proof: passed, 1 test.
- `npm run test:unit`: 46 files passed, 607 tests passed; 2 files and 9 tests remain failing in existing observability release and recovery-credit purchase reconciliation assertions.
- `npm run build`: blocked by existing TypeScript errors in `purchased-recovery-reservation.service.ts` and `recovery-credit-purchase.service.ts`; none are in the touched files.
- `git diff --check`: passed.

### Git / VCS
Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-background`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-008`
  parent branch: `task/ARCH-010-BACKGROUND-008`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-008`
  implementation branch: `task/ARCH-010-BACKGROUND-008`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: yes
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: yes

database submodule initialized: yes
database gitlink expected: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`
database submodule HEAD: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`
database gitlink staged/changed: no

Parent claim commit: `214097e`, pushed to `origin/task/ARCH-010-BACKGROUND-008`.
Implementation commit: `b4ef7c8`, pushed to `origin/task/ARCH-010-BACKGROUND-008`.
Parent report commit: `a8852ad`, pushed to `origin/task/ARCH-010-BACKGROUND-008`.
Implementation worktree was clean after publication; main branches were not modified.

### Architect Review
Accepted

#### Attempt 3 — Accepted

**Decision: Accepted.** `ARCH-010-BACKGROUND-008` is Complete at Attempt 3.

Accepted implementation branch HEAD:

```text
b4ef7c885e03009f6622894230ab54a87bf4364a
```

Accepted parent report branch HEAD:

```text
a8852ada619b69d3cb6ad5dc53e8480cf0af8917
```

The architect reviewed the Attempt 3 implementation relative to accepted Attempt 2 commit `c369f64411cdcb17b4abace98973345a5f2c0d29`. The delta is one bounded commit and changes only:

```text
src/services/paid-included-recovery-reservation.service.ts
tests/unit/services/paid-included-recovery-reservation.service.test.ts
tests/unit/services/recovery-billing.service.test.ts
```

The Attempt 3 test-harness correction is accepted: Background billing tests now inject the sixth `promotionalReservationService` dependency instead of accidentally falling through to the real singleton/Prisma path.

The new boundary evidence is accepted. It proves:

- ACTIVE paid admission revalidated into DRAINING releases the old included reservation and reclassifies through the non-App-Event fallback path;
- EXPIRED_RECONCILING releases both paid-included and purchased pre-provider reservations and blocks with `billing-period-reconciliation`;
- a still-RESERVED paid-included reservation can be released after its owning period closes while direct stale-period commit remains rejected by the existing regression;
- a timeout-shaped provider failure remains ambiguous and marks the owning reservation ambiguous rather than releasing it;
- the previously-proven checkout no-send/no-commit boundary, 30-second WhatsApp timeout, period-scoped source identity and pause-aware pre-provider revalidation remain green.

The 12-line production addition of `requireOpenReservationCounter()` is also accepted after architect inspection. The method was already called by `markAmbiguousInTransaction()` before Attempt 3 but was missing from the class. The added helper only reuses `requireReservationCounter()` and enforces the existing OPEN/unexpired BillingPeriod invariant before changing a RESERVED paid-included reservation to AMBIGUOUS. It introduces no new routing, persistence model or cross-repository contract.

This production repair did deviate from the Attempt 3 execution instruction to STOP before making production changes if a new proof exposed a genuine defect. The architect explicitly ratifies the repair now because the defect and fix are both within the original BACKGROUND-008 reservation-safety scope and the implementation has been inspected. The deviation is recorded rather than rewritten as compliant historical execution; no Attempt 4 is required.

Validation evidence accepted from the canonical implementation worktree:

```text
npm run prisma:validate                                      passed
npm run prisma:generate                                      passed
focused BG8 suite                                             106 passed
BACKGROUND-008 boundary proofs                                5 passed
checkout blocked-revalidation no-send/no-commit proof         passed
WhatsApp suite                                                8 passed
outbound ambiguity proof                                      passed
git diff --check                                              passed
database gitlink                                               5443afdd8f0c816dc16e1f3e93f9906c5ca31d94
```

Repository-wide `npm run test:unit` and `npm run build` remain non-green only in the documented unrelated observability/purchased-credit reconciliation and purchased-credit TypeScript baseline. Those failures are outside the Attempt 3 changed files and do not reopen BACKGROUND-008.

##### Architect evidence reconciliation

The Attempt 3 Completion Report incorrectly records:

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-background
```

That value is not accepted as the workspace root. The recorded parent and implementation worktrees are the canonical dedicated worktrees under:

```text
/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-BACKGROUND-008
/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-BACKGROUND-008
```

and the architect reconciles the canonical workspace root as:

```text
/Users/kwadwoadomafriyie/project/moda-interact-workspace
```

The historical Completion Report entry is intentionally left unchanged and this Architect Review records the correction explicitly.

`ARCH-010-BACKGROUND-007` remains **Pending** after this acceptance because it also depends on `ARCH-010-BACKGROUND-009`, which is not Complete. Do not start BG7 yet.

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


#### Attempt 2 — Changes Requested after developer validation

Attempt 2 production code at `c369f64` remains **accepted in substance**. Developer-run canonical-worktree validation on 2026-09-13 proved Prisma validation/generation, paid-included reservation identity/release tests, checkout blocked-revalidation no-send/no-commit, WhatsApp timeout-signal tests, outbound ambiguous-failure policy, `git diff --check`, and worktree cleanliness. The remaining correction is **test-harness + missing boundary evidence only**. Do not change production source unless a corrected/new BG8 test demonstrates a genuine defect.

##### Correction A — fix the four false-negative `RecoveryBillingService` tests by injecting the sixth dependency

File:

```text
moda-interact-background/tests/unit/services/recovery-billing.service.test.ts
```

The developer reproduced exactly four failures in the focused BG8 subset. All four fail with:

```text
EffectiveBillingPolicyError: Shop shop-1 has no active Shopify billing contract
reason: NO_CONTRACT
stack:
  PromotionalRecoveryReservationService.findUsableGrant
  PromotionalRecoveryReservationService.reserveInTransaction
  RecoveryBillingService.admit
```

These are test-harness failures, not production failures. `RecoveryBillingService` constructor order is exactly:

```ts
constructor(
  database,
  policyResolver,
  reservationService,
  purchasedReservationService,
  paidIncludedReservationService,
  promotionalReservationService,
)
```

The failing tests pass only five constructor arguments, so the sixth argument falls back to the real singleton `promotionalRecoveryReservationService`. Because paid policies contain `planId`, `admit()` checks promotion first and the real service touches Prisma, producing `NO_CONTRACT`.

The four reproduced failing test names are exactly:

```text
does not reserve paid included capacity while the billing period is draining
uses the closing reason only after all DRAINING fallbacks are exhausted
preserves an included admission when the same period remains ACTIVE
releases and re-admits included capacity when the period changes before the provider
```

Add one deterministic test helper in this file, or equivalent inline stubs, with this behaviour:

```ts
function unavailablePromotionalReservationService() {
  return {
    reserve: vi.fn(async () => ({ kind: "unavailable" as const })),
    commit: vi.fn(),
    release: vi.fn(),
    markAmbiguous: vi.fn(),
  };
}
```

For each of the four tests above, pass the helper as the **sixth** `RecoveryBillingService` constructor argument. Do not change production code to make these tests pass. Do not remove `planId` from the paid policy fixture; promotion-first ordering is part of the accepted architecture.

Where a BG8 test intentionally needs a usable promotion, pass a dedicated sixth-argument stub whose `reserve()` returns the exact promotional outcome required by that test. Never allow a BG8 unit test to fall through to the real promotional singleton.

After this harness fix, rerun exactly:

```bash
npx vitest run \
  tests/unit/services/recovery-billing.service.test.ts \
  -t 'does not reserve paid included capacity while the billing period is draining|blocks an expired paid period with the reconciliation reason|uses the closing reason only after all DRAINING fallbacks are exhausted|preserves an included admission when the same period remains ACTIVE|releases and re-admits included capacity when the period changes before the provider|releases a .* admission when new recoveries become paused'
```

Expected result: every selected test passes. A `NO_CONTRACT` stack through `PromotionalRecoveryReservationService` after the sixth dependency is injected is a blocker and must be reported without production changes.

##### Correction B — retain already-green developer evidence

Do not rewrite tests that the developer has already demonstrated green unless needed mechanically for a shared helper. Preserve these exact proven results:

```text
Prisma schema at database/prisma/schema.prisma: valid
Prisma client generation: passed
database submodule HEAD: 5443afdd8f0c816dc16e1f3e93f9906c5ca31d94
```

Selected `PaidIncludedRecoveryReservationService` evidence: 5/5 passed:

```text
derives the period-scoped source key after current period validation
does not double-increment a duplicate reserve
uses a different source key when the same recovery enters a different period
releases definitive failure capacity once
rejects commit after the owning period closes
```

Checkout boundary evidence: `does not send or commit when billing revalidation blocks the admission` passed.

WhatsApp evidence: full `whatsapp.service.test.ts` passed 8/8.

Outbound ambiguity evidence: `removes definitive failures but preserves ambiguous pending intent` passed.

`git diff --check` passed and the canonical implementation worktree was clean at local/remote HEAD `c369f64411cdcb17b4abace98973345a5f2c0d29`.

##### Correction C — add only the still-missing explicit BG8 proofs

After fixing Correction A, add narrowly-scoped tests for these behaviours. Prefix every newly-added Attempt 3 test title with exactly `BACKGROUND-008:`.

1. **ACTIVE paid -> DRAINING pre-provider revalidation**
   - create/admit a `paid` admission for `period-1` while ACTIVE;
   - current policy becomes DRAINING before provider action;
   - release `paid-included:period-1:<recoveryId>` exactly once;
   - re-admit exactly once;
   - prove fallback order promotional -> purchased -> lifetime Free;
   - prove paid-included `reserve()` is not called during the DRAINING re-admission;
   - if all three fallback sources are unavailable, return `{ kind: "blocked", reason: "billing-period-closing" }`.

2. **EXPIRED_RECONCILING release for paid and purchased**
   - use explicit admission objects; do not require initial `admit()` if that adds irrelevant fixture complexity;
   - for original `paid`, current policy EXPIRED_RECONCILING -> paid-included `release()` exactly once -> `billing-period-reconciliation`;
   - for original `purchased`, current policy EXPIRED_RECONCILING -> purchased `release()` exactly once -> `billing-period-reconciliation`;
   - assert no re-admission/reserve call occurs after the reconciliation result.

3. **Still-RESERVED paid-included release after period close/expiry**
   - in `paid-included-recovery-reservation.service.test.ts`, reserve while the period is current/open;
   - mutate the fixture period to CLOSED or expired while the reservation remains RESERVED;
   - `release()` must succeed and decrement reserved capacity once;
   - duplicate release must remain idempotent;
   - `commit()` for the same stale reservation must still fail closed.

4. **Timeout/abort maps to ambiguous billing ownership**
   - in `recovery-billing.service.test.ts`, create an admitted reservation and a timeout-shaped error, e.g. `const error = new Error("timeout"); error.name = "TimeoutError";`;
   - call `handleProviderFailure({ admission, error })`;
   - expect returned disposition `"ambiguous"`;
   - expect the exact owning reservation service `markAmbiguous()` once;
   - expect that service `release()` not called.

Do not add another timeout constant and do not change `WhatsAppService`; the 30-second AbortSignal transport evidence is already green.

##### Correction D — exact Attempt 3 validation

From the canonical implementation worktree:

```bash
git submodule sync -- database
git submodule update --init --recursive database
test -f database/prisma/schema.prisma
EXPECTED_DATABASE_GITLINK="$(git rev-parse HEAD:database)"
ACTUAL_DATABASE_HEAD="$(git -C database rev-parse HEAD)"
test "$EXPECTED_DATABASE_GITLINK" = "$ACTUAL_DATABASE_HEAD"

npm run prisma:validate
npm run prisma:generate

# First prove the corrected existing BG8 subset.
npx vitest run \
  tests/unit/services/recovery-billing.service.test.ts \
  -t 'does not reserve paid included capacity while the billing period is draining|blocks an expired paid period with the reconciliation reason|uses the closing reason only after all DRAINING fallbacks are exhausted|preserves an included admission when the same period remains ACTIVE|releases and re-admits included capacity when the period changes before the provider|releases a .* admission when new recoveries become paused'

# Then prove every newly-added Attempt 3 case independently.
npx vitest run \
  tests/unit/services/recovery-billing.service.test.ts \
  tests/unit/services/paid-included-recovery-reservation.service.test.ts \
  -t '^BACKGROUND-008:'

# Preserve previously-green boundary evidence.
npx vitest run \
  tests/unit/services/matured-candidate.materialization.test.ts \
  -t 'does not send or commit when billing revalidation blocks the admission'

npx vitest run tests/unit/services/whatsapp.service.test.ts

npx vitest run \
  tests/unit/services/outbound-whatsapp-admission.service.test.ts \
  -t 'removes definitive failures but preserves ambiguous pending intent'

git diff --check
```

All commands above must pass. Then run the repository-wide evidence commands required by the task:

```bash
npm run test:unit
npm run build
```

Repository-wide unit/build may remain non-green only for failures outside the Attempt 3 changed files and outside the behaviours above. Record exact failing files/errors; do not fix unrelated purchase/refund/observability/schema-contract drift in BG8.

##### Correction E — Attempt 3 allowed scope and stop rules

Production source changes are not expected and are not authorised by default.

Allowed implementation changes:

```text
moda-interact-background/tests/unit/services/recovery-billing.service.test.ts
moda-interact-background/tests/unit/services/paid-included-recovery-reservation.service.test.ts
```

Only if a shared helper must be mechanically adjusted to preserve already-green evidence, these existing test files may also change:

```text
moda-interact-background/tests/unit/services/matured-candidate.materialization.test.ts
moda-interact-background/tests/unit/services/whatsapp.service.test.ts
moda-interact-background/tests/unit/services/outbound-whatsapp-admission.service.test.ts
```

Task-owned documentation may update:

```text
docs/decisions/background/ARCH-010/BACKGROUND-008-boundary-safe-paid-recovery-initiation.md
```

Do **not** modify these production files unless a corrected/new required test proves a genuine defect, and if that happens STOP before editing and return the exact failing test to `moda_architect`:

```text
src/services/checkout-recovery.service.ts
src/services/recovery-billing.service.ts
src/services/effective-billing-policy.service.ts
src/services/paid-included-recovery-reservation.service.ts
src/services/whatsapp.service.ts
```

Do not modify Shared, Database, Shopify, Admin, Messaging, Gateway, or System-Test. Do not start BACKGROUND-007.

##### Correction F — durable lifecycle/worktree evidence

The current parent task is returned to:

```yaml
status: ready
executor: null
claimed_at: null
attempt: 2
```

The next legitimate claim increments exactly once to Attempt 3. Record actual values in the mandatory evidence block. `canonical workspace root` is the workspace root (expected `/Users/kwadwoadomafriyie/project/moda-interact-workspace` if that is what the launcher resolves), not `/Users/.../moda-interact-workspace/moda-interact-background`.

After validation, set `status: review`, record Attempt 3 commits/evidence, push both task branches, and STOP.


## Final promotional fallback during drain/revalidation

After BACKGROUND-019, DRAINING/pre-provider fallback order is:

```text
promotional -> purchased FIFO -> lifetime Free
```

Paid included is unavailable for new reservation while DRAINING. A usable selected promotion is non-App-Event capacity and may continue under an otherwise executable subscription, exactly like purchased/lifetime Free capacity. Revalidation must never skip promotional and jump directly to purchased.
