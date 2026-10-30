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
status: complete
priority: 34
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-048-BACKGROUND-007
enables:
  - ARCH-048-BACKGROUND-011
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-048-BACKGROUND-008 — Admit the next Woo recovery generation from a mature candidate

## Architecture

Architecture ID: `ARCH-048`.

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md` (recovery-generation amendment).

Coordinator: `moda_architect`. Originally defined from a 2026-10-29 source snapshot and materialised on the parent task branch before execution. The launcher prepared dedicated parent and implementation worktrees, verified BG007 Complete, and claimed Attempt 1 on 2026-10-30.

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

- [x] Implement strict candidate generation and exact candidate+watermark matching in admission evidence.
- [x] Replace any-generation existence prohibition with latest-row/previous-history admission rules.
- [x] Implement transaction-locked row-only Nth-generation insertion and origin-event metadata.
- [x] Implement exact-generation `already-exists`/`repairInitial` classification and P2002 recovery.
- [x] Extend unit, PostgreSQL and race tests; document results without changing unrelated services.

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

- [x] No prior row + matured generation 1 creates generation 1 exactly once.
- [x] Generation 1 CANCELLED by `CHECKOUT_RESUMED` + mature generation 2 creates an independent row with updated items/currency/total, distinct ID, frozen generation 1.
- [x] Generation 2 repeated maturity produces one gen-2 row and one `DETECTED` history row, with provenance-checked `already-exists`.
- [x] Duplicate gen-1 candidate after gen-2 creation, an active prior generation, an order-linked cancellation, `COMPLETED`, and mismatched history never create another row or enqueue request.
- [x] Missing candidate index after insert and P2002 collision do not admit a stale generation or conceal errors. Candidate and watermark are rechecked before the transaction; a database row lock and existing unique constraint fence concurrent inserts.
- [x] Consent denied/withdrawn/STOP/ambiguous recipient/invalid basket prevent admission; denied-admission merchant notification remains correctly deduplicated through the existing adapter.
- [x] No cross-generation send limit is introduced, and no Meta/provider operation or Redis call executes inside the SQL transaction.

## Validation

- [x] `npx vitest run tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts tests/unit/services/woocommerce-recovery/woo-recovery-consent-notice.adapter.test.ts` — 63 tests passed.
- [x] `node scripts/test-integration.mjs tests/integration/woo-recovery-admission.integration.test.ts tests/integration/woo-recovery-admission-races.integration.test.ts` — 8 PostgreSQL/Redis tests passed, including deterministic expired-lease fencing.
- [x] `npm run build` — Prisma client generation and TypeScript build passed.
- [x] Focused `npx eslint` on the five changed implementation/test files — passed.
- [x] `git diff --check` — passed.

A supplementary combined run of `npx vitest run tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts tests/unit/services/woocommerce-recovery/woo-recovery-consent-notice.adapter.test.ts tests/unit/runtime/entrypoint-isolation.test.ts` had 71 passing and 1 failing test. The failure is outside this task's changed files: `production worker entrypoints > wires bounded Shared logging for scheduled billing failures` expects `error.message.slice(0, 256)` at `tests/unit/runtime/entrypoint-isolation.test.ts:146`, while unchanged `src/entrypoints/billing.ts` records `errorMessage: message`. The repository baseline document has no matching baseline ID. This was not changed as it is out of task scope.

The prepared implementation worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-008`; the prepared parent worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-008`. Both use `task/ARCH-048-BACKGROUND-008`. Launcher startup evidence: implementation base `ddd13338247f26c2ed5e7146489709de9f5e3f7a`; parent base `2b73f710ff3d2e68c8d71b4a65214862c7daf916`; dependency gate passed for `ARCH-048-BACKGROUND-007` Complete; recursive submodules ready, including `moda-interact-database` at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`; Attempt 1 claim recorded for `codex`.

The implementation commits are published on `task/ARCH-048-BACKGROUND-008` at `https://github.com/kodjobaah/moda-interact-background.git`; the parent task branch is published at `https://github.com/kodjobaah/moda-interact-workspace.git`. Publication followed the user's explicit authorization. See the Completion Report's Git / VCS section for verified branch SHAs.

## Stop Condition

Complete only this admission capability, record the required Completion Report, set `status: review`, hand back to `moda_architect` and **STOP**. Do not integrate workers or begin BG009–BG011.

## Implementation Notes

Use `/moda-task` preparation; record **launcher-resolved dedicated parent and implementation worktree paths**, task-branch revisions, synchronization and recursive-submodule evidence. Use no `@modainteract/moda-interact-shared` source-code copies or new logger. All codes/fields above are acceptance contracts, not optional suggestions. Any discovered need for a new database migration or inter-service wire contract is a blocked architectural dependency, not permission for this agent to expand scope.

## Completion Report

### Status

Implementation and required validation are complete. The implementation task branch and parent task/report branch are published. Architect review accepted this task as Complete; no merge to `main` is implied.

### Files Changed

- `src/services/woocommerce-recovery/woo-recovery-admission.service.ts`
- `src/services/woocommerce-recovery/woo-recovery-admission-evidence.ts`
- `tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts`
- `tests/integration/woo-recovery-admission.integration.test.ts`
- `tests/integration/woo-recovery-admission-races.integration.test.ts`

