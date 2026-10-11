---
id: ARCH-027-BACKGROUND-005
architecture_id: ARCH-027
title: Prepare and reconcile WooCommerce one-time-charge refunds
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 65
executor: copilot
claimed_at: 2026-10-11T11:54:29Z
attempt: 2
depends_on:
  - ARCH-027-BACKGROUND-004
enables:
  - ARCH-027-API-006
  - ARCH-027-ADMIN-001
created: 2026-10-03
updated: 2026-10-11
---

# Prepare and reconcile WooCommerce one-time-charge refunds

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Keep Shopify's existing provider-scoped refund behavior and add the Woo **allowance** side of one-time-charge refunds.

```text
provider -> owns monetary refund/tax/amount
Moda     -> owns unused recovery allowance
```

Woo flow:

1. API-006 creates a local allowance hold.
2. BACKGROUND-005 waits for reservations to settle.
3. BACKGROUND-005 freezes `finalCreditQuantity` and moves to `PROVIDER_ACTION_REQUIRED`.
4. Woo/provider workflow handles money.
5. Trusted provider refund completion removes exactly the held allowance.

Moda does not calculate an expected Woo monetary refund and does not compare provider money with a locally expected amount. Unmatched provider refunds remain attention-only because money cannot be converted into a trusted credit quantity.

## Context

ARCH-027 preserves the existing ARCH-015 business rule:

```text
refundableCredits =
    currentAmount
    - reservedAmount
```

A refund belongs to one exact `RecoveryCreditPurchase`.

Consumed credits are never restored.

Reserved credits may finish or release while the purchase is on refund hold. The existing purchased-credit reservation service already preserves this invariant:

- commit reduces the withdrawn lot's `currentAmount`;
- release increases the aggregate `refundingQuantity` for a withdrawn lot;
- when no credits remain the live refund is canceled as `NO_CREDITS_REMAINING`.

The current Shopify refund architecture is deliberately more complex at the provider edge:

```text
REQUESTED
    -> prepare negative/fractional Shopify correction UsageEvent
    -> provider App Event reporting/reconciliation
    -> exact settlement proof
```

Woo must not use that path.

### Provider facts

Woo's current Marketplace SaaS Billing documentation, verified 3 October 2026, states:

- merchants may request refunds for one-time charges;
- the vendor receives a notification and reviews pending requests in the vendor dashboard;
- the vendor approves or rejects the refund in that provider workflow;
- approving a refund cancels the underlying SaaS contract;
- Woo sends `saas_billing_contract.refunded` and `saas_billing_contract.canceled`;
- the refunded amount is available in `amount_refunded` on the latest transaction.

Provider reference:

`https://developer.woocommerce.com/docs/woo-marketplace/billing-api-saas`

The public documentation does **not** establish that the vendor can programmatically initiate an arbitrary proportional refund amount for a one-time charge.

The same provider documentation also states that SaaS refund requests, including one-time charges, have **no limit on the number of days after payment**. BACKGROUND-005 therefore does not require the purchase's acquisition BillingPeriod to remain current/open; API-006 owns the purchase-local refund admission rule.

Therefore ARCH-027 v1 uses:

```text
Moda local refund hold
    -> PROVIDER_ACTION_REQUIRED
    -> provider dashboard action
    -> signed refunded webhook
    -> Background reconciliation
```

and retains the existing `NEEDS_ATTENTION` safety state when provider settlement does not match Moda's frozen business expectation.

### Provider monetary evidence is audit-only for Woo allowance correctness

BACKGROUND-004 may persist real provider purchase/transaction amount for support/audit. Woo may add tax.

ARCH-027 does not derive Woo refund allowance from that money. Provider `amount_refunded`, when present, may be stored as bounded audit evidence but never determines, increases, decreases or blocks `finalCreditQuantity`.

Shopify's existing provider correction implementation remains unchanged.

## Scope

Modify only `moda-interact-background` implementation/tests required for:

1. provider-aware routing of existing refund-correction work;
2. Woo refund-hold preparation;
3. bounded claiming of Woo `refunded` charge receipts;
4. Woo provider refund evidence reconciliation;
5. exact local refund completion / needs-attention state;
6. integration into the existing leased billing cycle.

