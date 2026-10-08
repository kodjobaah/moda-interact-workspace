---
id: ARCH-027-BACKGROUND-001
architecture_id: ARCH-027
title: Make Woo recovery accounting and frozen fallback provider-safe
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 45
executor: copilot
claimed_at: 2026-10-08T22:42:48Z
attempt: 2
depends_on:
  - ARCH-027-DATABASE-001
enables:
  - ARCH-027-BACKGROUND-002
created: 2026-10-03
updated: 2026-10-08
---

# Make Woo recovery accounting and frozen fallback provider-safe

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Make the existing Background recovery-accounting path safe for Woo before recurring Woo lifecycle activation is implemented.

This task owns three related prerequisites:

1. **paid included allowance semantics**
   ```text
   effectiveAllowance =
       currentAllowanceQuantity ?? grantedQuantity

   available =
       max(
           effectiveAllowance
           - committedQuantity
           - reservedQuantity
           - forfeitedQuantity,
           0
       )
   ```

2. **provider-correct UsageEvent attribution for every recovery capacity source**
   ```text
   SHOPIFY Shop     -> UsageEvent.provider = SHOPIFY
   WOOCOMMERCE Shop -> UsageEvent.provider = WOOCOMMERCE
   ```

3. **Woo payment-pause FROZEN fallback**
   ```text
   paid included allowance -> unavailable for new recovery
   active promotional credits -> existing eligibility
   purchased top-up credits -> usable
   lifetime Free credits -> usable
   ```

   Verified Woo cancellation is not a FROZEN state: BACKGROUND-002 keeps the prepaid paid Subscription ACTIVE with `cancelAtPeriodEnd=true`; normal paid capacity policy continues until prepaid entitlement actually ends, after which the Subscription returns to Free.

The task does not consume Woo billing receipts or change Subscription lifecycle state.

It prepares the existing recovery engine so BACKGROUND-002 can safely mark a Woo subscription paid/FROZEN without either creating Shopify reporting work for Woo, globally blocking credits the merchant already owns, or granting paid included recovery after the provider period is no longer current.

## Context

The current Background implementation is still Shopify-shaped in several ways that matter to ARCH-027:

1. `EffectiveBillingPolicyResolver` treats every `FROZEN` subscription as a hard error before fallback capacity can be considered.
2. `ShopExecutionEligibilityService` and `PendingRecoveryCandidateService` treat FROZEN as a Shop-wide execution denial.
3. `RecoveryBillingService` hard-blocks `EXPIRED_RECONCILING` paid periods before promotional/purchased/lifetime-Free fallback is attempted.
4. `PaidIncludedRecoveryReservationService.commit()` creates Shopify-reportable provider evidence.
5. The Free, promotional and purchased recovery commit services create `UsageEvent` rows with `shopifyReportState=NOT_APPLICABLE` but currently rely on the Prisma provider default, which would incorrectly label Woo recovery consumption as `SHOPIFY`.
6. Paid included availability currently reads `grantedQuantity` rather than the new mutable current allowance.

Woo provider behavior now fixed by architecture is different:

```text
paused
    -> recurring paid entitlement frozen
    -> provider may retry renewal

renewed
    -> successful financial evidence / provider coverage reconciliation
    -> does not itself reset Moda included allowance

canceled
    -> prepaid paid entitlement remains ACTIVE until the signed provider end

prepaid term end
    -> current Subscription returns to Free
```

While Woo is FROZEN because the provider recurring contract is paused/payment-recovering, already-owned non-recurring capacity remains usable. A verified scheduled cancellation remains paid/ACTIVE until the prepaid term actually ends. BACKGROUND-006 owns later exact-30-day allowance boundaries and the durable cancellation-end safety net.

The 2026-10-08 snapshot has already refactored `PendingRecoveryCandidateService` into a thin candidate facade plus `candidate-index.store.ts`, `candidate-lifecycle.service.ts`, `candidate-activity.service.ts` and `checkout-order-guard.service.ts`. Recovery reservation sources now reuse `recovery-reservation/reservation-lifecycle.ts` for narrow replay/transition/retry helpers. Preserve those boundaries; do not reintegrate them into a monolithic candidate or billing service. The Background nested `database/` snapshot predates the accepted ARCH-027 schema and must be advanced before code is compiled or tested against new fields.

The task relies on durable:

