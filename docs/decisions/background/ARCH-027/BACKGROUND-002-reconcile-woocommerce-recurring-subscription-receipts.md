---
id: ARCH-027-BACKGROUND-002
architecture_id: ARCH-027
title: Reconcile WooCommerce recurring subscription webhook receipts
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 50
executor: copilot
claimed_at: 2026-10-10T12:14:52Z
attempt: 4
depends_on:
  - ARCH-027-API-005
  - ARCH-027-BACKGROUND-001
enables:
  - ARCH-027-BACKGROUND-004
  - ARCH-027-BACKGROUND-006
created: 2026-10-03
updated: 2026-10-10
---

# Reconcile WooCommerce recurring subscription webhook receipts

## Architecture

Architecture ID: `ARCH-027`

Architecture document: `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator: `moda_architect`

## Objective

Consume authenticated durable Woo **subscription-wrapper** webhook receipts and idempotently reconcile provider financial/lifecycle evidence onto the Shop's one Moda `Subscription`, without treating webhook arrival order as provider causality and without making Woo financial renewal own Moda's exact-30-day included-recovery cadence.

Core separation:

```text
Woo financial/lifecycle evidence
    -> current provider contract
    -> ACTIVE/FROZEN
    -> providerCoverageEndAt
    -> cancelAtPeriodEnd / terminal end

Moda entitlement cadence
    -> BillingPeriod exact-30-day windows
    -> BACKGROUND-006 after the first paid period
```

This task opens the first paid entitlement period on verified activation. It does not roll later entitlement periods merely because `renewed` arrived.

## Context

ARCH-027 has already fixed:

- API-003: recurring create/switch/cancel intent is persisted before provider writes and the selected paid operational `BillingPlan` is materialised before provider I/O without changing merchant entitlement;
- API-005: Woo webhooks are HMAC-verified and durably stored without business mutation;
- BACKGROUND-001: paid included recovery accounting is Woo-safe and uses `currentAllowanceQuantity ?? grantedQuantity`;
- DATABASE-001: one Subscription per Shop, durable Woo operations/receipts, mutable current allowance and nullable `Subscription.providerCoverageEndAt`.

Woo recurring webhook payloads are durable authenticated **snapshots**. Woo does not provide ARCH-027 with a signed sequence/event ID that makes `WooCommerceBillingWebhookReceipt.receivedAt` a safe causal clock. Correctness must therefore survive duplicate, delayed, concurrent and out-of-order delivery.

The accepted product decisions are:

```text
canceled != entitlement ended
renewed != allowance reset
next_payment_date != currentPeriodEnd
receivedAt != provider event order
```

## Scope

Modify only `moda-interact-background` implementation/tests needed for:

1. bounded claiming of unprocessed Woo subscription-wrapper receipts;
2. trusted provider-contract/Shop correlation;
3. field-specific evidence reconciliation across durable receipts + recurring operations + current Subscription;
4. recurring Subscription lifecycle/financial projection;
5. first paid entitlement-period creation on verified activation;
6. receipt processed/error bookkeeping;
7. integration into the existing leased billing worker cycle.

Expected implementation areas are conceptually:

```text
src/services/woocommerce-billing/
  subscription-receipt-reconciliation.service.ts
  subscription-operation-resolution.ts
  subscription-evidence-reducer.ts
  subscription-transition.service.ts

src/entrypoints/billing.ts
```

Exact repository-local filenames may differ where the accepted refactor provides a clearer bounded owner.

Update the nested `database/` gitlink to the newest compatible architect-accepted database main commit and regenerate Prisma before source changes.

Reuse the existing billing worker deployment, leased billing scheduler, Prisma transactions, current Shop/Subscription lock conventions, existing paid-period close/release semantics, `recoveryCapacityResumeService` and Shared structured logging. Do not add another worker deployment.

## Out of Scope

- Woo `charge` receipt processing.
- Top-up activation/refund settlement.
- Woo provider GET/POST/DELETE calls.
- Woo credentials.
- Time-driven entitlement rollover after the first paid period; owned by `ARCH-027-BACKGROUND-006`.
- Treating `next_payment_date` as the Moda allowance-reset boundary.
- Creating catch-up allowance periods while financial coverage was absent.
- Shopify Partner API reconciliation changes.
- Shopify same-cycle plan-change behavior.
- API webhook validation.
- API command initiation.
- Admin/Woo UI.
- Gateway changes.
- Prisma schema/migration edits other than advancing the accepted nested database gitlink.
- A Shared lifecycle-event contract.
- Updating `docs/architecture/_index.md` or any domain `_index.md`.

## Requirements

### R1 — Reuse the existing billing worker

Keep bounded PostgreSQL receipt claiming, `SKIP LOCKED` concurrency and atomic business-state/receipt completion transactions. Claim concurrency does not weaken the business-state lock: after a worker obtains the Shop/Subscription lock it must re-read the durable evidence required to derive the projection.

### R2 — Trusted tenant/contract correlation

Resolve the Shop only from trusted Woo operation/current-or-historical provider-contract evidence. Never use merchant/browser tenant input from the provider payload.

The current recurring contract may mutate the current Subscription. A historical provider contract may update only its own operation/receipt bookkeeping; it cannot pause, renew, switch, cancel, end or reactivate a newer current contract.

### R3 — Receipt arrival is not provider ordering

Do not order Woo lifecycle by:

```text
WooCommerceBillingWebhookReceipt.id
WooCommerceBillingWebhookReceipt.receivedAt
HTTP delivery order
worker claim order
```

Do not populate Shopify-oriented lifecycle watermark fields from those transport values merely to manufacture a Woo sequence.

For each claimed receipt, derive the current provider-contract projection from all relevant durable authenticated receipts for that contract, serialized Moda recurring operations, and the locked current Subscription.

### R4 — Reconcile independent evidence dimensions

Do not define one total lifecycle rank such as `updated < renewed < paused < canceled`. Reconcile these dimensions independently:

```text
contract identity
plan intent
financial health / provider coverage
termination
```

Termination is monotonic for one provider contract:

```text
NONE -> CANCEL_SCHEDULED -> PREPAID_TERM_ENDED
```

A causally valid plan update may still apply after cancellation was scheduled for the remaining prepaid term, but it must never clear the newer cancellation. A stale payment-pause observation must not overwrite newer successful renewal evidence. No non-terminal observation may resurrect a terminally ended provider contract.

### R5 — Moda recurring operations order merchant plan intent

API-003 serializes recurring merchant commands. Use the durable recurring-operation history to decide which `SUBSCRIPTION_CREATE` / `PLAN_SWITCH` target may become the current plan.

An `updated` receipt may project a plan switch only when it is compatible with the current provider contract and the causally current accepted switch intent/provider snapshot. A late/stale `updated` receipt from an earlier switch must not revert a later accepted merchant plan decision.

If the authenticated provider evidence cannot be correlated safely to a unique current plan intent, fail closed with bounded sync-attention evidence rather than guessing from receipt arrival.

### R6 — Financial health and provider coverage use authenticated provider evidence

Use provider financial evidence inside the authenticated contract snapshot (including documented billing-intent/transaction timestamps/identities where available) to determine causally current payment health/coverage.

`providerCoverageEndAt` may move earlier or later when causally newer evidence changes Woo `next_payment_date`; never compute it with `MAX()` over all observed dates.

If the payload does not provide sufficient evidence to decide between contradictory financial observations, fail closed; do not use `receivedAt` as a tiebreaker.

### R7 — Verified first paid activation opens the first exact-30-day Moda period

A trusted `SUBSCRIPTION_CREATE` activates only when the current Moda Subscription is local Free:

```text
Subscription.status = ACTIVE
current plan = FREE
providerSubscriptionId = NULL
billingPeriodId = NULL
```

Let `activationAt` be the verified provider activation/payment-completion time. Atomically project:

```text
Subscription.status = ACTIVE
Subscription.planId = already-materialised target paid plan
Subscription.providerSubscriptionId = new recurring contract
Subscription.providerCoverageEndAt = causally current provider financial boundary
Subscription.cancelAtPeriodEnd = false