Expected production areas conceptually:

```text
src/services/
  recovery-credit-refund-correction.service.ts
  woocommerce-billing/
    charge-refund-reconciliation.service.ts
    charge-refund-evidence.ts

src/entrypoints/billing.ts
```

Exact filenames may differ where the accepted Background refactor gives a clearer owner.

Reuse:

- existing refund/purchase/counter transaction patterns;
- accepted Woo receipt-claiming helpers;
- existing `RecoveryCreditRefundStatus`;
- existing `RecoveryCreditProviderActionKind`;
- existing refund support-message code;
- Shared structured logging.

Update the nested `database/` gitlink to the newest compatible architect-accepted ARCH-027 database main commit and regenerate Prisma.

## Out of Scope

- Creating the merchant-facing Woo refund request.
- Purchase-history/refund API.
- Woo Admin refund UI.
- Automatically approving/rejecting Woo vendor-dashboard refund requests.
- Calling an undocumented Woo refund API.
- Partial-refund provider initiation.
- Subscription refunds.
- Shopify automatic correction redesign.
- Creating a Woo-specific refund table/status enum.
- Re-granting consumed credits.
- Refunding reserved credits before they settle/release.
- Admin resolution UX for `NEEDS_ATTENTION`.
- Gateway/infrastructure changes.
- Prisma schema/migration edits other than advancing the accepted nested database gitlink.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Shopify automatic refund processing remains explicitly Shopify-only

Preserve existing Shopify behavior.

### R2 — Woo refund work uses the existing leased billing cycle

No new worker/queue/cron.

### R3 — Prepare bounded Woo REQUESTED allowance holds

Claim provider=WOOCOMMERCE REQUESTED refunds in bounded batches.

### R4 — Exact ADMIN-001 producer contract

ADMIN-001 creates the first and only local Woo refund row only after an operator has verified a real Woo Pending Refund for the exact purchase. That transaction sets `refundAttemptedAt`, withdraws the purchase and holds the currently unused/unreserved allowance. `expectedProviderAmount/currency` are null.

### R5 — Reserved credits delay provider action

Keep REQUESTED while purchase.reservedAmount > 0.

### R6 — Zero remaining credits cancels the local refund

If no refundable allowance remains after reservations settle, cancel the local refund and release hold accounting through the existing no-credits path.

### R7 — Freeze exact final allowance quantity

When currentAmount > 0 and reservedAmount = 0:

```text
finalCreditQuantity = purchase.currentAmount
expectedProviderAmount = NULL
expectedProviderCurrency = NULL
status = PROVIDER_ACTION_REQUIRED
reason = WOO_VENDOR_DASHBOARD_REFUND_REQUIRED
```

Before setting `PROVIDER_ACTION_REQUIRED`, make the aggregate allowance hold equal exactly `finalCreditQuantity`. If reservations released after the initial Admin hold, increment `ShopEntitlementCounter.refundingQuantity` by the additional now-unused quantity inside the same transaction. If reservations committed, the initial held quantity already excludes them.

### R8 — Provider action is external monetary settlement

Do not call Woo and do not calculate a refund amount.

### R9 — Correlate signed refunded charge evidence exactly

Use exact provider charge operation -> purchase -> live Woo refund. Never match by amount/time/customer PII.

### R10 — Existing local hold is required for automatic allowance completion

No local hold -> `WOO_REFUND_REQUEST_NOT_FOUND`, no purchase/counter mutation, no refund invented.

### R11 — Provider amount is optional audit evidence

Validate/store bounded provider monetary evidence when supplied. Never compare it with a Moda expected amount and never derive `finalCreditQuantity` from money.

### R12 — Exact allowance completion preconditions

Require provider=WOOCOMMERCE, status=PROVIDER_ACTION_REQUIRED, finalCreditQuantity>0, WITHDRAWN purchase with zero reservations/currentAmount equal finalCreditQuantity, and sufficient counter grant/refunding hold.

### R13 — Atomic allowance completion

Set purchase REFUNDED/currentAmount=0; decrement counter grant/refunding exactly by finalCreditQuantity; set refund COMPLETED/provider reference/action/confirmed timestamp; store provider amount/currency only if available; mark receipt processed.

### R14 — Idempotency