```text
Shop.platform = SHOPIFY | WOOCOMMERCE
```

as the bounded ARCH-027 v1 dispatch evidence.

This remains a minimal provider-aware adaptation of the existing recovery domain, not a generic billing-provider framework.

## Scope

Modify only `moda-interact-background` production/tests needed for:

- effective paid allowance/current allowance;
- provider-aware recovery UsageEvent attribution;
- provider-aware FROZEN execution gating;
- fallback recovery source selection while Woo paid included entitlement is unavailable;
- deterministic exhaustion identity.

Expected directly relevant production areas include:

```text
src/services/effective-billing-policy.service.ts
src/services/shop-execution-eligibility.service.ts
src/services/pending-recovery-candidate.service.ts
src/services/pending-recovery-candidate/candidate-index.store.ts
src/services/pending-recovery-candidate/candidate-lifecycle.service.ts
src/services/pending-recovery-candidate/candidate-activity.service.ts
src/services/pending-recovery-candidate/checkout-order-guard.service.ts
src/services/recovery-reservation/reservation-lifecycle.ts
src/services/recovery-billing.service.ts
src/services/paid-included-recovery-reservation.service.ts
src/services/free-recovery-reservation.service.ts
src/services/promotional-recovery-reservation.service.ts
src/services/purchased-recovery-reservation.service.ts
src/services/outbound-whatsapp-admission.service.ts
```

Exact files may differ after inspection. The candidate facade and source-specific reservation services remain the owning public entry points; the extracted modules are implementation details to reuse, not new competing pathways.

Update the nested database gitlink to the **integrated, architect-accepted ARCH-027-DATABASE-001 database main commit**, rather than relying on an older Background `database/` schema or copying Prisma files. Verify `BillingOperation`, Woo billing receipt persistence, `Subscription.providerCoverageEndAt` and `BillingPeriodEntitlementCounter.currentAllowanceQuantity` exist in the adopted schema, then regenerate Prisma.

### Explicitly retained boundaries

This task MUST NOT:

- process Woo billing webhook receipts;
- create/switch/freeze/cancel a Subscription;
- open/renew/close a Woo BillingPeriod;
- buy a new top-up while FROZEN;
- reconcile a Woo top-up/refund;
- call Woo;
- add a new queue/provider framework.

## Out of Scope

- API webhook ingress.
- PostgreSQL receipt claiming.
- Woo recurring subscription lifecycle reconciliation.
- Woo paid `BillingPlan` materialisation.
- Woo billing-period creation/renewal.
- Woo plan-switch writer logic.
- Woo top-up activation/refund reconciliation.
- Shopify plan-change redesign.
- Shopify App Event publisher redesign.
- Woo API calls or credentials.
- Woo WordPress/UI changes.
- Admin changes.
- Gateway/infrastructure changes.
- Prisma schema/migration edits other than advancing the accepted nested database gitlink.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Current allowance is the paid included spend ceiling

Every new paid-included reservation uses:

```text
effectiveAllowance =
    currentAllowanceQuantity ?? grantedQuantity

available =
    max(
        effectiveAllowance
        - committedQuantity
        - reservedQuantity
        - forfeitedQuantity,
        0
    )
```

### R2 — Preserve the high-water grant invariant

Continue to require:

```text
committedQuantity + reservedQuantity + forfeitedQuantity <= grantedQuantity
```

When non-null:

```text
0 <= currentAllowanceQuantity <= grantedQuantity
```

Do not require committed/reserved usage to fit under a later lower current allowance.

### R3 — Existing paid reservations survive an allowance downgrade

A lower current allowance gates **new** paid included reservations. Existing RESERVED included capacity may still COMMIT or RELEASE.

### R4 — Upgrade exposes new capacity without usage reset

Raising current allowance makes the difference available without resetting committed/reserved/forfeited or changing BillingPeriod identity.

### R5 — Shopify null override is unchanged

For Shopify, `currentAllowanceQuantity = NULL` remains valid and effective allowance is `grantedQuantity`.

### R6 — Effective policy exposes platform/status/current allowance

The effective recovery policy must carry enough durable state to distinguish `Shop.platform`, `Subscription.status`, paid period phase and granted/current allowance.

### R7 — Shopify FROZEN remains a hard execution block

For Shopify FROZEN preserve existing `SUBSCRIPTION_FROZEN` execution denial.