BillingPeriod.periodStart = activationAt
BillingPeriod.periodEnd = activationAt + exact 30 days
Subscription.currentPeriodStart = same periodStart
Subscription.currentPeriodEnd = same periodEnd
full current-plan included allowance
committed/reserved/forfeited = 0
```

There is no detached former-period carry-forward. A new paid contract can be created only after any previous scheduled cancellation actually ended and the current Subscription is Free.

### R8 — Plan switch preserves the current Moda period/usage

For a causally current trusted `updated`/PLAN_SWITCH on the current provider contract:

```text
keep BillingPeriod id/start/end
keep committed/reserved/forfeited
update current plan
update currentAllowanceQuantity to target plan allowance
raise grantedQuantity high-water only when required by existing invariants
```

Provider monetary proration and `next_payment_date` are provider-owned. They may update `providerCoverageEndAt` only when the financial evidence is causally authoritative. They MUST NOT change `currentPeriodEnd`.

### R9 — Renewed updates financial coverage; it does not reset allowance

For a causally current verified `renewed` on the current provider contract:

```text
extend/re-establish providerCoverageEndAt from authoritative financial evidence
FROZEN -> ACTIVE when payment recovery is proven
keep current BillingPeriod/usage unchanged
do not grant a new included allowance merely because renewed arrived
```

After commit, the existing worker cycle may allow BACKGROUND-006 to reconcile a due entitlement boundary.

### R10 — Paused is the Woo payment-failure FROZEN state

For causally current verified `paused` on the current provider contract:

```text
Subscription.status = FROZEN
```

Preserve current paid plan/provider contract/BillingPeriod/counters and existing `providerCoverageEndAt`; do not invent future coverage and do not grant a new allowance. BACKGROUND-001 owns fallback to already-owned non-paid-included capacity.

A stale `paused` observation must not overwrite newer successful renewal evidence.

### R11 — Verified canceled schedules prepaid term end

For the current recurring contract, a trusted coherent `canceled` snapshot with signed `end_date` projects:

```text
Subscription.status = ACTIVE
paid plan remains current
providerSubscriptionId remains current contract
billingPeriodId/currentPeriod* remain current Moda allowance window
cancelAtPeriodEnd = true
providerCoverageEndAt = signed end_date
```

Confirm a matching `CANCEL` operation atomically where applicable. Do not return the Subscription to Free and do not recreate/reset lifetime-Free allowance.

If the signed `end_date <= now` when the receipt is processed, perform the terminal R12 transition immediately instead of creating a scheduled-cancel state in the past.

### R12 — prepaid_term_ended is terminal paid -> Free evidence

A coherent trusted `prepaid_term_ended` for the current provider contract may perform terminal transition even when the earlier `canceled` receipt was delayed/lost. Require provider evidence consistent with the prepaid term having ended within the accepted clock tolerance.

Atomically:

```text
close/truncate current paid BillingPeriod with CONTRACT_ENDED semantics
Subscription.status = ACTIVE
Subscription.planId = existing Free BillingPlan
Subscription.providerSubscriptionId = NULL
Subscription.providerCoverageEndAt = NULL
Subscription.billingPeriodId = NULL
Subscription.currentPeriodStart = NULL
Subscription.currentPeriodEnd = NULL
Subscription.cancelAtPeriodEnd = false
```

Preserve onboarding, lifetime-Free, purchased, promotional and historical state. Never recreate/reset lifetime-Free credits.

A later receipt from that historical contract cannot mutate the current Free state or a newer provider contract.

### R13 — Subscription monetary refund never mutates purchase-refund allowance

Treat subscription `refunded` only as recurring provider lifecycle/financial evidence when its authenticated snapshot establishes a relevant state. Never create or modify `RecoveryCreditRefund` top-up allowance state from subscription money.

### R14 — Authenticated but contradictory evidence is a bounded business conflict

A durable authenticated snapshot that cannot be reconciled safely is not retried forever as though PostgreSQL were unavailable. Record bounded safe sync-attention/error evidence, fail closed for new paid included entitlement where necessary, and mark the receipt processed when the contradiction is permanent.

Retryable infrastructure/transaction failures still leave the receipt retryable under the existing bounded mechanism.

### R15 — No provider network dependency / bounded logging

Use durable signed receipts + Moda state only. No Woo network calls occur during reconciliation. Use shared structured logging and never log credentials/full provider payloads.

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
- [x] Advance the nested database gitlink to the accepted ARCH-027 schema and regenerate Prisma.
- [x] Preserve bounded subscription-receipt claiming in the existing billing worker.
- [x] Implement trusted Shop/current-vs-historical provider-contract correlation.
- [x] Implement an evidence reducer that never uses receipt arrival time as provider causality.
- [x] Reconcile plan intent from serialized recurring operations and compatible provider evidence.
- [x] Reconcile financial health/`providerCoverageEndAt` from causally current authenticated provider evidence.
- [x] Implement first paid activation with exact `activationAt + 30 days` Moda period.
- [x] Implement same-period plan switch without moving `currentPeriodEnd`.
- [x] Implement `renewed` as coverage/payment recovery without allowance reset.
- [x] Implement causally current `paused -> FROZEN` without new allowance.
- [x] Implement `canceled -> cancelAtPeriodEnd=true/providerCoverageEndAt=end_date` while keeping paid entitlement current.
- [x] Implement terminal `prepaid_term_ended -> Free`, including when prior `canceled` delivery was missing.
- [x] Ensure old-contract lifecycle cannot mutate Free or a newer current contract.
- [x] Handle permanently contradictory authenticated evidence as bounded sync-attention rather than infinite retry.
- [x] Preserve purchased/lifetime-Free/promotional/onboarding state.
- [x] When a recurring receipt deterministically resolves a merchant/Moda operation, set `WooCommerceBillingWebhookReceipt.billingOperationId` exactly once; autonomous lifecycle receipts may remain null.
- [x] Add duplicate, delayed, concurrent and out-of-order reconciliation tests.

## Interfaces / Contracts

### Durable input

Owner: `ARCH-027-API-005` / database persistence from `ARCH-027-DATABASE-001`.

```text
WooCommerceBillingWebhookReceipt
    topic
    providerContractId?
    billingOperationId? (initially NULL; set only after deterministic correlation)
    normalizedPayload (authenticated provider-shaped subscription wrapper)
    receivedAt (transport metadata only)
    processedAt?
    processingError?