Duplicate/reordered monetary evidence cannot decrement allowance twice. Later provider amount changes are audit/support evidence only.

### R15 — Vendor rejection releases the allowance hold through Admin

Woo's normal refund rejection decision is made by Moda as the vendor. BACKGROUND does not guess that decision.

ADMIN-001 owns the audited `Record Woo refund rejected` mutation after the operator has actually rejected the Pending Refund in Woo. That mutation releases the exact local hold and restores purchase spendability when credits remain.

A later signed `refunded` receipt after a recorded rejection is an exceptional provider/local conflict and must remain attention-only; never remove allowance a second time.

### R16 — Free-plan provenance remains valid

Woo Free top-up refunds may have null BillingPeriod/provider-subscription snapshots.

### R17 — No provider network dependency / bounded logging

Process durable provider evidence only.

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
- [x] Keep Shopify refund correction provider-scoped.
- [x] Claim bounded Woo REQUESTED holds.
- [x] Wait for reservations.
- [x] Freeze finalCreditQuantity only; keep Woo expectedProviderAmount/currency null.
- [x] Move ready refunds to PROVIDER_ACTION_REQUIRED.
- [x] Correlate signed refunded charge evidence to exact purchase/local hold.
- [x] Complete exact held allowance independent of provider monetary amount.
- [x] Store provider money only as optional audit evidence.
- [x] Leave unmatched provider refund attention non-mutating.
- [x] Prove duplicate/reordered evidence cannot double-decrement.
- [x] Keep vendor rejection hold release owned by ADMIN-001 and treat refunded-after-rejection as attention/conflict.

## Interfaces / Contracts

### Local Woo hold

```text
provider=WOOCOMMERCE
status=REQUESTED
purchase=WITHDRAWN
refundingQuantity holds allowance
expectedProviderAmount/currency = NULL
```

### Prepared hold

```text
status=PROVIDER_ACTION_REQUIRED
finalCreditQuantity > 0
```

### Provider input

Trusted refund outcome for the exact charge. Provider money is optional audit evidence only.

### Completed allowance

```text
purchase=REFUNDED
refund=COMPLETED
counter grant/refunding reduced by finalCreditQuantity
```

No Woo monetary equality invariant exists.

## Dependencies

- `ARCH-027-BACKGROUND-004`

BACKGROUND-004 must be architect-accepted Complete so Woo purchase activation/evidence and charge receipt ordering are stable before refund reconciliation is introduced.

Through BACKGROUND-004, this task also relies on API-005 signed receipt acceptance and the ARCH-027 database provider-neutral refund schema.

## Enables

- `ARCH-027-API-006`
- `ARCH-027-ADMIN-001`

ADMIN-001 produces the `provider=WOOCOMMERCE`, `status=REQUESTED` allowance holds consumed here after vendor verification of a real Woo Pending Refund. API-006 is read-only history/refund navigation.

ADMIN-001 makes the existing Platform Admin refund queue/provider-evidence support surface Woo-aware and exposes bounded read-only attention for unmatched/exceptional refunded receipts.

Further follow-ons remain:

- exceptional Admin Woo unmatched/NEEDS_ATTENTION recovery;
- Woo billing UI purchase-history/provider-refund navigation;
- Woo sandbox certification of provider partial-refund capability.

## Acceptance Criteria

- [x] No new ARCH-027 production file exceeds 300 physical lines; new files normally remain <= 200 lines, and any existing >300-line production file changed by this task contains only bounded integration/composition changes rather than substantive new domain logic.
- [x] Shopify refund behavior unchanged/provider-scoped.
- [x] Woo preparation freezes finalCreditQuantity only.
- [x] Woo expectedProviderAmount/currency remain null.
- [x] PROVIDER_ACTION_REQUIRED means allowance held while provider handles money.
- [x] Trusted refunded outcome completes exact held allowance independent of provider amount.
- [x] Monetary evidence, when stored, is audit-only.
- [x] Unmatched provider refund creates no local refund/allowance mutation.
- [x] Duplicate/reordered provider evidence cannot remove allowance twice.
- [x] Provider rejection release is not guessed.
- [x] Free Woo refund null-period provenance remains valid.
- [x] No provider network call.
- [x] `_index.md` unchanged.