### R8 — Woo payment-pause FROZEN is not a Shop-wide recovery block

For Woo payment-pause FROZEN, execution gating must allow the recovery/conversation path to reach billing-capacity selection. `EffectiveBillingPolicyResolver` returns a bounded Woo FROZEN policy instead of throwing the generic frozen error.

### R9 — Woo payment-pause FROZEN capacity order

For Woo payment-pause FROZEN, new recovery admission tries only:

```text
active promotional
-> purchased
-> lifetime Free
-> capacity exhausted
```

It MUST NOT reserve from paid `INCLUDED_RECOVERY_CREDITS`.

### R10 — Expired Woo provider period also falls back

When a Woo paid current provider period is no longer active/current while lifecycle evidence converges, do not grant paid included capacity and do not globally block before fallback sources are tried.

Shopify expired-period behavior remains unchanged.

### R11 — Revalidation preserves valid fallback admissions across freeze races

Promotional/purchased/lifetime-Free admissions may remain valid if Woo freezes before provider send. A paid-included admission encountering Woo FROZEN/expired period must be released and re-admitted through fallback sources.

### R12 — Pending candidate scheduling is platform-aware

Remove/replace direct platform-agnostic FROZEN discard paths that would discard Woo candidates before fallback capacity can be evaluated. Check both the initial candidate scheduling path and checkout-update scheduling/refresh, as well as materialisation/execution eligibility. Preserve the refactored candidate index/lifecycle/activity/checkout-order-guard ownership and Shopify behavior.

### R13 — Every recovery UsageEvent has explicit provider attribution

For paid included, promotional, purchased and lifetime-Free recovery commits:

```text
Shopify -> provider=SHOPIFY
Woo     -> provider=WOOCOMMERCE
```

Do not rely on the database default.

### R14 — Paid included external reporting remains provider-specific

Shopify paid included remains PENDING/reportable with Shopify event/idempotency evidence. Woo paid included is `NOT_APPLICABLE` with null Shopify reporting fields.

### R15 — Non-reportable recovery sources stay non-reportable

Free/promotional/purchased recovery remains `shopifyReportState=NOT_APPLICABLE` on both platforms; only the explicit provider discriminator differs.

### R16 — Exhaustion identity includes current allowance

Include effective/current allowance in deterministic paid-capacity exhaustion/support identity.

### R17 — No duplicate Woo capacity ledger

Reuse existing counters/reservation services.

### R18 — Structured logging remains shared

Use the Shared structured logger and bounded identifiers only.

### Maintainability — bounded production modules

ARCH-027 must not extend the existing Background monoliths or create another catch-all service. For production source introduced or materially expanded by this task:

- target **<= 200 physical lines per new production file**;
- **300 physical lines is a hard ceiling** for a new production file;
- an existing production file already over 300 lines may receive only thin integration/composition changes required to delegate into focused modules;
- substantive new reconciliation, policy, evidence parsing, persistence/accounting or provider-specific mechanics must live in bounded focused modules with independently testable responsibilities;
- do not evade the rule by moving several unrelated responsibilities into one dense file just below the ceiling;
- cohesive test files are exempt from the production-source line ceiling when keeping the behavioural matrix together is clearer.

## Work Items

- [x] Keep ARCH-027 production implementation modular: new production files target <= 200 lines and never exceed 300; add only thin wiring to existing >300-line production files and extract substantive new behaviour into focused modules.
- [x] Integrate the accepted ARCH-027 database main commit into Background `database/`, verify its Woo schema fields and regenerate Prisma.
- [x] Reuse extracted candidate index/lifecycle/activity/checkout-order-guard modules and `recovery-reservation/reservation-lifecycle.ts`; retain source-specific reservation ownership.
- [x] Add current-allowance availability including forfeited quantity.
- [x] Load durable Shop.platform in effective policy/execution gating.
- [x] Keep Shopify FROZEN hard-block behavior.
- [x] Allow Woo FROZEN to reach capacity selection.
- [x] Skip Woo paid included while FROZEN or provider period is expired/pending lifecycle convergence.
- [x] Preserve promotional -> purchased -> lifetime-Free fallback.
- [x] Make pre-provider revalidation release paid included and retain/re-admit fallback capacity correctly.
- [x] Remove direct platform-agnostic Woo FROZEN candidate discard across checkout-created/update scheduling and downstream execution/materialisation gates; leave Shopify gates unchanged.
- [x] Explicitly write UsageEvent.provider for paid/free/promotional/purchased recovery commits.
- [x] Preserve Shopify paid App Event behavior.
- [x] Prove Woo NOT_APPLICABLE events cannot enter Shopify publishing.
- [x] Update deterministic exhaustion identity.
- [x] Add focused cross-provider regression tests, including the Attempt 2 reservation-writer boundaries.

