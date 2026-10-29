---
id: ARCH-048-BACKGROUND-008
architecture_id: ARCH-048
title: Admit the next Woo recovery generation from a mature candidate
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 34
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-048-BACKGROUND-007
enables:
  - ARCH-048-BACKGROUND-011
created: 2026-10-29
updated: 2026-10-29
---

# ARCH-048-BACKGROUND-008 — Admit the next Woo recovery generation from a mature candidate

## Architecture

Architecture ID: `ARCH-048`.

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md` (recovery-generation amendment).

Coordinator: `moda_architect`. **Defined but not materialised** from a 2026-10-29 source snapshot. Start only from launcher-prepared worktrees with this task marked Ready and BG007 accepted Complete.

## Objective

Make `WooRecoveryAdmissionService` create **exactly one `CheckoutRecovery` per mature, accepted Woo abandonment generation**, using the latest basket and existing consent/order policy, without reusing or reawakening an earlier generation.

## Context

Current `woo-recovery-admission.service.ts` returns `already-exists` for **any** row with `(shopId,checkoutToken)` and always INSERTs `generation: 1`. BG007 now owns `WooPendingCandidate.generation`, the generation-aware candidate index and the local `WooAdmissionOutcome` discriminant. A returned `already-exists` must never instruct the orchestrator to send an old generation merely because another generation exists.

## Scope

**Permitted implementation files (Background only):**

- `src/services/woocommerce-recovery/woo-recovery-admission.service.ts` — generation-scoped row lookup, admission, history and explicit retry outcomes.
- `src/services/woocommerce-recovery/woo-recovery-admission-evidence.ts` — candidate equality/validation and durable admission-origin event helpers.
- Focused admission tests under `tests/unit/services/woocommerce-recovery/`, `tests/integration/woo-recovery-admission.integration.test.ts`, `woo-recovery-admission-races.integration.test.ts` and existing source-isolation tests.

Consume BG007's `contracts.ts` **read-only**. Do not edit checkout scheduling, candidate queue, order reconciliation, outreach/billing, orchestrator, workers, API, plugin, Prisma model or any other architecture task.

## Out of Scope

No checkout-resumption closure (BG007), sending (BG009), WhatsApp inbound routing (BG010), worker composition (BG011), schema migration, new Customer creation or Shopify materialisation refactor.

## Requirements

1. **Validate candidate and generation.** Reject wrong source/shop/checkout, missing/invalid `generation` (must be positive safe integer), invalid event ID/timestamp, and unknown/empty/oversized/invalid item evidence exactly as current consent/admission policy requires. `sameAcceptedCandidate(expected,current)` must also compare `generation` and full bounded item evidence, not only event timestamp. The current generation's candidate index and accepted watermark must agree before admission.
2. **Current-row classification (under BG007's shared checkout coordinator):** find latest recovery by `generation DESC`. If no row exists, only `candidate.generation === 1` may be admitted. If latest is `N`, only candidate `N+1` can create a row, and only when the latest was conclusively closed by `CHECKOUT_RESUMED` (status history source `woocommerce.checkout`) or is a permissible non-order `EXPIRED` state with newer checkout evidence. Do **not** treat a generic `CANCELLED`, `COMPLETED`, order-linked or ambiguous terminal row as permission to re-enter. If latest is active, reject/defer creating another row. Candidate generations lower than the latest are `superseded`, not `already-exists` for the latest ID.
3. **Matching-row retry:** for `candidate.generation === latest.generation`, return `{kind:"already-exists", recoveryId, generation, repairInitial:true}` **only** when latest row is still `DETECTED` and its admission history metadata has the **same `lastEventId` and generation** as this candidate, proving this is the original INSERT→enqueue repair. Otherwise return `{repairInitial:false}` for an idempotent exact already-sent row or `superseded` for mismatched/stale evidence. Do not return a previous generation's ID as the repair target. Do not infer equivalence from `checkoutToken` alone or event-time equality.
4. **Recheck immediately before commit:** retain current Shop/Woo installation state, explicit current-recipient phone identity, consent/STOP, recovery execution eligibility, merchant delay, nonempty items, observed order and missing-consent notification behaviour from ARCH-046. Repeat bounded candidate/terminal checks under checkout coordination before the SQL transaction. Consent revocation/STOP races must be covered by `confirmCurrentWooConsent()` inside the transaction. `none-observed` is not proof that Woo has no order.
5. **Transactional admission:** inside one PostgreSQL transaction, acquire a stable row lock on the prior latest recovery when it exists (`SELECT ... FOR UPDATE` or equivalent safe lock), re-evaluate its status and `CHECKOUT_RESUMED` history, then INSERT `generation: candidate.generation` with `lineItems`, `currency`, `totalPrice`, `customerId`, `detectedAt`, `lastExternalActivityAt` from the **candidate's latest complete snapshot**. Insert its `DETECTED` status-history row **in that same transaction**. Preserve `reason="FIRST_MATURE_CHECKOUT_ADMISSION"` for generation 1 and use `reason="MATURE_CHECKOUT_REENTRY_ADMISSION"` for later generations; use `source="WOOCOMMERCE"` and bounded `metadata: {generation, lastEventId}` for **both** so BG007 can identify an exact admission-origin replay. Do not write to/modify earlier generation's basket, status or history during this admission.
6. **Uniqueness and concurrency:** keep existing `(shopId, checkoutToken, generation)` unique constraint; only a proven conflict on this exact target may be converted into an exact matching `already-exists` response after rereading the row/history. All other Prisma errors, lock conflicts and corrupt metadata propagate to BullMQ retry and are logged. Never return success for a different-generation insert or a row whose provenance cannot be verified.
7. **No send in admission:** `created` and `already-exists` report `recoveryId` and `generation` through BG007's local contract. Only BG011 may enqueue via BG009 after the transaction commits; never perform queue, Redis, external HTTP, Meta or billing operations inside the INSERT transaction. Keep existing ARCH-046 denied-admission Support notice hook; notify only a genuine denied candidate, with existing dedupe.
8. **Source isolation:** accepted Woo rows have `cartToken: null` and no fabricated restore URL. Preserve legacy Shopify candidate routing, existing credit identities and Woo outbound default-off. There is **no cross-generation initial outreach cap or cooldown** in admission.
9. **Diagnostics:** use the already published `@modainteract/moda-interact-shared/logging` with bounded shopId, generation, recoveryId, hashed event ID, stage, decision/reason; log and rethrow technical exceptions. No raw cart contents, addresses, phone numbers, checkout keys or consent payloads.

## Work Items

- [ ] Implement strict candidate generation and exact candidate+watermark matching in admission evidence.
- [ ] Replace any-generation existence prohibition with latest-row/previous-history admission rules.
- [ ] Implement transaction-locked row-only Nth-generation insertion and origin-event metadata.
- [ ] Implement exact-generate `already-exists`/`repairInitial` classification and P2002 recovery.
- [ ] Extend unit, PostgreSQL and races tests; document results without changing unrelated services.

## Interfaces / Contracts

- **Input:** `WooRecoveryAdmissionEvaluator.evaluateMatured(candidate: WooPendingCandidate, context:{jobId?:string})` from BG007, including required `generation`.
- **Output:** `WooAdmissionOutcome` v2 from BG007: `created { recoveryId, generation }`, `already-exists { recoveryId, generation, repairInitial }`, or `superseded/denied/deferred { reason }`.
- **Read ports:** BG007 generation-aware `WooCandidateManager.getPending(ref, expectedGeneration?)`; BG002 existing `WooObservedOrderStateReader` and checkout coordinator.
- **DB:** existing Prisma `CheckoutRecovery`, `CheckoutRecoveryStatusHistory`, existing recipient/consent tables. No migration or new externally published contract.
- **History metadata contract:** new admission rows use `metadata.generation` (positive int) and `metadata.lastEventId` (validated bounded event ID). Do not create a competing metadata shape in another file.

## Dependencies

- `ARCH-048-BACKGROUND-007` — must be architect-accepted **Complete**, not merely a successful branch push.
- Existing accepted `ARCH-048-BACKGROUND-003`, `ARCH-046-BACKGROUND-002` and `ARCH-046-BACKGROUND-004` are consumed; do not reopen them.

## Enables

- `ARCH-048-BACKGROUND-011` — generation-aware composition/dispatch.

## Acceptance Criteria

- [ ] No prior row + matured generation 1 creates generation 1 exactly once.
- [ ] Generation 1 CANCELLED by `CHECKOUT_RESUMED` + mature generation 2 creates an independent row with updated items/currency/total, distinct ID, frozen generation 1.
- [ ] Generation 2 repeated maturity or competing workers produce one gen-2 row and one `DETECTED` history row, with **provenance-checked** `already-exists`.
- [ ] Duplicate gen-1 candidate after gen-2 creation, an active prior generation, an order-linked cancellation, `COMPLETED`, and mismatched history never create another row or enqueue request.
- [ ] Redis index absent/completed, pre/post-transaction crashes, expired checkout lease and P2002 collision do not admit a stale generation or conceal errors.
- [ ] Consent denied/withdrawn/STOP/ambiguous recipient/invalid basket prevent admission; denied-admission merchant notification remains correctly deduplicated.
- [ ] No cross-generation send limit is introduced, and no Meta/provider operation or Redis call executes inside the SQL transaction.

## Validation

- [ ] `npx vitest run` the focused Woo admission unit tests and source-contract tests.
- [ ] `node scripts/test-integration.mjs tests/integration/woo-recovery-admission.integration.test.ts tests/integration/woo-recovery-admission-races.integration.test.ts` (or repository runner's documented equivalent if the script accepts files separately).
- [ ] `npm run build`; focused lint when available; `git diff --check`. Record exact executed commands, environment limitations and baseline IDs.

## Stop Condition

Complete only this admission capability, record the required Completion Report, set `status: review`, hand back to `moda_architect` and **STOP**. Do not integrate workers or begin BG009–BG011.

## Implementation Notes

Use `/moda-task` preparation; record **launcher-resolved dedicated parent and implementation worktree paths**, task-branch revisions, synchronization and recursive-submodule evidence. Use no `@modainteract/moda-interact-shared` source-code copies or new logger. All codes/fields above are acceptance contracts, not optional suggestions. Any discovered need for a new database migration or inter-service wire contract is a blocked architectural dependency, not permission for this agent to expand scope.

## Completion Report

### Status

Not Started — portable, not materialised.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Based only on the uploaded snapshot dated 2026-10-29; accepted code may differ on the developer's live task branch.

### Unresolved Issues

None at definition time.

### Architectural Concerns

See ARCH-048's event-only completeness limitation.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