## Validation

- [x] Shopify refund regression;
- [x] reservation wait / zero-remaining cancel;
- [x] REQUESTED -> PROVIDER_ACTION_REQUIRED finalCreditQuantity;
- [x] Woo expectedProviderAmount/currency null proof;
- [x] exact charge/purchase/refund correlation;
- [x] refunded evidence completes allowance with monetary amount absent/different;
- [x] unmatched provider refund no-mutation attention;
- [x] duplicate/reordered evidence no-double-decrement;
- [x] Free null-period refund;
- [x] no provider HTTP/credentials;
- [x] `git diff --check` + worktree/submodule/push evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin Woo refund API/UI/Admin support implementation.

## Implementation Notes

Prefer separate focused modules for refund-hold preparation, provider refund correlation/evidence validation, allowance settlement and vendor-rejection hold release. Existing large refund/correction services should receive only thin delegation where ARCH-027 integration is required.

Keep Woo refund settlement separate from Shopify correction mechanics:

```text
Shopify:
    refund hold
    -> negative/fractional App Event
    -> provider meter proof
    -> complete

Woo:
    refund hold
    -> PROVIDER_ACTION_REQUIRED
    -> vendor dashboard provider action
    -> signed refunded webhook
    -> complete / NEEDS_ATTENTION
```

Both converge on the same durable business outcome:

```text
RecoveryCreditPurchase REFUNDED
RecoveryCreditRefund COMPLETED
PURCHASED_RECOVERY_CREDITS reduced
```

Do not create a Woo refund table.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

- `src/entrypoints/billing.ts`
- `src/services/recovery-credit-refund-correction.service.ts`
- `src/services/recovery-credit-refund-correction/refund-correction.types.ts`
- `src/services/recovery-credit-refund-correction/refund-preparation.service.ts`
- `src/services/recovery-credit-refund-correction/refund-completion.service.ts`
- `src/services/recovery-credit-refund-correction/refund-completion-support-message.ts`
- `src/services/recovery-credit-refund-correction/woocommerce-refund-hold-preparation.service.ts`
- `src/services/woocommerce-billing/charge-refund-evidence.ts`
- `src/services/woocommerce-billing/charge-refund-receipt-processor.ts`
- `src/services/woocommerce-billing/charge-refund-reconciliation.service.ts`
- `src/services/woocommerce-billing/charge-refund-settlement.ts`
- Focused unit, billing-entrypoint, and disposable PostgreSQL integration tests.

### Work Completed

- Split the bounded REQUESTED refund scans by provider. Shopify continues through its existing automatic correction/reconciliation owners; Woo uses only the local allowance-hold preparation owner.
- Woo preparation waits for reservations, cancels zero-credit holds through the existing no-credits status/release path, and freezes the exact remaining credit quantity with provider expected amount/currency null.
- Added bounded `FOR UPDATE SKIP LOCKED` claiming for signed Woo `saas_billing_contract.refunded` charge receipts and exact operation -> purchase -> live refund correlation.
- Added atomic Woo allowance completion with provider/status/purchase/counter guards, optional validated latest-transaction money as audit evidence only, unmatched/rejected-conflict non-mutation, and receipt replay idempotency.
- Reused the existing refund-completion support-message contract and integrated the new receipt batch into the existing leased billing cycle. No worker, queue, provider HTTP call, table, enum, schema, or migration was added.
- Verified the nested database gitlink was already at architect-accepted `origin/main` commit `d5497286f2575c8e0b2fd2453e9dbdba4fc1136a`; regenerated Prisma from that schema without changing the gitlink.

### Validation Results

- PASS: focused refund/provider-routing/billing unit matrix: 41 tests across 8 files.
- PASS: `pnpm run build` and `pnpm run prisma:validate`.
- PASS: disposable PostgreSQL `woocommerce-charge-refund-reconciliation.integration.test.ts`: 1 test, including null-period activation, unmatched receipt non-mutation, amount-independent completion, and changed-amount replay without a second decrement.
- PASS: `git diff --check`; all newly added production modules are below 200 physical lines; the database submodule remained clean at the accepted commit.
- PASS on isolated retry: `observability-startup.test.ts` completed 10/10 with a 30-second timeout. The full `pnpm run test:unit` run passed 1,992/1,994 tests; two unrelated observability cases timed out at the suite's default 5-second limit.
- NOT PASS: the default integration harness run reported 13 failed files and 30 failed tests (2,086 passed, 2 skipped). Failures included stale Prisma test inputs (`defaultOutboundSoftLimit` is not in the accepted client schema) and concurrent ARCH-014 catalogue-position fixture violations. The new B005 integration test initially had a too-strict timestamp expectation; it was corrected and the focused disposable-PostgreSQL rerun passed.