## Interfaces / Contracts

### Effective paid allowance

```text
effectiveAllowance = currentAllowanceQuantity ?? grantedQuantity
available = max(effectiveAllowance - committed - reserved - forfeited, 0)
```

### Woo FROZEN / expired-period fallback

```text
paid included -> unavailable
promotion     -> eligible if active
purchased     -> eligible if available
lifetime Free -> eligible if available
```

### Recovery UsageEvent provider evidence

```text
Shopify recovery -> provider=SHOPIFY
Woo recovery     -> provider=WOOCOMMERCE
```

Only Shopify paid included usage is externally reportable.

## Dependencies

- `ARCH-027-DATABASE-001`

DATABASE-001 must be architect-accepted Complete and the Background nested database gitlink must point to the accepted database main commit before implementation.

This task does not depend on API-005 because it is the **capacity-safety prerequisite** for later Woo paid subscription activation and may execute in parallel with API provider-edge work once the database contract is accepted.

## Enables

- `ARCH-027-BACKGROUND-002`

## Acceptance Criteria

- [x] No new ARCH-027 production file exceeds 300 physical lines; new files normally remain <= 200 lines, and any existing >300-line production file changed by this task contains only bounded integration/composition changes rather than substantive new domain logic.
- [x] Paid included availability uses currentAllowance fallback and subtracts committed/reserved/forfeited.
- [x] Shopify null current allowance preserves existing behavior.
- [x] Shopify FROZEN still blocks execution.
- [x] Woo FROZEN reaches capacity selection rather than being discarded globally.
- [x] Woo FROZEN cannot reserve paid included capacity.
- [x] Woo FROZEN can use active promotional, purchased and lifetime-Free capacity.
- [x] Woo expired provider period cannot grant paid included capacity while lifecycle evidence is pending, but fallback capacity remains usable.
- [x] Paid admission then freeze-before-send releases/re-admits safely.
- [x] Pending-candidate scheduling, refresh, eligibility and materialisation cannot discard Woo FROZEN before allowed fallback capacity is evaluated; Shopify FROZEN remains blocked.
- [x] Candidate lifecycle/index/checkout-order-lock behaviour is preserved, with no duplicate scheduler or reservation ledger.
- [x] Background Prisma client is generated from the accepted integrated ARCH-027 database revision, including Woo billing/allowance fields.
- [x] Shopify paid included usage remains provider SHOPIFY + PENDING.
- [x] Woo paid included usage is provider WOOCOMMERCE + NOT_APPLICABLE.
- [x] Woo promotional, purchased and lifetime-Free recovery usage explicitly writes provider WOOCOMMERCE.
- [x] Shopify non-reportable recovery sources explicitly remain provider SHOPIFY.
- [x] Woo recovery UsageEvents cannot enter Shopify publication scans.
- [x] No Woo lifecycle writer is implemented in this task.
- [x] `docs/architecture/_index.md` is unchanged.

## Validation

Required categories include:

- [x] Prisma generate/validate (`npm run build` regenerated Prisma; `npm run prisma:validate` passed).
- [x] Build/typecheck (`npm run build` passed); no lint script is declared in this repository's `package.json`.
- [x] Current-allowance + forfeited availability tests, allowance upgrade without usage reset, Shopify null override and existing reservation commit after downgrade.
- [x] Shopify FROZEN hard-block regression.
- [x] Woo FROZEN promotional/purchased/lifetime-Free fallback tests.
- [x] Woo FROZEN no-paid-included test.
- [x] Freeze-before-send revalidation/re-admission test.
- [x] Candidate scheduling/refresh/materialisation Woo FROZEN not-discarded tests, including a Woo checkout-update path.
- [x] Refactored candidate index/checkout-order-lock regression tests (included in full unit suite).
- [x] Pending-candidate Shopify FROZEN discarded regression.
- [x] Provider attribution tests for paid/free/promotional/purchased commits on both platforms.
- [x] Shopify App Event reporting regression.
- [x] Woo NOT_APPLICABLE publication exclusion test.
- [x] Exhaustion identity test includes current allowance.
- [x] `git diff --check`.
- [x] Dedicated worktree/submodule/push evidence: Attempt 2 implementation commit `2135977f612a9db53c94f6a26e09a041a7d9d329` was pushed; the parent Completion Report update is being published on its `task/ARCH-027-BACKGROUND-001` branch.