```

### Merchant recurring intent

Owner: `ARCH-027-API-003`.

```text
BillingOperation
    shopId -> locked Woo Shop
    SUBSCRIPTION_CREATE | PLAN_SWITCH | CANCEL
    serialized per Shop
    target MerchantPricingPlan / providerReference / operation state
```

### Durable projection

```text
Subscription.providerSubscriptionId
Subscription.providerCoverageEndAt
Subscription.status
Subscription.cancelAtPeriodEnd
Subscription.planId
Subscription.billingPeriodId
Subscription.currentPeriodStart/currentPeriodEnd
BillingPeriod / BillingPeriodEntitlementCounter
```

`providerCoverageEndAt` and `currentPeriodEnd` are intentionally different clocks.

## Dependencies

- `ARCH-027-API-005`
- `ARCH-027-BACKGROUND-001`

Both must be architect-accepted Complete before this task becomes Ready.

## Enables

- `ARCH-027-BACKGROUND-004`
- `ARCH-027-BACKGROUND-006`

The charge-acquisition path and time-driven entitlement reconciler may proceed independently after this task is accepted.

## Acceptance Criteria

- [x] No new ARCH-027 production file exceeds 300 physical lines; new files normally remain <= 200 lines, and any existing >300-line production file changed by this task contains only bounded integration/composition changes rather than substantive new domain logic.
- [x] Woo receipt `receivedAt`, receipt ID, HTTP delivery order and worker claim order are never used as provider lifecycle causality.
- [x] Historical provider-contract receipts cannot mutate a newer current contract.
- [x] First paid activation opens exactly one Moda period ending `activationAt + 30 days`.
- [x] Plan switch preserves BillingPeriod id/start/end and usage while applying the target allowance ceiling.
- [x] Causally current provider financial evidence may change `providerCoverageEndAt` without changing `currentPeriodEnd`.
- [x] `renewed` extends/re-establishes financial coverage and can recover FROZEN, but does not reset included allowance.
- [x] A stale `paused` cannot regress newer successful renewal evidence.
- [x] Verified `canceled` leaves the paid plan/current period active, sets `cancelAtPeriodEnd=true`, and sets provider coverage to signed `end_date`.
- [x] A canceled snapshot already past `end_date` converges directly to terminal Free state.
- [x] `prepaid_term_ended` can terminally end the current contract even when earlier canceled delivery is missing, when signed term evidence is coherent.
- [x] Terminally ended old-contract events cannot resurrect or mutate the current Free/newer contract.
- [x] Lifetime-Free allowance is never recreated/reset by cancellation/end transitions.
- [x] Subscription `refunded` evidence never creates/modifies one-time purchase-refund allowance state.
- [x] Permanently contradictory authenticated evidence fails closed and does not retry forever; retryable infrastructure failures remain retryable.
- [x] All business projection + receipt completion transitions are atomic/idempotent under duplicate/concurrent delivery.
- [x] No Woo provider network call occurs in reconciliation.
- [x] No new worker deployment, Shared lifecycle contract or domain `_index.md` change is introduced.

## Validation

Required focused validation categories:

- [x] unit tests for evidence reduction/field-specific merge;
- [ ] database-backed duplicate/concurrent receipt tests (test added; developer execution pending);
- [ ] first Free -> paid activation exact-30-day period test (test added; developer execution pending);
- [ ] updated same-period plan-switch test including provider `next_payment_date` movement with unchanged `currentPeriodEnd` (test added; developer execution pending);
- [ ] renewed-without-reset test (test added; developer execution pending);
- [ ] paused -> FROZEN then newer renewed -> ACTIVE test (test added; developer execution pending);
- [ ] renewed delivered before stale paused test (test added; developer execution pending);
- [ ] canceled -> paid scheduled-end test (test added; developer execution pending);
- [ ] canceled whose end_date is already past -> direct terminal Free test (test added; developer execution pending);
- [ ] prepaid_term_ended without previously processed canceled -> terminal Free test (test added; developer execution pending);
- [ ] late updated after canceled preserves cancellation while applying only causally valid plan dimension (test added; developer execution pending);
- [ ] old-contract lifecycle after newer contract/current Free is non-mutating (test added; developer execution pending);
- [ ] contradictory-evidence bounded-attention/no-infinite-retry test (test added; developer execution pending);
- [ ] receipt exact-duplicate/business-idempotency tests (test added; developer execution pending);
- [ ] targeted lint/typecheck/build required by repository/task instructions;
- [x] `git diff --check`;
- [x] dedicated parent/implementation worktree, start-of-attempt synchronization and pushed task-branch evidence.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, finish the Completion Report, return control to `moda_architect` and STOP. Do not begin BACKGROUND-004 or BACKGROUND-006.

## Implementation Notes

Prefer a thin receipt-reconciliation coordinator with separate focused modules for operation correlation, authenticated provider-evidence reduction, recurring Subscription projection and first-paid-period activation. Do not build one large Woo subscription reconciler containing all evidence parsing, locking and projection rules.

Prefer one deterministic reconciliation reducer over topic handlers that independently overwrite shared Subscription fields. The reducer may retain topic-specific parsing, but the final projection must merge contract identity, plan intent, financial evidence and termination deliberately.

Do not query Woo during receipt processing to manufacture ordering. If SYSTEM-TEST-002 proves the signed provider snapshot is insufficient for a required causal comparison, return that provider capability gap to `moda_architect`.

## Completion Report

### Status

Blocked. The required disposable PostgreSQL integration suite cannot start because the host has no Docker CLI. Attempt 3 is not review-ready; executor and claimed_at are cleared while attempt 3 is preserved.

### Files Changed

Implementation changes are in `moda-interact-background`: bounded `src/services/woocommerce-billing/` modules, thin billing-worker integration, Woo-focused unit tests, and disposable database-backed lifecycle/concurrency coverage. The nested `database/` gitlink is at accepted database main commit `7e0dcebd6216a886d29e226ba1d9c63da204053e`. Attempt 3 changed only `src/entrypoints/billing.ts` and added `tests/unit/runtime/billing-entrypoint.woocommerce-failure.test.ts`.

### Work Completed

Added subscription-wrapper receipt claiming to the existing leased billing worker. Claims use a bounded batch and PostgreSQL `FOR UPDATE SKIP LOCKED`, filter only the seven subscription topics, and process the business projection plus receipt completion atomically. Tenant correlation uses only provider contract references on recurring operations/current subscriptions and validates Woo Shop platform; historical contract observations cannot mutate a different current contract.

Added provider-time evidence parsing and independent reducers for financial health/coverage, plan intent, and monotonic termination. Receipt IDs and `receivedAt` are not used for provider causality. First verified paid activation creates one exact 30-day Moda period; plan switches preserve period boundaries/usage and apply the target allowance; renewals restore coverage without resetting allowances; pause freezes; cancellation schedules the signed prepaid end; and terminal evidence closes the paid period and returns the existing subscription to Free without resetting lifetime-Free state. Permanent contradictions record bounded sync-attention evidence and terminate processing; provider I/O and top-up refund accounting are not introduced.

When uniquely resolvable, activation, plan-switch, and cancellation receipts link to the corresponding durable recurring operation. Added unit reducers and a disposable PostgreSQL integration matrix for duplicate/concurrent activation, exact period boundaries, plan switch, renewal/pause ordering, scheduled and terminal cancellation, historical-contract isolation, contradictions, and subscription-refund separation.

Attempt 2 addresses Architect Review items A1-R1 through A1-R4: operation attribution is receipt-topic-specific and preserves existing links; renewal recovery requires matching causally relevant successful payment evidence and ignores unrelated contract modifications; same-price plan switches require matching signed plan identity; and integration fixtures share one canonical Free plan with safe teardown. Focused regressions cover receipt attribution, historical/recent payment evidence, failed intents, same-price/different-name plans, and the shared Free fixture.

Attempt 3 addresses A2-R1 through A2-R3. A2-R1 is present in prior implementation commit `7f27ae63b6f9d459f96d67d678cdd50fa36b6018`, confirmed as an ancestor of the prepared Attempt 3 commit: successful/permanently reconciled receipts use `processedAt` with `processingError: null`; quarantined receipts keep `processedAt: null` with bounded `processingError`; the PostgreSQL suite asserts durable conflict diagnostics and no repeat claim. A2-R2 adds a narrowly scoped failure boundary around only the Woo receipt batch in `src/entrypoints/billing.ts`; bounded error name/message and lease/config correlation are logged, Woo completion is emitted only on success, and the existing global reconciliation callback runs once after either outcome. A2-R3 adds executable rejection and success-path regressions, including 64/256-character log-field bounds.

### Validation Results

Attempt 3 results:

- `npx vitest run tests/unit/services/woocommerce-billing tests/unit/runtime/billing-entrypoint.runtime-controls.test.ts tests/unit/runtime/billing-entrypoint.woocommerce-failure.test.ts` — 7 files, 32 tests passed.
- `npx vitest run tests/unit/runtime/billing-entrypoint.woocommerce-failure.test.ts` — 1 file, 2 tests passed after strengthening bounded-error assertions.
- `npm run test:unit` — 184 files; 1,933 passed and 12 failed (1,945 total). The failures are the unrelated Commerce tests in `tests/unit/commerce/model-bridge-diagnostics.test.ts` (5) and `tests/unit/commerce/production-model.test.ts` (7), where the installed Shared package lacks the expected model diagnostic exports.
- `npm run prisma:validate` — passed; schema valid against nested database commit `7e0dcebd6216a886d29e226ba1d9c63da204053e`.
- `npx tsc --noEmit` — failed with 10 diagnostics in four existing `src/commerce/` files due to missing/changed exports and fields in `@modainteract/moda-interact-shared/commerce/runner`; no task-touched Woo file was reported.
- `npm run build` — Prisma Client generation passed, then TypeScript compilation failed with the same 10 existing Commerce diagnostics.
- `git diff --check` — passed for the implementation changes before commit; final parent and implementation worktree checks are recorded below.

Required database-backed validation:

- Exact command: `npm run test:integration -- tests/integration/woocommerce-subscription-reconciliation.concurrency.integration.test.ts`.
- Result: exit code 1 before Vitest started; 0 integration tests executed. The shared disposable-infrastructure harness attempted PostgreSQL image `pgvector/pgvector:pg17` and failed with `Unable to start ephemeral PostgreSQL ... spawn docker ENOENT`. `command -v docker` returned no executable. Redis startup was not reached. All database-backed validation boxes remain unchecked, including the A2-R1 conflict/quarantine assertions.

### Deviations

The database-backed integration suite could not start because Docker is unavailable (`spawn docker ENOENT`), so no PostgreSQL or Redis-backed assertions are claimed as passing. Full unit/build/typecheck commands also expose unrelated existing Shared-package Commerce failures. Attempt 3 therefore remains `blocked`, not `review`, until the integration environment is available and required checks can pass.

### Assumptions

- The real Woo sandbox will be used by SYSTEM-TEST-002 to certify that signed snapshots contain sufficient financial/order evidence for the reducer.

### Unresolved Issues

The exact disposable PostgreSQL/Redis integration command above remains outstanding. The real Woo sandbox evidence sufficiency remains assigned to SYSTEM-TEST-002 as specified by the task.

### Architectural Concerns

No separate worker deployment, Shared lifecycle contract, provider network dependency, or domain index change was added. Architect review should inspect the authenticated evidence fields and operation causality assumptions against the ARCH-027 provider contract.

### Execution Evidence

- Launcher prepared Attempt 1 for canonical executor `copilot`; dependencies API-005 and BACKGROUND-001 passed. Parent claim commit: `b6d85222baed2ebd1879bccbfda59b8a9799963e`.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-027-BACKGROUND-002`, branch `task/ARCH-027-BACKGROUND-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-027-BACKGROUND-002`, branch `task/ARCH-027-BACKGROUND-002`.
- Start synchronization: parent and implementation task branches fast-forwarded `not-needed`; `origin/main` incorporated `already-current` in both worktrees. Recursive submodule sync/update passed; initial database submodule was `fb936e6da0c5bc9328cfd31d3c2fd3a3789b5dce`.
- Task implementation adopts database main commit `7e0dcebd6216a886d29e226ba1d9c63da204053e`; nested database worktree is clean.
- Attempt 2 was claimed by the launcher as `copilot` at `2026-10-09T17:47:13Z`; claim commit `9b0aa9cd6936bbe772d8500ae709fc5b9916b10a` was committed and pushed. Parent and implementation task branches were reused at their canonical worktree paths; `origin/main` was already incorporated and the database submodule initialized at `7e0dcebd6216a886d29e226ba1d9c63da204053e`.
- Implementation commits: `e9975f5`, `ba8aba1ab87d8fd0bc8706f739fd78009c8c0fd0`, and Attempt 2 correction `8729ed8b36819e33f91b567adceeb92f29f630e9`; all pushed to `origin/task/ARCH-027-BACKGROUND-002`.
- Attempt 3 was launcher-claimed as `copilot` at `2026-10-10T11:01:16Z`, claim commit `c97fa4264201db6b7b1a08b2b2d7447640e910df`; prepared implementation commit `41588922caede153912791edbd514be96affde67`; dependencies passed and the database submodule was `7e0dcebd6216a886d29e226ba1d9c63da204053e`.
- Attempt 3 implementation commit `765e4a9` (`fix(background): continue global billing scan after Woo batch failure`) is pushed on `task/ARCH-027-BACKGROUND-002`. It descends from prior A2-R1 correction commit `7f27ae63b6f9d459f96d67d678cdd50fa36b6018`.
- Attempt 3 ended `blocked`; `attempt: 3` is preserved and `executor`/`claimed_at` are cleared. The parent report commit and both branch push parity checks are recorded after publication.
- Shared workspace and shared Background source checkout were not switched or modified; no other task worktree was reused.