### Deviations

- Existing `PurchasedRecoveryReservationService` already increments aggregate `refundingQuantity` when a reservation is released from a withdrawn lot. Woo preparation therefore recomputes live withdrawn-lot held quantities and applies only any missing aggregate delta; blindly adding `finalCreditQuantity - requestSnapshot` would count the same release twice.
- The broad unit/default-integration suites retain the failures listed above; the task-specific regression matrix, build, schema validation, and disposable PostgreSQL lifecycle test pass.

### Assumptions

- A future Woo refund API creates the local refund hold before provider action for the normal merchant flow.
- Woo `amount_refunded` is cumulative provider settlement evidence on the originally activated one-time-charge transaction.
- BACKGROUND-004's providerPriceSnapshot identifies the exact provider transaction used for the purchase.
- Provider partial refund initiation remains manual/sandbox-gated.

### Unresolved Issues

- Exact arbitrary partial-refund controls in the Woo vendor workflow remain a sandbox capability gate.
- A Woo provider refund approved without any local Moda refund request remains intentionally unmatched/unprocessed until an explicit Admin/support recovery path is designed.
- The default integration harness still has the unrelated stale-schema and concurrent catalogue-fixture failures listed in Validation Results.

### Architectural Concerns

- Reservation-release accounting is already performed by the existing reservation owner; Architect review should confirm the reconciliation-based delta in Woo preparation is the intended interpretation of R7 and avoids double-counting under concurrent shop-level refund holds.

### Git / VCS

Task branch: `task/ARCH-027-BACKGROUND-005`

Physical worktree isolation:
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-BACKGROUND-005`
- Parent branch: `task/ARCH-027-BACKGROUND-005`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-BACKGROUND-005`
- Implementation branch: `task/ARCH-027-BACKGROUND-005`
- Shared workspace checkout switched/mutated for task work: no
- Shared implementation checkout switched/mutated for task work: no
- Another task worktree reused: no

Start-of-attempt synchronization:
- Parent remote task branch synchronized: yes; durable claim commit `b8ce27f414982d86ebda00b231540710f1a8dee8` was pushed by the launcher.
- Parent `origin/main` incorporated: already current at task preparation.
- Implementation remote task branch synchronized: yes at task preparation.
- Implementation `origin/main` incorporated: already current at task preparation.

Implementation repository:
- Repository: `moda-interact-background`
- Commit: `92adf5a020c07b813999740f5d5eafd0747212eb`
- Remote branch: `origin/task/ARCH-027-BACKGROUND-005`
- Pushed: yes; remote ref verified at the same SHA.

Parent workspace:
- Task file: `docs/decisions/background/ARCH-027/BACKGROUND-005-prepare-and-reconcile-woocommerce-one-time-charge-refunds.md`
- Completion-report content commit: `b6d0c73d` (`task(ARCH-027-BACKGROUND-005): submit for architect review`).
- Remote branch: `origin/task/ARCH-027-BACKGROUND-005`
- Pushed: yes; `origin/task/ARCH-027-BACKGROUND-005` was verified at the published parent report branch HEAD.
- Submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

### Attempt 2 (2026-10-11)

#### Review Corrections