### Execution Evidence

Physical worktree isolation:

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-BACKGROUND-001`
- Parent branch: `task/ARCH-027-BACKGROUND-001`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-BACKGROUND-001`
- Implementation branch: `task/ARCH-027-BACKGROUND-001`
- Shared workspace checkout switched/mutated for task work: no
- Shared implementation checkout switched/mutated for task work: no
- Another task worktree reused: no

Start-of-attempt synchronization:

- Parent remote task branch fast-forwarded: not-needed; no task-specific remote changes to fast-forward.
- Parent `origin/main` incorporated: yes.
- Implementation remote task branch fast-forwarded: not-needed; no task-specific remote changes to fast-forward.
- Implementation `origin/main` incorporated: already-current.

Attempt 2 launcher claim:

- Executor: `copilot`; attempt: 2; previous attempt: 1.
- Claim commit: `bae180c0dd16238ce33efe0a8dd302786f0c7bf0`, committed and pushed.
- Prepared parent head: `083a737c341f6c1934ca5907017bf10b6c68f381`.
- Prepared implementation head: `9dfbb38f2c34fa2510c65dc74a7a53b374aa7431`.

Recursive implementation submodules:

- `git submodule sync --recursive`: passed during launcher preparation.
- `git submodule update --init --recursive`: passed during launcher preparation.
- Prepared database submodule commit: `e86b16027595af663eab5ba5fb23745435307372`.
- ARCH-027 accepted integrated database commit adopted for this task: `ef51500b2728bc0c894e627dfa1c9e6c9d4d9a13`.

## Stop Condition

After all defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
    -> set task status to review
    -> return to moda_architect
    -> STOP
```

Do not begin Woo webhook receipt reconciliation or any enabled/follow-on work.

## Implementation Notes

Prefer focused modules for paid-included allowance calculation, Woo frozen/fallback capacity policy and UsageEvent provider attribution. In particular, do not add substantial ARCH-027 logic directly to existing large recovery accounting/reservation services; keep those files as composition points.

This task exists because the **current source would be unsafe to activate for Woo paid merchants as-is**.

Keep the implementation small:

```text
same BillingPeriod counter
same UsageReservation
same UsageEvent business metric

only:
    current allowance admission semantics
    +
    provider-aware external-reporting evidence
```

Do not use this task to redesign the billing domain.

The later Woo lifecycle task is responsible for atomically updating a counter on plan switch:

```text
if targetAllowance > grantedQuantity:
    grantedQuantity = targetAllowance