## Architect Review

### Review Status

Changes Requested — Attempt 3 (2026-10-10). PostgreSQL evidence complete; Ready for evidence-only finalization on a branch synchronized with accepted Shopify main.

### Review Notes

#### Architect re-gating following developer PostgreSQL run (2026-10-10)

- **Integration validation blocker resolved.** The developer ran the exact task's disposable PostgreSQL/Redis integration suite from the dedicated `ARCH-027-BACKGROUND-002` Background implementation worktree. Vitest 4.1.11 reported **1 test file passed; 6 tests passed, 0 failed**, including concurrent duplicate workers, 30-day period preservation, out-of-order renewal, plan-switch/cancellation evidence, uncorrelated receipt quarantine, and permanent contradictory-financial-evidence recording. Reported Vitest duration was 4.82 seconds (tests 4.16 seconds). This is developer-supplied terminal evidence, not a test rerun by the architect. The earlier Docker `ENOENT` report is historical and no longer the current integration blocker.
- **Lifecycle decision: `blocked` -> `ready`, with `attempt: 3` preserved and claim cleared.** This is a validation-only follow-up, not acceptance or a request to change Woo implementation code. The normal launcher must claim Attempt 4; do not manually invent a claim or mark the task Complete. The canonical Completion Report still describes the previous blocked run and must be updated by the repository agent with the developer's passing evidence and final actual validation results.
- **Remaining bounded finalization:** synchronize **Background `origin/main` into the existing implementation `task/ARCH-027-BACKGROUND-002` branch** using the launcher, preserving the accepted Shopify platform guards already merged on main (`3f9cb2076f2dad94b37708ed3313542e8cc7b857`). Re-run the affected Woo unit and Shopify guard regressions on the combined branch, and verify `git diff --check`. Rerun the six-case disposable PostgreSQL integration matrix on the combined revision if its reconciliation/runtime or fixtures have materially changed in the merge; otherwise retain the exact developer-run evidence and explain why it remains applicable. Do not modify Shopify reconciliation logic under this task.
- **Separate Commerce diagnostics:** continue to report the previously observed 12 Commerce unit failures and 10 TypeScript/build diagnostics accurately. The unchanged Commerce file/package blobs on main and this branch support their separate baseline classification, but do not claim an unrun check passed. If they worsen or the merge changes affected files, investigate the regression or report it for the owning service. Do not fix unrelated Commerce exports inside BACKGROUND-002.
- **Stop point:** once the Completion Report reflects the successful developer PostgreSQL evidence, post-main synchronization, focused validation and any remaining baseline exceptions, submit the existing task to `review`. BACKGROUND-004 and BACKGROUND-006 stay gated until a subsequent architect acceptance. No `_index.md` reconciliation is authorized.