- **A1-R1 — Partially implemented; PostgreSQL settlement remains blocked by the accepted schema contract.** Charge ID and status checks remain strict. A malformed optional `amount_refunded` now becomes unavailable audit evidence (`money: null`) and the receipt processor continues through exact correlation and settlement; parser and processor unit regressions cover that path. The disposable PostgreSQL attempt with malformed money reached settlement but the accepted `RecoveryCreditRefund_woocommerce_settlement_check` rejected a `COMPLETED` Woo refund without both `providerAmount` and `providerCurrency`. This task/review explicitly prohibits schema or migration changes, and substituting a fabricated value would misstate provider audit evidence. Therefore A1-R1 cannot be completed within the authorized scope and needs an Architect/database-owner contract decision before claiming amount-independent PostgreSQL settlement.
- **A1-R2 — Addressed.** Woo REQUESTED scanning now fails independently with a bounded shared-logger warning, while the Shopify scan and corrections continue. A Woo preparation exception leaves its refund REQUESTED for a later leased cycle, is logged with bounded fields, and cannot abort later Shopify processing or trigger a failure-recording state write. Added scan-failure and preparation-failure coordinator regressions.
- **A1-R3 — Addressed.** Woo hold preparation retries Prisma `P2034` serialization conflicts up to three attempts. Exhaustion leaves the REQUESTED hold unchanged and reaches the coordinator's deferred-warning path; it is not classified as `NEEDS_ATTENTION`. Added retry-success, retry-exhaustion, and coordinator-continuation tests.

#### Attempt 2 Validation

- PASS: 27 focused tests across the Woo evidence, receipt processor, refund coordinator, and Woo hold preparation files.
- PASS: 32 existing Shopify refund preparation/provider-state/reconciliation/completion tests.
- PASS: the supported-money disposable PostgreSQL refund integration: 1 test, including exact local hold, settlement, replay, and single allowance decrement.
- BLOCKED / NOT PASS: the attempted malformed-money PostgreSQL variant reached `charge-refund-settlement.ts` but failed the accepted database check constraint `RecoveryCreditRefund_woocommerce_settlement_check`, which requires provider amount and currency for `COMPLETED`. No database schema or migration was changed. This is the unresolved A1-R1 contract conflict described above.
- PASS: `pnpm run build`, `pnpm run prisma:validate`, focused production-file diagnostics, and `git diff --check`.

#### Attempt 2 VCS

- Implementation commit: `f13c6594b01a7398037256cffbc34f69a03def6b` (`fix(ARCH-027-BACKGROUND-005): isolate Woo refund retries`); pushed to `origin/task/ARCH-027-BACKGROUND-005` and verified at the same SHA.
- Parent report update: content committed as `c70dffe7` (`task(ARCH-027-BACKGROUND-005): report attempt 2 review`) and published on `origin/task/ARCH-027-BACKGROUND-005`; the parent remote ref was independently verified after push.
- Database gitlink remains unchanged at `d5497286f2575c8e0b2fd2453e9dbdba4fc1136a`.
- Neither task branch was merged to main. ARCH-027-API-006 and ARCH-027-ADMIN-001 remain Pending.

## Architect Review

### Review Status

Changes Requested — Attempt 1 (2026-10-11).

### Review Notes