### Work Completed

Admission now requires a positive safe generation and exact candidate/current-index/accepted-watermark agreement. It classifies the latest durable generation and its resumption/order history, admits only generation 1 initially or generation N+1 after a proven resumption or eligible non-order expiry, and treats stale generations as superseded. Matching-row recovery requires exact `DETECTED` admission provenance to set `repairInitial: true`; exact sent/engaged rows return `repairInitial: false`. Insertion locks and rechecks the prior row in the PostgreSQL transaction, writes the candidate generation's complete basket and admission-origin metadata atomically, and returns only a proven exact P2002 collision. Corrupt resumption/order provenance throws for retry. No queue or provider operation was added to the transaction.

Implementation commits: `2007c05a409342890b19e97ca824df61aee9094c` (`feat(background): admit mature Woo recovery generations`) and `e4b11a74d017276c8a8e321f9d5734f957647fee` (`test(background): cover expired checkout admission lease race`), published on `origin/task/ARCH-048-BACKGROUND-008`.

### Validation Results

- Focused Woo admission and consent-notice unit tests: 63 passed.
- PostgreSQL/Redis admission and race integration tests: 8 passed, including generation-2 basket refresh, frozen generation-1 history, and deterministic expired-lease fencing. The race test `fences simultaneous admission after an expired checkout lease with the PostgreSQL generation key` gives both contenders a simulated lease and releases both transactions through a barrier; PostgreSQL leaves one generation row and one history record, without a wall-clock wait.
- `npm run build`: passed.
- Focused ESLint over all five changed files: passed.
- `git diff --check`: passed.
- Supplementary runtime source-isolation suite: 9/10 passed; the lone billing logger expectation failure is documented under Validation and is outside the changed files.

### Deviations

No source or contract changes outside task scope. Publication proceeded after the user explicitly authorized publishing to the configured origins.

### Assumptions

The prepared launcher packet is authoritative for worktree paths, task branches, branch synchronization, dependency gate and recursive submodule evidence.

### Unresolved Issues

The expired checkout lease case is covered by `fences simultaneous admission after an expired checkout lease with the PostgreSQL generation key`: the test uses a fake Redis adapter that permits both lease acquisitions and a transaction barrier that releases both workers concurrently, then verifies the PostgreSQL generation key leaves exactly one recovery and one history record. The case is deterministic and uses no wall-clock delay.

### Git / VCS

Task branch: `task/ARCH-048-BACKGROUND-008`.

Physical worktree isolation:
- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-BACKGROUND-008`
- parent branch: `task/ARCH-048-BACKGROUND-008`
- implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-BACKGROUND-008`
- implementation branch: `task/ARCH-048-BACKGROUND-008`
- shared workspace checkout switched/mutated for task work: no
- shared implementation checkout switched/mutated for task work: no
- another task worktree reused: no

Start-of-attempt synchronization evidence from the prepared launcher: parent remote task branch fast-forwarded: not needed; parent `origin/main` incorporated before submission: yes (merged into the dedicated task branch); implementation remote task branch fast-forwarded: not needed (no remote task branch existed); implementation `origin/main` incorporated: already current.

Implementation repository:
- repository: `moda-interact-background`
- commit: `e4b11a74d017276c8a8e321f9d5734f957647fee`
- remote branch: `origin/task/ARCH-048-BACKGROUND-008`
- pushed: yes

Parent workspace:
- task file: `docs/decisions/background/ARCH-048/BACKGROUND-008-admit-subsequent-woo-recovery-generations.md`
- task/report submission commit: `b8c83f81c41116e2428954d8a139999870edb5ff`
- remote branch: `origin/task/ARCH-048-BACKGROUND-008`
- pushed: yes
- submodule gitlink staged: no

Merged to implementation main: no.
Merged to workspace main: no.

### Architectural Concerns

See ARCH-048's event-only completeness limitation.

## Architect Review

### Review Status

Accepted — Architect Review Accepted.

### Review Notes

Code review passes; no blocking defects found in the local implementation. Candidate/current-index/accepted-watermark checks, prior-generation provenance, and PostgreSQL concurrency fencing align with task acceptance criteria.

### Reviewed Files

- `src/services/woocommerce-recovery/woo-recovery-admission.service.ts`
- `src/services/woocommerce-recovery/woo-recovery-admission-evidence.ts`
- `tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts`
- `tests/integration/woo-recovery-admission.integration.test.ts`
- `tests/integration/woo-recovery-admission-races.integration.test.ts`

### Validation Reviewed

Reviewed the reported 63 focused unit tests, 8 PostgreSQL/Redis integration tests, build, focused ESLint and diff-check; these were not rerun. Also reviewed the documented supplementary 71/1 source-isolation result; its lone billing logger failure is outside changed files and remains disclosed. Implementation remote commit `e4b11a74d017276c8a8e321f9d5734f957647fee` and parent remote submit commit `0152abca0f3a28b86e4bff1da88a409f0f54c801` were verified; do not merge.

### Architecture Conformance

Requirements satisfied; no schema/wire expansion or provider/Redis call inside transaction.

### Follow-up

BG009 and BG010 remain Ready; BG011 remains Pending until BG009 and BG010 complete; no integrated deployment/live Woo sending implied.