currentAllowanceQuantity = targetAllowance
version += 1
```

This task only consumes that state correctly.

## Completion Report

### Status

Review

### Files Changed

Production:

- `database/` gitlink advanced to accepted ARCH-027 database main commit `ef51500b2728bc0c894e627dfa1c9e6c9d4d9a13`.
- Added bounded helpers `src/services/recovery-billing/paid-included-allowance.ts` (46 lines) and `src/services/recovery-billing/usage-event-provider.ts` (15 lines).
- Updated effective billing policy, shop execution eligibility, checkout-update orchestration, pending recovery candidate scheduling, recovery billing admission/revalidation, capacity admission/exhaustion identity, and the four source-specific reservation commit services.
- Updated the paid-included reservation writer to reject Woo FROZEN or expired provider coverage before counter mutation and to require a Shopify usage handle only for Shopify commits.

Tests:

- Updated focused billing policy, reservation (including direct Woo FROZEN/coverage-expiry rejection, Woo null-handle commit, and Shopify missing-handle rejection), capacity admission, revalidation, candidate scheduling/materialization, checkout-update orchestration, exhaustion notification, execution eligibility and Shopify usage publisher tests.

### Work Completed

- Paid included reservations now use `currentAllowanceQuantity ?? grantedQuantity`, subtract committed/reserved/forfeited quantities, preserve the high-water grant invariant, and allow existing reservations to commit/release after a downgrade.
- Paid-included reservations enforce the Woo FROZEN and provider-coverage-expiry fence inside the serializable writer transaction before any counter mutation. Woo paid commits no longer depend on a Shopify usage handle; Shopify paid commits still fail closed without one.
- Woo FROZEN and provider-coverage-expired paid policies reach promotional -> purchased -> lifetime-Free fallback without reserving paid-included capacity. Shopify frozen and expired behavior remains blocked as before.
- Pre-provider revalidation releases invalid paid-included reservations and re-admits fallback capacity; existing Woo fallback reservations survive freeze/expiry races.
- Checkout-created, checkout-updated and matured candidate paths use platform-aware recovery eligibility while preserving the extracted candidate index/lifecycle/activity/checkout-order-lock boundaries.
- Paid, promotional, purchased and lifetime-Free UsageEvents explicitly persist `provider`; only Shopify paid included events carry Shopify reporting state/handle/idempotency evidence. Woo NOT_APPLICABLE events remain outside Shopify publishing scans.
- Paid exhaustion identity now includes effective current allowance.
- Attempt 1 implementation commit `9dfbb38` remains the reviewed base. Attempt 2 correction commit `2135977f612a9db53c94f6a26e09a041a7d9d329` was pushed on `task/ARCH-027-BACKGROUND-001`.

### Validation Results

`npx vitest run tests/unit/services/paid-included-recovery-reservation.service.test.ts` passed (1 file, 30 tests); `npm run build` passed (Prisma generation plus TypeScript build); `npm run prisma:validate` passed; `npm run test:unit` passed (174 files, 1,872 tests); `git diff --check` passed. Both new production helpers are under 200 lines. No lint script is declared in `package.json`.

### Deviations

No implementation scope deviations. Repository lint is unavailable because no lint script is declared. The ARCH-027 accepted database gitlink update is included as an implementation change.

### Assumptions

- ARCH-027-DATABASE-001 is accepted before implementation.
- ARCH-027 v1 paid Woo billing runs only for `Shop.platform = WOOCOMMERCE`.
- Woo recovery consumption is locally accounted in Moda; paid included, promotional, purchased and lifetime-Free UsageEvents are explicitly provider=WOOCOMMERCE and are not reported through Shopify App Events.
- Existing Shopify usage publisher already selects only reportable Shopify states and therefore naturally excludes `NOT_APPLICABLE`.

### Unresolved Issues

None within this bounded capacity/accounting task.

### Architectural Concerns

A future architecture that allows a WooCommerce-platform Shop to use a non-Woo billing provider will require an explicit billing-provider discriminator rather than using `Shop.platform` as the v1 provider-reporting dispatch. ARCH-027 intentionally does not add that broader abstraction.

## Architect Review

### Review Status

Changes Requested — Attempt 1 (2026-10-08).

### Review Notes

Reviewed implementation commit `9dfbb38f2c34fa2510c65dc74a7a53b374aa7431` and parent task/Completion Report commit `4ed1b48bcf164c18f68f92bbfd26dfd232d7aebf` against the uploaded ARCH-027 task-worktree snapshot and the parent architecture. The accepted database submodule gitlink `ef51500b2728bc0c894e627dfa1c9e6c9d4d9a13` is correct. The bounded allowance helper, fallback admission order, candidate scheduling paths, explicit provider attribution for the four consumption sources, and Shopify publisher filtering are substantially aligned.

**A1-R1 — Remove the Shopify usage-handle prerequisite from Woo paid included commits.**

In `src/services/paid-included-recovery-reservation.service.ts`, `commitInTransaction()` unconditionally requires `plan.shopifyUsageEventHandle` before computing the platform-specific `UsageEvent`. This rejects an otherwise valid Woo `PAID_METERED` reservation when its operational BillingPlan has no Shopify event handle. ARCH-027 permits Woo paid included usage to be local and non-reportable. Require a Shopify usage handle only when `Shop.platform = SHOPIFY`, while retaining the paid-plan check for both platforms. For Woo, commit must write `provider=WOOCOMMERCE`, `shopifyReportState=NOT_APPLICABLE`, and null Shopify handle/idempotency fields, without creating any Shopify publishing work. Correct the paid reservation unit fixture, which currently always returns `shopifyUsageEventHandle: "paid-meter"` even for Woo. Add regressions proving a Woo paid commit with a null Shopify handle succeeds, and a Shopify paid commit lacking its required handle still fails closed. Preserve idempotent replay and reservation/counter invariants.

**A1-R2 — Enforce Woo payment-pause and provider-coverage expiry at the reservation writer boundary.**

`RecoveryCapacityAdmissionService.admit()` correctly skips paid included capacity when Woo is `FROZEN` or its billing-period phase is expired. However, public `PaidIncludedRecoveryReservationService.reserve()` resolves the policy independently and currently checks only paid plan kind and whether the underlying BillingPeriod is open/not past its local `periodEnd`. It does **not** check Woo `FROZEN` or the earlier `providerCoverageEndAt` deadline. A direct or future caller can consequently create/re-activate paid included capacity during Woo FROZEN or after verified provider coverage expires while the local BillingPeriod is still open. Enforce the Woo-specific source-of-truth status/phase/coverage fence inside the existing serializable reservation transaction, before any increment or creation, without relying exclusively on the admission coordinator. Maintain existing Shopify behaviour. Add focused direct-service negative tests covering Woo FROZEN with still-open local BillingPeriod and Woo expired coverage before local period end, asserting no reservation/counter mutation; retain the allowance-downgrade existing-reservation COMMIT/RELEASE regression and the coordinator fallback cases.

**A1-R3 — Reconcile the completion checklist.**

The Work Item `Add focused cross-provider regression tests` is still unchecked despite tests being reported and present. On Attempt 2, the implementing agent should mark it complete when the missing A1-R1/A1-R2 cases have passed and update the Completion Report with exact commands/results. No separate task or opportunistic refactor is authorized.

### Reviewed Files

- `src/services/paid-included-recovery-reservation.service.ts`
- `src/services/recovery-billing/paid-included-allowance.ts`
- `src/services/recovery-billing/usage-event-provider.ts`
- `src/services/recovery-billing/recovery-capacity-admission.service.ts`
- `src/services/recovery-billing.service.ts`
- `src/services/effective-billing-policy.service.ts`
- `src/services/shop-execution-eligibility.service.ts`
- `src/services/pending-recovery-candidate.service.ts`
- `src/services/checkout-recovery/checkout-event-orchestrator.service.ts`
- `src/services/free-recovery-reservation.service.ts`
- `src/services/promotional-recovery-reservation.service.ts`
- `src/services/purchased-recovery-reservation.service.ts`
- `tests/unit/services/paid-included-recovery-reservation.service.test.ts`
- `tests/unit/services/recovery-billing/recovery-capacity-admission-paid.test.ts`
- Reported changed tests for recovery revalidation, candidate scheduling/materialisation and Shopify publisher filtering; `package.json`; nested `database/` gitlink.

### Validation Reviewed

Completion Report states `npm run build` (Prisma generation + TypeScript), `npm run prisma:validate`, `npm run test:unit` (174 files / 1,868 tests) and `git diff --check` all passed. Inspected the declared `package.json` scripts; no lint script exists. Inspected relevant test assertions and source, but did not independently rerun npm tests (the uploaded source archive has no installed `node_modules`) or a PostgreSQL integration suite. Two uncovered boundary cases above prevent acceptance despite the reported green tests. Mirrored branch/commit and canonical dedicated-worktree preparation evidence are recorded in the Completion Report; physical execution was not independently observed in this external review environment.

### Architecture Conformance

Partially conforming. Correct accepted database revision, architecture-aligned source responsibilities and most fallback/provider behaviour. A1-R1 conflicts with Woo local-only paid usage and A1-R2 leaves the transactional paid reservation boundary weaker than the coordinator's Woo FROZEN/expired-coverage policy. The task is not accepted or Complete.

### Follow-up

Return the **same** `ARCH-027-BACKGROUND-001` task to `ready` for a clean Attempt 2 claim, with existing `attempt: 1` preserved and `executor`/`claimed_at` cleared. The implementation-owning `moda_background` agent corrects only A1-R1 through A1-R3, reruns the focused regressions and required task validation, publishes both mirrored task branches and resubmits for architect review. `ARCH-027-BACKGROUND-002` remains dependency-gated. No domain `_index.md` or architecture index reconciliation until the user explicitly requests finalization.