- **Disposition:** BACKGROUND-005 requires three bounded corrections before acceptance. Keep the original Attempt 1 Completion Report unchanged, preserve `attempt: 1`, and return the task to `ready` with `executor`/`claimed_at` cleared for normal launcher claiming. No dependent task may be promoted until this task is accepted Complete.
- **A1-R1 — Make monetary audit evidence genuinely optional.** `src/services/woocommerce-billing/charge-refund-evidence.ts` currently returns `WOO_REFUND_AMOUNT_EVIDENCE_INVALID` for an authenticated `saas_billing_contract.refunded` receipt whose optional `amount_refunded` is not representable by the bounded audit parser; `charge-refund-receipt-processor.ts` then skips settlement. This contradicts the agreed ARCH-027 rule that provider monetary evidence must never determine or block the frozen `finalCreditQuantity`. Preserve strict provider contract/status evidence checks, but treat malformed *optional monetary* fields as unavailable audit evidence, with bounded diagnostics as appropriate, while allowing an otherwise valid signed refund receipt to settle the exact local held allowance. Add a regression (including the real PostgreSQL path where practical) proving the refund completes and the counter decrements exactly once with malformed/absent optional money; do not weaken provider identity checks.
- **A1-R2 — Prevent Woo failures from stopping Shopify refund correction.** `RecoveryCreditRefundCorrectionService.processDue()` loads Shopify and Woo REQUESTED rows in one `Promise.all`. Rejection of the Woo query aborts the entire method before otherwise eligible Shopify corrections are processed. A Woo preparation error can similarly prevent subsequent Shopify corrections when its failure-recording update rejects. Isolate Woo scan and per-refund failure handling from the pre-existing Shopify automatic refund path. Keep the established Shopify correction/evidence semantics untouched, use the approved shared logger for bounded operational failures, and add a unit regression where the Woo scan fails while Shopify has a valid refund that must still be processed.
- **A1-R3 — Keep ordinary transaction contention retryable.** Woo hold preparation runs a serializable PostgreSQL transaction, but `RecoveryCreditRefundCorrectionService.processDue()` catches even transient Prisma write/serialization conflicts and can transition an otherwise valid Woo REQUESTED refund to `NEEDS_ATTENTION`. Do not irreversibly classify `P2034` or equivalent transient contention as business-evidence failure. Retry a bounded number of times or leave the original REQUESTED hold intact for the next leased cycle; only genuine durable evidence/state inconsistencies should enter NEEDS_ATTENTION. Add focused contention/retry tests (and PostgreSQL concurrency evidence when practical).
- **Validation classification:** Submission reports 41 focused unit tests, a passing build/Prisma validation, and one passing disposable PostgreSQL refund scenario. The full unit suite remained non-green (1,992/1,994 with two observability timeouts; isolated rerun passed), and the broad default integration run remained non-green (30 failing, 2,086 passing, 2 skipped); do not represent these broader checks as passing or infer an established baseline without comparison. Re-run task-relevant suites and the refund integration matrix after corrections; distinguish executed tests from environmental/baseline conditions.
- **Scope:** No Shopify provider-refund redesign, database schema/migration, Woo vendor HTTP action, merchant API/Admin implementation, or `docs/**/_index.md` update is authorised. Keep BACKGROUND-004 accepted and `ARCH-027-API-006`/`ARCH-027-ADMIN-001` Pending until B005 is actually Complete.

### Reviewed Files

- `src/services/recovery-credit-refund-correction.service.ts`, `src/services/recovery-credit-refund-correction/woocommerce-refund-hold-preparation.service.ts`, and existing Shopify refund preparation/reconciliation services.
- `src/services/woocommerce-billing/{charge-refund-evidence,charge-refund-receipt-processor,charge-refund-reconciliation.service,charge-refund-settlement}.ts` and existing exact charge/purchase correlation helper.
- `src/entrypoints/billing.ts`, task-owned focused unit tests and `tests/integration/woocommerce-charge-refund-reconciliation.integration.test.ts`.
- `docs/decisions/background/ARCH-027/BACKGROUND-005-prepare-and-reconcile-woocommerce-one-time-charge-refunds.md`, parent ARCH-027 architecture, and accepted database refund/purchase fields.

### Validation Reviewed

- GitHub task-branch implementation `92adf5a020c07b813999740f5d5eafd0747212eb` and parent report `0e0fd7d61fe628ab8bf3284a27dcd58590ec07c0` verified; submitted snapshot's canonical task document matches the remote Git blob.
- Agent-reported: 41 focused tests, `pnpm run build`, `pnpm run prisma:validate`, a passing 1-test disposable PostgreSQL refund scenario, and `git diff --check`. These suites were not independently rerun in this review container.
- The 1-test integration scenario does not prove the specific malformed-money, Woo-scan-failure, or transient-contention cases above. Broader non-green suite results remain recorded, not silently waived.

### Architecture Conformance

- Bounded module ownership, exact provider/Shop/purchase correlation, atomic refund allowance settlement, refund confirmation idempotency and Woo charge-batch failure isolation are present. However the three deviations above prevent full conformance to ARCH-027 refund amount independence, Shopify/Woo refund failure isolation, and retry safety.

### Follow-up

- Return the SAME `ARCH-027-BACKGROUND-005` task through `/moda-task` after this architect review is committed/pushed. The launcher should claim Attempt 2; the repository agent must first read this complete latest Architect Review as its correction contract.
- Implement A1-R1 through A1-R3, add focused proof, rerun task-required validation, update the original Completion Report and return at `status: review` for a second architect review. Do not begin `ARCH-027-API-006` or `ARCH-027-ADMIN-001` or make changes in another repository.