#### Previous blocked Attempt 3 review (historical)

#### Attempt 3 review — current (2026-10-10)

- **Disposition — Blocked; no new Woo implementation change requested by this review.** The authoritative task remains `status: blocked`, `attempt: 3`, `executor: null` and `claimed_at: null`. Do not promote dependants or mark the implementation Complete. The previous Attempt 2 correction contract remains historical evidence, not a request to repeat its already implemented source changes.
- **A2-R1 — Structurally addressed; PostgreSQL proof pending.** `completeWooReceipt` writes `processedAt` and clears `processingError`; `quarantineWooReceipt` preserves `processedAt: null` and writes a bounded `processingError`; `recordPermanentWooReceiptConflict` retains diagnostics in `Subscription.lastSyncErrorCode` and matching `BillingOperation.lastErrorCode`, completing the receipt with `processingError: null`. The six-scenario disposable PostgreSQL suite contains separate quarantine/no-reclaim and permanent-conflict assertions, but neither has been executed with the Attempt 3 revision.
- **A2-R2/A2-R3 — Structurally addressed.** The new `reconcileWooReceiptsAndGlobalBillingScan` boundary logs a bounded Woo batch failure using the shared structured logger and still calls the existing global Shopify billing scan once. It emits the Woo completion signal only when its batch succeeds. Two focused tests check failure continuation, logging bounds, success order and single-scan invocation. The Shopify scan implementation is not modified by this task.
- **Separate Shopify compatibility merge must be accounted for.** The developer's Shopify platform-guard change is already merged into `moda-interact-background` `main` (merge `3f9cb2076f2dad94b37708ed3313542e8cc7b857`). The Background task branch/uploaded snapshot predates that merge and therefore does not yet contain explicit `ShopPlatform.SHOPIFY` conditions in the Shopify global scan, reconstruction query or individual Shop lookup. The task and `main` differ only in their separately owned Woo source versus this Shopify guard on the respective sides of the branch comparison. Preserve the three already accepted Shopify guards via ordinary `origin/main`-into-task synchronization before final integrated validation/merge. Do not reimplement, reverse or delete the Shopify guards in BACKGROUND-002.
- **Commerce validation findings remain separate.** The reported 12 failing Commerce unit tests and 10 TypeScript/build diagnostics concern unchanged Commerce files and Shared-package exports. The affected Commerce source/tests plus `package.json` and `package-lock.json` have identical Git blobs on Background `main` and this task branch. These are not demonstrated as introduced by the Woo changes; they are also **not** reported as passing. Track their actual baseline/dependency remediation separately rather than changing Commerce under this Woo task.
- **Outstanding acceptance gate.** The Attempt 3 integration command stopped at `spawn docker ENOENT` before Vitest started; this is absence of execution evidence, not evidence of passing or failing reconciliation. The developer can run the repository's declared disposable PostgreSQL/Redis harness from a host shell with working Docker. The exact six-scenario integration suite and combined post-Shopify-merge focused validation are still required for acceptance.

#### Historical Attempt 2 review (retained verbatim below)

The following Attempt 2 correction contract is the **latest authoritative review** and supersedes the prior Attempt 1 follow-up/claim instructions below. Attempt 1 findings are retained for history. No code correction from the previous proposed receipt-state patch has been applied by the architect; the repository agent owns these corrections when it claims Attempt 3.

- **A2-R1 — Fix Woo receipt processing-state constraint (bounded Background implementation).** The developer's PostgreSQL/Redis matrix progressed to **4 of 5 passing tests** after the catalogue fixture correction. The remaining `isolates historical contracts and permanently records contradictory authenticated financial evidence` scenario fails in `subscription-receipt-bookkeeping.ts` with PostgreSQL SQLSTATE `23514`, `WooCommerceBillingWebhookReceipt_processing_state_check`. The currently submitted code sets both `processedAt` and `processingError` for permanently reconciled conflicts; `quarantineWooReceipt()` also writes that prohibited combination. Preserve the database constraint, and correct `subscription-receipt-bookkeeping.ts` plus its Woo processor call sites. Successfully or permanently reconciled receipts must have `processedAt` set and `processingError` null; retain a bounded `lastSyncErrorCode` on the Subscription and matching BillingOperations for durable attributable financial conflicts. Uncorrelated/malformed/platform-mismatched receipts must remain `processedAt: null` with a bounded `processingError`, excluded from repeat claims by the existing predicate. Do not swallow errors, mark a failed transaction successful, weaken the receipt constraint, or change another provider's billing path. Add PostgreSQL assertions for both permanent conflict and quarantine, including no repeated claim.

- **A2-R2 — Isolate Woo batch failure from the existing billing-cycle sequence (Woo-only entrypoint correction).** `src/entrypoints/billing.ts` currently awaits the new `wooSubscriptionReceiptReconciliationService.reconcileBatch(...)` before the existing `billingReconciliationService.reconcileOnce(...)`. A thrown Woo batch exception aborts the whole cycle before the Shopify global reconciliation attempt. Wrap **only the Woo batch invocation** in a bounded failure boundary. On a thrown Woo exception, emit a structured error with the existing `@modainteract/moda-interact-shared/logging` logger, include safe bounded error metadata and lease/config correlation, do not log a false Woo completion, and continue to invoke the **unchanged** Shopify global reconciliation once. Keep the existing lease/scheduler, other cycle work, and independent background worker behaviour; do not add a parallel scheduler or duplicate billing scans. A shared-database outage may still independently cause the Shopify attempt to fail; the guarantee is that the Woo exception itself does not prevent that attempt.

- **A2-R3 — Add focused regressions for the Woo failure boundary (tests).** Verify that a rejected Woo reconciliation batch is logged, does not emit the Woo success signal, and does not prevent exactly one subsequent call to the existing global billing reconciliation; verify the successful Woo path remains unchanged. Keep the test seam narrow and modules maintainable. Cover `processedAt`/`processingError` exclusivity, permanent conflict diagnostics, and quarantined receipt no-retry behaviour in the disposable PostgreSQL suite. The four scenarios already passing after the catalogue fixture fix must continue to pass.

- **A2-R4 — Complete outstanding validation and correct report status (evidence).** Run the exact developer-side `npm run test:integration -- tests/integration/woocommerce-subscription-reconciliation.concurrency.integration.test.ts` against disposable PostgreSQL/Redis **after** both changes, recording test counts, failures, harness environment and exit code. Also rerun affected Woo unit tests, the declared TypeScript/Prisma/build checks and `git diff --check`; record actual results in the Completion Report. The report's existing phrase `Ready for Architect Review` is stale while required integration validation is failing. Do not mark this task `review` until all required checks/acceptance criteria pass; return `blocked` with evidence if environment prevents validation.

- **A2-R5 — Strict scope boundary.** This correction is **WooCommerce-only within moda-interact-background**. Do **not** add `Shop.platform` filters to Shopify reconciliation, modify `billing-reconciliation.service.ts` or Shopify billing/subscription logic, alter Shopify provider selection, change Prisma schema/migrations, update shared contracts, edit another repository, or touch `docs/**/_index.md`. The earlier suggestion of Shopify-specific platform filters is expressly **outside this task** and must not be implemented in Attempt 3. Keep BACKGROUND-004 and BACKGROUND-006 pending until BACKGROUND-002 is architect-accepted Complete.

#### Historical Attempt 1 review (preserved)

- **A1-R1 — Correct receipt-specific BillingOperation correlation (source and PostgreSQL regression).** In `subscription-transition.service.ts:55-84`, `SUBSCRIPTION_CREATE` is confirmed during first activation but its ID is not carried into the returned result. Consequently `subscription-receipt-processor.ts:95-97` completes the `activated` receipt without the required `billingOperationId`, contrary to the already-written assertions at `woocommerce-subscription-reconciliation.concurrency.integration.test.ts:289-291`. Conversely, `subscription-transition.service.ts:94-134` returns a plan-switch operation ID derived from *all* contract receipts for the currently claimed receipt, and may use that ID for unrelated `renewed`, `paused`, `refunded` or `canceled` receipts. A prior plan switch can therefore mislink a canceled receipt that should correlate with its `CANCEL` operation. Derive the optional link from the **claimed receipt's** topic and deterministically compatible operation; keep independent projection/confirmation of other contract evidence separate from receipt attribution. Regression: first and duplicate activated -> unique create; updated -> matching switch only; canceled -> matching cancel; autonomous renewed/paused/refunded -> null unless an independently justified deterministic match exists. Preserve existing non-null links and fail closed on conflicts.

- **A1-R2 — Establish renewal-payment causality rather than accepting an unrelated historic payment (source and unit/PostgreSQL regression).** `subscription-receipt-evidence.ts:50-92` allows a `renewed` observation when *any* completed transaction linked to a completed billing intent exists, even if it predates the asserted renewal by days and the newer intent is failed. `providerAt` then prefers `contract.date_modified`, allowing unrelated recent contract edits to make old payment evidence appear current. The integration fixture `wrapper()` always uses the original 2026-10-01 payment even for its later 2026-10-05 `renewed` event. Require a causally relevant successful billing-intent/transaction for claimed renewal/payment recovery, or document and substantiate a provider contract guarantee that the signed `renewed` topic alone is sufficient financial proof; do not use a historical transaction as false corroboration. Preserve fail-closed behavior for ambiguous contradictory financial evidence. Cover old-payment-only, current-payment-success and newer-failed-intent cases.

- **A1-R3 — Fail closed on same-price plan identity ambiguity (source and regression).** `subscription-operation-resolution.ts:29-55` matches a newer `PLAN_SWITCH` intent to an `updated` snapshot using only provider timestamp and `quotedAmountMinor`. Two distinct catalogue plans can have the same price. A signed update still describing the old plan at that price can incorrectly activate the later target and its included-credit allowance. `subscription-receipt-evidence.ts` parses `planName` but the resolver does not use or validate plan identity. Correlate the provider snapshot to a uniquely supported accepted plan identity as far as the documented signed Woo fields permit; where unique correlation cannot be proved, record bounded sync attention instead of projecting the plan by price alone. Add same-price/different-plan positive and negative tests and retain the stale-update safeguard.

- **A1-R4 — Make disposable integration fixtures consistent with the canonical Free catalogue (test correction).** The integration `createFixture()` creates a distinct active global `BillingPlan(kind=FREE)` for each Shop (`...concurrency.integration.test.ts:35-64`). The terminal transition deliberately requires exactly one active global Free BillingPlan (`subscription-period-projection.ts:117-122`). The tests at lines 443-503 and 505-558 simultaneously create two such fixtures, so the terminal/related matrix cannot reliably pass under its own setup. Share or consistently seed one canonical Free plan across those fixtures, and make teardown safe, without weakening production's fail-closed uniqueness rule or changing unrelated tasks.

- **A1-R5 — Complete the required developer-owned integration validation before acceptance (evidence).** The Completion Report explicitly states that `npm run test:integration -- tests/integration/woocommerce-subscription-reconciliation.concurrency.integration.test.ts` was not executed. After correcting A1-R1 through A1-R4, run the repository's disposable PostgreSQL/Redis matrix in the developer environment, record the actual command, passing/failing test identifiers, infrastructure evidence and result in the same task report, and resolve all task-attributable failures. Rerun relevant unit, build, Prisma, typecheck and diff checks after source changes. Do not check the currently pending database-backed Validation items merely because their tests were authored.

### Reviewed Files

- `docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md` and `docs/decisions/background/ARCH-027/BACKGROUND-002-reconcile-woocommerce-recurring-subscription-receipts.md`.
- `src/entrypoints/billing.ts` and `src/services/woocommerce-billing/*.ts`, particularly `subscription-transition.service.ts`, `subscription-receipt-processor.ts`, `subscription-receipt-operation-correlation.ts`, `subscription-operation-resolution.ts`, `subscription-receipt-evidence.ts`, `subscription-period-projection.ts` and `subscription-receipt-bookkeeping.ts`.
- `tests/unit/services/woocommerce-billing/*.test.ts`, `tests/integration/woocommerce-subscription-reconciliation.concurrency.integration.test.ts` and `scripts/test-integration.mjs`.
- Implementation commits `e9975f5` and `ba8aba1ab87d8fd0bc8706f739fd78009c8c0fd0`; parent report commit `9e996aa5e64c9753750a6827354027584891ef0a`.

### Validation Reviewed

- **Developer-host integration result (2026-10-10, post Attempt 3):** Vitest 4.1.11, `tests/integration/woocommerce-subscription-reconciliation.concurrency.integration.test.ts`: **6/6 PASS**, one test file, 4.82 seconds total. This resolves the former `spawn docker ENOENT` no-execution blocker; no independent rerun or exit-code observation is claimed. The original test transcript is supplied by the developer in the architect conversation and must be durably reflected by the task executor in the Completion Report.
- **Final integration boundary:** Shopify platform guards are merged in Background `origin/main`, not yet included in the submission revision; synchronize `origin/main` into the task branch and run the scoped combined checks before review.
- **Attempt 3 source/repository review (2026-10-10):** inspected the exact uploaded Attempt 3 snapshot and the pushed Background task branch; checked the Woo receipt bookkeeping and processor, the new billing-cycle boundary and its two unit regressions. Relevant task/source Git blobs match the published task branches. Reported focused Woo tests: 32 passed; Prisma validation: passed. No independently executed npm/PostgreSQL test is claimed.
- **Attempt 3 outstanding evidence:** `npm run test:integration -- tests/integration/woocommerce-subscription-reconciliation.concurrency.integration.test.ts` exited before Vitest (`spawn docker ENOENT`); zero PostgreSQL assertions ran. Reported Commerce suite: 1,933 passed / 12 failed; TypeScript and build: 10 Commerce diagnostics. The touched Woo code was not among those TypeScript diagnostics. The same Commerce source/test/lockfile blobs exist on Background main, but no independently run mainline baseline is claimed.
- **Cross-branch check:** Background main includes accepted Shopify platform guards, whereas this task branch's three Shopify reconciliation files are still the older pre-merge versions. Final validation must preserve those mainline guards and independently test Woo batch failure continuation.
- **Attempt 2 developer evidence (2026-10-10):** the initial disposable integration run failed during `MerchantPricingPlan` fixture setup in all five tests; after the locally applied catalogue-fixture correction, **four of five PostgreSQL integration tests passed**. The remaining failed test was stopped by `WooCommerceBillingWebhookReceipt_processing_state_check` (SQLSTATE `23514`) in receipt bookkeeping, before successful conflict persistence could be established. This is developer-provided execution evidence, not an independently rerun integration suite. The previously provided receipt-state code patch was expressly **not applied**. The reported Attempt 2 unit/typecheck/build results do not satisfy the failing database integration requirement.
- The following Attempt 1 validation notes are retained as historical context and must not be interpreted as the current Attempt 2 test status.
- Submission reports 19/19 Woo-focused unit tests, 1,908/1,908 full unit tests, TypeScript check, build/Prisma validation and `git diff --check` passing. These results are **reported, not independently rerun** in this review environment.
- Independently inspected the source, regression assertions and matrix setup in the exact supplied snapshot. Relevant source and task file Git blob hashes match the pushed remote `task/ARCH-027-BACKGROUND-002` branches.
- The mandated disposable PostgreSQL/Redis matrix has **not run**; the static source/test contradictions listed in A1-R1 through A1-R4 prevent treating the claimed acceptance criteria as empirically established.

### Architecture Conformance

Partial. The implementation respects the single leased billing worker, bounded modules, provider-free reconciliation, Shop/Subscription lock boundary, exact-30-day first period and distinct provider coverage/Moda allowance clocks in structure. Receipt-to-operation attribution, financial renewal proof, and ambiguous same-price plan reconciliation remain non-conforming until corrected and demonstrated against PostgreSQL.

### Follow-up

- **Current re-gate (2026-10-10):** task is `ready`, `attempt: 3`, executor and claim null. The launcher must claim Attempt 4; update the stale Completion Report with developer PostgreSQL 6/6 evidence, incorporate latest Background main (retaining Shopify guards), validate the combined revision, and resubmit as `review` without unrelated source changes. Do not promote dependants before architect acceptance.
- Historical blocked/Attempt 2/Attempt 1 handoff statements below remain as audit history and are superseded by the current re-gate.
- **Current Attempt 3 disposition (2026-10-10): remain Blocked.** Do not claim Attempt 4, re-gate to Ready or accept until the outstanding disposable PostgreSQL/Redis matrix has actually run and its reported outcome is reviewed. Preserve `attempt: 3`; no implementation rewrite is requested solely because the agent shell lacked Docker.
- **Developer evidence path:** from the dedicated Background implementation worktree, verify Docker is available using `command -v docker` and `docker info`, then run `npm run test:integration -- tests/integration/woocommerce-subscription-reconciliation.concurrency.integration.test.ts`; record the exit code and all six outcomes. Do not substitute bare Vitest for the disposable harness.
- **Integration of previously accepted Shopify change:** before accepting or merging BACKGROUND-002, incorporate the latest Background `origin/main` *into* its implementation task branch through the approved synchronized worktree workflow, retaining Shopify platform guards. Validate the Woo focused tests and the Shopify guard regressions on the combined revision. Do not merge this blocked task into main or stage unrelated submodule pointers.
- **Commerce diagnostics:** compare with actual mainline baseline and route any Shared/Commerce export repair to the owning work; do not modify unrelated Commerce code in BACKGROUND-002. Once outstanding evidence passes, reconcile the lifecycle and submit this same task to `review` through its authorized path; BACKGROUND-004 and BACKGROUND-006 remain gated until acceptance.
- **Current Attempt 2 disposition (2026-10-10):** authorize return of this same stranded `in_progress` task to `ready`, clearing `executor` and `claimed_at` while **preserving `attempt: 2`**. After this review is committed/pushed on the parent task branch and the implementation task worktree is clean/synchronized, the deterministic launcher may claim **Attempt 3**. The repository agent must read and implement A2-R1 through A2-R5 above. Do not apply the previous receipt-state implementation patch as an additional independent step; the agent owns that code correction during Attempt 3. The historic Attempt 1 follow-up below is superseded.
- Return **this same task** to `ready`, with `executor: null`, `claimed_at: null`, and the accepted historical attempt count of `1` unchanged. The next deterministic launcher claim is Attempt 2. Preserve the entire existing Completion Report and this latest explicit correction contract.
- Repository owner `moda_background` should correct A1-R1 through A1-R4 within BACKGROUND-002, rerun focused validation and return an updated Completion Report after A1-R5 passes. Do not create an implementation-branch commit solely for report evidence when no code change is required.
- Keep `ARCH-027-BACKGROUND-004` and `ARCH-027-BACKGROUND-006` dependency-gated until this task is architect-accepted Complete. No provider network work, schema migration, Shared contract, other repository feature changes or `docs/**/_index.md` updates are authorised.
